import os
from typing import List, Tuple
from func import is_audio_file, is_valid_media
from domain.track import Track
from repositories.track_repository import TrackRepository


class AudioValidationService:
    """
    Service de validation des fichiers audio via FFprobe et Fleep.
    """

    def __init__(self, repository: TrackRepository = None):
        self.repository = repository or TrackRepository()

    def validate_file_paths(
            self, file_paths: List[str]) -> Tuple[List[Track], int]:
        """
        Valide une liste de chemins de fichiers et retourne les objets Track valides
        ainsi que le nombre de fichiers ignorés.
        """
        valid_tracks: List[Track] = []
        invalid_count = 0

        for path in file_paths:
            if not os.path.isfile(path):
                invalid_count += 1
                continue

            try:
                if is_audio_file(path) and is_valid_media(path):
                    st = os.stat(path)
                    track_hash = self.repository.compute_file_hash(path)
                    track = Track(
                        file_path=path,
                        file_size_bytes=st.st_size,
                        file_hash=track_hash,
                        is_valid=True
                    )
                    valid_tracks.append(track)
                else:
                    invalid_count += 1
            except Exception:
                invalid_count += 1

        return valid_tracks, invalid_count
