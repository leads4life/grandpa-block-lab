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


CAST = {                                            # other speakers: Kokoro voice + speed + voice effect (fixed, so they
    "tobias": dict(voice="am_santa", speed=1.12,    # sound the same in every line and scene). Tobias: Grandpa's own voice,
                   fx=dict(tone=1.33, pitch=1.203, highpass=150)),   # made a young kid's (user-picked "G4", ~270 Hz)
}


def apply_fx(a, sr, fx):
    """Voice effect with ffmpeg: tone (a smaller voice box: pitch and formants up together), then pitch on its own
    (rubberband, formants kept), then a high-pass to take out the adult chest rumble."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
        wav.write(src, sr, (np.clip(a, -1, 1) * 32767).astype(np.int16))
        tone = fx.get("tone", 1.0)
        af = "asetrate=%d,aresample=%d,atempo=%.5f,rubberband=pitch=%.5f:formant=preserved:window=short:pitchq=quality,highpass=f=%d" % (
            int(round(sr * tone)), sr, 1 / tone, fx.get("pitch", 1.0), fx.get("highpass", 20))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-ar", str(sr), dst], check=True)
        r, b = wav.read(dst)
    return b.astype(np.float64) / 32767


def main():
    path = C.story_path()
    story = C.load_story(path)
    os.makedirs(os.path.join(C.BUILD, "audio"), exist_ok=True)
    if os.path.abspath(path) != os.path.join(C.BUILD, "story.json"):
        shutil.copy(path, os.path.join(C.BUILD, "story.json"))
    from kokoro_onnx import Kokoro
    k = Kokoro(MODEL, VOICES)
    clips = []
    cast = dict(CAST, **story.get("cast", {}))
    for ln in story["lines"]:
        who = cast.get(ln.get("who"), {})                  # a line with no "who" is Grandpa, exactly as before
        a, sr = k.create(ln["text"], voice=ln.get("voice", who.get("voice", story["voice"])),
                         speed=ln.get("speed", who.get("speed", story["speed"])))[:2]
        a = np.asarray(a, dtype=np.float64)
        if who.get("fx"):
            a = apply_fx(a, sr, who["fx"])
        a = resample_poly(a, SR // 1000, sr // 1000)
        env = np.convolve(np.abs(a), np.ones(240) / 240, mode="same")
        idx = np.where(env > 0.01 * env.max())[0]
        clips.append(a[max(0, idx[0] - 480): idx[-1] + 960])
    meta, t = [], story["start"]
    for ln, a in zip(story["lines"], clips):
        meta.append(dict(id=ln["id"], text=ln["text"], start=round(t, 3), end=round(t + len(a) / SR, 3)))
        if ln.get("who"):
            meta[-1]["who"] = ln["who"]
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

    def mouth_of(tr):
        rms = np.array([np.sqrt(np.mean(tr[f * spf:(f + 1) * spf] ** 2)) for f in range(nf)])
        m = np.clip((rms / (rms.max() + 1e-9) - 0.06) / 0.55, 0, 1) ** 0.8
        return np.convolve(m, [0.25, 0.5, 0.25], mode="same")
    speakers = sorted({m["who"] for m in meta if m.get("who")})
    if speakers:                                       # each speaker's jaw follows only their own lines
        mouths = {}
        for who in [None] + speakers:
            tr = np.zeros(N)
            for m, a in zip(meta, clips):
                if m.get("who") == who:
                    j = int(round(m["start"] * SR)); tr[j:j + len(a)] += a[:N - j]
            mouths[who or "grandpa"] = mouth_of(tr * 0.7 / np.abs(track).max())
        mouth = mouths["grandpa"]
    else:
        mouth, mouths = mouth_of(track), None
    wav.write(os.path.join(C.BUILD, "audio", "voice.wav"), SR, (track * 32767).astype(np.int16))
    out = dict(voice=story["voice"], film=film, nf=nf, lines=meta, mouth=[round(float(m), 3) for m in mouth])
    if mouths:
        out["mouths"] = {k_: [round(float(m), 3) for m in v] for k_, v in mouths.items()}
    json.dump(out, open(os.path.join(C.BUILD, "dialogue.json"), "w"), indent=1)
    for m in meta:
        print("%6.2f-%6.2f  %s" % (m["start"], m["end"], m["text"]))
    plan = C.make_plan(story)
    C.save_plan(plan)
    print("film %.2f s (%d frames); plan written" % (film, nf))


if __name__ == "__main__":
    main()
