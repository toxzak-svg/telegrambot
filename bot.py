# bot.py - Telegram bot with Stars payment integration
import time
from database import init_db, get_user, set_user
import telebot
from telebot import types

# Initialize database
init_db()

# Bot configuration
TOKEN = "8497823601:AAGqS3S0FV1AvMuEsC_txUDQG0xUi9e1ogo"
bot = telebot.TeleBot(TOKEN)

# Configuration
FREE_WEEKLY = 3  # Free uses per week
PREMIUM_PRICE_STARS = 10  # Price in Telegram Stars for 1 week premium
SECONDS_IN_WEEK = 604800  # 7 days in seconds

# Telegram Stars payment configuration
PREMIUM_DURATION_DAYS = 7  # Premium duration after payment

# Helper function to check if user can use utility
def can_use_utility(user_id):
    """Check if user has uses left or active premium"""
    now = int(time.time())
    uses_left, premium_until = get_user(user_id)

    # Check if premium is active
    if premium_until and now < premium_until:
        return True, "premium"

    # Check if it's a new week (reset free uses)
    if premium_until is None or now > premium_until:
        # New week, reset free uses
        set_user(user_id, FREE_WEEKLY, now + SECONDS_IN_WEEK)
        return True, "free"

    # Check if user has free uses left
    if uses_left and uses_left > 0:
        return True, "free"

    return False, None

def deduct_use(user_id):
    """Deduct one use from user's free uses"""
    uses_left, premium_until = get_user(user_id)
    now = int(time.time())

    # Don't deduct if premium is active
    if premium_until and now < premium_until:
        return

    # Deduct one use
    if uses_left and uses_left > 0:
        set_user(user_id, uses_left - 1, premium_until)

# Command handlers

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command and check for 'premium' parameter"""
    user_id = message.from_user.id

    # Check if user wants to upgrade to premium
    # Command format: /start premium
    if len(message.text.split()) > 1 and message.text.split()[1].lower() == 'premium':
        send_premium_invoice(message)
    else:
        # Normal start message
        can_use, usage_type = can_use_utility(user_id)

        if usage_type == "premium":
            status_text = "✨ You have Premium access!"
        else:
            uses_left, _ = get_user(user_id)
            status_text = f"📊 Free uses remaining: {uses_left}/{FREE_WEEKLY}"

        markup = types.InlineKeyboardMarkup()
        upgrade_btn = types.InlineKeyboardButton(
            "⭐ Upgrade to Premium",
            callback_data="upgrade_premium"
        )
        markup.add(upgrade_btn)

        bot.send_message(
            message.chat.id,
            f"Welcome to TeleTextPlus! 🎉\n\n{status_text}\n\n"
            f"Upgrade to Premium for unlimited access!",
            reply_markup=markup
        )

@bot.message_handler(commands=['premium'])
def handle_premium_command(message):
    """Handle /premium command - show premium info and payment option"""
    send_premium_invoice(message)

@bot.callback_query_handler(func=lambda call: call.data == "upgrade_premium")
def handle_upgrade_callback(call):
    """Handle upgrade button press"""
    bot.answer_callback_query(call.id)
    send_premium_invoice(call.message)

def send_premium_invoice(message):
    """Send Telegram Stars invoice for premium upgrade"""
    user_id = message.chat.id

    # Check if already premium
    can_use, usage_type = can_use_utility(message.from_user.id)
    if usage_type == "premium":
        bot.send_message(
            user_id,
            "✨ You already have Premium access!"
        )
        return

    # Create invoice for Telegram Stars payment
    # Note: Telegram Stars use "XTR" as currency
    prices = [types.LabeledPrice(
        label="Premium Access (7 days)",
        amount=PREMIUM_PRICE_STARS  # Amount in Stars
    )]

    try:
        bot.send_invoice(
            chat_id=user_id,
            title="TeleTextPlus Premium",
            description=f"Get unlimited access for {PREMIUM_DURATION_DAYS} days! No more weekly limits.",
            invoice_payload=f"premium_upgrade_{user_id}",  # Payload to identify payment
            provider_token="",  # Empty for Telegram Stars
            currency="XTR",  # Telegram Stars currency code
            prices=prices,
            start_parameter="premium_payment"
        )
    except Exception as e:
        bot.send_message(
            user_id,
            f"❌ Error creating payment invoice: {str(e)}\n\n"
            "Please make sure Telegram Stars payments are enabled for your bot."
        )

@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(pre_checkout_query):
    """
    Handle pre-checkout query - called before payment confirmation
    This is where you can validate the payment before it's processed
    """
    # Always approve the checkout (you can add validation logic here)
    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    """
    Handle successful payment confirmation
    Update database to set premium_until timestamp
    """
    user_id = message.from_user.id
    payment_info = message.successful_payment

    # Calculate premium expiration time (7 days from now)
    now = int(time.time())
    premium_until = now + (PREMIUM_DURATION_DAYS * 24 * 60 * 60)  # 7 days in seconds

    # Update database - set uses to unlimited (999) and premium_until timestamp
    set_user(user_id, 999, premium_until)  # 999 uses as "unlimited" indicator

    # Send confirmation message
    bot.send_message(
        message.chat.id,
        f"✨ Payment successful! Thank you!\n\n"
        f"🎉 You now have Premium access for {PREMIUM_DURATION_DAYS} days!\n"
        f"💫 Enjoy unlimited access to all features!\n\n"
        f"Transaction ID: {payment_info.telegram_payment_charge_id}"
    )

    # Log the successful payment (optional)
    print(f"Premium upgrade successful for user {user_id}. "
          f"Charge ID: {payment_info.telegram_payment_charge_id}, "
          f"Amount: {payment_info.total_amount} Stars")

# Start the bot (for local testing)
if __name__ == '__main__':
    print("Bot started...")
    bot.infinity_polling()