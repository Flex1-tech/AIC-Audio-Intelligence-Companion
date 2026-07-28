import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from ui.components.track_item import TrackItem
from core.state import app_state

class LibraryView(ft.Container):
    """
    Vue principale du Hub Bibliothèque & Préférences Musicales.
     Contient la zone d'importation (Dropzone), la barre de recherche et la liste des pistes.
    """
    def __init__(self, on_pick_files=None, on_like_track=None, on_delete_track=None, on_search=None):
        self.on_pick_files = on_pick_files
        self.on_like_track = on_like_track
        self.on_delete_track = on_delete_track
        self.on_search = on_search

        # 1. Zone d'importation (Dropzone Card)
        self.dropzone = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=36, color=ObsidianColors.PRIMARY),
                ft.Text("Ajouter des fichiers audio", size=15, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
                ft.Text("Cliquez pour parcourir ou sélectionnez plusieurs morceaux audio (MP3, FLAC, WAV, OGG, AAC)", size=12, color=ObsidianColors.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            padding=Spacing.LG,
            border_radius=Radii.LG,
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.border.all(1, ObsidianColors.BORDER_DARK),
            on_click=lambda e: self.on_pick_files() if self.on_pick_files else None,
        )

        # 2. Barre de Recherche et Filtres
        self.search_entry = ft.TextField(
            placeholder_text="Rechercher par nom de fichier...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ObsidianColors.BORDER_DARK,
            focused_border_color=ObsidianColors.PRIMARY,
            text_size=13,
            height=40,
            content_padding=10,
            expand=True,
            on_change=self._handle_search_change,
        )

        self.filter_chip = ft.Chip(
            label=ft.Text("Likés uniquement", size=12),
            leading=ft.Icon(ft.Icons.FAVORITE, size=14, color=ObsidianColors.HEART_RED),
            selected=app_state.session.filter_liked_only,
            on_select=self._handle_filter_toggle,
        )

        # 3. Liste scrollable des morceaux (ListView)
        self.track_list = ft.ListView(
            expand=True,
            spacing=Spacing.SM,
            padding=ft.padding.only(right=6),
        )

        # 4. État Vide (Empty State)
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MUSIC_OFF_OUTLINED, size=48, color=ObsidianColors.TEXT_DISABLED),
                ft.Text("Aucun morceau importé", size=16, weight=ft.FontWeight.W600, color=ObsidianColors.TEXT_SECONDARY),
                ft.Text("Importez des fichiers audio pour commencer à entrainer l'assistant.", size=13, color=ObsidianColors.TEXT_MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            alignment=ft.alignment.center,
            padding=40,
        )

        super().__init__(
            content=ft.Column([
                self.dropzone,
                ft.Row([
                    self.search_entry,
                    self.filter_chip,
                ], spacing=12),
                ft.Container(
                    content=self.track_list,
                    expand=True,
                ),
            ], spacing=Spacing.MD, expand=True),
            padding=Spacing.LG,
            expand=True,
        )

    def refresh_tracks(self):
        """Mise à jour réactive des items de morceaux dans la liste."""
        self.track_list.controls.clear()
        query = app_state.session.search_query.lower()
        liked_only = app_state.session.filter_liked_only

        tracks = list(app_state.library.tracks.values())

        filtered_tracks = []
        for track in tracks:
            if liked_only and not track.is_liked:
                continue
            if query and query not in track.file_name.lower():
                continue
            filtered_tracks.append(track)

        if not filtered_tracks and not tracks:
            self.track_list.controls.append(self.empty_state)
        else:
            for track in filtered_tracks:
                item = TrackItem(
                    track=track,
                    on_like=self.on_like_track,
                    on_delete=self.on_delete_track,
                )
                self.track_list.controls.append(item)

        self.update()

    def _handle_search_change(self, e):
        if self.on_search:
            self.on_search(e.control.value)

    def _handle_filter_toggle(self, e):
        app_state.session.filter_liked_only = e.control.selected
        self.refresh_tracks()
