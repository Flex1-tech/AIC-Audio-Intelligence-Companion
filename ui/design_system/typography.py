"""
ui/design_system/typography.py
-------------------------------
Design Tokens - Hiérarchie typographique officielle pour AIC.

Règle d'usage Cinzel Decorative :
- Cinzel Decorative Bold / Regular est strictement réservée au BRANDING (Logo header, SplashScreen).
- Toute l'UI applicative (titres, corps, étiquettes, boutons) utilise la typographie système (Roboto / Segoe UI / San Francisco).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyStyle:
    size: int
    weight: str = "normal"
    font_family: str = "System"


class Typography:
    # ── Branding (Cinzel Decorative) ──────────────────────────────────────────
    BRAND_TITLE = TypographyStyle(size=20, font_family="Cinzel Decorative Bold")
    BRAND_SUBTITLE = TypographyStyle(size=12, font_family="Cinzel Decorative Regular")

    # ── Hiérarchie M3 / HIG ───────────────────────────────────────────────────
    DISPLAY = TypographyStyle(size=28, weight="bold")
    HEADLINE = TypographyStyle(size=20, weight="bold")
    TITLE = TypographyStyle(size=16, weight="w600")
    SUBTITLE = TypographyStyle(size=13, weight="w500")
    BODY = TypographyStyle(size=14, weight="normal")
    LABEL = TypographyStyle(size=12, weight="w500")
    CAPTION = TypographyStyle(size=12, weight="normal")
    METADATA = TypographyStyle(size=11, weight="normal")
    MONO = TypographyStyle(size=11, weight="normal", font_family="monospace")

    # Legacy aliases
    APP_TITLE = HEADLINE
    SECTION_HEADER = TITLE
