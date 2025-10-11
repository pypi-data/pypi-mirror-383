# gesture_wheels/core.py
import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports
import time

_robot = None
_cap = None

def connect_robot(port=None, baud=9600):
    """Auto-detect and connect to ESP32 robot via Serial."""
    global _robot
    if port is None:
        print("🔍 Searching for ESP32 robot...")
        for p in serial.tools.list_ports.comports():
            if any(name in p.description for name in ["USB", "ESP32", "CH340", "ttyUSB", "CP210"]):
                port = p.device
                print(f"✅ Found ESP32 on {port}")
                break
    if port is None:
        raise RuntimeError("❌ No ESP32 found. Plug it in and try again.")

    _robot = serial.Serial(port, baud, timeout=1)
    time.sleep(2)
    print(f"🔗 Connected to ESP32 robot on {port} at {baud} baud.")
    return _robot

def get_robot():
    global _robot
    if _robot is None:
        raise RuntimeError("❌ Robot not connected. Call connect_robot() first.")
    return _robot
