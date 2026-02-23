import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

from app.database import create_tables, save_burnout_record, get_user_records
from app.auth import register_user, login_user

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="BurnoutGuard",
    page_icon="🧠",
    layout="wide"
)

create_tables()

# ----------------------------
# GLASSMORPHISM + SaaS STYLE
# ----------------------------

st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}
.main {
    background-color: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
}
.card {
    padding:20px;
    border-radius:18px;
    background: rgba(255,255,255,0.08);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.4);
}
.sidebar .sidebar-content {
    background: rgba(0,0,0,0.4);
}
h1,h2,h3,h4 {
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# SESSION INIT
# ----------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

# ----------------------------
# LOGIN
# ----------------------------

def login_page():
    st.title("🧠 BurnoutGuard")
    st.subheader("AI-Powered Mental Wellness Companion")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        success, result = login_user(username, password)
        if success:
            st.session_state.user = result
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error(result)

    st.markdown("---")
    if st.button("Create Account"):
        st.session_state.page = "register"
        st.rerun()


# ----------------------------
# REGISTER
# ----------------------------

def register_page():
    st.title("✨ Create Your Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")
    role = st.selectbox("Select Role", ["student", "cr"])

    if st.button("Register"):
        success, message = register_user(username, password, role)
        if success:
            st.success("Account created successfully 🎉")
        else:
            st.error(message)

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ----------------------------
# GAUGE METER
# ----------------------------

def show_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Burnout Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#FF4B2B" if score>70 else "#FFA500" if score>40 else "#00C853"},
            'steps': [
                {'range': [0, 40], 'color': '#00C853'},
                {'range': [40, 70], 'color': '#FFA500'},
                {'range': [70, 100], 'color': '#FF4B2B'}
            ],
        }
    ))
    fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# STUDENT DASHBOARD
# ----------------------------

def student_dashboard():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Assessment", "Trends", "Logout"])

    model = joblib.load("model/burnout_model.pkl")

    if page == "Assessment":
        st.title("📊 Burnout Assessment")

        col1, col2 = st.columns(2)

        with col1:
            sleep = st.slider("Sleep Hours 😴", 0, 12, 6)
            study = st.slider("Study Hours 📚", 0, 12, 4)
            stress = st.slider("Stress Level 😫 → 😄", 1, 10, 5)

        with col2:
            screen = st.slider("Screen Time 📱", 0, 12, 4)
            attendance = st.slider("Attendance % 🎓", 0, 100, 75)

        if st.button("Analyze My Burnout Risk 🚀"):

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

            show_gauge(round(risk_score,1))

            if risk_score > 70:
                st.error("⚠ High Burnout Risk – Please slow down and take breaks.")
            elif risk_score > 40:
                st.warning("⚡ Moderate Risk – Maintain balance.")
            else:
                st.success("✅ You're doing well. Keep it up!")

    if page == "Trends":
        st.title("📈 Your Burnout Trends")

        records = get_user_records(st.session_state.user["id"])

        if records:
            df = pd.DataFrame([dict(row) for row in records])
            df["date"] = pd.to_datetime(df["date"])
            st.line_chart(df.set_index("date")["risk_score"])
        else:
            st.info("No records yet.")

    if page == "Logout":
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()


# ----------------------------
# ROUTING
# ----------------------------

if st.session_state.user is None:
    if st.session_state.page == "login":
        login_page()
    else:
        register_page()
else:
    student_dashboard()