import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json

from database import (
    create_tables,
    save_burnout_record,
    get_user_records,
    save_mood_entry,
    get_mood_entries,
    get_total_students,
    get_total_assessments,
    get_average_risk,
    get_high_risk_percentage,
    get_risk_distribution,
    get_recent_high_risk,
    get_campus_trend
)

from auth import register_user, login_user


# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="BurnoutGuard",
    page_icon="🎓",
    layout="wide"
)

# ===============================
# SaaS STYLE
# ===============================

st.markdown("""
<style>
body { background-color: #0E1117; }
.main { background-color: #0E1117; }
h1, h2, h3 { color: #FFFFFF; }

.metric-card {
    padding: 20px;
    border-radius: 16px;
    color: white;
    text-align: center;
    font-weight: 600;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
}

.card-blue { background: linear-gradient(135deg, #3A8DFF, #0052D4); }
.card-purple { background: linear-gradient(135deg, #8E2DE2, #4A00E0); }
.card-green { background: linear-gradient(135deg, #00C853, #00695C); }
.card-red { background: linear-gradient(135deg, #FF416C, #FF4B2B); }
</style>
""", unsafe_allow_html=True)

# ===============================
# INIT DB
# ===============================

create_tables()

# ===============================
# LOGIN PERSISTENCE
# ===============================

LOGIN_FILE = "login_state.json"

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None and os.path.exists(LOGIN_FILE):
    with open(LOGIN_FILE, "r") as f:
        st.session_state.user = json.load(f)


# ===============================
# LOGIN PAGE
# ===============================

def login_page():
    st.title("🔐 BurnoutGuard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        success, result = login_user(username, password)

        if success:
            clean_user = {}
            for key, value in result.items():
                if isinstance(value, bytes):
                    clean_user[key] = value.decode("utf-8")
                else:
                    clean_user[key] = value

            st.session_state.user = clean_user

            with open(LOGIN_FILE, "w") as f:
                json.dump(clean_user, f)

            st.rerun()
        else:
            st.error(result)

    st.markdown("---")

    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()


# ===============================
# REGISTER PAGE
# ===============================

def register_page():
    st.title("📝 Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["student", "cr"])

    if st.button("Register"):
        success, message = register_user(username, password, role)
        if success:
            st.success(message)
        else:
            st.error(message)

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ===============================
# STUDENT DASHBOARD
# ===============================

def student_dashboard():

    st.title("🎓 Student Dashboard")
    st.write(f"Welcome, {st.session_state.user['username']}")

    tabs = st.tabs(["Assessment", "Trends", "Mood Journal", "Profile"])

    model = joblib.load("model/burnout_model.pkl")

    # -------- ASSESSMENT --------
    with tabs[0]:

        st.subheader("Burnout Assessment")

        col1, col2 = st.columns(2)

        with col1:
            sleep = st.slider("Sleep Hours", 0, 12, 6)
            study = st.slider("Study Hours", 0, 12, 4)

            st.markdown("### Stress Level Scale")
            st.markdown("😫 1 = Extremely Stressed  |  😐 5 = Neutral  |  😄 10 = Very Happy")

            stress = st.slider("Select Your Stress Level", 1, 10, 5)

        with col2:
            screen = st.slider("Screen Time", 0, 12, 4)
            attendance = st.slider("Attendance %", 0, 100, 75)

        if st.button("Analyze Burnout"):

            input_data = np.array([[sleep, screen, study, attendance, stress]])
            prediction = model.predict(input_data)[0]
            probabilities = model.predict_proba(input_data)[0]
            confidence_dict = dict(zip(model.classes_, probabilities))

            risk_score = (
                confidence_dict.get("Low", 0) * 20 +
                confidence_dict.get("Medium", 0) * 60 +
                confidence_dict.get("High", 0) * 100
            )

            save_burnout_record(
                st.session_state.user["id"],
                sleep, screen, study, attendance, stress,
                risk_score,
                prediction
            )

            # Animated Risk Meter
            risk_color = "#00C853"
            if risk_score >= 70:
                risk_color = "#FF4B2B"
            elif risk_score >= 40:
                risk_color = "#FF9800"

            st.markdown(f"""
            <div style="
                background:#1c1f26;
                padding:30px;
                border-radius:20px;
                text-align:center;
            ">
                <h2 style="color:{risk_color}; font-size:50px;">
                    {round(risk_score,1)}%
                </h2>
                <p style="color:white; font-size:18px;">
                    {prediction} Burnout Risk
                </p>
            </div>
            """, unsafe_allow_html=True)

    # -------- TRENDS --------
    with tabs[1]:

        st.subheader("Weekly Burnout Trend")

        records = get_user_records(st.session_state.user["id"])

        if records:
            df = pd.DataFrame([dict(row) for row in records])
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            st.line_chart(df.set_index("date")["risk_score"])
        else:
            st.info("No data yet.")

    # -------- MOOD --------
    with tabs[2]:

        st.subheader("Mood Journal")

        mood_text = st.text_area("How are you feeling today?")
        mood_rating = st.slider("Mood Rating (1-10)", 1, 10, 5)

        if st.button("Save Mood Entry"):
            save_mood_entry(
                st.session_state.user["id"],
                mood_text,
                mood_rating
            )
            st.success("Mood saved!")

        moods = get_mood_entries(st.session_state.user["id"])
        if moods:
            mood_df = pd.DataFrame([dict(row) for row in moods])
            st.dataframe(mood_df)

    # -------- PROFILE --------
    with tabs[3]:

        st.subheader("Profile Info")
        st.write(f"Username: {st.session_state.user['username']}")
        st.write(f"Role: {st.session_state.user['role']}")

        if st.button("Logout"):
            st.session_state.user = None
            if os.path.exists(LOGIN_FILE):
                os.remove(LOGIN_FILE)
            st.rerun()


# ===============================
# CR DASHBOARD
# ===============================

def cr_dashboard():

    st.title("📊 Campus Burnout Analytics")

    total_students = get_total_students()
    total_assessments = get_total_assessments()
    avg_risk = get_average_risk()
    high_percent = get_high_risk_percentage()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card card-blue">
            <h3>Total Students</h3>
            <h2>{total_students}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card card-purple">
            <h3>Total Assessments</h3>
            <h2>{total_assessments}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card card-green">
            <h3>Avg Risk Score</h3>
            <h2>{round(avg_risk,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card card-red">
            <h3>% High Risk</h3>
            <h2>{round(high_percent,2)}%</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Risk Distribution")

    dist = get_risk_distribution()
    if dist:
        df_dist = pd.DataFrame([dict(row) for row in dist])
        df_dist = df_dist.set_index("burnout_level")
        st.bar_chart(df_dist["count"])

    st.markdown("---")

    st.subheader("Campus Trend")

    trend = get_campus_trend()
    if trend:
        df_trend = pd.DataFrame([dict(row) for row in trend])
        df_trend["date"] = pd.to_datetime(df_trend["date"])
        df_trend = df_trend.sort_values("date")
        st.line_chart(df_trend.set_index("date")["avg_risk"])

    st.markdown("---")

    st.subheader("Recent High Risk Students")

    high_students = get_recent_high_risk()
    if high_students:
        df_high = pd.DataFrame([dict(row) for row in high_students])
        st.dataframe(df_high)

    if st.button("Logout"):
        st.session_state.user = None
        if os.path.exists(LOGIN_FILE):
            os.remove(LOGIN_FILE)
        st.rerun()


# ===============================
# ROUTING
# ===============================

# ===============================
# ROUTING
# ===============================

# Try restoring session only if not already logged in
if st.session_state.user is None:
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r") as f:
                st.session_state.user = json.load(f)
        except:
            st.session_state.user = None

# Now decide what to show
if st.session_state.user is None:

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    else:
        register_page()

else:
    role = st.session_state.user["role"]

    if role == "student":
        student_dashboard()
    else:
        cr_dashboard()