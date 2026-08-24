"""
ui/components/splash_screen.py
-------------------------------
Splash Screen AIC V3 — Version Finale Équilibrée.

Fondation : OLD v1 (commit 73707ef)
- Composition compacte : carte Obsidian 110×110 px centrée.
- Logo icon.svg (64×64) dans la carte, fallback ft.Icons.GRAPHIC_EQ.
- Égaliseur audio 5 barres dynamiques (#FE8F40 Ambre).
- Halo BoxShadow Ambre pulsant (spread=6, blur=28 → spread=2, blur=14).
- Titre "AIC" 38pt bold blanc — typographie système (lisibilité maximale).
- Rythme strict ~2.3 secondes.
- Fallback GRAPHIC_EQ si icon.svg / icon.png absents.

Éléments NEW v2 intégrés (validés par comparaison visuelle) :
1. Sous-titre "Audio Intelligence Companion" en Cyan Électrique (#30C4EF)
   → Rétablit l'équilibre de marque Cyan (IA) + Ambre (Audio).
2. Glow ambiant radial Cyan/Ambre en fond (bg_glow)
   → Offre une atmosphère subtile derrière la carte sans altérer le halo pulsant.
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
    Splash Screen AIC V3.
    Fondation OLD v1 (carte 110×110, halo pulsant, 2.3s)
    + Sous-titre Cyan #30C4EF + Radial glow ambiant subtil.
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        logger.info("SPLASH: INIT")
        self.on_complete_callback = on_complete

        # Dimensions écran pour le glow ambiant
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

        # ── 2. Barres égaliseur audio (#FE8F40 Ambre) ─────────────────────────
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

        # ── 3. Carte logo avec halo Ambre réactif (110×110) ───────────────────
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

        # ── 4. Glow ambiant de fond (Cyan 12% + Ambre 8%) — Élément NEW ───────
        self.bg_glow = ft.Container(
            width=min(420, w),
            height=min(420, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=[
                    "rgba(48, 196, 239, 0.12)",  # Cyan IA
                    "rgba(254, 143, 64, 0.08)",  # Ambre Audio
                    "rgba(15, 17, 23, 0.0)",
                ],
                stops=[0.0, 0.45, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 5. Ligne séparatrice ──────────────────────────────────────────────
        self.wave_reveal_line = ft.Container(
            width=0,
            height=2,
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=1,
            opacity=0.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 6. Titre "AIC" (Système Bold — Lisibilité) ────────────────────────
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

        # ── 7. Sous-titre (Cyan Électrique #30C4EF — Élément NEW) ─────────────
        self.subtitle_text = ft.Text(
            "Audio Intelligence Companion",
            size=13,
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.ACCENT_CYAN,  # Cyan brand color
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
        logger.info("SPLASH: BUILD")

    async def start_animation_async(self) -> None:
        """
        Séquence d'animation asynchrone V3 finale (2.3s total).
        OLD v1 baseline + éveil simultané du glow ambiant.
        """
        logger.info("SPLASH: ANIMATION START")
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

            # Phase 3 : Impulsion Halo Ambre & expansion barres (t=700ms)
            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=6,
                blur_radius=28,
                color="#40FE8F40",  # Halo ambre fort
                offset=ft.Offset(0, 0),
            )
            self.wave_bar1.height = 14
            self.wave_bar2.height = 24
            self.wave_bar3.height = 32
            self.wave_bar4.height = 24
            self.wave_bar5.height = 14
            self._safe_update(self.logo_box)

            # Phase 4 : Titre "AIC" (t=1000ms)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            # Phase 4b : Atténuation douce du halo (t=1150ms)
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=14,
                color="#1AFE8F40",  # Halo ambre atténué
                offset=ft.Offset(0, 0),
            )
            self._safe_update(self.logo_box)

            # Phase 5 : Sous-titre Cyan (t=1350ms)
            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            # Phase 6 : Maintien & fondu de sortie (t=1900ms → t=2300ms)
            await asyncio.sleep(0.60)
            logger.info("SPLASH: ANIMATION COMPLETE")
            self.opacity = 0.0
            self._safe_update(self)

            await asyncio.sleep(0.40)

        except asyncio.CancelledError:
            logger.info("SPLASH: ANIMATION CANCELLED")
        except Exception as e:
            logger.error(f"SPLASH: ANIMATION ERROR: {e}", exc_info=True)
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                try:
                    self.on_complete_callback()
                except Exception as cb_err:
                    logger.error(f"SPLASH: CALLBACK ERROR: {cb_err}", exc_info=True)

    def _safe_update(self, control: ft.Control) -> None:
        try:
            if control and self.page and control.page:
                control.update()
        except Exception:
            pass
