import asyncio
import flet as ft
from services.storage_service import StorageService
from services.http_service import HTTPService
from models.control import Control
from components.icon_picker import IconPicker
from components.color_picker import ColorPicker
from components.dialogs import show_snackbar
from utils.constants import HTTP_METHODS, CONTROL_TYPES
from utils.validation import is_valid_json

class EditorScreen(ft.Container):
    def __init__(self, page: ft.Page, storage: StorageService, control_to_edit: Control = None, on_saved=None, on_cancel=None):
        self.page_ref = page
        self.storage = storage
        self.control_to_edit = control_to_edit
        self.on_saved = on_saved
        self.on_cancel = on_cancel

        self.is_editing = control_to_edit is not None

        # State fields
        self.selected_icon = control_to_edit.icon if control_to_edit else "lightbulb"
        self.selected_color = control_to_edit.color if control_to_edit else "#2196F3"
        self.selected_device_id = control_to_edit.device_id if control_to_edit else ""
        self.selected_category_id = control_to_edit.category_id if control_to_edit else "all"

        # Form Controls
        self.name_field = ft.TextField(
            label="Control Name *",
            value=control_to_edit.name if control_to_edit else "",
            hint_text="e.g. Bedroom Light",
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.control_type_dropdown = ft.Dropdown(
            label="Control Type",
            value=control_to_edit.control_type if control_to_edit else Control.TYPE_ACTION,
            options=[ft.dropdown.Option(item["value"], item["label"]) for item in CONTROL_TYPES],
            density=ft.ThemeVisualDensity.COMPACT,
            on_change=self._on_type_change
        )

        self.device_dropdown = ft.Dropdown(
            label="Target Device",
            value=self.selected_device_id if self.selected_device_id else "custom",
            options=self._get_device_options(),
            density=ft.ThemeVisualDensity.COMPACT,
            on_change=self._on_device_change
        )

        self.custom_url_field = ft.TextField(
            label="Custom Base URL (Optional)",
            value=control_to_edit.custom_url if control_to_edit else "",
            hint_text="http://192.168.1.100:8080",
            density=ft.ThemeVisualDensity.COMPACT,
            visible=(self.selected_device_id == "" or self.selected_device_id == "custom")
        )

        self.on_endpoint_field = ft.TextField(
            label="ON / Action Endpoint *",
            value=control_to_edit.on_endpoint if control_to_edit else "/on",
            hint_text="/on or /relay/1/on",
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.off_endpoint_field = ft.TextField(
            label="OFF Endpoint",
            value=control_to_edit.off_endpoint if control_to_edit else "/off",
            hint_text="/off",
            density=ft.ThemeVisualDensity.COMPACT,
            visible=(self.control_type_dropdown.value == Control.TYPE_TOGGLE)
        )

        self.http_method_dropdown = ft.Dropdown(
            label="HTTP Method",
            value=control_to_edit.http_method if control_to_edit else "GET",
            options=[ft.dropdown.Option(m) for m in HTTP_METHODS],
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.category_dropdown = ft.Dropdown(
            label="Category",
            value=self.selected_category_id,
            options=[ft.dropdown.Option(c.id, c.name) for c in self.storage.get_categories()],
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.timeout_field = ft.TextField(
            label="Timeout (seconds)",
            value=str(control_to_edit.timeout) if control_to_edit else "5",
            keyboard_type=ft.KeyboardType.NUMBER,
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.headers_field = ft.TextField(
            label="Custom Headers (JSON format)",
            value=str(control_to_edit.custom_headers) if (control_to_edit and control_to_edit.custom_headers) else "",
            hint_text='{"Authorization": "Bearer token"}',
            multiline=True,
            min_lines=2,
            max_lines=3,
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.body_field = ft.TextField(
            label="Request Body (JSON / Text)",
            value=control_to_edit.request_body if control_to_edit else "",
            hint_text='{"state": "ON"}',
            multiline=True,
            min_lines=2,
            max_lines=3,
            density=ft.ThemeVisualDensity.COMPACT
        )

        self.confirm_switch = ft.Switch(
            label="Require Confirmation Before Executing",
            value=control_to_edit.requires_confirmation if control_to_edit else False
        )

        # Icon Preview Button
        self.icon_preview_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(self._get_icon_attribute(self.selected_icon), size=20),
                    ft.Text("Change Icon")
                ],
                spacing=8,
                tight=True
            ),
            on_click=self._open_icon_picker
        )

        # Test Endpoint UI
        self.test_loader = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
        self.test_result_text = ft.Text("", size=12, selectable=True)

        super().__init__(
            content=ft.ListView(
                controls=[
                    self._build_header(),
                    ft.Container(height=8),
                    self._build_section("Basic Information", [
                        self.name_field,
                        self.control_type_dropdown,
                        self.category_dropdown,
                        ft.Row(controls=[self.icon_preview_btn], alignment=ft.MainAxisAlignment.START),
                        ColorPicker(current_color=self.selected_color, on_change=self._on_color_change)
                    ]),
                    ft.Container(height=12),
                    self._build_section("Device & Endpoint", [
                        self.device_dropdown,
                        self.custom_url_field,
                        self.on_endpoint_field,
                        self.off_endpoint_field,
                        self.http_method_dropdown
                    ]),
                    ft.Container(height=12),
                    self._build_section("Advanced Settings", [
                        self.timeout_field,
                        self.headers_field,
                        self.body_field,
                        self.confirm_switch
                    ]),
                    ft.Container(height=12),
                    self._build_test_section(),
                    ft.Container(height=20),
                    self._build_action_buttons()
                ],
                spacing=8,
                padding=16
            ),
            expand=True
        )

    def _get_icon_attribute(self, icon_name: str):
        icon_upper = icon_name.upper()
        return getattr(ft.Icons, icon_upper, ft.Icons.LIGHTBULB)

    def _get_device_options(self):
        opts = [ft.dropdown.Option("custom", "Custom URL (No Device Preset)")]
        for d in self.storage.get_devices():
            opts.append(ft.dropdown.Option(d.id, f"{d.name} ({d.host})"))
        return opts

    def _on_device_change(self, e):
        val = e.control.value
        self.selected_device_id = "" if val == "custom" else val
        self.custom_url_field.visible = (val == "custom")
        self.update()

    def _on_type_change(self, e):
        self.off_endpoint_field.visible = (e.control.value == Control.TYPE_TOGGLE)
        self.update()

    def _on_color_change(self, hex_code: str):
        self.selected_color = hex_code

    def _open_icon_picker(self, e):
        def _set_icon(icon_key: str):
            self.selected_icon = icon_key
            self.icon_preview_btn.content.controls[0].name = self._get_icon_attribute(icon_key)
            self.update()

        picker = IconPicker(current_icon=self.selected_icon, on_select=_set_icon)
        self.page_ref.dialog = picker
        picker.open = True
        self.page_ref.update()

    def _build_header(self) -> ft.Control:
        title = "Edit Control" if self.is_editing else "Add Control"
        return ft.Row(
            controls=[
                ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.on_cancel() if self.on_cancel else None)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def _build_section(self, title: str, controls: list) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    *controls
                ],
                spacing=10
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    def _build_test_section(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Test Endpoint", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    ft.Text(
                        "Verify that your endpoint settings work with the device right now.",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Test Endpoint",
                                icon=ft.Icons.NETWORK_CHECK,
                                on_click=self._handle_test_endpoint
                            ),
                            self.test_loader
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    self.test_result_text
                ],
                spacing=10
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    def _handle_test_endpoint(self, e):
        asyncio.create_task(self._run_endpoint_test())

    async def _run_endpoint_test(self):
        if not self.on_endpoint_field.value.strip():
            self.test_result_text.value = "✕ Endpoint path cannot be empty."
            self.test_result_text.color = ft.Colors.RED
            self.update()
            return

        self.test_loader.visible = True
        self.test_result_text.value = "Testing endpoint..."
        self.test_result_text.color = ft.Colors.ON_SURFACE
        self.update()

        dev = self.storage.get_device(self.selected_device_id) if self.selected_device_id else None

        # Build temp control for URL resolution
        temp_control = Control(
            name=self.name_field.value,
            custom_url=self.custom_url_field.value,
            on_endpoint=self.on_endpoint_field.value,
            http_method=self.http_method_dropdown.value
        )
        url = temp_control.get_full_url(dev)

        res = await HTTPService.send_request(
            url=url,
            method=self.http_method_dropdown.value,
            body=self.body_field.value,
            timeout=int(self.timeout_field.value) if self.timeout_field.value.isdigit() else 5
        )

        self.test_loader.visible = False
        if res.success:
            self.test_result_text.value = f"✓ Request Successful (HTTP {res.status_code})\nResponse: {res.response_text or '(Empty)'}"
            self.test_result_text.color = ft.Colors.GREEN_600
        else:
            self.test_result_text.value = f"✕ Request Failed: {res.error_message}"
            self.test_result_text.color = ft.Colors.RED_600

        self.update()

    def _build_action_buttons(self) -> ft.Control:
        return ft.Row(
            controls=[
                ft.OutlinedButton(
                    "Cancel",
                    on_click=lambda e: self.on_cancel() if self.on_cancel else None,
                    expand=True
                ),
                ft.ElevatedButton(
                    "Save Control",
                    icon=ft.Icons.SAVE,
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=self._handle_save_control,
                    expand=True
                )
            ],
            spacing=12
        )

    def _handle_save_control(self, e):
        name = self.name_field.value.strip()
        if not name:
            show_snackbar(self.page_ref, "Control name is required.", is_error=True)
            return

        # Parse headers if present
        headers_dict = {}
        if self.headers_field.value.strip():
            if not is_valid_json(self.headers_field.value):
                show_snackbar(self.page_ref, "Headers must be valid JSON object.", is_error=True)
                return
            import json
            headers_dict = json.loads(self.headers_field.value)

        timeout_val = int(self.timeout_field.value) if self.timeout_field.value.isdigit() else 5

        ctrl_id = self.control_to_edit.id if self.is_editing else None
        existing_state = self.control_to_edit.state if self.is_editing else False

        control = Control(
            id=ctrl_id,
            name=name,
            icon=self.selected_icon,
            color=self.selected_color,
            control_type=self.control_type_dropdown.value,
            device_id=self.selected_device_id,
            custom_url=self.custom_url_field.value,
            on_endpoint=self.on_endpoint_field.value,
            off_endpoint=self.off_endpoint_field.value,
            http_method=self.http_method_dropdown.value,
            request_body=self.body_field.value,
            custom_headers=headers_dict,
            timeout=timeout_val,
            requires_confirmation=self.confirm_switch.value,
            category_id=self.category_dropdown.value,
            state=existing_state
        )

        if self.is_editing:
            self.storage.update_control(control)
            show_snackbar(self.page_ref, f"Updated '{name}'")
        else:
            self.storage.add_control(control)
            show_snackbar(self.page_ref, f"Created '{name}'")

        if self.on_saved:
            self.on_saved()
