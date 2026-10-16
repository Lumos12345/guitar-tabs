# Example 02 — 暖暖, *Before the beginning* (Chinese pop vocal)

Demonstrates the **audio → key/chord analysis → beginner 弹唱谱** pipeline for a
**local original track with no published tab**.

> Note: this is a *different* song from Example 01 despite the similar title —
> it is a Chinese pop song by 暖暖 (N₂工作室), not the John Frusciante instrumental.
> This is exactly the title-collision trap the skill warns about: always confirm
> from the attached file, never from the title.

## What it shows

1. **Analyze the backing track** (`伴奏` mp3) with the pure-numpy detector in
   `scripts/chord_analyze.py` → key = **F# major**, chords = F#, A#m, D#m, C#, B, G#m.
2. **Transpose to C major** so only open chords remain (F#→C, A#m→Em, D#m→Am,
   C#→G, B→Fmaj7) — a beginner can actually play it.
3. **Compute the capo**: F# is 6 semitones above C ⇒ **capo 6 = original pitch**
   (sing along); no capo = 6 semitones lower (fine for solo practice).
4. **LRC-synced per-line chord chart**: parse the `.lrc` timestamps, analyse the
   chord over each lyric line → a "唱到哪句换哪个和弦" sheet.
5. **Render a 2-page 弹唱谱** with Pillow → `chord-chart-page1..2.png`.

## Files

| File | What |
|------|------|
| `chord-chart-page1.png` | Chords + capo note + song-structure summary |
| `chord-chart-page2.png` | Per-line lyrics with chord changes |
| `chordchart_render.py` | Pillow script generating both pages |

## Reproduce

```bash
# 1. key + per-line chords (needs the audio + .lrc)
python3 ../scripts/chord_analyze.py song.mp3 song.lrc

# 2. render the chord chart
python3 chordchart_render.py
```

## Result summary

- Original key: **F# major** (barre-chord heavy, unplayable for a beginner)
- Simplified to: **C key** — chords **C, Am, Em, Dm, G** (Fmaj7 for the rare F)
- Progression: verse ≈ C↔Am, pre-chorus ≈ C Am Em Dm C, chorus ≈ C↔G
- Capo 6 = same pitch as the original recording
