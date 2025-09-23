import json
import os
import sys

from src.libs.adb_controller import AdbController


def main():
    if len(sys.argv) < 2:
        print("Usage: python vai_xanh_la.py <device_id> [game_options_json]")
        sys.exit(1)

    device_id = sys.argv[1]
    game_options = {}

    # Parse game options if provided
    if len(sys.argv) > 2:
        try:
            game_options = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for game_options")
            sys.exit(1)

    manager = AdbController(device_id)

    print(f"[{device_id}] Starting vai xanh la automation with options: {game_options}")

    # Example: Tap at coordinates (500, 1000)
    manager.tap(500, 1000)

    # Example: Click on text
    manager.click_text("Submit")

    # Example: Click on image (template in assets)
    template_path = os.path.join("src", "assets", "button_template.png")
    manager.click_image(template_path)

    print(f"[{device_id}] Vai xanh la automation completed")


if __name__ == "__main__":
    main()
