# Getting Started

This repo is a Python CLI that generates [Reveal.js](https://revealjs.com/) slide decks from a JSON file.

**Core flow:** you write a JSON file describing your slides → the CLI validates it with Pydantic → Jinja renders it to an HTML file → open in a browser.

---

## Prerequisites

- Python 3.9+
- `vendor/reveal.js/` present in the repo root (the generated HTML loads these assets at runtime)

---

## Install

From the repo root:

```bash
pip install -e .
```

---

## Generate your first presentation

```bash
reveal-slides examples/quarterly-review.json --open
```

Or without installing:

```bash
python -m reveal_slides examples/quarterly-review.json --open
```

Output lands in `outputs/<slug>-<timestamp>/` containing the source JSON and rendered HTML.

---

## Start from a template

Instead of writing JSON from scratch, scaffold a deck skeleton:

```bash
reveal-slides new --list                                          # see available templates
reveal-slides new --template pitch-deck --out my-deck.json       # create a new deck
reveal-slides my-deck.json --open                                # generate and open
```

Edit `my-deck.json` to fill in your content, then regenerate.

---

## Key concepts

| Concept | Where it lives | What it does |
|---|---|---|
| Presentation JSON | `examples/` or your own file | Declares slides, theme, transition |
| Slide types | `src/reveal_slides/templates/slides/` | `title`, `content`, `two-column`, `image`, `table`, `quote`, `code`, `section-break`, `blank` |
| Themes | `src/reveal_slides/themes/` | JSON token files — colors, fonts, spacing |
| Deck templates | `src/reveal_slides/deck_templates/` | Pre-structured JSON skeletons (`pitch-deck`, `quarterly-review`, `technical-talk`) |
| Jinja templates | `src/reveal_slides/templates/` | `base.html.j2` + `css/base.css.j2` + per-slide-type partials |
| Python source | `src/reveal_slides/` | `cli.py`, `generator.py`, `models/presentation.py` |
| Reveal.js runtime | `vendor/reveal.js/` | Browser-side JS/CSS, never imported by Python |

---

## Where to go next

- **`docs/USAGE.md`** — full CLI reference, theme system, output structure
- **`docs/architecture-review.md`** — open items and known gaps per phase
- **`docs/requirements-p2.md`** — planned Phase 2 features
- **`docs/antigravity-vs-claude-transitions.md`** — Reveal.js transition options reference
