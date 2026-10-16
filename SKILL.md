---
name: guitar-tabs
description: "Retrieve real guitar tabs/chords/notation for a song from Ultimate Guitar, Songsterr, etc."
version: 1.0.0
author: agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Music, Guitar, Tabs, Chords, Scraping, UltimateGuitar, Songsterr]
---

# guitar-tabs

Fetch real, human-transcribed guitar tab / chord / notation for a named song. Covers
Ultimate Guitar (UG) and Songsterr, plus how to reason about what's achievable.

## When to use

The user asks for "the guitar tab / chords / sheet for <song>", attaches an audio file
and asks for a tab, or wants to play a song. Works for any song with a published tab.

## CRITICAL #1: confirm WHICH song before doing any work

Song titles are ambiguous. A title alone ("Before the Beginning") can point at a famous
piece you recognise (John Frusciante) while the user means a completely different local
track. **Do not infer the song from the title, from memory, or from a same-named famous
song.** This has burned a whole session: an entire multi-page tab was built for the wrong
song because the title matched a well-known track.

Before generating anything, disambiguate:
- If the user attached a file or gave a path, **that file IS the song** — analyse/open it,
  read its tags (.lrc/.mp3 metadata), never substitute a song you already know.
- A `.lrc` next to the audio carries title/artist/lyricist/composer inside its header lines
  (`{"t":...,"c":[{"tx":"演唱: ..."}]}`) — read it; it names the real song.
- If the title is ambiguous and there's no attached file, ask which song (one line) before
  spending effort. Cheap clarify > hours of wrong output.

## CRITICAL #2: do NOT auto-transcribe audio into tabs

Given an audio file (.m4a/.mp3/.wav) and "make me a tab", do NOT attempt to invent tabs
from listening or from memory. Automatic polyphonic/fingerstyle transcription is
unreliable and a fabricated tab wastes the user's time. State this limit plainly, then
retrieve a **real, human-verified** transcription instead. The only sanctioned
audio-to-MIDI route is Spotify Basic Pitch (see references) and it is a rough draft at
best — offer it only for simple single-note material and label it a draft.

## Primary path: Ultimate Guitar (UG)

UG tab pages embed the ENTIRE tab text as an HTML-escaped JSON blob in a
`data-content="..."` attribute. This is the reliable, scriptable path. No login needed for
public tabs.

### Steps

1. **Search** to find the tab URL and version ids:
   ```bash
   curl -sL --max-time 30 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" \
     "https://www.ultimate-guitar.com/search.php?search_type=title&value=<urlenc song+artist>" \
     -o ugsearch.html
   ```
   Results live in `data-content` too. Grep for `tab_url` to list versions, and read
   `rating` + `votes` + `type` (Tabs / Chords / Official / Pro / Bass) to pick the best.
   Prefer a high-rated `Tabs` version; `Official` is often gated behind Pro.

2. **Fetch the chosen tab page**:
   ```
   https://tabs.ultimate-guitar.com/tab/<artist>/<slug>-tabs-<id>
   ```
   Note: the `<id>` in the URL is the tab id (e.g. 1412535), NOT the song id.

3. **Extract the blob** (Python, run via a heredoc):
   ```python
   import re, html, json
   s = open('ugtab.html', encoding='utf-8', errors='replace').read()
   m = re.search(r'data-content="(.*?)">', s, re.S)
   d = json.loads(html.unescape(m.group(1)))
   tv = d['store']['page']['data']['tab_view']
   tab = d['store']['page']['data']['tab']
   content = tv['wiki_tab']['content']      # the raw tab text (has \r\n, [tab]...[/tab] blocks, &lt; entities)
   tuning  = tv['meta']['tuning']           # {'name':'Standard','value':'E A D G B E'}
   print(tab['song_name'], '/', tab['artist_name'], '|', 'v'+str(tab['version']), '|', tuning['value'])
   print(content)
   ```
   Key JSON path: `store.page.data.tab_view.wiki_tab.content`. Tuning is at
   `tab_view.meta.tuning`. See `references/ultimate-guitar-extraction.md` for a full
   worked example and the post-processing (strip `[tab]` markers, `html.unescape`,
   normalize CRLF, drop the tabber's personal notes).

### Cleanup for delivery
- Normalize `\r\n` → `\n`, `html.unescape()` (tab blocks contain `&lt;` `&gt;` `&amp;`).
- Tab sections are wrapped in `[tab]...[/tab]`; unwrap them into plain 6-line staves.
- The area outside tab blocks is the tabber's prose/notes — usually drop it for delivery.
- Do NOT relabel sections with invented names (Intro/Chorus) unless the source labels them.

### Rate limits / Cloudflare (curl blocked → browser fallback)

UG begins returning **HTTP 429** after a few curl hits, then a Cloudflare
`"Just a moment..."` interstitial (title becomes `Just a moment...`, body has
`detected a challenge`). Changing User-Agent and sleeping does NOT clear it.

Fix: fall back to the **browser tool**, which passes the challenge. Then extract the
tab from the rendered DOM instead of the JSON blob:
```
browser_navigate  https://tabs.ultimate-guitar.com/tab/<artist>/<slug>-<type>-<id>
browser_console   expression: "JSON.stringify({t:document.title, pre:(document.querySelector('pre')||{}).innerText})"
```
The tab text is in the single `<pre>` element's `innerText` (already entity-decoded,
no JSON parsing needed). The `data-content` attribute is often NOT present on the
browser-rendered page even though curl sees it — don't rely on it in browser mode.
So: **curl first (cheap, gets the JSON blob); if 429/challenge, switch to browser.**

### Fetching a different track (chords / rhythm / bass / a specific version)

Each arrangement is its own tab page with its own id and a distinguishing slug word:
`-tabs-<id>`, `-chords-<id>`, `-bass-<id>`, `-guitar-pro-<id>`, `-official-<id>`.
To get the backing-chords track alongside the solo tab, search once, then fetch BOTH
the best `Tabs` version and the `Chords` version and merge them into one deliverable.
The chords page also carries `Capo:` (e.g. "No capo") and the key/tonality in its meta.

## Secondary path: Songsterr

Songsterr has a usable search API but the NOTE data is streamed to the browser and NOT
exposed via a simple REST call — treat it as good for **metadata only** (confirm the
song exists, get tuning, list the tracks/parts and their difficulty):

```bash
curl -sL -A "Mozilla/5.0" "https://www.songsterr.com/api/songs?pattern=<song+artist>"
# -> [{songId, artist, title, tracks:[{name,instrument,tuning,hash,difficulty}], ...}]
curl -sL -A "Mozilla/5.0" "https://www.songsterr.com/api/meta/<songId>"        # includes revisionId
curl -sL -A "Mozilla/5.0" "https://www.songsterr.com/api/meta/<songId>/<revisionId>"  # full meta incl. tracks
```
Tuning arrays are MIDI note numbers: `[64,59,55,50,45,40]` = standard EADGBE. Useful to
tell the user "Songsterr also has a rhythm/chords track" but retrieve the actual tab text
from UG.

## Audio → key & chord analysis (for songs with no published tab)

When the song is a local/original track with **no tab on UG/Songsterr** (the user has the
.mp3 and often a `.lrc`), you can still produce a usable chord sheet by analysing the audio.
This is NOT tab transcription — it's **key + chord-progression detection**, which is far
more robust than note-level transcription. Recipe in `references/audio-chord-analysis.md`;
the reusable script is `scripts/chord_analyze.py`.

Pipeline (pure numpy — no librosa needed; librosa's install is slow/fragile here):
1. Convert with ffmpeg: `ffmpeg -v error -i song.mp3 -ac 1 -ar 22050 -y out.wav`
   (or convert the **伴奏/backing** version — it analyses far cleaner than the vocal mix).
2. STFT → chroma (12 pitch-class energy), log-compressed + normalised per frame.
3. Match each frame/window against major/minor **triad templates** (cosine similarity).
4. Global chroma → key estimate via Krumhansl-style major/minor profile correlation.
5. Aggregate per 2s (or per lyric line) to a chord sequence; collapse to changes.

Reliability: good for pop/singer-songwriter; the detected key + chord set is trustworthy
even when exact inversions/voicings are not. Always sanity-check the key against the chords
(e.g. F# major → chords should be F#, A#m, D#m, C#, B, G#m) before shipping.

### LRC-synced chord chart
If a `.lrc` exists, parse `[mm:ss.xx]` lines, then analyse the chord over each lyric line's
time window → a **per-line chord chart**. Header lines (`{"t":..,"c":[..]}`) give
title/artist/lyricist. This yields a "唱到哪句换哪个和弦" sheet beginners can follow.

Header metadata lines are `{"t":<ms>,"c":[{"tx":"角色: "},{"tx":"名字"}]}`; lyric lines are
`[mm:ss.xx]歌词`. Use `re.match(r'\[(\d+):(\d+\.\d+)\](.*)', line)`; window each lyric line
from its timestamp to the NEXT line's timestamp. See `references/audio-chord-analysis.md`.

### Full chord-chart (弹唱谱) deliverable — pitch-deck layout
The beginner deliverable for a **vocal** song is a chord chart, produced as 2 PIL pages
(not the LilyPond tab, which is for instrumental note-level tab):

Page 1 — chords & instructions:
1. Title line `歌手 — 歌名`, subtitle "零基础吉他弹唱谱 · 新手简化版", credits line
   (作词/作曲/原唱) pulled from the .lrc header.
2. Info bar: `调性：C 调 | 只用 N 个超好按的开放和弦 | 变调夹夹第 K 品 = 原唱调`.
3. Banner `① 五个和弦` + a ROW of chord grids (reuse the chord-diagram geometry). Under
   each: plain-language finger note. Add the F→Fmaj7 beginner substitute callout.
4. Green tip box: capo explanation — capo K = original pitch (can sing along), no capo =
   K semitones lower (fine for solo practice).
5. Banner `② 整首歌的和弦走向` + yellow tip box summarising verse/pre-chorus/chorus loops
   and the "整首歌主要就是 X 和弦" takeaway.

Page 2 — lyrics + chords, one lyric line per row, chord name in red at the row's left
(showing the chord only when it CHANGES, or repeat for clarity). Footer repeats the
transposition (`原调 X → 本谱 C 调指法 + 变调夹 K 品`) and the strum instruction.

Chords with no open voicing (F) get an **Fmaj7** substitute; state it on the page.

## Beginner key transposition (make hard keys playable)

Published keys are often full of barre chords (F#, A#m, D#m…) that a beginner cannot play.
Detect the key, then **transpose to C or G major** so only open chords remain, and tell the
user the **capo position** to get back to the original pitch:

- Semitones between source key and target key = capo fret. C→F# is 6 semitones ⇒ capo 6.
- Map each chord by scale degree, not by name. F# major (I F#, ii G#m, iii A#m, IV B, V C#,
  vi D#m) → C major: F#→C, G#m→Dm, A#m→Em, B→F, C#→G, D#m→Am.
- Deliver a **C-key sheet with only open chords** (C, Am, Em, Dm, G …), plus a plain-language
  capo note: "capo 6 = same as the original, can sing along; no capo = 6 semitones lower,
  fine for solo practice." Offer a lower-capo alternative (capo 2–3) if 6 is too high to fret.
- Suggest a beginner substitute for F (the one unavoidable barre): use **Fmaj7** instead.

## Rendering tab to a professional B&W image (LilyPond)

When the user wants a **print-ready tab image** (they show a reference JPG of a printed
tab book / Songsterr page and say "make one like this"), render with **LilyPond**:
```bash
sudo apt-get install -y lilypond
lilypond -dbackend=eps --png -dresolution=300 file.ly   # A4 → 2480x3508 px/page
```
Key gotchas (full recipe in `references/lilypond-tab-images.md`):
- `-dbackend=eps --png` is required for raster; multi-page scores emit ONE PNG PER PAGE
  (`file-page1.png`, ...) — combine manually if a single image is wanted.
- `stringTunings` must be ascending (string 6 → string 1): standard = `#'(e a d g b e')`.
  Wrong order → "negative fret" errors / wrong frets.
- Rhythm-less ASCII tab: lay each fret out as a uniform **eighth note**, and label the
  footer `Notation: eighth notes (positions only)`. Never invent a rhythm.
- Preserve technique markers as text (`^\markup \italic "b17"`) — lossless.
- **ALWAYS vision-verify the rendered pages** (6-line staff? correct frets? labels? no
  garble?) before declaring success; "compilation successful" alone is not proof.

## Beginner-friendly ("newbie") tab image — reproduce audio2guitar locally

When the user says "a tab a beginner who doesn't read music theory can use" and/or shows
reference JPGs of a printed pop guitar score (chords + TAB + jianpu/简谱 + lyrics), the
deliverable is NOT the raw LilyPond tab — it's a **teaching sheet**. If audio2guitar.com
is unavailable (Google-login only, blocked in China), build it locally instead of routing
the task through the service.

Render with **Pillow (PIL)**, NOT HTML: this environment has no headless browser,
`wkhtmltopdf`, or `weasyprint`, and `sudo apt-get` may require a password you must not
guess (piping to `sudo -S` is blocked). PIL + matplotlib are already installed and need
no root. Draw everything programmatically at A4 @ 200 DPI = **1654 x 2339 px/page**.

CJK font: `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` (index=0) renders Simplified
Chinese. Monospace for tab digits: `/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`;
compute char width with `font.getlength("0")` and lay characters left-to-right on the
correct string line. Full recipe (chord-diagram geometry, page layout, the tab-rendering
alignment trick) in `references/beginner-tab-image.md`.

A "newbie-friendly" sheet contains, in order:
1. Title + subtitle (artist · album/year) + a tuning/key/capo info bar.
2. **How to read TAB in 30 seconds**: 6 horizontal lines = 6 strings (top = thinnest),
   digits = which fret, `0` = open string. A small labelled 6-line visual sells it.
3. **Chord diagrams** (Em/D/G/C etc.) as fretboard grids — leftmost line = 6th string,
   dots on fretted positions, `0`/`x` above open/muted strings, plain-language finger
   notes below each. Show the backing-chord loop as `Em → D → G → C`.
4. **Symbol legend in plain language** — translate `b` (bend: push the string to raise the
   pitch, e.g. `15b17` = fret 15 → bend up to the pitch of fret 17), `r` (release), `v/vib`
   (vibrato), `h` (hammer-on), `p` (pull-off), `/` (slide) into human sentences, not jargon.
5. A **candid difficulty warning** for genuinely hard pieces (dense bends/vibrato): tell
   the beginner to learn note positions first, then add bends, then vibrato.
6. The TAB itself (you can reuse the verified LilyPond/ASCII tab; don't retranscribe).

Always vision-verify each rendered page (chords correct? Chinese renders as real glyphs,
not tofu boxes? first block's first note matches source? nothing clipped?).

## audio2guitar.com (the user's preferred newbie-tab tool)

When the user's stated goal for "tabs a beginner can read" points at **audio2guitar.com** —
an AI audio→tabs/chords/lyrics service — note it is **Google-login only** (no
email/password tab). You cannot register a Google account for the user (phone SMS +
reCAPTCHA + identity are unavoidable, and there is no programmatic signup route) — say so
plainly and point them at `accounts.google.com/signup` (China +86 numbers receive the code;
mainland users need a proxy/住宅IP to reach Google at all). Offer the **local Pillow-rendered
newbie sheet** (see above) rather than routing the whole task through the third-party
service.

## Delivery preference (this user)

- Default to **printing the tab in the chat** as a plain-text code block. When offered
  print-vs-save, this user chose print. Confirm before writing files.
- **Ask what deliverable format the user wants before assuming** — this user has wanted
  plain text, pure-ASCII text, per-track splits, AND a rendered image across a single
  session. Don't guess; a quick clarify saves rework.
- Output plain text (CLI user) — no MEDIA: tags.
- Cite the source (site, version, tabber, rating/vote count) so the user can trust it.
- **Offer BOTH a freeform version and a pure-ASCII version.** This user works on Windows
  and asked for ASCII-safe + separate-per-track files. Produce a set like:
  `<song>_吉他谱.txt` (full, may contain Chinese annotations), `<song>_吉他谱_ASCII.txt`
  (pure ASCII, all Chinese→English, safe for Notepad/printing), and a per-track split
  (`<song>_独奏谱.txt` / solo-only). Verify ASCII: assert no char with `ord(c) > 127`.
- When writing files on WSL, save to the Windows Desktop path the user named (e.g.
  `/mnt/c/Users/<user>/Desktop/...`). Use `write_file` (not heredoc) — heredoc file
  writes have been denied by this user before.

## Pitfalls
- UG `data-content` is HTML-entity-escaped; you MUST `html.unescape` before `json.loads`.
- The `data-content` regex `data-content="(.*?)">` works because the attribute is the last
  one before `>`; anchor with `re.S`.
- Google/DuckDuckGo HTML search often times out or is JS-blocked from the CLI — go
  straight to the site's own search endpoint with curl.
- Browser tools are overkill/slow for these static pages; curl + the JSON blob is faster
  and more reliable — but curl gets 429/Cloudflare-throttled after a few requests, so keep
  the browser as the fallback (see "Rate limits" above).
- Don't confuse tab id and song id; the URL id is the tab id.
- UG "Official" tabs may require login/Pro — fall back to the best-voted community Tab.
- **Delegation for heavy conversions**: turning a 20+ block tab into LilyPond is a long,
  mechanical job — delegate it to a subagent with the full tab text pasted in the prompt,
  then VERIFY the subagent's output yourself (vision-check the rendered pages; don't trust
  its "done / vision-verified" self-report).
- **Never fabricate a tab from audio.** Reiterated because it is the core failure mode
  this skill exists to prevent. (Key/chord *detection* from audio IS allowed — see the
  audio-analysis section — but note-level tab is not.)
- **Never infer the song from its title alone.** Confirm from the attached file / .lrc /
  the user before building anything. A same-named famous song is a trap.
- When the user gives local file paths, open THOSE files — don't fetch an equivalent-looking
  song from the web.

## References
- `references/ultimate-guitar-extraction.md` — full worked example (search → fetch →
  parse → clean) with real field values, plus the Basic Pitch audio→MIDI fallback recipe.
- `references/lilypond-tab-images.md` — full LilyPond recipe: install, render command,
  stringTunings quirk, rhythm-less→eighth-notes rule, section labels, vision verification.
- `references/beginner-tab-image.md` — Pillow recipe for the newbie teaching sheet: CJK
  font paths, chord-diagram geometry, TAB overlay alignment, page-1 content blocks,
  delegation + self-verification notes.
- `references/audio-chord-analysis.md` — pure-numpy chroma/key/chord detector for songs
  with no published tab: ffmpeg command, triad-template matching, key estimation,
  LRC-synced per-line chord chart, and the beginner key-transposition / capo recipe.
- `scripts/chord_analyze.py` — runnable detector: `python3 chord_analyze.py <audio>`
  prints global chroma, top key candidates, and a per-2s chord track.
