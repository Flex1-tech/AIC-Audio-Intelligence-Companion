"""
tests/test_capture_tool.py
--------------------------
Tests unitaires pour l'outil de capture HD/4K V3 (tools.capture.capture_app).

Vérifie :
1. La génération canonique des noms de fichiers de sortie (PNG, WebM, 4K, 1440p, Full HD).
2. Le calcul des résolutions cibles à partir du viewport et du device_scale_factor.
3. Le parseur d'en-tête EBML / WebM pour la détection de résolution vidéo sans dépendance externe.
4. La validation d'images PNG avec Pillow (dimensions, rejet des images noires/vides).
5. La validation de vidéos WebM (taille minimale, format).
6. La recherche dynamique de port TCP disponible.
7. La détection de pixels cyan (#30C4EF) dans une image synthétique.
8. La détection de pixels lumineux (bright) dans une image synthétique.
9. La validation anti-splash sur images synthétiques (Main UI vs Splash).
10. La validation différentielle entre deux screenshots (ImageChops).
"""

import pathlib

import pytest
from PIL import Image

from tools.capture.capture_app import (
    CaptureConfig,
    _count_bright_pixels,
    _count_cyan_pixels,
    _CYAN_TARGET,
    _ZONE_HEADER,
    _ZONE_NAV_RAIL,
    build_output_filename,
    find_free_port,
    parse_webm_resolution,
    validate_screenshot_is_not_splash,
    validate_screenshots_are_distinct,
    verify_image,
    verify_video,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_png(tmp_path: pathlib.Path, filename: str, size: tuple, color: tuple) -> pathlib.Path:
    """Crée un PNG synthétique de taille et couleur données."""
    p = tmp_path / filename
    img = Image.new("RGB", size, color=color)
    img.save(p, format="PNG")
    return p


def _make_png_with_zone(
    tmp_path: pathlib.Path,
    filename: str,
    canvas_size: tuple,
    canvas_color: tuple,
    zone_x: int,
    zone_y: int,
    zone_w: int,
    zone_h: int,
    zone_color: tuple,
) -> pathlib.Path:
    """
    Crée un PNG avec un fond uniforme et une zone colorée spécifique.
    Permet de simuler une image avec rail de navigation ou header visible.
    """
    p = tmp_path / filename
    img = Image.new("RGB", canvas_size, color=canvas_color)

    # Peindre la zone colorée
    for y in range(zone_y, min(zone_y + zone_h, canvas_size[1])):
        for x in range(zone_x, min(zone_x + zone_w, canvas_size[0])):
            img.putpixel((x, y), zone_color)

    img.save(p, format="PNG")
    return p


# ── Tests build_output_filename ────────────────────────────────────────────────


def test_build_output_filename_presets():
    """Vérifie la nomenclature canonique des fichiers pour les presets standard (PNG)."""
    # 4K screenshots
    assert build_output_filename("dashboard", 1920, 1080, 2.0) == "aic-dashboard-4k.png"
    assert build_output_filename("library", 1920, 1080, 2.0) == "aic-dashboard-4k.png"
    assert build_output_filename("telemetry", 1920, 1080, 2.0) == "aic-telemetry-4k.png"
    assert build_output_filename("metrics", 1920, 1080, 2.0) == "aic-telemetry-4k.png"
    assert build_output_filename("settings", 1920, 1080, 2.0) == "aic-settings-4k.png"

    # Full HD screenshots
    assert build_output_filename("dashboard", 1920, 1080, 1.0) == "aic-dashboard-fullhd.png"
    assert build_output_filename("telemetry", 1920, 1080, 1.0) == "aic-telemetry-fullhd.png"
    assert build_output_filename("settings", 1920, 1080, 1.0) == "aic-settings-fullhd.png"

    # 1440p (Mockup HQ)
    assert build_output_filename("dashboard", 1920, 1080, 1.5) == "aic-dashboard-1440p.png"
    assert build_output_filename("telemetry", 1920, 1080, 1.5) == "aic-telemetry-1440p.png"
    assert build_output_filename("settings", 1920, 1080, 1.5) == "aic-settings-1440p.png"

    # Custom resolutions
    assert build_output_filename("dashboard", 1280, 720, 1.0) == "aic-dashboard-1280x720.png"


def test_build_output_filename_video():
    """Vérifie la nomenclature des fichiers vidéo (WebM)."""
    assert build_output_filename("splash", 1920, 1080, 2.0, ext="webm") == "aic-splash-4k.webm"
    assert build_output_filename("splash", 1920, 1080, 1.0, ext="webm") == "aic-splash-fullhd.webm"
    assert build_output_filename("splash", 1920, 1080, 1.5, ext="webm") == "aic-splash-1440p.webm"


# ── Tests CaptureConfig ────────────────────────────────────────────────────────


def test_capture_config_target_dimensions():
    """Vérifie les propriétés calculées de CaptureConfig."""
    cfg_4k = CaptureConfig(
        width=1920,
        height=1080,
        scale=2.0,
        screen="dashboard",
        output_dir=pathlib.Path("output"),
    )
    assert cfg_4k.target_width == 3840
    assert cfg_4k.target_height == 2160
    assert cfg_4k.is_4k is True

    cfg_fhd = CaptureConfig(
        width=1920,
        height=1080,
        scale=1.0,
        screen="dashboard",
        output_dir=pathlib.Path("output"),
    )
    assert cfg_fhd.target_width == 1920
    assert cfg_fhd.target_height == 1080
    assert cfg_fhd.is_4k is False

    cfg_1440p = CaptureConfig(
        width=1920,
        height=1080,
        scale=1.5,
        screen="dashboard",
        output_dir=pathlib.Path("output"),
    )
    assert cfg_1440p.target_width == 2880
    assert cfg_1440p.target_height == 1620
    assert cfg_1440p.is_4k is False


def test_capture_config_diag_dir():
    """Vérifie que diag_dir est bien sous output/.diagnostics/."""
    output = pathlib.Path("tools/capture/output")
    cfg = CaptureConfig(
        width=1920,
        height=1080,
        scale=2.0,
        screen="dashboard",
        output_dir=output,
    )
    assert cfg.diag_dir == output / ".diagnostics"


# ── Tests find_free_port ───────────────────────────────────────────────────────


def test_find_free_port():
    """Vérifie que find_free_port retourne un numéro de port TCP valide."""
    port = find_free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535


# ── Tests verify_image ─────────────────────────────────────────────────────────


def test_verify_image_success(tmp_path: pathlib.Path):
    """Vérifie qu'une image valide et de dimension exacte est validée sans erreur."""
    test_file = _make_png(tmp_path, "sample_4k.png", (3840, 2160), (30, 40, 50))
    info = verify_image(test_file, 3840, 2160)
    assert info["width"] == 3840
    assert info["height"] == 2160
    assert info["format"] == "PNG"
    assert info["mode"] == "RGB"


def test_verify_image_dimension_mismatch(tmp_path: pathlib.Path):
    """Vérifie qu'une anomalie de dimension lève une exception ValueError."""
    test_file = _make_png(tmp_path, "bad_dims.png", (1920, 1080), (30, 40, 50))
    with pytest.raises(ValueError, match="Dimensions incorrectes"):
        verify_image(test_file, 3840, 2160)


def test_verify_image_blank_rejection(tmp_path: pathlib.Path):
    """Vérifie qu'une image entièrement noire est rejetée."""
    test_file = _make_png(tmp_path, "blank.png", (3840, 2160), (0, 0, 0))
    with pytest.raises(ValueError, match="totalement noir/vide"):
        verify_image(test_file, 3840, 2160)


# ── Tests verify_video ─────────────────────────────────────────────────────────


def test_verify_video_too_small(tmp_path: pathlib.Path):
    """Vérifie qu'un fichier vidéo incomplet ou corrompu (<10 Ko) est rejeté."""
    test_file = tmp_path / "corrupt.webm"
    test_file.write_bytes(b"\x1a\x45\xdf\xa3" * 10)
    with pytest.raises(ValueError, match="trop petit"):
        verify_video(test_file, min_size_kb=10.0)


# ── Tests parse_webm_resolution ────────────────────────────────────────────────


def test_parse_webm_resolution_synthetic(tmp_path: pathlib.Path):
    """Vérifie le parseur EBML sur une séquence binaire synthétique."""
    test_file = tmp_path / "test.webm"
    content = bytearray(b"\x00" * 32)
    content += bytes([0xB0, 0x82, 0x07, 0x80])  # PixelWidth = 1920
    content += bytes([0xBA, 0x82, 0x04, 0x38])  # PixelHeight = 1080
    content += b"\x00" * 100
    test_file.write_bytes(content)

    res = parse_webm_resolution(test_file)
    assert res == (1920, 1080)


# ── Tests détection de pixels ──────────────────────────────────────────────────


def test_count_cyan_pixels_exact_color():
    """Vérifie que _count_cyan_pixels détecte le cyan AIC exact (#30C4EF)."""
    cr, cg, cb = _CYAN_TARGET
    img = Image.new("RGB", (10, 10), color=(cr, cg, cb))
    count = _count_cyan_pixels(img)
    assert count == 100  # Tous les pixels sont cyan


def test_count_cyan_pixels_no_cyan():
    """Vérifie que _count_cyan_pixels ne détecte pas de cyan sur fond sombre."""
    img = Image.new("RGB", (10, 10), color=(10, 15, 26))  # Fond splash #0A0F1A
    count = _count_cyan_pixels(img)
    assert count == 0


def test_count_cyan_pixels_tolerance():
    """Vérifie que _count_cyan_pixels accepte des couleurs proches (±35) du cyan."""
    cr, cg, cb = _CYAN_TARGET
    # Couleur légèrement décalée (dans la tolérance de 35)
    img = Image.new("RGB", (5, 5), color=(cr + 20, cg - 20, cb + 10))
    count = _count_cyan_pixels(img)
    assert count == 25  # Tous les pixels dans la tolérance


def test_count_bright_pixels_dark():
    """Vérifie que _count_bright_pixels retourne 0 sur un fond entièrement sombre."""
    img = Image.new("RGB", (20, 20), color=(10, 15, 26))  # Fond splash
    count = _count_bright_pixels(img, min_lum=40)
    assert count == 0


def test_count_bright_pixels_bright():
    """Vérifie que _count_bright_pixels détecte les pixels lumineux."""
    img = Image.new("RGB", (10, 10), color=(200, 150, 100))
    count = _count_bright_pixels(img, min_lum=40)
    assert count == 100  # Tous lumineux


# ── Tests validate_screenshot_is_not_splash ────────────────────────────────────


def test_validate_screenshot_not_splash_pass_with_cyan_rail(tmp_path: pathlib.Path):
    """
    Vérifie qu'un screenshot avec rail de navigation cyan (#30C4EF) passe la validation.
    Simule une image Full HD (1920x1080, scale=1) avec le rail peint en cyan.
    """
    cr, cg, cb = _CYAN_TARGET
    # Image 1920x1080 avec rail de navigation peint en cyan
    test_file = _make_png_with_zone(
        tmp_path,
        "dashboard_fhd.png",
        canvas_size=(1920, 1080),
        canvas_color=(10, 15, 26),  # Fond sombre (comme AIC)
        zone_x=_ZONE_NAV_RAIL["x"],
        zone_y=_ZONE_NAV_RAIL["y"],
        zone_w=_ZONE_NAV_RAIL["w"],
        zone_h=_ZONE_NAV_RAIL["h"],
        zone_color=(cr, cg, cb),  # Cyan AIC exact
    )
    # Ne doit PAS lever d'exception
    validate_screenshot_is_not_splash(test_file, scale=1.0)


def test_validate_screenshot_not_splash_pass_with_bright_header(tmp_path: pathlib.Path):
    """
    Vérifie qu'un screenshot avec header lumineux passe la validation.
    Simule une image 4K (3840x2160, scale=2) avec le header peint en blanc.
    """
    test_file = _make_png_with_zone(
        tmp_path,
        "settings_4k.png",
        canvas_size=(3840, 2160),
        canvas_color=(10, 15, 26),
        zone_x=int(_ZONE_HEADER["x"] * 2),  # ×scale=2
        zone_y=int(_ZONE_HEADER["y"] * 2),
        zone_w=int(_ZONE_HEADER["w"] * 2),
        zone_h=int(_ZONE_HEADER["h"] * 2),
        zone_color=(220, 220, 220),  # Header lumineux
    )
    validate_screenshot_is_not_splash(test_file, scale=2.0)


def test_validate_screenshot_not_splash_fail_on_splash(tmp_path: pathlib.Path):
    """
    Vérifie qu'un screenshot entièrement sombre (comme le splash AIC) est rejeté.
    """
    # Image entièrement sombre = fond splash, aucun rail ni header visible
    test_file = _make_png(tmp_path, "splash_bg.png", (1920, 1080), (10, 15, 26))
    with pytest.raises(ValueError, match="ANTI-SPLASH"):
        validate_screenshot_is_not_splash(test_file, scale=1.0)


# ── Tests validate_screenshots_are_distinct ────────────────────────────────────


def test_validate_screenshots_are_distinct_pass(tmp_path: pathlib.Path):
    """Vérifie que deux screenshots visuellement différents passent la validation."""
    img1 = _make_png(tmp_path, "screen1.png", (1920, 1080), (50, 100, 150))
    img2 = _make_png(tmp_path, "screen2.png", (1920, 1080), (200, 80, 40))
    # Ne doit pas lever d'exception
    validate_screenshots_are_distinct([img1, img2], min_diff_ratio=0.05)


def test_validate_screenshots_are_distinct_fail_identical(tmp_path: pathlib.Path):
    """Vérifie que deux screenshots identiques sont rejetés comme doublons."""
    img1 = _make_png(tmp_path, "dup1.png", (1920, 1080), (50, 100, 150))
    img2 = _make_png(tmp_path, "dup2.png", (1920, 1080), (50, 100, 150))
    with pytest.raises(ValueError, match="trop similaires"):
        validate_screenshots_are_distinct([img1, img2], min_diff_ratio=0.05)


def test_validate_screenshots_single_no_error(tmp_path: pathlib.Path):
    """Vérifie que la validation différentielle ne lève pas d'erreur sur un seul fichier."""
    img1 = _make_png(tmp_path, "only.png", (1920, 1080), (50, 100, 150))
    validate_screenshots_are_distinct([img1])  # Pas d'erreur attendue
