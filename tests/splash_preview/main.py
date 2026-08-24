"""
tests/splash_preview/main.py
-----------------------------
Application Flet Web de comparaison visuelle interactive pour le Splash Screen AIC V3.

Usage:
  uv run flet run tests/splash_preview/main.py --web --port 8570

Routes URL:
  http://localhost:8570/?v=v3current
  http://localhost:8570/?v=v3immersive
  http://localhost:8570/?v=v3fullscreen
"""

import asyncio
import logging
import sys
from pathlib import Path

import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.splash_preview.splash_variants import (  # noqa: E402
    VARIANTS,
    VARIANT_LABELS,
    VARIANT_ORDER,
)
from ui.design_system.colors import ObsidianColors  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("splash_preview_app")


def main(page: ft.Page):
    page.title = "AIC Splash Screen — Laboratoire d'Immersion"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ObsidianColors.BG_DARK
    page.padding = 0
    page.spacing = 0

    current_task = None
    container_slot = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
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

        splash_cls = VARIANTS.get(v_key, VARIANTS["v3immersive"])
        splash_instance = splash_cls(page=page, on_complete=on_splash_complete)

        container_slot.content = splash_instance
        status_text.value = f"Exécution de [{VARIANT_LABELS.get(v_key, v_key)}]..."
        page.update()

        current_task = asyncio.create_task(splash_instance.start_animation_async())

    def on_variant_click(e):
        v_key = e.control.data
        asyncio.create_task(launch_variant(v_key))

    def on_replay_click(e):
        current_v = getattr(page, "_current_v", "v3immersive")
        asyncio.create_task(launch_variant(current_v))

    url_v = page.query.get("v") if page.query else None
    if isinstance(url_v, list):
        url_v = url_v[0]
    initial_v = url_v if url_v in VARIANTS else "v3immersive"
    page._current_v = initial_v

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
                ft.Text("IMMERSION LAB:", size=11, weight=ft.FontWeight.BOLD, color=ObsidianColors.PRIMARY),
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

    asyncio.create_task(launch_variant(initial_v))


if __name__ == "__main__":
    assets_path = str(PROJECT_ROOT / "assets")
    ft.app(target=main, assets_dir=assets_path)
