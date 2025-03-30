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

# Custom CSS for improved styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #3B82F6;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .success-message, .warning-message {
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .success-message {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
    }
    .warning-message {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
    }
    .book-card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .read-badge, .unread-badge {
        padding: 0.4rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        color: white;
    }
    .read-badge { background-color: #10B981; }
    .unread-badge { background-color: #F87171; }
    .stButton>button { border-radius: 0.375rem; }
</style>
""", unsafe_allow_html=True)

# Function to load lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load and save library data
def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            st.session_state.library = json.load(file)

def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file)

# Add and remove book functions
def add_book(title, author, year, genre, read_status):
    book = {
        'title': title, 'author': author, 'publication_year': year,
        'genre': genre, 'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.success("Book added successfully!")
    time.sleep(0.5)
    st.rerun()

def remove_book(index):
    del st.session_state.library[index]
    save_library()
    st.success("Book removed successfully!")
    st.rerun()

# Load library data
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>📚 Navigation</h1>", unsafe_allow_html=True)
nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Library Statistics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"

# Application header
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>📝 Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance", "Thriller", "Biography", "History", "Self-Help", "Poetry", "Science", "Philosophy", "Religion", "Art", "Other"])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        submit_button = st.form_submit_button("Add Book")
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_status)

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>📖 Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("Your library is empty. Add books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            st.markdown(f"""
            <div class='book-card'>
                <h3>{book['title']}</h3>
                <p><strong>Author:</strong> {book['author']}</p>
                <p><strong>Year:</strong> {book['publication_year']}</p>
                <p><strong>Genre:</strong> {book['genre']}</p>
                <p><span class='{'read-badge' if book['read_status'] else 'unread-badge'}'>{'Read' if book['read_status'] else 'Unread'}</span></p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Remove", key=f"remove_{i}"):
                remove_book(i)

st.markdown("---")
st.markdown("© 2025 Muhammad Sufiyan Personal Library Manager", unsafe_allow_html=True)
