from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Theme data models (4.2)
# ---------------------------------------------------------------------------


class ThemeColors(BaseModel):
    primary: str
    secondary: str
    text: str
    textMuted: str
    error: str


class ThemeGradients(BaseModel):
    slide1: str
    slide2: str
    slide3: str


class ThemeFonts(BaseModel):
    heading: str
    body: str
    monospace: str


class ThemeSizes(BaseModel):
    titleHeading: str
    slideHeading: str
    sectionHeading: str
    body: str
    small: str


class ThemeSpacing(BaseModel):
    slidePadding: str
    elementMargin: str
    lineHeight: str


class Theme(BaseModel):
    name: str
    colors: ThemeColors
    gradients: ThemeGradients
    fonts: ThemeFonts
    sizes: ThemeSizes
    spacing: ThemeSpacing
    highlightTheme: str = "monokai"


# ---------------------------------------------------------------------------
# Theme registry — auto-discovered at import time (4.3)
# ---------------------------------------------------------------------------

try:
    _THEMES_DIR = Path(str(files("reveal_slides") / "themes"))
    CUSTOM_THEMES: set[str] = {
        p.stem for p in _THEMES_DIR.glob("*.json") if p.stem != "index"
    }
except Exception:
    CUSTOM_THEMES = {"tech-future", "corporate-blue"}

REVEAL_THEMES = {
    "black",
    "white",
    "league",
    "beige",
    "sky",
    "night",
    "serif",
    "simple",
    "solarized",
    "blood",
    "moon",
    "dracula",
}

ALLOWED_THEMES = REVEAL_THEMES | CUSTOM_THEMES
ALLOWED_TRANSITIONS = {"none", "fade", "slide", "convex", "concave", "zoom"}


# ---------------------------------------------------------------------------
# Slide models
# ---------------------------------------------------------------------------


class BaseSlide(BaseModel):
    transition: Optional[str] = Field(default=None, max_length=50)


class TitleSlide(BaseSlide):
    type: Literal["title"]
    title: str = Field(..., min_length=1, max_length=120)
    subtitle: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = Field(default=None, max_length=400)


class ContentSlide(BaseSlide):
    type: Literal["content"]
    title: str = Field(..., min_length=1, max_length=120)
    bullets: List[str] = Field(..., min_length=1, max_length=5)

    @field_validator("bullets")
    @classmethod
    def bullets_length(cls, value: List[str]) -> List[str]:
        for index, bullet in enumerate(value, start=1):
            if len(bullet) > 100:
                raise ValueError(
                    f"Bullet {index} exceeds 100 characters ({len(bullet)} chars)"
                )
        return value


class TwoColumnSlide(BaseSlide):
    type: Literal["two-column"]
    title: Optional[str] = Field(default=None, max_length=120)
    left_title: Optional[str] = Field(default=None, max_length=80)
    right_title: Optional[str] = Field(default=None, max_length=80)
    left: List[str] = Field(..., min_length=1, max_length=5)
    right: List[str] = Field(..., min_length=1, max_length=5)


class ImageSlide(BaseSlide):
    type: Literal["image"]
    side: Literal["left", "right"] = Field(default="right")
    title: Optional[str] = Field(default=None, max_length=120)
    image: str = Field(..., description="Path or URL to image")
    alt: Optional[str] = Field(default="", max_length=200)
    caption: Optional[str] = Field(default=None, max_length=200)
    bullets: Optional[List[str]] = Field(default=None, max_length=5)


class QuoteSlide(BaseSlide):
    type: Literal["quote"]
    quote: str = Field(..., min_length=1, max_length=400)
    attribution: Optional[str] = Field(default=None, max_length=120)


class CodeSlide(BaseSlide):
    type: Literal["code"]
    title: Optional[str] = Field(default=None, max_length=120)
    language: str = Field(..., min_length=1, max_length=30)
    code: str = Field(..., min_length=1)


class TableSlide(BaseSlide):
    type: Literal["table"]
    title: Optional[str] = Field(default=None, max_length=120)
    headers: List[str] = Field(..., min_length=1, max_length=8)
    rows: List[List[str]] = Field(..., min_length=1, max_length=10)


class SectionBreakSlide(BaseSlide):
    type: Literal["section-break"]
    title: str = Field(..., min_length=1, max_length=120)
    subtitle: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = Field(default=None, max_length=400)


class BlankSlide(BaseSlide):
    type: Literal["blank"]


Slide = Annotated[
    Union[
        TitleSlide,
        ContentSlide,
        TwoColumnSlide,
        ImageSlide,
        QuoteSlide,
        CodeSlide,
        TableSlide,
        SectionBreakSlide,
        BlankSlide,
    ],
    Field(discriminator="type"),
]


class Presentation(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, max_length=200)
    theme: str = Field(default="tech-future")
    transition: str = Field(default="slide")
    controls: bool = Field(default=True)
    progress: bool = Field(default=True)
    showSlideNumbers: bool = Field(default=False)
    custom_css: Optional[str] = Field(default=None)
    slides: List[Slide] = Field(..., min_length=1, max_length=50)

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, value: str) -> str:
        if value not in ALLOWED_THEMES:
            raise ValueError(
                f"Unknown theme '{value}'. "
                f"Custom themes: {sorted(CUSTOM_THEMES)}. "
                f"Reveal built-ins: {sorted(REVEAL_THEMES)}"
            )
        return value

    @field_validator("transition")
    @classmethod
    def validate_transition(cls, value: str) -> str:
        if value not in ALLOWED_TRANSITIONS:
            raise ValueError(
                f"Unknown transition '{value}'. Allowed: {sorted(ALLOWED_TRANSITIONS)}"
            )
        return value
