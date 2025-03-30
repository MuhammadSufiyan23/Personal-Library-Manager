import streamlit as st 
import pandas as pd
import json
import os
from datetime import datetime
import time 
import requests
import plotly.express as px 
import plotly.graph_objects as go 
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"    
)

# Load Library Data

def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            st.session_state.library = json.load(file)
    else:
        st.session_state.library = []

def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file, indent=4)

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
    st.session_state.book_added = True

def remove_book(index):
    del st.session_state.library[index]
    save_library()
    st.session_state.book_removed = True

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres, authors, decades = {}, {}, {}
    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percentage_read': percentage_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items()))
    }

def create_visualization(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker=dict(colors=['#10B981', '#F87171'])
        )])
        fig_read_status.update_layout(title_text="Read vs Unread Books", height=400)
        st.plotly_chart(fig_read_status, use_container_width=True)
    
    if stats['genres']:
        df = pd.DataFrame({'Genre': list(stats['genres'].keys()), 'Count': list(stats['genres'].values())})
        fig_genres = px.bar(df, x='Genre', y='Count', color='Count', color_continuous_scale=px.colors.sequential.Blues)
        fig_genres.update_layout(title_text='Books by Genre', height=400)
        st.plotly_chart(fig_genres, use_container_width=True)
    
    if stats['decades']:
        df = pd.DataFrame({'Decade': [f"{decade}s" for decade in stats['decades']], 'Count': list(stats['decades'].values())})
        fig_decades = px.line(df, x='Decade', y='Count', markers=True, line_shape="spline")
        fig_decades.update_layout(title_text='Books by Decade', height=400)
        st.plotly_chart(fig_decades, use_container_width=True)

# UI Navigation
load_library()
st.sidebar.title("Navigation")
options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Library Statistics"])
st.title("Personal Library Manager")

if options == "Add Book":
    st.header("Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Technology", "History", "Fantasy"])
        read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True) == "Read"
        if st.form_submit_button("Add Book"):
            add_book(title, author, year, genre, read_status)
    if st.session_state.get("book_added"):
        st.success("Book added successfully!")
        st.session_state.book_added = False

elif options == "View Library":
    st.header("Your Library")
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.expander(f"{book['title']} by {book['author']}"):
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Publication Year:** {book['publication_year']}")
                st.write(f"**Read Status:** {'✅ Read' if book['read_status'] else '❌ Unread'}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Remove", key=f"remove_{i}"):
                        remove_book(i)
                        st.rerun()
                with col2:
                    new_status = not book['read_status']
                    label = "Mark as Read" if not book['read_status'] else "Mark as Unread"
                    if st.button(label, key=f"status_{i}"):
                        st.session_state.library[i]['read_status'] = new_status
                        save_library()
                        st.rerun()

elif options == "Library Statistics":
    st.header("Library Statistics")
    if not st.session_state.library:
        st.warning("Your library is empty. Add books to see statistics!")
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats['total_books'])
        col2.metric("Books Read", stats['read_books'])
        col3.metric("Read Percentage", f"{stats['percentage_read']:.1f}%")
        create_visualization(stats)

st.markdown("---")
st.markdown("Copyright © 2025 Muhammad Sufiyan Personal Library Manager")







 

