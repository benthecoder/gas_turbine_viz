from dotenv import load_dotenv
from twilio.rest import Client
import psycopg2
import pandas as pd
import os
import streamlit as st


def init_twilio():
    """
    Initialize twilio client
    Find your Account SID and Auth Token at twilio.com/console
    """
    load_dotenv()
    ACCOUNT_SID = os.getenv("ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    return client


def send_message(to_phone: str, message: str) -> str:

    client = init_twilio()

    # twilio acc phone number
    from_phone = "+15154979533"

    try:
        message = client.messages.create(body=message, from_=from_phone, to=to_phone)
    except Exception as err:
        return f"Exception caught: {err}"

    return "message successfully sent!"


with st.form("subscribe", clear_on_submit=True):
    st.header("Subscribe, and we'll send you a text message of the latest news!")
    name = st.text_input("Enter your name", value="Benedict")
    phone_num = st.text_input("Enter your phone number", value="+1")
    submitted = st.form_submit_button("Submit")

    message = f"""

    Hey {name}!, check out the latest news by Baker Hughes:

    - https://www.bakerhughes.com/company/energy-forward/new-materials-transforming-future-energy
    - https://www.bakerhughes.com/company/energy-forward/putting-corporate-responsibility-climate-action-villages-india
    - https://www.bakerhughes.com/company/energy-forward/passionate-problem-solver-takes-energy-technology

    Stay tuned for more updates!
    """

    if submitted:
        message = send_message(phone_num, message)
        if "successfully" in message:
            st.success(message)
        else:
            st.error("subscription failed, please try again")
