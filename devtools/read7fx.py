"""Scene 007 rewrite, table read WITH sound effects: Grandpa's voice + the show's own procedural sounds (from bl_audio)."""
import numpy as np, sys
from scipy.io import wavfile
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
sys.path.insert(0, "/home/user/blocklab")
# the sound kit: bl_audio's definitions (everything above its per-story mixing), with a stand-in plan
src = open("/home/user/blocklab/bl_audio.py").read()
kit = src[:src.index('stems = {k: np.zeros')]
kit = kit.replace("P = C.load_plan()", 'P = {"fps": 30, "film": 90.0}').replace('OUT = os.path.join(C.BUILD, "audio")', 'OUT = "."')
boar = src[src.index("def huff():"):src.index("def squeal():")]
K = {"__name__": "kit"}
exec(compile(kit + "\n" + boar, "bl_audio_kit", "exec"), K)
SR, place, mix, rng = K["SR"], K["place"], K["mix"], K["rng"]

k = Kokoro("/home/user/tts/full/kokoro-v1.0.onnx", "/home/user/tts/full/voices-v1.0.bin")
L = [("plan", "Chat, Tobias's garden is right where the boar livs. So... we're building him a safe one. Out in the open, by my cabin.", 0.95, 0.5),
     ("seed", "Then we move his seedlings in. The ones the boar left.", 0.95, 2.8),
     ("knees", "My knees remember this.", 0.95, 2.5),
     ("page", "A garden fence. With a lever gate.", 0.95, 2.0),
     ("cardio", "Post. Rail. Post. Rail. Chat, this is my cardio.", 0.95, 1.6),
     ("faster", "...Nope. Faster.", 1.0, 2.2),
     ("lift", "A lift gate. Boars push gates open... but they can't lift one.", 0.95, 1.0),
     ("vibes", "A rock? For... vibes? Nah. Skip.", 0.95, 2.5),
     ("giving", "This gate is NOT... giving.", 0.95, 2.0),
     ("seesaw", "Ohh. It's a seesaw.", 0.95, 0.6),
     ("cousin", "Like a seesaw: put your big cousin on the short end, and the little kid can lift the long end.", 0.95, 0.5),
     ("draw", "Drawbridges work the same way.", 0.95, 2.0),
     ("rizz", "Now THAT'S got... rizz.", 0.95, 1.6),
     ("shuts", "And it shuts by itself.", 0.95, 0.6),
     ("flip", "A boar-proof garden. Tobias is gonna flip.", 0.95, 2.5),
     ("scared", "Being scared's normal. Building something... helps.", 0.88, 0.5),
     ("tobias", "Don't tell Tobias I said that.", 0.95, 2.0),
     ("bottle", "...Is that... page thirteen?", 0.95, 1.5)]
T, voice, t = {}, [], 0.8
for lid, text, speed, gap in L:
    a, sr = k.create(text, voice="am_santa", speed=speed)
    a = np.asarray(a, dtype=np.float64)
    env = np.convolve(np.abs(a), np.ones(120) / 120, mode="same")
    idx = np.where(env > 0.01 * env.max())[0]
    a = resample_poly(a[max(0, idx[0] - 240): idx[-1] + 480], SR // 1000, sr // 1000)
    T[lid] = (t, t + len(a) / SR, t + len(a) / SR + gap)              # start, end, next line
    voice.append((t, a)); t += len(a) / SR + gap
N = int((t + 0.8) * SR)
v = np.zeros(N); fx = np.zeros(N); amb = np.zeros(N)
for t0, a in voice:
    place(v, t0, a / np.abs(a).max() * 0.8)
s_, e_, n_ = lambda i: T[i][0], lambda i: T[i][1], lambda i: T[i][2]
# ambience: soft wind, the stream close by, birds now and then
ta = np.arange(N) / SR
amb += K["lp"](rng.standard_normal(N), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * ta / 7.3)) * 0.25
amb += K["bp"](rng.standard_normal(N), 400, 3500) * (0.7 + 0.3 * np.sin(2 * np.pi * ta / 1.7) * np.sin(2 * np.pi * ta / 2.9)) * 0.10
for tb in np.arange(2.0, N / SR - 1, 6.5):
    place(amb, tb + rng.uniform(0, 2), K["chime"](rng.uniform(2600, 3400), 0.12) * 0.15)
# the trip hammer next door, still on its 3.3 s clock (CLUNK-CLUNK... rest)
for tc in np.arange(1.3, N / SR, 3.3):
    for off in (0.0, 0.55):
        place(fx, tc + off, mix(K["thunk"](0.55, 0.35), K["block_sound"]("wood", 0.6) * 0.8), 0.22)
# 1-2. walking to the stream; wobbling over the stepping stones; the webcam set down on the bank stone
for ts in np.arange(e_("plan") + 0.2, n_("seed") + 0.1, 0.45):
    place(fx, ts, K["step"](), 0.35)
for j, ts in enumerate(np.arange(s_("knees") - 0.2, n_("knees") - 1.0, 0.5)):
    place(fx, ts, K["block_sound"]("stone", 0.9 + 0.1 * (j % 2)) * 0.5, 0.45)
place(fx, n_("knees") - 0.5, K["sfx"]("settle"), 0.5)
place(fx, s_("page") - 0.5, K["sfx"]("page"), 0.6)
# 3-4. the fence: posts and rails, block by block; then the gate
for tb in np.arange(e_("page") + 0.4, e_("cardio") + 0.4, 0.2):
    place(fx, tb + rng.uniform(-0.03, 0.03), K["block_sound"]("wood", rng.uniform(0.9, 1.1)), rng.uniform(0.3, 0.45))
place(fx, e_("cardio") + 0.5, K["sfx"]("rustle"), 0.55)                 # something in the woods...
for tb in np.arange(e_("faster") + 0.1, n_("faster") - 0.1, 0.11):     # ...he builds twice as fast
    place(fx, tb + rng.uniform(-0.02, 0.02), K["block_sound"]("wood", rng.uniform(0.95, 1.15)), rng.uniform(0.3, 0.45))
for tb in np.arange(e_("lift") + 0.0, s_("vibes") - 0.1, 0.25):
    place(fx, tb, K["block_sound"]("planks", rng.uniform(0.9, 1.1)), 0.45)
# 5. oops: straining at the gate; his back creaks
place(fx, e_("vibes") + 0.6, K["creak"](0.7), 0.35)
place(fx, e_("vibes") + 1.7, K["sfx"]("creak"), 0.6)
# 6. checking the page
place(fx, e_("giving") + 0.4, K["sfx"]("page"), 0.6)
# 7. the rock goes on; one finger; the gate swings up
place(fx, e_("draw") + 0.4, K["block_sound"]("stone", 0.8), 0.8)
place(fx, e_("draw") + 1.2, K["creak"](0.9), 0.45)
place(fx, e_("rizz") + 0.3, K["creak"](0.8), 0.4)                    # he lets go: it drifts back down...
place(fx, e_("rizz") + 1.3, K["thunk"](0.8, 0.15), 0.5)                 # ...and shuts
# 9. the memory cloud: a faint, far-off boar huff
place(fx, e_("flip") + 0.6, K["lp"](K["reverb"](K["huff"](), 1.2, 0.5), 3000), 0.45)
# 10. the bottle bobbing down the stream
place(fx, e_("tobias") + 0.6, K["sfx"]("clink"), 0.25)
place(fx, e_("tobias") + 1.4, K["sfx"]("clink"), 0.18)
y = v * 1.0 + fx * 0.9 + amb * 0.8
y = y / np.abs(y).max() * 0.9
wavfile.write("scene007_tableread_fx.wav", SR, (y * 32767).astype(np.int16))
print("%.1f s" % (N / SR)); print({k_: tuple(round(x, 1) for x in v_) for k_, v_ in T.items()})
