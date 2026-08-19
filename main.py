"""Point d'entrée de l'application et initialisation de l'interface Flet."""

import datetime
import os
import pathlib
import sys
import traceback


def trace(msg: str) -> None:
    """Traceur de diagnostic bas-niveau : écrit immédiatement chaque étape sur disque."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    pid = os.getpid()
    log_line = f"[{timestamp}] [PID {pid}] {msg}\n"
    print(log_line, end="", flush=True)

    targets = [
        pathlib.Path("aic_boot_trace.log"),
        pathlib.Path.home() / "aic_boot_trace.log",
    ]
    appdata = os.environ.get("APPDATA")
    if appdata:
        targets.append(pathlib.Path(appdata) / "AIC" / "logs" / "aic_boot_trace.log")

    for dest in targets:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            pass


trace("=== DIAGNOSTIC BOOT START ===")
trace(f"STEP 00: Python executable = {sys.executable}")
trace(f"STEP 01: Python version = {sys.version}")
trace(f"STEP 02: CWD = {pathlib.Path.cwd()}")
trace(f"STEP 03: sys.path = {sys.path}")


def trace_environment_and_assets() -> None:
    """Diagnostic exhaustif de l'environnement de runtime et de la résolution des 8 assets critiques."""
    trace("=== SYSTEM & ENVIRONMENT DIAGNOSTIC ===")
    trace(f"sys.executable  = {sys.executable}")
    trace(f"sys.argv        = {sys.argv}")
    trace(f"sys.prefix      = {getattr(sys, 'prefix', None)}")
    trace(f"sys.base_prefix = {getattr(sys, 'base_prefix', None)}")
    trace(f"sys.frozen      = {getattr(sys, 'frozen', None)}")
    trace(f"sys._MEIPASS    = {getattr(sys, '_MEIPASS', None)}")
    trace(f"CWD             = {pathlib.Path.cwd()}")
    try:
        trace(f"main.py path    = {pathlib.Path(__file__).resolve()}")
    except Exception as e:
        trace(f"main.py path err = {e}")

    exe_dir = pathlib.Path(sys.executable).resolve().parent
    trace(f"exe_dir         = {exe_dir}")

    assets_to_test = [
        "icon.ico",
        "icon.png",
        "icon.svg",
        "layer_letterform.svg",
        "layer_wave.svg",
        "msd-musicnn-1.onnx",
        "fonts/CinzelDecorative-Bold.ttf",
        "fonts/CinzelDecorative-Regular.ttf",
    ]

    trace("=== ASSET RESOLUTION DIAGNOSTIC ===")
    for asset in assets_to_test:
        try:
            resolved = get_asset_path(asset)
            exists = resolved.exists() if resolved else False
            is_file = resolved.is_file() if resolved else False
            direct_bundle_path = exe_dir / "data" / "flutter_assets" / "assets" / asset
            direct_exists = direct_bundle_path.exists()
            trace(
                f"ASSET '{asset}':\n"
                f"  get_asset_path() -> {resolved}\n"
                f"  EXISTS={exists} | IS_FILE={is_file}\n"
                f"  Direct Flutter Bundle ({direct_bundle_path}) -> EXISTS={direct_exists}"
            )
        except Exception as asset_err:
            trace(f"ASSET '{asset}' DIAGNOSTIC ERROR: {asset_err}")


# ── Configuration du cache Numba cross-plateforme (Windows, macOS, Linux) ──────
# Sans cela, Numba (@jit cache=True dans librosa/core/notation.py) tente
# d'écrire son cache dans le répertoire source du .py packagé, qui pointe
# vers le chemin CI runner introuvable sur la machine utilisateur.
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
trace(f"STEP 04: NUMBA_CACHE_DIR = {os.environ.get('NUMBA_CACHE_DIR', 'default')}")


def _early_crash_handler(exc_type, exc_value, exc_tb):
    lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    trace(f"FATAL UNCAUGHT EXCEPTION:\n{''.join(lines)}")
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _early_crash_handler

# ── Imports applicatifs instrumentés ─────────────────────────────────────────
trace("STEP 05: Importing threading...")
import threading  # noqa: E402

trace("STEP 06: Importing flet...")
import flet as ft  # noqa: E402

trace("STEP 07: Importing core.state...")
from core.state import app_state  # noqa: E402

trace("STEP 14: Importing controllers...")
from controllers.library_controller import LibraryController  # noqa: E402
from controllers.recommendation_controller import RecommendationController  # noqa: E402

trace("STEP 15: Importing services...")
from services.ai_engine_service import AIEngineService  # noqa: E402
from services.database_service import DatabaseService  # noqa: E402

trace("STEP 16: Importing UI components...")
from ui.components.result_dialog import ResultDialog  # noqa: E402
from ui.components.splash_screen import SplashScreen  # noqa: E402
from ui.design_system import get_dark_theme, get_light_theme  # noqa: E402
from ui.design_system.colors import ObsidianColors  # noqa: E402
from ui.views.main_layout import MainLayout  # noqa: E402
from utils.path_utils import setup_logging, get_asset_path, write_crash_log, open_folder  # noqa: E402

trace("STEP 17: All imports completed successfully OK")

# Initialisation du logger applicatif
logger = setup_logging()


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
    trace("MAIN STEP 0: Entering main(page)")
    trace_environment_and_assets()
    try:
        trace("MAIN STEP 1: Setting page title & theme mode...")
        page.title = "AIC — Audio Intelligence Companion"
        page.theme_mode = ft.ThemeMode.DARK

        trace("MAIN STEP 2: Registering fonts in page.fonts...")
        page.fonts = {
            "Cinzel Decorative Bold": "fonts/CinzelDecorative-Bold.ttf",
            "Cinzel Decorative Regular": "fonts/CinzelDecorative-Regular.ttf",
        }

        trace("MAIN STEP 3: Resolving window icon...")
        icon_path = get_asset_path("icon.ico") or get_asset_path("icon.png")
        if icon_path and icon_path.exists():
            try:
                page.window.icon = str(icon_path)
            except Exception as e:
                logger.warning(f"Impossible de définir l'icône de fenêtre : {e}")

        trace("MAIN STEP 4: Updating page themes and dimensions...")
        page.update()
        page.theme = get_light_theme()
        page.dark_theme = get_dark_theme()
        page.window.width = app_state.session.window_width
        page.window.height = app_state.session.window_height
        page.window.min_width = 850
        page.window.min_height = 600
        page.padding = 0

        trace("MAIN STEP 5: Instantiating AIEngineService...")
        ai_service = AIEngineService()
        trace("MAIN STEP 6: Instantiating DatabaseService...")
        db_service = DatabaseService()
        trace("MAIN STEP 7: Instantiating Controllers...")
        library_controller = LibraryController()
        rec_controller = RecommendationController()

        trace("MAIN STEP 8: Appending FilePicker service...")
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
            page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
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
            trace("[GENERATION_TRIGGER] handle_start_recommendation called!")
            print("[GENERATION_TRIGGER] handle_start_recommendation called!")
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

        trace("MAIN STEP 9: Instantiating MainLayout...")
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

        def on_state_change() -> None:
            try:
                layout.update_all()
                page.update()
            except Exception:
                pass

        trace("MAIN STEP 10: Subscribing to app_state...")
        app_state.subscribe(on_state_change)

        # ── Intégration du Splash Screen & Main Layout ────────────────────────
        def finish_splash() -> None:
            try:
                if splash_screen in root_stack.controls:
                    root_stack.controls.remove(splash_screen)
                    root_stack.update()
            except Exception:
                pass

        trace("MAIN STEP 11: Instantiating SplashScreen...")
        splash_screen = SplashScreen(page=page, on_complete=finish_splash)

        trace("MAIN STEP 12: Creating root_stack...")
        root_stack = ft.Stack(
            [
                layout,
                splash_screen,
            ],
            expand=True,
        )

        trace("MAIN STEP 13: Adding root_stack to page...")
        page.add(root_stack)

        trace("MAIN STEP 14: Scheduling splash animation task...")

        async def run_splash_task() -> None:
            try:
                trace("SPLASH TASK: Starting animation...")
                await splash_screen.start_animation_async()
                trace("SPLASH TASK: Animation complete OK")
            except Exception as splash_err:
                trace(f"SPLASH TASK ERROR: {splash_err}")
                write_crash_log(type(splash_err), splash_err, splash_err.__traceback__, origin="SPLASH_ANIMATION_ERROR")
                logger.error(f"Erreur animation Splash Screen : {splash_err}", exc_info=True)

        page.run_task(run_splash_task)

        trace("MAIN STEP 15: Starting background preload thread...")

        def preload_background() -> None:
            try:
                trace("PRELOAD THREAD: Preloading AI & Database resources...")
                ai_service.preload_resources()
                db_service.initialize_db()
                app_state.notify()
                trace("PRELOAD THREAD: Preload complete OK")
            except Exception as e:
                trace(f"PRELOAD THREAD ERROR: {e}")
                write_crash_log(type(e), e, e.__traceback__, origin="PRELOAD_BACKGROUND_ERROR")
                logger.error(f"Erreur lors du préchargement en arrière-plan : {e}", exc_info=True)

        threading.Thread(target=preload_background, daemon=True).start()
        trace("MAIN STEP 16: main(page) initialization loop completed successfully OK")

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
