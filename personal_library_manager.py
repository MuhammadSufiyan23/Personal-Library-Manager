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

# Function to load Lottie animations
def load_lottie_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error loading animation: {e}")
    return None

# Load animation
lottie_book = load_lottie_url("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load library data from file
def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            st.session_state.library = json.load(file)

# Save library data to file
def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file, indent=4)

# Add a book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()

# Remove a book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        return True
    return False

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    st.session_state.search_results = [book for book in st.session_state.library if search_term in book[search_by].lower()]

# Load library data on app start
load_library()

# Sidebar navigation
st.sidebar.title("📚 Navigation")
if lottie_book:
    st.sidebar.lottie(lottie_book, height=200, key="book_animation")

nav_options = st.sidebar.radio("Go to:", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Header
st.title("📚 Personal Library Manager")

# Views
if st.session_state.current_view == "add_book":
    st.header("📝 Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=datetime.now().year)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Romance", "Thriller", "Biography", "History", "Self-Help", "Other"])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
        submitted = st.form_submit_button("Add Book")
        if submitted and title and author:
            add_book(title, author, publication_year, genre, read_status == "Read")
            st.success("Book added successfully!")
            st.experimental_rerun()

elif st.session_state.current_view == "view_library":
    st.header("📖 Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"📘 {book['title']} ({book['publication_year']})"):
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Status:** {'✅ Read' if book['read_status'] else '📖 Unread'}")
                col1, col2 = st.columns(2)
                if col1.button("Remove", key=f"remove_{i}"):
                    remove_book(i)
                    st.experimental_rerun()
                new_status = not book['read_status']
                if col2.button("Mark as Read" if not book['read_status'] else "Mark as Unread", key=f"toggle_{i}"):
                    st.session_state.library[i]['read_status'] = new_status
                    save_library()
                    st.experimental_rerun()

elif st.session_state.current_view == "search_books":
    st.header("🔍 Search Books")
    search_by = st.selectbox("Search by", ["title", "author", "genre"])
    search_term = st.text_input("Enter search term")
    if st.button("Search"):
        search_books(search_term, search_by)
    if st.session_state.search_results:
        for book in st.session_state.search_results:
            st.write(f"📘 **{book['title']}** - {book['author']} ({book['publication_year']})")
    elif search_term:
        st.warning("No books found.")

elif st.session_state.current_view == "library_statistics":
    st.header("📊 Library Statistics")
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    unread_books = total_books - read_books
    st.metric("Total Books", total_books)
    st.metric("Read Books", read_books)
    st.metric("Unread Books", unread_books)
    
    if total_books > 0:
        fig = go.Figure(data=[go.Pie(labels=['Read', 'Unread'], values=[read_books, unread_books], hole=.4)])
        fig.update_layout(title_text="Read vs Unread Books")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("© 2025 Muhammad Sufiyan | Personal Library Manager")
