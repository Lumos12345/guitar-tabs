# Rendering guitar tab to professional B&W images with LilyPond

Goal: turn ASCII tab (from UG/Songsterr text) into a print-ready black-and-white
guitar-tablature image (6-line TAB staff, optionally with standard notation above,
section labels, technique annotations) — the "looks like a real tab book / Songsterr
/ Guitar Pro page" deliverable. This is the format users mean when they show you a
reference JPG of a printed tab and say "make one like this."

## Install

```bash
sudo apt-get update -qq
sudo apt-get install -y lilypond    # pulls the whole TeX/font stack; ~1-2 min
lilypond --version                   # expect e.g. "GNU LilyPond 2.24.3"
```

Debian/Ubuntu package is self-contained (includes the Feta music font). No Go/pip needed.

## Render command

```bash
lilypond -dbackend=eps --png -dresolution=300 file.ly
```

- `-dbackend=eps --png` is REQUIRED for raster output; plain `lilypond file.ly` only
  emits PDF (and postscript).
- `-dresolution=300` → 300 DPI. A4 comes out as **2480 x 3508 px** per page.
- Multi-page scores produce `file-page1.png`, `file-page2.png`, ... — ONE PNG PER PAGE.
  LilyPond does NOT emit a single combined image. Concatenate manually (e.g. Python
  PIL `Image.new` + `paste` stacked vertically) if a single tall image is wanted.
- PDF is also produced for free; `-dresolution` is ignored for PDF (vector).

## The tuning-string quirk (the #1 bug)

`\new TabStaff` needs an explicit `stringTunings` in **ascending-pitch order (string 6
→ string 1)**. Write standard tuning as:

```lilypond
\new TabStaff {
  \set Staff.stringTunings = #`(,e, ,a, ,d ,g ,b ,e')
  ...
}
```

`e` here is the low E (string 6). Getting this wrong (e.g. putting the high e first)
makes LilyPond mis-assign strings and emit **"negative fret"** errors or wrong fret
numbers. Verify by rendering a one-note test and reading the output image.

To force a specific string for a note (so the rendered fret number exactly matches the
source tab), attach `\1`..`\6` to the pitch:
```lilypond
a'8\3    % A on string 3 → renders "2" (fret 2)
```

## Rhythm-less ASCII tab → uniform note values

UG/Songsterr text tabs usually carry note POSITIONS but no rhythmic values. There is no
faithful rhythm to transcribe. Standard practice: lay each fret-number out as one
**eighth note (duration 8)** in reading order (left→right, then top string line → bottom),
grouping bars to match the source barlines (`|`). Add a footer note like
`Notation: eighth notes (positions only)` so the reader knows the rhythm is approximate.
Do NOT try to invent a rhythm.

## Preserving technique markings

The ASCII markers mean: `b`=bend, `r`=release, `h`=hammer-on, `p`=pull-off,
`/` and `\` = slide, `v`=vibrato, `~`=hold/vibrato, `^`=slow bend, `x`=mute.
LilyPond has real commands (`\bendAfter`, `\vibrato`, `\glissando`) but for a position
tab the simplest lossless approach is to keep the fret number as a plain note and add the
marker as text above it, e.g. `^\markup \italic "b17"`. Nothing is lost even if the
built-in glyph isn't used.

## Section labels

Use `\markup` text or rehearsal marks above the relevant lines: e.g. blocks 1-4 = INTRO /
MAIN THEME, block 5 = INTERLUDE, 6-16 = THEME REPRISE, 17-20 = CLIMAX, 21-24 = OUTRO.
Explicit `\break` after each source block gives one system per block (clean, readable).

## Header / footer

```lilypond
\header {
  title = "Song Title"
  subtitle = "Artist"
  composer = "Album (Year)"
  tagline = "Standard tuning (E A D G B E) | Key: Em | No capo | Notation: eighth notes (positions only)"
}
```

## ALWAYS vision-verify the render

LilyPond fails silently in ways that still produce a PNG (wrong frets, empty staves,
mis-tuning). After rendering, load each page with `vision_analyze`:
- confirm it is a **6-line TAB staff** with visible fret numbers;
- spot-check a known value (e.g. "first bar, B-string line shows 15 and 17");
- confirm section labels and title are present;
- watch for garbled text or blank pages.
Only declare success after the vision check confirms frets match the source. Do not trust
"compilation successfully completed" alone.

## Harmless warnings

"barcheck failed" warnings appear when source blocks have irregular bar lengths vs. 4/4.
They do not affect output; barlines drawn explicitly with `\bar "|"` still render correctly.

## Verification checklist
1. `lilypond ... -dbackend=eps --png ... file.ly` → PNGs exist, A4@300dpi size (2480x3508).
2. `vision_analyze` each page: 6-line staff, correct frets, labels present, no garble.
3. Optional: stack pages into one combined PNG for a single-image deliverable.
4. Copy the .ly source next to the PNGs so the user can re-render with tweaks.
