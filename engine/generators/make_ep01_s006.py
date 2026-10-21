"""Grandpa's Block Lab, Episode 1, Scene 006 -- "Page Twelve" (16:9, ~60 s). Approved beat sheet (2026-10-21).
Starts from Scene 005's end, in Tobias's garden. Tobias shows his lean-to workshop (south of the garden, under the oak):
a grub jar, and Grandpa's own old blueprint book -- he designed the trip hammer. Micro-lesson: scale. Tobias leaves
for homework (the LIVE count drops to 3: he was the 4th viewer). Alone, an anxious thought sets off the flashback: the
memory cloud, "You kinda bussin'!" echoing three times. "Nope nope nope." Page twelve: a lever gate lifts off the page.
Pages are torn out. Hook: "Chat... batten down the hatches!"
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, facing, both
from forest_camkit import make_los as _make_los
FPS = 30
S5 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene005.json"))
C5 = json.load(open(os.path.join(HERE, "s5work/build/continuity.json")))
F5 = C5["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 005 left it
for name, st in S5["structures"].items():
    if C5["structures"][name]["blocks_standing"] == 0:
        continue
    S[name] = json.loads(json.dumps(st))
PROP_OUT = [round(C5["structures"]["prop"]["root"][i][3], 4) for i in range(3)]
# Tobias's lean-to workshop, south of his garden, tucked under the oak at (-6.39, 0.9): open to the south, a kid's bench
# along the back, a flat plank roof at 1.4-1.5 m.
DX = 0.05                                                           # the posts sit between grid cells
POSTS = [[x, y, z] for x in (-65, -58) for y in (13, 18) for z in range(14)]
S["lean_posts"] = dict(cells=POSTS, at=[0.0, 0.0, 0.0], centered=False, material="wood", block_shape=[0.5, 0.5, 1],
                       expect_blocks=len(POSTS), prebuilt=True)
ROOF = [[x, y, 14] for x in range(-65, -57) for y in range(12, 20)]
S["lean_roof"] = dict(cells=ROOF, at=[0.0, 0.0, 0.0], centered=False, material="planks", block_shape=[1, 1, 0.6],
                      expect_blocks=len(ROOF), prebuilt=True)
BENCH_LEGS = [[x, y, z] for x in (-64, -60) for y in (16, 17) for z in range(4)]
S["bench_legs"] = dict(cells=BENCH_LEGS, at=[DX, 0.0, 0.0], centered=False, material="planks", block_shape=[0.35, 0.35, 1],
                       expect_blocks=len(BENCH_LEGS), prebuilt=True)
S["bench"] = dict(cells=[[x, y, 4] for x in range(-64, -59) for y in (16, 17)], at=[DX, 0.0, 0.0], centered=False,
                  material="planks", block_shape=[1, 1, 0.35], expect_blocks=10, prebuilt=True)
BENCH_TOP = 0.5
BOOK = (-6.15, 1.63, BENCH_TOP)                                     # the open blueprint book, on the bench
S["book"] = dict(cells=[[0, 0, 0]], at=[BOOK[0], BOOK[1], BOOK[2] - 0.085], centered=False, material="leather",
                 block_shape=[2.3, 1.55, 0.15], expect_blocks=1, prebuilt=True)
S["pages"] = dict(cells=[[0, 0, 0]], at=[BOOK[0], BOOK[1], BOOK[2] - 0.075], centered=False, material="paper",
                  block_shape=[2.1, 1.35, 0.1], expect_blocks=1, prebuilt=True)
def _line(x0, y0, x1, y1, w, z, m):
    return dict(c=[round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4), z], s=[round(max(abs(x1 - x0), w), 4), round(max(abs(y1 - y0), w), 4), 0.0014], m=m)
INK = []
for k in range(14):                                                 # the grid: one square = one block
    x = -0.0975 + 0.015 * k
    if abs(x) > 0.004:
        INK.append(_line(x, -0.0625, x, 0.0625, 0.0013, 0.1006, "blue"))
for k in range(9):
    INK.append(_line(-0.1, -0.06 + 0.015 * k, 0.1, -0.06 + 0.015 * k, 0.0013, 0.1006, "blue"))
INK.append(_line(0.0, -0.067, 0.0, 0.067, 0.003, 0.1007, "leather"))   # the gutter
for (a, b, c_, d) in ((-0.09, -0.02, -0.05, -0.02), (-0.09, 0.02, -0.05, 0.02), (-0.09, -0.02, -0.09, 0.02), (-0.05, -0.02, -0.05, 0.02),  # wheel
                      (-0.05, 0.0, -0.02, 0.0), (-0.045, 0.03, -0.012, 0.03), (-0.03, 0.0, -0.03, 0.03),                            # axle, helve, post
                      (0.03, -0.045, 0.03, 0.03), (0.085, -0.045, 0.085, 0.03), (0.036, -0.04, 0.079, -0.04), (0.036, 0.0, 0.079, 0.0),  # gate
                      (0.036, -0.04, 0.036, 0.0), (0.079, -0.04, 0.079, 0.0), (0.018, 0.038, 0.097, 0.038), (0.04, 0.03, 0.04, 0.046)):  # lever
    INK.append(_line(a, b, c_, d, 0.0035, 0.1009, "darkiron"))
INK.append(dict(c=[-0.012, 0.03, 0.1009], s=[0.009, 0.009, 0.002], m="darkiron"))                                  # the hammer head
INK += [dict(c=[0.107, y, 0.0985], s=[0.006, 0.014, 0.003], m="paper") for y in (-0.045, -0.02, 0.012, 0.04)]    # torn-out stubs
S["pages"]["extras"] = INK
S["jar"] = dict(cells=[[0, 0, 0]], at=[-5.93, 1.68, BENCH_TOP - 0.01], centered=False, material="glass",
                block_shape=[0.6, 0.6, 0.9], expect_blocks=1, prebuilt=True)
S["jar_lid"] = dict(cells=[[0, 0, 0]], at=[-5.93, 1.68, BENCH_TOP - 0.01], centered=False, material="wood",
                    block_shape=[0.68, 0.68, 0.18], expect_blocks=1, prebuilt=True)
S["jar_lid"]["at"][2] = round(BENCH_TOP - 0.01 + 0.09 - 0.1 + 0.018, 4)  # (top flush: lifts the lid onto the jar)
LEAN_BOXES = [((-6.57, 1.13, 1.39), (-5.73, 1.97, 1.51)),                                                 # the roof
              ((-6.53, 1.27, 0.0), (-6.47, 1.33, 1.5)), ((-5.83, 1.27, 0.0), (-5.77, 1.33, 1.5)),        # front posts
              ((-6.53, 1.77, 0.0), (-6.47, 1.83, 1.5)), ((-5.83, 1.77, 0.0), (-5.77, 1.83, 1.5)),        # back posts
              ((-6.4, 1.55, 0.0), (-5.9, 1.75, 0.5))]                                                     # bench
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE + LEAN_BOXES, **kw)
def lean_free(eye):                                                 # the camera never inside the lean-to's roof or posts
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in LEAN_BOXES)
AIR = both(clear_air, lean_free)
PATH = both(solid_free, lean_free)

# ---------------------------------------------------------------- lines (who: tobias -> his voice, his jaw)
LINES = [("way", "Come on. My workshop's this way.", "tobias", None, None),
         ("have", "You have a WORKSHOP?", None, None, None),
         ("grubs", "...Is that a jar of grubs?", None, None, None),
         ("science", "For science.", "tobias", None, None),
         ("book", "And this is how I fixed your machine.", "tobias", None, None),
         ("hand", "Wait. That's... MY handwriting.", None, None, None),
         ("built", "I built that? ...I built that! Why'd I ever stop?", None, None, None),
         ("started", "You stopped building. So I started.", "tobias", None, None),
         ("scale", "Look, chat. One square on the page... is one block out here. That's scale.", None, None, None),
         ("homework", "Mom says homework. School night.", "tobias", None, None),
         ("twelve", "Page twelve. You'll figure it out...", "tobias", None, None),
         ("first", "You did the first time.", "tobias", None, None),
         ("justme", "...Just me, then.", None, None, None),
         ("alone", "Alone. In the woods. Where the boar... lives.", None, None, None),
         ("murmur", "You kinda bussin'... you kinda bussin'...", None, 0.8, dict(aecho="0.8:0.7:180|360:0.35|0.22")),
         ("nope", "Nope. Nope nope nope.", None, 1.05, None),
         ("page", "Page twelve...", None, None, None),
         ("fancy", "Ooh. Fancy. A garden gate... with a lever.", None, None, None),
         ("torn", "Chat... somebody's been tearing pages out of my book.", None, None, None),
         ("hatches", "Chat... batten down the hatches!", None, None, None)]
GUESS = dict(way=1.9, have=1.4, grubs=1.7, science=1.0, book=2.1, hand=2.2, built=3.4, started=2.1, scale=4.6, homework=2.2,
             twelve=2.1, first=1.4, justme=1.2, alone=3.4, murmur=3.9, nope=1.7, page=1.1, fancy=3.2, torn=3.2, hatches=2.1)
dur_file = os.path.join(HERE, "ep01_s006_durations.json")
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

L_HAND, R_HAND = (BOOK[0] - 0.12, BOOK[1] - 0.04, BOOK[2] + 0.05), (BOOK[0] + 0.12, BOOK[1] - 0.04, BOOK[2] + 0.05)
POSES = {
    "set_bench": dict(lean=0.22),
    "read_book": dict(lean=0.3, head=(0.0, -0.2, 0.0), hand_L={"world": list(L_HAND)}, hand_R={"world": list(R_HAND)}),
    "flip_page": dict(lean=0.3, head=(0.0, -0.2, 0.0), hand_L={"world": list(L_HAND)},
                      hand_R={"world": [R_HAND[0] - 0.04, R_HAND[1] + 0.02, R_HAND[2] + 0.02], "wave": [2.4, 0.05]}),
    "built_up": dict(lean=-0.08, hand_L={"char": [0.30, -0.14, 1.02]}, hand_R={"char": [-0.30, -0.14, 1.02]}),   # "I built that!"
    "nervous": dict(shrug=0.7, elbows=0.25, lean=-0.04),
    "peer_down": dict(lean=0.3, head=(0.0, -0.22, 0.0)),
    "admire": dict(lean=0.16, head=(0.0, -0.06, 0.0)),
    "dreamy": dict(head=(0.0, 0.16, 0.10), lean=-0.04),
    "batten": dict(lean=0.06, hand_L={"char": [0.2, -0.22, 0.98]}),     # (the left fist: clear of the posts)
}
CARRY = {"char": [-0.17, -0.18, 0.40]}
G0 = C5["grandpa"]["root"]                                          # (-5.43, 2.42), garden's east edge
T0 = (-6.0, 2.84)                                                   # Tobias, garden's north-west edge
G_WORK = (-6.15, 1.33)                                              # at the bench, facing it (north)
T_SPOT = (-6.66, 1.5)                                               # Tobias, just west of the lean-to
G_OUT = (-5.48, 1.38)                                               # stepped out east, to watch Tobias go
G_IN_VIA = [(-5.41, 1.95), (-5.4, 1.45), (-5.58, 0.98), (-6.02, 0.98)]
CUBE = (-6.35, 1.63)                                                # the webcam on the bench's west end
CAM_YAW = round(math.degrees(math.atan2(G_WORK[0] - CUBE[0], -(G_WORK[1] - CUBE[1]))), 2)   # lens (local -y) toward him
rotz = lambda v, a: (v[0] * math.cos(math.radians(a)) - v[1] * math.sin(math.radians(a)), v[0] * math.sin(math.radians(a)) + v[1] * math.cos(math.radians(a)))
_o = rotz((0.0, -0.1), CAM_YAW)
CAM_ROOT = [round(CUBE[0] - _o[0], 4), round(CUBE[1] - _o[1], 4), round(BENCH_TOP - 0.30, 3)]
deg = lambda a, b: round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 1)
face("surprised", -5.0, 0.3, set=dict(C5["grandpa"]["face"]))
act(type="face_camera", when=-5.0, until=0.3)

# 1. to the workshop
s, e = say("way", 0.0, at=0.35)
T_GO = s + 0.4
G_GO = s + 0.9
G_ARR = G_GO + 3.7
walk(G_GO, G_ARR, G_WORK, via=G_IN_VIA)
s, e = say("have", 0.25)
face("surprised", s - 0.1, e + 0.3, set=dict(brow=1.0))
T_ARR = T_GO + 3.2
# 2. Rule 2: the webcam goes down on the bench, pointed at him
SET_T = G_ARR + 0.55
pose("set_bench", SET_T - 0.5, SET_T + 0.4, ease=0.3)
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R", when=-1.0, until=round(SET_T, 3), reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CARRY, rot=[0, 0, 0]), dict(t=round(SET_T - 0.5, 3), at=CARRY, rot=[0, 0, 0]),
              dict(t=round(SET_T, 3), at=CAM_ROOT, rot=[0, 0, CAM_YAW])])
sfx("settle", SET_T - 0.05, 0.4)
look(G_ARR - 0.4, SET_T + 0.3, pos=(CUBE[0], CUBE[1], 0.55), body=True, rate=0.15)
# 3. the grub jar
s, e = say("grubs", 0.2, at=SET_T + 0.35)
look(s - 0.3, e + 0.4, pos=(-5.93, 1.68, 0.55), body=True, rate=0.15)
face("squint", s, e + 0.3)
s, e = say("science", 0.25)
face("side_eye", s, e + 0.4)
# 4. the book: his own handwriting
s, e = say("book", 0.3)
T_POINT = s + 0.3
look(s, e + 0.2, pos=(T_SPOT[0], T_SPOT[1], 0.7), body=False)
s, e = say("hand", 0.35)
LOOK_B = len(A); look(s - 0.5, 99.0, pos=BOOK, body=True, rate=0.15)
pose("read_book", s - 0.4, e + 4.0, ease=0.35)
face("surprised", s + 0.6, e + 0.4, set=dict(brow=1.1, smile=0.0))
s, e = say("built", 0.3)
B_UP = s + 1.4                                                      # "...I built that!"
pose("built_up", B_UP, B_UP + 1.3, ease=0.25)
face("smile", B_UP - 0.1, B_UP + 1.2, set=dict(smile=1.0, brow=0.8))
face("worried", B_UP + 1.3, e + 0.3)
s, e = say("started", 0.4)
LOOK_T = len(A); look(s - 0.4, e + 0.8, pos=(T_SPOT[0], T_SPOT[1], 0.7), body=False)
face("warm", s + 0.3, e + 0.9)
# 5. micro-lesson: scale (an insert of the page)
s, e = say("scale", 0.5)
pose("read_book", s - 0.3, e + 0.2, ease=0.3)
look(s - 0.3, e + 0.2, pos=BOOK, body=False)
face("raised", s, e)
SCALE0, SCALE1 = s, e
# 6. Tobias's graceful exit (homework; school night) -- he was the 4th viewer: the count drops
BUZZ = e + 0.3
sfx("buzz", BUZZ, 0.8)
s, e = say("homework", 0.35, at=BUZZ + 0.6)
TAB0, TAB1 = BUZZ + 0.15, e + 0.2
look(BUZZ, LE["homework"] + 0.6, pos=(T_SPOT[0], T_SPOT[1], 0.7), body=True, rate=0.15)
face("worried", s + 0.2, e + 0.6, set=dict(smile=0.0))
s, e = say("twelve", 0.3)
s, e = say("first", 0.25)
face("warm", s, e + 0.6)
T_LEAVE = e + 0.3
T_GONE = T_LEAVE + 3.6
VIEW_DROP = T_GONE - 0.8                                            # he logs off as he walks out of sight
# 7. alone: stepping out to watch him go
OUT0 = T_LEAVE + 0.5
OUT1 = OUT0 + 1.6
A[LOOK_B]["until"] = round(OUT0, 3)
walk(OUT0, OUT1, G_OUT, via=[(-6.02, 0.98), (-5.6, 0.98)])
look(OUT1 - 0.2, T_GONE + 0.4, pos=(-5.7, 4.6, 0.7), body=True, rate=0.12)
s, e = say("justme", 0.0, at=max(VIEW_DROP + 0.5, OUT1 + 0.2))
face("worried", s - 0.2, e + 0.5)
s, e = say("alone", 0.45)
pose("nervous", s - 0.1, e + 0.4, ease=0.3)
look(s, s + 1.0, pos=(-6.9, 2.2, 0.8), body=False)                   # glances at the dark woods...
look(s + 1.0, s + 2.0, pos=(-6.3, 0.2, 0.8), body=False)            # ...the other way...
look(s + 2.0, e + 0.6, pos=(-4.5, 1.0, 0.8), body=False)            # ...then the machine, the boar alarm
face("worried", s, e + 0.6, set=dict(brow=0.9))
# 8. the flashback: the picture ripples, the cloud drifts in, the real "You kinda bussin'!" echoes three times
DREAM0 = e + 0.35
ECHO_T = DREAM0 + 0.5
ECHO_REPS = 3
act(type="sfx", sound="echo|grandpa_ep01_scene004|bussin|%d" % ECHO_REPS, when=round(ECHO_T, 3), gain=0.9)
s, e = say("murmur", 0.0, at=ECHO_T + 2.5)                          # he hears it twice, then says it along with it
pose("dreamy", DREAM0 + 0.2, e + 0.8, ease=0.5)
face("content", DREAM0 + 0.2, e + 0.8, set=dict(lid=0.45, smile=0.45))
DREAM1 = max(e + 0.7, ECHO_T + 1.25 * (ECHO_REPS - 1) + 1.2)
act(type="face_camera", when=round(DREAM0, 3), until=round(DREAM1 + 0.2, 3))
CLOUD_AT = [G_OUT[0] + 0.15, G_OUT[1], 1.58]
CLOUD = dict(kind="memory_cloud", at=CLOUD_AT, visible=[round(DREAM0 + 0.3, 3), round(DREAM1, 3)], yaw=180.0,
             boar=dict(huffs=[round(ECHO_T + 0.4 + 1.25 * k, 3) for k in range(ECHO_REPS)],
                       stomps=[round(ECHO_T + 0.9 + 1.25 * k, 3) for k in range(ECHO_REPS - 1)],
                       clacks=[round(ECHO_T + 1.6, 3)]))
# 9. snap out of it -- and hurry back to the book
s, e = say("nope", 0.15, at=DREAM1 + 0.1)
pose("head_shake", s - 0.05, e + 0.1)
face("alert", s - 0.1, e + 0.4)
BACK0 = e + 0.1
BACK1 = BACK0 + 1.3
walk(BACK0, BACK1, G_WORK, via=[(-5.6, 0.98), (-6.02, 0.98)])
look(BACK1 - 0.3, 99.0, pos=BOOK, body=True, rate=0.18)
# 10. page twelve: the drawing lifts off the paper
FLIP = BACK1 + 0.3
pose("flip_page", FLIP, FLIP + 1.1, ease=0.2)
sfx("page", FLIP + 0.15, 0.7)
sfx("page", FLIP + 0.6, 0.6)
s, e = say("page", 0.0, at=FLIP + 0.3)
H0 = e + 0.3
HOLO = dict(kind="hologram", model="lever_gate", at=[BOOK[0], BOOK[1], round(BOOK[2] + 0.03, 3)], visible=[round(H0, 3), round(H0 + 3.4, 3)],
            size=0.75, yaw=0.0)
pose("admire", H0 - 0.2, H0 + 3.6, ease=0.35)
s, e = say("fancy", 0.0, at=H0 + 0.8)
face("raised", s - 0.2, e + 0.3, set=dict(smile=0.6))
# 11. the torn pages
s, e = say("torn", 0.45, at=H0 + 3.6)
pose("read_book", s - 0.6, s + 1.4, ease=0.3)
face("confused", s - 0.3, s + 1.2)
act(type="face_camera", when=round(s + 1.0, 3), until=99.0)
face("worried", s + 1.2, e + 0.4, set=dict(brow=1.0))
# 12. the hook
s, e = say("hatches", 0.45)
pose("batten", s + 0.2, 99.0, ease=0.25)
face("alert", s - 0.1, 99.0, set=dict(brow=-0.4, smile=0.0))
END = e + 0.8
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# the machine keeps running on its clock; the prop stays where Tobias tossed it
PERIOD, CAM_GAP = 3.3, 0.55
TRIP5 = [a for a in S5["actions"] if a["type"] == "trip"][0]
FIRST = TRIP5["first"] - F5
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

# ---------------------------------------------------------------- Tobias (bl_cast)
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[round(t0, 3), pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / sum(seg); out.append([round(tt, 3), p[0], p[1]])
    return out
T_IN = [T0, (-6.3, 2.62), (-6.36, 1.95), T_SPOT]
T_OUT = [T_SPOT, (-6.36, 1.95), (-6.2, 2.9), (-5.95, 3.4), (-5.75, 4.1), (-5.68, 4.9)]
path = [[0.0, T0[0], T0[1]]] + keyed(T_GO, T_ARR, T_IN) + keyed(T_LEAVE, T_GONE, T_OUT)[1:]
TO_G = deg(T_SPOT, G_WORK)
tobias = dict(kind="tobias", stride=0.16, seed=11, path=path,
              yaw=[[-1.0, deg(T0, G0)], [round(T_ARR, 3), deg(T_SPOT, BOOK)], [round(LS["started"] - 0.3, 3), TO_G],
                   [round(LE["started"] + 0.5, 3), deg(T_SPOT, BOOK)], [round(BUZZ, 3), TO_G]],
              tablet=[[round(TAB0, 3), round(TAB1, 3)]],
              poses=[[-1.0, round(FILM + 1.0, 3), "notebook_L"], [round(LS["way"], 3), round(LE["way"] + 0.2, 3), "point_R"],
                     [round(T_POINT, 3), round(T_POINT + 1.8, 3), "point_down"], [round(TAB0, 3), round(TAB1, 3), "hold_tablet"],
                     [round(LS["first"], 3), round(LE["first"], 3), "easy_R"]],
              faces=[[-1.0, "smile"], [round(LS["science"], 3), "deadpan"], [round(LE["science"] + 0.4, 3), "calm"],
                     [round(LS["started"], 3), "calm"], [round(LS["homework"], 3), "deadpan"], [round(LS["first"], 3), "smile"]],
              look=[[round(T_POINT, 3), round(T_POINT + 1.8, 3), list(BOOK)]],
              visible=[-1.0, round(T_GONE, 3)])

# ---------------------------------------------------------------- lines -> bl_voice
lines = []
for i, (lid, text, who, speed, fx) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if who: ln["who"] = who
    if speed: ln["speed"] = speed
    if fx: ln["fx"] = fx
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["hatches"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (forest rules, as in Scene 005)
def box_at(p, r=0.17, h=1.2):
    return ((p[0] - r, p[1] - r, 0.0), (p[0] + r, p[1] + r, h))
def kid(x, y):
    return [(x, y, 0.05), (x, y, 0.45), (x, y, 0.80)]
def g_in(x, y):                                                     # under the roof, across the bench: chest and face
    return [(x, y, 0.75), (x, y, 1.0)]
def kid_in(x, y):
    return [(x, y, 0.45), (x, y, 0.75)]
STOPS = [(0.0, G0[:2]), (G_GO, G0[:2])]
for leg_t0, leg_t1, pts in ((G_GO, G_ARR, [G0[:2]] + G_IN_VIA + [G_WORK]), (OUT0, OUT1, [G_WORK, (-6.02, 0.98), (-5.6, 0.98), G_OUT]),
                            (BACK0, BACK1, [G_OUT, (-5.6, 0.98), (-6.02, 0.98), G_WORK])):
    STOPS += [(p[0], (p[1], p[2])) for p in keyed(leg_t0, leg_t1, pts)[1:]]
    STOPS.append((leg_t1 + 0.001, pts[-1]))
STOPS.sort(key=lambda s: s[0])
def g_at(t):
    for (t0, a), (t1, b) in zip(STOPS, STOPS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); return [a[i] + (b[i] - a[i]) * u for i in range(2)]
    return list(STOPS[-1][1]) if t > STOPS[-1][0] else list(G0[:2])
who_at = lambda t: gp(*g_at(t))
L_BENCH = make_los([box_at(G_WORK), box_at(T_SPOT, 0.12, 0.85)])
L_OUT = make_los([box_at(G_OUT)])
BOOK_PTS = [(BOOK[0] - 0.11, BOOK[1] - 0.07, BOOK[2]), (BOOK[0] + 0.11, BOOK[1] + 0.07, BOOK[2])]
last = C5["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
CUT_INS = math.ceil((SCALE0 + 0.4) * FPS - 1e-6) / FPS
NORTH = facing(G_WORK, 90, 30)
CLOUD_PTS = gp(*G_OUT)[1:] + [(CLOUD_AT[0], CLOUD_AT[1], 2.05), (CLOUD_AT[0] - 0.42, CLOUD_AT[1], 1.6), (CLOUD_AT[0] + 0.42, CLOUD_AT[1], 1.6)]                                       # his face, at the bench
SHOTS = [
    # (the walk plays on Scene 005's last framing: they walk toward us; we cut in as he reaches the bench)
    # at the bench: Grandpa, the book, the jar, Tobias beside
    lambda: auto_frame(G_ARR - 2.0, g_in(*G_WORK) + kid_in(*T_SPOT) + [(-5.93, 1.68, 0.55)], (-6.3, 1.5, 0.75), 65, 11, 1.9,
                       both(AIR, NORTH), prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
    # "MY handwriting": closer, his face over the book
    lambda: auto_frame(LS["hand"] + 0.3, g_in(*G_WORK) + BOOK_PTS, (G_WORK[0], 1.45, 0.85), 62, 17, 1.75,
                       both(AIR, NORTH), prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
    # "You stopped building. So I started.": the two-shot
    lambda: auto_frame(LS["started"] - 0.2, g_in(*G_WORK) + kid_in(*T_SPOT), (-6.4, 1.42, 0.75), 65, 8, 1.9,
                       both(AIR, NORTH), apart=((G_WORK[0], G_WORK[1], 0.95), (T_SPOT[0], T_SPOT[1], 0.68)), apart_min=0.3,
                       prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
    # the scale lesson: an insert of the page (cutaway)
    lambda: [dict(cam[-1], at=round(CUT_INS - 1.0 / FPS, 4)),                       # a hard cut to the page (no push in)
             auto_frame(CUT_INS, BOOK_PTS, (BOOK[0], BOOK[1], BOOK[2]), 100, 55, 0.75, AIR, los=make_los([]))],
    # the tablet buzz and the exit: Tobias leaves, north, past the garden
    lambda: auto_frame(BUZZ + 0.2, g_in(*G_WORK) + kid_in(*T_SPOT) + [(-5.93, 1.68, 0.55)], (-6.3, 1.5, 0.75), 65, 11, 1.9,
                       both(AIR, NORTH), prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
    lambda: auto_frame(T_LEAVE + 1.9, g_in(*G_WORK) + kid(-6.2, 2.9), (-6.1, 2.3, 0.7), 60, 16, 2.8, AIR,
                       prev=cam, path_clear=PATH, los=make_los([]), who=who_at),
    # alone: "...Just me, then." / "Alone. In the woods."
    lambda: auto_frame(LS["justme"] - 0.2, gp(*G_OUT), (G_OUT[0], G_OUT[1], 0.95), 95, 8, 2.0, AIR,
                       prev=cam, path_clear=PATH, los=L_OUT, who=who_at),
    # the flashback: a slow push in, cloud and all
    lambda: auto_frame(DREAM0 + 0.4, CLOUD_PTS, (G_OUT[0] + 0.08, G_OUT[1], 1.3), 95, 8, 2.4, AIR,
                       prev=cam, path_clear=PATH, los=L_OUT, who=who_at),
    # back at the book: page twelve lifts off
    lambda: auto_frame(H0 + 0.2, g_in(*G_WORK) + BOOK_PTS + [(BOOK[0], BOOK[1], BOOK[2] + 0.42)], (G_WORK[0], 1.48, 0.8), 62, 20, 1.75,
                       both(AIR, NORTH), prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
    # torn pages, and the hook
    lambda: auto_frame(LS["torn"] + 1.0, g_in(*G_WORK), (G_WORK[0], G_WORK[1], 0.92), 65, 8, 1.9,
                       both(AIR, NORTH), prev=cam, path_clear=PATH, los=L_BENCH, who=who_at),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
    if CLOUD.get("face") is None and cam[-1]["at"] >= DREAM0:       # the cloud's stage (and its mini boar) faces that camera
        CLOUD["face"] = cam[-1]["az"] + 90
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C5["overlay"]["live_viewers"]], [round(VIEW_DROP, 3), 3]]),
         dict(style="panel", y="top", border="amber", when=round(SCALE0 + 0.3, 3), until=round(SCALE1 + 0.4, 3), rows=[
             dict(text="SCALE", color="white", at=round(SCALE0 + 0.4, 3), size=40),
             dict(text="1 square = 1 block", color="cyan", at=round(SCALE0 + 2.0, 3), size=32)]),
         dict(style="dream", when=round(DREAM0, 3), until=round(DREAM1 + 0.1, 3)),
         dict(style="panel", y="top", border="cyan", when=round(H0 + 0.3, 3), until=round(H0 + 3.4, 3), rows=[
             dict(text="PAGE 12", color="white", at=round(H0 + 0.4, 3), size=40),
             dict(text="a garden gate with a lever", color="cyan", at=round(LS["fancy"] + 1.4, 3), size=32)])]
W6 = {k: v for k, v in S5["world"].items() if k != "critters"}
W6["critters"] = [tobias, CLOUD, HOLO]
story = dict(title="Page Twelve", slug="grandpa_ep01_scene006", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["way"], tail=round(tail, 4), seed=29, blink=True, target_duration=60,
             engine_rev=3, scene=dict(episode=1, scene=6, name="Page Twelve", previous="ep01_scene005", next="ep01_scene007"),
             world=W6, lines=lines, grandpa=dict(start=list(G0), outfit=S5["grandpa"]["outfit"]),
             poses=dict(S5["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["webcam", "bench"], ["book", "bench"], ["jar", "bench"]],
                     frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve", "lean_posts", "bench_legs"],
                     cutaways=[[round(CUT_INS, 3), round(BUZZ + 0.2, 3)]]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene006.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, _, who, *_ in LINES:
    print("  %-9s %-7s %6.2f-%6.2f" % (lid, who or "grandpa", LS[lid], LE[lid]))
print("arrive %.2f set %.2f buzz %.2f leave %.2f-%.2f drop %.2f dream %.2f-%.2f holo %.2f" % (G_ARR, SET_T, BUZZ, T_LEAVE, T_GONE, VIEW_DROP, DREAM0, DREAM1, H0))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
