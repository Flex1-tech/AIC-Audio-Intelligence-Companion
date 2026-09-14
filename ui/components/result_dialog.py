import inspect
import logging
from pathlib import Path
from typing import Any, Callable, List, Optional

import flet as ft
from core.state import app_state
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing

logger = logging.getLogger("aic.ui.result_dialog")


async def _await_coroutine(coro: Any) -> Any:
    """Helper coroutine function pour exécuter et awaiter une coroutine déjà instanciée via page.run_task."""
    return await coro


class ResultDialog(ft.AlertDialog):
    """
    Modal de découverte post-recommandation Obsidian Horizon.
    
    Hiérarchie UX stricte :
    1. Célébration & Statut (Playlist générée et automatiquement exportée)
    2. Hero Action : « Écouter avec VLC »
    3. Cartouche d'Export Actuel :
       - Chemin d'export clair et concis
       - « Ouvrir le dossier » (accès rapide direct)
       - « Exporter vers… » (export ponctuel vers une autre destination)
       - (Optionnel) « Définir comme dossier par défaut »
    4. Volet dépliable des morceaux recommandés avec scores MMR
    5. Footer discret :
       - « Régénérer »
       - « Changer de bibliothèque »
       - « Fermer »
    """

    def __init__(
        self,
        count: int,
        file_name: str = "AIC Playlist.m3u8",
        file_path: str = "",
        folder_path: str = "",
        playlist_paths: Optional[List[str]] = None,
        lambda_mmr: float = 0.7,
        is_default_folder: bool = True,
        on_launch_vlc: Optional[Callable[[], Any]] = None,
        on_open_folder: Optional[Callable[[str], Any]] = None,
        on_export_to: Optional[Callable[[], Any]] = None,
        on_set_as_default: Optional[Callable[[str], Any]] = None,
        on_regenerate: Optional[Callable[[], Any]] = None,
        on_change_library: Optional[Callable[[], Any]] = None,
        on_close: Optional[Callable[[], Any]] = None,
        on_change_folder: Optional[Callable[[], Any]] = None,  # Rétrocompatibilité
    ):
        self.count = count
        self.file_name = file_name
        self.file_path = file_path
        self.folder_path = folder_path
        self.playlist_paths = playlist_paths or []
        self.lambda_mmr = lambda_mmr
        self._is_current_default = is_default_folder

        self._on_launch_vlc = on_launch_vlc
        self._on_open_folder = on_open_folder
        self._on_export_to = on_export_to or on_change_folder
        self._on_set_as_default = on_set_as_default
        self._on_regenerate = on_regenerate
        self._on_change_library = on_change_library
        self._on_close = on_close
        self._on_change_folder = on_change_folder

        # Calcul de la durée totale estimée
        total_duration_sec = 0.0
        for path in self.playlist_paths:
            if path in app_state.library.tracks:
                dur = app_state.library.tracks[path].duration_seconds
                if dur > 0:
                    total_duration_sec += dur
        if total_duration_sec <= 0:
            total_duration_sec = self.count * 210.0  # Estimation moyenne 3.5 min

        estimated_minutes = max(1, round(total_duration_sec / 60))

        # ── Composants d'état réactifs ──────────────────────────────────────────
        self._export_status_text = ft.Text(
            "Exportée automatiquement dans :" if self._is_current_default else "Exportée dans :",
            size=12,
            color=ObsidianColors.TEXT_MUTED,
        )

        self._export_path_text = ft.Text(
            self._format_display_path(self.folder_path, self.file_name),
            size=12,
            weight=ft.FontWeight.W_500,
            font_family="monospace",
            color=ObsidianColors.TEXT_PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            tooltip=self.file_path or self.folder_path,
        )

        self._set_default_btn = ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.BOOKMARK_BORDER_ROUNDED, size=14, color=ObsidianColors.PRIMARY),
                    ft.Text(
                        "Définir comme dossier par défaut",
                        size=11,
                        color=ObsidianColors.PRIMARY,
                    ),
                ],
                spacing=4,
                tight=True,
            ),
            style=ft.ButtonStyle(
                padding=ft.Padding(4, 2, 4, 2),
                mouse_cursor=ft.MouseCursor.CLICK,
            ),
            visible=not self._is_current_default,
            on_click=self._handle_set_default,
        )

        # Volet déroulant des pistes recommandées
        self._tracks_list_view = self._build_tracks_view()
        self._tracks_container = ft.Container(
            content=self._tracks_list_view,
            visible=False,
            height=160,
            bgcolor=ObsidianColors.SURFACE_DARK,
            border_radius=Radii.SM,
            padding=Spacing.SM,
            border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
        )

        self._toggle_tracks_icon = ft.Icon(
            ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
            size=18,
            color=ObsidianColors.TEXT_SECONDARY,
        )

        # ── Construction de la modale ─────────────────────────────────────────
        super().__init__(
            modal=True,
            content=ft.Container(
                width=520,
                content=ft.Column(
                    [
                        # 1. En-tête : Célébration & Statut
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_ROUNDED,
                                        color=ObsidianColors.SUCCESS,
                                        size=22,
                                    ),
                                    bgcolor=ObsidianColors.SUCCESS_BG,
                                    padding=6,
                                    border_radius=Radii.FULL,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Votre playlist est prête",
                                            size=17,
                                            weight=ft.FontWeight.BOLD,
                                            color=ObsidianColors.TEXT_PRIMARY,
                                        ),
                                        ft.Text(
                                            f"{self.count} morceaux recommandés  •  ~{estimated_minutes} min",
                                            size=12,
                                            color=ObsidianColors.TEXT_SECONDARY,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        f"MMR λ={self.lambda_mmr:.1f}",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=ObsidianColors.ACCENT_CYAN,
                                    ),
                                    bgcolor=ObsidianColors.ACCENT_CYAN_GLOW,
                                    padding=ft.Padding(8, 4, 8, 4),
                                    border_radius=Radii.SM,
                                    border=ft.Border.all(1, ObsidianColors.ACCENT_CYAN),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=4),

                        # 2. Hero Action : Écouter avec VLC (Action Principale #1)
                        ft.Container(
                            content=ft.FilledButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.PLAY_ARROW_ROUNDED,
                                            size=22,
                                            color=ObsidianColors.TEXT_ON_PRIMARY,
                                        ),
                                        ft.Text(
                                            "Écouter avec VLC",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=ObsidianColors.TEXT_ON_PRIMARY,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor={
                                        ft.ControlState.DEFAULT: ObsidianColors.PRIMARY,
                                        ft.ControlState.HOVERED: ObsidianColors.PRIMARY_HOVER,
                                    },
                                    shape=ft.RoundedRectangleBorder(radius=Radii.MD),
                                    padding=ft.Padding(16, 12, 16, 12),
                                    mouse_cursor=ft.MouseCursor.CLICK,
                                ),
                                on_click=self._handle_vlc,
                            ),
                            width=520,
                        ),
                        ft.Container(height=2),

                        # 3. Cartouche d'Export Actuel
                        ft.Container(
                            content=ft.Column(
                                [
                                    # Ligne d'information d'emplacement
                                    ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.FOLDER_OUTLINED,
                                                size=16,
                                                color=ObsidianColors.PRIMARY,
                                            ),
                                            self._export_status_text,
                                        ],
                                        spacing=6,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Container(
                                        content=self._export_path_text,
                                        padding=ft.Padding(6, 4, 6, 4),
                                        bgcolor=ObsidianColors.BG_DARK,
                                        border_radius=Radii.SM,
                                        border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
                                    ),
                                    # Rangée d'actions sur l'export
                                    ft.Row(
                                        [
                                            ft.OutlinedButton(
                                                content=ft.Row(
                                                    [
                                                        ft.Icon(
                                                            ft.Icons.FOLDER_OPEN_ROUNDED,
                                                            size=15,
                                                            color=ObsidianColors.TEXT_PRIMARY,
                                                        ),
                                                        ft.Text(
                                                            "Ouvrir le dossier",
                                                            size=12,
                                                            color=ObsidianColors.TEXT_PRIMARY,
                                                        ),
                                                    ],
                                                    spacing=6,
                                                    tight=True,
                                                ),
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=Radii.SM),
                                                    side={
                                                        ft.ControlState.DEFAULT: ft.BorderSide(
                                                            1, ObsidianColors.BORDER_DARK
                                                        ),
                                                        ft.ControlState.HOVERED: ft.BorderSide(
                                                            1, ObsidianColors.TEXT_SECONDARY
                                                        ),
                                                    },
                                                    mouse_cursor=ft.MouseCursor.CLICK,
                                                ),
                                                on_click=self._handle_open_folder,
                                            ),
                                            ft.OutlinedButton(
                                                content=ft.Row(
                                                    [
                                                        ft.Icon(
                                                            ft.Icons.DRIVE_FILE_MOVE_OUTLINED,
                                                            size=15,
                                                            color=ObsidianColors.ACCENT_CYAN,
                                                        ),
                                                        ft.Text(
                                                            "Exporter vers…",
                                                            size=12,
                                                            color=ObsidianColors.ACCENT_CYAN,
                                                        ),
                                                    ],
                                                    spacing=6,
                                                    tight=True,
                                                ),
                                                style=ft.ButtonStyle(
                                                    shape=ft.RoundedRectangleBorder(radius=Radii.SM),
                                                    side={
                                                        ft.ControlState.DEFAULT: ft.BorderSide(
                                                            1, ObsidianColors.BORDER_DARK
                                                        ),
                                                        ft.ControlState.HOVERED: ft.BorderSide(
                                                            1, ObsidianColors.ACCENT_CYAN
                                                        ),
                                                    },
                                                    mouse_cursor=ft.MouseCursor.CLICK,
                                                ),
                                                on_click=self._handle_export_to,
                                            ),
                                            self._set_default_btn,
                                        ],
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=Spacing.MD,
                            border_radius=Radii.MD,
                            bgcolor=ObsidianColors.SURFACE_ELEVATED,
                            border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
                        ),

                        # 4. Progressive Disclosure : Liste des morceaux
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.GestureDetector(
                                        content=ft.Row(
                                            [
                                                self._toggle_tracks_icon,
                                                ft.Text(
                                                    f"Voir les {self.count} morceaux recommandés",
                                                    size=12,
                                                    color=ObsidianColors.TEXT_SECONDARY,
                                                ),
                                            ],
                                            spacing=6,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        on_tap=self._toggle_tracks,
                                        mouse_cursor=ft.MouseCursor.CLICK,
                                    ),
                                    self._tracks_container,
                                ],
                                spacing=6,
                            ),
                            padding=ft.Padding(2, 2, 2, 2),
                        ),
                    ],
                    tight=True,
                    spacing=10,
                ),
            ),
            # 5. Footer d'actions discrètes
            actions=[
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.TextButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.REFRESH_ROUNDED,
                                                size=15,
                                                color=ObsidianColors.TEXT_SECONDARY,
                                            ),
                                            ft.Text(
                                                "Générer une autre playlist",
                                                size=12,
                                                color=ObsidianColors.TEXT_SECONDARY,
                                            ),
                                        ],
                                        spacing=5,
                                        tight=True,
                                    ),
                                    style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
                                    on_click=self._handle_regenerate,
                                ),
                                ft.TextButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.LIBRARY_MUSIC_OUTLINED,
                                                size=15,
                                                color=ObsidianColors.TEXT_SECONDARY,
                                            ),
                                            ft.Text(
                                                "Changer de bibliothèque",
                                                size=12,
                                                color=ObsidianColors.TEXT_SECONDARY,
                                            ),
                                        ],
                                        spacing=5,
                                        tight=True,
                                    ),
                                    style=ft.ButtonStyle(mouse_cursor=ft.MouseCursor.CLICK),
                                    on_click=self._handle_change_library,
                                ),
                            ],
                            spacing=6,
                        ),
                        ft.TextButton(
                            content="Fermer",
                            style=ft.ButtonStyle(
                                color={
                                    ft.ControlState.DEFAULT: ObsidianColors.TEXT_MUTED,
                                    ft.ControlState.HOVERED: ObsidianColors.TEXT_PRIMARY,
                                },
                                mouse_cursor=ft.MouseCursor.CLICK,
                            ),
                            on_click=self._handle_close,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            bgcolor=ObsidianColors.SURFACE_DARK,
            shape=ft.RoundedRectangleBorder(radius=Radii.LG),
            on_dismiss=self._handle_close,
        )

    def _format_display_path(self, folder_path: str, file_name: str) -> str:
        """Formate le chemin de manière élégante et concise."""
        if not folder_path:
            return file_name or "AIC Playlist.m3u8"
        p = Path(folder_path)
        # Afficher les 2 derniers composants du dossier + nom de fichier
        parts = p.parts
        if len(parts) > 2:
            concise_folder = f".../{parts[-2]}/{parts[-1]}"
        else:
            concise_folder = str(p)
        return f"{concise_folder} / {file_name}"

    def _build_tracks_view(self) -> ft.ListView:
        items = []
        for i, path in enumerate(self.playlist_paths, 1):
            track_obj = app_state.library.tracks.get(path)
            title = track_obj.file_name if track_obj else Path(path).name
            mmr_str = f"{track_obj.mmr_score:.2f}" if (track_obj and track_obj.mmr_score is not None) else ""

            items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                f"#{i:02d}",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=ObsidianColors.ACCENT_CYAN,
                                width=28,
                            ),
                            ft.Text(
                                title,
                                size=11,
                                color=ObsidianColors.TEXT_PRIMARY,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                            ft.Text(
                                f"Score MMR : {mmr_str}" if mmr_str else "",
                                size=10,
                                color=ObsidianColors.TEXT_MUTED,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.Padding(6, 3, 6, 3),
                    border_radius=Radii.SM,
                )
            )

        if not items:
            items.append(
                ft.Text(
                    f"{self.count} morceau(x) inclus dans la playlist .m3u8",
                    size=11,
                    color=ObsidianColors.TEXT_MUTED,
                )
            )

        return ft.ListView(controls=items, spacing=2, auto_scroll=False)

    def _toggle_tracks(self, _e=None) -> None:
        self._tracks_container.visible = not self._tracks_container.visible
        self._toggle_tracks_icon.name = (
            ft.Icons.KEYBOARD_ARROW_UP_ROUNDED
            if self._tracks_container.visible
            else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
        )
        try:
            if self.page:
                self.page.update()
        except RuntimeError:
            pass

    def update_export_location(
        self,
        folder_path: str,
        file_path: str,
        file_name: str,
        is_default: bool = False,
    ) -> None:
        """Met à jour l'affichage en place après un export ponctuel réussi."""
        self.folder_path = folder_path
        self.file_path = file_path
        self.file_name = file_name
        self._is_current_default = is_default

        self._export_status_text.value = (
            "Exportée automatiquement dans :" if is_default else "Exportée dans :"
        )
        self._export_path_text.value = self._format_display_path(folder_path, file_name)
        self._export_path_text.tooltip = file_path or folder_path
        self._set_default_btn.visible = not is_default

        page = self._get_page()
        if page:
            page.update()

    def mark_as_default(self) -> None:
        """Indique que l'emplacement actuel a été enregistré comme dossier par défaut."""
        self._is_current_default = True
        self._export_status_text.value = "Exportée dans (dossier par défaut) :"
        self._set_default_btn.visible = False
        page = self._get_page()
        if page:
            page.update()

    def _get_page(self) -> Optional[Any]:
        """Retourne la page Flet si le contrôle y est attaché, sinon None sans lever RuntimeError."""
        try:
            return self.page
        except RuntimeError:
            return None

    # ── Dispatching asynchrone sécurisé des callbacks ─────────────────────────
    def _safe_dispatch(self, callback: Optional[Callable[..., Any]], *args, **kwargs) -> None:
        """Exécute un callback de manière sécurisée en respectant l'API Flet 0.86.4.

        Règle Flet 0.86.4 :
          page.run_task(handler, *args, **kwargs) exige que `handler` soit une coroutine
          function (inspect.iscoroutinefunction(handler) is True). On ne peut PAS lui
          passer directement une coroutine déjà créée ni une lambda synchrone.

        Stratégie :
          1. Si callback est async def (inspect.iscoroutinefunction) :
             On passe directement la fonction à page.run_task(callback, *args, **kwargs).
             Flet appellera la fonction et awaitera la coroutine sur son event loop sans TypeError.
          2. Si callback est synchrone (ou wrapper / lambda synchrone) :
             On appelle le callback : res = callback(*args, **kwargs).
             Si res est une coroutine (inspect.iscoroutine(res)) :
               On passe la coroutine à page.run_task(_await_coroutine, res).
               Comme `_await_coroutine` est une vraie coroutine function (async def),
               Flet l'accepte et await la coroutine sans aucune TypeError ni RuntimeWarning.
               Si la page Flet n'est pas disponible, on ferme la coroutine (res.close())
               pour garantir qu'aucun RuntimeWarning 'never awaited' n'est émis.
        """
        if not callback:
            return
        try:
            page = self._get_page()
            if inspect.iscoroutinefunction(callback):
                if page:
                    page.run_task(callback, *args, **kwargs)
                else:
                    logger.warning(
                        "Impossible de dispatcher la coroutine : page Flet non disponible."
                    )
            else:
                res = callback(*args, **kwargs)
                if inspect.iscoroutine(res):
                    if page:
                        page.run_task(_await_coroutine, res)
                    else:
                        logger.warning(
                            "Impossible d'attendre la coroutine : page Flet non disponible."
                        )
                        res.close()
        except Exception as err:
            logger.error(f"Erreur callback ResultDialog : {err}", exc_info=True)

    def _handle_close(self, _e=None) -> None:
        self._safe_dispatch(self._on_close)

    def _handle_vlc(self, _e=None) -> None:
        self._safe_dispatch(self._on_launch_vlc)

    def _handle_open_folder(self, _e=None) -> None:
        self._safe_dispatch(self._on_open_folder, self.folder_path)

    def _handle_export_to(self, _e=None) -> None:
        self._safe_dispatch(self._on_export_to)

    def _handle_set_default(self, _e=None) -> None:
        self._safe_dispatch(self._on_set_as_default, self.folder_path)

    def _handle_regenerate(self, _e=None) -> None:
        self._safe_dispatch(self._on_regenerate)

    def _handle_change_library(self, _e=None) -> None:
        self._safe_dispatch(self._on_change_library)


# Alias sémantique
RecommendationDiscoveryModal = ResultDialog
