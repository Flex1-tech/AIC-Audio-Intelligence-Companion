"""
ui/design_system/theme.py
--------------------------
Thèmes Light et Dark officiels pour AIC.
Source de vérité unique dérivée de l'identité visuelle du logo AIC (#FE8F40 Audio Amber & #30C4EF Tech Cyan).

Architecture Material 3 :
- primary        → #FE8F40 (Ambre Audio — actions, audio, génération)
- secondary      → #30C4EF (Cyan IA — navigation, intelligence, technologie)
- tertiary       → #10B981 (Émeraude — succès, états sains)
- primary_container   → fond adaptatif ambre (dark: #3E2412 / light: #FFDEB3)
- secondary_container → fond adaptatif cyan  (dark: #0B2F3B / light: #C5EDF9)
- tertiary_container  → fond adaptatif vert  (dark: #064E3B / light: #BBF7D0)

Comportement au démarrage :
- ThemeMode.DARK forcé pendant le Splash pour éliminer le flash.
- ThemeMode.SYSTEM restauré dans finish_splash() dans main.py.
- Le Design System fournit les deux thèmes ; aucune couleur n'est imposée en dehors des rôles de marque.
"""

import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii


def get_dark_theme() -> ft.Theme:
    """
    Obsidian Horizon dark theme — AIC brand identity.
    Injecte les tokens de marque (#FE8F40 Audio Amber / #30C4EF Tech Cyan)
    dans le ColorScheme Material 3 de Flet.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # ── Couleurs de marque primaires ──────────────────────────────────
            primary=ObsidianColors.PRIMARY,  # #FE8F40 Ambre Audio
            on_primary=ObsidianColors.ON_PRIMARY,  # #0F1117 texte sombre sur ambre
            primary_container=ObsidianColors.PRIMARY_GLOW,  # #3E2412 fond badge ambre
            on_primary_container=ObsidianColors.TEXT_PRIMARY,  # #F9FAFB texte sur fond ambre
            # ── Couleurs de marque secondaires (Cyan IA) ──────────────────────
            secondary=ObsidianColors.ACCENT_CYAN,  # #30C4EF Cyan Électrique IA
            on_secondary=ObsidianColors.BG_DARK,  # #0F1117 texte sombre sur cyan
            secondary_container=ObsidianColors.ACCENT_CYAN_GLOW,  # #0B2F3B fond badge cyan
            on_secondary_container=ObsidianColors.TEXT_PRIMARY,  # #F9FAFB texte sur fond cyan
            # ── Couleurs tertiaires (Succès/Sain) ─────────────────────────────
            tertiary=ObsidianColors.SUCCESS,  # #10B981 Émeraude
            tertiary_container=ObsidianColors.SUCCESS_BG,  # #064E3B fond badge succès
            on_tertiary_container=ObsidianColors.TEXT_PRIMARY,  # #F9FAFB texte sur fond succès
            # ── Surfaces Obsidian ──────────────────────────────────────────────
            surface=ObsidianColors.BG_DARK,  # #0F1117
            on_surface=ObsidianColors.ON_SURFACE,  # #F9FAFB
            on_surface_variant=ObsidianColors.TEXT_SECONDARY,  # #9CA3AF
            surface_container=ObsidianColors.SURFACE_DARK,  # #161922
            surface_container_high=ObsidianColors.SURFACE_ELEVATED,  # #1E2330
            # ── Sémantiques ───────────────────────────────────────────────────
            error=ObsidianColors.ERROR,
            on_error=ObsidianColors.ON_ERROR,
            outline=ObsidianColors.OUTLINE,  # #2A3042
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
        dialog_theme=ft.DialogTheme(
            bgcolor=ObsidianColors.SURFACE_ELEVATED,
            shadow_color="rgba(0, 0, 0, 0.60)",
            shape=ft.RoundedRectangleBorder(radius=Radii.MD),
        ),
        card_theme=ft.CardTheme(
            color=ObsidianColors.SURFACE_DARK,
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=Radii.MD),
        ),
    )


# ── Tokens Light — surfaces neutres MD3 avec identité de marque AIC préservée ──
_LIGHT_SURFACE = "#F8F9FA"
_LIGHT_ON_SURFACE = "#1A1C1E"
_LIGHT_ON_SURFACE_VARIANT = "#5F6368"  # ratio ~8.0:1 sur #F8F9FA — WCAG AAA
_LIGHT_SURFACE_CONTAINER = "#ECEEF0"
_LIGHT_SURFACE_CONTAINER_HIGH = "#E6E8EA"
_LIGHT_OUTLINE = "#72777F"
_LIGHT_DIALOG_BG = "#FFFFFF"
_LIGHT_ON_ERROR = "#FFFFFF"

# Conteneurs de marque adaptatifs Light ─────────────────────────────────────────
_LIGHT_PRIMARY_CONTAINER = "#FFDEB3"  # fond ambre léger sur surfaces claires
_LIGHT_ON_PRIMARY_CONTAINER = "#1A1C1E"  # texte sombre sur fond ambre léger
_LIGHT_SECONDARY_CONTAINER = "#C5EDF9"  # fond cyan léger
_LIGHT_ON_SECONDARY_CONTAINER = "#1A1C1E"  # texte sombre sur fond cyan léger
_LIGHT_TERTIARY_CONTAINER = "#BBF7D0"  # fond vert léger (success)
_LIGHT_ON_TERTIARY_CONTAINER = "#1A1C1E"  # texte sombre sur fond vert léger


def get_light_theme() -> ft.Theme:
    """
    Obsidian Horizon light theme — identité de marque AIC préservée.
    Surfaces neutres Material 3 clair avec Primary (#FE8F40) et Secondary (#30C4EF).
    Les conteneurs (primary_container, secondary_container, tertiary_container)
    sont des variantes claires des couleurs de marque pour une lisibilité optimale.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # ── Couleurs de marque primaires ──────────────────────────────────
            primary=ObsidianColors.PRIMARY,  # #FE8F40 Ambre — inchangé
            on_primary=ObsidianColors.ON_PRIMARY,  # #0F1117
            primary_container=_LIGHT_PRIMARY_CONTAINER,  # fond ambre léger
            on_primary_container=_LIGHT_ON_PRIMARY_CONTAINER,
            # ── Couleurs de marque secondaires (Cyan IA) ──────────────────────
            secondary=ObsidianColors.ACCENT_CYAN,  # #30C4EF — inchangé
            on_secondary=ObsidianColors.BG_DARK,  # #0F1117
            secondary_container=_LIGHT_SECONDARY_CONTAINER,
            on_secondary_container=_LIGHT_ON_SECONDARY_CONTAINER,
            # ── Couleurs tertiaires (Succès) ───────────────────────────────────
            tertiary=ObsidianColors.SUCCESS,
            tertiary_container=_LIGHT_TERTIARY_CONTAINER,
            on_tertiary_container=_LIGHT_ON_TERTIARY_CONTAINER,
            # ── Surfaces neutres M3 ────────────────────────────────────────────
            surface=_LIGHT_SURFACE,
            on_surface=_LIGHT_ON_SURFACE,
            on_surface_variant=_LIGHT_ON_SURFACE_VARIANT,
            surface_container=_LIGHT_SURFACE_CONTAINER,
            surface_container_high=_LIGHT_SURFACE_CONTAINER_HIGH,
            # ── Sémantiques ───────────────────────────────────────────────────
            error=ObsidianColors.ERROR,
            on_error=_LIGHT_ON_ERROR,
            outline=_LIGHT_OUTLINE,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
        dialog_theme=ft.DialogTheme(
            bgcolor=_LIGHT_DIALOG_BG,
            shadow_color="rgba(0, 0, 0, 0.20)",
            shape=ft.RoundedRectangleBorder(radius=Radii.MD),
        ),
    )


# Alias de rétrocompatibilité
get_obsidian_theme = get_dark_theme
