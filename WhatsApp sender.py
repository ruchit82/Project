import streamlit as st
import pywhatkit as kit
from datetime import datetime

st.title("Automated WhatsApp Message Sender")

# User Inputs
phone_number = st.text_input("Enter Phone Number (with country code):", "+91")
message = st.text_area("Enter your message:")
send_now = st.checkbox("Send Now")
schedule_later = st.checkbox("Schedule for Later")

if send_now:
    # Get the current time and add a 1-minute buffer to avoid instant sending issues
    now = datetime.now()
    hour = now.hour
    minute = now.minute + 1  # Adding a minute buffer
    if minute >= 60:
        minute = 0
        hour += 1

    if st.button("Send Message"):
        try:
            kit.sendwhatmsg(phone_number, message, hour, minute)
            st.success("Message sent successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if schedule_later:
    hour = st.number_input("Hour (24-hour format):", min_value=0, max_value=23, value=datetime.now().hour)
    minute = st.number_input("Minute:", min_value=0, max_value=59, value=datetime.now().minute+2)
    
    if st.button("Schedule Message"):
        try:
            kit.sendwhatmsg(phone_number, message, hour, minute)
            st.success("Message scheduled successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
