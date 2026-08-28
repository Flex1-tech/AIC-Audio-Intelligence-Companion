import os
import pathlib
import sys
import threading

import flet as ft

from core.state import app_state
from controllers.library_controller import LibraryController
from controllers.recommendation_controller import RecommendationController
from services.ai_engine_service import AIEngineService
from services.database_service import DatabaseService
from ui.components.result_dialog import ResultDialog
from ui.components.splash_screen import SplashScreen
from ui.design_system import get_dark_theme, get_light_theme
from ui.design_system.colors import ObsidianColors
from ui.views.main_layout import MainLayout
from utils.path_utils import setup_logging, get_asset_path, write_crash_log, open_folder

# Initialisation du logger applicatif centralisé
logger = setup_logging()

# ── Configuration du cache Numba cross-plateforme (Windows, macOS, Linux) ──────
if os.name == "nt":
    _base_cache = pathlib.Path(os.environ.get("LOCALAPPDATA") or pathlib.Path.home() / "AppData" / "Local")
elif sys.platform == "darwin":
    _base_cache = pathlib.Path.home() / "Library" / "Caches"
else:  # Linux / Unix
    _xdg_cache = os.environ.get("XDG_CACHE_HOME")
    _base_cache = pathlib.Path(_xdg_cache) if _xdg_cache else pathlib.Path.home() / ".cache"

_aic_numba_cache = _base_cache / "AIC" / "numba_cache"
try:
    _aic_numba_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("NUMBA_CACHE_DIR", str(_aic_numba_cache))
except Exception:
    pass  # Fallback silencieux : Numba utilisera le répertoire par défaut


def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Hook enrichi : log via le logger ET via write_crash_log."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Écriture systématique dans aic_crash.log (%APPDATA%/AIC/logs/aic_crash.log, CWD, Home)
    write_crash_log(exc_type, exc_value, exc_traceback, origin="UNCAUGHT_MAIN_PROCESS")
    # Écriture dans aic.log (logger applicatif)
    logger.critical("Uncaught exception in main process:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = _handle_uncaught_exception


def _handle_thread_exception(args):
    write_crash_log(args.exc_type, args.exc_value, args.exc_traceback, origin="UNCAUGHT_THREAD_EXCEPTION")
    logger.error(
        "Uncaught exception in background thread:", exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )


threading.excepthook = _handle_thread_exception


def main(page: ft.Page) -> None:
    """Initialise la page Flet, les services et les événements UI."""
    try:
        page.title = "AIC — Audio Intelligence Companion"
        page.bgcolor = ObsidianColors.BG_DARK  # Dark background during splash
        page.theme_mode = ft.ThemeMode.DARK

        font_bold = get_asset_path("fonts/CinzelDecorative-Bold.ttf")
        font_regular = get_asset_path("fonts/CinzelDecorative-Regular.ttf")
        fonts_dict = {}
        if font_bold and font_bold.exists():
            fonts_dict["Cinzel Decorative Bold"] = str(font_bold)
        if font_regular and font_regular.exists():
            fonts_dict["Cinzel Decorative Regular"] = str(font_regular)
        if fonts_dict:
            page.fonts = fonts_dict

        icon_path = get_asset_path("icon.ico") or get_asset_path("icon.png")
        if icon_path and icon_path.exists():
            try:
                page.window.icon = str(icon_path)
            except Exception as e:
                logger.warning(f"Impossible de définir l'icône de fenêtre : {e}")

        page.theme = get_light_theme()
        page.dark_theme = get_dark_theme()
        page.window.width = app_state.session.window_width
        page.window.height = app_state.session.window_height
        page.window.min_width = 850
        page.window.min_height = 600
        page.padding = 0

        ai_service = AIEngineService()
        db_service = DatabaseService()
        library_controller = LibraryController()
        rec_controller = RecommendationController()

        file_picker = ft.FilePicker()
        page.services.append(file_picker)

        def _show_toast(message: str, is_error: bool = False, duration: int = 4000) -> None:
            """Affiche une notification toast dismissible (croix × uniquement) sur le thread UI."""
            snack = ft.SnackBar(
                content=ft.Text(
                    message,
                    color=ObsidianColors.TEXT_WHITE if is_error else ObsidianColors.BG_DARK,
                ),
                bgcolor=ObsidianColors.ERROR_BG if is_error else ObsidianColors.PRIMARY,
                duration=duration,
                show_close_icon=True,
                close_icon_color=ObsidianColors.TEXT_WHITE if is_error else ObsidianColors.BG_DARK,
            )
            page.overlay.clear()
            page.overlay.append(snack)
            snack.open = True
            try:
                page.update()
            except Exception:
                pass

        async def handle_pick_files() -> None:
            if app_state.is_processing:
                _show_toast("Un traitement ou un import est déjà en cours. Veuillez patienter.", is_error=False)
                return
            layout.library_view.set_loading(True)
            files = await file_picker.pick_files(
                allow_multiple=True,
                dialog_title="Sélectionner des fichiers audio pour AIC",
            )
            if not files:
                layout.library_view.set_loading(False)
                return

            file_paths = [f.path for f in files if f.path]
            if not file_paths:
                layout.library_view.set_loading(False)
                return

            _show_toast(f"Importation de {len(file_paths)} fichier(s)…")

            def on_complete_files(valid_count: int, invalid_count: int) -> None:
                async def _finish() -> None:
                    app_state.session.filter_liked_only = False
                    app_state.session.search_query = ""
                    layout.library_view.search_entry.value = ""
                    layout.library_view.filter_chip.selected = False
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) ajouté(s) ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_files_async(file_paths, on_complete=on_complete_files)

        async def handle_pick_folder() -> None:
            if app_state.is_processing:
                _show_toast("Un traitement ou un import est déjà en cours. Veuillez patienter.", is_error=False)
                return
            layout.library_view.set_loading(True)
            folder_path = await file_picker.get_directory_path(
                dialog_title="Sélectionner un dossier musical pour AIC",
            )
            if not folder_path:
                layout.library_view.set_loading(False)
                return

            _show_toast(f"Balayage du dossier : {folder_path}…")

            def on_complete_folder(valid_count: int, invalid_count: int) -> None:
                async def _finish() -> None:
                    app_state.session.filter_liked_only = False
                    app_state.session.search_query = ""
                    layout.library_view.search_entry.value = ""
                    layout.library_view.filter_chip.selected = False
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) indexé(s) depuis le dossier ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_folder_async(folder_path, on_complete=on_complete_folder)

        def handle_like_track(file_path: str) -> None:
            if app_state.is_processing:
                _show_toast("Impossible de modifier les likes pendant un traitement.", is_error=False)
                return
            library_controller.toggle_like(file_path)

        def handle_delete_track(file_path: str) -> None:
            if app_state.is_processing:
                _show_toast("Impossible de supprimer un morceau pendant un traitement.", is_error=False)
                return
            library_controller.remove_track(file_path)

        def handle_search(query: str) -> None:
            library_controller.set_search_query(query)

        def handle_reset() -> None:
            if app_state.is_processing:
                _show_toast("Impossible de réinitialiser la bibliothèque pendant un traitement.", is_error=False)
                return
            if app_state.library.total_tracks_count == 0:
                _show_toast("La bibliothèque est déjà vide.", is_error=False)
                return
            library_controller.reset_library()
            _show_toast("Bibliothèque réinitialisée.")

        def handle_theme_toggle(_e) -> None:
            current_mode = page.theme_mode
            if current_mode == ft.ThemeMode.DARK:
                new_mode = ft.ThemeMode.LIGHT
            else:
                new_mode = ft.ThemeMode.DARK
            page.theme_mode = new_mode
            page.bgcolor = ft.Colors.SURFACE
            app_state.session.theme_mode = "light" if new_mode == ft.ThemeMode.LIGHT else "dark"
            page.update()

        async def handle_pick_export_folder() -> None:
            folder_path = await file_picker.get_directory_path(
                dialog_title="Sélectionner le dossier d'exportation des playlists",
            )
            if folder_path:
                app_state.session.export_folder_path = folder_path
                layout.settings_view.update_export_folder(folder_path)
                _show_toast(f"Dossier d'exportation mis à jour : {folder_path}")

        def handle_start_recommendation() -> None:
            if app_state.is_processing:
                _show_toast("Un calcul de recommandation est déjà en cours. Veuillez patienter.", is_error=False)
                return
            total_count = app_state.library.total_tracks_count
            liked_count = app_state.library.liked_tracks_count
            if total_count == 0:
                _show_toast(
                    "Aucune chanson dans la bibliothèque. Importez des fichiers audio pour commencer.",
                    is_error=False,
                    duration=5000,
                )
                return
            if not app_state.library.is_recommendation_ready:
                if liked_count == 0:
                    _show_toast(
                        "Aucune chanson likée. Likez au moins 3 chansons pour générer une playlist.",
                        is_error=False,
                        duration=5000,
                    )
                else:
                    remaining = max(0, 3 - liked_count)
                    _show_toast(
                        f"Vous avez {liked_count}/3 morceau(x) liké(s). Likez encore {remaining} morceau(x) pour générer la playlist.",
                        is_error=False,
                        duration=5000,
                    )
                return

            def on_success(export_res) -> None:
                async def _open_modal() -> None:
                    def _do_open_folder() -> None:
                        success = open_folder(export_res.folder_path)
                        if not success:
                            _show_toast("Impossible d'ouvrir le dossier de destination.", is_error=True)

                    async def _do_change_folder() -> None:
                        page.pop_dialog()
                        await handle_pick_export_folder()

                    dialog = ResultDialog(
                        count=export_res.track_count,
                        file_name=export_res.file_name,
                        file_path=export_res.file_path,
                        folder_path=export_res.folder_path,
                        on_launch_vlc=_launch_vlc,
                        on_open_folder=_do_open_folder,
                        on_change_folder=_do_change_folder,
                        on_close=lambda: page.pop_dialog(),
                    )
                    page.show_dialog(dialog)

                page.run_task(_open_modal)

            def on_error(err: str) -> None:
                # Traduit les erreurs techniques en messages utilisateur intelligibles
                user_msg = err
                if "no locator available" in err or "cannot cache function" in err:
                    user_msg = "Erreur de configuration du cache audio. Redémarrez l'application."
                elif "FileNotFoundError" in err or "ffmpeg" in err.lower():
                    user_msg = "Fichier audio introuvable ou format non supporté."
                elif "OutOfMemoryError" in err or "MemoryError" in err:
                    user_msg = "Mémoire insuffisante pour traiter les fichiers. Réduisez le nombre de morceaux."
                elif len(err) > 120:
                    # Tronquer les messages techniques trop longs
                    user_msg = err[:120] + "…"

                async def _show_err() -> None:
                    _show_toast(f"Erreur recommandation : {user_msg}", is_error=True, duration=6000)

                page.run_task(_show_err)

            rec_controller.run_recommendation_async(on_success=on_success, on_error=on_error)

        def _launch_vlc() -> None:
            if not app_state.session.last_generated_playlist_path:
                _show_toast(
                    "Aucune playlist n'a encore été générée. Cliquez d'abord sur 'Générer la Playlist IA'.",
                    is_error=False,
                )
                return
            success, msg = rec_controller.launch_vlc()
            _show_toast(msg, is_error=not success)

        layout = MainLayout(
            on_pick_files=handle_pick_files,
            on_pick_folder=handle_pick_folder,
            on_like_track=handle_like_track,
            on_delete_track=handle_delete_track,
            on_search=handle_search,
            on_start_recommendation=handle_start_recommendation,
            on_reset=handle_reset,
            on_theme_toggle=handle_theme_toggle,
            on_pick_export_folder=handle_pick_export_folder,
        )

        splash_active = True

        def on_state_change() -> None:
            try:
                if not splash_active:
                    layout.update_all()
                    page.update()
            except Exception:
                pass

        app_state.subscribe(on_state_change)

        # ── Intégration du Splash Screen & Main Layout ────────────────────────
        def finish_splash() -> None:
            nonlocal splash_active
            logger.info("SPLASH: FINISH")
            try:
                splash_active = False
                if splash_screen in root_stack.controls:
                    root_stack.controls.remove(splash_screen)
                    logger.info("SPLASH: REMOVED")
                page.theme_mode = ft.ThemeMode.SYSTEM
                page.bgcolor = ft.Colors.SURFACE
                root_stack.update()
                layout.update_all()
                page.update()
            except Exception as e:
                logger.error(f"Erreur lors du retrait du Splash Screen : {e}", exc_info=True)

        splash_screen = SplashScreen(page=page, on_complete=finish_splash)

        root_stack = ft.Stack(
            [
                layout,
                splash_screen,
            ],
            expand=True,
        )

        page.add(root_stack)
        logger.info("SPLASH: ATTACHED")

        async def run_splash_task() -> None:
            try:
                try:
                    if page.window:
                        await page.window.to_front()
                except Exception as focus_err:
                    logger.debug(f"window.to_front() non disponible sur cette plateforme : {focus_err}")
                await splash_screen.start_animation_async()
            except Exception as splash_err:
                write_crash_log(type(splash_err), splash_err, splash_err.__traceback__, origin="SPLASH_ANIMATION_ERROR")
                logger.error(f"Erreur animation Splash Screen : {splash_err}", exc_info=True)
                finish_splash()

        page.run_task(run_splash_task)

        def preload_background() -> None:
            try:
                logger.info("Préchargement des ressources IA et base de données en arrière-plan...")
                ai_service.preload_resources()
                db_service.initialize_db()
                app_state.notify()
                logger.info("Préchargement des ressources terminé avec succès.")
            except Exception as e:
                write_crash_log(type(e), e, e.__traceback__, origin="PRELOAD_BACKGROUND_ERROR")
                logger.error(f"Erreur lors du préchargement en arrière-plan : {e}", exc_info=True)

        threading.Thread(target=preload_background, daemon=True).start()

    except Exception as fatal_err:
        log_file_path = write_crash_log(
            type(fatal_err), fatal_err, fatal_err.__traceback__, origin="FATAL_STARTUP_ERROR"
        )
        logger.critical("Erreur fatale au démarrage d'AIC:", exc_info=True)
        try:
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINED, color=ObsidianColors.ERROR, size=48),
                            ft.Text(
                                "Erreur lors du démarrage d'AIC",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ObsidianColors.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                f"Détails de l'erreur : {fatal_err}",
                                size=13,
                                color=ObsidianColors.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"Le journal détaillé a été enregistré dans :\n{log_file_path}",
                                size=12,
                                color=ObsidianColors.TEXT_MUTED,
                                font_family="monospace",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                    expand=True,
                )
            )
        except Exception:
            pass


if __name__ == "__main__":
    try:
        ft.run(main)
    except Exception as main_run_err:
        write_crash_log(type(main_run_err), main_run_err, main_run_err.__traceback__, origin="FT_RUN_MAIN_ERROR")
        sys.exit(1)
