# -*- coding: utf-8 -*-
"""Untitled13.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1R9miFoGSV0UfdnL0CEQEgBBunBn4X8ov
"""

import re
import pandas as pd
from PyPDF2 import PdfReader
import os
import streamlit as st

# Function to extract image codes from a PDF
def extract_codes_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    # Extract codes using regex
    codes = re.findall(r"(IT[A-Z]+\d+)\.(?:JPG|jpg)", text)
    return codes

# Function to append data to an Excel file
def append_to_excel(data, file_name="Extracted_Data.xlsx"):
    # Check if file exists
    if os.path.exists(file_name):
        # Load existing data
        existing_data = pd.read_excel(file_name)
        # Append new data
        combined_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        # If file doesn't exist, use the new data directly
        combined_data = data
    # Save the updated data back to the file
    combined_data.to_excel(file_name, index=False)

# Streamlit app
def main():
    st.title("PDF Data Extractor and Appender")
    st.write("Upload multiple PDF files to extract codes and append data to an Excel sheet.")

    # File uploader for multiple PDFs
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        all_data = []  # Store all extracted data

        for uploaded_file in uploaded_files:
            # Process each uploaded file
            st.write(f"Processing: {uploaded_file.name}")
            codes = extract_codes_from_pdf(uploaded_file)
            if codes:
                # Extract party name from PDF file name (without extension)
                party_name = os.path.splitext(uploaded_file.name)[0]
                # Append (Party Name, Code) pairs
                all_data.extend([(party_name, code) for code in codes])
            else:
                st.warning(f"No valid codes found in {uploaded_file.name}")

        if all_data:
            # Create a DataFrame
            df = pd.DataFrame(all_data, columns=["Party Name", "Code"])

            # Show extracted data in the app
            st.write("Extracted Data:")
            st.dataframe(df)

            # Save to Excel
            append_to_excel(df)
            st.success("Data appended to Extracted_Data.xlsx successfully.")
        else:
            st.warning("No valid codes were found in the uploaded PDFs.")

# Run the app
if __name__ == "__main__":
    main()

