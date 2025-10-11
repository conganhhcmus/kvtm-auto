import json
import os
import sys

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs.adb_controller import AdbController
from models.game_options import GameOptions
from scripts.core import (
    SellOption,
    go_down,
    go_last,
    go_up,
    harvest_tree,
    make_items,
    open_chest,
    open_game,
    plant_tree,
    sell_items,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python nuoc_hoa_tao.py <device_id> [game_options_json]")
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

    for i in range(100):
        print(f"{i}: Run nuoc hoa tao")
        if game_options.open_chest:
            open_chest(manager)

        for j in range(10):
            isEven = j % 2 == 0
            # auto
            go_up(manager)
            plant_tree(manager, "tao")
            go_up(manager, 2)
            plant_tree(manager, "tao")
            go_up(manager, 2)
            plant_tree(manager, "tao")
            go_up(manager, 2)
            plant_tree(manager, "tao")
            go_down(manager, 6)

            if isEven:
                harvest_tree(manager)
                plant_tree(manager, "tao")
                go_up(manager, 2)

            harvest_tree(manager)
            plant_tree(manager, "tuyet")
            go_up(manager, 2)
            harvest_tree(manager)
            plant_tree(manager, "tuyet")
            go_up(manager, 2)
            harvest_tree(manager)

            if not isEven:
                go_up(manager, 2)
                harvest_tree(manager)

            go_down(manager, 6)

            harvest_tree(manager)
            make_items(manager, 2, 0, 6)  # nuoc tao
            go_up(manager, 2)
            harvest_tree(manager)
            go_up(manager, 2)
            if isEven:
                harvest_tree(manager)

            make_items(manager, 1, 1, 6)  # tinh dau tao
            go_up(manager, 2)
            make_items(manager, 2, 1, 6)  # nuoc hoa tao
            go_last(manager)

        if game_options.sell_items:
            sell_items(
                manager,
                SellOption.GOODS,
                [{"key": "nuoc-hoa-tao", "value": 6}],
            )

        i += 1

    print("The automation completed")


if __name__ == "__main__":
    main()
