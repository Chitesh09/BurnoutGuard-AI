🎓 BurnoutGuard AI

Campus Burnout Monitoring & Mental Wellness System

BurnoutGuard AI is a machine learning-powered web application designed to predict, monitor, and analyze student burnout risk in academic environments.

It provides both individual student assessment and campus-level analytics dashboards for CRs or faculty members.

Live Demo

(Add your Streamlit deployment link here after deployment)

 Problem Statement

Academic burnout is increasingly common among students due to academic pressure, irregular sleep cycles, stress, and screen overuse. Institutions lack real-time monitoring systems to proactively detect burnout risk.

BurnoutGuard AI aims to:

.Predict burnout risk using ML

.Track student trends over time

.Provide personalized action insights

.Offer campus-level burnout analytics

 Key Features
 .Student Dashboard

.Secure authentication system

.Burnout risk prediction using ML model

.Animated risk score visualization

.Weekly burnout trend tracking

.Mood journal logging

.Personalized action recommendations

📊 CR / Faculty Dashboard

.Total students & assessment metrics

.Average campus risk score

.High-risk percentage tracking

.Risk distribution visualization

.Campus-wide burnout trend graph

.Recent high-risk student alerts

.Bulk CSV prediction support

🧪 Machine Learning Model

.Algorithm: Random Forest Classifier

Features Used:

.Sleep Hours

.Screen Time

.Study Hours

.Attendance Percentage

.Stress Level

Output Classes:

.Low Risk

.Medium Risk

.High Risk

.The model generates probability-based risk scoring for smoother interpretation.

🛠 Tech Stack

.Python

.Streamlit

.Scikit-Learn

.Pandas & NumPy

.SQLite

.Bcrypt (Password Hashing)

.Plotly

.GitHub

.Streamlit Cloud Deployment

🔐 Authentication System

.Secure password hashing using bcrypt

.Session persistence handling

.Role-based dashboard access (Student / CR)

📁 Project Structure 

BurnoutGuard-AI/
│
├── app/
│   ├── streamlit_app.py
│   ├── database.py
│   ├── auth.py
│
├── model/
│   └── burnout_model.pkl
│
├── dataset/
│   └── burnout_data.csv
│
├── requirements.txt
├── README.md

🎯 Future Improvements

.Cloud database integration (PostgreSQL / Supabase)

.Model explainability (SHAP integration)

.Email alert system for high-risk cases

.Admin-level campus analytics panel

💡 Author

Developed as a full-stack AI system for academic wellness monitoring and placement portfolio demonstration.