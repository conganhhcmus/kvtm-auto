"""
Script discovery and management system for KVTM Auto
Scans the scripts directory and extracts metadata from script files
"""

import importlib.util
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from ..models import Script


class ScriptManager:
    """Manages script discovery and metadata extraction"""

    def __init__(self, scripts_dir: Optional[Path] = None):
        """
        Initialize ScriptManager

        Args:
            scripts_dir: Path to scripts directory (defaults to backend/scripts)
        """
        if scripts_dir is None:
            # Default to backend/scripts relative to this file
            current_dir = Path(__file__).parent
            backend_dir = current_dir.parent.parent
            scripts_dir = backend_dir / "scripts"

        self.scripts_dir = scripts_dir

    def discover_scripts(self) -> List[Script]:
        """
        Discover all scripts in the scripts directory by scanning .py files

        Returns:
            List of Script objects with metadata
        """
        if not self.scripts_dir.exists():
            logger.warning(f"Scripts directory not found: {self.scripts_dir}")
            return []

        scripts = []

        # Scan all .py files in scripts directory
        for script_file in self.scripts_dir.glob("*.py"):
            if script_file.name.startswith("_") or script_file.name.startswith("__"):
                continue  # Skip _core.py, __init__.py and similar files

            try:
                script_meta = self._extract_script_metadata(script_file)
                if script_meta:
                    script = Script(**script_meta)
                    scripts.append(script)
                    logger.debug(f"Discovered script: {script.id}")
            except Exception as e:
                logger.error(f"Failed to process script {script_file.name}: {e}")
                continue

        # Sort by order field
        scripts.sort(key=lambda x: x.order)

        logger.info(f"Discovered {len(scripts)} scripts from {self.scripts_dir}")
        return scripts

    def get_script_by_id(self, script_id: str) -> Optional[Script]:
        """
        Get a specific script by ID

        Args:
            script_id: Script ID to search for

        Returns:
            Script object if found, None otherwise
        """
        scripts = self.discover_scripts()
        for script in scripts:
            if script.id == script_id:
                return script
        return None

    def get_script_path(self, script_id: str) -> Optional[Path]:
        """
        Get the file path for a script by ID

        Args:
            script_id: Script ID

        Returns:
            Path to script file if found, None otherwise
        """
        script_file = self.scripts_dir / f"{script_id}.py"
        return script_file if script_file.exists() else None

    def validate_script_structure(self, script_file: Path) -> Dict[str, Any]:
        """
        Validate that a script has the required structure (main function, etc.)

        Args:
            script_file: Path to the script file

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": False,
            "has_main_function": False,
            "has_script_meta": False,
            "errors": [],
        }

        try:
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for main function
            if re.search(r"def\s+main\s*\(", content):
                validation_result["has_main_function"] = True
            else:
                validation_result["errors"].append("Missing main() function")

            # Check for SCRIPT_META
            if "SCRIPT_META" in content:
                validation_result["has_script_meta"] = True
            else:
                validation_result["errors"].append("Missing SCRIPT_META")

            # Overall validity
            validation_result["valid"] = (
                validation_result["has_main_function"]
                and len(validation_result["errors"]) == 0
            )

        except Exception as e:
            validation_result["errors"].append(f"Failed to read file: {e}")

        return validation_result

    def _extract_script_metadata(self, script_file: Path) -> Optional[Dict[str, Any]]:
        """
        Extract SCRIPT_META dictionary from a script file

        Args:
            script_file: Path to the script file

        Returns:
            Dictionary with script metadata or None if not found/invalid
        """
        try:
            # Read file content
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Method 1: Try to extract SCRIPT_META using regex
            script_meta = self._extract_meta_with_regex(content)

            if script_meta:
                return self._normalize_script_meta(script_meta, script_file)

            # Method 2: If regex fails, try to import and get SCRIPT_META
            script_meta = self._extract_meta_with_import(script_file)

            if script_meta:
                return self._normalize_script_meta(script_meta, script_file)

            # Method 3: If no SCRIPT_META found, create basic metadata
            logger.warning(
                f"No SCRIPT_META found in {script_file.name}, creating basic metadata"
            )
            return {
                "id": script_file.stem,
                "name": script_file.stem.replace("_", " ").title(),
                "description": f"Script: {script_file.name}",
                "order": 999,
                "recommend": False,
            }

        except Exception as e:
            logger.error(f"Failed to extract metadata from {script_file}: {e}")
            return None

    def _normalize_script_meta(
        self, script_meta: Dict[str, Any], script_file: Path
    ) -> Dict[str, Any]:
        """Normalize script metadata with default values"""
        # Use filename as ID if not specified
        if "id" not in script_meta or not script_meta["id"]:
            script_meta["id"] = script_file.stem

        # Set default values
        script_meta.setdefault("name", script_file.stem.replace("_", " ").title())
        script_meta.setdefault("description", "")
        script_meta.setdefault("order", 999)
        script_meta.setdefault("recommend", False)

        return script_meta

    def _extract_meta_with_regex(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract SCRIPT_META using regex pattern matching

        Args:
            content: File content as string

        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            # Pattern to match SCRIPT_META = { ... }
            pattern = r"SCRIPT_META\s*=\s*\{([^}]*)\}"
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                return None

            meta_content = match.group(1)
            meta_dict = {}

            # Extract key-value pairs
            # Pattern for "key": "value" or "key": value
            kv_pattern = r'["\'](\w+)["\']\s*:\s*([^,\n]+)'

            for kv_match in re.finditer(kv_pattern, meta_content):
                key = kv_match.group(1)
                value_str = kv_match.group(2).strip()

                # Parse value
                if value_str.startswith('"') and value_str.endswith('"'):
                    value = value_str[1:-1]  # String value
                elif value_str.startswith("'") and value_str.endswith("'"):
                    value = value_str[1:-1]  # String value
                elif value_str.lower() == "true":
                    value = True
                elif value_str.lower() == "false":
                    value = False
                elif value_str.isdigit():
                    value = int(value_str)
                else:
                    value = value_str.strip("\"'")  # Default to string

                meta_dict[key] = value

            return meta_dict if meta_dict else None

        except Exception as e:
            logger.debug(f"Regex extraction failed: {e}")
            return None

    def _extract_meta_with_import(self, script_file: Path) -> Optional[Dict[str, Any]]:
        """
        Extract SCRIPT_META by importing the module

        Args:
            script_file: Path to the script file

        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            # Create module spec
            spec = importlib.util.spec_from_file_location("temp_script", script_file)
            if spec is None or spec.loader is None:
                return None

            # Create and load module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get SCRIPT_META
            if hasattr(module, "SCRIPT_META"):
                script_meta = module.SCRIPT_META
                if isinstance(script_meta, dict):
                    return script_meta

            return None

        except Exception as e:
            logger.debug(f"Import extraction failed for {script_file}: {e}")
            return None


# Global script manager instance
script_manager = ScriptManager()
