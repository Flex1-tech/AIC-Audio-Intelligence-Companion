import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class SettingsView(ft.Container):
    """
    Vue des Paramètres d'AIC (VLC, Dossier d'exportation des playlists, À propos).
    """

    def __init__(self, on_pick_export_folder=None):
        self.on_pick_export_folder = on_pick_export_folder

        self.vlc_path_input = ft.TextField(
            value=app_state.session.vlc_custom_path,
            hint_text="Chemin d'accès vers vlc.exe (détection automatique par défaut)",
            focused_border_color=ObsidianColors.PRIMARY,
            text_size=13,
            expand=True,
            on_change=self._handle_vlc_path_change,
        )

        self.export_folder_input = ft.TextField(
            value=app_state.session.get_effective_export_folder(),
            hint_text="Dossier d'exportation des playlists .m3u8",
            focused_border_color=ObsidianColors.PRIMARY,
            text_size=13,
            expand=True,
            on_change=self._handle_export_folder_change,
        )

        self.browse_export_btn = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                    ft.Text("Parcourir..."),
                ],
                spacing=6,
            ),
            style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
            on_click=self._handle_browse_export,
        )

        super().__init__(
            content=ft.Column(
                [
                    ft.Text(
                        "Réglages & Préférences",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Configurez les dossiers de sortie, les intégrations externes et les paramètres applicatifs.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=15),
                    # Export Folder Setting Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Dossier d'exportation des playlists",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    "Emplacement où seront enregistrées vos playlists .m3u8 générées par l'IA.",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Container(height=6),
                                ft.Row(
                                    [
                                        self.export_folder_input,
                                        self.browse_export_btn,
                                    ],
                                    spacing=10,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=Spacing.LG,
                        border_radius=Radii.MD,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    ),
                    ft.Container(height=15),
                    # VLC Path Setting Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Lecteur Média VLC",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    "Chemin d'accès personnalisé vers l'exécutable VLC sur votre ordinateur.",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Container(height=6),
                                ft.Row(
                                    [
                                        self.vlc_path_input,
                                    ]
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=Spacing.LG,
                        border_radius=Radii.MD,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    ),
                    ft.Container(height=15),
                    # About Card
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "À propos d'AIC (Audio Intelligence Companion)",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    "Version 2.0 • Propulsé par Flet, ONNX Runtime, LanceDB et BLAKE3.",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.Text(
                                    "Mode de fonctionnement : 100% Local & Souverain.",
                                    size=12,
                                    color=ObsidianColors.SUCCESS,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=Spacing.LG,
                        border_radius=Radii.MD,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    ),
                ],
                spacing=Spacing.MD,
                expand=True,
            ),
            padding=Spacing.LG,
            expand=True,
        )

    def update_export_folder(self, path: str):
        app_state.session.export_folder_path = path
        self.export_folder_input.value = path
        try:
            self.export_folder_input.update()
        except Exception:
            pass

    def _handle_vlc_path_change(self, e):
        app_state.session.vlc_custom_path = e.control.value.strip()

    def _handle_export_folder_change(self, e):
        app_state.session.export_folder_path = e.control.value.strip()

    def _handle_browse_export(self, _e):
        if self.on_pick_export_folder:
            self.on_pick_export_folder()
