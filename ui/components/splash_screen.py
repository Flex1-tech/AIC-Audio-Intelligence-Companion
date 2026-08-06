"""
ui/components/splash_screen.py
------------------------------
Splash Screen premium v2 — AIC / Obsidian Horizon Design System.

Architecture :
- Logo responsive : 65 % de la plus petite dimension de la fenetre (clamped 300-560 px).
- SVG divise en 2 couches animees independamment :
    * layer_letterform.svg -- structure "A" (3 paths #30C4EF)
    * layer_wave.svg       -- onde sonore (70 paths #FE8F40 et variantes)
- Effet "IA qui s'eveille" : un faisceau radial ambre parcourt la zone de l'onde (L->R).
- Typographie de branding : Cinzel Decorative (embarquee dans assets/fonts/).
- Timing centralise par pourcentage (SPLASH_ANIMATION_CONFIG) : modification instantanee
  de la vitesse globale en changeant uniquement ``total_ms``.
- Compatible Flet 0.86.4 (ft.Scale / ft.Offset / ft.BoxFit / ft.AnimationCurve).
"""

import asyncio
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from utils.path_utils import get_asset_path

# ── Configuration centralisee de l'animation (en pourcentages de total_ms) ───
SPLASH_ANIMATION_CONFIG = {
    "total_ms": 3000,
    "logo_intro": (0.00, 0.25),  # 0% -> 25% : Apparition structure A logo & fond
    "wave_dim": (0.15, 0.35),  # 15% -> 35% : Signal onde dormant (opacite 0.22)
    "wave_sweep": (0.28, 0.60),  # 28% -> 60% : Balayage du faisceau ambre L->R
    "wave_alive": (0.32, 0.65),  # 32% -> 65% : Eveil complet de l'onde (opacite 1.0)
    "halo_pulse": (0.55, 0.70),  # 55% -> 70% : Impulsion halo ambre BoxShadow
    "title_intro": (0.58, 0.78),  # 58% -> 78% : Apparition du titre "AIC"
    "subtitle_intro": (0.68, 0.88),  # 68% -> 88% : Apparition du sous-titre
    "fade_out": (0.88, 1.00),  # 88% -> 100% : Fondu vers l'UI principale
}

# ── Constantes de position de l'onde dans le SVG (viewBox 1024x1024) ---------
_WAVE_SVG_X_MIN = 378.0  # bord gauche de l'onde (SVG coords)
_WAVE_SVG_X_MAX = 652.0  # bord droit de l'onde
_WAVE_SVG_Y_MIN = 558.0  # bord haut de l'onde
_WAVE_SVG_Y_MAX = 628.0  # bord bas de l'onde
_SVG_SIZE = 1024.0


def _wave_rect(logo_size: int) -> tuple:
    """Retourne (left, top, width, height) de la zone onde en pixels ecran."""
    scale = logo_size / _SVG_SIZE
    left = _WAVE_SVG_X_MIN * scale
    top = _WAVE_SVG_Y_MIN * scale
    w = (_WAVE_SVG_X_MAX - _WAVE_SVG_X_MIN) * scale
    h = (_WAVE_SVG_Y_MAX - _WAVE_SVG_Y_MIN) * scale
    return left, top, w, h


class SplashScreen(ft.Container):
    """
    Composant Splash Screen premium avec animation SVG multi-couches.
    Séquencement 100% relatif piloter par SPLASH_ANIMATION_CONFIG.
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.on_complete_callback = on_complete

        # ── Calculs de timing adaptatifs ──────────────────────────────────────
        self.total_ms = SPLASH_ANIMATION_CONFIG["total_ms"]

        def _dur(pct_range: tuple) -> int:
            return int((pct_range[1] - pct_range[0]) * self.total_ms)

        cfg = SPLASH_ANIMATION_CONFIG

        # ── Taille du logo (responsive) ───────────────────────────────────────
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        self.logo_size = int(max(300, min(560, min(w, h) * 0.65)))
        S = self.logo_size

        # ── Resolution des assets SVG ─────────────────────────────────────────
        lf_path = get_asset_path("layer_letterform.svg")
        wv_path = get_asset_path("layer_wave.svg")
        icon_path = get_asset_path("icon.svg") or get_asset_path("icon.png")

        def _svg_src(p):
            return str(p) if p and p.exists() else None

        lf_src = _svg_src(lf_path)
        wv_src = _svg_src(wv_path)
        icon_src = _svg_src(icon_path)

        # ── Couche 1 : Letterform (#30C4EF – structure "A") ───────────────────
        if lf_src:
            self.letterform_img = ft.Image(
                src=lf_src,
                width=S,
                height=S,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            self.letterform_img = ft.Image(
                src=icon_src or "",
                width=S,
                height=S,
                fit=ft.BoxFit.CONTAIN,
            )

        # ── Couche 2 : Wave / Onde IA (#FE8F40 et variantes) ─────────────────
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

        # ── Couche 3 : Glow scanner (faisceau ambre L->R sur l'onde) ──────────
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
                colors=[
                    "transparent",
                    "#BFF59E0B",
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

        # ── Logo Stack ────────────────────────────────────────────────────────
        self.logo_stack = ft.Stack(
            [
                self.letterform_img,
                self.wave_img,
                self.wave_glow,
            ],
            width=S,
            height=S,
        )

        # Conteneur logo global — animations d'entree
        self.logo_container = ft.Container(
            content=self.logo_stack,
            width=S,
            height=S,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.88),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.03),
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(_dur(cfg["logo_intro"]) + 100, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["logo_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        # ── Titre "AIC" (Cinzel Decorative Bold) ───────────────────────────────
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
            animate_opacity=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["title_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Sous-titre (Cinzel Decorative Regular) ────────────────────────────
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
            animate_opacity=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(_dur(cfg["subtitle_intro"]), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Degrade radial de fond ────────────────────────────────────────────
        self.bg_glow = ft.Container(
            width=min(S * 1.6, w),
            height=min(S * 1.6, h),
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.5,
                colors=[
                    "#10F59E0B",
                    "transparent",
                ],
                stops=[0.0, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(_dur(cfg["logo_intro"]) + 300, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Layout global ─────────────────────────────────────────────────────
        gap_logo_text = max(12, int(S * 0.035))

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
            animate_opacity=ft.Animation(_dur(cfg["fade_out"]), ft.AnimationCurve.EASE_IN_OUT),
        )

    # ── Orchestration asynchrone donnee par SPLASH_ANIMATION_CONFIG ─────────
    async def start_animation_async(self) -> None:
        """
        Sequence d'animation 100% relative en pourcentages de SPLASH_ANIMATION_CONFIG["total_ms"].
        """
        cfg = SPLASH_ANIMATION_CONFIG
        t_current = 0.0

        def _sec_at(pct: float) -> float:
            return (pct * self.total_ms) / 1000.0

        async def _wait_until(target_pct: float) -> None:
            nonlocal t_current
            if target_pct > t_current:
                await asyncio.sleep(_sec_at(target_pct) - _sec_at(t_current))
                t_current = target_pct

        # Phase 1 : Apparition fond ambiant & structure logo A
        await _wait_until(cfg["logo_intro"][0])
        self.bg_glow.opacity = 1.0
        self.logo_container.opacity = 1.0
        self.logo_container.scale = ft.Scale(scale=1.0)
        self.logo_container.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.bg_glow)
        self._safe_update(self.logo_container)

        # Phase 2 : Signal onde dormant
        await _wait_until(cfg["wave_dim"][0])
        self.wave_img.opacity = 0.22
        self._safe_update(self.wave_img)

        # Phase 3 : Balayage du faisceau ambre L->R
        await _wait_until(cfg["wave_sweep"][0])
        self.wave_glow.opacity = 0.90
        self.wave_glow.left = self._scan_left_start
        self._safe_update(self.wave_glow)

        await asyncio.sleep(0.03)
        self.wave_glow.left = self._scan_left_end
        self._safe_update(self.wave_glow)

        # Phase 4 : Eveil complet de l'onde
        await _wait_until(cfg["wave_alive"][0])
        self.wave_img.opacity = 1.0
        self._safe_update(self.wave_img)

        # Phase 5 : Impulsion Halo ambre
        await _wait_until(cfg["halo_pulse"][0])
        self.logo_container.shadow = ft.BoxShadow(
            spread_radius=8,
            blur_radius=40,
            color="#38F59E0B",
            offset=ft.Offset(x=0, y=0),
        )
        self._safe_update(self.logo_container)

        # Disparition du scanner
        await _wait_until(cfg["wave_sweep"][1])
        self.wave_glow.opacity = 0.0
        self._safe_update(self.wave_glow)

        # Attenuation douce du halo
        await _wait_until(cfg["halo_pulse"][1])
        self.logo_container.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=16,
            color="#14F59E0B",
            offset=ft.Offset(x=0, y=0),
        )
        self._safe_update(self.logo_container)

        # Phase 6 : Titre "AIC"
        await _wait_until(cfg["title_intro"][0])
        self.title_box.opacity = 1.0
        self.title_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.title_box)

        # Phase 7 : Sous-titre
        await _wait_until(cfg["subtitle_intro"][0])
        self.subtitle_box.opacity = 1.0
        self.subtitle_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.subtitle_box)

        # Phase 8 : Fondu de sortie vers l'UI principale
        await _wait_until(cfg["fade_out"][0])
        self.opacity = 0.0
        self._safe_update(self)

        # Attente de la fin du fondu et nettoyage
        await _wait_until(cfg["fade_out"][1])
        await asyncio.sleep(0.05)

        if self.on_complete_callback:
            self.on_complete_callback()

    def _safe_update(self, control: ft.Control) -> None:
        try:
            control.update()
        except Exception:
            pass
