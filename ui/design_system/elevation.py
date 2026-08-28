"""
ui/design_system/elevation.py
------------------------------
Design Tokens - Élévation et Ombres (BoxShadow) pour AIC.
"""

import flet as ft


class Elevation:
    NONE = None

    SUBTLE = ft.BoxShadow(
        blur_radius=4,
        spread_radius=0,
        color="rgba(0, 0, 0, 0.25)",
        offset=ft.Offset(0, 2),
    )

    ELEVATED = ft.BoxShadow(
        blur_radius=12,
        spread_radius=0,
        color="rgba(0, 0, 0, 0.40)",
        offset=ft.Offset(0, 4),
    )

    FLOATING = ft.BoxShadow(
        blur_radius=24,
        spread_radius=2,
        color="rgba(0, 0, 0, 0.60)",
        offset=ft.Offset(0, 8),
    )

    BRAND_GLOW = ft.BoxShadow(
        blur_radius=20,
        spread_radius=2,
        color="rgba(254, 143, 64, 0.25)",  # AIC Audio Orange Glow
        offset=ft.Offset(0, 0),
    )

    CYAN_GLOW = ft.BoxShadow(
        blur_radius=20,
        spread_radius=2,
        color="rgba(48, 196, 239, 0.25)",  # AIC Tech Cyan Glow
        offset=ft.Offset(0, 0),
    )
