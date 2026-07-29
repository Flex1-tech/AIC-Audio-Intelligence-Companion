import os
from typing import List, Tuple
from domain.track import Track
from services.audio_validation_service import AudioValidationService

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}


class LibraryService:
    """
    Service gérant le balayage des dossiers et l'indexation de la bibliothèque.
    """

    def __init__(self, validation_service: AudioValidationService = None):
        self.validation_service = validation_service or AudioValidationService()

    def scan_directory(self, folder_path: str) -> List[str]:
        """
        Scanne récursivement un dossier source et retourne la liste des chemins de fichiers audio trouvés.
        """
        discovered_paths: List[str] = []
        if not os.path.isdir(folder_path):
            return discovered_paths

        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in AUDIO_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    discovered_paths.append(full_path)

        return discovered_paths

    def process_folder_import(
            self, folder_path: str) -> Tuple[List[Track], int]:
        """
        Scanne et valide un dossier complet.
        """
        paths = self.scan_directory(folder_path)
        return self.validation_service.validate_file_paths(paths)
