#!/usr/bin/env python3
"""Detect key + chord progression from an audio file (pure numpy + ffmpeg).

Usage:
    python3 chord_analyze.py <audio.mp3|wav>                 # key + per-2s chords
    python3 chord_analyze.py <audio.mp3> <lyrics.lrc>        # + per-lyric-line chords

No librosa required (numpy + ffmpeg only). Prefer a backing/instrumental track for
cleanest results. This detects KEY and CHORDS only -- it does NOT transcribe notes.
"""
import numpy as np, wave, sys, subprocess, re

def read_wav(path):
    with wave.open(path, 'rb') as w:
        nch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        data = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 4:
        a = np.frombuffer(data, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError("unsupported sample width")
    if nch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a, fr

def chroma(a, fr, hop=4096, win=8192):
    if len(a) < win:
        a = np.pad(a, (0, win - len(a)))
    n = 1 + (len(a) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    frames = a[idx] * np.hanning(win)[None, :]
    spec = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(win, 1.0 / fr)
    with np.errstate(divide='ignore'):
        midi = 69 + 12 * np.log2(np.maximum(freqs, 1e-6) / 440.0)
    pc = np.round(midi).astype(int) % 12
    valid = (freqs > 70) & (freqs < 2500)
    C = np.zeros((n, 12), dtype=np.float32)
    for k in range(12):
        C[:, k] = spec[:, valid & (pc == k)].sum(axis=1)
    C = np.log1p(C)
    s = C.sum(axis=1, keepdims=True); s[s == 0] = 1
    return C / s, fr / hop

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def templates():
    T = {}
    for r in range(12):
        maj = np.zeros(12); maj[[r, (r + 4) % 12, (r + 7) % 12]] = [1, 0.85, 0.9]
        mn = np.zeros(12); mn[[r, (r + 3) % 12, (r + 7) % 12]] = [1, 0.85, 0.9]
        T[NOTES[r]] = maj; T[NOTES[r] + 'm'] = mn
    return T

def best(frame, T):
    b, bs = None, -2
    for nm, t in T.items():
        s = float(np.dot(frame, t) / (np.linalg.norm(frame) * np.linalg.norm(t) + 1e-9))
        if s > bs:
            bs, b = s, nm
    return b, bs

def score_key(g):
    ks = {}
    for r in range(12):
        maj = np.zeros(12); maj[[r, (r+2)%12, (r+4)%12, (r+5)%12, (r+7)%12, (r+9)%12, (r+11)%12]] = [1,.5,1,.5,1,.5,.5]
        mn = np.zeros(12);  mn[[r, (r+2)%12, (r+3)%12, (r+5)%12, (r+7)%12, (r+8)%12, (r+11)%12]] = [1,.5,1,.5,1,.5,.5]
        ks[NOTES[r] + '大调'] = float(np.dot(g, maj) / (np.linalg.norm(g) * np.linalg.norm(maj) + 1e-9))
        ks[NOTES[r] + '小调'] = float(np.dot(g, mn) / (np.linalg.norm(g) * np.linalg.norm(mn) + 1e-9))
    return ks

if __name__ == '__main__':
    src = sys.argv[1]
    lrc = sys.argv[2] if len(sys.argv) > 2 else None
    wav = '/tmp/chord_analysis.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '22050', '-y', wav], check=True)
    a, fr = read_wav(wav)
    C, fps = chroma(a, fr)
    g = C.mean(axis=0)
    print("=== 全局着色 chroma ===")
    for i, n in enumerate(NOTES):
        print(f"  {n:3s} {g[i]:.3f}")
    print("\n=== 调性候选 ===")
    for k, v in sorted(score_key(g).items(), key=lambda x: -x[1])[:5]:
        print(f"  {k}: {v:.3f}")
    T = templates()
    if lrc:
        lines = []
        for ln in open(lrc, encoding='utf-8'):
            m = re.match(r'\[(\d+):(\d+\.\d+)\](.*)', ln.strip())
            if m:
                t = int(m.group(1)) * 60 + float(m.group(2)); txt = m.group(3).strip()
                if txt:
                    lines.append((t, txt))
        print("\n=== 逐句歌词和弦 ===")
        for i, (t, txt) in enumerate(lines):
            t2 = lines[i + 1][0] if i + 1 < len(lines) else t + 4
            seg = C[int(t * fps):max(int(t * fps) + 1, int(t2 * fps))].mean(axis=0)
            nm, sc = best(seg, T)
            print(f"  [{t:6.2f}s] {nm:5s} ({sc:.3f})  {txt}")
    else:
        step = max(1, int(round(2.0 * fps)))
        print("\n=== 每2秒和弦 ===")
        prev = None
        for i in range(0, len(C), step):
            seg = C[i:i + step].mean(axis=0); nm, sc = best(seg, T); t = i / fps
            print(f"  {t:6.2f}s  {nm:5s} ({sc:.3f}){'  *' if nm != prev else ''}")
            prev = nm
