# Telegram Bot with Stars Payment Integration

This bot integrates Telegram Stars payments to monetize utility commands. Users get free uses per week, and can purchase premium access for unlimited usage.

## Setup

### Environment Variables

For security reasons, the bot token is now stored as an environment variable instead of being hardcoded in the source code.

**Required Environment Variable:**
- `TELEGRAM_TOKEN` - Your Telegram bot token from @BotFather

**How to set up:**

1. **Linux/Mac:**
```bash
export TELEGRAM_TOKEN="your_bot_token_here"
```

2. **Windows (Command Prompt):**
```cmd
set TELEGRAM_TOKEN=your_bot_token_here
```

3. **Windows (PowerShell):**
```powershell
$env:TELEGRAM_TOKEN="your_bot_token_here"
```

4. **Using .env file (recommended for development):**
Create a `.env` file in the project root:
```
TELEGRAM_TOKEN=your_bot_token_here
```
Then use a package like `python-dotenv` to load it:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Note:** The bot will raise a `ValueError` if the `TELEGRAM_TOKEN` environment variable is not set, ensuring you don't accidentally run the bot without proper configuration.

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

## Configuration

### Premium Settings
- **Duration**: Set in `PREMIUM_DURATION_DAYS` (default: 7 days)
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

### Environment variable errors?
1. Make sure `TELEGRAM_TOKEN` is set in your environment
2. Verify the token value is correct (get it from @BotFather)
3. If using .env file, ensure it's in the project root and being loaded

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
✅ Secure token management with environment variables

## License

Feel free to use and modify for your projects!
