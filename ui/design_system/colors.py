"""
Design tokens — AIC / Obsidian Horizon official color palette.
Source de vérité unique dérivée de l'identité visuelle officielle du logo AIC.

Identité graphique AIC :
- Brand Primary (Audio Resonance / Onde) : #FE8F40 (Orange Solaire / Ambre chaud)
- Brand Accent (Intelligence IA / Structure) : #30C4EF (Cyan Électrique / Bleu Tech)
- Deep Space Surfaces (Studio Offline)      : #0F1117 / #161922 / #1E2330
"""


class ObsidianColors:
    # ── Backgrounds & surfaces (Obsidian Dark Space) ──────────────────────────
    BG_DARK = "#0F1117"  # Fond principal de l'application
    SURFACE_DARK = "#161922"  # Surface des cartes et conteneurs
    SURFACE_ELEVATED = "#1E2330"  # Dialogs, popovers, badges élevés
    SURFACE_HOVER = "#242A3A"  # État survolé (hover) des items

    # ── Bordures & séparateurs ────────────────────────────────────────────────
    BORDER_DARK = "#2A3042"  # Lignes de séparation et bordures subtiles

    # ── Identité de marque AIC — Primary Accent (Audio / Onde : #FE8F40) ──────
    PRIMARY = "#FE8F40"  # Ambre Audio Solaire — Action principale / Onde
    PRIMARY_HOVER = "#E57A2C"  # Survol ambre
    PRIMARY_LIGHT = "#FFB27D"  # Surbrillance claire ambre
    PRIMARY_GLOW = "#3E2412"  # Fond de badge ambre

    # ── Identité de marque AIC — Secondary Accent (IA / Cyan : #30C4EF) ────────
    ACCENT_CYAN = "#30C4EF"  # Cyan Électrique IA — Métriques / Intelligence
    ACCENT_CYAN_HOVER = "#1EB2DD"  # Survol cyan
    ACCENT_CYAN_LIGHT = "#8FE2F7"  # Surbrillance cyan
    ACCENT_CYAN_GLOW = "#0B2F3B"  # Fond de badge cyan

    # Alias rétrocompatible & sémantique
    SECONDARY = ACCENT_CYAN

    # ── Retours sémantiques ───────────────────────────────────────────────────
    SUCCESS = "#10B981"  # Émeraude — prêt / validé
    SUCCESS_BG = "#064E3B"  # Fond de badge success
    INFO = ACCENT_CYAN  # Cyan électrique — notifications d'information
    WARNING = PRIMARY  # Ambre solaire — alerte
    WARNING_BG = PRIMARY_GLOW  # Fond d'alerte ambre
    ERROR = "#EF4444"  # Rouge éco-système — erreur / destructif
    ERROR_BG = "#B91C1C"  # Fond de toast d'erreur

    # ── Typographie ───────────────────────────────────────────────────────────
    TEXT_PRIMARY = "#F9FAFB"  # Blanc chaud à fort contraste
    TEXT_SECONDARY = "#9CA3AF"  # Gris ardoise (sous-titres)
    TEXT_MUTED = "#6B7280"  # Gris acier (métadonnées)
    TEXT_DISABLED = "#4B5563"  # État désactivé
    TEXT_ON_PRIMARY = "#0F1117"  # Texte sombre sur fond ambre (8.79:1)
    TEXT_WHITE = "#FFFFFF"  # Blanc pur (toasts et contrastes élevés)

    # ── Éléments décoratifs ───────────────────────────────────────────────────
    HEART_RED = "#F43F5E"  # Icône de morceau liké

    # ── Aliases Material Design 3 (Mapping Theme Flet) ────────────────────────
    ON_PRIMARY = BG_DARK
    ON_SURFACE = TEXT_PRIMARY
    ON_ERROR = TEXT_PRIMARY
    OUTLINE = BORDER_DARK
    SURFACE_CONTAINER = SURFACE_DARK
    SURFACE_CONTAINER_HIGH = SURFACE_ELEVATED
