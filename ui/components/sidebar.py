import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing

class Sidebar(ft.Container):
    """
    Rail de navigation latéral style Obsidian / Linear.
    """
    def __init__(self, selected_index: int = 0, on_change=None):
        self.on_change_callback = on_change
        self.selected_index = selected_index

        self.rail = ft.NavigationRail(
            selected_index=selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=72,
            min_extended_width=180,
            bgcolor=ObsidianColors.SURFACE_DARK,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIBRARY_MUSIC_OUTLINED,
                    selected_icon=ft.Icons.LIBRARY_MUSIC,
                    label="Bibliothèque",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.QUERY_STATS_OUTLINED,
                    selected_icon=ft.Icons.QUERY_STATS,
                    label="Télémétrie IA",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Réglages",
                ),
            ],
            on_change=self._on_nav_change,
        )

        super().__init__(
            content=self.rail,
            bgcolor=ObsidianColors.SURFACE_DARK,
            border=ft.Border.only(right=ft.BorderSide(1, ObsidianColors.BORDER_DARK)),
        )

    def _on_nav_change(self, e):
        self.selected_index = e.control.selected_index
        if self.on_change_callback:
            self.on_change_callback(self.selected_index)
