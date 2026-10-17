#!/usr/bin/env python3
"""Extract a vocal melody contour -> C-major jianpu per lyric line.

Usage:
    python3 melody_jianpu.py <audio.m4a|mp3|wav> <lyrics.lrc>  [-o out.json]

Pure numpy + ffmpeg. No librosa, no ML model.

HONEST LIMIT: vocal-in-mix f0 tracking yields melodic CONTOUR, not note-accurate jianpu.
Label the output approximate on any printed sheet ("简谱(旋律仅供参考)" / "approximate").
For clean results you'd need spectral subtraction against a time-aligned instrumental of
identical duration; two versions with different lengths are different edits and invalid.

Key technique: OCTAVE-CONTINUITY CORRECTION. Raw autocorrelation f0 octave-errors
constantly on voice; pulling each frame to within ~1.55x of the line's median f0 is what
turns garbage into a usable contour. Do not remove that step.
"""
import numpy as np, wave, subprocess, re, json, sys, argparse


def read_wav(path):
    with wave.open(path, 'rb') as w:
        nch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        data = w.readframes(n)
    if sw != 2:
        raise ValueError("expected 16-bit PCM")
    a = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a, fr


def track_f0(a, fr, win=2048, hop=512, fmin=110.0, fmax=700.0):
    """Autocorrelation f0 tracker restricted to the vocal band.

    fmin=110 (A2), fmax=700 — NOT 80 Hz: a lower floor lets bass/guitar notes win the
    autocorrelation peak and poisons the whole melody.
    """
    n = 1 + (len(a) - win) // hop
    lag_min = max(1, int(fr / fmax))
    lag_max = min(win - 2, int(fr / fmin))
    f0 = np.zeros(n)
    conf = np.zeros(n)
    for i in range(n):
        seg = a[i * hop:i * hop + win].astype(np.float64)
        seg -= seg.mean()
        if float(np.dot(seg, seg)) < 1e-6:
            continue
        ac = np.correlate(seg, seg, mode='full')[win - 1:]
        if ac[0] != 0:
            ac = ac / ac[0]
        hi = min(len(ac) - 1, lag_max)
        if hi <= lag_min:
            continue
        k = int(np.argmax(ac[lag_min:hi])) + lag_min
        conf[i] = float(ac[k])
        kk = k
        if 1 <= k < len(ac) - 1:                      # parabolic sub-sample refine
            y0, y1, y2 = ac[k - 1], ac[k], ac[k + 1]
            den = y0 - 2 * y1 + y2
            if abs(den) > 1e-9:
                kk = k + 0.5 * (y0 - y2) / den
        f0[i] = fr / kk if kk > 0 else 0.0
    return f0, conf, fr / hop


def medfilt(x, k):
    h = k // 2
    out = np.copy(x)
    for i in range(len(x)):
        out[i] = np.median(x[max(0, i - h):min(len(x), i + h + 1)])
    return out


def octave_fix(hz, ref):
    """THE critical step. Pull hz's octave to within ~1.55x of ref."""
    if hz <= 0 or ref <= 0:
        return hz
    while hz / ref > 1.55:
        hz /= 2.0
    while ref / hz > 1.55:
        hz *= 2.0
    return hz


DEG = {0: '1', 2: '2', 4: '3', 5: '4', 7: '5', 9: '6', 11: '7'}


def to_jianpu(hz):
    if hz <= 0:
        return None
    midi = 69 + 12 * np.log2(hz / 440.0)
    m = int(round(midi))
    pc = m % 12
    bestd, bestp = None, None
    for d, deg in DEG.items():
        diff = min(abs(pc - d), 12 - abs(pc - d))
        if bestd is None or diff < bestd:
            bestd, bestp = diff, d
    octv = m // 12 - 1
    return DEG[bestp], octv


def parse_lrc(path):
    lines = []
    for ln in open(path, encoding='utf-8'):
        m = re.match(r'\[(\d+):(\d+\.\d+)\](.*)', ln.strip())
        if m:
            t = int(m.group(1)) * 60 + float(m.group(2))
            txt = m.group(3).strip()
            if txt:
                lines.append((t, txt))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('lrc')
    ap.add_argument('-o', '--out', default='/tmp/melody_jianpu.json')
    ap.add_argument('--sr', type=int, default=22050)
    args = ap.parse_args()

    wav = '/tmp/_mel_src.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-i', args.audio,
                    '-ac', '1', '-ar', str(args.sr), '-y', wav], check=True)
    a, fr = read_wav(wav)
    f0, conf, fps = track_f0(a, fr)
    f0 = medfilt(f0, 7)

    print("fps=%.2f frames=%d conf_median=%.3f" % (fps, len(f0), np.median(conf)))

    lines = parse_lrc(args.lrc)
    out = []
    for idx, (t, txt) in enumerate(lines):
        t2 = lines[idx + 1][0] if idx + 1 < len(lines) else t + 3.0
        i0 = max(0, int(t * fps))
        i1 = max(i0 + 1, int(t2 * fps))
        seg = f0[i0:i1].copy()
        cf = conf[i0:i1]
        seg[cf < 0.30] = 0.0
        valid = seg[seg > 0]
        if len(valid) < 3:
            out.append({"t": t, "line": txt, "jp": "", "note": "low-confidence"})
            continue

        ref = float(np.median(valid))
        seg = np.array([octave_fix(h, ref) if h > 0 else 0.0 for h in seg])

        ncell = min(12, max(4, len(txt) // 4))
        marks = []
        for c in range(ncell):
            s = int(len(seg) * c / ncell)
            e = int(len(seg) * (c + 1) / ncell)
            g = seg[s:e]
            g = g[g > 0]
            if len(g) == 0:
                marks.append("0")
                continue
            r = to_jianpu(float(np.median(g)))
            if not r:
                marks.append("0")
                continue
            deg, octv = r
            marks.append(deg + ("'" if octv >= 5 else ("," if octv <= 3 else "")))

        coll = []
        for m in marks:                       # collapse held notes
            if not coll or coll[-1] != m:
                coll.append(m)

        out.append({"t": t, "line": txt, "jp": " ".join(coll), "note": ""})
        print(f"[{t:6.2f}] {' '.join(coll):<34} {txt}")

    json.dump(out, open(args.out, 'w'), ensure_ascii=False, indent=1)
    print("\nwrote", args.out)
    print("NOTE: approximate contour only — label it as such on any printed sheet.")


if __name__ == '__main__':
    main()
