import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing

class ResultDialog(ft.AlertDialog):
    """
    Dialogue modal élégant affichant le résultat du calcul MMR (sans fermer l'application !).
    """
    def __init__(self, count: int, file_path: str = "playlist.m3u8", on_launch_vlc=None, on_close=None):
        self.on_launch_vlc = on_launch_vlc
        self.on_close_cb = on_close

        super().__init__(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ObsidianColors.SUCCESS, size=24),
                ft.Text("Playlist Recommandée avec Succès !", size=18, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            ], spacing=10),
            content=ft.Column([
                ft.Text(f"{count} morceau(x) ont été ordonnés par Maximal Marginal Relevance (MMR).", size=14, color=ObsidianColors.TEXT_PRIMARY),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=16, color=ObsidianColors.PRIMARY),
                        ft.Text(file_path, size=12, family="monospace", color=ObsidianColors.TEXT_SECONDARY),
                    ], spacing=8),
                    padding=10,
                    border_radius=Radii.SM,
                    bgcolor=ObsidianColors.SURFACE_ELEVATED,
                ),
            ], tight=True, spacing=6),
            actions=[
                ft.OutlinedButton(
                    text="Fermer et continuer",
                    on_click=self._handle_close,
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=18),
                        ft.Text("Lancer dans VLC", weight=ft.FontWeight.BOLD),
                    ], spacing=6),
                    style=ft.ButtonStyle(
                        color=ObsidianColors.BG_DARK,
                        bgcolor=ObsidianColors.PRIMARY,
                    ),
                    on_click=self._handle_vlc,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ObsidianColors.SURFACE_DARK,
            shape=ft.RoundedRectangleBorder(radius=Radii.LG),
        )

    def _handle_close(self, e):
        self.open = False
        if self.page:
            self.page.update()
        if self.on_close_cb:
            self.on_close_cb()

    def _handle_vlc(self, e):
        if self.on_launch_vlc:
            self.on_launch_vlc()
