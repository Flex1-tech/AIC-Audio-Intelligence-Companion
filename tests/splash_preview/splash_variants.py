"""
tests/splash_preview/splash_variants.py
----------------------------------------
Laboratoire de comparaison et de validation du Splash Screen AIC.

SOURCE DE VERITE : origin/main (SHA af092ec63b397a3edf43165e49627c4d6b282fa9)

Variantes disponibles :
1. SplashOriginMain : Référence origin/main (Scanner ambre).
2. SplashProductionLocal : Proxy vers la production actuelle ui/components/splash_screen.py.
"""

import asyncio
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from utils.path_utils import get_asset_path

# ── Configuration de l'animation (identique a origin/main) ─────────────────
SPLASH_ANIMATION_CONFIG = {
    "total_ms": 5000,
    "logo_intro": (0.00, 0.25),  # 0%  -> 25% : Apparition structure A logo & fond
    "wave_dim": (0.15, 0.35),  # 15% -> 35% : Signal onde dormant (opacite 0.22)
    "wave_sweep": (0.28, 0.60),  # 28% -> 60% : Balayage du faisceau ambre L->R
    "wave_alive": (0.32, 0.65),  # 32% -> 65% : Eveil complet de l'onde (opacite 1.0)
    "halo_pulse": (0.55, 0.70),  # 55% -> 70% : Impulsion halo ambre BoxShadow
    "title_intro": (0.58, 0.78),  # 58% -> 78% : Apparition du titre "AIC"
    "subtitle_intro": (0.68, 0.88),  # 68% -> 88% : Apparition du sous-titre
    "fade_out": (0.88, 1.00),  # 88% -> 100% : Fondu vers l'UI principale
}

# ── Constantes de position de l'onde dans le SVG (viewBox 1024x1024) ────────
_WAVE_SVG_X_MIN = 378.0
_WAVE_SVG_X_MAX = 652.0
_WAVE_SVG_Y_MIN = 558.0
_WAVE_SVG_Y_MAX = 628.0
_SVG_SIZE = 1024.0


def _wave_rect(logo_size: int) -> tuple:
    """Retourne (left, top, width, height) de la zone onde en pixels ecran."""
    scale = logo_size / _SVG_SIZE
    left = _WAVE_SVG_X_MIN * scale
    top = _WAVE_SVG_Y_MIN * scale
    w = (_WAVE_SVG_X_MAX - _WAVE_SVG_X_MIN) * scale
    h = (_WAVE_SVG_Y_MAX - _WAVE_SVG_Y_MIN) * scale
    return left, top, w, h


def _resolve_web(filename: str) -> str:
    p = get_asset_path(filename)
    if p and p.exists():
        return filename
    return filename


def _dur(pct_range: tuple, total_ms: int) -> int:
    return int((pct_range[1] - pct_range[0]) * total_ms)


def _safe_update(control: ft.Control) -> None:
    try:
        if control and control.page:
            control.update()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE 1 : SplashOriginMain (Scanner Ambre Original)
# ══════════════════════════════════════════════════════════════════════════════


class SplashOriginMain(ft.Container):
    """
    Reproduction fidele de origin/main:ui/components/splash_screen.py.
    """

    LABEL = "★ Reference origin/main (Scanner Ambre)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        cfg = SPLASH_ANIMATION_CONFIG
        self.total_ms = cfg["total_ms"]

        def _d(k):
            return _dur(cfg[k], self.total_ms)

        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        self.logo_size = int(max(300, min(560, min(w, h) * 0.65)))
        S = self.logo_size

        lf_src = _resolve_web("layer_letterform.svg")
        wv_src = _resolve_web("layer_wave.svg")
        icon_src = _resolve_web("icon.svg")

        self.letterform_img = ft.Image(
            src=lf_src if lf_src else icon_src,
            width=S,
            height=S,
            fit=ft.BoxFit.CONTAIN,
        )

        self.wave_img = ft.Image(
            src=wv_src if wv_src else "",
            width=S,
            height=S,
            fit=ft.BoxFit.CONTAIN,
            opacity=0.0,
            animate_opacity=ft.Animation(_d("wave_alive"), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        wave_left, wave_top, wave_w, wave_h = _wave_rect(S)
        beam_w = int(wave_w * 0.32)
        beam_h = int(wave_h * 2.6)
        beam_top = wave_top - (beam_h - wave_h) / 2

        self._scan_left_start = wave_left - beam_w * 0.2
        self._scan_left_end = wave_left + wave_w - beam_w * 0.8

        self.wave_glow = ft.Container(
            width=beam_w,
            height=beam_h,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["transparent", "#BFF59E0B", "transparent"],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.0,
            left=self._scan_left_start,
            top=beam_top,
            animate_opacity=ft.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.Animation(_d("wave_sweep"), ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_stack = ft.Stack(
            [self.letterform_img, self.wave_img, self.wave_glow],
            width=S,
            height=S,
        )

        self.logo_container = ft.Container(
            content=self.logo_stack,
            width=S,
            height=S,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.88),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.03),
            animate_opacity=ft.Animation(_d("logo_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(_d("logo_intro") + 100, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_d("logo_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        title_size = max(36, int(S * 0.095))
        self.title_box = ft.Container(
            content=ft.Text(
                "AIC",
                size=title_size,
                color=ObsidianColors.TEXT_PRIMARY,
                font_family="Cinzel Decorative Bold",
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.12),
            animate_opacity=ft.Animation(_d("title_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_d("title_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        subtitle_size = max(11, int(S * 0.030))
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion",
                size=subtitle_size,
                color=ObsidianColors.TEXT_MUTED,
                font_family="Cinzel Decorative Regular",
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(_d("subtitle_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_d("subtitle_intro"), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        self.bg_glow = ft.Container(
            width=min(S * 1.6, w),
            height=min(S * 1.6, h),
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.5,
                colors=["#10F59E0B", "transparent"],
                stops=[0.0, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(_d("logo_intro") + 300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        gap_logo_text = max(12, int(S * 0.035))

        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(content=self.bg_glow, alignment=ft.Alignment.CENTER, expand=True),
                    ft.Column(
                        [
                            self.logo_container,
                            ft.Container(height=gap_logo_text),
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
            animate_opacity=ft.Animation(_d("fade_out"), ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        cfg = SPLASH_ANIMATION_CONFIG
        t_current = 0.0

        def _sec_at(pct: float) -> float:
            return (pct * self.total_ms) / 1000.0

        async def _wait_until(target_pct: float) -> None:
            nonlocal t_current
            if target_pct > t_current:
                await asyncio.sleep(_sec_at(target_pct) - _sec_at(t_current))
                t_current = target_pct

        try:
            await _wait_until(cfg["logo_intro"][0])
            self.bg_glow.opacity = 1.0
            self.logo_container.opacity = 1.0
            self.logo_container.scale = ft.Scale(scale=1.0)
            self.logo_container.offset = ft.Offset(x=0, y=0)
            _safe_update(self.bg_glow)
            _safe_update(self.logo_container)

            await _wait_until(cfg["wave_dim"][0])
            self.wave_img.opacity = 0.22
            _safe_update(self.wave_img)

            await _wait_until(cfg["wave_sweep"][0])
            self.wave_glow.opacity = 0.90
            self.wave_glow.left = self._scan_left_start
            _safe_update(self.wave_glow)

            await asyncio.sleep(0.03)
            self.wave_glow.left = self._scan_left_end
            _safe_update(self.wave_glow)

            await _wait_until(cfg["wave_alive"][0])
            self.wave_img.opacity = 1.0
            _safe_update(self.wave_img)

            await _wait_until(cfg["halo_pulse"][0])
            self.logo_container.shadow = ft.BoxShadow(
                spread_radius=8,
                blur_radius=40,
                color="#38F59E0B",
                offset=ft.Offset(x=0, y=0),
            )
            _safe_update(self.logo_container)

            await _wait_until(cfg["wave_sweep"][1])
            self.wave_glow.opacity = 0.0
            _safe_update(self.wave_glow)

            await _wait_until(cfg["halo_pulse"][1])
            self.logo_container.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=16,
                color="#14F59E0B",
                offset=ft.Offset(x=0, y=0),
            )
            _safe_update(self.logo_container)

            await _wait_until(cfg["title_intro"][0])
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.title_box)

            await _wait_until(cfg["subtitle_intro"][0])
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.subtitle_box)

            await _wait_until(cfg["fade_out"][0])
            self.opacity = 0.0
            _safe_update(self)

            await _wait_until(cfg["fade_out"][1])
            await asyncio.sleep(0.05)

        except Exception:
            pass
        finally:
            if self.on_complete_callback:
                self.on_complete_callback()


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE 2 : Production locale (ui/components/splash_screen.SplashScreen)
# ══════════════════════════════════════════════════════════════════════════════


class SplashProductionLocal(ft.Container):
    """
    Proxy vers la production locale ui/components/splash_screen.SplashScreen.
    """

    LABEL = "Production locale (branch dev, HEAD)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        from ui.components.splash_screen import SplashScreen

        self._inner = SplashScreen(page=page, on_complete=on_complete)
        super().__init__(
            content=self._inner,
            expand=True,
            bgcolor=ObsidianColors.BG_DARK,
        )

    async def start_animation_async(self) -> None:
        await self._inner.start_animation_async()


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRE DES VARIANTES
# ══════════════════════════════════════════════════════════════════════════════

VARIANTS = {
    "origin_main": SplashOriginMain,
    "production": SplashProductionLocal,
}

VARIANT_ORDER = ["origin_main", "production"]

VARIANT_LABELS = {
    "origin_main": SplashOriginMain.LABEL,
    "production": SplashProductionLocal.LABEL,
}

SPLASH_ANIMATION_DURATION_MS = SPLASH_ANIMATION_CONFIG["total_ms"]


def calculate_target_responsive_dimensions(viewport_w: float, viewport_h: float) -> dict:
    vw = max(320.0, float(viewport_w or 900.0))
    vh = max(320.0, float(viewport_h or 700.0))
    min_dim = min(vw, vh)
    logo_size = int(max(300, min(560, min_dim * 0.65)))
    title_size = max(36, int(logo_size * 0.095))
    subtitle_size = max(11, int(logo_size * 0.030))
    gap_logo_text = max(12, int(logo_size * 0.035))
    bg_glow_size = int(min(logo_size * 1.6, min_dim))
    return {
        "logo_size": logo_size,
        "title_size": title_size,
        "subtitle_size": subtitle_size,
        "gap_logo_text": gap_logo_text,
        "bg_glow_size": bg_glow_size,
    }


SplashV3Target = SplashOriginMain
