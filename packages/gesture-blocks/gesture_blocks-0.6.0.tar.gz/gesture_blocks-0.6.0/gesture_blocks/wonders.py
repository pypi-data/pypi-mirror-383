# gesture_blocks/wonders.py
import cv2
import mediapipe as mp
import os

# Mediapipe setup
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
_mp_draw = mp.solutions.drawing_utils

def _count_fingers(hand_landmarks):
    """Count fingers for one hand"""
    fingers = []

    # Thumb
    fingers.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)

    # Other 4 fingers
    for tip in [8, 12, 16, 20]:
        fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y else 0)

    return sum(fingers)

def wonders_demo(folder="wonders", screen_width=1366, screen_height=768):
    """
    Show '7 Wonders of the World' images based on total fingers detected.
    - Requires a folder with 7 images inside (named in sorted order).
    """
    cap = cv2.VideoCapture(0)

    # Load images
    wonders = [cv2.imread(os.path.join(folder, img)) for img in sorted(os.listdir(folder))]
    wonders = [cv2.resize(img, (screen_width, screen_height)) for img in wonders]

    current_wonder = -1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _hands.process(rgb)

        fingers_up = 0
        if results.multi_hand_landmarks:
            counts = []
            for hand_landmarks in results.multi_hand_landmarks:
                _mp_draw.draw_landmarks(frame, hand_landmarks, _mp_hands.HAND_CONNECTIONS)
                counts.append(_count_fingers(hand_landmarks))
            fingers_up = sum(counts)  # sum both hands

        cv2.putText(frame, f"Fingers: {fingers_up}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Tracking", frame)

        # Display wonder based on finger count
        if 1 <= fingers_up <= 7:
            if current_wonder != fingers_up:
                current_wonder = fingers_up
                cv2.imshow("7 Wonders", wonders[fingers_up - 1])
        else:
            if current_wonder != -1:
                cv2.destroyWindow("7 Wonders")
                current_wonder = -1

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()
