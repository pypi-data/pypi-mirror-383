# DIYA_Gesture

Control your **ESP32 wheel robot** using hand gestures detected by a webcam.  
Designed for students and educators to learn how AI (MediaPipe) and IoT (ESP32) work together.

## Features
- Gesture control using **MediaPipe + OpenCV**
- Simple serial communication with **ESP32**
- Finger-count mapping:
  - 1 → FORWARD (F)
  - 2 → BACKWARD (B)
  - 3 → RIGHT (R)
  - 4 → LEFT (L)
  - 5 → STOP (S)
- Gesture must be **held for 2 seconds** to send command (reduces flicker)
- Safety: if no hand detected, robot receives **STOP**

## Installation
```bash
pip install DIYA-Gesture
