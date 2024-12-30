# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import io



# File uploader
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])

if uploaded_file:
    # Load data
    data = pd.read_excel(uploaded_file)

    # Check for required columns
    required_columns = ["DATE", "PARTY", "DESIGN NO", "TYPE", "WEIGHT", "QTY", "SIZE"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        st.error(f"The following required columns are missing from the uploaded file: {', '.join(missing_columns)}")
    else:
        # Standardize column names
        data.columns = data.columns.str.upper()

        # Convert date column to datetime
        data["DATE"] = pd.to_datetime(data["DATE"])

        # Summarize data by PARTY
        party_summary = data.groupby("PARTY")["WEIGHT"].sum().reset_index().sort_values(by="WEIGHT", ascending=False)
        party_summary["RANK"] = range(1, len(party_summary) + 1)

        # Summarize data by DESIGN NO
        design_summary = data.groupby("DESIGN NO")["WEIGHT"].sum().reset_index().sort_values(by="WEIGHT", ascending=False)

        st.success("Data uploaded successfully!")

        # Create the layout with a sidebar for navigation
        st.sidebar.title("Dashboard Navigation")
        app_mode = st.sidebar.radio("Select a page:", ["Home", "Party Summary", "Design Summary"])

        if app_mode == "Home":
            # Home Page: Display the main title and the upload feature
            st.write("# Welcome to the Data Analysis Dashboard")
            st.write("Upload your data to get started.")

            # Display graphs immediately after upload
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
                sns.barplot(data=top_10_designs, x="WEIGHT", y="DESIGN NO", palette="coolwarm", ax=ax)
                ax.set_title("Top 10 Designs by Weight", fontsize=14)
                st.pyplot(fig)

        elif app_mode == "Party Summary":
            # Party Summary Page: Display the summary for Party
            st.write("## Party Summary")
            st.write("This page provides insights on the total weight per party.")

            # Select a party to filter and view
            party_name = st.selectbox("Enter Party Name to Search:", party_summary["PARTY"].unique())
            selected_party_data = data[data["PARTY"] == party_name]

            st.write(f"### Details for Party: {party_name}")
            st.write(selected_party_data)

            # Display party data graph
            party_data = party_summary[party_summary["PARTY"] == party_name]
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=party_data, x="WEIGHT", y="PARTY", palette="Blues", ax=ax)
            ax.set_title(f"Weight for {party_name}", fontsize=14)
            st.pyplot(fig)

        elif app_mode == "Design Summary":
            # Design Summary Page: Display the summary for Design
            st.write("## Design Summary")
            st.write("This page provides insights on the total weight per design.")

            # Select a design to filter and view
            design_no = st.selectbox("Enter Design No to Search:", design_summary["DESIGN NO"].unique())
            selected_design_data = data[data["DESIGN NO"] == design_no]

            st.write(f"### Details for Design No: {design_no}")
            st.write(selected_design_data)

            # Display design data graph
            design_data = design_summary[design_summary["DESIGN NO"] == design_no]
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=design_data, x="WEIGHT", y="DESIGN NO", palette="coolwarm", ax=ax)
            ax.set_title(f"Weight for Design No: {design_no}", fontsize=14)
            st.pyplot(fig)

