import sqlite3
from datetime import datetime

DB_FILE = "antaryami.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        blocked INTEGER DEFAULT 0,
        reset_token TEXT,
        reset_token_expiry DATETIME
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        user_input TEXT,
        ai_response TEXT,
        thread_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users(email)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        reason TEXT,
        reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    )
    """)

    conn.commit()
    conn.close()

def create_user(email, password_hash, role='user'):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email, password_hash, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_reset_token(email, token, expiry):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?", (token, expiry, email))
    conn.commit()
    conn.close()

def reset_password(email, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE email = ?", (new_password_hash, email))
    conn.commit()
    conn.close()

def block_user(email, block=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET blocked = ? WHERE email = ?", (1 if block else 0, email))
    conn.commit()
    conn.close()

def save_chat(user_email, user_input, ai_response, thread_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (user_email, user_input, ai_response, thread_id)
        VALUES (?, ?, ?, ?)
    """, (user_email, user_input, ai_response, thread_id))
    conn.commit()
    conn.close()

def get_user_chats(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE user_email = ? ORDER BY timestamp DESC", (user_email,))
    chats = cursor.fetchall()
    conn.close()
    return chats

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, role, blocked FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def report_chat(chat_id, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (chat_id, reason) VALUES (?, ?)", (chat_id, reason))
    conn.commit()
    conn.close()

def export_chats_to_csv():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM chats", conn)
    conn.close()
    return df.to_csv(index=False).encode('utf-8')

def count_registered_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
