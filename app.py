import streamlit as st
import pandas as pd
import plotly.express as px
import cv2
import av
import queue
import time
import httpx
import os
import asyncio
import mediapipe as mp
from deepface import DeepFace
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- 1. CONFIGURATION MUST BE FIRST ---
st.set_page_config(page_title="Hospitality Dashboard", layout="wide", page_icon="📈")

# --- 2. INITIALIZE SESSION STATE IMMEDIATELY ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Revenue Metrics"
if "zoom_solstice" not in st.session_state:
    st.session_state["zoom_solstice"] = False
if "agg_level" not in st.session_state:
    st.session_state["agg_level"] = "Daily"

# --- 3. WEBRTC & MULTIMODAL PROCESSOR ---
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    HAS_MEDIAPIPE = True
except (ImportError, AttributeError):
    mp_hands = None
    HAS_MEDIAPIPE = False

class MultimodalProcessor(VideoProcessorBase):
    def __init__(self):
        if HAS_MEDIAPIPE:
            self.hands = mp_hands.Hands(
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7,
                max_num_hands=1
            )
        else:
            self.hands = None
            
        self.result_queue = queue.Queue(maxsize=1)
        self.frame_skip = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame_skip += 1
        
        # Process every 10th frame to save CPU
        if self.frame_skip % 10 == 0:
            gesture = None
            emotion = None
            
            # Gesture Recognition
            if HAS_MEDIAPIPE and self.hands:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        fingers_up = 0
                        tips = [8, 12, 16, 20]
                        pips = [6, 10, 14, 18]
                        
                        for tip, pip in zip(tips, pips):
                            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                                fingers_up += 1
                                
                        # Thumb
                        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                            fingers_up += 1
                            
                        if fingers_up >= 4:
                            gesture = "Open Hand"
                        elif fingers_up == 2:
                            gesture = "Peace"
                        elif fingers_up == 0:
                            gesture = "Fist"
            else:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Emotion Recognition
            try:
                res = DeepFace.analyze(img_rgb, actions=['emotion'], enforce_detection=False, silent=True)
                if isinstance(res, list):
                    emotion = res[0]['dominant_emotion']
                else:
                    emotion = res['dominant_emotion']
            except Exception:
                emotion = None

            # Push to queue
            if not self.result_queue.full() and (gesture or emotion):
                self.result_queue.put({"gesture": gesture, "emotion": emotion})

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- 4. UI SIDEBAR: START WEBRTC ---
st.sidebar.title("Multimodal Controls")
st.sidebar.markdown("Use your webcam for Gesture & Emotion control.")
if not HAS_MEDIAPIPE:
    st.sidebar.warning("⚠️ MediaPipe installation currently lacks Python 3.11+ Protobuf compatibility. Gestures disabled. Emotion detection active.")

webrtc_ctx = webrtc_streamer(
    key="multimodal",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=MultimodalProcessor,
    async_processing=True,
    media_stream_constraints={"video": True, "audio": False},
)

# Process the queue and update state
state_changed = False
if webrtc_ctx.state.playing and webrtc_ctx.video_processor:
    try:
        res = webrtc_ctx.video_processor.result_queue.get(timeout=0.1)
        
        # Handle Gestures
        if res.get("gesture") == "Open Hand" and st.session_state["active_tab"] != "Revenue Metrics":
            st.session_state["active_tab"] = "Revenue Metrics"
            state_changed = True
        elif res.get("gesture") == "Peace" and st.session_state["active_tab"] != "Global Reviews":
            st.session_state["active_tab"] = "Global Reviews"
            state_changed = True
        elif res.get("gesture") == "Fist":
             st.session_state["zoom_solstice"] = not st.session_state["zoom_solstice"]
             state_changed = True
             
        # Handle Emotions
        if res.get("emotion") in ["angry", "disgust", "fear", "sad"] and st.session_state["agg_level"] != "Monthly":
             st.session_state["agg_level"] = "Monthly"
             state_changed = True
        elif res.get("emotion") in ["happy", "neutral", "surprise"] and st.session_state["agg_level"] != "Daily":
             st.session_state["agg_level"] = "Daily"
             state_changed = True
             
    except queue.Empty:
        pass

st.sidebar.markdown(f"**Current Action Tab:** {st.session_state['active_tab']}")
st.sidebar.markdown(f"**Solstice Zoom:** {'Active' if st.session_state['zoom_solstice'] else 'Inactive'}")
st.sidebar.markdown(f"**Data Aggregation (Emotion):** {st.session_state['agg_level']}")

# --- 5. DATA LOADING AND CACHING ---
async def fetch_hotel_data(city_code="NYC"):
    """Fetches global pricing from FastAPI."""
    async with httpx.AsyncClient() as client:
        try:
            req = {"city_code": city_code, "check_in": "2026-06-01", "check_out": "2026-06-05"}
            res = await client.post(f"{BACKEND_URL}/api/hotels", json=req, timeout=10.0)
            res.raise_for_status()
            return res.json().get("hotels", [])
        except Exception as e:
            st.error(f"Backend Server Error (Hotels): {e}")
            return []

async def fetch_review_data(hotel_name="Grand Oasis NYC"):
    """Fetches True Sentiment Score from FastAPI."""
    async with httpx.AsyncClient() as client:
        try:
            req = {"hotel_name": hotel_name}
            res = await client.post(f"{BACKEND_URL}/api/reviews", json=req, timeout=10.0)
            res.raise_for_status()
            return res.json().get("nlp_analysis", {})
        except Exception as e:
            st.error(f"Backend Server Error (Reviews): {e}")
            return {}

@st.cache_data(ttl=300)
def load_data_sync_wrapper(city_code, hotel_name):
    """Sync wrapper for Streamlit cache to run the async fetches."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hotels = loop.run_until_complete(fetch_hotel_data(city_code))
    reviews = loop.run_until_complete(fetch_review_data(hotel_name))
    loop.close()
    return hotels, reviews

# For demo purposes, hardcoding initial search
live_hotels, live_reviews = load_data_sync_wrapper("NYC", "Grand Oasis NYC")

# --- 6. PREPROCESSING & UI LAYOUT ---
st.title("🏨 Aether Hospitality Global Ecosystem")
st.markdown("Live API Analytics with Kinematic & NLP Affective Control")

# Create a mock dataframe from the live API JSON to reuse existing visual logic
if live_hotels:
    mock_bookings = []
    for h in live_hotels:
        name = h.get("hotel", {}).get("name", "Unknown Hotel")
        price = float(h.get("offers", [{}])[0].get("price", {}).get("total", 0))
        # Mocking variation to show Disparity graph
        mock_bookings.append({"booking_platform": "Amadeus API", "check_in_date": "2026-06-01", "revenue_generated": price, "revenue_realized": price * 0.85})
        mock_bookings.append({"booking_platform": "Amadeus API", "check_in_date": "2026-06-02", "revenue_generated": price*1.2, "revenue_realized": price * 0.95})
        
    bookings_df = pd.DataFrame(mock_bookings)
    bookings_df['check_in_date'] = pd.to_datetime(bookings_df['check_in_date'])

    if st.session_state["agg_level"] == "Monthly":
        bookings_df['display_date'] = bookings_df['check_in_date'].dt.to_period('M').dt.to_timestamp()
    else:
        bookings_df['display_date'] = bookings_df['check_in_date']

    if st.session_state["zoom_solstice"]:
         start_date = pd.to_datetime("2026-06-01")
         end_date = pd.to_datetime("2026-06-03")
         bookings_filtered = bookings_df[(bookings_df['check_in_date'] >= start_date) & (bookings_df['check_in_date'] <= end_date)]
    else:
         bookings_filtered = bookings_df

    st.title("🏨 Strategic Hospitality Command Center")
    st.markdown("Dynamic Analytics with Kinematic & Affective Control")

    # Display logic based on initialized session state
    if st.session_state["active_tab"] == "Revenue Metrics":
        st.subheader(f"Live Price Disparity ({st.session_state['agg_level']} View)")
        platform_rev = bookings_filtered.groupby(['booking_platform', 'display_date'])[['revenue_generated', 'revenue_realized']].sum().reset_index()
        platform_rev_melted = platform_rev.melt(id_vars=['booking_platform', 'display_date'], 
                                              value_vars=['revenue_generated', 'revenue_realized'],
                                              var_name='Revenue Type', value_name='Amount')
        fig_rev = px.area(platform_rev_melted, x='display_date', y='Amount', color='Revenue Type', facet_col='booking_platform',
                         title="Revenue Disparity over Time (Live API)",
                         labels={'display_date': 'Date', 'Amount': 'Total Revenue (USD)'})
        st.plotly_chart(fig_rev, use_container_width=True)

    elif st.session_state["active_tab"] == "Global Reviews":
        st.subheader("NLP Sentiment Brain (Live Places Integration)")
        if live_reviews:
             col1, col2, col3 = st.columns(3)
             col1.metric("True Sentiment Score", f"{live_reviews.get('true_sentiment_score')}%")
             col2.metric("Total Reviews Analyzed", live_reviews.get('total_analyzed'))
             col3.metric("Frustration Index", f"{100 - live_reviews.get('true_sentiment_score', 100)}%")
             
             st.markdown("### Category Breakdown")
             # Converting NLP dict to dataframe for charting
             cat_data = []
             for cat, scores in live_reviews.get('category_breakdown', {}).items():
                 cat_data.append({"Category": cat, "Positive": scores['positive'], "Negative": scores['negative']})
                 
             if cat_data:
                cat_df = pd.DataFrame(cat_data).melt(id_vars=['Category'], value_vars=['Positive', 'Negative'], var_name='Sentiment', value_name='Count')
                fig_nlp = px.bar(cat_df, x='Category', y='Count', color='Sentiment', barmode='group', title="Sentiment Breakdown >90% Precision Filters")
                st.plotly_chart(fig_nlp, use_container_width=True)
             else:
                 st.info("No actionable categorization mapped yet.")
        else:
             st.warning("No review data returned from backend.")

# Keep app refreshing while camera runs
if webrtc_ctx.state.playing:
    if state_changed:
        st.rerun()
    else:
        time.sleep(1.0)
        st.rerun()