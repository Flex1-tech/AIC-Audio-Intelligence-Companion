"""
tests/splash_preview/main.py
-----------------------------
Application Flet Web de comparaison visuelle interactive pour le Splash Screen AIC V3.

Usage:
  uv run flet run tests/splash_preview/main.py --web --port 8560

Routes URL:
  http://localhost:8560/?v=old
  http://localhost:8560/?v=new
  http://localhost:8560/?v=v3base
  http://localhost:8560/?v=v3svg
  http://localhost:8560/?v=v3cinzel
  http://localhost:8560/?v=v3cyan
  http://localhost:8560/?v=v3glow
"""

import asyncio
import logging
import sys
from pathlib import Path

import flet as ft

# Inserer le dossier racine du projet dans sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.splash_preview.splash_variants import (
    VARIANTS,
    VARIANT_LABELS,
    VARIANT_ORDER,
)
from ui.design_system.colors import ObsidianColors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("splash_preview_app")


def main(page: ft.Page):
    page.title = "AIC Splash Screen — Laboratoire V3"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ObsidianColors.BG_DARK
    page.padding = 0
    page.spacing = 0

    # Charger les polices si disponibles dans assets/fonts/
    fonts_dir = PROJECT_ROOT / "assets" / "fonts"
    if fonts_dir.exists():
        page.fonts = {
            "Cinzel Decorative Bold": str(fonts_dir / "CinzelDecorative-Bold.ttf"),
            "Cinzel Decorative Regular": str(fonts_dir / "CinzelDecorative-Regular.ttf"),
        }

    current_task = None
    container_slot = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    # Status / Info bar
    status_text = ft.Text("Prêt", size=12, color=ObsidianColors.TEXT_MUTED)

    def on_splash_complete():
        logger.info("Splash animation terminée (callback fired)")
        status_text.value = "Animation terminée"
        page.update()

    async def launch_variant(v_key: str):
        nonlocal current_task
        page._current_v = v_key
        if current_task and not current_task.done():
            current_task.cancel()
            try:
                await current_task
            except Exception:
                pass

        splash_cls = VARIANTS.get(v_key, VARIANTS["v3base"])
        splash_instance = splash_cls(page=page, on_complete=on_splash_complete)

        container_slot.content = splash_instance
        status_text.value = f"Exécution de [{VARIANT_LABELS.get(v_key, v_key)}]..."
        page.update()

        current_task = asyncio.create_task(splash_instance.start_animation_async())

    def on_variant_click(e):
        v_key = e.control.data
        asyncio.create_task(launch_variant(v_key))

    def on_replay_click(e):
        # Relancer la variante courante
        current_v = getattr(page, "_current_v", "v3base")
        asyncio.create_task(launch_variant(current_v))

    # Determiner la variante initiale depuis l'URL
    url_v = page.query.get("v") if page.query else None
    if isinstance(url_v, list):
        url_v = url_v[0]
    initial_v = url_v if url_v in VARIANTS else "v3base"
    page._current_v = initial_v

    # Construire la barre de controle superieure
    buttons = []
    for v_key in VARIANT_ORDER:
        btn = ft.TextButton(
            text=VARIANT_LABELS[v_key],
            data=v_key,
            on_click=on_variant_click,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ObsidianColors.TEXT_SECONDARY,
                    ft.ControlState.HOVERED: ObsidianColors.PRIMARY,
                }
            ),
        )
        buttons.append(btn)

    replay_btn = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Relancer l'animation",
        icon_color=ObsidianColors.PRIMARY,
        on_click=on_replay_click,
    )

    control_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text("PREVIEW LAB:", size=11, weight=ft.FontWeight.BOLD, color=ObsidianColors.ACCENT_CYAN),
                ft.Row(buttons, spacing=4, scroll=ft.ScrollMode.AUTO),
                replay_btn,
                status_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        bgcolor="rgba(22, 25, 34, 0.90)",
        border=ft.border.only(bottom=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
    )

    page.add(
        ft.Column(
            [
                control_bar,
                container_slot,
            ],
            expand=True,
            spacing=0,
        )
    )

    # Lancer l'animation au chargement
    asyncio.create_task(launch_variant(initial_v))


if __name__ == "__main__":
    assets_path = str(PROJECT_ROOT / "assets")
    ft.app(target=main, assets_dir=assets_path)
