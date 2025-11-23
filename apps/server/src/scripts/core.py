from enum import IntEnum
from random import randint

from libs.adb_controller import AdbController, KeyCode


class SellOption(IntEnum):
    """Market sell category options"""

    TREES = 0
    GOODS = 1
    OTHERS = 2
    MINERAL = 3
    EVENTS = 4


full_tree_point = [
    # floor 1
    (850, 1730),  # 1
    (1015, 1730),  # 2
    (1180, 1730),  # 3
    (1345, 1730),  # 4
    (1510, 1730),  # 5
    (1675, 1730),  # 6
    # floor 2
    (1675, 1245),  # 12
    (1510, 1245),  # 11
    (1345, 1245),  # 10
    (1180, 1245),  # 9
    (1015, 1245),  # 8
    (850, 1245),  # 7
    # floor 3
    (850, 770),  # 13
    (1015, 770),  # 14
    (1180, 770),  # 15
    (1345, 770),  # 16
    (1510, 770),  # 17
    (1675, 770),  # 18
    # floor 4
    (1675, 290),  # 24
    (1510, 290),  # 23
    (1345, 290),  # 22
    (1180, 290),  # 21
    (1015, 290),  # 20
    (850, 290),  # 19
]

full_item_point = [
    (1000, 1000),  # 1
    (1140, 1000),  # 2
    (1280, 1000),  # 3
    (1140, 1150),  # 4
    (1280, 1150),  # 5
]

sell_options = [
    (975, 650),  # Trees
    (975, 800),  # Goods
    (975, 950),  # Others
    (975, 1100),  # Mineral
    (975, 1250),  # Events
]

sell_slot_point = [
    (630, 790),  # slot 1
    (920, 790),  # slot 2
    (1210, 790),  # slot 3
    (1500, 790),  # slot 4
    (630, 1210),  # slot 5
    (920, 1210),  # slot 6
    (1210, 1210),  # slot 7
    (1500, 1210),  # slot 8
]

friend_house_point = [
    (590, 1470),  # slot 1
    (860, 1470),  # slot 2
    (1130, 1470),  # slot 3
    (1400, 1470),  # slot 4
    (1670, 1470),  # slot 5
]

loop_num = 1000


def _close_all_popup(manager: AdbController, num=3):
    for _ in range(num):
        manager.press_key(KeyCode.BACK.value)
        manager.sleep(0.25)

    manager.tap(1240, 1150)
    manager.sleep(0.5)


def open_game(manager: AdbController):
    """Open the game application"""
    print("Opening game...")
    game_package = "vn.kvtm.js"
    manager.press_key(KeyCode.HOME.value)
    manager.close_app(game_package)
    manager.open_app(game_package)
    manager.sleep(10)
    manager.tap(1600, 2020)
    manager.sleep(1)
    manager.click_image("game")
    manager.sleep(10)
    _close_all_popup(manager, 15)


def open_chest(manager: AdbController):
    """Open chests in the game"""
    isFound = manager.find_image_on_screen("ruong-bau")

    if isFound:
        print("Opening chests...")
        manager.tap(810, 1040)
        manager.sleep(0.5)
        manager.tap(810, 1040)
        manager.tap(570, 1240)
        manager.tap(570, 1240)
        manager.sleep(0.5)
        manager.tap(1075, 1050)
        manager.tap(1075, 1050)
        for _ in range(10):
            manager.tap(1080, 1050)
            manager.sleep(0.25)
        _close_all_popup(manager)
    manager.sleep(0.5)


def make_event(manager: AdbController):
    has_event = manager.click_image("event")
    if has_event:
        manager.sleep(2)
        for _ in range(5):
            manager.tap(550, 1100)
            manager.sleep(1)

        points = [870, 690, 500, 1100]
        for _ in range(3):
            manager.swipe(*points, duration=100)
            manager.sleep(1)

        _close_all_popup(manager)
        manager.sleep(1)
        _close_all_popup(manager)


def go_up(manager: AdbController, times=1):
    points = [1160, 1050, 1160, 1700]
    for _ in range(times):
        manager.swipe(*points, duration=100)
        manager.sleep(0.1)
    manager.sleep(0.5)


def go_down(manager: AdbController, times=1):
    points = [1160, 1050, 1160, 400]
    for _ in range(times):
        manager.swipe(*points, duration=100)
        manager.sleep(0.1)
    manager.sleep(0.5)


def go_last(manager: AdbController):
    go_up(manager)
    manager.tap(0.51, 0.98)
    manager.sleep(1)


def plant_tree(manager: AdbController, tree=None, num=24, next=True):
    manager.tap(*full_tree_point[0])
    manager.sleep(0.5)
    slot = (640, 1640)
    if tree:
        slot = manager.find_image_on_screen(f"cay/{tree}")
        attempt = 5
        while not slot and attempt > 0:
            if next:
                manager.tap(905, 1530)
            else:
                manager.tap(360, 1530)
            manager.sleep(0.5)
            slot = manager.find_image_on_screen(f"cay/{tree}")
            attempt -= 1

    if not slot:
        raise LookupError("Image not found")

    points = [slot, *full_tree_point[:num]]
    manager.drag(points)
    manager.sleep(0.5)


def harvest_tree(manager: AdbController, num=24):
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

    points = [slot, *full_tree_point[:num]]
    manager.drag(points)
    manager.sleep(0.5)


def make_items(manager: AdbController, floor=1, slot=0, num=1):
    position = (560, 1700) if floor == 1 else (560, 1220)

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
        manager.drag([full_item_point[slot], (860, 1260)])
        manager.sleep(0.25)

    # fix & close
    if floor == 1:
        manager.tap(360, 1550)
    else:
        manager.tap(360, 1090)
    manager.sleep(0.1)
    manager.tap(1600, 1140)
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
    manager.tap(1375, 1530)
    manager.sleep(1)

    # back front market
    for _ in range(2):
        manager.swipe(500, 1000, 1650, 1000, 300)
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
        manager.swipe(1650, 1000, 500, 1000, 3000)
        manager.sleep(0.5)
        count += 1
        if count > 2:
            manager.tap(*sell_slot_point[randint(0, 3)])
            manager.sleep(0.5)
            manager.tap(1080, 1360)
            manager.sleep(0.5)
            manager.tap(1310, 500)
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
    manager.tap(1375, 1530)
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
        manager.tap(1835, 1020)
        manager.sleep(0.01)

    manager.sleep(0.5)

    if not setAds:
        manager.tap(1685, 1220)
        manager.sleep(0.5)
        # sell
        manager.tap(1685, 1330)
        manager.sleep(0.5)
        manager.tap(1310, 500)
        manager.sleep(0.5)
    else:
        # sell
        manager.tap(1685, 1330)
        manager.sleep(0.5)
        manager.tap(1080, 1360)
        manager.sleep(0.5)
        manager.tap(1310, 500)
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
