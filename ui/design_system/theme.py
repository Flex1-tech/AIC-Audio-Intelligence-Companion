import flet as ft
from ui.design_system.colors import ObsidianColors

def get_obsidian_theme() -> ft.Theme:
    """
    Construit le thème Flet global Obsidian Dark compatible avec Flet v0.86+.

    Note : `ColorScheme` en v0.86+ ne supporte plus `background` ni `on_background`.
    Le mapping correct est : background -> surface, on_background -> on_surface.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ObsidianColors.PRIMARY,
            on_primary=ObsidianColors.BG_DARK,
            surface=ObsidianColors.BG_DARK,
            on_surface=ObsidianColors.TEXT_PRIMARY,
            surface_container=ObsidianColors.SURFACE_DARK,
            surface_container_high=ObsidianColors.SURFACE_ELEVATED,
            error=ObsidianColors.ERROR,
            on_error=ObsidianColors.TEXT_PRIMARY,
            outline=ObsidianColors.BORDER_DARK,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
