# Building the 4-layer 弹唱谱 end-to-end

The full chain for "here's a video/audio of a song, make me a beginner sheet that looks
like this printed songbook page": **timed lyrics → key/chords → transposed open chord set →
4 stacked layers → paginated PNGs**. This file is the assembly guide; the individual
pieces live in the references and scripts it points at.

Layers, top→bottom, all sharing one x-grid per system:

```
① red chord names   — placed ABOVE the syllable where the change happens
② 6-line TAB staff  — X marks = right hand (strum / pick pattern)
③ blue 简谱 digits  — vocal melody, 1-7 (+ ' high / , low)
④ black lyrics      — as sung
```

Left-hand = ①, right-hand = ②, melody = ③, words = ④. Print a legend saying exactly that;
a 4-layer sheet without a legend reads as clutter to a beginner.

## Inputs you need before drawing anything

| Input | Where it comes from |
|-------|--------------------|
| timed lyrics (`[mm:ss.xx] line`) | `video-text-extraction` skill (hardsub OCR) or an existing `.lrc` |
| key + chords | `scripts/chord_analyze.py <audio> [lyrics.lrc]` |
| beginner chord set + capo | transposition section of SKILL.md |
| 简谱 tokens | `scripts/melody_jianpu.py <audio> <lyrics.lrc>` |

Do them in that order — the chord/chart steps consume the `.lrc`, so extract lyrics first.

## Assembly checklist

1. **Fix the key** from global chroma. One candidate should clearly win (e.g. F# major
   0.756 over C# 0.748). If it doesn't, the audio may be a different section/edit.
2. **Transpose to C or G** so the chord set is all open shapes. Capo = semitone distance
   back to the original. Sanity check: if the mapped set still contains a barre chord, the
   degree mapping is wrong — fix it before drawing.
3. **Reduce chords per line** to ≤2 (see "Chords: snap detections" in SKILL.md).
4. **Rasterise 简谱** per line, label it approximate.
5. **Draw page 1**: info bar (key / time sig / capo), 6 chord grids + plain-language finger
   notes, Fmaj7-substitutes-F callout, fingerpicking drawing (53231323 with T/1/2/3), strum
   grid (↓ ↓↑ ↑↓↑) with beat numbers, how-to-play box, 4-layer legend.
6. **Draw lyric pages**: one system per line, fixed `SYSTEM_H`, measure-then-flow pagination.
7. **Vision-verify every page.** Non-negotiable — see below.

## Chord set for a C-major beginner sheet

All open, no barre: **C · Dm · Em · Fmaj7 · G · Am**

| Chord | Frets (6→1) | Fingers | Plain-language note |
|-------|-------------|---------|---------------------|
| C | x32010 | -,-,3,2,1,- | 食指1弦1品·中指2弦2品·无名指3弦3品 |
| Dm | xx0231 | -,-,-,2,3,1 | 食指3弦2品·中指1弦1品·无名指2弦3品 |
| Em | 022000 | -,2,3,-,-,- | 中指5弦2品·无名指4弦2品 |
| Fmaj7 | xx3210 | -,-,3,2,1,- | 食指2弦1品·中指3弦2品·无名指4弦3品 |
| G | 320003 | 2,1,-,-,-,3 | 中指6弦3品·无名指5弦2品·小指1弦3品 |
| Am | x02210 | -,-,2,3,1,- | 食指2弦1品·中指4弦2品·无名指3弦2品 |

Always state on the page: **F 和弦用 Fmaj7 代替：不用横按** — the single most useful line
for a beginner.

## Right-hand patterns to draw

Fingerpicking (分解, 8 eighth-note slots) — string index 0 = 1st string (top line):

```python
pat = [(4,"T"),(2,"2"),(1,"1"),(2,"2"),(0,"3"),(2,"2"),(1,"1"),(2,"2")]
# 5弦T, 3弦2, 2弦1, 3弦2, 1弦3, ...  T=拇指, 1=食指, 2=中指, 3=无名指
```

Strumming (扫弦) — 8 slots, heavy separator every 2:

```python
slots = ["↓","↓","↑","·","↑","↓","↑","·"]   # ↓↓↑ ·↑↓↑
beats = ["1","&","2","&","3","&","4","&"]
```

Label the beats above the arrows and print the pattern as text too (`↓ ↓↑ ↑↓↑`). BOTH
drawings are mandatory — a sheet with no right-hand reference gets read as incomplete.

## Per-syllable chord placement

Never one chord per line. Compute each character's x, then drop the chord name at the x of
the syllable where it changes:

```python
char_w = min(30, (w - 10) / max(len(lyric), 1))
positions = [x + i*char_w for i in range(len(lyric))]
d.text((positions[0], chord_y), chords[0], font=cjk(27), fill=RED)
if len(chords) > 1:
    d.text((positions[len(lyric)//2], chord_y), chords[1], font=cjk(27), fill=RED)
```

Also print a small grey timestamp at the right edge of each system — it lets the learner
jump to that line in the recording, which is the whole point of having timed lyrics.

## Pagination

Fixed `SYSTEM_H`, check before drawing, save/switch only at loop top, and clear stale PNGs
first. Failure signature to look for in review: a system clipped at the bottom edge, or a
page whose content appears twice. Recipe and the buggy-vs-fixed contrast:
`references/jianpu-layer-and-pagination.md` §3.

## Verification (the step that actually catches bugs)

Vision-check each page with a specific question, not "does this look ok":

> "Are the chord diagrams correct with dots on the right strings? Is the fingerpicking
> drawing present with T/1/2/3 labels? Strum arrows present with beat numbers? Do Chinese
> characters render as real glyphs, not empty boxes? Anything clipped or overlapping?"

In practice this caught: a mis-positioned chord band crop, a duplicated/clipped system from
the naive pagination loop, and confirmed the last page wasn't over-full.

Also run a numeric check on the text side rather than eyeballing:

```python
assert all(ord(c) < 128 for c in ascii_txt)   # for the pure-ASCII deliverable
```

## Delivery set

Per this user: per-page PNGs + the generator script + a plain-text version + a pure-ASCII
version, saved into the folder they named (not just chat text). Keep the scripts runnable
with argv/env-parameterised paths so they're reusable and safe to publish:

```python
SRC    = sys.argv[1] if len(sys.argv) > 1 else "song.m4a"
outdir = os.environ.get("OUTDIR", "./out")
```

Hardcoded `/mnt/c/Users/<name>/...` paths must be scrubbed before anything goes to a public
repo — grep for the username, `/home/`, and `C:\Users` first.
