# Reveal.js Slide Generator - Phase 2 Good-to-Have Features

## Goal

Phase 2 is for useful enhancements after the core generator is stable. These items should improve authoring speed, output quality, and reuse, without turning the project into a production platform.

## Good-to-Have Features

### 1. Better input options

- generate presentations from Markdown files
- generate presentations from an outline format
- support importing slide content from structured local files
- YAML input as an alternative to JSON

### 2. Better output formats

- PDF export using a headless browser
- standalone export mode that copies required Reveal.js assets alongside the generated deck
- auto-open the generated deck in the default browser after generation

### 3. More slide types

- `timeline`
- `chart`
- `comparison`
- `numbered-steps`
- `agenda`
- `video`
- `iframe`

### 4. Reusable themes and templates

- support reusable custom themes stored as local files
- allow theme presets for different presentation styles
- add template presets for common deck types such as pitch, report, or workshop

### 5. Better asset handling

- support referencing local images with relative paths
- copy referenced images into an assets folder alongside the output
- add basic asset validation and organization

### 6. AI-assisted authoring

- generate slide JSON from a topic and outline
- expand rough notes into slide-ready content
- offer a review step before final rendering

### 7. Batch and editing workflows

- batch generation from an array of JSON files
- update or regenerate an existing presentation
- watch mode to regenerate on input file changes

### 8. CLI enhancements

- `--theme` flag to override the theme from the command line
- `--output` flag to specify a custom output path
- `--open` flag to auto-open the result in a browser
- `--dry-run` flag to validate without generating
- `--verbose` flag for detailed logging

### 9. Quality improvements

- stronger automated tests
- snapshot tests for generated HTML
- clearer logging and diagnostics

## Out of Scope Even for Phase 2

These are intentionally not part of the planned roadmap unless the project goals change:

- web server or API layer
- multi-tenant architecture
- API key management
- rate limiting for external customers
- database-backed metadata systems
- cloud storage and CDN distribution
