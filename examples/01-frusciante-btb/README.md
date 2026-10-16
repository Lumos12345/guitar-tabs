# Example 01 — John Frusciante, *Before the Beginning* (instrumental)

Demonstrates the **retrieve-real-tab → render** pipeline for an **instrumental solo**
piece with **no lyrics**.

## What it shows

1. **Retrieve a real, human-verified tab** (Ultimate Guitar, community v2 by "Avi",
   rated 4.92/5, standard tuning EADGBE, key Em) plus the backing-chord track
   (UG chords version) and cross-check against Songsterr metadata.
2. **Render a print-ready B&W tab** with LilyPond → `tab-source.ly` →
   `tab-page1..3.png` (A4 @ 300 DPI, section labels INTRO / INTERLUDE /
   THEME REPRISE / CLIMAX / OUTRO, technique markers preserved).
3. **Render a beginner teaching sheet** with Pillow → `newbie-page1..3.png`
   (chord diagrams, "how to read TAB in 30 seconds", plain-language symbol legend,
   and a candid difficulty warning — this piece is genuinely advanced).

## Files

| File | What |
|------|------|
| `tab-source.ly` | LilyPond source for the tab (edit + re-render to change layout) |
| `tab-page1..3.png` | Print-ready tab, one PNG per page |
| `newbie-page1..3.png` | Beginner teaching sheet (chords + how-to + legend + tab) |
| `newbie_render.py` | Pillow script that generates the newbie pages |

## Reproduce

```bash
# tab image (requires lilypond)
lilypond -dbackend=eps --png -dresolution=300 tab-source.ly

# beginner sheet (requires Pillow + a CJK font)
python3 newbie_render.py     # writes page1..3.png
```

See the skill's `references/lilypond-tab-images.md` and
`references/beginner-tab-image.md` for the full recipes and gotchas.

## Key lesson

The song title alone is ambiguous ("Before the Beginning" is also a Fleetwood Mac
track). Confirm from the attached audio / `.lrc` before building anything.
