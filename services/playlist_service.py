import subprocess
import time
from typing import List, Tuple
from extraction import recommend_playlist, make_m3u
from utils.audio_utils import find_vlc
from providers.musicnn_provider import MusicnnProvider
from repositories.track_repository import TrackRepository
from core.state import app_state


class PlaylistService:
    """
    Service de recommandation MMR, génération de playlists .m3u8 et exécution de VLC.
    """

    def __init__(self, provider: MusicnnProvider = None, repository: TrackRepository = None):
        self.provider = provider or MusicnnProvider()
        self.repository = repository or TrackRepository()

    def generate_recommendations(self, lambda_mmr: float = 0.7) -> List[str]:
        """
        Déclenche l'inférence audio ONNX et l'algorithme MMR LanceDB.
        """
        start_time = time.time()

        # Prépare le dict path_dict {path: is_liked} requis par extraction.py
        path_dict = {track.file_path: track.is_liked for track in app_state.library.tracks.values()}

        session = self.provider.get_session()
        table = self.repository.get_table()

        # Exécution de recommend_playlist (qui calcule aussi
        # process_files_batch)
        recommended_paths = recommend_playlist(path_dict=path_dict, session=session, table=table, lambda_mmr=lambda_mmr)

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

    def export_m3u8(self, playlist_paths: List[str], output_path: str = "playlist.m3u8") -> str:
        make_m3u(playlist_paths, output_path)
        app_state.session.last_generated_playlist_path = output_path
        app_state.notify()
        return output_path

    def launch_vlc(self, playlist_path: str = "playlist.m3u8") -> Tuple[bool, str]:
        vlc_path = app_state.session.vlc_custom_path or find_vlc()
        if not vlc_path:
            return (
                False,
                "VLC est introuvable. Veuillez l'installer ou préciser son chemin.",
            )

        try:
            subprocess.Popen([vlc_path, playlist_path])
            app_state.log_action("VLC_LAUNCHED", f"VLC lancé avec la playlist {playlist_path}")
            return True, "VLC lancé avec succès !"
        except Exception as e:
            return False, f"Erreur lors du lancement de VLC : {e}"
