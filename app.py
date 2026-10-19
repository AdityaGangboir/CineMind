import os
import gdown
import requests
import streamlit as st
import pickle
import pandas as pd

st.set_page_config(page_title="CineMind", page_icon="C", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:      #faf7f2;
  --white:   #ffffff;
  --s2:      #f5f1ea;
  --s3:      #ede8df;
  --bd:      #e4ddd3;
  --bd2:     #d5ccc0;
  --th:      #1c1712;
  --tb:      #3d3529;
  --tm:      #6b6054;
  --tl:      #9c9085;
  --txl:     #c0b8ae;
}

html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg) !important;
  color: var(--tb);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 0 2.5rem 2rem !important;
  max-width: 1380px !important;
  margin-top: -4rem !important;
}
* { box-sizing: border-box; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--s2); }
::-webkit-scrollbar-thumb { background: var(--bd2); border-radius: 4px; }

/* ── TOP HEADER BAR ── */
.header-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 1.8rem 0 1.2rem;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 1.2rem;
}
.brand-block {}
.brand-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.8rem;
  font-weight: 600;
  color: var(--th);
  letter-spacing: -0.5px;
  line-height: 1;
}
.brand-name em {
  font-style: italic;
  font-weight: 300;
  color: var(--tm);
}
.brand-sub {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-style: italic;
  font-weight: 300;
  color: var(--tl);
  margin-top: 1px;
  letter-spacing: 0.2px;
}
.header-right {
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--tl);
  padding-bottom: 4px;
}

/* ── SEARCH ROW ── */
.search-label {
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 2.8px;
  text-transform: uppercase;
  color: var(--tl);
  margin-bottom: 0.5rem;
}

/* ── STREAMLIT WIDGETS ── */
.stSelectbox label { display: none !important; }
.stSelectbox > div > div,
div[data-baseweb="select"] > div {
  background: var(--white) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 3px !important;
  color: var(--tb) !important;
  font-size: 0.9rem !important;
  box-shadow: none !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* PRIMARY BUTTON — DISCOVER */
.stButton > button {
  background: var(--th) !important;
  color: var(--bg) !important;
  border: 1px solid var(--th) !important;
  border-radius: 3px !important;
  padding: 0.62rem 1.4rem !important;
  font-weight: 500 !important;
  font-size: 0.75rem !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
  transition: background 0.18s ease !important;
  width: 100% !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover {
  background: var(--tm) !important;
  border-color: var(--tm) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* CARD TITLE BUTTON — inside columns */
div[data-testid="column"] .stButton > button {
  background: var(--white) !important;
  color: var(--th) !important;
  border: 1px solid var(--bd) !important;
  border-top: none !important;
  border-radius: 0 0 3px 3px !important;
  font-size: 0.74rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.2px !important;
  text-transform: none !important;
  padding: 0.45rem 0.4rem 0.5rem !important;
  line-height: 1.3 !important;
  white-space: normal !important;
  min-height: 2.4rem !important;
  height: auto !important;
}
div[data-testid="column"] .stButton > button:hover {
  background: var(--s3) !important;
  color: var(--th) !important;
  border-color: var(--bd2) !important;
}

/* ── BECAUSE LABEL ── */
.because {
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--tl);
  margin: 1rem 0 0.8rem;
  display: flex;
  align-items: center;
  gap: 10px;
}
.because strong { color: var(--th); font-weight: 600; letter-spacing: 1px; }
.because-line { flex: 1; height: 1px; background: var(--bd); }

/* ── FILM POSTER CARD ── */
div[data-testid="column"] div[data-testid="stImage"] img {
  border: 1px solid var(--bd);
  border-bottom: none;
  border-radius: 3px 3px 0 0;
  display: block;
  width: 100%;
}

/* ── EMPTY STATE ── */
.empty {
  text-align: center;
  padding: 3.5rem 2rem;
  border: 1px dashed var(--bd);
  border-radius: 3px;
  margin-top: 1rem;
}
.empty-h {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  font-weight: 400;
  color: var(--tm);
  margin-bottom: 0.4rem;
}
.empty-p { font-size: 0.82rem; color: var(--tl); line-height: 1.7; }

/* ================================================================
   DETAIL PAGE
   ================================================================ */

/* DETAIL NAV */
.det-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 0 1rem;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 0;
}
.det-brand {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.9rem;
  font-weight: 600;
  color: var(--th);
}
.det-brand em { font-style: italic; font-weight: 300; color: var(--tm); }
.det-crumb {
  font-size: 0.75rem;
  color: var(--tl);
  display: flex;
  align-items: center;
  gap: 7px;
}
.det-crumb-home { color: var(--tm); font-weight: 500; }
.det-crumb-sep { color: var(--txl); }
.det-crumb-cur { color: var(--th); font-weight: 500; max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* BACK BUTTON — override primary */
.back-wrap .stButton > button {
  background: transparent !important;
  color: var(--tm) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 3px !important;
  padding: 0.32rem 0.9rem !important;
  font-size: 0.75rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.4px !important;
  text-transform: none !important;
  width: auto !important;
}
.back-wrap .stButton > button:hover {
  background: var(--s2) !important;
  color: var(--th) !important;
  border-color: var(--bd2) !important;
}

/* BACKDROP */
.det-hero {
  position: relative;
  height: 320px;
  overflow: hidden;
  background: var(--s3);
}
.det-hero img.bk {
  position: absolute;
  inset: 0; width: 100%; height: 100%;
  object-fit: cover;
  filter: grayscale(25%) brightness(0.6) sepia(12%);
}
.det-hero-grad {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 20%, rgba(250,247,242,0.55) 65%, rgba(250,247,242,1) 100%);
}
.det-hero-txt {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 0 2rem 1.6rem;
}
.det-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.8rem;
  font-weight: 500;
  color: #fff;
  line-height: 1.1;
  text-shadow: 0 1px 14px rgba(0,0,0,0.3);
}
.det-tagline {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-style: italic;
  color: rgba(255,255,255,0.72);
  margin-top: 3px;
}

/* Fallback title */
.det-title-fb {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem;
  font-weight: 500;
  color: var(--th);
  padding-top: 1.2rem;
  margin-bottom: 0.3rem;
  line-height: 1.1;
}
.det-tag-fb {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  font-style: italic;
  color: var(--tm);
  margin-bottom: 1rem;
}

/* META STRIP */
.meta-strip {
  display: flex;
  gap: 1.4rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--bd);
  margin-bottom: 1.4rem;
}
.m-sep { width: 1px; height: 26px; background: var(--bd); }
.m-key {
  font-size: 0.58rem;
  font-weight: 500;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  color: var(--tl);
  margin-bottom: 2px;
}
.m-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem;
  font-weight: 500;
  color: var(--th);
  line-height: 1;
}
.r-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.85rem;
  font-weight: 600;
  color: var(--th);
  line-height: 1;
}
.r-den { font-size: 0.82rem; color: var(--tl); margin-left: 2px; }
.r-cnt { font-size: 0.65rem; color: var(--tl); margin-top: 2px; }
.stars { font-size: 0.8rem; color: var(--txl); letter-spacing: 2px; }
.stars .on { color: var(--tb); }

/* SECTION LABEL */
.dsec {
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 2.8px;
  text-transform: uppercase;
  color: var(--tl);
  padding-bottom: 7px;
  border-bottom: 1px solid var(--bd);
  margin: 1.8rem 0 0.8rem;
}

/* OVERVIEW */
.overview {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.08rem;
  color: var(--tb);
  line-height: 1.8;
}

/* GENRE PILL */
.gpill {
  display: inline-block;
  background: var(--s2);
  border: 1px solid var(--bd);
  border-radius: 2px;
  padding: 3px 11px;
  font-size: 0.73rem;
  color: var(--tm);
  margin: 2px;
}

/* PERSON ROW */
.prow {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 0;
  border-bottom: 1px solid var(--bd);
}
.prow:last-child { border-bottom: none; }
.pdot { width: 5px; height: 5px; border-radius: 50%; background: var(--bd2); flex-shrink: 0; }
.pname { font-size: 0.85rem; font-weight: 500; color: var(--th); }
.prole { font-size: 0.72rem; color: var(--tl); margin-left: auto; }

/* CAST CARD */
.cc {
  background: var(--white);
  border: 1px solid var(--bd);
  border-radius: 3px;
  padding: 11px 8px;
  text-align: center;
  margin-bottom: 8px;
}
.cc-n { font-size: 0.78rem; font-weight: 500; color: var(--th); margin-bottom: 2px; }
.cc-c { font-family: 'Cormorant Garamond', serif; font-size: 0.8rem; color: var(--tl); font-style: italic; }

/* POSTER */
div[data-testid="stImage"] img {
  border: 1px solid var(--bd);
  box-shadow: 3px 6px 24px rgba(28,23,18,0.09);
}

/* FINANCE */
.fin {
  display: flex;
  border: 1px solid var(--bd);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 10px;
}
.fin-c { flex: 1; padding: 11px; text-align: center; background: var(--white); }
.fin-c + .fin-c { border-left: 1px solid var(--bd); }
.fin-k { font-size: 0.58rem; font-weight: 500; letter-spacing: 2px; text-transform: uppercase; color: var(--tl); margin-bottom: 3px; }
.fin-v { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 500; color: var(--th); }

/* EXT LINK */
.exa {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  text-decoration: none;
  border: 1px solid var(--bd);
  border-radius: 3px;
  padding: 9px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--tm);
  background: var(--white);
  margin-top: 7px;
  transition: all 0.15s;
  letter-spacing: 0.4px;
}
.exa:hover { background: var(--th); color: var(--bg); border-color: var(--th); }

div[data-testid="stVideo"] { border: 1px solid var(--bd); border-radius: 3px; overflow: hidden; }
.stSpinner > div { border-top-color: var(--tm) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# === Data ===
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


def recommend(title):
    idx = movies[movies["title"] == title].index[0]
    top = sorted(enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])[1:6]
    return [{"title": movies.iloc[i].title, "id": movies.iloc[i].movie_id, "poster": fetch_poster(movies.iloc[i].movie_id)} for i,_ in top]


def money(v):
    if not v or v == 0: return "—"
    if v >= 1e9: return f"${v/1e9:.2f}B"
    if v >= 1e6: return f"${v/1e6:.1f}M"
    return f"${v:,}"


def stars_html(s):
    f = round(s / 2)
    return "".join(['<span class="on">\u2605</span>' if i < f else '\u2605' for i in range(5)])


# Session state
for k, v in [("page","home"),("mid",None),("recs",[]),("src",None),("history",[]),("det_title","")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ================================================================
# DETAIL PAGE
# ================================================================
if st.session_state.page == "detail":

    # Nav bar
    nb_l, nb_c, nb_r = st.columns([2, 3, 1], gap="small")
    with nb_l:
        st.markdown('<div class="det-nav"><div class="det-brand">Cine<em>Mind</em></div></div>', unsafe_allow_html=True)
    with nb_c:
        cur = st.session_state.get("det_title", "Film")
        st.markdown(f"""
        <div style="padding:1.3rem 0 1rem;">
          <div class="det-crumb">
            <span class="det-crumb-home">Home</span>
            <span class="det-crumb-sep">&#8250;</span>
            <span class="det-crumb-cur" title="{cur}">{cur}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with nb_r:
        st.markdown('<div class="back-wrap" style="padding-top:1rem;">', unsafe_allow_html=True)
        if st.button("\u2190 Back", key="back_btn"):
            if st.session_state.history:
                prev = st.session_state.history.pop()
                st.session_state.mid = prev["id"]
                st.session_state.det_title = prev["title"]
            else:
                st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin:0 0 0 0;border:none;border-top:1px solid var(--bd);">', unsafe_allow_html=True)

    with st.spinner("Loading..."):
        det = fetch_details(st.session_state.mid)

    if not det:
        st.error("Could not load film details.")
        st.stop()

    # Backdrop
    if det["backdrop"]:
        st.markdown(f"""
        <div class="det-hero">
          <img class="bk" src="{det['backdrop']}" />
          <div class="det-hero-grad"></div>
          <div class="det-hero-txt">
            <div class="det-title">{det['title']}</div>
            <div class="det-tagline">{det['tagline']}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="det-title-fb">{det["title"]}</div><div class="det-tag-fb">{det["tagline"]}</div>', unsafe_allow_html=True)

    # Meta strip
    year = det["release"][:4] if det["release"] else "—"
    rh = det["runtime"] // 60 if det["runtime"] else 0
    rm = det["runtime"] % 60  if det["runtime"] else 0
    rt = f"{rh}h {rm}m" if det["runtime"] else "—"
    gi = " / ".join(det["genres"][:3]) if det["genres"] else ""

    st.markdown(f"""
    <div class="meta-strip">
      <div>
        <div class="m-key">Score</div>
        <div style="display:flex;align-items:baseline;gap:3px;">
          <span class="r-num">{det['rating']}</span><span class="r-den">/10</span>
        </div>
        <div class="stars">{stars_html(det['rating'])}</div>
        <div class="r-cnt">{det['votes']:,} ratings</div>
      </div>
      <div class="m-sep"></div>
      <div><div class="m-key">Year</div><div class="m-val">{year}</div></div>
      <div class="m-sep"></div>
      <div><div class="m-key">Runtime</div><div class="m-val">{rt}</div></div>
      <div class="m-sep"></div>
      <div><div class="m-key">Language</div><div class="m-val">{det['language']}</div></div>
      <div class="m-sep"></div>
      <div><div class="m-key">Genre</div><div class="m-val" style="font-size:1rem;">{gi}</div></div>
      <div class="m-sep"></div>
      <div><div class="m-key">Status</div><div class="m-val" style="font-size:0.95rem;">{det['status']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    lc, rc = st.columns([1, 2.4], gap="large")

    with lc:
        if det["poster"]:
            st.image(det["poster"], use_container_width=True)
        if det["budget"] or det["revenue"]:
            st.markdown(f"""
            <div class="fin">
              <div class="fin-c"><div class="fin-k">Budget</div><div class="fin-v">{money(det['budget'])}</div></div>
              <div class="fin-c"><div class="fin-k">Box Office</div><div class="fin-v">{money(det['revenue'])}</div></div>
            </div>""", unsafe_allow_html=True)
        if det["imdb_id"]:
            st.markdown(f'<a class="exa" href="https://www.imdb.com/title/{det["imdb_id"]}" target="_blank">&#9733; View on IMDb</a>', unsafe_allow_html=True)
        if det["homepage"]:
            st.markdown(f'<a class="exa" href="{det["homepage"]}" target="_blank">&#8594; Official Site</a>', unsafe_allow_html=True)

    with rc:
        if det["genres"]:
            st.markdown('<div class="dsec">Genres</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="gpill">{g}</span>' for g in det["genres"]), unsafe_allow_html=True)

        st.markdown('<div class="dsec">Synopsis</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="overview">{det["overview"]}</p>', unsafe_allow_html=True)

        if det["directors"]:
            st.markdown('<div class="dsec">Direction</div>', unsafe_allow_html=True)
            for n in det["directors"]:
                st.markdown(f'<div class="prow"><span class="pdot"></span><span class="pname">{n}</span><span class="prole">Director</span></div>', unsafe_allow_html=True)

        if det["writers"]:
            st.markdown('<div class="dsec">Screenplay</div>', unsafe_allow_html=True)
            for n in det["writers"]:
                st.markdown(f'<div class="prow"><span class="pdot"></span><span class="pname">{n}</span><span class="prole">Writer</span></div>', unsafe_allow_html=True)

        if det["cast"]:
            st.markdown('<div class="dsec">Cast</div>', unsafe_allow_html=True)
            cc = st.columns(4)
            for i, (name, char) in enumerate(det["cast"]):
                with cc[i % 4]:
                    st.markdown(f'<div class="cc"><div class="cc-n">{name}</div><div class="cc-c">{char or "—"}</div></div>', unsafe_allow_html=True)

        if det["trailer"]:
            st.markdown('<div class="dsec">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={det['trailer']}")

    st.stop()


# ================================================================
# HOME PAGE
# ================================================================

# Combined header: big brand + tagline + nav right
st.markdown("""
<div class="header-bar">
  <div class="brand-block">
    <div class="brand-name">Cine<em>Mind</em></div>
    <div class="brand-sub">Find your next film</div>
  </div>
  <div class="header-right">Film &nbsp;&middot;&nbsp; Discover &nbsp;&middot;&nbsp; Curated</div>
</div>
""", unsafe_allow_html=True)

# Search row — inline, no card wrapper
st.markdown('<div class="search-label">Select a film you enjoy</div>', unsafe_allow_html=True)
sc1, sc2 = st.columns([5, 1], gap="small")
with sc1:
    chosen = st.selectbox("film", movies["title"].values, label_visibility="collapsed")
with sc2:
    go = st.button("Discover", use_container_width=True)

if go:
    with st.spinner("Curating..."):
        st.session_state.recs = recommend(chosen)
        st.session_state.src  = chosen

# Results
if st.session_state.recs:
    st.markdown(f"""
    <div class="because">
      <span>Because you watched</span>
      <strong>{st.session_state.src}</strong>
      <div class="because-line"></div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(5, gap="small")
    for i, col in enumerate(cols):
        r = st.session_state.recs[i]
        with col:
            if r["poster"]:
                st.image(r["poster"], use_container_width=True)
            if st.button(r["title"], key=f"r{i}", use_container_width=True):
                st.session_state.history   = []
                st.session_state.mid       = r["id"]
                st.session_state.det_title = r["title"]
                st.session_state.page      = "detail"
                st.rerun()
else:
    st.markdown("""
    <div class="empty">
      <div class="empty-h">Select a film above and click Discover</div>
      <div class="empty-p">Click any recommended film poster to explore full details — cast, crew, rating &amp; trailer.</div>
    </div>""", unsafe_allow_html=True)