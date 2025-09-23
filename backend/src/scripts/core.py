from src.libs.adb_controller import AdbController


def open_game(manager: AdbController):
    """Open the game application"""
    print("Opening game...")
    manager.tap(500, 1000)


def open_chest(manager: AdbController):
    """Open chests in the game"""
    print("Opening chests...")
    manager.tap(600, 800)


def sell_items(manager: AdbController):
    """Sell items in the game"""
    print("Selling items...")
    manager.tap(400, 900)
