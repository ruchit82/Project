# -*- coding: utf-8 -*-
"""House Helper Management System"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File Paths and User Credentials
EXCEL_FILE = 'house_helps.xlsx'
UPLOADS_DIR = 'uploads'
USER_CREDENTIALS = {"admin": "password123"}  # Simple dictionary for authentication

# Ensure the uploads directory exists
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# Create the Excel file if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        'name', 'age', 'gender', 'address', 'contact',
        'experience', 'photo_path', 'rate', 'registration_date'
    ])
    df.to_excel(EXCEL_FILE, index=False)

# Function: Register Helper
def register_helper():
    st.subheader("📝 Register New Helper")

    name = st.text_input("Enter Name:")
    age = st.number_input("Enter Age:", min_value=18, max_value=100)
    gender = st.selectbox("Select Gender:", ['Male', 'Female', 'Other'])
    address = st.text_area("Enter Address:")
    contact = st.text_input("Enter Contact Number:")
    experience = st.number_input("Enter Experience (in years):", min_value=0)
    rate = st.number_input("Enter Rate per Hour:", min_value=0.0)
    photo = st.file_uploader("Upload Photo", type=["jpg", "png", "jpeg"])

    if st.button("Register Helper"):
        try:
            if photo is not None:
                photo_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name}"
                photo_path = os.path.join(UPLOADS_DIR, photo_filename)
                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())
            else:
                photo_path = "No photo uploaded"

            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_data = {
                'name': name, 'age': age, 'gender': gender, 'address': address,
                'contact': contact, 'experience': experience, 'rate': rate,
                'photo_path': photo_path, 'registration_date': registration_date
            }

            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)

            st.success("✅ Registration successful!")
        except Exception as e:
            st.error(f"❌ Error during registration: {str(e)}")

# Function: Search Helpers by Rate
def search_helpers():
    st.subheader("🔍 Search Helpers by Rate")

    max_price = st.number_input("Enter Max Rate to Filter Helpers:", min_value=0.0)
    if st.button("Search"):
        try:
            df = pd.read_excel(EXCEL_FILE)
            filtered_df = df[df['rate'] <= max_price]

            if filtered_df.empty:
                st.warning("⚠️ No helpers found with the given criteria.")
            else:
                st.dataframe(filtered_df[['name', 'age', 'gender', 'rate']])
        except Exception as e:
            st.error(f"❌ Error during search: {str(e)}")

# Function: Download Excel File
def download_excel():
    st.subheader("📥 Download Excel File")

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.success("✅ Login successful!")

            if os.path.exists(EXCEL_FILE):
                try:
                    df = pd.read_excel(EXCEL_FILE)
                    file_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📂 Download Excel File",
                        data=file_data,
                        file_name="house_helps.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ Error while preparing the file for download: {str(e)}")
            else:
                st.error("❌ Excel file not found. Please ensure it exists.")
        else:
            st.error("❌ Invalid username or password.")

# Main Streamlit Application
def main():
    st.set_page_config(
        page_title="House Helper Management System",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .css-18e3th9 { background-color: #ffffff; }
    .css-1d391kg { color: #007bff; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏠 House Helper Management System")
    st.sidebar.header("📋 Navigation")

    menu = st.sidebar.radio(
        "Choose an Option:",
        ["Register Helper", "Search Helpers", "Download Excel File"]
    )

    if menu == "Register Helper":
        register_helper()
    elif menu == "Search Helpers":
        search_helpers()
    elif menu == "Download Excel File":
        download_excel()

# Run the Streamlit App
if __name__ == '__main__':
    main()
