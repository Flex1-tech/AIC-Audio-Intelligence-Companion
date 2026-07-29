from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class SessionState:
    """
    Entité représentant l'état persistant d'une session utilisateur AIC.
    """

    active_nav_index: int = 0
    search_query: str = ""
    filter_liked_only: bool = False
    lambda_mmr: float = 0.7
    vlc_custom_path: str = ""
    last_generated_playlist_path: str = "playlist.m3u8"
    theme_mode: str = "dark"  # "dark" ou "light"
    window_width: int = 1100
    window_height: int = 750

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_nav_index": self.active_nav_index,
            "search_query": self.search_query,
            "filter_liked_only": self.filter_liked_only,
            "lambda_mmr": self.lambda_mmr,
            "vlc_custom_path": self.vlc_custom_path,
            "last_generated_playlist_path": self.last_generated_playlist_path,
            "theme_mode": self.theme_mode,
            "window_width": self.window_width,
            "window_height": self.window_height,
        }
