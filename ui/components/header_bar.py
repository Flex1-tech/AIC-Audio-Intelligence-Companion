import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class HeaderBar(ft.Container):
    """
    Header principal avec logo AIC, badges de télémétrie IA et commutateur de thème.
    """

    def __init__(self, on_theme_toggle=None):
        self.on_theme_toggle = on_theme_toggle

        # Badges d'état IA
        self.onnx_badge = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.AUTO_AWESOME, size=14, color=ObsidianColors.SUCCESS
                    ),
                    ft.Text(
                        "Musicnn ONNX",
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=ObsidianColors.TEXT_PRIMARY,
                    ),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=Radii.FULL,
            bgcolor=ObsidianColors.SUCCESS_BG,
        )

        self.db_text = ft.Text(
            "LanceDB Active",
            size=12,
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.TEXT_PRIMARY,
        )

        self.db_badge = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.STORAGE, size=14, color=ObsidianColors.PRIMARY),
                    self.db_text,
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=Radii.FULL,
            bgcolor=ObsidianColors.PRIMARY_GLOW,
        )

        super().__init__(
            content=ft.Row(
                [
                    # Logo & Titre
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.GRAPHIC_EQ,
                                    size=22,
                                    color=ObsidianColors.PRIMARY,
                                ),
                                padding=8,
                                border_radius=Radii.SM,
                                bgcolor=ObsidianColors.SURFACE_ELEVATED,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "AIC",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ObsidianColors.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        "Audio Intelligence Companion",
                                        size=11,
                                        color=ObsidianColors.TEXT_MUTED,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=12,
                    ),
                    # Center / Badges
                    ft.Row(
                        [
                            self.onnx_badge,
                            self.db_badge,
                        ],
                        spacing=10,
                    ),
                    # Action droite
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.BRIGHTNESS_4_OUTLINED,
                                icon_size=18,
                                icon_color=ObsidianColors.TEXT_SECONDARY,
                                tooltip="Changer le thème",
                                on_click=self._handle_theme_toggle,
                            ),
                        ],
                        spacing=6,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.Border.only(bottom=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
        )

    def update_telemetry(self):
        """Mise à jour réactive des badges."""
        self.db_text.value = f"LanceDB ({app_state.total_embeddings_in_db} cache)"
        try:
            self.update()
        except RuntimeError:
            pass

    def _handle_theme_toggle(self, e):
        if self.on_theme_toggle:
            self.on_theme_toggle(e)
