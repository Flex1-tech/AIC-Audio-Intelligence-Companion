"""
tests/splash_preview/splash_variants.py
----------------------------------------
Variantes Splash Screen pour le Laboratoire V3.1.

Variantes disponibles :
  - SplashV3Current  : V3 actuelle (baseline 110x110, Ambre+Glow)
  - SplashV31A        : V3.1-A (Carte 110x110, amplitude equalizer accrue + halo fort, Ambre pur #FE8F40)
  - SplashV31B        : V3.1-B (Carte 130x130, icône 76px, equalizer 44px, Ambre pur #FE8F40)
  - SplashV31C        : V3.1-C (Carte 150x150, icône 88px, equalizer 50px, Ambre pur #FE8F40)
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft

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
# VARIANTE : SplashV3Current (Baseline V3 — Carte 110x110)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV3Current(ft.Container):
    """V3 actuelle — Baseline carte 110x110, 2.3s."""

    LABEL = "V3 Current (110px)"

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
                "Audio Intelligence Companion", size=13, weight=ft.FontWeight.W_500, color=ObsidianColors.ACCENT_CYAN
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
# VARIANTE : SplashV31A (Carte 110x110, amplitude + halo accrus, Ambre pur #FE8F40)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV31A(ft.Container):
    """V3.1-A : Carte 110x110, barres equalizer plus hautes (10->40px), Ambre pur #FE8F40."""

    LABEL = "V3.1-A (110px + Amplitude)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)

        # Barres 4px de large (vs 3px), hauteur max 40px (vs 32px)
        self.bar1 = ft.Container(width=4, height=10, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)
        self.bar2 = ft.Container(width=4, height=18, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar3 = ft.Container(width=4, height=28, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.bar4 = ft.Container(width=4, height=18, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar5 = ft.Container(width=4, height=10, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)

        self.wave_container = ft.Row(
            [self.bar1, self.bar2, self.bar3, self.bar4, self.bar5],
            spacing=3,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.logo_box = ft.Container(
            content=ft.Stack(
                [logo_content, ft.Container(content=self.wave_container, alignment=ft.Alignment(0, 0.58))],
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
        # Subtitle Ambre chaud #FE8F40 (100% Ambre audio)
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
            # Halo ambre renforcé (spread 8, blur 34)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=8, blur_radius=34, color="#48FE8F40")
            self.bar1.height = 16
            self.bar2.height = 28
            self.bar3.height = 40
            self.bar4.height = 28
            self.bar5.height = 16
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
# VARIANTE : SplashV31B (Carte 130x130, icône 76px, equalizer 44px, Ambre pur #FE8F40)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV31B(ft.Container):
    """V3.1-B : Carte 130x130, icône 76px, equalizer 44px, titre 42pt, Ambre pur #FE8F40."""

    LABEL = "V3.1-B (130px Moderé)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 76)

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
            width=130,
            height=130,
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
            content=ft.Text("AIC", size=42, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
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
            content=ft.Column(
                [self.logo_box, ft.Container(height=18), self.title_box, ft.Container(height=4), self.subtitle_box],
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
            self.logo_box.shadow = ft.BoxShadow(spread_radius=8, blur_radius=36, color="#48FE8F40")
            self.bar1.height = 18
            self.bar2.height = 30
            self.bar3.height = 44
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
# VARIANTE : SplashV31C (Carte 150x150, icône 88px, equalizer 50px, Ambre pur #FE8F40)
# ══════════════════════════════════════════════════════════════════════════════


class SplashV31C(ft.Container):
    """V3.1-C : Carte 150x150, icône 88px, equalizer 50px, titre 46pt, Ambre pur #FE8F40."""

    LABEL = "V3.1-C (150px Grand)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 88)

        self.bar1 = ft.Container(width=5, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)
        self.bar2 = ft.Container(width=5, height=24, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar3 = ft.Container(width=5, height=34, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
        self.bar4 = ft.Container(width=5, height=24, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.8)
        self.bar5 = ft.Container(width=5, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.5)

        self.wave_container = ft.Row(
            [self.bar1, self.bar2, self.bar3, self.bar4, self.bar5],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.logo_box = ft.Container(
            content=ft.Stack(
                [logo_content, ft.Container(content=self.wave_container, alignment=ft.Alignment(0, 0.60))],
                alignment=ft.Alignment.CENTER,
            ),
            width=150,
            height=150,
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
            content=ft.Text("AIC", size=46, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion", size=15, weight=ft.FontWeight.W_500, color=ObsidianColors.PRIMARY
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=20), self.title_box, ft.Container(height=6), self.subtitle_box],
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
            self.logo_box.shadow = ft.BoxShadow(spread_radius=10, blur_radius=42, color="#48FE8F40")
            self.bar1.height = 20
            self.bar2.height = 34
            self.bar3.height = 50
            self.bar4.height = 34
            self.bar5.height = 20
            _safe_update(self.logo_box)
            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(0, 0)
            _safe_update(self.title_box)
            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(spread_radius=4, blur_radius=20, color="#20FE8F40")
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
# REGISTRE des variantes pour le laboratoire V3.1
# ══════════════════════════════════════════════════════════════════════════════

VARIANTS = {
    "v3current": SplashV3Current,
    "v31a": SplashV31A,
    "v31b": SplashV31B,
    "v31c": SplashV31C,
}

VARIANT_ORDER = ["v3current", "v31a", "v31b", "v31c"]

VARIANT_LABELS = {
    "v3current": "V3 Initial (110px)",
    "v31a": "V3.1-A (110px + Amplitude)",
    "v31b": "V3.1-B (130px Moderé)",
    "v31c": "V3.1-C (150px Grand)",
}
