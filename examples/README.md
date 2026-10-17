# Examples

Three end-to-end worked examples, each in its own folder, showing the skill's main
pipelines:

| Folder | Song | Pipeline |
|--------|------|----------|
| [`01-frusciante-btb/`](01-frusciante-btb/) | John Frusciante — *Before the Beginning* (instrumental) | retrieve real tab (UG/Songsterr) → LilyPond tab image + Pillow beginner sheet |
| [`02-nuan-btb/`](02-nuan-btb/) | 暖暖 — *Before the beginning* (Chinese pop vocal) | audio → key/chord analysis → transpose to C → capo calc → Pillow 弹唱谱 |
| [`03-nikki-btb/`](03-nikki-btb/) | Nikki — *Before the Beginning* (English pop vocal) | burned-in subtitle OCR → lyrics+timestamps; audio → F#→C transpose → 4-layer 弹唱谱 (chords + TAB + 简谱 + lyrics) |

All three share a name on purpose — a live demonstration of the skill's
**"never infer the song from its title"** rule. Same title, three completely different
songs, three completely different deliverables.

Example 03 also covers two techniques the first two don't: recovering lyrics and
timestamps by OCR from **burned-in video subtitles** (no soft subtitle stream), and
rendering a **4-layer** sheet with the 简谱 melody row.

Each folder has its own `README.md` with the story, the files, and reproduce steps.
