import os
import pickle
import time
import urllib.parse

import gdown
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="CineMind", page_icon="C", layout="wide")

# ── Load external CSS ──
_css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "style.css")
with open(_css_path, encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# ── Data Loading ──
MOVIES_DICT_URL = "https://drive.google.com/uc?id=1CishRUVNw4h--ffoIblUfpg-p1F5m57c"
SIMILARITY_URL  = "https://drive.google.com/uc?id=1tH8Z4HkjoOI5n8n3ixO1L7ylAofLB5UD"

if not os.path.exists("movies_dict.pkl"):
    with st.spinner("Downloading movie data…"):
        gdown.download(MOVIES_DICT_URL, "movies_dict.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    with st.spinner("Downloading similarity matrix…"):
        gdown.download(SIMILARITY_URL, "similarity.pkl", quiet=False)

movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies      = pd.DataFrame(movies_dict)
similarity  = pickle.load(open("similarity.pkl", "rb"))

TMDB_KEY   = "8265bd1679663a7ea12ac168da84d2e8"
TRY_MOVIES = ["Avatar", "The Avengers", "Titanic", "The Dark Knight"]


# ── TMDB Helpers ──
def _get(url, retries=2, timeout=8):
    for attempt in range(retries + 1):
        try:
            return requests.get(url, timeout=timeout).json()
        except Exception:
            if attempt == retries:
                return {}
            time.sleep(1)


def fetch_poster(movie_id):
    r = _get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}", timeout=7)
    p = r.get("poster_path")
    return f"https://image.tmdb.org/t/p/w500/{p}" if p else ""


def fetch_details(movie_id):
    try:
        d   = _get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US")
        cr  = _get(f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_KEY}&language=en-US")
        vid = _get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_KEY}&language=en-US")
        if not d or not d.get("title"):
            return None
        crew = cr.get("crew", [])
        return {
            "title":     d.get("title", ""),
            "tagline":   d.get("tagline", ""),
            "overview":  d.get("overview", "No summary available."),
            "release":   d.get("release_date", ""),
            "runtime":   d.get("runtime", 0),
            "rating":    round(d.get("vote_average", 0), 1),
            "votes":     d.get("vote_count", 0),
            "budget":    d.get("budget", 0),
            "revenue":   d.get("revenue", 0),
            "language":  d.get("original_language", "").upper(),
            "status":    d.get("status", ""),
            "genres":    [g["name"] for g in d.get("genres", [])],
            "directors": [m["name"] for m in crew if m.get("job") == "Director"],
            "writers":   list(dict.fromkeys(
                [m["name"] for m in crew if m.get("job") in ("Screenplay", "Writer", "Story")]
            ))[:4],
            "cast":      [(m["name"], m.get("character", "")) for m in cr.get("cast", [])[:8]],
            "poster":    f"https://image.tmdb.org/t/p/w500/{d['poster_path']}" if d.get("poster_path") else "",
            "backdrop":  f"https://image.tmdb.org/t/p/w1280/{d['backdrop_path']}" if d.get("backdrop_path") else "",
            "trailer":   next(
                (v["key"] for v in vid.get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer"),
                None,
            ),
            "imdb_id":  d.get("imdb_id", ""),
            "homepage": d.get("homepage", ""),
        }
    except Exception:
        return None


def recommend(title, n=5):
    idx = movies[movies["title"] == title].index[0]
    top = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])[1:n + 1]
    return [
        {
            "title":  movies.iloc[i].title,
            "id":     movies.iloc[i].movie_id,
            "poster": fetch_poster(movies.iloc[i].movie_id),
        }
        for i, _ in top
    ]


def money(v):
    if not v:
        return "—"
    if v >= 1e9:
        return f"${v / 1e9:.2f}B"
    if v >= 1e6:
        return f"${v / 1e6:.1f}M"
    return f"${v:,}"


def stars_html(s):
    filled = round(s / 2)
    return "".join(['<span class="on">★</span>' if i < filled else "★" for i in range(5)])


# ── Navigation ──
def open_movie_detail(movie_id):
    st.session_state.mid  = movie_id
    st.session_state.page = "detail"
    st.query_params["movie"] = str(movie_id)
    if st.session_state.src:
        st.query_params["src"] = st.session_state.src
    st.rerun()


def return_home():
    """Go back to home keeping previous recommendations visible."""
    for k in ("movie", "id"):
        if k in st.query_params:
            del st.query_params[k]
    st.session_state.page = "home"
    st.session_state.mid  = None
    st.session_state["_prev_query_movie"] = None
    st.rerun()


def go_home_fresh():
    """Reset everything — clean slate home page."""
    st.session_state.page = "home"
    st.session_state.mid  = None
    st.session_state.src  = None
    st.session_state.recs = []
    st.session_state["_prev_query_movie"] = None
    st.query_params.clear()
    st.rerun()


# ── Session State ──
for k, v in {"page": "home", "mid": None, "recs": [], "src": None, "_prev_query_movie": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── URL Sync ──
url_movie = st.query_params.get("movie") or st.query_params.get("id")
url_src   = st.query_params.get("src")

if url_movie:
    try:
        st.session_state.mid  = int(url_movie)
        st.session_state.page = "detail"
    except (ValueError, TypeError):
        st.session_state.page = "home"
        st.session_state.mid  = None
        st.query_params.pop("movie", None)
elif not url_movie and st.session_state.get("_prev_query_movie"):
    st.session_state.page = "home"
    st.session_state.mid  = None

st.session_state["_prev_query_movie"] = url_movie

if url_src and url_src in movies["title"].values:
    if st.session_state.src != url_src or not st.session_state.recs:
        st.session_state.src  = url_src
        st.session_state.recs = recommend(url_src, n=5)
elif not url_src and not url_movie:
    st.session_state.recs = []
    st.session_state.src  = None


# ================================================================
# DETAIL PAGE
# ================================================================
if st.session_state.page == "detail":

    nl, nr = st.columns([5, 1], gap="small")
    with nl:
        st.markdown(
            '<div class="dbar"><div class="d-brand">Cine<em>Mind</em></div></div>',
            unsafe_allow_html=True,
        )

    with nr:
        st.markdown('<div class="bwrap" style="padding-top:0.75rem;display:flex;gap:0.4rem;">', unsafe_allow_html=True)
        if st.button("⌂ Home", key="home_btn"):
            go_home_fresh()
        if st.button("← Back", key="back_btn"):
            return_home()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr style="margin:0;border:none;border-top:1px solid var(--bd);">', unsafe_allow_html=True)

    with st.spinner("Loading…"):
        det = fetch_details(st.session_state.mid)

    if not det:
        st.error("Could not load film details. Please check your internet connection and try again.")
        if st.button("← Back", key="error_back_btn"):
            return_home()
        st.stop()

    if det["backdrop"]:
        st.markdown(f"""
        <div class="dhero">
          <img class="bk" src="{det['backdrop']}" />
          <div class="dhero-g"></div>
          <div class="dhero-t">
            <div class="dtitle">{det['title']}</div>
            <div class="dtagl">{det['tagline']}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="dtfb">{det["title"]}</div><div class="dtgfb">{det["tagline"]}</div>',
            unsafe_allow_html=True,
        )

    year = det["release"][:4] if det["release"] else "—"
    rh   = det["runtime"] // 60 if det["runtime"] else 0
    rm   = det["runtime"] % 60  if det["runtime"] else 0
    rt   = f"{rh}h {rm}m" if det["runtime"] else "—"
    gi   = " / ".join(det["genres"][:3]) if det["genres"] else ""

    st.markdown(f"""
    <div class="mstrip">
      <div>
        <div class="mk">Score</div>
        <div style="display:flex;align-items:baseline;gap:3px;">
          <span class="rn">{det['rating']}</span><span class="rd">/10</span>
        </div>
        <div class="st">{stars_html(det['rating'])}</div>
        <div class="rc">{det['votes']:,} ratings</div>
      </div>
      <div class="msep"></div>
      <div><div class="mk">Year</div><div class="mv">{year}</div></div>
      <div class="msep"></div>
      <div><div class="mk">Runtime</div><div class="mv">{rt}</div></div>
      <div class="msep"></div>
      <div><div class="mk">Language</div><div class="mv">{det['language']}</div></div>
      <div class="msep"></div>
      <div><div class="mk">Genre</div><div class="mv" style="font-size:0.95rem;">{gi}</div></div>
      <div class="msep"></div>
      <div><div class="mk">Status</div><div class="mv" style="font-size:0.9rem;">{det['status']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    lc, rc = st.columns([1, 2.4], gap="large")

    with lc:
        if det["poster"]:
            st.image(det["poster"], use_container_width=True)
        if det["budget"] or det["revenue"]:
            st.markdown(f"""
            <div class="fin">
              <div class="fc"><div class="fk">Budget</div><div class="fv">{money(det['budget'])}</div></div>
              <div class="fc"><div class="fk">Box Office</div><div class="fv">{money(det['revenue'])}</div></div>
            </div>""", unsafe_allow_html=True)
        if det["imdb_id"]:
            st.markdown(
                f'<a class="exa" href="https://www.imdb.com/title/{det["imdb_id"]}" target="_blank">&#9733; View on IMDb</a>',
                unsafe_allow_html=True,
            )
        if det["homepage"]:
            st.markdown(
                f'<a class="exa" href="{det["homepage"]}" target="_blank">&#8594; Official Site</a>',
                unsafe_allow_html=True,
            )

    with rc:
        if det["genres"]:
            st.markdown('<div class="ds">Genres</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="gp">{g}</span>' for g in det["genres"]), unsafe_allow_html=True)

        st.markdown('<div class="ds">Synopsis</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="ov">{det["overview"]}</p>', unsafe_allow_html=True)

        if det["directors"]:
            st.markdown('<div class="ds">Direction</div>', unsafe_allow_html=True)
            for name in det["directors"]:
                st.markdown(
                    f'<div class="pr"><span class="pdot"></span><span class="pn">{name}</span><span class="po">Director</span></div>',
                    unsafe_allow_html=True,
                )

        if det["writers"]:
            st.markdown('<div class="ds">Screenplay</div>', unsafe_allow_html=True)
            for name in det["writers"]:
                st.markdown(
                    f'<div class="pr"><span class="pdot"></span><span class="pn">{name}</span><span class="po">Writer</span></div>',
                    unsafe_allow_html=True,
                )

        if det["cast"]:
            st.markdown('<div class="ds">Cast</div>', unsafe_allow_html=True)
            cc = st.columns(4)
            for i, (name, char) in enumerate(det["cast"]):
                with cc[i % 4]:
                    st.markdown(
                        f'<div class="cc"><div class="ccn">{name}</div><div class="ccc">{char or "—"}</div></div>',
                        unsafe_allow_html=True,
                    )

        if det["trailer"]:
            st.markdown('<div class="ds">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={det['trailer']}")

    st.stop()


# ================================================================
# HOME PAGE
# ================================================================

def render_movie_card(col, r, i):
    with col:
        if r.get("poster"):
            st.image(r["poster"], use_container_width=True)
        else:
            st.markdown(
                f'<div class="poster-placeholder"><span>{r["title"]}</span></div>',
                unsafe_allow_html=True,
            )
        if st.button(r["title"], key=f"r{i}", use_container_width=True):
            open_movie_detail(r["id"])


# Header
st.markdown("""
<div class="hdr">
  <div>
    <div class="brand">Cine<em>Mind</em></div>
    <div class="brand-tag">Find your next film</div>
  </div>
  <div class="hdr-right">Film &nbsp;&middot;&nbsp; Discover &nbsp;&middot;&nbsp; Curated</div>
</div>
""", unsafe_allow_html=True)

# Search row
st.markdown('<div class="slabel">Select a film you enjoy</div>', unsafe_allow_html=True)
sc1, sc2 = st.columns([5, 1], gap="small")
with sc1:
    titles_list = list(movies["title"].values)
    sel_idx = titles_list.index(st.session_state.src) if st.session_state.src in titles_list else 0
    chosen = st.selectbox("film", movies["title"].values, index=sel_idx, label_visibility="collapsed")
with sc2:
    go = st.button("Discover", use_container_width=True)

if go:
    with st.spinner("Curating…"):
        st.session_state.recs = recommend(chosen, n=5)
        st.session_state.src  = chosen
        st.query_params["src"] = chosen
        st.query_params.pop("movie", None)

# Results grid
if st.session_state.recs:
    st.markdown(f"""
    <div class="rlabel">
      <span>Because you watched</span>
      <strong>{st.session_state.src}</strong>
      <div class="rline"></div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(5, gap="small")
    for i, rec in enumerate(st.session_state.recs[:5]):
        render_movie_card(cols[i], rec, i)

else:
    st.markdown("""
    <div class="empty">
      <div class="empty-h">Select a film and click Discover</div>
      <div class="empty-p">You'll get 5 personalised recommendations.<br>Click any poster to see cast, crew, rating &amp; trailer.</div>
      <div class="slabel" style="margin-top:1.2rem;text-align:center;letter-spacing:2.5px;">Or try one of these</div>
    </div>
    """, unsafe_allow_html=True)

    t_cols = st.columns(len(TRY_MOVIES), gap="small")
    for idx, p in enumerate(TRY_MOVIES):
        m_row = movies[movies["title"] == p]
        if not m_row.empty:
            mid_val = int(m_row["movie_id"].values[0])
            with t_cols[idx]:
                if st.button(p, key=f"try_{idx}", use_container_width=True):
                    open_movie_detail(mid_val)
