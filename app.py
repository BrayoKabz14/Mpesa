from flask import Flask, render_template, request
import requests, base64
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load credentials from .env
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
shortcode = os.getenv("SHORTCODE")
passkey = os.getenv("PASSKEY")
phone_number = os.getenv("PHONE")

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json()['access_token']

def stk_push(amount):
    token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://example.com/callback",
        "AccountReference": "MPesaPay",
        "TransactionDesc": "Payment"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )
    return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        amount = request.form["amount"]
        response = stk_push(amount)
        return render_template("index.html", response=response)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
