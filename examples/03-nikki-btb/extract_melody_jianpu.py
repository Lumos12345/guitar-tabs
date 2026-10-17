#!/usr/bin/env python3
"""Melody extraction v3: octave-continuity corrected + smoothed, realistic vocal band.
Produces jianpu per line with optional underline info (duration cells).
"""
import numpy as np, wave, subprocess, re, json, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else "song.m4a"
WAV = "/tmp/mel_src.wav"

def read_wav(path):
    with wave.open(path,'rb') as w:
        nch,sw,fr,n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        d = w.readframes(n)
    a = np.frombuffer(d, dtype=np.int16).astype(np.float32)/32768.0
    if nch==2: a = a.reshape(-1,2).mean(axis=1)
    return a, fr

a, fr = read_wav(WAV)
win, hop = 2048, 512
n = 1 + (len(a)-win)//hop
lag_min = max(1, int(fr/700.0))   # upper 700 Hz (soprano-ish)
lag_max = min(win-2, int(fr/110.0))  # lower 110 Hz (A2)

f0s = np.zeros(n); confs = np.zeros(n)
for i in range(n):
    seg = a[i*hop:i*hop+win].astype(np.float64)
    seg -= seg.mean()
    if float(np.dot(seg,seg)) < 1e-6: continue
    ac = np.correlate(seg, seg, mode='full')[win-1:]
    if ac[0] != 0: ac /= ac[0]
    hi = min(len(ac)-1, lag_max)
    if hi <= lag_min: continue
    k = int(np.argmax(ac[lag_min:hi])) + lag_min
    confs[i] = float(ac[k])
    # parabolic refine
    if 1 <= k < len(ac)-1:
        y0,y1,y2 = ac[k-1],ac[k],ac[k+1]
        den = y0-2*y1+y2
        kk = k + (0.5*(y0-y2)/den if abs(den)>1e-9 else 0)
    else:
        kk = k
    f0s[i] = fr/kk if kk>0 else 0

# median smooth
def medfilt(x,k):
    h=k//2; o=np.copy(x)
    for i in range(len(x)):
        o[i]=np.median(x[max(0,i-h):min(len(x),i+h+1)])
    return o
f0s = medfilt(f0s, 7)
fps = fr/hop

# OCTAVE CONTINUITY: track a running reference, pull each frame's octave to be near it
def octave_fix(hz, ref):
    if hz <= 0 or ref <= 0: return hz
    while hz / ref > 1.55: hz /= 2.0
    while ref / hz > 1.55: hz *= 2.0
    return hz

# per line, octave-fix against the line median region
DEG = {0:'1',2:'2',4:'3',5:'4',7:'5',9:'6',11:'7'}
def to_jianpu(hz):
    if hz <= 0: return None
    midi = 69 + 12*np.log2(hz/440.0)
    m = int(round(midi)); pc = m % 12
    bestd,bestp = None,None
    for d,deg in DEG.items():
        diff = min(abs(pc-d), 12-abs(pc-d))
        if bestd is None or diff < bestd: bestd,bestp = diff,d
    return DEG[bestp], m//12 - 1

lines = []
for ln in open(sys.argv[2] if len(sys.argv) > 2 else 'lyrics.lrc', encoding='utf-8'):
    mm = re.match(r'\[(\d+):(\d+\.\d+)\](.*)', ln.strip())
    if mm:
        t = int(mm.group(1))*60+float(mm.group(2)); txt=mm.group(3).strip()
        if txt: lines.append((t,txt))

out = []
for idx,(t,txt) in enumerate(lines):
    t2 = lines[idx+1][0] if idx+1<len(lines) else t+3.0
    i0 = max(0,int(t*fps)); i1 = max(i0+1,int(t2*fps))
    seg = f0s[i0:i1].copy(); cf = confs[i0:i1]
    seg[cf < 0.30] = 0.0
    valid = seg[seg>0]
    if len(valid) < 3:
        out.append({"t":t,"line":txt,"jp":"","note":"low"}); continue
    # global octave reference = median of valid
    ref = float(np.median(valid))
    seg = np.array([octave_fix(h, ref) if h>0 else 0.0 for h in seg])
    # subdivide into cells
    ncell = min(12, max(4, len(txt)//4))
    marks=[]
    for c in range(ncell):
        s=i0+int((i1-i0)*c/ncell); e=i0+int((i1-i0)*(c+1)/ncell)
        g = seg[s-i0:e-i0]
        g = g[g>0]
        if len(g)==0: marks.append("0"); continue
        r = to_jianpu(float(np.median(g)))
        if not r: marks.append("0"); continue
        deg,octv = r
        mark = deg + ("'" if octv>=5 else ("," if octv<=3 else ""))
        marks.append(mark)
    # collapse repeats
    coll=[]
    for m in marks:
        if not coll or coll[-1]!=m: coll.append(m)
    out.append({"t":t,"line":txt,"jp":" ".join(coll),"note":""})
    print(f"[{t:6.2f}] {' '.join(coll):<34} {txt}")

json.dump(out, open(os.environ.get('OUTJSON','./melody_jianpu.json'),'w'), ensure_ascii=False, indent=1)
