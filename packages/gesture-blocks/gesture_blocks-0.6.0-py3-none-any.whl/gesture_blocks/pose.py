# gesture_blocks/pose.py
import cv2
import mediapipe as mp
import time
from .core import get_arduino, connect_arduino

# Pose setup
_mp_pose = mp.solutions.pose
_pose = _mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
_draw = mp.solutions.drawing_utils

# Commands
CMD_FORWARD = b'F'
CMD_BACK = b'B'
CMD_LEFT = b'L'
CMD_RIGHT = b'R'
CMD_STOP = b'S'

def control_loop():
    """
    Control Otto robot using body pose:
    - Right hand up   -> FORWARD
    - Left hand up    -> BACK
    - Right leg lift  -> RIGHT
    - Left leg lift   -> LEFT
    - Otherwise       -> STOP
    """
    arduino = get_arduino()
    if arduino is None:
        raise RuntimeError("❌ Arduino not connected. Call connect_arduino() first.")

    cap = cv2.VideoCapture(0)
    last_cmd = None
    LEG_LIFT_THRESH = 0.12  # tune as needed

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _pose.process(img_rgb)

        command = CMD_STOP
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Key points
            r_wrist = lm[_mp_pose.PoseLandmark.RIGHT_WRIST]
            r_shoulder = lm[_mp_pose.PoseLandmark.RIGHT_SHOULDER]

            l_wrist = lm[_mp_pose.PoseLandmark.LEFT_WRIST]
            l_shoulder = lm[_mp_pose.PoseLandmark.LEFT_SHOULDER]

            r_ankle = lm[_mp_pose.PoseLandmark.RIGHT_ANKLE]
            r_hip = lm[_mp_pose.PoseLandmark.RIGHT_HIP]

            l_ankle = lm[_mp_pose.PoseLandmark.LEFT_ANKLE]
            l_hip = lm[_mp_pose.PoseLandmark.LEFT_HIP]

            # --- Gesture detection ---
            if r_wrist.y < r_shoulder.y:
                command = CMD_FORWARD
            elif l_wrist.y < l_shoulder.y:
                command = CMD_BACK
            else:
                right_leg_diff = r_ankle.y - r_hip.y
                left_leg_diff = l_ankle.y - l_hip.y

                if right_leg_diff < LEG_LIFT_THRESH:
                    command = CMD_RIGHT
                elif left_leg_diff < LEG_LIFT_THRESH:
                    command = CMD_LEFT
                else:
                    command = CMD_STOP

            # Draw skeleton
            _draw.draw_landmarks(frame, results.pose_landmarks, _mp_pose.POSE_CONNECTIONS)

        # Send if changed
        if command != last_cmd:
            arduino.write(command)
            print(f"➡️ Sent: {command.decode()}")
            last_cmd = command

        cv2.imshow("Otto Pose Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
