import flet as ft
from services.storage_service import StorageService
from screens.home import HomeScreen
from screens.devices import DevicesScreen
from screens.editor import EditorScreen
from screens.settings import SettingsScreen
from models.app_config import AppConfig

def main(page: ft.Page):
    # Setup Mobile Phone Page Parameters
    page.title = "ESP Control Hub"
    page.padding = 0
    page.spacing = 0
    page.window.width = 390
    page.window.height = 844
    page.window.resizable = True

    storage = StorageService()

    # Apply initial theme mode
    def apply_theme(mode_str: str):
        if mode_str == AppConfig.THEME_DARK:
            page.theme_mode = ft.ThemeMode.DARK
        elif mode_str == AppConfig.THEME_LIGHT:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
        page.update()

    apply_theme(storage.config.theme_mode)

    # Content Container
    body_container = ft.Container(expand=True)

    # State for current active screen and editing control
    current_index = 0
    editing_control = None

    def navigate_to(index: int, control_to_edit=None):
        nonlocal current_index, editing_control
        current_index = index
        editing_control = control_to_edit

        # Update navigation bar selection
        if nav_bar.selected_index != index:
            nav_bar.selected_index = index

        # Render corresponding screen
        if index == 0:
            home = HomeScreen(
                page=page,
                storage=storage,
                on_navigate_add=lambda: navigate_to(2, None),
                on_edit_control=lambda ctrl: navigate_to(2, ctrl)
            )
            body_container.content = home
        elif index == 1:
            devices = DevicesScreen(page=page, storage=storage)
            body_container.content = devices
        elif index == 2:
            editor = EditorScreen(
                page=page,
                storage=storage,
                control_to_edit=editing_control,
                on_saved=lambda: navigate_to(0),
                on_cancel=lambda: navigate_to(0)
            )
            body_container.content = editor
        elif index == 3:
            settings = SettingsScreen(
                page=page,
                storage=storage,
                on_theme_change=apply_theme
            )
            body_container.content = settings

        page.update()

    def on_nav_change(e):
        idx = e.control.selected_index
        navigate_to(idx, None)

    # Bottom Navigation Bar for Mobile
    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.GRID_VIEW_OUTLINED,
                selected_icon=ft.Icons.GRID_VIEW_ROUNDED,
                label="Controls"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ROUTER_OUTLINED,
                selected_icon=ft.Icons.ROUTER,
                label="Devices"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.ADD_CIRCLE,
                label="Add"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings"
            ),
        ]
    )

    page.navigation_bar = nav_bar
    page.add(body_container)

    # Initial view setup
    navigate_to(0)

if __name__ == "__main__":
    ft.app(target=main)
