#!/usr/bin/env python3
"""Render 4-layer beginner 弹唱谱 with CORRECT pagination (measure-then-flow)."""
import json, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1654, 2339
M = 90
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

RED = (200, 30, 40)
BLACK = (20, 20, 20)
GREY = (110, 110, 110)
LIGHT = (225, 225, 225)

def cjk(sz): return ImageFont.truetype(CJK, sz)
def mono(sz): return ImageFont.truetype(MONO, sz)

CHORDS = ["C","Dm","Em","Fmaj7","G","Am"]
SHAPES = {
    "C":     ([-1,3,2,0,1,0],[0,3,2,0,1,0],1),
    "Dm":    ([-1,-1,0,2,3,1],[0,0,0,2,3,1],1),
    "Em":    ([0,2,2,0,0,0],[0,2,3,0,0,0],1),
    "Fmaj7": ([-1,-1,3,2,1,0],[0,0,3,2,1,0],1),
    "G":     ([3,2,0,0,0,3],[2,1,0,0,0,3],1),
    "Am":    ([-1,0,2,2,1,0],[0,0,2,3,1,0],1),
}
FINGER = {
    "C":"食指1弦1品·中指2弦2品·无名指3弦3品",
    "Dm":"食指3弦2品·中指1弦1品·无名指2弦3品",
    "Em":"中指5弦2品·无名指4弦2品",
    "Fmaj7":"食指2弦1品·中指3弦2品·无名指4弦3品",
    "G":"中指6弦3品·无名指5弦2品·小指1弦3品",
    "Am":"食指2弦1品·中指4弦2品·无名指3弦2品",
}

def draw_chord(d, x, y, name, scale=1.0):
    frets, fingers, base = SHAPES[name]
    gw, gh, nfret = int(78*scale), int(112*scale), 4
    top = y + 26
    step = gw/5.0
    d.line([(x, top), (x+gw, top)], fill=BLACK, width=4)
    for i in range(6):
        xx = x + i*step
        d.line([(xx, top), (xx, top+gh)], fill=BLACK, width=2)
    for j in range(nfret+1):
        yy = top + j*gh/nfret
        d.line([(x, yy), (x+gw, yy)], fill=BLACK, width=2)
    for i in range(6):
        xx = x + i*step
        f = frets[i]
        if f == -1:
            d.line([(xx-5, top-19), (xx+5, top-9)], fill=BLACK, width=2)
            d.line([(xx-5, top-9), (xx+5, top-19)], fill=BLACK, width=2)
        elif f == 0:
            d.ellipse([xx-5, top-19, xx+5, top-9], outline=BLACK, width=2)
    r = max(6, int(9*scale))
    fnum = mono(max(9, int(12*scale)))
    for i in range(6):
        f = frets[i]
        if f and f > 0:
            cy = top + (f-base+0.5)*gh/nfret
            cx = x + i*step
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=BLACK)
            if fingers[i]:
                s = str(fingers[i])
                tw = d.textlength(s, font=fnum)
                d.text((cx-tw/2, cy-6*scale), s, font=fnum, fill="white")
    fnt = cjk(int(26*scale))
    nw = d.textlength(name, font=fnt)
    d.text((x + gw/2 - nw/2, y-2), name, font=fnt, fill=RED)
    return gw, gh+30

def draw_fingerpick(d, x, y, w):
    d.text((x, y), "右手分解和弦 53231323", font=cjk(24), fill=BLACK)
    y0 = y + 46; lh = 104
    for s in range(6):
        yy = y0 + s*lh/6
        d.line([(x+30, yy), (x+w, yy)], fill=LIGHT, width=2)
        d.text((x, yy-8), ["6","5","4","3","2","1"][s], font=mono(15), fill=GREY)
    pat = [(4,"T"),(2,"2"),(1,"1"),(2,"2"),(0,"3"),(2,"2"),(1,"1"),(2,"2")]
    sw = (w-60)/len(pat)
    for i,(st,fg) in enumerate(pat):
        cx = x + 40 + sw*(i+0.5)
        cy = y0 + st*lh/6
        d.ellipse([cx-12, cy-12, cx+12, cy+12], fill=RED)
        tw = d.textlength(fg, font=cjk(16))
        d.text((cx-tw/2, cy-9), fg, font=cjk(16), fill="white")
        d.text((cx-4, y0+lh+10), str(i+1), font=mono(14), fill=GREY)
    d.text((x+30, y0+lh+34), "T=拇指(弹低音弦)  1=食指  2=中指  3=无名指", font=cjk(19), fill=GREY)
    return lh + 78

def draw_strum(d, x, y, w):
    d.text((x, y), "右手扫弦  ↓ ↓↑ ↑↓↑", font=cjk(24), fill=BLACK)
    y0 = y + 48
    slots = ["↓","↓","↑","·","↑","↓","↑","·"]
    beats = ["1","&","2","&","3","&","4","&"]
    sw = w/len(slots)
    for i,s in enumerate(slots):
        cx = x + sw*(i+0.5)
        tw = d.textlength(beats[i], font=mono(15))
        d.text((cx-tw/2, y0-26), beats[i], font=mono(15), fill=BLACK if i%2==0 else GREY)
        if s == "·":
            d.ellipse([cx-4, y0+24, cx+4, y0+32], fill=GREY)
            continue
        col = RED if s=="↓" else (30,90,190)
        tw = d.textlength(s, font=cjk(46))
        d.text((cx-tw/2, y0), s, font=cjk(46), fill=col)
    for i in range(1, 5):
        xx = x + sw*i*2
        d.line([(xx, y0-4), (xx, y0+64)], fill=LIGHT, width=3)
    return 104

SYSTEM_H = 232
def draw_system(d, x, y, w, item):
    chords = item["chords"]; lyric = item["line"]; jp = item["jp"]
    ytop = y
    f_ch = cjk(27); f_lyr = cjk(28); f_jp = cjk(25)
    n = max(1, len(lyric))
    char_w = min(30, (w-10)/n)
    positions = [x + i*char_w for i in range(n)]

    if chords:
        d.text((positions[0], y), chords[0], font=f_ch, fill=RED)
    if len(chords) > 1:
        d.text((positions[n//2], y), chords[1], font=f_ch, fill=RED)
    y += 40

    tab_h = 90
    for s in range(6):
        yy = y + s*tab_h/6
        d.line([(x, yy), (x+w, yy)], fill=(185,185,185), width=2)
        d.text((x-24, yy-7), ["e","B","G","D","A","E"][s], font=mono(14), fill=GREY)
    pat = [0,3,1,3,0,3,1,3]
    nslot = 8
    for i in range(nslot):
        cx = x + 26 + (w-52)*(i+0.5)/nslot
        yy = y + pat[i]*tab_h/6
        d.line([(cx-6, yy-6), (cx+6, yy+6)], fill=BLACK, width=2)
        d.line([(cx-6, yy+6), (cx+6, yy-6)], fill=BLACK, width=2)
    y += tab_h + 12

    if jp:
        toks = jp.split(" ")
        stepj = min(50, (w-20)/max(len(toks),1))
        for i,tk in enumerate(toks):
            d.text((x+10 + i*stepj, y), tk, font=f_jp, fill=(30,60,160))
        d.line([(x, y+36), (x+w, y+36)], fill=(205,220,245), width=1)
    y += 44

    lx = x
    for ch in lyric:
        if lx + f_lyr.getlength(ch) > x + w:
            break
        d.text((lx, y), ch, font=f_lyr, fill=BLACK)
        lx += char_w
    y += 44

    mm = int(item["t"]//60); ss = item["t"]-mm*60
    d.text((x+w-70, ytop-16), f"{mm}:{ss:04.1f}", font=mono(13), fill=(195,195,195))
    d.line([(x, ytop+SYSTEM_H-24), (x+w, ytop+SYSTEM_H-24)], fill=(242,242,242), width=1)
    return SYSTEM_H

def page1(data, outpath):
    img, d = Image.new("RGB",(W,H),"white"), None
    d = ImageDraw.Draw(img)
    y = 70
    d.text((M,y), "Before the Beginning", font=cjk(52), fill=BLACK); y += 74
    d.text((M,y), "Performed by Nikki  ·  初学者弹唱谱（4层）", font=cjk(26), fill=GREY); y += 56
    d.rectangle([M,y,W-M,y+62], outline=BLACK, width=3)
    d.text((M+20,y+16), "调性 C大调   |   拍号 4/4   |   变调夹 Capo 6（夹6品＝原调F#，可跟唱）", font=cjk(24), fill=BLACK)
    y += 86
    d.text((M,y), "① 六个和弦（全部开放和弦，新手友好）", font=cjk(26), fill=BLACK); y += 44
    cx = M
    for name in CHORDS:
        gw,gh = draw_chord(d, cx, y, name)
        cx += gw + 58
    y += 176
    for name in CHORDS:
        d.text((M,y), f"{name}：{FINGER[name]}", font=cjk(19), fill=GREY); y += 27
    y += 8
    d.text((M,y), "※ F 和弦用 Fmaj7 代替：不用横按，新手也能按响", font=cjk(22), fill=RED); y += 52
    d.text((M,y), "② 右手节奏型", font=cjk(26), fill=BLACK); y += 42
    y += draw_fingerpick(d, M+20, y, W-2*M-60) + 4
    y += draw_strum(d, M+10, y, W-2*M-20) + 10
    by0 = y; by1 = y+186
    d.rectangle([M,by0,W-M,by1], outline=RED, width=3)
    d.text((M+18,by0+12), "③ 怎么弹（新手要点）", font=cjk(24), fill=RED)
    tips = [
      "主歌：用「分解和弦 53231323」，慢速稳定，每小节换一个和弦。",
      "副歌：用「扫弦 ↓ ↓↑ ↑↓↑」，节奏更饱满。",
      "换和弦要提前——右手不停，左手提前一个音换好。",
      "先慢速练熟左手换和弦，再加入右手节奏。",
      "变调夹夹第6品＝原调；不夹则低6个半音，单独练习也行。",
    ]
    ty = by0+52
    for t in tips:
        d.text((M+22,ty), "· "+t, font=cjk(20), fill=BLACK); ty += 26
    y = by1+26
    d.text((M,y), "④ 4层怎么看：红=和弦(左手) | TAB=右手 | 蓝数字=简谱(旋律仅供参考) | 黑=歌词", font=cjk(18), fill=GREY)
    d.text((W/2-8, H-56), "1", font=cjk(24), fill=GREY)
    img.save(outpath); return outpath

def page2(data, outpath_base):
    """Flow systems across pages with real measurement, no clipping."""
    img = Image.new("RGB",(W,H),"white"); d = ImageDraw.Draw(img)
    y = 70
    d.text((M,y), "Before the Beginning — 弹唱谱", font=cjk(34), fill=BLACK); y += 54
    d.text((M,y), "C大调 · Capo 6 · 主歌分解53231323 / 副歌扫弦↓ ↓↑ ↑↓↑", font=cjk(20), fill=GREY); y += 40
    d.line([(M,y),(W-M,y)], fill=BLACK, width=2); y += 22

    w = W-2*M
    bottom = H-90
    pages = []
    idx = 0
    pageno = 2
    while idx < len(data):
        if y + SYSTEM_H > bottom:
            d.text((W/2-8, H-56), str(pageno), font=cjk(24), fill=GREY)
            fn = outpath_base.replace(".png", f"_p{pageno}.png")
            img.save(fn); pages.append(fn)
            pageno += 1
            img = Image.new("RGB",(W,H),"white"); d = ImageDraw.Draw(img)
            y = 70
            d.text((M,y), f"Before the Beginning — 弹唱谱（续 {pageno-1}）", font=cjk(30), fill=BLACK); y += 46
            d.line([(M,y),(W-M,y)], fill=BLACK, width=2); y += 22
        draw_system(d, M, y, w, data[idx])
        y += SYSTEM_H
        idx += 1
    d.text((W/2-8, H-56), str(pageno), font=cjk(24), fill=GREY)
    fn = outpath_base.replace(".png", f"_p{pageno}.png")
    img.save(fn); pages.append(fn)
    return pages

if __name__ == "__main__":
    data = json.load(open('/tmp/sheet_data.json'))
    outdir = os.environ.get("OUTDIR", "./out")
    os.makedirs(outdir, exist_ok=True)
    # clean old outputs
    for f in os.listdir(outdir):
        if f.endswith(".png"):
            os.remove(os.path.join(outdir,f))
    p1 = page1(data, os.path.join(outdir,"Before_the_Beginning_新手弹唱谱_01.png"))
    pages = page2(data, os.path.join(outdir,"Before_the_Beginning_新手弹唱谱_02.png"))
    print("page1:", p1)
    for p in pages: print("page:", p)
