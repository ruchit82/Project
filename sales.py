import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# ✅ Move this to the top before anything else
st.set_page_config(layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .big-title { font-size: 26px; font-weight: bold; text-align: center; color: #4A90E2; }
    .section-title { font-size: 20px; font-weight: bold; color: #2C3E50; margin-top: 20px; }
    .metric-box { background-color: #F4F6F7; padding: 10px; border-radius: 10px; text-align: center; }
    .chart-container { background-color: #ECF0F1; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📊 Sales Analysis Dashboard</p>', unsafe_allow_html=True)
# -*- coding: utf-8 -*-
"""sales.ipynb"""


# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Dropdown for selecting analysis type
analysis_type = st.selectbox("Select the type of analysis", ["Monthly Sale", "Export Sale"])

if uploaded_file:
    try:
        # Read file based on type
        data = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

        if analysis_type == "Export Sale":
            st.markdown('<p class="section-title">📦 Export Sale Analysis</p>', unsafe_allow_html=True)
            st.write("### First 10 rows of the dataset:")
            st.dataframe(data.head(10))

            # KPI Metrics
            st.markdown('<p class="section-title">📌 Weight and Quantity Summary</p>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="metric-box">📏 Statistics for <b>WEIGHT</b></div>', unsafe_allow_html=True)
                st.write(data['WEIGHT'].describe())
            with col2:
                st.markdown('<div class="metric-box">📦 Statistics for <b>QTY</b></div>', unsafe_allow_html=True)
                st.write(data['QTY'].describe())

            # Unique counts
            st.markdown('<p class="section-title">🔢 Unique Values in Categorical Columns</p>', unsafe_allow_html=True)
            st.write(f"🎯 Unique Parties: **{data['PARTY'].nunique()}**")
            st.write(f"📂 Unique Types: **{data['TYPE'].nunique()}**")
            st.write(f"📏 Unique Sizes: **{data['SIZE'].nunique()}**")

            # Convert DATE column to datetime for time-based analysis
            data['DATE'] = pd.to_datetime(data['DATE'])
            time_summary = data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()

            # Time Series Analysis
            st.markdown('<p class="section-title">📅 Weight and Quantity Over Time</p>', unsafe_allow_html=True)
            with st.container():
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight', color='blue')
                sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity', color='red')
                ax1.set_title("📈 Weight and Quantity Over Time")
                plt.xlabel("Date")
                plt.ylabel("Total")
                plt.legend()
                st.pyplot(fig1)

            # Party-based Analysis
            st.markdown('<p class="section-title">🏆 Top and Bottom Parties by Weight</p>', unsafe_allow_html=True)
            party_summary = data.groupby('PARTY')['WEIGHT'].sum().reset_index()
            top_10_parties = party_summary.sort_values(by='WEIGHT', ascending=False).head(10)
            bottom_5_parties = party_summary.sort_values(by='WEIGHT').head(5)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="chart-container"><p class="section-title">🏅 Top 10 Parties</p></div>', unsafe_allow_html=True)
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                sns.barplot(x='WEIGHT', y='PARTY', data=top_10_parties, palette='Blues_r')
                ax2.set_title("🏅 Top 10 Parties by Weight")
                st.pyplot(fig2)
            with col2:
                st.markdown('<div class="chart-container"><p class="section-title">🥉 Bottom 5 Parties</p></div>', unsafe_allow_html=True)
                fig3, ax3 = plt.subplots(figsize=(8, 5))
                sns.barplot(x='WEIGHT', y='PARTY', data=bottom_5_parties, palette='Reds_r')
                ax3.set_title("🥉 Bottom 5 Parties by Weight")
                st.pyplot(fig3)

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")

else:
    st.info("📂 Please upload a file to start the analysis.")

