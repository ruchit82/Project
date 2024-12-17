import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit app title
st.title("Data Analysis Application")

# Dropdown for selecting the type of analysis
analysis_type = st.radio("Select Analysis Type", ("Monthly Sale", "Export Sale"))

# File uploader
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx", "xls", "csv"])

if uploaded_file:
    try:
        # Load the data based on file type
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        # Check for analysis type
        if analysis_type == "Monthly Sale":
            # Monthly Sale Analysis Code
            st.write("### Monthly Sale Analysis")
            
            # Display first 10 rows
            st.write("First 10 rows of the dataset:")
            st.dataframe(data.head(10))

            # Check for required columns
            required_columns = ['DocDate', 'type', 'parName', 'CATEGORY', 'weight', 'noPcs']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The dataset must contain these columns: {required_columns}")
            else:
                # Remove unwanted categories
                excluded_categories = ['ST', 'LOOSE PCS', 'PARA BIDS', 'Langadi', 'PROCESS LOSS',
                                       'SCRAP PCC', 'BALL CHAIN', 'SIGNING TAR', 'Fine']
                df = data[~data['CATEGORY'].isin(excluded_categories)]

                # Party-wise weight summary
                party_weight_summary = df.groupby('parName')['weight'].sum().reset_index()
                party_weight_summary['Rank'] = party_weight_summary['weight'].rank(ascending=False, method='dense')
                party_weight_summary = party_weight_summary.sort_values(by='weight', ascending=False)

                # Dropdown for party selection
                st.write("### Check Party Rank")
                party_name = st.selectbox("Select a party name:", options=party_weight_summary['parName'].unique())

                if party_name:
                    party_details = party_weight_summary[party_weight_summary['parName'] == party_name]
                    st.write(f"**Rank:** {int(party_details['Rank'].values[0])}")
                    st.write(f"**Party Name:** {party_name}")
                    st.write(f"**Total Weight:** {party_details['weight'].values[0]:.2f}")

                # Plots
                st.write("### Top 10 Parties by Weight")
                st.bar_chart(party_weight_summary.set_index('parName')['weight'])

                # Weight over time
                df['DocDate'] = pd.to_datetime(df['DocDate'])
                time_series = df.groupby('DocDate')['weight'].sum().reset_index()
                st.write("### Total Weight Over Time")
                st.line_chart(time_series.set_index('DocDate')['weight'])

        elif analysis_type == "Export Sale":
            # Export Sale Analysis Code
            st.write("### Export Sale Analysis")

            # Data Preview
            st.write("### Preview of Uploaded Data")
            st.dataframe(data.head(10))

            # Data Info
            st.write("### Data Information")
            buffer = data.info(buf=None)
            st.text(buffer)

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

            # Type-Based Analysis
            st.write("### Type-Based Analysis")
            type_summary = data.groupby('TYPE').agg({'WEIGHT': 'sum', 'QTY': 'sum'}).reset_index()
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='WEIGHT', y='TYPE', data=type_summary, palette='viridis')
            ax4.set_title("Weight by Type")
            st.pyplot(fig4)

            # Size Analysis
            st.write("### Size-Based Analysis")
            size_summary = data.groupby('SIZE').agg({'WEIGHT': 'sum'}).reset_index()
            fig5, ax5 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='SIZE', y='WEIGHT', data=size_summary, palette='coolwarm')
            ax5.set_title("Weight by Size")
            st.pyplot(fig5)

            # Design-Based Analysis
            st.write("### Top 5 Designs by Weight")
            design_summary = data.groupby('DESIGN NO')['WEIGHT'].sum().reset_index()
            top_5_designs = design_summary.sort_values(by='WEIGHT', ascending=False).head(5)
            fig6, ax6 = plt.subplots(figsize=(8, 6))
            sns.barplot(x='WEIGHT', y='DESIGN NO', data=top_5_designs, palette='Greens_r')
            ax6.set_title("Top 5 Designs by Weight")
            st.pyplot(fig6)

            # Correlation Analysis
            st.write("### Correlation Analysis")
            fig7, ax7 = plt.subplots(figsize=(8, 6))
            sns.heatmap(data[['WEIGHT', 'QTY']].corr(), annot=True, cmap='coolwarm')
            ax7.set_title("Correlation Matrix")
            st.pyplot(fig7)

            # Scatter Plot
            st.write("### Weight vs Quantity Scatter Plot")
            fig8, ax8 = plt.subplots(figsize=(8, 6))
            sns.scatterplot(x='WEIGHT', y='QTY', data=data, hue='TYPE', palette='tab10')
            ax8.set_title("Weight vs Quantity")
            st.pyplot(fig8)

            # Violin Plot
            st.write("### Weight Distribution by Party")
            fig9, ax9 = plt.subplots(figsize=(10, 6))
            sns.violinplot(x='PARTY', y='WEIGHT', data=data, scale='width')
            plt.xticks(rotation=45)
            ax9.set_title("Weight Distribution by Party")
            st.pyplot(fig9)

    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Please upload an Excel file to start the analysis.")

 
