import json
import os
import sys

from src.libs.adb_controller import AdbController
from src.models.game_options import GameOptions
from src.scripts.core import open_chest, open_game, sell_items


def main():
    if len(sys.argv) < 2:
        print("Usage: python vai_xanh_la.py <device_id> [game_options_json]")
        sys.exit(1)

    device_id = sys.argv[1]
    game_options = GameOptions()

    # Parse game options if provided
    if len(sys.argv) > 2:
        try:
            options_dict = json.loads(sys.argv[2])
            game_options = GameOptions.from_dict(options_dict)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for game_options")
            sys.exit(1)

    manager = AdbController(device_id)

    options_str = game_options.to_dict()
    print(f"[{device_id}] Starting vai xanh la automation with options:")
    print(f"[{device_id}] {options_str}")

    if game_options.open_game:
        open_game(manager)

    if game_options.open_chest:
        open_chest(manager)

    if game_options.sell_items:
        sell_items(manager)

    # Example: Click on text
    manager.click_text("Submit")

    # Example: Click on image (template in assets)
    template_path = os.path.join("src", "assets", "button_template.png")
    manager.click_image(template_path)

    print(f"[{device_id}] Vai xanh la automation completed")


if __name__ == "__main__":
    main()
