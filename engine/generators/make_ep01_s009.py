"""Grandpa's Block Lab, Episode 1, Scene 009 -- "Page Thirteen" (16:9, ~65 s). Approved beat sheet (2026-10-22).
Blueprint Build, Grandpa solo (Tobias only in chat). Starts from Scene 008's end beside the finished garden, the book in
his left hand, the bottle drifting downstream. It bumps past the waterwheel and snags on the bank by the path; he fishes
it out: page thirteen, an electric fence. Chat: "dont zap him!!" -- "It's a tickle... with attitude." A plain kid-safety
line. The build: white spools on the posts, the wire round the fence, a ticking box with a little solar panel. Oops: the
tester stays dark. Why: a loop (lesson: CIRCUIT). Fix: the ground rod goes in (CLANG); the tester lights. "It's ALIVE!"
Hook: the light goes golden, a huff from the woods, closer. "...Tonight, then."
He never touches the wire (a tester does). The boar is never harmed.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both
from forest_camkit import make_los as _make_los
FPS = 30
S8 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene008.json"))
C8 = json.load(open(os.path.join(HERE, "s8work/build/continuity.json")))
F8 = C8["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 008 left it
def root_of(name):
    r = C8["structures"][name]["root"]
    return [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)], round(math.degrees(math.atan2(r[1][0], r[0][0])), 2)
for name, st in S8["structures"].items():
    if C8["structures"][name]["blocks_standing"] == 0:
        continue
    st = json.loads(json.dumps(st))
    if name in ("pivot_post", "gate_arm", "stub_rock"):
        st["prebuilt"] = True                                       # built in Scene 008
    S[name] = st
PROP_OUT = root_of("prop")[0]
BOTTLE0 = root_of("bottle")[0]
for name in ("book", "pages", "bottle"):                            # the holds place them
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
# ---------------------------------------------------------------- page thirteen (rolled up in the bottle: he pulls it out)
INK13 = []
def _line(x0, y0, x1, y1, w, z, m):
    return dict(c=[round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4), z], s=[round(max(abs(x1 - x0), w), 4), round(max(abs(y1 - y0), w), 4), 0.0014], m=m)
for k in range(9):
    INK13.append(_line(-0.065 + 0.0162 * k, -0.045, -0.065 + 0.0162 * k, 0.045, 0.0012, 0.1006, "blue"))
for k in range(6):
    INK13.append(_line(-0.07, -0.042 + 0.0168 * k, 0.07, -0.042 + 0.0168 * k, 0.0012, 0.1006, "blue"))
for (a, b, c_, d) in ((-0.05, -0.02, 0.05, -0.02), (-0.05, 0.0, 0.05, 0.0), (-0.04, -0.03, -0.04, 0.015), (0.0, -0.03, 0.0, 0.015),
                      (0.04, -0.03, 0.04, 0.015), (-0.01, 0.022, 0.012, 0.022), (0.012, 0.022, -0.006, 0.034), (-0.006, 0.034, 0.016, 0.034)):
    INK13.append(_line(a, b, c_, d, 0.003, 0.1009, "darkiron"))     # a fence with two wires; a little lightning bolt
S["page13"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="paper", block_shape=[1.5, 1.0, 0.1], expect_blocks=1,
                   extras=INK13)
# ---------------------------------------------------------------- the electric fence (built on camera)
SIDE = {"s": ([(x, 15) for x in range(-38, -22) if x not in range(-32, -28)], [0.0, -0.06, 0.0], [1, 0.1, 0.1]),
        "w": ([(-38, y) for y in range(15, 31)], [-0.06, 0.0, 0.0], [0.1, 1, 0.1]),
        "n": ([(x, 30) for x in range(-38, -22)], [0.0, 0.06, 0.0], [1, 0.1, 0.1]),
        "e": ([(-23, y) for y in range(15, 31)], [0.06, 0.0, 0.0], [0.1, 1, 0.1])}
POSTS = {"s": [(-38, 15), (-33, 15), (-28, 15), (-23, 15)], "w": [(-38, 20), (-38, 25), (-38, 30)],
         "n": [(-33, 30), (-28, 30), (-23, 30)], "e": [(-23, 20), (-23, 25)]}
for k, (cells, off, shape) in SIDE.items():
    S["wire_" + k] = dict(cells=[[x, y, z] for x, y in cells for z in (2, 3)], at=off, centered=False, material="steel", block_shape=shape,
                          expect_blocks=2 * len(cells))
    S["spools_" + k] = dict(cells=[[x, y, z] for x, y in POSTS[k] for z in (2, 3)], at=[v * 0.55 for v in off], centered=False,
                            material="ceramic", block_shape=[0.35, 0.35, 0.3], expect_blocks=2 * len(POSTS[k]))
BOX = (-2.4, 1.3)
S["energizer"] = dict(cells=[[-24, 13, 0], [-24, 13, 1]], at=[0.0, 0.0, 0.0], centered=False, material="darkiron", block_shape=[0.9, 0.7, 1],
                      expect_blocks=2, extras=[dict(c=[-2.4, 1.3, 0.208], s=[0.17, 0.12, 0.012], m="blue"),        # the solar panel
                                               dict(c=[-2.4, 1.263, 0.15], s=[0.016, 0.006, 0.016], m="led")])     # its own little light
S["ground_rod"] = dict(cells=[[-24, 11, z] for z in range(3)], at=[0.0, 0.0, 0.0], centered=False, material="steel", block_shape=[0.25, 0.25, 1],
                       expect_blocks=3)
S["tester"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="red", block_shape=[0.25, 1.3, 0.25], expect_blocks=1,
                   extras=[dict(c=[0.0, 0.07, 0.088], s=[0.006, 0.02, 0.006], m="steel")])     # the probe tip
S["tester_led"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="ceramic", block_shape=[0.12, 0.12, 0.12],
                       expect_blocks=1, extras=[dict(c=[0.0, -0.05, 0.1], s=[0.018, 0.018, 0.012], m="led")])
STREAM_X = lambda y: -5.2 + 0.25 * math.sin(0.7 * y)
FENCE_BOXES = [((-3.9, 1.4, 0.0), (-2.2, 1.56, 0.5)), ((-3.9, 1.4, 0.0), (-3.74, 3.1, 0.5)),
               ((-3.9, 2.94, 0.0), (-2.2, 3.1, 0.5)), ((-2.36, 1.4, 0.0), (-2.2, 3.1, 0.5)), ((-3.33, 1.36, 0.0), (-2.57, 1.44, 0.9))]
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE, **kw)
def boxes_free(eye):
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in FENCE_BOXES)
AIR = both(clear_air, boxes_free)
PATH = both(solid_free, boxes_free)

# ---------------------------------------------------------------- lines
LINES = [("mail", "Chat... somebody's mailing me my own book.", None),
         ("page", "Page thirteen. An electric fence.", None),
         ("relax", "Relax, BoarFan. It doesn't hurt him. It's a tickle... with attitude.", None),
         ("safety", "And kids: never touch one, and never build one without a grown-up who knows how. I'm a grown-up. Allegedly.", None),
         ("spools", "Little spools, so the wire never touches the wood.", None),
         ("sun", "The sun charges the box. The box sends a tiny pulse. Tick... tick... tick.", None),
         ("truth", "Moment of truth...", None),
         ("nothing", "...Nothing.", None),
         ("loop", "Ohh. Electricity only travels in a loop. Out the wire, through whoever touches it, into the ground... and back to the box.", None),
         ("norod", "No rod, no loop.", None),
         ("alive", "It's alive. It's ALIVE!", None),
         ("late", "Chat, it's getting late.", None),
         ("tonight", "...Tonight, then.", 0.9)]
GUESS = dict(mail=2.6, page=2.3, relax=4.5, safety=6.5, spools=3.0, sun=5.0, truth=1.4, nothing=1.0, loop=7.0, norod=1.4, alive=2.0,
             late=1.6, tonight=1.3)
dur_file = os.path.join(HERE, "ep01_s009_durations.json")
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
def build(name, t0, t1, at, order="z", quiet=False):
    act(type="build", target=name, when=t0, until=t1, stand_at=[at[0], at[1], 0.0], order=order, **({"quiet": True} if quiet else {}))

POSES = {
    "crouch_reach": dict(lean=0.65, hips=[0.0, 0.0, -0.22]),
    "read_both": dict(head=(0.0, -0.22, 0.0)),
    "test_low": dict(lean=0.35, hips=[0.0, 0.0, -0.08]),
    "push_rod": dict(lean=0.55, hips=[0.0, 0.0, -0.14], hand_R={"world": [-2.4, 1.1, 0.34]}),
    "arms_up": dict(lean=-0.1, hand_R={"char": [-0.24, -0.1, 1.15]}),
    "freeze": dict(shrug=0.6, elbows=0.2, lean=-0.05),
}
BOOK_CARRY_B = {"char": [0.17, -0.2, 0.80]}
BOOK_CARRY_P = {"char": [0.17, -0.2, 0.81]}
G0 = C8["grandpa"]["root"][:2]                                      # (-3.0, 0.72)
G_FISH = (-4.55, 0.36)                                              # on the bank, south of the wheel
BOT_SNAG = (-4.78, 0.3, 0.0)                                        # the bottle bumps up onto the bank stones here
G_READ = (-3.6, 0.92)                                               # back by the bank stone (webcam), reading
STAND = {"s": (-3.42, 1.16), "w": (-4.04, 2.25), "n": (-3.05, 3.36), "e": (-1.98, 2.25)}
G_BOX = (-2.4, 0.86)                                                # south of the box and the rod
G_TEST = (-3.42, 1.08)                                              # testing the south wire between two posts (clear of the bank stone)
TIP = (-3.5, 1.43, 0.395)                                           # the tester's tip on the upper wire
TEST_ROOT = [TIP[0], TIP[1] - 0.06, round(TIP[2] - 0.09, 3)]
TEST_CARRY = {"char": [-0.14, -0.24, 0.62]}
HIDE = [0.0, 0.0, -5.0]
for name, carry in (("book", BOOK_CARRY_B), ("pages", BOOK_CARRY_P)):
    act(type="hold", target=name, hand="L", when=-1.0, until=99.0, reach=0.05, grip=[0.0, -0.07, 0.09],
        keys=[dict(t=-1.0, at=carry, rot=[0, 0, 0]), dict(t=99.0, at=carry, rot=[0, 0, 0])])
face("surprised", -5.0, 0.4, set=dict(C8["grandpa"]["face"]))

# 1. the bottle bumps downstream, past the wheel, and snags; he fishes it out
BOT_T1 = 4.2
bkeys = [dict(t=-1.0, at=BOTTLE0, rot=[0, 0, 0])]
for k in range(1, 11):
    u = k / 10; t = BOT_T1 * u
    y = BOTTLE0[1] + (BOT_SNAG[1] - BOTTLE0[1]) * u
    x = STREAM_X(y) + 0.1 + (0.1 if 0.4 < y < 1.7 else 0.0)        # (it nudges round the east side of the wheel)
    if k == 10: x = BOT_SNAG[0]
    bkeys.append(dict(t=round(t, 3), at=[round(x, 4), round(y, 4), round(-0.065 + 0.008 * math.sin(5 * t), 4)], rot=[round(6 * math.sin(3 * t), 2), 0, round(10 * math.sin(1.3 * t), 2)]))
walk(0.4, 3.4, G_FISH, via=[(-3.4, 0.6), (-4.0, 0.45)])
look(0.0, 3.6, pos=(STREAM_X(1.2) + 0.15, 1.2, 0.05), body=False, rate=0.3)
PICK = 4.4
pose("crouch_reach", PICK - 0.5, PICK + 0.4, ease=0.3)
look(3.4, PICK + 0.3, pos=BOT_SNAG, body=True, rate=0.3)
BCARRY = {"char": [-0.14, -0.24, 0.62]}
bkeys += [dict(t=round(PICK, 3), at=list(BOT_SNAG), rot=[0, 0, 0])]
act(type="hold", target="bottle", hand="none", when=-1.0, until=round(PICK - 0.3, 3), reach=0.05, keys=bkeys)   # drifting, then snagged
sfx("clink", PICK, 0.4)
OUT = PICK + 1.2                                                    # the page comes out of the bottle...
act(type="hold", target="bottle", hand="R", when=round(PICK, 3), until=round(OUT + 0.6, 3), reach=0.4, grip=[0.0, -0.05, 0.1],
    keys=[dict(t=round(PICK, 3), at=list(BOT_SNAG), rot=[0, 0, 0]), dict(t=round(PICK + 0.5, 3), at=BCARRY, rot=[0, 0, 0]),
          dict(t=round(OUT + 0.6, 3), at=BCARRY, rot=[0, 0, 0])])
act(type="hold", target="bottle", hand="none", when=round(OUT + 0.72, 3), until=99.0, reach=0.05,     # ...and he tosses it aside
    keys=[dict(t=round(OUT + 0.72, 3), at=BCARRY, rot=[0, 0, 0]), dict(t=round(OUT + 1.05, 3), at=[-4.25, 0.72, 0.0], rot=[0, 0, 90]),
          dict(t=99.0, at=[-4.25, 0.72, 0.0], rot=[0, 0, 90])])
sfx("clink", OUT + 0.95, 0.3)
PCARRY = {"char": [-0.06, -0.26, 0.86]}
build("page13", OUT + 1.25, OUT + 1.35, G_FISH, quiet=True)
s, e = say("mail", 0.0, at=OUT + 0.2)
face("confused", s, e + 0.3)
P_HOLD = len(A)
act(type="hold", target="page13", hand="R", when=round(OUT + 1.3, 3), until=99.0, reach=0.3, grip=[0.0, -0.05, 0.1],
    keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(OUT + 1.24, 3), at=HIDE, rot=[0, 0, 0]), dict(t=round(OUT + 1.25, 3), at=BCARRY, rot=[0, 0, 0]),
          dict(t=round(OUT + 1.7, 3), at=PCARRY, rot=[0, 0, 0])])
sfx("page", OUT + 1.4, 0.6)
G_READ = (-3.25, 0.9)                                               # back toward the garden, reading as he goes
walk(OUT + 1.9, OUT + 4.4, G_READ, via=[(-4.0, 0.5), (-3.5, 0.62)])
pose("read_both", OUT + 1.6, OUT + 2.0, ease=0.25)
s, e = say("page", 0.3, at=OUT + 1.8)
face("raised", s, e + 0.3, set=dict(smile=0.4))
# 2. chat: "dont zap him!!" -- the safety line
ZAP = e + 0.2
s, e = say("relax", 0.9)
act(type="face_camera", when=round(s - 0.3, 3), until=round(e + 0.2, 3))
face("side_eye", s, s + 1.4)
face("smirk", s + 1.4, e + 0.3)
s, e = say("safety", 0.4)
act(type="face_camera", when=round(s - 0.2, 3), until=round(e + 0.2, 3))
face("raised", s, e - 1.2, set=dict(brow=0.6))
face("smirk", e - 1.2, e + 0.3)
# the page goes onto the open book: his right hand is free to build
A[P_HOLD]["keys"] += [dict(t=round(e + 0.2, 3), at=PCARRY, rot=[0, 0, 0]), dict(t=round(e + 0.7, 3), at={"char": [0.17, -0.2, 0.83]}, rot=[0, 0, 0])]
A[P_HOLD]["until"] = round(e + 0.7, 3)
PAGE_ON_BOOK = e + 0.7
act(type="hold", target="page13", hand="none", when=round(e + 0.82, 3), until=99.0, reach=0.05,
    keys=[dict(t=round(e + 0.82, 3), at={"char": [0.17, -0.2, 0.83]}, rot=[0, 0, 0]), dict(t=99.0, at={"char": [0.17, -0.2, 0.83]}, rot=[0, 0, 0])])
# 3. the build: spools and wire round the fence, the box with its solar panel
B0 = e + 0.4
walk(B0, B0 + 0.8, STAND["s"])
T = B0 + 1.3
look(T - 0.2, T + 2.3, pos=(-3.2, 1.45, 0.35), body=True, rate=0.3)
build("spools_s", T, T + 0.6, STAND["s"], "x"); build("wire_s", T + 0.65, T + 2.0, STAND["s"], "x"); T += 2.05
s, e = say("spools", 0.0, at=B0 + 1.6)
walk(T, T + 1.3, STAND["w"], via=[(-3.42, 0.92), (-4.12, 0.9), (-4.06, 1.5)])
T += 1.4
look(T - 0.2, T + 1.6, pos=(-3.86, 2.25, 0.35), body=True, rate=0.3)
build("spools_w", T, T + 0.4, STAND["w"], "y"); build("wire_w", T + 0.45, T + 1.4, STAND["w"], "y"); T += 1.45
walk(T, T + 1.2, STAND["n"], via=[(-4.35, 2.75), (-4.35, 3.35), (-3.9, 3.42)])
T += 1.3
look(T - 0.2, T + 1.6, pos=(-3.05, 3.06, 0.35), body=True, rate=0.3)
build("spools_n", T, T + 0.4, STAND["n"], "x"); build("wire_n", T + 0.45, T + 1.4, STAND["n"], "x"); T += 1.45
walk(T, T + 0.8, STAND["e"], via=[(-2.0, 3.48)])
T += 0.9
look(T - 0.2, T + 1.6, pos=(-2.24, 2.25, 0.35), body=True, rate=0.3)
build("spools_e", T, T + 0.4, STAND["e"], "y"); build("wire_e", T + 0.45, T + 1.4, STAND["e"], "y"); T += 1.45
walk(T, T + 1.0, G_BOX, via=[(-1.98, 1.2), (-2.2, 0.9)])
T += 1.1
look(T - 0.2, T + 1.4, pos=(BOX[0], BOX[1], 0.15), body=True, rate=0.3)
build("energizer", T, T + 0.8, G_BOX); T += 0.85
BOX_ON = T
for k in range(int(30)):                                            # the box ticks, once a second, from now on
    sfx("tap", BOX_ON + 0.3 + k * 1.0, 0.25)
s, e = say("sun", 0.2, at=max(T, LE["spools"] + 0.5))
face("content", s, e + 0.3)
# 4. oops: the tester stays dark
walk(e + 0.2, e + 1.4, G_TEST, via=[(-2.9, 0.86)])
TEST0 = e + 1.6
pose("test_low", TEST0 - 0.3, TEST0 + 3.5, ease=0.3)
look(TEST0 - 0.4, TEST0 + 2.6, pos=TIP, body=True, rate=0.3)
TST = len(A)
act(type="hold", target="tester", hand="R", when=round(TEST0 - 0.6, 3), until=99.0, reach=0.3, grip=[0.0, -0.05, 0.1],
    keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(TEST0 - 0.6, 3), at=TEST_CARRY, rot=[0, 0, 0]),
          dict(t=round(TEST0, 3), at=TEST_ROOT, rot=[0, 0, 0]), dict(t=round(TEST0 + 2.4, 3), at=TEST_ROOT, rot=[0, 0, 0]),
          dict(t=round(TEST0 + 3.3, 3), at=TEST_CARRY, rot=[0, 0, 0])])
build("tester", TEST0 - 0.7, TEST0 - 0.6, G_TEST, quiet=True)
s, e = say("truth", 0.0, at=TEST0 - 0.2)
face("raised", s, e + 0.4, set=dict(brow=0.8))
s, e = say("nothing", 0.6)
face("confused", s - 0.2, e + 0.5)
GIVE_UP = e
# 5. why: the page shows a ground rod (lesson card)
s, e = say("loop", 0.4)
LESSON0 = s
look(s - 0.4, s + 1.2, obj="page13", body=False)
pose("read_both", s - 0.4, s + 1.2, ease=0.25)
act(type="face_camera", when=round(s + 1.4, 3), until=round(e + 0.2, 3))
face("raised", s + 0.3, e, set=dict(smile=0.3))
s, e = say("norod", 0.3)
LESSON1 = e
face("smirk", s, e + 0.3)
# 6. fix: the ground rod goes in -- CLANG, CLANG, CLANG -- and the tester lights
F0 = e + 0.3
walk(F0, F0 + 1.2, G_BOX, via=[(-2.9, 0.86)])
build("ground_rod", F0 + 1.3, F0 + 1.7, G_BOX)
for k in range(3):                                                  # pushed down in three shoves
    t = F0 + 2.0 + 0.55 * k
    pose("push_rod", t - 0.25, t + 0.3, ease=0.12)
    act(type="slide", target="ground_rod", by=[0.0, 0.0, -0.07], when=round(t, 3), until=round(t + 0.12, 3), sound="none")
    sfx("clink", t + 0.05, 1.0); sfx("settle", t + 0.07, 0.8)
F1 = F0 + 3.7
walk(F1, F1 + 1.2, G_TEST, via=[(-2.9, 0.86)])
TEST1 = F1 + 1.4
pose("test_low", TEST1 - 0.3, TEST1 + 1.5, ease=0.3)
look(TEST1 - 0.4, TEST1 + 1.4, pos=TIP, body=True, rate=0.3)
A[TST]["keys"] += [dict(t=round(TEST1 - 0.4, 3), at=TEST_CARRY, rot=[0, 0, 0]), dict(t=round(TEST1, 3), at=TEST_ROOT, rot=[0, 0, 0]),
                   dict(t=round(TEST1 + 0.7, 3), at=TEST_ROOT, rot=[0, 0, 0]), dict(t=round(TEST1 + 1.4, 3), at=TEST_CARRY, rot=[0, 0, 0])]
LED_ON = TEST1 + 0.25
act(type="hold", target="tester_led", hand="none", when=-1.0, until=99.0, reach=0.05,
    keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(LED_ON - 0.02, 3), at=HIDE, rot=[0, 0, 0]),
          dict(t=round(LED_ON, 3), at=TEST_ROOT, off=[0.0, -0.04, 0.0], rot=[0, 0, 0]),
          dict(t=round(TEST1 + 0.7, 3), at=TEST_ROOT, off=[0.0, -0.04, 0.0], rot=[0, 0, 0]),
          dict(t=round(TEST1 + 1.4, 3), at=TEST_CARRY, off=[0.0, -0.04, 0.0], rot=[0, 0, 0]),
          dict(t=99.0, at=TEST_CARRY, off=[0.0, -0.04, 0.0], rot=[0, 0, 0])])
build("tester_led", -0.5, -0.4, G0, quiet=True)
face("surprised", LED_ON, LED_ON + 0.8, set=dict(brow=1.2))
s, e = say("alive", 0.0, at=TEST1 + 1.5)                             # (tester lifted away first)
pose("arms_up", s + 0.8, e + 0.6, ease=0.2)
act(type="face_camera", when=round(s, 3), until=round(e + 0.6, 3))
face("smile", s, e + 0.6, set=dict(smile=1.0, brow=1.0))
# 7. the hook: golden light, a huff from the woods -- closer
s, e = say("late", 0.9)
act(type="face_camera", when=round(s - 0.3, 3), until=round(e + 0.2, 3))
face("content", s, e + 0.4)
HUFF = e + 0.5
sfx("huff_far", HUFF, 1.4)
look(HUFF + 0.15, 99.0, pos=(-6.0, 2.4, 0.6), body=False, rate=0.5)
face("alert", HUFF + 0.15, 99.0, set=dict(brow=1.1, smile=0.0))
s, e = say("tonight", 0.0, at=HUFF + 1.4)
act(type="face_camera", when=round(s - 0.2, 3), until=99.0)
END = e + 1.0
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# the machine keeps its clock; the prop stays put
PERIOD, CAM_GAP = 3.3, 0.55
TRIP8 = [a for a in S8["actions"] if a["type"] == "trip"][0]
FIRST = TRIP8["first"] - F8
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
tail = FILM - LE["tonight"] - 0.5 / FPS
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
FENCE_PTS = [(-3.8, 1.5, 0.05), (-2.3, 1.5, 0.5), (-3.8, 3.0, 0.5), (-2.3, 3.0, 0.05)]
LG = make_los([((-3.33, 1.38, 0.1), (-2.57, 1.42, 0.9)), ((-2.84, 1.36, 0.0), (-2.76, 1.44, 0.8))])
last = C8["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
AZ = dict(fish=(100, 22, 3.4), talk=(-40, 8, 1.6), build=(90, 12, 3.4), test=(-140, 22, 3.4), alive=(-40, 12, 2.0), hook=(-60, 8, 3.4))   # (scouted: clear air, clear view)
def cut(t, *a, **kw):
    tc = math.ceil(t * FPS - 1e-6) / FPS
    return lambda: [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), auto_frame(tc, *a, **kw)]
SHOTS = [
    # fishing out the bottle by the wheel
    cut(3.0, gp(*G_FISH)[1:] + [BOT_SNAG], (-4.65, 0.4, 0.45), AZ["fish"][0], AZ["fish"][1], AZ["fish"][2], AIR,
        los=make_los([box_at(G_FISH)], clutter_cast=MACHINE)),
    # "Relax, BoarFan" and the safety line: talking to us
    cut(OUT + 2.6, [(G_READ[0], G_READ[1], 0.75), (G_READ[0], G_READ[1], 1.12), (-3.6, 0.62, 1.1), (-3.6, 0.62, 0.7)], (-3.35, 0.8, 0.9),
        AZ["talk"][0], AZ["talk"][1], 2.2,
        AIR, los=make_los([box_at(G_READ)], clutter_cast=MACHINE)),
    # the build: high and wide, the wire going round the fence
    cut(B0 + 0.2, gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4), AZ["build"][0], AZ["build"][1], AZ["build"][2], AIR, los=LG),
    # the box and the tester
    cut(BOX_ON - 0.6, gp(*G_BOX)[1:] + gp(*G_TEST)[1:] + [(BOX[0], BOX[1], 0.2), TIP], (-2.95, 1.1, 0.5), AZ["test"][0], AZ["test"][1], AZ["test"][2],
        AIR, los=LG),
    # the lesson, to us
    cut(LS["loop"] + 1.3, [(G_TEST[0], G_TEST[1], 0.75), (G_TEST[0], G_TEST[1], 1.12), TIP], (-3.5, 1.2, 0.75), AZ["alive"][0], AZ["alive"][1], AZ["alive"][2],
        AIR, los=LG),
    # back wide for the rod going in
    cut(F0 + 0.9, gp(*G_BOX)[1:] + gp(*G_TEST)[1:] + [(BOX[0], BOX[1], 0.2), TIP], (-2.95, 1.1, 0.5), AZ["test"][0], AZ["test"][1], AZ["test"][2],
        AIR, los=LG),
    # the fix: the rod, the light, "It's ALIVE!"
    cut(LS["alive"] - 0.2, [(G_TEST[0], G_TEST[1], 0.75), (G_TEST[0], G_TEST[1], 1.12), TIP], (-3.5, 1.2, 0.75), AZ["alive"][0], AZ["alive"][1], AZ["alive"][2],
        AIR, los=LG),
    # the hook: golden light over the garden; the woods beyond
    cut(LS["late"] - 0.2, gp(*G_TEST) + FENCE_PTS[:2], (-3.4, 1.6, 0.6), AZ["hook"][0], AZ["hook"][1], AZ["hook"][2], AIR, los=LG),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
CHAT = [(ZAP, "BoarFan2009", "dont zap him!!"),
        (LS["safety"] + 3.0, "GardenGranny", "safety first dear"),
        (LE["loop"] - 1.5, "TobiasBuilds", "boars learn after one tickle. they never forget"),
        (LE["alive"] + 0.4, "lurker_77", "its alive")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C8["overlay"]["live_viewers"]]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="CIRCUIT", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="electricity needs a complete loop", color="cyan", at=round(LESSON0 + 1.4, 3), size=30)])]
W9 = {k: v for k, v in S8["world"].items() if k != "critters"}
W9["critters"] = []
W9["clouds_pass"] = [[round(FILM + 2.0, 3), 4.5, 0.45]]             # the light goes golden-dim toward the end ("it's getting late")
story = dict(title="Page Thirteen", slug="grandpa_ep01_scene009", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["mail"], tail=round(tail, 4), seed=41, blink=True, target_duration=70,
             engine_rev=3, scene=dict(episode=1, scene=9, name="Page Thirteen", previous="ep01_scene008", next="ep01_scene010"),
             world=W9, lines=lines, grandpa=dict(start=list(G0), outfit=S8["grandpa"]["outfit"]),
             poses=dict(S8["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"], ["webcam", "rock"]],
                     frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve", "lean_posts", "bench_legs",
                            "pivot_post", "energizer"] + ["fence_posts_" + k for k in "swne"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene009.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("pick %.2f build %.2f box %.2f test %.2f fix %.2f led %.2f huff %.2f" % (PICK, B0, BOX_ON, TEST0, F0, LED_ON, HUFF))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
