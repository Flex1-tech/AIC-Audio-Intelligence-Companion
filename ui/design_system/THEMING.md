# AIC Theming System

## Overview

AIC uses a **dual-theme architecture** built on Flet's `page.theme` / `page.dark_theme` duality
and the Material Design 3 `ColorScheme`.

- **`ObsidianColors`** is the single source of truth for **Obsidian Horizon design system tokens**
  (brand identity: **Audio Amber `#FE8F40`** & **Tech Cyan `#30C4EF`**, semantic feedback, and shared theme tokens).
- Neutral surface and typography shades specific to the light theme are defined in `theme.py` for
  optimal light-mode contrast.
- Adaptive container roles (`primary_container`, `secondary_container`, `tertiary_container`) automatically adjust
  badge backgrounds and navigation highlights for both Dark and Light modes.
- Both token sets are injected into Flet's Material 3 `ColorScheme` in `theme.py`.
- UI components reference M3 semantic roles (`ft.Colors.SURFACE_CONTAINER`, `ft.Colors.OUTLINE`, `ft.Colors.ON_SURFACE_VARIANT`, etc.)
  so they adapt automatically when switching between dark and light themes without using raw hex values directly.

---

## Architecture

```
ObsidianColors (Design Tokens)  ──┐
                                  ├──► theme.py ColorScheme ──► ft.Colors.* (UI Components)
Light Mode Neutrals (theme.py) ──┘
```

### Theme slots

| Slot | Function | Assigned in `main.py` |
|------|----------|-----------------------|
| `page.theme` | Active when `ThemeMode.LIGHT` | `get_light_theme()` |
| `page.dark_theme` | Active when `ThemeMode.DARK` | `get_dark_theme()` |

---

## ColorScheme Mapping

| M3 Role | Dark value (`ObsidianColors`) | Light value (`theme.py`) |
|---------|-------------------------------|---------------------------|
| `surface` | `BG_DARK` `#0F1117` | `#F8F9FA` |
| `on_surface` | `TEXT_PRIMARY` `#F9FAFB` | `#1A1C1E` |
| `on_surface_variant` | `TEXT_SECONDARY` `#9CA3AF` | `#5F6368` (WCAG AAA) |
| `surface_container` | `SURFACE_DARK` `#161922` | `#ECEEF0` |
| `surface_container_high` | `SURFACE_ELEVATED` `#1E2330` | `#E6E8EA` |
| `outline` | `BORDER_DARK` `#2A3042` | `#72777F` |
| `primary` | `PRIMARY` `#FE8F40` | `PRIMARY` `#FE8F40` |
| `on_primary` | `ON_PRIMARY` `#0F1117` | `#0F1117` |
| `primary_container` | `PRIMARY_GLOW` `#3E2412` | `#FFDEB3` |
| `on_primary_container` | `#F9FAFB` | `#1A1C1E` |
| `secondary` | `ACCENT_CYAN` `#30C4EF` | `ACCENT_CYAN` `#30C4EF` |
| `on_secondary` | `#0F1117` | `#0F1117` |
| `secondary_container` | `ACCENT_CYAN_GLOW` `#0B2F3B` | `#C5EDF9` |
| `on_secondary_container` | `#F9FAFB` | `#1A1C1E` |
| `tertiary` | `SUCCESS` `#10B981` | `SUCCESS` `#10B981` |
| `tertiary_container` | `SUCCESS_BG` `#064E3B` | `#BBF7D0` |
| `on_tertiary_container` | `#F9FAFB` | `#1A1C1E` |
| `error` | `ERROR` `#EF4444` | `ERROR` `#EF4444` |
| `on_error` | `#F9FAFB` | `#FFFFFF` |

---

## Token Usage Rules

### ✅ Use `ft.Colors.*` (via ColorScheme) for

- Container backgrounds: `ft.Colors.SURFACE_CONTAINER`, `ft.Colors.SURFACE_CONTAINER_HIGH`
- Adaptive Badge backgrounds: `ft.Colors.PRIMARY_CONTAINER`, `ft.Colors.SECONDARY_CONTAINER`, `ft.Colors.TERTIARY_CONTAINER`
- Border / divider colours: `ft.Colors.OUTLINE`
- Primary text: no explicit `color` (inherits `on_surface` automatically)
- Secondary & Metadata text: `ft.Colors.ON_SURFACE_VARIANT` (guarantees WCAG AAA contrast in both Dark and Light modes)

### ✅ Keep `ObsidianColors.*` explicit for

- Brand accents: `ObsidianColors.PRIMARY` (#FE8F40 Audio Amber), `ObsidianColors.ACCENT_CYAN` (#30C4EF Tech Cyan)
- Semantic feedback: `ObsidianColors.SUCCESS`, `ObsidianColors.ERROR`
- Disabled states: `ObsidianColors.TEXT_DISABLED`
- Decorative colours: `ObsidianColors.HEART_RED`
- Error toast backgrounds: `ObsidianColors.ERROR_BG`

---

## Brand Color Roles

| Brand Color | Hex Code | Visual Role | Applied Elements |
|-------------|----------|-------------|------------------|
| **CYAN** | `#30C4EF` | Intelligence, AI, System, Structure, Active Navigation, Tech Metrics | NavigationRail indicator, ONNX & LanceDB icons, AI Metric Cards, Log tags, Logo Structure |
| **AMBER** | `#FE8F40` | Audio, Signal, Waveform, Playback, Generation, Main Actions | "Générer la Playlist" button, MMR Slider, Audio track controls, File import, Audio waveform |

---

## Theme Toggle

The toggle in `HeaderBar` calls `handle_theme_toggle` in `main.py`:

```python
def handle_theme_toggle(_e) -> None:
    current_mode = page.theme_mode
    new_mode = ft.ThemeMode.LIGHT if current_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
    page.theme_mode = new_mode
    page.bgcolor = ft.Colors.SURFACE
    app_state.session.theme_mode = "light" if new_mode == ft.ThemeMode.LIGHT else "dark"
    page.update()
```

Widgets using `ft.Colors.*` roles update automatically. Widgets with explicit `ObsidianColors.*`
brand values retain their strong identity while container backgrounds adapt seamlessly.
