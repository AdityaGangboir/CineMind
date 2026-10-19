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

/* ── TOKENS ── */
:root {
  --bg:        #faf7f2;
  --surface:   #ffffff;
  --surface2:  #f5f1ea;
  --border:    #e8e1d5;
  --border2:   #d8cfc1;
  --text-h:    #1c1712;
  --text-b:    #3d3529;
  --text-m:    #6b6054;
  --text-l:    #9c9085;
  --text-xl:   #bdb4a8;
  --beige:     #e8e0d0;
  --beige2:    #f0ead8;
}

/* ── BASE ── */
html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text-b);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 0 3rem 4rem !important;
  max-width: 1320px !important;
}
* { box-sizing: border-box; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ── NAV BAR ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.4rem 0 1.2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}
.brand {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 600;
  color: var(--text-h);
  letter-spacing: 0.5px;
  text-decoration: none;
}
.brand em {
  font-style: italic;
  font-weight: 300;
  color: var(--text-m);
}
.nav-links {
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: var(--text-l);
}

/* ── BREADCRUMB ── */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--text-l);
  letter-spacing: 0.3px;
}
.breadcrumb a, .breadcrumb span { text-decoration: none; }
.breadcrumb .bc-home {
  color: var(--text-m);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s;
}
.breadcrumb .bc-home:hover { color: var(--text-h); }
.breadcrumb .bc-sep { color: var(--text-xl); font-size: 0.7rem; }
.breadcrumb .bc-cur { color: var(--text-h); font-weight: 500; max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ── BACK BUTTON (nav style — overrides primary) ── */
.nav-back-wrap > div > div > button,
.nav-back-wrap .stButton > button {
  background: transparent !important;
  color: var(--text-m) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  padding: 0.38rem 1rem !important;
  font-size: 0.78rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.5px !important;
  text-transform: none !important;
  width: auto !important;
  min-width: unset !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
}
.nav-back-wrap > div > div > button:hover,
.nav-back-wrap .stButton > button:hover {
  background: var(--surface2) !important;
  color: var(--text-h) !important;
  border-color: var(--border2) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── HERO ── */
.hero {
  padding: 5rem 0 3.5rem;
  text-align: center;
  border-bottom: 1px solid var(--border);
  margin-bottom: 3rem;
}
.hero-eyebrow {
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--text-l);
  margin-bottom: 1.2rem;
}
.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 5.2rem;
  font-weight: 300;
  color: var(--text-h);
  line-height: 1.05;
  letter-spacing: -2px;
  margin-bottom: 1.4rem;
}
.hero-title em {
  font-style: italic;
  font-weight: 300;
}
.hero-sub {
  font-size: 0.92rem;
  color: var(--text-m);
  font-weight: 400;
  max-width: 420px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ── SEARCH PANEL ── */
.search-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2.2rem 2.5rem 2rem;
  margin-bottom: 3rem;
}
.panel-label {
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--text-l);
  margin-bottom: 1rem;
}

/* ── STREAMLIT WIDGETS ── */
.stSelectbox label { display: none !important; }
.stSelectbox > div > div,
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  color: var(--text-b) !important;
  font-size: 0.92rem !important;
  box-shadow: none !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--border2) !important;
  box-shadow: 0 0 0 3px rgba(100,90,75,0.08) !important;
}

/* PRIMARY BUTTON */
.stButton > button {
  background: var(--text-h) !important;
  color: var(--beige2) !important;
  border: 1px solid var(--text-h) !important;
  border-radius: 3px !important;
  padding: 0.7rem 1.8rem !important;
  font-weight: 500 !important;
  font-size: 0.8rem !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  transition: all 0.22s ease !important;
  width: 100% !important;
  font-family: 'DM Sans', sans-serif !important;
  cursor: pointer !important;
}
.stButton > button:hover {
  background: var(--text-b) !important;
  border-color: var(--text-b) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* CARD BUTTON (columns) */
div[data-testid="column"] .stButton > button {
  background: transparent !important;
  color: var(--text-b) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 3px 3px !important;
  font-size: 0.76rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.3px !important;
  text-transform: none !important;
  padding: 0.55rem 0.5rem !important;
  transition: all 0.18s ease !important;
}
div[data-testid="column"] .stButton > button:hover {
  background: var(--surface2) !important;
  color: var(--text-h) !important;
  border-color: var(--border2) !important;
}

/* ── SECTION HEADER ── */
.sec-head {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.8rem;
}
.sec-head-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}
.sec-head-text {
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--text-l);
  white-space: nowrap;
}

/* ── FILM CARD ── */
.film-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 3px;
  overflow: hidden;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
  height: 100%;
}
.film-card:hover {
  box-shadow: 0 4px 24px rgba(28,23,18,0.08);
  border-color: var(--border2);
}
.film-card img { width: 100%; display: block; }
.film-card-info {
  padding: 10px 10px 0;
}
.film-card-title {
  font-size: 0.79rem;
  font-weight: 500;
  color: var(--text-b);
  line-height: 1.4;
  text-align: center;
}

/* ── EMPTY STATE ── */
.empty {
  text-align: center;
  padding: 6rem 2rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: var(--surface);
}
.empty-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 5rem;
  font-weight: 300;
  color: var(--beige);
  line-height: 1;
  margin-bottom: 0.5rem;
}
.empty-h {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.6rem;
  font-weight: 400;
  color: var(--text-m);
  margin-bottom: 0.5rem;
}
.empty-p {
  font-size: 0.84rem;
  color: var(--text-l);
  line-height: 1.7;
}

/* ── FOR label ── */
.for-label {
  font-size: 0.78rem;
  color: var(--text-l);
  margin-bottom: 1.8rem;
  letter-spacing: 0.3px;
}
.for-label strong {
  color: var(--text-h);
  font-weight: 600;
}

/* ================================================================
   DETAIL PAGE
   ================================================================ */

/* Back nav */
.detail-nav {
  display: flex;
  align-items: center;
  padding: 1.2rem 0 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}

/* Hero strip */
.detail-hero {
  position: relative;
  height: 480px;
  overflow: hidden;
  margin-bottom: 0;
  background: var(--surface2);
}
.detail-hero-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(30%) brightness(0.65) sepia(15%);
}
.detail-hero-grad {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(250,247,242,0) 0%,
    rgba(250,247,242,0) 30%,
    rgba(250,247,242,0.6) 70%,
    rgba(250,247,242,1) 100%
  );
}
.detail-hero-text {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 0 3rem 2.8rem;
}
.detail-title-hero {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.8rem;
  font-weight: 500;
  color: var(--surface);
  line-height: 1.1;
  letter-spacing: -1px;
  margin-bottom: 0.5rem;
  text-shadow: 0 1px 20px rgba(0,0,0,0.35);
}
.detail-tagline-hero {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-style: italic;
  font-weight: 300;
  color: rgba(255,255,255,0.78);
}

/* No backdrop fallback */
.detail-title-fallback {
  font-family: 'Cormorant Garamond', serif;
  font-size: 3.2rem;
  font-weight: 500;
  color: var(--text-h);
  line-height: 1.1;
  letter-spacing: -1px;
  margin-bottom: 0.5rem;
  padding-top: 2.5rem;
}
.detail-tagline-fallback {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-style: italic;
  color: var(--text-m);
  margin-bottom: 2rem;
}

/* Meta strip */
.meta-strip {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
  padding: 1.4rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2.5rem;
}
.meta-item {
  text-align: left;
}
.meta-key {
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--text-l);
  margin-bottom: 2px;
}
.meta-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.3rem;
  font-weight: 500;
  color: var(--text-h);
  line-height: 1;
}
.meta-divider {
  width: 1px;
  height: 30px;
  background: var(--border);
}

/* Rating */
.rating-block {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.rating-score {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-h);
  line-height: 1;
}
.rating-denom {
  font-size: 0.9rem;
  color: var(--text-l);
  font-weight: 300;
}
.rating-count {
  font-size: 0.7rem;
  color: var(--text-l);
  margin-top: 2px;
}

/* Stars */
.stars-row {
  font-size: 0.85rem;
  color: var(--text-xl);
  letter-spacing: 2px;
}
.stars-row .on { color: var(--text-m); }

/* Detail section */
.d-section {
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--text-l);
  margin: 2.5rem 0 0.9rem;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

/* Overview */
.d-overview {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.13rem;
  color: var(--text-b);
  line-height: 1.85;
  font-weight: 400;
}

/* Genre pill */
.g-pill {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 2px;
  padding: 4px 13px;
  font-size: 0.74rem;
  color: var(--text-m);
  margin: 2px;
  font-weight: 400;
  letter-spacing: 0.3px;
}

/* People row */
.person-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.person-row:last-child { border-bottom: none; }
.person-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--border2);
  flex-shrink: 0;
}
.person-name { font-size: 0.88rem; font-weight: 500; color: var(--text-h); }
.person-role { font-size: 0.76rem; color: var(--text-l); margin-left: auto; letter-spacing: 0.5px; }

/* Cast grid card */
.cast-c {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 14px 10px;
  text-align: center;
  margin-bottom: 10px;
}
.cast-c-name { font-size: 0.8rem; font-weight: 500; color: var(--text-h); margin-bottom: 3px; }
.cast-c-char { font-family: 'Cormorant Garamond', serif; font-size: 0.82rem; color: var(--text-l); font-style: italic; }

/* Ext links */
.ext-a {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 10px;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-m);
  background: var(--surface);
  margin-top: 8px;
  transition: all 0.18s ease;
  letter-spacing: 0.5px;
}
.ext-a:hover {
  background: var(--text-h);
  color: var(--beige2);
  border-color: var(--text-h);
}

/* Finance strip */
.fin-strip {
  display: flex;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 12px;
}
.fin-cell {
  flex: 1;
  padding: 12px;
  text-align: center;
  background: var(--surface);
}
.fin-cell + .fin-cell { border-left: 1px solid var(--border); }
.fin-key {
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-l);
  margin-bottom: 4px;
}
.fin-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.15rem;
  font-weight: 500;
  color: var(--text-h);
}

/* Poster shadow */
div[data-testid="stImage"] img {
  border: 1px solid var(--border);
  box-shadow: 4px 8px 32px rgba(28,23,18,0.1);
}

/* stVideo border */
div[data-testid="stVideo"] {
  border: 1px solid var(--border);
  border-radius: 3px;
  overflow: hidden;
}

/* spinner */
.stSpinner > div { border-top-color: var(--text-m) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# === Google Drive file URLs ===
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
            "title":      d.get("title", ""),
            "tagline":    d.get("tagline", ""),
            "overview":   d.get("overview", "No summary available."),
            "release":    d.get("release_date", ""),
            "runtime":    d.get("runtime", 0),
            "rating":     round(d.get("vote_average", 0), 1),
            "votes":      d.get("vote_count", 0),
            "budget":     d.get("budget", 0),
            "revenue":    d.get("revenue", 0),
            "language":   d.get("original_language", "").upper(),
            "status":     d.get("status", ""),
            "genres":     [g["name"] for g in d.get("genres", [])],
            "directors":  [m["name"] for m in crew if m.get("job") == "Director"],
            "writers":    list(dict.fromkeys([m["name"] for m in crew if m.get("job") in ("Screenplay","Writer","Story")]))[:4],
            "cast":       [(m["name"], m.get("character","")) for m in cr.get("cast",[])[:8]],
            "poster":     f"https://image.tmdb.org/t/p/w500/{d['poster_path']}" if d.get("poster_path") else "",
            "backdrop":   f"https://image.tmdb.org/t/p/w1280/{d['backdrop_path']}" if d.get("backdrop_path") else "",
            "trailer":    next((v["key"] for v in vid.get("results",[]) if v.get("site")=="YouTube" and v.get("type")=="Trailer"), None),
            "imdb_id":    d.get("imdb_id",""),
            "homepage":   d.get("homepage",""),
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


# ── Session ──
for k, v in [("page","home"),("mid",None),("recs",[]),("src",None),("history",[]),("det_title","")]:
    if k not in st.session_state: st.session_state[k] = v


# ================================================================
# DETAIL PAGE
# ================================================================
if st.session_state.page == "detail":

    # ── Persistent top nav bar ──
    nav_l, nav_c, nav_r = st.columns([2, 3, 2], gap="small")

    with nav_l:
        # Brand always goes home
        st.markdown("""
        <div class="topbar" style="border-bottom:none;padding:1rem 0 0.8rem;">
          <div class="brand">Cine<em>Mind</em></div>
        </div>
        """, unsafe_allow_html=True)

    with nav_c:
        # Breadcrumb: Home > Film Title
        cur_title = st.session_state.get("det_title", "Film")
        st.markdown(f"""
        <div style="padding:1.05rem 0 0.8rem;">
          <div class="breadcrumb">
            <span class="bc-home" id="bc-home-link">Home</span>
            <span class="bc-sep">&#8250;</span>
            <span class="bc-cur" title="{cur_title}">{cur_title}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with nav_r:
        # Back button — right-aligned, ghost style
        st.markdown('<div class="nav-back-wrap" style="display:flex;justify-content:flex-end;padding-top:0.85rem;">', unsafe_allow_html=True)
        back_col, _ = st.columns([1, 0.01])
        with back_col:
            if st.button("\u2190 Back", key="nav_back_btn"):
                if st.session_state.history:
                    # Pop back to the previous film
                    prev = st.session_state.history.pop()
                    st.session_state.mid = prev["id"]
                    st.session_state.det_title = prev["title"]
                else:
                    st.session_state.page = "home"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin:0;border:none;border-top:1px solid var(--border);">', unsafe_allow_html=True)

    with st.spinner("Loading..."):
        det = fetch_details(st.session_state.mid)

    if not det:
        st.error("Could not load film details.")
        st.stop()

    # Hero backdrop
    if det["backdrop"]:
        st.markdown(f"""
        <div class="detail-hero">
          <img class="detail-hero-img" src="{det['backdrop']}" />
          <div class="detail-hero-grad"></div>
          <div class="detail-hero-text">
            <div class="detail-title-hero">{det['title']}</div>
            <div class="detail-tagline-hero">{det['tagline']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="detail-title-fallback">{det['title']}</div>
        <div class="detail-tagline-fallback">{det['tagline']}</div>
        """, unsafe_allow_html=True)

    # Meta strip
    year = det["release"][:4] if det["release"] else "—"
    rh   = det["runtime"] // 60 if det["runtime"] else 0
    rm   = det["runtime"] % 60  if det["runtime"] else 0
    rt   = f"{rh}h {rm}m" if det["runtime"] else "—"
    genres_inline = " / ".join(det["genres"][:3]) if det["genres"] else ""

    st.markdown(f"""
    <div class="meta-strip">
      <div class="meta-item">
        <div class="meta-key">Score</div>
        <div class="rating-block">
          <span class="rating-score">{det['rating']}</span>
          <span class="rating-denom">/10</span>
        </div>
        <div class="stars-row">{stars_html(det['rating'])}</div>
        <div class="rating-count">{det['votes']:,} ratings</div>
      </div>
      <div class="meta-divider"></div>
      <div class="meta-item">
        <div class="meta-key">Year</div>
        <div class="meta-val">{year}</div>
      </div>
      <div class="meta-divider"></div>
      <div class="meta-item">
        <div class="meta-key">Runtime</div>
        <div class="meta-val">{rt}</div>
      </div>
      <div class="meta-divider"></div>
      <div class="meta-item">
        <div class="meta-key">Language</div>
        <div class="meta-val">{det['language']}</div>
      </div>
      <div class="meta-divider"></div>
      <div class="meta-item">
        <div class="meta-key">Genre</div>
        <div class="meta-val" style="font-size:1rem;">{genres_inline}</div>
      </div>
      <div class="meta-divider"></div>
      <div class="meta-item">
        <div class="meta-key">Status</div>
        <div class="meta-val" style="font-size:1rem;">{det['status']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout
    lc, rc = st.columns([1, 2.4], gap="large")

    with lc:
        if det["poster"]:
            st.image(det["poster"], use_container_width=True)

        # Finance
        if det["budget"] or det["revenue"]:
            st.markdown(f"""
            <div class="fin-strip">
              <div class="fin-cell">
                <div class="fin-key">Budget</div>
                <div class="fin-val">{money(det['budget'])}</div>
              </div>
              <div class="fin-cell">
                <div class="fin-key">Box Office</div>
                <div class="fin-val">{money(det['revenue'])}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Links
        if det["imdb_id"]:
            st.markdown(f'<a class="ext-a" href="https://www.imdb.com/title/{det["imdb_id"]}" target="_blank"><span>&#9733;</span> View on IMDb</a>', unsafe_allow_html=True)
        if det["homepage"]:
            st.markdown(f'<a class="ext-a" href="{det["homepage"]}" target="_blank"><span>&#8594;</span> Official Site</a>', unsafe_allow_html=True)

    with rc:
        # Synopsis
        st.markdown('<div class="d-section">Synopsis</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="d-overview">{det["overview"]}</p>', unsafe_allow_html=True)

        # Genres (pills)
        if det["genres"]:
            st.markdown('<div class="d-section">Genres</div>', unsafe_allow_html=True)
            st.markdown("".join(f'<span class="g-pill">{g}</span>' for g in det["genres"]), unsafe_allow_html=True)

        # Direction
        if det["directors"]:
            st.markdown('<div class="d-section">Direction</div>', unsafe_allow_html=True)
            for name in det["directors"]:
                st.markdown(f'<div class="person-row"><span class="person-dot"></span><span class="person-name">{name}</span><span class="person-role">Director</span></div>', unsafe_allow_html=True)

        # Screenplay
        if det["writers"]:
            st.markdown('<div class="d-section">Screenplay</div>', unsafe_allow_html=True)
            for name in det["writers"]:
                st.markdown(f'<div class="person-row"><span class="person-dot"></span><span class="person-name">{name}</span><span class="person-role">Writer</span></div>', unsafe_allow_html=True)

        # Cast
        if det["cast"]:
            st.markdown('<div class="d-section">Cast</div>', unsafe_allow_html=True)
            cc = st.columns(4)
            for i, (name, char) in enumerate(det["cast"]):
                with cc[i % 4]:
                    st.markdown(f'<div class="cast-c"><div class="cast-c-name">{name}</div><div class="cast-c-char">{char if char else "—"}</div></div>', unsafe_allow_html=True)

        # Trailer
        if det["trailer"]:
            st.markdown('<div class="d-section">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={det['trailer']}")

    st.stop()


# ================================================================
# HOME PAGE
# ================================================================

# Top bar
st.markdown("""
<div class="topbar">
  <div class="brand">Cine<em>Mind</em></div>
  <div class="nav-links">Film &nbsp;&middot;&nbsp; Discover &nbsp;&middot;&nbsp; Curated</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-Powered Film Discovery</div>
  <div class="hero-title">Find your<br><em>next film</em></div>
  <div class="hero-sub">Tell us what you love and we will find films crafted for your taste.</div>
</div>
""", unsafe_allow_html=True)

# Search panel
st.markdown('<div class="search-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-label">Select a film you enjoy</div>', unsafe_allow_html=True)
sc1, sc2 = st.columns([5, 1], gap="medium")
with sc1:
    chosen = st.selectbox("film", movies["title"].values, label_visibility="collapsed")
with sc2:
    go = st.button("Discover", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if go:
    with st.spinner("Curating your list..."):
        st.session_state.recs = recommend(chosen)
        st.session_state.src  = chosen

# Results
if st.session_state.recs:
    st.markdown(f"""
    <div class="sec-head">
      <span class="sec-head-text">Because you watched</span>
      <span class="sec-head-text" style="color:var(--text-b);font-weight:600;">{st.session_state.src}</span>
      <div class="sec-head-line"></div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5, gap="small")
    for i, col in enumerate(cols):
        r = st.session_state.recs[i]
        with col:
            if r["poster"]:
                st.image(r["poster"], use_container_width=True)
            if st.button(r["title"], key=f"r{i}", use_container_width=True):
                st.session_state.history   = []        # fresh history for home→detail
                st.session_state.mid       = r["id"]
                st.session_state.det_title = r["title"]
                st.session_state.page      = "detail"
                st.rerun()
else:
    st.markdown("""
    <div class="empty">
      <div class="empty-num">01</div>
      <div class="empty-h">Begin your discovery</div>
      <div class="empty-p">Choose a film from the search above and click <strong>Discover</strong>.<br>Then select any title to read full details — cast, crew, rating, and trailer.</div>
    </div>
    """, unsafe_allow_html=True)