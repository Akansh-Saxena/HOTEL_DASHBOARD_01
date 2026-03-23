import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Global Hospitality Ecosystem", layout="wide", page_icon="🌐")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Custom CSS for Futuristic Vibe ---
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .sidebar .sidebar-content { background: #1a1c23; }
    h1, h2, h3 { color: #00ffcc !important; }
    .stButton>button { border-radius: 20px; border: 1px solid #00ffcc; color: #00ffcc; background-color: transparent; }
    .stButton>button:hover { background-color: #00ffcc; color: #000; box-shadow: 0 0 10px #00ffcc; }
    .success-text { color: #00ffcc; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. INITIALIZE SESSION STATE ---
if "token" not in st.session_state:
    st.session_state["token"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Dashboard"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --- 3. AUTHENTICATION FLOW ---
def login_user(email, password):
    try:
        response = httpx.post(f"{BACKEND_URL}/token", data={"username": email, "password": password})
        if response.status_code == 200:
            st.session_state["token"] = response.json().get("access_token")
            st.rerun()
        else:
            st.error("Authentication Failed: Invalid Credentials.")
    except Exception as e:
        st.error(f"Cannot connect to Backend Brain: {e}. Is the FastAPI server running?")

if not st.session_state["token"]:
    st.title("🌐 Aether Core Gateway")
    st.markdown("### Secure Access Required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.text_input("Admin Email", key="email", value="saxenaakansh29@gmail.com")
            st.text_input("Master Password", type="password", key="password", value="admin123")
            submitted = st.form_submit_button("Initialize Uplink")
            if submitted:
                login_user(st.session_state.email, st.session_state.password)
    st.stop() # Halts execution until logged in

# --- 5. SIDEBAR & NAVIGATION ---
st.sidebar.title("🧠 Neural Command")
st.sidebar.success("🟢 Uplink Active. Authorized.")

if st.sidebar.button("📊 System Dashboard"): st.session_state["active_tab"] = "Dashboard"; st.rerun()
if st.sidebar.button("🌍 Global Booking Hub"): st.session_state["active_tab"] = "Booking"; st.rerun()
if st.sidebar.button("🗣️ Multilingual Assistant"): st.session_state["active_tab"] = "Assistant"; st.rerun()
st.sidebar.markdown("---")

# --- 6. MAIN WORKSPACE ---
if st.session_state["active_tab"] == "Dashboard":
    st.title("🏨 Strategic Hospitality Command Center")
    st.subheader(f"Global Rate Aggregation")
    
    mock_df = pd.DataFrame({
        "Date": pd.date_range(start="2026-06-01", periods=10),
        "Revenue": [12000, 15000, 11000, 18000, 16000, 22000, 21000, 19000, 25000, 24000],
        "Platform": ["MakeMyTrip", "Booking.com", "Agoda", "Direct", "MakeMyTrip", "Booking.com", "Agoda", "Direct", "MakeMyTrip", "Booking.com"]
    })
    fig = px.area(mock_df, x="Date", y="Revenue", color="Platform", title="Real-Time Disparity Engine (INR)")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#00ffcc")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state["active_tab"] == "Booking":
    st.title("🌍 Universal Booking Engine")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        city = st.text_input("📍 Destination", placeholder="e.g., Prayagraj, NYC, Tokyo")
        if st.button("Search Deep Web Inventory"):
            with st.spinner("Pinging Global APIs via FastAPI Brain..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    req = {"city_code": city if city else "ALL", "check_in": "2026-06-01", "check_out": "2026-06-05"}
                    res = httpx.post(f"{BACKEND_URL}/api/search-hotels", json=req, headers=headers)
                    results = res.json().get("results", [])
                    st.success("Data Retrieved.")
                    for r in results:
                        st.markdown(f"**{r['hotel_name']}** | {r['platform']} | ₹{r['price_inr']}")
                except Exception as e:
                    st.error(f"Backend Link Offline: {e}")

    with col2:
        st.markdown("### Secure Payment Gateway")
        st.selectbox("Select Node", ["Razorpay (UPI)", "Stripe (International)"])
        phone = st.text_input("WhatsApp Number", "+919027276598")
        if st.button("Authorize Payment & Book"):
            try:
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                notify_req = {"hotel_name": "Selected Hotel", "user_phone": phone}
                res = httpx.post(f"{BACKEND_URL}/api/notify", json=notify_req, headers=headers)
                st.balloons()
                st.markdown(f"<p class='success-text'>✅ {res.json().get('whatsapp_status')}</p>", unsafe_allow_html=True)
            except Exception as e:
                st.error("API Error")

elif st.session_state["active_tab"] == "Assistant":
    st.title("🗣️ Neural Voice Assistant")
    st.info("Awaiting Input...")
    user_input = st.chat_input("Ask Aether...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])