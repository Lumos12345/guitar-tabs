# -*- coding: utf-8 -*-
"""
Beginner-friendly CHORD sheet (弹唱谱) for
「暖暖 - Before the beginning」 (N2 工作室)
Chord/key analysis done from the backing track; simplified to C key
(original key F# major, capo 6 = original pitch).

Output: /tmp/song/page1.png, page2.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/tmp/song"
os.makedirs(OUT, exist_ok=True)
W, H = 1654, 2339
DARK = (31, 58, 95)
INK = (20, 20, 25)
GRAY = (130, 130, 138)
CHORDC = (176, 48, 48)
LIGHT = (235, 238, 242)
YEL_BG = (255, 248, 225); YEL_BR = (230, 168, 23)
RED_BG = (253, 236, 234); RED_BR = (217, 83, 79)
GRN_BG = (232, 245, 233); GRN_BR = (56, 142, 60)
WHITE = (255, 255, 255)

CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_fc = {}
def F(path, size, index=0):
    k = (path, size, index)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, index=index)
    return _fc[k]
def cjk(s): return F(CJK, s, 0)
def mono(s, b=False): return F(MONO_B if b else MONO, s)

def newpage():
    im = Image.new("RGB", (W, H), WHITE)
    return im, ImageDraw.Draw(im)

def banner(d, x, y, w, s, size=32, pad=14):
    f = cjk(size); bh = size + pad*2
    d.rounded_rectangle([x, y, x+w, y+bh], radius=8, fill=DARK)
    d.text((x+18, y+bh/2), s, font=f, fill=WHITE, anchor="lm")
    return y+bh

def para(d, x, y, s, font, maxw, lh=None, fill=INK):
    if lh is None: lh = int(font.size*1.5)
    cur = ""; lines=[]
    for ch in s:
        if ch=="\n": lines.append(cur); cur=""; continue
        if d.textlength(cur+ch, font=font) > maxw and cur:
            lines.append(cur); cur=ch
        else: cur+=ch
    if cur: lines.append(cur)
    for i,ln in enumerate(lines):
        d.text((x, y+i*lh), ln, font=font, fill=fill)
    return y + len(lines)*lh

def tip(d, x, y, w, h, bg, br, lines, size=24, pad=14):
    d.rounded_rectangle([x, y, x+w, y+h], radius=8, fill=bg, outline=br, width=3)
    f = cjk(size); yy = y+pad
    for ln in lines:
        d.text((x+16, yy), ln, font=f, fill=INK)
        yy += int(size*1.55)
    return y+h

def chord_diagram(d, x, y, name, frets, fingers, w=170):
    """frets: list of 6 (low->high) where -1=x(mute),0=open,n=fret. name shown above."""
    fN = cjk(34)
    d.text((x+w/2, y), name, font=fN, fill=CHORDC, anchor="ma")
    top = y+48
    sh = 26; nstr = 6; sw = w/ (nstr-1)
    # nut
    d.line([x, top, x+w, top], fill=INK, width=6)
    for i in range(nstr):
        xx = x + i*sw
        d.line([xx, top, xx, top+4*sh], fill=(90,90,98), width=2)
    for j in range(5):
        yy = top + j*sh
        d.line([x, yy, x+w, yy], fill=(90,90,98), width=2)
    # dots
    for i,fret in enumerate(frets):
        xx = x + i*sw
        if fret == -1:
            d.text((xx, top-16), "x", font=cjk(22), fill=GRAY, anchor="ma")
        elif fret == 0:
            d.text((xx, top-16), "o", font=cjk(22), fill=GRAY, anchor="ma")
        else:
            cy = top + (fret-0.5)*sh
            r = 9
            d.ellipse([xx-r, cy-r, xx+r, cy+r], fill=DARK)
    # finger text
    if fingers:
        d.text((x+w/2, top+4*sh+8), fingers, font=cjk(20), fill=(60,60,68), anchor="ma")

# chord fingerings in C key
CHORDS = {
  "C":   ( {"frets":[0,3,2,0,1,0], "fingers":"5弦3品·无名指"} ),
  "Am":  ( {"frets":[0,0,2,2,1,0], "fingers":"4弦2品·中指"} ),
  "F":   ( {"frets":[1,3,3,2,1,1], "fingers":"大横按(新手可用简化)"} ),
  "G":   ( {"frets":[3,2,0,0,0,3], "fingers":"6弦3品·无名指"} ),
  "Em":  ( {"frets":[0,2,2,0,0,0], "fingers":"5弦2品·中指"} ),
  "Dm":  ( {"frets":[-1,-1,0,2,3,1], "fingers":"3弦2品·食指"} ),
  "Fmaj7":({"frets":[-1,-1,3,2,1,0], "fingers":"简化F，超好按"} ),
}

def draw_chord(d, x, y, name, w=170):
    c = CHORDS[name]
    chord_diagram(d, x, y, name, c["frets"], c["fingers"], w=w)

# ---- lyric lines with chords (from analysis, in C key) ----
# format: (chord, lyric)  chord="" means same as previous (continue)
SONG = [
 ("C",   "全世界凝固在一刹那"),
 ("C",   "最后的那朵花随风落下"),
 ("C",   "世界漫长的坠落"),
 ("Am",  "在何时会停下"),
 ("C",   "原来成长的代价"),
 ("C",   "是不断失去吗"),
 ("Am",  "我搁浅在 失重的悬崖"),
 ("C",   "逆转的时间尽头 会有答案吗？"),
 ("Em",  "孤独的漫长旅程 我能走完吗？"),
 ("Dm",  "决心去守护 去改变 用 坚定的步伐"),
 ("C",   "不管什么代价 我能做到吗？"),
 ("C",   "会怀念小时候的盛夏"),
 ("Em",  "堆沙做城堡从不怕坍塌"),
 ("Em",  "时间不断地流走"),
 ("C",   "把一切都抛下"),
 ("C",   "难道成长的价码"),
 ("C",   "是接受失去吗"),
 ("C",   "这循环 的旅途 能否拨开 迷雾"),
 ("G",   "向星海方向"),
 ("G",   "追逐那束光"),
 ("G",   "逆转的时间尽头 冰雪在融化"),
 ("C",   "孤独的漫长旅程 我终于抵达"),
 ("C",   "世界蓬勃地 温暖地 又坚定地生长"),
 ("G",   "废墟之上 开满鲜花"),
 ("G",   "我们的故事开始 在晴朗盛夏"),
 ("C",   "全新的冒险旅程 马上要出发"),
 ("C",   "定下自由的 恢弘的 又勇敢的计划"),
 ("C",   "面向所有未来 让星光挥洒"),
]

def page1():
    im, d = newpage()
    M = 70; w = W-2*M
    y = 60
    d.text((W/2, y), "暖暖 — Before the beginning", font=cjk(46), fill=INK, anchor="ma")
    y += 66
    d.text((W/2, y), "零基础吉他弹唱谱 · 新手简化版", font=cjk(28), fill=GRAY, anchor="ma")
    y += 44
    d.text((W/2, y), "作词 郭倩倩 / 作曲 雅苏·刘冬 / 原唱 暖暖（N₂工作室）", font=cjk(20), fill=GRAY, anchor="ma")
    y += 44
    # info bar
    d.rounded_rectangle([M, y, W-M, y+54], radius=8, fill=LIGHT)
    d.text((W/2, y+27), "调性：C 调　|　只用 5 个超好按的开放和弦　|　变调夹夹第 6 品 = 原唱调", font=cjk(23), fill=INK, anchor="mm")
    y += 78

    # part 1: chords
    y = banner(d, M, y, w, "① 五个和弦（照着按，右手慢慢拨弦或扫弦都行）") + 22
    row = ["C","Am","Em","Dm","G"]
    cw = w/len(row)
    for i,nm in enumerate(row):
        x = M + i*cw + (cw-170)/2
        draw_chord(d, x, y, nm, w=170)
    y += 48 + 5*26 + 60
    d.text((M, y), "F 和弦（如果要用）：新手建议先按 Fmaj7（只按3弦2品+2弦1品+1弦空），比大横按简单得多。", font=cjk(22), fill=INK)
    y += 44
    y = tip(d, M, y, w, 130, GRN_BG, GRN_BR, [
        "变调夹怎么用：把变调夹夹在琴颈第 6 品（从琴头数第6格）。",
        "夹上后，用上面的 C/Am/Em/Dm/G 指法弹，音高就和原唱一样了，能跟着原唱一起唱。",
        "不夹变调夹直接弹也行，就是比原唱低 6 个音，自己弹唱完全够用。",
    ], size=22)
    y += 28

    # part 2 chord verse structure
    y = banner(d, M, y, w, "② 整首歌的和弦走向（记住这个循环就能弹全场）") + 22
    y = tip(d, M, y, w, 200, YEL_BG, YEL_BR, [
        "主歌：C → Am → C ……（基本围绕 C 和弦来回）",
        "预副歌：C → Am → Em → Dm → C",
        "副歌：C → G → C → G（副歌几乎是 C 和 G 轮流来）",
        "",
        "秘诀：整首歌主要就是 C 和弦，偶尔换 Am / Em / Dm / G。",
    ], size=23)
    y += 30
    d.text((M, y), "下一页：逐句歌词 + 对应的和弦（跟着换手就行）", font=cjk(24), fill=CHORDC)
    im.save(f"{OUT}/page1.png")
    return im

def page2():
    im, d = newpage()
    M = 60; w = W-2*M
    y = 50
    y = banner(d, M, y, w, "③ 逐句歌词 + 和弦（看歌词上方标注，唱到哪换哪个）") + 26
    fchord = cjk(30); flyr = cjk(27)
    lhy = 34
    for i,(ch,lyric) in enumerate(SONG):
        if y > H-140:
            break
        # show chord only when it changes
        if ch:
            d.text((M, y), ch, font=fchord, fill=CHORDC)
        else:
            pass
        d.text((M+150, y+2), lyric, font=flyr, fill=INK)
        y += lhy
        if ch and i < len(SONG)-1:
            pass
    # footer
    yy = H-90
    d.rounded_rectangle([M, yy, W-M, yy+60], radius=8, fill=LIGHT)
    d.text((W/2, yy+30), "原调 F# 大调 → 本谱 C 调指法 + 变调夹6品 ｜ 弹法：左手换和弦，右手每拍往下扫", font=cjk(22), fill=INK, anchor="mm")
    im.save(f"{OUT}/page2.png")
    return im

if __name__ == "__main__":
    page1(); page2()
    print("done")
