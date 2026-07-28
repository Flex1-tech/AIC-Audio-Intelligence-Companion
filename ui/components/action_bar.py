import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state

class ActionBar(ft.Container):
    """
    Barre de contrôle du bas (Sticky Bottom Bar) avec slider MMR et bouton de recommandation principal.
    """
    def __init__(self, on_start_recommendation=None, on_reset=None):
        self.on_start_recommendation = on_start_recommendation
        self.on_reset = on_reset

        # Slider MMR Lambda (0.0 = Diversité, 1.0 = Pertinence)
        self.lambda_slider = ft.Slider(
            min=0.0,
            max=1.0,
            divisions=10,
            value=app_state.session.lambda_mmr,
            label="{value}",
            width=160,
            active_color=ObsidianColors.PRIMARY,
            on_change=self._handle_slider_change,
        )

        self.status_text = ft.Text(
            "0 morceau(x) importé(s) | 0/3 Likés",
            size=13,
            color=ObsidianColors.TEXT_SECONDARY,
        )

        self.start_button = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color=ObsidianColors.BG_DARK),
                ft.Text("Générer la Playlist IA (MMR)", weight=ft.FontWeight.BOLD, color=ObsidianColors.BG_DARK),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            style=ft.ButtonStyle(
                bgcolor=ObsidianColors.PRIMARY,
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=Radii.SM),
            ),
            disabled=True,
            on_click=self._handle_start,
        )

        super().__init__(
            content=ft.Row(
                [
                    # Gauche : Stats & Slider MMR
                    ft.Row([
                        self.status_text,
                        ft.Container(width=1, height=20, bgcolor=ObsidianColors.BORDER_DARK),
                        ft.Row([
                            ft.Text("MMR λ :", size=12, color=ObsidianColors.TEXT_MUTED),
                            self.lambda_slider,
                        ], spacing=6),
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),

                    # Droite : Actions (Reset & Start)
                    ft.Row([
                        ft.OutlinedButton(
                            content="Réinitialiser",
                            style=ft.ButtonStyle(
                                color=ObsidianColors.TEXT_SECONDARY,
                                side=ft.BorderSide(1, ObsidianColors.BORDER_DARK),
                                shape=ft.RoundedRectangleBorder(radius=Radii.SM),
                            ),
                            on_click=self._handle_reset,
                        ),
                        self.start_button,
                    ], spacing=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.Border.only(top=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
        )

    def update_state(self):
        lib = app_state.library
        liked_cnt = lib.liked_tracks_count
        ready = lib.is_recommendation_ready
        
        self.status_text.value = f"{lib.total_tracks_count} morceau(x) importé(s) | {liked_cnt}/3 Likés (Requis: 3)"
        if ready:
            self.status_text.color = ObsidianColors.SUCCESS
        else:
            self.status_text.color = ObsidianColors.TEXT_SECONDARY

        self.start_button.disabled = not ready or app_state.is_processing
        self.update()

    def _handle_slider_change(self, e):
        app_state.session.lambda_mmr = round(e.control.value, 2)

    def _handle_start(self, e):
        if self.on_start_recommendation:
            self.on_start_recommendation()

    def _handle_reset(self, e):
        if self.on_reset:
            self.on_reset()
