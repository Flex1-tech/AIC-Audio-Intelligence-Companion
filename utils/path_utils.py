"""
utils/path_utils.py
-------------------
Gestionnaire cross-plateforme déterministe pour la résolution des chemins d'accès :
- Ressources embarquées (assets, modèles ONNX, icônes)
- Données utilisateur modifiables (base LanceDB, fichiers de logs, configuration)

Garantit la compatibilité multi-plateforme : Windows (.exe), Linux (AppImage/deb/bin) et macOS (.app).
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


def get_user_data_dir() -> Path:
    """
    Retourne le répertoire de données utilisateur propre à l'OS.

    Emplacements standards :
    - Windows : %APPDATA%/AIC (ex: C:\\Users\\<user>\\AppData\\Roaming\\AIC)
    - macOS : ~/Library/Application Support/AIC
    - Linux : $XDG_DATA_HOME/AIC ou ~/.local/share/AIC
    """
    if os.name == "nt":
        base_path = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base_path = Path.home() / "Library" / "Application Support"
    else:  # Linux / Unix
        xdg = os.environ.get("XDG_DATA_HOME")
        base_path = Path(xdg) if xdg else Path.home() / ".local" / "share"

    data_dir = base_path / "AIC"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def write_crash_log(exc_type, exc_value, exc_tb, origin: str = "CRASH") -> Path:
    """
    Écrit la trace complète de l'exception dans des emplacements persistants garantis :
    1. %APPDATA%/AIC/logs/aic_crash.log (emplacement principal officiel)
    2. %APPDATA%/AIC/aic_crash.log
    3. CWD/aic_crash.log
    4. ~/aic_crash.log
    """
    import traceback

    lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    content = f"\n{'='*72}\n[{origin}] {sys.executable}\n" + "".join(lines)

    primary_target = get_user_data_dir() / "logs" / "aic_crash.log"
    targets = [
        primary_target,
        get_user_data_dir() / "aic_crash.log",
        Path.cwd() / "aic_crash.log",
        Path.home() / "aic_crash.log",
    ]
    for dest in targets:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            continue

    return primary_target


def get_asset_path(filename: str) -> Optional[Path]:
    """
    Résolution multi-fallback des ressources embarquées (assets, modèles ML, icônes).

    Ordre des candidats inspectés :
    1. FLET_ASSETS_DIR (si défini par le runtime Flet)
    2. Structure d'assets Flutter desktop par plateforme (Windows/Linux/macOS)
    3. Emplacement de l'exécutable binaire (PyInstaller/serious_python)
    4. Répertoire racine du projet Python (Path(__file__))
    5. Répertoire de travail courant (CWD)
    """
    path_obj = Path(filename)
    if path_obj.is_absolute() and path_obj.is_file():
        return path_obj.resolve()

    clean_name = path_obj.name
    rel_path = path_obj
    candidates = []

    # 1. Variable d'environnement Flet runtime
    flet_assets = os.environ.get("FLET_ASSETS_DIR")
    if flet_assets:
        flet_p = Path(flet_assets)
        candidates.extend([flet_p / rel_path, flet_p / clean_name])

    # 2. Emplacement relatif à l'exécutable (Flutter Desktop bundle / serious_python)
    if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
        exe_dir = Path(sys.executable).resolve().parent
        # Windows / Linux Flutter layout
        candidates.extend(
            [
                exe_dir / "data" / "flutter_assets" / "assets" / rel_path,
                exe_dir / "data" / "flutter_assets" / "assets" / clean_name,
                exe_dir / "data" / "flutter_assets" / rel_path,
                exe_dir / "data" / "flutter_assets" / clean_name,
                exe_dir / "assets" / rel_path,
                exe_dir / "assets" / clean_name,
                exe_dir / rel_path,
                exe_dir / clean_name,
            ]
        )
        # macOS App Bundle layout
        if sys.platform == "darwin":
            mac_resources = exe_dir.parent / "Resources" / "flutter_assets"
            candidates.extend(
                [
                    mac_resources / "assets" / rel_path,
                    mac_resources / "assets" / clean_name,
                    mac_resources / rel_path,
                    mac_resources / clean_name,
                ]
            )

    # 3. PyInstaller sys._MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        mp = Path(meipass)
        candidates.extend(
            [
                mp / "assets" / rel_path,
                mp / "assets" / clean_name,
                mp / rel_path,
                mp / clean_name,
            ]
        )

    # 4. Arborescence du code source Python (Path(__file__))
    root_dir = Path(__file__).resolve().parent.parent
    candidates.extend(
        [
            root_dir / "assets" / rel_path,
            root_dir / "assets" / clean_name,
            root_dir / rel_path,
            root_dir / clean_name,
        ]
    )

    # 5. Répertoire de travail courant (CWD)
    cwd = Path.cwd()
    candidates.extend(
        [
            cwd / "assets" / rel_path,
            cwd / "assets" / clean_name,
            cwd / rel_path,
            cwd / clean_name,
        ]
    )

    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.resolve()
        except Exception:
            continue

    return None


def setup_logging() -> logging.Logger:
    """
    Initialise la journalisation applicative dans logs/aic.log et la console.
    """
    log_dir = get_user_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "aic.log"

    logger = logging.getLogger("AIC")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"))

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
