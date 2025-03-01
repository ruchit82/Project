import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Initialize session state for storing order data
if 'order_data' not in st.session_state:
    st.session_state.order_data = []

st.title("Order Processing App")

# File uploader for image
uploaded_image = st.file_uploader("Upload Order Image", type=["jpg", "png", "jpeg"])

# Order details input
order_no = st.text_input("Order Number")
party_name = st.text_input("Party Name")
party_code = st.text_input("Party Code")
weight = st.text_input("Weight")
size = st.text_input("Size")
rhodium = st.text_input("Rhodium")
remark = st.text_area("Remark")

if st.button("Generate Processed Image"):
    if uploaded_image and order_no:
        # Load image
        image = Image.open(uploaded_image)
        image = image.convert("RGB")
        draw = ImageDraw.Draw(image)
        
        # Define font (default system font if ttf is unavailable)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Text to overlay
        text = (f"Order No: {order_no}\nParty Name: {party_name}\nParty Code: {party_code}\n"
                f"Weight: {weight}\nSize: {size}\nRhodium: {rhodium}\nRemark: {remark}")
        draw.text((10, 10), text, fill="black", font=font)
        
        # Save processed image
        processed_image_path = "processed_image.jpg"
        image.save(processed_image_path)
        
        # Display image
        st.image(image, caption="Processed Image", use_column_width=True)
        
        # Store order details
        st.session_state.order_data.append([order_no, party_name, party_code, weight, size, rhodium, remark])
        
        # Provide download link
        with open(processed_image_path, "rb") as file:
            btn = st.download_button(label="Download Processed Image", data=file, file_name=f"Order_{order_no}.jpg", mime="image/jpeg")
    else:
        st.warning("Please upload an image and enter an order number.")

if st.button("Download Order Data (Excel)"):
    df = pd.DataFrame(st.session_state.order_data, columns=["Order No", "Party Name", "Party Code", "Weight", "Size", "Rhodium", "Remark"])
    excel_path = "order_data.xlsx"
    df.to_excel(excel_path, index=False)
    with open(excel_path, "rb") as file:
        st.download_button(label="Download Excel", data=file, file_name="Order_Data.xlsx", mime="application/vnd.ms-excel")
