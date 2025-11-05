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
    (0.38, 0.83),  # 1
    (0.46, 0.83),  # 2
    (0.55, 0.83),  # 3
    (0.64, 0.83),  # 4
    (0.73, 0.83),  # 5
    (0.82, 0.83),  # 6
    (0.82, 0.37),  # 12
    (0.73, 0.37),  # 11
    (0.64, 0.37),  # 10
    (0.55, 0.37),  # 9
    (0.46, 0.37),  # 8
    (0.38, 0.37),  # 7
]

full_item_point = [
    (0.46, 0.16),  # 1
    (0.53, 0.16),  # 2
    (0.60, 0.16),  # 3
    (0.53, 0.30),  # 4
    (0.60, 0.30),  # 5
]

sell_options = [
    (0.54, 0.23),  # Trees
    (0.54, 0.38),  # Goods
    (0.54, 0.53),  # Others
    (0.54, 0.69),  # Mineral
    (0.54, 0.84),  # Events
]

sell_slot_point = [
    (0.25, 0.37),  # slot 1
    (0.41, 0.37),  # slot 2
    (0.58, 0.37),  # slot 3
    (0.74, 0.37),  # slot 4
    (0.25, 0.76),  # slot 5
    (0.41, 0.76),  # slot 6
    (0.58, 0.76),  # slot 7
    (0.74, 0.76),  # slot 8
]

friend_house_point = [
    (0.75, 0.61),  # slot 1
    (0.22, 0.61),  # slot 2
    (0.38, 0.61),  # slot 3
    (0.53, 0.61),  # slot 4
    (0.68, 0.61),  # slot 5
]

loop_num = 1000


def _close_all_popup(manager: AdbController, num=3):
    for _ in range(num):
        manager.press_key(KeyCode.BACK.value)
        manager.sleep(0.25)

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
    manager.sleep(10)
    _close_all_popup(manager, 15)


def open_chest(manager: AdbController):
    """Open chests in the game"""
    isFound = manager.find_image_on_screen("ruong-bau")

    if isFound:
        print("Opening chests...")
        manager.tap(0.35, 0.22)
        manager.sleep(0.5)
        manager.tap(0.35, 0.22)
        manager.click_image("ruong-go")
        manager.click_image("mo-ngay")
        for _ in range(10):
            manager.tap(0.5, 0.62)
            manager.sleep(0.25)
        _close_all_popup(manager)
    manager.sleep(0.5)


def make_event(manager: AdbController):
    has_event = manager.click_image("event")
    if has_event:
        manager.sleep(2)
        for _ in range(5):
            manager.tap(0.17, 0.70)
            manager.sleep(1)

        points = [0.40, 0.26, 0.17, 0.62]
        for _ in range(3):
            manager.swipe(*points, duration=100)
            manager.sleep(1)

        _close_all_popup(manager)
        manager.sleep(1)
        _close_all_popup(manager)


def go_up(manager: AdbController, times=1):
    points = [0.5, 0.5, 0.5, 0.9]
    for _ in range(times):
        manager.swipe(*points, duration=100)
    manager.sleep(0.5)


def go_down(manager: AdbController, times=1):
    points = [0.5, 0.5, 0.5, 0.1]
    for _ in range(times):
        manager.swipe(*points, duration=100)
    manager.sleep(0.5)


def go_last(manager: AdbController):
    go_up(manager)
    manager.tap(0.51, 0.98)
    manager.sleep(1)


def plant_tree(manager: AdbController, tree=None, num=12, next=True):
    manager.tap(*full_tree_point[0])
    manager.sleep(0.5)
    slot = (0.25, 0.78)
    if tree:
        slot = manager.find_image_on_screen(f"cay/{tree}")
        attempt = 5
        while not slot and attempt > 0:
            if next:
                manager.tap(0.40, 0.68)
            else:
                manager.tap(0.10, 0.68)
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
    position = (0.22, 0.83) if floor == 1 else (0.22, 0.37)

    for _ in range(max(10, 2 * num)):
        manager.tap(*position)
        manager.sleep(0.25)

    attempt = 5
    while attempt > 0 and not manager.find_image_on_screen("o-trong-san-xuat"):
        manager.tap(*position)
        manager.sleep(0.25)
        attempt -= 1

    if attempt == 0:
        raise LookupError("Image not found")

    for _ in range(num):
        manager.drag([full_item_point[slot], (0.39, 0.42)])
        manager.sleep(0.25)

    # fix & close
    if floor == 1:
        manager.tap(0.10, 0.70)
    else:
        manager.tap(0.10, 0.25)
    manager.sleep(0.1)
    manager.tap(0.79, 0.71)
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
    manager.tap(0.68, 0.70)
    manager.sleep(1)

    # back front market
    for _ in range(2):
        manager.swipe(0.16, 0.60, 0.79, 0.60, 300)
        manager.sleep(0.5)

    # buy item
    item = _get_remain_item(items)
    while item:
        soldSlot = manager.find_image_on_screen("o-da-ban")
        if soldSlot:
            manager.tap(*soldSlot)
            manager.sleep(0.25)
            manager.tap(*soldSlot)
            manager.sleep(0.25)
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
        manager.swipe(0.84, 0.60, 0.22, 0.60, 3000)
        manager.sleep(0.5)
        count += 1
        if count > 2:
            manager.tap(0.26, 0.37)
            manager.sleep(0.5)
            manager.tap(0.50, 0.94)
            manager.sleep(0.5)
            manager.tap(0.63, 0.08)
            manager.sleep(0.5)

            _close_all_popup(manager)
            _roll_back_item(items, item)
            # recurse for remain items
            return sell_items(manager, option, items)

    _close_all_popup(manager)


def go_friend(manager: AdbController, slot=0):
    if manager.click_image("nha-ban"):
        manager.sleep(1)
        manager.tap(*friend_house_point[slot])
        manager.sleep(2)


def go_home(manager: AdbController):
    if manager.click_image("nha-minh"):
        manager.sleep(2)


def buy_8_slot(manager: AdbController):
    # open market
    manager.tap(0.68, 0.70)
    manager.sleep(1)

    for _ in range(2):
        for point in sell_slot_point:
            manager.tap(*point)
            manager.sleep(0.1)
            manager.tap(*point)
            manager.sleep(0.1)

    _close_all_popup(manager)


def _sell(manager: AdbController, setAds=True):
    manager.sleep(0.5)

    # increase price
    for _ in range(10):
        manager.tap(0.83, 0.60)
        manager.sleep(0.01)

    manager.sleep(0.5)

    if not setAds:
        manager.tap(0.74, 0.79)
        manager.sleep(0.5)
        # sell
        manager.tap(0.74, 0.91)
        manager.sleep(0.5)
        manager.tap(0.63, 0.08)
        manager.sleep(0.5)
    else:
        # sell
        manager.tap(0.74, 0.91)
        manager.sleep(0.5)
        manager.tap(0.50, 0.94)
        manager.sleep(0.5)
        manager.tap(0.63, 0.08)
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
