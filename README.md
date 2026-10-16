# guitar-tabs

A Hermes Agent skill for retrieving **real guitar tabs / chords / notation** for a song,
analyzing audio to get key + chord progression, transposing hard keys into beginner-friendly
open chords, and rendering print-ready tab / chord-chart images.

## What it covers

- **Retrieve real tabs** from Ultimate Guitar (JSON-blob extraction, Cloudflare fallback)
  and Songsterr (metadata).
- **Audio → key & chord analysis** with pure numpy (no librosa needed): STFT → chroma →
  triad-template matching → Krumhansl-style key detection, plus LRC-synced per-line chord
  charts.
- **Beginner key transposition** — move hard keys (F#, etc.) into C/G major so only open
  chords remain, and compute the capo fret to get back to the original pitch.
- **Rendering**:
  - Professional B&W tab images with **LilyPond**.
  - Beginner-friendly teaching sheets (chord diagrams + how-to-read-TAB + plain-language
    legend) and **弹唱谱** (lyric + chord charts) with **Pillow**.

## Ground rules encoded in the skill

- **Never fabricate a tab from audio.** Note-level transcription is unreliable; retrieve a
  real, human-verified tab or do key/chord *detection* only.
- **Never infer the song from its title alone.** Confirm from the attached file / `.lrc`
  before building anything — a same-named famous song is a classic trap.

## Layout

```
SKILL.md                              # main skill instructions
references/
  ultimate-guitar-extraction.md       # UG search → fetch → parse → clean
  lilypond-tab-images.md              # LilyPond tab rendering recipe
  beginner-tab-image.md               # Pillow newbie-sheet recipe
  audio-chord-analysis.md             # numpy chroma/key/chord detector + capo transposition
scripts/
  chord_analyze.py                    # runnable detector: python3 chord_analyze.py <audio>
```

## Usage

```bash
python3 scripts/chord_analyze.py /path/to/song.mp3
# prints global chroma, top key candidates, and a per-2s chord track
```

## License

MIT — see [LICENSE](LICENSE).

## Author

Built with [Hermes Agent](https://hermes-agent.nousresearch.com).
