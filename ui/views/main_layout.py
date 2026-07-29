import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.components.header_bar import HeaderBar
from ui.components.sidebar import Sidebar
from ui.components.action_bar import ActionBar
from ui.views.library_view import LibraryView
from ui.views.ai_metrics_view import AIMetricsView
from ui.views.settings_view import SettingsView
from core.state import app_state


class MainLayout(ft.Column):
    """
    Layout principal Shell unifiant le Header, la Navigation Rails, le Workspace et la Bottom ActionBar.
    """

    def __init__(
        self,
        on_pick_files=None,
        on_pick_folder=None,
        on_like_track=None,
        on_delete_track=None,
        on_search=None,
        on_start_recommendation=None,
        on_reset=None,
        on_theme_toggle=None,
    ):
        self.header_bar = HeaderBar(on_theme_toggle=on_theme_toggle)
        self.sidebar = Sidebar(
            selected_index=0,
            on_change=self._on_navigation_change)

        self.library_view = LibraryView(
            on_pick_files=on_pick_files,
            on_pick_folder=on_pick_folder,
            on_like_track=on_like_track,
            on_delete_track=on_delete_track,
            on_search=on_search,
        )
        self.metrics_view = AIMetricsView()
        self.settings_view = SettingsView()

        # Workspace switcher Container
        self.workspace_container = ft.Container(
            content=self.library_view,
            expand=True,
            bgcolor=ObsidianColors.BG_DARK,
        )

        self.action_bar = ActionBar(
            on_start_recommendation=on_start_recommendation,
            on_reset=on_reset,
        )

        super().__init__(
            controls=[
                self.header_bar,
                ft.Row([
                    self.sidebar,
                    self.workspace_container,
                ], expand=True, spacing=0),
                self.action_bar,
            ],
            spacing=0,
            expand=True,
        )

    def _on_navigation_change(self, index: int):
        app_state.session.active_nav_index = index
        if index == 0:
            self.workspace_container.content = self.library_view
            self.library_view.refresh_tracks()
        elif index == 1:
            self.workspace_container.content = self.metrics_view
            self.metrics_view.refresh_metrics()
        elif index == 2:
            self.workspace_container.content = self.settings_view

        try:
            self.workspace_container.update()
        except RuntimeError:
            pass

    def update_all(self):
        self.header_bar.update_telemetry()
        self.library_view.refresh_tracks()
        self.action_bar.update_state()
