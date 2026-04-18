from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .exceptions import InvalidInputError, ValidationFailedError
from .generator import generate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Reveal.js presentation from a JSON file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  reveal-slides examples/quarterly-review.json\n"
            "  python -m reveal_slides examples/quarterly-review.json\n"
            "  reveal-slides deck.json --standalone --output ./dist\n"
            "  reveal-slides deck.json --theme corporate-blue\n"
            "  reveal-slides deck.json --dry-run\n"
            "  reveal-slides new --list\n"
            "  reveal-slides new --template pitch-deck --out my-deck.json\n"
        ),
    )
    parser.add_argument(
        "json_path",
        type=Path,
        metavar="INPUT.JSON",
        help="Path to the presentation JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="DIR",
        help="Directory for generated output folders (default: ./outputs or $REVEAL_SLIDES_OUTPUT)",
    )
    parser.add_argument(
        "--vendor-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Path to vendor/ directory containing reveal.js (default: ./vendor or $REVEAL_SLIDES_VENDOR)",
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Copy reveal.js assets into the output folder so it can be shared without the vendor/ tree",
    )
    parser.add_argument(
        "--theme",
        default=None,
        metavar="THEME",
        help="Override the theme set in the JSON (e.g. corporate-blue, black)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the JSON and print the expected output path without writing any files",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Open the generated HTML in the default browser after generation",
    )
    return parser


def _cmd_new(argv: list[str]) -> None:
    import json
    from importlib.resources import files

    parser = argparse.ArgumentParser(
        prog="reveal-slides new",
        description="Create a new presentation JSON from a deck template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  reveal-slides new --list\n"
            "  reveal-slides new --template pitch-deck --out my-deck.json\n"
            "  reveal-slides new --template quarterly-review --title 'Q4 2026' --out q4.json\n"
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--template",
        metavar="NAME",
        help="Deck template name (use --list to see options)",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="List available deck templates",
    )
    parser.add_argument(
        "--out",
        type=Path,
        metavar="FILE",
        help="Output JSON path (default: <template-name>.json)",
    )
    parser.add_argument("--title", default="My Presentation", help="Presentation title")
    parser.add_argument("--author", default="", help="Author name")
    parser.add_argument("--date", default=str(date.today()), help="Date string")
    args = parser.parse_args(argv)

    from reveal_slides import __name__ as _pkg  # noqa: F401

    deck_templates_dir = Path(str(files("reveal_slides") / "deck_templates"))
    index_path = deck_templates_dir / "index.json"
    catalog = json.loads(index_path.read_text(encoding="utf-8"))

    if args.list:
        print("Available deck templates:")
        for entry in catalog:
            print(f"  {entry['name']:<22}{entry['description']}")
        raise SystemExit(0)

    template_entry = next((e for e in catalog if e["name"] == args.template), None)
    if template_entry is None:
        names = [e["name"] for e in catalog]
        print(
            f"ERROR: Unknown template '{args.template}'. Available: {names}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    template_path = deck_templates_dir / template_entry["file"]
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{{ title }}", args.title)
    content = content.replace("{{ author }}", args.author)
    content = content.replace("{{ date }}", args.date)

    out_path = args.out or Path(f"{args.template}.json")
    if out_path.exists():
        print(
            f"ERROR: '{out_path}' already exists. Choose a different --out path.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    out_path.write_text(content, encoding="utf-8")
    print(str(out_path))
    raise SystemExit(0)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "new":
        _cmd_new(sys.argv[2:])
        return

    parser = build_parser()
    args = parser.parse_args()

    if not args.json_path.exists():
        print(f"ERROR: File not found: '{args.json_path}'", file=sys.stderr)
        raise SystemExit(1)

    try:
        output = generate(
            args.json_path,
            output_dir=args.output,
            vendor_dir=args.vendor_dir,
            standalone=args.standalone,
            theme=args.theme,
            dry_run=args.dry_run,
        )
    except InvalidInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except ValidationFailedError as exc:
        print("ERROR: Input validation failed:", file=sys.stderr)
        for err in exc.errors:
            loc = " -> ".join(str(part) for part in err["loc"])
            print(f"  [{loc}] {err['msg']}", file=sys.stderr)
        raise SystemExit(1)

    print(str(output))

    if args.open_browser and not args.dry_run:
        import webbrowser
        webbrowser.open(output.resolve().as_uri())

    raise SystemExit(0)
