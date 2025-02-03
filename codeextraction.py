import re
import pandas as pd
from PyPDF2 import PdfReader
import os
import streamlit as st
from io import BytesIO

def extract_codes_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    codes = re.findall(r"IT([A-Z]+\d+)\.(?:JPG|jpg)", text)  # Removing 'IT'
    return codes

def append_to_excel(data, file_name="Extracted_Data.xlsx"):
    if os.path.exists(file_name):
        existing_data = pd.read_excel(file_name)
        combined_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        combined_data = data
    combined_data.to_excel(file_name, index=False)

def clear_excel(file_name="Extracted_Data.xlsx"):
    if os.path.exists(file_name):
        os.remove(file_name)

def create_download_link(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False, engine="openpyxl")
    processed_data = output.getvalue()
    return processed_data

def vlookup_weight(df_recent, weight_file="/mnt/data/weight.xlsx"):
    weight_df = pd.read_excel(weight_file)
    weight_df.columns = ['Code', 'Weight', 'Size', 'Qty']  # Ensure proper column names
    merged_data = df_recent.merge(weight_df, on='Code', how='left')
    return merged_data

def main():
    st.sidebar.title("📋 Navigation")
    options = ["Home", "Upload PDF", "View and Download Data", "Manage Data"]
    choice = st.sidebar.radio("Go to:", options)

    if choice == "Home":
        st.title("📄 PDF Data Extractor and Excel Manager")
        st.write("Welcome to the **PDF Data Extractor** tool. This app helps you:")
        st.markdown("""
        - Extract image codes from PDF files.
        - Manage the extracted data in an Excel sheet.
        - Download the data as a full history or recent extraction.
        - Clear old extraction history if needed.
        """)
        st.image("https://via.placeholder.com/800x200?text=PDF+Data+Extractor", caption="Extract and Manage Data Easily")

    elif choice == "Upload PDF":
        st.title("📤 Upload PDF Files")
        uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

        if uploaded_files:
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
                df_recent = vlookup_weight(df_recent)  # Merge weight, size, qty
                
                st.success("✅ Extraction Complete!")
                st.write("### Extracted Data (Recent):")
                st.dataframe(df_recent)

                append_to_excel(df_recent)
                st.success("📊 Data successfully appended to **Extracted_Data.xlsx**!")
                st.session_state["recent_data"] = df_recent
            else:
                st.warning("⚠️ No valid codes were found in the uploaded PDFs.")

    elif choice == "View and Download Data":
        st.title("📥 View and Download Data")
        if os.path.exists("Extracted_Data.xlsx"):
            excel_data = pd.read_excel("Extracted_Data.xlsx")
            st.write("### Current Data in Excel:")
            st.dataframe(excel_data)
            
            st.markdown("#### Download Options:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download Full History"):
                    processed_data = create_download_link(excel_data)
                    st.download_button("Click to Download Full History", data=processed_data, file_name="Extracted_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            with col2:
                if "recent_data" in st.session_state:
                    recent_data = st.session_state["recent_data"]
                    processed_recent = create_download_link(recent_data)
                    st.download_button("Click to Download Recent Data", data=processed_recent, file_name="Recent_Extraction.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("⚠️ No recent data available for download.")
        else:
            st.warning("⚠️ No data available. Please upload and extract data first.")

    elif choice == "Manage Data":
        st.title("🗑️ Manage Data")
        if st.button("🗑️ Clear Old Extraction History"):
            clear_excel()
            st.success("✅ Old extraction history cleared successfully.")
        else:
            st.info("Click the button above to clear all data.")

if __name__ == "__main__":
    if "recent_data" not in st.session_state:
        st.session_state["recent_data"] = None
    main()
