# -*- coding: utf-8 -*-
"""Enhanced Export Sales Dashboard for Gold Manufacturing Company"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')

# Streamlit configurations
st.set_page_config(
    page_title="Export Sales Analysis",
    layout="wide",
    page_icon="📊"
)

sns.set(style="whitegrid")

# Header
st.markdown("""
    <div class="header">
        <h1>📊 Export Sales Analysis Dashboard</h1>
        <p style="color: white;">Monthly Analysis of Export Orders for Gold Bangles and Rings</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for Filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", 
                                   value=(datetime(2024, 1, 1), datetime(2024, 12, 31)))
show_top_bottom = st.sidebar.radio("Select Analysis Type", ["Top Parties", "Bottom Parties"], index=0)
uploaded_file = st.sidebar.file_uploader("Upload the Export Sales Excel File", type=['xlsx', 'xls'])

if uploaded_file:
    # Load data
    data = pd.read_excel(uploaded_file)

    # Data Preview
    st.write("## Overview of Uploaded Data")
    st.dataframe(data.head(10), use_container_width=True)

    # Data Information
    with st.expander("Data Information"):
        buffer = []
        data.info(buf=buffer)
        st.text("".join(buffer))

    # Summary Statistics
    with st.expander("Data Summary"):
        st.write(data.describe())

    # Convert DATE column to datetime
    data['DATE'] = pd.to_datetime(data['DATE'])
    filtered_data = data[(data['DATE'] >= pd.Timestamp(date_range[0])) & (data['DATE'] <= pd.Timestamp(date_range[1]))]

    # Create Tabs for Different Analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Weight & Quantity Over Time", "Party Analysis", 
                                            "Type Analysis", "Size Analysis", "Design Analysis"])

    # 1. Weight and Quantity Over Time
    with tab1:
        st.subheader("Weight and Quantity Over Time")
        time_summary = filtered_data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()

        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight', color='gold')
        sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity', color='blue')
        ax1.set_title("Weight and Quantity Over Time")
        plt.xlabel("Date")
        plt.ylabel("Total")
        plt.legend()
        st.pyplot(fig1)

    # 2. Party Analysis
    with tab2:
        st.subheader("Top and Bottom Parties by Weight")
        party_summary = filtered_data.groupby('PARTY')['WEIGHT'].sum().reset_index()
        top_parties = party_summary.sort_values(by='WEIGHT', ascending=False).head(10)
        bottom_parties = party_summary.sort_values(by='WEIGHT').head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Top 10 Parties")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.barplot(x='WEIGHT', y='PARTY', data=top_parties, palette='gold')
            ax2.set_title("Top 10 Parties by Weight")
            st.pyplot(fig2)

        with col2:
            st.write("### Bottom 5 Parties")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            sns.barplot(x='WEIGHT', y='PARTY', data=bottom_parties, palette='Reds')
            ax3.set_title("Bottom 5 Parties by Weight")
            st.pyplot(fig3)

    # 3. Type Analysis
    with tab3:
        st.subheader("Type-Based Analysis")
        type_summary = filtered_data.groupby('TYPE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()

        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='WEIGHT', y='TYPE', data=type_summary, palette='viridis')
        ax4.set_title("Weight by Type")
        st.pyplot(fig4)

    # 4. Size Analysis
    with tab4:
        st.subheader("Size-Based Analysis")
        size_summary = filtered_data.groupby('SIZE').agg({'WEIGHT': 'sum'}).reset_index()

        fig5, ax5 = plt.subplots(figsize=(10, 6))
        sns.barplot(x='SIZE', y='WEIGHT', data=size_summary, palette='coolwarm')
        ax5.set_title("Weight by Size")
        st.pyplot(fig5)

    # 5. Design Analysis
    with tab5:
        st.subheader("Top 5 Designs by Weight")
        design_summary = filtered_data.groupby('DESIGN NO')['WEIGHT'].sum().reset_index()
        top_designs = design_summary.sort_values(by='WEIGHT', ascending=False).head(5)

        fig6, ax6 = plt.subplots(figsize=(8, 6))
        sns.barplot(x='WEIGHT', y='DESIGN NO', data=top_designs, palette='Greens')
        ax6.set_title("Top 5 Designs by Weight")
        st.pyplot(fig6)

    # Download Filtered Data
    st.sidebar.markdown("### Download Options")
    csv = filtered_data.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv'
    )

else:
    st.info("Please upload an Excel file to start the analysis.")
