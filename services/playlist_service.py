import subprocess
import time
from typing import List, Tuple, Optional
from utils.audio_utils import find_vlc
from providers.musicnn_provider import MusicnnProvider
from repositories.track_repository import TrackRepository
from core.state import app_state


from services.playlist_export_service import PlaylistExportService, ExportResult
from services.playback_service import PlaybackService


class PlaylistService:
    """
    Service de recommandation MMR, génération de playlists .m3u8 et lecture externe.
    """

    def __init__(
        self,
        provider: MusicnnProvider = None,
        repository: TrackRepository = None,
        export_service: PlaylistExportService = None,
        playback_service: PlaybackService = None,
    ):
        self.provider = provider or MusicnnProvider()
        self.repository = repository or TrackRepository()
        self.export_service = export_service or PlaylistExportService()
        self.playback_service = playback_service or PlaybackService()

    def generate_recommendations(self, lambda_mmr: float = 0.7) -> List[str]:
        """
        Déclenche l'inférence audio ONNX et l'algorithme MMR LanceDB.
        """
        from extraction import recommend_playlist

        start_time = time.time()

        # Prépare le dict path_dict {path: is_liked} et les hashes déjà calculés
        path_dict = {track.file_path: track.is_liked for track in app_state.library.tracks.values()}
        track_hashes = {
            track.file_path: track.file_hash
            for track in app_state.library.tracks.values()
            if track.file_hash
        }

        session = self.provider.get_session()
        table = self.repository.get_table()

        # Exécution de recommend_playlist avec réutilisation du file_hash
        recommended_paths = recommend_playlist(
            path_dict=path_dict,
            session=session,
            table=table,
            lambda_mmr=lambda_mmr,
            track_hashes=track_hashes,
        )

        duration_ms = (time.time() - start_time) * 1000.0
        app_state.last_inference_duration_ms = duration_ms
        app_state.total_embeddings_in_db = self.repository.count_rows()

        # Mise à jour des scores MMR et du statut in_database des tracks
        for rank, path in enumerate(recommended_paths):
            if path in app_state.library.tracks:
                t = app_state.library.tracks[path]
                t.in_database = True
                t.mmr_score = 1.0 - (rank / max(1, len(recommended_paths)))

        app_state.log_action(
            "RECOMMENDATION_SUCCESS",
            f"Playlist générée ({len(recommended_paths)} morceaux en {duration_ms:.0f}ms)",
        )
        return recommended_paths

    def export_m3u8(
        self,
        playlist_paths: List[str],
        custom_folder: Optional[str] = None,
        persist_as_default: bool = False,
    ) -> ExportResult:
        """
        Exporte la playlist de manière sécurisée via PlaylistExportService.
        """
        return self.export_service.export_playlist(
            playlist_paths,
            custom_folder=custom_folder,
            persist_as_default=persist_as_default,
        )

    def launch_vlc(self, playlist_path: str = "playlist.m3u8") -> Tuple[bool, str]:
        """Lance la playlist avec VLC (ou bascule vers l'application par défaut si VLC est absent)."""
        return self.playback_service.play_playlist(playlist_path, prefer_vlc=True)

    def play_playlist_default(self, playlist_path: str = "playlist.m3u8") -> Tuple[bool, str]:
        """Lance la playlist avec le lecteur par défaut du système."""
        return self.playback_service.play_with_default_app(playlist_path)

    def open_with_dialog(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre le dialogue 'Ouvrir avec…' du système."""
        return self.playback_service.open_with_dialog(file_path)

    def show_in_explorer(self, file_path: str) -> Tuple[bool, str]:
        """Affiche et sélectionne le fichier dans l'Explorateur."""
        return self.playback_service.show_in_explorer(file_path)
