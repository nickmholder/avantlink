# filename: affiliate_report_app.py

import streamlit as st
import requests
import csv
from datetime import datetime
import base64

st.title("Affiliate Report Generator")

# Merchant options pulled from secrets
merchant_credentials = st.secrets["merchants"]

# Choose merchant
merchant = st.selectbox("Select Merchant", ["All"] + list(merchant_credentials.keys()))

# Choose date range
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Run when button is clicked
if st.button("Generate Report"):
    if merchant == "All":
        selected_merchants = list(merchant_credentials.keys())
    else:
        selected_merchants = [merchant]

    for m in selected_merchants:
        creds = merchant_credentials[m]
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"{m}_affiliate_report_{timestamp}.csv"

        params = {
            "module": "MerchantReport",
            "merchant_id": creds["merchant_id"],
            "auth_key": creds["api_key"],
            "report_id": "15",
            "date_begin": start_date.strftime("%Y-%m-%d"),
            "date_end": end_date.strftime("%Y-%m-%d"),
            "output": "json"
        }

        st.write(f"Fetching report for **{m}**...")
        response = requests.get("https://classic.avantlink.com/api.php", params=params)
        data = response.json()

        csvheader = ['Affiliate ID', 'Affiliate Name', 'Clicks', 'Sales', 'No. of Sales', 'Conversion Rate']
        rows = []

        for x in data:
            row = [
                x['Affiliate Id'],
                x['Affiliate Name'],
                x['Click Throughs'],
                x['Sales'],
                x['# of Sales'],
                x['Conversion Rate'] + "%",
            ]
            rows.append(row)

        rows.sort(key=lambda r: int(r[2]), reverse=True)

        with open(filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csvheader)
            writer.writerows(rows)
            writer.writerow([])
            writer.writerow([f"Affiliate Report for {m} between {start_date} and {end_date}"])

        # Show success message and provide download link
        st.success(f"{filename} generated successfully!")

        # Generate download link
        with open(filename, "rb") as file:
            b64 = base64.b64encode(file.read()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
            st.markdown(href, unsafe_allow_html=True)
