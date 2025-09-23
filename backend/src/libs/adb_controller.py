import os
import subprocess
import tempfile

import cv2
import numpy as np
import pytesseract
from PIL import Image


class _MultiTouchController:
    """Private controller for managing multiple touch pointers on a device"""

    def __init__(self, serial):
        self.serial = serial
        self.device = self._get_touch_device(serial)
        self.pointers = {}  # {pointer_id: (x, y)}
        self.next_pointer_id = 0

    @staticmethod
    def _get_touch_device(serial):
        """Get touch device path for the given device serial"""
        cmd = ['adb', '-s', serial, 'shell', 'getevent -p']
        result = subprocess.run(cmd, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if 'ABS_MT_POSITION_X' in line:
                return line.split()[-1]  # Returns device path like /dev/input/event3
        raise RuntimeError("Touch device not found")

    @staticmethod
    def _send_touch_event(serial, device, event_type, event_code, value):
        """Send touch event to device"""
        cmd = ['adb', '-s', serial, 'shell', 'sendevent', device, str(event_type), str(event_code), str(value)]
        subprocess.run(cmd, check=True)

    def add_pointer(self, x, y):
        """Add a new touch pointer at the given coordinates"""
        pointer_id = self.next_pointer_id
        self.next_pointer_id += 1
        self.pointers[pointer_id] = (x, y)
        # Send DOWN event with tracking ID
        self._send_pointer_event('DOWN', pointer_id, x, y)
        return pointer_id

    def move_pointer(self, pointer_id, x, y):
        """Move an existing pointer to new coordinates"""
        if pointer_id not in self.pointers:
            raise ValueError("Invalid pointer ID")
        self.pointers[pointer_id] = (x, y)
        self._send_pointer_event('MOVE', pointer_id, x, y)

    def remove_pointer(self, pointer_id):
        """Remove a touch pointer"""
        if pointer_id not in self.pointers:
            raise ValueError("Invalid pointer ID")
        x, y = self.pointers[pointer_id]
        self._send_pointer_event('UP', pointer_id, x, y)
        del self.pointers[pointer_id]

    def _send_pointer_event(self, action, pointer_id, x, y):
        """Send touch event for a specific pointer"""
        # Event codes (may vary by device; common values)
        EV_ABS = 3
        ABS_MT_TRACKING_ID = 57  # Assign/remove tracking ID
        ABS_MT_POSITION_X = 53   # X coordinate
        ABS_MT_POSITION_Y = 54   # Y coordinate
        SYN_REPORT = 0           # Synchronize events

        if action == 'DOWN':
            self._send_touch_event(self.serial, self.device, EV_ABS, ABS_MT_TRACKING_ID, pointer_id)
        elif action == 'UP':
            self._send_touch_event(self.serial, self.device, EV_ABS, ABS_MT_TRACKING_ID, -1)  # -1 to release

        self._send_touch_event(self.serial, self.device, EV_ABS, ABS_MT_POSITION_X, x)
        self._send_touch_event(self.serial, self.device, EV_ABS, ABS_MT_POSITION_Y, y)
        self._send_touch_event(self.serial, self.device, SYN_REPORT, 0, 0)  # Sync all pointers


class AdbController:
    def __init__(self, serial):
        self.serial = serial
        self._multi_touch = _MultiTouchController(serial)

    def tap(self, x, y):
        """Simulate a tap at (x, y)"""
        subprocess.run(
            ["adb", "-s", self.serial, "shell", "input", "tap", str(x), str(y)], check=True
        )

    def capture_screen(self):
        """Capture device screen and return local file path"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            subprocess.run(
                ["adb", "-s", self.serial, "shell", "screencap", "-p"],
                stdout=tmp,
                check=True,
            )
            return tmp.name

    def find_image_on_screen(self, screenshot_path, template_path, threshold=0.8):
        """Find template image in screenshot using OpenCV"""
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        if screenshot is None or template is None:
            return None

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        return None

    def find_text_on_screen(self, screenshot_path, target_text, lang="eng"):
        """Find text position using OCR"""
        img = Image.open(screenshot_path)
        data = pytesseract.image_to_data(
            img, lang=lang, output_type=pytesseract.Output.DICT
        )

        for i in range(len(data["text"])):
            if target_text.lower() in data["text"][i].lower():
                x = data["left"][i] + data["width"][i] // 2
                y = data["top"][i] + data["height"][i] // 2
                return (x, y)
        return None

    def click_image(self, template_path, threshold=0.8):
        """Click on a template image found on screen"""
        screenshot_path = self.capture_screen()
        try:
            coords = self.find_image_on_screen(
                screenshot_path, template_path, threshold
            )
            if coords:
                self.tap(*coords)
                return True
            return False
        finally:
            os.unlink(screenshot_path)

    def click_text(self, target_text, lang="eng"):
        """Click on text found on screen"""
        screenshot_path = self.capture_screen()
        try:
            coords = self.find_text_on_screen(screenshot_path, target_text, lang)
            if coords:
                self.tap(*coords)
                return True
            return False
        finally:
            os.unlink(screenshot_path)

    def add_pointer(self, x, y):
        """Add a new touch pointer at the given coordinates"""
        return self._multi_touch.add_pointer(x, y)

    def move_pointer(self, pointer_id, x, y):
        """Move an existing pointer to new coordinates"""
        self._multi_touch.move_pointer(pointer_id, x, y)

    def remove_pointer(self, pointer_id):
        """Remove a touch pointer"""
        self._multi_touch.remove_pointer(pointer_id)

    def get_active_pointers(self):
        """Get list of active pointer IDs"""
        return list(self._multi_touch.pointers.keys())

    def clear_all_pointers(self):
        """Remove all active pointers"""
        for pointer_id in list(self._multi_touch.pointers.keys()):
            self._multi_touch.remove_pointer(pointer_id)
