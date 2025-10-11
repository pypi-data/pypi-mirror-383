# gesture_wheels/wheels.py
import cv2
import mediapipe as mp
import time
from .core import get_robot

# --- Mediapipe setup (only once) ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- Persistent camera ---
cap = cv2.VideoCapture(0)

# --- Finger landmark IDs ---
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]
THUMB_TIP, THUMB_IP = 4, 3

# --- Performance tracker ---
prev_time = 0

# --- Gesture Mapping ---
GESTURE_ACTIONS = {
    1: "FORWARD",
    2: "BACKWARD",
    3: "RIGHT",
    4: "LEFT",
    5: "STOP"
}


def detect_fingers():
    """Detect number of fingers and return command name."""
    global prev_time
    ret, frame = cap.read()
    if not ret:
        return "NONE"

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    count = 0
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Thumb
            if lm[THUMB_TIP].x < lm[THUMB_IP].x:
                count += 1
            # Other 4 fingers
            for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
                if lm[tip].y < lm[pip].y:
                    count += 1

    # Get readable action text
    action = GESTURE_ACTIONS.get(count, "NONE")

    # --- Draw blue-green command box ---
    cv2.rectangle(frame, (180, 20), (460, 80), (255, 255, 255), -1)
    cv2.rectangle(frame, (180, 20), (320, 80), (255, 0, 0), -1)
    cv2.rectangle(frame, (320, 20), (460, 80), (0, 255, 0), -1)
    cv2.putText(frame, f"Cmd: {action}", (200, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 4)

    # --- FPS display ---
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time + 1e-6)
    prev_time = curr_time
    cv2.putText(frame, f"{int(fps)} FPS", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Gesture Wheels", frame)
    return action


def send_command(robot, action):
    """Send action to ESP32 via Serial."""
    if robot and action != "NONE":
        try:
            robot.write((action[0] + "\n").encode())
            print(f"➡ Sent: {action}")
        except Exception as e:
            print(f"⚠ Serial Error: {e}")


def check_exit():
    """Press ESC to quit"""
    if cv2.waitKey(1) & 0xFF == 27:
        cap.release()
        cv2.destroyAllWindows()
        return True
    return False
