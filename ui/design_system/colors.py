"""
Design Tokens - Palette de couleurs Obsidian Horizon pour AIC.
Inspirée par Linear, Obsidian et Raycast.

Source de vérité unique pour toutes les couleurs du projet.
"""

import flet as ft


class ObsidianColors:
    # ── 1. Arrière-plans & Surfaces (Backgrounds & Surfaces) ────────────────
    BG_DARK = "#0F1117"  # Deep Obsidian (Arrière-plan principal)
    SURFACE_DARK = "#161922"  # Card Surface (Cartes, containers)
    SURFACE_ELEVATED = "#1E2330"  # Elevated Container / Dialog / Badges
    SURFACE_HOVER = "#242A3A"  # Component Hover State

    # ── 2. Frontières & Séparateurs (Borders & Dividers) ────────────────────
    BORDER_DARK = "#2A3042"  # Subtle Borders & Dividers

    # ── 3. Accents & Identité de Marque (Brand & Accents) ───────────────────
    PRIMARY = "#F59E0B"  # Refined Warm Amber / Gold
    PRIMARY_HOVER = "#D97706"  # Deep Amber Hover
    PRIMARY_LIGHT = "#FBBF24"  # Soft Amber Accent
    PRIMARY_GLOW = "#3D2B10"  # Subdued Glow Background

    # ── 4. États & Feedback (Status & Feedback) ─────────────────────────────
    SUCCESS = "#10B981"  # Emerald Green (ONNX Ready, Validated)
    SUCCESS_BG = "#064E3B"  # Success Pill BG
    WARNING = "#3B82F6"  # Electric Blue (Info, Recommending)
    WARNING_BG = "#1E3A8A"  # Warning Pill BG
    ERROR = "#EF4444"  # Crimson Red (Error, Delete)
    ERROR_BG = "#7F1D1D"  # Error Pill BG
    INFO = "#3B82F6"  # Information Accent

    # ── 5. Typographie & Icônes (Typography & Icons) ─────────────────────────
    TEXT_PRIMARY = "#F9FAFB"  # Pure Warm White (Titre, texte principal)
    TEXT_SECONDARY = "#9CA3AF"  # Slate Gray (Sous-titres, texte secondaire)
    TEXT_MUTED = "#6B7280"  # Darker Muted Steel (Métadonnées, hints)
    TEXT_DISABLED = "#4B5563"  # Disabled State Gray
    TEXT_ON_PRIMARY = "#0F1117"  # High contrast text on primary buttons
    TEXT_WHITE = "#FFFFFF"  # Pure White (Toasts / Overlays)
    HEART_RED = "#F43F5E"  # Liked Heart Red Icon

    # ── 6. Alias Flet & Composants (Flet & Component Mapping) ──────────────
    ON_PRIMARY = BG_DARK
    ON_SURFACE = TEXT_PRIMARY
    SURFACE_CONTAINER = SURFACE_DARK
    SURFACE_CONTAINER_HIGH = SURFACE_ELEVATED
    ON_ERROR = TEXT_PRIMARY
    OUTLINE = BORDER_DARK

    # Alias explicites des couleurs Flet communes pour l'application
    FLET_TRANSPARENT = ft.Colors.TRANSPARENT
