import cv2
import mediapipe as mp
import time
from .core import get_robot

# === Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# === Finger landmarks ===
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]
THUMB_TIP, THUMB_IP = 4, 3
prev_time = 0

# === Mapping ===
GESTURE_ACTIONS = {
    1: "FORWARD",
    2: "BACKWARD",
    3: "RIGHT",
    4: "LEFT",
    5: "STOP"
}

# === Dynamic Box Colors for Feedback ===
COLOR_MAP = {
    "FORWARD": (0, 255, 0),     # Green
    "BACKWARD": (0, 255, 255),  # Yellow
    "RIGHT": (255, 0, 0),       # Blue
    "LEFT": (255, 128, 0),      # Orange
    "STOP": (0, 0, 255),        # Red
    "NONE": (200, 200, 200)     # Gray (idle)
}

# === Gesture hold timer ===
last_action = "STOP"
hold_start = 0
hold_duration = 1.0   # seconds


def detect_fingers():
    """Detect hand gestures and display result with color feedback."""
    global prev_time
    ret, frame = cap.read()
    if not ret:
        return 0, "NONE"

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
            # Other fingers
            for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
                if lm[tip].y < lm[pip].y:
                    count += 1

    action = GESTURE_ACTIONS.get(count, "NONE")
    color = COLOR_MAP.get(action, (255, 255, 255))

    # === Draw Command Box ===
    box_start, box_end = (120, 20), (550, 80)
    cv2.rectangle(frame, box_start, box_end, color, -1)

    # Centered Text (e.g. "1 : FORWARD")
    cmd_text = f"{count} : {action}" if action != "NONE" else "0 : STOP"
    text_size = cv2.getTextSize(cmd_text, cv2.FONT_HERSHEY_SIMPLEX, 1.3, 4)[0]
    text_x = 120 + (430 - text_size[0]) // 2
    text_y = 70
    cv2.putText(frame, cmd_text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 4)

    # === FPS ===
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time + 1e-6)
    prev_time = curr_time
    cv2.putText(frame, f"{int(fps)} FPS", (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Gesture Wheels", frame)
    return count, action


def send_command(robot, action):
    """Send command if held steady for 2 seconds. Stop if no hand."""
    global last_action, hold_start

    if not robot:
        print("⚠ No robot connected.")
        return

    # Auto stop if no hand
    if action == "NONE":
        if last_action != "STOP":
            robot.write(b"S\n")
            last_action = "STOP"
            print("🛑 No hand detected — STOP sent.")
        return

    # Start holding timer if new gesture
    if action != last_action:
        hold_start = time.time()
        last_action = action
        return

    # If gesture held > 2 seconds, send
    if time.time() - hold_start >= hold_duration:
        try:
            robot.write((action[0] + "\n").encode())
            print(f"➡ Sent: {action[0]} ({action})")
            hold_start = time.time()  # reset timer
        except Exception as e:
            print(f"⚠ Serial error: {e}")


def check_exit():
    """Press ESC to quit."""
    if cv2.waitKey(1) & 0xFF == 27:
        cap.release()
        cv2.destroyAllWindows()
        return True
    return False
