"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone, unnumbered), Scene 01
"The Raid" (16:9, ~60 s). Script approved 2026-10-25: scenes/raccoon_lift/scene01_script.md.
Cold open (the crate raided, a cabbage rolls to the lens), the Morning Ritual (webcam tap, coffee, the regulars log in,
greeting), the clue (prints like tiny hands; lesson: look for clues before you guess), the sincere safety line, the build
(the crate back up, a stone lid) and the hook (two eyes blink in the vent under the cabin).
The land is Episode 1's (Rule 1): cabin, path, garden with its fence, the trip hammer by the stream. Webcam on the strap
all scene (hands free); the mug goes down on the chopping stump before he builds.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
FPS = 30
SLUG = "raccoon_lift_scene01"
S9 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene009.json"))
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the land as Episode 1 left it (Rule 1)
DROP = {"bottle", "page13", "tester", "tester_led", "pulse", "book", "pages", "prop"}
for name, st in S9["structures"].items():
    if name in DROP:
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
S["solar_panel"]["at"] = [-2.4, 1.3, 0.0]                           # on the fence box (Scene 009)
S["ground_rod"]["at"] = [0.0, 0.0, -0.21]                           # pushed in, three shoves of 7 cm (Scene 009)
for name in ("webcam", "cam_cap", "mug"):                            # placed by the holds below
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0

# ---------------------------------------------------------------- the food crate by the cabin's west wall
CX, CY = range(-25, -21), range(-1, 2)                             # 4 x 3 cells: x -2.55..-2.15, y -0.15..0.15
CRATE_C = (-2.35, 0.0)
crate = [(x, y, 0) for x in CX for y in CY] + [(x, y, z) for z in (1, 2) for x in CX for y in CY
                                               if x in (CX[0], CX[-1]) or y in (CY[0], CY[-1])]
S["crate"] = dict(cells=[list(c) for c in crate], at=[0.0, 0.0, 0.0], centered=False, material="planks", expect_blocks=len(crate))
S["lid"] = dict(cells=[[x, y, 3] for x in CX for y in CY], at=[0.0, 0.0, -0.025], centered=False, material="stone",
                block_shape=[1, 1, 0.5], expect_blocks=12)
WRECK = [(-27, 1), (-26, -2), (-24, -3), (-22, -2), (-28, -3), (-21, 2), (-26, 3), (-23, 2)]   # planks, flat in the grass
S["wreck"] = dict(cells=[[x, y, 0] for x, y in WRECK], at=[0.0, 0.0, -0.035], centered=False, material="planks",
                  block_shape=[1, 0.6, 0.3], expect_blocks=len(WRECK), prebuilt=True)
CAB_OUT = [(-29, -1), (-30, -3), (-25, -4)]                          # cabbages strewn about
S["cabbages_out"] = dict(cells=[[x, y, 0] for x, y in CAB_OUT], at=[0.0, 0.0, -0.01], centered=False, material="cabbage",
                         block_shape=[1.1, 1.1, 1.0], expect_blocks=len(CAB_OUT), prebuilt=True)
S["cabbages_in"] = dict(cells=[[x, 0, 1] for x in (-24, -23)] + [[-24, 0, 2]], at=[0.0, 0.0, 0.0], centered=False,
                        material="cabbage", block_shape=[0.95, 0.95, 0.95], expect_blocks=3)
ROLL0 = [-2.3, 0.18, 0.05]                                         # the cabbage that rolls to the lens (set below)
S["cabbage_roll"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="cabbage", block_shape=[1.1, 1.1, 1.1],
                         expect_blocks=1, prebuilt=True)
STUMP = (-2.8, 0.95)                                              # the chopping stump: the mug's spot while he builds
S["stump"] = dict(cells=[[0, 0, z] for z in range(5)], at=[STUMP[0], STUMP[1], 0.0], centered=True, material="oldwood",
                  block_shape=[2.2, 2.2, 1], expect_blocks=5, prebuilt=True)
STUMP_TOP = 0.5                                                     # (waist-high: the mug is an easy reach)

# ---------------------------------------------------------------- the clue: prints like tiny hands, crate -> the vent
PRINTS = [(-2.07, 0.03, -125), (-1.97, -0.07, -140), (-1.88, -0.16, -120), (-1.8, -0.25, -138)]   # (x, y, heading deg)
paw = []
for px, py, hd in PRINTS:
    a = math.radians(hd)
    rot = lambda u, v: (px + u * math.cos(a) - v * math.sin(a), py + u * math.sin(a) + v * math.cos(a))
    for (u, v, su, sv) in [(0.0, 0.0, 0.05, 0.045)] + [(0.05 * math.sin(math.radians(f)), 0.033 + 0.033 * math.cos(math.radians(f)), 0.012, 0.042)
                                                       for f in (-70, -35, 0, 35, 70)]:   # the palm, five long fingers
        x, y = rot(u, v)
        paw.append(dict(c=[round(x, 4), round(y, 4), 0.0], s=[su, sv, 0.004], m="coffee"))
S["mud"] = dict(cells=[[0, 0, 0]], at=[-1.95, -0.1, -0.046], centered=True, material="mud", block_shape=[4.6, 5.8, 0.05],
                expect_blocks=1, prebuilt=True, extras=[dict(e, c=[round(e["c"][0] + 1.95, 4), round(e["c"][1] + 0.1, 4), 0.1018]) for e in paw])
VENT = (-1.728, -0.3)                                               # a dark vent under the cabin floor, west wall
S["vent"] = dict(cells=[[0, 0, 0]], at=[VENT[0], VENT[1], 0.015], centered=True, material="rubber", block_shape=[0.2, 2.4, 1.0],
                 expect_blocks=1, prebuilt=True)
EYES_AT = [-1.745, VENT[1], 0.0]
S["eyes"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=True, material="rubber", block_shape=[0.05, 0.05, 0.05], expect_blocks=1,
                 prebuilt=True, extras=[dict(c=[0.0, dy, 0.065], s=[0.006, 0.02, 0.015], m="eyeshine") for dy in (-0.03, 0.03)])

# ---------------------------------------------------------------- lines (approved script)
LINES = [("cabbages", "My cabbages!", dict(lens=False, why="cold open: he shouts at the mess, not to chat")),
         ("robbed", "Somebody robbed me, chat. And they left... fingerprints.", {}),
         ("on", "Is this thing on?", {}),
         ("hot", "Hot. Too hot. ...Perfect.", {}),
         ("morning", "Good morning, chat. Welcome to Grandpa's Block Lab.", {}),
         ("look", "Not the boar, BoarFan. Look. Five little fingers...", {}),
         ("hand", "...like a tiny hand. A tiny, hungry hand.", {}),
         ("ratio", "A raccoon. My crate got... ratioed.", {}),
         ("wild", "Wild animals: we look. We don't touch. And we never feed them.", {}),
         ("ready", "Ready, chat? Blocks up!", {}),
         ("stone", "Stone lid. Raccoon-proof.", {}),
         ("nothing", "Nothing gets past Grandpa Tovi.", {})]
GUESS = dict(cabbages=1.1, robbed=3.6, on=1.2, hot=2.4, morning=2.9, look=3.2, hand=2.6, ratio=2.6, wild=3.8, ready=1.7, stone=1.9, nothing=1.9)
dur_file = os.path.join(HERE, "raccoon_s01_durations.json")
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
    "aghast": dict(lean=-0.08, shrug=0.5, elbows=0.5),
    "crouch_talk": dict(lean=0.25, hips=[0.0, 0.0, -0.16]),
    "tap_cam": dict(hand_R={"char": [-0.1, -0.27, 1.1]}),
    "point_low": dict(lean=0.2, hand_R={"char": [-0.12, -0.42, 0.55]}),
    "dust_hands": dict(hand_R={"char": [-0.05, -0.28, 0.72]}, hand_L={"char": [0.05, -0.28, 0.74]}),
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "reach_mug": dict(lean=0.05, hand_L=dict(obj="mug", off=[0.095, 0.0, 0.09])),   # hand on the handle (Episode 1)
}
G_IN = (-1.45, 0.66)                                                # just inside the open door
G1 = (-2.35, 0.52)                                                 # at the wreck (north of it): the crate's build spot too
G_PR = (-2.05, 0.4)                                                # where he points at the prints
MUG_GRIP = [0.095, 0.0, 0.09]                                      # wrist just outside the handle (Episode 1)
MUG_CARRY = {"char": [0.06, -0.27, 0.6]}
MUG_SIP = "mouth"
MUG_DOWN_ROT = [0, 0, 180]                                          # handle west: toward his left hand as he faces the stump
MUG_DOWN = [STUMP[0], STUMP[1] - 0.08, round(STUMP_TOP - 0.02, 3)]          # (the mug root sits 2 cm below its base)
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])
MUG = len(A)
act(type="hold", target="mug", hand="L", when=-1.0, until=99.0, reach=0.3, grip=MUG_GRIP,
    keys=[dict(t=-1.0, at=MUG_CARRY, rot=[0, 0, 0])])

# 1. cold open: the cabbage rolls to the lens; he rushes out of the door
ROLL1 = [-3.05, 0.3, 0.05]                                        # (toward the cold-open camera)
dist_roll = math.dist(ROLL0[:2], ROLL1[:2])
ROLL = len(A)
act(type="hold", target="cabbage_roll", hand="none", when=-1.0, until=99.0, reach=0.05,
    keys=[dict(t=-1.0, at=ROLL0, rot=[0, 0, 0])] +
         [dict(t=round(1.4 * u, 3), at=[round(ROLL0[i] + (ROLL1[i] - ROLL0[i]) * (1 - (1 - u) ** 2), 4) for i in range(3)],
               rot=[round(math.degrees(dist_roll * (1 - (1 - u) ** 2) / 0.055), 1) * -0.3, round(-math.degrees(dist_roll * (1 - (1 - u) ** 2) / 0.055), 1), 0])
          for u in (0.0, 0.25, 0.5, 0.75, 1.0)] + [dict(t=99.0, at=ROLL1, rot=[-0.3 * round(math.degrees(dist_roll / 0.055), 1), round(-math.degrees(dist_roll / 0.055), 1), 0])])
sfx("settle", 1.4, 0.3)
walk(0.25, 1.45, G1, via=[(-1.9, 0.58), (-2.2, 0.3)])
face("worried", -1.0, 1.6)
s, e = say("cabbages", 0.0, at=1.55)
look(1.45, e + 0.5, pos=(CRATE_C[0], CRATE_C[1], 0.0), body=True, rate=0.3)
pose("aghast", s - 0.1, e + 0.3, ease=0.15)
face("surprised", s, e + 0.4, set=dict(brow=1.2))
pose("crouch_talk", e + 0.3, e + 0.6 + D["robbed"] + 0.4, ease=0.3)
s, e = say("robbed", 0.5)
to_lens(s - 0.2, e + 0.2)
face("worried", s, s + 1.6)
face("side_eye", e - 1.1, e + 0.4)

# 2. the Morning Ritual: tap, coffee, the regulars, the greeting
TAP = e + 0.7
pose("tap_cam", TAP - 0.3, TAP + 0.35, ease=0.15)
sfx("tap", TAP, 0.5)
s, e = say("on", 0.0, at=TAP + 0.25)
to_lens(s - 0.4, e + 0.2)
face("raised", s, e + 0.3, set=dict(brow=0.7))
SIP = e + 0.4
A[MUG]["keys"] += [dict(t=round(SIP, 3), at=MUG_CARRY, rot=[0, 0, 0]), dict(t=round(SIP + 0.45, 3), at=MUG_SIP, off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
                   dict(t=round(SIP + 1.1, 3), at=MUG_SIP, off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]), dict(t=round(SIP + 1.5, 3), at=MUG_CARRY, rot=[0, 0, 0])]
sfx("sip", SIP + 0.5, 0.5)
face("worried", SIP + 1.0, SIP + 1.6, set=dict(brow=0.9))
s, e = say("hot", 0.0, at=SIP + 1.3)
to_lens(s - 0.2, e + 0.2)
face("smile", e - 0.7, e + 0.5, set=dict(smile=0.9))
CHAT0 = e + 0.4
REG = [("GardenGranny", "good morning dear ☕"), ("lurker_77", "👀"), ("BoarFan2009", "WAS IT THE BOAR??"), ("TobiasBuilds", "morning grandpa")]
CHAT = [(CHAT0 + 0.9 * k, u, x) for k, (u, x) in enumerate(REG)]
VIEWERS = [[0.0, 0]] + [[round(CHAT0 - 0.3 + 0.9 * k, 3), k + 1] for k in range(4)]
face("content", CHAT0, CHAT0 + 3.6)
s, e = say("morning", 0.0, at=CHAT0 + 3.5)
to_lens(s - 0.3, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=0.8))

# 3. the clue: prints like tiny hands
walk(e + 0.2, e + 1.0, G_PR)
s, e = say("look", 0.5, at=LE["morning"] + 1.1)
to_lens(s - 0.2, s + 1.2)
face("smirk", s, s + 1.2)
POINT = s + 1.3
look(POINT - 0.2, e + 0.3, pos=(PRINTS[1][0], PRINTS[1][1], 0.0), body=True, rate=0.3)
pose("point_low", POINT - 0.2, e + 0.2, ease=0.25)
act(type="point", pos=[PRINTS[1][0], PRINTS[1][1], 0.02], when=round(POINT, 3), until=round(e, 3))
INSERT = (POINT + 0.35, e + 0.25)                                   # close-up of the prints (he is off screen)
LESSON0 = s + 1.5
s, e = say("hand", 0.2)
to_lens(s - 0.2, e + 0.2)
face("confused", s, s + 1.2)
face("raised", s + 1.2, e + 0.3, set=dict(brow=0.8))
CHAT += [(e + 0.5, "TobiasBuilds", "raccoon. 100%"), (e + 1.3, "GardenGranny", "the masked bandit!!")]
s, e = say("ratio", 0.0, at=e + 2.2)
to_lens(s - 0.3, e + 0.2)
face("raised", s, s + 1.0, set=dict(brow=0.9))
face("smirk", s + 1.0, e + 0.4)                                     # proud of his slang (it's wrong)
LESSON1 = e
s, e = say("wild", 0.6)
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)                                         # sincere: no slang, calm

# 4. the build: mug on the stump, "Blocks up!", the crate back up, cabbages in, the stone lid
walk(e + 0.3, e + 1.3, (STUMP[0], STUMP[1] - 0.40))
DOWN = e + 1.5
look(e + 1.1, DOWN + 0.4, pos=MUG_DOWN, body=True, rate=0.3)
A[MUG]["keys"] += [dict(t=round(DOWN - 0.3, 3), at=MUG_CARRY, rot=[0, 0, 0]), dict(t=round(DOWN, 3), at=MUG_DOWN, rot=MUG_DOWN_ROT)]
A[MUG]["keys"].append(dict(t=round(DOWN + 0.3, 3), at=MUG_DOWN, rot=MUG_DOWN_ROT))   # he lets go after it has landed
A[MUG]["until"] = round(DOWN + 0.3, 3)
pose("reach_mug", DOWN - 0.35, DOWN + 0.7, ease=0.2)             # the hand stays on it as it lets go
sfx("clink", DOWN, 0.4)
MUG_REST = len(A)
act(type="hold", target="mug", hand="none", when=round(DOWN + 0.4, 3), until=99.0, reach=0.05,
    keys=[dict(t=round(DOWN + 0.4, 3), at=MUG_DOWN, rot=MUG_DOWN_ROT)])
s, e = say("ready", 0.0, at=DOWN + 0.5)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", s + 0.6, e + 0.4, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.4
act(type="remove", target="wreck", when=round(B0 + 0.4, 3), until=round(B0 + 1.4, 3), stand_at=[G1[0], G1[1], 0.0])
act(type="remove", target="cabbages_out", when=round(B0 + 1.45, 3), until=round(B0 + 1.95, 3), stand_at=[G1[0], G1[1], 0.0])
act(type="build", target="crate", when=round(B0 + 2.0, 3), until=round(B0 + 5.6, 3), stand_at=[G1[0], G1[1], 0.0], order="z")
act(type="build", target="cabbages_in", when=round(B0 + 5.7, 3), until=round(B0 + 6.5, 3), stand_at=[G1[0], G1[1], 0.0], order="z")
A[ROLL]["until"] = round(B0 + 1.65, 3)
act(type="hold", target="cabbage_roll", hand="none", when=round(B0 + 1.7, 3), until=99.0, reach=0.05,   # (this one goes in too)
    keys=[dict(t=round(B0 + 1.7, 3), at=HIDE, rot=[0, 0, 0])])
walk(B0 + 6.55, B0 + 7.0, (G1[0], G1[1] + 0.1))                     # a step back before the stone slab drops
LID = B0 + 7.1
act(type="build", target="lid", when=round(LID, 3), until=round(LID + 0.5, 3), stand_at=[G1[0], G1[1], 0.0], order="z", quiet=True)
sfx("thud", LID + 0.4, 1.0)
look(B0 + 0.3, LID + 0.9, pos=(CRATE_C[0], CRATE_C[1], 0.2), body=True, rate=0.3)
s, e = say("stone", 0.0, at=LID + 1.0)
to_lens(s - 0.3, e + 0.2)
pose("dust_hands", s - 0.2, e + 0.3, ease=0.2)
face("smirk", s, e + 0.4)

# 5. the hook: coffee again, so pleased with himself... two eyes blink in the vent
walk(e + 0.4, e + 1.4, (STUMP[0], STUMP[1] - 0.40))
UP = e + 1.6
look(e + 1.2, UP + 0.3, pos=MUG_DOWN, body=True, rate=0.3)
A[MUG_REST]["until"] = round(UP, 3)
pose("reach_mug", UP - 0.45, UP + 0.3, ease=0.2)                  # the hand gets there first
act(type="hold", target="mug", hand="L", when=round(UP, 3), until=99.0, reach=0.3, grip=MUG_GRIP,
    keys=[dict(t=round(UP, 3), at=MUG_DOWN, rot=MUG_DOWN_ROT), dict(t=round(UP + 0.15, 3), at=MUG_DOWN, rot=MUG_DOWN_ROT),
          dict(t=round(UP + 0.5, 3), at=MUG_CARRY, rot=[0, 0, 0]),
          dict(t=round(UP + 0.7, 3), at=MUG_CARRY, rot=[0, 0, 0]), dict(t=round(UP + 1.1, 3), at=MUG_SIP, off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
          dict(t=round(UP + 1.7, 3), at=MUG_SIP, off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]), dict(t=round(UP + 2.1, 3), at=MUG_CARRY, rot=[0, 0, 0])])
s, e = say("nothing", 0.0, at=UP + 2.2)
to_lens(s - 0.3, 99.0)
face("smirk", s, 99.0)
EYES_ON = UP + 0.9                                                  # (behind him, while he sips)
BLINKS = [EYES_ON + 1.6, e + 0.7]
ek = [dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(EYES_ON - 0.02, 3), at=HIDE, rot=[0, 0, 0]), dict(t=round(EYES_ON, 3), at=EYES_AT, rot=[0, 0, 0])]
for b in BLINKS:
    ek += [dict(t=round(b - 0.02, 3), at=EYES_AT, rot=[0, 0, 0]), dict(t=round(b, 3), at=HIDE, rot=[0, 0, 0]),
           dict(t=round(b + 0.12, 3), at=HIDE, rot=[0, 0, 0]), dict(t=round(b + 0.14, 3), at=EYES_AT, rot=[0, 0, 0])]
act(type="hold", target="eyes", hand="none", when=-1.0, until=99.0, reach=0.05, keys=ek)
END = BLINKS[-1] + 1.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)
for a in A:                                                         # every hold ends on a key at its end (it stays put)
    if a["type"] == "hold" and a["keys"][-1]["t"] < a["until"]:
        a["keys"].append(dict(a["keys"][-1], t=a["until"]))

# the trip hammer keeps its clock by the stream (Rule 1); the garden gate stays shut
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

lines = []
for i, (lid, text, extra) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0, **extra))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["nothing"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (west of the cabin: clear air, no trees)
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)); out.append([tt, p[0], p[1]])
    return out
STOPS = [(0.0, G_IN)]
pos_now = G_IN
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
    return list(STOPS[-1][1]) if t > STOPS[-1][0] else list(G_IN)
who_at = lambda t: gp(*g_at(t))
WALL_FREE = lambda eye: eye[0] < -1.95                              # never inside or behind the cabin wall
AIR = both(clear_air, WALL_FREE)
PATH = both(solid_free, WALL_FREE)
LOS = make_los([])
cam = []
def framed(t, must, tgt, az, el, d, *a, **kw):
    """auto_frame, widening the search when the wanted angle is blocked: other angles first, then a step back."""
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
WRECK_PTS = [(x * 0.1, y * 0.1, 0.03) for x, y in WRECK[:5]]
DOOR = (-1.9, 0.6, 1.0)                                             # just outside the open door
VENT_PT = (VENT[0] - 0.07, VENT[1], 0.08)                           # (just in front of the wall: the sight rules treat the wall as solid)
SHOTS = [
    # cold open: low and wide -- the wreck, the cabbage rolling at us, the open door he bursts out of
    (0.0, ([(CRATE_C[0], CRATE_C[1], 0.03), (-2.55, -0.15, 0.03), (-2.15, 0.15, 0.03), (DOOR[0], DOOR[1], 0.05), (DOOR[0], DOOR[1], 1.25)],
           (-2.2, 0.3, 0.55), 172, 10, 2.2)),
    # "Somebody robbed me": close on him, crouched by the mess
    (LS["robbed"] - 0.3, (gp(*G1)[1:] + [(CRATE_C[0], CRATE_C[1], 0.0)], (-2.4, 0.25, 0.6), 180, 10, 1.6)),
    # the Morning Ritual: a medium front shot
    (LS["on"] - 0.4, (gp(*G1)[1:], (G1[0], G1[1], 0.85), 180, 8, 1.5)),
    # the clue: he points
    (LS["look"] - 0.2, (gp(*G_PR)[1:] + [(PRINTS[1][0], PRINTS[1][1], 0.0)], (-2.05, 0.15, 0.55), 185, 12, 1.8)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
tc = math.ceil(INSERT[0] * FPS - 1e-6) / FPS                        # insert: the prints from above (a cutaway)
cam += [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), orbit(tc, (-1.95, -0.1, 0.0), 200, 52, 0.75)]
tc1 = math.ceil(INSERT[1] * FPS - 1e-6) / FPS
cam += [orbit(tc1 - 1.0 / FPS, (-1.95, -0.08, 0.0), 204, 50, 0.7)]
SHOTS2 = [
    (INSERT[1], (gp(*G_PR)[1:], (G_PR[0], G_PR[1], 0.85), 180, 8, 1.5)),
    # the build, wide: the stump, the crate going back up
    (LE["wild"] + 0.25, (gp(*G1) + gp(STUMP[0], STUMP[1] - 0.40) + [(CRATE_C[0], CRATE_C[1], 0.4)], (-2.55, 0.3, 0.55), 185, 16, 2.6)),
    # "Stone lid. Raccoon-proof.": on him by the finished crate
    (LS["stone"] - 0.3, (gp(*G1)[1:] + [(CRATE_C[0], CRATE_C[1], 0.36)], (-2.4, 0.2, 0.65), 180, 10, 1.7)),
    # the hook: wide, him with his coffee in front, the vent behind
    (LE["stone"] + 0.5, (gp(STUMP[0], STUMP[1] - 0.40) + [VENT_PT, (VENT_PT[0], VENT[1] - 0.15, 0.3), (CRATE_C[0], CRATE_C[1], 0.36)],
                         (-2.3, 0.15, 0.5), 190, 9, 2.4)),
]
for t, (must, tgt, az, el, d) in SHOTS2:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

cards = [dict(style="live", when=0.0, until="end", viewers=VIEWERS),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0})]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="CLUES", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="look before you guess", color="cyan", at=round(LESSON0 + 1.2, 3), size=30)])]
W = {k: v for k, v in S9["world"].items() if k not in ("clouds_pass", "critters")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[])
story = dict(title="The Raid", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["cabbages"], tail=round(tail, 4), seed=101, blink=True, target_duration=60,
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=1, name="The Raid", previous=None, next="raccoon_lift_scene02"),
             world=W, lines=lines, grandpa=dict(start=list(G_IN), outfit=S9["grandpa"]["outfit"]),
             poses=dict(S9["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"], cutaways=[[math.floor(tc * 1000) / 1000 - 0.001, math.ceil(tc1 * 1000) / 1000 + 0.001]],
                     solid=["crate", "lid", "stump", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-9s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("tap %.2f sip %.2f chat0 %.2f insert %.2f-%.2f build %.2f lid %.2f eyes %.2f" % (TAP, SIP, CHAT0, INSERT[0], INSERT[1], B0, LID, EYES_ON))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
