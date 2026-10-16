# Beginner-friendly (newbie) guitar sheet — Pillow recipe

Goal: produce a print-ready, A4, teaching-grade sheet for a user who does **not** read
music theory. Reproduces what audio2guitar.com / printed pop songbooks give (chord
diagrams + TAB + plain-language legend), built locally with Pillow.

## Why Pillow (not HTML)

This WSL environment has:
- NO headless chromium / `wkhtmltoimage` / `google-chrome`
- NO `weasyprint` / `cairosvg`
- `sudo apt-get install` may prompt for a password → do NOT pipe to `sudo -S` (blocked by
  the safety layer). Avoid needing root at all.
- PIL 12.x and matplotlib ARE preinstalled → use them.

CJK rendering:
```python
from PIL import Image, ImageDraw, ImageFont
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"   # WenQuanYi Zen Hei, index=0
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f_zh  = ImageFont.truetype(CJK, 22, index=0)
f_tab = ImageFont.truetype(MONO, 20)
cw = f_tab.getlength("0")   # monospace char width for column-aligned tab layout
```
If Chinese renders as boxes/tofu, the font path or `index` is wrong — fix before shipping.

## Page geometry

A4 @ 200 DPI = **1654 x 2339 px** per page, white background. Keep every page's last
drawn y within 2339 (add a little breathing room, e.g. stop by ~2280).

## Chord diagram geometry (one grid)

Leftmost vertical line = **6th string (low E)**, rightmost = **1st string (high e)**.
Draw 6 vertical lines + 4–5 horizontal fret lines; the top horizontal is a thick "nut".
Fret-dot placement by the chord's string-notation (low-E→high-e order):

| Chord | Notation (6→1) | Dots (diagram line from LEFT) | Open / mute above |
|-------|----------------|-------------------------------|-------------------|
| Em | 022000 | line2(string5) fret2, line3(string4) fret2 | 0,0,0,0,0 all open |
| D  | xx0232 | line4(G) fret2, line5(B) fret3, line6(e) fret2 | x,x,0,... |
| G  | 320003 | line1(lowE) fret3, line2(A) fret2, line6(e) fret3 | all 0 |
| C  | x32010 | line2(A) fret3, line3(D) fret2, line5(B) fret1 | x,0,0,0,0 |

Below each grid write finger notes in plain Chinese, e.g.
`5弦2品·中指 / 4弦2品·无名指`. Keep them simple — exact finger assignment is a guide,
not gospel (hand sizes differ).

## Rendering the TAB itself onto a page

The verified tab text is 6 ASCII lines per block (string1 top → string6 bottom). To make it
look like real tablature:
1. Draw 6 horizontal string lines across the page width.
2. Overlay the monospace tab characters on the correct string line, left-to-right at
   `cw` spacing, so it reads exactly like the source ASCII (numbers, `b/h/p/r/v/~`, `/`,
   `-`, `|`).
3. Scale the font down (22→20→18) or split a block's measures across lines if a block is
   too wide — never clip content off the page.
4. Section banners (dark blue `#1f3a5f`, white text) between groups: INTRO/MAIN THEME,
   INTERLUDE, THEME REPRISE, CLIMAX, OUTRO. Put a footer on each tab page:
   `标准调弦 E-A-D-G-B-E ｜ 调性 Em ｜ 不使用变调夹 ｜ 位置记谱（不含时值）`.

## Page-1 content blocks (dark-blue banner, white text)

- `① 先看懂这张谱（30秒速成）` — 6 lines = 6 strings; digits = fret; `0` = open.
  Yellow tip box (`#fff8e1` bg, `#e6a817` left border) for the finger-hint.
- `② 四个和弦（伴奏用，照着按）` — the 4 chord grids + `Em → D → G → C` loop line.
- `③ 符号说明（新手版·人话对照）` — translate every technique abbreviation into a plain
  sentence (bend, release, vibrato, hammer-on, pull-off, slide).
- Red warning box (`#fdecea` bg, `#d9534f` left border) with the candid difficulty note.

## Delegation note

This is a long, mechanical drawing job. It CAN be delegated to a subagent with the full
tab text + layout spec pasted in the prompt. But the subagent's "done / vision-verified"
self-report is NOT proof — **you must vision_analyze each page yourself** (confirm chords,
Chinese glyphs, first note matches source, no clipping) before delivering.

## Output set (this user)

Ship per-page PNGs plus the generator script, e.g.:
`新手谱_第1页_入门说明和和弦图.png`, `新手谱_第2页_...png`, `新手谱_第3页_...png`,
`新手谱_生成脚本.py`. Save to the Windows Desktop path the user named
(`/mnt/c/Users/<user>/Desktop/...`) using `write_file`/copy — not heredoc.
Offer a combined long strip (phone reading) or a pure-B&W ink-saver version as follow-ups.
