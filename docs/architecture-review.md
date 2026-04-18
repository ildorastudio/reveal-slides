# Architectural Review

A rolling scan of the repo against its own stated goals (`docs/requirements-p1.md`, `docs/restructuring-plan.md`, `docs/rejected-decisions.md`). Items are grouped by phase so the critical work can land first.

The Python CLI is the declared product. Prior-round Phase 1 and most of Phase 2 (Node-path removal, vendor dedup, orphan `models/` cleanup, `pyproject.toml` packaging with `importlib.resources`, dropping `generate.py` shim, custom-theme validation, template split into `base.html.j2` + `css/base.css.j2` + `slides/<type>.html.j2`, `ImageSlide` with `side`, typed exceptions, CLI flags `--output`, `--vendor-dir`, `--standalone`) are now in. This document tracks what is still open and what has surfaced since.

---

## Phase 2 — Remaining

### 2.6 Two overlapping "theme" concepts in docs
`docs/theme-system-plan.md` describes the theme design as a proposal while `docs/USAGE.md` and the code now implement it. `docs/requirements-p1.md` §7 still lists only "theme colors applied consistently" without referencing the custom JSON themes or the `CUSTOM_THEMES` set.

Impact: three different mental models for the same system. `theme-system-plan.md` also lists themes that do not exist on disk (`nature-green`, etc.).

Action: fold theme docs into a single "Themes" section in `docs/USAGE.md`. Delete `docs/theme-system-plan.md` or move it to `docs/legacy/`. Update `requirements-p1.md` §4 to reference `image` (with `side`) instead of the now-removed `image-left` / `image-right`.

### 2.7 `docs/USAGE.md` is stale
It still references `python generate.py examples/…json` (§ "Generate a presentation") and a repo-root `templates/` folder (§ "Packaging-aware layout" and "Folder responsibilities") — both removed. It also claims "older Node-based generator files in the repo for reference" — they are gone.

Action: rewrite `Generate a presentation` to use `reveal-slides` or `python -m reveal_slides`. Delete the "Notes on legacy files" section. Update folder-responsibilities to point at `src/reveal_slides/templates/` and `src/reveal_slides/themes/`.

### 2.8 `requirements-p1.md` "Definition of Done" step has drifted
Lists `python generate.py <input.json>` as the canonical invocation and the slide-type list names `image-left` / `image-right`. Update to match the current surface area once 2.7 is done.

---

## Phase 3 — Quality & ergonomics

### 3.2b Missing CLI flags (partial)
`--output`, `--vendor-dir`, `--standalone` landed. Still absent: `--theme` (override `presentation.theme` from the CLI for quick iteration), `--dry-run` (validate JSON, skip writing), and `--open` (launch default browser on the generated HTML).

Action: add these as thin argparse options. `--theme` is one line — override `presentation.theme` after `parse_presentation`, re-run `validate_theme`. `--dry-run` short-circuits before `output_folder.mkdir`.

### 3.4b Stale tool scratch directories on disk
`.kilo/`, `.playwright-mcp/`, `.ruff_cache/` still exist in the working tree. `.gitignore` covers them, so they don't pollute git, but they are noise when grepping or zipping the repo.

Action: delete from disk. One-time cleanup.

### 3.6 `outputs/` has mixed legacy artifacts
`outputs/` still contains loose top-level files: `ai-healthcare-presentation.json`, `ai-healthcare-stunning.json`, `ev-presentation.html`, and three `presentation-YYYYMMDD-HHMMSS-*.html` files — all pre-dating the per-presentation-folder convention. They coexist with the new `<slug>-<timestamp>/` folders.

Action: move to `outputs/_legacy/` or delete. A clean `outputs/` makes the folder-per-presentation convention self-evident.

### 3.7 No tests
No `tests/` directory, no `pytest` dependency, no CI. The generator has enough branching (theme-data present vs. absent, standalone vs. vendor-relative, missing vendor dir, each of nine slide types) that regressions will silently ship.

Action (minimum viable): add `pytest` and `pytest-snapshot` as dev deps. Golden-file test per slide type: JSON input → rendered HTML → snapshot. One integration test that runs `generate()` end-to-end on `examples/quarterly-review.json` and asserts the output folder structure. This is small (a day of work) and catches the kinds of drift documented below (§4.x).

---

## Phase 4 — Consistency (the current primary pain point)

The user-visible symptom is "generated slides aren't consistent." This section diagnoses why and proposes concrete fixes. Most of these are cheap; the value is compounding because each deck benefits.

### 4.1 Theme JSON defines tokens the CSS ignores
`themes/<name>.json` exposes a full token set: `colors`, `gradients`, `fonts`, `sizes` (`heading1`, `heading2`, `body`, `small`) and `spacing` (`slidePadding`, `elementMargin`, `lineHeight`).

`src/reveal_slides/templates/css/base.css.j2` only consumes `colors`, `gradients`, and `fonts`. `sizes` and `spacing` are never read. That's why themes can only recolor; they can't restyle.

Worse, heading sizes are hard-coded inconsistently across slide types:
- `slide-title h1`: `2em`
- `slide-content h2`: `1.3em`
- `slide-image h2`: `1.2em`
- `slide-two-column > h2`: `1.3em`
- `slide-table h2`: `1.3em`
- `slide-section-break h2`: `1.8em`

And padding:
- `slide-content`: `1.5em 2.5em`
- `slide-image`: `1.5em 2.5em`
- `slide-two-column`: `1.5em 2.5em`
- `slide-table`: `1.5em 2.5em`

The content/image/two-column/table padding is the same number repeated four times — the classic signal that it should be a variable, not a literal.

Action:
1. Extend `css/base.css.j2` to emit CSS custom properties for `sizes` and `spacing` (mirror the `colors`/`gradients`/`fonts` block).
2. Replace every literal with a `var(--…)`. Define a **modular scale** (e.g., `--fs-h1: 2.4em; --fs-h2: 1.3em; --fs-body: 0.75em; --fs-small: 0.65em`) so a new slide type picks from the ladder instead of inventing its own value.
3. Add `sizes` and `spacing` to the two existing theme JSONs to match what the CSS reads.

This is the single biggest consistency win available.

### 4.2 No design-token schema / theme validation
The theme JSON is parsed with plain `json.loads` in `generator.py:53`. Nothing validates that `theme_data.colors.primary` actually exists — a typo or missing key silently renders a broken CSS var like `var(--clr-primary, )`.

Action: add a `Theme` Pydantic model next to `Presentation` (colors, gradients, fonts, sizes, spacing, each with required keys). Call `Theme.model_validate(json.loads(...))` in `load_theme_data`. Fail loudly at generate-time, not at browser-open-time.

### 4.3 Custom themes hard-coded in a Python `set`
`presentation.py:22-25` hard-codes `CUSTOM_THEMES = {"tech-future", "corporate-blue"}`. Adding a new JSON file to `src/reveal_slides/themes/` without editing that set causes `validate_theme` to reject the theme name.

Action: discover themes at import-time from `themes/index.json`, or from `THEMES_DIR.glob("*.json")` (excluding `index.json`). Keep `CUSTOM_THEMES` as the derived set so downstream code doesn't change.

### 4.4 Code slides silently ship without syntax highlighting
`slides/code.html.j2` emits `<code class="language-{{ slide.language }}" data-trim data-noescape>` which relies on Reveal's `highlight` plugin, but `base.html.j2` doesn't register it (`Reveal.initialize({ ... })` has no `plugins: [ RevealHighlight ]` and no `<link>` to `plugin/highlight/monokai.css`).

Impact: every `code` slide renders as plain grey preformatted text. `examples/quarterly-review.json` has a JSON code block that renders unstyled today.

Action: load `vendor/reveal.js/plugin/highlight/highlight.js` and the CSS in `base.html.j2`, pass `plugins: [ RevealHighlight ]`. Also expose `highlight` theme via the theme JSON (so `tech-future` uses monokai, `corporate-blue` uses a light scheme) — otherwise code slides break theme consistency.

### 4.5 Per-slide `transition` override contradicts the consistency rules
`requirements-p1.md` §7 says "transition configured at the presentation level, not per slide" — an explicit consistency rule. But `BaseSlide.transition` is a per-slide field (`models/presentation.py:32`) and every slide template honors it (`data-transition=…`).

Two options, either is fine — pick one deliberately:
- (a) Remove `BaseSlide.transition` to match the stated rule. Simpler, enforces consistency.
- (b) Keep the override but update `requirements-p1.md` §7 to reflect that it's intentional. Then the docs are accurate.

Either way, resolve the contradiction. Right now the "consistency rule" is false advertising.

### 4.6 No layout-overflow detection
Pydantic caps bullet count (5) and length (100 chars) for `ContentSlide`. But `TwoColumnSlide` allows 5 + 5 = 10 bullets on one slide, `ImageSlide` allows 5 bullets next to an image with a caption, and `TableSlide` allows 10 rows × 8 columns. Combined with theme-specified font sizes, all of these can overflow the 1280×720 viewport and clip or scroll.

Current state: there is no way to know a slide overflowed until a human opens it in a browser.

Action (cheap): add a `--check` mode that renders each deck to PDF via headless Chrome (Playwright is already in dev tooling) and runs a heuristic: if any slide's natural height > 720px, fail with the slide index. Not perfect, but catches 80% of real overflow bugs.

Action (architectural): tighten the per-slide-type limits. E.g., TwoColumn caps each side at 4 bullets of 80 chars; Table caps rows×cols to a combined budget. Document the budget next to each model class.

### 4.7 Bullet-animation CSS doesn't scale
`css/base.css.j2:98-102, 159-162, 230-239` hand-writes `animation-delay` for each `:nth-child(N)` up to N=5. If someone later raises the bullet cap to 6, bullets 6+ will not animate (no `animation-delay` rule → `forwards` fill with `opacity: 0` → bullet is permanently invisible).

Action: use CSS `animation-delay: calc(var(--n, 0) * 0.1s)` with `style="--n: {{ loop.index }}"` on each `<li>`. Removes hard-coded N-style and survives any cap change.

### 4.8 `.slide-body` class referenced in template but not styled
`slides/title.html.j2` emits `<p class="slide-body">` when `body` is present (title slide's optional body line), but `css/base.css.j2` has no rule for `.slide-body`. Same applies to `section-break.html.j2` (which renders `body` into `<h3>` — inconsistent tag, different visual weight than the title variant).

Action: either style `.slide-body` uniformly and use the same tag in both templates, or delete the `body` field from `TitleSlide` (it's rarely used and creates a near-duplicate of `section-break`).

---

## Phase 5 — Templates (the other half of consistency)

"Templates" in this repo currently means **per-slide-type Jinja templates** — the atoms. There is no concept of a **deck template** — the molecule — that would give a user a ready-made, consistent starting point. This is the gap behind the request "I need consistency in generated slides."

### 5.1 No deck templates exist today
Every user starts from `examples/quarterly-review.json` and manually writes each slide's JSON. That's fine for a one-off but doesn't scale, and it's why different decks look different: each author makes different structural choices (how many bullets, when to use `section-break`, whether to open with a `title` or dive straight into `content`).

Gap: no library of curated deck skeletons — `pitch-deck.json`, `technical-talk.json`, `quarterly-review.json`, `weekly-status.json` — each encoding a known-good structure with placeholder content.

### 5.2 Proposal: `templates/` at the deck level
Add a `src/reveal_slides/deck_templates/` directory containing JSON skeletons. Wire a new CLI subcommand:

```
reveal-slides new --template pitch-deck --out my-deck.json
reveal-slides new --template quarterly-review --title "Q4 2026" --out q4.json
reveal-slides my-deck.json     # existing flow
```

The `new` command copies a template, optionally substitutes a small set of macros (`{{ title }}`, `{{ author }}`, `{{ date }}`), and writes a JSON file the user edits. This separates **structural consistency** (template) from **theming consistency** (theme JSON) from **per-deck content** (user JSON).

Benefits:
- Every pitch deck has the same 10-slide structure. Every quarterly review has the same section cadence. Authors don't re-derive structure each time.
- New slide types or theme changes propagate into every deck built from the template.
- Drives down cognitive load for first-time users — one command to a sensible starting file.

### 5.3 Template catalog to ship first
Start with three, all 8-10 slides, each calibrated to different use cases:

1. **`pitch-deck`** — title → problem → solution → market → product → traction → team → ask (section-breaks between tiers).
2. **`quarterly-review`** — title → section-break → content (highlights) → two-column (wins/misses) → table (numbers) → quote (customer) → content (next Q) → section-break (Q&A). Matches `examples/quarterly-review.json` but with placeholders.
3. **`technical-talk`** — title → agenda (content) → section-break per topic → code slides → image (diagram) → content (takeaways) → section-break (Q&A).

Each ships as a plain JSON file in `src/reveal_slides/deck_templates/<name>.json`. List them via `reveal-slides new --list` (reads `deck_templates/index.json`, same pattern as themes).

### 5.4 Slide-level variants (medium-term)
Distinct from deck templates: add **variants within a slide type**. E.g., `ContentSlide.variant: Literal["bullets", "numbered", "checklist"]`. Or `TableSlide.variant: Literal["default", "kpi-cards"]`. One JSON model, rendered differently, driven by a variant field.

This is a smaller version of the deck-template idea and handles the case where two authors want the same information to look different (checklist for runbook, numbered for steps). Better than forcing them to write raw HTML in `custom_css`.

### 5.5 Composable Jinja partials for repeated structures
Three slide types (`content`, `image`, `two-column`) all render `<ul><li>…</li></ul>` from a `bullets` list with fade-up animations. The markup is duplicated across three `.j2` files; the CSS is duplicated via selectors. A shared `_bullets.html.j2` partial (`{% include 'partials/_bullets.html.j2' %}`) makes bullet styling change in one place.

Same for captions (`img-caption` class used under image, could be used under table or code).

Action: extract `partials/_bullets.html.j2`, `partials/_caption.html.j2`, `partials/_slide_heading.html.j2`. Reduces the "three-places-to-edit" tax when changing bullet behavior.

### 5.6 `presentation.theme` should support a template default
Today the user must pick a theme in every JSON. A deck template should be able to declare a default (`"theme": "corporate-blue"` in `quarterly-review.json`) so the theme-to-template pairing is part of the consistency contract. This already works — it's just not documented as an intentional feature.

Action: document in USAGE.md that deck templates embed theme choice, and add a `--theme` CLI override (§3.2b) so the user can retheme without editing the JSON.

---

## Phase 6 — Deferred / tracked elsewhere

Captured in `docs/requirements-p2.md`; listed here for completeness:

- Additional slide types (timeline, chart, agenda, …)
- AI-assisted authoring
- Live-preview / `--watch` mode

These should not drive architecture work until Phase 2-5 is done.

---

## Suggested sequencing

1. **Week 1 — docs & stale paths.** 2.6, 2.7, 2.8, 3.4b, 3.6. Small PRs, unblocks new contributors.
2. **Week 2 — consistency core.** 4.1 (token plumbing), 4.3 (theme auto-discovery), 4.2 (theme schema). 4.1 is the highest-leverage single change in this doc.
3. **Week 3 — rendering fixes.** 4.4 (code highlighting), 4.5 (transition override), 4.7 (bullet animation), 4.8 (`.slide-body`). Each is a handful of lines.
4. **Week 4 — templates foundation.** 5.2 + 5.3 (three deck templates and `new` subcommand). 5.5 (Jinja partials).
5. **Week 5 — tests.** 3.7 golden-file snapshots so the above doesn't regress. Also lets 4.6 (overflow detection) land with confidence.
6. **Ongoing — CLI polish.** 3.2b (`--theme`, `--dry-run`, `--open`), 5.4 (slide variants).

## Out of scope

- Performance (generator is sub-second on 10-slide decks).
- Security (local-first tool, no network surface).
- Accessibility of generated HTML — worth its own pass after 4.1 when tokens carry color contrast.
