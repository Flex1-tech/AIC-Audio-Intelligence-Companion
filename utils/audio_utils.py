"""
utils/audio_utils.py
--------------------
Utilitaires audio purs (sans dépendance GUI).

Extrait de func.py pour découpler les services Flet (audio_validation_service,
playlist_service) de customtkinter, qui n'est disponible que dans l'ancienne
interface CTK (interface.py / func.py).

Fonctions disponibles :
    - get_media_type(filepath)   → 'audio' | 'video' | None
    - is_audio_file(filepath)    → bool
    - is_valid_media(filepath)   → bool
    - run_ffprobe(cmd, timeout)  → subprocess.CompletedProcess
    - find_vlc()                 → str | None
"""

import sys
import subprocess
import platform
from pathlib import Path
from shutil import which

import fleep


def get_media_type(filepath):
    """Retourne 'audio', 'video' ou None selon le contenu du fichier."""
    try:
        with open(filepath, "rb") as file:
            info = fleep.get(file.read(128))
        types = info.type
        if not types:
            return None
        if "audio" in types:
            return "audio"
        elif "video" in types:
            return "video"
        return None
    except Exception:
        return None


def is_audio_file(filepath):
    """Retourne True si le fichier est reconnu comme audio ou vidéo par fleep."""
    with open(filepath, "rb") as file:
        info = fleep.get(file.read(128))
    # Certains fichiers audio peuvent être classés comme vidéo
    return "audio" in info.type or "video" in info.type


def run_ffprobe(cmd, timeout=5):
    """Exécute une commande ffprobe et retourne le CompletedProcess."""
    kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "timeout": timeout,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.run(cmd, **kwargs)


def is_valid_media(filepath):
    """Retourne True si ffprobe valide le fichier comme média lisible."""
    try:
        result = run_ffprobe(
            [
                "ffprobe",
                "-v",
                "error",
                filepath,
            ]
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False


def find_vlc():
    """
    Recherche l'exécutable VLC sur le système (PATH, emplacements courants).
    Retourne le chemin absolu ou None si introuvable.
    """
    vlc = which("vlc")
    if vlc:
        return vlc

    system = platform.system()

    if system == "Windows":
        possible_paths = []
        for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            possible_paths.extend(
                [
                    Path(f"{drive}:/Program Files/VideoLAN/VLC/vlc.exe"),
                    Path(f"{drive}:/Program Files (x86)/VideoLAN/VLC/vlc.exe"),
                ]
            )
        for path in possible_paths:
            if path.exists():
                return str(path)

    elif system == "Linux":
        linux_paths = [
            Path("/usr/bin/vlc"),
            Path("/usr/local/bin/vlc"),
            Path("/snap/bin/vlc"),
            Path("/flatpak/exports/bin/org.videolan.VLC"),
        ]
        for path in linux_paths:
            if path.exists():
                return str(path)

    elif system == "Darwin":
        mac_paths = [
            Path("/Applications/VLC.app/Contents/MacOS/VLC"),
            Path("~/Applications/VLC.app/Contents/MacOS/VLC").expanduser(),
        ]
        for path in mac_paths:
            if path.exists():
                return str(path)

    return None
