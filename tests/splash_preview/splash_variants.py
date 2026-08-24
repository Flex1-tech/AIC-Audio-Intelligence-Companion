"""
tests/splash_preview/splash_variants.py
----------------------------------------
Laboratoire de comparaison des variantes du Splash Screen AIC.

Variantes :
  - SplashProduction   (Production réelle `ui.components.splash_screen.SplashScreen`)
  - SplashV3Current    (Variante A : Baseline compacte 110x110 px, 2.3s)
  - SplashV3Immersive  (Variante B : Carte adaptative 130-165 px, equalizer max 45px, 2.3s)
  - SplashV3Fullscreen (Variante C : Fullscreen maîtrisée sans carte, 2.8s)
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft

from ui.components.splash_screen import SplashScreen
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path

logger = logging.getLogger("splash_preview")


def _resolve_icon() -> Optional[str]:
    p = get_asset_path("icon.svg") or get_asset_path("icon.png")
    return str(p) if p and p.exists() else None


def _make_logo_image(icon_src: Optional[str], size: int = 64) -> ft.Control:
    if icon_src:
        return ft.Image(src=icon_src, width=size, height=size, fit=ft.BoxFit.CONTAIN)
    return ft.Icon(ft.Icons.GRAPHIC_EQ, size=int(size * 0.75), color=ObsidianColors.PRIMARY)


def _safe_update(control: ft.Control) -> None:
    try:
        if control and control.page:
            control.update()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE PRODUCTION : Wrapper direct du composant réel
# ══════════════════════════════════════════════════════════════════════════════


class SplashProduction(SplashScreen):
    """Production réelle (ui/components/splash_screen.py)."""

    LABEL = "Production (V3 Réalisée)"


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE A : SplashV3Current (Baseline compacte 110x110)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV3Current(ft.Container):
    """Variante A — Baseline compacte 110x110 px, 2.3s."""

    LABEL = "Variante A — Baseline V3 (110px)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)

        self.bar1 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)
        self.bar2 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
        self.bar3 = ft.Container(width=3, height=22, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.bar4 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
        self.bar5 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)

        self.wave_container = ft.Row(
            [self.bar1, self.bar2, self.bar3, self.bar4, self.bar5],
            spacing=3,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.logo_box = ft.Container(
            content=ft.Stack(
                [logo_content, ft.Container(content=self.wave_container, alignment=ft.Alignment(0, 0.55))],
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
        )
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion", size=13, weight=ft.FontWeight.W_500, color=ObsidianColors.PRIMARY
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=16), self.title_box, ft.Container(height=4), self.subtitle_box],
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
        cb_called = False
        try:
            await asyncio.sleep(0.05)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(1.0)
            self.logo_box.offset = ft.Offset(0, 0)
            _safe_update(self.logo_box)
            await asyncio.sleep(0.35)
            self.wave_container.opacity = 1.0
            _safe_update(self.wave_container)
            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=6, blur_radius=28, color="#40FE8F40")
            self.bar1.height = 14
            self.bar2.height = 24
            self.bar3.height = 32
            self.bar4.height = 24
            self.bar5.height = 14
            _safe_update(self.logo_box)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(0, 0)
            _safe_update(self.title_box)
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=2, blur_radius=14, color="#1AFE8F40")
            _safe_update(self.logo_box)
            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(0, 0)
            _safe_update(self.subtitle_box)
            await asyncio.sleep(0.60)
            self.opacity = 0.0
            _safe_update(self)
            await asyncio.sleep(0.40)
        except Exception:
            pass
        finally:
            if self.on_complete_callback and not cb_called:
                cb_called = True
                self.on_complete_callback()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE B : SplashV3Immersive (Carte adaptative 130-165px, amplitude 45px, 2.3s)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV3Immersive(ft.Container):
    """Variante B — V3 Immersive (carte adaptative 130-165px, amplitude 45px, 2.3s)."""

    LABEL = "Variante B — V3 Immersive (140px adaptatif)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete

        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        card_size = int(max(130, min(165, min(w, h) * 0.22)))
        icon_size = int(card_size * 0.58)

        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, icon_size)

        self.bar1 = ft.Container(width=4, height=12, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)
        self.bar2 = ft.Container(width=4, height=20, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar3 = ft.Container(width=4, height=30, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.bar4 = ft.Container(width=4, height=20, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar5 = ft.Container(width=4, height=12, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)

        self.wave_container = ft.Row(
            [self.bar1, self.bar2, self.bar3, self.bar4, self.bar5],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.logo_box = ft.Container(
            content=ft.Stack(
                [logo_content, ft.Container(content=self.wave_container, alignment=ft.Alignment(0, 0.58))],
                alignment=ft.Alignment.CENTER,
            ),
            width=card_size,
            height=card_size,
            border_radius=Radii.LG,
            bgcolor=ObsidianColors.SURFACE_DARK,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.92),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.04),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.bg_glow = ft.Container(
            width=min(460, w),
            height=min(460, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=["rgba(254, 143, 64, 0.12)", "rgba(48, 196, 239, 0.05)", "rgba(15, 17, 23, 0.0)"],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        title_size = int(card_size * 0.30)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=title_size, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion", size=14, weight=ft.FontWeight.W_500, color=ObsidianColors.PRIMARY
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(content=self.bg_glow, alignment=ft.Alignment.CENTER, expand=True),
                    ft.Column(
                        [
                            self.logo_box,
                            ft.Container(height=18),
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

    async def start_animation_async(self) -> None:
        cb_called = False
        try:
            await asyncio.sleep(0.05)
            self.bg_glow.opacity = 1.0
            _safe_update(self.bg_glow)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(1.0)
            self.logo_box.offset = ft.Offset(0, 0)
            _safe_update(self.logo_box)
            await asyncio.sleep(0.35)
            self.wave_container.opacity = 1.0
            _safe_update(self.wave_container)
            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=8, blur_radius=34, color="#48FE8F40")
            self.bar1.height = 18
            self.bar2.height = 30
            self.bar3.height = 45
            self.bar4.height = 30
            self.bar5.height = 18
            _safe_update(self.logo_box)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(0, 0)
            _safe_update(self.title_box)
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=3, blur_radius=18, color="#20FE8F40")
            _safe_update(self.logo_box)
            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(0, 0)
            _safe_update(self.subtitle_box)
            await asyncio.sleep(0.60)
            self.opacity = 0.0
            _safe_update(self)
            await asyncio.sleep(0.40)
        except Exception:
            pass
        finally:
            if self.on_complete_callback and not cb_called:
                cb_called = True
                self.on_complete_callback()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE C : SplashV3Fullscreen (Fullscreen maîtrisée sans carte, 2.8s)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV3Fullscreen(ft.Container):
    """Variante C — V3 Fullscreen maîtrisée (logo adaptatif 170-240px, 2.8s)."""

    LABEL = "Variante C — V3 Fullscreen (200px open)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete

        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        logo_size = int(max(170, min(240, min(w, h) * 0.30)))

        icon_src = _resolve_icon()
        logo_image = _make_logo_image(icon_src, logo_size)

        self.bar1 = ft.Container(width=5, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.4)
        self.bar2 = ft.Container(width=5, height=24, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.7)
        self.bar3 = ft.Container(width=5, height=36, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.9)
        self.bar4 = ft.Container(width=5, height=52, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=1.0)
        self.bar5 = ft.Container(width=5, height=36, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.9)
        self.bar6 = ft.Container(width=5, height=24, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.7)
        self.bar7 = ft.Container(width=5, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=3, opacity=0.4)

        self.wave_container = ft.Row(
            [self.bar1, self.bar2, self.bar3, self.bar4, self.bar5, self.bar6, self.bar7],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_halo = ft.Container(
            content=logo_image,
            width=logo_size,
            height=logo_size,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.90),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.03),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        self.bg_glow = ft.Container(
            width=min(600, w),
            height=min(600, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=["rgba(254, 143, 64, 0.16)", "rgba(48, 196, 239, 0.06)", "rgba(15, 17, 23, 0.0)"],
                stops=[0.0, 0.45, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(700, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        title_size = int(max(44, logo_size * 0.25))
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=title_size, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        subtitle_size = int(max(13, logo_size * 0.075))
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "AUDIO INTELLIGENCE COMPANION",
                size=subtitle_size,
                weight=ft.FontWeight.W_500,
                color=ObsidianColors.PRIMARY,
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        gap = int(logo_size * 0.10)
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(content=self.bg_glow, alignment=ft.Alignment.CENTER, expand=True),
                    ft.Column(
                        [
                            self.logo_halo,
                            ft.Container(height=gap),
                            self.wave_container,
                            ft.Container(height=gap),
                            self.title_box,
                            ft.Container(height=6),
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
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        cb_called = False
        try:
            await asyncio.sleep(0.08)
            self.bg_glow.opacity = 1.0
            _safe_update(self.bg_glow)
            self.logo_halo.opacity = 1.0
            self.logo_halo.scale = ft.Scale(1.0)
            self.logo_halo.offset = ft.Offset(0, 0)
            _safe_update(self.logo_halo)

            await asyncio.sleep(0.40)
            self.wave_container.opacity = 1.0
            _safe_update(self.wave_container)

            await asyncio.sleep(0.35)
            self.bar1.height = 20
            self.bar2.height = 36
            self.bar3.height = 54
            self.bar4.height = 68
            self.bar5.height = 54
            self.bar6.height = 36
            self.bar7.height = 20
            _safe_update(self.wave_container)

            await asyncio.sleep(0.30)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(0, 0)
            _safe_update(self.title_box)

            await asyncio.sleep(0.25)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(0, 0)
            _safe_update(self.subtitle_box)

            await asyncio.sleep(0.70)
            self.opacity = 0.0
            _safe_update(self)
            await asyncio.sleep(0.45)
        except Exception:
            pass
        finally:
            if self.on_complete_callback and not cb_called:
                cb_called = True
                self.on_complete_callback()


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRE des variantes pour le laboratoire de preview
# ══════════════════════════════════════════════════════════════════════════════

VARIANTS = {
    "production": SplashProduction,
    "v3current": SplashV3Current,
    "v3immersive": SplashV3Immersive,
    "v3fullscreen": SplashV3Fullscreen,
}

VARIANT_ORDER = ["production", "v3current", "v3immersive", "v3fullscreen"]

VARIANT_LABELS = {
    "production": "Production (V3.2 Clean & Paramétré)",
    "v3current": "A — Baseline V3 (110px)",
    "v3immersive": "B — V3 Immersive (140px)",
    "v3fullscreen": "C — V3 Fullscreen (200px open)",
}
