"""Finish the Frankenstein lab test: sound (narration + rain + thunder on every flash + spark crackles), captions,
titles, and the MP4.    python3 compose.py   (after lab.py --render)"""
import json
import os
import subprocess

import bpy
import numpy as np
import scipy.io.wavfile as wav
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import butter, sosfilt
import sys
sys.path.insert(0, "/home/user/blocklab")
import voxelkit as VK  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, SR, W, H = 30, 48000, 1080, 1920
V = json.load(open(os.path.join(HERE, "voice.json")))
NF = int(V["total"] * FPS)
N = int(NF / FPS * SR)
rng = np.random.default_rng(1818)

# ---- read the flash and spark keys from the scene, so the sound lands exactly on the picture
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "lab.blend"))


def keyed_frames(datablock, path, above):
    return sorted(kp.co[0] for c in VK.fcurves_of(datablock) if c.data_path == path for kp in c.keyframe_points if kp.co[1] > above)


flash_f = keyed_frames(bpy.data.lights["Flash"], "energy", 800)
spark_f = keyed_frames(bpy.data.lights["SparkLight"], "energy", 30)
strikes = [fr for i, fr in enumerate(flash_f) if i == 0 or fr - flash_f[i - 1] > 15]
print("strikes at", [round(x / FPS, 2) for x in strikes], "| sparks:", len(spark_f))

# ---- sound
def lowpass(x, hz, order=2):
    return sosfilt(butter(order, hz, "lowpass", fs=SR, output="sos"), x)


def band(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)


voice = wav.read(os.path.join(HERE, "voice.wav"))[1].astype(np.float64) / 32768
mix = np.zeros(N)
mix[:min(N, len(voice))] += voice[:N]
rain = band(rng.standard_normal(N), 900, 7000) * 0.025 + lowpass(rng.standard_normal(N), 400) * 0.02
mix += rain * (0.8 + 0.2 * np.sin(np.arange(N) / SR * 0.7))
for fr in strikes:                                          # a close storm: a crack, then a long rolling rumble
    t0 = fr / FPS + 0.35
    n = int(4.5 * SR)
    j = int(t0 * SR)
    tt = np.arange(n) / SR
    crack = band(rng.standard_normal(n), 300, 5000) * np.exp(-tt / 0.12) * 0.5
    roll = lowpass(rng.standard_normal(n), 140, 3) * 3.0 * (1 - np.exp(-tt / 0.15)) * np.exp(-tt / 1.6)
    roll *= 0.7 + 0.3 * np.abs(np.sin(tt * 5.3)) ** 2
    seg = crack + roll
    mix[j:j + n] += seg[:max(0, min(n, N - j))]
for fr in spark_f:                                          # electric crackle
    j, n = int(fr / FPS * SR), int(0.07 * SR)
    burst = band(rng.standard_normal(n), 2000, 9000) * (rng.random(n) > 0.6) * 0.22
    mix[j:j + n] += burst[:max(0, min(n, N - j))]
mix = np.tanh(mix * 1.2) / 1.2
mix *= 0.89 / np.abs(mix).max()
stereo = np.stack([mix, mix], axis=1)
wav.write(os.path.join(HERE, "mix.wav"), SR, (stereo * 32767).astype(np.int16))

# ---- captions: each passage split into short phrases, timed by their share of words
FD = "/usr/share/fonts/truetype/dejavu"
fcap, ftag, ftitle, fsub = (ImageFont.truetype(os.path.join(FD, n), s) for n, s in
                            (("DejaVuSans-Bold.ttf", 52), ("DejaVuSans-Bold.ttf", 30), ("DejaVuSerif-Bold.ttf", 120), ("DejaVuSerif.ttf", 40)))
caps = []
for p in V["parts"]:
    words = p["text"].split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 26 or w.endswith((",", ";", ".")):
            chunks.append(" ".join(cur)); cur = []
    if cur:
        chunks.append(" ".join(cur))
    total = sum(len(c) for c in chunks)
    t = p["start"]
    for c in chunks:
        d = (p["end"] - p["start"]) * len(c) / total
        caps.append((t, t + d, c))
        t += d


def outlined(d, xy, s, font, fill, a=1.0, stroke=6):
    d.text(xy, s, font=font, fill=fill + (int(255 * a),), anchor="mm", stroke_width=stroke, stroke_fill=(10, 8, 6, int(235 * a)))


T_END = V["parts"][-1]["end"] + 0.4
out = os.path.join(HERE, "frankenstein_lab_test.mp4")
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                       "-i", os.path.join(HERE, "mix.wav"), "-map", "0:v", "-map", "1:a",
                       "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k",
                       "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for fr in range(NF):
    t = fr / FPS
    src = os.path.join(HERE, "frames", "%04d.png" % fr)
    if not os.path.exists(src):                              # look test rendered at 15 fps: show each frame twice
        src = os.path.join(HERE, "frames", "%04d.png" % (fr - fr % 2))
    im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    if t < 4.0:
        a = min(1.0, t / 0.5, (4.0 - t) / 0.5)
        outlined(d, (W // 2, 230), "MARY SHELLEY'S FRANKENSTEIN (1818)", ftag, (230, 215, 180), a, 4)
        outlined(d, (W // 2, 280), "CHAPTER 5", ftag, (180, 170, 150), a, 4)
    for t0, t1, c in caps:
        if t0 <= t < t1:
            outlined(d, (W // 2, 1300), c, fcap, (255, 255, 255))
    if t >= T_END:
        a = min(1.0, (t - T_END) / 0.6)
        ov.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        d = ImageDraw.Draw(ov)
        outlined(d, (W // 2, 860), "FRANKENSTEIN", ftitle, (225, 205, 150), a, 8)
        outlined(d, (W // 2, 990), "Mary Shelley, 1818", fsub, (220, 215, 200), a, 4)
    im.alpha_composite(ov)
    ff.stdin.write(im.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()
print("wrote", out)
