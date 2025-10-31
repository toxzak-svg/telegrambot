# app.py - Flask app for TeleTextPlus mini app with payment integration
from flask import Flask, request, jsonify, render_template, send_from_directory
import urllib.parse
import json
import time
from database import get_user, set_user

# Custom Flask class to avoid conflicts with Vue.js template syntax
class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='[%',
        variable_end_string='%]',
        comment_start_string='[#',
        comment_end_string='#]',
    ))

app = CustomFlask(__name__, static_folder='static')

# Configuration (same as bot.py)
FREE_WEEKLY = 3
PREMIUM_PRICE_STARS = 10
SECONDS_IN_WEEK = 604800

@app.route("/")
def index():
    """Serve the main HTML mini app page"""
    return render_template('index.html')

@app.route("/static/<path:path>")
def static_files(path):
    """Serve static files from the static directory"""
    return send_from_directory(app.static_folder, path)

@app.route("/get_user_status", methods=["POST"])
def get_user_status():
    """
    API endpoint to get user's premium status and remaining uses
    Called from the mini app frontend
    """
    try:
        data = request.json
        initData = data.get("initData", "")

        # Parse Telegram user ID from initData
        telegram_user_id = parse_user_id_from_init_data(initData)

        if not telegram_user_id:
            return jsonify({"error": "Invalid initData"}), 400

        # Get user data from database
        uses_left, premium_until = get_user(telegram_user_id)
        now = int(time.time())

        # Check if premium is active
        is_premium = premium_until and now < premium_until

        # Calculate remaining days if premium
        premium_days_left = 0
        if is_premium:
            premium_days_left = (premium_until - now) // 86400  # Convert seconds to days

        return jsonify({
            "success": True,
            "isPremium": is_premium,
            "usesLeft": uses_left if uses_left else 0,
            "freeWeekly": FREE_WEEKLY,
            "premiumDaysLeft": premium_days_left,
            "premiumPriceStars": PREMIUM_PRICE_STARS
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_invoice", methods=["POST"])
def get_invoice():
    """
    API endpoint to generate payment invoice link
    This triggers the bot to send a Telegram Stars invoice
    """
    try:
        data = request.json
        initData = data.get("initData", "")

        # Parse Telegram user ID from initData
        telegram_user_id = parse_user_id_from_init_data(initData)

        if not telegram_user_id:
            return jsonify({"error": "Invalid initData"}), 400

        # Check if already premium
        uses_left, premium_until = get_user(telegram_user_id)
        now = int(time.time())
        is_premium = premium_until and now < premium_until

        if is_premium:
            return jsonify({
                "error": "You already have Premium access!",
                "isPremium": True
            }), 400

        # Return the bot link to trigger payment
        # User should use the /start premium or /premium command in bot
        # Or click the upgrade button in the bot
        bot_username = "YOUR_BOT_USERNAME"  # Replace with your actual bot username
        invoice_link = f"https://t.me/{bot_username}?start=premium"

        return jsonify({
            "success": True,
            "invoiceLink": invoice_link,
            "message": "Click the link to upgrade via Telegram bot"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/record_use", methods=["POST"])
def record_use():
    """
    API endpoint to record usage of a utility feature
    Deducts one use from user's free uses (if not premium)
    """
    try:
        data = request.json
        initData = data.get("initData", "")

        # Parse Telegram user ID from initData
        telegram_user_id = parse_user_id_from_init_data(initData)

        if not telegram_user_id:
            return jsonify({"error": "Invalid initData"}), 400

        # Get user data
        uses_left, premium_until = get_user(telegram_user_id)
        now = int(time.time())

        # Check if premium is active (don't deduct uses)
        if premium_until and now < premium_until:
            return jsonify({
                "success": True,
                "isPremium": True,
                "usesLeft": uses_left
            })

        # Check if user has uses left
        if not uses_left or uses_left <= 0:
            return jsonify({
                "error": "No uses left. Please upgrade to Premium!",
                "usesLeft": 0
            }), 403

        # Deduct one use
        new_uses = uses_left - 1
        set_user(telegram_user_id, new_uses, premium_until)

        return jsonify({
            "success": True,
            "usesLeft": new_uses,
            "isPremium": False
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def parse_user_id_from_init_data(initData):
    """
    Helper function to parse Telegram user ID from initData
    For production, you should also verify the HMAC signature
    """
    try:
        # Parse the initData query string
        parsed = urllib.parse.parse_qs(initData)

        # Get the user JSON string
        user_json = parsed.get("user", [""])[0]

        if not user_json:
            return None

        # Parse the JSON to get user ID
        user_dict = json.loads(user_json)
        telegram_user_id = user_dict.get("id")

        return telegram_user_id
    except:
        return None

# Run the Flask app (for local testing)
if __name__ == '__main__':
    app.run(debug=True, port=5000)