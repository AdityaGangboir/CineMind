import os
import gdown
import requests
import streamlit as st
import pickle
import pandas as pd
import random
import urllib.parse

st.set_page_config(page_title="CineMind", page_icon="C", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:   #faf7f2;
  --wh:   #ffffff;
  --s2:   #f5f1ea;
  --s3:   #ede8df;
  --bd:   #e4ddd3;
  --bd2:  #d5ccc0;
  --th:   #1c1712;
  --tb:   #3d3529;
  --tm:   #6b6054;
  --tl:   #9c9085;
  --txl:  #c0b8ae;
}

html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg) !important;
  color: var(--tb);
}
#MainMenu, footer, header { visibility: hidden; }

/* Kill Streamlit's default top padding without going negative */
.stApp > div:first-child { padding-top: 0 !important; }
.block-container {
  padding: 1.4rem 2.8rem 2rem !important;
  max-width: 1400px !important;
}

* { box-sizing: border-box; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--s2); }
::-webkit-scrollbar-thumb { background: var(--bd2); border-radius: 4px; }

/* ── HOME HEADER ── */
.hdr {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 1rem;
}
.brand {
  font-family: 'Cormorant Garamond', serif;
  font-size: 4rem;
  font-weight: 600;
  color: var(--th);
  letter-spacing: -1px;
  line-height: 1;
}
.brand em { font-style: italic; font-weight: 300; color: var(--tm); }
.brand-tag {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-style: italic;
  font-weight: 300;
  color: var(--tl);
  margin-top: 3px;
  letter-spacing: 0.3px;
}
.hdr-right {
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  color: var(--tl);
  padding-bottom: 6px;
}

/* ── SEARCH ROW ── */
.slabel {
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 2.8px;
  text-transform: uppercase;
  color: var(--tl);
  margin-bottom: 0.45rem;
}

/* ── WIDGETS ── */
.stSelectbox label { display: none !important; }
.stSelectbox > div > div,
div[data-baseweb="select"] > div {
  background: var(--wh) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 2px !important;
  color: var(--tb) !important;
  font-size: 0.9rem !important;
  box-shadow: none !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* PRIMARY BUTTON */
.stButton > button {
  background: var(--th) !important;
  color: var(--bg) !important;
  border: 1px solid var(--th) !important;
  border-radius: 2px !important;
  padding: 0.62rem 1.2rem !important;
  font-weight: 500 !important;
  font-size: 0.72rem !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
  transition: background 0.15s !important;
  width: 100% !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover {
  background: var(--tm) !important;
  border-color: var(--tm) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* CARD TITLE BUTTON */
div[data-testid="column"] .stButton > button {
  background: var(--wh) !important;
  color: var(--th) !important;
  border: 1px solid var(--bd) !important;
  border-top: none !important;
  border-radius: 0 0 2px 2px !important;
  font-size: 0.72rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.1px !important;
  text-transform: none !important;
  padding: 0.4rem 0.35rem 0.45rem !important;
  line-height: 1.3 !important;
  white-space: normal !important;
  min-height: 2.2rem !important;
  height: auto !important;
}
div[data-testid="column"] .stButton > button:hover {
  background: var(--s3) !important;
  color: var(--th) !important;
  border-color: var(--bd2) !important;
}

/* ── RESULTS LABEL ── */
.rlabel {
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--tl);
  margin: 0.8rem 0 0.6rem;
  display: flex;
  align-items: center;
  gap: 10px;
}
.rlabel strong { color: var(--th); font-weight: 600; letter-spacing: 1px; }
.rline { flex: 1; height: 1px; background: var(--bd); }

/* ── POSTER LINK & IMAGE IN CARD ── */
div[data-testid="column"] .stMarkdown:has(.poster-link) {
  margin-bottom: 0 !important;
}
div[data-testid="column"] .stMarkdown:has(.poster-link) p {
  margin: 0 !important;
  line-height: 0 !important;
}
.poster-link {
  display: block;
  text-decoration: none;
  cursor: pointer;
  line-height: 0;
  margin-bottom: 0 !important;
  border-radius: 2px 2px 0 0;
  overflow: hidden;
}
.poster-img {
  border: 1px solid var(--bd);
  border-bottom: none;
  border-radius: 2px 2px 0 0;
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  display: block;
  transition: opacity 0.15s ease, filter 0.15s ease;
}
.poster-link:hover .poster-img {
  opacity: 0.88;
  filter: brightness(0.96);
}
.poster-placeholder {
  border: 1px solid var(--bd);
  border-bottom: none;
  border-radius: 2px 2px 0 0;
  width: 100%;
  aspect-ratio: 2 / 3;
  background: var(--s2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem;
  text-align: center;
  font-family: 'Cormorant Garamond', serif;
  font-size: 0.95rem;
  color: var(--tm);
  line-height: 1.3;
}
div[data-testid="column"] div[data-testid="stImage"] img {
  border: 1px solid var(--bd);
  border-bottom: none;
  border-radius: 2px 2px 0 0;
  width: 100%;
  display: block;
}

/* ── EMPTY STATE ── */
.empty {
  text-align: center;
  padding: 3rem 2rem;
  border: 1px dashed var(--bd);
  border-radius: 2px;
  margin-top: 0.8rem;
}
.empty-h {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem;
  color: var(--tm);
  margin-bottom: 0.35rem;
}
.empty-p { font-size: 0.8rem; color: var(--tl); line-height: 1.7; }

/* ── SUGGESTION ROW ── */
.sug-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--tl);
  flex-wrap: wrap;
}
.sug-pill {
  display: inline-block;
  background: var(--s2);
  border: 1px solid var(--bd);
  border-radius: 2px;
  padding: 4px 11px;
  font-size: 0.73rem;
  color: var(--tm);
  cursor: pointer;
  letter-spacing: 0.2px;
  text-decoration: none !important;
  transition: all 0.15s ease;
  line-height: 1.4;
}
.sug-pill:hover {
  background: var(--s3);
  color: var(--th);
  border-color: var(--bd2);
  transform: translateY(-1px);
}

/* ==================================================
   DETAIL PAGE
   ================================================== */

/* DETAIL NAVBAR */
.dbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 0 0.8rem;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 0;
}
.d-brand {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 600;
  color: var(--th);
  line-height: 1;
}
.d-brand em { font-style: italic; font-weight: 300; color: var(--tm); }
.d-crumb {
  font-size: 0.72rem;
  color: var(--tl);
  display: flex;
  align-items: center;
  gap: 6px;
}
.d-ch { color: var(--tm); font-weight: 500; }
.d-cs { color: var(--txl); }
.d-cc { color: var(--th); font-weight: 500; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* BACK BUTTON override */
.bwrap .stButton > button {
  background: transparent !important;
  color: var(--tm) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 2px !important;
  padding: 0.3rem 0.85rem !important;
  font-size: 0.72rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.3px !important;
  text-transform: none !important;
  width: auto !important;
}
.bwrap .stButton > button:hover {
  background: var(--s2) !important;
  color: var(--th) !important;
  border-color: var(--bd2) !important;
}

/* BACKDROP */
.dhero {
  position: relative;
  height: 300px;
  overflow: hidden;
  background: var(--s3);
}
.dhero img.bk {
  position: absolute;
  inset: 0; width: 100%; height: 100%;
  object-fit: cover;
  filter: grayscale(20%) brightness(0.58) sepia(10%);
}
.dhero-g {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 15%, rgba(250,247,242,0.5) 60%, rgba(250,247,242,1) 100%);
}
.dhero-t {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 0 2rem 1.4rem;
}
.dtitle { font-family: 'Cormorant Garamond', serif; font-size: 2.6rem; font-weight: 500; color: #fff; line-height: 1.1; text-shadow: 0 1px 12px rgba(0,0,0,0.28); }
.dtagl  { font-family: 'Cormorant Garamond', serif; font-size: 0.95rem; font-style: italic; color: rgba(255,255,255,0.7); margin-top: 2px; }

/* fallback */
.dtfb { font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 500; color: var(--th); padding-top: 1rem; margin-bottom: 0.25rem; line-height: 1.1; }
.dtgfb { font-family: 'Cormorant Garamond', serif; font-size: 0.95rem; font-style: italic; color: var(--tm); margin-bottom: 0.8rem; }

/* META STRIP */
.mstrip {
  display: flex;
  gap: 1.2rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 1.2rem;
}
.msep { width: 1px; height: 24px; background: var(--bd); }
.mk { font-size: 0.55rem; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; color: var(--tl); margin-bottom: 2px; }
.mv { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 500; color: var(--th); line-height: 1; }
.rn { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 600; color: var(--th); line-height: 1; }
.rd { font-size: 0.78rem; color: var(--tl); margin-left: 2px; }
.rc { font-size: 0.62rem; color: var(--tl); margin-top: 2px; }
.st { font-size: 0.75rem; color: var(--txl); letter-spacing: 2px; }
.st .on { color: var(--tb); }

/* SECTION LABEL */
.ds { font-size: 0.58rem; font-weight: 500; letter-spacing: 2.8px; text-transform: uppercase; color: var(--tl); padding-bottom: 6px; border-bottom: 1px solid var(--bd); margin: 1.5rem 0 0.7rem; }

/* OVERVIEW */
.ov { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; color: var(--tb); line-height: 1.8; }

/* GENRE PILL */
.gp { display: inline-block; background: var(--s2); border: 1px solid var(--bd); border-radius: 2px; padding: 3px 10px; font-size: 0.71rem; color: var(--tm); margin: 2px; }

/* PERSON ROW */
.pr { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--bd); }
.pr:last-child { border-bottom: none; }
.pdot { width: 5px; height: 5px; border-radius: 50%; background: var(--bd2); flex-shrink: 0; }
.pn { font-size: 0.83rem; font-weight: 500; color: var(--th); }
.po { font-size: 0.7rem; color: var(--tl); margin-left: auto; }

/* CAST CARD */
.cc { background: var(--wh); border: 1px solid var(--bd); border-radius: 2px; padding: 10px 7px; text-align: center; margin-bottom: 7px; }
.ccn { font-size: 0.76rem; font-weight: 500; color: var(--th); margin-bottom: 2px; }
.ccc { font-family: 'Cormorant Garamond', serif; font-size: 0.78rem; color: var(--tl); font-style: italic; }

/* POSTER (detail) */
div[data-testid="stImage"] img { border: 1px solid var(--bd); box-shadow: 3px 6px 20px rgba(28,23,18,0.08); }

/* FINANCE */
.fin { display: flex; border: 1px solid var(--bd); border-radius: 2px; overflow: hidden; margin-top: 9px; }
.fc { flex: 1; padding: 10px; text-align: center; background: var(--wh); }
.fc + .fc { border-left: 1px solid var(--bd); }
.fk { font-size: 0.55rem; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; color: var(--tl); margin-bottom: 3px; }
.fv { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; font-weight: 500; color: var(--th); }

/* EXT LINK */
.exa { display: flex; align-items: center; justify-content: center; gap: 5px; text-decoration: none; border: 1px solid var(--bd); border-radius: 2px; padding: 8px; font-size: 0.73rem; font-weight: 500; color: var(--tm); background: var(--wh); margin-top: 6px; transition: all 0.14s; }
.exa:hover { background: var(--th); color: var(--bg); border-color: var(--th); }

div[data-testid="stVideo"] { border: 1px solid var(--bd); border-radius: 2px; overflow: hidden; }
.stSpinner > div { border-top-color: var(--tm) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Data ──
movies_dict_url = "https://drive.google.com/uc?id=1CishRUVNw4h--ffoIblUfpg-p1F5m57c"
similarity_url  = "https://drive.google.com/uc?id=1tH8Z4HkjoOI5n8n3ixO1L7ylAofLB5UD"

if not os.path.exists("movies_dict.pkl"):
    gdown.download(movies_dict_url, "movies_dict.pkl", quiet=False)
if not os.path.exists("similarity.pkl"):
    gdown.download(similarity_url, "similarity.pkl", quiet=False)

movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies      = pd.DataFrame(movies_dict)
similarity  = pickle.load(open("similarity.pkl", "rb"))

TMDB_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# Popular seed suggestions shown on empty state (verified present in dataset)
SEEDS = [
    "Inception", "The Dark Knight", "Avatar", "The Avengers",
    "Interstellar", "Fight Club", "The Matrix", "Pulp Fiction",
    "The Shawshank Redemption", "Forrest Gump", "The Godfather", "Titanic"
]


def fetch_poster(movie_id):
    try:
        r = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}", timeout=7).json()
        p = r.get("poster_path")
        return f"https://image.tmdb.org/t/p/w500/{p}" if p else ""
    except Exception:
        return ""


def fetch_details(movie_id):
    try:
        d   = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US", timeout=8).json()
        cr  = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_KEY}&language=en-US", timeout=8).json()
        vid = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_KEY}&language=en-US", timeout=8).json()
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
            "writers":   list(dict.fromkeys([m["name"] for m in crew if m.get("job") in ("Screenplay","Writer","Story")]))[:4],
            "cast":      [(m["name"], m.get("character","")) for m in cr.get("cast",[])[:8]],
            "poster":    f"https://image.tmdb.org/t/p/w500/{d['poster_path']}" if d.get("poster_path") else "",
            "backdrop":  f"https://image.tmdb.org/t/p/w1280/{d['backdrop_path']}" if d.get("backdrop_path") else "",
            "trailer":   next((v["key"] for v in vid.get("results",[]) if v.get("site")=="YouTube" and v.get("type")=="Trailer"), None),
            "imdb_id":   d.get("imdb_id",""),
            "homepage":  d.get("homepage",""),
        }
    except Exception:
        return None


def recommend(title, n=10):
    idx = movies[movies["title"] == title].index[0]
    top = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])[1:n+1]
    return [{"title": movies.iloc[i].title, "id": movies.iloc[i].movie_id,
             "poster": fetch_poster(movies.iloc[i].movie_id)} for i, _ in top]


def money(v):
    if not v or v == 0: return "—"
    if v >= 1e9: return f"${v/1e9:.2f}B"
    if v >= 1e6: return f"${v/1e6:.1f}M"
    return f"${v:,}"


def stars_html(s):
    f = round(s / 2)
    return "".join(['<span class="on">\u2605</span>' if i < f else '\u2605' for i in range(5)])


# Session state initialization
for k, v in [("page","home"),("mid",None),("recs",[]),("src",None),("history",[]),("det_title","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# Synchronize with URL query parameters for browser navigation (Back / Forward buttons & deep linking)
url_movie = st.query_params.get("movie") or st.query_params.get("id")
url_src   = st.query_params.get("src")

if url_movie:
    try:
        current_mid = int(url_movie)
        st.session_state.mid = current_mid
        st.session_state.page = "detail"
        match = movies[movies["movie_id"] == current_mid]
        if not match.empty:
            st.session_state.det_title = match["title"].values[0]
    except (ValueError, TypeError):
        st.session_state.page = "home"
        st.session_state.mid = None
        if "movie" in st.query_params:
            del st.query_params["movie"]
else:
    st.session_state.page = "home"
    st.session_state.mid = None

if url_src and url_src in movies["title"].values:
    if st.session_state.src != url_src or not st.session_state.recs:
        st.session_state.src = url_src
        st.session_state.recs = recommend(url_src, n=10)
elif not url_src and not url_movie:
    # Navigated back to root: clear active recommendations to restore clean home state
    st.session_state.recs = []
    st.session_state.src = None


# ================================================================
# DETAIL PAGE
# ================================================================
if st.session_state.page == "detail":

    # Navbar: brand | breadcrumb | back button
    nl, nc, nr = st.columns([2, 4, 1], gap="small")
    home_query = f"?src={urllib.parse.quote(st.session_state.src)}" if st.session_state.src else "?"
    with nl:
        st.markdown(f'<div class="dbar"><a href="{home_query}" target="_self" style="text-decoration:none;color:inherit;"><div class="d-brand">Cine<em>Mind</em></div></a></div>', unsafe_allow_html=True)
    with nc:
        cur = st.session_state.get("det_title", "Film")
        st.markdown(f"""
        <div style="padding:0.95rem 0 0.75rem;">
          <div class="d-crumb">
            <a href="{home_query}" target="_self" class="d-ch" style="text-decoration:none;cursor:pointer;">Home</a>
            <span class="d-cs">&#8250;</span>
            <span class="d-cc" title="{cur}">{cur}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with nr:
        st.markdown('<div class="bwrap" style="padding-top:0.75rem;">', unsafe_allow_html=True)
        if st.button("\u2190 Back", key="back_btn"):
            if "movie" in st.query_params:
                del st.query_params["movie"]
            if "id" in st.query_params:
                del st.query_params["id"]
            if st.session_state.history:
                prev = st.session_state.history.pop()
                st.session_state.mid = prev["id"]
                st.session_state.det_title = prev["title"]
                st.query_params["movie"] = str(prev["id"])
            else:
                st.session_state.page = "home"
                st.session_state.mid = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin:0;border:none;border-top:1px solid var(--bd);">', unsafe_allow_html=True)

    with st.spinner("Loading..."):
        det = fetch_details(st.session_state.mid)

    if not det:
        st.error("Could not load film details.")
        if st.button("\u2190 Back to Home", key="error_back_btn"):
            if "movie" in st.query_params:
                del st.query_params["movie"]
            if "id" in st.query_params:
                del st.query_params["id"]
            st.session_state.page = "home"
            st.session_state.mid = None
            st.rerun()
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
        st.markdown(f'<div class="dtfb">{det["title"]}</div><div class="dtgfb">{det["tagline"]}</div>', unsafe_allow_html=True)

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
            st.markdown(f'<a class="exa" href="https://www.imdb.com/title/{det["imdb_id"]}" target="_blank">&#9733; View on IMDb</a>', unsafe_allow_html=True)
        if det["homepage"]:
            st.markdown(f'<a class="exa" href="{det["homepage"]}" target="_blank">&#8594; Official Site</a>', unsafe_allow_html=True)

    with rc:
        if det["genres"]:
            st.markdown('<div class="ds">Genres</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="gp">{g}</span>' for g in det["genres"]), unsafe_allow_html=True)

        st.markdown('<div class="ds">Synopsis</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="ov">{det["overview"]}</p>', unsafe_allow_html=True)

        if det["directors"]:
            st.markdown('<div class="ds">Direction</div>', unsafe_allow_html=True)
            for n in det["directors"]:
                st.markdown(f'<div class="pr"><span class="pdot"></span><span class="pn">{n}</span><span class="po">Director</span></div>', unsafe_allow_html=True)

        if det["writers"]:
            st.markdown('<div class="ds">Screenplay</div>', unsafe_allow_html=True)
            for n in det["writers"]:
                st.markdown(f'<div class="pr"><span class="pdot"></span><span class="pn">{n}</span><span class="po">Writer</span></div>', unsafe_allow_html=True)

        if det["cast"]:
            st.markdown('<div class="ds">Cast</div>', unsafe_allow_html=True)
            cc = st.columns(4)
            for i, (name, char) in enumerate(det["cast"]):
                with cc[i % 4]:
                    st.markdown(f'<div class="cc"><div class="ccn">{name}</div><div class="ccc">{char or "—"}</div></div>', unsafe_allow_html=True)

        if det["trailer"]:
            st.markdown('<div class="ds">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={det['trailer']}")

    st.stop()


# ================================================================
# HOME PAGE
# ================================================================

# Helper to render a movie card with clickable poster & title button
def render_movie_card(col, r, i):
    with col:
        src_str = f"&src={urllib.parse.quote(st.session_state.src)}" if st.session_state.src else ""
        safe_title = r["title"].replace('"', '&quot;')
        if r.get("poster"):
            poster_markup = f"""
            <a href="?movie={r['id']}{src_str}" target="_self" class="poster-link" title="{safe_title}"
               onclick="const col = this.closest('div[data-testid=\\'column\\']'); const btn = col ? col.querySelector('.stButton button') : null; if(btn){{ btn.click(); return false; }}">
              <img src="{r['poster']}" alt="{safe_title}" class="poster-img" />
            </a>"""
        else:
            poster_markup = f"""
            <a href="?movie={r['id']}{src_str}" target="_self" class="poster-link" title="{safe_title}"
               onclick="const col = this.closest('div[data-testid=\\'column\\']'); const btn = col ? col.querySelector('.stButton button') : null; if(btn){{ btn.click(); return false; }}">
              <div class="poster-placeholder"><span>{safe_title}</span></div>
            </a>"""
        st.markdown(poster_markup, unsafe_allow_html=True)

        if st.button(r["title"], key=f"r{i}", use_container_width=True):
            st.query_params["movie"] = str(r["id"])
            if st.session_state.src:
                st.query_params["src"] = st.session_state.src
            st.session_state.history   = []
            st.session_state.mid       = r["id"]
            st.session_state.det_title = r["title"]
            st.session_state.page      = "detail"
            st.rerun()


# Header — big brand, tagline, nav
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
    with st.spinner("Curating..."):
        st.session_state.recs = recommend(chosen, n=10)
        st.session_state.src  = chosen
        st.query_params["src"] = chosen
        if "movie" in st.query_params:
            del st.query_params["movie"]

# Results grid
if st.session_state.recs:
    st.markdown(f"""
    <div class="rlabel">
      <span>Because you watched</span>
      <strong>{st.session_state.src}</strong>
      <div class="rline"></div>
    </div>""", unsafe_allow_html=True)

    # First row — 5 films
    row1 = st.columns(5, gap="small")
    for i in range(min(5, len(st.session_state.recs))):
        render_movie_card(row1[i], st.session_state.recs[i], i)

    # Second row — next 5 films
    if len(st.session_state.recs) > 5:
        st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
        row2 = st.columns(5, gap="small")
        for i in range(5, min(10, len(st.session_state.recs))):
            render_movie_card(row2[i - 5], st.session_state.recs[i], i)
else:
    # Pick 4 random seeds guaranteed to be present in the database
    avail = [s for s in SEEDS if s in movies["title"].values]
    picks = random.sample(avail, min(4, len(avail))) if avail else []
    pills = []
    for p in picks:
        m_row = movies[movies["title"] == p]
        if not m_row.empty:
            mid_val = int(m_row["movie_id"].values[0])
            safe_p = p.replace('"', '&quot;')
            pills.append(f'<a href="?movie={mid_val}" target="_self" class="sug-pill" title="View details for {safe_p}">{p}</a>')
    pills_html = "".join(pills)

    st.markdown(f"""
    <div class="empty">
      <div class="empty-h">Select a film and click Discover</div>
      <div class="empty-p">You'll get 10 personalised recommendations. Click any to see cast, crew, rating &amp; trailer.</div>
      <div class="sug-row" style="justify-content:center;margin-top:1rem;">
        <span>Try:</span>{pills_html}
      </div>
    </div>""", unsafe_allow_html=True)