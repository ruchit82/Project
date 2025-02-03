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
    codes = re.findall(r"IT([A-Z]+\d+)\.(?:JPG|jpg)", text)  # Removing 'IT' prefix
    return codes

def merge_with_weight_data(extracted_df, weight_data_file):
    weight_df = pd.read_excel(weight_data_file)
    merged_df = extracted_df.merge(weight_df, left_on="Code", right_on="CODE", how="left")
    merged_df = merged_df[["Party Name", "Code", "WEIGHT", "QTY", "SIZE"]]
    merged_df.rename(columns={"WEIGHT": "Weight", "QTY": "Quantity", "SIZE": "Size"}, inplace=True)
    return merged_df

def append_to_excel(data, file_name="Final_Extracted_Data.xlsx"):
    if os.path.exists(file_name):
        existing_data = pd.read_excel(file_name)
        combined_data = pd.concat([existing_data, data], ignore_index=True)
    else:
        combined_data = data
    combined_data.to_excel(file_name, index=False)

def create_download_link(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

def main():
    st.sidebar.title("📋 Navigation")
    options = ["Home", "Upload PDF", "Upload Weight Data", "View and Download Data"]
    choice = st.sidebar.radio("Go to:", options)
    
    if choice == "Home":
        st.title("📄 PDF Data Extractor & Weight Data Merger")
        st.write("Extract codes from PDFs and merge with weight data using VLOOKUP.")
    
    elif choice == "Upload PDF":
        st.title("📤 Upload PDF Files")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        if uploaded_files:
            recent_data = []
            for uploaded_file in uploaded_files:
                st.write(f"Processing: {uploaded_file.name}")
                codes = extract_codes_from_pdf(uploaded_file)
                party_name = os.path.splitext(uploaded_file.name)[0]
                recent_data.extend([(party_name, code) for code in codes])
            
            if recent_data:
                df_recent = pd.DataFrame(recent_data, columns=["Party Name", "Code"])
                st.session_state["extracted_data"] = df_recent
                st.success("✅ Extraction Complete!")
                st.write(df_recent)
            else:
                st.warning("⚠️ No valid codes found.")
    
    elif choice == "Upload Weight Data":
        st.title("📥 Upload Weight Data File")
        weight_file = st.file_uploader("Upload the Weight Excel File", type=["xls", "xlsx"])
        
        if weight_file and "extracted_data" in st.session_state:
            extracted_df = st.session_state["extracted_data"]
            merged_df = merge_with_weight_data(extracted_df, weight_file)
            st.session_state["final_data"] = merged_df
            st.success("✅ Weight data merged successfully!")
            st.write(merged_df)
    
    elif choice == "View and Download Data":
        st.title("📥 View & Download Merged Data")
        if "final_data" in st.session_state:
            final_data = st.session_state["final_data"]
            st.write(final_data)
            processed_data = create_download_link(final_data)
            st.download_button(
                label="📥 Download Merged Data",
                data=processed_data,
                file_name="Final_Extracted_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No merged data available.")

if __name__ == "__main__":
    main()
