"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 02
"Locks Don't Work" (16:9, ~65 s). Script: scenes/raccoon_lift/scene02_script.md (standing authorization, 2026-10-25).
Next morning: the stone lid shoved off, the crate raided again. The build: a plank lid on a hinge with an iron hook latch.
That evening (golden light) he watches from far back: a raccoon opens the hook in three seconds (Word Card DEXTEROUS).
A clap from far away sends her off -- to the cabin corner, where two kits peek out of the vent: a mama feeding her family.
Kid safety: give it space, a little noise, never feed. Hook: "maybe the answer is UP."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene02"
S1 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene01.json"))
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the land as Scene 01 left it (Rule 1)
DROP = {"wreck", "cabbages_out", "cabbage_roll", "eyes", "mug"}
for name, st in S1["structures"].items():
    if name in DROP:
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
CX, CY = range(-25, -21), range(-1, 2)                              # the crate (Scene 01): x -2.55..-2.15, y -0.15..0.15
CRATE_C = (-2.35, 0.0)
CRATE_W = -2.55                                                     # its west face (the latch side, toward the camera)
S["lid"]["at"] = [-0.5, 0.0, -0.325]                                # the stone lid, shoved off into the grass (west)
S["lid"]["prebuilt"] = True
S["cabbages_in"]["cells"] = [[-24, 0, 1]]                           # one cabbage left
S["cabbages_in"]["expect_blocks"] = 1
LEAVES = [(-26, 2), (-28, -1), (-21, 3), (-27, 3), (-20, -2), (-24, 4)]   # chewed leaves in the grass
S["leaves"] = dict(cells=[[x, y, 0] for x, y in LEAVES], at=[0.0, 0.0, -0.04], centered=False, material="cabbage",
                   block_shape=[0.9, 0.7, 0.2], expect_blocks=len(LEAVES), prebuilt=True)
S["lid2"] = dict(cells=[[x, y, 3] for x in CX for y in CY], at=[0.0, 0.0, -0.03], centered=False, material="planks",
                 block_shape=[1, 1, 0.4], expect_blocks=12)          # the new plank lid (hinged on its east edge)
S["hook"] = dict(cells=[[-26, 0, 2]], at=[0.045, 0.0, 0.0], centered=False, material="darkiron",
                 block_shape=[0.25, 0.35, 1.3], expect_blocks=1)     # the iron hook over the lid's west edge
HINGE = [-22, 0, 3]                                                 # lid pivot (east column): the west edge lifts
STUMP = (-2.8, 0.95)
STUMP_TOP = 0.5
VENT = (-1.728, -0.3)

# ---------------------------------------------------------------- the raccoons: a mama and two kits
G_FAR = (-3.3, 0.72)                                                # where he watches from that evening (well back)

# ---------------------------------------------------------------- lines
LINES = [("moved", "They moved the STONE?!", dict(lens=False, why="shouted at the mess, like Scene 01's cold open")),
         ("okay", "Okay. Stone didn't work. We need a real lock.", {}),
         ("ready", "Ready, chat? Blocks up!", {}),
         ("hook", "Hook latch. Let's see a bandit do THAT.", {}),
         ("here", "Here she comes...", dict(lens=False, why="whispered, eyes on the raccoon (we see her over his shoulder)")),
         ("three", "...Three seconds. THREE.", {}),
         ("dext", "That's a word for good with your hands. Five fingers... and they feel everything.", {}),
         ("hey", "Hey! Not tonight!", dict(lens=False, why="called out to the raccoon, from far away")),
         ("mama", "Oh. A mama. With babies.", dict(lens=False, why="said as the kits peek out: the wide shot keeps them in view")),
         ("bandit", "She's not a bandit, chat. She's feeding her family.", {}),
         ("safety", "If you see one: give it space, make a little noise, and never feed it.", {}),
         ("up", "If they can open anything... maybe the answer is UP.", {})]
GUESS = dict(moved=1.6, okay=3.4, ready=2.1, hook=2.6, here=1.4, three=2.0, dext=4.6, hey=1.4, mama=2.0, bandit=3.0, safety=4.2, up=3.4)
dur_file = os.path.join(HERE, "raccoon_s02_durations.json")
D = dict(GUESS, **(json.load(open(dur_file)) if "--fit" in sys.argv and os.path.exists(dur_file) else {}))
LS, LE, cursor = {}, {}, [0.0]
def say(lid, gap, at=None):
    LS[lid] = round(max(cursor[0], (LE[list(LE)[-1]] if LE else 0.0) + gap, at or 0.0), 3)
    LE[lid] = round(LS[lid] + D[lid], 3)
    cursor[0] = LE[lid]
    return LS[lid], LE[lid]
def act(**a):
    A.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in a.items()})
def pose(n, t0, t1, **kw): act(type="pose", pose=n, when=t0, until=t1, **kw)
def face(e, t0, t1, **kw): act(type="face", expr=e, when=t0, until=t1, **kw)
def look(t0, t1, pos=None, body=False, **kw):
    a = dict(type="look", when=t0, until=t1, body=body, **kw)
    if pos is not None: a["pos"] = [round(v, 3) for v in pos]
    act(**a)
def to_lens(t0, t1): act(type="face_camera", when=t0, until=t1)
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)
def walk(t0, t1, to, via=()):
    act(type="move", to=[to[0], to[1], 0.0], via=[[v[0], v[1], 0.0] for v in via], when=t0, until=t1, face="path")

POSES = {
    "aghast": dict(lean=-0.08, shrug=0.5, elbows=0.5),
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "tug": dict(lean=0.2, hand_R={"world": [CRATE_W - 0.03, 0.0, 0.3]}),
    "crouch_watch": dict(lean=0.22, hips=[0.0, 0.0, -0.12]),
    "clap": dict(hand_R={"char": [-0.03, -0.32, 0.92]}, hand_L={"char": [0.03, -0.32, 0.92]}),
    "clap_open": dict(hand_R={"char": [-0.2, -0.3, 0.95]}, hand_L={"char": [0.2, -0.3, 0.95]}),
    "look_up": dict(lean=-0.12, head=[0.0, 0.35, 0.0]),
}
G_IN = (-1.45, 0.66)
G1 = (-2.35, 0.52)                                                  # north of the crate (its build spot, Scene 01)
G_LID = (-2.85, 0.42)                                               # beside the shoved-off stone lid
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. morning: the stone lid shoved off, the crate raided again
walk(0.3, 1.5, G1, via=[(-1.9, 0.58), (-2.15, 0.55)])
face("worried", -1.0, 1.6)
s, e = say("moved", 0.0, at=1.6)
look(1.4, e + 0.6, pos=(-2.85, 0.0, 0.0), body=True, rate=0.3)
pose("aghast", s - 0.1, e + 0.3, ease=0.15)
face("surprised", s, e + 0.4, set=dict(brow=1.2))
CHAT = [(e + 0.4, "TobiasBuilds", "raccoons are strong for their size"), (e + 1.3, "BoarFan2009", "respect tbh")]
s, e = say("okay", 2.0)
to_lens(s - 0.3, e + 0.2)
face("raised", s, s + 1.4, set=dict(brow=0.8))
face("content", s + 1.4, e + 0.3)

# 2. the build: the stone goes, a plank lid on a hinge, an iron hook latch
s, e = say("ready", 0.5)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", s + 0.6, e + 0.4, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.4
act(type="remove", target="lid", when=round(B0 + 0.7, 3), until=round(B0 + 1.5, 3), stand_at=[G_LID[0], G_LID[1], 0.0])
act(type="remove", target="leaves", when=round(B0 + 1.9, 3), until=round(B0 + 2.4, 3), stand_at=[G1[0], G1[1], 0.0])
act(type="build", target="lid2", when=round(B0 + 2.5, 3), until=round(B0 + 4.3, 3), stand_at=[G1[0], G1[1] + 0.07, 0.0], order="x")
act(type="build", target="hook", when=round(B0 + 4.4, 3), until=round(B0 + 4.7, 3), stand_at=[G1[0], G1[1], 0.0], order="z")
sfx("clink", B0 + 4.65, 0.7)
look(B0 + 0.4, B0 + 4.9, pos=(CRATE_C[0], CRATE_C[1], 0.3), body=True, rate=0.3)
TUG = B0 + 5.1
walk(TUG - 0.6, TUG - 0.1, (CRATE_W - 0.38, 0.22))                  # round to the latch side
pose("tug", TUG, TUG + 0.7, ease=0.2)
look(TUG - 0.3, TUG + 0.8, pos=(CRATE_W, 0.0, 0.3), body=True, rate=0.3)
sfx("tap", TUG + 0.25, 0.6); sfx("tap", TUG + 0.5, 0.5)
s, e = say("hook", 0.0, at=TUG + 0.9)
to_lens(s - 0.2, e + 0.2)
face("smirk", s, e + 0.4)

# 3. that evening: the light goes golden; he watches from far back
TC = e + 1.0                                                        # "THAT EVENING..." card (the cut lands here)
walk(TC - 0.2, TC + 1.4, G_FAR, via=[(-3.0, 0.45)])
pose("crouch_watch", TC + 1.5, 99.0, ease=0.4)
MAMA_IN = TC + 1.9
ARRIVE = MAMA_IN + 2.0
M_AT = (-2.62, 0.0)                                                 # her feet: the little hands reach the hook
look(TC + 1.4, 99.0, pos=(CRATE_W, 0.0, 0.25), body=True, rate=0.12)
s, e = say("here", 0.0, at=MAMA_IN + 0.6)
face("alert", s - 0.3, e + 0.3, set=dict(brow=0.9))
FID0, FID1 = ARRIVE + 0.3, ARRIVE + 3.3                             # three seconds
OPEN = FID1 - 0.2
act(type="spin", target="hook", axis="x", degrees=-90.0, pivot=[-26, 0, 2], when=round(OPEN - 0.25, 3), until=round(OPEN, 3))
sfx("clink", OPEN, 0.8)
act(type="spin", target="lid2", axis="y", degrees=100.0, pivot=HINGE, when=round(OPEN + 0.2, 3), until=round(OPEN + 0.9, 3))
sfx("door_creak", OPEN + 0.2, 0.25)
face("surprised", OPEN, OPEN + 0.9, set=dict(brow=1.3))
s, e = say("three", 0.4, at=OPEN + 1.0)
to_lens(s - 0.3, e + 0.2)
face("worried", s, e + 0.3)
WORD0 = None
s, e = say("dext", 0.4)
WORD0 = s
to_lens(s - 0.2, e + 0.2)
face("raised", s, e + 0.2, set=dict(brow=0.7, smile=0.3))
CLAP = e + 0.5
pose("clap_open", CLAP - 0.35, CLAP - 0.05, ease=0.1)
for k in range(2):
    pose("clap", CLAP + 0.3 * k - 0.08, CLAP + 0.3 * k + 0.08, ease=0.05)
    sfx("clap", CLAP + 0.3 * k, 1.0)
look(CLAP - 0.4, LE["dext"] + 4.0, pos=(-2.62, 0.0, 0.2), body=False, rate=0.4)
s, e = say("hey", 0.0, at=CLAP + 0.7)
face("alert", CLAP - 0.2, e + 0.3, set=dict(brow=1.0))
RUN0 = CLAP + 0.15                                                  # she bolts at the first clap...
M_CORNER = (-1.9, -0.55)                                            # ...to the cabin corner, by the vent
RUN1 = RUN0 + 1.1
KITS = RUN1 + 0.6
look(RUN0, KITS + 2.0, pos=(VENT[0], VENT[1], 0.1), body=True, rate=0.15)
s, e = say("mama", 0.6, at=KITS + 0.8)
face("surprised", s - 0.4, s + 0.6, set=dict(brow=1.0))
face("warm", s + 0.6, e + 0.4)
s, e = say("bandit", 0.6)
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)                                         # sincere: calm, no slang
s, e = say("safety", 0.5)
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
s, e = say("up", 0.6)
PINE = (-2.89, -1.18, 1.8)                                          # the tall pine south of the crate
look(s - 0.4, s + 1.6, pos=PINE, body=True, rate=0.2)
pose("look_up", s - 0.3, s + 1.6, ease=0.3)
to_lens(s + 1.6, 99.0)
face("raised", s, s + 1.6, set=dict(brow=1.0))
face("smirk", s + 1.6, 99.0)
END = e + 1.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# the raccoons (absolute times)
mama = dict(kind="raccoon", name="Mama", visible=[MAMA_IN, FILM + 1.0], heading=1.2,
            path=[[MAMA_IN, -3.0, -1.25], [MAMA_IN + 1.0, -2.95, -0.55], [ARRIVE, M_AT[0], M_AT[1]],
                  [RUN0, M_AT[0], M_AT[1]], [RUN0 + 0.5, -2.3, -0.4], [RUN1, M_CORNER[0], M_CORNER[1]], [FILM + 1.0, M_CORNER[0], M_CORNER[1]]],
            yaw=[[ARRIVE, 0.0], [RUN1 + 0.2, 180.0]], poses=[[FID0 - 0.25, FID1, "fiddle"], [RUN1 + 0.4, FILM + 1.0, "sit"]],
            look=[[RUN1 + 0.4, FILM + 1.0, [G_FAR[0], G_FAR[1], 0.8]]], chitters=[ARRIVE + 0.1, RUN1 + 0.3], stride=0.09)
kits = [dict(kind="raccoon", name="Kit%d" % i, k=0.6, visible=[KITS, FILM + 1.0], heading=math.pi, yaw=[[KITS, 180.0 + dy * 60]],
             path=[[KITS, -1.70, VENT[1] + dy], [KITS + 0.5, -1.74, VENT[1] + dy], [FILM + 1.0, -1.74, VENT[1] + dy]],
             z=[[0.0, -0.035]], look=[[KITS + 0.6, FILM + 1.0, [G_FAR[0], G_FAR[1], 0.8]]], chitters=[KITS + 0.3 + 0.4 * i])
        for i, dy in enumerate((0.06, -0.06))]

# the trip hammer keeps its clock by the stream (Rule 1)
PERIOD, CAM_GAP = 3.3, 0.55
FIRST = 0.9
T0_ = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": [-4.4, 1.95, 0.6]} if name == "head" else {}))
for a in A:                                                         # every hold ends on a key at its end
    if a["type"] == "hold" and a["keys"][-1]["t"] < a["until"]:
        a["keys"].append(dict(a["keys"][-1], t=a["until"]))

lines = []
for i, (lid, text, extra) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0, **extra))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["up"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (west of the cabin)
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)); out.append([tt, p[0], p[1]])
    return out
STOPS = [(0.0, G_IN)]
pos_now = G_IN
for a in sorted([a for a in A if a["type"] in ("move", "build", "remove") and not a.get("quiet")], key=lambda a: a["when"]):
    if a["type"] == "move":
        pts = [pos_now] + [tuple(v[:2]) for v in a["via"]] + [tuple(a["to"][:2])]
        STOPS.append((a["when"], pos_now))
        STOPS += [(p[0], (p[1], p[2])) for p in keyed(a["when"], a["until"], pts)[1:]]
        pos_now = tuple(a["to"][:2])
    else:
        p = tuple(a["stand_at"][:2])
        if p != pos_now:
            STOPS += [(a["when"] - 0.05, pos_now), (a["when"], p)]
            pos_now = p
STOPS.sort(key=lambda s: s[0])
def g_at(t):
    for (t0, a), (t1, b) in zip(STOPS, STOPS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); return [a[i] + (b[i] - a[i]) * u for i in range(2)]
    return list(STOPS[-1][1]) if t > STOPS[-1][0] else list(G_IN)
who_at = lambda t: gp(*g_at(t))
WALL_FREE = lambda eye: eye[0] < -1.95
AIR = both(clear_air, WALL_FREE)
PATH = both(solid_free, WALL_FREE)
WHEEL_BOX = ((-5.12, 0.38, -0.05), (-4.88, 1.62, 1.18))                # the waterwheel: its spokes must not cross the view
LOS = make_los(SIGHT_BLOCKERS)
cam = []
def framed(t, must, tgt, az, el, d, *a, **kw):
    for dk, dz in ((1.0, 0), (1.0, 35), (1.0, -35), (1.3, 0), (1.3, 35), (1.3, -35), (1.3, 70), (1.3, -70)):
        try:
            return auto_frame(t, must, tgt, az + dz, el, d * dk, *a, **kw)
        except SystemExit:
            continue
    raise SystemExit("no clear camera at %.2f s (wanted az %s)" % (t, az))
def cut(t, *a, **kw):
    tc = math.ceil(t * FPS - 1e-6) / FPS
    if not cam:
        return [framed(0.0, *a, **kw)]
    return [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), framed(tc, *a, **kw)]
DOOR = (-1.9, 0.6, 1.0)
CRATE_PTS = [(CRATE_C[0], CRATE_C[1], 0.03), (-2.55, -0.15, 0.03), (-2.15, 0.15, 0.03), (CRATE_C[0], CRATE_C[1], 0.36)]
LATCH = (CRATE_W - 0.01, 0.0, 0.28)
SHOTS = [
    (0.0, (CRATE_PTS + [(-2.85, 0.0, 0.03), (DOOR[0], DOOR[1], 0.05), (DOOR[0], DOOR[1], 1.25)], (-2.3, 0.25, 0.55), 172, 10, 2.2)),
    (LS["okay"] - 0.3, (gp(*G1)[1:], (G1[0], G1[1], 0.85), 180, 8, 1.5)),
    (LS["ready"] + 1.0, (gp(*G1) + gp(*G_LID) + CRATE_PTS, (-2.55, 0.3, 0.55), 185, 16, 2.6)),
    (TUG - 0.7, (gp(CRATE_W - 0.38, 0.22)[1:] + [LATCH], (-2.75, 0.15, 0.6), 175, 12, 1.7)),
    # that evening: wide -- him far back on the path, the crate, the woods she comes out of
    (TC, (gp(*G_FAR)[1:] + CRATE_PTS + [(-2.95, -0.55, 0.05)], (-2.75, 0.2, 0.45), 195, 14, 2.6)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
INS = (FID0 - 0.2, OPEN + 1.0)                                      # insert: the little hands at the hook (a cutaway)
tc = math.ceil(INS[0] * FPS - 1e-6) / FPS
tc1 = math.ceil(INS[1] * FPS - 1e-6) / FPS
cam += [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), orbit(tc, (CRATE_W - 0.04, 0.0, 0.27), 115, 20, 0.7),   # her hands on the hook, from the side
        orbit(tc1 - 1.0 / FPS, (CRATE_W - 0.04, 0.0, 0.27), 115, 20, 0.7)]
SHOTS2 = [
    (INS[1], (gp(*G_FAR)[1:], (G_FAR[0], G_FAR[1], 0.75), 200, 8, 1.6)),
    (LS["bandit"] - 0.3, (gp(*G_FAR)[1:], (G_FAR[0], G_FAR[1], 0.75), 200, 8, 1.6)),
    (LS["up"] - 0.3, (gp(*G_FAR) + [(G_FAR[0], G_FAR[1], 1.3)], (G_FAR[0], G_FAR[1], 0.8), 205, 6, 1.9)),
]
for t, (must, tgt, az, el, d) in SHOTS2:
    if t > RUN0:
        break
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
RUNSHOT = (RUN0 + 0.35, LS["bandit"] - 0.3)                         # cutaway: she runs to the corner, the kits peek out
cam += cut(RUNSHOT[0], [(M_CORNER[0], M_CORNER[1], 0.05), (M_CORNER[0], M_CORNER[1], 0.25), (-1.80, VENT[1], 0.08), (-1.80, VENT[1], 0.16)],
           (-1.95, -0.42, 0.15), 260, 11, 1.6, AIR, los=LOS)                # from the south, along the wall: the corner and the vent
for t, (must, tgt, az, el, d) in SHOTS2:
    if t > RUN0:
        cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["three"] + 0.3, "GardenGranny", "clever girl"), (LE["mama"] + 0.4, "TobiasBuilds", "raccoon moms raise kits alone. thats a lot of mouths"),
         (LE["safety"] + 0.5, "lurker_77", "*still lurking*")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0})]),
         dict(style="title", text="THAT EVENING...", color="amber", y=185, size=80, when=round(TC, 3), until=round(TC + 2.4, 3)),
         dict(style="word", word="dexterous", say="dex-ter-us", meaning="good with your hands",
              when=round(WORD0, 3), until=round(WORD0 + 3.8, 3))]
W = {k: v for k, v in S1["world"].items() if k not in ("clouds_pass", "critters")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[mama] + kits,
         clouds_pass=[[round(TC + 1.6, 3), 2.0, 0.55, [1.0, 0.62, 0.32], True]])   # evening falls during the card, and stays
story = dict(title="Locks Don't Work", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["moved"], tail=round(tail, 4), seed=102, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=2, name="Locks Don't Work", previous="raccoon_lift_scene01",
                                      next="raccoon_lift_scene03"),
             world=W, lines=lines, grandpa=dict(start=list(G_IN), outfit=S1["grandpa"]["outfit"]),
             poses=dict(S1["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"], cutaways=[[math.floor(tc * 1000) / 1000 - 0.001, math.ceil(tc1 * 1000) / 1000 + 0.001],
                                                                 [math.floor(RUNSHOT[0] * FPS) / FPS - 0.001, math.ceil(RUNSHOT[1] * FPS) / FPS + 0.001]],
                     solid=["crate", "lid2", "stump", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("build %.2f tug %.2f card %.2f mama %.2f-%.2f open %.2f clap %.2f kits %.2f" % (B0, TUG, TC, MAMA_IN, ARRIVE, OPEN, CLAP, KITS))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
