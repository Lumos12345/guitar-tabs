# Professional multi-layer pop 弹唱谱 (chord chart) — Pillow recipe

This is the **high-end** deliverable, distinct from the simple "newbie sheet" in
`beginner-tab-image.md`. Use it when the user shows reference JPGs of a printed pop
songbook / 吉他教材 and wants THAT level of detail, or when they complain a simpler
chord sheet is "too crude / not detailed enough / no right-hand fingering".

## The user-preference lesson (learned the hard way)

A chart that prints **one chord name at the start of each lyric line** WILL be rejected
as too crude. The user's exact complaints (translated):

> "the chord guidance and the lyric alignment are not detailed enough, and there is
> no right-hand fingering"

What they actually want (this is the bar):
1. **Right-hand fingering** — BOTH a fingerpicking (分解和弦) pattern drawing AND a
   strumming (扫弦) pattern drawing. This is non-negotiable; a chord sheet with no
   right-hand reference is considered incomplete.
2. **Per-syllable chord alignment** — each chord sits directly ABOVE the specific
   syllable/character where it changes, NOT one chord per line.
3. **Fingering detail** — chord diagrams with fret-dot positions AND plain-language
   finger notes (which finger on which string/fret).
4. **Playing guidance** — a box saying which pattern to use where (verse=fingerpick,
   chorus=strum), plus "change chords early, right hand never stops".

## The reference layout (4 stacked layers per "system")

A professional 弹唱谱 is four vertically-stacked layers, all aligned:
```
① chord name (+ small chord diagram)   ← left hand
② TAB staff (6 lines)                  ← right hand: X = plucked string, ↓↑ = strum
③ jianpu 简谱 1-7 (vocal melody)        ← optional 4th layer (see below)
④ lyrics (one hanzi per melody note)
```
This session delivered layers ①②④ (three-layer version) and offered ③ (jianpu) as a
follow-up. Confirm with the user how many layers they want before building — the jianpu
melody layer requires vocal-pitch extraction and is materially more work.

## Right-hand pattern drawings (reuse these)

**Fingerpicking (分解和弦) — classic 53231323 arpeggio:**
Draw a mini 6-line staff. String index 0 = 1st string (top) … 5 = 6th string (bottom).
Plot a red dot on the right string for each of the 8 eighth-note slots, with a finger
label above each dot:
```python
pat = [(4,"T"),(2,"2"),(1,"1"),(2,"2"),(0,"3"),(2,"2"),(1,"1"),(2,"2")]
# (string_index, finger)  → 5弦T, 3弦2, 2弦1, 3弦2, 1弦3 ...
# fingers: T=拇指(thumb, plays bass strings), 1=食指(index), 2=中指(middle), 3=无名指(ring)
```

**Strumming (扫弦) — 4-beat grid, 8 slots:**
```
slots = ["↓","↓","↑","·","↑","↓","↑","·"]   # ↓↓↑ ·↑↓↑  (the common pop pattern)
```
- Draw the 8 slots across the bar width; big red down/up arrows.
- Label beats `1 ＆ 2 ＆ 3 ＆ 4 ＆` above, bolding the 4 main beats.
- Draw a heavier separator every 2 slots (each beat).
- Put "下 上" text under each beat to help beginners.
- State the pattern also as text: `↓↓↑ ↑↓↑`.

## Per-syllable chord placement (the key trick)

Do NOT place one chord per line. Compute each character's x-position, then draw the chord
name at the x of the syllable where it changes:
```python
f_ly = cjk(28)
positions = []
cx = M
for ch in lyric:
    positions.append((ch, cx))
    cx += d.textlength(ch, font=f_ly) + gap   # gap ≈ 4px
# syl_chord = {char_index: "C", ...}  e.g. {0:"C", 8:"Em"}
for idx, chord in syl_chord.items():
    d.text((positions[idx][1], chord_y), chord, font=cjk(26), fill=RED)
```
The syllable→chord mapping comes from the fine-grained audio analysis (split each lyric
line into first-half / second-half chord, see `audio-chord-analysis.md`).

## Instrumental / no-lyric sections

前奏/间奏/尾奏 have no lyrics. Still show the TAB accompaniment and print the bar chords
spaced across the (empty) lyric row, or just leave the vocal line blank with a
`前奏·器乐` note.

## Chord diagram + finger note

Reuse the grid geometry from `beginner-tab-image.md` (leftmost line = 6th string). This
session's chord set (C-key, for a F#-original pop song):
`C x32010 · Am x02210 · Em 022000 · Fmaj7 xx3210 · F 133211 · G 320003 · Dm xx0231`.
Always print the **Fmaj7 substitute** callout next to F.

## Page structure

- Page 1: title + info bar (调性 / 拍号 / 速度 BPM / 变调夹 capo) + `① 六个和弦` (grid row
  + Fmaj7 note) + `② 右手节奏型` (fingerpick drawing + strum drawing) + playing-guide box.
- Page 2+: systems grouped under section banners (前奏 / 主歌A / 间奏 / 主歌B / 过渡 /
  副歌 / 尾奏). Overflow → start a new page; never let a system get clipped.

## Pitfall: which Python runs the Pillow script

`execute_code` runs in a sandbox with a DIFFERENT Python that may NOT have PIL. Write the
script to a file and run it via **terminal** `python3 script.py` — that interpreter has
Pillow. (This is a runner-choice issue, not "execute_code is broken".)

## Verify

Vision-verify EVERY page yourself (do not trust a subagent's self-report): chord grids
correct? right-hand drawings present (fingerpick dots + strum arrows)? chords above
specific syllables (not one per line)? Chinese renders as real glyphs? nothing clipped?
