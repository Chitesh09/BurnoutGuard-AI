import sqlite3
from datetime import datetime

DB_NAME = "burnout.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        role TEXT NOT NULL,
        login_token TEXT
    )
    """)

    # Burnout records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS burnout_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sleep REAL,
        screen REAL,
        study REAL,
        attendance REAL,
        stress REAL,
        risk_score REAL,
        burnout_level TEXT,
        date TEXT
    )
    """)

    # Mood entries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mood_text TEXT,
        mood_rating INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()