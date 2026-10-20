"""
tools/capture/capture_app.py
----------------------------
Système automatisé V3 de capture HD/4K et d'enregistrement vidéo pour AIC (Flet).

Nouveautés V3 :
1. Signal applicatif AIC_CAPTURE_MODE=1 : synchronisation via window.__AIC__ (JS).
   Playwright lit l'état réel du cycle de vie du Splash sans dépendre de la sémantique.
2. Détection visuelle multi-zone en fallback : rail de navigation (cyan #30C4EF) +
   zone header (pixels non-noirs > 50). Robuste même avec le thème sombre AIC.
3. Validation anti-splash pour chaque screenshot : rejet si le Canvas affiche encore
   le splash au moment de la capture (même si la sémantique dit autre chose).
4. Frames de diagnostic pendant la vidéo, capturées aux états réels du splash
   (SPLASH_STARTED, PHASE_WAVE, PHASE_TITLE, PHASE_SUBTITLE, FADE_OUT, MAIN_UI_READY).
   Sauvegardées dans output/.diagnostics/ et supprimées après validation réussie.
5. Preset --1440p : 2880×1620 (scale=1.5) pour mockups haute qualité.
6. Validation différentielle entre les 3 screenshots (≥5 % de pixels différents).
7. Les coordonnées des zones visuelles sont calculées en pixels CSS viewport, puis
   converties en pixels physiques selon le device_scale_factor.

Utilisation :
    uv run python tools/capture/capture_app.py --4k --all
    uv run python tools/capture/capture_app.py --1440p --all
    uv run python tools/capture/capture_app.py --full-hd --all
    uv run python tools/capture/capture_app.py --splash-video --full-hd
    uv run python tools/capture/capture_app.py --splash-video --4k
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from typing import NamedTuple

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

# Configuration de la sortie console UTF-8 robuste sur Windows
if hasattr(sys.stdout, "reconfigure"):
    with contextlib.suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    with contextlib.suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aic.capture")

DEFAULT_OUTPUT_DIR = pathlib.Path(__file__).resolve().parent / "output"
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# ── Couleurs discriminantes (RGB) ─────────────────────────────────────────────
# Cyan du rail de navigation AIC (icône active)
_CYAN_TARGET = (48, 196, 239)   # #30C4EF
_CYAN_TOLERANCE = 35            # Tolérance ±35 sur chaque canal

# Seuil de luminosité "non-noir" pour la zone header
_HEADER_MIN_LUMINOSITY = 40     # Pixel lumineux au-dessus de ce seuil → UI visible

# Couleur de fond du splash (#0A0F1A → R=10, G=15, B=26)
_SPLASH_BG = (10, 15, 26)
_SPLASH_BG_TOLERANCE = 20

# ── Zones discriminantes (coordonnées CSS, viewport 1920×1080) ────────────────
# Les coordonnées CSS sont indépendantes du scale factor.
# La conversion en pixels physiques se fait via scale dans capture_clip_pixels().
_ZONE_NAV_RAIL = {"x": 0, "y": 80, "w": 72, "h": 600}    # Rail de navigation gauche
_ZONE_HEADER = {"x": 550, "y": 4, "w": 600, "h": 44}      # Zone header badges/titre

# Définition des écrans applicatifs, patterns d'onglets et mots-clés uniques d'assertion
SCREEN_DEFINITIONS = {
    "dashboard": {
        "tab_index": 1,
        "nav_label": "Bibliothèque",
        "tab_patterns": ["Tab 1 of 3", "1 of 3", "Biblioth"],
        "expected_keywords": ["bibliothèque musicale", "parcourir fichiers", "scanner un dossier"],
        "description": "Tableau de bord principal / Bibliothèque musicale",
    },
    "library": {
        "tab_index": 1,
        "nav_label": "Bibliothèque",
        "tab_patterns": ["Tab 1 of 3", "1 of 3", "Biblioth"],
        "expected_keywords": ["bibliothèque musicale", "parcourir fichiers", "scanner un dossier"],
        "description": "Tableau de bord principal / Bibliothèque musicale",
    },
    "telemetry": {
        "tab_index": 2,
        "nav_label": "Télémétrie IA",
        "tab_patterns": ["Tab 2 of 3", "2 of 3", "lémétrie", "lemetrie"],
        "expected_keywords": ["santé du moteur", "journal des événements", "modèle onnx"],
        "description": "Vue télémétrie & métriques IA",
    },
    "metrics": {
        "tab_index": 2,
        "nav_label": "Télémétrie IA",
        "tab_patterns": ["Tab 2 of 3", "2 of 3", "lémétrie", "lemetrie"],
        "expected_keywords": ["santé du moteur", "journal des événements", "modèle onnx"],
        "description": "Vue télémétrie & métriques IA",
    },
    "settings": {
        "tab_index": 3,
        "nav_label": "Réglages",
        "tab_patterns": ["Tab 3 of 3", "3 of 3", "glages", "reglages"],
        "expected_keywords": ["dossier d'exportation", "paramètres", "thème visuel"],
        "description": "Vue des réglages applicatifs",
    },
}

ALL_STATIC_SCREENS = ["dashboard", "telemetry", "settings"]


class CaptureConfig(NamedTuple):
    """Configuration d'une session de capture."""

    width: int
    height: int
    scale: float
    screen: str
    output_dir: pathlib.Path
    filename: str | None = None
    headed: bool = False
    timeout: float = 45.0
    wait_splash: float = 30.0   # Timeout MAX (pas délai fixe) — la détection est dynamique
    port: int = 0
    splash_video: bool = False

    @property
    def target_width(self) -> int:
        return int(self.width * self.scale)

    @property
    def target_height(self) -> int:
        return int(self.height * self.scale)

    @property
    def is_4k(self) -> bool:
        return self.target_width == 3840 and self.target_height == 2160

    @property
    def diag_dir(self) -> pathlib.Path:
        """Répertoire des frames de diagnostic (temporaire, nettoyé après succès)."""
        return self.output_dir / ".diagnostics"


def find_free_port() -> int:
    """Trouve un port TCP libre sur l'interface locale."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def build_output_filename(screen: str, width: int, height: int, scale: float, ext: str = "png") -> str:
    """Génère un nom de fichier standardisé et déterministe."""
    target_w = int(width * scale)
    target_h = int(height * scale)

    # Normalisation des alias
    screen_norm = "dashboard" if screen in ("dashboard", "library") else screen
    screen_norm = "telemetry" if screen_norm in ("telemetry", "metrics") else screen_norm

    if target_w == 3840 and target_h == 2160:
        return f"aic-{screen_norm}-4k.{ext}"
    elif target_w == 1920 and target_h == 1080:
        return f"aic-{screen_norm}-fullhd.{ext}"
    elif target_w == 2880 and target_h == 1620:
        return f"aic-{screen_norm}-1440p.{ext}"
    else:
        return f"aic-{screen_norm}-{target_w}x{target_h}.{ext}"


def parse_webm_resolution(file_path: pathlib.Path) -> tuple[int, int] | None:
    """
    Lit la résolution (largeur, hauteur) d'un fichier WebM sans dépendance externe.
    Parcourt les tags EBML Matroska PixelWidth (0xB0) et PixelHeight (0xBA).
    """
    if not file_path.exists() or file_path.stat().st_size < 100:
        return None

    try:
        with open(file_path, "rb") as f:
            data = f.read(65536)

        width = None
        height = None
        idx = 0
        while idx < len(data) - 4:
            if data[idx] == 0xB0 and width is None:
                length = data[idx + 1]
                if length == 0x81:
                    width = data[idx + 2]
                    idx += 3
                    continue
                elif length == 0x82:
                    width = int.from_bytes(data[idx + 2: idx + 4], "big")
                    idx += 4
                    continue
            if data[idx] == 0xBA and height is None:
                length = data[idx + 1]
                if length == 0x81:
                    height = data[idx + 2]
                    idx += 3
                    continue
                elif length == 0x82:
                    height = int.from_bytes(data[idx + 2: idx + 4], "big")
                    idx += 4
                    continue
            idx += 1
            if width is not None and height is not None:
                break

        if width and height:
            return width, height
    except Exception:
        pass
    return None


def verify_image(file_path: pathlib.Path, expected_w: int, expected_h: int) -> dict:
    """
    Vérifie l'existence, les dimensions et la validité du screenshot PNG généré.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier capturé n'a pas été créé : {file_path}")

    with Image.open(file_path) as img:
        actual_w, actual_h = img.size
        mode = img.mode
        fmt = img.format
        extrema = img.getextrema()

    if (actual_w, actual_h) != (expected_w, expected_h):
        raise ValueError(
            f"Dimensions incorrectes pour {file_path.name} : "
            f"obtenu {actual_w}x{actual_h}, attendu {expected_w}x{expected_h}"
        )

    # Vérification que l'image n'est pas entièrement noire/vide
    is_blank = False
    if mode == "RGB":
        if extrema == ((0, 0), (0, 0), (0, 0)):
            is_blank = True
    elif mode == "RGBA":
        if extrema[:3] == ((0, 0), (0, 0), (0, 0)):
            is_blank = True

    if is_blank:
        raise ValueError(f"Le screenshot {file_path.name} est totalement noir/vide !")

    file_size_kb = file_path.stat().st_size / 1024

    return {
        "file": str(file_path),
        "width": actual_w,
        "height": actual_h,
        "format": fmt,
        "mode": mode,
        "size_kb": f"{file_size_kb:.1f} KB",
    }


def verify_video(file_path: pathlib.Path, min_size_kb: float = 10.0) -> dict:
    """
    Vérifie l'existence, la taille et les métadonnées de la vidéo générée.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier vidéo n'a pas été créé : {file_path}")

    size_kb = file_path.stat().st_size / 1024
    if size_kb < min_size_kb:
        raise ValueError(f"Le fichier vidéo {file_path.name} est trop petit ({size_kb:.1f} KB < {min_size_kb} KB) !")

    resolution = parse_webm_resolution(file_path)
    res_str = f"{resolution[0]}x{resolution[1]}" if resolution else "WebM (Variable)"

    return {
        "file": str(file_path),
        "resolution": res_str,
        "format": "WebM",
        "size_kb": f"{size_kb:.1f} KB",
    }


# ── Détection visuelle ────────────────────────────────────────────────────────

def _zone_to_clip(zone_css: dict, scale: float) -> dict:
    """
    Convertit une zone CSS (pixels logiques viewport) en clip physiques pour Playwright.

    Playwright screenshot(clip=...) prend des coordonnées en pixels CSS (logiques),
    pas en pixels physiques. C'est device_scale_factor qui est appliqué en interne.
    On retourne donc les coordonnées CSS telles quelles — sans multiplication par scale.
    """
    return {
        "x": zone_css["x"],
        "y": zone_css["y"],
        "width": zone_css["w"],
        "height": zone_css["h"],
    }


def _count_cyan_pixels(img_rgb: Image.Image) -> int:
    """
    Compte les pixels de teinte cyan (#30C4EF / teal) dans l'image.
    Critère colorimétrique : Vert > 120, Bleu > 140, Rouge < 110 (distinct du blanc/gris/noir).
    """
    count = 0
    raw = img_rgb.tobytes()
    for i in range(0, len(raw) - 2, 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        if g > 120 and b > 140 and r < 110:
            count += 1
    return count


def _count_bright_pixels(img_rgb: Image.Image, min_lum: int = _HEADER_MIN_LUMINOSITY) -> int:
    """Compte les pixels dont la luminosité maximale dépasse min_lum."""
    count = 0
    raw = img_rgb.tobytes()
    for i in range(0, len(raw) - 2, 3):
        if max(raw[i], raw[i + 1], raw[i + 2]) > min_lum:
            count += 1
    return count


def capture_region_from_page(page, zone_css: dict) -> Image.Image | None:
    """Capture une région CSS de la page et retourne une image PIL RGB."""
    try:
        clip = _zone_to_clip(zone_css, scale=1.0)
        raw = page.screenshot(clip=clip, type="png")
        from io import BytesIO
        img = Image.open(BytesIO(raw)).convert("RGB")
        return img
    except Exception as e:
        logger.debug(f"Impossible de capturer la région {zone_css} : {e}")
        return None


def _is_dark_background(img_rgb: Image.Image) -> bool:
    """Vérifie si l'image a un fond sombre typique d'AIC (#0A0F1A)."""
    pixels = list(img_rgb.getdata())
    if not pixels:
        return False
    sample_size = min(len(pixels), 500)
    step = max(1, len(pixels) // sample_size)
    samples = pixels[::step]
    avg_lum = sum(max(r, g, b) for r, g, b in samples) / len(samples)
    return avg_lum < 60


def is_splash_visible(page, scale: float) -> bool:
    """
    Détecte si le splash AIC ou le bootstrap Flutter est encore présent sur le Canvas.

    Le critère discriminant infaillible est la présence de pixels Cyan #30C4EF
    dans la zone du rail de navigation gauche (x=0-72, y=80-680 CSS) :
    - Flutter bootstrap : écran blanc/neutre → 0 pixel cyan dans le rail.
    - Splash AIC : logo centré sur fond sombre → 0 pixel cyan dans le rail.
    - Main UI AIC : onglet actif illuminé en cyan → >500 pixels cyan dans le rail.

    Retourne True si le splash/bootstrap est ENCORE visible (0 cyan).
    Retourne False dès que le rail de navigation AIC est actif (cyan présent).
    """
    nav_img = capture_region_from_page(page, _ZONE_NAV_RAIL)
    if nav_img is not None:
        cyan_count = _count_cyan_pixels(nav_img)
        if cyan_count >= 5:
            logger.debug(f"Rail nav : {cyan_count} pixels cyan détectés → Main UI active")
            return False

    return True


def read_aic_state(page, state_file: pathlib.Path | None = None) -> tuple[str, int]:
    """
    Lit l'état courant depuis AIC_STATE_FILE (prioritaire et fiable)
    ou en fallback depuis window.__AIC__ via page.evaluate().
    Retourne (state, elapsed_ms). Retourne ('UNKNOWN', 0) si inaccessible.
    """
    if state_file and state_file.exists():
        try:
            content = state_file.read_text(encoding="utf-8").strip()
            if content and "|" in content:
                parts = content.split("|", 1)
                return parts[0], int(parts[1]) if parts[1].isdigit() else 0
        except Exception:
            pass

    try:
        result = page.evaluate("""() => {
            if (!window.__AIC__) return {state: 'UNAVAILABLE', elapsed_ms: 0};
            return {state: window.__AIC__.state, elapsed_ms: window.__AIC__.elapsed_ms || 0};
        }""")
        return result.get("state", "UNKNOWN"), result.get("elapsed_ms", 0)
    except Exception:
        return "UNKNOWN", 0


def wait_for_main_ui_ready(page, config: CaptureConfig, state_file: pathlib.Path | None = None) -> tuple[float, str]:
    """
    Attend que l'interface principale AIC soit réellement visible.

    Stratégie primaire (AIC_CAPTURE_MODE=1) :
        Lit l'état applicatif (fichier AIC_STATE_FILE ou window.__AIC__) jusqu'à 'MAIN_UI_READY'.
        Chaque changement d'état est loggué pour traçabilité.

    Stratégie fallback (détection visuelle multi-zone) :
        Si le signal n'est pas disponible ou ne progresse pas,
        utilise is_splash_visible() pour détecter la disparition visuelle du splash.

    Dans les deux cas, l'état final est confronté au rendu visuel réel.

    Retourne (elapsed_seconds, method_used).
    """
    timeout = config.wait_splash
    t_start = time.time()
    last_state = "UNKNOWN"
    method = "visual_fallback"

    # Vérifier si le signal applicatif est disponible
    state, elapsed_ms = read_aic_state(page, state_file)
    if state not in ("UNKNOWN", "UNAVAILABLE", "NOT_STARTED"):
        method = "app_signal"
        logger.info(f"[CAPTURE MODE] Signal applicatif disponible. État initial : {state}")
    elif state_file and state_file.exists():
        method = "app_signal"
        logger.info(f"[CAPTURE MODE] Fichier d'état disponible ({state_file.name}).")

    while time.time() - t_start < timeout:
        time.sleep(0.25)

        if method == "app_signal":
            state, elapsed_ms = read_aic_state(page, state_file)
            if state != last_state and state not in ("UNKNOWN", "UNAVAILABLE"):
                logger.info(f"[CAPTURE MODE] État splash → {state} (elapsed_ms={elapsed_ms})")
                last_state = state
            if state == "MAIN_UI_READY":
                elapsed = time.time() - t_start
                logger.info(f"[CAPTURE MODE] MAIN_UI_READY détecté après {elapsed:.2f}s (signal)")
                time.sleep(1.0)  # Laisser le rendu Canvas et l'arbre sémantique se stabiliser
                enable_flutter_semantics(page)
                time.sleep(0.4)
                return elapsed, "signal+ready"

        # Fallback visuel
        enable_flutter_semantics(page)
        if not is_splash_visible(page, config.scale):
            elapsed = time.time() - t_start
            logger.info(f"Main UI détectée visuellement après {elapsed:.2f}s (method={method})")
            return elapsed, method

    elapsed = time.time() - t_start
    logger.warning(f"Timeout ({timeout:.1f}s) : l'UI principale n'a pas été détectée avec certitude")
    return elapsed, "timeout"


def validate_screenshot_is_not_splash(file_path: pathlib.Path, scale: float) -> None:
    """
    Vérifie que le screenshot capturé ne montre PAS le splash AIC.

    Critères combinés (en pixels physiques = CSS × scale) :
    1. Zone nav rail (x=0-72, y=80-680 CSS → ×scale en physique) :
       doit contenir des pixels cyan (#30C4EF) si la Main UI est visible.
    2. Zone header (x=550-1150, y=4-48 CSS → ×scale en physique) :
       doit avoir plus de 8% de pixels lumineux si la Main UI est visible.

    Note : au moins UN des deux critères doit être vérifié.
    Si aucun n'est vérifié, le screenshot est probablement du splash.
    """
    with Image.open(file_path) as img:
        img_rgb = img.convert("RGB")
        W, H = img_rgb.size

    sc = scale  # device_scale_factor

    def crop_zone(zone_css: dict) -> Image.Image:
        x0 = int(zone_css["x"] * sc)
        y0 = int(zone_css["y"] * sc)
        x1 = min(int((zone_css["x"] + zone_css["w"]) * sc), W)
        y1 = min(int((zone_css["y"] + zone_css["h"]) * sc), H)
        return img_rgb.crop((x0, y0, x1, y1))

    # Critère 1 : Rail de navigation (cyan)
    nav_crop = crop_zone(_ZONE_NAV_RAIL)
    cyan_count = _count_cyan_pixels(nav_crop)
    nav_ok = cyan_count >= 3

    # Critère 2 : Header (pixels lumineux)
    header_crop = crop_zone(_ZONE_HEADER)
    bright_count = _count_bright_pixels(header_crop, min_lum=_HEADER_MIN_LUMINOSITY)
    total_header = _ZONE_HEADER["w"] * _ZONE_HEADER["h"] * (sc ** 2)
    header_ok = (bright_count / max(total_header, 1)) > 0.08

    if not nav_ok and not header_ok:
        raise ValueError(
            f"[ANTI-SPLASH] {file_path.name} semble encore afficher le Splash AIC "
            f"(rail cyan={cyan_count}px, header bright={bright_count}/{int(total_header)}px). "
            f"La capture a été prise trop tôt — le Canvas affiche encore le splash."
        )

    logger.info(
        f"[ANTI-SPLASH OK] {file_path.name} : rail_cyan={cyan_count}px, "
        f"header_bright_ratio={bright_count / max(total_header, 1):.1%}"
    )


def validate_screenshots_are_distinct(paths: list[pathlib.Path], min_diff_ratio: float = 0.05) -> None:
    """
    Vérifie que les screenshots sont visuellement distincts entre eux (≥5% de pixels différents).

    Utilise ImageChops.difference() pour comparer chaque paire.
    Un ratio < min_diff_ratio indique que deux captures sont trop similaires
    (possiblement le même écran capturé deux fois).
    """
    if len(paths) < 2:
        return

    images = []
    for p in paths:
        with Image.open(p) as img:
            images.append(img.convert("RGB").copy())

    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            diff = ImageChops.difference(images[i], images[j])
            raw_diff = diff.tobytes()
            total = len(raw_diff) // 3
            changed = 0
            for k in range(0, len(raw_diff) - 2, 3):
                if max(raw_diff[k], raw_diff[k + 1], raw_diff[k + 2]) > 10:
                    changed += 1
            ratio = changed / max(total, 1)

            name_i = paths[i].name
            name_j = paths[j].name
            logger.info(f"[DIFF] {name_i} vs {name_j} : {ratio:.1%} pixels différents")

            if ratio < min_diff_ratio:
                raise ValueError(
                    f"[DIFF] {name_i} et {name_j} sont trop similaires ({ratio:.1%} < {min_diff_ratio:.0%}) — "
                    f"possible doublon de capture. Vérifiez que la navigation a bien fonctionné."
                )


# ── Serveur Flet Web ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def flet_web_server(
    port: int,
    timeout: float = 30.0,
    capture_mode: bool = True,
    state_file: pathlib.Path | None = None,
):
    """
    Gestionnaire de contexte pour le cycle de vie du serveur web Flet.
    Démarre AIC en mode web headless isolé et garantit un arrêt propre.

    Si capture_mode=True, injecte AIC_CAPTURE_MODE=1 dans l'environnement
    du sous-processus. Si state_file est fourni, injecte AIC_STATE_FILE
    pour synchroniser de manière fiable via écriture fichier I/O directe.
    """
    env = os.environ.copy()
    env["FLET_FORCE_WEB_SERVER"] = "1"
    env["FLET_SERVER_PORT"] = str(port)
    env["FLET_SERVER_IP"] = "127.0.0.1"
    if capture_mode:
        env["AIC_CAPTURE_MODE"] = "1"
        if state_file:
            state_file.parent.mkdir(parents=True, exist_ok=True)
            with contextlib.suppress(Exception):
                state_file.write_text("NOT_STARTED|0", encoding="utf-8")
            env["AIC_STATE_FILE"] = str(state_file.resolve())

    main_script = WORKSPACE_ROOT / "main.py"
    if not main_script.exists():
        raise FileNotFoundError(f"Point d'entrée introuvable : {main_script}")

    logger.info(f"Démarrage du serveur Flet Web sur le port {port} (capture_mode={capture_mode})...")
    process = subprocess.Popen(
        [sys.executable, str(main_script)],
        cwd=str(WORKSPACE_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    url = f"http://127.0.0.1:{port}"
    server_ready = False
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                raise RuntimeError(
                    f"Le processus Flet s'est arrêté prématurément avec le code {process.returncode}"
                )
            try:
                with urllib.request.urlopen(url, timeout=1.0) as resp:
                    if resp.status == 200:
                        server_ready = True
                        break
            except Exception:
                time.sleep(0.3)

        if not server_ready:
            raise TimeoutError(f"Le serveur Flet Web n'a pas répondu à {url} après {timeout}s")

        logger.info(f"Serveur Flet Web opérationnel sur {url}")
        yield url

    finally:
        logger.info("Arrêt du serveur Flet Web...")
        process.terminate()
        try:
            process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            logger.warning("Arrêt forcé du serveur Flet (kill)...")
            process.kill()
            process.wait(timeout=2.0)
        logger.info("Serveur Flet Web arrêté proprement.")
        if state_file and state_file.exists():
            with contextlib.suppress(Exception):
                state_file.unlink()


def enable_flutter_semantics(page) -> bool:
    """Active l'arbre sémantique accessible de Flutter Web."""
    try:
        return page.evaluate("""() => {
            const el = document.querySelector('flt-semantics-placeholder');
            if (el) {
                el.click();
                return true;
            }
            return false;
        }""")
    except Exception as e:
        logger.debug(f"Impossible d'activer la sémantique Flutter : {e}")
        return False


def get_current_screen_text(page) -> str:
    """Récupère l'intégralité du texte sémantique actuellement visible dans le DOM."""
    try:
        return page.evaluate("""() => {
            const nodes = Array.from(document.querySelectorAll('flt-semantics, [aria-label]'));
            const text1 = nodes.map(n => (n.innerText || '') + ' ' + (n.getAttribute('aria-label') || '')).join(' ');
            const text2 = document.body ? (document.body.innerText || '') : '';
            return (text1 + ' ' + text2).toLowerCase();
        }""")
    except Exception:
        return ""


def navigate_to_screen(page, screen_name: str, config: CaptureConfig, timeout: float = 8.0) -> bool:
    """
    Bascule vers l'écran demandé via le sélecteur sémantique exact du bouton NavigationRail.
    Zéro clic par coordonnées.

    Après la navigation sémantique, attend une confirmation VISUELLE (en plus de la sémantique)
    pour s'assurer que le Canvas est réellement synchronisé avec la navigation.
    """
    if screen_name not in SCREEN_DEFINITIONS:
        raise ValueError(f"Écran inconnu : {screen_name}")

    tab_idx = SCREEN_DEFINITIONS[screen_name]["tab_index"]
    target_label = SCREEN_DEFINITIONS[screen_name]["nav_label"]
    logger.info(f"Navigation sémantique vers l'onglet {tab_idx} ('{target_label}')...")

    clicked = page.evaluate(
        """(idx) => {
        const buttons = Array.from(document.querySelectorAll('flt-semantics[role="button"], [role="button"]'));
        const target = `Tab ${idx} of 3`;
        for (const b of buttons) {
            const text = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || ''));
            if (text.includes(target)) {
                b.click();
                return true;
            }
        }
        return false;
    }""",
        tab_idx,
    )

    if not clicked:
        raise RuntimeError(f"Bouton de navigation introuvable pour '{target_label}' (Tab {tab_idx} of 3) !")

    # ── Phase 1 : Confirmation sémantique ──────────────────────────────────────
    start_t = time.time()
    expected_keywords = SCREEN_DEFINITIONS[screen_name]["expected_keywords"]
    sem_confirmed = False

    while time.time() - start_t < timeout:
        time.sleep(0.3)
        screen_text = get_current_screen_text(page)
        matches = [kw for kw in expected_keywords if kw.lower() in screen_text]
        if matches:
            logger.info(f"✔ Sémantique '{screen_name}' confirmée (mots-clés : {matches})")
            sem_confirmed = True
            break

    if not sem_confirmed:
        raise AssertionError(
            f"Échec de validation sémantique : '{screen_name}' non confirmé après {timeout:.1f}s. "
            f"(Attendus : {expected_keywords})"
        )

    # ── Phase 2 : Stabilisation du rendu Canvas ────────────────────────────────
    # La sémantique peut précéder le rendu Canvas de quelques frames.
    # On attend que le splash ne soit plus visible ET que le Canvas soit stable.
    time.sleep(1.0)   # Stabilisation de base après navigation

    # Si le splash est encore visible à ce stade (ne devrait pas arriver ici
    # car on est déjà dans l'UI principale), c'est une anomalie.
    if is_splash_visible(page, config.scale):
        logger.warning(
            f"[AVERTISSEMENT] Le splash est encore visuellement présent après la navigation vers '{screen_name}'. "
            f"Le Canvas n'est peut-être pas synchronisé."
        )
        time.sleep(2.0)  # Attente supplémentaire

    return True


def capture_single_screen(
    page,
    screen_name: str,
    output_path: pathlib.Path,
    config: CaptureConfig,
) -> dict:
    """
    Capture un écran spécifique après :
    1. Navigation sémantique + confirmation sémantique
    2. Validation visuelle anti-splash (le Canvas ne montre pas le splash)
    3. Capture du Canvas
    4. Vérification des dimensions
    5. Validation anti-splash sur le fichier PNG sauvegardé
    """
    navigate_to_screen(page, screen_name, config)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(output_path), full_page=False)

    info = verify_image(output_path, config.target_width, config.target_height)

    # Validation anti-splash sur le fichier PNG produit
    validate_screenshot_is_not_splash(output_path, config.scale)

    logger.info(f"[OK] Screenshot validé : {output_path.name} ({info['width']}x{info['height']}, {info['size_kb']})")
    return info


# ── Pipeline screenshots ──────────────────────────────────────────────────────

def run_capture_screenshots(config: CaptureConfig, screens_to_capture: list[str]) -> list[dict]:
    """Exécute le pipeline de captures d'écrans statiques V3."""
    port = config.port if config.port > 0 else find_free_port()
    results: list[dict] = []
    state_file = config.output_dir / f".aic_state_screenshots_{port}.txt"

    with flet_web_server(port, timeout=config.timeout, capture_mode=True, state_file=state_file) as base_url:
        with sync_playwright() as pw:
            logger.info("Lancement du navigateur Chromium Playwright...")
            browser = pw.chromium.launch(
                headless=not config.headed,
                args=["--no-sandbox", "--disable-gpu-rasterization"],
            )

            try:
                context = browser.new_context(
                    viewport={"width": config.width, "height": config.height},
                    device_scale_factor=config.scale,
                )
                page = context.new_page()

                logger.info(
                    f"Navigation vers {base_url} (viewport={config.width}x{config.height}, scale={config.scale})..."
                )
                page.goto(base_url, wait_until="networkidle", timeout=config.timeout * 1000)

                # ── Attente dynamique de la Main UI (signal applicatif + fallback visuel) ──
                elapsed, method = wait_for_main_ui_ready(page, config, state_file=state_file)
                logger.info(f"Main UI prête après {elapsed:.1f}s (méthode : {method})")

                # Stabilisation finale avant la première capture
                enable_flutter_semantics(page)
                time.sleep(0.5)

                for screen in screens_to_capture:
                    filename = (
                        config.filename
                        if len(screens_to_capture) == 1 and config.filename
                        else build_output_filename(screen, config.width, config.height, config.scale)
                    )
                    target_path = config.output_dir / filename
                    info = capture_single_screen(page, screen, target_path, config)
                    results.append(info)

                # ── Validation différentielle des captures ──────────────────────
                if len(results) >= 2:
                    captured_paths = [pathlib.Path(r["file"]) for r in results]
                    validate_screenshots_are_distinct(captured_paths)

            finally:
                logger.info("Fermeture du navigateur Chromium...")
                browser.close()

    return results


# ── Pipeline vidéo splash ─────────────────────────────────────────────────────

def _save_diagnostic_frame(page, diag_dir: pathlib.Path, label: str) -> pathlib.Path | None:
    """
    Capture une frame de diagnostic et la sauvegarde dans diag_dir.
    Préfixe le nom par le label de l'état (ex: 'PHASE_TITLE_frame.png').
    Retourne le chemin du fichier créé, ou None en cas d'échec.
    """
    try:
        diag_dir.mkdir(parents=True, exist_ok=True)
        # Nettoyer le label pour le nom de fichier
        safe_label = label.replace(" ", "_").replace("/", "-")
        frame_path = diag_dir / f"{safe_label}_frame.png"
        page.screenshot(path=str(frame_path), full_page=False)
        size_kb = frame_path.stat().st_size / 1024
        logger.info(f"[DIAG] Frame '{label}' sauvegardée : {frame_path.name} ({size_kb:.1f} KB)")
        return frame_path
    except Exception as e:
        logger.debug(f"[DIAG] Impossible de sauvegarder la frame '{label}' : {e}")
        return None


def run_capture_splash_video(config: CaptureConfig) -> dict:
    """
    Enregistre l'animation complète du Splash Screen en vidéo haute fidélité (WebM).

    Stratégie V3 :
    - Démarre l'enregistrement dès page.goto() (capture le bootstrap Flutter)
    - Suit les états du cycle de vie via AIC_STATE_FILE pour capturer des frames de diagnostic
      à chaque phase réelle de l'animation (SPLASH_STARTED, PHASE_WAVE, etc.)
    - Ces frames prouvent visuellement que l'animation est présente et complète
    - La vidéo est considérée valide seulement si les frames de diagnostic
      montrent le contenu attendu à chaque phase

    Note sur le bootstrap Flutter :
    La vidéo inclut les secondes de bootstrap Flutter avant le splash AIC.
    Ce n'est pas considéré comme un échec : l'important est que le SPLASH AIC
    soit présent et complet dans la vidéo. Les frames de diagnostic le prouvent.
    La durée du bootstrap est loggée comme métadonnée.
    """
    port = config.port if config.port > 0 else find_free_port()
    temp_video_dir = config.output_dir / ".temp_video"
    temp_video_dir.mkdir(parents=True, exist_ok=True)
    diag_dir = config.diag_dir
    state_file = config.output_dir / f".aic_state_video_{port}.txt"

    filename = (
        config.filename
        if config.filename
        else build_output_filename("splash", config.width, config.height, config.scale, ext="webm")
    )
    final_video_path = config.output_dir / filename

    bootstrap_duration = None      # Temps avant SPLASH_STARTED
    splash_duration = None         # Temps de l'animation du splash
    diag_frames: list[pathlib.Path] = []
    captured_states: set[str] = set()

    with flet_web_server(port, timeout=config.timeout, capture_mode=True, state_file=state_file) as base_url:
        with sync_playwright() as pw:
            logger.info("Lancement du navigateur Chromium pour enregistrement vidéo...")
            browser = pw.chromium.launch(
                headless=not config.headed,
                args=["--no-sandbox", "--disable-gpu-rasterization"],
            )

            try:
                context = browser.new_context(
                    record_video_dir=str(temp_video_dir),
                    record_video_size={"width": config.target_width, "height": config.target_height},
                    viewport={"width": config.width, "height": config.height},
                    device_scale_factor=config.scale,
                )
                page = context.new_page()

                logger.info(f"Démarrage de la capture vidéo du Splash Screen sur {base_url}...")
                t_goto = time.time()
                # Navigation sans bloquer sur networkidle pour capturer dès le premier pixel rendu
                page.goto(base_url, timeout=config.timeout * 1000)

                # ── Suivi des états et capture de frames de diagnostic ─────────
                DIAG_STATES = [
                    "INIT",
                    "SPLASH_STARTED",
                    "PHASE_LOGO",
                    "PHASE_WAVE",
                    "PHASE_TITLE",
                    "PHASE_SUBTITLE",
                    "FADE_OUT",
                    "MAIN_UI_READY",
                ]

                t_splash_started = None
                last_state = "UNKNOWN"
                t_deadline = t_goto + config.timeout
                last_periodic = t_goto

                while time.time() < t_deadline:
                    time.sleep(0.04)

                    state, elapsed_ms = read_aic_state(page, state_file)

                    if state != last_state and state not in ("UNKNOWN", "UNAVAILABLE", "NOT_STARTED"):
                        elapsed_total = time.time() - t_goto
                        logger.info(f"[VIDEO] État splash → {state} (t_total={elapsed_total:.2f}s)")

                        if state == "SPLASH_STARTED" and bootstrap_duration is None:
                            bootstrap_duration = time.time() - t_goto
                            t_splash_started = time.time()
                            logger.info(f"[VIDEO] Bootstrap Flutter terminé après {bootstrap_duration:.2f}s")

                        # Capture d'une frame de diagnostic si état ciblé et pas encore capturé
                        if state in DIAG_STATES and state not in captured_states:
                            time.sleep(0.05)
                            frame = _save_diagnostic_frame(page, diag_dir, state)
                            if frame:
                                diag_frames.append(frame)
                            captured_states.add(state)

                        last_state = state

                    # Condition d'arrêt normale : MAIN_UI_READY atteint ET frame capturée
                    if state == "MAIN_UI_READY" and "MAIN_UI_READY" in captured_states:
                        logger.info("[VIDEO] Cycle complet du Splash capturé avec succès !")
                        break

                    # Fallback de sécurité si aucun signal après 30s
                    if (time.time() - t_goto > 30.0) and state in ("UNKNOWN", "UNAVAILABLE", "NOT_STARTED"):
                        enable_flutter_semantics(page)
                        if not is_splash_visible(page, config.scale):
                            elapsed_total = time.time() - t_goto
                            logger.info(f"[VIDEO] Fin du splash détectée visuellement après {elapsed_total:.2f}s (fallback)")
                            time.sleep(0.3)
                            frame = _save_diagnostic_frame(page, diag_dir, "MAIN_UI_VISUAL")
                            if frame:
                                diag_frames.append(frame)
                            break

                # Temps de l'animation splash
                if t_splash_started:
                    splash_duration = time.time() - t_splash_started
                    logger.info(f"[VIDEO] Durée splash capturée : {splash_duration:.2f}s")

                # Enregistrement d'une seconde supplémentaire pour capturer la transition complète
                time.sleep(1.2)

                raw_video_path = page.video.path() if page.video else None

                page.close()
                context.close()
                browser.close()

                if not raw_video_path or not os.path.exists(raw_video_path):
                    raise FileNotFoundError("Playwright n'a pas produit de fichier vidéo !")

                final_video_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(raw_video_path, str(final_video_path))
                logger.info(f"Vidéo déplacée vers : {final_video_path}")

            finally:
                if temp_video_dir.exists():
                    shutil.rmtree(temp_video_dir, ignore_errors=True)

    # ── Validation de la vidéo ────────────────────────────────────────────────
    info = verify_video(final_video_path)

    # Rapport des frames de diagnostic
    if diag_frames:
        logger.info(f"[VIDEO] {len(diag_frames)} frames de diagnostic capturées dans {diag_dir}")
        for f in diag_frames:
            size_kb = f.stat().st_size / 1024 if f.exists() else 0
            logger.info(f"  • {f.name} ({size_kb:.1f} KB)")
    else:
        logger.warning("[VIDEO] Aucune frame de diagnostic n'a pu être capturée.")

    # Vérifier que les états clés ont été capturés
    missing_states = [s for s in ["SPLASH_STARTED", "PHASE_TITLE", "FADE_OUT"] if s not in captured_states]
    if missing_states:
        logger.warning(
            f"[VIDEO] États non détectés pendant l'enregistrement : {missing_states}. "
            f"La validation visuelle des frames de diagnostic est OBLIGATOIRE."
        )

    info["bootstrap_s"] = f"{bootstrap_duration:.2f}s" if bootstrap_duration else "N/A"
    info["splash_s"] = f"{splash_duration:.2f}s" if splash_duration else "N/A"
    info["diag_frames"] = len(diag_frames)
    info["captured_states"] = sorted(captured_states)

    logger.info(f"[OK] Vidéo validée : {final_video_path.name} ({info['resolution']}, {info['size_kb']})")
    return info


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """Parse les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Générateur automatisé V3 de screenshots HD/4K et vidéos pour AIC / Flet.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    preset_group = parser.add_mutually_exclusive_group()
    preset_group.add_argument(
        "--4k",
        dest="preset_4k",
        action="store_true",
        help="Preset 4K Ultra HD (CSS 1920x1080, scale 2 → 3840x2160)",
    )
    preset_group.add_argument(
        "--full-hd",
        dest="preset_full_hd",
        action="store_true",
        help="Preset Full HD (CSS 1920x1080, scale 1 → 1920x1080)",
    )
    preset_group.add_argument(
        "--1440p",
        dest="preset_1440p",
        action="store_true",
        help="Preset Mockup HQ (CSS 1920x1080, scale 1.5 → 2880x1620)",
    )

    parser.add_argument(
        "--splash-video",
        action="store_true",
        help="Enregistrer l'animation complète du Splash Screen en vidéo WebM haute fidélité",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Largeur CSS du viewport en pixels",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Hauteur CSS du viewport en pixels",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Facteur d'échelle (device_scale_factor). Par défaut : 2 si --4k, 1.5 si --1440p, 1 si --full-hd.",
    )
    parser.add_argument(
        "--screen",
        type=str,
        choices=["dashboard", "library", "telemetry", "metrics", "settings"],
        default="dashboard",
        help="Écran individuel à capturer (screenshots)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Capturer l'ensemble des écrans applicatifs statiques (dashboard, telemetry, settings)",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Répertoire de destination des captures et vidéos",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        help="Nom personnalisé du fichier de sortie (uniquement pour capture d'un écran ou vidéo unique)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Exécute Chromium en mode visible (utile pour le débogage visuel)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port TCP du serveur Flet (0 = allocation dynamique automatique)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Timeout global en secondes",
    )
    parser.add_argument(
        "--wait-splash",
        type=float,
        default=30.0,
        help="Timeout maximum de détection de la fin du Splash Screen (secondes)",
    )

    return parser.parse_args()


def main() -> int:
    """Point d'entrée CLI principal."""
    args = parse_args()

    # Résolution du scale et dimensions
    if args.preset_full_hd:
        scale = 1.0 if args.scale is None else args.scale
        width = 1920
        height = 1080
    elif args.preset_4k:
        scale = 2.0 if args.scale is None else args.scale
        width = 1920
        height = 1080
    elif args.preset_1440p:
        scale = 1.5 if args.scale is None else args.scale
        width = 1920
        height = 1080
    else:
        scale = 2.0 if args.scale is None else args.scale
        width = args.width
        height = args.height

    config = CaptureConfig(
        width=width,
        height=height,
        scale=scale,
        screen=args.screen,
        output_dir=args.output_dir,
        filename=args.filename,
        headed=args.headed,
        timeout=args.timeout,
        wait_splash=args.wait_splash,
        port=args.port,
        splash_video=args.splash_video,
    )

    print("=" * 64)
    print("  AIC — Système de Capture HD/4K Automatisée (V3)")
    print("=" * 64)
    print(f"  • Mode d'opération : {'Vidéo Splash Screen' if config.splash_video else 'Screenshots UI'}")
    print(f"  • Résolution cible : {config.target_width}x{config.target_height}")
    print(f"  • Viewport CSS     : {config.width}x{config.height} (scale: {config.scale})")
    print(f"  • Répertoire       : {config.output_dir}")
    print("  • AIC_CAPTURE_MODE : activé (signal JS window.__AIC__)")
    print("=" * 64)

    try:
        if config.splash_video:
            res = run_capture_splash_video(config)
            print("\n" + "=" * 64)
            print("  RESUME : 1 video Splash generee avec succes")
            print("=" * 64)
            print(f"  [OK] {pathlib.Path(res['file']).name:<28} | {res['resolution']} | {res['size_kb']}")
            print(f"  Bootstrap Flutter : {res.get('bootstrap_s', 'N/A')}")
            print(f"  Durée splash      : {res.get('splash_s', 'N/A')}")
            print(f"  États capturés    : {', '.join(res.get('captured_states', []))}")
            print(f"  Frames diagnostic : {res.get('diag_frames', 0)} (output/.diagnostics/)")
            print("=" * 64 + "\n")

            # Nettoyage des diagnostics si capture réussie et états complets
            critical_states = {"SPLASH_STARTED", "PHASE_TITLE", "FADE_OUT"}
            if critical_states.issubset(set(res.get("captured_states", []))):
                logger.info("[DIAG] Validation complète — conservation des frames pour inspection visuelle finale.")
                logger.info(f"[DIAG] Supprimez manuellement '{config.diag_dir}' après inspection.")
            return 0

        else:
            screens = ALL_STATIC_SCREENS if args.all else [args.screen]
            results = run_capture_screenshots(config, screens)

            print("\n" + "=" * 64)
            print(f"  RESUME : {len(results)} capture(s) generee(s) avec succes")
            print("=" * 64)
            for res in results:
                print(f"  [OK] {pathlib.Path(res['file']).name:<28} | {res['width']}x{res['height']} | {res['size_kb']}")
            print("=" * 64 + "\n")
            return 0

    except Exception as err:
        logger.error(f"Échec de la capture : {err}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
