# 03 — Nikki "Before the Beginning" → 4-layer 弹唱谱

A **third** different song titled "Before the Beginning" (yes, really). This one is an
English pop track performed by **Nikki**, delivered as a 4-layer beginner 弹唱谱:
chord diagrams + TAB + 简谱 + lyrics, with per-syllable chord placement.

This example exists mainly to show two techniques the other examples don't cover:

1. **Lyrics + timestamps recovered by OCR from burned-in video subtitles.**
2. **A 4-layer sheet** (the first two examples produce a LilyPond tab + a 2-page
   chord chart; neither has the 简谱 layer).

## Why this is example 03 of the "same title" series

| # | Song | Artist | What it proves |
|---|------|--------|----------------|
| 01 | Before the beginning | John Frusciante | a famous same-title song is a trap |
| 02 | Before the beginning | 暖暖 | a local .mp3 wins over an inferred title |
| 03 | Before the Beginning | Nikki | a *third* unrelated song with the same title |

Three different songs, one title. Never infer the song from its name — open the file.

## Input

- `video_*.m4s` — video-only stream (1920x1080, 156.6 s), **no audio, no subtitle track**.
- `before the beginning（英文版）.m4a` — the matching audio (156.6 s, exact duration match).
- The video has the **official lyrics burned into the lower-left corner** as white
  subtitle text over the artwork.

## Step 1 — lyrics + timestamps from burned-in subtitles (OCR)

There is no soft subtitle stream, so the lyric text only exists as pixels.

```bash
# 1. sample 2 frames per second -> ~313 frames for a 156 s song
ffmpeg -i video.m4s -vf fps=2 /tmp/ocr_frames/f_%04d.png

# 2. crop the subtitle band (measured: y≈910, height 95, x from 90, width 1500)
#    and OCR each frame
ffmpeg -i f_0001.png -vf "crop=1500:95:90:910,scale=3000:-1,format=gray" band.png
tesseract band.png stdout --psm 6
```

Getting tesseract working without root (this environment has no sudo password):

```bash
apt-get download tesseract-ocr tesseract-ocr-eng libtesseract5 libleptonica-dev liblept5 libarchive13t64 libgif7 ...
for f in *.deb; do dpkg-deb -x "$f" /tmp/tess; done
export LD_LIBRARY_PATH=/tmp/tess/usr/lib/x86_64-linux-gnu
export TESSDATA_PREFIX=/tmp/tess/usr/share/tesseract-ocr/5/tessdata
/tmp/tess/usr/bin/tesseract img.png stdout --psm 6
```

**Pitfall:** `liblept.so.5` is a chain of symlinks; the real file is
`liblept.so.5.0.4` from the `liblept5` package. Extracting only `libleptonica-dev`
leaves a dangling link and tesseract dies with "cannot open shared object file".

OCR read most lines cleanly but the low-contrast text over bright artwork garbled
some. Those frames were re-read with a vision model, which handled them reliably.
Result: `[mm:ss.xx] line` data — see `sheet_data.json`.

Cross-check: whisper (`faster-whisper medium`) on the audio gave the timings and a
sanity check, but **misheard several words** ("pedals" → "pedophiles",
"petals" → "pedals"). The OCR'd on-screen text is authoritative.

> HuggingFace is unreachable from mainland China; use `HF_ENDPOINT=https://hf-mirror.com`
> **and** `HF_HUB_DISABLE_XET=1` (the xet backend 401s against the mirror).

## Step 2 — key + chords from audio

```
==== key candidates ====
F#大调: 0.756    C#大调: 0.748    A#小调: 0.744
```

F# major, and every chord (F#, A#m, C#, B, D#m) is a **barre chord** — unplayable for a
beginner. Transposed **down 6 semitones to C major**, then:

- F# → C, A#m → Em, C# → G, B → Fmaj7, G#m → Dm, D#m → Am
- capo 6 returns to the original pitch for singing along
- chord set is all open shapes: **C Dm Em Fmaj7 G Am**

Quarter-by-quarter chroma detection was noisy (`Cm`, `Bb`, `Ab` appeared), so results
were snapped to the C-major diatonic set and capped at 2 chord changes per lyric line —
a beginner can't be changing chords 4 times a bar.

## Step 3 — 简谱 melody (approximate)

`extract_melody_jianpu.py` — pure numpy f0 tracking (autocorrelation, 2048-sample
window, hop 512) over the vocal mix, then:

1. octave-continuity correction (pull each frame within ~1.55× of the line's median,
   killing the octave-jumping that a naive tracker produces)
2. median smoothing
3. snap to the nearest C-major degree, quantise into cells per lyric line

**Honest caveat:** this gives melody *contour*, not note-accurate 简谱. Vocal-in-mix f0
tracking is the weak tier. The rendered sheet labels the 简谱 layer
"仅供参考" (reference only). For an accurate melody, transcribe by ear or replace the
layer with a blank 简谱 grid for the learner to fill in.

## Step 4 — render

`render_4layer_sheet.py` (Pillow, A4 @ 200 DPI = 1654×2339).

Must be run under the **terminal** `python3` (has PIL), not `execute_code`.

```bash
python3 render_4layer_sheet.py
```

Output: `page1-chords-and-rhythm.png` + `page2..5-lyrics.png`.

Page 1: info bar (key/time/capo), six chord grids with plain-language finger notes,
Fmaj7-substitutes-F callout, right-hand fingerpicking drawing (53231323 with T/1/2/3
labels), strumming arrow grid (↓ ↓↑ ↑↓↑) with beat numbers, a how-to-play box, and the
4-layer legend.

Page 2+: one system per lyric line, four stacked layers —
red chord names (placed above the syllable where the change happens),
6-line TAB with X marks, blue 简谱 numbers, black lyrics — plus a timestamp at the right.

**Pagination pitfall:** a naive "save when full, keep drawing" loop writes the
overflowing system onto *both* the old and new page and clips the last row. Measure the
system height, then flow: check `y + SYSTEM_H > bottom` **before** drawing, and start the
new page by re-drawing that same system once.

## Verified

Every page vision-checked: chord grids vs. real fingerings, right-hand drawings present,
chords above syllables (not one per line), Chinese rendering as glyphs not tofu,
nothing clipped or overlapping at page breaks.

## Files

| File | What |
|------|------|
| `page1-chords-and-rhythm.png` | chords, right-hand patterns, how-to-play |
| `page2-lyrics.png` … `page5-lyrics.png` | the 4-layer lyric systems |
| `render_4layer_sheet.py` | Pillow renderer (re-runnable) |
| `extract_melody_jianpu.py` | vocal f0 → 简谱 extraction |
| `sheet_data.json` | per-line: timestamp, chords, jianpu, lyrics |
