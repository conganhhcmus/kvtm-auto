class GameOptions:
    def __init__(self, open_game=False, open_chest=False, sell_items=False):
        self.open_game = open_game
        self.open_chest = open_chest
        self.sell_items = sell_items

    def to_dict(self):
        return {
            "open_game": self.open_game,
            "open_chest": self.open_chest,
            "sell_items": self.sell_items,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            open_game=data.get("open_game", False),
            open_chest=data.get("open_chest", False),
            sell_items=data.get("sell_items", False),
        )
