"""
services/playback_service.py
----------------------------
Service découplé pour la lecture externe et l'exploration des fichiers média et playlists.
Gère de façon portable :
- Lecture via VLC (optionnel)
- Fallback transparent vers l'application par défaut du système (os.startfile / open / xdg-open)
- Boîte de dialogue native 'Ouvrir avec…' (Windows)
- Affichage et sélection dans l'Explorateur Windows / Finder
"""

from __future__ import annotations

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Tuple

from core.state import app_state
from utils.audio_utils import find_vlc

log = logging.getLogger("aic.playback")


class PlaybackService:
    """Service de lecture multimédia et d'exploration de fichiers multiplateforme."""

    def play_playlist(self, playlist_path: str, prefer_vlc: bool = True) -> Tuple[bool, str]:
        """
        Lit une playlist :
        1. Tente VLC si demandé et disponible.
        2. Sinon, bascule de manière transparente sur l'application par défaut du système.
        3. En cas d'échec total, retourne un message d'erreur clair.
        """
        if not playlist_path or not os.path.exists(playlist_path):
            return False, f"Fichier playlist introuvable : '{playlist_path}'"

        if prefer_vlc:
            vlc_path = app_state.session.vlc_custom_path or find_vlc()
            if vlc_path:
                try:
                    subprocess.Popen([vlc_path, playlist_path])
                    app_state.log_action("PLAYBACK_VLC", f"VLC lancé avec {playlist_path}")
                    return True, "Playlist lancée avec VLC !"
                except Exception as e:
                    log.warning(f"[PLAYBACK] Échec du lancement de VLC ({e}), repli vers l'application par défaut.")

        # Fallback automatique sur l'application par défaut
        ok, msg = self.play_with_default_app(playlist_path)
        if ok and prefer_vlc:
            return True, f"VLC non détecté : {msg}"
        return ok, msg

    def play_track(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre un morceau audio avec l'application par défaut."""
        return self.play_with_default_app(file_path)

    def play_with_default_app(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre un fichier avec l'application par défaut du système d'exploitation."""
        if not file_path or not os.path.exists(file_path):
            return False, f"Fichier introuvable : '{file_path}'"

        try:
            norm_path = os.path.normpath(file_path)
            if sys.platform == "win32":
                os.startfile(norm_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", norm_path])
            else:
                subprocess.Popen(["xdg-open", norm_path])

            app_state.log_action("PLAYBACK_DEFAULT", f"Ouvert avec le lecteur par défaut : {file_path}")
            return True, "Lecture lancée avec l'application par défaut."
        except Exception as err:
            log.error(f"[PLAYBACK] Erreur lors de l'ouverture par défaut de {file_path} : {err}")
            return False, f"Impossible d'ouvrir avec l'application par défaut : {err}"

    def open_with_dialog(self, file_path: str) -> Tuple[bool, str]:
        """Affiche le dialogue natif 'Ouvrir avec…'."""
        if not file_path or not os.path.exists(file_path):
            return False, f"Fichier introuvable : '{file_path}'"

        try:
            norm_path = os.path.normpath(file_path)
            if sys.platform == "win32":
                subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", norm_path])
                return True, "Boîte de dialogue 'Ouvrir avec…' ouverte."
            else:
                return self.play_with_default_app(file_path)
        except Exception as err:
            log.error(f"[PLAYBACK] Erreur 'Ouvrir avec' pour {file_path} : {err}")
            return False, f"Impossible d'afficher 'Ouvrir avec…' : {err}"

    def show_in_explorer(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre le gestionnaire de fichiers en surlignant le fichier cible."""
        if not file_path:
            return False, "Aucun chemin de fichier spécifié."

        try:
            norm_path = os.path.normpath(file_path)
            if sys.platform == "win32":
                if os.path.isfile(norm_path):
                    subprocess.Popen(["explorer.exe", f"/select,{norm_path}"])
                elif os.path.isdir(norm_path):
                    os.startfile(norm_path)
                else:
                    parent = os.path.dirname(norm_path)
                    if os.path.isdir(parent):
                        os.startfile(parent)
                    else:
                        return False, f"Chemin parent introuvable : '{norm_path}'"
            elif sys.platform == "darwin":
                if os.path.exists(norm_path):
                    subprocess.Popen(["open", "-R", norm_path])
                else:
                    subprocess.Popen(["open", os.path.dirname(norm_path)])
            else:
                parent = os.path.dirname(norm_path) if os.path.isfile(norm_path) else norm_path
                subprocess.Popen(["xdg-open", parent])

            app_state.log_action("EXPLORER_SHOW", f"Explorateur ouvert pour {file_path}")
            return True, "Fichier localisé dans l'Explorateur."
        except Exception as err:
            log.error(f"[PLAYBACK] Erreur explorateur pour {file_path} : {err}")
            return False, f"Impossible d'ouvrir l'Explorateur : {err}"
