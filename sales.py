# -*- coding: utf-8 -*-
"""sales.ipynb"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

st.set_page_config(layout="wide")  # Set the layout to wide mode
st.title("Sales Analysis Dashboard")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

analysis_type = st.selectbox("Select the type of analysis", ["Monthly Sale", "Export Sale"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        if analysis_type == "Monthly Sale":
            st.write("### Monthly Sale Analysis")
            st.write("First 10 rows of the dataset:")
            st.dataframe(data.head(10))

            required_columns = ['DocDate', 'type', 'parName', 'CATEGORY','CatCd', 'weight', 'noPcs']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The dataset must contain these columns: {required_columns}")
            else:
                excluded_categories = ['ST', 'LOOSE PCS', 'PARA BIDS', 'Langadi', 'PROCESS LOSS',
                                       'SCRAP PCC', 'BALL CHAIN', 'SIGNING TAR', 'Fine']
                df = data[~data['CATEGORY'].isin(excluded_categories)]

                party_weight_summary = df.groupby('parName')['weight'].sum().reset_index()
                party_weight_summary['Rank'] = party_weight_summary['weight'].rank(
                    ascending=False, method='min')
                party_weight_summary = party_weight_summary.sort_values(by='weight', ascending=False)

                CatCd_summary = df.groupby('CatCd')['weight'].sum().reset_index()
                CatCd_summary['Rank'] = CatCd_summary['weight'].rank(ascending=False, method='min')
                CatCd_summary = CatCd_summary.sort_values(by='weight', ascending=False)

                st.write("### KPI Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Parties", len(party_weight_summary))
                with col2:
                    st.metric("Total Categories", len(CatCd_summary))
                with col3:
                    st.metric("Total Weight", f"{df['weight'].sum():.2f}")

                party_name = st.selectbox("Select a party name:", options=party_weight_summary['parName'].unique())
                if party_name:
                    party_details = party_weight_summary[party_weight_summary['parName'] == party_name]
                    st.write(f"**Rank:** {int(party_details['Rank'].values[0])}")
                    st.write(f"**Party Name:** {party_name}")
                    st.write(f"**Total Weight:** {party_details['weight'].values[0]:.2f}")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Top 10 Parties by Weight")
                    fig1, ax1 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='parName', data=party_weight_summary.head(10), palette='Blues_r', ax=ax1)
                    ax1.set_title('Top 10 Parties by Weight')
                    st.pyplot(fig1)
                with col2:
                    st.write("### Bottom 5 Parties by Weight")
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='parName', data=party_weight_summary.tail(5), palette='Reds_r', ax=ax2)
                    ax2.set_title('Bottom 5 Parties by Weight')
                    st.pyplot(fig2)

                col3, col4 = st.columns(2)
                with col3:
                    st.write("### Top 10 Categories by Weight")
                    fig3, ax3 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='CatCd', data=CatCd_summary.head(10), palette='pastel', ax=ax3)
                    ax3.set_title('Top 10 Categories by Weight')
                    st.pyplot(fig3)
                with col4:
                    st.write("### Bottom 5 Categories by Weight")
                    fig4, ax4 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='CatCd', data=CatCd_summary.tail(5), palette='Oranges_r', ax=ax4)
                    ax4.set_title('Bottom 5 Categories by Weight')
                    st.pyplot(fig4)

                st.write("### Total Weight Over Time")
                df['DocDate'] = pd.to_datetime(df['DocDate'])
                time_series = df.groupby('DocDate')['weight'].sum().reset_index()
                fig5, ax5 = plt.subplots(figsize=(10, 6))
                sns.lineplot(x='DocDate', y='weight', data=time_series, marker='o', color='blue', ax=ax5)
                ax5.set_title('Total Weight Over Time')
                st.pyplot(fig5)

        elif analysis_type == "Export Sale":
            st.write("### Export Sale Analysis")
            st.write("First 10 rows of the dataset:")
            st.dataframe(data.head(10))
            
            st.write("### Data Summary")
            st.write(data.describe())
            
            st.write("### Weight and Quantity Over Time")
            data['DATE'] = pd.to_datetime(data['DATE'])
            time_summary = data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
            fig6, ax6 = plt.subplots(figsize=(10, 6))
            sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight')
            sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity')
            ax6.set_title("Weight and Quantity Over Time")
            plt.legend()
            st.pyplot(fig6)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload an Excel or CSV file to start the analysis.")
