import os
import gdown
import requests
import streamlit as st
import pickle
import pandas as pd

# === Google Drive file URLs ===
movies_dict_url = "https://drive.google.com/uc?id=1CishRUVNw4h--ffoIblUfpg-p1F5m57c"
similarity_url = "https://drive.google.com/uc?id=1tH8Z4HkjoOI5n8n3ixO1L7ylAofLB5UD"

# === Download the .pkl files if not already present ===
if not os.path.exists("movies_dict.pkl"):
    gdown.download(movies_dict_url, "movies_dict.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    gdown.download(similarity_url, "similarity.pkl", quiet=False)

# === Load the pickled files ===
movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

# === Poster fetcher ===
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""

# === Recommender function ===
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_titles, recommended_posters

# === Streamlit UI ===
st.title("🎬 CineMind: Movie Recommender")

selected_movie_name = st.selectbox(
    'Select a movie you like:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
