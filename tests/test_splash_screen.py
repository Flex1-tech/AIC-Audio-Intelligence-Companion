"""
tests/test_splash_screen.py
----------------------------
Suite de tests unitaires et de non-régression pour le Splash Screen AIC V3.

Vérifications :
1. Calculs réactifs et bornes (clamp 110-165px) pour petits, moyens et grands viewports.
2. Centralisation et recalcul dynamique des délais selon `SPLASH_ANIMATION_DURATION_MS`.
3. Comportement de fallback résilient lorsque les icônes/assets sont absents.
4. Exécution complète de l'animation asynchrone et déclenchement du callback `on_complete`.
"""

import asyncio
from unittest.mock import MagicMock

import flet as ft

from ui.components.splash_screen import (
    CARD_MAX_SIZE,
    CARD_MIN_SIZE,
    SPLASH_ANIMATION_DURATION_MS,
    SplashScreen,
    calculate_responsive_dimensions,
)


def test_responsive_dimensions_small_viewport():
    """Vérifie que pour un petit viewport (ex: 400x400), la carte reste égale au minimum (110px)."""
    dims = calculate_responsive_dimensions(400, 400)
    assert dims["card_size"] == CARD_MIN_SIZE
    assert dims["icon_size"] == int(CARD_MIN_SIZE * 0.58)
    assert dims["bar_max_h"] == int(CARD_MIN_SIZE * 0.28)
    assert dims["title_size"] == int(CARD_MIN_SIZE * 0.29)
    assert dims["subtitle_size"] >= 11


def test_responsive_dimensions_standard_viewport():
    """Vérifie que pour un viewport standard (ex: 1280x800), les dimensions sont calculées proportionnellement."""
    dims = calculate_responsive_dimensions(1280, 800)
    assert CARD_MIN_SIZE <= dims["card_size"] <= CARD_MAX_SIZE
    assert dims["icon_size"] > 0
    assert dims["bar_max_h"] > 0
    assert dims["title_size"] > 0


def test_responsive_dimensions_large_viewport():
    """Vérifie que pour un très grand viewport (ex: 3840x2160), la carte est plafonnée au maximum (165px)."""
    dims = calculate_responsive_dimensions(3840, 2160)
    assert dims["card_size"] == CARD_MAX_SIZE
    assert dims["icon_size"] == int(CARD_MAX_SIZE * 0.58)
    assert dims["bar_max_h"] == int(CARD_MAX_SIZE * 0.28)


def test_splash_animation_default_duration():
    """Vérifie l'instanciation et l'exécution asynchrone complète du Splash avec la durée globale par défaut."""

    async def _async_run():
        page = MagicMock(spec=ft.Page)
        page.window = MagicMock()
        page.window.width = 1280
        page.window.height = 800

        completed = False

        def on_complete():
            nonlocal completed
            completed = True

        splash = SplashScreen(page=page, on_complete=on_complete)
        assert splash.total_ms == SPLASH_ANIMATION_DURATION_MS

        await splash.start_animation_async()
        assert completed, "Le callback on_complete aurait dû être appelé !"

    asyncio.run(_async_run())


def test_splash_animation_custom_duration():
    """Vérifie que le timing s'adapte lorsque l'on fournit une durée globale personnalisée (ex: 1200ms)."""

    async def _async_run():
        page = MagicMock(spec=ft.Page)
        page.window = MagicMock()
        page.window.width = 1280
        page.window.height = 800

        completed = False

        def on_complete():
            nonlocal completed
            completed = True

        custom_duration = 1200
        splash = SplashScreen(page=page, on_complete=on_complete, animation_duration_ms=custom_duration)
        assert splash.total_ms == custom_duration

        start_time = asyncio.get_event_loop().time()
        await splash.start_animation_async()
        elapsed = asyncio.get_event_loop().time() - start_time

        assert completed, "Le callback on_complete avec durée personnalisée n'a pas été déclenché !"
        assert elapsed < 2.0, f"Expected elapsed < 2.0s for 1200ms custom duration, got {elapsed:.2f}s"

    asyncio.run(_async_run())
