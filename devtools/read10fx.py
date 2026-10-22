"""Scene 010 "Night Shift", table read WITH sound effects: Grandpa's voice (the production model) + the show's sounds,
plus first drafts of the new night sounds (owl, snore, sniffing, rooting, a happy grunt)."""
import numpy as np, sys, subprocess
from scipy.io import wavfile
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
sys.path.insert(0, "/home/user/blocklab")
src = open("/home/user/blocklab/bl_audio.py").read()
kit = src[:src.index('stems = {k: np.zeros')]
kit = kit.replace("P = C.load_plan()", 'P = {"fps": 30, "film": 90.0}').replace('OUT = os.path.join(C.BUILD, "audio")', 'OUT = "."')
boar = src[src.index("def huff():"):src.index('for c in W.get("critters", []):')]
K = {"__name__": "kit"}
exec(compile(kit + "\n" + boar, "bl_audio_kit", "exec"), K)
SR, place, mix, rng, tt, lp, bp, reverb = K["SR"], K["place"], K["mix"], K["rng"], K["tt"], K["lp"], K["bp"], K["reverb"]

# ---------------------------------------------------------------- new night sounds (drafts; they move into bl_audio once approved)
def owl():                        # a tawny owl: hoo... hoo-hoo, soft and far
    out = np.zeros(int(1.6 * SR))
    for t0, d, f in ((0.0, 0.32, 420), (0.75, 0.16, 400), (0.98, 0.42, 410)):
        x = tt(d)
        v = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.02 * np.sin(2 * np.pi * 6 * x))) / SR) * np.sin(np.pi * x / x[-1]) ** 1.5
        j = int(t0 * SR); out[j:j + len(v)] += v
    return lp(reverb(out * 0.5, 1.6, 0.6), 2500)

def snore(n=2):                   # an old man's snore: a rattling in-breath, a whistling out-breath
    out = np.zeros(int(n * 2.4 * SR))
    for k in range(n):
        x = tt(1.1); j = int(k * 2.4 * SR)
        rattle = bp(rng.standard_normal(len(x)), 80, 600) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * x)))
        out[j:j + len(x)] += rattle * np.sin(np.pi * x / x[-1]) ** 2 * 0.9
        y = tt(0.9); j2 = j + int(1.2 * SR)
        whistle = np.sin(2 * np.pi * np.cumsum(900 - 300 * y / y[-1]) / SR) * 0.08 + bp(rng.standard_normal(len(y)), 300, 2000) * 0.25
        out[j2:j2 + len(y)] += whistle * np.sin(np.pi * y / y[-1]) ** 2
    return lp(out, 3000)

def sniff(n=3):                   # quick sniffs through a snout
    out = np.zeros(int(n * 0.22 * SR + 0.2 * SR))
    for k in range(n):
        x = tt(0.12); j = int(k * 0.22 * SR)
        out[j:j + len(x)] += bp(rng.standard_normal(len(x)), 1200, 6000) * np.sin(np.pi * x / x[-1]) * 0.5
    return out

def root_dig(d=4.0):              # rooting: the snout shoving through soft earth, little grunts
    out = np.zeros(int(d * SR)); t = 0.0
    while t < d - 0.4:
        x = tt(0.25); j = int(t * SR)
        out[j:j + len(x)] += bp(rng.standard_normal(len(x)), 300, 2500) * np.exp(-x * 9) * 0.6
        if rng.random() < 0.35:
            g = tt(0.15)
            out[j:j + len(g)] += lp(np.sin(2 * np.pi * np.cumsum(110 + 30 * rng.random() * np.ones(len(g))) / SR), 600) * np.hanning(len(g)) * 0.35
        t += rng.uniform(0.25, 0.5)
    return out

def happy_grunt():                # a pleased little oink-grunt, twice
    out = np.zeros(int(0.7 * SR))
    for t0 in (0.0, 0.32):
        x = tt(0.2); f = 150 + 60 * np.sin(np.pi * x / x[-1])
        v = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        j = int(t0 * SR); out[j:j + len(v)] += lp(v, 900) * np.hanning(len(v)) * 0.5
    return out

def spark():                      # the fence's tiny pulse meeting a wet nose: a snap and a short crackle
    x = tt(0.08)
    return np.concatenate([bp(rng.standard_normal(len(x)), 3000, 9000) * np.exp(-x * 60) * 1.2, K["sfx"]("fizzle") * 0.5])

# ---------------------------------------------------------------- the lines (speed, gap after)
k = Kokoro("/home/user/tts/kokoro-q8-timed.onnx", "/home/user/tts/voices.bin")
L = [("stake", "Chat... we're whispering now. This is a stakeout.", 0.9, 2.2),
     ("hat", "I AM wearing a hat.", 0.95, 1.0),
     ("awake", "Awake! Totally awake. Eyes like an eagle.", 1.0, 1.6),          # (after the snore and the owl)
     ("medium", "Chat, I'm not scared. I'm... medium-key nervous.", 0.95, 1.4),
     ("nocap", "NO CAP, CHAT!", 1.05, 2.8),
     ("sorry", "...Sorry, buddy.", 0.85, 3.6),
     ("seedlings", "He's not even looking at the seedlings...", 0.9, 1.2),
     ("grubs", "He doesn't want the garden. He wants grubs.", 0.88, 3.4),
     ("neighbour", "Chat... I think we just met our neighbour.", 0.9, 1.8),
     ("spot", "...His own spot.", 0.88, 1.5)]
PRE = {"awake": 6.2, "medium": 0.0}                                        # extra room before a line (the nap)
LOUD = {"stake": 0.55, "hat": 0.6, "awake": 0.85, "medium": 0.6, "nocap": 1.0, "sorry": 0.55, "seedlings": 0.6,
        "grubs": 0.65, "neighbour": 0.55, "spot": 0.55}                     # whispering, mostly
T, voice, t = {}, [], 1.6
for lid, text, speed, gap in L:
    t += PRE.get(lid, 0.0)
    a, sr = k.create(text, voice="am_santa", speed=speed)[:2]
    a = np.asarray(a, dtype=np.float64)
    env = np.convolve(np.abs(a), np.ones(120) / 120, mode="same")
    idx = np.where(env > 0.01 * env.max())[0]
    a = resample_poly(a[max(0, idx[0] - 240): idx[-1] + 480], SR // 1000, sr // 1000)
    T[lid] = (t, t + len(a) / SR)
    voice.append((t, a / np.abs(a).max() * 0.8 * LOUD[lid])); t += len(a) / SR + gap
N = int((t + 1.5) * SR)
v, fx, amb = np.zeros(N), np.zeros(N), np.zeros(N)
for t0, a in voice:
    place(v, t0, a)
s_, e_ = lambda i: T[i][0], lambda i: T[i][1]
ta = np.arange(N) / SR

# night bed: a low breeze, the stream, crickets; the energizer ticking once a second
amb += lp(rng.standard_normal(N), 500) * (0.6 + 0.4 * np.sin(2 * np.pi * ta / 9.1)) * 0.12
amb += bp(rng.standard_normal(N), 400, 3000) * (0.8 + 0.2 * np.sin(2 * np.pi * ta / 2.3)) * 0.06
tk = 0.3
while tk < N / SR - 0.3:
    for q in range(3):
        x = tt(0.018); j = int((tk + q * 0.045) * SR)
        c = np.sin(2 * np.pi * 4600 * x) * np.hanning(len(x)); amb[j:j + len(c)] += c[:N - j] * 0.12
    tk += rng.uniform(0.7, 1.4)
for tt_ in np.arange(0.5, N / SR, 1.0):
    place(fx, tt_, K["sfx"]("tap"), 0.12)

# 1. the stakeout: blanket rustle, a sip from the thermos
place(fx, 0.4, K["sfx"]("settle"), 0.4)
place(fx, e_("stake") + 0.5, K["sfx"]("sip"), 0.5)
# 2. he nods off (snore), the owl wakes him
place(fx, e_("hat") + 1.2, snore(2), 0.5)
place(fx, s_("awake") - 1.2, owl(), 0.5)
place(fx, s_("awake") - 0.3, K["sfx"]("settle"), 0.6)                     # jolts upright
# 3. a rustle... a huff, close; hooves splash through the stream
place(fx, e_("medium") + 0.2, K["sfx"]("rustle"), 0.6)
place(fx, s_("nocap") - 0.5, K["huff"](), 0.9)
# 4. the boar at the fence: hooves, sniffing, the spark, the squeal, a snort, a stomp
for j, ts in enumerate(np.arange(e_("nocap") + 0.3, e_("nocap") + 1.6, 0.2)):
    place(fx, ts, mix(lp(K["thunk"](0.9, 0.06), 1200) * 0.7, bp(rng.standard_normal(int(0.08 * SR)), 500, 3000) * 0.2), 0.45)
place(fx, e_("nocap") + 1.7, sniff(4), 0.5)
place(fx, e_("nocap") + 2.6, spark(), 0.8)
place(fx, e_("nocap") + 2.63, K["squeal"](), 0.8)
place(fx, e_("nocap") + 3.1, K["huff"](), 0.6)
place(fx, e_("nocap") + 3.5, K["hoof_stomp"](), 0.7)
# 5. it trots off along the fence and starts rooting outside it
for ts in np.arange(e_("sorry") + 0.3, e_("sorry") + 1.7, 0.2):
    place(fx, ts, lp(K["thunk"](0.9, 0.06), 1200) * 0.7, 0.35)
place(fx, e_("sorry") + 1.9, root_dig(s_("neighbour") - e_("sorry") - 3.0), 0.6)
# 6. a grub! a happy grunt; hooves away into the woods
place(fx, e_("grubs") + 0.9, happy_grunt(), 0.7)
for j, ts in enumerate(np.arange(e_("grubs") + 1.8, e_("grubs") + 3.6, 0.2)):
    place(fx, ts, lp(K["thunk"](0.9, 0.06), 1200) * 0.7, 0.35 * (1 - j / 10))
place(fx, e_("spot") + 0.8, K["huff_far"]() if "huff_far" in K else K["sfx"]("huff_far"), 0.35)   # a friendly huff, far off

out = v + fx + amb
out = out / np.abs(out).max() * 0.9
wavfile.write("read10fx.wav", SR, (out * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "read10fx.wav", "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "48000",
                "-c:a", "aac", "-b:a", "160k", sys.argv[1]], check=True)
print("%.1f s" % (N / SR))
for lid, *_ in L:
    print("  %-10s %5.1f-%5.1f" % (lid, s_(lid), e_(lid)))
