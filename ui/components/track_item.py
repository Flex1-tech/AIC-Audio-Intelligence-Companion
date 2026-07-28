import flet as ft
from domain.track import Track
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing

class TrackItem(ft.Container):
    """
    Carte réutilisable affichant un morceau audio avec métadonnées, BLAKE3 hash et bouton like.
    """
    def __init__(self, track: Track, on_like=None, on_delete=None):
        self.track = track
        self.on_like = on_like
        self.on_delete = on_delete

        # Heart Icon Button
        self.like_button = ft.IconButton(
            icon=ft.Icons.FAVORITE if track.is_liked else ft.Icons.FAVORITE_BORDER,
            icon_color=ObsidianColors.HEART_RED if track.is_liked else ObsidianColors.TEXT_MUTED,
            icon_size=20,
            tooltip="Liker ce morceau" if not track.is_liked else "Morceau liké",
            on_click=self._handle_like,
        )

        # Format Badge (ex: MP3, FLAC)
        format_badge = ft.Container(
            content=ft.Text(track.audio_format or "AUDIO", size=10, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_SECONDARY),
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            border_radius=Radii.SM,
            bgcolor=ObsidianColors.SURFACE_ELEVATED,
        )

        # Hash Badge
        hash_badge = ft.Container(
            content=ft.Text(track.short_hash, size=10, font_family="monospace", color=ObsidianColors.TEXT_MUTED),
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            border_radius=Radii.SM,
            bgcolor=ObsidianColors.SURFACE_ELEVATED,
        )

        super().__init__(
            content=ft.Row(
                [
                    # Gauche : Icône + Nom + Métadonnées
                    ft.Row([
                        ft.Icon(ft.Icons.MUSIC_NOTE, size=20, color=ObsidianColors.PRIMARY if track.is_liked else ObsidianColors.TEXT_SECONDARY),
                        ft.Column([
                            ft.Text(track.file_name, size=14, weight=ft.FontWeight.W_500, color=ObsidianColors.TEXT_PRIMARY, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                            ft.Row([
                                format_badge,
                                ft.Text(track.formatted_size, size=11, color=ObsidianColors.TEXT_MUTED),
                                hash_badge,
                            ], spacing=8),
                        ], spacing=2, expand=True),
                    ], spacing=12, expand=True),

                    # Droite : Actions (Like & Delete)
                    ft.Row([
                        self.like_button,
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINED,
                            icon_color=ObsidianColors.TEXT_MUTED,
                            icon_size=18,
                            tooltip="Retirer de la liste",
                            on_click=self._handle_delete,
                        ),
                    ], spacing=4),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
            border_radius=Radii.MD,
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.Border.all(1, ObsidianColors.PRIMARY if track.is_liked else ObsidianColors.BORDER_DARK),
        )

    def _handle_like(self, e):
        if self.on_like:
            self.on_like(self.track.file_path)

    def _handle_delete(self, e):
        if self.on_delete:
            self.on_delete(self.track.file_path)
