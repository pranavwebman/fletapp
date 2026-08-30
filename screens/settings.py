import json
import flet as ft
from services.storage_service import StorageService
from services.import_export_service import ImportExportService
from models.app_config import AppConfig
from components.dialogs import show_confirm_dialog, show_snackbar
from utils.constants import APP_NAME, APP_VERSION

class SettingsScreen(ft.Container):
    def __init__(self, page: ft.Page, storage: StorageService, on_theme_change=None):
        self.page_ref = page
        self.storage = storage
        self.on_theme_change = on_theme_change

        # User Name Input
        self.user_name_field = ft.TextField(
            label="Your Name",
            value=self.storage.config.user_name,
            on_change=self._on_user_name_change
        )

        # Theme Selector Radio Group
        self.theme_radio_group = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    ft.Radio(value=AppConfig.THEME_LIGHT, label="Light"),
                    ft.Radio(value=AppConfig.THEME_DARK, label="Dark"),
                    ft.Radio(value=AppConfig.THEME_SYSTEM, label="System")
                ],
                spacing=12
            ),
            value=self.storage.config.theme_mode,
            on_change=self._on_theme_radio_change
        )

        # Confirm Switch
        self.confirm_switch = ft.Switch(
            label="Require confirmation for all actions",
            value=self.storage.config.global_requires_confirmation,
            on_change=self._on_global_confirm_change
        )

        # Import/Export json text area
        self.json_import_export_field = ft.TextField(
            label="Configuration Data (JSON)",
            hint_text="Paste configuration JSON here to import...",
            multiline=True,
            min_lines=4,
            max_lines=6
        )

        super().__init__(
            content=ft.ListView(
                controls=[
                    self._build_header(),
                    ft.Container(height=8),
                    self._build_section("Appearance", [
                        self.user_name_field,
                        ft.Text("Theme Mode", size=14, weight=ft.FontWeight.W_500),
                        self.theme_radio_group
                    ]),
                    ft.Container(height=12),
                    self._build_section("Default Behavior", [
                        self.confirm_switch
                    ]),
                    ft.Container(height=12),
                    self._build_section("Manage Categories", [
                        ft.ElevatedButton(
                            "Add New Category",
                            icon=ft.Icons.ADD,
                            on_click=self._open_add_category_dialog
                        ),
                        self._build_categories_list()
                    ]),
                    ft.Container(height=12),
                    self._build_section("Data Management (Backup & Restore)", [
                        self.json_import_export_field,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton("Export JSON", icon=ft.Icons.DOWNLOAD, on_click=self._handle_export),
                                ft.ElevatedButton("Import JSON", icon=ft.Icons.UPLOAD, on_click=self._handle_import)
                            ],
                            spacing=10
                        ),
                        ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                        ft.OutlinedButton(
                            "Reset Configuration",
                            icon=ft.Icons.DELETE_FOREVER,
                            style=ft.ButtonStyle(color=ft.Colors.RED),
                            on_click=self._handle_reset
                        )
                    ]),
                    ft.Container(height=12),
                    self._build_section("About", [
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.MEMORY, size=32, color=ft.Colors.PRIMARY),
                                ft.Column(
                                    controls=[
                                        ft.Text(APP_NAME, size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Version {APP_VERSION} • Mobile First", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=12
                        ),
                        ft.Text(
                            "ESP Control Hub is designed for high-performance direct HTTP control of local ESP32, ESP8266, and IoT microcontrollers without relying on cloud services.",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ])
                ],
                spacing=8,
                padding=16
            ),
            expand=True
        )

    def _build_header(self) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Text("Settings", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Configure app behavior and manage data", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
            ],
            spacing=2
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
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    def _build_categories_list(self) -> ft.Control:
        categories = self.storage.get_categories()
        cat_rows = []
        for cat in categories:
            if cat.id == "all":
                continue

            icon_attr = getattr(ft.Icons, cat.icon.upper(), ft.Icons.FOLDER)
            row = ft.Row(
                controls=[
                    ft.Icon(icon_attr, size=20, color=ft.Colors.PRIMARY),
                    ft.Text(cat.name, size=14, weight=ft.FontWeight.W_500, expand=True),
                    ft.IconButton(
                        ft.Icons.EDIT_OUTLINED,
                        icon_size=18,
                        on_click=lambda e, c=cat: self._open_edit_category_dialog(c)
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINED,
                        icon_size=18,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, c=cat: self._delete_category(c)
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            cat_rows.append(row)
        return ft.Column(controls=cat_rows, spacing=4)

    def _open_add_category_dialog(self, e):
        name_field = ft.TextField(label="Category Name *", hint_text="e.g. Garden")

        def _save(e):
            n = name_field.value.strip()
            if not n:
                show_snackbar(self.page_ref, "Category name is required.", is_error=True)
                return
            from models.category import Category
            new_cat = Category(name=n, icon="folder", order=len(self.storage.get_categories()))
            self.storage.add_category(new_cat)
            dialog.open = False
            self.page_ref.update()
            self.update()
            show_snackbar(self.page_ref, f"Added category '{n}'")

        dialog = ft.AlertDialog(
            title=ft.Text("Add Category", weight=ft.FontWeight.BOLD),
            content=ft.Container(content=name_field, width=280),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or self.page_ref.update()),
                ft.ElevatedButton("Save", on_click=_save)
            ]
        )
        self.page_ref.dialog = dialog
        dialog.open = True
        self.page_ref.update()

    def _open_edit_category_dialog(self, cat):
        name_field = ft.TextField(label="Category Name *", value=cat.name)

        def _save(e):
            n = name_field.value.strip()
            if not n:
                show_snackbar(self.page_ref, "Category name is required.", is_error=True)
                return
            cat.name = n
            self.storage.update_category(cat)
            dialog.open = False
            self.page_ref.update()
            self.update()
            show_snackbar(self.page_ref, f"Renamed category to '{n}'")

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Category", weight=ft.FontWeight.BOLD),
            content=ft.Container(content=name_field, width=280),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or self.page_ref.update()),
                ft.ElevatedButton("Save", on_click=_save)
            ]
        )
        self.page_ref.dialog = dialog
        dialog.open = True
        self.page_ref.update()

    def _delete_category(self, cat):
        show_confirm_dialog(
            self.page_ref,
            title=f"Delete '{cat.name}'?",
            message="Controls in this category will be moved to 'All'.",
            confirm_label="Delete",
            confirm_color=ft.Colors.RED,
            on_confirm=lambda: self._do_delete_category(cat.id)
        )

    def _do_delete_category(self, cat_id: str):
        self.storage.delete_category(cat_id)
        self.update()
        show_snackbar(self.page_ref, "Category deleted.")

    def _on_user_name_change(self, e):
        self.storage.config.user_name = e.control.value.strip() or "User"
        self.storage.save()

    def _on_theme_radio_change(self, e):
        new_theme = e.control.value
        self.storage.config.theme_mode = new_theme
        self.storage.save()
        if self.on_theme_change:
            self.on_theme_change(new_theme)

    def _on_global_confirm_change(self, e):
        self.storage.config.global_requires_confirmation = e.control.value
        self.storage.save()

    def _handle_export(self, e):
        json_str = ImportExportService.export_config(self.storage)
        self.json_import_export_field.value = json_str
        self.update()
        show_snackbar(self.page_ref, "Configuration exported to JSON text field.")

    def _handle_import(self, e):
        json_str = self.json_import_export_field.value
        if not json_str or not json_str.strip():
            show_snackbar(self.page_ref, "Please paste configuration JSON to import.", is_error=True)
            return

        show_confirm_dialog(
            self.page_ref,
            title="Overwrite Configuration?",
            message="Importing will replace your current devices, controls, and settings.",
            confirm_label="Import & Overwrite",
            confirm_color=ft.Colors.RED,
            on_confirm=lambda: self._do_import(json_str)
        )

    def _do_import(self, json_str: str):
        success, msg = ImportExportService.import_config(json_str, self.storage)
        if success:
            show_snackbar(self.page_ref, msg)
            if self.on_theme_change:
                self.on_theme_change(self.storage.config.theme_mode)
        else:
            show_snackbar(self.page_ref, msg, is_error=True)

    def _handle_reset(self, e):
        show_confirm_dialog(
            self.page_ref,
            title="Reset All Data?",
            message="This will wipe all controls, devices, and settings back to defaults.",
            confirm_label="Reset Everything",
            confirm_color=ft.Colors.RED,
            on_confirm=self._do_reset
        )

    def _do_reset(self):
        self.storage.reset_all()
        self.user_name_field.value = self.storage.config.user_name
        self.theme_radio_group.value = self.storage.config.theme_mode
        self.json_import_export_field.value = ""
        self.update()
        if self.on_theme_change:
            self.on_theme_change(self.storage.config.theme_mode)
        show_snackbar(self.page_ref, "All configuration reset to defaults.")
