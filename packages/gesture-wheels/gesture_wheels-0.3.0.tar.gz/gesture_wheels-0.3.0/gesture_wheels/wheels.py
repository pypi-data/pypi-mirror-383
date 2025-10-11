# gesture_wheels/wheels.py
import cv2
import mediapipe as mp
import time
from .core import get_robot

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def control_loop():
    robot = get_robot()
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    print("🎥 Starting Gesture Wheels Control...")

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        cmd = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                lm = handLms.landmark
                tips = [4, 8, 12, 16, 20]
                fingers = []

                # Thumb
                fingers.append(1 if lm[tips[0]].x < lm[tips[0] - 1].x else 0)

                # Other 4 fingers
                for i in range(1, 5):
                    fingers.append(1 if lm[tips[i]].y < lm[tips[i] - 2].y else 0)

                count = fingers.count(1)

                # Map gestures
                if count == 1:
                    cmd = "F"
                elif count == 2:
                    cmd = "B"
                elif count == 3:
                    cmd = "R"
                elif count == 4:
                    cmd = "L"
                elif count == 5:
                    cmd = "S"

        # === Display Command Box ===
        if cmd:
            cmd_label = {
                "F": "FORWARD",
                "B": "BACKWARD",
                "L": "LEFT",
                "R": "RIGHT",
                "S": "STOP"
            }.get(cmd, "")

            box_w, box_h = 320, 80
            x_center = frame.shape[1] // 2
            y_start = 20

            x1, y1 = x_center - box_w // 2, y_start
            x2, y2 = x_center + box_w // 2, y_start + box_h

            # Blue left half, Green right half
            cv2.rectangle(frame, (x1, y1), (x1 + box_w // 2, y2), (255, 0, 0), -1)
            cv2.rectangle(frame, (x1 + box_w // 2, y1), (x2, y2), (0, 255, 0), -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)

            # Center text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(cmd_label, font, 1.4, 3)[0]
            text_x = x_center - text_size[0] // 2
            text_y = y1 + (box_h + text_size[1]) // 2
            cv2.putText(frame, cmd_label, (text_x, text_y), font, 1.4, (255, 255, 255), 4, cv2.LINE_AA)

            # Send to ESP32
            robot.write(f"{cmd}\n".encode())
            print(f"Sent: {cmd}")

        cv2.imshow("Gesture Wheels", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()
