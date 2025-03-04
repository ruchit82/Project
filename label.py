import pandas as pd
import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os

# Load all sheets from an Excel file
def load_all_sheets(file_path):
    return pd.read_excel(file_path, sheet_name=None, dtype=str)

# Search for product code in all sheets
def find_product(data_sheets, product_code):
    for sheet_name, df in data_sheets.items():
        if "DESIGN NO" in df.columns and product_code in df["DESIGN NO"].values:
            return df[df["DESIGN NO"] == product_code].iloc[0].to_dict()
    return None

# Generate barcode
def generate_barcode(data, filename="barcode"):
    barcode_obj = Code128(data, writer=ImageWriter())
    barcode_path = f"{filename}.png"
    barcode_obj.save(barcode_path)
    return barcode_path

# Create label with barcode
def create_label(product_data):
    label_width, label_height = 400, 300
    img = Image.new("RGB", (label_width, label_height), "white")
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Prepare text content
    text = f"Order No: {product_data['Order No']}\nParty Code: {product_data['Party Code']}\n"
    for key, value in product_data.items():
        if key not in ["Order No", "Party Code", "DESIGN NO"]:
            text += f"{key}: {value}\n"

    draw.text((10, 10), text, fill="black", font=font)

    # Generate and paste barcode
    barcode_path = generate_barcode(product_data["MACH CODE"])
    barcode_img = Image.open(barcode_path).resize((200, 50))
    img.paste(barcode_img, (100, 220))

    label_path = "label.png"
    img.save(label_path)
    return label_path

# Streamlit App
st.title("Label Generator with Barcode")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    data_sheets = load_all_sheets(uploaded_file)

    product_code = st.text_input("Enter Product Code:")
    
    if st.button("Fetch Product Data"):
        product_data = find_product(data_sheets, product_code)

        if product_data:
            # Additional user inputs
            product_data["Order No"] = st.text_input("Order No", "Default_Order")
            product_data["Party Code"] = st.text_input("Party Code", "Default_Party")

            # Editable fields
            for key in product_data.keys():
                product_data[key] = st.text_input(key, product_data[key])

            if st.button("Generate Label"):
                label_path = create_label(product_data)
                st.image(label_path, caption="Generated Label")

                # Option to Download
                with open(label_path, "rb") as file:
                    st.download_button("Download Label", file, file_name="label.png")

                # Print Duplicate Option
                if st.button("Print Duplicate Label"):
                    os.system(label_path)
                    st.success("Duplicate Label Sent to Printer!")
        else:
            st.error("Product Code not found in any sheet.")

