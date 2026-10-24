"""Narration for the Frankenstein lab test: Mary Shelley, Frankenstein (1818), ch. 5 (public domain), British voice."""
import json, numpy as np, scipy.io.wavfile as wav
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
K = Kokoro("/home/user/tts/kokoro-q8-timed.onnx", "/home/user/tts/voices.bin")
PARTS = [("night", "It was on a dreary night of November that I beheld the accomplishment of my toils.", 0.6),
         ("spark", "With an anxiety that almost amounted to agony, I collected the instruments of life around me, "
                   "that I might infuse a spark of being into the lifeless thing that lay at my feet.", 0.7),
         ("candle", "It was already one in the morning; the rain pattered dismally against the panes, and my candle was nearly burnt out,", 0.35),
         ("eye", "when, by the glimmer of the half-extinguished light, I saw the dull yellow eye of the creature open;", 0.5),
         ("limbs", "it breathed hard, and a convulsive motion agitated its limbs.", 0.0)]
SR, t, out, meta = 48000, 1.2, [], []
for pid, text, pause in PARTS:
    a, sr = K.create(text, voice="bm_george", speed=0.88)[:2]
    a = resample_poly(np.asarray(a, dtype=np.float64), SR // 1000, sr // 1000)
    env = np.convolve(np.abs(a), np.ones(240) / 240, mode="same"); idx = np.where(env > 0.01 * env.max())[0]
    a = a[max(0, idx[0] - 480): idx[-1] + 960]
    meta.append(dict(id=pid, text=text, start=round(t, 3), end=round(t + len(a) / SR, 3)))
    out.append((t, a)); t += len(a) / SR + pause
total = t + 3.2
track = np.zeros(int(total * SR))
for t0, a in out:
    j = int(t0 * SR); track[j:j + len(a)] += a
track *= 0.6 / np.abs(track).max()
wav.write("voice.wav", SR, (track * 32767).astype(np.int16))
json.dump(dict(parts=meta, total=round(total, 3)), open("voice.json", "w"), indent=1)
for m in meta: print("%6.2f-%6.2f %s" % (m["start"], m["end"], m["id"]))
print("total %.2f s" % total)
