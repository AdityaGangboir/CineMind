import os
import gdown
import requests
import streamlit as st
import pickle
import pandas as pd

# === Page Config ===
st.set_page_config(
    page_title="CineMind - Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

# === CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #f7f3ee !important;
    color: #1a1208;
}

/* ── Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem !important; max-width: 1280px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #ede8e0; }
::-webkit-scrollbar-thumb { background: #c8b89a; border-radius: 3px; }

/* ── HOME: Hero ── */
.home-hero {
    text-align: center;
    padding: 3.5rem 1rem 2.5rem;
}
.home-logo {
    font-family: 'Playfair Display', serif;
    font-size: 3.6rem;
    font-weight: 700;
    color: #1a1208;
    letter-spacing: -1.5px;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.home-logo span {
    color: #b08d57;
}
.home-tagline {
    font-size: 1rem;
    color: #8a7a65;
    font-weight: 400;
    letter-spacing: 0.5px;
    margin-bottom: 0;
}

/* ── Divider ── */
.elegant-divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #d4c5ae, transparent);
    margin: 1.5rem 0;
}

/* ── Search bar container ── */
.search-wrap {
    background: #ffffff;
    border: 1px solid #e4dace;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 20px rgba(176,141,87,0.07);
}

/* ── Selectbox ── */
.stSelectbox label { display: none !important; }
.stSelectbox > div > div {
    background: #faf8f4 !important;
    border: 1.5px solid #d4c5ae !important;
    border-radius: 10px !important;
    color: #1a1208 !important;
    font-size: 0.97rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease !important;
}
.stSelectbox > div > div:hover {
    border-color: #b08d57 !important;
}
div[data-baseweb="select"] > div {
    background: #faf8f4 !important;
    border-color: #d4c5ae !important;
}

/* ── Primary button ── */
.stButton > button {
    background: #1a1208 !important;
    color: #f7f0e6 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 500 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.4px !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: #b08d57 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(176,141,87,0.3) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Section label ── */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #b08d57;
    margin: 2rem 0 1rem;
}

/* ── Movie cards ── */
.movie-card {
    background: #ffffff;
    border: 1px solid #ede6da;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    position: relative;
    cursor: pointer;
}
.movie-card:hover {
    border-color: #b08d57;
    box-shadow: 0 10px 40px rgba(176,141,87,0.18);
    transform: translateY(-5px);
}
.movie-card img {
    width: 100%;
    display: block;
    border-radius: 13px 13px 0 0;
}
.movie-card-body {
    padding: 10px 12px 12px;
}
.movie-card-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #1a1208;
    line-height: 1.35;
    text-align: center;
}

/* ── Movie card click button override ── */
div[data-testid="column"] .stButton > button {
    background: transparent !important;
    color: #1a1208 !important;
    border: 1px solid #e4dace !important;
    border-radius: 0 0 14px 14px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.75rem !important;
    letter-spacing: 0.2px !important;
    text-align: center !important;
    margin-top: 0 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: #1a1208 !important;
    color: #f7f0e6 !important;
    border-color: #1a1208 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    background: #ffffff;
    border: 1px dashed #d4c5ae;
    border-radius: 20px;
    margin-top: 1rem;
    color: #b0a090;
}
.empty-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.6;
}
.empty-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #6b5d4f;
    margin-bottom: 0.5rem;
}
.empty-sub {
    font-size: 0.88rem;
    color: #b0a090;
}

/* ── Because you liked ── */
.because-label {
    font-size: 0.92rem;
    color: #8a7a65;
    margin: 0.5rem 0 1.5rem;
}
.because-label strong {
    color: #1a1208;
    font-weight: 600;
}

/* ── DETAIL PAGE ── */

/* Back button */
.stButton.back-btn-wrap > button {
    background: transparent !important;
    color: #8a7a65 !important;
    border: 1px solid #e4dace !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 1rem !important;
    width: auto !important;
    font-weight: 400 !important;
    letter-spacing: 0 !important;
}
.stButton.back-btn-wrap > button:hover {
    background: #1a1208 !important;
    color: #f7f0e6 !important;
    border-color: #1a1208 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Backdrop */
.backdrop-hero {
    width: 100%;
    height: 380px;
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    margin-bottom: 2rem;
    background-color: #e8e0d5;
}
.backdrop-hero-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.55;
    filter: sepia(20%) saturate(80%);
}
.backdrop-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(247,243,238,0.1) 0%,
        rgba(247,243,238,0.05) 40%,
        rgba(26,18,8,0.75) 100%
    );
}
.backdrop-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2rem 2.5rem;
}
.backdrop-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #faf6f0;
    line-height: 1.15;
    margin-bottom: 0.35rem;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.backdrop-tagline {
    font-size: 0.95rem;
    color: #d4c5ae;
    font-style: italic;
    font-weight: 300;
}

/* Stat card */
.stat-card {
    background: #ffffff;
    border: 1px solid #ede6da;
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    margin-bottom: 10px;
}
.stat-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #b08d57;
    margin-bottom: 4px;
}
.stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #1a1208;
    line-height: 1.2;
}
.stat-sub {
    font-size: 0.7rem;
    color: #b0a090;
    margin-top: 3px;
}

/* Stars */
.star-filled { color: #b08d57; }
.star-empty  { color: #d4c5ae; }

/* External link */
.ext-link {
    display: block;
    text-align: center;
    border-radius: 9px;
    padding: 9px 12px;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none;
    margin-top: 8px;
    transition: all 0.2s ease;
    letter-spacing: 0.3px;
}
.ext-link-imdb {
    background: #f5c5181a;
    border: 1px solid #f5c51866;
    color: #8a6800;
}
.ext-link-imdb:hover { background: #f5c518; color: #1a1208; }
.ext-link-web {
    background: #e8e0d5;
    border: 1px solid #d4c5ae;
    color: #5a4a3a;
}
.ext-link-web:hover { background: #1a1208; color: #f7f0e6; border-color: #1a1208; }

/* Section header (detail) */
.detail-section {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #b08d57;
    margin: 2rem 0 0.75rem;
    padding-bottom: 6px;
    border-bottom: 1px solid #ede6da;
}

/* Overview */
.overview-text {
    font-size: 0.97rem;
    color: #4a3d2e;
    line-height: 1.85;
    font-weight: 400;
}

/* Genre tag */
.genre-tag {
    display: inline-block;
    background: #f0ebe2;
    border: 1px solid #d4c5ae;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #5a4a3a;
    margin: 3px;
    font-weight: 500;
    letter-spacing: 0.2px;
}

/* People chip */
.people-chip {
    display: inline-block;
    background: #faf8f4;
    border: 1px solid #d4c5ae;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #3a2e20;
    margin: 3px;
    font-weight: 500;
}

/* Cast card */
.cast-card {
    background: #ffffff;
    border: 1px solid #ede6da;
    border-radius: 12px;
    padding: 12px 8px;
    text-align: center;
    margin-bottom: 8px;
    transition: border-color 0.2s ease;
}
.cast-card:hover { border-color: #b08d57; }
.cast-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1a1208;
    margin-bottom: 2px;
}
.cast-char {
    font-size: 0.71rem;
    color: #8a7a65;
    font-style: italic;
}

/* Spinner */
.stSpinner > div { border-top-color: #b08d57 !important; }

/* Poster image border */
.poster-wrap img {
    border-radius: 14px;
    border: 1px solid #e4dace;
    box-shadow: 0 8px 30px rgba(26,18,8,0.12);
}
</style>
""", unsafe_allow_html=True)

# === Google Drive file URLs ===
movies_dict_url = "https://drive.google.com/uc?id=1CishRUVNw4h--ffoIblUfpg-p1F5m57c"
similarity_url  = "https://drive.google.com/uc?id=1tH8Z4HkjoOI5n8n3ixO1L7ylAofLB5UD"

if not os.path.exists("movies_dict.pkl"):
    gdown.download(movies_dict_url, "movies_dict.pkl", quiet=False)
if not os.path.exists("similarity.pkl"):
    gdown.download(similarity_url, "similarity.pkl", quiet=False)

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies      = pd.DataFrame(movies_dict)
similarity  = pickle.load(open('similarity.pkl', 'rb'))

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"


def fetch_poster(movie_id):
    try:
        url  = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        pp   = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{pp}" if pp else ""
    except Exception:
        return ""


def fetch_movie_details(movie_id):
    try:
        d   = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US", timeout=8).json()
        cr  = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US", timeout=8).json()
        vid = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US", timeout=8).json()

        crew      = cr.get('crew', [])
        directors = [m['name'] for m in crew if m.get('job') == 'Director']
        writers   = [m['name'] for m in crew if m.get('job') in ('Screenplay', 'Writer', 'Story')][:3]
        cast      = [(m['name'], m.get('character', '')) for m in cr.get('cast', [])[:8]]

        trailer_key = next(
            (v['key'] for v in vid.get('results', []) if v.get('site') == 'YouTube' and v.get('type') == 'Trailer'),
            None
        )

        pp = d.get('poster_path', '')
        bp = d.get('backdrop_path', '')

        return {
            "title":             d.get('title', 'Unknown'),
            "tagline":           d.get('tagline', ''),
            "overview":          d.get('overview', 'No overview available.'),
            "release_date":      d.get('release_date', 'N/A'),
            "runtime":           d.get('runtime', 0),
            "vote_average":      round(d.get('vote_average', 0), 1),
            "vote_count":        d.get('vote_count', 0),
            "budget":            d.get('budget', 0),
            "revenue":           d.get('revenue', 0),
            "original_language": d.get('original_language', 'N/A').upper(),
            "status":            d.get('status', 'N/A'),
            "genres":            [g['name'] for g in d.get('genres', [])],
            "directors":         directors,
            "writers":           writers,
            "cast":              cast,
            "poster_url":        f"https://image.tmdb.org/t/p/w500/{pp}" if pp else "",
            "backdrop_url":      f"https://image.tmdb.org/t/p/w1280/{bp}" if bp else "",
            "trailer_key":       trailer_key,
            "homepage":          d.get('homepage', ''),
            "imdb_id":           d.get('imdb_id', ''),
        }
    except Exception:
        return None


def recommend(movie):
    idx       = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    top5      = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]
    return [
        {"title": movies.iloc[i].title, "movie_id": movies.iloc[i].movie_id, "poster": fetch_poster(movies.iloc[i].movie_id)}
        for i, _ in top5
    ]


def fmt_currency(val):
    if val and val > 0:
        if val >= 1_000_000_000: return f"${val/1_000_000_000:.2f}B"
        if val >= 1_000_000:     return f"${val/1_000_000:.1f}M"
        return f"${val:,}"
    return "N/A"


def star_rating_html(score):
    filled = round(score / 2)
    stars  = '<span class="star-filled">' + "\u2605" * filled + '</span>'
    stars += '<span class="star-empty">'  + "\u2605" * (5 - filled) + '</span>'
    return stars


# === Session State ===
for key, default in [("page","home"),("selected_movie_id",None),("recommendations",[]),("source_movie",None)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# DETAIL PAGE
# ============================================================
if st.session_state.page == "detail":

    if st.button("\u2190  Back to recommendations"):
        st.session_state.page = "home"
        st.rerun()

    with st.spinner("Fetching movie details..."):
        det = fetch_movie_details(st.session_state.selected_movie_id)

    if not det:
        st.error("Could not load movie details. Please go back and try again.")
        st.stop()

    # ── Backdrop ──
    if det["backdrop_url"]:
        st.markdown(f"""
        <div class="backdrop-hero">
            <img class="backdrop-hero-img" src="{det['backdrop_url']}" />
            <div class="backdrop-overlay"></div>
            <div class="backdrop-content">
                <div class="backdrop-title">{det['title']}</div>
                <div class="backdrop-tagline">{det['tagline']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="padding:2rem 0 1rem;">
            <div class="backdrop-title" style="color:#1a1208;font-size:2.4rem;">{det['title']}</div>
            <div class="backdrop-tagline" style="color:#8a7a65;">{det['tagline']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Two columns ──
    left, right = st.columns([1, 2.6], gap="large")

    with left:
        if det["poster_url"]:
            st.markdown('<div class="poster-wrap">', unsafe_allow_html=True)
            st.image(det["poster_url"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        year = det["release_date"][:4] if det["release_date"] != "N/A" else "N/A"
        rh   = det["runtime"] // 60 if det["runtime"] else 0
        rm   = det["runtime"] % 60  if det["runtime"] else 0
        rt   = f"{rh}h {rm}m" if det["runtime"] else "N/A"

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Rating</div>
            <div class="stat-value">{det['vote_average']} <span style="font-size:0.9rem;color:#8a7a65;">/ 10</span></div>
            <div style="font-size:1rem;margin:3px 0;">{star_rating_html(det['vote_average'])}</div>
            <div class="stat-sub">{det['vote_count']:,} ratings</div>
        </div>
        """, unsafe_allow_html=True)

        cols2 = st.columns(2)
        with cols2[0]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Year</div><div class="stat-value" style="font-size:1.15rem;">{year}</div></div>', unsafe_allow_html=True)
        with cols2[1]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Runtime</div><div class="stat-value" style="font-size:1.05rem;">{rt}</div></div>', unsafe_allow_html=True)

        cols3 = st.columns(2)
        with cols3[0]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Language</div><div class="stat-value" style="font-size:1.1rem;">{det["original_language"]}</div></div>', unsafe_allow_html=True)
        with cols3[1]:
            st.markdown(f'<div class="stat-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:0.95rem;">{det["status"]}</div></div>', unsafe_allow_html=True)

        if det["budget"] or det["revenue"]:
            cols4 = st.columns(2)
            with cols4[0]:
                st.markdown(f'<div class="stat-card"><div class="stat-label">Budget</div><div class="stat-value" style="font-size:1rem;">{fmt_currency(det["budget"])}</div></div>', unsafe_allow_html=True)
            with cols4[1]:
                st.markdown(f'<div class="stat-card"><div class="stat-label">Box Office</div><div class="stat-value" style="font-size:1rem;">{fmt_currency(det["revenue"])}</div></div>', unsafe_allow_html=True)

        if det["imdb_id"]:
            st.markdown(f'<a class="ext-link ext-link-imdb" href="https://www.imdb.com/title/{det["imdb_id"]}" target="_blank">&#9733; View on IMDb</a>', unsafe_allow_html=True)
        if det["homepage"]:
            st.markdown(f'<a class="ext-link ext-link-web" href="{det["homepage"]}" target="_blank">&#8599; Official Website</a>', unsafe_allow_html=True)

    with right:

        if det["genres"]:
            st.markdown('<div class="detail-section">Genres</div>', unsafe_allow_html=True)
            st.markdown("".join([f'<span class="genre-tag">{g}</span>' for g in det["genres"]]), unsafe_allow_html=True)

        st.markdown('<div class="detail-section">Synopsis</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="overview-text">{det["overview"]}</p>', unsafe_allow_html=True)

        if det["directors"]:
            st.markdown('<div class="detail-section">Direction</div>', unsafe_allow_html=True)
            st.markdown("".join([f'<span class="people-chip">&#127909; &nbsp;{d}</span>' for d in det["directors"]]), unsafe_allow_html=True)

        if det["writers"]:
            st.markdown('<div class="detail-section">Screenplay</div>', unsafe_allow_html=True)
            st.markdown("".join([f'<span class="people-chip">&#9999; &nbsp;{w}</span>' for w in det["writers"]]), unsafe_allow_html=True)

        if det["cast"]:
            st.markdown('<div class="detail-section">Cast</div>', unsafe_allow_html=True)
            cc = st.columns(4)
            for i, (name, char) in enumerate(det["cast"]):
                with cc[i % 4]:
                    st.markdown(f"""
                    <div class="cast-card">
                        <div class="cast-name">{name}</div>
                        <div class="cast-char">{char if char else "—"}</div>
                    </div>
                    """, unsafe_allow_html=True)

        if det["trailer_key"]:
            st.markdown('<div class="detail-section">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={det['trailer_key']}")

    st.stop()


# ============================================================
# HOME PAGE
# ============================================================

st.markdown("""
<div class="home-hero">
    <div class="home-logo">Cine<span>Mind</span></div>
    <div class="home-tagline">Your personal cinema, curated by taste</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="elegant-divider">', unsafe_allow_html=True)

# Search section
st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Find your next favourite film</div>', unsafe_allow_html=True)
c1, c2 = st.columns([5, 1], gap="medium")
with c1:
    selected = st.selectbox("Movie", movies['title'].values, label_visibility="collapsed")
with c2:
    go = st.button("Discover", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if go:
    with st.spinner("Curating recommendations..."):
        st.session_state.recommendations = recommend(selected)
        st.session_state.source_movie    = selected

# Recommendations
if st.session_state.recommendations:
    st.markdown(f'<div class="because-label">Showing recommendations for &nbsp;<strong>{st.session_state.source_movie}</strong></div>', unsafe_allow_html=True)

    cols = st.columns(5, gap="small")
    for idx, col in enumerate(cols):
        rec = st.session_state.recommendations[idx]
        with col:
            if rec["poster"]:
                st.image(
                    rec["poster"],
                    use_container_width=True,
                    caption=None,
                )
            if st.button(rec["title"], key=f"rec_{idx}", use_container_width=True):
                st.session_state.selected_movie_id = rec["movie_id"]
                st.session_state.page = "detail"
                st.rerun()
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">&#127909;</div>
        <div class="empty-title">Discover your next watch</div>
        <div class="empty-sub">Select a film above and click <strong>Discover</strong> to get personalised recommendations.<br>Click any film to explore full cast, crew, ratings, and trailer.</div>
    </div>
    """, unsafe_allow_html=True)