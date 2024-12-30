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
st.set_page_config(page_title="Export Sales Analysis", layout="wide")
sns.set(style="whitegrid")
st.title("📊 Export Sales Analysis Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.write("Use the options below to navigate:")
menu = st.sidebar.radio(
    "Sections", 
    ["Upload Data", "Party Ranking", "Party-Based Analysis", "Design-Based Analysis", "Summary Statistics", "Time-Based Analysis", "Type-Based Analysis", "Size-Based Analysis", "Correlation Analysis", "Scatter & Violin Plots"]
)

# Add date range filter to sidebar
st.sidebar.write("### Filter by Date Range")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(pd.to_datetime('2024-01-01'), pd.to_datetime('2024-12-31')),  # Default date range
    min_value=pd.to_datetime('2020-01-01'),  # Adjust as per your data's date range
    max_value=pd.to_datetime('2024-12-31'),
    key="date_range"
)

# Unpack the date range
start_date, end_date = date_range

# Upload Excel file
uploaded_file = st.sidebar.file_uploader("Upload the Export Sales Excel File", type=['xlsx', 'xls'])

if uploaded_file:
    # Load data
    data = pd.read_excel(uploaded_file)
    data['DATE'] = pd.to_datetime(data['DATE'])

    # Filter data based on the selected date range
    filtered_data = data[(data['DATE'] >= start_date) & (data['DATE'] <= end_date)]

    # Main Dashboard Content
    if menu == "Upload Data":
        st.write("### Preview of Uploaded Data (Filtered by Date Range)")
        st.dataframe(filtered_data.head(10))

        st.write("### Data Information")
        with st.expander("Click to view Data Information"):
            buffer = io.StringIO()
            filtered_data.info(buf=buffer)
            info_string = buffer.getvalue()
            st.text(info_string)

    elif menu == "Summary Statistics":
        st.write("### Data Summary")
        st.write(filtered_data.describe())

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Statistics for WEIGHT")
            st.write(filtered_data['WEIGHT'].describe())
        with col2:
            st.write("#### Statistics for QTY")
            st.write(filtered_data['QTY'].describe())

        st.write("### Unique Values in Categorical Columns")
        st.write(f"Unique Parties: {filtered_data['PARTY'].nunique()}")
        st.write(f"Unique Types: {filtered_data['TYPE'].nunique()}")
        st.write(f"Unique Sizes: {filtered_data['SIZE'].nunique()}")

    elif menu == "Time-Based Analysis":
        st.write("### Weight and Quantity Over Time")
        time_summary = filtered_data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight')
        sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity')
        ax1.set_title("Weight and Quantity Over Time", fontsize=16, fontweight='bold')
        plt.xlabel("Date")
        plt.ylabel("Total")
        plt.legend()
        st.pyplot(fig1)

    elif menu == "Party-Based Analysis":
        st.write("### Top and Bottom Parties by Weight")
        party_summary = filtered_data.groupby('PARTY')['WEIGHT'].sum().reset_index()
        top_10_parties = party_summary.sort_values(by='WEIGHT', ascending=False).head(10)
        bottom_5_parties = party_summary.sort_values(by='WEIGHT').head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Top 10 Parties")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.barplot(x='WEIGHT', y='PARTY', data=top_10_parties, palette='Blues_r')
            ax2.set_title("Top 10 Parties by Weight", fontsize=14, fontweight='bold')
            st.pyplot(fig2)
        with col2:
            st.write("#### Bottom 5 Parties")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            sns.barplot(x='WEIGHT', y='PARTY', data=bottom_5_parties, palette='Reds_r')
            ax3.set_title("Bottom 5 Parties by Weight", fontsize=14, fontweight='bold')
            st.pyplot(fig3)

    elif menu == "Party Ranking":
        st.write("### Party Ranking by Total Weight")
        party_summary = filtered_data.groupby('PARTY')['WEIGHT'].sum().reset_index()
        party_summary['Rank'] = party_summary['WEIGHT'].rank(ascending=False, method='min')
        party_summary = party_summary.sort_values(by='Rank')

        st.write("#### Party Ranking Table")
        st.dataframe(party_summary[['Rank', 'PARTY', 'WEIGHT']].style.highlight_max(axis=0, color='lightgreen'))

        # Party Dropdown
        selected_party = st.selectbox("Select a Party", options=party_summary['PARTY'].unique())
        party_details = party_summary[party_summary['PARTY'] == selected_party]
        st.write(f"### Details for {selected_party}")
        st.write(party_details)

    elif menu == "Type-Based Analysis":
        st.write("### Type-Based Analysis")
        type_summary = filtered_data.groupby('TYPE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='WEIGHT', y='TYPE', data=type_summary, palette='viridis')
        ax4.set_title("Weight by Type", fontsize=14, fontweight='bold')
        st.pyplot(fig4)

    elif menu == "Size-Based Analysis":
        st.write("### Size-Based Analysis")
        size_summary = filtered_data.groupby('SIZE').agg({'WEIGHT': 'sum'}).reset_index()
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='SIZE', y='WEIGHT', data=size_summary, palette='coolwarm')
        ax5.set_title("Weight by Size", fontsize=14, fontweight='bold')
        st.pyplot(fig5)

    elif menu == "Design-Based Analysis":
        st.write("### Top 5 Designs by Weight")
        design_summary = filtered_data.groupby('DESIGN NO')['WEIGHT'].sum().reset_index()
        top_5_designs = design_summary.sort_values(by='WEIGHT', ascending=False).head(5)
        fig6, ax6 = plt.subplots(figsize=(8, 6))
        sns.barplot(x='WEIGHT', y='DESIGN NO', data=top_5_designs, palette='Greens_r')
        ax6.set_title("Top 5 Designs by Weight", fontsize=14, fontweight='bold')
        st.pyplot(fig6)

    elif menu == "Correlation Analysis":
        st.write("### Correlation Analysis")
        fig7, ax7 = plt.subplots(figsize=(8, 6))
        sns.heatmap(filtered_data[['WEIGHT', 'QTY']].corr(), annot=True, cmap='coolwarm')
        ax7.set_title("Correlation Matrix", fontsize=14, fontweight='bold')
        st.pyplot(fig7)

    elif menu == "Scatter & Violin Plots":
        st.write("### Weight vs Quantity Scatter Plot")
        fig8, ax8 = plt.subplots(figsize=(8, 6))
        sns.scatterplot(x='WEIGHT', y='QTY', data=filtered_data, hue='TYPE', palette='tab10')
        ax8.set_title("Weight vs Quantity", fontsize=14, fontweight='bold')
        st.pyplot(fig8)

        st.write("### Weight Distribution by Party")
        fig9, ax9 = plt.subplots(figsize=(10, 6))
        sns.violinplot(x='PARTY', y='WEIGHT', data=filtered_data, scale='width')
        plt.xticks(rotation=45)
        ax9.set_title("Weight Distribution by Party", fontsize=14, fontweight='bold')
        st.pyplot(fig9)

else:
    st.info("📂 Please upload a valid Excel file to begin analysis.")
