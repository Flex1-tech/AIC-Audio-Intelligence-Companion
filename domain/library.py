from dataclasses import dataclass, field
from typing import List, Dict
from domain.track import Track


@dataclass
class MusicLibrary:
    """
    Entité représentant la bibliothèque musicale gérée par AIC.
    Gère les dossiers sources, les pistes indexées et les métriques globales.
    """
    name: str = "Ma Bibliothèque Principale"
    folder_paths: List[str] = field(default_factory=list)
    tracks: Dict[str, Track] = field(
        default_factory=dict)  # {file_path: Track}
    last_scanned_timestamp: float = 0.0

    @property
    def total_tracks_count(self) -> int:
        return len(self.tracks)

    @property
    def liked_tracks_count(self) -> int:
        return sum(1 for track in self.tracks.values() if track.is_liked)

    @property
    def in_db_tracks_count(self) -> int:
        return sum(1 for track in self.tracks.values() if track.in_database)

    @property
    def is_recommendation_ready(self) -> bool:
        """Au moins 3 morceaux likés sont requis pour l'inférence MMR."""
        return self.liked_tracks_count >= 3

    def get_liked_tracks(self) -> List[Track]:
        return [track for track in self.tracks.values() if track.is_liked]

    def clear(self) -> None:
        self.tracks.clear()
