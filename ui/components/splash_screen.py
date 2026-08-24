"""
ui/components/splash_screen.py
-------------------------------
Splash Screen AIC V3.1 — Évolution Conservatrice (Ambre Pur & Amplitude Accrue).

Architecture :
- Baseline : Fondation V3 / OLD v1 (Carte Obsidian 110×110 px centrée).
- Identité couleur audio : 100% Ambre (#FE8F40 / ObsidianColors.PRIMARY).
  * Equalizer = Ambre #FE8F40
  * Halo BoxShadow = Ambre #FE8F40
  * Sous-titre = Ambre #FE8F40
- Amplitude animation :
  * Barres d'égaliseur 4px de large (vs 3px), hauteur max 40px (vs 32px) +25% de mouvement.
  * Halo pulsant réactif renforcé (spread=8, blur=34 → spread=3, blur=18).
- Glow ambiant radial Ambre doux (#FE8F40 à 10% d'opacité) en arrière-plan.
- Typographie : Système Bold 38pt (lisibilité maximale instantanée).
- Rythme strict ~2.3 secondes.
- Fallback automatique ft.Icons.GRAPHIC_EQ si assets absents.
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path

logger = logging.getLogger("aic.splash")


class SplashScreen(ft.Container):
    """
    Splash Screen AIC V3.1.
    Fondation V3 (110×110 px, 2.3s) avec signal audio Ambre #FE8F40 pur
    et amplitude visuelle d'égaliseur accrue (max 40px).
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        logger.info("SPLASH V3.1: INIT")
        self.on_complete_callback = on_complete

        # Dimensions écran pour le glow ambiant ambre
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700

        # ── 1. Résolution du logo (icon.svg → icon.png → fallback icône) ─────
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

        # ── 2. Barres égaliseur audio (#FE8F40 Ambre — Amplitude accrue) ─────
        self.wave_bar1 = ft.Container(width=4, height=10, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)
        self.wave_bar2 = ft.Container(width=4, height=18, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.wave_bar3 = ft.Container(width=4, height=28, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.wave_bar4 = ft.Container(width=4, height=18, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.wave_bar5 = ft.Container(width=4, height=10, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)

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

        # ── 3. Carte logo avec halo Ambre réactif (110×110) ───────────────────
        self.logo_box = ft.Container(
            content=ft.Stack(
                [
                    logo_content,
                    ft.Container(
                        content=self.wave_container,
                        alignment=ft.Alignment(0, 0.58),
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

        # ── 4. Glow ambiant de fond (Ambre 10% opacité) ───────────────────────
        self.bg_glow = ft.Container(
            width=min(420, w),
            height=min(420, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=[
                    "rgba(254, 143, 64, 0.10)",  # Ambre Audio
                    "rgba(15, 17, 23, 0.0)",
                ],
                stops=[0.0, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 5. Ligne séparatrice ambre ─────────────────────────────────────────
        self.wave_reveal_line = ft.Container(
            width=0,
            height=2,
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=1,
            opacity=0.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 6. Titre "AIC" (Système Bold — Blanc #F9FAFB) ──────────────────────
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

        # ── 7. Sous-titre (Ambre #FE8F40 — Identité Audio Pur) ────────────────
        self.subtitle_text = ft.Text(
            "Audio Intelligence Companion",
            size=13,
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.PRIMARY,  # Ambre #FE8F40
        )

        self.subtitle_box = ft.Container(
            content=self.subtitle_text,
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 8. Layout global ──────────────────────────────────────────────────
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(
                        content=self.bg_glow,
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    ft.Column(
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
                ],
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
            bgcolor=ObsidianColors.BG_DARK,
            opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )
        logger.info("SPLASH V3.1: BUILD")

    async def start_animation_async(self) -> None:
        """
        Séquence d'animation asynchrone V3.1 (~2.3s total).
        Égaliseur amplitude accrue (max 40px) + Halo ambre vif.
        """
        logger.info("SPLASH V3.1: ANIMATION START")
        callback_called = False
        try:
            # Phase 1 : Apparition fond ambiant & Logo (t=0 → t=50ms)
            await asyncio.sleep(0.05)
            self.bg_glow.opacity = 1.0
            self._safe_update(self.bg_glow)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(scale=1.0)
            self.logo_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.logo_box)

            # Phase 2 : Éveil de l'onde sonore (t=400ms)
            await asyncio.sleep(0.35)
            self.wave_container.opacity = 1.0
            self._safe_update(self.wave_container)

            # Phase 3 : Impulsion Halo Ambre vif & expansion barres max 40px (t=700ms)
            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=8,
                blur_radius=34,
                color="#48FE8F40",  # Halo ambre fort
                offset=ft.Offset(0, 0),
            )
            self.wave_bar1.height = 16
            self.wave_bar2.height = 28
            self.wave_bar3.height = 40
            self.wave_bar4.height = 28
            self.wave_bar5.height = 16
            self._safe_update(self.logo_box)

            # Phase 4 : Titre "AIC" (t=1000ms)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            # Phase 4b : Atténuation douce du halo (t=1150ms)
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=3,
                blur_radius=18,
                color="#20FE8F40",  # Halo ambre atténué
                offset=ft.Offset(0, 0),
            )
            self._safe_update(self.logo_box)

            # Phase 5 : Sous-titre Ambre (t=1350ms)
            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            # Phase 6 : Maintien & fondu de sortie (t=1900ms → t=2300ms)
            await asyncio.sleep(0.60)
            logger.info("SPLASH V3.1: ANIMATION COMPLETE")
            self.opacity = 0.0
            self._safe_update(self)

            await asyncio.sleep(0.40)

        except asyncio.CancelledError:
            logger.info("SPLASH V3.1: ANIMATION CANCELLED")
        except Exception as e:
            logger.error(f"SPLASH V3.1: ANIMATION ERROR: {e}", exc_info=True)
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                try:
                    self.on_complete_callback()
                except Exception as cb_err:
                    logger.error(f"SPLASH V3.1: CALLBACK ERROR: {cb_err}", exc_info=True)

    def _safe_update(self, control: ft.Control) -> None:
        try:
            if control and self.page and control.page:
                control.update()
        except Exception:
            pass
