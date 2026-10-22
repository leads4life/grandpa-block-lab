"""Grandpa's Block Lab, Episode 1, Scene 008 -- "Leverage" (16:9, ~50 s). Approved beat sheet (2026-10-22).
Blueprint Build, Grandpa solo (Tobias only in chat). Starts from Scene 007's end at the fence's gap, the book still open in
his left hand, the webcam on the bank stone, LIVE 4 (Tobias watching from home). He builds the lift gate: a tall pivot
post, the plank gate on its long arm, a short stub past the pivot. "Boars push gates open... but they can't lift one."
He skips the rock ("For... vibes? Nah. Skip."). Oops: far too heavy. Why: it's a seesaw (lesson: COUNTERWEIGHT). Fix: the
rock goes on the stub; one finger and the gate swings up ("rizz"); he lets go and it shuts by itself. "A boar-proof
garden. Tobias is gonna flip." Feelings beat (no slang). "Don't tell Tobias I said that." -- TobiasBuilds: "too late".
Hook: a bottle drifts down the stream -- page thirteen?
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both
from forest_camkit import make_los as _make_los
FPS = 30
S7 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene007.json"))
C7 = json.load(open(os.path.join(HERE, "s7work/build/continuity.json")))
F7 = C7["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 007 left it
def root_of(name):
    r = C7["structures"][name]["root"]
    return [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)], round(math.degrees(math.atan2(r[1][0], r[0][0])), 2)
for name, st in S7["structures"].items():
    if C7["structures"][name]["blocks_standing"] == 0:
        continue
    st = json.loads(json.dumps(st))
    if name.startswith("fence_"):
        st["prebuilt"] = True                                       # built in Scene 007: simply there now
    S[name] = st
PROP_OUT = root_of("prop")[0]
CAM_ROOT, CAM_YAW = root_of("webcam")                               # on the bank stone (Scene 007)
for name in ("webcam", "cam_cap"):
    S[name]["at"] = CAM_ROOT; S[name]["yaw"] = CAM_YAW
for name in ("book", "pages"):                                      # still open in his left hand: the hold places them
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
# ---------------------------------------------------------------- the lift gate (built on camera), across the gap (x -3.27..-2.83)
# A tall pivot post just outside the gap's east post; the arm runs west across the gap with the plank gate hanging under it,
# and a short stub runs east past the pivot. The whole arm turns about the pivot (axis y): the gate end swings UP.
S["pivot_post"] = dict(cells=[[-28, 14, z] for z in range(7)], at=[0.0, 0.0, 0.0], centered=False, material="wood",
                       block_shape=[0.7, 0.7, 1], expect_blocks=7)
ARM = [[x, 14, 7] for x in range(-33, -25)]                          # x -3.3 .. -2.6, z 0.7-0.8 (on top of the pivot post)
PANEL = [[x, 14, z] for x in range(-32, -28) for z in range(1, 7)]  # x -3.2 .. -2.9, z 0.1-0.7: hangs under the arm
S["gate_arm"] = dict(cells=ARM + PANEL, at=[0.0, 0.0, 0.0], centered=False, material="planks", block_shape=[1, 0.4, 1],
                     expect_blocks=len(ARM) + len(PANEL))
PIVOT = [-28, 14, 6.5]                                              # the pivot: top of the post, x -2.8, z 0.7
OPEN = 75.0                                                         # degrees about +y: the west (gate) end rises
S["ground_rock"] = dict(cells=[[-22, 10, 0]], at=[0.0, 0.0, 0.0], centered=False, material="stone", block_shape=[0.9, 0.9, 0.9],
                        expect_blocks=1, prebuilt=True)              # the rock, lying by the gate
S["stub_rock"] = dict(cells=[[-26, 14, 8]], at=[0.0, 0.0, 0.0], centered=False, material="stone", block_shape=[0.9, 0.9, 0.9],
                      expect_blocks=1)                               # ...and on the stub (z 0.8-0.9)
# the bottle (hook): down the stream, north of the machine
S["bottle"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="glass", block_shape=[0.9, 2.2, 0.9], expect_blocks=1,
                   extras=[dict(c=[0.0, 0.118, 0.055], s=[0.045, 0.03, 0.045], m="wood"), dict(c=[0.0, 0.0, 0.056], s=[0.05, 0.16, 0.05], m="paper")])
STREAM_X = lambda y: -5.2 + 0.25 * math.sin(0.7 * y)
FENCE_BOXES = [((-3.84, 1.46, 0.0), (-2.26, 1.54, 0.5)), ((-3.84, 1.46, 0.0), (-3.76, 3.04, 0.5)),
               ((-3.84, 2.96, 0.0), (-2.26, 3.04, 0.5)), ((-2.34, 1.46, 0.0), (-2.26, 3.04, 0.5)), ((-2.84, 1.36, 0.0), (-2.76, 1.44, 0.8))]
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE, **kw)
def boxes_free(eye):
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in FENCE_BOXES)
AIR = both(clear_air, boxes_free)
PATH = both(solid_free, boxes_free)

# ---------------------------------------------------------------- lines
LINES = [("fine", "...It's fine. It's FINE. Gate.", None),
         ("lift", "A lift gate. Boars push gates open... but they can't lift one.", None),
         ("vibes", "A rock? For... vibes? Nah. Skip.", None),
         ("giving", "This gate is NOT... giving.", None),
         ("seesaw", "Ohh. It's a seesaw.", None),
         ("cousin", "Put your big cousin on the short end, and the little kid can lift the long end.", None),
         ("draw", "Drawbridges work the same way.", None),
         ("rizz", "Now THAT'S got... rizz.", None),
         ("shuts", "And it shuts by itself.", None),
         ("flip", "A boar-proof garden. Tobias is gonna flip.", None),
         ("scared", "Being scared's normal. Building something... helps.", 0.88),
         ("tobias", "Don't tell Tobias I said that.", None),
         ("bottle", "...Is that... page thirteen?", None)]
GUESS = dict(fine=2.4, lift=4.3, vibes=2.6, giving=2.1, seesaw=1.6, cousin=4.6, draw=2.0, rizz=2.0, shuts=1.5, flip=3.2, scared=3.7,
             tobias=2.3, bottle=2.0)
dur_file = os.path.join(HERE, "ep01_s008_durations.json")
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

ARM_END = (-3.3, 1.4, 0.75)                                         # where he grips to lift (the gate end of the arm)
POSES = {
    "strain_lift": dict(lean=0.3, hips=[0.0, 0.0, -0.08], shrug=0.5, hand_R={"world": [ARM_END[0] + 0.04, ARM_END[1] - 0.04, ARM_END[2] - 0.02]}),
    "strain_lift_b": dict(lean=0.4, hips=[0.0, 0.0, -0.12], shrug=0.7, hand_R={"world": [ARM_END[0] + 0.04, ARM_END[1] - 0.04, ARM_END[2] - 0.02]}),
    "finger_lift": dict(lean=0.15, hand_R={"world": [ARM_END[0] + 0.04, ARM_END[1] - 0.05, ARM_END[2] - 0.04]}),
    "crouch_pick": dict(lean=0.6, hips=[0.0, 0.0, -0.2]),
    "place_high": dict(lean=0.18, hand_R={"world": [-2.6, 1.34, 0.86]}),
    "read_held": dict(head=(0.0, -0.25, 0.0)),
    "proud": dict(lean=-0.08, hand_R={"char": [-0.2, -0.06, 0.6]}),
    "freeze": dict(shrug=0.6, elbows=0.2, lean=-0.05),
    "dreamy": dict(head=(0.0, 0.12, 0.08), lean=-0.03),
}
BOOK_CARRY_B = {"char": [0.17, -0.2, 0.80]}
BOOK_CARRY_P = {"char": [0.17, -0.2, 0.81]}
G0 = C7["grandpa"]["root"][:2]                                      # (-3.05, 1.05) at the gap
G_POST = (-2.62, 1.08)                                              # building the pivot post / placing the rock
G_GATE = (-3.05, 1.08)                                              # building the gate; in front of it
G_LIFT = (-3.32, 1.1)                                               # at the gate end of the arm
G_ROCK = (-2.42, 0.95)                                              # by the rock on the ground (at -2.2, 1.0)
G_BACK = (-3.0, 0.72)                                               # stepping back to admire it
for name, carry in (("book", BOOK_CARRY_B), ("pages", BOOK_CARRY_P)):
    act(type="hold", target=name, hand="L", when=-1.0, until=99.0, reach=0.05, grip=[0.0, -0.07, 0.09],
        keys=[dict(t=-1.0, at=carry, rot=[0, 0, 0]), dict(t=99.0, at=carry, rot=[0, 0, 0])])
face("surprised", -5.0, 0.4, set=dict(C7["grandpa"]["face"]))
look(-5.0, 0.9, pos=(-5.8, 2.6, 0.5), body=False)                    # still staring toward the huff...

# 1. "It's fine. It's FINE. Gate."
s, e = say("fine", 0.0, at=0.5)
act(type="face_camera", when=round(s + 0.9, 3), until=round(e + 0.3, 3))
face("worried", s, s + 1.0, set=dict(brow=1.0))
face("alert", s + 1.0, e + 0.3, set=dict(brow=-0.3))
# 2. the build: the pivot post, then the gate on its arm
B0 = e + 0.3
walk(B0, B0 + 0.6, G_POST)
T = B0 + 0.7
look(T - 0.2, T + 1.2, pos=(-2.8, 1.4, 0.35), body=True, rate=0.25)
build("pivot_post", T, T + 1.1, G_POST); T += 1.15
walk(T, T + 0.5, G_GATE)
T += 0.6
look(T - 0.2, T + 2.4, pos=(-3.0, 1.4, 0.5), body=True, rate=0.25)
build("gate_arm", T, T + 2.2, G_GATE, order="x"); T += 2.25
s, e = say("lift", 0.0, at=B0 + 1.0)
face("raised", s + 1.5, e + 0.3, set=dict(smile=0.4))
# 3. the rock, on the page... skipped
s, e = say("vibes", 0.3, at=T + 0.1)
look(s - 0.2, s + 1.0, obj="book", body=False)
pose("read_held", s - 0.2, s + 1.0, ease=0.25)
look(s + 1.0, e - 0.6, pos=(-2.2, 1.0, 0.05), body=False)           # glances at the rock on the ground
face("smirk", s + 1.6, e + 0.3)
act(type="face_camera", when=round(e - 0.7, 3), until=round(e + 0.2, 3))
# 4. oops: far too heavy
O0 = e + 0.2
walk(O0, O0 + 0.6, G_LIFT)
LOOK_ARM = len(A); look(O0 + 0.5, 99.0, pos=ARM_END, body=True, rate=0.25)
P0 = O0 + 0.8
pose("strain_lift", P0, P0 + 1.0, ease=0.3)
pose("strain_lift_b", P0 + 0.9, P0 + 2.2, ease=0.25)
act(type="swing", target="gate_arm", axis="y", degrees=0.8, period=0.2, pivot=PIVOT, when=round(P0 + 0.5, 3), until=round(P0 + 2.0, 3))
face("wince", P0 + 0.3, P0 + 2.3)
sfx("creak", P0 + 1.6, 0.7)                                          # his back
s, e = say("giving", 0.25, at=P0 + 2.0)
face("worried", s, e + 0.3)
GIVING = s
# 5. why: it's a seesaw
s, e = say("seesaw", 0.6)
A[LOOK_ARM]["until"] = round(s - 0.6, 3)
look(s - 0.6, s + 0.9, obj="book", body=False)
pose("read_held", s - 0.6, s + 0.9, ease=0.25)
look(s + 0.9, e + 0.4, pos=(-2.6, 1.4, 0.75), body=False)           # ...then at the stub
face("raised", s + 0.3, e + 0.3, set=dict(brow=1.1, smile=0.3))
s, e = say("cousin", 0.35)
LESSON0 = s
act(type="face_camera", when=round(s - 0.2, 3), until=round(e + 0.2, 3))
face("raised", s, e, set=dict(smile=0.4))
s, e = say("draw", 0.3)
LESSON1 = e
face("smile", s, e + 0.3)
# 6. fix: the rock goes on the stub; one finger; it swings up -- and shuts by itself
F0 = e + 0.3
walk(F0, F0 + 0.8, G_ROCK)
look(F0 + 0.6, F0 + 1.6, pos=(-2.2, 1.0, 0.05), body=True, rate=0.3)
pose("crouch_pick", F0 + 0.8, F0 + 1.5, ease=0.25)
act(type="remove", target="ground_rock", when=round(F0 + 1.05, 3), until=round(F0 + 1.25, 3), stand_at=[G_ROCK[0], G_ROCK[1], 0.0])
walk(F0 + 1.5, F0 + 1.9, G_POST)
look(F0 + 1.8, F0 + 2.8, pos=(-2.6, 1.4, 0.85), body=True, rate=0.3)
pose("place_high", F0 + 2.0, F0 + 2.8, ease=0.25)
act(type="build", target="stub_rock", when=round(F0 + 2.3, 3), until=round(F0 + 2.6, 3), stand_at=[G_POST[0], G_POST[1], 0.0], quiet=True)
sfx("settle", F0 + 2.5, 0.5)
walk(F0 + 2.9, F0 + 3.6, G_LIFT)
look(F0 + 3.4, F0 + 6.0, pos=ARM_END, body=True, rate=0.3)
U0 = F0 + 3.8
pose("finger_lift", U0 - 0.4, U0 + 0.6, ease=0.25)
for name in ("gate_arm", "stub_rock"):
    act(type="spin", target=name, axis="y", degrees=OPEN, pivot=PIVOT, when=round(U0, 3), until=round(U0 + 1.4, 3))
sfx("creak", U0 + 0.1, 0.4)
face("surprised", U0 + 0.2, U0 + 1.2, set=dict(brow=1.0))
look(U0 + 0.4, U0 + 3.0, pos=(-3.1, 1.4, 1.2), body=False)            # watching it rise
s, e = say("rizz", 0.0, at=U0 + 1.4)
face("smile", s, e + 0.4, set=dict(smile=1.0))
D0 = e + 0.4                                                         # ...lets go: it drifts back down
for name in ("gate_arm", "stub_rock"):
    act(type="spin", target=name, axis="y", degrees=-OPEN, pivot=PIVOT, when=round(D0, 3), until=round(D0 + 2.0, 3))
sfx("creak", D0 + 0.2, 0.3)
sfx("settle", D0 + 1.95, 0.8)                                        # the thunk as it shuts
look(D0, D0 + 2.3, pos=(-3.05, 1.4, 0.45), body=False)
s, e = say("shuts", 0.0, at=D0 + 2.1)
face("content", s, e + 0.3)
# 7. step back: the whole garden
walk(e + 0.2, e + 1.2, G_BACK)
act(type="face_camera", when=round(e + 1.1, 3), until=round(e + 4.6, 3))
s, e = say("flip", 0.2, at=e + 1.2)
pose("proud", s, e + 0.4, ease=0.3)
face("smile", s, e + 0.4, set=dict(smile=0.9))
# 8. the feelings beat: a little cloud tries to puff up... he looks at the gate; it pops
CL0 = e + 0.5
CL1 = CL0 + 2.4
look(CL0 + 0.1, CL0 + 1.0, pos=(-2.85, 0.72, 1.45), body=False)
look(CL0 + 1.0, CL1 + 0.2, pos=(-3.05, 1.4, 0.4), body=False)
face("worried", CL0 + 0.1, CL0 + 1.1)
face("content", CL0 + 1.1, CL1 + 0.5)
CLOUD = dict(kind="memory_cloud", at=[G_BACK[0] + 0.2, G_BACK[1], 1.45], visible=[round(CL0, 3), round(CL1, 3)], yaw=180.0, size=0.6,
             boar=dict(huffs=[round(CL0 + 0.6, 3)], stomps=[], clacks=[]))
s, e = say("scared", 0.4, at=CL1 + 0.2)
act(type="face_camera", when=round(s - 0.4, 3), until=99.0)
face("warm", s, e + 0.2)
s, e = say("tobias", 0.35)
face("side_eye", s, e + 0.3, set=dict(smile=0.4))
TOO_LATE = e + 0.4                                                  # chat: "too late" -- he freezes
pose("freeze", TOO_LATE + 0.3, TOO_LATE + 1.8, ease=0.12)
face("surprised", TOO_LATE + 0.35, TOO_LATE + 1.8, set=dict(brow=1.3, smile=0.0))
# 9. the hook: a bottle comes down the stream
H0 = TOO_LATE + 1.9
BOT_Y0, BOT_Y1 = 4.2, 2.75
BOT_T0, BOT_T1 = H0 - 2.6, H0 + 3.0
keys, n = [], 12
for k in range(n + 1):
    u = k / n; t = BOT_T0 + (BOT_T1 - BOT_T0) * u; y = BOT_Y0 + (BOT_Y1 - BOT_Y0) * u
    keys.append(dict(t=round(t, 3), at=[round(STREAM_X(y) + 0.1, 4), round(y, 4), round(-0.065 + 0.008 * math.sin(5 * t), 4)],
                     rot=[round(6 * math.sin(3 * t), 2), 0, round(10 + 8 * math.sin(1.3 * t), 2)]))
keys = [dict(keys[0], t=-1.0)] + keys + [dict(keys[-1], t=99.0)]
act(type="hold", target="bottle", hand="none", when=-1.0, until=99.0, reach=0.05, keys=keys)
look(H0 - 0.2, 99.0, pos=(STREAM_X(3.0) + 0.1, 3.0, 0.05), body=False, rate=0.35)
s, e = say("bottle", 0.0, at=H0 + 0.5)
face("surprised", s - 0.4, 99.0, set=dict(brow=1.2, smile=0.0))
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
TRIP7 = [a for a in S7["actions"] if a["type"] == "trip"][0]
FIRST = TRIP7["first"] - F7
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
def box_at(p, r=0.17, h=1.2):
    return ((p[0] - r, p[1] - r, 0.0), (p[0] + r, p[1] + r, h))
GATE_PTS = [(-3.3, 1.4, 0.05), (-2.6, 1.4, 0.9), (-3.3, 1.4, 1.25)]
LG = make_los([((-3.33, 1.38, 0.1), (-2.57, 1.42, 0.9)), ((-2.84, 1.36, 0.0), (-2.76, 1.44, 0.8))])   # the gate itself blocks the view
last = C7["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
def cut(t, *a, **kw):                                               # a hard cut to a new framing at t
    tc = math.ceil(t * FPS - 1e-6) / FPS
    return lambda: [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), auto_frame(tc, *a, **kw)]
SHOTS = [
    # the build: through the fence from inside the plot, the whole gap and his face
    cut(B0 + 0.6, gp(*G_GATE)[1:] + [(-3.3, 1.4, 0.05), (-2.6, 1.4, 0.9)], (-2.95, 1.3, 0.6), 60, 28, 3.0, AIR, los=LG),
    # the oops: his straining face at the arm's end
    cut(P0 - 0.2, gp(*G_LIFT)[1:] + [ARM_END, (-2.8, 1.4, 0.75)], (-3.1, 1.25, 0.8), 50, 28, 2.2, AIR, los=LG),
    # (the lesson plays on the oops framing: his face, the arm and the stub)
    # the fix: rock on, the gate swings up and back down -- the whole gate in frame
    cut(F0 + 0.2, gp(*G_ROCK) + gp(*G_LIFT)[1:] + GATE_PTS, (-2.95, 1.3, 0.6), 50, 28, 3.0, AIR, los=LG),
    # "A boar-proof garden": wide, the whole fence and gate
    cut(LS["flip"] - 0.3, gp(*G_BACK) + [(-3.8, 3.0, 0.5), (-2.3, 1.5, 0.05), (-2.3, 3.0, 0.5)], (-3.0, 1.9, 0.5), -180, 28, 3.6, AIR,    # high, from the west: the whole fence and gate, and him
        los=LG),
    # the feelings beat and "too late": close on him, the little cloud
    cut(CL0 - 0.2, gp(*G_BACK)[1:] + [(CLOUD["at"][0], CLOUD["at"][1], 1.75)], (G_BACK[0] + 0.05, G_BACK[1], 1.15), -60, 16, 2.6, AIR,
        los=make_los([box_at(G_BACK)])),
    # the hook: him and the bottle
    cut(H0 - 0.1, gp(*G_BACK) + [(STREAM_X(3.0) + 0.1, 3.0, 0.03), (STREAM_X(3.6) + 0.1, 3.6, 0.03)], (-3.6, 1.7, 0.6), -120, 28, 4.2, AIR,
        los=make_los([])),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
    if CLOUD.get("face") is None and cam[-1]["at"] >= CL0 - 0.5:
        CLOUD["face"] = cam[-1]["az"] + 90
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
CHAT = [(LE["lift"] + 0.3, "BoarFan2009", "rude"),
        (LE["giving"] + 0.3, "GardenGranny", "read the page dear"),
        (LE["shuts"] + 0.2, "lurker_77", "ok thats cool"),
        (TOO_LATE, "TobiasBuilds", "too late")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C7["overlay"]["live_viewers"]]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="COUNTERWEIGHT", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="a heavy rock on the short side balances the long gate", color="cyan", at=round(LESSON0 + 1.4, 3), size=28)])]
W8 = {k: v for k, v in S7["world"].items() if k != "critters"}
W8["critters"] = [CLOUD]
story = dict(title="Leverage", slug="grandpa_ep01_scene008", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["fine"], tail=round(tail, 4), seed=37, blink=True, target_duration=50,
             engine_rev=3, scene=dict(episode=1, scene=8, name="Leverage", previous="ep01_scene007", next="ep01_scene009"),
             world=W8, lines=lines, grandpa=dict(start=list(G0), outfit=S7["grandpa"]["outfit"]),
             poses=dict(S7["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"], ["webcam", "rock"]],
                     frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve", "lean_posts", "bench_legs",
                            "pivot_post"] + ["fence_posts_" + k for k in "swne"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene008.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("build %.2f push %.2f fix %.2f lift %.2f down %.2f cloud %.2f-%.2f too-late %.2f bottle %.2f" % (B0, P0, F0, U0, D0, CL0, CL1, TOO_LATE, H0))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
