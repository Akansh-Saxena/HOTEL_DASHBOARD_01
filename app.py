import streamlit as st
import pandas as pd
import plotly.express as px
import cv2
import av
import queue
import mediapipe as mp
from deepface import DeepFace
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode

# Configuration
st.set_page_config(page_title="Hospitality Dashboard", layout="wide", page_icon="📈")

# --- INITIALIZE SESSION STATE ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Revenue Metrics"
if "zoom_solstice" not in st.session_state:
    st.session_state["zoom_solstice"] = False
if "agg_level" not in st.session_state:
    st.session_state["agg_level"] = "Daily"  # Default granular

# --- WEBRTC & MULTIMODAL PROCESSOR (PHASE 2 & 3) ---
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
        
        # Only process every 5th frame to save CPU
        if self.frame_skip % 5 == 0:
            gesture = None
            emotion = None
            
            # --- PHASE 2: MediaPipe Gesture Recognition ---
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Simple heuristic for finger counting
                    # landmarks: 4 (thumb), 8 (index), 12 (middle), 16 (ring), 20 (pinky)
                    # For simplicity, check Y-coordinate tip vs pip (joint below)
                    fingers_up = 0
                    tips = [8, 12, 16, 20]
                    pips = [6, 10, 14, 18]
                    for tip, pip in zip(tips, pips):
                        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                            fingers_up = fingers_up + 1
                    # Thumb
                    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                        fingers_up = int(fingers_up) + 1
                        
                    if fingers_up >= 4:
                        gesture = "Open Hand" # Switch to Revenue View
                    elif fingers_up == 2:
                        gesture = "Peace" # Switch to Occupancy View
                    elif fingers_up == 0:
                        gesture = "Fist" # Toggle Solstice Zoom
            
            # --- PHASE 3: DeepFace Emotion Recognition ---
            # Try/except to prevent thread crash if no face is found
            try:
                # Use a lightweight backend if possible, or just default deepface
                res = DeepFace.analyze(img_rgb, actions=['emotion'], enforce_detection=False, silent=True)
                if isinstance(res, list):
                    emotion = res[0]['dominant_emotion']
                else:
                    emotion = res['dominant_emotion']
            except Exception as e:
                emotion = None

            # Push to queue safely
            if not self.result_queue.full() and (gesture or emotion):
                self.result_queue.put({"gesture": gesture, "emotion": emotion})

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- UI SIDEBAR: START WEBRTC ---
st.sidebar.title("Multimodal Controls")
st.sidebar.markdown("Use your webcam for Gesture & Emotion control.")

webrtc_ctx = webrtc_streamer(
    key="multimodal",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=MultimodalProcessor,
    async_processing=True,
    media_stream_constraints={"video": True, "audio": False},
)

if webrtc_ctx.state.playing:
    try:
        res = webrtc_ctx.video_processor.result_queue.get(timeout=0.1)
        if res["gesture"] == "Open Hand":
            st.session_state["active_tab"] = "Revenue Metrics"
        elif res["gesture"] == "Peace":
            st.session_state["active_tab"] = "Spatial Saturation"
        elif res["gesture"] == "Fist":
             st.session_state["zoom_solstice"] = not st.session_state["zoom_solstice"]
             
        if res["emotion"] in ["angry", "disgust", "fear", "sad"]:
             st.session_state["agg_level"] = "Monthly"
        elif res["emotion"] in ["happy", "neutral", "surprise"]:
             st.session_state["agg_level"] = "Daily"
             
    except queue.Empty:
        pass

st.sidebar.markdown(f"**Current Action Tab:** {st.session_state['active_tab']}")
st.sidebar.markdown(f"**Solstice Zoom:** {'Active' if st.session_state['zoom_solstice'] else 'Inactive'}")
st.sidebar.markdown(f"**Data Aggregation (Emotion):** {st.session_state['agg_level']}")

# --- DATA LOADING AND CACHING ---
@st.cache_data
def load_data():
    try:
        bookings_df = pd.read_csv("bookings.csv")
        occupancy_df = pd.read_csv("occupancy.csv")
        rooms_df = pd.read_csv("rooms.csv")
        return bookings_df, occupancy_df, rooms_df
    except FileNotFoundError as e:
        st.error(f"Error loading data files: {e}")
        return None, None, None

bookings_df, occupancy_df, rooms_df = load_data()

# --- PREPROCESSING ---
if bookings_df is not None and occupancy_df is not None and rooms_df is not None:
    if 'capacityy' in occupancy_df.columns:
        occupancy_df.rename(columns={'capacityy': 'capacity'}, inplace=True)
    if 'room\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n             ' in occupancy_df.columns:
         occupancy_df.rename(columns={'room\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n             ': 'room_id'}, inplace=True)
    elif 'room' in occupancy_df.columns:
         occupancy_df.rename(columns={'room': 'room_id'}, inplace=True)
         
    occupancy_df['room_id'] = occupancy_df['room_id'].astype(str).str.strip()
    rooms_df['room_id'] = rooms_df['room_id'].astype(str).str.strip()

    occupancy_merged = pd.merge(occupancy_df, rooms_df, on="room_id", how="left")
    occupancy_merged['occupancy_pct'] = (occupancy_merged['successful_bookings'] / occupancy_merged['capacity'].replace(0, 1)) * 100

    bookings_df['booking_date'] = pd.to_datetime(bookings_df['booking_date'], errors='coerce')
    bookings_df['check_in_date'] = pd.to_datetime(bookings_df['check_in_date'], errors='coerce')
    occupancy_merged['check_in_date'] = pd.to_datetime(occupancy_merged['check_in_date'], errors='coerce')

    # Apply Aggregation based on Emotion State
    if st.session_state["agg_level"] == "Monthly":
        bookings_df['display_date'] = bookings_df['check_in_date'].dt.to_period('M').dt.to_timestamp()
    else:
        bookings_df['display_date'] = bookings_df['check_in_date']

    # Apply Solstice Zoom (June 21st +/- 5 days) Filter
    if st.session_state["zoom_solstice"]:
         # Filter bookings around June 2022
         start_date = pd.to_datetime("2022-06-16")
         end_date = pd.to_datetime("2022-06-26")
         bookings_filtered = bookings_df[(bookings_df['check_in_date'] >= start_date) & (bookings_df['check_in_date'] <= end_date)]
    else:
         bookings_filtered = bookings_df

    # --- UI LAYOUT ---
    st.title("🏨 Strategic Hospitality Command Center")
    st.markdown("Dynamic Analytics with Kinematic & Affective Control")

    if st.session_state["active_tab"] == "Revenue Metrics":
        st.subheader(f"Revenue Disparity ({st.session_state['agg_level']} View)")
        
        platform_rev = bookings_filtered.groupby(['booking_platform', 'display_date'])[['revenue_generated', 'revenue_realized']].sum().reset_index()
        
        # Melt for dodged bar/line chart
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
        
        category_occ['occupancy_pct'] = (category_occ['total_successful'] / category_occ['total_capacity']) * 100
        
        fig_occ = px.bar(category_occ, x='room_class', y='occupancy_pct', 
                         title="Average Occupancy % across Room Categories (RT1-RT4)",
                         labels={'room_class': 'Room Category', 'occupancy_pct': 'Occupancy Percentage (%)'},
                         color='occupancy_pct', color_continuous_scale='Inferno')
        fig_occ.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_occ, use_container_width=True)
