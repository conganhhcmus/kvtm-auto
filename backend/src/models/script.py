import os
from datetime import datetime


class Script:
    def __init__(self, path):
        self.id = os.path.splitext(os.path.basename(path))[0]
        self.path = path
        self.name = self.id.replace("_", " ").title()
        self.created = datetime.fromtimestamp(os.path.getctime(path))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created.isoformat(),
            "path": self.path,
        }
