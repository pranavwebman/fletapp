import flet as ft

def show_confirm_dialog(
    page: ft.Page,
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    confirm_color: str = ft.Colors.RED,
    on_confirm=None
):
    """Displays a mobile-friendly confirmation dialog."""
    def _on_confirm(e):
        dialog.open = False
        page.update()
        if on_confirm:
            on_confirm()

    def _on_cancel(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(message, size=14),
        actions=[
            ft.TextButton("Cancel", on_click=_on_cancel),
            ft.ElevatedButton(
                confirm_label,
                bgcolor=confirm_color,
                color=ft.Colors.WHITE,
                on_click=_on_confirm
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.dialog = dialog
    dialog.open = True
    page.update()


def show_snackbar(page: ft.Page, message: str, is_error: bool = False):
    """Displays a non-intrusive snackbar feedback message."""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
        duration=3000
    )
    page.snack_bar.open = True
    page.update()
