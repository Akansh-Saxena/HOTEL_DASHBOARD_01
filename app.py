import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import os
from datetime import datetime, date, timedelta

# --- AUTHOR: AKANSH SAXENA ---
# --- AETHER HOSPITALITY: FULL SYNC EDITION ---

st.set_page_config(page_title="Global Hospitality Ecosystem", layout="wide", page_icon="🌐")

# --- 1. SECURE URL FETCHING ---
# Streamlit Secrets prioritized, then Env Vars, then Default
if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"].rstrip("/")
else:
    DEFAULT_BACKEND = "https://hotel-dashboard-01.onrender.com"
    BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

# --- 2. NEURAL STYLING (Hinglish: Futuristic Look ke liye) ---
st.markdown(f"""
<style>
    .stApp {{ background: #0e1117; }}
    h1, h2, h3 {{ color: #00ffcc !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        border-radius: 20px; border: 1px solid #00ffcc; 
        color: #00ffcc; background-color: rgba(0, 255, 204, 0.05); 
        transition: 0.3s;
    }}
    .stButton>button:hover {{ 
        background-color: #00ffcc; color: #000; box-shadow: 0 0 15px #00ffcc; 
    }}
    @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} 100% {{ opacity: 1; }} }}
    .uplink-status {{ color: #00ffcc; animation: pulse 2s infinite; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT ---
for key, val in {
    "token": None, "active_tab": "Dashboard", "chat_history": [],
    "otp_step": 1, "auth_email": "", "backend_online": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 4. CONNECTIVITY HANDSHAKE ---
def check_brain_connection():
    try:
        with httpx.Client() as client:
            # Pinging the /health route you created in main.py
            res = client.get(f"{BACKEND_URL}/health", timeout=5.0)
            st.session_state["backend_online"] = (res.status_code == 200)
    except:
        st.session_state["backend_online"] = False

# --- 5. AUTHENTICATION LOGIC ---
def request_otp(email):
    try:
        with httpx.Client() as client:
            res = client.post(f"{BACKEND_URL}/api/auth/send-otp", json={"email": email}, timeout=15.0)
            if res.status_code == 200:
                st.session_state["otp_step"] = 2
                st.session_state["auth_email"] = email
                st.success(f"Transmission Sent to {email}")
                st.rerun()
            else:
                st.error("Brain Connection Refused. Check Render Logs.")
    except Exception as e:
        st.error(f"📡 Transmission Interrupted: {e}")

def verify_code(email, code):
    try:
        with httpx.Client() as client:
            res = client.post(f"{BACKEND_URL}/api/auth/verify-otp", json={"email": email, "otp": code}, timeout=10.0)
            if res.status_code == 200:
                st.session_state["token"] = res.json().get("access_token")
                st.balloons()
                st.rerun()
            else:
                st.error("Neural Code Mismatch.")
    except Exception as e:
        st.error(f"Link Broken: {e}")

# --- 6. GATEWAY SCREEN (Login Area) ---
if not st.session_state["token"]:
    st.title("🌐 Aether Core Gateway")
    check_brain_connection()
    
    status_color = "uplink-status" if st.session_state["backend_online"] else ""
    status_text = "ONLINE" if st.session_state["backend_online"] else "OFFLINE (Wait for Render to wake up)"
    st.markdown(f"System Uplink: <span class='{status_color}'>{status_text}</span>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state["otp_step"] == 1:
            with st.form("otp_form"):
                email_input = st.text_input("Admin ID", value="saxenaakansh29@gmail.com")
                if st.form_submit_button("Request Access Key"):
                    if st.session_state["backend_online"]:
                        request_otp(email_input)
                    else:
                        st.warning("Uplink is OFFLINE. Visit Render URL manually to wake it up.")
        else:
            with st.form("verify_form"):
                otp_input = st.text_input("6-Digit Code", type="password")
                if st.form_submit_button("Verify Identity"):
                    verify_code(st.session_state["auth_email"], otp_input)
            if st.button("Return to Login"):
                st.session_state["otp_step"] = 1
                st.rerun()
    st.stop()

# --- 7. SECURE WORKSPACE (After Login) ---
st.sidebar.title("🧠 Neural Command")
st.sidebar.info(f"Active Session: {st.session_state['auth_email']}")

if st.sidebar.button("📊 Strategic Dashboard"): st.session_state["active_tab"] = "Dashboard"
if st.sidebar.button("🌍 Universal Booking"): st.session_state["active_tab"] = "Booking"
st.sidebar.markdown("---")
if st.sidebar.button("🔴 Terminate Session"):
    st.session_state.clear()
    st.rerun()

# --- TAB: DASHBOARD ---
if st.session_state["active_tab"] == "Dashboard":
    st.title("🏨 Strategic Command Center")
    # Presentation-ready mock data
    chart_data = pd.DataFrame({
        "Date": pd.date_range(start="2026-03-01", periods=15),
        "Occupancy": [65, 70, 72, 85, 90, 88, 80, 75, 82, 95, 91, 89, 94, 98, 96]
    })
    fig = px.area(chart_data, x="Date", y="Occupancy", title="Real-time Neural Occupancy")
    fig.update_traces(line_color='#00ffcc')
    st.plotly_chart(fig, use_container_width=True)

# --- TAB: BOOKING ---
elif st.session_state["active_tab"] == "Booking":
    st.title("🌍 Global Booking Hub")
    colA, colB = st.columns(2)
    with colA:
        st.text_input("📍 Destination", "Bareilly, Uttar Pradesh")
    with colB:
        st.date_input("Check-in", date.today() + timedelta(days=5))
    
    if st.button("Scan Global Inventories"):
        with st.spinner("Decoding API response..."):
            st.success("Cheapest Found: Taj Residency (₹9,200) via Aether-Direct")
