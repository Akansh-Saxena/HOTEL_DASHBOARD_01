import streamlit as st
import httpx
import time

# =====================================================================
# SYSTEM: AETHER SUPER-APP v6.0 (ULTIMATE EDITION)
# AUTHOR: AKANSH SAXENA | J.K. INSTITUTE
# FEATURES: GPS, OTP, HOTEL+FOOD+TRAVEL AGGREGATOR
# =====================================================================

st.set_page_config(page_title="Aether Super-App | Akansh Saxena", layout="wide")

# CUSTOM CSS FOR REALISTIC "SUPER-APP" LOOK
st.markdown("""
    <style>
    .stApp { background: #f4f7fb; color: #1a1a1a; }
    .main-nav { background: #ffffff; padding: 15px; border-bottom: 2px solid #eee; display: flex; gap: 30px; justify-content: center; }
    .service-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; text-align: center; transition: 0.3s; }
    .service-card:hover { border-color: #008cff; transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .price-tag { color: #d32f2f; font-weight: bold; font-size: 20px; }
    .vendor-compare { background: #f9f9f9; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 5px; border-left: 4px solid #ffb200; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATES ---
if "auth_status" not in st.session_state: st.session_state.auth_status = False
if "location" not in st.session_state: st.session_state.location = "Detecting..."

# --- STEP 1: INTERNATIONAL OTP LOGIN ---
if not st.session_state.auth_status:
    st.title("🛰️ Aether Global Login")
    with st.container():
        st.markdown("<div style='max-width:400px; margin:auto;'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1: country_code = st.selectbox("Code", ["+91", "+1", "+44", "+971"])
        with col2: mobile = st.text_input("Mobile Number")
        
        if st.button("SEND OTP"):
            st.info(f"Verification Code sent to {country_code} {mobile}")
        
        otp = st.text_input("Enter 6-Digit OTP", type="password")
        if st.button("VERIFY & PROCEED"):
            if len(otp) == 6:
                st.session_state.auth_status = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- STEP 2: GPS & DASHBOARD ---
else:
    # Top Navigation
    st.markdown("""
        <div class="main-nav">
            <b>🏨 Hotels</b> | ✈️ Flights | 🚆 Trains | 🍔 Food | 🛒 Grocery | 🚕 Cabs
        </div>
    """, unsafe_allow_html=True)

    # GPS DETECTION (Realistic Simulation)
    with st.sidebar:
        st.header("📍 User Node")
        st.write(f"**Developer:** Akansh Saxena")
        if st.button("Detect My GPS Location"):
            with st.spinner("Accessing Satellite Data..."):
                time.sleep(2)
                st.session_state.location = "Prayagraj, Uttar Pradesh" # Auto-detected
        st.success(f"Current City: {st.session_state.location}")

    st.title(f"What are you looking for in {st.session_state.location}?")

    # --- SERVICE AGGREGATOR ---
    tab1, tab2, tab3 = st.tabs(["🏨 Stay & Travel", "🍔 Food & Quick Commerce", "📦 Full Package"])

    with tab1:
        st.subheader("Hotel Availability & Price Comparison")
        c1, c2, c3 = st.columns(3)
        
        # MOCK DATA FOR 90% ACCURACY DEMO
        hotel_data = [
            {"name": "Radisson Blu", "price": 8500, "mmt": 8900, "booking": 8500, "agoda": 8700},
            {"name": "Hotel Kanha Shyam", "price": 4200, "mmt": 4500, "booking": 4200, "agoda": 4400}
        ]

        for h in hotel_data:
            with st.container():
                st.markdown(f"""
                <div class="service-card">
                    <h3>{h['name']}</h3>
                    <p class="price-tag">Best Price: ₹{h['price']}</p>
                    <div class="vendor-compare">
                        MMT: ₹{h['mmt']} | Booking.com: ₹{h['booking']} | Agoda: ₹{h['agoda']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Book via Aadhar Auth: {h['name']}"):
                    st.warning("Please Enter Aadhar for Secure Transaction")

    with tab2:
        st.subheader("Food & Grocery Comparison (Real-time)")
        f1, f2 = st.columns(2)
        with f1:
            st.markdown("""
            <div class="service-card">
                <h4>🍔 Paneer Butter Masala</h4>
                <p><b>Zomato:</b> ₹320 (30 mins)<br><b>Swiggy:</b> ₹290 (45 mins)</p>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="service-card">
                <h4>🥛 Milk & Bread</h4>
                <p><b>Zepto:</b> ₹85 (10 mins)<br><b>Blinkit:</b> ₹82 (12 mins)</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("📦 Complete Hospitality Package")
        st.info("Includes: Flight + Cab + 5-Star Hotel + Food Credits")
        st.markdown("### Total Package: ₹45,000")
        if st.button("PROCEED TO PAYMENT (ALL-IN-ONE)"):
            st.balloons()
