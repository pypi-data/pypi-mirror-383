# gesture_wheels/wheels.py
import cv2
import mediapipe as mp
from gesture_wheels.core import get_robot

_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
_draw = mp.solutions.drawing_utils

def _count_fingers(hand):
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    count = 0
    if hand.landmark[tips[0]].x < hand.landmark[pips[0]].x:
        count += 1
    for tip, pip in zip(tips[1:], pips[1:]):
        if hand.landmark[tip].y < hand.landmark[pip].y:
            count += 1
    return count

def control_loop():
    """1→F, 2→B, 3→R, 4→L, 5→S"""
    esp = get_robot()
    cap = cv2.VideoCapture(0)
    last = ""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = _hands.process(rgb)
        command = "S"
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                _draw.draw_landmarks(frame, hand, _mp_hands.HAND_CONNECTIONS)
                fingers = _count_fingers(hand)
                if fingers == 1: command = "F"
                elif fingers == 2: command = "B"
                elif fingers == 3: command = "R"
                elif fingers == 4: command = "L"
                elif fingers == 5: command = "S"
        if command != last:
            esp.write((command + "\n").encode())
            print(f"➡️ Sent: {command}")
            last = command
        cv2.putText(frame, f"Cmd: {command}", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.imshow("Gesture Wheels", frame)
        if cv2.waitKey(1) & 0xFF == 27: break
    cap.release()
    cv2.destroyAllWindows()
