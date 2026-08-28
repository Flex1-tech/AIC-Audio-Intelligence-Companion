"""
ui/design_system/motion.py
---------------------------
Design Tokens - Animation & Motion config pour AIC.
Centralise les durées, les courbes d'accélération (easings) et les délais de transition.
"""

import flet as ft


class Motion:
    # Durées standards (en millisecondes)
    INSTANT = 50
    FAST = 150
    NORMAL = 300
    SLOW = 500
    SPLASH_TOTAL = 5000

    # Courbes d'animation Flet (M3 Standard Easings)
    EASING_STANDARD = ft.AnimationCurve.EASE_IN_OUT
    EASING_DECELERATE = ft.AnimationCurve.DECELERATE
    EASING_ACCELERATE = ft.AnimationCurve.EASE_IN
    EASING_BOUNCE = ft.AnimationCurve.BOUNCE_OUT

    # Configurations d'animation réutilisables pour ft.Container.animate
    ANIMATE_FAST = ft.Animation(FAST, EASING_STANDARD)
    ANIMATE_NORMAL = ft.Animation(NORMAL, EASING_STANDARD)
    ANIMATE_SLOW = ft.Animation(SLOW, EASING_DECELERATE)
