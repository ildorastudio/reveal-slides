from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import ValidationError

from reveal_slides.exceptions import InvalidInputError, ValidationFailedError
from reveal_slides.models import Presentation
from reveal_slides.models.presentation import CUSTOM_THEMES, Theme

_PACKAGE = files("reveal_slides")
TEMPLATES_DIR = Path(str(_PACKAGE / "templates"))
THEMES_DIR = Path(str(_PACKAGE / "themes"))

_REVEAL_DIST_SUBDIRS = ("dist", "plugin")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InvalidInputError(f"Invalid JSON in '{path}': {exc}") from exc
    except OSError as exc:
        raise InvalidInputError(f"Cannot read '{path}': {exc}") from exc


def parse_presentation(data: dict) -> Presentation:
    try:
        return Presentation.model_validate(data)
    except ValidationError as exc:
        raise ValidationFailedError(exc.errors()) from exc


def load_theme_data(theme: str) -> Theme | None:
    if theme not in CUSTOM_THEMES:
        return None
    theme_path = THEMES_DIR / f"{theme}.json"
    try:
        raw = json.loads(theme_path.read_text(encoding="utf-8"))
        return Theme.model_validate(raw)
    except ValidationError as exc:
        raise InvalidInputError(
            f"Theme file '{theme}.json' is invalid: {exc}"
        ) from exc


def build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(searchpath=TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(presentation: Presentation, asset_prefix: str, theme_data: Theme | None) -> str:
    env = build_env()
    template = env.get_template("base.html.j2")
    return template.render(
        presentation=presentation,
        asset_prefix=asset_prefix,
        theme_data=theme_data,
    )


def _copy_standalone_assets(vendor_dir: Path, output_folder: Path) -> None:
    reveal_src = vendor_dir / "reveal.js"
    reveal_dst = output_folder / "reveal.js"
    reveal_dst.mkdir(exist_ok=True)
    for subdir in _REVEAL_DIST_SUBDIRS:
        src = reveal_src / subdir
        dst = reveal_dst / subdir
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def generate(
    input_path: Path,
    output_dir: Path | None = None,
    vendor_dir: Path | None = None,
    standalone: bool = False,
    theme: str | None = None,
    dry_run: bool = False,
) -> Path:
    if vendor_dir is None:
        vendor_dir = Path(
            os.environ.get("REVEAL_SLIDES_VENDOR", Path.cwd() / "vendor")
        )
    if output_dir is None:
        output_dir = Path(
            os.environ.get("REVEAL_SLIDES_OUTPUT", Path.cwd() / "outputs")
        )

    data = load_json(input_path)
    if theme is not None:
        data = {**data, "theme": theme}
    presentation = parse_presentation(data)
    theme_data = load_theme_data(presentation.theme)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(presentation.title)
    output_folder = output_dir / f"{slug}-{timestamp}"

    if dry_run:
        return output_folder / f"{slug}.html"

    output_folder.mkdir(parents=True, exist_ok=True)

    json_output_path = output_folder / f"{slug}.json"
    json_output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if standalone:
        _copy_standalone_assets(vendor_dir, output_folder)
        asset_prefix = "./reveal.js"
    else:
        asset_prefix = Path(os.path.relpath(vendor_dir, start=output_folder)).as_posix()

    html_output_path = output_folder / f"{slug}.html"
    html = render(presentation, asset_prefix, theme_data)
    html_output_path.write_text(html, encoding="utf-8")
    return html_output_path
