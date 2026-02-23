import bcrypt
import uuid
import sqlite3
from app.database import get_connection


def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, hashed_pw, role))

        conn.commit()
        conn.close()
        return True, "User registered successfully!"

    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists."

    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        token = str(uuid.uuid4())

        cursor.execute(
            "UPDATE users SET login_token = ? WHERE id = ?",
            (token, user["id"])
        )

        conn.commit()

        user_dict = dict(user)
        user_dict["login_token"] = token

        conn.close()
        return True, user_dict

    conn.close()
    return False, "Invalid username or password."