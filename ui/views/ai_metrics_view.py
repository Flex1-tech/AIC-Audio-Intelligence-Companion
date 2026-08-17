import flet as ft
from ui.design_system.colors import ObsidianColors
from ui.design_system.spacing import Radii, Spacing
from core.state import app_state


class AIMetricsView(ft.Container):
    """
    Vue Télémétrie IA et Moteur Vectoriel LanceDB.
    """

    def __init__(self):
        self.log_list = ft.ListView(
            expand=True,
            spacing=6,
        )
        self.clipboard = ft.Clipboard()

        super().__init__(
            content=ft.Column(
                [
                    ft.Text(
                        "Télémétrie & Santé du Moteur IA",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        # no explicit color — inherits on_surface
                    ),
                    ft.Text(
                        "Supervision en temps réel des modèles Deep Learning et du cache vectoriel.",
                        size=13,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                    ft.Container(height=10),
                    # Metric Cards Grid
                    ft.Row(
                        [
                            self._build_card(
                                "Modèle ONNX",
                                "MusiCNN (16kHz)",
                                ft.Icons.AUTO_AWESOME,
                                ObsidianColors.SUCCESS,
                            ),
                            self._build_card(
                                "Base Vectorielle",
                                "LanceDB Active",
                                ft.Icons.STORAGE,
                                ObsidianColors.PRIMARY,
                            ),
                            self._build_card(
                                "Embeddings en Cache",
                                f"{app_state.total_embeddings_in_db} morceaux",
                                ft.Icons.GRID_VIEW,
                                ObsidianColors.INFO,
                            ),
                        ],
                        spacing=Spacing.MD,
                    ),
                    ft.Container(height=15),
                    # Header du journal avec bouton copier
                    ft.Row(
                        [
                            ft.Text(
                                "Journal des Événements du Moteur",
                                size=15,
                                weight=ft.FontWeight.W_600,
                                # no explicit color — inherits on_surface
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY,
                                icon_size=16,
                                tooltip="Copier les journaux",
                                mouse_cursor=ft.MouseCursor.CLICK,
                                on_click=self._handle_copy_logs,
                                # no icon_color — inherits on_surface_variant
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Action Logs List
                    self.log_list,
                ],
                spacing=Spacing.MD,
                expand=True,
            ),
            padding=Spacing.LG,
            expand=True,
        )
        self.refresh_metrics()

    def _handle_copy_logs(self, e: ft.ControlEvent) -> None:
        """Copie l'historique des journaux d'événements du moteur dans le presse-papier."""
        if not app_state.action_history:
            return

        logs_text = "\n".join(
            f"[{log.formatted_time}] [{log.action_type}] {log.description}"
            for log in reversed(app_state.action_history)
        )

        page = e.page or self.page
        if not page:
            return

        if self.clipboard not in page.services:
            page.services.append(self.clipboard)

            try:
                page.update()
            except Exception:
                pass

        async def _copy_and_toast() -> None:
            await self.clipboard.set(logs_text)
            snack = ft.SnackBar(
                content=ft.Text("Journaux copiés dans le presse-papier !", color=ObsidianColors.BG_DARK),
                bgcolor=ObsidianColors.PRIMARY,
                duration=3000,
                show_close_icon=True,
                close_icon_color=ObsidianColors.BG_DARK,
            )
            page.overlay.clear()
            page.overlay.append(snack)
            snack.open = True
            try:
                page.update()
            except Exception:
                pass

        page.run_task(_copy_and_toast)

    def _build_card(self, title: str, value: str, icon: "ft.IconData", accent_color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, size=20, color=accent_color),  # semantic colour — explicit
                            ft.Text(title, size=12, color=ObsidianColors.TEXT_MUTED),  # 3rd-level — explicit
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        # no explicit color — inherits on_surface
                    ),
                ],
                spacing=6,
            ),
            padding=Spacing.MD,
            border_radius=Radii.MD,
            bgcolor=ft.Colors.SURFACE_CONTAINER,  # = SURFACE_DARK via ColorScheme
            border=ft.Border.all(1, ft.Colors.OUTLINE),  # = BORDER_DARK via ColorScheme
            expand=True,
        )

    def refresh_metrics(self):
        self.log_list.controls.clear()
        for log in reversed(app_state.action_history[-20:]):
            self.log_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                log.formatted_time,
                                size=11,
                                font_family="monospace",
                                color=ObsidianColors.TEXT_MUTED,
                            ),
                            ft.Text(
                                log.action_type,
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=ObsidianColors.PRIMARY,  # brand accent — explicit
                            ),
                            ft.Text(
                                log.description,
                                size=12,
                                # no explicit color — inherits on_surface
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=8,
                    border_radius=Radii.SM,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                )
            )
        try:
            self.update()
        except RuntimeError:
            pass
