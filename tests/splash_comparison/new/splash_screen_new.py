"""
tests/splash_comparison/new/splash_screen_new.py
--------------------------------------------------
Nouvelle version du Splash Screen AIC (v2 SVG Multi-couches + Faisceau Scanner + Cinzel Decorative).
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft
from ui.design_system.colors import ObsidianColors
from utils.path_utils import get_asset_path

logger = logging.getLogger("splash_new")

SPLASH_ANIMATION_CONFIG = {
    "total_ms": 5000,
    "logo_intro": (0.00, 0.25),
    "wave_dim": (0.15, 0.35),
    "wave_sweep": (0.28, 0.60),
    "wave_alive": (0.32, 0.65),
    "halo_pulse": (0.55, 0.70),
    "title_intro": (0.58, 0.78),
    "subtitle_intro": (0.68, 0.88),
    "fade_out": (0.88, 1.00),
}

_WAVE_SVG_X_MIN = 277.0
_WAVE_SVG_X_MAX = 757.3
_WAVE_SVG_Y_MIN = 590.5
_WAVE_SVG_Y_MAX = 704.5
_SVG_SIZE = 1024.0


def _wave_rect(logo_size: int) -> tuple:
    scale = logo_size / _SVG_SIZE
    left = _WAVE_SVG_X_MIN * scale
    top = _WAVE_SVG_Y_MIN * scale
    w = (_WAVE_SVG_X_MAX - _WAVE_SVG_X_MIN) * scale
    h = (_WAVE_SVG_Y_MAX - _WAVE_SVG_Y_MIN) * scale
    return left, top, w, h


class SplashScreenNEW(ft.Container):
    """
    Implémentation de la NOUVELLE version du Splash Screen (v2).
    - SVG multi-couches (layer_letterform.svg + layer_wave.svg)
    - Faisceau balayage ambre (Wave Sweep Scanner)
    - Dégradé ambiant radial Cyan/Ambre (#30C4EF / #FE8F40)
    - Typographie Cinzel Decorative Bold/Regular
    - Timing adaptatif 5s
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.on_complete_callback = on_complete
        self.total_ms = SPLASH_ANIMATION_CONFIG["total_ms"]

        def _dur(pct_range: tuple) -> int:
            return int((pct_range[1] - pct_range[0]) * self.total_ms)

        cfg = SPLASH_ANIMATION_CONFIG

        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        self.logo_size = int(max(300, min(560, min(w, h) * 0.65)))
        S = self.logo_size

        def _svg_asset_name(filename: str) -> Optional[str]:
            p = get_asset_path(filename)
            if p and p.exists():
                return filename
            return None

        lf_src = _svg_asset_name("layer_letterform.svg")
        wv_src = _svg_asset_name("layer_wave.svg")
        icon_src = _svg_asset_name("icon.svg") or _svg_asset_name("icon.png")

        if lf_src:
            self.letterform_img = ft.Image(
                src=lf_src,
                width=S,
                height=S,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            self.letterform_img = ft.Image(
                src=icon_src or "icon.png",
                width=S,
                height=S,
                fit=ft.BoxFit.CONTAIN,
            )

        if wv_src:
            self.wave_img = ft.Image(
                src=wv_src,
                width=S,
                height=S,
                fit=ft.BoxFit.CONTAIN,
                opacity=0.0,
                animate_opacity=ft.Animation(_dur(cfg["wave_alive"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            )
        else:
            self.wave_img = ft.Container()

        wl, wt, ww, wh = _wave_rect(S)
        beam_w = max(18.0, ww * 0.18)
        beam_h = wh * 1.15
        beam_top = wt - (wh * 0.075)

        self._scan_left_start = wl - beam_w
        self._scan_left_end = wl + ww + (beam_w * 0.5)

        self.wave_glow = ft.Container(
            width=beam_w,
            height=beam_h,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[
                    "transparent",
                    "rgba(254, 143, 64, 0.85)",
                    "transparent",
                ],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.0,
            left=self._scan_left_start,
            top=beam_top,
            animate_opacity=ft.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.Animation(_dur(cfg["wave_sweep"]), ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_stack = ft.Stack(
            [
                self.letterform_img,
                self.wave_img,
                self.wave_glow,
            ],
            width=S,
            height=S,
        )

        self.logo_container = ft.Container(
            content=self.logo_stack,
            width=S,
            height=S,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.TRANSPARENT,
            scale=ft.Scale(scale=0.90),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.02),
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(_dur(cfg["logo_intro"]) + 100, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        title_size = max(40, int(S * 0.10))
        self.title_box = ft.Container(
            content=ft.Text(
                "AIC",
                size=title_size,
                color=ObsidianColors.TEXT_PRIMARY,
                font_family="Cinzel Decorative Bold",
                weight=ft.FontWeight.BOLD,
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        subtitle_size = max(13, int(S * 0.035))
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "AUDIO INTELLIGENCE COMPANION",
                size=subtitle_size,
                color=ObsidianColors.ACCENT_CYAN,
                font_family="Cinzel Decorative Regular",
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.08),
            animate_opacity=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        self.bg_glow = ft.Container(
            width=min(S * 2.2, w),
            height=min(S * 2.2, h),
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=[
                    "rgba(48, 196, 239, 0.25)",
                    "rgba(254, 143, 64, 0.15)",
                    "rgba(15, 17, 23, 0.0)",
                ],
                stops=[0.0, 0.45, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]) + 300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        gap_logo_text = max(16, int(S * 0.040))

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
                            self.logo_container,
                            ft.Container(height=gap_logo_text),
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
            animate_opacity=ft.Animation(_dur(cfg["fade_out"]), ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        """Séquence d'animation asynchrone NEW (5s total)."""
        logger.info("NEW SPLASH: START")
        callback_called = False
        try:
            cfg = SPLASH_ANIMATION_CONFIG
            t_current = 0.0

            def _sec_at(pct: float) -> float:
                return (pct * self.total_ms) / 1000.0

            async def _wait_until(target_pct: float) -> None:
                nonlocal t_current
                if target_pct > t_current:
                    await asyncio.sleep(_sec_at(target_pct) - _sec_at(t_current))
                    t_current = target_pct

            await _wait_until(cfg["logo_intro"][0])
            self.bg_glow.opacity = 1.0
            self.logo_container.opacity = 1.0
            self.logo_container.scale = ft.Scale(scale=1.0)
            self.logo_container.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.bg_glow)
            self._safe_update(self.logo_container)

            await _wait_until(cfg["wave_dim"][0])
            self.wave_img.opacity = 0.60
            self._safe_update(self.wave_img)

            await _wait_until(cfg["wave_sweep"][0])
            self.wave_glow.opacity = 0.90
            self.wave_glow.left = self._scan_left_start
            self._safe_update(self.wave_glow)

            await asyncio.sleep(0.03)
            self.wave_glow.left = self._scan_left_end
            self.wave_img.opacity = 1.0
            self._safe_update(self.wave_glow)
            self._safe_update(self.wave_img)

            await _wait_until(cfg["wave_sweep"][1])
            self.wave_glow.opacity = 0.0
            self._safe_update(self.wave_glow)

            await _wait_until(cfg["title_intro"][0])
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            await _wait_until(cfg["subtitle_intro"][0])
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            await asyncio.sleep(0.40)
            logger.info("NEW SPLASH: ANIMATION COMPLETE")

            await _wait_until(cfg["fade_out"][0])
            self.opacity = 0.0
            self._safe_update(self)

            await _wait_until(cfg["fade_out"][1])
            await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"NEW SPLASH ERROR: {e}")
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
