"""
tests/splash_comparison/main.py
--------------------------------
Application Flet Web isolée de comparaison objective OLD vs NEW Splash Screen AIC.
Permet d'exécuter et d'observer côte à côte ou successivement l'ancien (OLD v1) et le nouveau (NEW v2) Splash.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Ajout de la racine du projet dans sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.environ["FLET_ASSETS_DIR"] = str(project_root / "assets")

import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.theme import get_dark_theme
from utils.path_utils import get_asset_path

from tests.splash_comparison.old.splash_screen_old import SplashScreenOLD
from tests.splash_comparison.new.splash_screen_new import SplashScreenNEW

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("splash_comparison")


def main(page: ft.Page) -> None:
    logger.info("SPLASH COMPARISON: Initialisation de la page Flet Web")
    page.title = "AIC — Splash Screen Comparison (OLD vs NEW)"
    page.bgcolor = ObsidianColors.BG_DARK
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_dark_theme()
    page.dark_theme = get_dark_theme()
    page.padding = 0

    font_bold = get_asset_path("fonts/CinzelDecorative-Bold.ttf")
    font_regular = get_asset_path("fonts/CinzelDecorative-Regular.ttf")
    fonts_dict = {}
    if font_bold and font_bold.exists():
        fonts_dict["Cinzel Decorative Bold"] = str(font_bold)
    if font_regular and font_regular.exists():
        fonts_dict["Cinzel Decorative Regular"] = str(font_regular)
    if fonts_dict:
        page.fonts = fonts_dict

    current_splash = None

    def render_control_panel(active_label: str = "Aucun"):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"Mode actuel: {active_label}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.ACCENT_CYAN,
                    ),
                    ft.Container(width=16),
                    ft.Button(
                        "Lancer OLD Splash (v1)",
                        icon=ft.Icons.PLAY_ARROW,
                        on_click=lambda e: run_splash("OLD"),
                    ),
                    ft.Button(
                        "Lancer NEW Splash (v2)",
                        icon=ft.Icons.PLAY_ARROW,
                        on_click=lambda e: run_splash("NEW"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=12,
            bgcolor=ObsidianColors.SURFACE_DARK,
        )

    def finish_splash_callback(version_name: str) -> None:
        logger.info(f"SPLASH COMPARISON: {version_name} Splash terminé !")
        completion_card = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=48, color=ObsidianColors.PRIMARY),
                    ft.Text(
                        f"Animation {version_name} Splash terminée avec succès !",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        "Sélectionnez une version pour rejouer la comparaison.",
                        size=14,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                    ft.Container(height=16),
                    render_control_panel(active_label=f"{version_name} (Terminé)"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=ObsidianColors.BG_DARK,
            expand=True,
        )
        page.clean()
        page.add(completion_card)
        page.update()

    def run_splash(version: str) -> None:
        nonlocal current_splash
        logger.info(f"SPLASH COMPARISON: Démarrage de {version}...")
        page.clean()

        if version == "OLD":
            current_splash = SplashScreenOLD(
                page=page,
                on_complete=lambda: finish_splash_callback("OLD"),
            )
        else:
            current_splash = SplashScreenNEW(
                page=page,
                on_complete=lambda: finish_splash_callback("NEW"),
            )

        page.add(current_splash)
        page.update()

        async def _async_start():
            logger.info(f"SPLASH COMPARISON: Démarrage immédiat animation {version}...")
            await asyncio.sleep(0.3)
            await current_splash.start_animation_async()

        page.run_task(_async_start)

    # Démarrage automatique par route / paramètre d'URL (?version=old ou ?version=new)
    version_param = ""
    route_str = str(page.route or "").lower()
    query_str = str(getattr(page, "query", "")).lower()

    if "version=old" in route_str or "version=old" in query_str or "/old" in route_str:
        version_param = "OLD"
    elif "version=new" in route_str or "version=new" in query_str or "/new" in route_str:
        version_param = "NEW"

    if version_param in ("OLD", "NEW"):
        run_splash(version_param)
    else:
        initial_view = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "AIC — BANC D'ESSAI COMPARATIF SPLASH SCREEN",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        "Comparaison objective visuelle & temporelle OLD (v1) vs NEW (v2)",
                        size=14,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                    ft.Container(height=24),
                    render_control_panel(active_label="Sélectionnez une version"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=ObsidianColors.BG_DARK,
            expand=True,
        )
        page.add(initial_view)
        page.update()


if __name__ == "__main__":
    assets_path = str(project_root / "assets")
    ft.app(target=main, assets_dir=assets_path)
