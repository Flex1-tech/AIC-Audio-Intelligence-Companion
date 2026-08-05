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
- Typographie : Cinzel Decorative (embarque dans assets/fonts/), fallback sans-serif.
- Duree totale : ~3.0 s a 60 FPS.
- Aucune dependance reseau au demarrage.
- Compatible Flet 0.86.4 (ft.Scale / ft.Offset / ft.BoxFit / ft.AnimationCurve).

Sequence :
  80 ms  -- letterform : opacity 0->1 / scale 0.88->1.0 / easeOutCubic 700ms
 500 ms  -- wave (dim) : opacity 0->0.22 / easeOutCubic 500ms
 900 ms  -- glow scanner : balaye L->R sur la zone onde / 950ms
 950 ms  -- wave (alive) : opacity 0.22->1.0 / easeOutCubic 650ms
1150 ms  -- halo ambre BoxShadow / impulsion unique
1350 ms  -- attenuation halo
1600 ms  -- titre "AIC" : offset Y ->0 / opacity 0->1 / 520ms
1950 ms  -- sous-titre : opacity 0->1 / 400ms
2550 ms  -- SplashScreen opacity 1->0 / 450ms
3020 ms  -- on_complete() / retrait du Stack
"""

import asyncio
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from utils.path_utils import get_asset_path

# ── Constantes de position de l'onde dans le SVG (viewBox 1024x1024) ---------
# Deduites de l'analyse des paths #FE8F40 dans icon.svg.
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
    Passer ``page`` pour le calcul responsive de la taille du logo.
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.on_complete_callback = on_complete

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
            # Fallback : logo complet si les couches sont absentes
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
                animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            )
        else:
            self.wave_img = ft.Container()  # noop fallback

        # ── Couche 3 : Glow scanner (faisceau ambre L→R sur l'onde) ──────────
        wave_left, wave_top, wave_w, wave_h = _wave_rect(S)

        # Le faisceau est legerement plus large et haut que la zone onde.
        beam_w = int(wave_w * 0.32)  # ~32 % de la largeur de l'onde
        beam_h = int(wave_h * 2.6)  # legerement plus haut que l'onde
        beam_top = wave_top - (beam_h - wave_h) / 2  # centre verticalement

        # Depart : juste avant le bord gauche de l'onde
        self._scan_left_start = wave_left - beam_w * 0.2
        # Arrivee : juste apres le bord droit de l'onde
        self._scan_left_end = wave_left + wave_w - beam_w * 0.8

        self.wave_glow = ft.Container(
            width=beam_w,
            height=beam_h,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[
                    "transparent",
                    "#BFF59E0B",  # ambre 75% opacite centre
                    "transparent",
                ],
                stops=[0.0, 0.5, 1.0],
            ),
            opacity=0.0,
            left=self._scan_left_start,
            top=beam_top,
            animate_opacity=ft.Animation(180, ft.AnimationCurve.EASE_IN_OUT),
            animate_position=ft.Animation(950, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── Logo Stack (couches superposees) ──────────────────────────────────
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
            animate_opacity=ft.Animation(700, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(800, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(700, ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        # ── Titre "AIC" (Cinzel Decorative Bold) ───────────────────────────────
        title_size = max(36, int(S * 0.095))
        self.title_box = ft.Container(
            content=ft.Text(
                "AIC",
                size=title_size,
                weight=ft.FontWeight.BOLD,
                color=ObsidianColors.TEXT_PRIMARY,
                font_family="Cinzel Decorative",
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.12),
            animate_opacity=ft.Animation(520, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(520, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Sous-titre ────────────────────────────────────────────────────────
        subtitle_size = max(11, int(S * 0.030))
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion",
                size=subtitle_size,
                weight=ft.FontWeight.W_500,
                color=ObsidianColors.TEXT_MUTED,
                font_family="Cinzel Decorative",
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Degre radial de fond (profondeur / halo ambiant) ──────────────────
        self.bg_glow = ft.Container(
            width=min(S * 1.6, w),
            height=min(S * 1.6, h),
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.5,
                colors=[
                    "#10F59E0B",  # ambre tres translucide au centre
                    "transparent",
                ],
                stops=[0.0, 1.0],
            ),
            opacity=0.0,
            animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Layout global ─────────────────────────────────────────────────────
        gap_logo_text = max(12, int(S * 0.035))

        super().__init__(
            content=ft.Stack(
                [
                    # Fond degrade centre
                    ft.Container(
                        content=self.bg_glow,
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    # Contenu principal centre
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
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_IN_OUT),
        )

    # ── Orchestration asynchrone ──────────────────────────────────────────────
    async def start_animation_async(self) -> None:
        """
        Sequence d'animation premium (~3.0 s, 60 FPS).
        Toutes les durees sont en secondes.
        """
        # Phase 1 : Fond ambiant + Letterform (80ms)
        await asyncio.sleep(0.08)

        self.bg_glow.opacity = 1.0
        self.logo_container.opacity = 1.0
        self.logo_container.scale = ft.Scale(scale=1.0)
        self.logo_container.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.bg_glow)
        self._safe_update(self.logo_container)

        # Phase 2 : Onde endormie — signal tres discret (500ms)
        await asyncio.sleep(0.42)

        self.wave_img.opacity = 0.22
        self._safe_update(self.wave_img)

        # Phase 3 : Glow scanner L->R (900ms)
        await asyncio.sleep(0.38)

        # Apparition du faisceau au point de depart
        self.wave_glow.opacity = 0.90
        self.wave_glow.left = self._scan_left_start
        self._safe_update(self.wave_glow)

        await asyncio.sleep(0.04)

        # Sweep vers la droite — le faisceau "lit" l'onde
        self.wave_glow.left = self._scan_left_end
        self._safe_update(self.wave_glow)

        # Phase 4 : Wave s'eveille (950ms -> pleine intensite)
        await asyncio.sleep(0.05)

        self.wave_img.animate_opacity = ft.Animation(650, ft.AnimationCurve.EASE_OUT_CUBIC)
        self.wave_img.opacity = 1.0
        self._safe_update(self.wave_img)

        # Phase 5 : Halo ambre — impulsion unique (1150ms)
        await asyncio.sleep(0.28)

        self.logo_container.shadow = ft.BoxShadow(
            spread_radius=8,
            blur_radius=40,
            color="#38F59E0B",  # halo ambre 22% opacite
            offset=ft.Offset(x=0, y=0),
        )
        self._safe_update(self.logo_container)

        # Scanner disparait apres le passage
        await asyncio.sleep(0.40)

        self.wave_glow.opacity = 0.0
        self._safe_update(self.wave_glow)

        # Attenuation douce du halo (1350ms)
        await asyncio.sleep(0.20)

        self.logo_container.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=16,
            color="#14F59E0B",  # halo tres attenue
            offset=ft.Offset(x=0, y=0),
        )
        self._safe_update(self.logo_container)

        # Phase 6 : Titre "AIC" (1600ms)
        await asyncio.sleep(0.10)

        self.title_box.opacity = 1.0
        self.title_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.title_box)

        # Phase 7 : Sous-titre (1950ms)
        await asyncio.sleep(0.35)

        self.subtitle_box.opacity = 1.0
        self.subtitle_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.subtitle_box)

        # Phase 8 : Maintien puis fondu de sortie (2550ms)
        await asyncio.sleep(0.62)

        self.opacity = 0.0
        self._safe_update(self)

        # Attente de la fin du fondu (450ms) + marge de securite
        await asyncio.sleep(0.50)

        if self.on_complete_callback:
            self.on_complete_callback()

    def _safe_update(self, control: ft.Control) -> None:
        try:
            control.update()
        except Exception:
            pass
