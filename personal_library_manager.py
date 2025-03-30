import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Lottie animation
@st.cache_data
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load and save library data
LIBRARY_FILE = 'library.json'

def load_library():
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, 'r') as file:
            return json.load(file)
    return []

def save_library(library):
    with open(LIBRARY_FILE, 'w') as file:
        json.dump(library, file, indent=4)

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = load_library()
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Sidebar navigation
st.sidebar.title("📚 Navigation")
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    st.sidebar.lottie(lottie_book, height=200)
nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Page header
st.title("📚 Personal Library Manager")

# Add Book View
if st.session_state.current_view == "add_book":
    st.header("📝 Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        genre = st.text_input("Genre")
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        submit_button = st.form_submit_button("Add Book")
        
        if submit_button and title and author:
            new_book = {
                "title": title,
                "author": author,
                "publication_year": publication_year,
                "genre": genre,
                "read_status": read_status,
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.library.append(new_book)
            save_library(st.session_state.library)
            st.success("Book added successfully!")
            st.balloons()

# View Library
elif st.session_state.current_view == "view_library":
    st.header("📖 Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"📖 {book['title']} - {book['author']}"):
                st.write(f"**Publication Year:** {book['publication_year']}")
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Status:** {'✅ Read' if book['read_status'] else '📖 Unread'}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.library.pop(i)
                        save_library(st.session_state.library)
                        st.rerun()
                with col2:
                    if st.button("Toggle Read Status", key=f"toggle_{i}"):
                        st.session_state.library[i]['read_status'] = not book['read_status']
                        save_library(st.session_state.library)
                        st.rerun()

# Search Books
elif st.session_state.current_view == "search_books":
    st.header("🔍 Search Books")
    search_term = st.text_input("Enter search term:")
    search_results = [book for book in st.session_state.library if search_term.lower() in book['title'].lower()]
    if search_results:
        for book in search_results:
            st.write(f"📖 {book['title']} - {book['author']}")
    elif search_term:
        st.warning("No books found matching your search criteria.")

# Library Statistics
elif st.session_state.current_view == "library_statistics":
    st.header("📊 Library Statistics")
    total_books = len(st.session_state.library)
    read_books = sum(book['read_status'] for book in st.session_state.library)
    st.metric("Total Books", total_books)
    st.metric("Books Read", read_books)
    st.metric("Percentage Read", f"{(read_books / total_books * 100) if total_books else 0:.1f}%")
    if total_books:
        genres = pd.DataFrame({
            "Genre": [book['genre'] for book in st.session_state.library],
        }).value_counts().reset_index()
        genres.columns = ["Genre", "Count"]
        st.plotly_chart(px.bar(genres, x="Genre", y="Count", color="Count", title="Books by Genre"))

st.markdown("---")
st.markdown("© 2025 Muhammad Sufiyan - Personal Library Manager")
