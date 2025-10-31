# Telegram Bot with Stars Payment Integration

This bot integrates Telegram Stars payments to monetize utility commands. Users get free uses per week, and can purchase premium access for unlimited usage.

## Features Implemented

✅ **Telegram Stars Payment Integration**
- Users can purchase premium access with Telegram Stars
- Beginner-friendly payment flow
- Automatic payment verification

✅ **Usage Tracking**
- 3 free uses per week for all users
- Premium users get unlimited uses
- Automatic weekly reset of free uses

✅ **Database Management**
- SQLite database tracks users, uses_left, and premium_until
- Helper functions for easy data management
- Automatic premium expiration handling

## File Structure

### bot.py
Main bot file with:
- Payment invoice sending (`send_payment_invoice`)
- Pre-checkout handler (`process_pre_checkout`)
- Successful payment handler (`process_successful_payment`)
- Usage checking (`can_use_utility`)
- Example utility command (`/text`)

### database.py
Database functions:
- `init_db()` - Initialize database
- `get_user(user_id)` - Get user data
- `set_user(user_id, uses_left, premium_until)` - Update user data
- `grant_premium(user_id, duration_seconds)` - Grant premium access
- `is_premium(user_id)` - Check premium status
- `deduct_free_use(user_id)` - Deduct one free use
- `get_remaining_uses(user_id)` - Get remaining free uses

### app.py
Flask wrapper (if needed for web hooks)

## Configuration

```python
FREE_WEEKLY = 3  # Free uses per week
PREMIUM_PRICE_STARS = 10  # Price in Telegram Stars
SECONDS_IN_WEEK = 604800  # 1 week duration
```

## Bot Commands

- `/start` - Welcome message and instructions
- `/text <your text>` - Example utility (converts to uppercase)
- `/status` - Check usage and premium status
- `/buy` - Purchase premium access with Telegram Stars

## How It Works

### 1. User Tries a Utility Command
When a user runs `/text hello`:
1. Bot checks if user can use the utility (`can_use_utility`)
2. If yes: processes the command and deducts a free use (if not premium)
3. If no: sends message with payment option

### 2. User Purchases Premium
When a user runs `/buy`:
1. Bot sends Telegram Stars invoice
2. User completes payment in Telegram
3. Bot receives `pre_checkout_query` (approves it)
4. Bot receives `successful_payment` message
5. Bot grants premium for 1 week
6. Bot sends confirmation message

### 3. Premium Access
- Premium users bypass usage limits
- Premium expires after 1 week (604800 seconds)
- Can be extended by purchasing again

## Testing Guide

### Step 1: Start the Bot
```bash
python bot.py
```

### Step 2: Test Free Uses
1. Send `/start` to see welcome message
2. Send `/text hello world` three times
3. On the 4th try, you'll see the payment prompt

### Step 3: Test Status
```
/status
```
Shows remaining free uses or premium status

### Step 4: Test Payment (Testing Mode)
To test payments:
1. Make sure your bot is added to @BotFather
2. Use Telegram's test environment OR
3. Use a small amount of Stars for real testing
4. Send `/buy`
5. Complete the payment
6. Bot will grant premium access

### Step 5: Test Premium Status
```
/status
```
Should show unlimited uses and time remaining

### Step 6: Test Unlimited Usage
Try `/text` more than 3 times - should work unlimited times

## Adding Your Own Utility Commands

To add a new utility command:

```python
# 1. Create the utility function
def process_your_utility(message):
    user_input = message.text.replace('/yourcommand ', '', 1)
    # Your utility logic here
    result = your_processing(user_input)
    bot.send_message(message.chat.id, f"Result: {result}")

# 2. Create the command handler with payment check
@bot.message_handler(commands=['yourcommand'])
def your_utility_command(message):
    user_id = message.from_user.id

    # Check if user can use the utility
    can_use, status = can_use_utility(user_id)

    if can_use:
        # Process the utility
        process_your_utility(message)

        # Deduct use if not premium
        if status == "free":
            deduct_use(user_id)
            uses_left, _ = get_user(user_id)
            bot.send_message(message.chat.id, f"Uses left: {uses_left}")
    else:
        # Send payment prompt
        bot.send_message(
            message.chat.id,
            "❌ No uses left! Use /buy to get premium."
        )
```

## Important Notes

### Telegram Stars Payment
- **Currency Code**: `XTR` (Telegram Stars)
- **Provider Token**: Empty string `""` for Stars
- **Price**: Set in `PREMIUM_PRICE_STARS` (in whole Stars, not fractions)

### Database
- Uses SQLite (`db.sqlite3`)
- Automatically created on first run
- Stores: `user_id`, `uses_left`, `premium_until` (Unix timestamp)

### Weekly Reset
- Free uses reset automatically when user tries to use the bot after the week expires
- No cron job needed - handled in `can_use_utility` function

## Troubleshooting

### Payment not working?
1. Check bot token is correct
2. Ensure currency is set to `XTR`
3. Provider token must be empty string for Stars
4. Make sure bot has payment permissions from @BotFather

### Database errors?
1. Check `db.sqlite3` file exists and has write permissions
2. Run `init_db()` to create tables

### Users not tracked?
1. Check database functions are being called
2. Verify `user_id` is being passed correctly

## Next Steps

1. **Add more utility commands** following the pattern
2. **Customize pricing** by changing `PREMIUM_PRICE_STARS`
3. **Adjust free uses** by changing `FREE_WEEKLY`
4. **Add analytics** to track payments and usage
5. **Deploy to production** server for 24/7 operation

## Code Quality

✅ Beginner-friendly with comments
✅ Easy to test with `/status` command
✅ Modular design - easy to add new commands
✅ Error handling for payment failures
✅ Clear separation of concerns (bot logic, database, utilities)

## License

Feel free to use and modify for your projects!