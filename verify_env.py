import sys

print(f"🔍 Checking environment using Python version: {sys.version.split()[0]}\n")

libraries = [
    "streamlit",
    "pandas",
    "plotly",
    "cv2",            # This is opencv-python
    "av",             # PyAV for WebRTC
    "mediapipe",
    "deepface",
    "streamlit_webrtc"
]

all_passed = True

for lib in libraries:
    try:
        __import__(lib)
        print(f"✅ Successfully imported: {lib}")
    except ImportError as e:
        print(f"❌ FAILED to import: {lib} --> Error: {e}")
        all_passed = False

print("\n--------------------------------------------------")
if all_passed:
    print("🎉 ALL SYSTEMS GO! You are ready to run app.py")
else:
    print("⚠️  Some libraries are still missing. Check the red X's above.")
print("--------------------------------------------------")
