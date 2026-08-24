"""
tests/splash_preview/splash_variants.py
----------------------------------------
Toutes les variantes Splash pour le laboratoire de comparaison V3.

Variantes disponibles :
  - SplashOLD        : OLD v1 exact (copie splash_comparison/old)
  - SplashNEW        : NEW v2 exact (copie splash_comparison/new)
  - SplashV3Base     : V3-base = OLD v1 exact (identique à production actuelle post-réécriture)
  - SplashV3SVG      : V3-base + layer_letterform.svg dans la carte 110x110
  - SplashV3Cinzel   : V3-base + Cinzel Decorative sur "AIC"
  - SplashV3Cyan     : V3-base + sous-titre en ACCENT_CYAN
  - SplashV3Glow     : V3-base + radial glow bg (complément du halo)
  - SplashV3Beam     : V3-base + scan beam ambre (expérimental)

Chaque variante est une classe autonome héritant de ft.Container.
Interface publique uniforme : __init__(page, on_complete) + start_animation_async().
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path

logger = logging.getLogger("splash_preview")

# ── Helpers communs ────────────────────────────────────────────────────────────

def _resolve_icon() -> Optional[str]:
    """Résout icon.svg → icon.png → None."""
    p = get_asset_path("icon.svg") or get_asset_path("icon.png")
    return str(p) if p and p.exists() else None


def _resolve_svg(name: str) -> Optional[str]:
    """Résout un SVG par nom relatif (pour Flet Web + Desktop)."""
    p = get_asset_path(name)
    return name if p and p.exists() else None


def _make_logo_image(icon_src: Optional[str], size: int = 64) -> ft.Control:
    if icon_src:
        return ft.Image(src=icon_src, width=size, height=size, fit=ft.BoxFit.CONTAIN)
    return ft.Icon(ft.Icons.GRAPHIC_EQ, size=int(size * 0.75), color=ObsidianColors.PRIMARY)


def _make_equalizer_bars():
    """5 barres d'égaliseur avec état initial et état animé."""
    bar1 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)
    bar2 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
    bar3 = ft.Container(width=3, height=22, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0)
    bar4 = ft.Container(width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7)
    bar5 = ft.Container(width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4)
    row = ft.Row(
        [bar1, bar2, bar3, bar4, bar5],
        spacing=3,
        alignment=ft.MainAxisAlignment.CENTER,
        opacity=0.0,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )
    return bar1, bar2, bar3, bar4, bar5, row


def _make_logo_box(logo_content, wave_container):
    """Carte 110×110 Obsidian avec logo + égaliseur."""
    return ft.Container(
        content=ft.Stack(
            [logo_content, ft.Container(content=wave_container, alignment=ft.Alignment(0, 0.55))],
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


def _safe_update(control: ft.Control) -> None:
    try:
        if control and control.page:
            control.update()
    except Exception:
        pass


async def _run_old_animation(splash, callback_called_ref):
    """Séquence animation OLD (~2.3s)."""
    try:
        await asyncio.sleep(0.05)
        splash.logo_box.opacity = 1.0
        splash.logo_box.scale = ft.Scale(scale=1.0)
        splash.logo_box.offset = ft.Offset(x=0, y=0)
        _safe_update(splash.logo_box)

        await asyncio.sleep(0.35)
        splash.wave_container.opacity = 1.0
        _safe_update(splash.wave_container)

        await asyncio.sleep(0.30)
        splash.logo_box.shadow = ft.BoxShadow(
            spread_radius=6, blur_radius=28, color="#40FE8F40", offset=ft.Offset(0, 0)
        )
        splash.wave_bar1.height = 14
        splash.wave_bar2.height = 24
        splash.wave_bar3.height = 32
        splash.wave_bar4.height = 24
        splash.wave_bar5.height = 14
        _safe_update(splash.logo_box)

        await asyncio.sleep(0.25)
        splash.title_box.opacity = 1.0
        splash.title_box.offset = ft.Offset(x=0, y=0)
        _safe_update(splash.title_box)

        await asyncio.sleep(0.15)
        splash.logo_box.shadow = ft.BoxShadow(
            spread_radius=2, blur_radius=14, color="#1AFE8F40", offset=ft.Offset(0, 0)
        )
        _safe_update(splash.logo_box)

        await asyncio.sleep(0.20)
        splash.subtitle_box.opacity = 1.0
        splash.subtitle_box.offset = ft.Offset(x=0, y=0)
        _safe_update(splash.subtitle_box)

        await asyncio.sleep(0.60)
        splash.opacity = 0.0
        _safe_update(splash)
        await asyncio.sleep(0.40)

    except (asyncio.CancelledError, Exception) as e:
        logger.debug(f"Animation OLD interrupted: {e}")
    finally:
        if splash.on_complete_callback and not callback_called_ref[0]:
            callback_called_ref[0] = True
            try:
                splash.on_complete_callback()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashOLD  (OLD v1 exact)
# ══════════════════════════════════════════════════════════════════════════════

class SplashOLD(ft.Container):
    """OLD v1 exact — carte 110×110, equalizer ambre, halo pulsant, système, 2.3s."""

    LABEL = "OLD v1"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)
        self.wave_bar1, self.wave_bar2, self.wave_bar3, self.wave_bar4, self.wave_bar5, self.wave_container = _make_equalizer_bars()
        self.logo_box = _make_logo_box(logo_content, self.wave_container)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0, offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text("Audio Intelligence Companion", size=13,
                            weight=ft.FontWeight.W_500, color=ObsidianColors.TEXT_MUTED),
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=16), self.title_box,
                 ft.Container(height=4), self.subtitle_box],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        r = [False]
        await _run_old_animation(self, r)


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashNEW  (NEW v2 exact)
# ══════════════════════════════════════════════════════════════════════════════

class SplashNEW(ft.Container):
    """NEW v2 exact — SVG plein écran 65% viewport, Cinzel Decorative, 5s."""

    LABEL = "NEW v2"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        self.total_ms = 5000

        def _dur(r): return int((r[1] - r[0]) * self.total_ms)

        cfg = {
            "logo_intro": (0.00, 0.25), "wave_dim": (0.15, 0.35),
            "wave_sweep": (0.28, 0.60), "wave_alive": (0.32, 0.65),
            "title_intro": (0.58, 0.78), "subtitle_intro": (0.68, 0.88),
            "fade_out": (0.88, 1.00),
        }
        self._cfg = cfg
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        S = int(max(300, min(560, min(w, h) * 0.65)))
        self.logo_size = S

        lf_src = _resolve_svg("layer_letterform.svg")
        wv_src = _resolve_svg("layer_wave.svg")
        icon_src = _resolve_icon()

        if lf_src:
            self.letterform_img = ft.Image(src=lf_src, width=S, height=S, fit=ft.BoxFit.CONTAIN)
        else:
            self.letterform_img = ft.Image(src=icon_src or "icon.png", width=S, height=S, fit=ft.BoxFit.CONTAIN)

        if wv_src:
            self.wave_img = ft.Image(
                src=wv_src, width=S, height=S, fit=ft.BoxFit.CONTAIN, opacity=0.0,
                animate_opacity=ft.Animation(_dur(cfg["wave_alive"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            )
        else:
            self.wave_img = ft.Container()

        # Scan beam (simplifié pour la preview)
        _WAVE_SVG_X_MIN, _WAVE_SVG_X_MAX = 277.0, 757.3
        _WAVE_SVG_Y_MIN, _WAVE_SVG_Y_MAX = 590.5, 704.5
        scale = S / 1024.0
        wl = _WAVE_SVG_X_MIN * scale
        wt = _WAVE_SVG_Y_MIN * scale
        ww = (_WAVE_SVG_X_MAX - _WAVE_SVG_X_MIN) * scale
        wh = (_WAVE_SVG_Y_MAX - _WAVE_SVG_Y_MIN) * scale
        beam_w = max(18.0, ww * 0.18)
        beam_h = wh * 1.15
        self._scan_left_start = wl - beam_w
        self._scan_left_end = wl + ww + (beam_w * 0.5)
        self.wave_glow = ft.Container(
            width=beam_w, height=beam_h,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=["transparent", "rgba(254, 143, 64, 0.85)", "transparent"],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.0, left=self._scan_left_start, top=wt - (wh * 0.075),
            animate_opacity=ft.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.Animation(_dur(cfg["wave_sweep"]), ft.AnimationCurve.EASE_IN_OUT),
        )

        self.logo_container = ft.Container(
            content=ft.Stack([self.letterform_img, self.wave_img, self.wave_glow], width=S, height=S),
            width=S, height=S, alignment=ft.Alignment.CENTER, bgcolor=ft.Colors.TRANSPARENT,
            scale=ft.Scale(scale=0.90), opacity=0.0, offset=ft.Offset(x=0, y=0.02),
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(_dur(cfg["logo_intro"]) + 100, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        title_size = max(40, int(S * 0.10))
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=title_size, color=ObsidianColors.TEXT_PRIMARY,
                            font_family="Cinzel Decorative Bold", weight=ft.FontWeight.BOLD),
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        subtitle_size = max(13, int(S * 0.035))
        self.subtitle_box = ft.Container(
            content=ft.Text("AUDIO INTELLIGENCE COMPANION", size=subtitle_size,
                            color=ObsidianColors.ACCENT_CYAN, font_family="Cinzel Decorative Regular"),
            opacity=0.0, offset=ft.Offset(x=0, y=0.08),
            animate_opacity=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.bg_glow = ft.Container(
            width=min(S * 2.2, w), height=min(S * 2.2, h), border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0), radius=0.50,
                colors=["rgba(48, 196, 239, 0.25)", "rgba(254, 143, 64, 0.15)", "rgba(15, 17, 23, 0.0)"],
                stops=[0.0, 0.45, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]) + 300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        gap = max(16, int(S * 0.040))
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(content=self.bg_glow, alignment=ft.Alignment.CENTER, expand=True),
                    ft.Column(
                        [self.logo_container, ft.Container(height=gap), self.title_box,
                         ft.Container(height=6), self.subtitle_box],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
                    ),
                ],
                alignment=ft.Alignment.CENTER, expand=True,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(_dur(cfg["fade_out"]), ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        callback_called = False
        cfg = self._cfg
        t_current = 0.0

        def _sec_at(pct): return (pct * self.total_ms) / 1000.0

        async def _wait_until(pct):
            nonlocal t_current
            if pct > t_current:
                await asyncio.sleep(_sec_at(pct) - _sec_at(t_current))
                t_current = pct

        try:
            await _wait_until(cfg["logo_intro"][0])
            self.bg_glow.opacity = 1.0
            self.logo_container.opacity = 1.0
            self.logo_container.scale = ft.Scale(scale=1.0)
            self.logo_container.offset = ft.Offset(x=0, y=0)
            _safe_update(self.bg_glow)
            _safe_update(self.logo_container)

            await _wait_until(cfg["wave_dim"][0])
            self.wave_img.opacity = 0.60
            _safe_update(self.wave_img)

            await _wait_until(cfg["wave_sweep"][0])
            self.wave_glow.opacity = 0.90
            self.wave_glow.left = self._scan_left_start
            _safe_update(self.wave_glow)

            await asyncio.sleep(0.03)
            self.wave_glow.left = self._scan_left_end
            self.wave_img.opacity = 1.0
            _safe_update(self.wave_glow)
            _safe_update(self.wave_img)

            await _wait_until(cfg["wave_sweep"][1])
            self.wave_glow.opacity = 0.0
            _safe_update(self.wave_glow)

            await _wait_until(cfg["title_intro"][0])
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.title_box)

            await _wait_until(cfg["subtitle_intro"][0])
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.subtitle_box)

            await asyncio.sleep(0.40)
            await _wait_until(cfg["fade_out"][0])
            self.opacity = 0.0
            _safe_update(self)
            await _wait_until(cfg["fade_out"][1])
            await asyncio.sleep(0.05)

        except (asyncio.CancelledError, Exception) as e:
            logger.debug(f"NEW animation interrupted: {e}")
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                try:
                    self.on_complete_callback()
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashV3SVG  (OLD + layer_letterform.svg dans carte 110×110)
# ══════════════════════════════════════════════════════════════════════════════

class SplashV3SVG(ft.Container):
    """V3-SVG : OLD v1 avec layer_letterform.svg (80×80) dans carte 110×110."""

    LABEL = "V3 + SVG"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        lf_src = _resolve_svg("layer_letterform.svg")
        icon_src = _resolve_icon()

        # Utilise layer_letterform.svg si disponible, sinon fallback icon.svg
        if lf_src:
            logo_content = ft.Image(src=lf_src, width=80, height=80, fit=ft.BoxFit.CONTAIN)
        else:
            logo_content = _make_logo_image(icon_src, 64)

        self.wave_bar1, self.wave_bar2, self.wave_bar3, self.wave_bar4, self.wave_bar5, self.wave_container = _make_equalizer_bars()
        self.logo_box = _make_logo_box(logo_content, self.wave_container)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0, offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text("Audio Intelligence Companion", size=13,
                            weight=ft.FontWeight.W_500, color=ObsidianColors.TEXT_MUTED),
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=16), self.title_box,
                 ft.Container(height=4), self.subtitle_box],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        r = [False]
        await _run_old_animation(self, r)


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashV3Cinzel  (OLD + Cinzel Decorative sur "AIC")
# ══════════════════════════════════════════════════════════════════════════════

class SplashV3Cinzel(ft.Container):
    """V3-Cinzel : OLD v1 + Cinzel Decorative Bold sur le titre 'AIC'."""

    LABEL = "V3 + Cinzel"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)
        self.wave_bar1, self.wave_bar2, self.wave_bar3, self.wave_bar4, self.wave_bar5, self.wave_container = _make_equalizer_bars()
        self.logo_box = _make_logo_box(logo_content, self.wave_container)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD,
                            color=ObsidianColors.TEXT_PRIMARY,
                            font_family="Cinzel Decorative Bold"),  # ← NEW
            opacity=0.0, offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text("Audio Intelligence Companion", size=13,
                            weight=ft.FontWeight.W_500, color=ObsidianColors.TEXT_MUTED),
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=16), self.title_box,
                 ft.Container(height=4), self.subtitle_box],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        r = [False]
        await _run_old_animation(self, r)


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashV3Cyan  (OLD + sous-titre en ACCENT_CYAN)
# ══════════════════════════════════════════════════════════════════════════════

class SplashV3Cyan(ft.Container):
    """V3-Cyan : OLD v1 + sous-titre en ACCENT_CYAN (#30C4EF) au lieu de TEXT_MUTED."""

    LABEL = "V3 + Cyan"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)
        self.wave_bar1, self.wave_bar2, self.wave_bar3, self.wave_bar4, self.wave_bar5, self.wave_container = _make_equalizer_bars()
        self.logo_box = _make_logo_box(logo_content, self.wave_container)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0, offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text("Audio Intelligence Companion", size=13,
                            weight=ft.FontWeight.W_500,
                            color=ObsidianColors.ACCENT_CYAN),  # ← NEW : cyan vs muted
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Column(
                [self.logo_box, ft.Container(height=16), self.title_box,
                 ft.Container(height=4), self.subtitle_box],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        r = [False]
        await _run_old_animation(self, r)


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE : SplashV3Glow  (OLD + radial glow bg, halo pulsant CONSERVÉ)
# ══════════════════════════════════════════════════════════════════════════════

class SplashV3Glow(ft.Container):
    """V3-Glow : OLD v1 + radial glow bg Cyan+Ambre (EN COMPLÉMENT du halo pulsant)."""

    LABEL = "V3 + Glow"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        icon_src = _resolve_icon()
        logo_content = _make_logo_image(icon_src, 64)
        self.wave_bar1, self.wave_bar2, self.wave_bar3, self.wave_bar4, self.wave_bar5, self.wave_container = _make_equalizer_bars()
        self.logo_box = _make_logo_box(logo_content, self.wave_container)
        self.title_box = ft.Container(
            content=ft.Text("AIC", size=38, weight=ft.FontWeight.BOLD, color=ObsidianColors.TEXT_PRIMARY),
            opacity=0.0, offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        self.subtitle_box = ft.Container(
            content=ft.Text("Audio Intelligence Companion", size=13,
                            weight=ft.FontWeight.W_500, color=ObsidianColors.TEXT_MUTED),
            opacity=0.0, offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        # ← NEW : radial glow bg (complément du halo pulsant)
        self.bg_glow = ft.Container(
            width=min(400, w), height=min(400, h), border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0), radius=0.50,
                colors=["rgba(48, 196, 239, 0.12)", "rgba(254, 143, 64, 0.08)", "rgba(15, 17, 23, 0.0)"],
                stops=[0.0, 0.45, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        super().__init__(
            content=ft.Stack(
                [
                    ft.Container(content=self.bg_glow, alignment=ft.Alignment.CENTER, expand=True),
                    ft.Column(
                        [self.logo_box, ft.Container(height=16), self.title_box,
                         ft.Container(height=4), self.subtitle_box],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
                    ),
                ],
                alignment=ft.Alignment.CENTER, expand=True,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
            bgcolor=ObsidianColors.BG_DARK, opacity=1.0,
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        )

    async def start_animation_async(self) -> None:
        callback_called = False
        try:
            # Phase 0 : Glow bg apparaît avec le logo
            await asyncio.sleep(0.05)
            self.bg_glow.opacity = 1.0
            _safe_update(self.bg_glow)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(scale=1.0)
            self.logo_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.logo_box)

            await asyncio.sleep(0.35)
            self.wave_container.opacity = 1.0
            _safe_update(self.wave_container)

            await asyncio.sleep(0.30)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=6, blur_radius=28, color="#40FE8F40", offset=ft.Offset(0, 0)
            )
            self.wave_bar1.height = 14; self.wave_bar2.height = 24
            self.wave_bar3.height = 32; self.wave_bar4.height = 24; self.wave_bar5.height = 14
            _safe_update(self.logo_box)

            await asyncio.sleep(0.25)
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.title_box)

            await asyncio.sleep(0.15)
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=2, blur_radius=14, color="#1AFE8F40", offset=ft.Offset(0, 0)
            )
            _safe_update(self.logo_box)

            await asyncio.sleep(0.20)
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.subtitle_box)

            await asyncio.sleep(0.60)
            self.opacity = 0.0
            _safe_update(self)
            await asyncio.sleep(0.40)

        except (asyncio.CancelledError, Exception) as e:
            logger.debug(f"Glow animation interrupted: {e}")
        finally:
            if self.on_complete_callback and not callback_called:
                callback_called = True
                try:
                    self.on_complete_callback()
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRE des variantes pour la mini-app
# ══════════════════════════════════════════════════════════════════════════════

VARIANTS = {
    "old": SplashOLD,
    "new": SplashNEW,
    "v3base": SplashOLD,        # V3-base = OLD exact (production reconstruite)
    "v3svg": SplashV3SVG,
    "v3cinzel": SplashV3Cinzel,
    "v3cyan": SplashV3Cyan,
    "v3glow": SplashV3Glow,
}

VARIANT_ORDER = ["old", "new", "v3base", "v3svg", "v3cinzel", "v3cyan", "v3glow"]

VARIANT_LABELS = {
    "old": "OLD v1",
    "new": "NEW v2",
    "v3base": "V3-base (≡ OLD)",
    "v3svg": "V3 + SVG letterform",
    "v3cinzel": "V3 + Cinzel",
    "v3cyan": "V3 + Cyan",
    "v3glow": "V3 + Radial Glow",
}
