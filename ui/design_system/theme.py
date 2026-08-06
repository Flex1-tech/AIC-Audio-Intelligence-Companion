"""
Dark and light theme definitions for AIC.

ObsidianColors serves as the single source of truth for Obsidian Horizon design system
tokens (brand identity, semantic feedback, and shared theme tokens).

Neutral surface and typography shades specific to the light theme are defined in theme.py
to provide optimal contrast on light surfaces. All tokens and neutral values are injected
into Flet's Material 3 ColorScheme so that UI components consume only Material 3 roles
(ft.Colors.*) and remain fully theme-adaptive without using raw hex values directly.

Mapping contract (dark → light):
  surface            = BG_DARK              → #F8F9FA
  on_surface         = TEXT_PRIMARY         → #1A1C1E
  on_surface_variant = TEXT_SECONDARY       → #5F6368  (darker grey for readability)
  surface_container  = SURFACE_DARK         → #ECEEF0
  surface_container_high = SURFACE_ELEVATED → #E6E8EA
  outline            = BORDER_DARK          → #72777F
  primary            = PRIMARY              → PRIMARY  (shared amber brand accent)
  on_primary         = ON_PRIMARY (BG_DARK) → #0F1117  (dark text on amber — 8.79:1)
  error              = ERROR                → ERROR
  on_error           = ON_ERROR (TEXT_PRIMARY) → #FFFFFF
"""

import flet as ft
from ui.design_system.colors import ObsidianColors


def get_dark_theme() -> ft.Theme:
    """
    Obsidian Horizon dark theme.
    Maps ObsidianColors tokens into Material 3 ColorScheme roles.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ObsidianColors.PRIMARY,
            on_primary=ObsidianColors.ON_PRIMARY,  # BG_DARK — 8.79:1 on PRIMARY
            surface=ObsidianColors.BG_DARK,
            on_surface=ObsidianColors.ON_SURFACE,  # TEXT_PRIMARY
            on_surface_variant=ObsidianColors.TEXT_SECONDARY,
            surface_container=ObsidianColors.SURFACE_DARK,
            surface_container_high=ObsidianColors.SURFACE_ELEVATED,
            error=ObsidianColors.ERROR,
            on_error=ObsidianColors.ON_ERROR,  # TEXT_PRIMARY
            outline=ObsidianColors.OUTLINE,  # BORDER_DARK
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def get_light_theme() -> ft.Theme:
    """
    Obsidian Horizon light theme.
    Preserves the amber brand identity on neutral MD3 light surfaces.
    Injects light-mode neutral values into the Material 3 ColorScheme.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ObsidianColors.PRIMARY,  # shared amber brand accent
            on_primary=ObsidianColors.ON_PRIMARY,  # #0F1117 — dark text on amber (8.79:1)
            surface="#F8F9FA",
            on_surface="#1A1C1E",
            on_surface_variant="#5F6368",  # secondary text — ~6:1 on light surface
            surface_container="#ECEEF0",
            surface_container_high="#E6E8EA",
            error=ObsidianColors.ERROR,
            on_error="#FFFFFF",
            outline="#72777F",
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


# Backward-compatibility alias
get_obsidian_theme = get_dark_theme
