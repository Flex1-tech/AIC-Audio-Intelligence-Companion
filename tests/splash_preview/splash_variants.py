"""
tests/splash_preview/splash_variants.py
----------------------------------------
Laboratoire de comparaison et de validation du Splash Screen AIC.

SOURCE DE VERITE : origin/main (SHA af092ec63b397a3edf43165e49627c4d6b282fa9)

Architecture de reference :
- Logo responsive : 65% de la plus petite dimension (clamp 300-560 px).
- SVG divise en 2 couches animees independamment :
    * layer_letterform.svg  -- structure "A" (3 paths Cyan #30C4EF)
    * layer_wave.svg        -- onde sonore (70 paths Ambre #FE8F40)
- Scanner ambiant ambre horizontal L->R (wave_glow).
- Typographie de branding : Cinzel Decorative (embarquee dans assets/fonts/).
- Timing centralise par pourcentage (SPLASH_ANIMATION_CONFIG).
- Compatible Flet 0.86.4.

NOTE WEB :
En mode Flet Web (FastAPI), les chemins absolu Windows ne sont pas resolus
par le navigateur. Les assets sont passes sous forme de CHEMINS RELATIFS
servis directement par le serveur HTTP :
    "layer_letterform.svg" -> http://localhost:8570/layer_letterform.svg
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
    """
    Resout l'asset pour Flet Web : retourne le nom relatif du fichier
    si l'asset existe dans le dossier assets/ du projet.
    En mode Web, Flet sert assets_dir comme racine HTTP, donc "layer_letterform.svg"
    est accessible sous http://localhost:8570/layer_letterform.svg.
    En mode Desktop, get_asset_path() retourne le chemin absolu.
    """
    p = get_asset_path(filename)
    if p and p.exists():
        return filename  # chemin relatif pour Flet Web
    return filename  # fallback: meme nom relatif


def _dur(pct_range: tuple, total_ms: int) -> int:
    return int((pct_range[1] - pct_range[0]) * total_ms)


def _safe_update(control: ft.Control) -> None:
    try:
        if control and control.page:
            control.update()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTE PRINCIPALE : SplashOriginMain
# Reproduction fidele de origin/main avec les nouveaux logos transparents
# et les chemins relatifs Flet Web.
# ══════════════════════════════════════════════════════════════════════════════


class SplashOriginMain(ft.Container):
    """
    Reproduction fidele de origin/main:ui/components/splash_screen.py.

    Seules differences par rapport a l'original :
    - Chemins des assets SVG relatifs (au lieu d'absolus str(Path)) pour Flet Web.
    - Polices declarees via page.fonts dans main.py.
    - Les logos sont desormais transparents (fond noir retire).

    Tout le reste est identique :
    - Sizing : clamp(300, min(w,h)*0.65, 560) px.
    - Timing : 5000 ms, 100% relatif via SPLASH_ANIMATION_CONFIG.
    - Scanner horizontal L->R (wave_glow LinearGradient).
    - Halo ambre BoxShadow pulsant.
    - Cinzel Decorative Bold / Regular.
    - Fond Obsidian BG_DARK (#0F1117).
    """

    LABEL = "★ Reference origin/main (nouveaux logos transparents)"

    def __init__(self, page: ft.Page, on_complete: Optional[Callable[[], None]] = None):
        self.on_complete_callback = on_complete
        cfg = SPLASH_ANIMATION_CONFIG
        self.total_ms = cfg["total_ms"]

        def _d(k):
            return _dur(cfg[k], self.total_ms)

        # ── Taille du logo (identique a origin/main : 65% de min_dim, clamp 300-560) ──
        w = (page.window.width or 900) if page.window else 900
        h = (page.window.height or 700) if page.window else 700
        self.logo_size = int(max(300, min(560, min(w, h) * 0.65)))
        S = self.logo_size

        # ── Resolution des assets SVG (chemin relatif pour Flet Web) ────────────
        lf_src = _resolve_web("layer_letterform.svg")
        wv_src = _resolve_web("layer_wave.svg")
        icon_src = _resolve_web("icon.svg")

        # ── Couche 1 : Letterform (#30C4EF – structure "A") ─────────────────────
        self.letterform_img = ft.Image(
            src=lf_src if lf_src else icon_src,
            width=S,
            height=S,
            fit=ft.BoxFit.CONTAIN,
        )

        # ── Couche 2 : Wave / Onde IA (#FE8F40) ─────────────────────────────────
        self.wave_img = ft.Image(
            src=wv_src if wv_src else "",
            width=S,
            height=S,
            fit=ft.BoxFit.CONTAIN,
            opacity=0.0,
            animate_opacity=ft.Animation(_d("wave_alive"), ft.AnimationCurve.EASE_OUT_CUBIC),
        )

        # ── Couche 3 : Scanner ambiant ambre horizontal L->R ────────────────────
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

        # ── Logo Stack (letterform + wave + scanner) ────────────────────────────
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

        # ── Titre "AIC" (Cinzel Decorative Bold) ────────────────────────────────
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

        # ── Sous-titre (Cinzel Decorative Regular) ───────────────────────────────
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

        # ── Degrade radial de fond ───────────────────────────────────────────────
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

        # ── Layout global ────────────────────────────────────────────────────────
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
        """
        Sequence d'animation identique a origin/main, 100% relative
        en pourcentages de SPLASH_ANIMATION_CONFIG["total_ms"].
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

        try:
            # Phase 1 : Apparition fond ambiant & structure logo A
            await _wait_until(cfg["logo_intro"][0])
            self.bg_glow.opacity = 1.0
            self.logo_container.opacity = 1.0
            self.logo_container.scale = ft.Scale(scale=1.0)
            self.logo_container.offset = ft.Offset(x=0, y=0)
            _safe_update(self.bg_glow)
            _safe_update(self.logo_container)

            # Phase 2 : Signal onde dormant
            await _wait_until(cfg["wave_dim"][0])
            self.wave_img.opacity = 0.22
            _safe_update(self.wave_img)

            # Phase 3 : Balayage du faisceau ambre L->R
            await _wait_until(cfg["wave_sweep"][0])
            self.wave_glow.opacity = 0.90
            self.wave_glow.left = self._scan_left_start
            _safe_update(self.wave_glow)

            await asyncio.sleep(0.03)
            self.wave_glow.left = self._scan_left_end
            _safe_update(self.wave_glow)

            # Phase 4 : Eveil complet de l'onde
            await _wait_until(cfg["wave_alive"][0])
            self.wave_img.opacity = 1.0
            _safe_update(self.wave_img)

            # Phase 5 : Impulsion halo ambre
            await _wait_until(cfg["halo_pulse"][0])
            self.logo_container.shadow = ft.BoxShadow(
                spread_radius=8,
                blur_radius=40,
                color="#38F59E0B",
                offset=ft.Offset(x=0, y=0),
            )
            _safe_update(self.logo_container)

            # Disparition du scanner
            await _wait_until(cfg["wave_sweep"][1])
            self.wave_glow.opacity = 0.0
            _safe_update(self.wave_glow)

            # Attenuation douce du halo
            await _wait_until(cfg["halo_pulse"][1])
            self.logo_container.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=16,
                color="#14F59E0B",
                offset=ft.Offset(x=0, y=0),
            )
            _safe_update(self.logo_container)

            # Phase 6 : Titre "AIC"
            await _wait_until(cfg["title_intro"][0])
            self.title_box.opacity = 1.0
            self.title_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.title_box)

            # Phase 7 : Sous-titre
            await _wait_until(cfg["subtitle_intro"][0])
            self.subtitle_box.opacity = 1.0
            self.subtitle_box.offset = ft.Offset(x=0, y=0)
            _safe_update(self.subtitle_box)

            # Phase 8 : Fondu de sortie vers l'UI principale
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
# VARIANTE COMPARAISON : Production locale actuelle (ui/components/splash_screen.py)
# ══════════════════════════════════════════════════════════════════════════════


class SplashProductionLocal(ft.Container):
    """
    Proxy vers la production locale ui/components/splash_screen.SplashScreen.
    Permet de comparer la production locale avec la reference origin/main.
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

# Pour la compatibilite avec les anciens tests
SPLASH_ANIMATION_DURATION_MS = SPLASH_ANIMATION_CONFIG["total_ms"]


def calculate_target_responsive_dimensions(viewport_w: float, viewport_h: float) -> dict:
    """Calcule les dimensions du logo selon la formule origin/main."""
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


# Alias pour les tests existants
SplashV3Target = SplashOriginMain
