"""Grandpa's Block Lab, Episode 1, Scene 007 -- "The Fence" (16:9, ~45 s). Approved (2026-10-21): the split's first half.
Grandpa solo. Starts from Scene 006's end at Tobias's bench. Tobias's garden is in the boar's woods, so Grandpa builds him a
safe one out in the open meadow by the cabin (seedlings move in later). Rule 2: the webcam (and the book) come along; the
webcam goes back on the Scene 003 bank stone (Rule 1). Across the stepping stones ("My knees remember this."), page twelve,
then the fence, side by side ("Post. Rail. Post. Rail. Chat, this is my cardio."). A rustle in the woods across the stream:
"...Nope. Faster." -- the last two sides go up twice as fast. Cliffhanger: "Chat... gate. NOW." (Scene 008 builds the gate.)
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both
from forest_camkit import make_los as _make_los
FPS = 30
S6 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene006.json"))
C6 = json.load(open(os.path.join(HERE, "s6work/build/continuity.json")))
F6 = C6["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 006 left it
def root_of(name):
    r = C6["structures"][name]["root"]
    return [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)], round(math.degrees(math.atan2(r[1][0], r[0][0])), 2)
for name, st in S6["structures"].items():
    if C6["structures"][name]["blocks_standing"] == 0:
        continue
    S[name] = json.loads(json.dumps(st))
PROP_OUT = root_of("prop")[0]
CAM0, CAM0_YAW = root_of("webcam")
BOOK0 = root_of("book")[0]; PAGES0 = root_of("pages")[0]
for name in ("webcam", "cam_cap", "book", "pages"):                 # the holds place them
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
ROCK_TOP = 0.10                                                     # the Scene 003 bank stone, (-3.75, 1.25)
# ---------------------------------------------------------------- the fence: a 1.5 m square in the meadow (x -3.8..-2.3, y 1.5..3.0)
PX, PY = (-38, -33, -28, -23), (15, 20, 25, 30)                     # post lines (cells); the gate gap: south side, x -33..-28
GAP = range(-32, -28)
def posts(cells): return dict(cells=[[x, y, z] for x, y in cells for z in range(5)], at=[0.0, 0.0, 0.0], centered=False,
                              material="wood", block_shape=[0.6, 0.6, 1], expect_blocks=5 * len(cells))
def rails(cells, along):
    return dict(cells=[[x, y, z] for x, y in cells for z in (1, 3)], at=[0.0, 0.0, 0.0], centered=False, material="planks",
                block_shape=[1, 0.35, 0.5] if along == "x" else [0.35, 1, 0.5], expect_blocks=2 * len(cells))
SIDES = {
    "s": ([(x, 15) for x in PX], [(x, 15) for x in range(-37, -23) if x not in PX and x not in GAP], "x"),
    "w": ([(-38, y) for y in PY[1:]], [(-38, y) for y in range(16, 30) if y not in PY], "y"),
    "n": ([(x, 30) for x in PX[1:]], [(x, 30) for x in range(-37, -23) if x not in PX], "x"),
    "e": ([(-23, y) for y in PY[1:-1]], [(-23, y) for y in range(16, 30) if y not in PY], "y"),
}
for k, (pc, rc, along) in SIDES.items():
    S["fence_posts_" + k] = posts(pc)
    S["fence_rails_" + k] = rails(rc, along)
FENCE_BOXES = [((-3.84, 1.46, 0.0), (-2.26, 1.54, 0.5)), ((-3.84, 1.46, 0.0), (-3.76, 3.04, 0.5)),
               ((-3.84, 2.96, 0.0), (-2.26, 3.04, 0.5)), ((-2.34, 1.46, 0.0), (-2.26, 3.04, 0.5))]
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]
LEAN_BOXES = [((-6.57, 1.13, 1.39), (-5.73, 1.97, 1.51)), ((-6.53, 1.27, 0.0), (-6.47, 1.33, 1.5)), ((-5.83, 1.27, 0.0), (-5.77, 1.33, 1.5)),
              ((-6.53, 1.77, 0.0), (-6.47, 1.83, 1.5)), ((-5.83, 1.77, 0.0), (-5.77, 1.83, 1.5)), ((-6.4, 1.55, 0.0), (-5.9, 1.75, 0.5))]
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE + LEAN_BOXES, **kw)
def boxes_free(eye):
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in LEAN_BOXES + FENCE_BOXES)
AIR = both(clear_air, boxes_free)
PATH = both(solid_free, boxes_free)

# ---------------------------------------------------------------- lines
LINES = [("plan", "Chat, Tobias's garden is right where the boar lives. So... we're building him a safe one. Out in the open, by my cabin.", None,
          "Chat, Tobias's garden is right where the boar livs. So... we're building him a safe one. Out in the open, by my cabin."),
         ("seed", "Then we move his seedlings in. The ones the boar left.", None, None),
         ("knees", "My knees remember this.", None, None),
         ("page", "A garden fence. With a lever gate.", None, None),
         ("cardio", "Post. Rail. Post. Rail. Chat, this is my cardio.", None, None),
         ("faster", "...Nope. Faster.", 1.0, None),
         ("now", "Chat... gate. NOW.", None, None)]
GUESS = dict(plan=7.9, seed=3.5, knees=1.6, page=2.5, cardio=3.9, faster=1.3, now=1.8)
dur_file = os.path.join(HERE, "ep01_s007_durations.json")
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
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)
def walk(t0, t1, to, via=()):
    act(type="move", to=[to[0], to[1], 0.0], via=[[v[0], v[1], 0.0] for v in via], when=t0, until=t1, face="path")
def build(name, t0, t1, at, order):
    act(type="build", target=name, when=t0, until=t1, stand_at=[at[0], at[1], 0.0], order=order)

POSES = {
    "pick_up": dict(lean=0.25),
    "set_down": dict(lean=0.55, hips=[0.0, 0.0, -0.06]),
    "wobble_a": dict(hand_L=dict(char=(0.46, -0.04, 0.92)), twist=0.14, lean=-0.06),
    "wobble_b": dict(hand_L=dict(char=(0.42, 0.02, 1.02)), twist=-0.14, lean=0.04),
    "peer_down": dict(lean=0.18, head=(0.0, -0.22, 0.0)),
    "freeze": dict(shrug=0.5, elbows=0.2, lean=-0.05),
    "pant": dict(lean=0.22, hips=[0.0, 0.0, -0.03], hand_R={"char": [-0.15, -0.1, 0.52]}),    # a hand on his knee (the book's in the other)
}
CARRY = {"char": [-0.17, -0.18, 0.40]}
BOOK_CARRY_B = {"char": [0.17, -0.2, 0.80]}                          # the book held open in front (left hand)
BOOK_CARRY_P = {"char": [0.17, -0.2, 0.81]}
G0 = C6["grandpa"]["root"][:2]                                      # (-6.15, 1.33) at the bench
G_PICK = (-6.22, 1.42)
OUT_VIA = [(-6.16, 1.08), (-5.58, 0.98), (-5.4, 1.45), (-5.41, 1.95), (-5.43, 2.42)]
STONES = [(-5.18, 2.45), (-4.98, 2.45), (-4.7, 2.45)]
ACROSS = [(-4.4, 2.45), (-3.9, 2.6), (-3.25, 2.0), (-3.25, 0.88)]   # off the stones, north of the machine, through the empty plot
P_SET = (-3.74, 0.93)                                               # Scene 003's spot: the bank stone just ahead
CUBE = (-3.75, 1.25)
CAM_YAW = round(math.degrees(math.atan2(-3.05 - CUBE[0], -(2.25 - CUBE[1]))), 2)   # lens (local -y) into the plot
rotz = lambda v, a: (v[0] * math.cos(math.radians(a)) - v[1] * math.sin(math.radians(a)), v[0] * math.sin(math.radians(a)) + v[1] * math.cos(math.radians(a)))
_o = rotz((0.0, -0.1), CAM_YAW)
CAM_ROOT = [round(CUBE[0] - _o[0], 4), round(CUBE[1] - _o[1], 4), round(ROCK_TOP - 0.30, 3)]
STAND = {"s": (-3.05, 1.16), "w": (-4.09, 2.6), "n": (-3.05, 3.36), "e": (-1.98, 2.25)}   # outside each side, facing it
face("smile", -5.0, 0.4, set=dict(C6["grandpa"]["face"]))
act(type="face_camera", when=-5.0, until=0.3)

# 1. the plan -- and Rule 2: the webcam and the book come along
walk(0.05, 0.6, G_PICK)
PICK = 1.1
pose("pick_up", PICK - 0.5, PICK + 0.4, ease=0.3)
cam_holds, book_holds = [], []
for name in ("webcam", "cam_cap"):
    cam_holds.append(len(A))
    act(type="hold", target=name, hand="R", when=round(PICK - 0.3, 3), until=99.0, reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CAM0, rot=[0, 0, CAM0_YAW]), dict(t=PICK, at=CAM0, rot=[0, 0, CAM0_YAW]), dict(t=round(PICK + 0.6, 3), at=CARRY, rot=[0, 0, 0])])
for name, r0, carry in (("book", BOOK0, BOOK_CARRY_B), ("pages", PAGES0, BOOK_CARRY_P)):
    book_holds.append(len(A))
    act(type="hold", target=name, hand="L", when=round(PICK - 0.2, 3), until=99.0, reach=0.3, grip=[0.0, -0.07, 0.09],
        keys=[dict(t=-1.0, at=r0, rot=[0, 0, 0]), dict(t=round(PICK + 0.1, 3), at=r0, rot=[0, 0, 0]), dict(t=round(PICK + 0.7, 3), at=carry, rot=[0, 0, 0])])
look(PICK - 0.6, PICK + 0.4, pos=(-6.25, 1.68, 0.55), body=False)
s, e = say("plan", 0.0, at=PICK + 0.6)
act(type="face_camera", when=round(s - 0.1, 3), until=round(s + 4.0, 3))
face("worried", s + 0.3, s + 2.4, set=dict(brow=0.8))
face("smile", s + 2.6, e + 0.3)
WALK0 = s + 4.2
WALK1 = WALK0 + 4.4
walk(WALK0, WALK1, OUT_VIA[-1], via=OUT_VIA[:-1])
s, e = say("seed", 0.4)
face("warm", s, e + 0.3)
# 2. back over the stepping stones (wobbling); round the machine to the bank stone
ST0 = WALK1
ST1 = ST0 + 2.0
walk(ST0, ST1, STONES[-1], via=STONES[:-1])
for k in range(int((ST1 - ST0) / 0.35)):
    pose("wobble_a" if k % 2 == 0 else "wobble_b", ST0 + 0.35 * k, ST0 + 0.35 * (k + 1) + 0.15, ease=0.12)
s, e = say("knees", 0.0, at=ST0 + 0.3)
face("worried", s - 0.2, e + 0.3)
AC0 = ST1 + 0.05
AC1 = AC0 + 2.6
walk(AC0, AC1, P_SET, via=ACROSS)
# 3. the webcam goes back on the bank stone (Rule 2); the book stays open in his left hand -- he builds from the plan
SET_T = AC1 + 0.55
look(AC1 - 0.4, SET_T + 0.3, pos=(CUBE[0], CUBE[1], 0.1), body=True, rate=0.18)
pose("set_down", SET_T - 0.55, SET_T + 0.45, ease=0.3)
for i in cam_holds:
    A[i]["until"] = round(SET_T, 3)
    A[i]["keys"] += [dict(t=round(SET_T - 0.5, 3), at=CARRY, rot=[0, 0, 0]), dict(t=round(SET_T, 3), at=CAM_ROOT, rot=[0, 0, CAM_YAW])]
sfx("settle", SET_T - 0.05, 0.4)
sfx("page", SET_T + 0.7, 0.6)
s, e = say("page", 0.3, at=SET_T + 0.9)
look(s - 0.3, e + 0.2, obj="book", body=False)
pose("peer_down", s - 0.2, e, ease=0.3)
face("raised", s + 0.6, e + 0.3, set=dict(smile=0.5))
# 4. the fence: south side, then west -- "Post. Rail. Post. Rail."
B0 = e + 0.4
walk(B0, B0 + 0.9, STAND["s"], via=[(-3.4, 1.05)])
T = B0 + 1.0
look(T - 0.2, T + 4.2, pos=(-3.05, 1.5, 0.25), body=True, rate=0.2)
build("fence_posts_s", T, T + 1.8, STAND["s"], "x"); build("fence_rails_s", T + 1.85, T + 3.6, STAND["s"], "x"); T += 3.65
s, e = say("cardio", 0.0, at=B0 + 1.4)
face("smirk", s + 2.0, e + 0.3)
walk(T, T + 1.8, STAND["w"], via=[(-3.3, 0.82), (-4.12, 0.85), (-4.06, 1.45), (-3.98, 1.75), (-3.98, 2.25)])   # round the bank stone, past the anvil
T += 1.9
look(T - 0.2, T + 3.0, pos=(-3.8, 2.25, 0.25), body=True, rate=0.2)
build("fence_posts_w", T, T + 1.3, STAND["w"], "y"); build("fence_rails_w", T + 1.35, T + 2.8, STAND["w"], "y"); T += 2.85
# 5. a rustle across the stream. He freezes. "...Nope. Faster."
RUSTLE = T + 0.2
sfx("rustle", RUSTLE, 0.8)
look(RUSTLE + 0.15, RUSTLE + 1.9, pos=(-6.3, 3.4, 0.6), body=False, rate=0.4)
pose("freeze", RUSTLE + 0.1, RUSTLE + 2.0, ease=0.12)
face("surprised", RUSTLE + 0.15, RUSTLE + 1.9, set=dict(brow=1.2, smile=0.0))
s, e = say("faster", 0.0, at=RUSTLE + 1.3)
face("alert", s, e + 0.4, set=dict(brow=-0.3))
T = e + 0.15                                                        # twice as fast now: north, then east
walk(T, T + 1.2, STAND["n"], via=[(-4.35, 2.75), (-4.35, 3.35), (-3.9, 3.42)])   # round the oak
T += 1.25
look(T - 0.2, T + 1.6, pos=(-3.05, 3.0, 0.25), body=True, rate=0.3)
build("fence_posts_n", T, T + 0.7, STAND["n"], "x"); build("fence_rails_n", T + 0.72, T + 1.5, STAND["n"], "x"); T += 1.55
walk(T, T + 0.8, STAND["e"], via=[(-2.0, 3.48)])
T += 0.85
look(T - 0.2, T + 1.6, pos=(-2.3, 2.25, 0.25), body=True, rate=0.3)
build("fence_posts_e", T, T + 0.6, STAND["e"], "y"); build("fence_rails_e", T + 0.62, T + 1.3, STAND["e"], "y"); T += 1.35
# 6. the gap where the gate goes -- cliffhanger
G_GAP = (-3.05, 1.05)
walk(T, T + 1.0, G_GAP, via=[(-1.98, 1.2), (-2.6, 1.02)])
pose("pant", T + 1.0, T + 2.0, ease=0.25)
look(T + 0.9, T + 2.0, pos=(-3.05, 1.5, 0.3), body=True, rate=0.25)
act(type="face_camera", when=round(T + 2.0, 3), until=99.0)
s, e = say("now", 0.0, at=T + 2.1)
face("alert", s - 0.2, 99.0, set=dict(brow=-0.4, smile=0.0))
END = e + 0.8
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# the machine keeps its clock; the prop stays put
PERIOD, CAM_GAP = 3.3, 0.55
TRIP6 = [a for a in S6["actions"] if a["type"] == "trip"][0]
FIRST = TRIP6["first"] - F6
FIRST = round(FIRST + PERIOD * math.ceil(-FIRST / PERIOD) - PERIOD, 4)
T0_ = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": [-4.4, 1.95, 0.6]} if name == "head" else {}))
act(type="hold", target="prop", hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
    keys=[dict(t=-1.0, at=PROP_OUT, rot=[0, 90, 0]), dict(t=round(FILM + 1.0, 3), at=PROP_OUT, rot=[0, 90, 0])])

lines = []
for i, (lid, text, speed, speak) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if speed: ln["speed"] = speed
    if speak: ln["speak"] = speak
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["now"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)); out.append([tt, p[0], p[1]])
    return out
STOPS = [(0.0, tuple(G0))]
pos_now = tuple(G0)
for a in sorted([a for a in A if a["type"] in ("move", "build")], key=lambda a: a["when"]):
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
def box_at(p, r=0.17, h=1.2):
    return ((p[0] - r, p[1] - r, 0.0), (p[0] + r, p[1] + r, h))
FENCE_PTS = [(-3.8, 1.5, 0.05), (-2.3, 1.5, 0.5), (-3.8, 3.0, 0.5), (-2.3, 3.0, 0.05)]
last = C6["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
SHOTS = [
    # leaving the workshop, along the bank: he walks toward us
    lambda: auto_frame(WALK0 + 1.2, gp(*OUT_VIA[3]), (-5.5, 2.8, 0.6), 80, 8, 2.6, AIR, prev=cam, path_clear=PATH, los=make_los([]), who=who_at),
    # the stepping stones
    lambda: auto_frame(ST0 + 0.3, gp(*STONES[1]) + gp(*STONES[-1])[1:], (-4.95, 2.45, 0.55), 70, 8, 3.4, AIR, prev=cam, path_clear=PATH,
                       los=make_los([]), who=who_at),
    # the bank stone and the stump; page twelve
    lambda: auto_frame(AC0 + 1.2, gp(*P_SET) + [(CUBE[0], CUBE[1], 0.1)], (-3.7, 1.1, 0.55), 90, 8, 3.0,
                       AIR, prev=cam, path_clear=PATH, los=make_los([box_at(P_SET)]), who=who_at),
    # the fence going up: the whole meadow plot
    lambda: auto_frame(B0 + 1.2, gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4), 100, 8, 3.4, AIR, prev=cam, path_clear=PATH,
                       los=make_los([]), who=who_at),
    lambda: auto_frame(RUSTLE + 0.3, gp(*STAND["w"])[1:] + [(-3.8, 1.6, 0.4), (-3.8, 2.9, 0.4)], (-3.95, 2.45, 0.8), 50, 8, 2.4, AIR,
                       prev=cam, path_clear=PATH, los=make_los([box_at(STAND["w"])]), who=who_at),     # the freeze: his face
    lambda: [dict(cam[-1], at=round(math.ceil((LE["faster"] + 0.1) * FPS - 1e-6) / FPS - 1.0 / FPS, 4)),      # a hard cut: the race is on
             auto_frame(math.ceil((LE["faster"] + 0.1) * FPS - 1e-6) / FPS, gp(*STAND["n"]) + gp(*STAND["e"]) + FENCE_PTS, (-3.0, 2.25, 0.4),
                        110, 8, 4.0, AIR, los=make_los([]))],
    # the gap -- "Chat... gate. NOW."
    lambda: auto_frame(LS["now"] - 0.4, gp(*G_GAP) + [(-3.3, 1.5, 0.45), (-2.8, 1.5, 0.45)], (-3.05, 1.3, 0.75), 90, 8, 2.8, AIR,
                       prev=cam, path_clear=PATH, los=make_los([box_at(G_GAP)]), who=who_at),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C6["overlay"]["live_viewers"]]])]
W7 = {k: v for k, v in S6["world"].items() if k != "critters"}
W7["critters"] = []
story = dict(title="The Fence", slug="grandpa_ep01_scene007", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["plan"], tail=round(tail, 4), seed=31, blink=True, target_duration=45,
             engine_rev=3, scene=dict(episode=1, scene=7, name="The Fence", previous="ep01_scene006", next="ep01_scene008"),
             world=W7, lines=lines, grandpa=dict(start=list(G0), outfit=S6["grandpa"]["outfit"]),
             poses=dict(S6["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"], ["webcam", "rock"]],
                     frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve", "lean_posts", "bench_legs"]
                           + ["fence_posts_" + k for k in SIDES]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene007.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("walk %.2f-%.2f stones %.2f-%.2f set %.2f fence %.2f rustle %.2f" % (WALK0, WALK1, ST0, ST1, SET_T, B0, RUSTLE))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
