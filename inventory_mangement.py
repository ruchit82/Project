# -*- coding: utf-8 -*-
"""Inventory_Mangement.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tL_XZvVhlQcM57r8T5JziIGw-sql3Ph3
"""
# -*- coding: utf-8 -*-
"""Inventory_Mangement.ipynb"""

# -*- coding: utf-8 -*-
"""Inventory_Mangement.ipynb"""

import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px
import numpy as np
from io import BytesIO
from sklearn.linear_model import LinearRegression
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

# Google Sheet URLs
SALES_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Jwx4TntDxlwghFn_eC_NgooXlpvR6WTDdvWy4PO0zgk/export?format=csv&gid=2076018430"
FACTORY_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Jwx4TntDxlwghFn_eC_NgooXlpvR6WTDdvWy4PO0zgk/export?format=csv&gid=0"

# Function to load data from Google Sheets
def load_data():
    sales_df = pd.read_csv(SALES_SHEET_URL)
    factory_df = pd.read_csv(FACTORY_SHEET_URL)
    
    sales_df['DATE'] = pd.to_datetime(sales_df['DATE'], errors='coerce')
    factory_df['DATE'] = pd.to_datetime(factory_df['DATE'], errors='coerce')
    
    sales_df = sales_df[~sales_df['DELIVERED'].astype(str).str.lower().eq('out')]
    factory_df = factory_df[~factory_df['DELIVERED'].astype(str).str.lower().eq('out')]
    
    return sales_df, factory_df

# Function to extract category
def extract_category(design_no):
    categories = ["CM", "CL", "CN", "CZ", "EX", "FR", "FS", "GL", "GT", "OP", "PL", "LN", "LO", "MD", "MV", "NA", "SP", "SPE", "UN"]
    for category in categories:
        if category in design_no:
            return category
    return "Other"

# Load Data
sales_df, factory_df = load_data()

sales_df['CATEGORY'] = sales_df['DESIGN NO'].astype(str).apply(extract_category)
factory_df['CATEGORY'] = factory_df['DESIGN NO'].astype(str).apply(extract_category)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Dashboard", "Aged Stock", "Inventory Data", "Export Data", "Stock Forecast", "Reports"])

st.experimental_set_query_params(page=page)

# Clear previous pages when navigating
def clear_page():
    st.empty()

# Home Page
if page == "Home":
    clear_page()
    st.title("Welcome to ITAN Jewels Stock Inventory Management")

# Dashboard Page
elif page == "Dashboard":
    clear_page()
    st.title("Stock Inventory Dashboard")
    total_sales_weight = sales_df['WT'].sum()
    total_factory_weight = factory_df['WT'].sum()
    overall_weight = total_sales_weight + total_factory_weight
    
    st.metric("Total Sales Weight (WT)", total_sales_weight)
    st.metric("Total Factory Stock Weight (WT)", total_factory_weight)
    st.metric("Overall Inventory Weight (WT)", overall_weight)
    
    category_weight = sales_df.groupby('CATEGORY')['WT'].sum().reset_index()
    fig = px.bar(category_weight, x='CATEGORY', y='WT', title="Sales Weight by Category")
    st.plotly_chart(fig)
    
    sales_trend = sales_df.groupby('DATE')['WT'].sum().reset_index()
    fig2 = px.line(sales_trend, x='DATE', y='WT', title="Sales Trend Over Time")
    st.plotly_chart(fig2)

# Aged Stock Page
elif page == "Aged Stock":
    clear_page()
    st.title("Aged Stock Inventory")
    
    # Combine sales and factory data
    combined_df = pd.concat([sales_df, factory_df], ignore_index=True)
    
    # Filter out items marked as "out" (delivered)
    combined_df = combined_df[~combined_df['DELIVERED'].astype(str).str.lower().eq('out')]
    
    # Calculate the age of each item (days since DATE)
    combined_df['AGE'] = (datetime.datetime.now() - combined_df['DATE']).dt.days
    
    # Filter items that have been in inventory for more than 10 days
    aged_stock = combined_df[combined_df['AGE'] > 10]
    
    # Display the aged stock
    st.write(f"Total Aged Stock Items: {len(aged_stock)}")
    st.dataframe(aged_stock)


# Inventory Data Page (with search feature added here)
elif page == "Inventory Data":
    clear_page()
    st.title("Inventory Data")
    
    # Search Input Moved Here
    search_query = st.text_input("Search Inventory")

    inventory_option = st.selectbox("Select Inventory Data", ["Sales Inventory", "Factory Inventory", "Both"])
    
    if inventory_option == "Sales Inventory":
        filtered_df = sales_df[sales_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
        st.dataframe(filtered_df)
    elif inventory_option == "Factory Inventory":
        filtered_df = factory_df[factory_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
        st.dataframe(filtered_df)
    else:
        combined_df = pd.concat([sales_df, factory_df], ignore_index=True)
        filtered_df = combined_df[combined_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)]
        st.dataframe(filtered_df)

# Export Data Page
elif page == "Export Data":
    clear_page()
    st.title("Export Filtered Data")
    export_option = st.radio("Choose data to export", ["Overall Inventory", "Salesperson Inventory", "Factory Inventory"])
    
    if export_option == "Overall Inventory":
        export_df = sales_df
    elif export_option == "Salesperson Inventory":
        export_df = sales_df[sales_df['CATEGORY'] == "SP"]
    else:
        export_df = factory_df
    
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="Filtered_Inventory.csv", mime='text/csv')

# Stock Forecast Page
elif page == "Stock Forecast":
    clear_page()
    st.title("Stock Forecasting")
    sales_df['Day'] = (sales_df['DATE'] - sales_df['DATE'].min()).dt.days
    X = sales_df[['Day']]
    y = sales_df['WT']
    model = LinearRegression()
    model.fit(X, y)
    future_days = np.array([[i] for i in range(X['Day'].max() + 1, X['Day'].max() + 31)])
    future_predictions = model.predict(future_days)
    forecast_df = pd.DataFrame({"Day": future_days.flatten(), "Predicted WT": future_predictions})
    fig = px.line(forecast_df, x='Day', y='Predicted WT', title="Stock Prediction for Next 30 Days")
    st.plotly_chart(fig)

# Reports Page
elif page == "Reports":
    clear_page()
    st.title("Scheduled and Manual Reports")
    
    def send_report(receiver_email):
        sender_email = "ruchitsanap00@gmail.com"
        subject = "Stock Report"
        body = "Attached is the latest stock report."
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("ruchitsanap00@gmail.com", "blhm mtru wcbn wqza")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        st.success("Report Sent Successfully")
    
    receiver_email = st.text_input("Enter Email Address to Send Report")
    if st.button("Send Report"):
        if receiver_email:
            send_report(receiver_email)
        else:
            st.error("Please enter a valid email address.")
    
    def schedule_report():
        send_report("recipient@example.com")
    
    schedule.every().monday.at("08:00").do(schedule_report)
    st.write("Reports are automatically sent every Monday at 08:00 AM.")

# Run Scheduled Jobs in Background
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)
thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()
