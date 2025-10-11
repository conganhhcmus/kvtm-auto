import os
import re
from datetime import datetime


class Script:
    def __init__(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        # Strip number prefix pattern (e.g., "01.", "99.")
        self.id = re.sub(r"^\d+\.", "", filename)
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
