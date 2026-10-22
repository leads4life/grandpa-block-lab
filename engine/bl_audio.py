"""Block Lab: procedural sound for the active story (from build/plan.json) + grandpa's voice -> build/audio/mix.wav.

Every sound comes from a story event: block settles, footsteps, card pops, highlights, grow, crack, collapse.
"""
import json
import os
import subprocess

import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import resample_poly, butter, sosfilt

import bl_common as C

P = C.load_plan()
OUT = os.path.join(C.BUILD, "audio")
SR, FPS = 48000, P["fps"]
N0 = int(P["film"] * SR)
NL = int(0.4 * SR) if P.get("loop") else 0          # looping Short: render a little past the end, then fold it onto the start
N = N0 + NL
t_all = np.arange(N) / SR
rng = np.random.default_rng(9)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "highpass", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def place(buf, t, x, g=1.0):
    j = int(round(t * SR))
    if 0 <= j < len(buf):
        e = min(len(buf), j + len(x))
        buf[j:e] += x[:e - j] * g


def click(p=1.0):
    t = tt(0.07)
    x = sum(a * np.sin(2 * np.pi * f * p * t + rng.uniform(0, 6.3)) * np.exp(-t * dmp) for f, a, dmp in ((1850, 0.9, 70), (2930, 0.6, 95), (4320, 0.4, 130)))
    return (x * 0.5 + bp(rng.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 900) * 0.8) * (1 - np.exp(-t * 4000))


def thunk(p=1.0, d=0.16):
    t = tt(d)
    body = np.sin(2 * np.pi * np.cumsum(150 * p * (1 + 0.25 * np.exp(-t * 60))) / SR) * np.exp(-t * 30)
    return (body + lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 70) * 0.8) * (1 - np.exp(-t * 2500))


def modes(t, p, parts):
    """Sum of decaying partials [(Hz, amplitude, decay per second), ...] with random phases."""
    return sum(a * np.sin(2 * np.pi * f * p * t + rng.uniform(0, 6.3)) * np.exp(-t * d) for f, a, d in parts)


BLOCK_SOUND = {                                                  # material -> (length s, loudness) of its placement sound
    "wood": (0.20, 0.95), "stone": (0.16, 1.0), "sandstone": (0.15, 0.85), "brick": (0.11, 0.9),
    "gold": (0.45, 0.6), "grass": (0.13, 0.9), "blue": (0.13, 0.9), "iron": (0.35, 0.75), "rubber": (0.13, 0.9), "red": (0.25, 0.8),
    "steel": (0.30, 0.6), "oldwood": (0.20, 0.9)}


def block_sound(material, p=1.0):
    """One block settling, voiced by what it is made of: wood knocks, stone clacks, sandstone taps softly,
    brick taps dry, gold tinks, grass / blue pop."""
    dur, loud = BLOCK_SOUND.get(material, BLOCK_SOUND["stone"])
    t = tt(dur)
    n = rng.standard_normal(len(t))
    if material in ("wood", "oldwood"):   # hollow knock: low body resonances, little top end
        x = modes(t, p, ((380, 1.0, 38), (610, 0.6, 45), (980, 0.35, 60))) + bp(n, 300, 1800) * np.exp(-t * 400) * 0.6 \
            + np.sin(2 * np.pi * 120 * p * t) * np.exp(-t * 35) * 0.5
    elif material == "sandstone":  # soft gritty tap: grainy noise, a little tone
        grain = np.repeat(rng.uniform(0.3, 1.0, len(t) // 96 + 1), 96)[:len(t)]
        x = bp(n, 450, 2200) * grain * np.exp(-t * 120) * 0.8 + modes(t, p, ((700, 0.25, 90),)) \
            + np.sin(2 * np.pi * 110 * p * t) * np.exp(-t * 40) * 0.8
    elif material == "brick":     # dry sharp tap: short bright partials, almost no ring
        x = modes(t, p, ((1600, 0.8, 140), (2450, 0.6, 170), (3500, 0.35, 200))) + bp(n, 2000, 8000) * np.exp(-t * 1100) * 0.8 \
            + np.sin(2 * np.pi * 180 * p * t) * np.exp(-t * 60) * 0.3
    elif material == "gold":      # bright tink: high, slightly inharmonic, rings a little
        x = modes(t, p, ((2960, 1.0, 14), (4410, 0.55, 18), (6120, 0.3, 24), (7830, 0.15, 30))) \
            + bp(n, 4000, 12000) * np.exp(-t * 1500) * 0.4 + np.sin(2 * np.pi * 220 * p * t) * np.exp(-t * 50) * 0.2
    elif material == "iron":      # metallic clank: inharmonic ring over a dull hit, like a girder being set
        x = modes(t, p, ((520, 1.0, 22), (1410, 0.6, 28), (2380, 0.45, 35), (3720, 0.25, 45))) \
            + bp(n, 1200, 6000) * np.exp(-t * 600) * 0.6 + np.sin(2 * np.pi * 140 * p * t) * np.exp(-t * 40) * 0.5
    elif material == "steel":     # small bright steel: a light high ting, like keys on a ring
        x = modes(t, p, ((2350, 1.0, 20), (3900, 0.6, 26), (5600, 0.35, 34))) + bp(n, 3000, 10000) * np.exp(-t * 1400) * 0.5
    elif material == "red":       # painted steel panel: a bright, short clank
        x = modes(t, p, ((780, 1.0, 30), (1960, 0.5, 42), (3100, 0.25, 55))) + bp(n, 1500, 7000) * np.exp(-t * 700) * 0.5
    elif material in ("grass", "blue", "rubber"):  # muffled pop
        x = lp(n, 600) * np.exp(-t * 60) * 0.9 + np.sin(2 * np.pi * 95 * p * t) * np.exp(-t * 45) * 0.7
    else:                         # stone (and anything new): solid clack with a heavy thunk under it
        x = modes(t, p, ((1150, 0.7, 80), (1720, 0.5, 95), (2600, 0.3, 120))) + bp(n, 1500, 7000) * np.exp(-t * 700) * 0.7 \
            + thunk(p, dur) * 0.6
    x = x * (1 - np.exp(-t * 4000))                             # same instant attack for every material (keeps click sync)
    return x / max(1e-9, np.abs(x).max()) * loud


def mix(*xs):
    """Sum sounds of different lengths (padded to the longest)."""
    n = max(len(x) for x in xs)
    return sum(np.pad(x, (0, n - len(x))) for x in xs)


def step():
    t = tt(0.16)
    crunch = np.zeros(len(t))
    for _ in range(12):
        j = int(rng.uniform(0, 0.07) * SR)
        g = bp(rng.standard_normal(int(0.006 * SR)), 1200, 5500) * np.hanning(int(0.006 * SR))
        crunch[j:j + len(g)] += g * rng.uniform(0.2, 0.7)
    return np.sin(2 * np.pi * 85 * t) * np.exp(-t * 45) * 0.6 + crunch


def soft_hit(f0=70, d=0.6):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-t * 20))) / SR) * np.exp(-t * 7)


def chime(f=880, d=1.2):
    t = tt(d)
    return sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1.0), (2.01, 0.35), (3.0, 0.15))) * np.exp(-t * 3.5) * 0.4


def blip(f=1500, d=0.08):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 45)


def snap():
    t = tt(0.05)
    return bp(rng.standard_normal(len(t)), 1500, 9000) * np.exp(-t * 160) + np.sin(2 * np.pi * 320 * t) * np.exp(-t * 90) * 0.5


def creak(d=0.5):
    t = tt(d)
    f = 70 + 40 * np.sin(2 * np.pi * 3 * t)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * bp(rng.standard_normal(len(t)), 200, 1500) * np.hanning(len(t)) * 0.4


def boom(d=2.5):
    t = tt(d)
    return (np.sin(2 * np.pi * np.cumsum(42 * (0.6 + 0.8 * np.exp(-t * 4))) / SR) * np.exp(-t * 2) * 1.6 +
            lp(rng.standard_normal(len(t)), 260) * np.exp(-t * 3) * 2.4) * (1 - np.exp(-t * 500))


def reverb(x, d=0.9, wet_k=0.5):
    """A small room / distant forest: decaying noise impulse response (output is len(x) + len(ir) long)."""
    ir = rng.standard_normal(int(d * SR)) * np.exp(-np.arange(int(d * SR)) / SR * 6.0 / d)
    wet = np.pad(np.convolve(x, ir), (0, 1))
    wet = wet / max(1e-9, np.abs(wet).max()) * np.abs(x).max()
    return np.pad(x, (0, len(ir))) * (1 - wet_k) + wet * wet_k


def sfx(kind):
    """One-off foley for {"type": "sfx", "sound": kind}."""
    n = lambda d: rng.standard_normal(len(tt(d)))
    if kind == "tap":            # fingertip on a plastic-ish block: short, dull, a little hollow
        t = tt(0.08)
        return (modes(t, 1.0, ((1250, 1.0, 120), (2300, 0.4, 160))) * 0.4 + bp(n(0.08), 800, 4000) * np.exp(-t * 300)) * (1 - np.exp(-t * 3000))
    if kind == "clink":          # ceramic mug set on wood / picked up
        t = tt(0.35)
        th = thunk(1.8, 0.08)
        return modes(t, 1.0, ((2650, 1.0, 26), (4100, 0.5, 34), (5900, 0.25, 45))) * 0.6 + np.pad(th, (0, len(t) - len(th))) * 0.5
    if kind == "sip":            # slurp: a filtered noise swell with a gulp
        t = tt(0.55)
        sl = bp(n(0.55), 900, 5000) * np.sin(np.pi * t / t[-1]) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
        g = np.zeros(len(t)); j = int(0.42 * SR); gl = thunk(0.9, 0.1); g[j:j + len(gl)] += gl[:len(t) - j] * 0.6
        return mix(sl * 0.5, g)
    if kind == "slosh":          # coffee sloshing in a tipping mug
        t = tt(0.45)
        return lp(n(0.45), 1400) * np.exp(-t * 6) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t) ** 2)
    if kind == "creak":          # wooden chair taking his weight
        return creak(0.5) * 1.4
    if kind == "scrape":         # chair legs dragged on floorboards
        t = tt(0.6)
        return bp(n(0.6), 250, 2200) * np.hanning(len(t)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 31 * t)))
    if kind == "clatter":        # a block bouncing off the table
        out = np.zeros(int(0.6 * SR))
        for k, (dt, g) in enumerate(((0.0, 1.0), (0.17, 0.55), (0.29, 0.3), (0.37, 0.15))):
            x = block_sound("planks", 1.15 + 0.05 * k); j = int(dt * SR); out[j:j + len(x)] += x[:len(out) - j] * g
        return out
    if kind == "click_block":    # the block snapping back into place: the show's signature click
        return mix(block_sound("stone", 1.25) * 0.7, click(1.1) * 0.6)
    if kind == "clunk_far":      # two heavy wooden clunks somewhere out in the forest
        out = np.zeros(int(1.6 * SR))
        for dt in (0.0, 0.55):
            x = lp(mix(thunk(0.55, 0.35), block_sound("wood", 0.6) * 0.8), 900); j = int(dt * SR); out[j:j + len(x)] += x[:len(out) - j]
        return reverb(out, 1.1, 0.55)
    if kind == "crumble":        # rotten wood giving way: a soft wet crunch and a few bits dropping
        t = tt(0.7)
        crunch = bp(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 7) * (0.5 + 0.5 * (rng.random(len(t)) > 0.97))
        bits = np.zeros(len(t))
        for dt in (0.12, 0.27, 0.41):
            x = block_sound("oldwood", 0.8) * 0.4; j = int(dt * SR); bits[j:j + len(x)] += x[:len(t) - j]
        return lp(crunch, 1800) * 0.8 + bits
    if kind == "door_creak":     # an old wooden door swinging open on dry hinges
        t = tt(1.1)
        f = 260 + 120 * np.sin(2 * np.pi * 1.3 * t) + 60 * np.sin(2 * np.pi * 7 * t)
        sq = np.sin(2 * np.pi * np.cumsum(f) / SR) * bp(rng.standard_normal(len(t)), 300, 3500) * 0.6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
        return sq * np.hanning(len(t)) ** 0.6
    if kind == "kick":           # a boot kicking a wooden prop out: a knock and the prop clattering away
        return mix(block_sound("wood", 0.85), thunk(1.1, 0.08) * 0.6, np.pad(sfx("clatter") * 0.5, (int(0.12 * SR), 0)))
    if kind == "wedge":          # a wooden stick jammed under the hammer arm
        return mix(block_sound("oldwood", 0.9), np.pad(block_sound("wood", 1.05) * 0.6, (int(0.09 * SR), 0)))
    if kind == "rustle":         # something big pushing through the bushes
        t = tt(1.2)
        return bp(n(1.2), 600, 6000) * np.hanning(len(t)) * (0.5 + 0.5 * (np.sin(2 * np.pi * 5.5 * t) > 0.3)) * 0.8
    if kind.startswith("echo|"):  # "echo|<frozen slug>|<line id>|<repeats>": a remembered line, echoing (dream flashback)
        import json as _json
        _, slug, lid, reps = kind.split("|")
        fz = os.path.join(C.HERE, "frozen", slug)
        ln = [l for l in _json.load(open(os.path.join(fz, "dialogue.json")))["lines"] if l["id"] == lid][0]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(fz, "voice.flac"), "-ss", "%.3f" % ln["start"],
                              "-t", "%.3f" % (ln["end"] - ln["start"]), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                             check=True, capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767
        out = np.zeros(int((len(x) / SR + 1.25 * int(reps) + 2.0) * SR))
        for k in range(int(reps)):                       # each repeat fainter, a touch slower and lower, more reverb
            y = resample_poly(x, 100 + 4 * k, 100) if k else x
            y = reverb(y, 0.9 + 0.35 * k, 0.35 + 0.15 * k) * 0.72 ** k
            j = int(1.25 * k * SR); out[j:j + len(y)] += y[:len(out) - j]
        return lp(out, 6500)
    if kind == "huff_far":       # a boar's huff from across the stream: distant, reverberant (a cliffhanger sting)
        t = tt(0.42)                                      # (the boar's huff, as below -- sfx() runs before that's defined)
        blast = bp(rng.standard_normal(len(t)), 250, 3200) * np.exp(-t * 9) * (1 - np.exp(-t * 400))
        grunt = np.sin(2 * np.pi * np.cumsum(95 * (1 - 0.3 * t)) / SR) * np.exp(-t * 11) * (0.6 + 0.4 * (rng.random(len(t)) > 0.5))
        return lp(reverb(lp(blast + lp(grunt, 700) * 0.5, 4500), 1.4, 0.6), 2500) * 0.7
    if kind == "buzz":           # a tablet buzzing: two short vibrations
        out = np.zeros(int(0.7 * SR))
        for t0 in (0.0, 0.35):
            x = tt(0.22)
            v = np.sign(np.sin(2 * np.pi * 150 * x)) * 0.5 + bp(rng.standard_normal(len(x)), 120, 900) * 0.3
            j = int(t0 * SR); out[j:j + len(x)] += lp(v, 1500) * np.hanning(len(x)) ** 0.3 * 0.6
        return out
    if kind == "zip":            # a little electric pulse setting off: a quick rising tick
        x = tt(0.25)
        return np.sin(2 * np.pi * np.cumsum(900 + 2600 * x / x[-1]) / SR) * np.exp(-x * 9) * 0.35
    if kind == "fizzle":         # the pulse dies out: a short crackle that fades
        x = tt(0.6)
        crack = bp(rng.standard_normal(len(x)), 2000, 8000) * (rng.random(len(x)) > 0.93) * 2.0
        return lp(crack + bp(rng.standard_normal(len(x)), 300, 3000) * 0.15, 7000) * np.exp(-x * 5)
    if kind == "page":           # a page turning: a papery swish and a soft flap
        x = tt(0.45)
        sw = bp(rng.standard_normal(len(x)), 1500, 9000) * np.sin(np.pi * x / x[-1]) ** 2 * 0.5
        flap = np.pad(bp(rng.standard_normal(int(0.05 * SR)), 300, 3000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 60) * 0.8, (int(0.36 * SR), 0))
        return mix(sw, flap)
    if kind == "settle":         # settling into the chair / cloth rustle
        t = tt(0.4)
        return bp(n(0.4), 500, 3500) * np.hanning(len(t)) * 0.5
    raise SystemExit("unknown sfx sound %r" % kind)


stems = {k: np.zeros(N + 4 * SR) for k in ("build", "fx", "ambience")}
counts = {n: sum(1 for b in P["blocks"] if b["struct"] == n) for n in P["structures"]}
for b in P["blocks"]:
    if b["prebuilt"]:
        continue
    ts = b["settle"] / FPS
    many = counts[b["struct"]] > 24
    p = rng.uniform(0.92, 1.08) * (0.9 if many else 1.0)
    g = rng.uniform(0.3, 0.42) if many else 0.75
    place(stems["build"], ts, block_sound(P["structures"][b["struct"]]["material"], p), g * 1.1)
def on_floor(f):
    x, y = P["path"][min(f, len(P["path"]) - 1)][:2]
    return P.get("world", {}).get("interior") == "cabin" and -1.6 < x < 1.4 and -0.9 < y < 1.6


for s in P["steps"]:                                            # indoors: boots knock on floorboards
    if on_floor(s["frame"]):
        place(stems["build"], s["frame"] / FPS, mix(block_sound("wood", 0.72) * 0.6, thunk(0.7, 0.1) * 0.5), 0.3)
    else:
        place(stems["build"], s["frame"] / FPS, step(), 0.3)
if "hammer" in P.get("outfit", {}).get("extras", []):          # a light hammer tap just after each block lands
    for b in P["blocks"]:
        if not b["prebuilt"]:
            x = tt(0.09)
            place(stems["build"], b["settle"] / FPS + 0.09, modes(x, rng.uniform(0.95, 1.05), ((3100, 1.0, 60), (4700, 0.5, 80))) * np.exp(-x * 40), 0.12)
for b in P["blocks"]:                                           # blocks being taken down: a soft lift-off
    if b.get("vanish"):
        place(stems["build"], b["vanish"] / FPS, block_sound(P["structures"][b["struct"]]["material"], rng.uniform(1.05, 1.2)),
              0.35 if counts[b["struct"]] <= 24 else 0.12)
zs = [p[2] for p in P["path"]]                                  # boots on ladder rungs while climbing
for f in range(1, len(zs)):
    if abs(zs[f] - zs[f - 1]) * FPS > 0.05 and int(zs[f] / 0.1) != int(zs[f - 1] / 0.1):
        place(stems["build"], f / FPS, block_sound("wood", rng.uniform(0.8, 0.9)), 0.3)
for c in P["cards"]:
    st = c.get("style", "title")
    if st == "title":
        place(stems["fx"], c["t0"], soft_hit(70, 0.7), 0.5)
    elif st in ("bubble", "tag"):
        place(stems["fx"], c["t0"], blip(1500), 0.3)
    elif st == "panel":
        for r in c["rows"]:
            place(stems["fx"], r["t"], blip(1400), 0.35)
    elif st == "end":
        place(stems["fx"], c["t0"], soft_hit(50, 1.2), 0.6)
    elif st == "live":                                          # a soft blip each time the viewer count goes up
        for (ta, na), (tb, nb) in zip(c.get("viewers", []), c.get("viewers", [])[1:]):
            if nb > na:
                place(stems["fx"], tb, blip(1760) + np.pad(blip(2350), (int(0.07 * SR), 0))[:len(blip(1760))], 0.25)
for a in P["actions"]:
    if a["type"] == "sfx":                                      # foley sits with the build sounds; far-off sounds with fx
        place(stems["fx" if a["sound"] == "clunk_far" else "build"], a["t0"], sfx(a["sound"]), a.get("gain", 1.0))
    elif a["type"] == "slide" and a.get("sound") == "scrape":
        place(stems["build"], a["t0"], sfx("scrape"), a.get("gain", 1.0))
    elif a["type"] == "highlight":
        place(stems["fx"], a["t0"], chime(988), 0.4)
    elif a["type"] == "grow" and a.get("sound") == "none":
        pass
    elif a["type"] == "grow":
        x = tt(a["t1"] - a["t0"] + 0.4)
        rise = np.sin(2 * np.pi * np.cumsum(120 + 500 * (x / x[-1]) ** 1.5) / SR) * 0.25 + bp(rng.standard_normal(len(x)), 500, 6000) * 0.35
        shimmer = sum(np.sin(2 * np.pi * f * x) for f in (1320, 1760, 2217)) * 0.06 * (x / x[-1])
        place(stems["fx"], a["t0"], (rise + shimmer) * np.hanning(len(x)) ** 0.7, 0.7)
        place(stems["fx"], a["t0"], lp(rng.standard_normal(len(x)), 120) * (x / x[-1]) * 1.2, 0.6)
    elif a["type"] == "crack" and a.get("sound") == "none":
        pass
    elif a["type"] == "crack" and a.get("sound") == "spark":     # spark plug: a sharp electric snap
        for k in range(3):
            place(stems["fx"], a["t0"] + 0.025 * k, snap(), 0.5)
    elif a["type"] == "crack" and a.get("sound") == "bang":      # the fuel burning: a punchy little explosion
        place(stems["fx"], a["t0"], boom(0.9), 0.55)
        place(stems["fx"], a["t0"], snap(), 0.6)
    elif a["type"] == "crack" and a.get("sound") == "sizzle":    # hot metal: a hiss as it heats, steam as it cools
        x = tt(max(0.4, a["t1"] - a["t0"]) + 0.6)
        place(stems["fx"], a["t0"], bp(rng.standard_normal(len(x)), 2500, 9000) * np.exp(-x * 2.5) * (1 - np.exp(-x * 20)), 0.35)
        if a.get("c0") is not None:
            x = tt(a["c1"] - a["c0"] + 0.5)
            hiss = bp(rng.standard_normal(len(x)), 1800, 7000) * (1 - x / x[-1]) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * x))
            place(stems["fx"], a["c0"], hiss, 0.4)
    elif a["type"] == "crack":
        for k in range(22):
            place(stems["fx"], a["t0"] + (a["t1"] - a["t0"]) * (k / 22) ** 0.6, snap(), rng.uniform(0.35, 0.7))
        place(stems["fx"], a["t0"], creak(max(0.2, a["t1"] - a["t0"])), 0.6)
    elif a["type"] == "collapse":
        place(stems["fx"], a["t0"], boom(2.8), 1.2)
        for k in range(70):
            place(stems["fx"], a["t0"] + 0.15 + rng.gamma(2.0, 0.22), thunk(rng.uniform(0.5, 0.8), 0.3), rng.uniform(0.25, 0.6))
        x = tt(2.0)
        place(stems["fx"], a["t0"] + 0.2, bp(rng.standard_normal(len(x)), 300, 3000) * np.exp(-x * 1.5) * 0.4)
    elif a["type"] == "melt":                                   # hot hiss, then the blocks clink down into the slab
        mat_ = P["structures"][a["target"]]["material"]
        x = tt(2.2)
        place(stems["fx"], a["t0"] - 0.3, bp(rng.standard_normal(len(x)), 2500, 9000) * np.exp(-x * 1.4) * (1 - np.exp(-x * 8)), 0.5)
        place(stems["fx"], a["t0"], lp(rng.standard_normal(len(x)), 180) * np.exp(-x * 1.8), 0.9)
        for k in range(60):
            place(stems["fx"], a["t0"] + rng.gamma(2.0, 0.25), block_sound(mat_, rng.uniform(0.85, 1.1)), rng.uniform(0.15, 0.4))
    elif a["type"] == "fly" and a.get("sound") == "none":
        pass
    elif a["type"] == "fly":                                    # a whoosh through the air, a thud if it lands
        x = tt(max(0.2, a["t1"] - a["t0"]))
        whoosh = bp(rng.standard_normal(len(x)), 500, 3000) * (0.3 + 0.7 * np.sin(np.pi * x / x[-1]))
        place(stems["fx"], a["t0"], whoosh, 0.25)
        if a.get("land"):
            place(stems["fx"], a["t1"], thunk(0.6, 0.35), 0.9)
            place(stems["fx"], a["t1"], boom(0.7), 0.35)
    elif a["type"] == "slide" and a.get("sound") == "none":
        pass
    elif a["type"] == "slide" and a.get("sound") == "click":     # a lock pin: a small bright click as it seats
        place(stems["fx"], a["t1"] - 0.01, click(rng.uniform(0.9, 1.1)), 0.4)
        place(stems["fx"], a["t1"] - 0.01, thunk(1.6, 0.04), 0.12)
    elif a["type"] == "slide" and a.get("sound") == "clunk":     # a bolt or a jammed part: a solid metal clunk
        place(stems["fx"], a["t1"] - 0.02, thunk(0.9, 0.1), 0.6)
        place(stems["fx"], a["t1"] - 0.02, click(0.45), 0.25)
    elif a["type"] == "slide" and a.get("sound") == "chug":      # engine part: a mechanical knock at the end of its stroke
        place(stems["fx"], a["t1"] - 0.02, thunk(0.75, 0.12), 0.45)
        place(stems["fx"], a["t1"] - 0.02, click(0.5), 0.12)
    elif a["type"] == "slide" and P["structures"][a["target"]]["material"] == "wood":   # crate on a pulley: squeak + rope
        x = tt(a["t1"] - a["t0"] + 0.1)
        sp = np.array([C.smoother((k / SR) / max(1e-6, a["t1"] - a["t0"])) for k in range(len(x))])
        speed = np.abs(np.gradient(sp)); speed /= max(1e-9, speed.max())
        squeak = np.sin(2 * np.pi * np.cumsum(1050 + 180 * np.sin(2 * np.pi * 7 * x)) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * x) ** 2)
        rope = bp(rng.standard_normal(len(x)), 300, 2000) * 0.5
        place(stems["fx"], a["t0"], (squeak * 0.25 + rope) * speed, 0.45)
        place(stems["fx"], a["t1"], block_sound("wood", 0.7), 0.6)
    elif a["type"] == "slide":                                  # stone scrape that follows the slide's speed
        x = tt(a["t1"] - a["t0"] + 0.1)
        sp = np.array([C.smoother((k / SR) / max(1e-6, a["t1"] - a["t0"])) for k in range(len(x))])
        speed = np.abs(np.gradient(sp)); speed /= max(1e-9, speed.max())
        grind = bp(rng.standard_normal(len(x)), 150, 1400) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 23 * x)))
        place(stems["fx"], a["t0"], grind * speed, 0.5)
    elif a["type"] == "spin" and a.get("ticks_per_turn", 12):  # a ratchet tick every 1/ticks_per_turn of a turn (0 = silent)
        step_deg = 360.0 / a.get("ticks_per_turn", 12)
        last = 0
        for k in range(int((a["t1"] - a["t0"]) * 1000) + 1):
            tk = a["t0"] + k / 1000
            n = int(abs(C.motion_angle(a, tk)) // step_deg)
            if n > last:
                place(stems["fx"], tk, click(rng.uniform(0.55, 0.65)), 0.35)
                place(stems["fx"], tk, thunk(1.4, 0.06), 0.15)
                last = n
    elif a["type"] == "swing":                                  # a whoosh each time it sweeps through the bottom
        half = a.get("period", 1.6) / 2
        tk = a["t0"] + half
        while tk < a["t1"] - 0.2:
            x = tt(0.5)
            w = abs(C.motion_angle(a, tk - half / 2)) / max(1e-6, abs(a["degrees"]))
            place(stems["fx"], tk - 0.25, bp(rng.standard_normal(len(x)), 400, 2500) * np.hanning(len(x)) * w, 0.4)
            tk += half
W = P.get("world", {})


def ambience(indoors=None):
    """Background bed that matches the world: wind, rain, waves, crickets at night, birds / gulls calling.
    Indoors ("interior": "cabin") the outside is muffled through the walls, over a quiet room tone and a ticking clock."""
    indoors = W.get("interior") == "cabin" if indoors is None else indoors
    wind = lp(rng.standard_normal(N), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * t_all / 7.3))
    amb = wind * (0.35 if W.get("time") == "night" or W.get("weather") == "snow" else 0.6)
    if indoors:
        amb = amb * 0.25 + lp(rng.standard_normal(N), 180) * 0.35            # walls muffle the wind; low room tone
    if W.get("weather") == "rain":
        amb = amb * 0.5 + bp(rng.standard_normal(N), 900, 9000) * 0.5
        drops = np.zeros(N)
        for tk in np.sort(rng.uniform(0, N / SR, int(N / SR * 40))):
            j = int(tk * SR); x = bp(rng.standard_normal(240), 2000, 8000) * np.exp(-np.arange(240) / 30)
            drops[j:j + len(x)] += x[:N - j] * rng.uniform(0.2, 1.0)
        amb = amb + drops * 0.6
    if W.get("ground") == "paris":                                  # distant city murmur
        amb = amb * 0.7 + lp(bp(rng.standard_normal(N), 150, 900), 600) * (0.8 + 0.2 * np.sin(2 * np.pi * t_all / 11)) * 0.5
    if W.get("ground") == "beach":                                  # slow waves
        swell = 0.5 + 0.5 * np.sin(2 * np.pi * t_all / 6.5) ** 2
        amb = amb + lp(rng.standard_normal(N), 1500) * swell * 0.8
    if W.get("time") == "night" and W.get("weather") not in ("rain", "snow"):   # crickets: trains of short 4.6 kHz pulses
        tk = rng.uniform(0.2, 0.9)
        while tk < N / SR - 0.3:
            for q in range(3):
                x = tt(0.018); j = int((tk + q * 0.045) * SR)
                c = np.sin(2 * np.pi * 4600 * x) * np.hanning(len(x))
                amb[j:j + len(c)] += c[:N - j] * 0.25
            tk += rng.uniform(0.7, 1.4)
    for kind in W.get("animals", []):
        tk = rng.uniform(1.0, 3.0)
        while tk < N / SR - 1.0:
            if kind == "birds":                                     # two or three quick rising tweets
                for q in range(rng.integers(2, 4)):
                    x = tt(0.07); f = 3200 + 1600 * x / x[-1]
                    c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.hanning(len(x))
                    j = int((tk + q * 0.11) * SR); amb[j:j + len(c)] += c[:N - j] * 0.12
                tk += rng.uniform(3.0, 6.0)
            elif kind == "pigeons":                                 # soft "hoo-hoo-rrroo" coo
                for q, (f0, d) in enumerate(((420, 0.16), (440, 0.16), (380, 0.45))):
                    x = tt(d); f = f0 * (1 + 0.04 * np.sin(2 * np.pi * 28 * x))
                    c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.hanning(len(x))
                    j = int((tk + q * 0.22) * SR); amb[j:j + len(c)] += c[:N - j] * 0.10
                tk += rng.uniform(4.0, 8.0)
            elif kind == "seagulls":                                # falling "kee-ow"
                x = tt(0.45); f = 1300 - 600 * (x / x[-1]) ** 0.7
                ph = 2 * np.pi * np.cumsum(f) / SR
                c = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * np.hanning(len(x))
                j = int(tk * SR); amb[j:j + len(c)] += c[:N - j] * 0.08
                tk += rng.uniform(5.0, 9.0)
            else:
                break
    if indoors:
        amb = lp(amb, 5000)                                            # birds heard through the window
        tick = tt(0.012)
        tk = 0.37
        while tk < N / SR - 0.05:                                     # the wall clock
            j = int(tk * SR)
            c = bp(rng.standard_normal(len(tick)), 2500, 7000) * np.exp(-tick * 600)
            amb[j:j + len(c)] += c[:N - j] * 0.10
            tk += 1.0
    return amb


AMB_W = {"rain": 0.22, "snow": 0.08}.get(W.get("weather"), 0.12)
# ---- where grandpa is: inside the cabin (walls between him and the world) or out in it; the stream mic is the one he carries
fpath = np.array(P["path"])
CABIN = (-1.6, 1.4, -0.9, 1.6)
inside_f = ((fpath[:, 0] > CABIN[0]) & (fpath[:, 0] < CABIN[1]) & (fpath[:, 1] > CABIN[2]) & (fpath[:, 1] < CABIN[3])).astype(float) \
    if W.get("interior") == "cabin" else np.zeros(len(fpath))
door = W.get("door_open")
door_f = np.array([C.smooth((f / FPS - door[0]) / max(1e-3, door[1] - door[0])) for f in range(len(fpath))]) if door else np.zeros(len(fpath))
walls_f = inside_f * (1 - 0.7 * door_f)                         # 1 = shut in; an open door lets most of the outside in
k_s = np.convolve(np.pad(walls_f, (15, 15), mode="edge"), np.ones(31) / 31, mode="valid")
walls = np.interp(t_all, np.arange(len(k_s)) / FPS, k_s)
if W.get("terrain") == "forest_west" and W.get("interior") == "cabin":
    amb_in, amb_out = ambience(True), ambience(False)
    amb_now = amb_in * walls + amb_out * (1 - walls)
    sx = lambda y: -5.2 + 0.25 * np.sin(y * 0.7)                  # the stream (same line as bl_world.STREAM_X)
    d_stream = np.abs(fpath[:, 0] - sx(fpath[:, 1]))
    g_s = np.interp(t_all, np.arange(len(fpath)) / FPS, np.clip(1.2 / (d_stream + 0.6), 0.05, 1.2))
    babble = bp(rng.standard_normal(N), 350, 2600) * (0.7 + 0.3 * np.sin(2 * np.pi * t_all * 0.37) * np.sin(2 * np.pi * t_all * 1.13))
    amb_now = amb_now + babble * g_s * (1 - 0.85 * walls) * 0.9
    rich = P.get("engine_rev", 1) >= 3                             # rev 3: richer forest (rustle, second songbird)
    gust = np.full(N, 0.25 if rich else 0.0)                       # leaves rustle in the breeze (louder when it gusts)
    Lf = W.get("leaves")
    if Lf:
        gust += 0.9 * np.clip(np.minimum((t_all - Lf["t0"] + 1.0) / 1.0, (Lf["t1"] + 2.5 - t_all) / 1.5), 0, 1)
    for tm, hw, depth, *_ in W.get("clouds_pass", []):
        gust += 0.5 * depth * np.clip(1 - np.abs(t_all - tm) / (hw + 0.5), 0, 1)
    if rich:                                                       # (no random draws otherwise: older scenes sound the same)
        rustle = bp(rng.standard_normal(N), 1800, 7000) * (0.6 + 0.4 * np.sin(2 * np.pi * t_all * 0.23) ** 2)
        amb_now = amb_now + rustle * gust * (1 - walls) * 0.35
    tk = 2.3 if rich else 1e9                                      # a second songbird: a quick falling trill
    while tk < N / SR - 1.0:
        for q in range(7):
            x = tt(0.035); f = 4200 - 160 * q
            c = np.sin(2 * np.pi * f * x) * np.hanning(len(x))
            j = int((tk + q * 0.05) * SR); amb_now[j:j + len(c)] += c[:N - j] * 0.07 * (1 - walls[min(j, N - 1)])
        tk += rng.uniform(4.5, 7.5)
    stems["ambience"][:N] += amb_now
else:
    stems["ambience"][:N] += ambience()
def heard(t, x, y, k=0.5, lo=0.08, hi=0.6):                    # a sound at (x, y), heard at grandpa (his webcam is the mic)
    f = min(len(fpath) - 1, max(0, int(t * FPS)))
    return float(np.clip(k / (float(np.hypot(fpath[f, 0] - x, fpath[f, 1] - y)) + 0.4), lo, hi))


def huff():                       # a wild boar's warning: an explosive blast of breath through the nose, a grunt under it
    t = tt(0.42)
    blast = bp(rng.standard_normal(len(t)), 250, 3200) * np.exp(-t * 9) * (1 - np.exp(-t * 400))
    grunt = np.sin(2 * np.pi * np.cumsum(95 * (1 - 0.3 * t)) / SR) * np.exp(-t * 11) * (0.6 + 0.4 * (rng.random(len(t)) > 0.5))
    return lp(blast * 1.0 + lp(grunt, 700) * 0.5, 4500)


def tusk_clack():                 # tusks and teeth snapping together, twice
    out = np.zeros(int(0.3 * SR))
    for dt in (0.0, 0.13):
        x = tt(0.05); c = modes(x, rng.uniform(0.95, 1.05), ((1900, 1.0, 120), (3300, 0.6, 160), (5200, 0.3, 220)))
        c = (c + bp(rng.standard_normal(len(x)), 2000, 8000) * np.exp(-x * 500) * 0.6) * (1 - np.exp(-x * 5000))
        j = int(dt * SR); out[j:j + len(c)] += c[:len(out) - j]
    return out * 0.6


def hoof_stomp():                 # a hard hoof slammed on the earth: a low thud and a scatter of dirt
    x = tt(0.35)
    thud = lp(thunk(0.55, 0.3), 500) * 1.2
    dirt = bp(rng.standard_normal(len(x)), 900, 5000) * np.exp(-x * 14) * 0.25
    return np.pad(thud, (0, len(x) - len(thud))) + dirt


def squeal():                     # startled: a short rising squeal
    x = tt(0.38)
    f = 520 + 900 * np.sin(np.pi * x / x[-1])
    v = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return bp(v + bp(rng.standard_normal(len(x)), 800, 4000) * 0.3, 300, 5000) * np.hanning(len(x)) * 0.5


for c in W.get("critters", []):
    if c["kind"] == "boar":                                     # trotting hooves, huffs, tusk clacks, stomps, a squeal
        for ts in C.actor_steps(c):
            x, y = C.critter_state(dict(c, hop=0.0), ts)[:2]
            place(stems["build"], ts, lp(thunk(0.9, 0.06), 1200) * 0.7, heard(ts, x, y, 0.4))
        for key, snd, g in (("huffs", huff, 0.9), ("clacks", tusk_clack, 0.7), ("stomps", hoof_stomp, 1.0)):
            for ts in c.get(key, []):
                x, y = C.critter_state(dict(c, hop=0.0), ts)[:2]
                place(stems["fx"], ts, snd(), g * heard(ts, x, y, 0.8, 0.15, 1.0))
        if c.get("startle") is not None:
            x, y = C.critter_state(dict(c, hop=0.0), c["startle"])[:2]
            place(stems["fx"], c["startle"] + 0.03, squeal(), heard(c["startle"], x, y, 0.8, 0.15, 1.0))
        continue
    if c["kind"] == "memory_cloud":                             # the remembered boar: faint, far off, reverberant
        b = c.get("boar", {})
        for key, snd, g in (("huffs", huff, 0.5), ("clacks", tusk_clack, 0.35), ("stomps", hoof_stomp, 0.45)):
            for ts in b.get(key, []):
                place(stems["fx"], ts, lp(reverb(snd(), 1.2, 0.5), 3000), g)
        continue
    if c["kind"] == "hologram":                                 # a soft rising shimmer as the drawing lifts off the page
        x = tt(1.2)
        f = 880 + 660 * x / x[-1]
        sh = sum(a * np.sin(2 * np.pi * np.cumsum(f * m) / SR) for m, a in ((1.0, 0.5), (1.5, 0.25), (2.0, 0.15)))
        place(stems["fx"], c["visible"][0], sh * np.hanning(len(x)) * 0.12)
        continue
    if c["kind"] == "tobias":                                   # a kid's light footsteps on the grass
        for ts in C.actor_steps(dict(c, stride=c.get("stride", 0.16))):
            x, y = C.critter_state(dict(c, hop=0.0), ts)[:2]
            place(stems["build"], ts, step() * 0.6, heard(ts, x, y, 0.4))
        continue
    for tl in C.critter_landings(c):                            # a rabbit's soft thumps on the grass, as heard at grandpa
        f = min(len(fpath) - 1, int(tl * FPS))
        x, y = C.critter_state(c, tl)[:2]
        d = float(np.hypot(fpath[f, 0] - x, fpath[f, 1] - y))
        th = lp(thunk(1.3, 0.07), 900) + lp(rng.standard_normal(len(tt(0.07))), 1200) * np.exp(-tt(0.07) * 60) * 0.4
        place(stems["build"], tl, th, float(np.clip(0.5 / (d + 0.4), 0.08, 0.6)))
for a in P["actions"]:                                          # trip hammer: one clunk per cam strike, as heard at grandpa
    if a["type"] != "trip":
        continue
    src = np.array(a.get("sound_at", [0.0, 0.0, 0.0]))
    for sk in C.trip_strikes(a, 0.0, P["film"] + 0.5):
        f = min(len(fpath) - 1, int(sk * FPS))
        d = float(np.linalg.norm(fpath[f, :2] - src[:2]))
        base = mix(thunk(0.55, 0.35), block_sound("wood", 0.6) * 0.8)             # the very same clunk as Scene 001
        if walls_f[f] > 0.5:                                    # through the cabin walls: Scene 001's muffled version
            x = reverb(lp(base, 900), 1.1, 0.55); g = 1.0
        else:
            x = reverb(lp(base, float(np.clip(9000 / (1 + d), 1200, 7000))), 0.8, float(np.clip(0.12 * d, 0.1, 0.5)))
            g = float(np.clip(3.2 / (d + 0.8), 1.0, 3.0))
        place(stems["fx"], sk, x, g * a.get("gain", 1.0))

for k in stems:
    stems[k] = stems[k][:N]
    if NL:                                          # what plays past the cut becomes the opening, crossfading into it
        w = np.linspace(0.0, 1.0, NL)
        stems[k][:NL] = stems[k][:NL] * w + stems[k][N0:N0 + NL] * (1 - w)
    stems[k] = stems[k][:N0]
N = N0
t_all = t_all[:N0]
norm = lambda s: s / max(1e-9, np.abs(s).max())
bed = hp(0.8 * norm(stems["build"]) + 0.9 * norm(stems["fx"]) + AMB_W * norm(stems["ambience"]), 30)
_, v = wav.read(os.path.join(OUT, "voice.wav"))
v = v.astype(np.float64)[:N] / 32768
v = np.pad(v, (0, N - len(v)))
active = lp((np.abs(v) > 0.02).astype(float), 3)
duck = 1 - 0.5 * np.clip(active / max(1e-9, active.max()), 0, 1)
for ln in P["lines"]:
    a, z = int(ln["start"] * SR), int(ln["end"] * SR)
    need = 10 ** (9 / 20) * np.sqrt(np.mean((bed[a:z] * duck[a:z]) ** 2) + 1e-12) / np.sqrt(np.mean(v[a:z] ** 2))
    v[a:z] *= max(need, 1.0)
mix = bed * duck + v
stems["voice"] = v
mix = mix / np.abs(mix).max()
mix = mix * 0.5
pre = os.path.join(OUT, "mix_pre.wav")
wav.write(pre, SR, (np.stack([mix, mix], 1) * 32767).astype(np.int16))
def integrated_lufs(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(json.loads(p.stderr[p.stderr.rindex("{"):p.stderr.rindex("}") + 1])["input_i"])


# -14 LUFS: add the missing gain, then a brick-wall peak limiter (which gives a little back), and repeat until within 0.3 dB
gain, out_wav = 0.0, os.path.join(OUT, "mix.wav")
lufs = integrated_lufs(pre)
for _ in range(4):
    gain += -14.0 - lufs
    af = "volume=%.2fdB,alimiter=limit=0.75:attack=2:release=60:level=false" % gain
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", af, "-ar", "48000", out_wav], check=True)
    lufs = integrated_lufs(out_wav)
    if abs(lufs + 14.0) < 0.3:
        break
os.remove(pre)
for k, s in stems.items():
    wav.write(os.path.join(OUT, "stem_%s.wav" % k), SR, (np.clip(norm(s) * 0.7, -1, 1) * 32767).astype(np.int16))
print("audio ok: %.2f s, %d block sounds, %d footsteps" % (N / SR, sum(1 for b in P["blocks"] if not b["prebuilt"]), len(P["steps"])))
