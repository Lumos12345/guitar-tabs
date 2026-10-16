# Audio → key & chord analysis (pure numpy)

For songs with **no published tab** where the user has the audio (often a `.mp3` + `.lrc`).
This detects KEY and CHORD PROGRESSION — it is NOT note-level tab transcription (that stays
forbidden). Key/chord detection is robust on pop/singer-songwriter material.

## Why not librosa
`pip install librosa` here pulls numba/llvmlite and can take many minutes and still trip
PEP 668 (`--break-system-packages` needed). numpy alone is enough. scipy is handy but not
required. `scripts/chord_analyze.py` is dependency-light (numpy + ffmpeg only).

## Pipeline

1. Decode to mono 22.05 kHz wav:
   ```bash
   ffmpeg -v error -i "song.mp3" -ac 1 -ar 22050 -y out.wav
   ```
   **Prefer the 伴奏 / instrumental / backing version if it exists** — the vocal mix
   smears the chroma badly. A backing track makes key + chords far cleaner.

2. STFT → chroma. Frame with a Hann window (win=8192, hop=4096 at 22.05 kHz), rFFT,
   fold bins 70–2500 Hz onto the 12 pitch classes (`round(midi) % 12`), sum energy per
   class, `log1p` compress, normalise each frame to sum 1.

3. Chord match. Build 12 major + 12 minor triad templates (root, third, fifth weighted
   ~[1, 0.85, 0.9]). Score each window by **cosine similarity** to every template; take the
   argmax. Aggregating ~2 s windows over the frame axis is stable enough.

4. Key estimate. Average the global chroma and correlate against Krumhansl-style
   major/minor key profiles (weights [1,.5,1,.5,1,.5,.5] on the diatonic degrees). The top
   candidate is the key. **Sanity-check**: the detected key's diatonic chords should match
   the detected chord set. (Example: key F# major ✓ chords F#, A#m, D#m, C#, B, G#m.)

5. Emit the sequence. Print per-2s chord, collapsing repeats. Cross-check against the
   lyric structure: verse often loops I–vi, chorus often I–V.

## LRC-synced per-line chord chart

If a `.lrc` exists:
- Header lines look like `{"t":0,"c":[{"tx":"演唱: "},{"tx":"暖暖"}]}` → title/artist/
  lyricist/composer. Read them to learn the real song identity before anything else.
- Lyric lines are `[mm:ss.xx]text`. Parse to `(t_seconds, text)`.
- For each line, average the chroma over `[t_i, t_{i+1})` and pick the best chord.
- Result: a per-line `和弦 + 歌词` chart — exactly what a beginner needs ("唱到哪换哪个").

## Beginner key transposition / capo

Then transpose the detected key to C (or G) and drop to open chords only:
- capo fret = semitone distance from target key to source key (C→F# = 6 ⇒ capo 6).
- map chords by degree. F# major (I=F#, ii=G#m, iii=A#m, IV=B, V=C#, vi=D#m) → C major:
  F#→C, G#m→Dm, A#m→Em, B→F, C#→G, D#m→Am.
- deliver the C-key sheet + a plain-language capo line. Suggest Fmaj7 as the beginner stand-in
  for F (the one barre that's hard to avoid).

## Rendering the sheet
Draw it with the same Pillow recipe as `beginner-tab-image.md` (A4 1654×2339, wqy-zenhei CJK,
chord grids + lyric lines with the chord name printed above/left of each line). Vision-verify.

## Caveats
- Voicings/inversions are not detected — only the chord root+quality. That's fine for a
  beginner strumming chart.
- Dense jazz/classical harmony will misclassify; pop is reliable.
- Always state the source ("analysed from your backing track") so the user knows it's derived,
  not a published transcription.
