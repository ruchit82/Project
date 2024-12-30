# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import warnings
import io

# Suppress warnings
warnings.filterwarnings('ignore')

# Streamlit configurations
st.set_page_config(page_title="Export Sales Analysis", layout="wide", page_icon="📈")
sns.set(style="whitegrid")
st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #e9ecef; }
    h1, h2, h3 { color: #495057; }
    .block-container { padding: 2rem; }
    .css-1offfwp { background-color: #ffffff; border-radius: 15px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Export Sales Analysis Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.write("Use the options below to navigate:")
menu = st.sidebar.radio(
    "Sections",
    [
        "Upload Data",
        "Summary Statistics",
        "Time-Based Analysis",
        "Party-Based Analysis",
        "Type-Based Analysis",
        "Size-Based Analysis",
        "Design-Based Analysis",
        "Correlation Analysis",
        "Scatter & Violin Plots",
        "Search Party Rank",
    ],
)

# Upload Excel file
uploaded_file = st.sidebar.file_uploader("Upload the Export Sales Excel File", type=["xlsx", "xls"])

if uploaded_file:
    # Load data
    data = pd.read_excel(uploaded_file)
    data["DATE"] = pd.to_datetime(data["DATE"])

    # Main Dashboard Content
    if menu == "Upload Data":
        st.write("### Preview of Uploaded Data")
        st.dataframe(data.head(10))

        st.write("### Data Information")
        with st.expander("Click to view Data Information"):
            buffer = io.StringIO()
            data.info(buf=buffer)
            info_string = buffer.getvalue()
            st.text(info_string)

    elif menu == "Summary Statistics":
        st.write("### Data Summary")
        st.write(data.describe())

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Statistics for WEIGHT")
            st.write(data["WEIGHT"].describe())
        with col2:
            st.write("#### Statistics for QTY")
            st.write(data["QTY"].describe())

        st.write("### Unique Values in Categorical Columns")
        st.write(f"Unique Parties: {data['PARTY'].nunique()}")
        st.write(f"Unique Types: {data['TYPE'].nunique()}")
        st.write(f"Unique Sizes: {data['SIZE'].nunique()}")

    elif menu == "Time-Based Analysis":
        st.write("### Weight and Quantity Over Time")
        time_summary = data.groupby("DATE").agg({"WEIGHT": "sum", "QTY": "sum"}).reset_index()
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(x="DATE", y="WEIGHT", data=time_summary, marker="o", label="Weight")
        sns.lineplot(x="DATE", y="QTY", data=time_summary, marker="o", label="Quantity")
        ax1.set_title("Weight and Quantity Over Time")
        plt.xlabel("Date")
        plt.ylabel("Total")
        plt.legend()
        st.pyplot(fig1)

    elif menu == "Party-Based Analysis":
        st.write("### Top and Bottom Parties by Weight")
        party_summary = data.groupby("PARTY")["WEIGHT"].sum().reset_index()
        top_10_parties = party_summary.sort_values(by="WEIGHT", ascending=False).head(10)
        bottom_5_parties = party_summary.sort_values(by="WEIGHT").head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Top 10 Parties")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.barplot(x="WEIGHT", y="PARTY", data=top_10_parties, palette="Blues_r")
            ax2.set_title("Top 10 Parties by Weight")
            st.pyplot(fig2)
        with col2:
            st.write("#### Bottom 5 Parties")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            sns.barplot(x="WEIGHT", y="PARTY", data=bottom_5_parties, palette="Reds_r")
            ax3.set_title("Bottom 5 Parties by Weight")
            st.pyplot(fig3)

    elif menu == "Search Party Rank":
        st.write("### Search Party Rank")
        party_summary = data.groupby("PARTY")["WEIGHT"].sum().reset_index().sort_values(by="WEIGHT", ascending=False)
        party_summary["RANK"] = range(1, len(party_summary) + 1)
        party_to_search = st.text_input("Enter Party Name to Search:")
        if party_to_search:
            if party_to_search in party_summary["PARTY"].values:
                rank = party_summary.loc[party_summary["PARTY"] == party_to_search, "RANK"].values[0]
                weight = party_summary.loc[party_summary["PARTY"] == party_to_search, "WEIGHT"].values[0]
                st.success(f"Party `{party_to_search}` is ranked #{rank} with a total weight of {weight}.")
            else:
                st.error(f"Party `{party_to_search}` not found in the dataset.")

    # Other menu options remain unchanged
    # ...

else:
    st.info("Please upload an Excel file to start the analysis.")

