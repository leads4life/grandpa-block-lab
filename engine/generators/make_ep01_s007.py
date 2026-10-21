"""Grandpa's Block Lab, Episode 1, Scene 007 -- "Leverage" (16:9, ~60 s). Approved beat sheet (2026-10-21).
Blueprint Build, Grandpa solo (Tobias is an occasional visitor, not in 007-010). Starts from Scene 006's end at the bench.
Rule 2: he takes the webcam (and the book) to the build spot and sets them down. The ritual: find, build, oops, why, fix,
button. He builds the lever gate on the garden's north side: two guide posts, a plank panel, a beam over it on a stone
fulcrum, a counterweight. Oops: the fulcrum is by his hands -- the push does nothing. Why: the page draws it by the gate
(lesson: LEVER). Fix: he slides it over; one finger lifts the gate. Feelings beat (no slang). Hook: a bottle drifts down
the stream -- page thirteen? Slang woven in where the moment calls, always a bit wrong.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, facing, both
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
CAM0, CAM0_YAW = root_of("webcam")                                  # on the bench's west end
BOOK0 = root_of("book")[0]; PAGES0 = root_of("pages")[0]
for name in ("webcam", "cam_cap", "book", "pages"):                 # the holds place them
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
# two flat stones by the build spot: one for the webcam, one to prop the book open on
S["cam_stone"] = dict(cells=[[-61, 40, 0], [-60, 40, 0], [-61, 41, 0], [-60, 41, 0]], at=[0.0, 0.0, 0.0], centered=False, material="stone",
                      block_shape=[1, 1, 0.8], expect_blocks=4, prebuilt=True)
S["book_stone"] = dict(cells=[[-58, 45, 0], [-57, 45, 0], [-58, 46, 0], [-57, 46, 0]], at=[0.0, 0.0, 0.0], centered=False, material="stone",
                       block_shape=[1, 1, 0.8], expect_blocks=4, prebuilt=True)
STONE_TOP = 0.08
# the lever gate (built on camera): at the garden's north opening (y 2.9)
S["gate_posts"] = dict(cells=[[x, 29, z] for x in (-62, -57) for z in range(7)], at=[0.0, 0.0, 0.0], centered=False, material="wood",
                       block_shape=[0.6, 0.6, 1], expect_blocks=14, stand="front")
S["gate"] = dict(cells=[[x, 29, z] for x in range(-61, -57) for z in range(4)], at=[0.0, 0.0, 0.0], centered=False, material="planks",
                 block_shape=[1, 0.35, 1], expect_blocks=16,
                 extras=[dict(c=[-6.0, 2.9, 0.45], s=[0.01, 0.01, 0.1], m="wood")])      # the rope up to the beam
S["beam"] = dict(cells=[[-60, y, 5] for y in range(29, 40)], at=[0.0, 0.0, 0.0], centered=False, material="planks",
                 block_shape=[0.5, 1, 1], expect_blocks=11)
S["fulcrum"] = dict(cells=[[-60, 37, z] for z in range(5)], at=[0.0, 0.0, 0.0], centered=False, material="stone",
                    block_shape=[0.8, 0.8, 1], expect_blocks=5)
S["weight"] = dict(cells=[[-60, 38, 6]], at=[0.0, 0.0, 0.0], centered=False, material="stone", block_shape=[0.9, 0.9, 1], expect_blocks=1)
PIVOT = [-60, 32, 4.5]                                              # the fulcrum's top, once it is slid under y 3.2
SWING = -28.0                                                       # his end goes down, the gate end comes up
LIFT = round(0.3 * math.sin(math.radians(-SWING)), 3)               # load arm 0.3 m
# the bottle (hook): drifts down the stream with a rolled page inside
S["bottle"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="glass", block_shape=[0.9, 2.2, 0.9], expect_blocks=1,
                   extras=[dict(c=[0.0, 0.118, 0.055], s=[0.045, 0.03, 0.045], m="wood"),                    # cork
                           dict(c=[0.0, 0.0, 0.056], s=[0.05, 0.16, 0.05], m="paper")])                    # the rolled page
STREAM_X = lambda y: -5.2 + 0.25 * math.sin(0.7 * y)
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]
LEAN_BOXES = [((-6.57, 1.13, 1.39), (-5.73, 1.97, 1.51)), ((-6.53, 1.27, 0.0), (-6.47, 1.33, 1.5)), ((-5.83, 1.27, 0.0), (-5.77, 1.33, 1.5)),
              ((-6.53, 1.77, 0.0), (-6.47, 1.83, 1.5)), ((-5.83, 1.77, 0.0), (-5.77, 1.83, 1.5)), ((-6.4, 1.55, 0.0), (-5.9, 1.75, 0.5))]
GATE_BOXES = [((-6.24, 2.87, 0.0), (-6.16, 2.93, 0.7)), ((-5.74, 2.87, 0.0), (-5.66, 2.93, 0.7)), ((-6.15, 2.88, 0.0), (-5.75, 2.92, 0.4)),
              ((-6.03, 2.85, 0.5), (-5.97, 3.95, 0.6))]
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE + LEAN_BOXES, **kw)
def lean_free(eye):
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in LEAN_BOXES + GATE_BOXES)
AIR = both(clear_air, lean_free)
PATH = both(solid_free, lean_free)

# ---------------------------------------------------------------- lines
LINES = [("field", "Chat, we're going on a field trip. Ten feet. Very exciting.", None),
         ("page", "Page twelve. A gate. With a lever. How hard can it be?", None),
         ("dont", "...Don't answer that.", None),
         ("squares", "Three squares... three blocks.", None),
         ("vibes", "And a rock. For... vibes.", None),
         ("giving", "This gate is NOT... giving.", None),
         ("drawn", "Wait. The pivot's drawn way over here. By the gate.", None),
         ("lesson", "The farther you push from the pivot, the less push you need.", None),
         ("archi", "Old Archimedes said, give him a long enough lever and he'd move the world. I just want to move a gate.", None),
         ("rizz", "Ohhh. Now THAT'S got... rizz.", None),
         ("scared", "Being scared's normal. Building something... helps.", 0.88),
         ("tobias", "Don't tell Tobias I said that.", None),
         ("bottle", "...Is that... page thirteen?", None)]
GUESS = dict(field=3.4, page=3.4, dont=1.2, squares=1.9, vibes=1.8, giving=2.0, drawn=3.0, lesson=3.4, archi=5.6, rizz=2.2,
             scared=3.4, tobias=1.6, bottle=1.9)
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
def build(name, t0, t1, at, order="z"):
    act(type="build", target=name, when=t0, until=t1, stand_at=[at[0], at[1], 0.0], order=order)

BEAM_END = (-6.0, 3.86, 0.62)
DOWN_END = (-6.0, 3.2 + 0.66 * math.cos(math.radians(SWING)), 0.55 + 0.66 * math.sin(math.radians(SWING)) + 0.06)
POSES = {
    "pick_up": dict(lean=0.25),
    "set_down": dict(lean=0.5, hips=[0.0, 0.0, -0.06]),
    "strain": dict(lean=0.42, hips=[0.0, 0.0, -0.04], shrug=0.4, hand_R={"world": list(BEAM_END)}, hand_L={"world": [BEAM_END[0] + 0.1, BEAM_END[1], BEAM_END[2]]}),
    "strain_b": dict(lean=0.5, hips=[0.0, 0.0, -0.06], shrug=0.6, hand_R={"world": list(BEAM_END)}, hand_L={"world": [BEAM_END[0] + 0.1, BEAM_END[1], BEAM_END[2]]}),
    "peer_down": dict(lean=0.35, head=(0.0, -0.22, 0.0)),
    "push_low": dict(lean=0.55, hips=[0.0, 0.0, -0.12], hand_R={"char": [-0.16, -0.06, 0.32]}, hand_L={"char": [-0.05, -0.12, 0.32]}),
    "finger_top": dict(lean=0.2, hand_R={"world": list(BEAM_END)}),
    "finger_dn": dict(lean=0.38, hand_R={"world": [round(v, 3) for v in DOWN_END]}),
    "proud": dict(lean=-0.08, hand_L={"char": [0.18, -0.08, 0.6]}),           # hands on hips-ish
    "dreamy": dict(head=(0.0, 0.12, 0.08), lean=-0.03),
}
CARRY = {"char": [-0.17, -0.18, 0.40]}                             # the webcam, as in Scenes 002-006
BOOK_CARRY_B = {"char": [0.21, -0.06, 0.43]}                         # the book, tucked under his left arm
BOOK_CARRY_P = {"char": [0.21, -0.06, 0.44]}
G0 = C6["grandpa"]["root"][:2]                                      # (-6.15, 1.33) at the bench
G_SET = (-5.74, 4.16)                                               # between the two stones
G_BUILD = (-5.62, 3.35)
G_PUSH = (-5.78, 4.14)                                              # at the beam's end, facing the gate (south)
G_BOOK = G_PUSH                                                     # (the book is just behind him: he turns round)
G_SLIDE0, G_SLIDE1 = (-5.8, 3.72), (-5.8, 3.24)                      # beside the fulcrum, sliding it toward the gate
OUT_VIA = [(-6.02, 0.98), (-5.58, 0.98), (-5.4, 1.45), (-5.41, 1.95), (-5.42, 2.6), (-5.48, 3.3), (-5.6, 3.9)]
CUBE = (-6.05, 4.05)
CAM_YAW = round(math.degrees(math.atan2(-5.85 - CUBE[0], -(3.4 - CUBE[1]))), 2)   # lens (local -y) at the build
rotz = lambda v, a: (v[0] * math.cos(math.radians(a)) - v[1] * math.sin(math.radians(a)), v[0] * math.sin(math.radians(a)) + v[1] * math.cos(math.radians(a)))
_o = rotz((0.0, -0.1), CAM_YAW)
CAM_ROOT = [round(CUBE[0] - _o[0], 4), round(CUBE[1] - _o[1], 4), round(STONE_TOP - 0.30, 3)]
BOOK_AT = (-5.75, 4.55)                                             # propped open on the book stone
BOOK_ROOT = [BOOK_AT[0], BOOK_AT[1], round(STONE_TOP - 0.085, 3)]
PAGES_ROOT = [BOOK_AT[0], BOOK_AT[1], round(STONE_TOP - 0.075, 3)]
face("smile", -5.0, 0.4, set=dict(C6["grandpa"]["face"]))
act(type="face_camera", when=-5.0, until=0.3)

# 1. pack up (Rule 2): the webcam and the book come along
PICK = 0.9
pose("pick_up", PICK - 0.5, PICK + 0.4, ease=0.3)
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R", when=round(PICK - 0.3, 3), until=99.0, reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CAM0, rot=[0, 0, CAM0_YAW]), dict(t=PICK, at=CAM0, rot=[0, 0, CAM0_YAW]), dict(t=round(PICK + 0.6, 3), at=CARRY, rot=[0, 0, 0])])
for name, r0, carry in (("book", BOOK0, BOOK_CARRY_B), ("pages", PAGES0, BOOK_CARRY_P)):
    act(type="hold", target=name, hand="L", when=round(PICK - 0.2, 3), until=99.0, reach=0.3, grip=[0.11, 0.0, 0.1],
        keys=[dict(t=-1.0, at=r0, rot=[0, 0, 0]), dict(t=round(PICK + 0.1, 3), at=r0, rot=[0, 0, 0]), dict(t=round(PICK + 0.7, 3), at=carry, rot=[0, 0, 0])])
look(PICK - 0.6, PICK + 0.4, pos=(-6.25, 1.68, 0.55), body=False)
s, e = say("field", 0.0, at=PICK + 0.5)
act(type="face_camera", when=round(s - 0.1, 3), until=round(s + 1.4, 3))
face("smirk", s, e + 0.2)
WALK0 = s + 1.5
WALK1 = WALK0 + 5.6
walk(WALK0, WALK1, G_SET, via=OUT_VIA)
# 2. find the spot: set the webcam and the book down
SET_T = WALK1 + 0.55
SET_B = SET_T                                                       # the book, on the stone ahead of him
SET_T = SET_B + 1.1                                                 # then the webcam, on the stone to his left
look(WALK1 - 0.4, SET_B + 0.3, pos=(BOOK_AT[0], BOOK_AT[1], 0.1), body=True, rate=0.18)
look(SET_B + 0.3, SET_T + 0.5, pos=(CUBE[0], CUBE[1], 0.1), body=True, rate=0.18)
pose("set_down", SET_B - 0.55, SET_B + 0.35, ease=0.3)
pose("set_down", SET_T - 0.55, SET_T + 0.45, ease=0.3)
for i, a in enumerate(A):
    if a["type"] == "hold":
        if a["target"] in ("webcam", "cam_cap"):
            a["until"] = round(SET_T, 3)
            a["keys"] += [dict(t=round(SET_T - 0.5, 3), at=CARRY, rot=[0, 0, 0]), dict(t=round(SET_T, 3), at=CAM_ROOT, rot=[0, 0, CAM_YAW])]
        elif a["target"] in ("book", "pages"):
            a["until"] = round(SET_B, 3)
            a["keys"] += [dict(t=round(SET_B - 0.5, 3), at=BOOK_CARRY_B if a["target"] == "book" else BOOK_CARRY_P, rot=[0, 0, 0]),
                          dict(t=round(SET_B, 3), at=BOOK_ROOT if a["target"] == "book" else PAGES_ROOT, rot=[0, 0, 0])]
sfx("settle", SET_B - 0.05, 0.3)
sfx("settle", SET_T - 0.05, 0.4)
s, e = say("page", 0.35, at=SET_T + 0.5)
look(s - 0.2, s + 1.4, pos=(BOOK_AT[0], BOOK_AT[1], 0.1), body=False)
face("raised", s + 1.4, e + 0.2, set=dict(smile=0.5))
s, e = say("dont", 0.4)
act(type="face_camera", when=round(s - 0.3, 3), until=round(e + 0.3, 3))
face("side_eye", s - 0.2, e + 0.3)
# 3. build: posts, gate, beam (counting squares), the fulcrum (in the wrong place), the counterweight
B0 = e + 0.5
walk(B0, B0 + 0.9, G_BUILD, via=[(-5.55, 3.8)])
T = B0 + 0.9
build("gate_posts", T, T + 1.3, G_BUILD); T += 1.35
build("gate", T, T + 1.2, G_BUILD); T += 1.25
s, e = say("squares", 0.0, at=T + 0.1)
build("beam", T, T + 1.6, G_BUILD, order="y"); T += 1.65
build("fulcrum", T, T + 0.9, G_BUILD); T += 0.95
s, e = say("vibes", 0.3, at=T)
build("weight", s + 0.4, s + 0.8, G_BUILD)
face("smirk", s + 0.6, e + 0.3)
BUILT = max(e, s + 0.8)
# 4. oops: he pushes -- nothing moves
walk(BUILT + 0.3, BUILT + 1.6, G_PUSH, via=[(-5.55, 3.85)])
LOOK_PUSH = len(A); look(BUILT + 1.3, 99.0, pos=(-6.0, 3.0, 0.4), body=True, rate=0.15)
P0 = BUILT + 1.8
pose("strain", P0, P0 + 1.0, ease=0.3)
pose("strain_b", P0 + 0.9, P0 + 2.2, ease=0.25)
act(type="swing", target="beam", axis="x", degrees=0.6, period=0.18, pivot=[-60, 37, 4.5], when=round(P0 + 0.6, 3), until=round(P0 + 2.0, 3))
face("wince", P0 + 0.3, P0 + 2.3)
sfx("creak", P0 + 1.6, 0.7)                                         # his back files a complaint
s, e = say("giving", 0.3, at=P0 + 2.0)
face("worried", s, e + 0.3)
# 5. why: the page draws the pivot by the gate (lesson card)
W0 = e + 0.3
A[LOOK_PUSH]["until"] = round(W0, 3)
LOOK_BOOK = len(A); look(W0, 99.0, pos=(BOOK_AT[0], BOOK_AT[1], 0.1), body=True, rate=0.18)      # he turns round to the page
pose("peer_down", W0 + 1.0, W0 + 3.4, ease=0.3)
s, e = say("drawn", 0.0, at=W0 + 1.2)
face("squint", s, s + 1.2)
face("raised", s + 1.2, e + 0.3)
s, e = say("lesson", 0.35)
LESSON0 = s
act(type="face_camera", when=round(s - 0.2, 3), until=round(e + 0.2, 3))
face("raised", s, e, set=dict(smile=0.3))
# 6. fix: slide the fulcrum over (Archimedes on the way), then one finger
F0 = e + 0.35
A[LOOK_BOOK]["until"] = round(F0, 3)
walk(F0, F0 + 0.9, G_SLIDE0)
SL0 = F0 + 1.1
SL1 = SL0 + 1.4
pose("push_low", SL0 - 0.3, SL1 + 0.2, ease=0.3)
walk(SL0, SL1, G_SLIDE1)
act(type="slide", target="fulcrum", by=[0.0, -0.5, 0.0], when=round(SL0, 3), until=round(SL1, 3), sound="scrape", gain=0.6)
act(type="look", when=round(SL0 - 0.3, 3), until=round(SL1 + 0.2, 3), body=False, pos=[-6.0, 3.45, 0.2])
s, e = say("archi", 0.2, at=SL1 + 0.3)
LESSON1 = e
walk(s + 0.4, s + 1.9, G_PUSH)
look(s + 1.7, 99.0, pos=(-6.0, 3.0, 0.4), body=True, rate=0.15)
face("smirk", e - 1.6, e + 0.3)
U0 = max(e + 0.4, s + 2.2)                                          # one finger...
pose("finger_top", U0 - 0.5, U0 + 0.1, ease=0.3)
pose("finger_dn", U0, U0 + 2.6, ease=1.0)
for name in ("beam", "weight"):
    act(type="spin", target=name, axis="x", degrees=SWING, pivot=PIVOT, when=round(U0 + 0.05, 3), until=round(U0 + 1.05, 3))
act(type="slide", target="gate", by=[0.0, 0.0, LIFT], when=round(U0 + 0.1, 3), until=round(U0 + 1.1, 3), sound="none")
sfx("creak", U0 + 0.2, 0.35)
face("surprised", U0 + 0.4, U0 + 1.3, set=dict(brow=1.0))
s, e = say("rizz", 0.0, at=U0 + 1.3)
pose("proud", s + 0.3, e + 0.6, ease=0.3)
act(type="face_camera", when=round(s, 3), until=round(e + 0.5, 3))
face("smile", s, e + 0.5, set=dict(smile=1.0))
# 7. the feelings beat: a little memory cloud tries to puff up... he looks at the gate; it pops (no slang)
CL0 = e + 0.5
CL1 = CL0 + 2.4
look(CL0 + 0.1, CL0 + 1.0, pos=(-5.7, 3.4, 1.4), body=False)        # glances up at it
look(CL0 + 1.0, CL1 + 0.2, pos=(-5.95, 2.9, 0.5), body=False)       # ...then at the gate: pop
face("worried", CL0 + 0.1, CL0 + 1.1)
face("content", CL0 + 1.1, CL1 + 0.5)
CLOUD = dict(kind="memory_cloud", at=[G_PUSH[0] + 0.2, G_PUSH[1], 1.45], visible=[round(CL0, 3), round(CL1, 3)], yaw=180.0, size=0.6,
             boar=dict(huffs=[round(CL0 + 0.6, 3)], stomps=[], clacks=[]))
s, e = say("scared", 0.4, at=CL1 + 0.2)
act(type="face_camera", when=round(s - 0.4, 3), until=round(e + 0.2, 3))
face("warm", s, e + 0.2)
s, e = say("tobias", 0.3)
act(type="face_camera", when=round(s - 0.2, 3), until=round(e + 0.4, 3))
face("side_eye", s, e + 0.4, set=dict(smile=0.4))
# 8. the hook: a bottle comes down the stream
H0 = e + 0.4
BOT_Y0, BOT_Y1 = 5.0, 3.55
BOT_T0, BOT_T1 = H0 - 2.6, H0 + 2.8
keys, n = [], 12
for k in range(n + 1):
    u = k / n; t = BOT_T0 + (BOT_T1 - BOT_T0) * u; y = BOT_Y0 + (BOT_Y1 - BOT_Y0) * u
    keys.append(dict(t=round(t, 3), at=[round(STREAM_X(y) - 0.12, 4), round(y, 4), round(-0.065 + 0.008 * math.sin(5 * t), 4)],
                     rot=[round(6 * math.sin(3 * t), 2), 0, round(10 + 8 * math.sin(1.3 * t), 2)]))
keys = [dict(keys[0], t=-1.0)] + keys + [dict(keys[-1], t=99.0)]
act(type="hold", target="bottle", hand="none", when=-1.0, until=99.0, reach=0.05, keys=keys)
look(H0 - 0.3, 99.0, pos=(STREAM_X(3.8) - 0.12, 3.8, 0.05), body=True, rate=0.2)
s, e = say("bottle", 0.0, at=H0 + 0.4)
face("surprised", s - 0.3, 99.0, set=dict(brow=1.2, smile=0.0))
sfx("clink", s - 0.6, 0.25)
END = e + 0.9
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

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
for i, (lid, text, speed) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if speed: ln["speed"] = speed
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["bottle"] - 0.5 / FPS
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
LOS = make_los([])
GATE_PTS = [(-6.2, 2.9, 0.05), (-5.7, 2.9, 0.7), (-6.0, 3.9, 0.6)]
last = C6["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
CUT_INS = None
SHOTS = [
    # the walk to the garden's north side, along the bank: seen from across the stream
    lambda: auto_frame(WALK0 + 1.4, gp(*OUT_VIA[3]) + gp(*G_SET)[1:], (-5.6, 2.8, 0.6), -35, 12, 4.0, AIR, prev=cam, path_clear=PATH, los=LOS, who=who_at),
    # setting down: the webcam, the book; "How hard can it be?"
    lambda: auto_frame(SET_T - 0.3, gp(*G_SET) + [(CUBE[0], CUBE[1], 0.1), (BOOK_AT[0], BOOK_AT[1], 0.1)], (-5.85, 4.25, 0.5), 20, 12, 3.2,
                       AIR, prev=cam, path_clear=PATH, los=make_los([box_at(G_SET)]), who=who_at),
    # the build: a side view of the whole gate
    lambda: auto_frame(B0 + 1.0, gp(*G_BUILD) + GATE_PTS, (-5.85, 3.35, 0.5), 0, 16, 3.2, AIR, prev=cam, path_clear=PATH,
                       los=make_los([box_at(G_BUILD)]), who=who_at),
    # the oops: his straining face, the beam that won't budge
    lambda: auto_frame(P0 + 0.2, gp(*G_PUSH) + [(-6.0, 3.0, 0.4), BEAM_END], (-5.85, 3.7, 0.65), 20, 12, 2.6,
                       AIR, prev=cam, path_clear=PATH, los=make_los([box_at(G_PUSH)]), who=who_at),
    # why: the page (insert, a hard cut)
    lambda: [dict(cam[-1], at=round(math.ceil((LS["drawn"] + 0.6) * FPS - 1e-6) / FPS - 1.0 / FPS, 4)),
             auto_frame(math.ceil((LS["drawn"] + 0.6) * FPS - 1e-6) / FPS, [(BOOK_AT[0] - 0.11, BOOK_AT[1] - 0.07, STONE_TOP), (BOOK_AT[0] + 0.11, BOOK_AT[1] + 0.07, STONE_TOP)],
                        (BOOK_AT[0], BOOK_AT[1], STONE_TOP), 100, 32, 0.7, AIR, los=LOS)],   # from beyond the book: he's behind it
    # the lesson to chat
    lambda: [dict(cam[-1], at=round(math.ceil(LS["lesson"] * FPS - 1e-6) / FPS - 1.0 / FPS, 4)),
             auto_frame(math.ceil(LS["lesson"] * FPS - 1e-6) / FPS, [(G_BOOK[0], G_BOOK[1], 0.75), (G_BOOK[0], G_BOOK[1], 1.12)], (G_BOOK[0], G_BOOK[1], 0.9), 40, 10, 2.2, AIR,
                        los=make_los([box_at(G_BOOK)]))],
    # the fix: slide the fulcrum, Archimedes, one finger, the gate goes up
    lambda: auto_frame(SL0 + 0.2, gp(*G_SLIDE0)[1:] + GATE_PTS, (-5.85, 3.4, 0.5), 0, 12, 3.2, AIR, prev=cam, path_clear=PATH,
                       los=make_los([box_at(G_SLIDE0)]), who=who_at),
    lambda: auto_frame(U0 - 0.2, gp(*G_PUSH) + GATE_PTS[:2] + [(-6.0, 2.9, 0.62)], (-5.9, 3.5, 0.6), 10, 12, 2.8,
                       AIR, prev=cam, path_clear=PATH, los=make_los([box_at(G_PUSH)]), who=who_at),
    # the feelings beat: close, the little cloud
    lambda: auto_frame(CL0 + 0.1, gp(*G_PUSH)[1:] + [(CLOUD["at"][0], CLOUD["at"][1], 1.75)], (G_PUSH[0] + 0.05, G_PUSH[1], 1.15), 40, 8, 2.4,
                       AIR, prev=cam, path_clear=PATH, los=make_los([box_at(G_PUSH)]), who=who_at),
    # the hook: the bottle and him
    lambda: auto_frame(H0 + 0.2, gp(*G_PUSH)[1:] + [(STREAM_X(3.8) - 0.12, 3.8, 0.03), (STREAM_X(4.4) - 0.12, 4.4, 0.03)],
                       (-5.45, 3.95, 0.45), 20, 14, 2.4, AIR, prev=cam, path_clear=PATH, los=make_los([box_at(G_PUSH)]), who=who_at),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
    if CLOUD.get("face") is None and cam[-1]["at"] >= CL0 - 0.5:
        CLOUD["face"] = cam[-1]["az"] + 90
cam.sort(key=lambda k: k["at"])
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
INS0 = math.ceil((LS["drawn"] + 0.6) * FPS - 1e-6) / FPS
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C6["overlay"]["live_viewers"]]]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.3, 3), rows=[
             dict(text="LEVER", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="long arm + pivot near the load = easy lift", color="cyan", at=round(LESSON0 + 1.4, 3), size=30)])]
W7 = {k: v for k, v in S6["world"].items() if k != "critters"}
W7["critters"] = [CLOUD]
story = dict(title="Leverage", slug="grandpa_ep01_scene007", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["field"], tail=round(tail, 4), seed=31, blink=True, target_duration=60,
             engine_rev=3, scene=dict(episode=1, scene=7, name="Leverage", previous="ep01_scene006", next="ep01_scene008"),
             world=W7, lines=lines, grandpa=dict(start=list(G0), outfit=S6["grandpa"]["outfit"]),
             poses=dict(S6["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"], ["webcam", "cam_stone"], ["book", "book_stone"]],
                     frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve", "lean_posts", "bench_legs",
                            "gate_posts", "fulcrum"],
                     cutaways=[[round(INS0, 3), round(math.ceil(LS["lesson"] * FPS - 1e-6) / FPS, 3)]]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene007.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("set %.2f build %.2f-%.2f push %.2f slide %.2f-%.2f lift %.2f (%.3f m) cloud %.2f-%.2f bottle %.2f" % (SET_T, B0, BUILT, P0, SL0, SL1, U0, LIFT, CL0, CL1, H0))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
