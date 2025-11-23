import json
import os
import sys

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.adb_controller import AdbController
from models.game_options import GameOptions
from scripts.core import (
    go_last,
    go_up,
    harvest_tree,
    open_chest,
    open_game,
    plant_tree,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python trong_cay_su_kien.py <device_id> [game_options_json]")
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

    for i in range(1000):
        print(f"{i}: Run trong cay su kien")
        if game_options.open_chest and (i % 10) == 0:
            open_chest(manager)

        # Todo
        if i == 0:
            go_up(manager)
            plant_tree(manager)
            go_up(manager, 4)
            plant_tree(manager)
            go_up(manager, 4)
            plant_tree(manager)
            go_last(manager)

        if i < 999:
            go_up(manager)
            harvest_tree(manager)
            plant_tree(manager)
            go_up(manager, 4)
            harvest_tree(manager)
            plant_tree(manager)
            go_up(manager, 4)
            harvest_tree(manager)
            plant_tree(manager)
            go_last(manager)

        else:
            go_up(manager)
            harvest_tree(manager)
            go_up(manager, 4)
            harvest_tree(manager)
            go_up(manager, 4)
            harvest_tree(manager)
            go_last(manager)

    print("The automation completed")


if __name__ == "__main__":
    main()
