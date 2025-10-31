import sqlite3
import time

def init_db():
    """Initialize the database with users table"""
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                uses_left INTEGER,
                premium_until INTEGER
            )
        ''')
        conn.commit()

def get_user(user_id):
    """Get user data from database

    Args:
        user_id: Telegram user ID

    Returns:
        tuple: (uses_left, premium_until) or (None, None) if user not found
    """
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT uses_left, premium_until FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row if row else (None, None)

def set_user(user_id, uses_left, premium_until):
    """Set or update user data in database

    Args:
        user_id: Telegram user ID
        uses_left: Number of free uses remaining
        premium_until: Unix timestamp when premium expires (or None)
    """
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, uses_left, premium_until)
            VALUES (?, ?, ?)
        ''', (user_id, uses_left, premium_until))
        conn.commit()

def grant_premium(user_id, duration_seconds):
    """Grant premium access to a user

    Args:
        user_id: Telegram user ID
        duration_seconds: Duration of premium access in seconds
    """
    now = int(time.time())
    uses_left, premium_until = get_user(user_id)

    # If user already has premium, extend it
    if premium_until and premium_until > now:
        new_premium_until = premium_until + duration_seconds
    else:
        new_premium_until = now + duration_seconds

    # Keep uses_left or set to 999 for display purposes
    if uses_left is None:
        uses_left = 999

    set_user(user_id, uses_left, new_premium_until)

def is_premium(user_id):
    """Check if user has active premium

    Args:
        user_id: Telegram user ID

    Returns:
        bool: True if user has active premium, False otherwise
    """
    now = int(time.time())
    uses_left, premium_until = get_user(user_id)
    return premium_until is not None and now < premium_until

def deduct_free_use(user_id):
    """Deduct one free use from user (only if not premium)

    Args:
        user_id: Telegram user ID
    """
    if is_premium(user_id):
        return  # Don't deduct if premium

    uses_left, premium_until = get_user(user_id)
    if uses_left and uses_left > 0:
        set_user(user_id, uses_left - 1, premium_until)

def get_remaining_uses(user_id):
    """Get number of remaining free uses

    Args:
        user_id: Telegram user ID

    Returns:
        int: Number of remaining free uses
    """
    uses_left, _ = get_user(user_id)
    return uses_left if uses_left else 0