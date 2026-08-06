"""Point d'entrée de l'application et initialisation de l'interface Flet."""

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
from utils.path_utils import setup_logging, get_asset_path, get_user_data_dir

# Initialisation du logger applicatif
logger = setup_logging()


def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception in main process:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = _handle_uncaught_exception


def _handle_thread_exception(args):
    logger.error(
        "Uncaught exception in background thread:", exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )


threading.excepthook = _handle_thread_exception


def main(page: ft.Page) -> None:
    """Initialise la page Flet, les services et les événements UI."""
    try:
        page.title = "AIC — Audio Intelligence Companion"
        page.theme_mode = ft.ThemeMode.DARK

        # Polices embarquées localement (.ttf pour compatibilité Flutter Desktop)
        # Cinzel Decorative — assets/fonts/ (TTF officiel)
        page.fonts = {
            "Cinzel Decorative Bold": "fonts/CinzelDecorative-Bold.ttf",
            "Cinzel Decorative Regular": "fonts/CinzelDecorative-Regular.ttf",
        }

        # Résolution sécurisée de l'icône de fenêtre avec vérification d'existence
        icon_path = get_asset_path("icon.ico") or get_asset_path("icon.png")
        if icon_path and icon_path.exists():
            try:
                page.window.icon = str(icon_path)
            except Exception as e:
                logger.warning(f"Impossible de définir l'icône de fenêtre : {e}")

        page.update()
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

        def _show_toast(message: str, is_error: bool = False) -> None:
            """Affiche une notification toast sur le thread UI avec contraste WCAG optimisé."""
            snack = ft.SnackBar(
                content=ft.Text(
                    message,
                    color=ObsidianColors.TEXT_WHITE if is_error else ObsidianColors.BG_DARK,
                ),
                bgcolor=ObsidianColors.ERROR_BG if is_error else ObsidianColors.PRIMARY,
                duration=4000,
            )
            page.overlay.append(snack)
            snack.open = True
            try:
                page.update()
            except Exception:
                pass

        async def handle_pick_files() -> None:
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
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) ajouté(s) ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_files_async(file_paths, on_complete=on_complete_files)

        async def handle_pick_folder() -> None:
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
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) indexé(s) depuis le dossier ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_folder_async(folder_path, on_complete=on_complete_folder)

        def handle_like_track(file_path: str) -> None:
            library_controller.toggle_like(file_path)

        def handle_delete_track(file_path: str) -> None:
            library_controller.remove_track(file_path)

        def handle_search(query: str) -> None:
            library_controller.set_search_query(query)

        def handle_reset() -> None:
            library_controller.reset_library()
            _show_toast("Bibliothèque réinitialisée.")

        def handle_theme_toggle(_e) -> None:
            page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
            page.update()

        def handle_start_recommendation() -> None:
            def on_success(playlist_paths: list) -> None:
                async def _open_modal() -> None:
                    dialog = ResultDialog(
                        count=len(playlist_paths),
                        file_path=app_state.session.last_generated_playlist_path,
                        on_launch_vlc=_launch_vlc,
                        on_close=lambda: page.pop_dialog(),
                    )
                    page.show_dialog(dialog)

                page.run_task(_open_modal)

            def on_error(err: str) -> None:
                async def _show_err() -> None:
                    _show_toast(f"Erreur : {err}", is_error=True)

                page.run_task(_show_err)

            rec_controller.run_recommendation_async(on_success=on_success, on_error=on_error)

        def _launch_vlc() -> None:
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
        )

        def on_state_change() -> None:
            try:
                layout.update_all()
                page.update()
            except Exception:
                pass

        app_state.subscribe(on_state_change)

        # ── Intégration du Splash Screen & Main Layout ────────────────────────
        def finish_splash() -> None:
            try:
                if splash_screen in root_stack.controls:
                    root_stack.controls.remove(splash_screen)
                    root_stack.update()
            except Exception:
                pass

        splash_screen = SplashScreen(page=page, on_complete=finish_splash)

        root_stack = ft.Stack(
            [
                layout,
                splash_screen,
            ],
            expand=True,
        )

        page.add(root_stack)

        async def run_splash_task() -> None:
            await splash_screen.start_animation_async()

        page.run_task(run_splash_task)

        def preload_background() -> None:
            try:
                ai_service.preload_resources()
                db_service.initialize_db()
                app_state.notify()
            except Exception as e:
                logger.error(f"Erreur lors du préchargement en arrière-plan : {e}", exc_info=True)

        threading.Thread(target=preload_background, daemon=True).start()

    except Exception as fatal_err:
        logger.critical("Erreur fatale au démarrage d'AIC:", exc_info=True)
        log_file_path = get_user_data_dir() / "logs" / "aic.log"
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


if __name__ == "__main__":
    ft.run(main)
