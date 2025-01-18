import streamlit as st
import os
from google.cloud import firestore
from datetime import datetime
from google.oauth2 import service_account

# Load Firebase credentials from Streamlit secrets
firebase_credentials = st.secrets["firebase"]

# Initialize Firebase
credentials = service_account.Credentials.from_service_account_info(firebase_credentials)
db = firestore.Client(credentials=credentials, project=firebase_credentials["project_id"])

# Function to insert a bookmark into Firestore
def insert_bookmark(link, description, keywords, category):
    bookmark_data = {
        "link": link,
        "description": description,
        "keywords": keywords,
        "category": category,
        "date_added": datetime.utcnow()
    }
    db.collection("bookmarks").add(bookmark_data)

# Function to retrieve bookmarks by category
def get_bookmarks_by_category(category):
    try:
        bookmarks = (
            db.collection("bookmarks")
            .where("category", "==", category)
            .order_by("date_added")
            .stream()
        )
        return [doc.to_dict() for doc in bookmarks]
    except Exception as e:
        st.error("Error fetching bookmarks. Ensure the required Firestore index exists.")
        st.error(str(e))
        return []

# Function to display bookmarks in a card style
def display_bookmarks(bookmarks):
    if not bookmarks:
        st.info("No bookmarks found.")
        return

    for bookmark in bookmarks:
        st.markdown(f"""
        <div style="background-color: #f4f4f9; padding: 15px; margin: 10px 0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4 style="font-weight: bold; color: #2c3e50;">{bookmark['description']}</h4>
            <p><a href="{bookmark['link']}" target="_blank" style="color: #2980b9; font-weight: bold;">Visit Link</a></p>
            <p style="color: #2c3e50;"><strong>Keywords:</strong> {bookmark['keywords']}</p>
            <p style="color: #2c3e50;"><strong>Category:</strong> {bookmark['category']}</p>
        </div>
        """, unsafe_allow_html=True)

# Streamlit UI
st.title("💾 Bookmark Manager")
st.sidebar.header("📚 Options")

# Main menu
menu = st.sidebar.radio("Choose an action", ["Insert Bookmark", "View Bookmarks"])

if menu == "Insert Bookmark":
    st.header("🔖 Insert a Bookmark")
    link = st.text_input("Enter the bookmark link:", placeholder="https://example.com")
    description = st.text_input("Enter a description:", placeholder="A brief description of the bookmark")
    keywords = st.text_input("Enter keywords (comma-separated):", placeholder="keyword1, keyword2")
    category = st.selectbox(
        "Select a category:",
        ["Code-article", "Food", "Sport", "Junk", "Entertainment", "Website", "Any-article", "YouTube"]
    )
    
    if st.button("Add Bookmark", key="add"):
        if link and description and keywords and category:
            insert_bookmark(link, description, keywords.split(","), category)
            st.success("✅ Bookmark added successfully!")
        else:
            st.error("❌ Please fill out all fields.")

elif menu == "View Bookmarks":
    st.header("👀 View Bookmarks by Category")
    selected_category = st.selectbox(
        "Select a category to view bookmarks:",
        ["Code-article", "Food", "Sport", "Junk", "Entertainment", "Website", "Any-article", "YouTube"]
    )
    
    if st.button("View Bookmarks", key="view"):
        bookmarks = get_bookmarks_by_category(selected_category)
        display_bookmarks(bookmarks)
