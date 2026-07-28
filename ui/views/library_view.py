import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from ui.components.track_item import TrackItem
from core.state import app_state

class LibraryView(ft.Container):
    """
    Vue principale du Hub Bibliothèque & Préférences Musicales.
    Contient la zone d'importation (Dropzone), la sélection de fichiers/dossiers, la recherche et la liste des pistes.
    """
    def __init__(
        self,
        on_pick_files=None,
        on_pick_folder=None,
        on_like_track=None,
        on_delete_track=None,
        on_search=None,
    ):
        self.on_pick_files = on_pick_files
        self.on_pick_folder = on_pick_folder
        self.on_like_track = on_like_track
        self.on_delete_track = on_delete_track
        self.on_search = on_search

        # 1. Zone d'importation (Dropzone Card avec choix Fichiers / Dossier)
        self.dropzone = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=34, color=ObsidianColors.PRIMARY),
                ft.Text("Bibliothèque Musicale AIC", size=15, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
                ft.Text("Sélectionnez des fichiers audio ou scannez un dossier complet (D:\\Musique, E:\\FLAC, etc.)", size=12, color=ObsidianColors.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                ft.Container(height=4),
                ft.Row([
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.AUDIO_FILE, size=16, color=ObsidianColors.BG_DARK),
                            ft.Text("Parcourir Fichiers", size=12, weight=ft.FontWeight.BOLD, color=ObsidianColors.BG_DARK),
                        ], spacing=6),
                        style=ft.ButtonStyle(bgcolor=ObsidianColors.PRIMARY),
                        on_click=lambda e: self.on_pick_files() if self.on_pick_files else None,
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color=ObsidianColors.TEXT_PRIMARY),
                            ft.Text("Scanner un Dossier", size=12, color=ObsidianColors.TEXT_PRIMARY),
                        ], spacing=6),
                        style=ft.ButtonStyle(side=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
                        on_click=lambda e: self.on_pick_folder() if self.on_pick_folder else None,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            padding=Spacing.LG,
            border_radius=Radii.LG,
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
        )

        # 2. Barre de Recherche et Filtres
        self.search_entry = ft.TextField(
            hint_text="Rechercher par nom de fichier...",
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
            padding=ft.Padding.only(right=6),
        )

        # 4. État Vide (Empty State)
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.MUSIC_OFF_OUTLINED, size=48, color=ObsidianColors.TEXT_DISABLED),
                ft.Text("Aucun morceau dans la bibliothèque", size=16, weight=ft.FontWeight.W_600, color=ObsidianColors.TEXT_SECONDARY),
                ft.Text("Importez des fichiers ou scannez un dossier pour alimenter l'IA.", size=13, color=ObsidianColors.TEXT_MUTED),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            alignment=ft.Alignment.CENTER,
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

        try:
            self.update()
        except RuntimeError:
            pass

    def _handle_search_change(self, e):
        if self.on_search:
            self.on_search(e.control.value)

    def _handle_filter_toggle(self, e):
        app_state.session.filter_liked_only = e.control.selected
        self.refresh_tracks()
