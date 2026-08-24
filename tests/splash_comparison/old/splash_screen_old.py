"""
tests/splash_comparison/old/splash_screen_old.py
--------------------------------------------------
Ancienne version du Splash Screen AIC (Commit 73707ef - Obsidian Horizon v1).
Rendu Flet 0.86.4 adaptatif (Icon Box 100x100 + Égaliseur 5 barres animées + Halo Ambre réactif + Typographie système).
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path

logger = logging.getLogger("splash_old")


class SplashScreenOLD(ft.Container):
    """
    Implémentation exacte de l'ANCIEN SplashScreen (v1).
    - Logo icon.svg / graphic_eq dans carte Obsidian Surface (100x100)
    - Égaliseur audio 5 barres dynamiques #FE8F40
    - Pulsation de halo BoxShadow Ambre translucide (#40F59E0B)
    - Typographie système AIC + Audio Intelligence Companion
    - Séquence rapide ~2.3s
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.on_complete_callback = on_complete

        # ── 1. Chargement de l'icône/logo ────────────────────────────────────
        svg_path = get_asset_path("icon.svg") or get_asset_path("icon.png")
        icon_src = str(svg_path) if svg_path and svg_path.exists() else None

        if icon_src:
            logo_content = ft.Image(
                src=icon_src,
                width=64,
                height=64,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            logo_content = ft.Icon(
                ft.Icons.GRAPHIC_EQ,
                size=48,
                color=ObsidianColors.PRIMARY,
            )

        # ── 2. Barres d'égaliseur audio animées (#FE8F40) ─────────────────────
        self.wave_bar1 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)
        self.wave_bar2 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
        self.wave_bar3 = ft.Container(width=3, height=22, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.wave_bar4 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
        self.wave_bar5 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)

        self.wave_container = ft.Row(
            [
                self.wave_bar1,
                self.wave_bar2,
                self.wave_bar3,
                self.wave_bar4,
                self.wave_bar5,
            ],
            spacing=3,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        # Conteneur du Logo avec Halo réactif (100x100)
        self.logo_box = ft.Container(
            content=ft.Stack(
                [
                    logo_content,
                    ft.Container(
                        content=self.wave_container,
                        alignment=ft.Alignment(0, 0.55),
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            width=110,
            height=110,
            border_radius=Radii.LG,
            bgcolor=ObsidianColors.SURFACE_DARK,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.92),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.04),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        self.wave_reveal_line = ft.Container(
            width=0,
            height=2,
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=1,
            opacity=0.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 3. Titre "AIC" ────────────────────────────────────────────────────
        self.title_text = ft.Text(
            "AIC",
            size=38,
            weight=ft.FontWeight.BOLD,
            color=ObsidianColors.TEXT_PRIMARY,
        )

        self.title_box = ft.Container(
            content=self.title_text,
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 4. Sous-titre "Audio Intelligence Companion" ──────────────────────
        self.subtitle_text = ft.Text(
            "Audio Intelligence Companion",
            size=13,
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.TEXT_MUTED,
        )

        self.subtitle_box = ft.Container(
            content=self.subtitle_text,
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 5. Layout global ──────────────────────────────────────────────────
        super().__init__(
            content=ft.Column(
                [
                    self.logo_box,
                    ft.Container(height=16),
                    self.wave_reveal_line,
                    ft.Container(height=4),
                    self.title_box,
                    ft.Container(height=4),
                    self.subtitle_box,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
            bgcolor=ObsidianColors.BG_DARK,
            opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        """Séquence d'animation asynchrone OLD (~2.3s total)."""
        logger.info("OLD SPLASH: START")
        callback_called = False
        try:
            # 1. Apparition fluide du Logo (0 -> 100ms)
            await asyncio.sleep(0.05)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(scale=1.0)
            self.logo_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.logo_box)

            # 2. Éveil de l'onde sonore (400ms)
            await asyncio.sleep(0.35)
            self.wave_container.opacity = 1.0
            self._safe_update(self.wave_container)

            # 3. Impulsion Halo Ambre & expansion des barres (750ms)
            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=6,
                blur_radius=28,
                color="#40FE8F40",  # Halo ambre
                offset=ft.Offset(0, 0),
            )
            self.wave_bar1.height = 14
            self.wave_bar2.height = 24
            self.wave_bar3.height = 32
            self.wave_bar4.height = 24
            self.wave_bar5.height = 14
            self._safe_update(self.logo_box)

            # 4. Titre "AIC" (1000ms)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            # Atténuation douce du halo
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=14,
                color="#1AFE8F40",
                offset=ft.Offset(0, 0),
            )
            self._safe_update(self.logo_box)

            # 5. Apparition Sous-titre (1350ms)
            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            # 6. Maintien et fondu de sortie (1900ms -> 2300ms)
            await asyncio.sleep(0.60)
            logger.info("OLD SPLASH: ANIMATION COMPLETE")
            self.opacity = 0.0
            self._safe_update(self)

            await asyncio.sleep(0.40)
        except Exception as e:
            logger.error(f"OLD SPLASH ERROR: {e}")
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                self.on_complete_callback()

    def _safe_update(self, control: ft.Control) -> None:
        try:
            if control and self.page and control.page:
                control.update()
        except Exception:
            pass
