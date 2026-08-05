import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from typing import Callable, Optional


class ResultDialog(ft.AlertDialog):
    """
    Dialogue modal élégant affichant le résultat du calcul MMR.
    N'interrompt PAS l'application — l'utilisateur peut continuer à l'utiliser.

    La fermeture est déléguée au parent via `on_close` (qui appelle page.pop_dialog()).
    """

    def __init__(
        self,
        count: int,
        file_path: str = "playlist.m3u8",
        on_launch_vlc: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        self._on_launch_vlc = on_launch_vlc
        self._on_close = on_close

        super().__init__(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_OUTLINED,
                        color=ObsidianColors.SUCCESS,  # semantic — explicit
                        size=24,
                    ),
                    ft.Text(
                        "Playlist Recommandée avec Succès !",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        # no explicit color — inherits on_surface
                    ),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"{count} morceau(x) ont été ordonnés par Maximal Marginal Relevance (MMR).",
                        size=14,
                        # no explicit color — inherits on_surface
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.DESCRIPTION_OUTLINED,
                                    size=16,
                                    color=ObsidianColors.PRIMARY,  # brand accent — explicit
                                ),
                                ft.Text(
                                    file_path,
                                    size=12,
                                    font_family="monospace",
                                    color=ft.Colors.ON_SURFACE_VARIANT,  # secondary text — via ColorScheme
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=10,
                        border_radius=Radii.SM,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,  # = SURFACE_ELEVATED via ColorScheme
                    ),
                ],
                tight=True,
                spacing=6,
            ),
            actions=[
                ft.OutlinedButton(
                    content="Fermer et continuer",
                    on_click=self._handle_close,
                    # no explicit colors — inherits from theme
                ),
                ft.FilledButton(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PLAY_ARROW_ROUNDED,
                                size=18,
                                color=ObsidianColors.ON_PRIMARY,  # dark on amber — explicit
                            ),
                            ft.Text(
                                "Lancer dans VLC",
                                weight=ft.FontWeight.BOLD,
                                color=ObsidianColors.ON_PRIMARY,
                            ),
                        ],
                        spacing=6,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ObsidianColors.PRIMARY,  # brand action — explicit
                    ),
                    on_click=self._handle_vlc,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,  # = SURFACE_ELEVATED via ColorScheme
            shape=ft.RoundedRectangleBorder(radius=Radii.LG),
            on_dismiss=self._handle_close,
        )

    def _handle_close(self, _e=None) -> None:
        if self._on_close:
            self._on_close()

    def _handle_vlc(self, _e=None) -> None:
        if self._on_launch_vlc:
            self._on_launch_vlc()
