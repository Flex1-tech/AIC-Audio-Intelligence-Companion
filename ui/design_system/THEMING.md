# AIC Theming System

## Overview

AIC uses a **dual-theme architecture** built on Flet's `page.theme` / `page.dark_theme` duality
and the Material Design 3 `ColorScheme`. The `ObsidianColors` class remains the **single source
of truth** for all colour values. Widgets reference M3 semantic roles (`ft.Colors.SURFACE_CONTAINER`,
etc.) rather than raw hex values, but those roles are always configured via `ColorScheme` using
`ObsidianColors` tokens.

---

## Architecture

```
ObsidianColors        ← single source of truth for all hex values
       │
       ▼
theme.py ColorScheme  ← maps design tokens to M3 roles (per theme)
       │
       ▼
ft.Colors.*           ← used by widgets to reference roles adaptively
```

### Theme slots

| Slot | Function | Assigned in `main.py` |
|------|----------|-----------------------|
| `page.theme` | Active when `ThemeMode.LIGHT` | `get_light_theme()` |
| `page.dark_theme` | Active when `ThemeMode.DARK` | `get_dark_theme()` |

---

## ColorScheme Mapping

| M3 Role | Dark value (`ObsidianColors`) | Light value |
|---------|-------------------------------|-------------|
| `surface` | `BG_DARK` `#0F1117` | `#F8F9FA` |
| `on_surface` | `ON_SURFACE` / `TEXT_PRIMARY` `#F9FAFB` | `#1A1C1E` |
| `on_surface_variant` | `TEXT_SECONDARY` `#9CA3AF` | `#5F6368` |
| `surface_container` | `SURFACE_DARK` `#161922` | `#ECEEF0` |
| `surface_container_high` | `SURFACE_ELEVATED` `#1E2330` | `#E6E8EA` |
| `outline` | `OUTLINE` / `BORDER_DARK` `#2A3042` | `#72777F` |
| `primary` | `PRIMARY` `#F59E0B` | `PRIMARY` `#F59E0B` |
| `on_primary` | `ON_PRIMARY` / `BG_DARK` `#0F1117` | `#0F1117` |
| `error` | `ERROR` `#EF4444` | `ERROR` `#EF4444` |
| `on_error` | `ON_ERROR` / `TEXT_PRIMARY` `#F9FAFB` | `#FFFFFF` |

---

## Token Usage Rules

### ✅ Use `ft.Colors.*` (via ColorScheme) for

- Container backgrounds: `ft.Colors.SURFACE_CONTAINER`, `ft.Colors.SURFACE_CONTAINER_HIGH`
- Border / divider colours: `ft.Colors.OUTLINE`
- Primary text: no explicit `color` (inherits `on_surface` automatically)
- Secondary text: `ft.Colors.ON_SURFACE_VARIANT`

### ✅ Keep `ObsidianColors.*` explicit for

- Brand accents: `ObsidianColors.PRIMARY`, `ObsidianColors.ON_PRIMARY`
- Semantic feedback: `ObsidianColors.SUCCESS`, `ObsidianColors.ERROR`, `ObsidianColors.INFO`
- Badge backgrounds: `ObsidianColors.SUCCESS_BG`, `ObsidianColors.PRIMARY_GLOW`
- Typographic hierarchy tier 3: `ObsidianColors.TEXT_MUTED`
- Disabled states: `ObsidianColors.TEXT_DISABLED`
- Decorative colours: `ObsidianColors.HEART_RED`
- Specific contrast scenarios: `ObsidianColors.TEXT_WHITE` (on ERROR)

---

## Adding New Semantic Colours

1. Add the token to `ObsidianColors` in `colors.py` with a clear comment.
2. If the colour maps to a standard M3 role, add it to **both** `get_dark_theme()` and
   `get_light_theme()` in `theme.py`.
3. Update the mapping table above.
4. In widgets, reference `ft.Colors.<ROLE>` rather than the raw token.

If no M3 role exists, keep the token explicit in widgets.

---

## Creating Theme-Aware Widgets

```python
# Good — adapts automatically
ft.Container(
    bgcolor=ft.Colors.SURFACE_CONTAINER,
    border=ft.Border.all(1, ft.Colors.OUTLINE),
    content=ft.Text("Hello"),  # inherits on_surface
)

# Bad — frozen to dark palette
ft.Container(
    bgcolor=ObsidianColors.SURFACE_DARK,   # ← hardcoded
    border=ft.Border.all(1, ObsidianColors.BORDER_DARK),
    content=ft.Text("Hello", color=ObsidianColors.TEXT_PRIMARY),
)
```

For brand/semantic colours that must stay explicit:

```python
ft.Text("Status", color=ObsidianColors.SUCCESS)     # OK — semantic, no M3 equivalent
ft.Text("Primary", color=ObsidianColors.PRIMARY)    # OK — brand identity
ft.Text("Muted", color=ObsidianColors.TEXT_MUTED)   # OK — 3rd-level hierarchy, no M3 equivalent
```

---

## Common Mistakes to Avoid

| Mistake | Why it breaks | Fix |
|---------|--------------|-----|
| Using `ft.Colors.SURFACE_CONTAINER` without configuring `ColorScheme.surface_container` | Falls back to Material default palette, bypasses design system | Always configure the role in both themes |
| Removing `ObsidianColors.PRIMARY` on interactive elements | Flet's default primary may differ | Keep explicit on brand elements |
| Removing `TEXT_MUTED` color | No M3 equivalent — text becomes `on_surface` (too prominent) | Keep explicit |
| Setting `bgcolor` on `NavigationRail` | Disables native adaptive behaviour | Omit `bgcolor`; the rail adapts automatically |
| Setting `border_color` on `TextField` | Locks to a single theme | Omit it; Flet uses `outline` from `ColorScheme` |
| Using `BG_DARK` for button text instead of `ON_PRIMARY` | Semantically incorrect (coincidentally equal in dark mode, may diverge) | Use `ObsidianColors.ON_PRIMARY` |

---

## Theme Toggle

The toggle in `HeaderBar` calls `handle_theme_toggle` in `main.py`:

```python
def handle_theme_toggle(_e) -> None:
    page.theme_mode = (
        ft.ThemeMode.LIGHT
        if page.theme_mode == ft.ThemeMode.DARK
        else ft.ThemeMode.DARK
    )
    page.update()
```

This is sufficient because both `page.theme` and `page.dark_theme` are now populated.
Widgets using `ft.Colors.*` roles update automatically. Widgets with explicit `ObsidianColors.*`
values (brand/semantic tokens) are intentionally theme-invariant.
