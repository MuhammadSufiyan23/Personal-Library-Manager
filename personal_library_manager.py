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

# Load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load library data
if os.path.exists('library.json'):
    with open('library.json', 'r') as file:
        st.session_state.library = json.load(file)

# Save library data
def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file)

# Add a book
def add_book(title, author, year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.success("Book added successfully!")
    time.sleep(1)
    st.rerun()

# Remove a book
def remove_book(index):
    del st.session_state.library[index]
    save_library()
    st.success("Book removed successfully!")
    st.rerun()

# Sidebar navigation
st.sidebar.title("📚 Navigation")
nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = nav_options.lower().replace(" ", "_")

# App header
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add_book":
    st.subheader("📝 Add a New Book")
    with st.form(key='add_book_form'):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Romance", "Thriller", "Biography", "History", "Self-Help", "Poetry", "Science", "Philosophy", "Religion", "Art", "Other"])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        submit_button = st.form_submit_button("Add Book")
        if submit_button and title and author:
            add_book(title, author, year, genre, read_status)

elif st.session_state.current_view == "view_library":
    st.subheader("📖 Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books to get started!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"{book['title']} ({'Read' if book['read_status'] else 'Unread'})"):
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Year:** {book['publication_year']}")
                st.write(f"**Genre:** {book['genre']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_book(i)
                with col2:
                    new_status = not book['read_status']
                    if st.button(f"Mark as {'Read' if new_status else 'Unread'}", key=f"status_{i}"):
                        book['read_status'] = new_status
                        save_library()
                        st.rerun()

elif st.session_state.current_view == "search_books":
    st.subheader("🔍 Search Books")
    search_term = st.text_input("Enter search term:")
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    if st.button("Search") and search_term:
        results = [book for book in st.session_state.library if search_term.lower() in book[search_by.lower()].lower()]
        if results:
            for book in results:
                st.write(f"**{book['title']}** by {book['author']} ({'Read' if book['read_status'] else 'Unread'})")
        else:
            st.warning("No books found.")

elif st.session_state.current_view == "library_statistics":
    st.subheader("📊 Library Statistics")
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    unread_books = total_books - read_books
    if total_books > 0:
        st.metric("Total Books", total_books)
        st.metric("Books Read", read_books)
        st.metric("Unread Books", unread_books)
        fig = go.Figure(data=[go.Pie(labels=['Read', 'Unread'], values=[read_books, unread_books], hole=.3)])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available. Add books to see statistics.")

st.markdown("---")
st.markdown("Copyright © 2025 Muhammad Sufiyan Personal Library Manager", unsafe_allow_html=True)
