"""Design tokens — Obsidian Horizon colour palette for AIC."""


class ObsidianColors:
    # Backgrounds & surfaces
    BG_DARK = "#0F1117"  # Main app background
    SURFACE_DARK = "#161922"  # Card / container surface
    SURFACE_ELEVATED = "#1E2330"  # Elevated dialogs, badges
    SURFACE_HOVER = "#242A3A"  # Component hover state

    # Borders & dividers
    BORDER_DARK = "#2A3042"  # Subtle borders and dividers

    # Brand accent
    PRIMARY = "#F59E0B"  # Warm amber – primary action / brand
    PRIMARY_HOVER = "#D97706"  # Darker amber – hover on primary elements
    PRIMARY_LIGHT = "#FBBF24"  # Lighter amber – subtle highlights
    PRIMARY_GLOW = "#3D2B10"  # Subdued amber background (badge glow)

    # Semantic feedback
    SUCCESS = "#10B981"  # Emerald green – ready / validated
    SUCCESS_BG = "#064E3B"  # Success badge background
    INFO = "#3B82F6"  # Electric blue – informational state
    WARNING = PRIMARY  # No distinct warning state in UI – aliases PRIMARY (amber)
    WARNING_BG = PRIMARY_GLOW  # Warning badge background – aliases PRIMARY_GLOW
    ERROR = "#EF4444"  # Crimson red – error / destructive
    ERROR_BG = "#B91C1C"  # Dark crimson red – error toast background (7.55:1 AAA on TEXT_WHITE)

    # Typography
    TEXT_PRIMARY = "#F9FAFB"  # Warm white – headings, body text
    TEXT_SECONDARY = "#9CA3AF"  # Slate grey – subtitles
    TEXT_MUTED = "#6B7280"  # Steel grey – metadata, hints
    TEXT_DISABLED = "#4B5563"  # Disabled state
    TEXT_ON_PRIMARY = "#0F1117"  # Text on a primary-coloured surface (8.79:1 on PRIMARY)
    TEXT_WHITE = "#FFFFFF"  # Pure white – error toast text on ERROR bg (3.8:1)

    # Decorative icon colour
    HEART_RED = "#F43F5E"  # Liked-track heart icon

    # Material Design 3 semantic role aliases
    # These mirror ft.ColorScheme fields used in theme.py for readability and forward compatibility.
    ON_PRIMARY = BG_DARK  # M3 on_primary: text / icon on PRIMARY surface
    ON_SURFACE = TEXT_PRIMARY  # M3 on_surface: text / icon on any surface
    ON_ERROR = TEXT_PRIMARY  # M3 on_error: text / icon on ERROR surface
    OUTLINE = BORDER_DARK  # M3 outline: decorative border / divider
    SURFACE_CONTAINER = SURFACE_DARK  # M3 surface_container
    SURFACE_CONTAINER_HIGH = SURFACE_ELEVATED  # M3 surface_container_high
