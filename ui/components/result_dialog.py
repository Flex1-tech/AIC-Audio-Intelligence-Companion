import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from typing import Callable, Optional


class ResultDialog(ft.AlertDialog):
    """
    Dialogue modal moderne affichant le résultat de l'export de playlist MMR.
    Permet à l'utilisateur de :
    - Voir le nombre de morceaux et le nom du fichier généré
    - Consulter l'emplacement d'exportation
    - Ouvrir le dossier natif de l'OS
    - Modifier le dossier d'exportation
    - Lancer la playlist directement dans VLC
    - Fermer le dialogue sans fermer l'application
    """

    def __init__(
        self,
        count: int,
        file_name: str = "AIC Playlist.m3u8",
        file_path: str = "",
        folder_path: str = "",
        on_launch_vlc: Optional[Callable[[], None]] = None,
        on_open_folder: Optional[Callable[[], None]] = None,
        on_change_folder: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        self._on_launch_vlc = on_launch_vlc
        self._on_open_folder = on_open_folder
        self._on_change_folder = on_change_folder
        self._on_close = on_close

        super().__init__(
            modal=True,
            title=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_OUTLINED,
                        color=ObsidianColors.SUCCESS,
                        size=24,
                    ),
                    ft.Text(
                        "Playlist IA Générée avec Succès !",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=10,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        f"{count} morceau(x) ordonnés par Maximal Marginal Relevance (MMR).",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=6),
                    # Carte d'information de l'export
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.FOLDER, size=16, color=ObsidianColors.PRIMARY),
                                        ft.Text(
                                            "Destination :",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            folder_path or file_path,
                                            size=11,
                                            font_family="monospace",
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=6,
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=16, color=ObsidianColors.PRIMARY
                                        ),
                                        ft.Text(
                                            "Fichier :",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            file_name,
                                            size=11,
                                            font_family="monospace",
                                            color=ft.Colors.ON_SURFACE_VARIANT,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=6,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=Spacing.MD,
                        border_radius=Radii.SM,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    ),
                ],
                tight=True,
                spacing=8,
            ),
            actions=[
                ft.OutlinedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                            ft.Text("Ouvrir le dossier", size=12),
                        ],
                        spacing=6,
                    ),
                    style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
                    on_click=self._handle_open_folder,
                ),
                ft.OutlinedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DRIVE_FILE_MOVE_OUTLINED, size=16),
                            ft.Text("Changer dossier", size=12),
                        ],
                        spacing=6,
                    ),
                    style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
                    on_click=self._handle_change_folder,
                ),
                ft.FilledButton(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PLAY_ARROW_ROUNDED,
                                size=18,
                                color=ObsidianColors.ON_PRIMARY,
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
                        bgcolor=ObsidianColors.PRIMARY,
                        mouse_cursor=ft.MouseCursor.CLICK,
                    ),
                    on_click=self._handle_vlc,
                ),
                ft.TextButton(
                    content="Fermer",
                    style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
                    on_click=self._handle_close,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            shape=ft.RoundedRectangleBorder(radius=Radii.LG),
            on_dismiss=self._handle_close,
        )

    def _handle_close(self, _e=None) -> None:
        if self._on_close:
            self._on_close()

    def _handle_vlc(self, _e=None) -> None:
        if self._on_launch_vlc:
            self._on_launch_vlc()

    def _handle_open_folder(self, _e=None) -> None:
        if self._on_open_folder:
            self._on_open_folder()

    def _handle_change_folder(self, _e=None) -> None:
        if self._on_change_folder:
            self._on_change_folder()
