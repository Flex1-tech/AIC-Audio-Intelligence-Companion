import threading
from typing import Callable, List
from core.state import app_state
from services.playlist_service import PlaylistService


class RecommendationController:
    """
    Contrôleur gérant le lancement de l'inférence MMR, l'export et l'exécution VLC.
    """

    def __init__(self, playlist_service: PlaylistService = None):
        self.playlist_service = playlist_service or PlaylistService()

    def run_recommendation_async(
        self,
        on_success: Callable[[List[str]], None] = None,
        on_error: Callable[[str], None] = None,
    ) -> None:
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
                playlist_paths = self.playlist_service.generate_recommendations(lambda_mmr=app_state.session.lambda_mmr)
                # Export automatique vers le dossier par défaut de la session.
                # persist_as_default=True : mémorise le dossier d'export utilisé comme préférence persistante.
                export_res = self.playlist_service.export_m3u8(playlist_paths, persist_as_default=True)

                app_state.is_processing = False
                app_state.processing_status_message = "Prêt"
                app_state.notify()

                if on_success:
                    on_success(export_res)

            except Exception as e:
                app_state.is_processing = False
                app_state.processing_status_message = "Erreur"
                app_state.log_action("RECOMMENDATION_ERROR", f"Erreur MMR : {e}")
                app_state.notify()

                if on_error:
                    on_error(str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def launch_vlc(self) -> tuple[bool, str]:
        """Lance la playlist avec VLC (ou bascule sur l'app par défaut)."""
        return self.playlist_service.launch_vlc(app_state.session.last_generated_playlist_path)

    def play_playlist_default(self) -> tuple[bool, str]:
        """Lance la playlist avec l'application par défaut."""
        return self.playlist_service.play_playlist_default(app_state.session.last_generated_playlist_path)

    def open_playlist_with_dialog(self) -> tuple[bool, str]:
        """Ouvre le dialogue 'Ouvrir avec…' pour la playlist."""
        return self.playlist_service.open_with_dialog(app_state.session.last_generated_playlist_path)

    def show_playlist_in_explorer(self) -> tuple[bool, str]:
        """Affiche et sélectionne la playlist dans l'Explorateur."""
        return self.playlist_service.show_in_explorer(app_state.session.last_generated_playlist_path)

    def play_track(self, file_path: str) -> tuple[bool, str]:
        """Ouvre un morceau individuel avec le lecteur par défaut."""
        return self.playlist_service.playback_service.play_track(file_path)

    def show_track_in_explorer(self, file_path: str) -> tuple[bool, str]:
        """Affiche et sélectionne un morceau individuel dans l'Explorateur."""
        return self.playlist_service.playback_service.show_in_explorer(file_path)

    def export_playlist(
        self,
        playlist_paths: List[str],
        custom_folder: str = None,
        persist_as_default: bool = False,
    ):
        """Exporte la playlist vers une destination donnée."""
        return self.playlist_service.export_m3u8(
            playlist_paths,
            custom_folder=custom_folder,
            persist_as_default=persist_as_default,
        )

    def set_default_export_folder(self, folder_path: str) -> None:
        """Définit la destination d'export par défaut persistante."""
        self.playlist_service.export_service.set_default_export_folder(folder_path)
