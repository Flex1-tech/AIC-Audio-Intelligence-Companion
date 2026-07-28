import flet as ft
from ui.design_system.colors import ObsidianColors

def get_obsidian_theme() -> ft.Theme:
    """
    Construit le thème Flet global Obsidian Dark.
    """
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            background=ObsidianColors.BG_DARK,
            surface=ObsidianColors.SURFACE_DARK,
            primary=ObsidianColors.PRIMARY,
            on_primary=ObsidianColors.BG_DARK,
            on_surface=ObsidianColors.TEXT_PRIMARY,
            on_background=ObsidianColors.TEXT_PRIMARY,
            error=ObsidianColors.ERROR,
            outline=ObsidianColors.BORDER_DARK,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
