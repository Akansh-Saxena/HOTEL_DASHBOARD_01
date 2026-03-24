import streamlit as st
import httpx

st.set_page_config(page_title="Aether Global India", layout="wide")

# CSS for a truly professional 'Aether' look
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .hotel-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #00ffcc;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ Aether Neural Scan: Pan-India Data")

if st.button("Initialize Deep Scan (All India)"):
    with st.spinner("Scanning Indian Sectors..."):
        try:
            # Ab hum naye endpoint ko call kar rahe hain
            res = httpx.get(f"{st.secrets['BACKEND_URL']}/api/v1/search-india", timeout=30.0)
            if res.status_code == 200:
                hotels = res.json().get("results", [])
                
                if not hotels:
                    st.warning("No data returned. Check API quota on RapidAPI.")
                else:
                    st.success(f"Found {len(hotels)} properties across India!")
                    cols = st.columns(3)
                    for i, hotel in enumerate(hotels):
                        with cols[i % 3]:
                            st.markdown(f"""
                                <div class="hotel-box">
                                    <img src="{hotel.get('main_photo_url')}" style="width:100%; border-radius:10px;">
                                    <h4>{hotel.get('hotel_name')}</h4>
                                    <p>📍 {hotel.get('city')}, {hotel.get('address')}</p>
                                    <h3 style="color:#00ffcc;">₹{hotel.get('price_breakdown', {}).get('gross_amount')}</h3>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Uplink failed. Is the API Key correct?")
        except Exception as e:
            st.error(f"Error: {e}")
