import asyncio
import flet as ft
from models.control import Control
from models.device import Device
from services.http_service import HTTPService
from components.dialogs import show_confirm_dialog, show_snackbar

class ControlCard(ft.Container):
    def __init__(
        self,
        control: Control,
        device: Device = None,
        is_edit_mode: bool = False,
        on_edit=None,
        on_delete=None,
        on_duplicate=None,
        on_state_change=None
    ):
        self.control = control
        self.device = device
        self.is_edit_mode = is_edit_mode
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_duplicate = on_duplicate
        self.on_state_change = on_state_change

        self.is_loading = False
        self.feedback_icon = None  # None, "check", or "error"
        self.status_msg = ""

        # Control UI elements
        self.title_text = ft.Text(
            self.control.name,
            weight=ft.FontWeight.BOLD,
            size=14,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        self.subtitle_text = ft.Text(
            self._get_subtitle_text(),
            size=11,
            color=ft.Colors.ON_SURFACE_VARIANT,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        self.icon_box = ft.Container(
            content=ft.Icon(
                self._get_icon_attribute(self.control.icon),
                size=26,
                color=ft.Colors.WHITE if self.control.state else self.control.color
            ),
            width=44,
            height=44,
            border_radius=22,
            bgcolor=self.control.color if self.control.state else ft.Colors.SURFACE_CONTAINER_HIGHEST,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        )

        self.state_badge = ft.Container(
            content=ft.Text(
                self._get_state_label(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE if self.control.state else ft.Colors.ON_SURFACE_VARIANT
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10,
            bgcolor=self.control.color if self.control.state else ft.Colors.SURFACE_CONTAINER_HIGHEST
        )

        self.loader = ft.ProgressRing(width=20, height=20, stroke_width=2.5, visible=False)

        # Build card content layout
        card_content = self._build_card_content()

        super().__init__(
            content=card_content,
            padding=12,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border=ft.border.all(1.5, self.control.color if self.control.state else ft.Colors.OUTLINE_VARIANT),
            shadow=ft.BoxShadow(
                blur_radius=8,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            ink=not self.is_edit_mode,
            on_click=self._handle_card_tap if not self.is_edit_mode else None
        )

    def _get_icon_attribute(self, icon_name: str):
        icon_upper = icon_name.upper()
        return getattr(ft.Icons, icon_upper, ft.Icons.LIGHTBULB)

    def _get_subtitle_text(self) -> str:
        if self.device:
            return self.device.name
        elif self.control.custom_url:
            return "Custom URL"
        return "No Device"

    def _get_state_label(self) -> str:
        if self.control.control_type == Control.TYPE_TOGGLE:
            return "ON" if self.control.state else "OFF"
        elif self.control.control_type == Control.TYPE_MOMENTARY:
            return "HOLD"
        else:
            return "ACTION"

    def _build_card_content(self) -> ft.Control:
        if self.is_edit_mode:
            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.icon_box,
                            ft.Column(
                                controls=[
                                    self.title_text,
                                    self.subtitle_text
                                ],
                                spacing=2,
                                expand=True
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_ROUNDED,
                                icon_size=18,
                                tooltip="Edit",
                                on_click=lambda e: self.on_edit(self.control) if self.on_edit else None
                            ),
                            ft.IconButton(
                                icon=ft.Icons.COPY_ROUNDED,
                                icon_size=18,
                                tooltip="Duplicate",
                                on_click=lambda e: self.on_duplicate(self.control) if self.on_duplicate else None
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINED,
                                icon_size=18,
                                icon_color=ft.Colors.RED,
                                tooltip="Delete",
                                on_click=lambda e: self.on_delete(self.control) if self.on_delete else None
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    )
                ],
                tight=True,
                spacing=4
            )

        # Standard interactive card
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.icon_box,
                        ft.Container(
                            content=self.loader if self.is_loading else self.state_badge,
                            alignment=ft.alignment.center_right
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=10),
                self.title_text,
                self.subtitle_text
            ],
            tight=True,
            spacing=2
        )

    def _handle_card_tap(self, e):
        if self.is_loading:
            return  # Prevent duplicate taps during active request

        if self.control.requires_confirmation:
            show_confirm_dialog(
                e.page,
                title=f"Execute '{self.control.name}'?",
                message=f"Are you sure you want to run this control?",
                confirm_label="Run",
                confirm_color=self.control.color,
                on_confirm=lambda: asyncio.create_task(self._execute_action(e.page))
            )
        else:
            asyncio.create_task(self._execute_action(e.page))

    async def _execute_action(self, page: ft.Page):
        self.is_loading = True
        self.loader.visible = True
        self.state_badge.visible = False
        self.update()

        # Determine state flip for toggle controls
        target_is_off = False
        if self.control.control_type == Control.TYPE_TOGGLE:
            target_is_off = self.control.state  # If currently ON, send OFF endpoint

        url = self.control.get_full_url(self.device, is_off=target_is_off)

        result = await HTTPService.send_request(
            url=url,
            method=self.control.http_method,
            headers=self.control.custom_headers,
            body=self.control.request_body,
            timeout=self.control.timeout
        )

        self.is_loading = False
        self.loader.visible = False
        self.state_badge.visible = True

        if result.success:
            if self.control.control_type == Control.TYPE_TOGGLE:
                self.control.state = not self.control.state

            show_snackbar(page, f"✓ {self.control.name}: Request successful (HTTP {result.status_code})")

            if self.on_state_change:
                self.on_state_change(self.control)
        else:
            show_snackbar(page, f"✕ {self.control.name}: {result.error_message}", is_error=True)

        self._update_visual_state()
        self.update()

    def _update_visual_state(self):
        self.icon_box.bgcolor = self.control.color if self.control.state else ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.icon_box.content.color = ft.Colors.WHITE if self.control.state else self.control.color
        self.state_badge.bgcolor = self.control.color if self.control.state else ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.state_badge.content.value = self._get_state_label()
        self.state_badge.content.color = ft.Colors.WHITE if self.control.state else ft.Colors.ON_SURFACE_VARIANT
        self.border = ft.border.all(1.5, self.control.color if self.control.state else ft.Colors.OUTLINE_VARIANT)
