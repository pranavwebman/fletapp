import flet as ft
from utils.constants import AVAILABLE_ICONS

class IconPicker(ft.AlertDialog):
    def __init__(self, current_icon: str, on_select):
        self.selected_icon = current_icon
        self.on_select_callback = on_select

        self.search_field = ft.TextField(
            hint_text="Search icons...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filter_icons,
            expand=True
        )

        self.icons_grid = ft.GridView(
            runs_count=4,
            max_extent=60,
            spacing=8,
            run_spacing=8,
            height=240,
            expand=True
        )

        super().__init__(
            title=ft.Text("Select Icon", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self.search_field,
                        ft.Container(height=10),
                        self.icons_grid
                    ],
                    tight=True,
                    spacing=5
                ),
                width=300,
                height=300
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._close)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self._populate_icons()

    def _get_icon_attribute(self, icon_name: str):
        icon_upper = icon_name.upper()
        return getattr(ft.Icons, icon_upper, ft.Icons.LIGHTBULB)

    def _populate_icons(self, query: str = ""):
        self.icons_grid.controls.clear()
        q = query.strip().lower()

        for item in AVAILABLE_ICONS:
            name = item["name"]
            icon_key = item["icon"]

            if q and q not in name.lower() and q not in icon_key.lower():
                continue

            icon_attr = self._get_icon_attribute(icon_key)
            is_selected = (icon_key == self.selected_icon)

            btn = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            icon_attr,
                            size=24,
                            color=ft.Colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            name,
                            size=9,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2
                ),
                padding=6,
                border_radius=8,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else ft.Colors.TRANSPARENT,
                ink=True,
                on_click=lambda e, k=icon_key: self._select_icon(k)
            )
            self.icons_grid.controls.append(btn)

    def _filter_icons(self, e):
        self._populate_icons(e.control.value)
        self.icons_grid.update()

    def _select_icon(self, icon_key: str):
        self.selected_icon = icon_key
        if self.on_select_callback:
            self.on_select_callback(icon_key)
        self._close(None)

    def _close(self, e):
        self.open = False
        if self.page:
            self.page.update()
