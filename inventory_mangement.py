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
from fpdf import FPDF  # Import FPDF for PDF generation

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
    
    # Add a search bar for the Aged Stock page
    search_query_aged = st.text_input("Search Aged Stock")
    
    # Add inventory selection option
    inventory_option_aged = st.selectbox("Select Inventory Data for Aged Stock", ["Sales Inventory", "Factory Inventory", "Both"])
    
    # Filter data based on the selected inventory option
    if inventory_option_aged == "Sales Inventory":
        aged_df = sales_df.copy()
    elif inventory_option_aged == "Factory Inventory":
        aged_df = factory_df.copy()
    else:
        aged_df = pd.concat([sales_df, factory_df], ignore_index=True)
    
    # Filter out items marked as "out" (delivered)
    aged_df = aged_df[~aged_df['DELIVERED'].astype(str).str.lower().eq('out')]
    
    # Calculate the age of each item (days since DATE)
    aged_df['AGE'] = (datetime.datetime.now() - aged_df['DATE']).dt.days
    
    # Filter items that have been in inventory for more than 10 days
    aged_stock = aged_df[aged_df['AGE'] > 10]
    
    # Apply search filter (if search query is provided)
    if search_query_aged:
        aged_stock = aged_stock[aged_stock.astype(str).apply(lambda x: x.str.contains(search_query_aged, case=False, na=False)).any(axis=1)]
    
    # Display the aged stock
    st.write(f"Total Aged Stock Items: {len(aged_stock)}")
    
    # Show a breakdown of aged stock by category
    st.write("Aged Stock by Category:")
    aged_stock_by_category = aged_stock.groupby('CATEGORY').size().reset_index(name='Count')
    st.dataframe(aged_stock_by_category)
    
    # Display the full aged stock dataframe
    st.dataframe(aged_stock)

# Inventory Data Page
elif page == "Inventory Data":
    clear_page()
    st.title("Inventory Data")
    
    # Search Input
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
    
    # Debug: Display the first few rows of the data
    st.write("First few rows of the data:", sales_df.head())
    
    # Debug: Check for missing values in 'DATE' and 'WT'
    st.write("Missing values in 'DATE':", sales_df['DATE'].isnull().sum())
    st.write("Missing values in 'WT':", sales_df['WT'].isnull().sum())
    
    # Debug: Check for infinite values in 'WT'
    st.write("Infinite values in 'WT':", np.isinf(sales_df['WT']).sum())
    
    # Clean the data: Drop rows with missing or invalid values
    sales_df_clean = sales_df.dropna(subset=['DATE', 'WT'])  # Drop rows with missing DATE or WT
    sales_df_clean = sales_df_clean[sales_df_clean['WT'] > 0]  # Ensure WT is positive
    
    # Debug: Display the cleaned data
    st.write("Cleaned data:", sales_df_clean.head())
    
    # Check if there is enough data for forecasting
    if len(sales_df_clean) == 0:
        st.error("No valid data available for forecasting.")
    else:
        # Prepare data for forecasting
        sales_df_clean['Day'] = (sales_df_clean['DATE'] - sales_df_clean['DATE'].min()).dt.days
        X = sales_df_clean[['Day']].values  # Convert to NumPy array
        y = sales_df_clean['WT'].values  # Convert to NumPy array
        
        # Debug: Display the shape of X and y
        st.write("Shape of X:", X.shape)
        st.write("Shape of y:", y.shape)
        
        # Check for finite values in X and y
        if not np.isfinite(X).all() or not np.isfinite(y).all():
            st.error("Data contains non-finite values. Please clean the data.")
        else:
            # Fit the Linear Regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict for the next 30 days
            future_days = np.array([[i] for i in range(X.max() + 1, X.max() + 31)])  # X is now a NumPy array
            future_predictions = model.predict(future_days)
            
            # Debug: Display the future predictions
            st.write("Future predictions:", future_predictions)
            
            # Create a DataFrame for the forecast
            forecast_df = pd.DataFrame({"Day": future_days.flatten(), "Predicted WT": future_predictions})
            
            # Debug: Display the forecast DataFrame
            st.write("Forecast DataFrame:", forecast_df)
            
            # Plot the forecast
            fig = px.line(forecast_df, x='Day', y='Predicted WT', title="Stock Prediction for Next 30 Days")
            st.plotly_chart(fig)

# Reports Page
elif page == "Reports":
    clear_page()
    st.title("Scheduled and Manual Reports")

    # Function to generate the report as a PDF
    def generate_pdf_report():
        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add Dashboard Data to the PDF
        pdf.cell(200, 10, txt="Dashboard Summary", ln=True, align="C")
        total_sales_weight = sales_df['WT'].sum()
        total_factory_weight = factory_df['WT'].sum()
        overall_weight = total_sales_weight + total_factory_weight
        pdf.cell(200, 10, txt=f"- Total Sales Weight (WT): {total_sales_weight}", ln=True)
        pdf.cell(200, 10, txt=f"- Total Factory Stock Weight (WT): {total_factory_weight}", ln=True)
        pdf.cell(200, 10, txt=f"- Overall Inventory Weight (WT): {overall_weight}", ln=True)

        # Add Aged Stock Data to the PDF
        pdf.cell(200, 10, txt="Aged Stock Summary", ln=True, align="C")
        aged_df = pd.concat([sales_df, factory_df], ignore_index=True)
        aged_df = aged_df[~aged_df['DELIVERED'].astype(str).str.lower().eq('out')]
        aged_df['AGE'] = (datetime.datetime.now() - aged_df['DATE']).dt.days
        aged_stock = aged_df[aged_df['AGE'] > 10]
        pdf.cell(200, 10, txt=f"- Total Aged Stock Items: {len(aged_stock)}", ln=True)

        # Add Aged Stock by Category to the PDF
        pdf.cell(200, 10, txt="Aged Stock by Category:", ln=True)
        aged_stock_by_category = aged_stock.groupby('CATEGORY').size().reset_index(name='Count')
        for _, row in aged_stock_by_category.iterrows():
            pdf.cell(200, 10, txt=f"- {row['CATEGORY']}: {row['Count']}", ln=True)

        # Add the entire Aged Stock Data to the PDF
        pdf.cell(200, 10, txt="Full Aged Stock Data:", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        for _, row in aged_stock.iterrows():
            pdf.cell(200, 10, txt=f"Design No: {row['DESIGN NO']}, Category: {row['CATEGORY']}, Weight: {row['WT']}, Age: {row['AGE']} days", ln=True)

        # Save the PDF to a BytesIO object
        pdf_output = BytesIO()
        pdf_output.write(pdf.output(dest='S').encode('latin-1'))  # Write PDF content to BytesIO
        pdf_output.seek(0)
        return pdf_output

    # Display the report when the "Generate Report" button is clicked
    if st.button("Generate Report"):
        pdf_output = generate_pdf_report()
        st.success("Report generated successfully!")
        st.download_button(
            label="Download Report as PDF",
            data=pdf_output,
            file_name="inventory_report.pdf",
            mime="application/pdf"
        )

    # Email functionality (optional)
    def send_report(receiver_email):
        sender_email = "ruchitsanap00@gmail.com"
        subject = "Stock Report"
        body = "Please find the attached stock report."
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF report
        pdf_output = generate_pdf_report()
        attachment = MIMEText(pdf_output.getvalue(), 'base64', 'application/pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename="inventory_report.pdf")
        msg.attach(attachment)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("ruchitsanap00@gmail.com", "blhm mtru wcbn wqza")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        st.success("Report Sent Successfully")

    # Email input and send button
    receiver_email = st.text_input("Enter Email Address to Send Report")
    if st.button("Send Report via Email"):
        if receiver_email:
            send_report(receiver_email)
        else:
            st.error("Please enter a valid email address.")

    # Schedule reports (optional)
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
