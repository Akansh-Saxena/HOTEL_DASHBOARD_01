import streamlit as st
import httpx
import time
import pandas as pd
import plotly.express as px
import os

# =====================================================================
# SYSTEM: AETHER SUPER-APP v6.0 (ULTIMATE EDITION)
# AUTHOR: AKANSH SAXENA | J.K. INSTITUTE
# FEATURES: GPS, OTP, HOTEL+FOOD+TRAVEL AGGREGATOR, AADHAR KYC, RAZORPAY
# =====================================================================

st.set_page_config(page_title="Aether Super-App | Akansh Saxena", layout="wide", initial_sidebar_state="expanded")

# CUSTOM CSS FOR REALISTIC "SUPER-APP" LOOK
st.markdown("""
    <style>
    .stApp { background: #0B1120; color: #f4f7fb; }
    .main-nav { background: #111827; padding: 20px; border-bottom: 2px solid #1f2937; display: flex; gap: 30px; justify-content: center; font-size: 18px; color: #3B82F6; font-weight: bold; border-radius: 0 0 20px 20px;}
    .service-card { background: rgba(17, 24, 39, 0.8); padding: 20px; border-radius: 15px; border: 1px solid #374151; transition: 0.3s; color: white;}
    .service-card:hover { border-color: #3b82f6; box-shadow: 0 10px 20px rgba(59,130,246,0.2); }
    .price-tag { color: #10B981; font-weight: 900; font-size: 28px; }
    .vendor-compare { background: rgba(31, 41, 55, 0.5); padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 10px; border-left: 4px solid #3B82F6; color: #9CA3AF;}
    .stTextInput>div>div>input { background-color: #1F2937; color: white; }
    .stSelectbox>div>div>div { background-color: #1F2937; color: white; }
    </style>
""", unsafe_allow_html=True)

# Define API Gateway URL (Update to Render URL for production)
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- SESSION STATES ---
if "auth_status" not in st.session_state: st.session_state.auth_status = False
if "token" not in st.session_state: st.session_state.token = None
if "location" not in st.session_state: st.session_state.location = "NYC"
if "scan_data" not in st.session_state: st.session_state.scan_data = None
if "analytics_data" not in st.session_state: st.session_state.analytics_data = None

def fetch_data(city):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = httpx.get(f"{API_URL}/api/v1/akansh/scan/all", params={"city": city}, headers=headers)
        if res.status_code == 200:
            st.session_state.scan_data = res.json()["results"]
            
        an_res = httpx.get(f"{API_URL}/api/v1/akansh/analytics/dashboard", headers=headers)
        if an_res.status_code == 200:
            st.session_state.analytics_data = an_res.json()
    except Exception as e:
        st.error(f"Backend Server Offline -> {e}")

# --- STEP 1: INTERNATIONAL OTP LOGIN ---
if not st.session_state.auth_status:
    st.markdown("<h1 style='text-align: center; color: #3B82F6;'>🛰️ Aether Global Gateway</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>Ultra-Premium Hospitality & Quick Commerce Aggregator</p>", unsafe_allow_html=True)
    
    with st.container():
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Authentication")
            email = st.text_input("Email Address", value="admin@aether.com")
            
            if st.button("SEND NEURAL OTP", use_container_width=True):
                try:
                    res = httpx.post(f"{API_URL}/api/v1/akansh/auth/send-otp", json={"email": email})
                    if res.status_code == 200:
                        st.success(res.json()["msg"])
                    else:
                        st.error("Failed to Dispatch OTP.")
                except Exception as e:
                    st.error("API Gateway unreachable. Is backend running?")
            
            otp = st.text_input("Enter 6-Digit OTP", type="password", help="Default is 123456")
            if st.button("VERIFY & PROCEED", type="primary", use_container_width=True):
                try:
                    res = httpx.post(f"{API_URL}/api/v1/akansh/auth/verify", json={"email": email, "otp": otp})
                    if res.status_code == 200:
                        st.session_state.token = res.json()["access_token"]
                        st.session_state.auth_status = True
                        st.rerun()
                    else:
                        st.error("Invalid Credentials. Access Denied.")
                except Exception as e:
                    st.error("Verification failed network issue.")

# --- STEP 2: GPS & DASHBOARD ---
else:
    # Top Navigation
    st.markdown("""
        <div class="main-nav">
            🏨 Stays & Hotels &nbsp;&nbsp;|&nbsp;&nbsp; 🍔 Quick Commerce & Food &nbsp;&nbsp;|&nbsp;&nbsp; 💳 Aadhar Checkout
        </div>
    """, unsafe_allow_html=True)

    # GPS DETECTION & LOGOUT
    with st.sidebar:
        st.header("📍 Control Node")
        st.markdown(f"**Developer:** Akansh Saxena")
        st.write(f"**Token:** `SECURE_JWT_ACTIVE`")
        
        city = st.text_input("Override GPS City", value=st.session_state.location)
        if st.button("Initiate Deep Scan"):
            st.session_state.location = city
            with st.spinner(f"Aggregating {city} via LiveDataEngine..."):
                fetch_data(city)
                st.success(f"Scan Complete for {city}!")
        
        st.divider()
        if st.button("Logout Session"):
            st.session_state.auth_status = False
            st.session_state.token = None
            st.rerun()

    st.title(f"Aether Aggregator Output: {st.session_state.location}")
    
    # Check if data exists
    if not st.session_state.scan_data:
        st.info("Initiate a Deep Scan from the sidebar to fetch memory-optimized LRU Live Data.")
    else:
        # --- SERVICE AGGREGATOR ---
        tab1, tab2, tab3 = st.tabs(["🏨 Stay Aggregation", "🍔 Quick Commerce", "📈 Real-Time Analytics"])

        # STAYS
        with tab1:
            st.subheader("LRU Cache Multi-Platform Aggregation")
            hotels = st.session_state.scan_data.get("hotels", [])
            if not hotels:
                st.warning("No hotel inventory retrieved from Amadeus/MMT API.")
            else:
                cols = st.columns(2)
                for idx, h in enumerate(hotels[:6]): # Show top 6 for UI layout
                    col = cols[idx % 2]
                    with col:
                        st.markdown(f"""
                        <div class="service-card">
                            <h3 style='margin-bottom:0px; color: #60A5FA;'>{h['hotel_name']}</h3>
                            <p style='color: #9CA3AF; font-size: 14px; margin-top:2px;'>Platform: <b>{h['platform']}</b> | Rating: {h['rating']}⭐</p>
                            <p class="price-tag">${h['price_usd']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Secure Checkout Form for this item
                        with st.popover(f"Book {h['hotel_name']} Securely"):
                            st.write("**Aadhar Authenticated Checkout**")
                            aadhar_in = st.text_input("12-Digit Aadhar", key=f"aadhar_{idx}")
                            if st.button("Verify KYC & Pay via Razorpay", key=f"pay_{idx}"):
                                if len(aadhar_in) != 12:
                                    st.error("Aadhar must be exactly 12 digits")
                                else:
                                    with st.spinner("Authorizing Razorpay Gateway..."):
                                        try:
                                            res = httpx.post(
                                                f"{API_URL}/api/v1/akansh/pay/secure",
                                                headers={"Authorization": f"Bearer {st.session_state.token}"},
                                                json={"hotel_name": h['hotel_name'], "amount_inr": int(h['price_usd']*83), "aadhar_no": aadhar_in}
                                            )
                                            if res.status_code == 200:
                                                data = res.json()
                                                st.success(f"KYC Verified! ✅ Razorpay Order Created: {data['order_id']}")
                                                st.balloons()
                                                st.info(f"Amount: ₹{data['amount_paise']/100}. Gateway Initialized!")
                                            else:
                                                st.error(res.json()["detail"])
                                        except Exception as e:
                                            st.error("Gateway execution failed.")

        # QUICK COMMERCE
        with tab2:
            st.subheader("Food & Grocery Real-time Variance")
            foods = st.session_state.scan_data.get("food_compare", [])
            if not foods:
                st.warning("No food inventory.")
            else:
                cols = st.columns(2)
                for idx, f in enumerate(foods):
                    col = cols[idx % 2]
                    with col:
                        v_str = ""
                        prices = []
                        if 'zomato' in f: 
                            v_str += f"Zomato: ₹{f['zomato']} | "
                            prices.append(f['zomato'])
                        if 'swiggy' in f: 
                            v_str += f"Swiggy: ₹{f['swiggy']} | "
                            prices.append(f['swiggy'])
                        if 'zepto' in f: 
                            v_str += f"Zepto: ₹{f['zepto']} | "
                            prices.append(f['zepto'])
                        if 'blinkit' in f: 
                            v_str += f"Blinkit: ₹{f['blinkit']} | "
                            prices.append(f['blinkit'])
                            
                        best = min(prices)
                        st.markdown(f"""
                        <div class="service-card">
                            <h3 style='color: #10B981; margin-bottom: 0px;'>{f['item']}</h3>
                            <p class="price-tag" style='margin-top: 10px; font-size: 24px;'>Best Rate: ₹{best}</p>
                            <div class="vendor-compare">
                                {v_str} <br><b>Recommended: {f.get('best_vendor', 'Auto')}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Add to Cart", key=f"cart_{idx}"):
                            st.success(f"Added {f['item']} via {f.get('best_vendor')}!")

        # ANALYTICS
        if st.session_state.analytics_data:
            with tab3:
                st.subheader("Platform Metrics Dashboard")
                rev_data = st.session_state.analytics_data.get("revenue", [])
                occ_data = st.session_state.analytics_data.get("occupancy", [])
                
                c1, c2 = st.columns(2)
                with c1:
                    if rev_data:
                        df_rev = pd.DataFrame(rev_data)
                        fig = px.bar(df_rev, x='name', y='revenue', title="Revenue Output ($)", color_discrete_sequence=['#3b82f6'])
                        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig, use_container_width=True)
                with c2:
                    if occ_data:
                        df_occ = pd.DataFrame(occ_data)
                        fig2 = px.bar(df_occ, x='rate', y='name', title="Occupancy Fulfillment (%)", orientation='h', color_discrete_sequence=['#10b981'])
                        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig2, use_container_width=True)
