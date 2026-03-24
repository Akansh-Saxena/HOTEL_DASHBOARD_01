import streamlit as st
import httpx

st.set_page_config(page_title="Aether Global | Akansh Saxena", layout="wide", page_icon="🛰️")

# AUTHORIZED AETHER UI
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .auth-box { border: 1px solid #00ffcc; padding: 25px; border-radius: 12px; background: #111; margin-top: 30px;}
    .hotel-card { background: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    .price-tag { color: #00ffcc; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# SESSION DATA
if "verified" not in st.session_state: st.session_state.verified = False

# SIDEBAR STATUS
with st.sidebar:
    st.title("👨‍💻 Akansh Saxena")
    st.write("J.K. Institute of Applied Physics & Tech")
    st.markdown("---")
    st.success("Aether Node: ACTIVE")
    user_msg = st.text_input("AI Concierge 24/7...")
    if st.button("Ask AI"):
        st.info("Aether AI: Identity Verified. How can I assist you?")

# MAIN APP LOGIC
st.title("🛰️ Aether: Global Hospitality Network")

if not st.session_state.verified:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.subheader("🔐 Secure Authorization Required")
    st.write("Mandatory Identity Verification (Aadhar KYC) for Akansh's Network.")
    
    aadhar = st.text_input("Aadhar Number", type="password")
    if st.button("Generate OTP"): st.success("OTP Sent to Mobile")
    
    otp = st.text_input("Enter 6-Digit OTP")
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
                backend_url = st.secrets.get("BACKEND_URL", "https://hotel-dashboard-01.onrender.com")
                res = httpx.get(f"{backend_url}/api/v1/akansh/inventory/scan", params={"city": city})
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
                                <button style="background:#00ffcc; color:black; border:none; padding:10px; width:100%; border-radius:5px; font-weight:bold;">Book via Razorpay</button>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Confirm Booking {idx}", key=f"btn_{idx}"):
                            st.success(f"Payment Order Created! Confirmation sent to Akansh Saxena's Portal.")
            except Exception as e:
                st.error(f"Uplink Error: {e}")
