import numpy as np
from scipy.io import wavfile
from kokoro_onnx import Kokoro
k = Kokoro("/home/user/tts/full/kokoro-v1.0.onnx", "/home/user/tts/full/voices-v1.0.bin")
# (spoken text, speed, silence after in seconds -- the silences stand for the action between lines)
L = [("Chat, Tobias's garden is right where the boar livs. So... we're building him a safe one. Out in the open, by my cabin.", 0.95, 3.0),
     ("My knees remember this.", 0.95, 2.5),
     ("A garden fence. With a lever gate.", 0.95, 2.0),
     ("Post. Rail. Post. Rail. Chat, this is my cardio.", 0.95, 3.0),
     ("A rock? For... vibes? Nah. Skip.", 0.95, 2.5),
     ("This gate is NOT... giving.", 0.95, 2.0),
     ("Ohh. It's a seesaw.", 0.95, 0.6),
     ("Like a seesaw: put your big cousin on the short end, and the little kid can lift the long end.", 0.95, 0.5),
     ("Drawbridges work the same way.", 0.95, 2.0),
     ("Now THAT'S got... rizz.", 0.95, 1.5),
     ("A boar-proof garden. Tobias is gonna flip.", 0.95, 2.5),
     ("Being scared's normal. Building something... helps.", 0.88, 0.5),
     ("Don't tell Tobias I said that.", 0.95, 2.0),
     ("...Is that... page thirteen?", 0.95, 1.0)]
out, sr = [np.zeros(int(0.5 * 24000))], 24000
for text, speed, gap in L:
    a, sr = k.create(text, voice="am_santa", speed=speed)
    a = np.asarray(a, dtype=np.float64)
    env = np.convolve(np.abs(a), np.ones(120) / 120, mode="same")
    idx = np.where(env > 0.01 * env.max())[0]
    out += [a[max(0, idx[0] - 240): idx[-1] + 480], np.zeros(int(gap * sr))]
y = np.concatenate(out); y = y / np.abs(y).max() * 0.9
wavfile.write("scene007_tableread.wav", sr, (y * 32767).astype(np.int16)); print("%.1f s" % (len(y) / sr))
