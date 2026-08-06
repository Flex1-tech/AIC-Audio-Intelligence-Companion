"""
test_font_view.py
-----------------
Vue de test visuelle pour la police Cinzel Decorative (Regular & Bold) à 72px.
Permet de confirmer sans ambiguïté le rendu des empattements décoratifs.
"""

import flet as ft
from ui.design_system.colors import ObsidianColors


def main(page: ft.Page):
    page.title = "AIC — Test de Police Cinzel Decorative"
    page.bgcolor = ObsidianColors.BG_DARK
    page.window.width = 900
    page.window.height = 600
    page.alignment = ft.Alignment.CENTER

    # Enregistrement des polices TTF pour Flutter Desktop
    page.fonts = {
        "Cinzel Decorative": "fonts/CinzelDecorative-Bold.ttf",
        "Cinzel Decorative Regular": "fonts/CinzelDecorative-Regular.ttf",
    }

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Cinzel Decorative — Audit Visuel",
                        size=20,
                        weight=ft.FontWeight.W_500,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                    ft.Container(height=30),
                    # Variante Regular (400)
                    ft.Text(
                        "AIC",
                        size=72,
                        color=ObsidianColors.PRIMARY,
                        font_family="Cinzel Decorative Regular",
                    ),
                    ft.Text(
                        "Cinzel Decorative Regular (72px)",
                        size=14,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                    ft.Container(height=30),
                    # Variante Bold (700)
                    ft.Text(
                        "AIC",
                        size=72,
                        weight=ft.FontWeight.BOLD,
                        color=ObsidianColors.TEXT_PRIMARY,
                        font_family="Cinzel Decorative",
                    ),
                    ft.Text(
                        "Cinzel Decorative Bold (72px)",
                        size=14,
                        color=ObsidianColors.TEXT_MUTED,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
