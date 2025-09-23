from libs.adb_controller import AdbController, KeyCode


def _close_all_popup(manager: AdbController):
    for _ in range(10):
        manager.press_key(KeyCode.BACK.value)
        manager.sleep(0.2)

    manager.click_image("o-lai.png")


def open_game(manager: AdbController):
    """Open the game application"""
    print("Opening game...")
    game_package = "vn.kvtm.js"
    manager.press_key(KeyCode.HOME.value)
    manager.close_app(game_package)
    manager.open_app(game_package)
    manager.sleep(10)
    manager.click_image("game.png")
    manager.sleep(15)
    _close_all_popup(manager)


def open_chest(manager: AdbController):
    """Open chests in the game"""
    print("Opening chests...")
    isFound = manager.find_image_on_screen("ruong-bau.png")

    if isFound:
        manager.tap_by_percent(35.0, 22.22)
        manager.sleep(0.5)
        manager.tap_by_percent(35.0, 22.22)
        manager.click_image("ruong-go.png")
        manager.click_image("mo-ngay.png")
        for _ in range(10):
            manager.tap_by_percent(50.0, 62.22)
            manager.sleep(0.2)
        _close_all_popup(manager)


def sell_items(manager: AdbController):
    """Sell items in the game"""
    print("Selling items...")
    # 1920x1080
    points = [(950, 100), (950, 900)]
    manager.drag(points, steps=10)
    manager.sleep(1)
    points = [(950, 900), (950, 100)]
    manager.drag(points, steps=10)
