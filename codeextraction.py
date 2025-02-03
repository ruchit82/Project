import re
import pandas as pd
from PyPDF2 import PdfReader
import os
import streamlit as st
from io import BytesIO

def extract_codes_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    codes = re.findall(r"IT([A-Z]+\d+)\.(?:JPG|jpg)", text)  # Extract without 'IT'
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
    return output.getvalue()

def main():
    st.sidebar.title("📋 Navigation")
    options = ["Home", "Upload PDF", "Merge with Data", "View and Download Data", "Manage Data"]
    choice = st.sidebar.radio("Go to:", options)

    if choice == "Home":
        st.title("📄 PDF Data Extractor & Data Merger")
        st.markdown("""
        - Extract image codes from PDFs (without 'IT').
        - Merge extracted data with a Weight Excel file.
        - Download the final dataset.
        """)

    elif choice == "Upload PDF":
        st.title("📤 Upload PDF Files")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            recent_data = []
            for uploaded_file in uploaded_files:
                st.write(f"📂 Processing: {uploaded_file.name}")
                codes = extract_codes_from_pdf(uploaded_file)
                if codes:
                    party_name = os.path.splitext(uploaded_file.name)[0]
                    recent_data.extend([(party_name, code) for code in codes])
                else:
                    st.warning(f"⚠️ No valid codes in {uploaded_file.name}")
            
            if recent_data:
                df_recent = pd.DataFrame(recent_data, columns=["Party Name", "Code"])
                append_to_excel(df_recent)
                st.success("✅ Data extracted & saved!")
                st.session_state["recent_data"] = df_recent

    elif choice == "Merge with Data":
        st.title("🔗 Merge Data with Weight, Size, and Qty")
        uploaded_weight = st.file_uploader("Upload Data Excel File", type=["xlsx"])
        if uploaded_weight:
            extracted_data = pd.read_excel("Extracted_Data.xlsx")
            weight_data = pd.read_excel(uploaded_weight)
            weight_data = weight_data.rename(columns={"Code": "Code", "Weight": "Weight", "Size": "Size", "Qty": "Qty"})
            merged_data = extracted_data.merge(weight_data, on="Code", how="left")
            
            st.write("### Merged Data:")
            st.dataframe(merged_data)
            st.session_state["merged_data"] = merged_data

            processed_data = create_download_link(merged_data)
            st.download_button("📥 Download Merged Data", data=processed_data, file_name="Merged_Data.xlsx")

    elif choice == "View and Download Data":
        st.title("📥 View & Download Data")
        if os.path.exists("Extracted_Data.xlsx"):
            excel_data = pd.read_excel("Extracted_Data.xlsx")
            st.dataframe(excel_data)
            processed_data = create_download_link(excel_data)
            st.download_button("📥 Download Data", data=processed_data, file_name="Extracted_Data.xlsx")
        else:
            st.warning("⚠️ No data available. Upload PDFs first.")

    elif choice == "Manage Data":
        st.title("🗑️ Manage Data")
        if st.button("🗑️ Clear Data"):
            clear_excel()
            st.success("✅ Data cleared.")

if __name__ == "__main__":
    if "recent_data" not in st.session_state:
        st.session_state["recent_data"] = None
    main()
