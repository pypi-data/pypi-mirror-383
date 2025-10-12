# DIYA_Gesture/wheels.py
"""
Gesture detection and serial command sender for ESP32 wheeled robots.

Behavior:
 - Detect finger count (0..5) using MediaPipe.
 - Map finger counts to actions (words): FORWARD, BACKWARD, RIGHT, LEFT, STOP
 - When a gesture is held steadily for HOLD_SECONDS, send a single character command
   to the robot over serial: F, B, R, L, S.
 - If no hand detected => send STOP once (safety).
"""

import time
import cv2
import mediapipe as mp
from .core import get_robot

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# Camera (open default)
_cap = None

def start_camera(index: int = 0):
    global _cap
    if _cap is None:
        _cap = cv2.VideoCapture(index)
        if not _cap.isOpened():
            raise RuntimeError("❌ Could not open webcam.")
    return _cap

def stop_camera():
    global _cap
    if _cap is not None:
        _cap.release()
        _cap = None
    cv2.destroyAllWindows()

# Landmarks used to compute fingers up
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]
THUMB_TIP, THUMB_IP = 4, 3

# Gesture->Action mapping
GESTURE_ACTIONS = {
    1: "FORWARD",
    2: "BACKWARD",
    3: "RIGHT",
    4: "LEFT",
    5: "STOP"
}

# Color map for the command box
COLOR_MAP = {
    "FORWARD": (0, 200, 0),     # green
    "BACKWARD": (0, 200, 200),  # cyan-ish
    "RIGHT": (200, 0, 0),       # blue-red
    "LEFT": (0, 128, 255),      # orange
    "STOP": (0, 0, 220),        # red-ish
    "NONE": (80, 80, 80)        # grey
}

# Hold time required before sending command (seconds)
HOLD_SECONDS = 1.0

# Internal state for hold logic
_last_sent_action = None
_hold_start_time = None


def _count_fingers_from_landmarks(hand_landmarks):
    """Return count (0..5) from mediapipe hand_landmarks object."""
    lm = hand_landmarks.landmark
    count = 0
    # Thumb heuristic (x comparison assumes a roughly frontal hand)
    try:
        if lm[THUMB_TIP].x < lm[THUMB_IP].x:
            count += 1
    except Exception:
        # be tolerant of any indexing issues
        pass
    # Other fingers: tip above pip (y smaller)
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        try:
            if lm[tip].y < lm[pip].y:
                count += 1
        except Exception:
            continue
    return count


def detect_fingers(show: bool = True):
    """
    Read one frame from camera, detect finger count and return (count, action).
    If show=True it will render annotated frame and command box.
    """
    cap = start_camera()
    ret, frame = cap.read()
    if not ret:
        return 0, "NONE"

    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    count = 0
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            count = _count_fingers_from_landmarks(handLms)
            break

    action = GESTURE_ACTIONS.get(count, "NONE")

    if show:
        # draw command box (half blue, half green style)
        left, top, right, bottom = 120, 20, 550, 80
        # draw left half deep blue and right half green to match earlier design
        cv2.rectangle(frame, (left, top), (int((left+right)/2), bottom), (255, 0, 0), -1)   # blue
        cv2.rectangle(frame, (int((left+right)/2), top), (right, bottom), (0, 255, 0), -1)   # green

        # Put command text centered
        text = f"Cmd: {action}" if action != "NONE" else "Cmd: STOP"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)
        tx = left + ((right - left) - tw) // 2
        ty = top + (bottom - top + th) // 2 - 6
        cv2.putText(frame, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)

        # FPS small
        fps = int(1.0 / max(1e-6, (time.time() - getattr(detect_fingers, "_last_time", 0))))
        detect_fingers._last_time = time.time()
        cv2.putText(frame, f"{fps} FPS", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2)

        cv2.imshow("DIYA Gesture Control", frame)

    return count, action


def send_command_if_stable(robot, action: str):
    """
    Send the single-letter command to robot if action is held stable for HOLD_SECONDS.
    If action == "NONE" or "STOP" the robot will be sent STOP immediately (once).
    """
    global _last_sent_action, _hold_start_time

    if robot is None:
        print("⚠ Robot not connected (send_command_if_stable).")
        return

    # Map action -> character
    char_map = {"FORWARD": "F", "BACKWARD": "B", "RIGHT": "R", "LEFT": "L", "STOP": "S"}

    # If no actionable hand detected -> STOP once
    if action == "NONE" or action == "STOP":
        if _last_sent_action != "STOP":
            try:
                robot.write(b"S\n")
                print("➡ Sent: S (STOP) [no/invalid hand]")
                _last_sent_action = "STOP"
            except Exception as e:
                print(f"⚠ Serial send error: {e}")
        # reset hold timer
        _hold_start_time = None
        return

    # New gesture started -> reset timer
    if action != _last_sent_action:
        _hold_start_time = time.time()
        _last_sent_action = action
        return

    # Same gesture still present -> check hold duration
    if _hold_start_time is None:
        _hold_start_time = time.time()
        return

    if time.time() - _hold_start_time >= HOLD_SECONDS:
        # send once, then reset timer so we don't spam
        try:
            cmd = char_map.get(action, "S").encode() + b"\n"
            robot.write(cmd)
            print(f"➡ Sent: {cmd.strip().decode()} ({action})")
        except Exception as e:
            print(f"⚠ Serial send error: {e}")
        # reset hold start so repeated sends require another hold
        _hold_start_time = None
        _last_sent_action = None  # require re-hold to re-send same action


def check_exit():
    """Return True when ESC pressed (and cleanup)."""
    if cv2.waitKey(1) & 0xFF == 27:
        stop_camera()
        return True
    return False


def control_loop(port: str = None):
    """
    High level loop:
      1) auto-connects robot if port is None
      2) starts camera and runs gesture detection until ESC pressed
    """
    robot = None
    try:
        robot = get_robot()  # if already connected externally
    except RuntimeError:
        # try to auto-connect using core.connect_robot
        from .core import connect_robot
        robot = connect_robot(port)

    start_camera()
    print("🎥 Camera started. Show your hand. Press ESC to quit.")

    try:
        while True:
            _, action = detect_fingers(show=True)
            send_command_if_stable(robot, action)
            if check_exit():
                print("👋 Exiting gesture control.")
                break
    finally:
        stop_camera()
