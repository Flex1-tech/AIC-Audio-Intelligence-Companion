from typing import List
import threading
from core.state import app_state
from domain.track import Track
from services.audio_validation_service import AudioValidationService

class LibraryController:
    """
    Contrôleur gérant la bibliothèque musicale, l'importation, les filtres et les likes.
    """
    def __init__(self, validation_service: AudioValidationService = None):
        self.validation_service = validation_service or AudioValidationService()

    def import_files_async(self, file_paths: List[str], on_complete=None) -> None:
        """
        Valide et importe des fichiers audio dans un thread séparé non-bloquant.
        """
        if not file_paths:
            return

        app_state.is_processing = True
        app_state.processing_status_message = "Validation des fichiers audio..."
        app_state.notify()

        def _worker():
            valid_tracks, invalid_count = self.validation_service.validate_file_paths(file_paths)
            
            for track in valid_tracks:
                if track.file_path not in app_state.library.tracks:
                    app_state.library.tracks[track.file_path] = track

            app_state.is_processing = False
            app_state.processing_status_message = "Prêt"
            
            app_state.log_action(
                "IMPORT_FILES",
                f"{len(valid_tracks)} morceaux importés ({invalid_count} ignorés)",
                {"imported": len(valid_tracks), "ignored": invalid_count}
            )

            if on_complete:
                on_complete(len(valid_tracks), invalid_count)

        threading.Thread(target=_worker, daemon=True).start()

    def toggle_like(self, file_path: str) -> None:
        if file_path in app_state.library.tracks:
            track = app_state.library.tracks[file_path]
            track.is_liked = not track.is_liked
            app_state.log_action(
                "TOGGLE_LIKE",
                f"{'Liké' if track.is_liked else 'Unliké'} : {track.file_name}"
            )
            app_state.notify()

    def remove_track(self, file_path: str) -> None:
        if file_path in app_state.library.tracks:
            track = app_state.library.tracks.pop(file_path)
            app_state.log_action("REMOVE_TRACK", f"Morceau retiré : {track.file_name}")
            app_state.notify()

    def reset_library(self) -> None:
        app_state.library.clear()
        app_state.log_action("RESET_LIBRARY", "Bibliothèque réinitialisée")
        app_state.notify()

    def set_search_query(self, query: str) -> None:
        app_state.session.search_query = query.strip()
        app_state.notify()

    def toggle_liked_filter(self) -> None:
        app_state.session.filter_liked_only = not app_state.session.filter_liked_only
        app_state.notify()
