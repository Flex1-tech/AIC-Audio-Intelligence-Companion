"""
ui/components/splash_screen.py
------------------------------
Écran et animation de démarrage (Splash Screen) premium pour AIC.
Cohérent avec le design system Obsidian Horizon (inspiration Linear / Raycast / Arc).

Séquence d'animation (~2.2s à 60 FPS) :
1. Fond plein écran Obsidian (BG_DARK #0F1117).
2. Apparition progressive du logo (opacité 0→1, scale 0.92→1.0, ease-out-cubic).
3. Animation de l'onde sonore centrale (barres d'égaliseur animées en balayage).
4. Impulsion de halo lumineux ambre (ObsidianColors.PRIMARY).
5. Révélation synchronisée du titre "AIC" (montée 6px, opacité 0→1).
6. Apparition du sous-titre "Audio Intelligence Companion" avec délai.
7. Fondu de sortie fluide (opacity 1.0→0.0 sur 400ms) révélant l'UI principale sans écran noir.
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
    """

    def __init__(self, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete

        # ── 1. Résolution de l'asset SVG / Icone ──────────────────────────────
        svg_path = get_asset_path("icon.svg") or get_asset_path("icon.png")
        icon_src = str(svg_path) if svg_path and svg_path.exists() else None

        # ── 2. Logo Container avec Halo & Transformation ─────────────────────
        if icon_src:
            logo_content = ft.Image(
                src=icon_src,
                width=84,
                height=84,
                fit=ft.ImageFit.CONTAIN,
            )
        else:
            logo_content = ft.Icon(
                ft.Icons.GRAPHIC_EQ,
                size=48,
                color=ObsidianColors.PRIMARY,
            )

        # Barres d'égaliseur intégrées animées (Signal IA)
        self.wave_bar1 = ft.Container(
            width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4
        )
        self.wave_bar2 = ft.Container(
            width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7
        )
        self.wave_bar3 = ft.Container(
            width=3, height=22, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=1.0
        )
        self.wave_bar4 = ft.Container(
            width=3, height=14, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.7
        )
        self.wave_bar5 = ft.Container(
            width=3, height=8, bgcolor=ObsidianColors.PRIMARY, border_radius=2, opacity=0.4
        )

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

        # Conteneur du Logo avec Halo réactif
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
            scale=ft.transform.Scale(0.92),
            opacity=0.0,
            offset=ft.transform.Offset(0, 0.04),
            animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(600, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC),
            # Box shadow pour l'impulsion lumineuse (Halo ambre)
            shadow=None,
        )

        # Ligne de balayage lumineuse (Wave Reveal)
        self.wave_reveal_line = ft.Container(
            width=0,
            height=2,
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=1,
            opacity=0.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 3. Titre "AIC" ────────────────────────────────────────────────────
        self.title_text = ft.Text(
            "AIC",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=ObsidianColors.TEXT_PRIMARY,
        )

        self.title_box = ft.Container(
            content=self.title_text,
            opacity=0.0,
            offset=ft.transform.Offset(0, 0.15),  # 6-8px montée verticale
            animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 4. Sous-titre "Audio Intelligence Companion" ──────────────────────
        self.subtitle_text = ft.Text(
            "Audio Intelligence Companion",
            size=13,
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.TEXT_MUTED,
        )

        self.subtitle_box = ft.Container(
            content=self.subtitle_text,
            opacity=0.0,
            offset=ft.transform.Offset(0, 0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 5. Layout global du Splash Screen ─────────────────────────────────
        super().__init__(
            content=ft.Column(
                [
                    self.logo_box,
                    ft.Container(height=12),
                    self.wave_reveal_line,
                    ft.Container(height=4),
                    self.title_box,
                    ft.Container(height=2),
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

    # ── Orchestration Asynchrone de la Séquence d'Animation ─────────────
    async def start_animation_async(self) -> None:
        """
        Déclenche la séquence d'animation à 60 FPS (~2.1s).
        """
        # Étape 1 : Apparition fluide du Logo (0 -> 100ms)
        await asyncio.sleep(0.05)
        self.logo_box.opacity = 1.0
        self.logo_box.scale = ft.transform.Scale(1.0)
        self.logo_box.offset = ft.transform.Offset(0, 0)
        self._safe_update(self.logo_box)

        # Étape 2 : Éveil de l'onde sonore intégrée (400ms)
        await asyncio.sleep(0.35)
        self.wave_container.opacity = 1.0
        self._safe_update(self.wave_container)

        # Étape 3 : Impulsion de Halo Ambre & Balayage de l'onde (750ms)
        await asyncio.sleep(0.30)
        self.logo_box.shadow = ft.BoxShadow(
            spread_radius=6,
            blur_radius=28,
            color="#40F59E0B",  # Halo ambre translucide (25% opacité)
            offset=ft.Offset(0, 0),
        )
        self._safe_update(self.logo_box)

        # Animation des barres de signal
        self.wave_bar1.height = 14
        self.wave_bar2.height = 24
        self.wave_bar3.height = 32
        self.wave_bar4.height = 24
        self.wave_bar5.height = 14
        self._safe_update(self.logo_box)

        # Étape 4 : Transition par onde (Wave Reveal) & Titre "AIC" (1000ms)
        await asyncio.sleep(0.25)
        self.title_box.opacity = 1.0
        self.title_box.offset = ft.transform.Offset(0, 0)
        self._safe_update(self.title_box)

        # Atténuation douce du halo après l'impulsion
        await asyncio.sleep(0.15)
        self.logo_box.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=14,
            color="#1AF59E0B",  # Diminution douce
            offset=ft.Offset(0, 0),
        )
        self._safe_update(self.logo_box)

        # Étape 5 : Apparition du Sous-titre (1350ms)
        await asyncio.sleep(0.20)
        self.subtitle_box.opacity = 1.0
        self.subtitle_box.offset = ft.transform.Offset(0, 0)
        self._safe_update(self.subtitle_box)

        # Étape 6 : Maintien et transition vers l'application (1900ms -> 2300ms)
        await asyncio.sleep(0.60)
        self.opacity = 0.0
        self._safe_update(self)

        # Attente de la fin du fondu (400ms) puis appel du callback de fermeture
        await asyncio.sleep(0.42)
        if self.on_complete_callback:
            self.on_complete_callback()

    def _safe_update(self, control: ft.Control) -> None:
        try:
            control.update()
        except Exception:
            pass
