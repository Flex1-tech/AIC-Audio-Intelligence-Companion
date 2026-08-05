"""
ui/components/splash_screen.py
------------------------------
Écran et animation de démarrage (Splash Screen) premium pour AIC.
Cohérent avec le design system Obsidian Horizon (inspiration Linear / Raycast / Arc).

Séquence d'animation (~2.2s à 60 FPS) :
1. Fond plein écran Obsidian (BG_DARK #0F1117).
2. Apparition progressive du logo (opacité 0→1, scale 0.92→1.0, ease-out-cubic).
3. Animation de l'onde sonore centrale (barres d'égaliseur en balayage).
4. Impulsion de halo lumineux ambre (ObsidianColors.PRIMARY).
5. Révélation synchronisée du titre "AIC" (montée 6px, opacité 0→1).
6. Apparition du sous-titre "Audio Intelligence Companion" avec délai.
7. Fondu de sortie fluide (opacity 1.0→0.0 sur 400ms) révélant l'UI sans écran noir.

API Flet 0.86.4 :
- ft.BoxFit (pas ft.ImageFit)
- ft.Scale / ft.Offset (pas ft.transform.Scale / ft.transform.Offset)
- ft.AnimationCurve (enum disponible directement)
"""

import asyncio
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path


class SplashScreen(ft.Container):
    """
    Composant Splash Screen haute performance avec animations séquencées.
    Compatible Flet 0.86.4.
    """

    def __init__(self, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete

        # ── 1. Résolution de l'asset SVG ──────────────────────────────────────
        svg_path = get_asset_path("icon.svg") or get_asset_path("icon.png")
        icon_src = str(svg_path) if svg_path and svg_path.exists() else None

        if icon_src:
            logo_content = ft.Image(
                src=icon_src,
                width=84,
                height=84,
                fit=ft.BoxFit.CONTAIN,  # Flet 0.86.4 : ft.BoxFit, pas ft.ImageFit
            )
        else:
            logo_content = ft.Icon(
                ft.Icons.GRAPHIC_EQ,
                size=48,
                color=ObsidianColors.PRIMARY,
            )

        # ── 2. Barres d'égaliseur (Signal IA) ────────────────────────────────
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

        # ── 3. Logo Box avec transformation initiale ──────────────────────────
        # Flet 0.86.4 : ft.Scale(scale=...) et ft.Offset(x=..., y=...)
        self.logo_box = ft.Container(
            content=ft.Stack(
                [
                    logo_content,
                    ft.Container(
                        content=self.wave_container,
                        alignment=ft.Alignment(0, 0.45),
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            width=100,
            height=100,
            border_radius=Radii.LG,
            bgcolor=ObsidianColors.SURFACE_DARK,
            alignment=ft.Alignment.CENTER,
            scale=ft.Scale(scale=0.92),  # ft.Scale, pas ft.transform.Scale
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.04),  # ft.Offset, pas ft.transform.Offset
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            shadow=None,
        )

        # ── 4. Titre "AIC" ────────────────────────────────────────────────────
        self.title_box = ft.Container(
            content=ft.Text(
                "AIC",
                size=36,
                weight=ft.FontWeight.BOLD,
                color=ObsidianColors.TEXT_PRIMARY,
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.15),
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 5. Sous-titre ─────────────────────────────────────────────────────
        self.subtitle_box = ft.Container(
            content=ft.Text(
                "Audio Intelligence Companion",
                size=13,
                weight=ft.FontWeight.W_500,
                color=ObsidianColors.TEXT_MUTED,
            ),
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 6. Layout global ──────────────────────────────────────────────────
        super().__init__(
            content=ft.Column(
                [
                    self.logo_box,
                    ft.Container(height=16),
                    self.title_box,
                    ft.Container(height=4),
                    self.subtitle_box,
                ],
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

    # ── Orchestration asynchrone ──────────────────────────────────────────────
    async def start_animation_async(self) -> None:
        """
        Déclenche la séquence d'animation (~2.2s, 60 FPS).
        """
        # Étape 1 – Logo : entrée (scale + opacity + offset), 50ms
        await asyncio.sleep(0.05)
        self.logo_box.opacity = 1.0
        self.logo_box.scale = ft.Scale(scale=1.0)
        self.logo_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.logo_box)

        # Étape 2 – Onde sonore apparaît, 350ms
        await asyncio.sleep(0.35)
        self.wave_container.opacity = 1.0
        self._safe_update(self.wave_container)

        # Étape 3 – Impulsion de halo ambre, 650ms
        await asyncio.sleep(0.30)
        self.logo_box.shadow = ft.BoxShadow(
            spread_radius=6,
            blur_radius=28,
            color="#40F59E0B",  # Halo ambre translucide 25%
            offset=ft.Offset(x=0, y=0),
        )
        # Barres d'égaliseur : montée de hauteur (AI awakening)
        self.wave_bar1.height = 14
        self.wave_bar2.height = 24
        self.wave_bar3.height = 32
        self.wave_bar4.height = 24
        self.wave_bar5.height = 14
        self._safe_update(self.logo_box)

        # Étape 4 – Titre "AIC", 1000ms
        await asyncio.sleep(0.25)
        self.title_box.opacity = 1.0
        self.title_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.title_box)

        # Atténuation douce du halo après l'impulsion
        await asyncio.sleep(0.15)
        self.logo_box.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=14,
            color="#1AF59E0B",  # Atténuation
            offset=ft.Offset(x=0, y=0),
        )
        self._safe_update(self.logo_box)

        # Étape 5 – Sous-titre, 1200ms
        await asyncio.sleep(0.20)
        self.subtitle_box.opacity = 1.0
        self.subtitle_box.offset = ft.Offset(x=0, y=0)
        self._safe_update(self.subtitle_box)

        # Étape 6 – Fondu de sortie, ~1800ms → 2200ms
        await asyncio.sleep(0.60)
        self.opacity = 0.0
        self._safe_update(self)

        # Attente du fondu (400ms) puis callback de nettoyage
        await asyncio.sleep(0.42)
        if self.on_complete_callback:
            self.on_complete_callback()

    def _safe_update(self, control: ft.Control) -> None:
        try:
            control.update()
        except Exception:
            pass
