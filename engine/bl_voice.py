"""Block Lab: grandpa's lines -> build/audio/voice.wav + build/dialogue.json (timings, mouth curve), then the plan.

    python bl_voice.py --story stories/giants.json
(KOKORO_MODEL / KOKORO_VOICES env vars point at the Kokoro model files.)
"""
import json
import math
import os
import shutil

import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import butter, resample_poly, sosfilt

import bl_common as C

SR = 48000
MODEL = os.environ.get("KOKORO_MODEL", "/home/user/tts/kokoro-q8-timed.onnx")
VOICES = os.environ.get("KOKORO_VOICES", "/home/user/tts/voices.bin")


def main():
    path = C.story_path()
    story = C.load_story(path)
    os.makedirs(os.path.join(C.BUILD, "audio"), exist_ok=True)
    if os.path.abspath(path) != os.path.join(C.BUILD, "story.json"):
        shutil.copy(path, os.path.join(C.BUILD, "story.json"))
    from kokoro_onnx import Kokoro
    k = Kokoro(MODEL, VOICES)
    clips = []
    for ln in story["lines"]:
        a, sr = k.create(ln["text"], voice=ln.get("voice", story["voice"]), speed=ln.get("speed", story["speed"]))[:2]
        a = resample_poly(np.asarray(a, dtype=np.float64), SR // 1000, sr // 1000)
        env = np.convolve(np.abs(a), np.ones(240) / 240, mode="same")
        idx = np.where(env > 0.01 * env.max())[0]
        clips.append(a[max(0, idx[0] - 480): idx[-1] + 960])
    meta, t = [], story["start"]
    for ln, a in zip(story["lines"], clips):
        meta.append(dict(id=ln["id"], text=ln["text"], start=round(t, 3), end=round(t + len(a) / SR, 3)))
        t += len(a) / SR + ln.get("pause", 0.45)
    film = math.ceil((meta[-1]["end"] + story["tail"]) * C.FPS) / C.FPS
    nf = int(round(film * C.FPS))
    N = int(film * SR)
    track = np.zeros(N)
    for m, a in zip(meta, clips):
        j = int(round(m["start"] * SR))
        track[j:j + len(a)] += a[:N - j]
    track = sosfilt(butter(2, 90, "highpass", fs=SR, output="sos"), track)
    track = sosfilt(butter(2, 9000, "lowpass", fs=SR, output="sos"), track)
    track *= 0.7 / np.abs(track).max()
    spf = SR // C.FPS
    rms = np.array([np.sqrt(np.mean(track[f * spf:(f + 1) * spf] ** 2)) for f in range(nf)])
    mouth = np.clip((rms / (rms.max() + 1e-9) - 0.06) / 0.55, 0, 1) ** 0.8
    mouth = np.convolve(mouth, [0.25, 0.5, 0.25], mode="same")
    wav.write(os.path.join(C.BUILD, "audio", "voice.wav"), SR, (track * 32767).astype(np.int16))
    json.dump(dict(voice=story["voice"], film=film, nf=nf, lines=meta, mouth=[round(float(m), 3) for m in mouth]),
              open(os.path.join(C.BUILD, "dialogue.json"), "w"), indent=1)
    for m in meta:
        print("%6.2f-%6.2f  %s" % (m["start"], m["end"], m["text"]))
    plan = C.make_plan(story)
    C.save_plan(plan)
    print("film %.2f s (%d frames); plan written" % (film, nf))


if __name__ == "__main__":
    main()
