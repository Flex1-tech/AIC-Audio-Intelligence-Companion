import flet as ft
import threading
from typing import Optional

from core.state import app_state
from services.ai_engine_service import AIEngineService
from services.database_service import DatabaseService
from controllers.library_controller import LibraryController
from controllers.recommendation_controller import RecommendationController
from ui.design_system import get_obsidian_theme
from ui.views.main_layout import MainLayout
from ui.components.result_dialog import ResultDialog

def main(page: ft.Page):
    # 1. Configuration de la fenêtre et du thème Flet Obsidian Horizon
    page.title = "AIC — Audio Intelligence Companion"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_obsidian_theme()
    page.window_width = app_state.session.window_width
    page.window_height = app_state.session.window_height
    page.window_min_width = 850
    page.window_min_height = 600
    page.padding = 0

    # 2. Instanciation des Services et Contrôleurs
    ai_service = AIEngineService()
    db_service = DatabaseService()
    library_controller = LibraryController()
    rec_controller = RecommendationController()

    # 3. FilePicker Flet Native
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    # 4. Handlers d'événements UI
    def handle_pick_files():
        file_picker.pick_files(
            allow_multiple=True,
            dialog_title="Sélectionner des fichiers audio pour AIC",
        )

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_paths = [f.path for f in e.files if f.path]
            show_toast(f"Importation de {len(file_paths)} fichier(s)...")
            
            def on_complete(valid_count, invalid_count):
                page.run_thread(lambda: show_toast(f"{valid_count} morceau(x) ajouté(s) ({invalid_count} ignoré(s))"))
                app_state.notify()

            library_controller.import_files_async(file_paths, on_complete=on_complete)

    file_picker.on_result = on_file_picker_result

    def handle_like_track(file_path: str):
        library_controller.toggle_like(file_path)

    def handle_delete_track(file_path: str):
        library_controller.remove_track(file_path)

    def handle_search(query: str):
        library_controller.set_search_query(query)

    def handle_reset():
        library_controller.reset_library()
        show_toast("Bibliothèque réinitialisée.")

    def handle_theme_toggle(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        page.update()

    def handle_start_recommendation():
        def on_success(playlist_paths):
            def _open_modal():
                dialog = ResultDialog(
                    count=len(playlist_paths),
                    file_path=app_state.session.last_generated_playlist_path,
                    on_launch_vlc=lambda: _launch_vlc(),
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
            
            page.run_thread(_open_modal)

        def on_error(err):
            page.run_thread(lambda: show_toast(f"Erreur : {err}", is_error=True))

        rec_controller.run_recommendation_async(on_success=on_success, on_error=on_error)

    def _launch_vlc():
        success, msg = rec_controller.launch_vlc()
        show_toast(msg, is_error=not success)

    def show_toast(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor="#EF4444" if is_error else "#F59E0B",
            duration=4000,
        )
        page.snack_bar = snack
        snack.open = True
        page.update()

    # 5. Construction de l'interface principale Shell Layout
    layout = MainLayout(
        on_pick_files=handle_pick_files,
        on_like_track=handle_like_track,
        on_delete_track=handle_delete_track,
        on_search=handle_search,
        on_start_recommendation=handle_start_recommendation,
        on_reset=handle_reset,
        on_theme_toggle=handle_theme_toggle,
    )

    # Abonnement aux événements AppState (Réactivité globale)
    def on_state_change():
        try:
            layout.update_all()
            page.update()
        except Exception:
            pass

    app_state.subscribe(on_state_change)
    page.add(layout)

    # 6. Chargement asynchrone des ressources (ONNX & LanceDB) en tâche de fond
    def preload_background():
        ai_service.preload_resources()
        db_service.initialize_db()
        app_state.notify()

    threading.Thread(target=preload_background, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main)
