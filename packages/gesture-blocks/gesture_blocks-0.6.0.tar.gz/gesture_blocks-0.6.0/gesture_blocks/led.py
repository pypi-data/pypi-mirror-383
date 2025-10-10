# gesture_blocks/led.py
from .core import get_arduino

def turn_on(device):
    """
    Turn on LED1/LED2/LED3 by name.
    Example:
        turn_on("LED1")
    """
    arduino = get_arduino()
    if arduino is None:
        raise RuntimeError("❌ Arduino not connected. Call connect_arduino() first.")

    if device == "LED1":
        arduino.write(b'1'); print("💡 LED1 ON")
    elif device == "LED2":
        arduino.write(b'2'); print("💡 LED2 ON")
    elif device == "LED3":
        arduino.write(b'3'); print("💡 LED3 ON")
    else:
        raise ValueError(f"❌ Unknown device: {device}")

def turn_off(device="ALL"):
    """
    Turn off LEDs. Device arg is just for display message.
    Example:
        turn_off("LED1")
        turn_off("ALL")
    """
    arduino = get_arduino()
    if arduino is None:
        raise RuntimeError("❌ Arduino not connected. Call connect_arduino() first.")

    arduino.write(b'0')
    print(f"❌ {device} OFF")
