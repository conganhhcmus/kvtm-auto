import json
import os
import sys

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.adb_controller import AdbController
from models.game_options import GameOptions
from scripts.core import open_chest, open_game, go_friend, go_home, buy_8_slot


def main():
    if len(sys.argv) < 2:
        print("Usage: python mua_vpsk.py <device_id> [game_options_json]")
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

    if game_options.open_game:
        open_game(manager)

    if game_options.open_chest:
        open_chest(manager)

    go_friend(manager, slot=1)

    for i in range(100_000):
        print(f"{i}: Run mua vat pham su kien")
        # Todo
        buy_8_slot(manager)

    go_home(manager)
    print("The automation completed")


if __name__ == "__main__":
    main()
