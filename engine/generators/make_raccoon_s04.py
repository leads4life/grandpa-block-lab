"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 04
"The Big Idea" (16:9, ~60 s). Script: scenes/raccoon_lift/scene04_script.md (standing authorization, 2026-10-25).
Morning: the blueprint from his back pocket on the Page Card (an old-time water-balance lift), back in the pocket (hands
free). The tower comes down (its posts reused) and the lift frame goes up by the path's end: two tall posts, a beam, two
pulleys, a rope, the food box on one end and a bucket on the other, hanging balanced. Demo: a stone in the bucket -- the
bucket sinks, the box rises; out again -- it sinks back (lesson: COUNTERWEIGHT). Safety: never stand under a hanging load.
Hook: "Tomorrow... we let the river do the lifting."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP, SHOW_R, take_out, show_and_pocket
FPS = 30
SLUG = "raccoon_lift_scene04"
S3 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene03.json"))
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the land as Scene 03 left it (Rule 1)
for name, st in S3["structures"].items():
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st

# ---------------------------------------------------------------- the lift frame (cells absolute, 0.1 m)
FY = 7                                                              # the frame stands along y = 0.7
S["frame_posts"] = dict(cells=[[x, FY, z] for x in (-47, -37) for z in range(24)], at=[0.0, 0.0, 0.0], centered=False,
                        material="wood", block_shape=[0.9, 0.9, 1], expect_blocks=48)
S["beam"] = dict(cells=[[x, FY, 24] for x in range(-47, -36)], at=[0.0, 0.0, 0.0], centered=False, material="planks",
                 block_shape=[1, 0.9, 0.9], expect_blocks=11)
BX, KX = -4.0, -4.45                                                # the box hangs at x -4.0, the bucket at x -4.45
S["pulley_box"] = dict(cells=[[-40, FY, 22]], at=[0.0, 0.0, 0.0], centered=False, material="darkiron", block_shape=[1.6, 0.5, 1.6],
                       expect_blocks=1)
S["pulley_bkt"] = dict(cells=[[-44, FY, 22]], at=[-0.05, 0.0, 0.0], centered=False, material="darkiron", block_shape=[1.6, 0.5, 1.6],
                       expect_blocks=1)
PUL_Z = 2.25                                                        # wheel centres
PUL_R = 0.08
Z0 = 0.6                                                            # box and bucket hang balanced, both 0.6 m up
S["liftbox"] = dict(cells=[[x, y, z] for x in range(-41, -38) for y in range(6, 9) for z in range(3)], at=[0.0, 0.0, Z0],
                    centered=False, material="planks", expect_blocks=27)
S["bucket"] = dict(cells=[[x, FY, z] for x in (-45, -44) for z in range(3)], at=[0.0, 0.0, Z0], centered=False, material="oldwood",
                   block_shape=[1, 2, 1], expect_blocks=6)
S["stone_w"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="stone", block_shape=[0.9, 0.9, 0.8], expect_blocks=1)
S["blueprint"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="paper", block_shape=[1.5, 1.0, 0.1], expect_blocks=1)
TOWER = ["foodbox", "platform", "braces", "posts"]
LIFT_C = (-4.2, 0.7)

# ---------------------------------------------------------------- lines
LINES = [("drew", "I drew this last night. An old-time water-balance lift.", {}),
         ("hangs", "The box hangs on one end of a rope. A bucket hangs on the other.", {}),
         ("fill", "Fill the bucket with water... it gets heavy, it goes down... and the box goes UP.", {}),
         ("ready", "Ready, chat? Blocks up!", {}),
         ("heavy", "Heavy side goes down. The other side goes up.", {}),
         ("seesaw", "Like a seesaw on a rope. That's a counterweight.", {}),
         ("under", "And when something heavy hangs on a rope: never stand underneath.", {}),
         ("stream", "The stream, Granny. All day, for free.", {}),
         ("river", "Tomorrow... we let the river do the lifting.", {})]
GUESS = dict(drew=4.2, hangs=4.4, fill=6.2, ready=2.1, heavy=3.6, seesaw=3.6, under=4.6, stream=3.0, river=3.2)
dur_file = os.path.join(HERE, "raccoon_s04_durations.json")
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
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "point_up": dict(lean=-0.1, hand_R={"char": [-0.2, -0.25, 1.35]}),
    "drop_in": dict(lean=0.15, hand_R={"world": [KX, 0.7, Z0 + 0.42]}),
    "reach_out": dict(lean=0.2, hand_R={"world": [KX, 0.7, 0.42]}),
    "pick_low": dict(lean=0.55, hips=[0.0, 0.0, -0.2]),
}
G0 = (-3.6, 0.3)                                                    # on the path, south-east of the frame
G_BKT = (KX, 0.3)                                                   # south of the bucket, clear of it
STONE0 = [-3.3, 0.15, 0.04]
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. the blueprint: out of the back pocket, shown big, back in the pocket
T_OUT = 0.3
acts, t_out = take_out("blueprint", T_OUT, until=T_OUT + 1.0)
A += acts
s, e = say("drew", 0.0, at=0.5)
to_lens(-1.0, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=0.6))
s, e = say("hangs", 0.5)
to_lens(s - 0.2, e + 0.2)
s, e = say("fill", 0.4)
to_lens(s - 0.2, e + 0.2)
face("raised", s, e, set=dict(brow=0.7))
POCKET = e - 0.3
DRAW = dict(rects=[[0.12, 0.62, 0.30, 0.80], [0.66, 0.30, 0.80, 0.48]],          # the box (left), the bucket (right)
            lines=[[0.08, 0.06, 0.08, 1.0], [0.92, 0.06, 0.92, 1.0], [0.04, 0.06, 0.96, 0.06]],   # two posts, the beam
            circles=[[0.21, 0.13, 0.05], [0.73, 0.13, 0.05]],
            ropes=[[0.21, 0.08, 0.73, 0.08], [0.16, 0.13, 0.16, 0.62], [0.68, 0.13, 0.68, 0.30]],
            arrows=[[0.86, 0.36, 0.86, 0.6], [0.36, 0.78, 0.36, 0.54]],
            labels=[[0.21, 0.88, "FOOD"], [0.73, 0.55, "WATER"]])
acts, cards_bp, item = show_and_pocket("blueprint", t_out + 0.9, {"char": list(SHOW_R)}, POCKET,
                                       page=dict(title="WATER-BALANCE LIFT", drawing=DRAW), icon="map", name="Blueprint")
A += acts
act(type="hold", target="blueprint", hand="none", when=-1.0, until=round(T_OUT - 0.05, 3), reach=0.05,   # in the pocket at first
    keys=[dict(t=-1.0, at={"char": [-0.10, 0.13, 0.50]}, rot=[90, 0, 90], scale=0.35)])

# 2. the build: the tower comes down, the lift goes up
s, e = say("ready", 0.6)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", s + 0.6, e + 0.4, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.4
for name, d in zip(TOWER, (0.4, 0.4, 0.5, 0.8)):
    act(type="remove", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0])
    B0 += d + 0.05
for name, d in (("frame_posts", 1.8), ("beam", 0.8), ("pulley_box", 0.25), ("pulley_bkt", 0.25), ("liftbox", 1.0), ("bucket", 0.6)):
    act(type="build", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0], order="z")
    B0 += d + 0.08
ROPES_ON = B0 - 1.7                                                 # the rope goes on with the box and the bucket
look(LE["ready"] + 0.3, B0, pos=(LIFT_C[0], LIFT_C[1], 1.2), body=True, rate=0.3)

# 3. the demo: a stone in the bucket -- it sinks, the box rises; out again -- back
PICK = B0 + 0.9
walk(B0 + 0.1, PICK - 0.15, (STONE0[0] + 0.05, STONE0[1] + 0.28))
pose("pick_low", PICK - 0.35, PICK + 0.25, ease=0.2)
look(PICK - 0.6, PICK + 0.3, pos=STONE0, body=True, rate=0.3)
DROP = PICK + 1.9
walk(PICK + 0.3, DROP - 0.4, G_BKT)
pose("drop_in", DROP - 0.45, DROP + 0.2, ease=0.2)
look(DROP - 0.6, DROP + 2.0, pos=(KX, 0.7, Z0 + 0.3), body=True, rate=0.3)
SINK0, SINK1 = DROP + 0.15, DROP + 1.6
TRAVEL = 0.5
def stone_in_bucket(t):                                            # the stone sits in the bucket as it moves
    u = max(0.0, min(1.0, (t - SINK0) / (SINK1 - SINK0)))
    u = u * u * u * (u * (u * 6 - 15) + 10)
    return [KX, 0.7, round(Z0 + 0.32 - TRAVEL * u, 4)]
OUT = SINK1 + 4.6                                                   # after "heavy side goes down..."
RISE0, RISE1 = OUT + 0.25, OUT + 1.7
act(type="hold", target="stone_w", hand="R", when=round(PICK, 3), until=round(DROP, 3), reach=0.3, grip=[0.0, 0.0, 0.04],
    keys=[dict(t=round(PICK, 3), at=STONE0, rot=[0, 0, 0]), dict(t=round(PICK + 0.4, 3), at={"char": [-0.14, -0.26, 0.62]}, rot=[0, 0, 0]),
          dict(t=round(DROP - 0.4, 3), at={"char": [-0.14, -0.26, 0.62]}, rot=[0, 0, 0]), dict(t=round(DROP, 3), at=stone_in_bucket(DROP), rot=[0, 0, 0])])
act(type="hold", target="stone_w", hand="none", when=round(DROP + 0.05, 3), until=round(OUT, 3), reach=0.05,
    keys=[dict(t=round(t, 3), at=stone_in_bucket(t), rot=[0, 0, 0]) for t in [DROP + 0.05] + [SINK0 + (SINK1 - SINK0) * q / 6 for q in range(7)] + [OUT]])
sfx("clink", DROP + 0.05, 0.6)
act(type="slide", target="bucket", by=[0.0, 0.0, -TRAVEL], when=round(SINK0, 3), until=round(SINK1, 3))
act(type="slide", target="liftbox", by=[0.0, 0.0, TRAVEL], when=round(SINK0, 3), until=round(SINK1, 3))
TURN = round(math.degrees(TRAVEL / PUL_R), 2)
for p in ("pulley_box", "pulley_bkt"):
    act(type="spin", target=p, axis="y", degrees=TURN, pivot=S[p]["cells"][0], when=round(SINK0, 3), until=round(SINK1, 3))
sfx("creak", SINK0 + 0.1, 0.4)
s, e = say("heavy", 0.0, at=SINK0 + 0.3)
to_lens(s + 1.2, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=0.8))
pose("reach_out", OUT - 0.4, OUT + 0.3, ease=0.2)                   # the stone comes out...
act(type="hold", target="stone_w", hand="R", when=round(OUT, 3), until=round(OUT + 1.6, 3), reach=0.3, grip=[0.0, 0.0, 0.04],
    keys=[dict(t=round(OUT, 3), at=stone_in_bucket(OUT), rot=[0, 0, 0]), dict(t=round(OUT + 0.5, 3), at={"char": [-0.14, -0.26, 0.62]}, rot=[0, 0, 0]),
          dict(t=round(OUT + 1.2, 3), at={"char": [-0.2, -0.2, 0.3]}, rot=[0, 0, 0]), dict(t=round(OUT + 1.6, 3), at=[KX + 0.2, 0.25, 0.04], rot=[0, 0, 0])])
act(type="hold", target="stone_w", hand="none", when=round(OUT + 1.65, 3), until=99.0, reach=0.05,
    keys=[dict(t=round(OUT + 1.65, 3), at=[KX + 0.2, 0.25, 0.04], rot=[0, 0, 0])])
act(type="slide", target="bucket", by=[0.0, 0.0, TRAVEL], when=round(RISE0, 3), until=round(RISE1, 3))   # ...and back they go
act(type="slide", target="liftbox", by=[0.0, 0.0, -TRAVEL], when=round(RISE0, 3), until=round(RISE1, 3))
for p in ("pulley_box", "pulley_bkt"):
    act(type="spin", target=p, axis="y", degrees=-TURN, pivot=S[p]["cells"][0], when=round(RISE0, 3), until=round(RISE1, 3))
sfx("creak", RISE0 + 0.1, 0.35)
CHAT = [(RISE1 + 0.1, "TobiasBuilds", "like a seesaw on a rope")]
s, e = say("seesaw", 0.5, at=RISE1 + 0.6)
LESSON0, LESSON1 = s, e
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
walk(e + 0.2, e + 0.9, (G_BKT[0] + 0.25, 0.15))                    # a step back, clear of anything hanging
s, e = say("under", 0.6)
to_lens(s + 1.6, e + 0.2)
pose("point_up", s, s + 1.6, ease=0.25)
look(s - 0.2, s + 1.6, pos=(BX, 0.7, Z0 + 0.3), body=False, rate=0.3)
face("raised", s, e + 0.3, set=dict(brow=0.8))
CHAT += [(e + 0.4, "GardenGranny", "where does the water come from dear?")]
s, e = say("stream", 1.6)
look(s - 0.6, s + 1.0, pos=(-5.2, 0.6, 0.1), body=True, rate=0.25)
to_lens(s + 1.0, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=0.6))
s, e = say("river", 0.6)
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
tail = FILM - LE["river"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# the rope: over both pulleys, down to the box and the bucket (they follow their slides)
rig = dict(ropes=[dict(top=[BX, 0.7, PUL_Z], follow="liftbox", at=[BX, 0.7, Z0 + 0.3], visible=[ROPES_ON, FILM + 1]),
                  dict(top=[KX, 0.7, PUL_Z], follow="bucket", at=[KX, 0.7, Z0 + 0.3], visible=[ROPES_ON, FILM + 1]),
                  dict(top=[KX, 0.7, PUL_Z + PUL_R], follow="beam", at=[BX, 0.7, PUL_Z + PUL_R], visible=[ROPES_ON, FILM + 1])])

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
FRAME_FREE = lambda eye: not all(FRAME_BOX[0][i] - 0.2 <= eye[i] <= FRAME_BOX[1][i] + 0.2 for i in range(3))
AIR = both(clear_air, WALL_FREE, FRAME_FREE)
PATH = both(solid_free, WALL_FREE, FRAME_FREE)
LOS = make_los([])
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
LIFT_PTS = [(-4.7, 0.7, 0.02), (-3.7, 0.7, 0.02), (-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5)]
SHOTS = [
    (0.0, (gp(*G0)[1:], (G0[0], G0[1], 0.85), -25, 8, 1.6)),
    (LS["ready"] + 1.0, (gp(*G0) + LIFT_PTS, (-4.15, 0.55, 1.2), -20, 8, 3.6)),
    (PICK - 0.6, (gp(*G_BKT) + [(KX, 0.7, Z0), (BX, 0.7, Z0 + 0.3 + TRAVEL), STONE0], (-4.1, 0.5, 0.7), -30, 10, 2.4)),
    (LS["seesaw"] - 0.3, (gp(*G_BKT)[1:], (G_BKT[0], G_BKT[1], 0.85), -15, 8, 1.6)),
    (LS["under"] - 0.3, (gp(G_BKT[0] + 0.25, 0.15) + [(BX, 0.7, Z0 + 0.3)], (-4.1, 0.4, 0.8), -20, 10, 2.2)),
    (LS["stream"] - 0.3, (gp(G_BKT[0] + 0.25, 0.15)[1:], (G_BKT[0] + 0.25, 0.15, 0.85), -10, 8, 1.6)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["river"] - 0.8, "BoarFan2009", "RIVER POWER")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0}),
                                                               dict(icon="map", name="Blueprint", **{"in": -1.0, "out": T_OUT}), item]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="COUNTERWEIGHT", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="the heavy side goes down, the other side goes up", color="cyan", at=round(LESSON0 + 1.2, 3), size=28)])] + cards_bp
W = {k: v for k, v in S3["world"].items() if k not in ("clouds_pass", "critters")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[], rigging=rig)
story = dict(title="The Big Idea", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["drew"], tail=round(tail, 4), seed=104, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=4, name="The Big Idea", previous="raccoon_lift_scene03",
                                      next="raccoon_lift_scene05"),
             world=W, lines=lines, grandpa=dict(start=list(G0), outfit=S3["grandpa"]["outfit"]),
             poses=dict(S3["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"],
                     solid=["frame_posts", "beam", "liftbox", "bucket", "crate", "stump", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("pocket %.2f build-end %.2f pick %.2f drop %.2f out %.2f" % (POCKET, B0, PICK, DROP, OUT))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
