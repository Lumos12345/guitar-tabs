# Jianpu (简谱) melody layer + multi-page pagination — working recipe

Companion to `professional-chord-sheet.md`. Covers the two things that actually broke
when building a real 4-layer sheet, and the fix for each.

## 1. Jianpu melody extraction that produces usable output

The SKILL.md correctly warns that vocal-pitch extraction is the unreliable tier. This is
the best local pipeline found, and its honest ceiling.

### The pipeline (pure numpy, no librosa, no ML model)

frame → autocorrelation f0 → median smooth → **octave-continuity correction** →
snap to C-major scale degrees → per-cell median → jianpu token.

Working implementation: `scripts/melody_jianpu.py` in this skill. Run:

```bash
python3 scripts/melody_jianpu.py <audio.m4a> <lyrics.lrc>   # writes /tmp/melody_jianpu.json
```

### THE critical step: octave-continuity correction

Without it, output is garbage that jumps octaves randomly:

```
1 7, 1 4, 5, 6, 4' 6, 7, 4,      <- WRONG, jumps between octave 3 and 5
```

Raw autocorrelation f0 doubles/halves on voice (octave errors are the dominant failure).
Fix — pull every frame's octave to within ~1.55x of a per-line reference:

```python
def octave_fix(hz, ref):
    if hz <= 0 or ref <= 0: return hz
    while hz / ref > 1.55: hz /= 2.0
    while ref / hz > 1.55: hz *= 2.0
    return hz
# ref = median of the valid f0 frames in that lyric line
```

After the fix the same line reads `1 7, 4, 5, 6, 7,` — a plausible contour.

### Other parameters that matter

- **Narrow the lag window to the vocal band**, not the guitar band: `lag_min = fr/700`,
  `lag_max = fr/110`. Using 80 Hz as the floor lets bass/guitar notes win the
  autocorrelation peak and poisons everything downstream.
- **Parabolic interpolation** around the winning lag (sub-sample accuracy) — cheap, improves
  pitch precision noticeably.
- **Median filter f0 with a wider kernel** (7 frames) before per-cell sampling.
- **Drop low-confidence frames** (`conf < 0.30`) before taking a cell median; `conf` is the
  normalized autocorrelation peak height.
- Cells per line: `min(12, max(4, len(line)//4))`, then collapse consecutive duplicate
  tokens (a held vowel is one note, not six).

### Honest ceiling — state it on the sheet

Even after all of the above, vocal-in-mix f0 tracking yields **melodic contour, not
note-accurate jianpu**. Values still jump non-stepwise (4→6→4→1), which no real melody does.
Two acceptable deliveries, both honest:

1. Ship the jianpu row **labelled approximate** (`简谱(旋律仅供参考)` / "approximate, AI-extracted")
   and say so in the chat reply.
2. Print a **blank jianpu grid** for the learner to fill by ear.

Never ship it unlabelled as authoritative. The skill's CRITICAL #2 rule ("don't fabricate")
applies to the melody layer too — labelling is what makes it non-fabrication.

### Spectral-subtraction caveat
`max(|V| - k·|A|, 0)` needs a **time-aligned instrumental version of identical duration**.
Two files with different durations (e.g. 181 s vs 156 s) are different arrangements/edits —
subtraction is invalid. Check durations with ffprobe first; if they differ, don't attempt it.

## 2. Clean chords: snap, don't trust per-quarter chroma

Per-quarter chroma detection on a full mix produces a lot of junk (`Cm`, `Gm`, `Ab`, `Eb`,
`Bb` on a song that is squarely F# major). Raw output is not directly usable.

Fix, in order:
1. **Establish the key** from the global chroma (this session: F# major, score 0.756 — clear).
2. **Map every detected chord into the diatonic set of the transposed key** with an explicit
   dict, defaulting anything unknown to the tonic. Never emit a chord outside the beginner set.
3. **Collapse consecutive duplicates**, then **cap at 2 chord changes per lyric line** for a
   beginner sheet (take the first, and the one at the midpoint). One chord per line is too
   crude; four is unreadable for a beginner.

```python
F2C = {'F#':'C','F#m':'Am','G#m':'Dm','A#m':'Em','B':'Fmaj7',
       'C#':'G','C#m':'Am','D#m':'Em','G#':'G','A':'Fmaj7',
       'Fm':'Fmaj7','F':'Fmaj7','D#':'Fmaj7','A#':'Fmaj7','Gm':'Em','Cm':'Am'}
```

### Worked transposition: F# major → C major, capo 6
F# → C is 6 semitones, so `capo 6` restores original pitch for singing while every shape
stays open. Degree map used: F#(I)→C, G#m(ii)→Dm, A#m(iii)→Em, B(IV)→Fmaj7,
C#(V)→G, D#m(vi)→Am. Resulting chord set: **C · Dm · Em · Fmaj7 · G · Am** — all open,
F replaced by Fmaj7. Print the capo line as "夹6品＝原调F#，可跟唱；不夹则低6个半音".

## 3. Multi-page pagination pitfall (clipped / duplicated systems)

**The bug:** a naive `page2()` that does

```python
if y + h > bottom:
    img.save(outpath)          # save old page
    img, d = new_page()        # new page
    ...
draw_system(...)               # BUG: draws on the NEW page but y was never reset
y += h
```

produces a page where the overflowing system is drawn on the fresh page **and** the old
page keeps accumulating to the wrong path — you get a final page with clipped systems and
stray `_p2` files that duplicate content.

**The fix — measure-then-flow, fixed system height:**

```python
SYSTEM_H = 232                  # fixed per-system height, computed once
bottom = H - 90                 # leave room for the page number
pageno = 2
while idx < len(data):
    if y + SYSTEM_H > bottom:   # only break BEFORE drawing
        save_page(img, pageno); pageno += 1
        img, d = new_page(); y = header(d, pageno)
    draw_system(d, M, y, w, data[idx])
    y += SYSTEM_H               # uniform advance == guaranteed no overlap
    idx += 1
save_page(img, pageno)
```

Key points:
- **Uniform `SYSTEM_H`** removes the need to measure each system; just check
  `y + SYSTEM_H > bottom` *before* drawing.
- **Only save/switch at the top of the loop**, never mid-draw.
- Write each page to its own incremented filename; don't reuse one path with suffix hacks.
- **Delete stale outputs first** (`for f in os.listdir(outdir): if f.endswith('.png'): remove`)
  or a previous run's `_p2/_p3` pages linger and look like duplicates.
- Verify with vision: ask "how many complete systems, anything clipped at the bottom, page
  number visible?" — a clipped system at the bottom edge is the signature failure.

## 4. Layout numbers that worked (A4 @ 200 DPI = 1654×2339)

- margin `M = 90`; system width `W - 2*M`
- system internals: chord row 40 px → TAB staff 90 px → jianpu row 44 px → lyrics 44 px
- chord diagram: grid 78×112, 4 frets, name above in red
- fingerpick drawing: 6 lines over 104 px + 78 px for the finger legend below
- strum drawing: 104 px, 8 slots, beat labels `1 & 2 & 3 & 4 &` above
- char advance for per-syllable chord placement: `char_w = min(30, (w-10)/len(lyric))`
