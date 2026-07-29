import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class SettingsView(ft.Container):
    """
    Vue des Paramètres d'AIC.
    """

    def __init__(self):
        self.vlc_path_input = ft.TextField(
            value=app_state.session.vlc_custom_path,
            hint_text="Chemin d'accès vers vlc.exe (détection automatique par défaut)",
            border_color=ObsidianColors.BORDER_DARK,
            focused_border_color=ObsidianColors.PRIMARY,
            text_size=13,
            expand=True,
            on_change=self._handle_vlc_path_change,
        )

        super().__init__(
            content=ft.Column([
                ft.Text(
                    "Réglages & Préférences",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ObsidianColors.TEXT_PRIMARY),
                ft.Text(
                    "Configurez les intégrations externes et les paramètres du moteur IA.",
                    size=13,
                    color=ObsidianColors.TEXT_MUTED),
                ft.Container(height=15),

                # VLC Path Setting Card
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Lecteur Média VLC",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=ObsidianColors.TEXT_PRIMARY),
                        ft.Text(
                            "Chemin d'accès personnalisé vers l'exécutable VLC sur votre ordinateur.",
                            size=12,
                            color=ObsidianColors.TEXT_MUTED),
                        ft.Container(height=6),
                        ft.Row([
                            self.vlc_path_input,
                        ]),
                    ], spacing=6),
                    padding=Spacing.LG,
                    border_radius=Radii.MD,
                    bgcolor=ObsidianColors.SURFACE_DARK,
                    border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
                ),

                ft.Container(height=15),
                # About Card
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "À propos d'AIC (Audio Intelligence Companion)",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=ObsidianColors.TEXT_PRIMARY),
                        ft.Text(
                            "Version 2.0 • Propulsé par Flet, ONNX Runtime, LanceDB et BLAKE3.",
                            size=12,
                            color=ObsidianColors.TEXT_MUTED),
                        ft.Text(
                            "Mode de fonctionnement : 100% Local & Souverain.",
                            size=12,
                            color=ObsidianColors.SUCCESS),
                    ], spacing=6),
                    padding=Spacing.LG,
                    border_radius=Radii.MD,
                    bgcolor=ObsidianColors.SURFACE_DARK,
                    border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
                ),
            ], spacing=Spacing.MD, expand=True),
            padding=Spacing.LG,
            expand=True,
        )

    def _handle_vlc_path_change(self, e):
        app_state.session.vlc_custom_path = e.control.value.strip()
