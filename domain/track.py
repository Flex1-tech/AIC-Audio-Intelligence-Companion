from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Track:
    """
    Entité du Domaine représentant une piste audio dans AIC.
    Contient les métadonnées de la piste, son hash BLAKE3 et son état d'interaction.
    """

    file_path: str
    file_name: str = ""
    file_hash: Optional[str] = None
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    audio_format: str = ""
    is_liked: bool = False
    is_valid: bool = True
    in_database: bool = False
    mmr_score: Optional[float] = None

    def __post_init__(self):
        if not self.file_name and self.file_path:
            p = Path(self.file_path)
            self.file_name = p.name
            if not self.audio_format:
                self.audio_format = p.suffix.lstrip(".").upper()

    @property
    def formatted_size(self) -> str:
        """Retourne la taille du fichier formatée (ex: 8.5 MB)."""
        if self.file_size_bytes <= 0:
            return "0 B"
        size = float(self.file_size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def short_hash(self) -> str:
        """Retourne un affichage court du hash BLAKE3."""
        if not self.file_hash:
            return "Non indexé"
        return f"{self.file_hash[:8]}..."
