import pickle
import gzip
import streamlit as st
import pandas as pd
import requests
import time

# ----------------------------- #
# Function to fetch poster image
# ----------------------------- #
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        poster = data.get('poster_path')
        if poster:
            return "https://image.tmdb.org/t/p/w500/" + poster
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except requests.RequestException:
        st.warning("⚠️ Could not fetch poster; showing placeholder.")
        return "https://via.placeholder.com/500x750?text=Error"

# ----------------------------- #
# Load compressed similarity matrix
# ----------------------------- #
@st.cache_data
def load_similarity():
    with gzip.open('similarity.pkl.gz', 'rb') as f:
        return pickle.load(f)

# ----------------------------- #
# Recommendation Logic
# ----------------------------- #
def recommend(movie_title):
    idx = movies[movies['title'] == movie_title].index[0]
    sims = list(enumerate(similarity[idx]))
    sims = sorted(sims, key=lambda x: x[1], reverse=True)[1:6]
    names, posters = [], []
    for i, _ in sims:
        m_id = movies.iloc[i].movie_id
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(m_id))
    return names, posters

# ----------------------------- #
# Streamlit App Layout
# ----------------------------- #
st.set_page_config(layout="wide")
st.title("🎬 Movie Recommender System")

# Load small pickled movie data
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

# Load the compressed similarity matrix
similarity = load_similarity()

# User input
movie_list = movies["title"].values
selection = st.selectbox("📽️ Select a movie:", movie_list)

# Show recommendations
if st.button("🔍 Show Recommendation"):
    rec_names, rec_posters = recommend(selection)
    cols = st.columns(5)
    for col, name, poster in zip(cols, rec_names, rec_posters):
        with col:
            st.text(name)
            st.image(poster)
