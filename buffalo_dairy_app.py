import re

import streamlit as st
import pandas as pd
from twilio.rest import Client
from datetime import datetime

# ---------------- CONFIG ---------------- #

ACCOUNT_SID = "TWILIO_SID"
AUTH_TOKEN = "TWILIO_TOKEN"
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+918688263431"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# -------------- VALIDATION ---------------- #

E164_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")


def validate_phone_number(phone: str) -> tuple[bool, str]:
    """Validate that a phone number is in E.164 format.

    E.164 numbers start with '+', followed by a non-zero country code digit
    and 6-14 additional digits (total 7-15 digits).

    Returns (is_valid, error_message).
    """
    phone = phone.strip()
    if not phone:
        return False, "Phone number is required."
    if not phone.startswith("+"):
        return False, (
            "Phone number must start with '+' and include the country code "
            "(e.g. +911234567890)."
        )
    if not E164_PATTERN.match(phone):
        return False, (
            "Phone number is not valid. Expected E.164 format: "
            "+<country code><number> (e.g. +911234567890)."
        )
    return True, ""


# --------------- UI ---------------- #

st.set_page_config(page_title="Buffalo Dairy", page_icon="🐃")

st.title("🐃 Buffalo Dairy Milk Orders")

st.write("Fresh Buffalo Milk Delivery 🚚")

# -------------- FORM ---------------- #

with st.form("order_form"):

    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number", placeholder="+911234567890")
    address = st.text_area("Delivery Address")

    milk_type = st.selectbox(
        "Milk Type",
        ["Buffalo Milk", "Cow Milk"]
    )

    liters = st.number_input("Liters", min_value=1)

    date = st.date_input("Delivery Date")

    submit = st.form_submit_button("Place Order")

# -------------- PROCESS ---------------- #

if submit:

    phone_valid, phone_error = validate_phone_number(phone)

    if not name.strip():
        st.error("Please enter a customer name.")
    elif not phone_valid:
        st.error(phone_error)
    elif not address.strip():
        st.error("Please enter a delivery address.")
    else:

        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "Name": name,
            "Phone": phone.strip(),
            "Address": address,
            "Milk": milk_type,
            "Liters": liters,
            "Date": date,
            "Ordered At": order_time
        }

        df = pd.DataFrame([data])

        # Save Excel
        try:
            old = pd.read_excel("orders.xlsx")
            df = pd.concat([old, df])
        except:
            pass

        df.to_excel("orders.xlsx", index=False)

        # WhatsApp Message
        message_body = f"""
🐃 New Milk Order

Name: {name}
Phone: {phone}
Milk: {milk_type}
Liters: {liters}
Date: {date}
Address: {address}
"""

        try:
            client.messages.create(
                body=message_body,
                from_=FROM_WHATSAPP,
                to=TO_WHATSAPP
            )

            st.success("Order Placed & WhatsApp Sent ✅")

        except Exception as e:
            st.success("Order Saved ✅")
            st.warning("WhatsApp Failed — Check Twilio Setup")
