import json
from typing import Tuple, Dict, Any
from services.storage_service import StorageService
from models.device import Device
from models.control import Control
from models.category import Category
from models.app_config import AppConfig
from utils.validation import validate_config_json

class ImportExportService:
    @staticmethod
    def export_config(storage: StorageService) -> str:
        """Exports the full application state into a formatted JSON string."""
        data = {
            "version": 1,
            "config": storage.config.to_dict(),
            "devices": [d.to_dict() for d in storage.get_devices()],
            "categories": [c.to_dict() for c in storage.get_categories()],
            "controls": [c.to_dict() for c in storage.get_controls()]
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def import_config(json_str: str, storage: StorageService) -> Tuple[bool, str]:
        """Validates and imports configuration JSON into the storage service."""
        if not json_str or not json_str.strip():
            return False, "Import content is empty."

        try:
            data = json.loads(json_str)
        except Exception as e:
            return False, f"Invalid JSON format: {str(e)}"

        valid, msg = validate_config_json(data)
        if not valid:
            return False, msg

        try:
            if "config" in data and isinstance(data["config"], dict):
                storage.config = AppConfig.from_dict(data["config"])

            if "devices" in data:
                storage.devices = [Device.from_dict(d) for d in data["devices"]]

            if "categories" in data and data["categories"]:
                storage.categories = [Category.from_dict(c) for c in data["categories"]]

            if "controls" in data:
                storage.controls = [Control.from_dict(c) for c in data["controls"]]

            storage.save()
            return True, "Configuration imported successfully!"
        except Exception as e:
            return False, f"Failed to apply configuration: {str(e)}"
