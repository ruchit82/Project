# -*- coding: utf-8 -*-
"""house_help_app.py"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configure file paths
EXCEL_FILE = 'house_helps.xlsx'
UPLOADS_DIR = 'uploads'

# User authentication
USER_CREDENTIALS = {"admin": "password123"}  # Simple dictionary for username and password

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# Create Excel file if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        'name', 'age', 'gender', 'address', 'contact',
        'experience', 'photo_path', 'rate', 'registration_date'
    ])
    df.to_excel(EXCEL_FILE, index=False)

# Apply custom CSS for styling
st.markdown("""
    <style>
        /* Background and header styling */
        .main {
            background-color: #f7f9fc;
        }
        h1, h2, h3 {
            color: #2b3e50;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stRadio>div {
            font-size: 16px;
        }
        /* Sidebar styling */
        .css-1y0tads {
            background-color: #2b3e50;
        }
        .css-1y0tads h1 {
            color: #f7f9fc;
        }
        .css-1y0tads a {
            color: #f7f9fc;
        }
    </style>
""", unsafe_allow_html=True)

# Function to register a helper
def register_helper():
    st.subheader("🔄 Register New Helper")

    # Form for helper registration
    with st.form(key='register_form'):
        name = st.text_input("👤 Name")
        age = st.number_input("📅 Age", min_value=18, max_value=100)
        gender = st.radio("⚥ Gender", ['Male', 'Female', 'Other'])
        address = st.text_area("📍 Address")
        contact = st.text_input("📞 Contact Number")
        experience = st.number_input("💼 Experience (in years)", min_value=0)
        rate = st.number_input("💵 Rate per Hour", min_value=0.0)
        photo = st.file_uploader("🖼️ Upload Photo", type=["jpg", "png", "jpeg"])
        submit_button = st.form_submit_button(label="Register Helper")

        if submit_button:
            try:
                if photo is not None:
                    photo_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name}"
                    photo_path = os.path.join(UPLOADS_DIR, photo_filename)
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())
                else:
                    photo_path = "No photo uploaded"

                registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'address': address,
                    'contact': contact,
                    'experience': experience,
                    'rate': rate,
                    'registration_date': registration_date,
                    'photo_path': photo_path
                }

                df = pd.read_excel(EXCEL_FILE)
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                df.to_excel(EXCEL_FILE, index=False)

                st.success("✅ Registration successful!")
            except Exception as e:
                st.error(f"❌ Error during registration: {str(e)}")

# Function to search helpers by rate
def search_helpers():
    st.subheader("🔍 Search Helpers by Rate")

    max_price = st.number_input("💵 Enter Max Rate to filter helpers", min_value=0.0)
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

# Function to handle Excel file download with authentication
def download_excel():
    st.subheader("📥 Download Excel File")

    with st.form(key='login_form'):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        login_button = st.form_submit_button(label="Login")

        if login_button:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.success("✅ Login successful!")
                with open(EXCEL_FILE, "rb") as file:
                    st.download_button(
                        label="📂 Download Excel File",
                        data=file,
                        file_name="house_helps.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("❌ Invalid username or password")

# Main Streamlit UI
def main():
    st.title("🏠 House Helper Management System")

    # Sidebar Navigation
    menu = st.sidebar.radio(
        "📋 Choose an Option",
        ["Register Helper", "Search Helpers", "Download Excel File"]
    )

    if menu == "Register Helper":
        register_helper()
    elif menu == "Search Helpers":
        search_helpers()
    elif menu == "Download Excel File":
        download_excel()

# Run the app
if __name__ == '__main__':
    main()
