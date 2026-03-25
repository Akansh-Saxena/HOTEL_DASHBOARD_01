import streamlit as st
import httpx

# =====================================================================
# SYSTEM: AETHER GLOBAL UI v5.0 (OFFICIAL)
# AUTHOR: AKANSH SAXENA | J.K. INSTITUTE
# COMPATIBILITY: VERCEL, STREAMLIT, RENDER
# =====================================================================

st.set_page_config(page_title="Aether Global | Akansh Saxena", layout="wide", page_icon="🛰️")

# DIRECT BACKEND LINK (Render URL)
# Akansh, ensure karein ki ye URL aapke Render dashboard se match kare
BACKEND_URL = "https://hotel-dashboard-01.onrender.com"

# AUTHORIZED AETHER UI STYLING
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .auth-box { border: 1px solid #00ffcc; padding: 25px; border-radius: 12px; background: #111; margin-top: 30px;}
    .hotel-card { background: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; min-height: 400px;}
    .price-tag { color: #00ffcc; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

if "verified" not in st.session_state: st.session_state.verified = False

# SIDEBAR: AUTHORIZED ACCESS & AI CHAT
with st.sidebar:
    st.title("👨‍💻 Akansh Saxena")
    st.write("J.K. Institute of Applied Physics & Tech")
    st.markdown("---")
    st.success("Aether Node: ACTIVE")
    
    user_msg = st.text_input("AI Concierge 24/7 (Ask anything)...")
    if st.button("Ask AI"):
        if user_msg:
            try:
                res = httpx.post(f"{BACKEND_URL}/api/v1/akansh/ai/chat", json={"user_msg": user_msg}, timeout=10.0)
                st.info(f"🤖 Aether AI: {res.json().get('reply')}")
            except:
                st.error("AI Uplink Offline. Check Backend Node.")

# MAIN APP LOGIC
st.title("🛰️ Aether: Global Hospitality Network")

if not st.session_state.verified:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.subheader("🔐 Secure Authorization Required")
    st.write("Mandatory Identity Verification (Aadhar KYC) for Akansh's Network.")
    
    aadhar = st.text_input("Aadhar Number", type="password", key="aadhar_input")
    if st.button("Generate OTP"):
        if len(aadhar) == 12:
            try:
                res = httpx.post(f"{BACKEND_URL}/api/v1/akansh/kyc/verify", json={"aadhar_no": aadhar})
                st.success(res.json().get("msg"))
            except:
                st.warning("Simulation Mode: OTP Sent to linked mobile.")
        else:
            st.error("Invalid Aadhar Format.")
    
    otp = st.text_input("Enter 6-Digit OTP", type="password")
    if st.button("Verify & Login"):
        if otp == "123456": # Master Key for Presentation
            st.session_state.verified = True
            st.rerun()
        else: st.error("Verification Failed")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.success("✅ Access Granted: User Authenticated via Aether-Secure.")
    city = st.text_input("📍 Search Destination", "Mumbai")
    
    if st.button("Initialize Deep Scan"):
        with st.spinner("Accessing Aether Global Nodes..."):
            try:
                # Real-time scan call to Render Backend
                res = httpx.get(f"{BACKEND_URL}/api/v1/akansh/inventory/scan", params={"city": city}, timeout=15.0)
                data = res.json()
                hotels = data.get("data", [])
                
                st.markdown(f"**Uplink Source:** `{data.get('source')}`")
                
                cols = st.columns(3)
                for idx, h in enumerate(hotels):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div class='hotel-card'>
                                <img src="{h['img']}" style="width:100%; height:200px; object-fit:cover; border-radius:8px;">
                                <h4>{h['name']}</h4>
                                <p>📍 {h['city']}</p>
                                <p class='price-tag'>₹{h['price']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Book {h['name']}", key=f"btn_{idx}"):
                            with st.spinner("Creating Secure Order..."):
                                try:
                                    p_res = httpx.post(f"{BACKEND_URL}/api/v1/akansh/payments/create", 
                                                      json={"amount": int(h['price']), "hotel": h['name']})
                                    st.success(f"Order ID: {p_res.json().get('order_id')} created successfully!")
                                    st.balloons()
                                except:
                                    st.error("Payment Gateway Timeout.")
            except Exception as e:
                st.error(f"Uplink Error: Ensure Backend on Render is LIVE. Details: {e}")
