import sqlite3
from datetime import datetime

DB_NAME = "burnout.db"


# ===============================
# CONNECTION
# ===============================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================
# CREATE TABLES
# ===============================

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # DROP old users table completely
    cursor.execute("DROP TABLE IF EXISTS users")

    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        role TEXT NOT NULL,
        login_token TEXT
    )
    """)

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
# ===============================
# STUDENT DATA
# ===============================

def save_burnout_record(user_id, sleep, screen, study, attendance, stress, risk_score, burnout_level):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO burnout_records 
        (user_id, sleep, screen, study, attendance, stress, risk_score, burnout_level, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, sleep, screen, study, attendance, stress,
        risk_score, burnout_level,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_records(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, risk_score 
        FROM burnout_records
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def save_mood_entry(user_id, mood_text, mood_rating):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mood_entries (user_id, mood_text, mood_rating, date)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        mood_text,
        mood_rating,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_mood_entries(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, mood_text, mood_rating
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data


# ===============================
# CAMPUS ANALYTICS
# ===============================

def get_total_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
    result = cursor.fetchone()
    conn.close()
    return result["count"]


def get_total_assessments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM burnout_records")
    result = cursor.fetchone()
    conn.close()
    return result["count"]


def get_average_risk():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(risk_score) as avg_risk FROM burnout_records")
    result = cursor.fetchone()
    conn.close()
    return result["avg_risk"] if result["avg_risk"] else 0


def get_high_risk_percentage():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM burnout_records")
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) as high_count 
        FROM burnout_records 
        WHERE burnout_level = 'High'
    """)
    high = cursor.fetchone()["high_count"]

    conn.close()

    if total == 0:
        return 0
    return (high / total) * 100


def get_risk_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT burnout_level, COUNT(*) as count
        FROM burnout_records
        GROUP BY burnout_level
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_recent_high_risk(limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT users.username, burnout_records.risk_score, burnout_records.date
        FROM burnout_records
        JOIN users ON burnout_records.user_id = users.id
        WHERE burnout_records.burnout_level = 'High'
        ORDER BY burnout_records.date DESC
        LIMIT ?
    """, (limit,))

    data = cursor.fetchall()
    conn.close()
    return data


def get_campus_trend():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, AVG(risk_score) as avg_risk
        FROM burnout_records
        GROUP BY date
        ORDER BY date ASC
    """)

    data = cursor.fetchall()
    conn.close()
    return data
