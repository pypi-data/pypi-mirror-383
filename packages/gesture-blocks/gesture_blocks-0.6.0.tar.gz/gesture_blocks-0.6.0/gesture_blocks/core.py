# gesture_blocks/core.py
import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports
import time

# ========== GLOBALS ==========
_arduino = None   # Arduino connection (shared across projects)
_cap = None       # Camera object

# ========== MEDIAPIPE SETUP ==========
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
_mp_draw = mp.solutions.drawing_utils


# ========== ARDUINO HELPERS ==========
def connect_arduino(port: str = None, baud: int = 9600):
    """
    Connect to Arduino over serial.
    Automatically detects available port if not provided.

    Example:
        connect_arduino()          # auto-detects
        connect_arduino('COM3')    # manually specify
    """
    global _arduino

    # --- Auto port detection ---
    if port is None:
        print("🔍 Searching for connected Arduino devices...")
        ports = list(serial.tools.list_ports.comports())

        for p in ports:
            # Match common identifiers (Arduino official + clone chips)
            if any(name in p.description for name in ["Arduino", "CH340", "CP210", "USB-SERIAL", "ttyACM", "ttyUSB"]):
                port = p.device
                print(f"✅ Arduino detected on {port} ({p.description})")
                break

        if port is None:
            raise RuntimeError("❌ No Arduino found! Please connect your board and try again.")

    # --- Serial connection ---
    _arduino = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # wait for Arduino reset
    print(f"🔗 Connected to Arduino on {port} at {baud} baud.")
    return _arduino


def get_arduino():
    """Return the Arduino Serial object (or None if not connected)."""
    global _arduino
    if _arduino is None:
        raise RuntimeError("❌ Arduino not connected. Call connect_arduino() first.")
    return _arduino


# ========== CAMERA HELPERS ==========
def start_camera(index=0):
    """Start the default webcam."""
    global _cap
    _cap = cv2.VideoCapture(index)
    if not _cap.isOpened():
        raise RuntimeError("❌ Could not open webcam")
    return _cap


def get_camera():
    """Return the global camera object (or None if not started)."""
    return _cap


# ========== FINGER DETECTION ==========
def detect_fingers(cap=None, show=True):
    """
    Detect number of fingers (0..5).
    Draws result on the frame if show=True.
    Returns the count.
    """
    global _cap, _hands, _mp_draw
    if cap is None:
        cap = _cap
    if cap is None:
        raise RuntimeError("❌ Camera not started. Call start_camera() first.")

    success, img = cap.read()
    if not success:
        return 0

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _hands.process(img_rgb)
    fingers_up = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if show:
                _mp_draw.draw_landmarks(img, handLms, _mp_hands.HAND_CONNECTIONS)

            tip_ids = [4, 8, 12, 16, 20]
            landmarks = handLms.landmark
            fingers = []

            # Thumb (simple heuristic assuming right hand)
            fingers.append(1 if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x else 0)

            # Other 4 fingers
            for i in range(1, 5):
                fingers.append(1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y else 0)

            fingers_up = fingers.count(1)

    if show:
        cv2.putText(img, f"Fingers: {fingers_up}", (60, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        cv2.imshow("Gesture Control", img)

    return fingers_up
