# gesture_blocks/otto.py
import cv2
import mediapipe as mp
from .core import get_arduino, start_camera

# Mediapipe setup
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
_mp_draw = mp.solutions.drawing_utils

def _count_fingers(hand_landmarks):
    """Utility to count fingers from Mediapipe landmarks"""
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    thumb_tip, thumb_ip = 4, 3
    count = 0

    # Thumb check (x-axis)
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_ip].x:
        count += 1

    # Other 4 fingers (y-axis check)
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            count += 1

    return count

def control_loop():
    """
    Gesture-controlled Otto loop.
    1 finger  -> FORWARD
    2 fingers -> BACKWARD
    3 fingers -> LEFT
    4 fingers -> RIGHT
    5 fingers -> DANCE
    0 fingers -> STOP
    """
    arduino = get_arduino()
    if arduino is None:
        raise RuntimeError("❌ Arduino not connected. Call connect_arduino() first.")

    cap = start_camera()
    last_command = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _hands.process(rgb)

        command = "STOP"
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                _mp_draw.draw_landmarks(frame, hand_landmarks, _mp_hands.HAND_CONNECTIONS)
                fingers = _count_fingers(hand_landmarks)

                if fingers == 1: command = "FORWARD"
                elif fingers == 2: command = "BACKWARD"
                elif fingers == 3: command = "LEFT"
                elif fingers == 4: command = "RIGHT"
                elif fingers == 5: command = "DANCE"

        if command != last_command:
            arduino.write((command + "\n").encode())
            print(f"➡️ Sent: {command}")
            last_command = command

        cv2.putText(frame, f"Command: {command}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Otto Control", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()
