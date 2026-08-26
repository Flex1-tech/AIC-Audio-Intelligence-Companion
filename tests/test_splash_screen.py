"""
tests/test_splash_screen.py
----------------------------
Suite de tests unitaires et de non-regression pour le Splash Screen AIC.

Source de verite : origin/main (SHA af092ec63b397a3edf43165e49627c4d6b282fa9)

Verifications :
1. Calculs reactifs et bornes (clamp 300-560 px) pour 7 resolutions d'ecran.
2. Resolution des deux calques SVG officiels (layer_letterform.svg + layer_wave.svg).
3. Instanciation et execution asynchrone complete de SplashOriginMain dans le laboratoire.
4. Declenchement du callback on_complete.
5. Composant production SplashScreen (ui/components/splash_screen.py).
"""

import asyncio
from unittest.mock import MagicMock

import flet as ft
import pytest

from tests.splash_preview.splash_variants import (
    SplashOriginMain,
    SplashV3Target,
    SPLASH_ANIMATION_DURATION_MS,
    calculate_target_responsive_dimensions,
)
from ui.components.splash_screen import (
    CARD_MAX_SIZE,
    CARD_MIN_SIZE,
    SPLASH_ANIMATION_DURATION_MS as PROD_SPLASH_DURATION_MS,
    SplashScreen,
    calculate_responsive_dimensions,
)
from utils.path_utils import get_asset_path


@pytest.mark.parametrize(
    "vw, vh, expected_logo",
    [
        (360, 640, 300),  # Mobile narrow -> clamp min 300
        (400, 400, 300),  # Square viewport -> clamp min 300
        (768, 1024, 499),  # Tablet portrait -> 768 * 0.65 = 499
        (1280, 720, 468),  # Small laptop -> 720 * 0.65 = 468
        (1920, 1080, 560),  # Full HD -> clamp max 560
        (2560, 1440, 560),  # QHD 2K -> clamp max 560
        (3840, 2160, 560),  # 4K -> clamp max 560
    ],
)
def test_origin_main_responsive_dimensions(vw, vh, expected_logo):
    """
    Verifie le sizing responsif conforme a origin/main :
    logo_size = clamp(300, min(vw,vh) * 0.65, 560)
    """
    dims = calculate_target_responsive_dimensions(vw, vh)
    assert dims["logo_size"] == expected_logo, f"@{vw}x{vh}: attendu {expected_logo}, obtenu {dims['logo_size']}"


def test_official_svg_assets_exist():
    """Verifie que les calques SVG officiels existent dans le dossier assets."""
    lf = get_asset_path("layer_letterform.svg")
    wv = get_asset_path("layer_wave.svg")
    icon = get_asset_path("icon.svg")

    assert lf is not None and lf.exists(), "layer_letterform.svg doit exister !"
    assert wv is not None and wv.exists(), "layer_wave.svg doit exister !"
    assert icon is not None and icon.exists(), "icon.svg doit exister !"


def test_svg_assets_have_no_background_rect():
    """
    Verifie que les SVG sont transparents (pas de <rect> de fond).
    Les logos ont ete modifies pour retirer le fond noir integre.
    """
    for fname in ("layer_letterform.svg", "layer_wave.svg"):
        p = get_asset_path(fname)
        content = p.read_text(encoding="utf-8")
        assert "<rect" not in content, f"{fname} ne doit pas contenir de <rect> (fond opaque detecte)"


def test_splash_origin_main_instantiation():
    """Verifie l'instanciation de SplashOriginMain sur Full HD (1920x1080)."""
    page = MagicMock(spec=ft.Page)
    page.window = MagicMock()
    page.window.width = 1920
    page.window.height = 1080

    splash = SplashOriginMain(page=page)
    assert splash.total_ms == SPLASH_ANIMATION_DURATION_MS
    assert splash.logo_size == 560  # clamp max


def test_splash_origin_main_animation_executes():
    """Verifie l'execution asynchrone complete et le declenchement de on_complete."""

    async def _run():
        page = MagicMock(spec=ft.Page)
        page.window = MagicMock()
        page.window.width = 800
        page.window.height = 600

        completed = False

        def on_done():
            nonlocal completed
            completed = True

        splash = SplashOriginMain(page=page, on_complete=on_done)
        await splash.start_animation_async()
        assert completed, "Le callback on_complete doit etre appele apres l'animation !"

    asyncio.run(_run())


def test_production_splash_screen_instantiation():
    """Verifie que le composant production SplashScreen s'instancie sans erreur."""
    page = MagicMock(spec=ft.Page)
    page.window = MagicMock()
    page.window.width = 1280
    page.window.height = 720

    splash = SplashScreen(page=page)
    assert splash.total_ms == PROD_SPLASH_DURATION_MS
    dims = calculate_responsive_dimensions(1280, 720)
    assert CARD_MIN_SIZE <= dims["card_size"] <= CARD_MAX_SIZE


def test_splash_v3_target_alias():
    """Verifie que SplashV3Target est un alias vers SplashOriginMain."""
    assert SplashV3Target is SplashOriginMain
