import os

from models.script import Script


class ScriptManager:
    def __init__(self, script_dir, exclude_file=".ignore"):
        self.scripts = {}
        self.exclude_patterns = []

        # Resolve the path relative to the script's directory (src)
        if not os.path.isabs(script_dir):
            # Get the directory where this script is located (src)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to src directory, then find the scripts folder
            src_dir = os.path.dirname(current_dir)
            self.script_dir = os.path.join(src_dir, script_dir)
        else:
            self.script_dir = script_dir

        self.exclude_file = os.path.join(self.script_dir, exclude_file)
        self.load_exclude_patterns()
        self.load_scripts()

    def load_exclude_patterns(self):
        """Load exclude patterns from the exclude file"""
        if os.path.exists(self.exclude_file):
            with open(self.exclude_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.exclude_patterns.append(line)

    def is_excluded(self, filename):
        """Check if a file should be excluded based on patterns"""
        import fnmatch

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def load_scripts(self):
        """Load all scripts from the script directory"""
        for filename in os.listdir(self.script_dir):
            if filename.endswith(".py") and not self.is_excluded(filename):
                path = os.path.join(self.script_dir, filename)
                script = Script(path)
                self.scripts[script.id] = script

    def get_script(self, script_id):
        return self.scripts.get(script_id)

    def list_scripts(self):
        return sorted(self.scripts.values(), key=lambda s: s.path)
