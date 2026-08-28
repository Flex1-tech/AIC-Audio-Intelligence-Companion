import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class HeaderBar(ft.Container):
    """
    Header principal avec logo AIC, badges de télémétrie IA et commutateur de thème.

    Surface and border colours delegate to the theme via ft.Colors so that they
    adapt when the user toggles the theme.  Brand-specific colours (PRIMARY,
    SUCCESS, badge backgrounds) remain explicit because they are semantic design
    decisions of the Obsidian Horizon system, not generic Material roles.
    Text colours for PRIMARY and body content are removed so ft inherits
    on_surface from the active ColorScheme.  TEXT_MUTED is kept explicit because
    it represents a deliberate typographic hierarchy tier with no M3 equivalent.
    """

    def __init__(self, on_theme_toggle=None):
        self.on_theme_toggle = on_theme_toggle

        # Badges d'état IA — M3 adaptive containers + Cyan (#30C4EF) for Tech/DB
        self.onnx_badge = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=14, color=ObsidianColors.SUCCESS),
                    ft.Text(
                        "Musicnn ONNX",
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.ON_TERTIARY_CONTAINER,
                    ),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=Radii.FULL,
            bgcolor=ft.Colors.TERTIARY_CONTAINER,
        )

        self.db_text = ft.Text(
            "LanceDB Active",
            size=12,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SECONDARY_CONTAINER,
        )

        self.db_badge = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.STORAGE, size=14, color=ObsidianColors.ACCENT_CYAN),
                    self.db_text,
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=Radii.FULL,
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
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
                                    color=ObsidianColors.ACCENT_CYAN,  # Brand Cyan for AI structure logo
                                ),
                                padding=8,
                                border_radius=Radii.SM,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "AIC",
                                        size=16,
                                        font_family="Cinzel Decorative Bold",
                                    ),
                                    ft.Text(
                                        "Audio Intelligence Companion",
                                        size=11,
                                        font_family="Cinzel Decorative Regular",
                                        color=ft.Colors.ON_SURFACE_VARIANT,
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
                                tooltip="Changer le thème",
                                mouse_cursor=ft.MouseCursor.CLICK,
                                on_click=self._handle_theme_toggle,
                                # no icon_color — inherits on_surface_variant from theme
                            ),
                        ],
                        spacing=6,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            bgcolor=ft.Colors.SURFACE_CONTAINER,  # = ObsidianColors.SURFACE_DARK via ColorScheme
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE)),  # = BORDER_DARK via ColorScheme
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
