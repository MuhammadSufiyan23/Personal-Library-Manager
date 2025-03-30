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
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load library data from file
def load_library():
    try:
        if os.path.exists('library.json') and os.path.getsize('library.json') > 0:
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
        else:
            st.session_state.library = []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        st.error(f"Error loading library: {e}")
        st.session_state.library = []

# Save library data to file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Add a book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': int(publication_year),
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove a book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        st.rerun()
    else:
        st.warning("Book index is invalid.")

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower().strip()
    if not search_term:
        st.warning("Please enter a search term.")
        return
    
    results = [book for book in st.session_state.library if search_term in book[search_by.lower()].lower()]
    st.session_state.search_results = results

# Load library data
load_library()

# Sidebar navigation
st.sidebar.title("📚 Navigation")
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    st.sidebar.lottie(lottie_book, height=200, key="book_animation")

nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books"])
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# Application header
st.title("📚 Personal Library Manager")

# Handle views
if st.session_state.current_view == "add_book":
    st.subheader("🗃️ Add a New Book")
    with st.form(key='add_book_form'):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Other"])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        
        if st.form_submit_button("Add Book") and title and author:
            add_book(title, author, publication_year, genre, read_status)
    
    if st.session_state.book_added:
        st.success("Book added successfully!")
        st.balloons()
        st.session_state.book_added = False

elif st.session_state.current_view == "view_library":
    st.subheader("📚 Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove", key=f"remove_{i}"):
                    remove_book(i)
            with col2:
                new_status = not book['read_status']
                if st.button("Toggle Read Status", key=f"status_{i}"):
                    st.session_state.library[i]['read_status'] = new_status
                    save_library()
                    st.rerun()

elif st.session_state.current_view == "search_books":
    st.subheader("🔍 Search Books")
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"]).lower()
    search_term = st.text_input("Enter search term:")
    if st.button("Search"):
        search_books(search_term, search_by)
    
    if st.session_state.search_results:
        for book in st.session_state.search_results:
            st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
    elif search_term:
        st.warning("No books found matching your search.")
