import json
import os
from typing import List, Optional
from models.device import Device
from models.control import Control
from models.category import Category
from models.app_config import AppConfig
from utils.constants import DEFAULT_CATEGORIES

STORAGE_FILE = "esp_control_hub_data.json"

class StorageService:
    def __init__(self, filepath: str = STORAGE_FILE):
        self.filepath = filepath
        self.config = AppConfig()
        self.devices: List[Device] = []
        self.categories: List[Category] = []
        self.controls: List[Control] = []
        self.load()

    def load(self):
        """Loads data from local JSON storage file."""
        if not os.path.exists(self.filepath):
            self._create_defaults()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.config = AppConfig.from_dict(data.get("config", {}))

            self.devices = [Device.from_dict(d) for d in data.get("devices", [])]

            categories_data = data.get("categories", [])
            if not categories_data:
                self.categories = [Category.from_dict(c) for c in DEFAULT_CATEGORIES]
            else:
                self.categories = [Category.from_dict(c) for c in categories_data]

            self.controls = [Control.from_dict(c) for c in data.get("controls", [])]

            # If brand new setup with empty controls, seed a default demo device & control if desired
            if not self.devices and not self.controls and not os.path.exists(self.filepath):
                self._create_defaults()

        except Exception as e:
            print(f"Error loading storage: {e}")
            self._create_defaults()

    def save(self):
        """Saves data to local JSON storage file."""
        data = {
            "version": 1,
            "config": self.config.to_dict(),
            "devices": [d.to_dict() for d in self.devices],
            "categories": [c.to_dict() for c in self.categories],
            "controls": [c.to_dict() for c in self.controls]
        }
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving storage: {e}")

    def _create_defaults(self):
        self.config = AppConfig()
        self.categories = [Category.from_dict(c) for c in DEFAULT_CATEGORIES]
        self.devices = []
        self.controls = []
        self.save()

    # --- Config ---
    def update_config(self, config: AppConfig):
        self.config = config
        self.save()

    # --- Devices ---
    def get_devices(self) -> List[Device]:
        return self.devices

    def get_device(self, device_id: str) -> Optional[Device]:
        for d in self.devices:
            if d.id == device_id:
                return d
        return None

    def add_device(self, device: Device):
        self.devices.append(device)
        self.save()

    def update_device(self, device: Device):
        for i, d in enumerate(self.devices):
            if d.id == device.id:
                self.devices[i] = device
                break
        self.save()

    def delete_device(self, device_id: str):
        self.devices = [d for d in self.devices if d.id != device_id]
        # Clear device_id on controls referencing this device
        for ctrl in self.controls:
            if ctrl.device_id == device_id:
                ctrl.device_id = ""
        self.save()

    # --- Categories ---
    def get_categories(self) -> List[Category]:
        return sorted(self.categories, key=lambda c: c.order)

    def get_category(self, cat_id: str) -> Optional[Category]:
        for c in self.categories:
            if c.id == cat_id:
                return c
        return None

    def add_category(self, category: Category):
        self.categories.append(category)
        self.save()

    def update_category(self, category: Category):
        for i, c in enumerate(self.categories):
            if c.id == category.id:
                self.categories[i] = category
                break
        self.save()

    def delete_category(self, category_id: str):
        if category_id == "all":
            return  # Prevent deleting "All"
        self.categories = [c for c in self.categories if c.id != category_id]
        # Move controls in this category to "all"
        for ctrl in self.controls:
            if ctrl.category_id == category_id:
                ctrl.category_id = "all"
        self.save()

    # --- Controls ---
    def get_controls(self, category_id: Optional[str] = None, search_query: Optional[str] = None) -> List[Control]:
        res = self.controls
        if category_id and category_id != "all":
            res = [c for c in res if c.category_id == category_id]

        if search_query and search_query.strip():
            q = search_query.strip().lower()
            filtered = []
            for c in res:
                dev = self.get_device(c.device_id)
                dev_name = dev.name.lower() if dev else ""
                cat = self.get_category(c.category_id)
                cat_name = cat.name.lower() if cat else ""

                if (q in c.name.lower() or
                    q in dev_name or
                    q in cat_name):
                    filtered.append(c)
            res = filtered

        return sorted(res, key=lambda c: c.order)

    def get_control(self, control_id: str) -> Optional[Control]:
        for c in self.controls:
            if c.id == control_id:
                return c
        return None

    def add_control(self, control: Control):
        self.controls.append(control)
        self.save()

    def update_control(self, control: Control):
        for i, c in enumerate(self.controls):
            if c.id == control.id:
                self.controls[i] = control
                break
        self.save()

    def delete_control(self, control_id: str):
        self.controls = [c for c in self.controls if c.id != control_id]
        self.save()

    def reorder_controls(self, control_ids: List[str]):
        id_to_order = {cid: idx for idx, cid in enumerate(control_ids)}
        for c in self.controls:
            if c.id in id_to_order:
                c.order = id_to_order[c.id]
        self.save()

    def reset_all(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        self._create_defaults()
