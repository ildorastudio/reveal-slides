# Usage Guide

## Primary flow

The Python CLI is the product. High-level flow:

1. Python reads a presentation JSON file.
2. Pydantic validates the input.
3. Jinja renders the HTML deck.
4. The generated HTML loads local `reveal.js` assets from `vendor/reveal.js/`.

`reveal.js` is not a Python dependency. It is a browser-side runtime used by the generated HTML.

## Generate a presentation

From the repo root (installed via `pip install -e .`):

```bash
reveal-slides examples/quarterly-review.json
```

Or without installing:

```bash
python -m reveal_slides examples/quarterly-review.json
```

The command prints the generated HTML path to stdout.

## CLI reference

```
reveal-slides INPUT.JSON [options]

Options:
  --output DIR        Directory for output folders (default: ./outputs)
  --vendor-dir DIR    Path to vendor/ with reveal.js (default: ./vendor)
  --standalone        Copy reveal.js into the output folder for sharing
  --theme THEME       Override the theme set in the JSON
  --dry-run           Validate JSON and print expected output path; write nothing
  --open              Open the generated HTML in the default browser
```

### Subcommand: new

Create a new presentation JSON from a curated deck template:

```bash
reveal-slides new --list
reveal-slides new --template pitch-deck --out my-deck.json
reveal-slides new --template quarterly-review --title "Q4 2026" --out q4.json
```

Supported options: `--template NAME`, `--list`, `--out FILE`, `--title`, `--author`, `--date`.

## Output structure

Each generation creates a topic-and-timestamp folder under `outputs/`:

```text
outputs/
└── q3-business-review-20260416-202025/
    ├── q3-business-review.json
    └── q3-business-review.html
```

The source JSON and generated HTML are kept together.

## Packaging-aware layout

```text
reveal-slides/
├── src/
│   └── reveal_slides/
│       ├── cli.py
│       ├── generator.py
│       ├── models/
│       ├── templates/         ← Jinja templates (base + per-slide-type)
│       │   ├── partials/      ← shared Jinja partials
│       │   ├── css/
│       │   └── slides/
│       ├── themes/            ← custom theme JSON files
│       └── deck_templates/    ← deck skeleton JSON files
├── examples/
├── vendor/
│   └── reveal.js/
├── outputs/
└── docs/
```

## Folder responsibilities

- `src/reveal_slides/`: Python application code
- `src/reveal_slides/templates/`: Jinja templates for deck rendering
- `src/reveal_slides/themes/`: custom theme JSON definitions
- `src/reveal_slides/deck_templates/`: deck skeleton JSON files used by `reveal-slides new`
- `vendor/reveal.js/`: checked-in third-party frontend runtime assets
- `examples/`: example input JSON files
- `outputs/`: generated presentations

## Themes

### Custom themes (JSON-based)

Custom themes live in `src/reveal_slides/themes/` as JSON files and are auto-discovered at startup. Two themes ship by default:

| Name | Description |
|---|---|
| `tech-future` | Dark blue gradients with cyan/neon accents |
| `corporate-blue` | Professional blue/white scheme |

Each theme JSON defines:

- **colors** — primary, secondary, text, textMuted, error
- **gradients** — slide1 (body), slide2 (title), slide3 (section-break)
- **fonts** — heading, body, monospace
- **sizes** — titleHeading, slideHeading, sectionHeading, body, small
- **spacing** — slidePadding, elementMargin, lineHeight
- **highlightTheme** — syntax-highlight CSS theme (`monokai`, `zenburn`)

All size and spacing tokens are emitted as CSS custom properties and consumed throughout the slide templates, so changing a token in the JSON reskins every slide type uniformly.

To add a new theme, create `src/reveal_slides/themes/<name>.json` following the same structure. The theme is available immediately — no Python changes required.

### Reveal.js built-in themes

Any of the standard Reveal.js themes (`black`, `white`, `league`, `beige`, `sky`, `night`, `serif`, `simple`, `solarized`, `blood`, `moon`, `dracula`) can be set as the `theme` field in the presentation JSON. Built-in themes load the vendor CSS directly and do not use the custom token system.

### Overriding theme at runtime

```bash
reveal-slides deck.json --theme corporate-blue
```

The `--theme` flag overrides `presentation.theme` in the JSON without modifying the file.

A deck template can declare a default theme (e.g. `"theme": "corporate-blue"` in `quarterly-review.json`) which is part of the consistency contract for that template. Use `--theme` to retheme without editing the JSON.

## Deck templates

The `new` subcommand creates a pre-structured JSON skeleton from a curated template. This separates structural consistency (template) from theme (theme JSON) from per-deck content (user JSON).

```bash
reveal-slides new --list
# pitch-deck           Investor pitch: problem → solution → traction → team → ask
# quarterly-review     Quarterly business review: highlights → wins/misses → numbers → next steps
# technical-talk       Technical presentation: background → implementation → code → takeaways

reveal-slides new --template quarterly-review --title "Q3 2026 Review" --out q3.json
reveal-slides q3.json
```

Each template encodes a known-good slide structure with placeholder content. Edit the output JSON to fill in your content, then generate as usual.
