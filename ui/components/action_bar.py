import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class ActionBar(ft.Container):
    """
    Barre de contrôle du bas (Sticky Bottom Bar) avec slider MMR et bouton de recommandation principal.

    Surface and border colours delegate to the theme.
    Brand colours (PRIMARY) and typographic hierarchy colours (TEXT_MUTED) remain explicit.
    TEXT_SECONDARY in dynamic updates uses ft.Colors.ON_SURFACE_VARIANT which resolves
    to ObsidianColors.TEXT_SECONDARY in dark mode via ColorScheme.
    """

    def __init__(self, on_start_recommendation=None, on_reset=None):
        self.on_start_recommendation = on_start_recommendation
        self.on_reset = on_reset

        # Slider MMR Lambda (0.00 = Diversité, 1.00 = Pertinence)
        self.lambda_slider = ft.Slider(
            min=0.0,
            max=1.0,
            divisions=100,
            value=app_state.session.lambda_mmr,
            label="{value}",
            width=160,
            active_color=ObsidianColors.PRIMARY,  # brand identity — explicit
            on_change=self._handle_slider_change,
        )

        self.lambda_text = ft.Text(
            f"λ = {app_state.session.lambda_mmr:.2f}",
            size=12,
            weight=ft.FontWeight.W_600,
            color=ObsidianColors.PRIMARY,  # brand accent — explicit
        )

        self.status_text = ft.Text(
            "0 morceau(x) importé(s) | 0/3 Likés",
            size=13,
            color=ft.Colors.ON_SURFACE_VARIANT,  # secondary text — via ColorScheme
        )

        self.reset_button = ft.OutlinedButton(
            content="Réinitialiser",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=Radii.SM),
                mouse_cursor=ft.MouseCursor.CLICK,
            ),
            on_click=self._handle_reset,
        )

        self.start_button = ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color=ObsidianColors.ON_PRIMARY),
                    ft.Text(
                        "Générer la Playlist IA (MMR)",
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.ON_PRIMARY,  # = BG_DARK — dark on amber (8.79:1)
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=ObsidianColors.PRIMARY,  # brand action — explicit
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=Radii.SM),
                mouse_cursor=ft.MouseCursor.FORBIDDEN,
            ),
            disabled=True,
            on_click=self._handle_start,
        )

        super().__init__(
            content=ft.Row(
                [
                    # Gauche : Stats & Slider MMR
                    ft.Row(
                        [
                            self.status_text,
                            ft.Container(
                                width=1,
                                height=20,
                                bgcolor=ft.Colors.OUTLINE,  # = BORDER_DARK via ColorScheme
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        "Balance MMR :",
                                        size=12,
                                        color=ObsidianColors.TEXT_MUTED,  # 3rd-level hierarchy — explicit
                                    ),
                                    self.lambda_slider,
                                    self.lambda_text,
                                ],
                                spacing=6,
                            ),
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    # Droite : Actions (Reset & Start)
                    ft.Row(
                        [
                            self.reset_button,
                            self.start_button,
                        ],
                        spacing=12,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            bgcolor=ft.Colors.SURFACE_CONTAINER,  # = SURFACE_DARK via ColorScheme
            border=ft.Border.only(top=ft.BorderSide(1, ft.Colors.OUTLINE)),  # = BORDER_DARK via ColorScheme
        )

    def update_state(self):
        lib = app_state.library
        liked_cnt = lib.liked_tracks_count
        ready = lib.is_recommendation_ready
        processing = app_state.is_processing

        if processing:
            self.status_text.value = app_state.processing_status_message or "Génération des recommandations en cours…"
            self.status_text.color = ObsidianColors.PRIMARY
            self.start_button.content = ft.Row(
                [
                    ft.ProgressRing(width=16, height=16, stroke_width=2.5, color=ObsidianColors.ON_PRIMARY),
                    ft.Text(
                        "Génération en cours…",
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.ON_PRIMARY,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        else:
            self.status_text.value = f"{lib.total_tracks_count} morceau(x) importé(s) | {liked_cnt}/3 Likés (Requis: 3)"
            self.status_text.color = ObsidianColors.SUCCESS if ready else ft.Colors.ON_SURFACE_VARIANT
            self.start_button.content = ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color=ObsidianColors.ON_PRIMARY),
                    ft.Text(
                        "Générer la Playlist IA (MMR)",
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.ON_PRIMARY,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            )

        self.start_button.disabled = not ready or processing
        self.lambda_slider.disabled = processing
        self.reset_button.disabled = processing

        cursor = ft.MouseCursor.WAIT if processing else (ft.MouseCursor.CLICK if ready else ft.MouseCursor.FORBIDDEN)
        self.start_button.style.mouse_cursor = cursor
        self.reset_button.style.mouse_cursor = ft.MouseCursor.WAIT if processing else ft.MouseCursor.CLICK
        try:
            self.update()
        except RuntimeError:
            pass

    def _handle_slider_change(self, e):
        val = round(float(e.control.value), 2)
        app_state.session.lambda_mmr = val
        self.lambda_text.value = f"λ = {val:.2f}"
        try:
            self.lambda_text.update()
        except RuntimeError:
            pass

    def _handle_start(self, e):
        ctrl = getattr(e, "control", None)
        print(f"[GENERATION_TRIGGER] ActionBar._handle_start event={e}, control={ctrl}")
        if self.on_start_recommendation:
            self.on_start_recommendation()

    def _handle_reset(self, e):
        ctrl = getattr(e, "control", None)
        print(f"[EVENT] ActionBar._handle_reset event={e}, control={ctrl}")
        if self.on_reset:
            self.on_reset()
