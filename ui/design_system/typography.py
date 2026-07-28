"""
Design Tokens - Hiérarchie typographique pour AIC.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class TypographyStyle:
    size: int
    weight: str = "normal"  # "normal", "bold", "w500", "w600", "w700"
    family: str = "System"

class Typography:
    APP_TITLE = TypographyStyle(size=20, weight="bold")
    SECTION_HEADER = TypographyStyle(size=16, weight="w600")
    SUBTITLE = TypographyStyle(size=13, weight="w500")
    BODY = TypographyStyle(size=14, weight="normal")
    CAPTION = TypographyStyle(size=12, weight="normal")
    MONO = TypographyStyle(size=11, weight="normal", family="monospace")
