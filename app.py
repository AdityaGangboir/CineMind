import os
import gdown
import requests
import streamlit as st
import pickle
import pandas as pd

# === Page Config ===
st.set_page_config(
    page_title="CineMind - Movie Recommender",
    page_icon="movie_camera",
    layout="wide",
)

# === Custom CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0f0c1a 100%);
    color: #e8e8f0;
}

#MainMenu, footer, header { visibility: hidden; }

.hero-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #f472b6, #fb923c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
    letter-spacing: -1px;
}
.hero-sub {
    text-align: center;
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2.5rem;
    font-weight: 400;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #db2777) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.45) !important;
}

.detail-genre-tag {
    display: inline-block;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #c4b5fd;
    margin: 3px;
    font-weight: 500;
}
.detail-stat-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    margin-bottom: 10px;
}
.detail-stat-label {
    font-size: 0.72rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.detail-stat-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #a78bfa;
}
.cast-chip {
    display: inline-block;
    background: rgba(244,114,182,0.12);
    border: 1px solid rgba(244,114,182,0.3);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #f9a8d4;
    margin: 3px;
    font-weight: 500;
}
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #c4b5fd;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1.5rem 0 0.75rem;
    border-bottom: 1px solid rgba(167,139,250,0.2);
    padding-bottom: 6px;
}
.overview-text {
    color: #9ca3af;
    line-height: 1.8;
    font-size: 0.97rem;
}
.rating-stars {
    color: #fbbf24;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# === Google Drive file URLs ===
movies_dict_url = "https://drive.google.com/uc?id=1CishRUVNw4h--ffoIblUfpg-p1F5m57c"
similarity_url = "https://drive.google.com/uc?id=1tH8Z4HkjoOI5n8n3ixO1L7ylAofLB5UD"

# === Download the .pkl files if not already present ===
if not os.path.exists("movies_dict.pkl"):
    gdown.download(movies_dict_url, "movies_dict.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    gdown.download(similarity_url, "similarity.pkl", quiet=False)

# === Load the pickled files ===
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"


# === Poster fetcher ===
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        data = requests.get(url, timeout=8).json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
    except Exception:
        return ""


# === Full movie details fetcher ===
def fetch_movie_details(movie_id):
    try:
        detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        detail_data = requests.get(detail_url, timeout=8).json()

        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"
        credits_data = requests.get(credits_url, timeout=8).json()

        videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}&language=en-US"
        videos_data = requests.get(videos_url, timeout=8).json()

        crew = credits_data.get('crew', [])
        directors = [m['name'] for m in crew if m.get('job') == 'Director']
        writers = [m['name'] for m in crew if m.get('job') in ('Screenplay', 'Writer', 'Story')][:3]

        cast = credits_data.get('cast', [])[:8]
        cast_characters = [(m['name'], m.get('character', '')) for m in cast]

        trailer_key = None
        for v in videos_data.get('results', []):
            if v.get('site') == 'YouTube' and v.get('type') == 'Trailer':
                trailer_key = v.get('key')
                break

        genres = [g['name'] for g in detail_data.get('genres', [])]

        poster_path = detail_data.get('poster_path', '')
        backdrop_path = detail_data.get('backdrop_path', '')
        poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""
        backdrop_url = f"https://image.tmdb.org/t/p/w1280/{backdrop_path}" if backdrop_path else ""

        return {
            "title": detail_data.get('title', 'Unknown'),
            "tagline": detail_data.get('tagline', ''),
            "overview": detail_data.get('overview', 'No overview available.'),
            "release_date": detail_data.get('release_date', 'N/A'),
            "runtime": detail_data.get('runtime', 0),
            "vote_average": round(detail_data.get('vote_average', 0), 1),
            "vote_count": detail_data.get('vote_count', 0),
            "popularity": round(detail_data.get('popularity', 0), 1),
            "budget": detail_data.get('budget', 0),
            "revenue": detail_data.get('revenue', 0),
            "original_language": detail_data.get('original_language', 'N/A').upper(),
            "status": detail_data.get('status', 'N/A'),
            "genres": genres,
            "directors": directors,
            "writers": writers,
            "cast": cast_characters,
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "trailer_key": trailer_key,
            "homepage": detail_data.get('homepage', ''),
            "imdb_id": detail_data.get('imdb_id', ''),
        }
    except Exception:
        return None


# === Recommender function ===
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append({
            "title": movies.iloc[i[0]].title,
            "movie_id": movie_id,
            "poster": fetch_poster(movie_id),
        })
    return recommended_movies


# === Helper: format currency ===
def fmt_currency(val):
    if val and val > 0:
        if val >= 1_000_000_000:
            return f"${val/1_000_000_000:.2f}B"
        elif val >= 1_000_000:
            return f"${val/1_000_000:.1f}M"
        return f"${val:,}"
    return "N/A"


# === Helper: star rating ===
def star_rating(score):
    filled = round(score / 2)
    return "\u2605" * filled + "\u2606" * (5 - filled)


# ====================================================
# SESSION STATE
# ====================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None
if "selected_movie_title" not in st.session_state:
    st.session_state.selected_movie_title = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "source_movie" not in st.session_state:
    st.session_state.source_movie = None


# ====================================================
# PAGE: MOVIE DETAIL
# ====================================================
if st.session_state.page == "detail":
    movie_id = st.session_state.selected_movie_id

    if st.button("\u2190 Back to Recommendations"):
        st.session_state.page = "home"
        st.rerun()

    with st.spinner("Loading movie details..."):
        details = fetch_movie_details(movie_id)

    if not details:
        st.error("Could not load movie details. Please try again.")
        st.stop()

    if details["backdrop_url"]:
        st.markdown(
            f"""
            <div style="
                width:100%;
                height:320px;
                border-radius:20px;
                overflow:hidden;
                background: linear-gradient(to bottom, transparent 40%, #0a0a0f),
                            url('{details["backdrop_url"]}') center/cover no-repeat;
                margin-bottom: 1.5rem;
                position:relative;
            ">
                <div style="
                    position:absolute; bottom:0; left:0; right:0;
                    padding:24px 28px;
                    background:linear-gradient(to top, rgba(10,10,15,0.95) 0%, transparent 100%);
                ">
                    <div style="font-size:2.2rem;font-weight:800;color:#fff;line-height:1.2;">{details["title"]}</div>
                    <div style="color:#a78bfa;font-size:1rem;margin-top:4px;font-style:italic;">{details["tagline"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div class="hero-title">{details["title"]}</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.5], gap="large")

    with left_col:
        if details["poster_url"]:
            st.image(details["poster_url"], use_container_width=True)

        year = details["release_date"][:4] if details["release_date"] != "N/A" else "N/A"
        runtime_h = details["runtime"] // 60 if details["runtime"] else 0
        runtime_m = details["runtime"] % 60 if details["runtime"] else 0
        runtime_str = f"{runtime_h}h {runtime_m}m" if details["runtime"] else "N/A"

        st.markdown(f"""
        <div class="detail-stat-box">
            <div class="detail-stat-label">Rating</div>
            <div class="detail-stat-value">{details["vote_average"]} / 10</div>
            <div class="rating-stars">{star_rating(details["vote_average"])}</div>
            <div style="color:#6b7280;font-size:0.75rem;margin-top:2px;">{details["vote_count"]:,} votes</div>
        </div>
        <div class="detail-stat-box">
            <div class="detail-stat-label">Year</div>
            <div class="detail-stat-value">{year}</div>
        </div>
        <div class="detail-stat-box">
            <div class="detail-stat-label">Runtime</div>
            <div class="detail-stat-value">{runtime_str}</div>
        </div>
        <div class="detail-stat-box">
            <div class="detail-stat-label">Language</div>
            <div class="detail-stat-value">{details["original_language"]}</div>
        </div>
        <div class="detail-stat-box">
            <div class="detail-stat-label">Status</div>
            <div class="detail-stat-value" style="font-size:1rem;">{details["status"]}</div>
        </div>
        """, unsafe_allow_html=True)

        if details["budget"] or details["revenue"]:
            st.markdown(f"""
            <div class="detail-stat-box">
                <div class="detail-stat-label">Budget</div>
                <div class="detail-stat-value" style="font-size:1rem;">{fmt_currency(details["budget"])}</div>
            </div>
            <div class="detail-stat-box">
                <div class="detail-stat-label">Box Office</div>
                <div class="detail-stat-value" style="font-size:1rem;">{fmt_currency(details["revenue"])}</div>
            </div>
            """, unsafe_allow_html=True)

        if details["imdb_id"]:
            st.markdown(
                f'<a href="https://www.imdb.com/title/{details["imdb_id"]}" target="_blank" style="display:block;text-align:center;background:rgba(245,197,24,0.15);border:1px solid rgba(245,197,24,0.4);border-radius:10px;padding:8px;color:#f5c518;font-weight:600;text-decoration:none;margin-top:8px;">View on IMDb</a>',
                unsafe_allow_html=True,
            )
        if details["homepage"]:
            st.markdown(
                f'<a href="{details["homepage"]}" target="_blank" style="display:block;text-align:center;background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);border-radius:10px;padding:8px;color:#a78bfa;font-weight:600;text-decoration:none;margin-top:8px;">Official Website</a>',
                unsafe_allow_html=True,
            )

    with right_col:
        if details["genres"]:
            st.markdown('<div class="section-header">Genres</div>', unsafe_allow_html=True)
            genre_html = "".join([f'<span class="detail-genre-tag">{g}</span>' for g in details["genres"]])
            st.markdown(genre_html, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="overview-text">{details["overview"]}</p>', unsafe_allow_html=True)

        if details["directors"]:
            st.markdown('<div class="section-header">Director(s)</div>', unsafe_allow_html=True)
            st.markdown(
                "".join([f'<span class="cast-chip">&#127909; {d}</span>' for d in details["directors"]]),
                unsafe_allow_html=True,
            )

        if details["writers"]:
            st.markdown('<div class="section-header">Screenplay</div>', unsafe_allow_html=True)
            st.markdown(
                "".join([f'<span class="cast-chip">&#9999; {w}</span>' for w in details["writers"]]),
                unsafe_allow_html=True,
            )

        if details["cast"]:
            st.markdown('<div class="section-header">Top Cast</div>', unsafe_allow_html=True)
            cast_cols = st.columns(4)
            for idx, (name, char) in enumerate(details["cast"]):
                with cast_cols[idx % 4]:
                    st.markdown(
                        f"""
                        <div style="
                            background:rgba(244,114,182,0.07);
                            border:1px solid rgba(244,114,182,0.2);
                            border-radius:12px;
                            padding:10px;
                            text-align:center;
                            margin-bottom:8px;
                        ">
                            <div style="font-weight:600;font-size:0.82rem;color:#f9a8d4;">{name}</div>
                            <div style="font-size:0.72rem;color:#6b7280;margin-top:2px;font-style:italic;">{char}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if details["trailer_key"]:
            st.markdown('<div class="section-header">Trailer</div>', unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={details['trailer_key']}")

    st.stop()


# ====================================================
# PAGE: HOME
# ====================================================
st.markdown('<div class="hero-title">CineMind</div>', unsafe_allow_html=True)
st.markdown("<div class=\"hero-sub\">Discover movies you'll love &mdash; powered by AI</div>", unsafe_allow_html=True)

col_sel, col_btn = st.columns([4, 1])
with col_sel:
    selected_movie_name = st.selectbox(
        "Select a movie:",
        movies['title'].values,
        label_visibility="collapsed",
    )
with col_btn:
    recommend_btn = st.button("Recommend", use_container_width=True)

if recommend_btn:
    with st.spinner("Finding similar movies..."):
        st.session_state.recommendations = recommend(selected_movie_name)
        st.session_state.source_movie = selected_movie_name

if st.session_state.recommendations:
    st.markdown(
        f'<div style="margin:2rem 0 1rem;font-size:1.1rem;font-weight:600;color:#9ca3af;">Because you liked <span style="color:#a78bfa;">{st.session_state.source_movie}</span>...</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5, gap="medium")
    for idx, col in enumerate(cols):
        rec = st.session_state.recommendations[idx]
        with col:
            if rec["poster"]:
                st.image(rec["poster"], use_container_width=True)
            if st.button(rec["title"], key=f"movie_btn_{idx}", use_container_width=True):
                st.session_state.selected_movie_id = rec["movie_id"]
                st.session_state.selected_movie_title = rec["title"]
                st.session_state.page = "detail"
                st.rerun()

if not st.session_state.recommendations:
    st.markdown("""
    <div style="
        text-align:center;
        padding:4rem 2rem;
        background:rgba(255,255,255,0.02);
        border:1px dashed rgba(255,255,255,0.1);
        border-radius:20px;
        margin-top:2rem;
        color:#4b5563;
    ">
        <div style="font-size:3rem;margin-bottom:1rem;">&#127909;</div>
        <div style="font-size:1.1rem;font-weight:500;">Select a movie above and click <strong style="color:#a78bfa;">Recommend</strong> to get started</div>
        <div style="font-size:0.85rem;margin-top:0.5rem;">Click any recommended movie title to see full details, cast, trailers and more</div>
    </div>
    """, unsafe_allow_html=True)