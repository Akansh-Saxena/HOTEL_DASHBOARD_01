import streamlit as st
import httpx

st.set_page_config(page_title="Aether Global Hub", layout="wide", page_icon="🛰️")

# Aether Neural UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #00ffcc;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        transition: 0.4s;
    }
    .card:hover { transform: translateY(-5px); box-shadow: 0 0 20px #00ffcc44; }
    .price-tag { color: #00ffcc; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ Aether Neural Scan: Pan-India Inventory")

# Sidebar Status
st.sidebar.title("System Status")
st.sidebar.success("Uplink: ACTIVE")

if st.button("Initialize Deep Scan"):
    with st.spinner("Establishing Connection to Global Nodes..."):
        try:
            # Backend URL check
            backend_url = st.secrets.get("BACKEND_URL", "https://hotel-dashboard-01.onrender.com")
            response = httpx.get(f"{backend_url}/api/v1/search-india", timeout=20.0)
            
            if response.status_code == 200:
                data = response.json()
                hotels = data.get("results", [])
                
                st.markdown(f"**Data Source:** `{data.get('source')}`")
                
                # Grid Display
                cols = st.columns(3)
                for idx, h in enumerate(hotels):
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <div class="card">
                                <img src="{h['photo']}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                                <h4 style="margin-top:10px;">{h['hotel_name']}</h4>
                                <p>📍 {h['city']}</p>
                                <p class="price-tag">₹{h['price']}</p>
                                <hr style="border-color:#333">
                                <p style="font-size:10px;">Secure Aether-Direct Booking</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Neural Link timed out. Using local protocols.")
        except Exception as e:
            st.error(f"Uplink Failed: {e}")
