# gesture_blocks/sign.py
import cv2
import mediapipe as mp

# Mediapipe setup
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
_mp_draw = mp.solutions.drawing_utils

def _get_finger_state(hand_landmarks):
    """Return a list of 5 values (1=open, 0=closed) for [Thumb, Index, Middle, Ring, Pinky]"""
    fingers = []

    # Thumb
    fingers.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)

    # Other 4 fingers
    for tip in [8, 12, 16, 20]:
        fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y else 0)

    return fingers

def _map_gesture(fingers):
    """Map finger states to words"""
    total = sum(fingers)

    if fingers == [1, 0, 0, 0, 0]:
        return "Yes"
    elif fingers == [0, 1, 1, 0, 0]:
        return "No"
    elif total == 5:
        return "Hello"
    elif total == 0:
        return "Bye"
    elif fingers == [0, 1, 0, 0, 0]:
        return "Thanks"
    elif fingers == [0, 1, 1, 1, 1]:
        return "More"
    else:
        return "Unknown"

def converter_loop():
    """
    Start Sign Language Converter loop.
    Shows words based on gestures:
    - Thumb only      -> Yes
    - Index+Middle    -> No
    - All open        -> Hello
    - Fist (all down) -> Bye
    - Index only      -> Thanks
    - All except thumb-> More
    """
    cap = cv2.VideoCapture(0)
    word = "No gesture"

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                _mp_draw.draw_landmarks(frame, hand_landmarks, _mp_hands.HAND_CONNECTIONS)
                fingers = _get_finger_state(hand_landmarks)
                word = _map_gesture(fingers)

        cv2.putText(frame, f"Word: {word}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Sign Language Converter", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
