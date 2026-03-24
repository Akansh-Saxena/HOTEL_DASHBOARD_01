import streamlit as st
import httpx

st.set_page_config(page_title="Aether Global Hub", layout="wide")

# Neural Styling
st.markdown("""
    <style>
    .hotel-card {
        background-color: #111; border: 1px solid #00ffcc; border-radius: 12px;
        padding: 15px; margin-bottom: 20px; text-align: center;
    }
    .price { color: #00ffcc; font-size: 22px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ Aether Neural Scan: Pan-India Inventory")

if st.button("Initialize Deep Scan"):
    with st.spinner("Accessing Global Nodes..."):
        try:
            res = httpx.get(f"{st.secrets['BACKEND_URL']}/api/v1/search-india", timeout=20.0)
            data = res.json()
            hotels = data.get("results", [])
            
            st.info(f"Data Source: {data.get('source')}")
            
            cols = st.columns(3)
            for i, h in enumerate(hotels):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="hotel-card">
                            <img src="{h['photo']}" style="width:100%; height:180px; object-fit:cover; border-radius:8px;">
                            <h4 style="margin:10px 0;">{h['hotel_name']}</h4>
                            <p>📍 {h['city']}</p>
                            <p class="price">₹{h['gross_amount']}</p>
                        </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Uplink Failed: {e}")
