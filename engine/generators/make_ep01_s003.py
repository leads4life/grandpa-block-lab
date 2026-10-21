"""Grandpa's Block Lab, Episode 1, Scene 003 -- "Rotten to the Core" (16:9, ~30 s).
Starts from Scene 002's continuity file. Rule 1: "this thing's been broken for years" -- whoever got it running only
replaced one post; the old one by the water is rotten. Rule 2: he sets the webcam down before working with both hands.
The trip hammer keeps its Scene 001/002 clock (2 cams, 60 deg apart, one turn every 3.3 s); while the rotten post sags,
the second cam misses (the rhythm stumbles) until the new post is in.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, eye_of, fix_path, TAN_H, TAN_V
import bl_world as BW
FPS, B = 30, 0.1
S2 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene002.json"))
C2 = json.load(open("/home/user/blocklab/ep01_scene002/grandpa_ep01_scene002_continuity.json"))
F2 = C2["film"]
S, A = {}, []

def add(p, q):
    return [round(p[i] + q[i], 4) for i in range(3)]
def rotz(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2])

# ---------------------------------------------------------------- the world exactly as Scene 002 left it
for name, st in S2["structures"].items():
    st = json.loads(json.dumps(st))
    if name not in ("wheel", "axle", "cam1", "cam2"):                # spinning parts: continuity stores them rotated about
        root = C2["structures"][name]["root"]                        # the pivot, so they keep their own place; their spin
        st["at"] = [round(root[0][3], 4), round(root[1][3], 4), round(root[2][3], 4)]   # carries on from the clock instead
    S[name] = st
CARRY = {"char": [-0.17, -0.18, 0.40]}                              # how he held the webcam at the end of Scene 002
CUBE_OFF = (0.0, -0.1, 0.35)
# the replacement: a stone footing, then a fresh post, exactly where the rotten one stands
OLD = S["axle_posts"]
S["footing"] = dict(cells=[[-47, 10, 0], [-47, 10, 1], [-47, 11, 0], [-47, 11, 1]], at=[0.0, 0.0, 0.0], centered=False,
                    material="stone", expect_blocks=4)
S["post2"] = dict(cells=[[-47, 10, z] for z in (2, 3, 4)], at=[0.0, 0.0, 0.0], centered=False, material="planks",
                  block_shape=[0.7, 0.7, 1], expect_blocks=3)
# a flat bank stone where he sets the webcam down (Rule 2: on something, pointed at the work)
S["rock"] = dict(cells=[[-38, 12, 0], [-37, 12, 0], [-38, 13, 0], [-37, 13, 0]], at=[0.0, 0.0, 0.0], centered=False,
                 material="stone", expect_blocks=4, prebuilt=True)
ROCK_TOP = 0.1
# tiny boot prints in the mud by the old post, leading down to the water
prints = [(-46, 12), (-47, 13), (-47, 14), (-48, 15), (-48, 16), (-49, 17)]
S["footprints"] = dict(cells=[[x, y, 0] for x, y in prints], at=[0.0, 0.0, -0.096], centered=False, material="coffee",
                       block_shape=[0.4, 0.6, 0.06], expect_blocks=len(prints), prebuilt=True)
POST = (-4.7, 1.0)
AXLE_PARTS = ["axle", "wheel", "cam1", "cam2"]
OAK = [t for t in BW.forest_trees() if abs(t[0] + 4.08) < 0.05 and abs(t[1] - 3.03) < 0.05][0]   # the real tree (Rule 1)

# ---------------------------------------------------------------- lines
LINES = [("hands", "Hang on, chat... Grandpa needs both hands."),
         ("notice", "Someone fixed that post... but not this one."),
         ("mush", "Oh! It's mush!"),
         ("rot", "Wet wood rots: tiny fungi eat it, and by a stream it never dries."),
         ("stone", "So we start with stone. Stone doesn't rot."),
         ("back", "There! Clunk, clunk... rest."),
         ("morning", "Morning!"),
         ("subscribe", "Hey! Don't forget to subscribe... bruh."),
         ("prints", "Wait... those aren't my footprints. And they're tiny."),
         ("rabbits", "...No. Rabbits don't fix machines.")]
GUESS = dict(hands=2.9, notice=2.8, mush=1.1, rot=4.2, stone=2.8, back=2.2, morning=0.7, subscribe=2.7, prints=3.2, rabbits=2.3)
dur_file = os.path.join(HERE, "ep01_s003_durations.json")
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
def look(t0, t1, pos=None, obj=None, off=None, body=False, **kw):
    a = dict(type="look", when=t0, until=t1, body=body, **kw)
    if pos is not None: a["pos"] = [round(v, 3) for v in pos]
    if obj: a["obj"], a["off"] = obj, list(off or (0, 0, 0))
    act(**a)
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)
def walk(t0, t1, to, via=()):
    act(type="move", to=list(to), via=[list(v) for v in via], when=t0, until=t1, face="path")

# the clunk clock, continued from Scene 002 (strikes at 1.28 + 3.3 k there; that scene lasted F2 s)
PERIOD, CAM_GAP = 3.3, 0.55
FIRST = round(1.28 + PERIOD * math.ceil((F2 - 1.28) / PERIOD) - F2 - PERIOD, 4)
STRIKES = [round(FIRST + PERIOD * k + o, 3) for k in range(0, 13) for o in (0.0, CAM_GAP)]
pair_after = lambda t: [s_ for i, s_ in enumerate(STRIKES) if i % 2 == 0 and s_ > t][0]

POSES = {
    "set_down": dict(lean=0.55, hips=[0.0, 0.0, -0.06]),
    "press_post": dict(hand_L=dict(world=[POST[0] + 0.08, POST[1], 0.36]), lean=0.25),
    "lift_axle": dict(hand_L=dict(world=[POST[0] + 0.1, 0.96, 0.47]), hand_R=dict(world=[POST[0] + 0.1, 1.04, 0.47]), lean=0.3),
    "peer_down": dict(lean=0.35, head=[0.0, -0.25, 0.0]),
}
G0 = C2["grandpa"]["root"]
face("alert", -5.0, 0.8, ease_out=0.4, set=dict(C2["grandpa"]["face"]))
act(type="face_camera", when=-5.0, until=0.6)                       # as Scene 002 ended: facing us
# 1. sets the webcam down on the grass, pointed at the work (Rule 2)
SET_SPOT = (-3.75, 1.25)                                            # where the cam cube sits: on the bank stone
CAM_YAW = 104.7                                                     # lens toward the old post
cube = (SET_SPOT[0], SET_SPOT[1], 0.35 - 0.30 + 0.0)
root_xy = [SET_SPOT[i] - rotz((0, -0.1, 0), CAM_YAW)[i] for i in range(2)]
CAM_ROOT = [round(root_xy[0], 4), round(root_xy[1], 4), round(-0.30 + ROCK_TOP, 3)]   # sits on the rock
s, e = say("hands", 0.0, at=0.35)
P_SET = [-3.74, 0.93, 0.0]
walk(0.5, 1.6, P_SET)
SET_T = max(1.9, e - 0.5)
pose("set_down", SET_T - 0.6, SET_T + 0.45, ease=0.3)
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R", when=-1.0, until=round(SET_T, 3), reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CARRY, rot=[0, 0, 0]), dict(t=round(SET_T - 0.55, 3), at=CARRY, rot=[0, 0, 0]),
              dict(t=round(SET_T, 3), at=CAM_ROOT, rot=[0, 0, CAM_YAW])])
look(0.5, SET_T + 0.3, pos=(SET_SPOT[0], SET_SPOT[1], 0.1), body=True, rate=0.12)
sfx("settle", SET_T - 0.05, 0.5)
# 2. "Somebody fixed that post... but not this old one."
WORK = [-4.44, 0.72, 0.0]
s, e = say("notice", 0.3)
walk(SET_T + 0.4, SET_T + 1.6, WORK, via=[(-4.0, 0.55, 0.0)])                # round the new post, not through it
act(type="point", target="new_post", pos=[-4.1, 0.86, 0.45], when=round(s + 0.2, 3), until=round(s + 1.3, 3))   # just short of it: no touching
look(SET_T + 0.4, s + 1.4, pos=(-4.1, 1.0, 0.4), body=True, rate=0.12)
look(s + 1.4, e + 1.0, pos=(POST[0], POST[1], 0.35), body=True, rate=0.12)
# 3. he presses it: it's mush -- the post sinks, the axle sags, the second cam starts missing
PRESS = e + 0.15
pose("press_post", PRESS - 0.3, PRESS + 0.9, ease=0.25)
sfx("crumble", PRESS + 0.1, 0.9)
SAG = 0.05
act(type="slide", target="axle_posts", by=[0.0, 0.0, -SAG], when=round(PRESS + 0.1, 3), until=round(PRESS + 0.4, 3), sound="none")
for n in AXLE_PARTS:
    act(type="slide", target=n, by=[0.0, 0.0, -SAG], when=round(PRESS + 0.15, 3), until=round(PRESS + 0.45, 3), sound="none")
face("surprised", PRESS + 0.1, PRESS + 0.8, ease=0.1)
s, e = say("mush", 0.0, at=PRESS + 0.25)
face("worried", e, e + 1.2)
# 4. the lesson, while he pulls the rotten blocks off
s, e = say("rot", 0.3)
RM0 = s + 0.3
act(type="remove", target="axle_posts", when=round(RM0, 3), until=round(RM0 + 1.6, 3), stand_at=list(WORK))
look(s, e + 0.2, pos=(POST[0], POST[1], 0.25), body=False)
face("content", e - 1.2, e + 0.2, set=dict(lid=0.2, smile=0.2))
# 5. stone first, then the post -- block by block
s, e = say("stone", 0.3)
B0 = s + 0.4
BF, BP = 0.8, 0.8                                                   # footing, post: block by block
P_NEXT = pair_after(B0 + BF + BP + 0.65)                             # the pair the restored rhythm should land on
if P_NEXT - (B0 + BF + BP + 0.65) > 1.6 and B0 + BF + BP + 0.65 - 0.6 > B0 + 1.2:
    pass
act(type="build", target="footing", when=round(B0, 3), until=round(B0 + BF, 3), stand_at=list(WORK), order="z")
act(type="build", target="post2", when=round(B0 + BF + 0.05, 3), until=round(B0 + BF + 0.05 + BP, 3), stand_at=list(WORK), order="z")
LIFT = B0 + BF + BP + 0.2
pose("lift_axle", LIFT - 0.3, LIFT + 0.75, ease=0.25)
for n in AXLE_PARTS:
    act(type="slide", target=n, by=[0.0, 0.0, SAG], when=round(LIFT, 3), until=round(LIFT + 0.4, 3), sound="none")
sfx("click_block", LIFT + 0.38, 0.8)
SKIP = [[round(PRESS + 0.1, 3), round(LIFT + 0.4, 3), 1]]           # cam 2 misses while the axle sags
# 6. the rhythm comes back: "There! Clunk, clunk... rest."
P_BACK = pair_after(LIFT + 0.4)
s, e = say("back", 0.2, at=P_BACK + CAM_GAP + 0.35)
face("warm", P_BACK, e + 0.4)
look(P_BACK - 0.3, e, pos=(-4.4, 1.95, 0.6), body=True, rate=0.1)
# 7. a rabbit hops out from behind the oak, sits and looks at him; "Morning!" -- then hops back behind the tree
RAB_SIT = (-3.55, 1.95)
R_IN = s + 0.5                                                       # it pops out while he is still talking
R_SIT0, R_SIT1 = R_IN + 1.2, R_IN + 3.0
behind = (OAK[0] + 0.05, OAK[1] + 0.35)
rabbit = dict(kind="rabbit", hop=0.09, hop_len=0.2, path=[[0.0, behind[0], behind[1]], [round(R_IN, 3), behind[0], behind[1]],
              [round(R_SIT0, 3), RAB_SIT[0], RAB_SIT[1]], [round(R_SIT1, 3), RAB_SIT[0], RAB_SIT[1]],
              [round(R_SIT1 + 1.1, 3), behind[0] - 0.05, behind[1] + 0.05]],
              visible=[round(R_IN - 0.05, 3), round(R_SIT1 + 1.15, 3)])     # pops out from behind the oak, then is gone again
look(R_IN + 0.3, R_SIT1 + 0.4, pos=(RAB_SIT[0], RAB_SIT[1], 0.15), body=True, rate=0.1)
s, e = say("morning", 0.0, at=R_SIT0 + 0.15)
pose("wave_R", s - 0.1, s + 1.3, ease=0.25)
face("smile", s - 0.1, s + 1.2)
# "Hey! Don't forget to subscribe... bruh." -- still waving at the tree
s, e = say("subscribe", 0.1, at=R_SIT1 + 0.15)
look(R_SIT1 + 0.3, e + 0.3, pos=(OAK[0], OAK[1], 0.6), body=True, rate=0.1)
pose("wave_R", e - 1.0, e + 0.3, ease=0.2)
face("smirk", e - 0.9, e + 0.4)
# 8. the tiny footprints in the mud; the rabbit? "...No. Rabbits don't fix machines."
s, e = say("prints", 0.2)
look(s - 0.2, e, pos=(-4.75, 1.45, 0.0), body=True, rate=0.12)
pose("peer_down", s, e + 0.1, ease=0.3)
face("confused", s + 0.3, e)
s, e = say("rabbits", 0.15)
look(s, s + 0.9, pos=(OAK[0], OAK[1], 0.4), body=False)
face("side_eye", s, s + 1.0)
act(type="face_camera", when=round(s + 0.9, 3), until=99.0)
face("alert", e - 0.4, 99.0)
END = e + 0.45
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# ---------------------------------------------------------------- the machine keeps running (Scene 002's clock)
T0 = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0) / PERIOD
for name, t0 in (("wheel", T0), ("axle", T0), ("cam1", T0), ("cam2", T0 + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
HAMMER_HEAD = (-4.4, 1.95, 0.6)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, skip=SKIP, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": list(HAMMER_HEAD)} if name == "head" else {}))

# ---------------------------------------------------------------- lines -> bl_voice
lines = []
for i, (lid, text) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["rabbits"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (auto-framed, clear of trees, walls and the machine)
TREES = BW.forest_trees()
def clear_air(eye):
    x, y, z = eye
    if -2.0 < x < 1.8 and -1.25 < y < 2.0 and z < 2.8:                  # inside the cabin, or against its walls
        return False
    if -5.6 < x < -3.95 and 0.3 < y < 2.3 and z < 1.3:                  # inside the machine
        return False
    for tx, ty, h, k in TREES + [(-2.0, 0.9, 0.45, "sapling")]:
        if math.hypot(x - tx, y - ty) < (1.0 if k != "sapling" else 0.4) and z < h + 1.2:   # trunks stay out of the shot
            return False
    return z > 0.3
POST_PT, AXLE_PT, PRINTS_PT = (POST[0], POST[1], 0.3), (POST[0], POST[1], 0.55), (-4.75, 1.45, 0.02)
CHEST = (WORK[0], WORK[1], 0.75)
def at_t(t):                                                         # where Grandpa stands at t (straight-line walk legs)
    legs = [(0.5, 1.6, G0, P_SET), (SET_T + 0.4, SET_T + 1.0, P_SET, (-4.0, 0.55)), (SET_T + 1.0, SET_T + 1.6, (-4.0, 0.55), WORK)]
    pos = G0
    for t0, t1, a, b in legs:
        if t >= t1: pos = b
        elif t > t0:
            u = (t - t0) / (t1 - t0); pos = [a[i] + (b[i] - a[i]) * u for i in range(2)]
    return gp(pos[0], pos[1])
def clear_far(eye):                                                 # wide shots: also well away from the cabin and its roof
    return clear_air(eye) and not (-2.45 < eye[0] < 2.0 and -1.7 < eye[1] < 2.3)
def solid_free(eye):                                                # the moving camera never enters a wall, canopy or the machine
    x, y, z = eye
    if -2.0 < x < 1.8 and -1.25 < y < 2.0 and z < 2.8:
        return False
    if -5.6 < x < -3.95 and 0.3 < y < 2.3 and z < 1.3:
        return False
    for tx, ty, h, k in TREES + [(-2.0, 0.9, 0.45, "sapling")]:
        half, top = {"oak": (0.375, h + 0.7), "pine": (0.4, 0.45 + h * 0.84 + 0.33), "sapling": (0.25, 0.8)}[k]
        if max(abs(x - tx), abs(y - ty)) < half + 0.25 and z < top + 0.25:
            return False
    return z > 0.3
BLOCKERS = [((-1.72, -0.9, 0.0), (-1.6, 1.72, 2.6)), ((1.4, -0.9, 0.0), (1.52, 1.72, 2.6)),      # cabin walls
            ((-1.72, 1.6, 0.0), (1.52, 1.72, 2.6)), ((-1.9, -1.1, 2.0), (1.7, 1.9, 2.9))]          # back wall, roof
for tx, ty, h, k in TREES:                                          # trunks and canopies, as built
    if k == "oak":
        BLOCKERS += [((tx - 0.07, ty - 0.07, 0), (tx + 0.07, ty + 0.07, h)), ((tx - 0.375, ty - 0.375, h - 0.03), (tx + 0.375, ty + 0.375, h + 0.47))]
    else:
        BLOCKERS += [((tx - 0.06, ty - 0.06, 0), (tx + 0.06, ty + 0.06, 0.5))] + [
            ((tx - w / 2, ty - w / 2, 0.45 + h * 0.28 * j - 0.01), (tx + w / 2, ty + w / 2, 0.45 + h * 0.28 * j + 0.33))
            for j, w in enumerate((0.8, 0.6, 0.4, 0.2))]
def seg_hits_box(p, q, lo, hi):                                     # slab test, segment p->q against an axis-aligned box
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = q[i] - p[i]
        if abs(d) < 1e-9:
            if p[i] < lo[i] or p[i] > hi[i]: return False
            continue
        a, b = (lo[i] - p[i]) / d, (hi[i] - p[i]) / d
        if a > b: a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1: return False
    return True
def clutter(eye, aim):                                              # share of a 7x5 ray grid over the frame hitting something
    f = [aim[i] - eye[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]   # before `aim`
    r = [f[1], -f[0], 0.0]; rn = math.hypot(r[0], r[1]); r = [v / rn for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    near = [(lo, hi) for lo, hi in BLOCKERS if math.dist(eye, [(lo[i] + hi[i]) / 2 for i in range(3)]) < n + 1.0]
    hits = 0
    for ix in range(-3, 4):
        for iy in range(-2, 3):
            dx, dy = ix / 3 * TAN_H * 0.9, iy / 2 * TAN_V * 0.9
            q = [eye[i] + (f[i] + dx * r[i] + dy * u[i]) * n for i in range(3)]
            hits += any(seg_hits_box(eye, q, lo, hi) for lo, hi in near)
    return hits / 35.0
def los(eye, pts):                                                  # nothing built stands between the lens and these points,
    aim = [sum(p[i] for p in pts) / len(pts) for i in range(3)]    # and little foreground clutter covers the frame
    if clutter(eye, aim) > 0.15:
        return False
    for p in pts:
        d = math.dist(eye, p); q = [p[i] + (eye[i] - p[i]) * min(0.25, d) / d for i in range(3)]   # stop 25 cm short
        if any(seg_hits_box(eye, q, lo, hi) for lo, hi in BLOCKERS):
            return False
    return True
GP_BODY = ((WORK[0] - 0.17, WORK[1] - 0.17, 0.0), (WORK[0] + 0.17, WORK[1] + 0.17, 1.15))   # Grandpa at work, as a box
def sees_repair(eye):                                               # repair shots: footing and post in view, not behind him
    pts = [(POST[0], POST[1], z) for z in (0.06, 0.16, 0.3)] + [(POST[0] + dx, POST[1], 0.1) for dx in (-0.06, 0.06)]
    return clear_air(eye) and not any(seg_hits_box(eye, p, *GP_BODY) for p in pts) and los(eye, pts)
last = C2["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
SHOTS = [
    lambda: auto_frame(SET_T - 0.2, gp(*P_SET[:2]) + [(SET_SPOT[0], SET_SPOT[1], 0.05)], (-3.75, 1.1, 0.6), -40, 14, 1.8, clear_air, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(LS["notice"] + 0.8, gp(*WORK[:2]) + [POST_PT, (-4.1, 1.0, 0.45)], (-4.4, 0.9, 0.55), -100, 14, 1.9, clear_air,
                  apart=(CHEST, POST_PT), prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(PRESS + 0.3, gp(*WORK[:2]) + [POST_PT, AXLE_PT], (-4.55, 0.9, 0.5), -150, 16, 1.6, sees_repair, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(LS["rot"] + 1.5, gp(*WORK[:2]) + [POST_PT], (-4.55, 0.9, 0.45), -150, 18, 1.6, sees_repair, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(B0 + 0.5, gp(*WORK[:2]) + [POST_PT, AXLE_PT], (-4.55, 0.9, 0.45), -150, 18, 1.6, sees_repair, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(P_BACK, gp(*WORK[:2]) + [(-5.0, 1.0, 0.55), HAMMER_HEAD, AXLE_PT], (-4.45, 1.2, 0.55), -20, 18, 2.3, clear_air, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(round(R_IN - 0.15, 3), gp(*WORK[:2]) + [(behind[0], behind[1], 0.1), (RAB_SIT[0], RAB_SIT[1], 0.1), (OAK[0], OAK[1], 1.0), (OAK[0], OAK[1], 0.2)],
                       (-3.95, 1.9, 0.55), -40, 14, 2.4, clear_far, prev=cam, path_clear=solid_free, los=los, who=at_t),   # the rabbit, in and out
    lambda: auto_frame(LS["prints"] + 0.4, gp(*WORK[:2]) + [PRINTS_PT, (-4.9, 1.65, 0.02)], (-4.6, 1.15, 0.35), -30, 26, 1.6, clear_air, prev=cam, path_clear=solid_free, los=los, who=at_t),
    lambda: auto_frame(FILM, gp(*WORK[:2]) + [PRINTS_PT], (-4.45, 0.95, 0.75), -40, 12, 1.6, clear_air, prev=cam, path_clear=solid_free, los=los, who=at_t),
]
for shot in SHOTS:                                                  # each move is checked against the key before it
    k = shot()
    cam += k if isinstance(k, list) else [k]
cam, PATCHED = fix_path(cam, clear_air, at_t, path_clear=solid_free)
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C2["overlay"]["live_viewers"]]]),
         dict(style="panel", y="top", border="amber", when=round(LS["rot"] + 0.3, 3), until=round(LS["stone"] + 0.3, 3), rows=[
             dict(text="WET WOOD + FUNGI = ROT", color="white", at=round(LS["rot"] + 0.4, 3), size=40)]),
         dict(style="panel", y="top", border="cyan", when=round(LS["stone"] + 0.5, 3), until=round(LE["back"] + 0.3, 3), rows=[
             dict(text="STONE FOOTING", color="white", at=round(LS["stone"] + 0.6, 3), size=40),
             dict(text="keeps the post dry", color="cyan", at=round(LS["stone"] + 1.6, 3), size=40)])]
W3 = dict(S2["world"])
W3["door_open"] = [-2.0, -1.0, S2["world"]["door_open"][2]]          # still standing open
W3["clouds_pass"] = [[round(LS["rot"] + 2.0, 3), 2.6, 0.45]]          # a cloud slides over the sun during the lesson
W3["leaves"] = dict(at=[-3.9, 1.6], r=1.8, n=14, t0=round(LE["back"] - 0.5, 3), t1=round(LE["subscribe"], 3))
W3["critters"] = [rabbit]
story = dict(title="Rotten to the Core", slug="grandpa_ep01_scene003", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["hands"], tail=round(tail, 4), seed=13, blink=True, target_duration=30,
             engine_rev=3, scene=dict(episode=1, scene=3, name="Rotten to the Core", previous="ep01_scene002", next="ep01_scene004"),
             world=W3, lines=lines, grandpa=dict(start=list(G0), outfit=S2["grandpa"]["outfit"]),
             poses=dict(S2["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["webcam", "rock"]], frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene003.json", "w"), indent=1)
print("film %.2f s; speech %.2f s; first strikes %s" % (FILM, sum(D[l] for l, _ in LINES), STRIKES[:6]))
for lid, _ in LINES:
    print("  %-10s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("camera keys patched at", PATCHED)
print("set %.2f press %.2f build %.2f lift %.2f back-pair %.2f rabbit %.2f-%.2f" % (SET_T, PRESS, B0, LIFT, P_BACK, R_IN, R_SIT1 + 1.1))
