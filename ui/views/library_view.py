import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from ui.components.track_item import TrackItem
from core.state import app_state


class LibraryView(ft.Container):
    """
    Vue principale du Hub Bibliothèque & Préférences Musicales.
    Contient la zone d'importation (Dropzone), la sélection de fichiers/dossiers,
    la recherche, la liste des pistes et un loader visible pendant l'import.
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

        # ── Boutons d'import (références stockées pour les désactiver) ───────
        self._btn_files = ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.AUDIO_FILE, size=16, color=ObsidianColors.ON_PRIMARY),
                    ft.Text(
                        "Parcourir Fichiers",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.ON_PRIMARY,
                    ),
                ],
                spacing=6,
            ),
            style=ft.ButtonStyle(bgcolor=ObsidianColors.PRIMARY, mouse_cursor=ft.MouseCursor.CLICK),
            on_click=lambda e: (e.page.run_task(self.on_pick_files) if self.on_pick_files else None),
        )

        self._btn_folder = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER_OPEN, size=16),
                    ft.Text("Scanner un Dossier", size=12),
                ],
                spacing=6,
            ),
            style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
            on_click=lambda e: (e.page.run_task(self.on_pick_folder) if self.on_pick_folder else None),
        )

        # ── Indicateur de chargement ─────────────────────────────────────────
        self._loader_text = ft.Text(
            "Analyse en cours…",
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )
        self._loader_ring = ft.ProgressRing(
            width=20,
            height=20,
            stroke_width=2.5,
            color=ObsidianColors.PRIMARY,  # brand — explicit
        )
        self._loader_row = ft.Row(
            [self._loader_ring, self._loader_text],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False,  # Masqué par défaut
        )

        # ── Zone d'importation (Dropzone) ────────────────────────────────────
        self.dropzone = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.CLOUD_UPLOAD_OUTLINED,
                        size=34,
                        color=ObsidianColors.PRIMARY,  # brand — explicit
                    ),
                    ft.Text(
                        "Bibliothèque Musicale AIC",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        r"Sélectionnez des fichiers audio ou scannez un dossier (D:\Musique, E:\FLAC…)",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=4),
                    ft.Row(
                        [self._btn_files, self._btn_folder],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    self._loader_row,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            padding=Spacing.LG,
            border_radius=Radii.LG,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
        )

        # ── Barre de Recherche et Filtres ────────────────────────────────────
        self.search_entry = ft.TextField(
            hint_text="Rechercher par nom de fichier...",
            prefix_icon=ft.Icons.SEARCH,
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
            selected_color=ObsidianColors.PRIMARY_GLOW,
            on_select=self._handle_filter_toggle,
        )

        # ── Liste scrollable des morceaux (ListView) ─────────────────────────
        self.track_list = ft.ListView(
            expand=True,
            spacing=Spacing.SM,
            padding=ft.Padding.only(right=6),
        )

        # ── État Vide (Empty State) ──────────────────────────────────────────
        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.MUSIC_OFF_OUTLINED,
                        size=48,
                        color=ObsidianColors.TEXT_DISABLED,
                    ),
                    ft.Text(
                        "Aucun morceau dans la bibliothèque",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        "Importez des fichiers ou scannez un dossier pour alimenter l'IA.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment.CENTER,
            padding=40,
        )

        self._is_loading = False

        super().__init__(
            content=ft.Column(
                [
                    self.dropzone,
                    ft.Row([self.search_entry, self.filter_chip], spacing=12),
                    ft.Container(content=self.track_list, expand=True),
                ],
                spacing=Spacing.MD,
                expand=True,
            ),
            padding=Spacing.LG,
            expand=True,
        )

    # ── API Loader ──────────────────────────────────────────────────────────
    def set_loading(self, loading: bool, message: str = "Analyse en cours…") -> None:
        """
        Active / désactive l'état de chargement :
        - Affiche / cache le ProgressRing et le message
        - Désactive / réactive les boutons d'import
        Doit être appelé depuis le thread UI (ou via page.run_task).
        """
        self._is_loading = loading
        self._loader_text.value = message
        disabled = loading or app_state.is_processing
        self._btn_files.disabled = disabled
        self._btn_folder.disabled = disabled

        cursor = (
            ft.MouseCursor.WAIT
            if loading
            else (ft.MouseCursor.FORBIDDEN if app_state.is_processing else ft.MouseCursor.CLICK)
        )
        self._btn_files.style.mouse_cursor = cursor
        self._btn_folder.style.mouse_cursor = cursor
        self._loader_row.visible = loading
        try:
            self._btn_files.update()
            self._btn_folder.update()
            self._loader_row.update()
        except RuntimeError:
            pass

    # ── Rafraîchissement de la liste ─────────────────────────────────────────
    def refresh_tracks(self) -> None:
        """Mise à jour réactive des items de morceaux dans la liste."""
        is_disabled = getattr(self, "_is_loading", False) or app_state.is_processing
        self._btn_files.disabled = is_disabled
        self._btn_folder.disabled = is_disabled
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

    def _handle_search_change(self, e) -> None:
        if self.on_search:
            self.on_search(e.control.value)

    def _handle_filter_toggle(self, e) -> None:
        app_state.session.filter_liked_only = e.control.selected
        self.refresh_tracks()
