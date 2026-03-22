import sys
print(f"Python sys.executable: {sys.executable}")

try:
    import mediapipe as mp
    print(f"MediaPipe path: {mp.__file__}")
    print(f"MediaPipe version: {mp.__version__}")
    print(f"Has solutions? {hasattr(mp, 'solutions')}")
    if hasattr(mp, 'solutions'):
        print(f"Has hands? {hasattr(mp.solutions, 'hands')}")
except Exception as e:
    print(f"Error checking mediapipe: {e}")
