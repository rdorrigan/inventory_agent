import json
from typing import Dict, Any, Optional

class InventoryRepository:
    def __init__(self, filepath: str = "data/mock_db.json"):
        self.filepath = filepath
        self._db = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback inline mock
            return {
                "SKU-101": {"stock": 12, "rop": 50, "unit_cost": 45.0, "eoq": 100},
                "SKU-303": {"stock": 5, "rop": 30, "unit_cost": 1200.0, "eoq": 20}
            }

    def get_sku_details(self, sku: str) -> Optional[Dict[str, Any]]:
        return self._db.get(sku.upper())