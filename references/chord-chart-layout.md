# 弹唱谱 (chord+lyric chart) deliverable — concrete layout

For a **vocal** song with audio/.lrc and no need for note-level tab. Two A4 Pillow pages
(1654×2339 @ 200 DPI, wqy-zenhei CJK). This is the standard beginner deliverable.

## Page 1 — chords & instructions
1. Title `歌手 — 歌名` (46px), subtitle "零基础吉他弹唱谱 · 新手简化版" (28px),
   credits line `作词 X / 作曲 Y / 原唱 Z` from the .lrc header (20px, gray).
2. Info bar (rounded, light gray): `调性：<key> 调 | 只用 N 个超好按的开放和弦 | 变调夹夹第 K 品 = 原唱调`.
3. Dark banner `① N 个和弦…`, then a ROW of chord grids (reuse chord-diagram geometry from
   `beginner-tab-image.md`; leftmost line = 6th string). Under each: plain-language finger
   note. Add the F→**Fmaj7** beginner substitute callout.
4. Green tip box: capo explanation — "capo K = original pitch (can sing along); no capo =
   K semitones lower (fine for solo practice)".
5. Dark banner `② 整首歌的和弦走向`, yellow tip box listing verse / pre-chorus / chorus
   loops + the takeaway ("整首歌主要就是 X 和弦，偶尔换 A/B/C").

## Page 2 — lyric + chord chart
One lyric line per row (row pitch ~34px). Chord name in red (30px) at the row's LEFT,
lyric (27px, x offset ~150px) to its right. Show the chord only when it CHANGES (or repeat
for clarity). Footer bar repeats `原调 X → 本谱 C 调指法 + 变调夹 K 品 | 弹法：左手换和弦，右手每拍往下扫`.
Stop adding rows before `H-140`; the footer sits at `H-90`.

## Verse/ chorus structure cheat
Print loops rather than a 28-line wall: verse "C → Am → C …", pre-chorus "C → Am → Em → Dm
→ C", chorus "C → G → C → G". This is far more actionable for a beginner than exact
per-line chords, though page 2 gives the exact per-line chart.

## Vision-verify
Load each page: title correct? chord dots on correct frets/strings? Chinese renders as real
glyphs (not tofu)? lyrics complete, no row overlap, nothing clipped?

## Worked example (this repo's session)
Song: 暖暖 — Before the beginning (Chinese original, N₂工作室). Analysed the **伴奏** mp3:
key = F# major; core chords F#, A#m, D#m, C#, B, G#m. Transposed down 6 semitones to C:
C, Am, Em, Dm, G, F. Delivered a 2-page chart: page 1 = 5 chord grids (C/Am/Em/Dm/G) + capo
6 note + Fmaj7 tip + structure summary; page 2 = 28 lyric lines with per-line chords. Capo
6 restores the original F# pitch for singing along.
