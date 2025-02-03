# -*- coding: utf-8 -*-
import re
import pandas as pd
from PyPDF2 import PdfReader
import os
import streamlit as st
from io import BytesIO

# Function to extract image codes from a PDF and clean them
def extract_codes_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    # Extract and clean codes (remove "IT" prefix)
    codes = [re.sub(r"^IT", "", code) for code in re.findall(r"(IT[A-Z]+\d+)\.(?:JPG|jpg)", text)]
    return codes

# Function to append data to an Excel file
def append_to_excel(data, file_name="Extracted_Data.xlsx"):
    if os.path.exists(file_name):
        existing_data = pd.read_excel(file_name)
        combined_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        combined_data = data
    combined_data.to_excel(file_name, index=False)

# Function to merge extracted data with weight sheet
def merge_with_weight_data(extracted_df, weight_file):
    weight_df = pd.read_excel(weight_file, sheet_name=0)  # Load weight sheet
    weight_df.rename(columns=str.strip, inplace=True)  # Remove unwanted spaces from column names
    
    # Ensure column names are correct
    if "Code" not in weight_df.columns or "Category" not in weight_df.columns or "Weight" not in weight_df.columns:
        st.error("❌ Weight sheet format is incorrect. Ensure it has 'Code', 'Category', and 'Weight' columns.")
        return extracted_df
    
    # Merge extracted data with weight data
    merged_df = extracted_df.merge(weight_df, on="Code", how="left")
    return merged_df

# Function to create a download link
def create_download_link(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

# Streamlit App
def main():
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    options = ["Home", "Upload PDF", "View and Download Data", "Manage Data"]
    choice = st.sidebar.radio("Go to:", options)

    # Home Page
    if choice == "Home":
        st.title("📄 PDF Data Extractor and Excel Manager")
        st.write("Welcome to the **PDF Data Extractor** tool. This app helps you:")
        st.markdown("""
        - Extract image codes from PDF files.
        - Match extracted codes with weight sheet data.
        - Manage and download the extracted data in an Excel sheet.
        - Clear old extraction history if needed.
        """)

    # Upload PDF Page
    elif choice == "Upload PDF":
        st.title("📤 Upload PDF Files")
        uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)
        weight_file = st.file_uploader("📊 Upload Weight Data (Excel)", type="xlsx")

        if uploaded_files and weight_file:
            recent_data = []

            for uploaded_file in uploaded_files:
                st.write(f"📂 Processing: {uploaded_file.name}")
                codes = extract_codes_from_pdf(uploaded_file)
                if codes:
                    party_name = os.path.splitext(uploaded_file.name)[0]
                    recent_data.extend([(party_name, code) for code in codes])
                else:
                    st.warning(f"⚠️ No valid codes found in {uploaded_file.name}")

            if recent_data:
                df_recent = pd.DataFrame(recent_data, columns=["Party Name", "Code"])
                
                # Merge extracted data with weight data
                merged_df = merge_with_weight_data(df_recent, weight_file)
                
                # Display extracted data
                st.success("✅ Extraction & Merge Complete!")
                st.write("### Extracted Data with Weights:")
                st.dataframe(merged_df)

                # Append the merged data to the Excel sheet
                append_to_excel(merged_df)
                st.success("📊 Data successfully saved in **Extracted_Data.xlsx**!")

                # Store recent data globally for download
                st.session_state["recent_data"] = merged_df

            else:
                st.warning("⚠️ No valid codes were found in the uploaded PDFs.")

    # View and Download Data Page
    elif choice == "View and Download Data":
        st.title("📥 View and Download Data")
        if os.path.exists("Extracted_Data.xlsx"):
            excel_data = pd.read_excel("Extracted_Data.xlsx")
            st.write("### Current Data in Excel:")
            st.dataframe(excel_data)

            # Download options
            st.markdown("#### Download Options:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download Full Data"):
                    processed_data = create_download_link(excel_data)
                    st.download_button(
                        label="Click to Download Full Data",
                        data=processed_data,
                        file_name="Extracted_Data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            with col2:
                if "recent_data" in st.session_state:
                    recent_data = st.session_state["recent_data"]
                    processed_recent = create_download_link(recent_data)
                    st.download_button(
                        label="Click to Download Recent Data",
                        data=processed_recent,
                        file_name="Recent_Extraction.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ No recent data available for download.")

    # Manage Data Page
    elif choice == "Manage Data":
        st.title("🗑️ Manage Data")
        if st.button("🗑️ Clear Old Extraction History"):
            if os.path.exists("Extracted_Data.xlsx"):
                os.remove("Extracted_Data.xlsx")
            st.success("✅ Old extraction history cleared successfully.")

# Run the app
if __name__ == "__main__":
    if "recent_data" not in st.session_state:
        st.session_state["recent_data"] = None
    main()
