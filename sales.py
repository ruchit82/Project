# -*- coding: utf-8 -*-
"""sales.ipynb"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Custom CSS for enhanced dashboard styling
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .dashboard-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .chart-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

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

            required_columns = ['DocDate', 'type', 'parName', 'CATEGORY', 'CatCd', 'weight', 'noPcs']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The dataset must contain these columns: {required_columns}")
            else:
                excluded_categories = ['ST', 'LOOSE PCS', 'PARA BIDS', 'Langadi', 'PROCESS LOSS', 'SCRAP PCC', 'BALL CHAIN', 'SIGNING TAR', 'Fine']
                df = data[~data['CATEGORY'].isin(excluded_categories)]

                party_weight_summary = df.groupby('parName')['weight'].sum().reset_index()
                party_weight_summary['Rank'] = party_weight_summary['weight'].rank(ascending=False, method='min')
                party_weight_summary = party_weight_summary.sort_values(by='weight', ascending=False)

                CatCd_summary = df.groupby('CatCd')['weight'].sum().reset_index()
                CatCd_summary['Rank'] = CatCd_summary['weight'].rank(ascending=False, method='min')
                CatCd_summary = CatCd_summary.sort_values(by='weight', ascending=False)

                party_name = st.selectbox("Select a party name:", options=party_weight_summary['parName'].unique())
                if party_name:
                    party_details = party_weight_summary[party_weight_summary['parName'] == party_name]
                    st.write(f"**Rank:** {int(party_details['Rank'].values[0])}")
                    st.write(f"**Party Name:** {party_name}")
                    st.write(f"**Total Weight:** {party_details['weight'].values[0]:.2f}")
                
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

                st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                st.write("### Top 10 Parties by Weight")
                top_10_parties = party_weight_summary.head(10)
                fig2, ax2 = plt.subplots()
                sns.barplot(x='weight', y='parName', data=top_10_parties, palette='Blues_r', ax=ax2)
                ax2.set_title('Top 10 Parties by Weight')
                st.pyplot(fig2)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                st.write("### Bottom 5 Parties by Weight")
                bottom_5_parties = party_weight_summary.tail(5)
                fig3, ax3 = plt.subplots()
                sns.barplot(x='weight', y='parName', data=bottom_5_parties, palette='Reds_r', ax=ax3)
                ax3.set_title('Bottom 5 Parties by Weight')
                st.pyplot(fig3)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                st.write("### Total Weight Over Time")
                df['DocDate'] = pd.to_datetime(df['DocDate'])
                time_series = df.groupby('DocDate')['weight'].sum().reset_index()
                fig6, ax6 = plt.subplots()
                sns.lineplot(x='DocDate', y='weight', data=time_series, marker='o', color='blue', ax=ax6)
                ax6.set_title('Total Weight Over Time')
                st.pyplot(fig6)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload an Excel or CSV file to start the analysis.")
