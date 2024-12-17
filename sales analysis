import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Streamlit App Title
st.title("Data Analysis Application for Monthly Sales and Export Data")

# File type selection
file_type = st.radio("Choose the file type to analyze:", ("Monthly Sales", "Export"))

# File uploader
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx", "csv", "xls"])

if uploaded_file:
    try:
        # Load the uploaded file
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        st.write("### First 10 Rows of the Dataset:")
        st.dataframe(data.head(10))
        
        # Analysis for Monthly Sales
        if file_type == "Monthly Sales":
            # Required Columns Check
            required_columns = ['DocDate', 'type', 'parName', 'CATEGORY', 'weight', 'noPcs']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The Monthly Sales dataset must contain these columns: {required_columns}")
            else:
                # Remove unwanted categories
                excluded_categories = ['ST', 'LOOSE PCS', 'PARA BIDS', 'Langadi', 'PROCESS LOSS',
                                       'SCRAP PCC', 'BALL CHAIN', 'SIGNING TAR', 'Fine']
                df = data[~data['CATEGORY'].isin(excluded_categories)]

                # Party-wise weight summary
                party_weight_summary = df.groupby('parName')['weight'].sum().reset_index()
                party_weight_summary['Rank'] = party_weight_summary['weight'].rank(ascending=False, method='dense')
                party_weight_summary = party_weight_summary.sort_values(by='weight', ascending=False)

                # Party rank based on user input
                st.write("### Check Party Rank")
                party_name = st.text_input("Enter the party name:")
                if party_name:
                    if party_name in party_weight_summary['parName'].values:
                        party_details = party_weight_summary[party_weight_summary['parName'] == party_name]
                        st.write(f"**Rank:** {int(party_details['Rank'].values[0])}")
                        st.write(f"**Party Name:** {party_name}")
                        st.write(f"**Total Weight:** {party_details['weight'].values[0]:.2f}")
                    else:
                        st.error("Party name not found in the dataset.")

                # Top 10 and bottom 5 parties
                top_10_parties = party_weight_summary.head(10)
                bottom_5_parties = party_weight_summary.tail(5)

                # Visualizations
                st.write("### Top 10 Parties by Weight")
                st.bar_chart(top_10_parties.set_index('parName')['weight'])

                st.write("### Bottom 5 Parties by Weight")
                st.bar_chart(bottom_5_parties.set_index('parName')['weight'])

                # Time series for weight
                df['DocDate'] = pd.to_datetime(df['DocDate'])
                time_series = df.groupby('DocDate')['weight'].sum().reset_index()
                st.write("### Total Weight Over Time")
                st.line_chart(time_series.set_index('DocDate')['weight'])

        # Analysis for Export Data
        elif file_type == "Export":
            # Required Columns Check
            required_columns_export = ['DATE', 'PARTY', 'WEIGHT', 'QTY', 'TYPE', 'SIZE', 'DESIGN NO']
            if not all(col in data.columns for col in required_columns_export):
                st.error(f"The Export dataset must contain these columns: {required_columns_export}")
            else:
                st.write("### Summary Statistics")
                st.write("Statistics for WEIGHT:")
                st.dataframe(data['WEIGHT'].describe())

                st.write("Statistics for QTY:")
                st.dataframe(data['QTY'].describe())

                # Unique values
                st.write(f"**Unique Parties:** {data['PARTY'].nunique()}")
                st.write(f"**Unique Types:** {data['TYPE'].nunique()}")
                st.write(f"**Unique Sizes:** {data['SIZE'].nunique()}")

                # Time-Based Analysis
                data['DATE'] = pd.to_datetime(data['DATE'])
                time_summary = data.groupby('DATE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()

                st.write("### Weight and Quantity Over Time")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(x='DATE', y='WEIGHT', data=time_summary, marker='o', label='Weight', ax=ax)
                sns.lineplot(x='DATE', y='QTY', data=time_summary, marker='o', label='Quantity', ax=ax)
                plt.title("Weight and Quantity Over Time")
                plt.xlabel("Date")
                plt.ylabel("Total")
                plt.legend()
                st.pyplot(fig)

                # Party Analysis
                party_summary = data.groupby('PARTY')['WEIGHT'].sum().reset_index()
                top_10_parties = party_summary.sort_values(by='WEIGHT', ascending=False).head(10)
                st.write("### Top 10 Parties by Total Weight")
                st.bar_chart(top_10_parties.set_index('PARTY')['WEIGHT'])

                # Type-Based Analysis
                type_summary = data.groupby('TYPE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
                st.write("### Weight by Type")
                fig, ax = plt.subplots()
                sns.barplot(x='WEIGHT', y='TYPE', data=type_summary, palette='viridis', ax=ax)
                plt.title("Weight by Type")
                st.pyplot(fig)

                # Size-Based Analysis
                size_summary = data.groupby('SIZE')['WEIGHT'].sum().reset_index()
                st.write("### Weight by Size")
                st.bar_chart(size_summary.set_index('SIZE')['WEIGHT'])

                # Correlation Analysis
                numerical_data = data[['WEIGHT', 'QTY']]
                st.write("### Correlation Matrix")
                st.dataframe(numerical_data.corr())

                # Scatter Plot
                st.write("### Scatter Plot: Weight vs Quantity")
                fig, ax = plt.subplots()
                sns.scatterplot(x='WEIGHT', y='QTY', data=data, hue='TYPE', palette='tab10', ax=ax)
                plt.title("Weight vs Quantity")
                st.pyplot(fig)
    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Awaiting file upload...")
