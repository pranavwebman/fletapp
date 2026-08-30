import flet as ft
from services.storage_service import StorageService
from components.control_card import ControlCard
from components.dialogs import show_confirm_dialog, show_snackbar
from models.control import Control

class HomeScreen(ft.Container):
    def __init__(self, page: ft.Page, storage: StorageService, on_navigate_add=None, on_edit_control=None):
        self.page_ref = page
        self.storage = storage
        self.on_navigate_add = on_navigate_add
        self.on_edit_control = on_edit_control

        self.selected_category_id = "all"
        self.search_query = ""
        self.is_edit_mode = False

        # Category Filter Chips
        self.category_chips_row = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            controls=[]
        )

        # Search bar
        self.search_field = ft.TextField(
            hint_text="Search controls or devices...",
            prefix_icon=ft.Icons.SEARCH,
            density=ft.ThemeVisualDensity.COMPACT,
            border_radius=24,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_change=self._on_search_change,
            expand=True
        )

        # Controls Grid
        self.controls_grid = ft.GridView(
            runs_count=2,
            max_extent=200,
            spacing=12,
            run_spacing=12,
            expand=False,
            padding=ft.padding.only(bottom=80)
        )

        # Empty state container
        self.empty_state = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.DEVICES_OTHER, size=64, color=ft.Colors.OUTLINE),
                    ft.Text("No controls yet", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Create your first control to start controlling your ESP devices.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Add Control",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: self.on_navigate_add() if self.on_navigate_add else None
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            padding=30,
            alignment=ft.alignment.center,
            visible=False
        )

        super().__init__(
            content=ft.ListView(
                controls=[
                    self._build_header(),
                    self.category_chips_row,
                    ft.Container(height=8),
                    self.controls_grid,
                    self.empty_state
                ],
                spacing=12,
                padding=16
            ),
            expand=True
        )

        self.refresh_controls()

    def _build_header(self) -> ft.Control:
        greeting = f"Good day, {self.storage.config.user_name}"

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("ESP Control Hub", size=22, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            width=8, height=8, border_radius=4, bgcolor=ft.Colors.GREEN_500
                                        ),
                                        ft.Text(greeting, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
                                    ],
                                    spacing=6,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ],
                            spacing=2
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_NOTE if not self.is_edit_mode else ft.Icons.CHECK,
                            tooltip="Toggle Edit Mode",
                            icon_color=ft.Colors.PRIMARY if self.is_edit_mode else ft.Colors.ON_SURFACE,
                            on_click=self._toggle_edit_mode
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[self.search_field],
                    spacing=0
                )
            ],
            spacing=10
        )

    def _toggle_edit_mode(self, e):
        self.is_edit_mode = not self.is_edit_mode
        self.refresh_controls()

    def _on_search_change(self, e):
        self.search_query = e.control.value
        self.refresh_controls()

    def _select_category(self, cat_id: str):
        self.selected_category_id = cat_id
        self.refresh_controls()

    def refresh_controls(self):
        # 1. Update Category Chips
        self.category_chips_row.controls.clear()
        categories = self.storage.get_categories()

        for cat in categories:
            is_selected = (cat.id == self.selected_category_id)
            icon_attr = getattr(ft.Icons, cat.icon.upper(), ft.Icons.FOLDER)

            chip = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            icon_attr,
                            size=16,
                            color=ft.Colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            cat.name,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                            color=ft.Colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE
                        )
                    ],
                    spacing=6,
                    tight=True
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=20,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border=ft.border.all(1, ft.Colors.PRIMARY if is_selected else ft.Colors.TRANSPARENT),
                ink=True,
                on_click=lambda e, cid=cat.id: self._select_category(cid)
            )
            self.category_chips_row.controls.append(chip)

        # 2. Get Controls
        controls_list = self.storage.get_controls(
            category_id=self.selected_category_id,
            search_query=self.search_query
        )

        self.controls_grid.controls.clear()

        if not controls_list:
            self.controls_grid.visible = False
            self.empty_state.visible = True
        else:
            self.controls_grid.visible = True
            self.empty_state.visible = False

            for ctrl in controls_list:
                dev = self.storage.get_device(ctrl.device_id)
                card = ControlCard(
                    control=ctrl,
                    device=dev,
                    is_edit_mode=self.is_edit_mode,
                    on_edit=self.on_edit_control,
                    on_delete=self._handle_delete_control,
                    on_duplicate=self._handle_duplicate_control,
                    on_state_change=self._handle_state_change
                )
                self.controls_grid.controls.append(card)

        if self.page_ref:
            self.update()

    def _handle_state_change(self, control: Control):
        self.storage.update_control(control)

    def _handle_delete_control(self, control: Control):
        show_confirm_dialog(
            self.page_ref,
            title=f"Delete '{control.name}'?",
            message="This action cannot be undone.",
            confirm_label="Delete",
            confirm_color=ft.Colors.RED,
            on_confirm=lambda: self._do_delete_control(control.id)
        )

    def _do_delete_control(self, control_id: str):
        self.storage.delete_control(control_id)
        show_snackbar(self.page_ref, "Control deleted.")
        self.refresh_controls()

    def _handle_duplicate_control(self, control: Control):
        new_ctrl = Control.from_dict(control.to_dict())
        new_ctrl.id = None  # Generate new ID
        new_ctrl.name = f"{control.name} (Copy)"
        self.storage.add_control(new_ctrl)
        show_snackbar(self.page_ref, f"Duplicated '{control.name}'")
        self.refresh_controls()
