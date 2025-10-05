from enum import IntEnum

from libs.adb_controller import AdbController, KeyCode


class SellOption(IntEnum):
    """Market sell category options"""

    TREES = 0
    GOODS = 1
    OTHERS = 2
    MINERAL = 3
    EVENTS = 4


full_tree_point = [
    (720, 900),  # 1
    (890, 900),  # 2
    (1060, 900),  # 3
    (1230, 900),  # 4
    (1400, 900),  # 5
    (1570, 900),  # 6
    (1570, 400),  # 12
    (1400, 400),  # 11
    (1230, 400),  # 10
    (1060, 400),  # 9
    (890, 400),  # 8
    (720, 400),  # 7
]

full_item_point = [
    (880, 170),  # 1
    (1020, 170),  # 2
    (1160, 170),  # 3
    (1020, 320),  # 4
    (1160, 320),  # 5
]

sell_options = [
    (1040, 250),  # Trees
    (1040, 410),  # Goods
    (1040, 575),  # Others
    (1040, 740),  # Mineral
    (1040, 910),  # Events
]


def _close_all_popup(manager: AdbController, num=3):
    for _ in range(num):
        manager.press_key(KeyCode.BACK.value)
        manager.sleep(0.2)

    manager.click_image("o-lai")
    manager.sleep(0.5)


def open_game(manager: AdbController):
    """Open the game application"""
    print("Opening game...")
    game_package = "vn.kvtm.js"
    manager.press_key(KeyCode.HOME.value)
    manager.close_app(game_package)
    manager.open_app(game_package)
    manager.sleep(10)
    manager.click_image("game")
    manager.sleep(20)
    _close_all_popup(manager, 15)


def open_chest(manager: AdbController):
    """Open chests in the game"""
    isFound = manager.find_image_on_screen("ruong-bau")

    if isFound:
        print("Opening chests...")
        manager.tap(672, 240)
        manager.sleep(0.5)
        manager.tap(672, 240)
        manager.click_image("ruong-go")
        manager.click_image("mo-ngay")
        for _ in range(10):
            manager.tap(960, 672)
            manager.sleep(0.2)
        _close_all_popup(manager)
    manager.sleep(0.5)


def go_up(manager: AdbController, times=1):
    points = [960, 540, 960, 972]
    for _ in range(times):
        manager.swipe(*points, duration=100)
    manager.sleep(0.5)


def go_down(manager: AdbController, times=1):
    points = [960, 540, 960, 108]
    for _ in range(times):
        manager.swipe(*points, duration=100)
    manager.sleep(0.5)


def go_last(manager: AdbController):
    go_up(manager)
    manager.tap(970, 1055)
    manager.sleep(1)


def plant_tree(manager: AdbController, tree=None, num=12, next=True):
    manager.tap(*full_tree_point[0])
    manager.sleep(0.5)
    slot = (488, 844)
    if tree:
        slot = manager.find_image_on_screen(f"cay/{tree}")
        attempt = 5
        while not slot and attempt > 0:
            if next:
                manager.tap(775, 730)
            else:
                manager.tap(200, 730)
            manager.sleep(0.5)
            slot = manager.find_image_on_screen(f"cay/{tree}")
            attempt -= 1

    if not slot:
        raise LookupError("Image not found")

    points = [slot, *full_tree_point[:num]]
    manager.drag(points)
    manager.sleep(0.5)


def harvest_tree(manager: AdbController):
    manager.tap(*full_tree_point[0])
    manager.sleep(0.5)
    slot = manager.find_image_on_screen("thu-hoach")
    attempt = 3
    while not slot and attempt > 0:
        manager.tap(*full_tree_point[0])
        manager.sleep(0.5)
        slot = manager.find_image_on_screen("thu-hoach")
        attempt -= 1

    if not slot:
        raise LookupError("Image not found")

    points = [slot, *full_tree_point]
    manager.drag(points)
    manager.sleep(0.5)


def make_items(manager: AdbController, floor=1, slot=0, num=1):
    position = (420, 900) if floor == 1 else (420, 400)

    for _ in range(max(10, 2 * num)):
        manager.tap(*position)
        manager.sleep(0.2)

    attempt = 5
    while attempt > 0 and not manager.find_image_on_screen("o-trong-san-xuat"):
        manager.tap(*position)
        manager.sleep(0.2)
        attempt -= 1

    if attempt == 0:
        raise LookupError("Image not found")

    for _ in range(num):
        manager.drag([full_item_point[slot], (740, 450)])
        manager.sleep(0.2)

    # fix & close
    if floor == 1:
        manager.tap(190, 760)
    else:
        manager.tap(190, 270)
    manager.sleep(0.1)
    manager.tap(1512, 770)
    manager.sleep(0.1)
    _close_all_popup(manager)


def sell_items(manager: AdbController, option: SellOption, items):
    """
    Sell items in the game market

    Args:
        manager (AdbController): Device controller instance
        option (SellOption): Sell category (use SellOption enum):
            SellOption.TREES = 0
            SellOption.GOODS = 1
            SellOption.OTHERS = 2
            SellOption.MINERAL = 3
            SellOption.EVENTS = 4
        items (list): List of item dictionaries with format:
            [
                {"key": "vat-pham/nuoc-chanh", "value": 5},  # Sell 5 lemon juice
                {"key": "vat-pham/tinh-dau-chanh", "value": 3}  # Sell 3 lemon oil
            ]
            - "key": Image asset path (relative to assets directory)
            - "value": Quantity to sell (decremented as items are sold)

    Example:
        items_to_sell = [
            {"key": "vat-pham/nuoc-chanh", "value": 10},
            {"key": "vat-pham/tinh-dau-chanh", "value": 5}
        ]
        sell_items(manager, option=SellOption.GOODS, items=items_to_sell)

    Note:
        Uses _get_remain_item() to get next item with value > 0 and decrements count.
        Recursively calls itself if market slots are full to continue selling remaining items.
    """
    choose_type = sell_options[option]
    count = 0

    # open market
    manager.tap(1300, 760)
    manager.sleep(1)

    # back front market
    for _ in range(2):
        manager.swipe(310, 650, 1510, 650, 300)
        manager.sleep(0.5)

    # buy item
    item = _get_remain_item(items)
    while item:
        soldSlot = manager.find_image_on_screen("o-da-ban")
        if soldSlot:
            manager.tap(*soldSlot)
            manager.sleep(0.2)
            manager.tap(*soldSlot)
            manager.sleep(0.2)
            manager.tap(*choose_type)
            manager.sleep(0.5)

            manager.click_image(f"vat-pham/{item}")
            _sell(manager)
            item = _get_remain_item(items)
            continue
        emptySlot = manager.find_image_on_screen("o-trong-ban")
        if emptySlot:
            manager.tap(*emptySlot)
            manager.sleep(0.5)
            manager.tap(*choose_type)
            manager.sleep(0.5)

            manager.click_image(f"vat-pham/{item}")
            _sell(manager)
            item = _get_remain_item(items)
            continue

        # move next
        manager.swipe(1620, 648, 420, 648, 3000)
        manager.sleep(0.5)
        count += 1
        if count > 2:
            manager.tap(490, 396)
            manager.sleep(0.5)
            manager.tap(960, 1010)
            manager.sleep(0.5)
            manager.tap(1200, 85)
            manager.sleep(0.5)

            _close_all_popup(manager)
            _roll_back_item(items, item)
            # recurse for remain items
            return sell_items(manager, option, items)

    _close_all_popup(manager)


def _sell(manager: AdbController, setAds=True):
    manager.sleep(0.5)

    # increase price
    for _ in range(10):
        manager.tap(1584, 648)
        manager.sleep(0.01)

    manager.sleep(0.5)

    if not setAds:
        manager.tap(1416, 850)
        manager.sleep(0.5)
        # sell
        manager.tap(1416, 985)
        manager.sleep(0.5)
        manager.tap(1200, 85)
        manager.sleep(0.5)
    else:
        # sell
        manager.tap(1416, 985)
        manager.sleep(0.5)
        manager.tap(960, 1010)
        manager.sleep(0.5)
        manager.tap(1200, 85)
        manager.sleep(0.5)


def _get_remain_item(items):
    """Get next available item and decrement its count"""
    if isinstance(items, list):
        for item in items:
            if item.get("value", 0) > 0:
                item["value"] -= 1
                return item.get("key")
    return None


def _roll_back_item(items, key):
    """Increment item count back when rolling back"""
    if isinstance(items, list):
        for item in items:
            if item.get("key") == key:
                item["value"] += 1
                break
