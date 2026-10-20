import os
import logging
from typing import List, Tuple
from domain.track import Track
from services.audio_validation_service import AudioValidationService

log = logging.getLogger("aic.library")


class LibraryService:
    """
    Service gérant le balayage des dossiers et l'indexation de la bibliothèque.
    """

    def __init__(self, validation_service: AudioValidationService = None):
        self.validation_service = validation_service or AudioValidationService()

    def scan_directory(self, folder_path: str) -> List[str]:
        """
        Scanne récursivement un dossier source et retourne la liste des chemins de fichiers découverts.
        Ignore uniquement les fichiers et dossiers système cachés (.git, .cache...) et temporaires.
        La validation de contenu (magic bytes + codec audio) est confiée à AudioValidationService.
        """
        discovered_paths: List[str] = []
        if not os.path.isdir(folder_path):
            return discovered_paths

        def _on_walk_error(err: OSError):
            log.warning(f"[SCAN] Erreur d'accès ignorée : {err}")

        try:
            for root, dirs, files in os.walk(folder_path, onerror=_on_walk_error):
                # Ignorer les dossiers cachés en place (.git, .cache...)
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    # Ignorer les fichiers cachés ou temporaires
                    if file.startswith(".") or file.startswith("~") or file.endswith(".tmp"):
                        continue

                    full_path = os.path.join(root, file)
                    try:
                        if os.path.isfile(full_path):
                            discovered_paths.append(full_path)
                    except OSError as e:
                        log.warning(f"[SCAN] Erreur d'accès fichier {full_path} : {e}")
        except Exception as e:
            log.warning(f"[SCAN] Erreur lors de l'exploration de {folder_path} : {e}")

        return discovered_paths

    def process_folder_import(self, folder_path: str) -> Tuple[List[Track], int]:
        """
        Scanne et valide un dossier complet via la pipeline commune AudioValidationService.
        """
        paths = self.scan_directory(folder_path)
        return self.validation_service.validate_file_paths(paths)

