"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 08
"The Brake" (16:9, ~60 s). Script: scenes/raccoon_lift/scene08_script.md (standing authorization).
Afternoon, the crate at the top (Scene 07). Coming down is the hard part: a valve on the barrel (a brake made of water) --
a quarter turn and the crate sinks gently (lesson: CONTROL THE DRAIN). The EGG TEST: an egg rides up and down on the crate
and doesn't crack. Then smooth metal collars round both posts (lesson: SMOOTH METAL -- claws can't grip it). The light
goes golden: "Tonight's the night." A chitter far off in the woods: "...Game on."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene08"
S7 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene07.json"))
S, A = {}, []

# ---------------------------------------------------------------- the land as Scene 07 left it (Rule 1)
for name, st in S7["structures"].items():
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
BX, KX = -4.0, -4.45
PUL_Z, PUL_R = 2.25, 0.08
ZK0 = 1.2
UP = 1.8                                                            # the crate is at the top: up 1.8, the barrel down 0.9
PL_C = (BX + 0.05, 0.7)
CAR = ["platform_l", "crate2"]                                       # (the egg follows the crate by its own keys)
BAR = ["barrel", "barrel_bands", "block", "fill_line", "valve"]
for n in ("platform_l", "crate2"):
    S[n]["at"] = [S[n]["at"][0], S[n]["at"][1], S[n]["at"][2] + UP]
for n in ("barrel", "barrel_bands", "block", "fill_line"):
    S[n]["at"] = [S[n]["at"][0], S[n]["at"][1], S[n]["at"][2] - UP / 2]
ZK = ZK0 - UP / 2                                                   # where the barrel hangs now (bottom at 0.3)
S["valve"] = dict(cells=[[-45, 5, 0]], at=[0.05, 0.03, ZK - 0.05], centered=False, material="darkiron", block_shape=[0.6, 0.6, 0.6],
                  expect_blocks=1, extras=[dict(c=[-4.5, 0.465, 0.05], s=[0.07, 0.008, 0.07], m="red")])   # on the barrel's south face; a red wheel
S["egg"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="ceramic", block_shape=[0.4, 0.4, 0.55], expect_blocks=1)
COL_W = [(-48, 6), (-48, 7), (-48, 8), (-47, 6), (-47, 8)]          # outer faces only: the barrel and the platform pass inside
COL_E = [(-36, 6), (-36, 7), (-36, 8), (-37, 6), (-37, 8)]
S["baffles"] = dict(cells=[[x, y, z] for x, y in COL_W + COL_E for z in (6,)], at=[0.0, 0.0, 0.0], centered=False, material="steel",
                    block_shape=[1, 1, 0.3], expect_blocks=10)

# ---------------------------------------------------------------- lines
LINES = [("hard", "Coming down is the hard part. Pull the plug and -- whump.", {}),
         ("valve", "So: a valve. Open it a little, water trickles out, the barrel gets lighter... slowly.", {}),
         ("brake", "A brake made of water.", {}),
         ("egg", "The egg test. If it breaks, it's not a brake.", {}),
         ("crack", "Up... and down. Not a crack!", {}),
         ("last", "Last thing. They climbed my tower like a tree.", {}),
         ("smooth", "Smooth metal. Claws can't grip it. No grip... no climb.", {}),
         ("tonight", "Tonight's the night. Chat, bring snacks. For YOU, not for them.", {}),
         ("game", "...Game on.", {})]
GUESS = dict(hard=4.2, valve=6.4, brake=2.0, egg=3.6, crack=3.0, last=3.4, smooth=4.6, tonight=4.6, game=1.4)
dur_file = os.path.join(HERE, "raccoon_s08_durations.json")
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
def lift(t0, t1, up):                                               # the platform moves `up`; the barrel -up / 2 (2:1)
    for n in CAR:
        act(type="slide", target=n, by=[0.0, 0.0, up], when=round(t0, 3), until=round(t1, 3))
    for n in BAR:
        act(type="slide", target=n, by=[0.0, 0.0, -up / 2], when=round(t0, 3), until=round(t1, 3))
    for p in ("pulley_box", "pulley_bkt"):
        act(type="spin", target=p, axis="y", degrees=round(math.degrees(up / PUL_R), 2), pivot=S[p]["cells"][0], when=round(t0, 3), until=round(t1, 3))
def gate(t, dz):
    act(type="slide", target="gate", by=[0.0, 0.0, dz], when=round(t, 3), until=round(t + 0.15, 3))

POSES = {
    "turn_valve": dict(lean=0.45, hips=[0.0, 0.0, -0.14], hand_R={"world": [KX, 0.47, ZK + 0.05]}),
    "turn_valve_up": dict(lean=0.45, hips=[0.0, 0.0, -0.14], hand_R={"world": [KX, 0.47, ZK + 0.05 + UP / 2]}),
    "egg_down": dict(lean=0.3, hand_R={"world": [PL_C[0], PL_C[1] - 0.05, 0.3]}),
    "pull_cord": dict(lean=0.1, hand_R={"world": [-4.7, 0.6, 0.95]}),
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "point_up": dict(lean=-0.1, hand_R={"char": [-0.2, -0.25, 1.35]}),
    "cheer": dict(lean=-0.1, hand_R={"char": [-0.24, -0.1, 1.2]}, hand_L={"char": [0.24, -0.1, 1.2]}),
}
G0 = (-3.6, 0.3)
G_VALVE = (KX, 0.18)
G_EGG = (PL_C[0] + 0.05, 0.3)
G_CORD = (-4.62, 0.28)
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. the problem; the valve
s, e = say("hard", 0.0, at=0.6)
to_lens(-1.0, e + 0.2)
face("raised", s, e + 0.3, set=dict(brow=0.7))
s, e = say("valve", 0.5)
to_lens(s - 0.2, e + 0.2)
B0 = s + 1.0
act(type="build", target="valve", when=round(B0, 3), until=round(B0 + 0.4, 3), stand_at=[G0[0], G0[1], 0.0], order="z")
TURN1 = e + 1.2
walk(e + 0.2, TURN1 - 0.2, G_VALVE)
pose("turn_valve", TURN1 - 0.3, TURN1 + 0.6, ease=0.2)
act(type="spin", target="valve", axis="y", degrees=90.0, pivot=[-45, 5, 0], when=round(TURN1, 3), until=round(TURN1 + 0.4, 3))
sfx("creak", TURN1, 0.3)
D10, D11 = TURN1 + 0.8, TURN1 + 5.8                                 # gently down
lift(D10, D11, -UP)
look(TURN1 + 0.6, D11, pos=(PL_C[0], PL_C[1], 1.0), body=True, rate=0.2)
s, e = say("brake", 0.0, at=D10 + 2.2)
to_lens(s - 0.2, e + 0.2)
face("smile", s, e + 0.4, set=dict(smile=0.9))
act(type="spin", target="valve", axis="y", degrees=-90.0, pivot=[-45, 5, 0], when=round(D11 + 0.2, 3), until=round(D11 + 0.5, 3))

# 2. the egg test
EGG = D11 + 1.4
walk(D11 + 0.4, EGG - 0.3, G_EGG)
pose("egg_down", EGG - 0.3, EGG + 0.4, ease=0.2)
EGG_AT = [PL_C[0], PL_C[1], 0.25 + 0.027]                           # on top of the crate (platform down)
act(type="hold", target="egg", hand="R", when=round(EGG - 0.5, 3), until=round(EGG, 3), reach=0.3, grip=[0.0, 0.0, 0.0],
    keys=[dict(t=round(EGG - 0.5, 3), at={"char": [-0.14, -0.26, 0.7]}, rot=[0, 0, 0]), dict(t=round(EGG, 3), at=EGG_AT, rot=[0, 0, 0])])
act(type="hold", target="egg", hand="none", when=-1.0, until=round(EGG - 0.55, 3), reach=0.05,
    keys=[dict(t=-1.0, at=[0.0, 0.0, -5.0], rot=[0, 0, 0])])                      # (in his pocket until then)
EGG_HOLD = len(A)
act(type="hold", target="egg", hand="none", when=round(EGG + 0.05, 3), until=99.0, reach=0.05, keys=[dict(t=round(EGG + 0.05, 3), at=EGG_AT, rot=[0, 0, 0])])
s, e = say("egg", 0.3, at=EGG + 0.3)
to_lens(s - 0.2, e + 0.2)
face("smirk", s, e + 0.3)
CHAT = [(e + 0.2, "GardenGranny", "not my good eggs dear")]
UP0 = e + 1.0
walk(e + 0.1, UP0 - 0.1, G_CORD)
pose("pull_cord", UP0 - 0.1, UP0 + 0.3, ease=0.12)
gate(UP0, 0.04)
U0, U1 = UP0 + 0.6, UP0 + 4.6
lift(U0, U1, UP)
gate(U1 - 0.3, -0.04)
DN = U1 + 0.8
walk(U1 - 0.6, DN - 0.2, G_VALVE)
pose("turn_valve_up", DN - 0.3, DN + 0.5, ease=0.2)                # (the barrel hangs low: its valve is at hand)
act(type="spin", target="valve", axis="y", degrees=90.0, pivot=[-45, 5, 0], when=round(DN, 3), until=round(DN + 0.4, 3))
D20, D21 = DN + 0.6, DN + 5.0
lift(D20, D21, -UP)
act(type="spin", target="valve", axis="y", degrees=-90.0, pivot=[-45, 5, 0], when=round(D21 + 0.2, 3), until=round(D21 + 0.5, 3))
smoother = lambda u: (lambda v: v * v * v * (v * (v * 6 - 15) + 10))(max(0.0, min(1.0, u)))
for t0, t1, sgn in ((U0, U1, 1.0), (D20, D21, -1.0)):              # the egg rides the crate, up and down
    base = 0.0 if sgn > 0 else UP
    A[EGG_HOLD]["keys"] += [dict(t=round(t0 + (t1 - t0) * q / 10, 3), at=[EGG_AT[0], EGG_AT[1], round(EGG_AT[2] + base + sgn * UP * smoother(q / 10), 4)],
                                 rot=[0, 0, 0]) for q in range(11)]
look(U0 - 0.3, D21 + 0.3, pos=(PL_C[0], PL_C[1], 1.0), body=True, rate=0.2)
s, e = say("crack", 0.0, at=D21 - 1.6)
face("alert", U0, D21 - 1.6, set=dict(brow=0.6))
pose("cheer", e - 0.6, e + 0.6, ease=0.2)
to_lens(e - 0.6, e + 0.3)
face("smile", e - 0.8, e + 0.8, set=dict(smile=1.0))
CHAT += [(e + 0.3, "BoarFan2009", "EGG SURVIVED")]

# 3. the baffles: smooth metal
s, e = say("last", 1.0)
look(s - 0.2, s + 1.5, pos=(-4.7, 0.7, 0.8), body=True, rate=0.3)
to_lens(s + 1.5, e + 0.2)
face("raised", s, e + 0.3, set=dict(brow=0.8))
B1 = e + 0.4
walk(B1 - 0.2, B1 + 0.6, G0)
act(type="build", target="baffles", when=round(B1 + 0.7, 3), until=round(B1 + 2.2, 3), stand_at=[G0[0], G0[1], 0.0], order="z")
sfx("clink", B1 + 1.0, 0.5); sfx("clink", B1 + 1.8, 0.5)
s, e = say("smooth", 0.3, at=B1 + 2.4)
LESSON0, LESSON1 = s, e
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
GOLD = e + 0.5                                                      # the light goes golden
s, e = say("tonight", 0.8, at=GOLD + 1.2)
look(s - 0.6, s + 0.8, pos=(-4.0, -3.0, 2.5), body=False, rate=0.3)
to_lens(s + 0.8, e + 0.2)
face("smirk", s, e + 0.4)
CHIT = e + 0.6
sfx("chitter_far", CHIT, 1.0)
look(CHIT + 0.1, CHIT + 1.3, pos=(-3.6, -1.6, 0.4), body=False, rate=0.5)
face("alert", CHIT + 0.1, CHIT + 1.2, set=dict(brow=1.1))
s, e = say("game", 0.0, at=CHIT + 1.4)
to_lens(s - 0.3, 99.0)
face("smirk", s, 99.0)
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
BLK = [KX, 0.7, ZK + 0.43]
VALVE_OUT = [KX + 0.0, 0.46, ZK + 0.02]
rig = dict(ropes=[dict(top=[KX - 0.05, 0.7, PUL_Z], follow="block", at=[BLK[0] - 0.05, 0.7, BLK[2]]),
                  dict(top=[-4.25, 0.7, 2.31], follow="block", at=[BLK[0] + 0.05, 0.7, BLK[2]]),
                  dict(top=[KX, 0.7, PUL_Z + PUL_R], follow="beam", at=[BX, 0.7, PUL_Z + PUL_R]),
                  dict(top=[-4.4, 0.95, 1.86], follow="frame_posts", at=[-4.7, 0.6, 0.95], width=0.008)]
                 + [dict(top=[BX, 0.7, PUL_Z - 0.05], follow="platform_l", at=[cx, cy, 0.05 + UP], width=0.01) for cx, cy in CORNERS],
           fills=[dict(follow="barrel", at=[KX + 0.05, 0.7, ZK], size=[0.27, 0.27, 0.36],
                       level=[[D10, 0.62], [D11, 0.05], [U0 - 0.4, 0.05], [U1, 0.62], [D20, 0.62], [D21, 0.05], [FILM + 1, 0.05]])],
           pours=[dict(**{"from": VALVE_OUT}, from_follow="barrel", follow="frame_posts", at=[VALVE_OUT[0], VALVE_OUT[1] - 0.04, -0.02],
                       on=[[TURN1 + 0.3, D11 + 0.2], [DN + 0.3, D21 + 0.2]], width=0.012),
                  dict(**{"from": [-4.42, 0.9, 1.72]}, follow="barrel", at=[KX + 0.05, 0.75, ZK + 0.36], on=[[UP0 + 0.05, U1 - 0.2]], width=0.02)])

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
tail = FILM - LE["game"] - 0.5 / FPS
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
TRAVEL = [(PL_C[0], PL_C[1], 0.02), (PL_C[0], PL_C[1], 2.05)]
SHOTS = [
    (0.0, (gp(*G0)[1:] + [(PL_C[0], PL_C[1], 2.05)], (-3.9, 0.45, 1.2), -25, 10, 2.6)),
    (TURN1 - 0.6, (gp(*G_VALVE)[1:] + TRAVEL, (-4.25, 0.55, 1.1), 63, 20, 4.4)),
    (EGG - 0.6, (gp(*G_EGG)[1:] + [EGG_AT], (G_EGG[0], 0.45, 0.6), -30, 14, 1.8)),
    (UP0 + 0.2, (gp(*G_CORD)[1:] + TRAVEL, (-4.25, 0.55, 1.1), 63, 20, 4.4)),
    (LS["last"] - 0.3, (gp(*G_VALVE)[1:], (G_VALVE[0], G_VALVE[1], 0.85), -30, 8, 1.6)),
    (B1 + 0.5, (gp(*G0)[1:] + [(-4.75, 0.7, 0.65), (-3.6, 0.7, 0.65), (-4.75, 0.7, 2.5)], (-4.15, 0.55, 1.1), 63, 16, 4.0)),
    (LS["smooth"] - 0.3, (gp(*G0)[1:], (G0[0], G0[1], 0.85), -20, 8, 1.6)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["tonight"] + 0.2, "lurker_77", "*brings popcorn*")]
HW = 3.0
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0}),
                                                               dict(icon="map", name="Blueprint", **{"in": -1.0})]),
         dict(style="panel", y="top", border="amber", when=round(LS["valve"] + 1.5, 3), until=round(LE["brake"] + 0.4, 3), rows=[
             dict(text="CONTROL THE DRAIN", color="white", at=round(LS["valve"] + 1.6, 3), size=40),
             dict(text="a little out at a time = a gentle way down", color="cyan", at=round(LS["valve"] + 2.8, 3), size=28)]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="SMOOTH METAL", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="claws can't grip it", color="cyan", at=round(LESSON0 + 1.2, 3), size=30)])]
W = {k: v for k, v in S7["world"].items() if k not in ("clouds_pass", "critters", "rigging")}
W.update(time="day", door_open=[-2.0, -1.0, 125.0], critters=[], rigging=rig,
         clouds_pass=[[round(GOLD + HW, 3), HW, 0.5, [1.0, 0.62, 0.32], True]])   # the afternoon turns golden and stays
story = dict(title="The Brake", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["hard"], tail=round(tail, 4), seed=108, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=8, name="The Brake", previous="raccoon_lift_scene07",
                                      next="raccoon_lift_scene09"),
             world=W, lines=lines, grandpa=dict(start=list(G0), outfit=S7["grandpa"]["outfit"]),
             poses=dict(S7["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"],
                     solid=["frame_posts", "beam", "barrel", "flume", "trestles", "crate", "stump", "scale_base", "baffles", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("turn %.2f down %.2f-%.2f egg %.2f up %.2f-%.2f down2 %.2f-%.2f baffles %.2f gold %.2f" % (TURN1, D10, D11, EGG, U0, U1, D20, D21, B1, GOLD))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
