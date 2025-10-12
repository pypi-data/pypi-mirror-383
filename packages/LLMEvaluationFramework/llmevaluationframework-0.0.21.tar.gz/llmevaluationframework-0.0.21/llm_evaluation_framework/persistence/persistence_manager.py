import json
import os
from typing import Any, Dict, Optional


class PersistenceManager:
    """Handles saving and loading data to/from JSON files."""

    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save(self, filename: str, data: Dict[str, Any]) -> None:
        """Save data to a JSON file."""
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from a JSON file."""
        filepath = os.path.join(self.storage_dir, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, filename: str) -> None:
        """Delete a JSON file."""
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
