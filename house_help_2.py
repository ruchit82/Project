import streamlit as st
import pandas as pd
import os

# Constants
EXCEL_FILE = 'house_helps.xlsx'
USER_CREDENTIALS = {'admin': 'password123'}  # Example admin credentials

# Function: Register Helper
def register_helper():
    st.subheader("📝 Register Helper")
    
    # Icons for inputs
    name = st.text_input("👤 Enter Helper's Name")
    age = st.number_input("📅 Enter Helper's Age", min_value=18, max_value=100, step=1)
    gender = st.selectbox("⚥ Select Gender", ["Male", "Female", "Other"])
    contact = st.text_input("📞 Enter Helper's Contact Number")
    rate = st.number_input("💵 Enter Hourly Rate", min_value=1, step=1)
    address = st.text_input("📍 Enter Address")
    experience = st.number_input("💼 Enter Years of Experience", min_value=1, step=1)
    
    if st.button("📥 Register Helper"):
        if name and age and gender and contact and rate and address and experience:
            if os.path.exists(EXCEL_FILE):
                df = pd.read_excel(EXCEL_FILE)
            else:
                df = pd.DataFrame(columns=['name', 'age', 'gender', 'contact', 'rate', 'address', 'experience', 'registration_date'])

            new_helper = {
                'name': name,
                'age': age,
                'gender': gender,
                'contact': contact,
                'rate': rate,
                'address': address,
                'experience': experience,
                'registration_date': pd.to_datetime('today').strftime('%Y-%m-%d')
            }
            df = df.append(new_helper, ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            st.success(f"✅ {name} has been successfully registered as a helper!")
        else:
            st.warning("⚠️ Please fill in all the fields.")

# Function: Search Helper
def search_helper():
    st.subheader("🔍 Search Helper")
    
    contact_to_search = st.text_input("📞 Enter Helper's Contact Number")
    
    if st.button("🔍 Search Helper"):
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            helper = df[df['contact'] == contact_to_search]
            if not helper.empty:
                st.write(helper[['name', 'age', 'gender', 'contact', 'rate', 'address', 'experience', 'registration_date']])
            else:
                st.warning("⚠️ No helper found with this contact number.")
        else:
            st.error("❌ No data found. Please register helpers first.")

# Function: Admin Use (Overview, Deletion, and Download)
def admin_use():
    st.subheader("👨‍💻 Admin Panel")

    # Check if the user is logged in
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")

        if st.button("✅ Login", key="login_button"):
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("✅ Login successful!")
            else:
                st.error("❌ Invalid username or password.")
    else:
        st.write(f"👋 Welcome, {st.session_state['username']}!")
        
        # Show options once logged in
        menu = st.selectbox(
            "Choose an Admin Action:",
            ["Overview of Helpers", "Delete Helper", "Download Excel File"]
        )

        # Load the data
        df = pd.read_excel(EXCEL_FILE)

        # Overview of Helpers
        if menu == "Overview of Helpers":
            st.dataframe(df[['name', 'age', 'gender', 'rate', 'address', 'experience', 'registration_date']])

        # Delete Helper
        elif menu == "Delete Helper":
            contact_to_delete = st.text_input("📞 Enter the contact number of the helper to delete:")
            if st.button("🗑️ Delete Helper"):
                if contact_to_delete in df['contact'].values:
                    df = df[df['contact'] != contact_to_delete]
                    df.to_excel(EXCEL_FILE, index=False)
                    st.success("✅ Helper deleted successfully!")
                else:
                    st.warning("⚠️ Helper not found with this contact number.")

        # Download Excel File
        elif menu == "Download Excel File":
            try:
                file_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📂 Download Excel File",
                    data=file_data,
                    file_name="house_helps.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"❌ Error while preparing the file for download: {str(e)}")

        # Log out option
        if st.button("🚪 Log out"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.success("👋 You have logged out.")

# Main Streamlit Application
def main():
    st.set_page_config(
        page_title="House Helper Management System",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS Styling
    st.markdown("""<style>
    .main { background-color: #f8f9fa; }
    .css-18e3th9 { background-color: #ffffff; }
    .css-1d391kg { color: #007bff; font-size: 24px; font-weight: bold; }
    .stButton > button { background-color: #007bff; color: white; border-radius: 8px; padding: 12px 24px; font-size: 16px;}
    .stButton > button:hover { background-color: #0056b3;}
    .stTextInput input { background-color: #f1f1f1; border: 1px solid #007bff; border-radius: 8px;}
    .stTextArea textarea { background-color: #f1f1f1; border: 1px solid #007bff; border-radius: 8px;}
    .stSelectbox select { background-color: #f1f1f1; border: 1px solid #007bff; border-radius: 8px;}
    .stNumberInput input { background-color: #f1f1f1; border: 1px solid #007bff; border-radius: 8px;}
    .stFileUploader { background-color: #f1f1f1; border: 1px solid #007bff; border-radius: 8px;}
    .stFileUploader:hover { background-color: #e2e6ea;}
    .stTextInput input:focus { border: 2px solid #007bff;}
    .stSelectbox select:focus { border: 2px solid #007bff;}
    .stTextArea textarea:focus { border: 2px solid #007bff;}
    .stButton > button { background-color: #28a745;}
    .stButton > button:hover { background-color: #218838;}
    .stTextInput { padding: 10px; }
    .stNumberInput { padding: 10px; }
    .stSelectbox { padding: 10px; }
    .stTextArea { padding: 10px; }
    .stButton { margin-top: 10px;}
    .stFileUploader { background-color: #e9ecef; padding: 15px; border-radius: 8px; }
    .stSelectbox { background-color: #f7f8fa;}
    .stButton > button { font-size: 18px; border-radius: 12px;}
    .stFileUploader:hover { background-color: #d6d8db;}
    </style>""", unsafe_allow_html=True)

    st.title("🏠 House Helper Management System")
    st.sidebar.header("📋 Navigation")

    menu = st.sidebar.radio(
        "Choose an Option:",
        ["Register Helper", "Search Helper", "Admin Use"]
    )

    if menu == "Register Helper":
        register_helper()
    elif menu == "Search Helper":
        search_helper()
    elif menu == "Admin Use":
        admin_use()

# Run the Streamlit App
if __name__ == '__main__':
    main()
