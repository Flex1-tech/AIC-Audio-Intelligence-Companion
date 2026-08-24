"""
ui/components/splash_screen.py
-------------------------------
Splash Screen AIC V3 — Implémentation de Référence Réactive & Paramétrée.

Principes architecturaux :
- Fondation V1/V3 : Carte Obsidian centrée avec halo BoxShadow Ambre pulsant réactif.
- Identité de marque : 100% Ambre (#FE8F40 / ObsidianColors.PRIMARY) pour la résonance audio,
  le signal égaliseur, le halo luminescent et la typographie de sous-titre.
- Performance & Lisibilité : Typographie système Bold privilégiée pour garantir une
  lisibilité instantanée sans temps de chargement de police custom pendant les ~2.3s.
- Configuration centralisée : Le paramètre `SPLASH_ANIMATION_DURATION_MS` contrôle la
  durée totale. Toutes les sous-phases d'animation recalculent automatiquement leurs délais.
- Dimensionnement réactif harmonieux : L'ensemble de la composition (carte, logo, égaliseur,
  halo, typographie et espacements) s'adapte dynamiquement selon les bornes du viewport.
"""

import asyncio
import logging
from typing import Callable, Optional

import flet as ft

from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii
from utils.path_utils import get_asset_path

logger = logging.getLogger("aic.splash")

# ── 1. Configuration centralisée du timing (Durée globale paramétrable) ─────
SPLASH_ANIMATION_DURATION_MS: int = 2300

# Pourcentages relatifs des sous-phases de la séquence d'animation (0.00 à 1.00)
_PHASE_TIMING = {
    "logo_appear": 0.02,  # Apparition initiale de la carte et du fond
    "wave_reveal": 0.16,  # Éveil de la ligne d'onde sonore
    "halo_pulse": 0.30,  # Peak du halo lumineux Ambre & impulsion max des barres
    "title_reveal": 0.42,  # Apparition du titre "AIC"
    "halo_soften": 0.50,  # Atténuation douce du halo
    "subtitle_reveal": 0.60,  # Apparition du sous-titre
    "hold_duration": 0.85,  # Maintien contemplatif de la composition finale
}

# ── 2. Bornes de responsivité de la composition ──────────────────────────────
CARD_MIN_SIZE: int = 110
CARD_MAX_SIZE: int = 165
CARD_VIEWPORT_RATIO: float = 0.22


def calculate_responsive_dimensions(viewport_w: float, viewport_h: float) -> dict:
    """
    Calcule l'ensemble des dimensions de la composition Splash en fonction du viewport.
    Garantit des Proportions Harmonieuses entre la carte, le logo, l'égaliseur et le texte.
    """
    vw = max(320.0, float(viewport_w or 900.0))
    vh = max(320.0, float(viewport_h or 700.0))
    min_dim = min(vw, vh)

    # Calcul de la taille de la carte Obsidian centrale
    card_raw = min_dim * CARD_VIEWPORT_RATIO
    card_size = int(max(CARD_MIN_SIZE, min(CARD_MAX_SIZE, card_raw)))

    # Proportions calculées
    icon_size = int(card_size * 0.58)
    bar_max_h = int(card_size * 0.28)
    title_size = int(card_size * 0.29)
    subtitle_size = int(max(11, card_size * 0.095))
    gap_logo_text = int(max(10, card_size * 0.12))
    bg_glow_size = int(max(320, min(500, min_dim * 0.55)))

    return {
        "card_size": card_size,
        "icon_size": icon_size,
        "bar_max_h": bar_max_h,
        "title_size": title_size,
        "subtitle_size": subtitle_size,
        "gap_logo_text": gap_logo_text,
        "bg_glow_size": bg_glow_size,
    }


class SplashScreen(ft.Container):
    """
    Composant Splash Screen AIC V3.
    Offre une séquence d'initialisation élégante, réactive et totalement paramétrable.
    """

    def __init__(
        self,
        page: ft.Page,
        on_complete: Optional[Callable[[], None]] = None,
        animation_duration_ms: Optional[int] = None,
    ):
        logger.info("SPLASH: INIT")
        self.on_complete_callback = on_complete

        # Prise en compte de la durée d'animation (par défaut globale)
        self.total_ms = animation_duration_ms or SPLASH_ANIMATION_DURATION_MS

        # Obtenir les dimensions réelles du viewport
        vw = (page.window.width or 900) if page.window else 900
        vh = (page.window.height or 700) if page.window else 700
        dims = calculate_responsive_dimensions(vw, vh)
        self._dims = dims
        S = dims["card_size"]

        # ── 1. Chargement de l'icône de marque (avec fallback résilient) ─────
        svg_path = get_asset_path("icon.svg") or get_asset_path("icon.png")
        icon_src = str(svg_path) if svg_path and svg_path.exists() else None

        if icon_src:
            logo_content = ft.Image(
                src=icon_src,
                width=dims["icon_size"],
                height=dims["icon_size"],
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            logo_content = ft.Icon(
                ft.Icons.GRAPHIC_EQ,
                size=int(dims["icon_size"] * 0.75),
                color=ObsidianColors.PRIMARY,
            )

        # ── 2. Barres d'égaliseur audio Ambre (#FE8F40) ───────────────────────
        bar_w = int(max(3, S * 0.028))
        self.wave_bar1 = ft.Container(
            width=bar_w,
            height=int(dims["bar_max_h"] * 0.40),
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=2,
            opacity=0.5,
        )
        self.wave_bar2 = ft.Container(
            width=bar_w,
            height=int(dims["bar_max_h"] * 0.65),
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=2,
            opacity=0.8,
        )
        self.wave_bar3 = ft.Container(
            width=bar_w,
            height=int(dims["bar_max_h"] * 1.00),
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=2,
            opacity=1.0,
        )
        self.wave_bar4 = ft.Container(
            width=bar_w,
            height=int(dims["bar_max_h"] * 0.65),
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=2,
            opacity=0.8,
        )
        self.wave_bar5 = ft.Container(
            width=bar_w,
            height=int(dims["bar_max_h"] * 0.40),
            bgcolor=ObsidianColors.PRIMARY,
            border_radius=2,
            opacity=0.5,
        )

        self.wave_container = ft.Row(
            [
                self.wave_bar1,
                self.wave_bar2,
                self.wave_bar3,
                self.wave_bar4,
                self.wave_bar5,
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        # ── 3. Carte Obsidian centrale (Le halo pulsant V1 entoure cette carte) ──
        self.logo_box = ft.Container(
            content=ft.Stack(
                [
                    logo_content,
                    ft.Container(
                        content=self.wave_container,
                        alignment=ft.Alignment(0, 0.58),
                    ),
                ],
                alignment=ft.Alignment.CENTER,
            ),
            width=S,
            height=S,
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

        # ── 4. Glow ambiant de fond (Lueur Ambre atmosphérique très douce) ───
        self.bg_glow = ft.Container(
            width=dims["bg_glow_size"],
            height=dims["bg_glow_size"],
            border_radius=9999,
            bgcolor=ft.Colors.TRANSPARENT,
            gradient=ft.RadialGradient(
                center=ft.Alignment(0, 0),
                radius=0.50,
                colors=[
                    "rgba(254, 143, 64, 0.11)",  # Ambre Audio
                    "rgba(48, 196, 239, 0.04)",  # Cyan IA très diffus
                    "rgba(15, 17, 23, 0.0)",
                ],
                stops=[0.0, 0.55, 1.0],
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

        # ── 6. Titre "AIC" (Typographie système Bold — Lisibilité optimale) ──
        self.title_text = ft.Text(
            "AIC",
            size=dims["title_size"],
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

        # ── 7. Sous-titre ("Audio Intelligence Companion" — Ambre #FE8F40) ────
        self.subtitle_text = ft.Text(
            "Audio Intelligence Companion",
            size=dims["subtitle_size"],
            weight=ft.FontWeight.W_500,
            color=ObsidianColors.PRIMARY,
        )

        self.subtitle_box = ft.Container(
            content=self.subtitle_text,
            opacity=0.0,
            offset=ft.Offset(x=0, y=0.10),
            animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── 8. Disposition globale centrée ───────────────────────────────────
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
                            ft.Container(height=dims["gap_logo_text"]),
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
        Séquence d'animation asynchrone V3 paramétrée par `self.total_ms`.
        Chaque délai de sous-phase est calculé au prorata de `self.total_ms`.
        """
        logger.info(f"SPLASH: ANIMATION START (total_ms={self.total_ms})")
        callback_called = False

        def _dur(pct: float) -> float:
            return (pct * self.total_ms) / 1000.0

        try:
            # Phase 1 : Apparition initiale de la carte et du fond ambiant
            await asyncio.sleep(_dur(_PHASE_TIMING["logo_appear"]))
            self.bg_glow.opacity = 1.0
            self._safe_update(self.bg_glow)
            self.logo_box.opacity = 1.0
            self.logo_box.scale = ft.Scale(scale=1.0)
            self.logo_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.logo_box)

            # Phase 2 : Éveil des barres d'onde sonore
            await asyncio.sleep(_dur(_PHASE_TIMING["wave_reveal"]) - _dur(_PHASE_TIMING["logo_appear"]))
            self.wave_container.opacity = 1.0
            self._safe_update(self.wave_container)

            # Phase 3 : Impulsion du halo pulsant Ambre & pic d'amplitude des barres
            await asyncio.sleep(_dur(_PHASE_TIMING["halo_pulse"]) - _dur(_PHASE_TIMING["wave_reveal"]))
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=8,
                blur_radius=34,
                color="#48FE8F40",  # Impulsion halo Ambre vive
                offset=ft.Offset(0, 0),
            )
            h_max = self._dims["bar_max_h"]
            self.wave_bar1.height = int(h_max * 0.40)
            self.wave_bar2.height = int(h_max * 0.65)
            self.wave_bar3.height = int(h_max * 1.00)
            self.wave_bar4.height = int(h_max * 0.65)
            self.wave_bar5.height = int(h_max * 0.40)
            self._safe_update(self.logo_box)

            # Phase 4 : Révélation du titre "AIC"
            await asyncio.sleep(_dur(_PHASE_TIMING["title_reveal"]) - _dur(_PHASE_TIMING["halo_pulse"]))
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.title_box)

            # Phase 4b : Atténuation douce du halo vers un niveau d'équilibre
            await asyncio.sleep(_dur(_PHASE_TIMING["halo_soften"]) - _dur(_PHASE_TIMING["title_reveal"]))
            self.logo_box.shadow = ft.BoxShadow(
                spread_radius=3,
                blur_radius=18,
                color="#20FE8F40",  # Halo Ambre stabilisé
                offset=ft.Offset(0, 0),
            )
            self._safe_update(self.logo_box)

            # Phase 5 : Apparition du sous-titre
            await asyncio.sleep(_dur(_PHASE_TIMING["subtitle_reveal"]) - _dur(_PHASE_TIMING["halo_soften"]))
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            self._safe_update(self.subtitle_box)

            # Phase 6 : Maintien de contemplation puis fondu de sortie global
            await asyncio.sleep(_dur(_PHASE_TIMING["hold_duration"]) - _dur(_PHASE_TIMING["subtitle_reveal"]))
            logger.info("SPLASH: ANIMATION COMPLETE")
            self.opacity = 0.0
            self._safe_update(self)

            # Pause finale pour laisser le fondu Flet (400ms) s'exécuter proprement
            await asyncio.sleep(_dur(1.00) - _dur(_PHASE_TIMING["hold_duration"]))

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
