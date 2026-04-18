# Project Restructuring Plan

## Why this document exists

The current repository layout does not make the architecture obvious. In particular:

- It is not clear how Python uses `reveal.js`.
- There are two generation paths in the repo today: a Python CLI and an older Node-based generator.
- `reveal.js` exists in both `vendor/` and `vendor-npm/`, which makes ownership unclear.
- The docs and implementation are not fully aligned on where third-party assets should live.

This document records the restructuring direction before we move files around.

## Current architecture

The Python app does **not** import `reveal.js` as a Python library.

Instead, the flow is:

1. `generate.py` reads a presentation JSON file.
2. Python validates the JSON with Pydantic models.
3. Python renders Jinja templates into a standalone HTML file.
4. The generated HTML references local `reveal.js` CSS and JS files.
5. The browser loads `reveal.js` when the HTML file is opened.

So `reveal.js` is a **frontend runtime asset**, not a Python module.

## Decision: where should `reveal.js` live?

`reveal.js` should **not** live in a Python `lib/` folder.

Reason:

- `lib/` usually implies application code that we own or import directly in runtime code.
- Python never imports `reveal.js`.
- The generated HTML only points to static JS/CSS assets on disk.

Better options are:

- `vendor/reveal.js/`
- `third_party/reveal.js/`

For this repo, `vendor/reveal.js/` is the clearest choice because it already matches the Python template paths and the project requirement docs.

## Problem areas in the current structure

### 1. Mixed implementation directions

We currently have:

- `generate.py` for the Python-first flow
- `scripts/generate-slide.js` for a Node-first flow

This makes it hard to know which path is the primary product.

### 2. Duplicate Reveal asset locations

We currently have:

- `vendor/reveal.js/`
- `vendor-npm/node_modules/reveal.js/`

This is redundant and invites drift.

### 3. Scripts folder is overloaded

The `scripts/` directory currently mixes:

- active app logic
- helper logic
- older implementation code

That makes it hard to tell what is part of the product and what is tooling.

### 4. Outputs need a clearer contract

Ignoring cleanup of existing `outputs/` contents for now, the future output rule should be:

- each generated presentation gets its own folder
- the folder name is based on topic slug + timestamp
- that folder contains both the source JSON and generated HTML

## Recommended target structure

```text
reveal-slides/
├── docs/
│   ├── requirements-p1.md
│   ├── requirements-p2.md
│   ├── theme-system-plan.md
│   └── restructuring-plan.md
├── src/
│   └── reveal_slides/
│       ├── __init__.py
│       ├── cli.py
│       ├── generator.py
│       ├── models/
│       ├── rendering/
│       └── themes/
├── templates/
│   ├── base.html.j2
│   └── slides/
├── examples/
├── vendor/
│   └── reveal.js/
├── outputs/
│   └── <topic-slug>-<timestamp>/
│       ├── <topic-slug>.json
│       └── <topic-slug>.html
├── scripts/
│   └── sync_vendor_assets.(js|py)
├── tests/
├── pyproject.toml
└── README.md
```

## Meaning of each top-level folder

### `src/`

Own application code only.

- CLI entrypoints
- generation logic
- validation models
- theme loading logic that belongs to the Python app

### `templates/`

Jinja templates used to render HTML.

### `vendor/`

Checked-in third-party frontend assets needed at runtime by generated presentations.

- `reveal.js` belongs here

### `scripts/`

Repository maintenance helpers only.

Examples:

- sync `reveal.js` from npm into `vendor/`
- developer utility scripts
- one-time migration helpers

App logic should not live here long-term.

### `outputs/`

Generated artifacts only.

Future convention:

- folder per generation
- folder name: `<topic-slug>-<timestamp>`
- contains both `.json` and `.html`

We are intentionally ignoring cleanup/reorganization of current `outputs/` content in this phase.

## Recommended restructuring decisions

### Decision 1: make Python the primary implementation

If the product direction is Python, then:

- keep `generate.py` behavior
- migrate it into `src/reveal_slides/`
- treat the Node generator as legacy or remove it after migration

### Decision 2: keep only one runtime copy of `reveal.js`

Preferred runtime location:

- `vendor/reveal.js/`

If npm is still needed to fetch updates, use it only as a supplier during development, not as the runtime path used by generated HTML.

That means:

- generated HTML should point to `vendor/reveal.js/...`
- `vendor-npm/` should be optional tooling, or removed after sync

### Decision 3: separate app code from repo utilities

- move Python business logic out of repo root and into `src/`
- keep `scripts/` only for maintenance helpers
- avoid storing product code in `scripts/`

### Decision 4: document folder ownership

Each top-level folder should answer one question clearly:

- is this app code?
- is this a template?
- is this third-party code?
- is this generated output?
- is this documentation?

If a folder cannot be explained in one sentence, it probably needs to be renamed or split.

## Suggested migration sequence

1. Confirm Python is the main implementation path.
2. Move Python app code into `src/reveal_slides/`.
3. Decide whether `scripts/generate-slide.js` is legacy or still required.
4. Standardize on `vendor/reveal.js/` as the runtime asset location.
5. Keep `vendor-npm/` only if needed for asset syncing, otherwise remove it.
6. Add a small README section describing how generation works end-to-end.
7. Leave `outputs/` history alone for now, but keep the new folder-per-presentation rule going forward.

## Final note

The key architectural point is:

- Python is the **generator**
- Jinja is the **renderer**
- `reveal.js` is the **browser-side presentation runtime**

Once the directory structure reflects that separation, the repo will be much easier to understand and maintain.
