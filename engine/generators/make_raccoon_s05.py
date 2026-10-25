"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 05
"Test 1: Cabbage Launch" (16:9, ~55 s). Script: scenes/raccoon_lift/scene05_script.md (standing authorization).
Morning: box down with three cabbages on it, bucket up and empty (the loaded box is the heavier side). The build: a flume
on trestles from upstream (water runs downhill) to a spout with a little sluice gate over the bucket. Gate wide open: the
bucket fills in a flash and drops until it hits the ground (BANG) -- the box jerks to a stop at 1.2 m and a cabbage sails
into the stream. Lesson: a little at a time. Gate shut, plug out, the box comes back down. Second go: the gate open a
crack, the box rises slowly... and stops halfway (the plug is not quite in: water leaks out as fast as it comes in --
Scene 06 finds it). Physics: rope length is kept (box up = bucket down); the bucket cannot go below the ground.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene05"
S4 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene04.json"))
S, A = {}, []

# ---------------------------------------------------------------- the land as Scene 04 left it (Rule 1)
for name, st in S4["structures"].items():
    if name in ("foodbox", "platform", "braces", "posts", "blueprint"):   # the tower came down in Scene 04; the page is pocketed
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
FY = 7
BX, KX = -4.0, -4.45
PUL_Z, PUL_R = 2.25, 0.08
ZB0, ZK0 = 0.0, 1.2                                                 # box down (loaded: heavier), bucket up (empty)
S["liftbox"]["at"] = [0.0, 0.0, ZB0]
S["bucket"]["at"] = [0.0, 0.0, ZK0]
S["stone_w"]["at"] = [KX + 0.2, 0.25, 0.04]                         # where he left it
S["cabbages3"] = dict(cells=[[x, FY, 3] for x in (-41, -40)], at=[0.0, 0.0, ZB0 - 0.005], centered=False, material="cabbage",
                      block_shape=[0.9, 0.9, 0.9], expect_blocks=2)
S["cab_fly"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="cabbage", block_shape=[0.9, 0.9, 0.9], expect_blocks=1)
CAB0 = [-3.9, 0.7, ZB0 + 0.345]                                     # the third cabbage, on the box's east end

# ---------------------------------------------------------------- the flume: upstream on trestles, down to a spout over the bucket
FX = 0.05                                                           # x offset: the channel runs along x -4.75
fl_bottom, fl_walls, fl_water = [], [], []
def zb(y):                                                          # the channel bottom steps down toward the lift
    return 19 if y >= 20 else 18 if y >= 14 else 17
for y in range(10, 27):
    z = zb(y)
    fl_bottom.append([-48, y, z])
    fl_walls += [[-49, y, z + 1], [-47, y, z + 1]]
    fl_water.append([-48, y, z + 1])
for x in (-47, -46, -45):                                           # the spout turns east over the bucket (y 0.9, clear of the post)
    fl_bottom.append([x, 9, 17])
    fl_walls += [[x, 8, 18], [x, 10, 18]]
    fl_water.append([x, 9, 18])
fl_walls.append([-48, 8, 18])
S["trestles"] = dict(cells=[[-48, y, z] for y in (15, 24) for z in range(zb(y))], at=[FX, 0.0, 0.0], centered=False, material="oldwood",
                     block_shape=[0.6, 0.6, 1], expect_blocks=sum(zb(y) for y in (15, 24)))
S["flume"] = dict(cells=fl_bottom + fl_walls, at=[FX, 0.0, 0.0], centered=False, material="planks", block_shape=[1, 1, 0.5],
                  expect_blocks=len(fl_bottom) + len(fl_walls))
S["flume_water"] = dict(cells=fl_water, at=[FX, 0.0, -0.05], centered=False, material="blue", block_shape=[0.8, 1, 0.25],
                        expect_blocks=len(fl_water))
S["gate"] = dict(cells=[[-44, 9, 18]], at=[FX - 0.04, 0.0, 0.0], centered=False, material="planks", block_shape=[0.25, 1.2, 1.2],
                 expect_blocks=1)
SPOUT = [-4.42, 0.9, 1.72]                                          # where the water leaves the spout
CLEAT = [-4.7, 0.6, 0.95]                                           # the gate cord's cleat on the west post
FRAME_PTS = [(-4.7, 0.7, 0.02), (-3.7, 0.7, 0.02), (-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5)]

# ---------------------------------------------------------------- lines
LINES = [("down", "Box down, cabbages in. Bucket up, and empty.", {}),
         ("downhill", "Water runs downhill. So we catch it upstream, where it's higher... and let it slide all the way here.", {}),
         ("ready", "Ready, chat? Blocks up!", {}),
         ("open", "Moment of truth. Gate... OPEN!", {}),
         ("huh", "...Huh.", dict(lens=False, why="stunned, staring at the stream where the cabbage landed")),
         ("swim", "The cabbage is fine. The cabbage is... swimming.", {}),
         ("lesson", "Too much water, too fast. Lesson one: open a gate a little at a time.", {}),
         ("little", "Little... by little...", dict(lens=False, why="whispered, eyes on the rising box")),
         ("stop", "...Why did it stop?", {})]
GUESS = dict(down=3.6, downhill=6.4, ready=2.1, open=3.0, huh=1.0, swim=3.6, lesson=5.2, little=2.4, stop=1.8)
dur_file = os.path.join(HERE, "raccoon_s05_durations.json")
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
def lift(t0, t1, dz):                                               # box up by dz = bucket down by dz (one rope); pulleys turn
    act(type="slide", target="liftbox", by=[0.0, 0.0, dz], when=round(t0, 3), until=round(t1, 3))
    act(type="slide", target="cabbages3", by=[0.0, 0.0, dz], when=round(t0, 3), until=round(t1, 3))
    act(type="slide", target="bucket", by=[0.0, 0.0, -dz], when=round(t0, 3), until=round(t1, 3))
    for p in ("pulley_box", "pulley_bkt"):
        act(type="spin", target=p, axis="y", degrees=round(math.degrees(dz / PUL_R), 2), pivot=S[p]["cells"][0], when=round(t0, 3), until=round(t1, 3))

POSES = {
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "point_far": dict(lean=-0.05, hand_R={"char": [-0.25, -0.35, 1.15]}),
    "pull_cord": dict(lean=0.1, hand_R={"world": CLEAT}),
    "aghast": dict(lean=-0.08, shrug=0.5, elbows=0.5),
    "lean_watch": dict(head=[0.0, 0.0, 0.22], lean=0.05),
}
G0 = (-3.6, 0.3)
G_CORD = (-4.62, 0.28)                                              # by the west post, south of it: the gate cord
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. box down, bucket up; the flume
s, e = say("down", 0.0, at=0.5)
to_lens(-1.0, e + 0.2)
face("content", s, e + 0.3)
s, e = say("downhill", 0.5)
pose("point_far", s, s + 2.2, ease=0.25)
look(s - 0.2, s + 2.2, pos=(-5.0, 3.5, 1.6), body=True, rate=0.25)
to_lens(s + 2.2, e + 0.2)
face("raised", s, e, set=dict(brow=0.6))
s, e = say("ready", 0.4)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", s + 0.6, e + 0.4, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.4
for name, d in (("trestles", 1.0), ("flume", 2.4), ("flume_water", 0.4), ("gate", 0.3)):
    act(type="build", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0], order="z" if name != "flume" else "y",
        **({"quiet": True} if name == "flume_water" else {}))
    B0 += d + 0.08
look(LE["ready"] + 0.3, B0, pos=(-4.75, 1.8, 1.7), body=True, rate=0.3)

# 2. gate wide open: CABBAGE LAUNCH
walk(B0 + 0.1, B0 + 1.4, G_CORD)
s, e = say("open", 0.2, at=B0 + 1.5)
to_lens(s - 0.2, s + 1.5)
OPEN1 = e - 0.1
pose("pull_cord", OPEN1 - 0.35, OPEN1 + 0.3, ease=0.12)
look(s + 1.5, OPEN1 + 3.5, pos=(KX, 0.7, 1.4), body=True, rate=0.3)
act(type="slide", target="gate", by=[0.0, 0.0, 0.14], when=round(OPEN1, 3), until=round(OPEN1 + 0.15, 3))
sfx("gush", OPEN1 + 0.05, 1.0)
FILL1 = (OPEN1 + 0.1, OPEN1 + 0.7)
DROP0, DROP1 = OPEN1 + 0.3, OPEN1 + 0.8                             # fast: the bucket is far heavier
lift(DROP0, DROP1, ZK0)                                             # the bucket falls all the way to the ground...
BANG = DROP1
sfx("thud", BANG, 1.1); sfx("clatter", BANG + 0.02, 0.6)            # ...BANG: the box stops dead at 1.2 m
FLY1 = BANG + 0.95
LAND = [-5.2, 0.2, -0.05]
apex = [(CAB0[0] + LAND[0]) / 2, (CAB0[1] + LAND[1]) / 2, ZK0 + 0.345 + 0.9]
def cab_at(u):
    p0 = [CAB0[0], CAB0[1], CAB0[2] + ZK0]
    return [round(p0[i] + (LAND[i] - p0[i]) * u + (0 if i < 2 else 4 * (apex[2] - (p0[2] + LAND[2]) / 2) * u * (1 - u)), 4) for i in range(3)]
cab_keys = [dict(t=-1.0, at=CAB0, rot=[0, 0, 0])]
cab_keys += [dict(t=round(DROP0 + (DROP1 - DROP0) * q / 4, 3), at=[CAB0[0], CAB0[1], round(CAB0[2] + ZK0 * (lambda u: u * u * u * (u * (u * 6 - 15) + 10))(q / 4), 4)], rot=[0, 0, 0])
             for q in range(5)]
cab_keys += [dict(t=round(BANG + (FLY1 - BANG) * q / 8, 3), at=cab_at(q / 8), rot=[0, round(-60 * q, 1), round(25 * q, 1)]) for q in range(1, 9)]
cab_keys += [dict(t=round(FLY1 + 0.6, 3), at=[LAND[0], LAND[1] - 0.25, -0.04], rot=[0, -480, 200]), dict(t=99.0, at=[LAND[0], LAND[1] - 0.25, -0.04], rot=[0, -480, 200])]
act(type="hold", target="cab_fly", hand="none", when=-1.0, until=99.0, reach=0.05, keys=cab_keys)
sfx("splash", FLY1, 1.0)
face("surprised", BANG - 0.05, FLY1 + 1.2, set=dict(brow=1.3))
pose("aghast", BANG, FLY1 + 0.8, ease=0.12)
look(BANG + 0.1, FLY1 + 1.6, pos=(LAND[0], LAND[1], 0.3), body=False, rate=0.4)
CLOSE1 = BANG + 1.1
act(type="slide", target="gate", by=[0.0, 0.0, -0.14], when=round(CLOSE1, 3), until=round(CLOSE1 + 0.2, 3))
s, e = say("huh", 0.0, at=FLY1 + 0.6)
CHAT = [(e + 0.3, "BoarFan2009", "CABBAGE LAUNCH"), (e + 1.1, "GardenGranny", "is the cabbage okay dear")]
s, e = say("swim", 1.8)
to_lens(s - 0.3, e + 0.2)
face("smirk", s, e + 0.4)

# 3. the lesson: gate shut, plug out, the box comes down
s, e = say("lesson", 0.5)
LESSON0, LESSON1 = s, e
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
PLUG = s + 0.8
DRAIN = (PLUG, PLUG + 2.4)
DOWN0, DOWN1 = PLUG + 1.4, PLUG + 3.4                                # lighter than the box again: down it comes (slower)
lift(DOWN0, DOWN1, -ZK0)
sfx("creak", DOWN0 + 0.1, 0.35)

# 4. second go: a crack... the box rises slowly... and stops halfway
OPEN2 = max(DOWN1 + 0.6, LE["lesson"] + 0.5)
pose("pull_cord", OPEN2 - 0.35, OPEN2 + 0.3, ease=0.12)
act(type="slide", target="gate", by=[0.0, 0.0, 0.03], when=round(OPEN2, 3), until=round(OPEN2 + 0.2, 3))
RISE0, RISE1 = OPEN2 + 1.2, OPEN2 + 5.2
HALF = 0.6
lift(RISE0, RISE1, HALF)
s, e = say("little", 0.0, at=RISE0 + 0.4)
look(OPEN2 + 0.3, RISE1 + 1.0, pos=(BX, 0.7, 0.6), body=True, rate=0.2)
pose("lean_watch", RISE0, RISE1 + 0.4, ease=0.4)
face("alert", OPEN2 + 0.2, RISE1, set=dict(brow=0.6))
s, e = say("stop", 0.0, at=RISE1 + 1.1)
to_lens(s - 0.3, 99.0)
face("confused", RISE1 + 0.3, 99.0)
END = e + 1.3
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# the water: the gush, the drain, the trickle (and a drip from the plug that isn't quite in)
FILL_AT = [KX, 0.7, ZK0 + 0.03]
rig = dict(ropes=[dict(top=[BX, 0.7, PUL_Z], follow="liftbox", at=[BX, 0.7, ZB0 + 0.3]),
                  dict(top=[KX, 0.7, PUL_Z], follow="bucket", at=[KX, 0.7, ZK0 + 0.3]),
                  dict(top=[KX, 0.7, PUL_Z + PUL_R], follow="beam", at=[BX, 0.7, PUL_Z + PUL_R]),
                  dict(top=[-4.4, 0.95, 1.86], follow="frame_posts", at=CLEAT, width=0.008)],      # the gate cord
           fills=[dict(follow="bucket", at=FILL_AT, size=[0.17, 0.17, 0.25],
                       level=[[FILL1[0], 0.0], [FILL1[1], 1.0], [DRAIN[0], 1.0], [DRAIN[1], 0.0], [RISE0 - 0.6, 0.0], [RISE1, 0.55], [FILM + 1, 0.55]])],
           pours=[dict(**{"from": SPOUT}, follow="bucket", at=[KX, 0.72, ZK0 + 0.3], on=[[OPEN1 + 0.05, CLOSE1 + 0.1]], width=0.05),
                  dict(**{"from": SPOUT}, follow="bucket", at=[KX, 0.72, ZK0 + 0.3], on=[[OPEN2 + 0.1, FILM + 1]], width=0.012),
                  dict(**{"from": [KX + 0.06, 0.62, ZK0 - 0.01]}, from_follow="bucket", follow="frame_posts", at=[KX + 0.06, 0.62, -0.02],
                       on=[[DRAIN[0], DRAIN[1]]], width=0.03),                         # plug out: it drains to the ground
                  dict(**{"from": [KX + 0.06, 0.62, ZK0 - 0.01]}, from_follow="bucket", follow="frame_posts", at=[KX + 0.06, 0.62, -0.02],
                       on=[[RISE1 - 0.5, FILM + 1]], width=0.006)])                    # the plug not quite in: a drip

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
tail = FILM - LE["stop"] - 0.5 / FPS
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
WHEEL_BOX = ((-5.12, 0.38, -0.05), (-4.88, 1.62, 1.18))
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
SHOTS = [
    (0.0, (gp(*G0) + [(BX, 0.7, 0.4), (KX, 0.7, 1.5)], (-4.0, 0.5, 0.8), -25, 10, 2.6)),
    (LS["ready"] + 1.0, (gp(*G0)[1:] + [(-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5), (-4.6, 0.9, 1.75), (BX, 0.7, 0.0)], (-4.1, 0.6, 1.3), 80, 17, 4.6)),
    (B0 + 0.2, (gp(*G_CORD)[1:] + [(BX, 0.7, 1.55), (KX, 0.7, 0.0), (BX, 0.7, 0.0)], (-4.3, 0.55, 0.9), -40, 10, 2.8)),
    (BANG + 0.25, ([cab_at(0.3), cab_at(0.7), (LAND[0], LAND[1], 0.0), (BX, 0.7, 1.55)], (-4.6, 0.45, 1.0), 96, 26, 4.2)),   # the cabbage flies (a cutaway)
    (FLY1 + 0.5, (gp(*G_CORD)[1:] + [(BX, 0.7, 1.55)], (-4.4, 0.5, 1.0), -40, 8, 2.2)),
    (LS["swim"] - 0.3, (gp(*G_CORD)[1:], (G_CORD[0], G_CORD[1], 0.85), -40, 8, 1.6)),
    (DOWN0 - 0.4, (gp(*G_CORD) + [(BX, 0.7, 0.0), (BX, 0.7, 1.55), (KX, 0.7, 1.5)], (-4.25, 0.5, 0.9), -35, 10, 2.8)),
    (LS["stop"] - 0.4, (gp(*G_CORD)[1:] + [(BX, 0.7, HALF + 0.3)], (-4.35, 0.45, 0.85), -40, 8, 2.0)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["lesson"] + 0.3, "TobiasBuilds", "slow is smooth. smooth is fast")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0}),
                                                               dict(icon="map", name="Blueprint", **{"in": -1.0})]),
         dict(style="panel", y="top", border="amber", when=round(LS["downhill"] + 1.0, 3), until=round(LE["downhill"] + 0.4, 3), rows=[
             dict(text="WATER RUNS DOWNHILL", color="white", at=round(LS["downhill"] + 1.1, 3), size=40),
             dict(text="so the flume starts upstream, where it is higher", color="cyan", at=round(LS["downhill"] + 2.4, 3), size=28)]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="A LITTLE AT A TIME", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="too much, too fast = trouble", color="cyan", at=round(LESSON0 + 1.2, 3), size=30)])]
W = {k: v for k, v in S4["world"].items() if k not in ("clouds_pass", "critters", "rigging")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[], rigging=rig)
story = dict(title="Test 1: Cabbage Launch", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["down"], tail=round(tail, 4), seed=105, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=5, name="Test 1: Cabbage Launch", previous="raccoon_lift_scene04",
                                      next="raccoon_lift_scene06"),
             world=W, lines=lines, grandpa=dict(start=list(G0), outfit=S4["grandpa"]["outfit"]),
             poses=dict(S4["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"], cutaways=[[round(math.ceil((BANG + 0.25) * FPS) / FPS - 0.001, 3), round(math.ceil((FLY1 + 0.5) * FPS) / FPS + 0.001, 3)]],
                     solid=["frame_posts", "beam", "liftbox", "bucket", "flume", "trestles", "crate", "stump", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("open %.2f bang %.2f splash %.2f drain %.2f-%.2f open2 %.2f rise %.2f-%.2f" % (OPEN1, BANG, FLY1, DRAIN[0], DRAIN[1], OPEN2, RISE0, RISE1))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
