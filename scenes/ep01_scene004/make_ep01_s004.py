"""Grandpa's Block Lab, Episode 1, Scene 004 -- "No Cap, Chat!" (16:9, ~30 s). Approved beat sheet (2026-10-21).
Starts from Scene 003's continuity file. Grandpa Tovi props the hammer up to follow the prints in peace: silence. A wild
boar pushes out of the bushes; "You kinda bussin'!" -- it huffs, clacks its tusks, stomps; he freezes: "NO CAP, CHAT!"
Tobias steps out from behind the oak: the trip hammer is his boar alarm (water-powered boar scarer, Rule 1: the clunks
of Scenes 001-003 were always for this). He pulls the prop: the cam takes the hammer and CLUNK, CLUNK -- the boar bolts.
"Tobias... you just gained a thousand aura points!" -- "That's not how aura works, Grandpa."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, eye_of, fix_path, project, TAN_H, TAN_V
import bl_world as BW
FPS = 30
S3 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene003.json"))
C3 = json.load(open("/home/user/blocklab/ep01_scene003/grandpa_ep01_scene003_continuity.json"))
F3 = C3["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 003 left it
for name, st in S3["structures"].items():
    cs = C3["structures"][name]
    if cs["blocks_standing"] == 0:
        continue                                                    # the rotten post is gone
    st = json.loads(json.dumps(st))
    if name in ("footing", "post2"):
        st["prebuilt"] = True                                       # built in Scene 003: simply there now
    if name in ("webcam", "cam_cap"):                               # set down on the bank stone (Rule 2)
        r = cs["root"]
        st["at"] = [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)]
        st["yaw"] = round(math.degrees(math.atan2(r[1][0], r[0][0])), 2)
    S[name] = st
# the prop: a short stick Grandpa wedges between the anvil and the lifted hammer head
S["prop"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="oldwood", block_shape=[0.5, 0.5, 2.0], expect_blocks=1,
                 prebuilt=True)
OAK = [t for t in BW.forest_trees() if abs(t[0] + 4.08) < 0.05 and abs(t[1] - 3.03) < 0.05][0]

# ---------------------------------------------------------------- lines (who: tobias -> his voice, his jaw)
LINES = [("bussin", "You kinda bussin'!", None),
         ("nocap", "NO CAP, CHAT!", None),
         ("alarm", "Grandpa. You turned off the boar alarm.", "tobias"),
         ("how", "The water turns the wheel, the cams lift the hammer, and every few seconds...", "tobias"),
         ("hate", "Boars hate surprise noises. I fixed it so he stays out of my garden.", "tobias"),
         ("aura", "Tobias... you just gained a thousand aura points!", None),
         ("works", "That's not how aura works, Grandpa.", "tobias")]
GUESS = dict(bussin=1.3, nocap=1.1, alarm=2.0, how=4.3, hate=3.6, aura=3.0, works=1.9)
dur_file = os.path.join(HERE, "ep01_s004_durations.json")
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

# the clunk clock, continued from Scene 003 (strike pairs every 3.3 s, cams 0.55 s apart)
PERIOD, CAM_GAP = 3.3, 0.55
TRIP3 = [a for a in S3["actions"] if a["type"] == "trip"][0]
FIRST = TRIP3["first"] - F3
FIRST = round(FIRST + PERIOD * math.ceil(-FIRST / PERIOD) - PERIOD, 4)          # same grid, first pair at or before 0
PAIRS = [round(FIRST + PERIOD * k, 3) for k in range(0, 14)]
pair_after = lambda t: [p for p in PAIRS if p >= t][0]
PIVOT = (-4.4, 1.3, 0.75)
HAMMER_HEAD = (-4.4, 1.95, 0.6)

POSES = {
    "pry": dict(lean=0.04),                                         # one hand on the lever (the stick), the other on his back
    "finger_guns": dict(hand_R=dict(char=(-0.22, -0.30, 0.80)), hand_L=dict(char=(0.22, -0.30, 0.80)), lean=-0.05),
    "freeze": dict(hand_R=dict(char=(-0.34, -0.06, 1.08)), hand_L=dict(char=(0.34, -0.06, 1.08)), lean=-0.22, head=(0.0, 0.05, 0.0)),
    "admire": dict(hand_R=dict(char=(-0.06, -0.17, 0.82)), lean=0.06, head=(0.0, 0.04, 0.0)),   # proud: hand on his heart
}
G0 = C3["grandpa"]["root"]                                          # (-4.44, 0.72), by the footprints
HELVE_SPOT = (-4.06, 1.56)                                          # where he stands after: a step clear of the anvil
LIFT_SPOT = (-4.10, 1.66)                                           # where he works: in reach of the hammer head and the prop
face("alert", -5.0, 0.6, ease_out=0.4, set=dict(C3["grandpa"]["face"]))
act(type="face_camera", when=-5.0, until=0.3)
# 1. he props the hammer up so he can follow the prints in peace -- silence
WALK_VIA = [(-4.2, 0.58), (-3.45, 0.85), (-3.5, 1.5)]               # south of the new post, east of the bank stone
walk(0.3, 2.4, LIFT_SPOT, via=[(x, y, 0.0) for x, y in WALK_VIA])
LOOK_H = len(A); look(2.1, 99.0, pos=HAMMER_HEAD, body=True, rate=0.12)
S_A = pair_after(2.2)                                               # the last pair before the quiet
LIFT0 = S_A + CAM_GAP + 0.15
pose("pry", LIFT0 - 0.25, LIFT0 + 1.15, ease=0.2)
pose("hand_on_back", LIFT0 - 0.1, LIFT0 + 1.3, ease=0.25)                # his back files a complaint
act(type="spin", target="helve", axis="x", degrees=16.0, pivot=[-44, 13, 7], when=round(LIFT0, 3), until=round(LIFT0 + 0.6, 3))
act(type="spin", target="head", axis="x", degrees=16.0, pivot=[-44, 13, 7], when=round(LIFT0, 3), until=round(LIFT0 + 0.6, 3))
PROP_LIE = [-4.36, 1.79, 0.525]                                     # lying on top of the anvil, in reach
PROP_IN = [-4.3, 1.88, 0.55]                                        # stood on the anvil, under the near edge of the lifted head
act(type="hold", target="prop", hand="none", when=-1.0, until=round(LIFT0 - 0.7, 3), reach=0.05,
    keys=[dict(t=-1.0, at=PROP_LIE, rot=[0, 90, 0]), dict(t=round(LIFT0 - 0.7, 3), at=PROP_LIE, rot=[0, 90, 0])])
PROP_PUSH = [-4.22, 1.80, 0.6]                                      # as far as his arm goes; then he shoves it home
act(type="hold", target="prop", hand="R", when=round(LIFT0 - 0.35, 3), until=round(LIFT0 + 0.55, 3), reach=0.3, grip=[-0.09, 0.0, 0.05],
    keys=[dict(t=round(LIFT0 - 0.35, 3), at=PROP_LIE, rot=[0, 90, 0]), dict(t=round(LIFT0 + 0.15, 3), at=[-4.2, 1.76, 0.72], rot=[0, 30, 0]),
          dict(t=round(LIFT0 + 0.55, 3), at=PROP_PUSH, rot=[0, 8, 0])])
act(type="hold", target="prop", hand="none", when=round(LIFT0 + 0.6, 3), until=round(LIFT0 + 0.85, 3), reach=0.05,
    keys=[dict(t=round(LIFT0 + 0.6, 3), at=PROP_PUSH, rot=[0, 8, 0]), dict(t=round(LIFT0 + 0.83, 3), at=PROP_IN, rot=[0, 0, 0])])
sfx("wedge", LIFT0 + 0.83, 0.9)
face("content", LIFT0 + 0.9, LIFT0 + 2.0)
act(type="move", to=[HELVE_SPOT[0], HELVE_SPOT[1], 0.0], via=[], when=round(LIFT0 + 1.05, 3), until=round(LIFT0 + 1.6, 3))   # a step back, still facing it
QUIET0 = S_A + CAM_GAP + 0.1                                         # no more strikes from here...
# 2. the boar
T_R = LIFT0 + 1.9
BOAR_IN, BOAR_STOP = (-2.35, 0.95), (-3.3, 1.22)                     # from the south-east; stops about a metre off
sfx("rustle", T_R, 0.8)
B_ARR = T_R + 1.5
A[LOOK_H]["until"] = round(LIFT0 - 0.01, 3)                         # one look at a time
look(LIFT0 + 0.01, T_R + 0.25, pos=HAMMER_HEAD, body=True, rate=0.12)     # (re-issued after the hammer spin starts)
LOOK_B = len(A); look(T_R + 0.25, 99.0, pos=(BOAR_STOP[0], BOAR_STOP[1], 0.35), body=True, rate=0.1)
face("raised", T_R + 0.3, B_ARR + 0.2)
s, e = say("bussin", 0.0, at=B_ARR + 0.25)
pose("finger_guns", s - 0.15, e + 0.25, ease=0.15)
face("smirk", s - 0.1, e + 0.3)
HUFF = e + 0.45
CLACK, ST1, ST2 = HUFF + 0.55, HUFF + 1.0, HUFF + 1.4
s, e = say("nocap", 0.0, at=ST2 + 0.12)                             # frozen, eyes wide, blurted fast and high
FREEZE0 = s - 0.08
face("surprised", FREEZE0, 99.0, ease=0.05, set=dict(brow=1.3, lid=0.0, smile=-0.6, gz=0.0))
pose("freeze", FREEZE0, 99.0, ease=0.08)
# 3. Tobias steps out from behind the oak
T_HIDE, T_OUT, T_PULL = (OAK[0] - 0.05, OAK[1] + 0.38), (OAK[0] - 0.1, OAK[1] - 0.3), (-4.12, 2.18)
TOB_IN = e + 0.25
s, e = say("alarm", 0.0, at=TOB_IN + 0.35)
TOB_AT = TOB_IN + 1.6
s, e = say("how", 0.2)
H_WHEEL, H_CAMS, H_HAMMER = s + 0.15, s + 0.45 * D["how"], s + 0.72 * D["how"]
S_K = pair_after(e + 0.5)                                            # the strike that comes back after he pulls the prop
PULL = S_K - 0.45                                                    # the cam takes the hammer's weight from here
act(type="spin", target="helve", axis="x", degrees=-16.0, pivot=[-44, 13, 7], when=round(PULL, 3), until=round(S_K, 3))
act(type="spin", target="head", axis="x", degrees=-16.0, pivot=[-44, 13, 7], when=round(PULL, 3), until=round(S_K, 3))
PROP_OUT = [-4.0, 2.33, 0.025]                                     # tossed over his shoulder into the grass
act(type="hold", target="prop", hand="none", when=round(PULL - 0.05, 3), until=round(PULL + 0.5, 3), reach=0.05,
    keys=[dict(t=round(PULL - 0.05, 3), at=PROP_IN, rot=[0, 0, 0]), dict(t=round(PULL + 0.1, 3), at=[-4.22, 1.98, 0.68], rot=[0, 25, 0]),
          dict(t=round(PULL + 0.28, 3), at=[-4.08, 2.2, 0.62], rot=[0, 70, 0]), dict(t=round(PULL + 0.45, 3), at=PROP_OUT, rot=[0, 90, 0])])
sfx("kick", PULL, 0.8)
# (a spin steers his body toward the spinning part's origin -- for the hammer that is the world origin -- so his
#  looks are re-issued right after each hammer spin starts, keeping them in charge)
look(PULL + 0.01, 99.0, pos=(T_PULL[0], T_PULL[1], 0.7), body=False)
SKIP = [[round(QUIET0, 3), round(S_K - 0.01, 3), 0], [round(QUIET0, 3), round(S_K - 0.01, 3), 1]]
# 4. CLUNK, CLUNK -- the boar bolts
s, e = say("hate", 0.0, at=S_K + CAM_GAP + 0.35)
s, e = say("aura", 0.3)
look(s - 0.4, 99.0, obj=None, pos=(T_PULL[0], T_PULL[1], 0.6), body=True, rate=0.12)
for a in A:                                                           # he unfreezes for the compliment
    if a["type"] in ("pose", "face") and a.get("until") == 99.0 and a.get("pose", a.get("expr")) in ("freeze", "surprised"):
        a["until"] = round(s - 0.2, 3)
face("warm", s - 0.25, 99.0)
pose("admire", s - 0.1, e + 0.4, ease=0.25)
s, e = say("works", 0.25)
END = e + 0.55
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# the machine keeps running on its clock (wheel and cams turning; strikes skipped while it's propped up)
T0 = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0) / PERIOD
for name, t0 in (("wheel", T0), ("axle", T0), ("cam1", T0), ("cam2", T0 + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, skip=SKIP, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": list(HAMMER_HEAD)} if name == "head" else {}))

# ---------------------------------------------------------------- the boar and Tobias (bl_cast)
BOAR_OUT = (-2.25, 0.25)
BOAR_BACK = (-2.95, 1.02)                                            # it backs off a step when Tobias steps in
boar = dict(kind="boar", stride=0.17,
            path=[[0.0, BOAR_IN[0], BOAR_IN[1]], [round(T_R + 0.2, 3), BOAR_IN[0], BOAR_IN[1]], [round(B_ARR, 3), BOAR_STOP[0], BOAR_STOP[1]],
                  [round(TOB_AT - 0.3, 3), BOAR_STOP[0], BOAR_STOP[1]], [round(TOB_AT + 0.9, 3), BOAR_BACK[0], BOAR_BACK[1]],
                  [round(S_K + 0.35, 3), BOAR_BACK[0], BOAR_BACK[1]], [round(S_K + 1.9, 3), BOAR_OUT[0], BOAR_OUT[1]]],
            backing=[[round(TOB_AT - 0.3, 3), round(TOB_AT + 0.9, 3)]],
            yaw=[[round(B_ARR, 3), math.degrees(math.atan2(HELVE_SPOT[1] - BOAR_STOP[1], HELVE_SPOT[0] - BOAR_STOP[0]))]],
            mood=[[-1.0, "calm"], [round(HUFF - 0.02, 3), "agitated"]],
            huffs=[round(HUFF, 3), round(ST2 + 0.6, 3)], clacks=[round(CLACK, 3)], stomps=[round(ST1, 3), round(ST2, 3)],
            startle=round(S_K + 0.02, 3), visible=[round(T_R + 0.15, 3), round(S_K + 1.85, 3)])
TOB_FACE = math.degrees(math.atan2(HELVE_SPOT[1] - T_PULL[1], HELVE_SPOT[0] - T_PULL[0]))
deg = lambda p: round(math.degrees(math.atan2(p[1] - T_PULL[1], p[0] - T_PULL[0])), 1)
tobias = dict(kind="tobias", stride=0.15, seed=7,
              path=[[0.0, T_HIDE[0], T_HIDE[1]], [round(TOB_IN, 3), T_HIDE[0], T_HIDE[1]], [round(TOB_IN + 0.5, 3), T_OUT[0], T_OUT[1]],
                    [round(TOB_AT, 3), T_PULL[0], T_PULL[1]]],
              yaw=[[round(TOB_AT, 3), round(TOB_FACE, 1)], [round(H_WHEEL - 0.1, 3), deg((-5.0, 1.0))], [round(H_CAMS - 0.1, 3), deg((-4.4, 1.0))],
                   [round(H_HAMMER - 0.1, 3), deg((-4.4, 1.93))], [round(S_K + 0.6, 3), round(TOB_FACE, 1)]],
              poses=[[round(TOB_IN, 3), round(FILM + 1.0, 3), "notebook_L"],
                     [round(H_WHEEL, 3), round(H_CAMS - 0.05, 3), "point_R"], [round(H_CAMS, 3), round(H_HAMMER - 0.05, 3), "point_R"],
                     [round(PULL - 0.35, 3), round(PULL + 0.25, 3), "point_R"], [round(LS["works"] - 0.2, 3), round(FILM + 1.0, 3), "write_R"]],
              faces=[[round(TOB_IN, 3), "calm"], [round(LS["works"], 3), "deadpan"]],
              look=[[round(TOB_IN + 0.3, 3), round(TOB_AT + 0.2, 3), [HELVE_SPOT[0], HELVE_SPOT[1], 1.0]]],
              visible=[round(TOB_IN, 3), round(FILM + 1.0, 3)])
A[LOOK_B]["until"] = round(TOB_IN + 0.2, 3)
look(TOB_IN + 0.2, LS["aura"] - 0.4, pos=(T_PULL[0], T_PULL[1], 0.7), body=False)   # head only: he is still frozen

# ---------------------------------------------------------------- lines -> bl_voice
lines = []
for i, (lid, text, who) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if who:
        ln["who"] = who
    if lid == "nocap":                                              # blurted: fast and high (Character Bible)
        ln["speed"], ln["fx"] = 1.3, dict(tone=1.0, pitch=1.12, highpass=20)
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["works"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (auto-framed; every move checked, as in Scene 003)
TREES = BW.forest_trees()
def clear_air(eye):
    x, y, z = eye
    if -2.0 < x < 1.8 and -1.25 < y < 2.0 and z < 2.8:
        return False
    if -5.6 < x < -3.95 and 0.3 < y < 2.3 and z < 1.3:
        return False
    for tx, ty, h, k in TREES + [(-2.0, 0.9, 0.45, "sapling")]:
        if math.hypot(x - tx, y - ty) < (1.0 if k != "sapling" else 0.4) and z < h + 1.2:
            return False
    return z > 0.3
def solid_free(eye):
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
BLOCKERS = [((-1.72, -0.9, 0.0), (-1.6, 1.72, 2.6)), ((-1.72, 1.6, 0.0), (1.52, 1.72, 2.6)), ((-1.9, -1.1, 2.0), (1.7, 1.9, 2.9))]
for tx, ty, h, k in TREES:
    if k == "oak":
        BLOCKERS += [((tx - 0.07, ty - 0.07, 0), (tx + 0.07, ty + 0.07, h)), ((tx - 0.375, ty - 0.375, h - 0.03), (tx + 0.375, ty + 0.375, h + 0.47))]
    else:
        BLOCKERS += [((tx - 0.06, ty - 0.06, 0), (tx + 0.06, ty + 0.06, 0.5))] + [
            ((tx - w / 2, ty - w / 2, 0.45 + h * 0.28 * j - 0.01), (tx + w / 2, ty + w / 2, 0.45 + h * 0.28 * j + 0.33)) for j, w in enumerate((0.8, 0.6, 0.4, 0.2))]
def seg_hits_box(p, q, lo, hi):
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
def clutter(eye, aim, extra=()):
    f = [aim[i] - eye[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]; rn = math.hypot(r[0], r[1]); r = [v / rn for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    near = [(lo, hi) for lo, hi in list(BLOCKERS) + list(extra) if math.dist(eye, [(lo[i] + hi[i]) / 2 for i in range(3)]) < n + 1.0]
    hits = 0
    for ix in range(-3, 4):
        for iy in range(-2, 3):
            dx, dy = ix / 3 * TAN_H * 0.9, iy / 2 * TAN_V * 0.9
            q = [eye[i] + (f[i] + dx * r[i] + dy * u[i]) * n for i in range(3)]
            hits += any(seg_hits_box(eye, q, lo, hi) for lo, hi in near)
    return hits / 35.0
def los(eye, pts):
    aim = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    if clutter(eye, aim) > 0.15:
        return False
    for p in pts:
        d = math.dist(eye, p); q = [p[i] + (eye[i] - p[i]) * min(0.25, d) / d for i in range(3)]
        if any(seg_hits_box(eye, q, lo, hi) for lo, hi in BLOCKERS):
            return False
    return True
GP_BOX = ((HELVE_SPOT[0] - 0.17, HELVE_SPOT[1] - 0.17, 0.0), (HELVE_SPOT[0] + 0.17, HELVE_SPOT[1] + 0.17, 1.2))
GP_ARMS = ((HELVE_SPOT[0] - 0.38, HELVE_SPOT[1] - 0.38, 0.85), (HELVE_SPOT[0] + 0.38, HELVE_SPOT[1] + 0.38, 1.25))   # arms up when frozen
BOAR_BOX = ((BOAR_STOP[0] - 0.36, BOAR_STOP[1] - 0.3, 0.0), (BOAR_STOP[0] + 0.36, BOAR_STOP[1] + 0.3, 0.72))
BOAR_BOX2 = ((BOAR_BACK[0] - 0.36, BOAR_BACK[1] - 0.3, 0.0), (BOAR_BACK[0] + 0.36, BOAR_BACK[1] + 0.3, 0.72))
TOB_BOX = ((T_PULL[0] - 0.12, T_PULL[1] - 0.12, 0.0), (T_PULL[0] + 0.12, T_PULL[1] + 0.12, 0.85))
def inside(p, box, m=0.02):
    return all(box[0][i] - m <= p[i] <= box[1][i] + m for i in range(3))
def make_los(cast, clutter_cast=()):                                 # the cast block the view too (but not their own points)
    def f(eye, pts):
        if not los(eye, pts):
            return False
        if clutter_cast:                                            # ...and no cast member looms in the foreground
            aim = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
            own = [b for b in clutter_cast if any(inside(p, b) for p in pts)]
            if clutter(eye, aim, [b for b in clutter_cast if b not in own]) - clutter(eye, aim) > 0.08:
                return False
        return not any(seg_hits_box(eye, p, *b) for p in pts for b in cast if not inside(p, b))
    return f
def facing(pos, heading_deg, max_deg):                               # the camera stands in front of this face
    def f(eye):
        a = math.degrees(math.atan2(eye[1] - pos[1], eye[0] - pos[0])) - heading_deg
        return abs((a + 180) % 360 - 180) <= max_deg
    return f
def both(*fs):
    return lambda eye: all(f(eye) for f in fs)
G_TO_BOAR = math.degrees(math.atan2(BOAR_STOP[1] - HELVE_SPOT[1], BOAR_STOP[0] - HELVE_SPOT[0]))
G_TO_TOB = math.degrees(math.atan2(T_PULL[1] - HELVE_SPOT[1], T_PULL[0] - HELVE_SPOT[0]))
def g_at(t):                                                        # Grandpa's position (straight-line legs of his walk)
    pts = [tuple(G0[:2])] + WALK_VIA + [LIFT_SPOT]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]; T_ = 2.1 / sum(seg); t0 = 0.3; legs = []
    for a, b, d in zip(pts, pts[1:], seg):
        legs.append((t0, t0 + d * T_, a, b)); t0 += d * T_
    pos = G0[:2]
    for t0, t1, a, b in legs:
        if t >= t1: pos = b
        elif t > t0:
            u = (t - t0) / (t1 - t0); pos = [a[i] + (b[i] - a[i]) * u for i in range(2)]
    if t >= LIFT0 + 1.05:
        u = min(1.0, (t - LIFT0 - 1.05) / 0.55); pos = [LIFT_SPOT[i] + (HELVE_SPOT[i] - LIFT_SPOT[i]) * u for i in range(2)]
    return pos
def who_at(t):
    return gp(*g_at(t))
def kid(x, y):
    return [(x, y, 0.05), (x, y, 0.45), (x, y, 0.80)]
B_HEAD_DEG = math.degrees(math.atan2(HELVE_SPOT[1] - BOAR_STOP[1], HELVE_SPOT[0] - BOAR_STOP[0]))
def boar_pts(x, y):                                                 # nose, middle and rump: all of it in frame
    c, s_ = math.cos(math.radians(B_HEAD_DEG)), math.sin(math.radians(B_HEAD_DEG))
    return [(x, y, 0.1), (x, y, 0.62), (x + 0.48 * c, y + 0.48 * s_, 0.3), (x - 0.42 * c, y - 0.42 * s_, 0.35)]
last = C3["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
H = HELVE_SPOT
L_G = make_los([GP_BOX, GP_ARMS])                                             # before the boar / Tobias are there
L_GB = make_los([GP_BOX, GP_ARMS, BOAR_BOX])
L_ALL = make_los([GP_BOX, GP_ARMS, BOAR_BOX, TOB_BOX])
L_GT = make_los([GP_BOX, GP_ARMS, TOB_BOX])
L_LESSON = make_los([GP_BOX, GP_ARMS, TOB_BOX, BOAR_BOX2], clutter_cast=[BOAR_BOX2])
L_ALL2 = make_los([GP_BOX, GP_ARMS, BOAR_BOX2, TOB_BOX])
BOAR_HEAD = (BOAR_STOP[0] + 0.4 * math.cos(math.radians(B_HEAD_DEG)), BOAR_STOP[1] + 0.4 * math.sin(math.radians(B_HEAD_DEG)), 0.4)
SHOTS = [
    lambda: auto_frame(LIFT0 + 0.2, gp(*H) + [HAMMER_HEAD, PROP_IN, (PROP_IN[0], PROP_IN[1], 0.5)], (-4.25, 1.75, 0.6), 20, 16, 1.9, clear_air, prev=cam, path_clear=solid_free, los=L_G, who=who_at),
    lambda: auto_frame(B_ARR - 0.3, gp(*H) + boar_pts(*BOAR_STOP), (-3.7, 1.45, 0.55), 20, 12, 2.4,
                       both(clear_air, facing(H, G_TO_BOAR, 75)), prev=cam, path_clear=solid_free, los=L_GB, who=who_at),
    lambda: auto_frame(LS["nocap"] - 0.1, gp(*H) + [BOAR_HEAD], (-3.9, 1.5, 0.75), 20, 8, 1.7,
                       both(clear_air, facing(H, G_TO_BOAR, 50)), prev=cam, path_clear=solid_free, los=L_GB, who=who_at),
    lambda: auto_frame(TOB_AT, gp(*H) + boar_pts(*BOAR_STOP) + kid(*T_PULL), (-3.8, 1.7, 0.5), 10, 14, 2.6, clear_air, prev=cam, path_clear=solid_free, los=L_ALL, who=who_at),
    lambda: auto_frame(H_CAMS, kid(*T_PULL) + [(-5.0, 1.0, 0.55), (-4.4, 1.0, 0.5), HAMMER_HEAD], (-4.5, 1.6, 0.5), 10, 18, 2.2,
                       both(clear_air, facing(T_PULL, deg((-4.4, 1.0)), 80)), prev=cam, path_clear=solid_free, los=L_LESSON),   # cutaway
    lambda: auto_frame(S_K, gp(*H) + kid(*T_PULL) + boar_pts(*BOAR_BACK), (-3.65, 1.6, 0.5), 10, 14, 2.8, clear_air, prev=cam, path_clear=solid_free, los=L_ALL2, who=who_at),
    lambda: auto_frame(LS["aura"] + 0.3, gp(*H) + kid(*T_PULL), (-4.12, 1.9, 0.6), 25, 12, 1.8,
                       both(clear_air, facing(H, G_TO_TOB, 85)), prev=cam, path_clear=solid_free, los=L_GT, who=who_at),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
cam, PATCHED = fix_path(cam, clear_air, who_at, path_clear=solid_free)
ks = [k["at"] for k in cam]
cuts = [t for t in ks if any(abs(t - u - 1.0 / FPS) < 1e-3 for u in ks)]                    # keys that start a hard cut
c0 = min(cuts, key=lambda t: abs(t - H_CAMS))                                                   # the cut into the cutaway
c1 = min([t for t in cuts if t > c0 + 0.5] or [S_K])                                            # and the cut out of it
assert abs(c0 - H_CAMS) < 0.1, ("the cutaway should start with a cut", c0, H_CAMS)
CUTAWAYS = [[round(c0, 3), round(c1 + 1.0 / FPS, 3)]]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C3["overlay"]["live_viewers"]]]),
         dict(style="panel", y=170, border="amber", when=round(LS["how"] + 0.2, 3), until=round(LE["hate"] + 0.2, 3), rows=[
             dict(text="WATER-POWERED BOAR SCARER", color="white", at=round(LS["how"] + 0.3, 3), size=40),
             dict(text="like Japan's shishi-odoshi", color="cyan", at=round(S_K + 0.7, 3), size=36)])]
W4 = {k: v for k, v in S3["world"].items() if k not in ("leaves", "clouds_pass", "critters")}
W4["critters"] = [boar, tobias]
story = dict(title="No Cap, Chat!", slug="grandpa_ep01_scene004", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["bussin"], tail=round(tail, 4), seed=17, blink=True, target_duration=30,
             engine_rev=3, scene=dict(episode=1, scene=4, name="No Cap, Chat!", previous="ep01_scene003", next="ep01_scene005"),
             world=W4, lines=lines, grandpa=dict(start=list(G0), outfit=S3["grandpa"]["outfit"]),
             poses=dict(S3["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["webcam", "rock"]], frame_points=["hat", "face", "chest"],
                     cutaways=CUTAWAYS,
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene004.json", "w"), indent=1)
print("film %.2f s; first pairs %s" % (FILM, PAIRS[:6]))
for lid, _, who in LINES:
    print("  %-7s %-7s %6.2f-%6.2f" % (lid, who or "grandpa", LS[lid], LE[lid]))
print("lift %.2f quiet %.2f rustle %.2f boar %.2f huff %.2f stomps %.2f/%.2f tobias %.2f-%.2f pull %.2f CLUNK %.2f" %
      (LIFT0, QUIET0, T_R, B_ARR, HUFF, ST1, ST2, TOB_IN, TOB_AT, PULL, S_K))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
