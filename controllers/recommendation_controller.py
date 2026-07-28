import threading
from typing import Callable, Optional, List
from core.state import app_state
from services.playlist_service import PlaylistService

class RecommendationController:
    """
    Contrôleur gérant le lancement de l'inférence MMR, l'export et l'exécution VLC.
    """
    def __init__(self, playlist_service: PlaylistService = None):
        self.playlist_service = playlist_service or PlaylistService()

    def run_recommendation_async(self, on_success: Callable[[List[str]], None] = None, on_error: Callable[[str], None] = None) -> None:
        """
        Exécute le processus MMR dans un thread séparé avec retour visuel réactif.
        """
        if not app_state.library.is_recommendation_ready:
            if on_error:
                on_error("Veuillez liker au moins 3 morceaux pour générer une recommandation.")
            return

        app_state.is_processing = True
        app_state.processing_status_message = "Calcul des embeddings MusiCNN & Ranking MMR..."
        app_state.notify()

        def _worker():
            try:
                playlist_paths = self.playlist_service.generate_recommendations(
                    lambda_mmr=app_state.session.lambda_mmr
                )
                self.playlist_service.export_m3u8(playlist_paths)

                app_state.is_processing = False
                app_state.processing_status_message = "Prêt"
                app_state.notify()

                if on_success:
                    on_success(playlist_paths)

            except Exception as e:
                app_state.is_processing = False
                app_state.processing_status_message = "Erreur"
                app_state.log_action("RECOMMENDATION_ERROR", f"Erreur MMR : {e}")
                app_state.notify()

                if on_error:
                    on_error(str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def launch_vlc(self) -> tuple[bool, str]:
        return self.playlist_service.launch_vlc(app_state.session.last_generated_playlist_path)
