import streamlit as st
import pandas as pd
import plotly.express as px
import httpx
import os
import datetime

# --- AUTHOR: AKANSH SAXENA ---
# --- AETHER HOSPITALITY: CLOUD INTEGRATION EDITION ---

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Global Hospitality Ecosystem", layout="wide", page_icon="🌐")

# CRITICAL: This pulls from your Vercel Environment Variables
# If not set, it defaults to your Render URL (Replace with your actual Render link)
DEFAULT_BACKEND = "https://hotel-dashboard-01.onrender.com"
BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

# --- Custom CSS for Neural/Futuristic Vibe ---
st.markdown(f"""
<style>
    .stApp {{ background: #0e1117; }}
    h1, h2, h3 {{ color: #00ffcc !important; font-family: 'Courier New', monospace; }}
    .stButton>button {{ 
        border-radius: 20px; 
        border: 1px solid #00ffcc; 
        color: #00ffcc; 
        background-color: rgba(0, 255, 204, 0.05); 
        transition: 0.3s;
    }}
    .stButton>button:hover {{ 
        background-color: #00ffcc; 
        color: #000; 
        box-shadow: 0 0 15px #00ffcc; 
    }}
    /* Neural Pulse Animation */
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
        100% {{ opacity: 1; }}
    }}
    .uplink-status {{ color: #00ffcc; animation: pulse 2s infinite; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
for key, val in {
    "token": None, "active_tab": "Dashboard", "chat_history": [],
    "otp_step": 1, "auth_email": "", "backend_online": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 3. BACKEND CONNECTIVITY CHECK ---
def check_brain_connection():
    try:
        # Simple health check to Render
        with httpx.Client() as client:
            res = client.get(f"{BACKEND_URL}/health", timeout=5.0)
            st.session_state["backend_online"] = (res.status_code == 200)
    except:
        st.session_state["backend_online"] = False

# --- 4. AUTHENTICATION LOGIC ---
def request_otp(email):
    try:
        with httpx.Client() as client:
            res = client.post(f"{BACKEND_URL}/api/auth/send-otp", json={"email": email}, timeout=15.0)
            if res.status_code == 200:
                st.session_state["otp_step"] = 2
                st.session_state["auth_email"] = email
                st.rerun()
            else:
                st.error(f"Brain Refused Connection: {res.json().get('detail', 'Access Denied')}")
    except Exception as e:
        st.error(f"📡 Transmission Interrupted. Ensure Render Backend is Active. Error: {e}")

def verify_code(email, code):
    try:
        with httpx.Client() as client:
            res = client.post(f"{BACKEND_URL}/api/auth/verify-otp", json={"email": email, "otp": code}, timeout=15.0)
            if res.status_code == 200:
                st.session_state["token"] = res.json().get("access_token")
                st.success("Identity Verified. Entering Aether...")
                st.rerun()
            else:
                st.error("Neural Code Mismatch. Please retry.")
    except Exception as e:
        st.error(f"Verification Link Broken: {e}")

# --- GATEWAY SCREEN ---
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
                submit = st.form_submit_button("Request Access Key")
                if submit:
                    request_otp(email_input)
        else:
            with st.form("verify_form"):
                otp_input = st.text_input("6-Digit Neural Code", type="password")
                if st.form_submit_button("Verify Identity"):
                    verify_code(st.session_state["auth_email"], otp_input)
            if st.button("Return to Gateway"):
                st.session_state["otp_step"] = 1
                st.rerun()
    st.stop()

# --- 5. NEURAL COMMAND (SIDEBAR) ---
st.sidebar.markdown(f"### 🧠 Neural Command")
st.sidebar.markdown(f"User: `{st.session_state['auth_email']}`")

tabs = {
    "📊 System Dashboard": "Dashboard",
    "🌍 Booking Hub": "Booking",
    "🗣️ AI Concierge": "Assistant"
}

for label, tab_id in tabs.items():
    if st.sidebar.button(label):
        st.session_state["active_tab"] = tab_id
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔴 Terminate Session"):
    st.session_state.clear()
    st.rerun()

# --- 6. WORKSPACE ---

# --- TAB: DASHBOARD ---
if st.session_state["active_tab"] == "Dashboard":
    st.title("🏨 Strategic Command Center")
    
    # Mock Data for Final Year Presentation
    dates = pd.date_range(start=datetime.date.today(), periods=12)
    mock_df = pd.DataFrame({
        "Timeline": dates,
        "Occupancy %": [65, 72, 80, 85, 90, 88, 75, 70, 82, 95, 92, 89],
        "Platform": ["Direct"]*3 + ["Booking.com"]*3 + ["Agoda"]*3 + ["Expedia"]*3
    })
    
    fig = px.line(mock_df, x="Timeline", y="Occupancy %", color="Platform", markers=True, 
                 title="Live Neural Occupancy Forecast")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                     font_color="#00ffcc", xaxis_gridcolor="#1a1c23", yaxis_gridcolor="#1a1c23")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB: BOOKING ---
elif st.session_state["active_tab"] == "Booking":
    st.title("🌍 Universal Booking Engine")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Inventory Search")
        dest = st.text_input("📍 Destination", "Prayagraj, India")
        d1, d2 = st.columns(2)
        checkin = d1.date_input("In", datetime.date.today())
        checkout = d2.date_input("Out", datetime.date.today() + datetime.timedelta(days=1))
        
        if st.button("Scan Global Inventories"):
            with st.spinner("Bypassing Meta-Aggregators..."):
                st.success("Cheapest Found: Agoda (₹8,450) - Taj Residency")
                st.session_state["selected_price"] = 8450

    with c2:
        st.subheader("Secure Checkout")
        if "selected_price" in st.session_state:
            st.metric("Total (Neural-Rate)", f"₹{st.session_state['selected_price']}")
            if st.button("Initiate Razorpay"):
                st.toast("Redirecting to Secure Gateway...")
                st.balloons()
        else:
            st.info("Awaiting scan results...")

# --- TAB: ASSISTANT ---
elif st.session_state["active_tab"] == "Assistant":
    st.title("🗣️ AI Support Concierge")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("How can I assist your stay?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # In production, you would replace this with an API call to your backend LLM
        response = "Neural Logic Processing: Your query about '" + prompt + "' is being handled by our support core."
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)
