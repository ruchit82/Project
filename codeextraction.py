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

def vlookup_weight(extracted_data, weight_file):
    weight_df = pd.read_excel(weight_file)
    weight_df.columns = ['Code', 'Weight']  # Ensure columns match
    merged_data = extracted_data.merge(weight_df, on='Code', how='left')
    return merged_data

def create_download_link(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

def main():
    st.sidebar.title("📋 Navigation")
    choice = st.sidebar.radio("Go to:", ["Home", "Upload PDF", "Upload Weight File", "View and Download Data"])
    
    if choice == "Home":
        st.title("📄 PDF Data Extractor and Excel Manager")
        st.markdown("Extract codes, match weights, and manage Excel data.")
    
    elif choice == "Upload PDF":
        st.title("📤 Upload PDF Files")
        uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        
        if uploaded_files:
            recent_data = []
            for uploaded_file in uploaded_files:
                codes = extract_codes_from_pdf(uploaded_file)
                party_name = os.path.splitext(uploaded_file.name)[0]
                recent_data.extend([(party_name, code) for code in codes])
            
            if recent_data:
                df_recent = pd.DataFrame(recent_data, columns=["Party Name", "Code"])
                st.session_state["recent_data"] = df_recent
                append_to_excel(df_recent)
                st.success("✅ Data Extracted Successfully!")
                st.dataframe(df_recent)
    
    elif choice == "Upload Weight File":
        st.title("📥 Upload Weight Excel File")
        weight_file = st.file_uploader("Upload Weight Excel", type=["xlsx"])
        if weight_file and "recent_data" in st.session_state:
            df_recent = st.session_state["recent_data"]
            merged_data = vlookup_weight(df_recent, weight_file)
            st.session_state["final_data"] = merged_data
            st.success("✅ Weight Data Merged Successfully!")
            st.dataframe(merged_data)
    
    elif choice == "View and Download Data":
        st.title("📥 View and Download Data")
        if "final_data" in st.session_state:
            final_data = st.session_state["final_data"]
            st.dataframe(final_data)
            processed_data = create_download_link(final_data)
            st.download_button("Download Final Data", data=processed_data, file_name="Final_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("⚠️ No final data available. Upload and process files first.")

if __name__ == "__main__":
    if "recent_data" not in st.session_state:
        st.session_state["recent_data"] = None
    if "final_data" not in st.session_state:
        st.session_state["final_data"] = None
    main()
