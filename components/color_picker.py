import flet as ft
from utils.constants import COLOR_PALETTE

class ColorPicker(ft.Container):
    def __init__(self, current_color: str, on_change):
        self.selected_color = current_color or "#2196F3"
        self.on_change_callback = on_change

        palette_wrap = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=[]
        )

        for item in COLOR_PALETTE:
            hex_code = item["hex"]
            is_selected = (hex_code.lower() == self.selected_color.lower())

            color_swatch = ft.Container(
                width=36,
                height=36,
                border_radius=18,
                bgcolor=hex_code,
                alignment=ft.Alignment.CENTER,
                border=ft.Border.all(2, ft.Colors.PRIMARY if is_selected else ft.Colors.TRANSPARENT),
                content=ft.Icon(
                    ft.Icons.CHECK,
                    size=18,
                    color=ft.Colors.WHITE
                ) if is_selected else None,
                ink=True,
                on_click=lambda e, c=hex_code: self._select_color(c)
            )
            palette_wrap.controls.append(color_swatch)

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text("Accent Color", size=14, weight=ft.FontWeight.W_500),
                    palette_wrap
                ],
                tight=True,
                spacing=8
            )
        )

    def _select_color(self, hex_code: str):
        self.selected_color = hex_code
        if self.on_change_callback:
            self.on_change_callback(hex_code)
