"""
tests/splash_preview/main.py
-----------------------------
Laboratoire Flet Web de validation visuelle du Splash Screen AIC.

SOURCE DE VERITE : origin/main (af092ec63b397a3edf43165e49627c4d6b282fa9)

Usage:
    uv run flet run tests/splash_preview/main.py --web --port 8570

Variantes disponibles :
    http://localhost:8570/?v=origin_main    <- Reference origin/main (nouveaux logos)
    http://localhost:8570/?v=production     <- Production locale (branch dev)
"""

import asyncio
import logging
import sys
from pathlib import Path

import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.splash_preview.splash_variants import VARIANT_LABELS, VARIANT_ORDER, VARIANTS  # noqa: E402
from ui.design_system.colors import ObsidianColors  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("splash_preview_app")


def main(page: ft.Page):
    page.title = "AIC Splash Screen — Laboratoire (Reference: origin/main)"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ObsidianColors.BG_DARK
    page.padding = 0
    page.spacing = 0

    # Enregistrement des polices Cinzel Decorative (identique a l'app principale)
    page.fonts = {
        "Cinzel Decorative": "fonts/CinzelDecorative-Regular.ttf",
        "Cinzel Decorative Regular": "fonts/CinzelDecorative-Regular.ttf",
        "Cinzel Decorative Bold": "fonts/CinzelDecorative-Bold.ttf",
    }

    current_task = None
    container_slot = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
    status_text = ft.Text("Pret", size=12, color=ObsidianColors.TEXT_MUTED)

    def on_splash_complete():
        logger.info("Splash animation terminee (callback fired)")
        status_text.value = "Animation terminee"
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

        splash_cls = VARIANTS.get(v_key, VARIANTS["origin_main"])
        splash_instance = splash_cls(page=page, on_complete=on_splash_complete)

        container_slot.content = splash_instance
        status_text.value = f"Execution de [{VARIANT_LABELS.get(v_key, v_key)}]..."
        page.update()

        current_task = asyncio.create_task(splash_instance.start_animation_async())

    def on_variant_click(e):
        v_key = e.control.data
        asyncio.create_task(launch_variant(v_key))

    def on_replay_click(e):
        current_v = getattr(page, "_current_v", "origin_main")
        asyncio.create_task(launch_variant(current_v))

    # Parsing securise du query param "v"
    url_v = None
    try:
        if page.query:
            if hasattr(page.query, "get"):
                try:
                    url_v = page.query.get("v")
                except KeyError:
                    url_v = None
            if not url_v and hasattr(page.query, "v"):
                url_v = getattr(page.query, "v", None)
    except Exception as qe:
        logger.warning(f"Query param error: {qe}")
        url_v = None

    if isinstance(url_v, list):
        url_v = url_v[0] if url_v else None
    initial_v = url_v if (url_v and url_v in VARIANTS) else "origin_main"
    page._current_v = initial_v

    buttons = []
    for v_key in VARIANT_ORDER:
        btn = ft.TextButton(
            content=ft.Text(VARIANT_LABELS[v_key], size=11),
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
                ft.Text(
                    "SPLASH LAB:",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ObsidianColors.PRIMARY,
                ),
                ft.Row(buttons, spacing=4, scroll=ft.ScrollMode.AUTO),
                replay_btn,
                status_text,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.Padding(16, 8, 16, 8),
        bgcolor="rgba(22, 25, 34, 0.90)",
        border=ft.Border(bottom=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
    )

    page.add(
        ft.Column(
            [control_bar, container_slot],
            expand=True,
            spacing=0,
        )
    )

    asyncio.create_task(launch_variant(initial_v))


if __name__ == "__main__":
    assets_path = str((PROJECT_ROOT / "assets").resolve())
    ft.app(target=main, assets_dir=assets_path)
