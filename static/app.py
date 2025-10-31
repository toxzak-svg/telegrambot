from flask import Flask, request, jsonify, send_from_directory
import telebot
from telebot import types
import hashlib
import hmac
import os
import urllib.parse
import json

# Initialize Flask BEFORE defining routes
app = Flask(__name__, static_folder='static')

TOKEN = "YOUR_BOTFATHER_TOKEN"  # Replace with your actual Telegram bot token
bot = telebot.TeleBot(TOKEN)
PREMIUM_PRICE = 99

# --- [Optional] Secure verification of initData from Telegram ---
def verify_init_data(init_data):
    # Telegram recommends HMAC verification: https://core.telegram.org/bots/webapps#checking-user-authorization
    params = urllib.parse.parse_qs(init_data)
    params_dict = {k: v[0] for k, v in params.items()}
    hash_to_check = params_dict.pop('hash', None)
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(params_dict.items())])
    secret_key = hmac.new(
        key=bytes(TOKEN, 'utf-8'),
        msg=b'WebAppData',
        digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=bytes(data_check_string, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_to_check, params_dict

@app.route("/")
def index():
    # Load the HTML mini app from static directory
    return send_from_directory(app.static_folder, "index.html")

@app.route("/static/<path:path>")
def static_files(path):
    # Serve other static files (JS, CSS, etc.)
    return send_from_directory(app.static_folder, path)

@app.route("/get_invoice", methods=["POST"])
def get_invoice():
    data = request.json
    initData = data.get("initData", "")
    # Uncomment for real security in production
    # is_verified, params = verify_init_data(initData) if initData else (True, {"user": '{"id":123456789}'})
    # if not is_verified:
    #     return jsonify({"error":"Init data not verified."}), 403

    # Parse Telegram user ID from params (you can adjust for stricter parsing)
    # For proof-of-concept, fall back to a default ID
    try:
        params = urllib.parse.parse_qs(initData)
        user_json = params.get('user', ['{"id":123456789}'])[0]
        user_id = json.loads(user_json)["id"]
    except Exception:
        user_id = 123456789

    prices = [types.LabeledPrice(label="Weekly Unlimited Text Utility", amount=PREMIUM_PRICE)]
    invoice_url = bot.create_invoice_link(
        title="Weekly Premium",
        description="Unlock unlimited text utility for one week!",
        payload="weekly_premium",
        provider_token="",       # Stars payments: leave blank
        currency="XTR",
        prices=prices
    )
    return jsonify({"invoice_url": invoice_url})

if __name__ == "__main__":
    app.run()
