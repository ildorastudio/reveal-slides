# Antigravity vs Claude — Slide Transitions Reference

Each slide in this presentation uses a distinct Reveal.js transition so you can compare all available options in one run. Pick your favourite and we'll apply it globally.

---

## How Per-Slide Transitions Work

Reveal.js lets you override the global transition on any individual slide via the `data-transition` attribute. The `transition` field in the JSON maps directly to this attribute.

**Syntax options:**
- `"zoom"` — same animation in and out
- `"zoom-in slide-out"` — different animation entering vs leaving
- Combined keywords: `zoom`, `slide`, `fade`, `convex`, `concave`, `none`

---

## Slide-by-Slide Breakdown

| # | Slide Title | Type | Transition | What It Looks Like |
|---|-------------|------|------------|-------------------|
| 1 | Antigravity vs Claude | `title` | `zoom` | Explodes outward from the centre — dramatic, cinematic opener |
| 2 | ⚡ Round 1: The Challengers ⚡ | `section-break` | `convex` | Swivels away like a card flipped face-up — punchy section divider |
| 3 | Meet the Contenders | `two-column` | `slide` | Classic horizontal push — clean, professional, easy to follow |
| 4 | The Physics of Antigravity | `content` | `concave` | Caves inward toward you — intimate, like pulling the viewer in |
| 5 | Claude's Neural Architecture | `content` | `fade` | Pure cross-dissolve — smooth, cerebral, lets content breathe |
| 6 | ⚔️ Head-to-Head Showdown | `table` | `zoom-in slide-out` | Zooms in on arrival, slides away on exit — energetic data reveal |
| 7 | Quote | `quote` | `slide-in fade-out` | Slides in with authority, fades out softly — cinematic quote moment |
| 8 | Future Applications | `two-column` | `convex-in concave-out` | Swivels in, caves out — asymmetric combo feels futuristic |
| 9 | Where They Converge | `content` | `fade-in zoom-out` | Fades in gently, zooms away — builds tension toward the verdict |
| 10 | 🏆 The Verdict | `section-break` | `zoom-in convex-out` | Bursts in large, swivels out — leaves a strong final impression |

---

## Quick Comparison Guide

| Transition | Feel | Best For |
|------------|------|----------|
| `zoom` | Explosive, cinematic | Title slides, high-impact moments |
| `convex` | Punchy, card-flip | Section breaks, dividers |
| `slide` | Clean, professional | Standard content flow |
| `concave` | Intimate, pulling-in | Detail slides, close-up content |
| `fade` | Smooth, cerebral | Quotes, reflective slides |
| `zoom-in slide-out` | Energetic | Data, tables, comparisons |
| `slide-in fade-out` | Authoritative → soft | Quotes, statements |
| `convex-in concave-out` | Futuristic, asymmetric | Vision / applications slides |
| `fade-in zoom-out` | Builds tension | Penultimate slides |
| `zoom-in convex-out` | Memorable exit | Final verdict / closing slides |

---

## To Apply One Transition Globally

Remove all `"transition"` fields from individual slides and set the top-level key:

```json
{
  "transition": "zoom"
}
```

The global value must be one of: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`.

> Combined forms like `"zoom-in slide-out"` are only supported per-slide via `data-transition`, not in the global Reveal.initialize config.
