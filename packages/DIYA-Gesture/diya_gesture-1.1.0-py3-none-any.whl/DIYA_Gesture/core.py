# DIYA_Gesture/core.py
"""Serial helpers: auto-detect and connect to ESP32 via USB serial."""

import time
import serial
import serial.tools.list_ports

_robot = None

def connect_robot(port: str = None, baud: int = 9600, timeout: float = 1.0):
    """
    Connect to the ESP32 robot via serial.
    If port is None => auto-detect common USB -> serial device names.
    Returns a serial.Serial object.
    """
    global _robot
    if _robot is not None and _robot.is_open:
        return _robot

    if port is None:
        print("🔍 Searching for ESP32 / USB serial device...")
        for p in serial.tools.list_ports.comports():
            desc = (p.description or "").lower()
            if any(tag in desc for tag in ("esp32", "usb", "ch340", "cp210", "ttyusb")):
                port = p.device
                print(f"✅ Found candidate: {p.device} ({p.description})")
                break

    if port is None:
        raise RuntimeError("❌ No ESP32/USB serial device found. Plug it in and try again.")

    try:
        _robot = serial.Serial(port, baud, timeout=timeout)
        # some boards reset on open — let them boot
        time.sleep(2.0)
        print(f"🔗 Connected to robot on {port} @ {baud} baud.")
        return _robot
    except Exception as e:
        raise RuntimeError(f"❌ Failed to open serial port {port}: {e}") from e


def get_robot():
    """Return the connected serial object or raise if not connected."""
    global _robot
    if _robot is None or not getattr(_robot, "is_open", False):
        raise RuntimeError("❌ Robot not connected. Call connect_robot() first.")
    return _robot
