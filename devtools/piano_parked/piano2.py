"""Grandpa's Block Lab: the two piano themes, v2 -- played on the Salamander Grand Piano V3 (Yamaha C5, Alexander Holm,
CC BY 3.0), stereo, multi-velocity, with sustain pedal, a little human timing and a warm room.
The music is original: lush jazz voicings (9ths, 13ths, 6/9s, ii-V turnarounds) and rippling harp-like runs at the ends
of phrases -- the style of 1970s TV jazz piano, not any existing tune.
    python3 piano2.py OUTDIR"""
import os, subprocess, sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salamander", "Samples")
LAYERS = (3, 5, 7, 9, 11, 13)
NAMES = {"A": 9, "C": 0, "D#": 3, "F#": 6}
ROOTS = {}                                                   # midi -> sample name stem
for o in range(1, 8):
    for n, pc in NAMES.items():
        midi = 12 * (o + 1) + pc
        if os.path.exists(os.path.join(SAMPLES, "%s%dv9.flac" % (n, o))):
            ROOTS[midi] = "%s%d" % (n, o)
_cache = {}


def sample(stem, layer, max_s=9.0):
    key = (stem, layer)
    if key not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SAMPLES, "%sv%d.flac" % (stem, layer)), "-t", str(max_s),
                              "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
        _cache[key] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)
    return _cache[key]


def voice(pitch, vel, length):
    """One note: the nearest sampled root, the velocity layer for vel, re-pitched; held `length` s, then damped."""
    root = min(ROOTS, key=lambda r: abs(r - pitch))
    layer = LAYERS[int(np.clip(round((vel / 127) * (len(LAYERS) - 1) + 0.2), 0, len(LAYERS) - 1))]
    x = sample(ROOTS[root], layer)
    ratio = 2 ** ((pitch - root) / 12)
    n = min(int((length + 0.45) * SR), int(len(x) / ratio) - 1)
    pos = np.arange(n) * ratio
    i0 = pos.astype(int); fr = (pos - i0)[:, None]
    y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    rel = int(length * SR)
    if rel < n:                                              # the damper comes down: a quick, soft fade
        env = np.ones(n)
        k = np.arange(n - rel)
        env[rel:] = np.exp(-k / (0.09 * SR))
        y = y * env[:, None]
    f = min(len(y), int(0.3 * SR))                           # (never cut a long-ringing sample off abruptly)
    y[-f:] *= np.linspace(1, 0, f)[:, None]
    return y * (0.55 + 0.45 * vel / 127)


def room(n, seconds=1.9):
    """A warm room: decaying stereo noise, darker as it fades, a short pre-delay."""
    rng = np.random.default_rng(7)
    t = np.arange(int(seconds * SR)) / SR
    ir = rng.standard_normal((len(t), 2)) * np.exp(-t * 3.6)[:, None]
    ir = sosfilt(butter(2, 4500, "low", fs=SR, output="sos"), ir, axis=0)
    ir = np.vstack([np.zeros((int(0.022 * SR), 2)), ir])
    return ir / np.abs(ir).sum(axis=0).max() * 6.0


def perform(events, pedal, total, seed):
    """events: (time_s, dur_s, pitch, vel). pedal: [(down_s, up_s)]: a note keeps ringing until the pedal lifts."""
    rng = np.random.default_rng(seed)
    out = np.zeros((int((total + 3.0) * SR), 2))
    for t, d, p, v in events:
        t = max(0.0, t + rng.normal(0, 0.006))
        v = int(np.clip(v + rng.normal(0, 3), 8, 120))
        end = t + d
        for a, b in pedal:
            if a <= end < b:
                end = b
        y = voice(p, v, end - t)
        j = int(t * SR)
        out[j:j + len(y)] += y[:len(out) - j]
    wet = np.stack([fftconvolve(out[:, c], room(len(out))[:, c])[:len(out)] for c in range(2)], axis=1)
    mix = out * 0.82 + wet * 0.30
    return mix / np.abs(mix).max() * 0.85


N = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
def m(name):
    name = name.replace("Bb", "A#").replace("Eb", "D#").replace("Ab", "G#").replace("Db", "C#").replace("Gb", "F#")
    return 12 * (int(name[-1]) + 1) + N[name[:-1]]
def notes(s):
    return [m(x) for x in s.split()]


def run(t0, span, pitches, vel=40, up=True):
    """A rippling harp-like arpeggio across `pitches` (sorted), evenly over `span` s."""
    ps = sorted(pitches) if up else sorted(pitches, reverse=True)
    return [(t0 + span * k / len(ps), span * 1.5, p, vel - 6 * (k % 2)) for k, p in enumerate(ps)]


# ------------------------------------------------------------------------- morning: "Coffee's On" (F major, gentle swing)
def morning():
    bpm = 96; B = 60 / bpm; bar = 4
    sw = lambda b: (int(b) + (2 / 3 if abs(b % 1 - 0.5) < 1e-6 else b % 1)) * B
    # (bar, beat, left hand voicing, right hand inner voicing)
    chords = [(0, 0, "F2 C3 E3 A3", "G4"), (1, 0, "G2 F3 Bb3", "A4"), (1, 2, "C2 Bb2 E3 A3", "D4"), (2, 0, "F2 C3 E3 A3", "G4"),
              (3, 0, "Eb2 D3 Gb3 A3", ""), (3, 2, "D2 C3 F#3 Bb3", "Eb4"), (4, 0, "G2 F3 Bb3 D4", "A4"), (5, 0, "C2 Bb2 E3 A3", "D4"),
              (6, 0, "A2 G3 C4", "E4"), (6, 2, "D2 C3 F#3", "B3"), (7, 0, "G2 F3 Bb3", "D4"), (7, 2, "C2 Bb2 E3", "A3"),
              (8, 0, "F2 C3 E3 A3", "G4"), (9, 0, "D2 C3 F3 A3", "E4"), (10, 0, "G2 F3 Bb3 D4", ""), (10, 2, "C2 Bb2 E3 A3", "D4"),
              (11, 0, "F1 C3 E3 A3", "D4 G4")]
    mel = [(0, 0, 1, "A4"), (0, 1, 1, "C5"), (0, 2, 2, "E5"),
           (1, 0, 1.5, "D5"), (1, 1.5, 0.5, "C5"), (1, 2, 2, "A4"),
           (2, 0, 1, "Bb4"), (2, 1, 1, "D5"), (2, 2, 1, "F5"), (2, 3, 1, "E5"),
           (3, 0, 2.5, "D5"),
           (4, 0, 1, "C5"), (4, 1, 0.5, "A4"), (4, 1.5, 0.5, "C5"), (4, 2, 2, "F5"),
           (5, 0, 1, "D5"), (5, 1, 1, "F5"), (5, 2, 2, "A5"),
           (6, 0, 1, "C5"), (6, 1, 1, "E5"), (6, 2, 1, "F#5"), (6, 3, 1, "E5"),
           (7, 0, 2, "D5"), (7, 2, 1, "Bb4"), (7, 3, 1, "G4"),
           (8, 0, 1, "A4"), (8, 1, 1, "C5"), (8, 2, 1, "E5"), (8, 3, 1, "G5"),
           (9, 0, 3, "F5"), (9, 3, 1, "D5"),
           (10, 0, 1, "E5"), (10, 1, 1, "D5"), (10, 2, 1, "Bb4"), (10, 3, 0.5, "G4"), (10, 3.5, 0.5, "E4"),
           (11, 0, 3, "F4")]
    ev, pedal = [], []
    for k, (b, beat, lh, rh) in enumerate(chords):
        t = (b * bar + beat) * B
        nxt = chords[k + 1] if k + 1 < len(chords) else (12, 0)
        span = ((nxt[0] * bar + nxt[1]) - (b * bar + beat)) * B
        ps = notes(lh)
        ev.append((t, span * 0.95, ps[0], 50))                           # the bass note
        for p in ps[1:] + (notes(rh) if rh else []):
            ev.append((t + 0.03, span * 0.9, p, 36))                       # the chord, a breath after the bass
        pedal.append((t + 0.05, t + span - 0.02))
    for b, beat, du, n in mel:
        t = sw(b * bar + beat)
        ev.append((t, du * B * 0.95, m(n), 66 if beat % 1 == 0 else 56))
        if b in (5, 9) and beat == 2:                                      # a sixth below on the long notes: warmth
            ev.append((t + 0.01, du * B * 0.95, m(n) - 9 + (1 if n == "F5" else 0), 44))
    ev += run(3 * bar * B + 2.4 * B, 1.4 * B, notes("D4 F#4 A4 C5 Eb5 F#5 A5 C6"), 42)          # turnaround ripple
    end = 11 * bar * B
    ev += run(end + 1.2 * B, 2.2 * B, notes("F4 A4 C5 D5 E5 G5 A5 C6 D6 E6 G6 A6"), 40)        # the big F6/9 ripple up
    ev.append((end + 3.6 * B, 3.5, m("F6"), 30))
    pedal[-1] = (pedal[-1][0], end + 8.0)
    return ev, pedal, end + 8.0


# ------------------------------------------------------------------------- goodnight: "Lamp's Low" (G major, slow waltz)
def goodnight():
    bpm = 72; B = 60 / bpm; bar = 3
    # broken-chord left hand: root, fifth, tenth across the three beats; right-hand inner notes held
    chords = ["G2 D3 B3 | F#4 A4", "E2 B2 G3 | D4 F#4", "A2 E3 C4 | G4 B4", "D2 A2 F#3 | C4 E4", "G2 D3 B3 | F#4 A4",
              "C2 G2 E3 | B3 D4", "B1 F#2 D3 | A3 C#4", "E2 B2 G#3 | D4 F4", "A2 E3 C4 | G4 B4", "Eb2 Bb2 G3 | D4 A4",
              "D2 A2 C4 | E4 F#4", "G1 D3 B3 | E4 A4"]
    mel = [(0, 0, 2, "B4"), (0, 2, 1, "D5"),
           (1, 0, 3, "G5"),
           (2, 0, 1, "E5"), (2, 1, 1, "C5"), (2, 2, 1, "A4"),
           (3, 0, 2, "F#4"), (3, 2, 1, "A4"),
           (4, 0, 2, "B4"), (4, 2, 1, "D5"),
           (5, 0, 2, "E5"), (5, 2, 1, "G5"),
           (6, 0, 3, "F#5"),
           (7, 0, 2, "D5"), (7, 2, 1, "B4"),
           (8, 0, 2, "C5"), (8, 2, 1, "E5"),
           (9, 0, 3, "D5"),
           (10, 0, 1, "C5"), (10, 1, 1, "B4"), (10, 2, 1, "A4"),
           (11, 0, 5, "G4")]
    ev, pedal = [], []
    for b, ch in enumerate(chords):
        lh, rh = (notes(s) for s in ch.split("|"))
        t = b * bar * B
        last = b == len(chords) - 1
        for k, p in enumerate(lh):                                         # one-two-three, rolling up
            ev.append((t + k * B, (bar - k) * B + (4 if last else 0), p, 46 - 6 * k))
        for p in rh:
            ev.append((t + 1.02 * B, 2 * B + (4 if last else 0), p, 32))
        pedal.append((t + 0.06, t + bar * B - 0.03 + (9 if last else 0)))
    for b, beat, du, n in mel:
        ev.append((b * bar * B + beat * B, du * B * 0.97, m(n), 58))
    ev += run(5 * bar * B + 2.2 * B, 0.8 * B, notes("B4 D5 E5 G5"), 38)                         # a little sigh up
    end = 11 * bar * B
    ev += run(end + 2.0 * B, 2.6 * B, notes("G3 D4 A4 B4 E5 G5 A5 D6"), 34)                    # the lamp goes low...
    ev.append((end + 6.0 * B, 4.0, m("G6"), 26))                                                 # ...click.
    return ev, pedal, end + 11.0


out = sys.argv[1]
for name, fn, seed in (("morning", morning, 1), ("goodnight", goodnight, 2)):
    ev, pedal, total = fn()
    y = perform(ev, pedal, total, seed)
    wav = os.path.join(out, "piano2_%s.wav" % name)
    import scipy.io.wavfile as wf
    wf.write(wav, SR, (y * 32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", "silenceremove=stop_periods=-1:stop_duration=1.5:stop_threshold=-62dB,loudnorm=I=-18:TP=-2",
                    "-ar", "48000", "-c:a", "aac", "-b:a", "224k", os.path.join(out, "piano_%s_DEMO_v2.m4a" % name)], check=True)
    print(name, "%.1f s" % total)
