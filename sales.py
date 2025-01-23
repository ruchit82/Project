# -*- coding: utf-8 -*-
"""sales.ipynb"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

st.title("Sales Analysis Dashboard")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

analysis_type = st.selectbox("Select the type of analysis", ["Monthly Sale", "Export Sale"])

if uploaded_file:
    error_logs = []  # Collect errors for display
    try:
        # Load the data based on file type
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        if analysis_type == "Monthly Sale":
            st.write("### Monthly Sale Analysis")
            st.write("First 10 rows of the dataset:")
            st.dataframe(data.head(10))

            # Check for required columns
            required_columns = ['DocDate', 'type', 'parName', 'CATEGORY','CatCd', 'weight', 'noPcs']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The dataset must contain these columns: {required_columns}")
            else:
                try:
                    excluded_categories = ['ST', 'LOOSE PCS', 'PARA BIDS', 'Langadi', 'PROCESS LOSS',
                                           'SCRAP PCC', 'BALL CHAIN', 'SIGNING TAR', 'Fine']
                    df = data[~data['CATEGORY'].isin(excluded_categories)]

                    # Party-wise weight summary
                    party_weight_summary = df.groupby('parName')['weight'].sum().reset_index()
                    party_weight_summary['Rank'] = party_weight_summary['weight'].rank(
                        ascending=False, method='min')
                    party_weight_summary = party_weight_summary.sort_values(by='weight', ascending=False)

                    # Dropdown for party selection
                    st.write("### Check Party Rank")
                    party_name = st.selectbox("Select a party name:", options=party_weight_summary['parName'].unique())

                    if party_name:
                        party_details = party_weight_summary[party_weight_summary['parName'] == party_name]
                        st.write(f"**Rank:** {int(party_details['Rank'].values[0])}")
                        st.write(f"**Party Name:** {party_name}")
                        st.write(f"**Total Weight:** {party_details['weight'].values[0]:.2f}")

                    # Pie Chart: Category-wise Weight Distribution (Top 15)
                    st.write("### Category-wise Weight Distribution (Top 15)")
                    category_summary = df.groupby('CatCd')['weight'].sum().reset_index()
                    top_15_categories = category_summary.sort_values(by='weight', ascending=False).head(15)  # Fixed variable name
                    positive_weights = top_15_categories['weight'].apply(lambda x: abs(x))

                    fig1, ax1 = plt.subplots(figsize=(8, 8))
                    ax1.pie(positive_weights, labels=top_15_categories['CatCd'],
                             autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
                    ax1.set_title('Category-wise Weight Distribution (Top 15)')
                    st.pyplot(fig1)

                    # Bar Plot: Top 10 Parties by Weight
                    st.write("### Top 10 Parties by Weight")
                    top_10_parties = party_weight_summary.head(10)
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='parName', data=top_10_parties, palette='Blues_r', ax=ax2)
                    ax2.set_title('Top 10 Parties by Weight')
                    st.pyplot(fig2)

                    # Bar Plot: Bottom 5 Parties by Weight
                    st.write("### Bottom 5 Parties by Weight")
                    bottom_5_parties = party_weight_summary.tail(5)
                    fig3, ax3 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='parName', data=bottom_5_parties, palette='Reds_r', ax=ax3)
                    ax3.set_title('Bottom 5 Parties by Weight')
                    st.pyplot(fig3)

                    # Bar Plot: Top 10 Categories by Weight
                    st.write("### Top 10 Categories by Weight")
                    top_10_category = category_summary.sort_values(by='weight', ascending=False).head(10)
                    fig4, ax4 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='CatCd', data=top_10_category, palette='Greens_r', ax=ax4)
                    ax4.set_title('Top 10 Categories by Weight')
                    st.pyplot(fig4)

                    # Bar Plot: Bottom 5 Categories by Weight
                    st.write("### Bottom 5 Categories by Weight")
                    bottom_5_category = category_summary.sort_values(by='weight').head(5)
                    fig5, ax5 = plt.subplots(figsize=(10, 6))
                    sns.barplot(x='weight', y='CatCd', data=bottom_5_category, palette='Oranges_r', ax=ax5)
                    ax5.set_title('Bottom 5 Categories by Weight')
                    st.pyplot(fig5)

                    # Line Plot: Weight Over Time
                    st.write("### Total Weight Over Time")
                    df['DocDate'] = pd.to_datetime(df['DocDate'])
                    time_series = df.groupby('DocDate')['weight'].sum().reset_index()
                    fig6, ax6 = plt.subplots(figsize=(10, 6))
                    sns.lineplot(x='DocDate', y='weight', data=time_series, marker='o', color='blue', ax=ax6)
                    ax6.set_title('Total Weight Over Time')
                    st.pyplot(fig6)

                except Exception as e:
                    st.error(f"An error occurred during Monthly Sale analysis: {e}")
                
        elif analysis_type == "Export Sale":
            st.write("### Export Sale Analysis")
            try:
                # Data Preview
                st.write("### Preview of Uploaded Data")
                st.dataframe(data.head(10))

                # Data Info
                st.write("### Data Information")
                buffer = []
                data.info(buf=buffer)
                st.text("".join(buffer))

                # Summary Statistics
                st.write("### Data Summary")
                st.write(data.describe())

                # Weight and Quantity Summary
                st.write("### Weight and Quantity Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("#### Statistics for WEIGHT")
                    st.write(data['WEIGHT'].describe())
                with col2:
                    st.write("#### Statistics for QTY")
                    st.write(data['QTY'].describe())

                # Unique counts for categorical columns
                st.write("### Unique Values in Categorical Columns")
                st.write(f"Unique Parties: {data['PARTY'].nunique()}")
                st.write(f"Unique Types: {data['TYPE'].nunique()}")
                st.write(f"Unique Sizes: {data['SIZE'].nunique()}")

                # Time-based Analysis
                st.write("### Weight and Quantity Over Time")
                data['DATE'] = pd.to_datetime(data['DATE'])
                time_summary = data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight')
                sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity')
                ax1.set_title("Weight and Quantity Over Time")
                plt.xlabel("Date")
                plt.ylabel("Total")
                plt.legend()
                st.pyplot(fig1)

                # Party-based Analysis
                st.write("### Top and Bottom Parties by Weight")
                party_summary = data.groupby('PARTY')['WEIGHT'].sum().reset_index()
                top_10_parties = party_summary.sort_values(by='WEIGHT', ascending=False).head(10)
                bottom_5_parties = party_summary.sort_values(by='WEIGHT').head(5)

                col1, col2 = st.columns(2)
                with col1:
                    st.write("#### Top 10 Parties")
                    fig2, ax2 = plt.subplots(figsize=(8, 6))
                    sns.barplot(x='WEIGHT', y='PARTY', data=top_10_parties, palette='Blues_r')
                    ax2.set_title("Top 10 Parties by Weight")
                    st.pyplot(fig2)
                with col2:
                    st.write("#### Bottom 5 Parties")
                    fig3, ax3 = plt.subplots(figsize=(8, 6))
                    sns.barplot(x='WEIGHT', y='PARTY', data=bottom_5_parties, palette='Reds_r')
                    ax3.set_title("Bottom 5 Parties by Weight")
                    st.pyplot(fig3)

            except Exception as e:
                st.error(f"An error occurred during Export Sale analysis: {e}")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload an Excel or CSV file to start the analysis.")
