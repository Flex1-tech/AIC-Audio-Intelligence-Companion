"""
services/playback_service.py
----------------------------
Service centralisé et multiplateforme pour la lecture externe et l'exploration de fichiers.
Compatible Windows, Linux et macOS.

Fonctionnalités :
- Lecture de playlist : VLC privilégié si disponible, avec fallback transparent et explicite
  vers le lecteur par défaut du système.
- Lecture de morceau : ouverture via l'application associée par défaut par l'OS.
- Action « Ouvrir avec… » :
    * Windows : dialogue natif via rundll32.exe shell32.dll,OpenAs_RunDLL
    * macOS : dialogue natif d'application via AppleScript (choose application)
    * Linux : sélecteur graphique (zenity/kdialog) si disponible, ou message explicite invitant
      à utiliser la lecture par défaut.
- Action « Afficher dans le gestionnaire de fichiers » :
    * Windows : sélection directe dans l'Explorateur (explorer.exe /select,...)
    * macOS : sélection directe dans le Finder (open -R ...)
    * Linux : sélection directe si supportée (nautilus, dolphin, nemo) ou ouverture du dossier parent (xdg-open).
"""

from __future__ import annotations

import os
import sys
import platform
import subprocess
import logging
from shutil import which
from typing import Tuple, Optional

from core.state import app_state
from utils.audio_utils import find_vlc

log = logging.getLogger("aic.playback")


class PlaybackService:
    """Service multiplateforme pour la lecture multimédia et l'exploration de fichiers."""

    def __init__(self, system_name: Optional[str] = None):
        self._system_override = system_name

    @property
    def system(self) -> str:
        """Retourne le nom normalisé du système ('Windows', 'Darwin', 'Linux')."""
        if self._system_override:
            return self._system_override
        if sys.platform == "win32":
            return "Windows"
        elif sys.platform == "darwin":
            return "Darwin"
        return platform.system()

    # -----------------------------------------------------------------------
    # 1. Lecture de Playlists & Morceaux
    # -----------------------------------------------------------------------

    def play_playlist(self, playlist_path: str, prefer_vlc: bool = True) -> Tuple[bool, str]:
        """
        Lit une playlist :
        1. Tente VLC si demandé et disponible.
        2. Si VLC échoue ou est absent, bascule sur l'application par défaut.
        3. En cas d'erreur de lancement, retourne un résultat explicite.
        """
        if not playlist_path or not os.path.exists(playlist_path):
            return False, f"Fichier playlist introuvable : '{playlist_path}'"

        norm_path = os.path.abspath(os.path.normpath(playlist_path))

        if prefer_vlc:
            vlc_path = app_state.session.vlc_custom_path or find_vlc()
            if vlc_path:
                try:
                    subprocess.Popen([vlc_path, norm_path])
                    app_state.log_action("PLAYBACK_VLC", f"VLC lancé avec {norm_path}")
                    return True, "Playlist lancée avec VLC !"
                except (FileNotFoundError, PermissionError, OSError) as e:
                    log.warning(f"[PLAYBACK] Échec du lancement de VLC ({e}), repli vers l'application par défaut.")

        # Fallback automatique sur l'application par défaut
        ok, msg = self.play_with_default_app(norm_path)
        if ok and prefer_vlc:
            return True, f"VLC non détecté : {msg}"
        return ok, msg

    def play_track(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre un morceau audio avec l'application par défaut du système."""
        return self.play_with_default_app(file_path)

    def play_with_default_app(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre un fichier avec l'application par défaut de l'OS (Windows, macOS, Linux)."""
        if not file_path or not os.path.exists(file_path):
            return False, f"Fichier introuvable : '{file_path}'"

        norm_path = os.path.abspath(os.path.normpath(file_path))
        sys_name = self.system

        if sys_name == "Windows":
            return self._play_default_windows(norm_path)
        elif sys_name == "Darwin":
            return self._play_default_macos(norm_path)
        elif sys_name == "Linux":
            return self._play_default_linux(norm_path)
        else:
            return self._play_default_linux(norm_path)

    def _play_default_windows(self, norm_path: str) -> Tuple[bool, str]:
        try:
            os.startfile(norm_path)
            app_state.log_action("PLAYBACK_DEFAULT", f"Ouvert avec le lecteur par défaut Windows : {norm_path}")
            return True, "Lecture lancée avec l'application par défaut."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur os.startfile pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir avec l'application par défaut : {err}"

    def _play_default_macos(self, norm_path: str) -> Tuple[bool, str]:
        open_bin = which("open") or "/usr/bin/open"
        try:
            subprocess.Popen([open_bin, norm_path])
            app_state.log_action("PLAYBACK_DEFAULT", f"Ouvert avec le lecteur par défaut macOS : {norm_path}")
            return True, "Lecture lancée avec l'application par défaut."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur open macOS pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir avec l'application par défaut (open) : {err}"

    def _play_default_linux(self, norm_path: str) -> Tuple[bool, str]:
        opener = which("xdg-open") or which("gio") or which("kde-open5") or which("kde-open")
        if not opener:
            return False, "Aucun utilitaire d'ouverture par défaut (xdg-open, gio) n'est disponible sur ce système."

        try:
            if os.path.basename(opener) == "gio":
                subprocess.Popen([opener, "open", norm_path])
            else:
                subprocess.Popen([opener, norm_path])
            app_state.log_action(
                "PLAYBACK_DEFAULT", f"Ouvert avec le lecteur par défaut Linux ({opener}) : {norm_path}"
            )
            return True, "Lecture lancée avec l'application par défaut."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur d'ouverture Linux ({opener}) pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir avec l'application par défaut : {err}"

    # -----------------------------------------------------------------------
    # 2. Action « Ouvrir avec… »
    # -----------------------------------------------------------------------

    def open_with_dialog(self, file_path: str) -> Tuple[bool, str]:
        """Affiche le sélecteur natif d'application pour le fichier."""
        if not file_path or not os.path.exists(file_path):
            return False, f"Fichier introuvable : '{file_path}'"

        norm_path = os.path.abspath(os.path.normpath(file_path))
        sys_name = self.system

        if sys_name == "Windows":
            return self._open_with_windows(norm_path)
        elif sys_name == "Darwin":
            return self._open_with_macos(norm_path)
        elif sys_name == "Linux":
            return self._open_with_linux(norm_path)
        else:
            return self._open_with_linux(norm_path)

    def _open_with_windows(self, norm_path: str) -> Tuple[bool, str]:
        try:
            subprocess.Popen(["rundll32.exe", "shell32.dll,OpenAs_RunDLL", norm_path])
            app_state.log_action("OPEN_WITH", f"Dialogue 'Ouvrir avec…' Windows ouvert pour {norm_path}")
            return True, "Boîte de dialogue 'Ouvrir avec…' ouverte."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur 'Ouvrir avec' Windows pour {norm_path} : {err}")
            return False, f"Impossible d'afficher 'Ouvrir avec…' : {err}"

    def _open_with_macos(self, norm_path: str) -> Tuple[bool, str]:
        osascript_bin = which("osascript") or "/usr/bin/osascript"
        script = (
            "on run argv\n"
            "    set filePath to item 1 of argv\n"
            '    set appPath to choose application with prompt "Choisir une application pour ouvrir ce fichier :"\n'
            '    tell application "Finder" to open (POSIX file filePath) using appPath\n'
            "end run"
        )
        try:
            subprocess.Popen([osascript_bin, "-e", script, norm_path])
            app_state.log_action("OPEN_WITH", f"Sélecteur d'application macOS ouvert pour {norm_path}")
            return True, "Sélecteur d'application macOS ouvert."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur sélecteur d'application macOS pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir le sélecteur d'application macOS : {err}"

    def _open_with_linux(self, norm_path: str) -> Tuple[bool, str]:
        zenity_bin = which("zenity")
        kdialog_bin = which("kdialog")

        if zenity_bin:
            try:
                runner_code = (
                    "import sys, subprocess, os, shutil\n"
                    "fpath = sys.argv[1]\n"
                    "zbin = sys.argv[2]\n"
                    "p = subprocess.run([zbin, '--file-selection', '--title=Choisir une application', '--filename=/usr/share/applications/'], capture_output=True, text=True)\n"
                    "target = p.stdout.strip()\n"
                    "if target and os.path.exists(target):\n"
                    "    base = os.path.basename(target).removesuffix('.desktop')\n"
                    "    if shutil.which('gtk-launch'):\n"
                    "        subprocess.run(['gtk-launch', base, fpath])\n"
                    "    else:\n"
                    "        subprocess.run(['xdg-open', fpath])\n"
                )
                subprocess.Popen([sys.executable, "-c", runner_code, norm_path, zenity_bin])
                app_state.log_action("OPEN_WITH", f"Sélecteur d'application zenity ouvert pour {norm_path}")
                return True, "Sélecteur d'application ouvert."
            except (FileNotFoundError, PermissionError, OSError) as err:
                log.error(f"[PLAYBACK] Erreur sélecteur zenity pour {norm_path} : {err}")
                return False, f"Impossible d'ouvrir le sélecteur d'application : {err}"

        elif kdialog_bin:
            try:
                runner_code = (
                    "import sys, subprocess, os, shutil\n"
                    "fpath = sys.argv[1]\n"
                    "kbin = sys.argv[2]\n"
                    "p = subprocess.run([kbin, '--getopenfilename', '/usr/share/applications/', '*.desktop'], capture_output=True, text=True)\n"
                    "target = p.stdout.strip()\n"
                    "if target and os.path.exists(target):\n"
                    "    if shutil.which('kioclient5'):\n"
                    "        subprocess.run(['kioclient5', 'exec', target, fpath])\n"
                    "    elif shutil.which('gtk-launch'):\n"
                    "        base = os.path.basename(target).removesuffix('.desktop')\n"
                    "        subprocess.run(['gtk-launch', base, fpath])\n"
                    "    else:\n"
                    "        subprocess.run(['xdg-open', fpath])\n"
                )
                subprocess.Popen([sys.executable, "-c", runner_code, norm_path, kdialog_bin])
                app_state.log_action("OPEN_WITH", f"Sélecteur d'application kdialog ouvert pour {norm_path}")
                return True, "Sélecteur d'application ouvert."
            except (FileNotFoundError, PermissionError, OSError) as err:
                log.error(f"[PLAYBACK] Erreur sélecteur kdialog pour {norm_path} : {err}")
                return False, f"Impossible d'ouvrir le sélecteur d'application : {err}"

        else:
            return (
                False,
                "Aucun sélecteur d'application standard (ex: zenity, kdialog) n'est disponible sur ce système Linux. "
                "Utilisez l'action 'Écouter' pour ouvrir avec le lecteur par défaut.",
            )

    # -----------------------------------------------------------------------
    # 3. Action « Afficher dans le gestionnaire de fichiers »
    # -----------------------------------------------------------------------

    def show_in_explorer(self, file_path: str) -> Tuple[bool, str]:
        """Ouvre le gestionnaire de fichiers du système en ciblant le fichier spécifié."""
        if not file_path:
            return False, "Aucun chemin de fichier spécifié."

        norm_path = os.path.abspath(os.path.normpath(file_path))
        if not os.path.exists(norm_path):
            return False, f"Fichier introuvable : '{norm_path}'"

        sys_name = self.system

        if sys_name == "Windows":
            return self._show_in_explorer_windows(norm_path)
        elif sys_name == "Darwin":
            return self._show_in_explorer_macos(norm_path)
        elif sys_name == "Linux":
            return self._show_in_explorer_linux(norm_path)
        else:
            return self._show_in_explorer_linux(norm_path)

    def _show_in_explorer_windows(self, norm_path: str) -> Tuple[bool, str]:
        try:
            if os.path.isfile(norm_path):
                subprocess.Popen(["explorer.exe", f"/select,{norm_path}"])
            else:
                subprocess.Popen(["explorer.exe", norm_path])
            app_state.log_action("EXPLORER_SHOW", f"Explorateur Windows ouvert pour {norm_path}")
            return True, "Fichier localisé dans l'Explorateur Windows."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur explorateur Windows pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir l'Explorateur : {err}"

    def _show_in_explorer_macos(self, norm_path: str) -> Tuple[bool, str]:
        open_bin = which("open") or "/usr/bin/open"
        try:
            if os.path.isfile(norm_path):
                subprocess.Popen([open_bin, "-R", norm_path])
            else:
                subprocess.Popen([open_bin, norm_path])
            app_state.log_action("EXPLORER_SHOW", f"Finder macOS ouvert pour {norm_path}")
            return True, "Fichier localisé dans le Finder."
        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur Finder macOS pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir le Finder : {err}"

    def _show_in_explorer_linux(self, norm_path: str) -> Tuple[bool, str]:
        nautilus_bin = which("nautilus")
        dolphin_bin = which("dolphin")
        nemo_bin = which("nemo")

        try:
            if os.path.isfile(norm_path):
                if nautilus_bin:
                    subprocess.Popen([nautilus_bin, "--select", norm_path])
                    app_state.log_action("EXPLORER_SHOW", f"Nautilus ouvert pour {norm_path}")
                    return True, "Fichier localisé dans le gestionnaire de fichiers."
                elif dolphin_bin:
                    subprocess.Popen([dolphin_bin, "--select", norm_path])
                    app_state.log_action("EXPLORER_SHOW", f"Dolphin ouvert pour {norm_path}")
                    return True, "Fichier localisé dans le gestionnaire de fichiers."
                elif nemo_bin:
                    subprocess.Popen([nemo_bin, "--no-desktop", norm_path])
                    app_state.log_action("EXPLORER_SHOW", f"Nemo ouvert pour {norm_path}")
                    return True, "Fichier localisé dans le gestionnaire de fichiers."

            # Fallback : ouvrir le dossier parent avec xdg-open ou gio
            parent_dir = os.path.dirname(norm_path) if os.path.isfile(norm_path) else norm_path
            opener = which("xdg-open") or which("gio")
            if opener:
                if os.path.basename(opener) == "gio":
                    subprocess.Popen([opener, "open", parent_dir])
                else:
                    subprocess.Popen([opener, parent_dir])
                app_state.log_action("EXPLORER_SHOW", f"Dossier parent ouvert pour {norm_path}")
                return True, "Dossier parent ouvert dans le gestionnaire de fichiers."
            else:
                return False, "Aucun gestionnaire de fichiers (xdg-open, gio) disponible sur ce système."

        except (FileNotFoundError, PermissionError, OSError) as err:
            log.error(f"[PLAYBACK] Erreur gestionnaire de fichiers Linux pour {norm_path} : {err}")
            return False, f"Impossible d'ouvrir le gestionnaire de fichiers : {err}"
