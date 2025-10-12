# 🤖 Gesture Wheels

Control your **ESP32 Wheel Robot** using **hand gestures** detected by a webcam!  
This library is built for **students and educators** to learn how AI (MediaPipe) and IoT (ESP32) can work together.  

---

## 🚀 Features
- 🖐️ Gesture control using **MediaPipe + OpenCV**
- 🔌 Simple serial communication with **ESP32**
- 🎮 Finger-count mapping for robot motion:
  | Fingers | Command | Robot Action |
  |----------|----------|--------------|
  | ☝️ 1 | F | Move Forward |
  | ✌️ 2 | B | Move Backward |
  | 🤟 3 | R | Turn Right |
  | 🖖 4 | L | Turn Left |
  | 🖐️ 5 | S | Stop |

---

## 🧰 Requirements
- Python 3.7+
- ESP32 (connected via USB)
- Motor driver (L298N / L293D)
- `opencv-python`
- `mediapipe`
- `pyserial`

---

## ⚙️ Installation

```bash
pip install gesture-wheels
