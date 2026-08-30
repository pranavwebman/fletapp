import flet as ft
from services.storage_service import StorageService
from models.device import Device
from components.dialogs import show_confirm_dialog, show_snackbar
from utils.validation import is_valid_host, is_valid_port

class DevicesScreen(ft.Container):
    def __init__(self, page: ft.Page, storage: StorageService):
        self.page_ref = page
        self.storage = storage

        # List view for devices
        self.devices_list = ft.ListView(spacing=10, expand=True)

        # Empty State
        self.empty_state = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ROUTER, size=64, color=ft.Colors.OUTLINE),
                    ft.Text("No ESP devices configured", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Add your ESP32, ESP8266, or other HTTP microcontrollers to control them.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Add Device",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: self._open_device_dialog()
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            padding=30,
            alignment=ft.Alignment.CENTER,
            visible=False
        )

        super().__init__(
            content=ft.Column(
                controls=[
                    self._build_header(),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    self.devices_list,
                    self.empty_state
                ],
                spacing=12
            ),
            padding=16,
            expand=True
        )

        self.refresh_devices()

    def _build_header(self) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("ESP Devices", size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Manage your microcontrollers", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
                    ],
                    spacing=2
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    mini=True,
                    tooltip="Add Device",
                    on_click=lambda e: self._open_device_dialog()
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def refresh_devices(self):
        devices = self.storage.get_devices()
        self.devices_list.controls.clear()

        if not devices:
            self.devices_list.visible = False
            self.empty_state.visible = True
        else:
            self.devices_list.visible = True
            self.empty_state.visible = False

            for dev in devices:
                card = self._build_device_card(dev)
                self.devices_list.controls.append(card)

        try:
            self.update()
        except Exception:
            pass

    def _build_device_card(self, device: Device) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.MEMORY, size=24, color=ft.Colors.PRIMARY),
                                width=40, height=40, border_radius=20,
                                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                                alignment=ft.Alignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(device.name, weight=ft.FontWeight.BOLD, size=15),
                                    ft.Text(
                                        f"{device.host}:{device.port}" if device.port != 80 else device.host,
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ],
                                spacing=2,
                                expand=True
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.EDIT_OUTLINED,
                                        icon_size=18,
                                        tooltip="Edit Device",
                                        on_click=lambda e, d=device: self._open_device_dialog(d)
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINED,
                                        icon_size=18,
                                        icon_color=ft.Colors.RED,
                                        tooltip="Delete Device",
                                        on_click=lambda e, d=device: self._handle_delete_device(d)
                                    )
                                ],
                                spacing=0
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Text(device.description, size=12, italic=True) if device.description else ft.Container()
                ],
                spacing=6
            ),
            padding=12,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    def _open_device_dialog(self, device: Device = None):
        is_edit = device is not None

        name_field = ft.TextField(
            label="Device Name *",
            value=device.name if device else "",
            hint_text="e.g. Living Room ESP32"
        )

        host_field = ft.TextField(
            label="Host / IP Address *",
            value=device.host if device else "",
            hint_text="192.168.1.42 or esp32.local"
        )

        port_field = ft.TextField(
            label="Port",
            value=str(device.port) if device else "80",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        desc_field = ft.TextField(
            label="Description",
            value=device.description if device else "",
            hint_text="e.g. Controls ceiling fan and main light"
        )

        def _save_device(e):
            name = name_field.value.strip()
            host = host_field.value.strip()
            port = port_field.value.strip()

            if not name:
                show_snackbar(self.page_ref, "Device name is required.", is_error=True)
                return

            if not is_valid_host(host):
                show_snackbar(self.page_ref, "Please enter a valid Host/IP address.", is_error=True)
                return

            if not is_valid_port(port):
                show_snackbar(self.page_ref, "Port must be between 1 and 65535.", is_error=True)
                return

            dev_id = device.id if is_edit else None
            dev_obj = Device(
                id=dev_id,
                name=name,
                host=host,
                port=int(port),
                description=desc_field.value.strip()
            )

            if is_edit:
                self.storage.update_device(dev_obj)
                show_snackbar(self.page_ref, f"Updated '{name}'")
            else:
                self.storage.add_device(dev_obj)
                show_snackbar(self.page_ref, f"Added '{name}'")

            dialog.open = False
            self.page_ref.update()
            self.refresh_devices()

        def _cancel(e):
            dialog.open = False
            self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Device" if is_edit else "Add Device", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[name_field, host_field, port_field, desc_field],
                    tight=True,
                    spacing=10
                ),
                width=300
            ),
            actions=[
                ft.TextButton("Cancel", on_click=_cancel),
                ft.ElevatedButton(
                    "Save",
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=_save_device
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page_ref.dialog = dialog
        dialog.open = True
        self.page_ref.update()

    def _handle_delete_device(self, device: Device):
        show_confirm_dialog(
            self.page_ref,
            title=f"Delete '{device.name}'?",
            message="Controls linked to this device will fall back to custom URLs.",
            confirm_label="Delete",
            confirm_color=ft.Colors.RED,
            on_confirm=lambda: self._do_delete_device(device.id)
        )

    def _do_delete_device(self, device_id: str):
        self.storage.delete_device(device_id)
        show_snackbar(self.page_ref, "Device deleted.")
        self.refresh_devices()
