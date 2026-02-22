import bcrypt
import uuid
from database import get_connection
from datetime import datetime

# ===============================
# REGISTER USER
# ===============================

def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
        INSERT INTO users (username, password, role, created_at)
        VALUES (?, ?, ?, ?)
        """, (
            username,
            hashed_pw,
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()
        return True, "User registered successfully!"

    except:
        conn.close()
        return False, "Username already exists."

# ===============================
# LOGIN USER
# ===============================

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):

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
