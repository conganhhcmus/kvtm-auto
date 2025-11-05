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
    make_event,
    loop_num,
)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python tinh_dau_dua_tra_hoa_hong.py <device_id> [game_options_json]"
        )
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

    for i in range(loop_num):
        print(f"{i}: Run tinh dau dua, tra hoa hong")
        if game_options.open_chest:
            open_chest(manager)

        for j in range(10):
            # auto
            isEven = j % 2 == 0

            go_up(manager)
            plant_tree(manager, "tuyet", next=False)
            go_up(manager, 2)
            plant_tree(manager, "tuyet")
            go_up(manager, 2)
            plant_tree(manager, "tuyet")
            go_down(manager, 4)

            if isEven:
                harvest_tree(manager)
                plant_tree(manager, "hong")
                go_up(manager, 2)
                harvest_tree(manager)
                plant_tree(manager, "hong")
                go_up(manager, 2)
                harvest_tree(manager)
                plant_tree(manager, "hong")
                go_down(manager, 4)

            harvest_tree(manager)
            plant_tree(manager, "dua")
            go_up(manager, 2)
            harvest_tree(manager)
            plant_tree(manager, "dua")
            go_up(manager, 2)
            harvest_tree(manager)
            plant_tree(manager, "dua", num=6)
            go_down(manager, 4)

            make_items(manager, 1, 0, 6)  # hoa hong say
            make_items(manager, 2, 1, 3)  # nuoc tuyet
            harvest_tree(manager)
            go_up(manager, 2)
            harvest_tree(manager)
            go_up(manager, 2)
            harvest_tree(manager)
            make_items(manager, 1, 3, 6)  # tinh dau dua
            make_items(manager, 2, 0, 3)  # tra hoa hong
            go_last(manager)

        if game_options.sell_items:
            sell_items(
                manager,
                SellOption.GOODS,
                [
                    {"key": "tinh-dau-dua", "value": 6},
                    {"key": "tra-hoa-hong", "value": 3},
                ],
            )

        make_event(manager)

    print("The automation completed")


if __name__ == "__main__":
    main()
