"""Grandpa's Block Lab: two original piano themes (demo). Notes written here, played by FluidSynth with the FluidR3 GM
acoustic grand (MIT licence). Morning: a light swing in F. Goodnight: a slow waltz in G."""
import struct, subprocess, sys

TPB = 480


def vlq(n):
    out = [n & 0x7F]
    while n > 127:
        n >>= 7
        out.append((n & 0x7F) | 0x80)
    return bytes(reversed(out))


def write_midi(path, notes, bpm, beats_per_bar):
    """notes: (start_beat, dur_beats, pitch, velocity). One track, program 0 (acoustic grand), sustain-free."""
    ev = []
    for st, du, p, v in notes:
        ev.append((int(round(st * TPB)), 1, bytes([0x90, p, v])))
        ev.append((int(round((st + du) * TPB)), 0, bytes([0x80, p, 0])))
    ev.sort(key=lambda e: (e[0], e[1]))
    trk = vlq(0) + b"\xff\x51\x03" + struct.pack(">I", int(60_000_000 / bpm))[1:]
    trk += vlq(0) + b"\xff\x58\x04" + bytes([beats_per_bar, 2, 24, 8])
    trk += vlq(0) + bytes([0xC0, 0]) + vlq(0) + bytes([0xB0, 91, 70]) + vlq(0) + bytes([0xB0, 93, 20])   # reverb, chorus sends
    now = 0
    for t, _, data in ev:
        trk += vlq(t - now) + data
        now = t
    trk += vlq(TPB * beats_per_bar) + b"\xff\x2f\x00"
    open(path, "wb").write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, TPB) + b"MTrk" + struct.pack(">I", len(trk)) + trk)


def swing(b):
    """Swung eighths: an off-beat eighth lands two-thirds of the way through the beat."""
    whole, frac = divmod(b, 1.0)
    return whole + (2 / 3 if abs(frac - 0.5) < 1e-6 else frac)


N = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
def m(name):                                                     # "Bb4" -> MIDI number
    name = name.replace("Bb", "A#").replace("Eb", "D#")
    return 12 * (int(name[-1]) + 1) + N[name[:-1]]


# ---------------------------------------------------------------- morning: "Coffee's On" (swing, F major, 4/4)
def morning():
    bpm, bar = 100, 4
    chords = ["F2 A3 E4", "D2 F3 C4", "G2 Bb3 F4", "C2 Bb3 E4", "F2 A3 E4", "Bb1 A3 D4", "A2 G3 C4|D2 F#3 C4", "G2 F3 Bb3|C2 Bb3 E4",
              "F2 A3 E4", "D2 F3 C4", "G2 F3 Bb3|C2 Bb3 E4", "F2 A3 D4"]
    mel = [  # (bar, beat, beats, note)
        (0, 0, 1, "A4"), (0, 1, 1, "C5"), (0, 2, 2, "E5"),
        (1, 0, 1.5, "D5"), (1, 1.5, 0.5, "C5"), (1, 2, 2, "A4"),
        (2, 0, 1, "Bb4"), (2, 1, 1, "D5"), (2, 2, 1, "F5"), (2, 3, 1, "E5"),
        (3, 0, 3, "D5"),
        (4, 0, 1, "C5"), (4, 1, 0.5, "A4"), (4, 1.5, 0.5, "C5"), (4, 2, 2, "F5"),
        (5, 0, 1, "D5"), (5, 1, 1, "F5"), (5, 2, 2, "A5"),
        (6, 0, 1, "C5"), (6, 1, 1, "E5"), (6, 2, 1, "F#5"), (6, 3, 1, "E5"),
        (7, 0, 2, "D5"), (7, 2, 1, "Bb4"), (7, 3, 1, "G4"),
        (8, 0, 1, "A4"), (8, 1, 1, "C5"), (8, 2, 1, "E5"), (8, 3, 1, "G5"),
        (9, 0, 3, "F5"), (9, 3, 1, "D5"),
        (10, 0, 1, "E5"), (10, 1, 1, "D5"), (10, 2, 1, "Bb4"), (10, 3, 0.5, "G4"), (10, 3.5, 0.5, "E4"),
        (11, 0, 4, "F4")]
    notes = []
    for b, ch in enumerate(chords):
        halves = ch.split("|")
        for h, c in enumerate(halves):
            span = bar / len(halves); t0 = b * bar + h * span
            ps = [m(x) for x in c.split()]
            notes.append((t0, span * 0.9, ps[0], 50))                     # bass on the beat
            for k in range(1, int(span), 2):                              # soft shells on 2 and 4
                for p in ps[1:]:
                    notes.append((t0 + k, 0.55, p, 38))
    for b, beat, du, n in mel:
        st = b * bar + beat
        notes.append((swing(st), du * 0.95, m(n), 62 if beat % 1 == 0 else 52))
    notes.append((11 * bar + 2, 2.0, m("C6"), 34))                       # a little sparkle at the end
    notes.append((11 * bar + 2.5, 1.5, m("F6"), 30))
    return notes, bpm, bar


# ---------------------------------------------------------------- goodnight: "Lamp's Low" (waltz, G major, 3/4)
def goodnight():
    bpm, bar = 76, 3
    chords = ["G2 B3 D4 F#4", "E2 G3 B3 D4", "A2 C4 E4 G4", "D2 C4 F#4", "G2 B3 D4 F#4", "C3 E4 G4 B4", "B1 D4 F#4 A4", "E2 D4 G#4 B4",
              "A2 C4 E4 G4", "D2 C4 F#4 A4", "G2 B3 E4", "G2 B3 D4"]
    mel = [(0, 0, 2, "B4"), (0, 2, 1, "D5"),
           (1, 0, 3, "G5"),
           (2, 0, 1, "E5"), (2, 1, 1, "C5"), (2, 2, 1, "A4"),
           (3, 0, 2, "F#4"), (3, 2, 1, "A4"),
           (4, 0, 2, "B4"), (4, 2, 1, "D5"),
           (5, 0, 2, "E5"), (5, 2, 1, "G5"),
           (6, 0, 3, "F#5"),
           (7, 0, 2, "D5"), (7, 2, 1, "B4"),
           (8, 0, 2, "C5"), (8, 2, 1, "E5"),
           (9, 0, 1, "D5"), (9, 1, 1, "C5"), (9, 2, 1, "A4"),
           (10, 0, 3, "B4"),
           (11, 0, 5, "G4")]
    notes = []
    for b, ch in enumerate(chords):
        ps = [m(x) for x in ch.split()]
        t0 = b * bar
        notes.append((t0, bar * 0.95 + (2 if b == len(chords) - 1 else 0), ps[0], 46))   # bass, held
        for k, p in enumerate(ps[1:]):                                   # a slow rolled arpeggio up through the chord
            notes.append((t0 + 1 + 0.5 * k, bar - 1 - 0.5 * k + (2 if b == len(chords) - 1 else 0), p, 34))
    for b, beat, du, n in mel:
        notes.append((b * bar + beat, du * 0.97, m(n), 56))
    notes.append((11 * bar + 4.0, 3.0, m("G6"), 26))                     # the lamp clicks off: one high, soft note
    return notes, bpm, bar


SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
for name, fn in (("morning", morning), ("goodnight", goodnight)):
    notes, bpm, bar = fn()
    write_midi(name + ".mid", notes, bpm, bar)
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", "48000", "-F", name + "_raw.wav", SF2, name + ".mid"], check=True,
                   capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", name + "_raw.wav", "-af",
                    "silenceremove=stop_periods=-1:stop_duration=1.5:stop_threshold=-60dB,loudnorm=I=-18:TP=-2",
                    "-ar", "48000", "-c:a", "aac", "-b:a", "192k", sys.argv[1] + "/piano_" + name + "_DEMO.m4a"], check=True)
    print(name, "ok")
