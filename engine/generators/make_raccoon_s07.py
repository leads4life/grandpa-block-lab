"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 07
"Calibration Montage" (16:9, ~55 s). Script: scenes/raccoon_lift/scene07_script.md (standing authorization).
Two problems: the box only rises as far as the barrel falls, and raccoons reach a metre. Word Card PULLEY. The build: a
pulley block on the barrel with the rope's end tied to the beam (block and tackle, reversed): the platform now rises twice
as far as the barrel drops (lesson: MECHANICAL ADVANTAGE -- twice the height, twice the water). Montage: TEST 3 (too little:
nothing), TEST 4 (too much: up too fast, gate shut, drained back down), TEST 5 (just right: the barrel drops 0.9 m, the crate
glides 1.8 m to the top). A FILL TO HERE line on the barrel. Hook: coming down drops like a stone -- "we need a brake."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene07"
S6 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene06.json"))
S, A = {}, []

# ---------------------------------------------------------------- the land as Scene 06 left it (Rule 1)
for name, st in S6["structures"].items():
    if name in ("liftbox", "cabbages3", "bucket", "crate_g"):           # gone in Scene 06 (the crate is back on the platform)
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
BX, KX = -4.0, -4.45
PUL_Z, PUL_R = 2.25, 0.08
ZK0 = 1.2
PL_C = (BX + 0.05, 0.7)
S["gate"]["at"] = [S["gate"]["at"][0], 0.0, 0.0]                     # shut
S["scale_crate"]["at"] = [-3.2 - 0.33, -0.15, 0.135]
S["block"] = dict(cells=[[-45, 7, 0]], at=[0.05, 0.0, ZK0 + 0.36], centered=False, material="darkiron", block_shape=[1.4, 0.6, 1.4],
                  expect_blocks=1)                                   # the pulley block on the barrel's lid
S["anchor"] = dict(cells=[[-43, 7, 23]], at=[0.05, 0.0, 0.0], centered=False, material="darkiron", block_shape=[0.6, 0.6, 0.6],
                   expect_blocks=1)                                  # the rope's end, tied to the beam
S["fill_line"] = dict(cells=[[-45, 6, 2]], at=[0.05, 0.0, ZK0 - 0.05], centered=False, material="ceramic", block_shape=[3.05, 1.06, 0.25],
                      expect_blocks=1)                               # FILL TO HERE (painted on the barrel's south face)
BAR = ["barrel", "barrel_bands", "block", "fill_line"]               # everything that rides on the barrel
CAR = ["platform_l", "crate2"]                                       # everything that rides on the platform

# ---------------------------------------------------------------- lines
LINES = [("two", "Two problems. The box only goes up as far as the barrel comes down. And raccoons can reach a metre.", {}),
         ("pulley", "These wheels are pulleys. A wheel with a groove, so a rope can run over it.", {}),
         ("ready", "Now watch. Ready, chat? Blocks up!", {}),
         ("t3", "Test three. Too little water... nothing.", {}),
         ("t4", "Test four. Too much. Easy, easy!", dict(lens=False, why="watching the platform shoot up")),
         ("t5", "Test five...", dict(lens=False, why="whispered, watching it glide up")),
         ("trade", "The barrel drops a little; the box goes up twice as far. That's the trade: twice the height, twice the water.", {}),
         ("tobias", "Mechanical advantage. Tobias knows.", {}),
         ("brake", "Up high. Out of reach. But going DOWN... it drops like a stone. We need a brake.", {})]
GUESS = dict(two=7.0, pulley=5.0, ready=2.6, t3=3.4, t4=3.0, t5=1.4, trade=7.4, tobias=2.6, brake=6.0)
dur_file = os.path.join(HERE, "raccoon_s07_durations.json")
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
def lift(t0, t1, up):                                               # the platform rises `up`; the barrel drops up / 2 (2:1)
    for n in CAR:
        act(type="slide", target=n, by=[0.0, 0.0, up], when=round(t0, 3), until=round(t1, 3))
    for n in BAR:
        act(type="slide", target=n, by=[0.0, 0.0, -up / 2], when=round(t0, 3), until=round(t1, 3))
    for p in ("pulley_box", "pulley_bkt"):
        act(type="spin", target=p, axis="y", degrees=round(math.degrees(up / PUL_R), 2), pivot=S[p]["cells"][0], when=round(t0, 3), until=round(t1, 3))
def gate(t, dz):
    act(type="slide", target="gate", by=[0.0, 0.0, dz], when=round(t, 3), until=round(t + 0.15, 3))

POSES = {
    "two_fingers": dict(hand_R={"char": [-0.15, -0.3, 1.05]}),
    "point_up": dict(lean=-0.1, hand_R={"char": [-0.2, -0.25, 1.35]}),
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "pull_cord": dict(lean=0.1, hand_R={"world": [-4.7, 0.6, 0.95]}),
    "shrug": dict(shrug=0.8, elbows=0.3),
    "wince": dict(lean=-0.12, shrug=0.4, elbows=0.5),
    "paint": dict(lean=0.3, hand_R={"world": [KX + 0.02, 0.53, ZK0 - 0.9 + 0.2]}),   # where the line goes after TEST 5
}
G0 = (-3.6, 0.3)
G_CORD = (-4.62, 0.28)
G_PAINT = (KX + 0.02, 0.22)
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. two problems; PULLEY
s, e = say("two", 0.0, at=0.6)
to_lens(-1.0, e + 0.2)
pose("two_fingers", s, s + 1.6, ease=0.2)
face("raised", s, e + 0.3, set=dict(brow=0.7))
s, e = say("pulley", 0.5)
WORD0 = s
pose("point_up", s, s + 2.0, ease=0.25)
look(s - 0.2, s + 2.0, pos=(-4.2, 0.7, 2.25), body=False, rate=0.3)
to_lens(s + 2.0, e + 0.2)
s, e = say("ready", 0.4)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", e - 0.9, e + 0.3, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.3
for name, d in (("block", 0.4), ("anchor", 0.3)):
    act(type="build", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0], order="z")
    B0 += d + 0.1
ROPES_ON = B0 - 0.6
look(LE["ready"] + 0.2, B0 + 0.2, pos=(KX, 0.7, 1.8), body=True, rate=0.3)

# 2. the montage: TEST 3, TEST 4, TEST 5
walk(B0 + 0.1, B0 + 1.2, G_CORD)
T3 = B0 + 1.4
pose("pull_cord", T3 - 0.1, T3 + 0.3, ease=0.12)
gate(T3, 0.02); gate(T3 + 1.2, -0.02)                               # a dribble...
s, e = say("t3", 0.0, at=T3 + 0.4)
to_lens(s - 0.2, e + 0.2)
pose("shrug", e - 1.0, e + 0.2, ease=0.15)
T4 = e + 0.8
pose("pull_cord", T4 - 0.1, T4 + 0.3, ease=0.12)
gate(T4, 0.14)                                                      # ...a flood
UP4 = 1.0
lift(T4 + 0.4, T4 + 1.3, UP4)
sfx("gush", T4 + 0.05, 0.8); sfx("creak", T4 + 0.5, 0.5)
gate(T4 + 1.25, -0.14)
s, e = say("t4", 0.0, at=T4 + 0.5)
pose("wince", s, e + 0.2, ease=0.15)
face("worried", s, e + 0.4)
look(T4 + 0.3, e + 0.4, pos=(PL_C[0], PL_C[1], 1.2), body=True, rate=0.3)
PLUG4 = e + 0.4                                                     # plug out: drained, the platform back down
lift(PLUG4 + 0.6, PLUG4 + 2.6, -UP4)
sfx("creak", PLUG4 + 0.7, 0.35)
T5 = PLUG4 + 3.0
pose("pull_cord", T5 - 0.1, T5 + 0.3, ease=0.12)
gate(T5, 0.04)
UP5 = 1.8                                                           # the barrel drops 0.9, the crate rises 1.8 (2:1)
R50, R51 = T5 + 0.8, T5 + 5.0
lift(R50, R51, UP5)
gate(R51 - 0.3, -0.04)
sfx("creak", R50 + 0.2, 0.4)
s, e = say("t5", 0.0, at=R50 + 0.6)
look(R50, R51 + 0.4, pos=(PL_C[0], PL_C[1], 1.6), body=True, rate=0.2)
face("alert", R50, R51, set=dict(brow=0.6))
face("smile", R51, R51 + 1.4, set=dict(smile=0.9))

# 3. the trade; the fill line; the hook
s, e = say("trade", 0.6, at=R51 + 0.6)
LESSON0, LESSON1 = s, e
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
PAINT = e + 0.4
walk(PAINT, PAINT + 0.8, G_PAINT)
pose("paint", PAINT + 0.9, PAINT + 1.9, ease=0.2)
look(PAINT + 0.7, PAINT + 2.0, pos=(KX, 0.55, ZK0 - UP5 / 2 + 0.3), body=True, rate=0.3)
act(type="build", target="fill_line", when=round(PAINT + 1.0, 3), until=round(PAINT + 1.6, 3), stand_at=[G_PAINT[0], G_PAINT[1], 0.0], order="x")
CHAT = [(PAINT + 2.0, "TobiasBuilds", "mechanical advantage!!")]
s, e = say("tobias", 0.4, at=PAINT + 2.6)
to_lens(s - 0.3, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
s, e = say("brake", 0.6)
look(s - 0.2, s + 1.6, pos=(PL_C[0], PL_C[1], 2.0), body=True, rate=0.25)
to_lens(s + 1.6, 99.0)
face("worried", s + 1.6, e - 1.0)
face("raised", e - 1.0, 99.0, set=dict(brow=0.8))
END = e + 1.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# ropes and water
CORNERS = [(PL_C[0] + dx, PL_C[1] + dy) for dx in (-0.17, 0.17) for dy in (-0.17, 0.17)]
BLK = [KX, 0.7, ZK0 + 0.43]
rig = dict(ropes=[dict(top=[KX - 0.05, 0.7, PUL_Z], follow="block", at=[BLK[0] - 0.05, 0.7, BLK[2]]),         # down from the beam pulley...
                  dict(top=[-4.25, 0.7, 2.31], follow="block", at=[BLK[0] + 0.05, 0.7, BLK[2]], visible=[ROPES_ON, FILM + 1]),   # ...up to the tie
                  dict(top=[KX, 0.7, PUL_Z + PUL_R], follow="beam", at=[BX, 0.7, PUL_Z + PUL_R]),
                  dict(top=[-4.4, 0.95, 1.86], follow="frame_posts", at=[-4.7, 0.6, 0.95], width=0.008)]
                 + [dict(top=[BX, 0.7, PUL_Z - 0.05], follow="platform_l", at=[cx, cy, 0.05], width=0.01) for cx, cy in CORNERS],
           fills=[dict(follow="barrel", at=[KX + 0.05, 0.7, ZK0], size=[0.27, 0.27, 0.36],
                       level=[[T3, 0.0], [T3 + 1.2, 0.12], [T4, 0.12], [T4 + 1.2, 1.0], [PLUG4, 1.0], [PLUG4 + 2.4, 0.0], [T5, 0.0], [R51, 0.62], [FILM + 1, 0.62]])],
           pours=[dict(**{"from": [-4.42, 0.9, 1.72]}, follow="barrel", at=[KX + 0.05, 0.75, ZK0 + 0.36], on=[[T3 + 0.05, T3 + 1.2]], width=0.008),
                  dict(**{"from": [-4.42, 0.9, 1.72]}, follow="barrel", at=[KX + 0.05, 0.75, ZK0 + 0.36], on=[[T4 + 0.05, T4 + 1.3]], width=0.045),
                  dict(**{"from": [KX + 0.12, 0.6, ZK0 - 0.06]}, from_follow="barrel", follow="frame_posts", at=[KX + 0.12, 0.6, -0.02],
                       on=[[PLUG4, PLUG4 + 2.5]], width=0.025),
                  dict(**{"from": [-4.42, 0.9, 1.72]}, follow="barrel", at=[KX + 0.05, 0.75, ZK0 + 0.36], on=[[T5 + 0.05, R51 - 0.2]], width=0.02)])

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
tail = FILM - LE["brake"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)); out.append([tt, p[0], p[1]])
    return out
STOPS = [(0.0, G0)]
pos_now = G0
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
    return list(STOPS[-1][1]) if t > STOPS[-1][0] else list(G0)
who_at = lambda t: gp(*g_at(t))
WALL_FREE = lambda eye: eye[0] < -1.95
FRAME_BOX = ((-4.8, 0.6, 0.0), (-3.6, 0.8, 2.6))
FLUME_BOX = ((-4.9, 0.8, 0.0), (-4.3, 2.7, 2.0))
free = lambda B: (lambda eye: not all(B[0][i] - 0.2 <= eye[i] <= B[1][i] + 0.2 for i in range(3)))
AIR = both(clear_air, WALL_FREE, free(FRAME_BOX), free(FLUME_BOX))
PATH = both(solid_free, WALL_FREE, free(FRAME_BOX), free(FLUME_BOX))
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
LIFT = [(PL_C[0], PL_C[1], 0.02), (PL_C[0], PL_C[1], 2.1), (KX, 0.7, 1.6), (KX, 0.7, 0.3)]
SHOTS = [
    (0.0, (gp(*G0)[1:], (G0[0], G0[1], 0.85), -20, 8, 1.6)),
    (LS["ready"] + 0.8, (gp(*G0)[1:] + [(-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5), (PL_C[0], PL_C[1], 0.0), (KX, 0.7, ZK0)], (-4.1, 0.6, 1.3), 80, 17, 4.6)),
    (T3 - 0.4, (gp(*G_CORD)[1:] + LIFT[:2], (-4.25, 0.55, 1.1), 63, 20, 4.4)),
    (LS["trade"] - 0.3, (gp(*G_CORD)[1:], (G_CORD[0], G_CORD[1], 0.85), -40, 8, 1.6)),
    (PAINT + 0.3, (gp(*G_PAINT)[1:] + [(KX, 0.55, 0.9)], (KX, 0.4, 0.8), -30, 10, 1.8)),
    (LS["brake"] - 0.3, (gp(*G_PAINT)[1:] + [(PL_C[0], PL_C[1], 2.05)], (-4.15, 0.45, 1.2), -25, 10, 2.6)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["brake"] - 1.5, "GardenGranny", "a brake made of what dear")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0}),
                                                               dict(icon="map", name="Blueprint", **{"in": -1.0})]),
         dict(style="word", word="pulley", say="pull-ee", meaning="a wheel with a groove for a rope", when=round(WORD0, 3), until=round(WORD0 + 3.8, 3)),
         dict(style="title", text="TEST 3", color="amber", y=185, size=72, when=round(T3 - 0.3, 3), until=round(T3 + 1.6, 3)),
         dict(style="title", text="TEST 4", color="amber", y=185, size=72, when=round(T4 - 0.3, 3), until=round(T4 + 1.6, 3)),
         dict(style="title", text="TEST 5", color="amber", y=185, size=72, when=round(T5 - 0.3, 3), until=round(T5 + 1.6, 3)),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="MECHANICAL ADVANTAGE", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="twice the height = twice the water", color="cyan", at=round(LESSON0 + 2.0, 3), size=30)])]
W = {k: v for k, v in S6["world"].items() if k not in ("clouds_pass", "critters", "rigging")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[], rigging=rig)
story = dict(title="Calibration Montage", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["two"], tail=round(tail, 4), seed=107, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=7, name="Calibration Montage", previous="raccoon_lift_scene06",
                                      next="raccoon_lift_scene08"),
             world=W, lines=lines, grandpa=dict(start=list(G0), outfit=S6["grandpa"]["outfit"]),
             poses=dict(S6["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"],
                     solid=["frame_posts", "beam", "barrel", "flume", "trestles", "crate", "stump", "scale_base", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("t3 %.2f t4 %.2f t5 %.2f rise %.2f-%.2f paint %.2f" % (T3, T4, T5, R50, R51, PAINT))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
