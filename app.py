import streamlit as st
import pandas as pd
import plotly.express as px
import cv2
import av
import queue
import time
import mediapipe as mp
from deepface import DeepFace
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode

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
mp_hands = mp.solutions.hands

class MultimodalProcessor(VideoProcessorBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
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
        elif res.get("gesture") == "Peace" and st.session_state["active_tab"] != "Spatial Saturation":
            st.session_state["active_tab"] = "Spatial Saturation"
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
@st.cache_data
def load_data():
    try:
        b_df = pd.read_csv("bookings.csv")
        o_df = pd.read_csv("occupancy.csv")
        r_df = pd.read_csv("rooms.csv")
        return b_df, o_df, r_df
    except FileNotFoundError as e:
        st.error(f"Error loading data files: {e}. Please ensure CSV files are in the same directory.")
        return None, None, None

bookings_df, occupancy_df, rooms_df = load_data()

# --- 6. PREPROCESSING & UI LAYOUT ---
if bookings_df is not None and occupancy_df is not None and rooms_df is not None:
    
    occupancy_df['room_category'] = occupancy_df['room_category'].astype(str).str.strip()
    rooms_df['room_id'] = rooms_df['room_id'].astype(str).str.strip()

    occupancy_merged = pd.merge(occupancy_df, rooms_df, left_on="room_category", right_on="room_id", how="left")
    
    occupancy_merged['capacity'] = occupancy_merged['capacity'].fillna(1).replace(0, 1)
    occupancy_merged['occupancy_pct'] = (occupancy_merged['successful_bookings'] / occupancy_merged['capacity']) * 100

    bookings_df['booking_date'] = pd.to_datetime(bookings_df['booking_date'], errors='coerce')
    bookings_df['check_in_date'] = pd.to_datetime(bookings_df['check_in_date'], errors='coerce')
    occupancy_merged['check_in_date'] = pd.to_datetime(occupancy_merged['check_in_date'], errors='coerce')

    if st.session_state["agg_level"] == "Monthly":
        bookings_df['display_date'] = bookings_df['check_in_date'].dt.to_period('M').dt.to_timestamp()
    else:
        bookings_df['display_date'] = bookings_df['check_in_date']

    if st.session_state["zoom_solstice"]:
         start_date = pd.to_datetime("2022-06-16")
         end_date = pd.to_datetime("2022-06-26")
         bookings_filtered = bookings_df[(bookings_df['check_in_date'] >= start_date) & (bookings_df['check_in_date'] <= end_date)]
    else:
         bookings_filtered = bookings_df

    st.title("🏨 Strategic Hospitality Command Center")
    st.markdown("Dynamic Analytics with Kinematic & Affective Control")

    # Display logic based on initialized session state
    if st.session_state["active_tab"] == "Revenue Metrics":
        st.subheader(f"Revenue Disparity ({st.session_state['agg_level']} View)")
        platform_rev = bookings_filtered.groupby(['booking_platform', 'display_date'])[['revenue_generated', 'revenue_realized']].sum().reset_index()
        platform_rev_melted = platform_rev.melt(id_vars=['booking_platform', 'display_date'], 
                                              value_vars=['revenue_generated', 'revenue_realized'],
                                              var_name='Revenue Type', value_name='Amount')
        fig_rev = px.area(platform_rev_melted, x='display_date', y='Amount', color='Revenue Type', facet_col='booking_platform',
                         title="Revenue Disparity over Time",
                         labels={'display_date': 'Date', 'Amount': 'Total Revenue (INR)'})
        st.plotly_chart(fig_rev, use_container_width=True)

    elif st.session_state["active_tab"] == "Spatial Saturation":
        st.subheader("Spatial Saturation")
        category_occ = occupancy_merged.groupby('room_class').agg(
            total_successful=('successful_bookings', 'sum'),
            total_capacity=('capacity', 'sum')
        ).reset_index()
        category_occ['occupancy_pct'] = (category_occ['total_successful'] / category_occ['total_capacity'].replace(0, 1)) * 100
        fig_occ = px.bar(category_occ, x='room_class', y='occupancy_pct', 
                         title="Average Occupancy % across Room Categories (RT1-RT4)",
                         labels={'room_class': 'Room Category', 'occupancy_pct': 'Occupancy Percentage (%)'},
                         color='occupancy_pct', color_continuous_scale='Inferno')
        fig_occ.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_occ, use_container_width=True)

# Keep app refreshing while camera runs
if webrtc_ctx.state.playing:
    if state_changed:
        st.rerun()
    else:
        time.sleep(1.0)
        st.rerun()