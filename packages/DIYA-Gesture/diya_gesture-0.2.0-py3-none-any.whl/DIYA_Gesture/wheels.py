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

# === MediaPipe setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# === Camera object ===
_cap = None


def start_camera(index: int = 0):
    """Initialize webcam."""
    global _cap
    if _cap is None:
        _cap = cv2.VideoCapture(index)
        if not _cap.isOpened():
            raise RuntimeError("❌ Could not open webcam.")
    return _cap


def stop_camera():
    """Release camera and destroy all windows."""
    global _cap
    if _cap is not None:
        _cap.release()
        _cap = None
    cv2.destroyAllWindows()


# === Gesture logic ===
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]
THUMB_TIP, THUMB_IP = 4, 3

GESTURE_ACTIONS = {
    1: "FORWARD",
    2: "BACKWARD",
    3: "RIGHT",
    4: "LEFT",
    5: "STOP"
}

HOLD_SECONDS = 1.0
_last_sent_action = None
_hold_start_time = None


def _count_fingers_from_landmarks(hand_landmarks):
    """Return count (0..5) from mediapipe hand landmarks."""
    lm = hand_landmarks.landmark
    count = 0
    try:
        if lm[THUMB_TIP].x < lm[THUMB_IP].x:
            count += 1
    except Exception:
        pass

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
    Draws full blue box with gesture text centered (no Cmd/FPS).
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
        # Dynamic text box: width based on text size
        text = f"{count} : {action}" if action != "NONE" else "0 : STOP"
        font_scale = 1.2
        thickness = 3
        font = cv2.FONT_HERSHEY_SIMPLEX

        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        padding = 25
        x, y = 60, 80
        box_width = text_width + padding * 2
        box_height = text_height + padding

        # Draw full blue background box
        cv2.rectangle(frame, (x, y - box_height), (x + box_width, y + 10), (255, 0, 0), -1)

        # Center white text
        text_x = x + padding
        text_y = y - int(padding / 2)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # Display
        cv2.imshow("DIYA Gesture Control", frame)

    return count, action


def send_command_if_stable(robot, action: str):
    """
    Send a single-letter command to robot if gesture is stable for HOLD_SECONDS.
    Sends STOP when no hand is detected.
    """
    global _last_sent_action, _hold_start_time

    if robot is None:
        print("⚠ Robot not connected (send_command_if_stable).")
        return

    char_map = {"FORWARD": "F", "BACKWARD": "B", "RIGHT": "R", "LEFT": "L", "STOP": "S"}

    # If no valid hand -> STOP once
    if action == "NONE" or action == "STOP":
        if _last_sent_action != "STOP":
            try:
                robot.write(b"S\n")
                print("➡ Sent: S (STOP) [no/invalid hand]")
                _last_sent_action = "STOP"
            except Exception as e:
                print(f"⚠ Serial send error: {e}")
        _hold_start_time = None
        return

    # New gesture → reset timer
    if action != _last_sent_action:
        _hold_start_time = time.time()
        _last_sent_action = action
        return

    # Same gesture still active → check hold duration
    if _hold_start_time is None:
        _hold_start_time = time.time()
        return

    if time.time() - _hold_start_time >= HOLD_SECONDS:
        try:
            cmd = char_map.get(action, "S").encode() + b"\n"
            robot.write(cmd)
            print(f"➡ Sent: {cmd.strip().decode()} ({action})")
        except Exception as e:
            print(f"⚠ Serial send error: {e}")
        _hold_start_time = None
        _last_sent_action = None


def check_exit():
    """Return True when ESC pressed and cleanup."""
    if cv2.waitKey(1) & 0xFF == 27:
        stop_camera()
        return True
    return False


def control_loop(port: str = None):
    """Main gesture detection + control loop."""
    robot = None
    try:
        robot = get_robot()
    except RuntimeError:
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
