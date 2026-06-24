
import streamlit as st
import pickle
import numpy as np
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
import os

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Student Performance Predictor",
    page_icon="🎓",
    layout="wide"
)
# ---------------- LOGIN SYSTEM ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .stApp{
        background: linear-gradient(135deg,#2563eb,#7c3aed);
    }

    .login-box{
        background:white;
        padding:40px;
        border-radius:20px;
        max-width:450px;
        margin:auto;
        margin-top:80px;
        box-shadow:0px 8px 25px rgba(0,0,0,0.2);
        text-align:center;
    }

    .login-title{
        color:#2563eb;
        font-size:32px;
        font-weight:bold;
    }

    .login-subtitle{
        color:gray;
        margin-bottom:20px;
    }

    .stButton>button{
        width:100%;
        height:50px;
        border-radius:10px;
        font-size:18px;
        font-weight:bold;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-box">
        <h1>🎓</h1>
        <div class="login-title">
            Student Performance System
        </div>
        <div class="login-subtitle">
            LOGIN PORTAL
        </div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("👤 USERNAME")
    password = st.text_input("🔑 PASSWORD", type="password")

    if st.button("🚀 Login"):

        users = {
            "admin": "admin123",
            "teacher": "teacher123"
        }

        if username in users and users[username] == password:

            st.success("✅ Login Successful")

            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("❌ Invalid Username or Password")

    st.stop()
# ---------------- DATABASE ---------------- #

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
roll TEXT,
attendance INTEGER,
prediction REAL
)
""")

conn.commit()





# ---------------- DARK MODE ---------------- #

dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
    <style>
    .stApp{
        background-color:#0E1117;
        color:white;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- MODEL ---------------- #

model = pickle.load(open("student_model.pkl","rb"))

# ---------------- HEADER ---------------- #

st.markdown("""
<div class='header'>
<h1>🎓 Student Academic Performance Prediction System</h1>
<p>Predict student performance using Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("📘 Project Information")

st.sidebar.info("""
Predict student performance using:

• Attendance

• Assignment Score

• Internal Assessment

• Quiz Score

• Previous Marks
""")

# ---------------- DELETE RECORD ---------------- #

st.sidebar.subheader("🗑 Delete Student Record")

roll_delete = st.sidebar.text_input(
    "Enter Roll Number"
)

if st.sidebar.button("Delete Record"):

    cursor.execute(
        "SELECT * FROM students WHERE roll = ?",
        (roll_delete,)
    )

    record = cursor.fetchone()

    if record:

        cursor.execute(
            "DELETE FROM students WHERE roll = ?",
            (roll_delete,)
        )

        conn.commit()

        st.sidebar.success(
            f"Record with Roll No {roll_delete} deleted!"
        )

    else:

        st.sidebar.error(
            "Roll Number not found!"
        )
# ---------------- STUDENT INFO ---------------- #

st.markdown("## 👤 Student Information")

colA,colB = st.columns(2)

with colA:
    student_name = st.text_input("Student Name")

with colB:
    roll_no = st.text_input("Roll Number")

st.markdown("---")

# ---------------- INPUTS ---------------- #

st.markdown("## 📊 Academic Indicators")

col1,col2 = st.columns(2)

with col1:

    attendance = st.slider(
        "Attendance (%)",
        0,100,75
    )

    assignment = st.slider(
        "Assignment Score",
        0,100,70
    )

    internal = st.slider(
        "Internal Assessment",
        0,100,70
    )

with col2:

    quiz = st.slider(
        "Quiz Score",
        0,100,70
    )

    previous = st.slider(
        "Previous Marks",
        0,100,70
    )

# ---------------- METRICS ---------------- #

st.markdown("### 📈 Academic Overview")

c1,c2,c3 = st.columns(3)

with c1:
    st.metric("Attendance", f"{attendance}%")

with c2:
    st.metric("Assignment", assignment)

with c3:
    st.metric("Internal", internal)

# ---------------- GAUGE ---------------- #

st.markdown("### 🎯 Attendance Gauge")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=attendance,
    title={"text":"Attendance %"}
))

st.plotly_chart(fig, use_container_width=True)

# ---------------- PREDICTION ---------------- #

if st.button("🚀 Predict Performance"):

    data = pd.DataFrame({
        "Attendance": [attendance],
        "Assignment": [assignment],
        "Internal": [internal],
        "Quiz": [quiz],
        "PreviousMarks": [previous]
    })

    prediction = model.predict(data)

    marks = prediction[0]

    cursor.execute(
    """
    INSERT INTO students
    (name,roll,attendance,prediction)
    VALUES (?,?,?,?)
    """,
    (student_name,roll_no,attendance,float(marks))
    )

    conn.commit()

    st.subheader("🎯 Prediction Result")

    st.metric(
        "Predicted Final Marks",
        f"{marks:.2f}"
    )

    if marks >= 80:
        st.success("⭐ Excellent Performance")
        st.balloons()

    elif marks >= 60:
        st.info("👍 Good Performance")

    elif marks >= 40:
        st.warning("⚠ Average Performance")

    else:
        st.error("❌ Poor Performance")

    if marks < 40:
        st.error("🚨 High Risk Student")

    elif marks < 60:
        st.warning("⚠ Needs Improvement")

    else:
        st.success("✅ Student Performing Well")

    # PDF REPORT

    pdf_file = "report.pdf"

    c = canvas.Canvas(pdf_file)

    c.drawString(100,750,f"Student Name: {student_name}")
    c.drawString(100,720,f"Roll Number: {roll_no}")
    c.drawString(100,690,f"Predicted Marks: {marks:.2f}")

    c.save()

    with open(pdf_file,"rb") as file:

        st.download_button(
            "📄 Download PDF Report",
            file,
            "Student_Report.pdf",
            mime="application/pdf"
        )
# ---------------- CSS ---------------- #
st.markdown("---")
st.header("📊 Analytics Dashboard")

df = pd.read_sql_query(
    """
    SELECT
        name,
        roll,
        attendance,
        prediction
    FROM students
    """,
    conn
)
if len(df) > 0:

    # KPI Metrics

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "👨‍🎓 Total Students",
            len(df)
        )

    with c2:
        st.metric(
            "📈 Average Marks",
            round(df["prediction"].mean(), 2)
        )

    with c3:
        st.metric(
            "🏆 Highest Marks",
            round(df["prediction"].max(), 2)
        )

    # Bar Chart

    fig = px.bar(
        df,
        x="name",
        y="prediction",
        color="prediction",
        text_auto=".2f",
        title="🎓 Student Performance Predictions"
    )

    fig.update_layout(
    xaxis_title="Student Name",
    yaxis_title="Predicted Marks",
    template="plotly_white",
    height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Pie Chart

    st.subheader(
        "📊 Performance Distribution"
    )

    excellent = len(
        df[df["prediction"] >= 80]
    )

    good = len(
        df[
            (df["prediction"] >= 60)
            &
            (df["prediction"] < 80)
        ]
    )

    average = len(
        df[
            (df["prediction"] >= 40)
            &
            (df["prediction"] < 60)
        ]
    )

    poor = len(
        df[df["prediction"] < 40]
    )

    pie_df = pd.DataFrame({
        "Category": [
            "Excellent",
            "Good",
            "Average",
            "Poor"
        ],
        "Count": [
            excellent,
            good,
            average,
            poor
        ]
    })

    pie_fig = px.pie(
        pie_df,
        names="Category",
        values="Count",
        title="Student Performance Categories"
    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

    st.subheader(
        "📋 Student Records"
    )

    st.dataframe(df)

else:
    st.info(
        "No student records available yet."
    )
# ---------------- RECORDS ---------------- #

if st.sidebar.button("📋 View Student Records"):

    df = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    st.subheader("Saved Student Records")

    st.dataframe(df)

# ---------------- ANALYTICS ---------------- #


# ---------------- FOOTER ---------------- #

st.markdown("---")
st.markdown(
"### Developed using Python, Streamlit, Plotly, SQLite and Machine Learning"
)
