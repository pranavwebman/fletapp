import unittest
import os
import json
import asyncio
from models.device import Device
from models.control import Control
from models.category import Category
from models.app_config import AppConfig
from utils.validation import is_valid_host, is_valid_port, validate_config_json
from services.storage_service import StorageService
from services.import_export_service import ImportExportService
from services.http_service import HTTPService

TEST_DB_FILE = "test_esp_hub.json"

class TestESPControlHub(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        self.storage = StorageService(filepath=TEST_DB_FILE)

    def tearDown(self):
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)

    def test_device_model_and_url(self):
        dev = Device(name="Test ESP32", host="192.168.1.50", port=8080)
        self.assertEqual(dev.base_url, "http://192.168.1.50:8080")

        dev_dict = dev.to_dict()
        dev_restored = Device.from_dict(dev_dict)
        self.assertEqual(dev_restored.name, "Test ESP32")
        self.assertEqual(dev_restored.host, "192.168.1.50")
        self.assertEqual(dev_restored.port, 8080)

    def test_control_url_resolution(self):
        dev = Device(name="Test ESP32", host="192.168.1.50", port=80)
        ctrl = Control(name="Fan", device_id=dev.id, on_endpoint="/fan/on", off_endpoint="/fan/off")

        url_on = ctrl.get_full_url(dev, is_off=False)
        url_off = ctrl.get_full_url(dev, is_off=True)

        self.assertEqual(url_on, "http://192.168.1.50/fan/on")
        self.assertEqual(url_off, "http://192.168.1.50/fan/off")

    def test_custom_url_resolution(self):
        ctrl = Control(name="Custom Light", custom_url="http://10.0.0.15:3000", on_endpoint="/turn_on")
        url = ctrl.get_full_url(None)
        self.assertEqual(url, "http://10.0.0.15:3000/turn_on")

    def test_validation_utilities(self):
        self.assertTrue(is_valid_host("192.168.1.1"))
        self.assertTrue(is_valid_host("esp32.local"))
        self.assertFalse(is_valid_host("999.999.999.999"))
        self.assertTrue(is_valid_port(80))
        self.assertFalse(is_valid_port(70000))

        valid_cfg, _ = validate_config_json({"devices": [], "controls": []})
        self.assertTrue(valid_cfg)
        invalid_cfg, _ = validate_config_json("not a dict")
        self.assertFalse(invalid_cfg)

    def test_storage_service_crud(self):
        dev = Device(name="Bedroom ESP", host="192.168.1.10")
        self.storage.add_device(dev)
        self.assertEqual(len(self.storage.get_devices()), 1)

        ctrl = Control(name="Relay Switch", device_id=dev.id)
        self.storage.add_control(ctrl)
        self.assertEqual(len(self.storage.get_controls()), 1)

        # Search query check
        self.assertEqual(len(self.storage.get_controls(search_query="Relay")), 1)
        self.assertEqual(len(self.storage.get_controls(search_query="NonExistent")), 0)

        # Deleting device clears reference on control
        self.storage.delete_device(dev.id)
        fetched_ctrl = self.storage.get_control(ctrl.id)
        self.assertEqual(fetched_ctrl.device_id, "")

    def test_import_export_service(self):
        dev = Device(name="Workshop ESP", host="192.168.1.25")
        ctrl = Control(name="Bench Light", device_id=dev.id)
        self.storage.add_device(dev)
        self.storage.add_control(ctrl)

        exported_json = ImportExportService.export_config(self.storage)
        self.assertIn("Workshop ESP", exported_json)
        self.assertIn("Bench Light", exported_json)

        # Create new storage instance and import
        new_db_file = "test_esp_hub_import.json"
        if os.path.exists(new_db_file):
            os.remove(new_db_file)

        new_storage = StorageService(filepath=new_db_file)
        success, msg = ImportExportService.import_config(exported_json, new_storage)
        self.assertTrue(success)
        self.assertEqual(len(new_storage.get_devices()), 1)
        self.assertEqual(new_storage.get_devices()[0].name, "Workshop ESP")

        if os.path.exists(new_db_file):
            os.remove(new_db_file)

    def test_http_service_unreachable(self):
        async def run_test():
            # Test timeout / connection failure handling to invalid IP
            res = await HTTPService.send_request("http://192.0.2.1:12345/test", timeout=1)
            self.assertFalse(res.success)
            self.assertIn("Could not reach", res.error_message)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
