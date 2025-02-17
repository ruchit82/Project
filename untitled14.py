# -*- coding: utf-8 -*-
"""Untitled14.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aHPwHTOHyDChtT8tTnmoHPKD_f39w-iK
"""
import streamlit as st
import pandas as pd
import datetime
import requests
from io import BytesIO
from fpdf import FPDF

# Google Sheets Information
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Jwx4TntDxlwghFn_eC_NgooXlpvR6WTDdvWy4PO0zgk/export?format=csv&gid="

SHEET_IDS = {
    "salesperson_inventory": "2076018430",  # GID for salesperson inventory
    "factory_inventory": "0"  # GID for factory inventory
}

# Function to Load Data from Google Sheets
@st.cache_data
def load_data(sheet_gid):
    try:
        url = GOOGLE_SHEET_URL + sheet_gid
        df = pd.read_csv(url)
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')  # Ensure DATE is datetime
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to get aged stock (more than 15 days old)
def get_aged_stock(df):
    today = datetime.date.today()
    aged_stock = df[df['DATE'].dt.date < (today - datetime.timedelta(days=15))]
    return aged_stock

# Function to generate Excel report
def generate_excel(df, file_name):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
    buffer.seek(0)
    return buffer

# Function to generate PDF report
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Inventory Report", ln=True, align="C")
    
    # Add the column names as header
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for col in df.columns:
        pdf.cell(30, 10, col, border=1)
    pdf.ln(10)
    
    # Add rows
    for _, row in df.iterrows():
        for value in row:
            pdf.cell(30, 10, str(value), border=1)
        pdf.ln(10)
    
    return pdf.output(dest='S')

# App Title and Sidebar Navigation
st.sidebar.title("📊 Inventory App")
page = st.sidebar.radio("🔍 Navigate to", ["Home", "Dashboard", "Salesperson Inventory", "Factory Inventory", "Aged Stock"])

# Refresh Button (To Reload Data)
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.success("Data refreshed successfully!")

# Home Page
if page == "Home":
    st.title("🏠 Welcome to the Inventory Management App")
    st.write("""
    - 📊 **Dashboard:** View key inventory statistics.  
    - 🚛 **Salesperson Inventory:** Check stock assigned to salespersons.  
    - 🏭 **Factory Inventory:** Monitor stock available in the factory.  
    - 🔄 **Use the refresh button** to get the latest data.
    """)

# Dashboard Page
elif page == "Dashboard":
    st.title("📈 Stock Inventory Dashboard")

    df_sales = load_data(SHEET_IDS["salesperson_inventory"])
    df_factory = load_data(SHEET_IDS["factory_inventory"])

    if not df_sales.empty and not df_factory.empty:
        # Overall Inventory Statistics
        total_pcs = df_sales["PCS"].sum() + df_factory["PCS"].sum()
        total_wt = df_sales["WT"].sum() + df_factory["WT"].sum()
        st.subheader("📊 Overall Inventory Statistics")
        col1, col2 = st.columns(2)
        col1.metric("📦 Total Pieces", total_pcs)
        col2.metric("⚖️ Total Weight", total_wt)

        # Salesperson Inventory Statistics
        salesperson_pcs = df_sales["PCS"].sum()
        salesperson_wt = df_sales["WT"].sum()
        st.subheader("🚛 Salesperson Inventory Statistics")
        col3, col4 = st.columns(2)
        col3.metric("📦 Salesperson Pieces", salesperson_pcs)
        col4.metric("⚖️ Salesperson Weight", salesperson_wt)

        # Factory Inventory Statistics
        factory_pcs = df_factory["PCS"].sum()
        factory_wt = df_factory["WT"].sum()
        st.subheader("🏭 Factory Inventory Statistics")
        col5, col6 = st.columns(2)
        col5.metric("📦 Factory Pieces", factory_pcs)
        col6.metric("⚖️ Factory Weight", factory_wt)
        
        # Salesperson vs Factory comparison
        salesperson_stock = df_sales.groupby("Category")["PCS"].sum()
        factory_stock = df_factory.groupby("Category")["PCS"].sum()
        st.subheader("📊 Salesperson vs Factory Stock")
        st.bar_chart([salesperson_stock, factory_stock], width=700)

        # Visualization: Stock Distribution Over Time
        st.subheader("📅 Stock Distribution Over Time")
        combined_df = pd.concat([df_sales, df_factory])
        st.line_chart(combined_df.groupby(combined_df["DATE"].dt.date)["PCS"].sum())
    else:
        st.warning("⚠️ No data available! Please check your Google Sheet link.")

# Salesperson Inventory Page
elif page == "Salesperson Inventory":
    st.title("🚛 Salesperson Inventory")

    df_sales = load_data(SHEET_IDS["salesperson_inventory"])
    if not df_sales.empty:
        st.dataframe(df_sales)
        
        # Search functionality
        search_term = st.text_input("Search Inventory")
        if search_term:
            df_sales = df_sales[df_sales['Category'].str.contains(search_term, case=False, na=False)]
        
        # Filter options
        category_filter = st.selectbox("Filter by Category", df_sales['Category'].unique())
        df_sales_filtered = df_sales[df_sales['Category'] == category_filter] if category_filter else df_sales
        st.dataframe(df_sales_filtered)
        
        # Download buttons for Excel & PDF
        st.download_button("📥 Download Salesperson Inventory (Excel)", generate_excel(df_sales, "salesperson_inventory.xlsx"), "salesperson_inventory.xlsx")
        st.download_button("📥 Download Salesperson Inventory (PDF)", generate_pdf(df_sales), "salesperson_inventory.pdf")
    else:
        st.warning("⚠️ No data available!")

# Factory Inventory Page
elif page == "Factory Inventory":
    st.title("🏭 Factory Inventory")

    df_factory = load_data(SHEET_IDS["factory_inventory"])
    if not df_factory.empty:
        st.dataframe(df_factory)
        
        # Search functionality
        search_term = st.text_input("Search Inventory")
        if search_term:
            df_factory = df_factory[df_factory['Category'].str.contains(search_term, case=False, na=False)]
        
        # Filter options
        category_filter = st.selectbox("Filter by Category", df_factory['Category'].unique())
        df_factory_filtered = df_factory[df_factory['Category'] == category_filter] if category_filter else df_factory
        st.dataframe(df_factory_filtered)
        
        # Download buttons for Excel & PDF
        st.download_button("📥 Download Factory Inventory (Excel)", generate_excel(df_factory, "factory_inventory.xlsx"), "factory_inventory.xlsx")
        st.download_button("📥 Download Factory Inventory (PDF)", generate_pdf(df_factory), "factory_inventory.pdf")
    else:
        st.warning("⚠️ No data available!")

# Aged Stock Page
elif page == "Aged Stock":
    st.title("⏳ Aged Stock (More than 15 Days)")

    df_sales = load_data(SHEET_IDS["salesperson_inventory"])
    df_factory = load_data(SHEET_IDS["factory_inventory"])

    if not df_sales.empty and not df_factory.empty:
        # Calculate Aged Stock
        salesperson_aged_stock = get_aged_stock(df_sales)
        factory_aged_stock = get_aged_stock(df_factory)

        if not salesperson_aged_stock.empty:
            st.subheader("🧑‍💼 Salesperson Aged Stock")
            st.dataframe(salesperson_aged_stock)

        if not factory_aged_stock.empty:
            st.subheader("🏭 Factory Aged Stock")
            st.dataframe(factory_aged_stock)
    else:
        st.warning("⚠️ No data available!")
