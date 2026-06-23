# App.py
# ============================================================
# SMART MEDICAL ASSISTANCE SYSTEM
# FINAL YEAR PROJECT
# PART 1
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
import folium
import plotly.express as px

from pathlib import Path
from datetime import datetime
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from math import radians, sin, cos, sqrt, atan2

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Medical Assistance System",
    page_icon="🏥",
    layout="wide"
)

# ============================================================
# DATABASE
# ============================================================

DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "medical.db"

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    conn = sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn

# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = get_connection()

    cursor = conn.cursor()

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # REPORTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        file_name TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DISEASE HISTORY

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disease_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        symptoms TEXT,
        predicted_disease TEXT,
        confidence_score REAL,
        prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # CHATBOT HISTORY

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        user_message TEXT,
        bot_response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # HOSPITALS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_name TEXT,
        address TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        available_beds INTEGER,
        emergency_contact TEXT,
        rating REAL
    )
    """)

    conn.commit()
    conn.close()

# ============================================================
# INSERT DEFAULT HOSPITALS
# ============================================================

def insert_default_hospitals():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM hospitals"
    )

    count = cursor.fetchone()[0]

    if count == 0:

        hospitals = [

            (
                "Apollo Hospital",
                "Greams Road",
                "Chennai",
                13.0632,
                80.2518,
                45,
                "04428290200",
                4.8
            ),

            (
                "Fortis Malar Hospital",
                "Adyar",
                "Chennai",
                13.0067,
                80.2573,
                32,
                "04442892222",
                4.6
            ),

            (
                "MIOT Hospital",
                "Manapakkam",
                "Chennai",
                13.0216,
                80.1848,
                40,
                "04442002288",
                4.7
            ),

            (
                "SIMS Hospital",
                "Vadapalani",
                "Chennai",
                13.0500,
                80.2120,
                18,
                "04420002001",
                4.4
            )

        ]

        cursor.executemany("""
        INSERT INTO hospitals(
            hospital_name,
            address,
            city,
            latitude,
            longitude,
            available_beds,
            emergency_contact,
            rating
        )
        VALUES(
            ?,?,?,?,?,?,?,?
        )
        """, hospitals)

        conn.commit()

    conn.close()

# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# ============================================================
# USER FUNCTIONS
# ============================================================

def get_user(username):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user

def create_user(
    username,
    password,
    role="user"
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users(
            username,
            password,
            role
        )
        VALUES(
            ?,?,?
        )
        """,
        (
            username,
            hash_password(password),
            role
        )
    )

    conn.commit()
    conn.close()

# ============================================================
# REGISTER PAGE
# ============================================================

def register_page():

    st.title(
        "📝 User Registration"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm = st.text_input(
        "Confirm Password",
        type="password"
    )

    if st.button(
        "Register"
    ):

        if not username or not password:

            st.error(
                "Fill all fields."
            )

            return

        if password != confirm:

            st.error(
                "Passwords do not match."
            )

            return

        existing = get_user(
            username
        )

        if existing:

            st.warning(
                "User already exists."
            )

            return

        create_user(
            username,
            password
        )

        st.success(
            "Registration Successful"
        )

# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.title(
        "🔐 User Login"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login"
    ):

        user = get_user(
            username
        )

        if user is None:

            st.error(
                "User not found."
            )

            return

        if (
            user["password"]
            ==
            hash_password(password)
        ):

            st.session_state.logged_in = True

            st.session_state.username = (
                user["username"]
            )

            st.session_state.role = (
                user["role"]
            )

            st.success(
                "Login Successful"
            )

            st.rerun()

        else:

            st.error(
                "Invalid Password"
            )

# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "username" not in st.session_state:

    st.session_state.username = ""

if "role" not in st.session_state:

    st.session_state.role = "user"

# ============================================================
# INITIALIZE DATABASE
# ============================================================

create_tables()
insert_default_hospitals()
# ============================================================
# PART 2
# DISEASE PREDICTION + GPS HOSPITAL LOCATOR
# ============================================================

# ============================================================
# DISEASE KNOWLEDGE BASE
# ============================================================

DISEASE_DATA = {

    "Common Cold": {
        "symptoms": [
            "Cough",
            "Sneezing",
            "Runny Nose",
            "Sore Throat"
        ],
        "precautions": [
            "Drink warm fluids",
            "Take rest",
            "Avoid cold food"
        ]
    },

    "Viral Fever": {
        "symptoms": [
            "Fever",
            "Headache",
            "Body Pain",
            "Fatigue"
        ],
        "precautions": [
            "Drink water",
            "Take proper rest",
            "Monitor body temperature"
        ]
    },

    "Migraine": {
        "symptoms": [
            "Headache",
            "Nausea",
            "Vomiting",
            "Light Sensitivity"
        ],
        "precautions": [
            "Avoid bright lights",
            "Sleep adequately",
            "Reduce stress"
        ]
    },

    "Food Poisoning": {
        "symptoms": [
            "Vomiting",
            "Diarrhea",
            "Stomach Pain",
            "Nausea"
        ],
        "precautions": [
            "Drink ORS",
            "Avoid outside food",
            "Consult doctor"
        ]
    },

    "Respiratory Infection": {
        "symptoms": [
            "Cough",
            "Breathing Difficulty",
            "Chest Pain",
            "Fever"
        ],
        "precautions": [
            "Visit doctor",
            "Wear mask",
            "Follow medication"
        ]
    }
}

# ============================================================
# ALL SYMPTOMS
# ============================================================

ALL_SYMPTOMS = sorted(
    list(
        {
            symptom
            for disease in DISEASE_DATA.values()
            for symptom in disease["symptoms"]
        }
    )
)

# ============================================================
# SAVE PREDICTION
# ============================================================

def save_prediction(
    username,
    symptoms,
    disease,
    confidence
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO disease_history(
            username,
            symptoms,
            predicted_disease,
            confidence_score
        )
        VALUES(
            ?,?,?,?
        )
        """,
        (
            username,
            symptoms,
            disease,
            confidence
        )
    )

    conn.commit()
    conn.close()

# ============================================================
# PREDICTION ENGINE
# ============================================================

def predict_disease(
    selected_symptoms
):

    best_match = None

    highest_score = 0

    for disease, details in DISEASE_DATA.items():

        disease_symptoms = set(
            details["symptoms"]
        )

        selected = set(
            selected_symptoms
        )

        match = len(
            disease_symptoms.intersection(
                selected
            )
        )

        score = (
            match /
            len(disease_symptoms)
        )

        if score > highest_score:

            highest_score = score

            best_match = disease

    confidence = round(
        highest_score * 100,
        2
    )

    return (
        best_match,
        confidence
    )

# ============================================================
# DISEASE PAGE
# ============================================================

def disease_prediction_page():

    st.title(
        "🩺 Disease Prediction"
    )

    symptoms = st.multiselect(
        "Select Symptoms",
        ALL_SYMPTOMS
    )

    if st.button(
        "Predict Disease"
    ):

        if len(symptoms) == 0:

            st.warning(
                "Select symptoms."
            )

            return

        disease, confidence = (
            predict_disease(
                symptoms
            )
        )

        st.success(
            f"Predicted Disease: {disease}"
        )

        st.info(
            f"Confidence Score: {confidence}%"
        )

        st.subheader(
            "Precautions"
        )

        for precaution in DISEASE_DATA[
            disease
        ]["precautions"]:

            st.write(
                f"✔ {precaution}"
            )

        save_prediction(
            st.session_state.username,
            ", ".join(symptoms),
            disease,
            confidence
        )

# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371

    dlat = radians(
        lat2 - lat1
    )

    dlon = radians(
        lon2 - lon1
    )

    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon / 2) ** 2
    )

    c = (
        2 *
        atan2(
            sqrt(a),
            sqrt(1 - a)
        )
    )

    return (
        earth_radius * c
    )

# ============================================================
# GET USER GPS
# ============================================================

def get_user_location():

    location = (
        streamlit_geolocation()
    )

    if (
        location
        and location["latitude"]
        and location["longitude"]
    ):

        return (
            location["latitude"],
            location["longitude"]
        )

    return (
        None,
        None
    )

# ============================================================
# SEARCH HOSPITALS
# ============================================================

def get_nearby_hospitals(
    latitude,
    longitude,
    radius=10000
):

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"]
      (
        around:{radius},
        {latitude},
        {longitude}
      );
    );
    out;
    """

    url = (
        "https://overpass-api.de"
        "/api/interpreter"
    )

    try:

        response = requests.get(
            url,
            params={"data": query},
            timeout=30
        )

        data = response.json()

        hospitals = []

        for item in data["elements"]:

            name = (
                item.get(
                    "tags",
                    {}
                )
                .get(
                    "name",
                    "Unknown Hospital"
                )
            )

            lat = item["lat"]
            lon = item["lon"]

            distance = (
                calculate_distance(
                    latitude,
                    longitude,
                    lat,
                    lon
                )
            )

            hospitals.append(
                {
                    "Hospital": name,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Distance (km)": round(
                        distance,
                        2
                    )
                }
            )

        hospitals = sorted(
            hospitals,
            key=lambda x:
            x["Distance (km)"]
        )

        return hospitals

    except Exception as e:

        st.error(
            f"Error: {e}"
        )

        return []

# ============================================================
# DISPLAY MAP
# ============================================================

def display_hospital_map(
    user_lat,
    user_lon,
    hospitals
):

    fmap = folium.Map(
        location=[
            user_lat,
            user_lon
        ],
        zoom_start=13
    )

    folium.Marker(
        [
            user_lat,
            user_lon
        ],
        popup="Your Location",
        tooltip="You"
    ).add_to(fmap)

    for hospital in hospitals[:20]:

        folium.Marker(
            [
                hospital["Latitude"],
                hospital["Longitude"]
            ],
            popup=hospital["Hospital"],
            tooltip=hospital["Hospital"]
        ).add_to(fmap)

    st_folium(
        fmap,
        width=1200,
        height=500
    )

# ============================================================
# HOSPITAL LOCATOR PAGE
# ============================================================

def hospital_locator_page():

    st.title(
        "🏥 Nearby Hospital Finder"
    )

    latitude, longitude = (
        get_user_location()
    )

    if (
        latitude is None
        or longitude is None
    ):

        st.warning(
            "Please allow GPS access."
        )

        return

    st.success(
        "GPS Location Detected"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Latitude",
        round(latitude, 5)
    )

    col2.metric(
        "Longitude",
        round(longitude, 5)
    )

    radius = st.slider(
        "Search Radius (meters)",
        1000,
        20000,
        10000
    )

    if st.button(
        "Find Hospitals"
    ):

        hospitals = (
            get_nearby_hospitals(
                latitude,
                longitude,
                radius
            )
        )

        if not hospitals:

            st.error(
                "No hospitals found."
            )

            return

        df = pd.DataFrame(
            hospitals
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        display_hospital_map(
            latitude,
            longitude,
            hospitals
        )

        st.subheader(
            "Navigation"
        )

        for hospital in hospitals[:10]:

            maps_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&destination="
                f"{hospital['Latitude']},"
                f"{hospital['Longitude']}"
            )

            st.markdown(
                f"""
### {hospital['Hospital']}
Distance: **{hospital['Distance (km)']} km**

[Open in Google Maps]({maps_url})
"""
            )
            # ============================================================
# PART 3
# REPORTS + ANALYTICS + CHATBOT + ADMIN + MAIN APP
# ============================================================

# ============================================================
# SAVE REPORT
# ============================================================

def save_report(username, file_name):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports(
            username,
            file_name
        )
        VALUES(?,?)
        """,
        (
            username,
            file_name
        )
    )

    conn.commit()
    conn.close()

# ============================================================
# REPORT PAGE
# ============================================================

def report_page():

    st.title("📄 Medical Reports")

    uploaded_file = st.file_uploader(
        "Upload Medical Report",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:

        if st.button("Upload Report"):

            file_path = (
                UPLOAD_DIR /
                uploaded_file.name
            )

            with open(
                file_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            save_report(
                st.session_state.username,
                uploaded_file.name
            )

            st.success(
                "Report Uploaded Successfully"
            )

    conn = get_connection()

    reports = pd.read_sql_query(
        """
        SELECT *
        FROM reports
        WHERE username = ?
        ORDER BY upload_date DESC
        """,
        conn,
        params=(
            st.session_state.username,
        )
    )

    conn.close()

    if not reports.empty:

        st.subheader(
            "Uploaded Reports"
        )

        st.dataframe(
            reports,
            use_container_width=True
        )

# ============================================================
# ANALYTICS PAGE
# ============================================================

def analytics_page():

    st.title(
        "📊 Analytics Dashboard"
    )

    conn = get_connection()

    users_df = pd.read_sql_query(
        "SELECT * FROM users",
        conn
    )

    reports_df = pd.read_sql_query(
        "SELECT * FROM reports",
        conn
    )

    disease_df = pd.read_sql_query(
        """
        SELECT *
        FROM disease_history
        """,
        conn
    )

    conn.close()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Users",
        len(users_df)
    )

    col2.metric(
        "Reports",
        len(reports_df)
    )

    col3.metric(
        "Predictions",
        len(disease_df)
    )

    if not disease_df.empty:

        st.subheader(
            "Disease Distribution"
        )

        disease_count = (
            disease_df[
                "predicted_disease"
            ]
            .value_counts()
            .reset_index()
        )

        disease_count.columns = [
            "Disease",
            "Count"
        ]

        fig = px.pie(
            disease_count,
            names="Disease",
            values="Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = px.bar(
            disease_count,
            x="Disease",
            y="Count"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ============================================================
# CHATBOT
# ============================================================

CHATBOT_RESPONSES = {

    "fever":
    """
Possible Causes:
• Viral Fever
• Flu
• Infection

Advice:
• Drink water
• Rest well
• Consult doctor
""",

    "cough":
    """
Possible Causes:
• Common Cold
• Allergy
• Respiratory Infection

Advice:
• Drink warm fluids
• Avoid dust
""",

    "headache":
    """
Possible Causes:
• Migraine
• Stress
• Dehydration

Advice:
• Sleep properly
• Stay hydrated
"""
}

# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(
    username,
    user_message,
    bot_response
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chatbot_history(
            username,
            user_message,
            bot_response
        )
        VALUES(
            ?,?,?
        )
        """,
        (
            username,
            user_message,
            bot_response
        )
    )

    conn.commit()
    conn.close()

# ============================================================
# CHAT RESPONSE
# ============================================================

def chatbot_response(message):

    msg = message.lower()

    for keyword in CHATBOT_RESPONSES:

        if keyword in msg:

            return CHATBOT_RESPONSES[
                keyword
            ]

    return """
I am a Smart Medical Chatbot.

Try asking:
• Fever
• Headache
• Cough

For emergencies contact a doctor.
"""

# ============================================================
# CHATBOT PAGE
# ============================================================

def chatbot_page():

    st.title(
        "🤖 Medical Chatbot"
    )

    message = st.text_input(
        "Ask Your Question"
    )

    if st.button("Send"):

        if message:

            response = (
                chatbot_response(
                    message
                )
            )

            save_chat(
                st.session_state.username,
                message,
                response
            )

            st.success(
                "Response"
            )

            st.write(
                response
            )

    conn = get_connection()

    chats = pd.read_sql_query(
        """
        SELECT *
        FROM chatbot_history
        WHERE username = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        conn,
        params=(
            st.session_state.username,
        )
    )

    conn.close()

    if not chats.empty:

        st.subheader(
            "Recent Chats"
        )

        st.dataframe(
            chats,
            use_container_width=True
        )

# ============================================================
# ADMIN PAGE
# ============================================================

def admin_page():

    if (
        st.session_state.role
        != "admin"
    ):

        st.error(
            "Admin Access Only"
        )

        return

    st.title(
        "🛠 Admin Dashboard"
    )

    conn = get_connection()

    users = pd.read_sql_query(
        "SELECT * FROM users",
        conn
    )

    hospitals = pd.read_sql_query(
        "SELECT * FROM hospitals",
        conn
    )

    reports = pd.read_sql_query(
        "SELECT * FROM reports",
        conn
    )

    predictions = pd.read_sql_query(
        """
        SELECT *
        FROM disease_history
        """,
        conn
    )

    conn.close()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Users",
            "Hospitals",
            "Reports",
            "Predictions"
        ]
    )

    with tab1:
        st.dataframe(
            users,
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            hospitals,
            use_container_width=True
        )

    with tab3:
        st.dataframe(
            reports,
            use_container_width=True
        )

    with tab4:
        st.dataframe(
            predictions,
            use_container_width=True
        )

# ============================================================
# HOME PAGE
# ============================================================

def home_page():

    st.title(
        "🏥 Smart Medical Assistance System"
    )

    st.markdown(
        """
### Features

✔ Disease Prediction

✔ Nearby Hospital Finder

✔ GPS Tracking

✔ Medical Reports

✔ Healthcare Analytics

✔ AI Medical Chatbot

✔ Admin Dashboard
"""
    )

# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "user"

    st.rerun()

# ============================================================
# MAIN APPLICATION
# ============================================================

if not st.session_state.logged_in:

    option = st.sidebar.selectbox(
        "Choose",
        [
            "Login",
            "Register"
        ]
    )

    if option == "Login":

        login_page()

    else:

        register_page()

else:

    st.sidebar.title(
        f"Welcome {st.session_state.username}"
    )

    menu = [
        "Home",
        "Disease Prediction",
        "Hospital Finder",
        "Reports",
        "Analytics",
        "Chatbot"
    ]

    if (
        st.session_state.role
        == "admin"
    ):

        menu.append(
            "Admin"
        )

    page = st.sidebar.radio(
        "Navigation",
        menu
    )

    if page == "Home":
        home_page()

    elif page == "Disease Prediction":
        disease_prediction_page()

    elif page == "Hospital Finder":
        hospital_locator_page()

    elif page == "Reports":
        report_page()

    elif page == "Analytics":
        analytics_page()

    elif page == "Chatbot":
        chatbot_page()

    elif page == "Admin":
        admin_page()

    st.sidebar.button(
        "Logout",
        on_click=logout
    )

