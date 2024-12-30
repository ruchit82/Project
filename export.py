# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import io

# Streamlit configurations
st.set_page_config(page_title="Export Sales Analysis", layout="wide", page_icon="📊")

# Custom CSS for professional styling
st.markdown(
    """
    <style>
    /* Main Page Styling */
    .main { background-color: #f4f4f4; font-family: 'Arial', sans-serif; }
    h1, h2, h3 { color: #333333; font-weight: bold; }
    
    /* Sidebar Styling */
    .css-1vbd788 {
        background-color: #393e46 !important; 
        color: white !important; 
        border-radius: 10px; 
        padding: 0.5rem;
    }
    .css-1vbd788:hover {
        background-color: #222831 !important; 
        color: #ffffff !important;
    }

    /* Tooltip and Chart Interactivity */
    .tooltip { font-size: 0.85rem; color: #666666; }
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
        "Design-Based Analysis",
        "Interactive Search",
    ],
)

# Upload Data Section
uploaded_file = st.sidebar.file_uploader("📤 Upload Your Excel File", type=["xlsx", "xls"])

if uploaded_file:
    # Load data
    data = pd.read_excel(uploaded_file)
    data["DATE"] = pd.to_datetime(data["DATE"])

    # Data Preprocessing
    party_summary = data.groupby("PARTY")["WEIGHT"].sum().reset_index().sort_values(by="WEIGHT", ascending=False)
    party_summary["RANK"] = range(1, len(party_summary) + 1)
    design_summary = data.groupby("DESIGN")["WEIGHT"].sum().reset_index().sort_values(by="WEIGHT", ascending=False)

    st.success("Data uploaded successfully!")

    # Display key graphs immediately after upload
    st.write("### Key Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.write("#### Top 10 Parties by Weight")
        top_10_parties = party_summary.head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=top_10_parties, x="WEIGHT", y="PARTY", palette="viridis", ax=ax)
        ax.set_title("Top 10 Parties by Weight", fontsize=14)
        st.pyplot(fig)

    with col2:
        st.write("#### Top 10 Designs by Weight")
        top_10_designs = design_summary.head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=top_10_designs, x="WEIGHT", y="DESIGN", palette="coolwarm", ax=ax)
        ax.set_title("Top 10 Designs by Weight", fontsize=14)
        st.pyplot(fig)

    # Navigation menu options
    if menu == "Summary Statistics":
        st.write("### Summary Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Weight Statistics")
            st.write(data["WEIGHT"].describe())
        with col2:
            st.write("#### Quantity Statistics")
            st.write(data["QTY"].describe())

    elif menu == "Time-Based Analysis":
        st.write("### Time-Based Analysis")
        time_summary = data.groupby("DATE").agg({"WEIGHT": "sum", "QTY": "sum"}).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Weight Over Time")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=time_summary, x="DATE", y="WEIGHT", marker="o", ax=ax)
            ax.set_title("Weight Trend Over Time")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.write("#### Quantity Over Time")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=time_summary, x="DATE", y="QTY", marker="o", ax=ax)
            ax.set_title("Quantity Trend Over Time")
            plt.xticks(rotation=45)
            st.pyplot(fig)

    elif menu == "Party-Based Analysis":
        st.write("### Party-Based Analysis")
        st.write("#### Top 10 Parties by Weight")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_10_parties, x="WEIGHT", y="PARTY", palette="viridis", ax=ax)
        ax.set_title("Top 10 Parties by Weight", fontsize=14)
        st.pyplot(fig)

    elif menu == "Design-Based Analysis":
        st.write("### Design-Based Analysis")
        st.write("#### Top 10 Designs by Weight")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_10_designs, x="WEIGHT", y="DESIGN", palette="coolwarm", ax=ax)
        ax.set_title("Top 10 Designs by Weight", fontsize=14)
        st.pyplot(fig)

    elif menu == "Interactive Search":
        st.write("### Search Party Details")
        party_name = st.selectbox(
            "Enter Party Name to Search:",
            options=party_summary["PARTY"].values,
        )
        if party_name:
            rank = party_summary.loc[party_summary["PARTY"] == party_name, "RANK"].values[0]
            weight = party_summary.loc[party_summary["PARTY"] == party_name, "WEIGHT"].values[0]
            st.success(f"Party `{party_name}` is ranked #{rank} with a total weight of {weight}.")

else:
    st.info("📂 Please upload a valid Excel file to begin analysis.")
