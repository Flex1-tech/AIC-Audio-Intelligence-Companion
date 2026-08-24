"""
ui/components/splash_screen.py
-------------------------------
Splash Screen AIC V3.2 — Version Immersive Adaptative.

Architecture :
- Fondation : OLD v1 / V3 (Composition maîtrisée avec carte Obsidian & Halo Ambre pulsant).
- Format adaptatif responsive :
    card_size = clamp(130, min(window_width, window_height) * 0.22, 160) px
- Identité couleur audio : 100% Ambre (#FE8F40 / ObsidianColors.PRIMARY).
  * Equalizer = Ambre #FE8F40 (5 barres, hauteur max 45px)
  * Halo BoxShadow = Ambre #FE8F40 (spread=9, blur=38 → spread=3, blur=20)
  * Sous-titre = Ambre #FE8F40
- Fond ambiant radial Ambre doux (#FE8F40 à 12% opacité) en arrière-plan.
- Typographie : Système Bold adaptatif (lisibilité maximale instantanée).
- Rythme strict ~2.5 secondes.
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
    Splash Screen AIC V3.2 Immersif.
    Carte Obsidian adaptative (130-160px), halo Ambre pulsant,
    égaliseur 45px et sous-titre Ambre #FE8F40 (2.5s).
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        logger.info("SPLASH V3.2: INIT")
        self.on_complete_callback = on_complete

        # ── Dimensions adaptatives responsive ──────────────────────────────────
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        self.card_size = int(max(130, min(160, min(w, h) * 0.22)))
        S = self.card_size
        icon_size = int(S * 0.58)

        # ── 1. Résolution du logo (icon.svg → icon.png → fallback icône) ─────
        svg_path = get_asset_path("icon.svg") or get_asset_path("icon.png")
        icon_src = str(svg_path) if svg_path and svg_path.exists() else None

        if icon_src:
            logo_content = ft.Image(
                src=icon_src,
                width=icon_size,
                height=icon_size,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            logo_content = ft.Icon(
                ft.Icons.GRAPHIC_EQ,
                size=int(icon_size * 0.75),
                color=ObsidianColors.PRIMARY,
            )

        # ── 2. Barres égaliseur audio (#FE8F40 Ambre — Amplitude 45px) ────────
        self.wave_bar1 = ft.Container(width=4, height=12, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)
        self.wave_bar2 = ft.Container(width=4, height=20, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.wave_bar3 = ft.Container(width=4, height=30, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.wave_bar4 = ft.Container(width=4, height=20, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.wave_bar5 = ft.Container(width=4, height=12, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)

        self.wave_container = ft.Row(
            [
                self.wave_bar1,
                self.wave_bar2,
                self.wave_bar3,
                self.wave_bar4,
                self.wave_bar5,
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 3. Carte logo avec halo Ambre réactif ─────────────────────────────
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
            width=S,
            height=S,
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

        # ── 4. Glow ambiant de fond (Ambre 12% opacité) ───────────────────────
        self.bg_glow = ft.Container(
            width=min(480, w),
            height=min(480, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=[
                    "rgba(254, 143, 64, 0.12)",  # Ambre Audio
                    "rgba(48, 196, 239, 0.05)",  # Cyan IA subtil
                    "rgba(15, 17, 23, 0.0)",
                ],
                stops=[0.0, 0.5, 1.0],
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

        # ── 6. Titre "AIC" (Système Bold — Blanc #F9FAFB adaptatif) ────────────
        title_size = int(S * 0.30)
        self.title_text = ft.Text(
            "AIC",
            size=title_size,
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
            size=14,
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
                            ft.Container(height=18),
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
        logger.info("SPLASH V3.2: BUILD")

    async def start_animation_async(self) -> None:
        """
        Séquence d'animation asynchrone V3.2 Immersive (~2.5s total).
        Carte Obsidian 130-160px adaptative + Égaliseur max 45px + Halo ambre vif.
        """
        logger.info("SPLASH V3.2: ANIMATION START")
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

            # Phase 2 : Éveil de l'onde sonore (t=430ms)
            await asyncio.sleep(0.38)
            self.wave_container.opacity = 1.0
            self._safe_update(self.wave_container)

            # Phase 3 : Impulsion Halo Ambre vif & expansion barres max 45px (t=750ms)
            await asyncio.sleep(0.32)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=9,
                blur_radius=38,
                color="#48FE8F40",  # Halo ambre fort
                offset=ft.Offset(0, 0),
            )
            self.wave_bar1.height = 18
            self.wave_bar2.height = 30
            self.wave_bar3.height = 45
            self.wave_bar4.height = 30
            self.wave_bar5.height = 18
            self._safe_update(self.logo_box)

            # Phase 4 : Titre "AIC" (t=1030ms)
            await asyncio.sleep(0.28)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            # Phase 4b : Atténuation douce du halo (t=1210ms)
            await asyncio.sleep(0.18)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=3,
                blur_radius=20,
                color="#20FE8F40",  # Halo ambre atténué
                offset=ft.Offset(0, 0),
            )
            self._safe_update(self.logo_box)

            # Phase 5 : Sous-titre Ambre (t=1430ms)
            await asyncio.sleep(0.22)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            # Phase 6 : Maintien & fondu de sortie (t=2080ms → t=2500ms)
            await asyncio.sleep(0.65)
            logger.info("SPLASH V3.2: ANIMATION COMPLETE")
            self.opacity = 0.0
            self._safe_update(self)

            await asyncio.sleep(0.40)

        except asyncio.CancelledError:
            logger.info("SPLASH V3.2: ANIMATION CANCELLED")
        except Exception as e:
            logger.error(f"SPLASH V3.2: ANIMATION ERROR: {e}", exc_info=True)
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                try:
                    self.on_complete_callback()
                except Exception as cb_err:
                    logger.error(f"SPLASH V3.2: CALLBACK ERROR: {cb_err}", exc_info=True)

    def _safe_update(self, control: ft.Control) -> None:
        try:
            if control and self.page and control.page:
                control.update()
        except Exception:
            pass
