import streamlit as st
import httpx
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# Render dashboard se URL copy karke yahan ya Streamlit Secrets mein daalein
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://hotel-dashboard-01.onrender.com")

st.set_page_config(page_title="Aether Core Gateway", layout="wide")

# --- CUSTOM CSS FOR NEURAL LOOK ---
st.markdown("""
    <style>
    .hotel-card {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #00ffcc;
        transition: 0.3s;
    }
    .hotel-card:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 15px #00ffcc;
    }
    .price-tag {
        color: #00ffcc;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
st.title("🌐 Global Booking Hub")
st.sidebar.title("🧠 Neural Command")

# Session State for Auth
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # --- LOGIN UI ---
    email = st.text_input("Enter Email", "saxenaakansh29@gmail.com")
    otp = st.text_input("6-Digit Code", type="password")
    
    if st.button("Verify Identity"):
        with st.spinner("Authenticating..."):
            try:
                # Backend check
                res = httpx.post(f"{BACKEND_URL}/api/auth/verify-otp", json={"email": email, "otp": otp})
                if res.status_code == 200:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Neural Token")
            except Exception as e:
                st.error(f"Uplink Error: {e}")
else:
    # --- DASHBOARD UI ---
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        destination = st.text_input("📍 Destination", "Bareilly")
    with col2:
        checkin = st.date_input("Check-in", datetime.now())
    with col3:
        st.write("##")
        search_btn = st.button("Scan Global Inventories")

    if search_btn:
        with st.spinner(f"Neural Scanning {destination}..."):
            try:
                # Backend API Call
                params = {"dest": destination, "checkin": str(checkin)}
                response = httpx.get(f"{BACKEND_URL}/api/v1/search", params=params, timeout=15.0)
                
                if response.status_code == 200:
                    results = response.json().get("results", {}).get("result", [])
                    
                    if not results:
                        st.warning("No properties found in this sector.")
                    
                    # --- DISPLAY CARDS ---
                    for hotel in results[:10]: # Top 10 hotels
                        name = hotel.get("hotel_name", "Unknown Property")
                        price = hotel.get("price_breakdown", {}).get("gross_amount", "N/A")
                        img_url = hotel.get("main_photo_url", "").replace("square60", "square600")
                        rating = hotel.get("review_score", "New")
                        
                        st.markdown(f"""
                            <div class="hotel-card">
                                <div style="display: flex; gap: 20px;">
                                    <img src="{img_url}" style="width: 250px; border-radius: 10px;">
                                    <div>
                                        <h3>🏢 {name}</h3>
                                        <p>⭐ Rating: {rating}/10</p>
                                        <p class="price-tag">₹{price}</p>
                                        <button style="background-color:#00ffcc; border:none; border-radius:5px; padding:10px 20px; color:black; font-weight:bold;">Initialize Booking</button>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("API Limit reached or Backend error.")
            except Exception as e:
                st.error(f"Uplink Offline: {e}")

    if st.sidebar.button("Terminate Session"):
        st.session_state.authenticated = False
        st.rerun()
