"""Grandpa's Block Lab, Episode 1, Scene 001 -- "Is This Thing On?" (16:9, ~30 s, continuity into Scene 002).
Grandpa's first livestream from his log cabin. Every action is placed against the measured narration:
pass 1 synthesises the voice (durations -> ep01_s001_durations.json); pass 2 (--fit) re-times everything to it.
World coordinates in metres; furniture cells are absolute (at = [0, 0, 0], centered = false, 1 cell = 0.1 m)."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, B = 30, 0.1
S, A, CARDS = {}, [], []

def st(name, cells, mat, shape=None, at=(0.0, 0.0, 0.0), **kw):
    cells = sorted(set(tuple(c) for c in cells))
    S[name] = dict(cells=[list(c) for c in cells], at=[round(v, 4) for v in at], centered=False, material=mat,
                   expect_blocks=len(cells), prebuilt=True, **kw)
    if shape:
        S[name]["block_shape"] = shape

def rotz(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2])

def add(p, q):
    return [round(p[i] + q[i], 4) for i in range(3)]

# ---------------------------------------------------------------- set: table, chair, monitor + home-made webcam, mug
TABLE_TOP = 0.5
st("table_legs", [(x, y, z) for x in (-4, 4) for y in (-1, 2) for z in range(5)], "planks", [0.5, 0.5, 1])
st("table_top", [(x, y, 4) for x in range(-4, 5) for y in range(-1, 3)], "planks", [1, 1, 0.5])   # y -0.15..0.25
st("chair_legs", [(x, 5, z) for x in (-1, 1) for z in range(3)] + [(x, 7, z) for x in (-1, 1) for z in range(7)], "wood", [0.5, 0.5, 1],
   at=(0.0, 0.04, 0.0))
st("seat", [(x, y, 2) for x in (-1, 0, 1) for y in (5, 6)], "wood", [1, 1, 0.5], at=(0.0, 0.04, 0.0))
st("chair_back", [(0, 7, 4), (0, 7, 5), (-1, 7, 6), (0, 7, 6), (1, 7, 6)], "wood", [1, 0.4, 1], at=(0.0, 0.04, 0.0))
SEAT_TOP = 0.30
LAP_AT, LAP_YAW = (-0.12, 0.14, TABLE_TOP - 0.08), -18.0         # laptop, turned toward his chair; its base sits on the table
st("laptop_base", [(x, y, 0) for x in (-1, 0, 1) for y in (-1, 0)], "steel", [1, 1, 0.2], at=LAP_AT, yaw=LAP_YAW)
st("laptop_screen", [(x, -1, z) for x in (-1, 0, 1) for z in (1, 2)], "steel", [1, 0.2, 1], at=LAP_AT, yaw=LAP_YAW,
   extras=[dict(c=[0, -0.088, 0.21], s=[0.27, 0.004, 0.17], m="screen")])
st("webcam", [(0, -1, 3)], "rubber", [0.8, 0.6, 1], at=LAP_AT, yaw=LAP_YAW,      # his home-made block webcam
   extras=[dict(c=[0, -0.066, 0.35], s=[0.046, 0.008, 0.046], m="steel"), dict(c=[0, -0.061, 0.35], s=[0.026, 0.004, 0.026], m="coffee"),
           dict(c=[0.026, -0.066, 0.383], s=[0.01, 0.006, 0.01], m="led")])
st("cam_cap", [(0, -1, 4)], "red", [0.8, 0.6, 1], at=LAP_AT, yaw=LAP_YAW)    # the block that pops off when he taps the camera
LENS = add(LAP_AT, rotz((0, -0.06, 0.35), LAP_YAW))
SCREEN = add(LAP_AT, rotz((0, -0.08, 0.21), LAP_YAW))
MUG0 = (0.22, 0.06, TABLE_TOP - 0.02)                           # mug root: its single cell spans z +0.02..+0.10
st("mug", [(0, 0, 0)], "ceramic", [0.6, 0.6, 0.8], at=MUG0,
   extras=[dict(c=[0, 0, 0.096], s=[0.05, 0.05, 0.004], m="coffee"), dict(c=[0.042, 0, 0.083], s=[0.024, 0.014, 0.012], m="ceramic"),
           dict(c=[0.042, 0, 0.037], s=[0.024, 0.014, 0.012], m="ceramic"), dict(c=[0.05, 0, 0.06], s=[0.012, 0.014, 0.05], m="ceramic")])
MUG_GRIP = (0.095, 0.0, 0.09)                                   # wrist just outside the handle
ROOT = (0.0, 0.34, 0.0)                                          # grandpa's feet, just past the table edge
DOOR = (-1.6, 0.70, 0.95)
CHAIR = ["chair_legs", "seat", "chair_back"]

# ---------------------------------------------------------------- lines (dialogue exactly as written, split at sentences)
LINES = [("hello", "Hello? Can anybody hear me?"), ("on", "Is this thing on?"),
         ("box", "An old man talking to a box."), ("committed", "My grandfather would've had me committed."),
         ("viewers", "Three viewers?"), ("pharmacy", "I get more attention at the pharmacy blood pressure machine."),
         ("welcome", "Anyway, welcome to Grandpa's Block Lab."), ("creator", "Apparently I'm a content creator now."),
         ("coffee", "Ah, coffee."), ("reliable", "The one reliable thing in my life."), ("spill", "Until I spill it."),
         ("up", "All right, up we go."), ("back", "Oh! My back just filed a complaint."), ("what", "...What was that?")]
GUESS = dict(hello=2.0, on=1.3, box=1.9, committed=2.6, viewers=1.0, pharmacy=3.6, welcome=2.5, creator=2.6,
             coffee=0.9, reliable=1.8, spill=1.1, up=1.3, back=2.6, what=1.0)
dur_file = os.path.join(HERE, "ep01_s001_durations.json")
D = dict(GUESS, **(json.load(open(dur_file)) if "--fit" in sys.argv and os.path.exists(dur_file) else {}))
LS, LE = {}, {}
cursor = [0.0]
def say(lid, gap):
    """Line `lid` starts `gap` s after the previous one ends (or at the cursor, whichever is later)."""
    LS[lid] = round(max(cursor[0], (LE[list(LE)[-1]] if LE else 0.0) + gap), 3)
    LE[lid] = round(LS[lid] + D[lid], 3)
    cursor[0] = LE[lid]
    return LS[lid], LE[lid]
def act(**a):
    A.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in a.items()})
def pose(name, t0, t1, **kw): act(type="pose", pose=name, when=t0, until=t1, **kw)
def face(expr, t0, t1, **kw): act(type="face", expr=expr, when=t0, until=t1, **kw)
def look(pos, t0, t1, body=False, **kw): act(type="look", pos=[round(v, 3) for v in pos], when=t0, until=t1, body=body, **kw)
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)

POSES = {
    "hands_table": dict(hand_R=dict(char=[-0.32, -0.17, 0.585]), hand_L=dict(char=[0.14, -0.16, 0.59])),    # beside the laptop / behind the mug
    "tap_cam": dict(hand_R=dict(obj="webcam", off=[0.0, -0.025, 0.35], tap=[2.2, 0.018]), twist=-0.12),
    "fix_lean": dict(lean=0.50, twist=-0.15, hips=[0.0, -0.10, 0.0], hand_L=dict(char=[0.24, -0.10, 0.70])),   # scoots forward and stretches
    "catch_mug": dict(hand_R=dict(obj="mug", off=[-0.07, 0.0, 0.08]), lean=0.06),
    "reach_mug": dict(lean=0.25),
    "push_up": dict(hand_R=dict(char=[-0.15, -0.085, 0.63]), hand_L=dict(char=[0.15, -0.085, 0.63]), elbows=0.6),
    "peer": dict(lean=0.08, head=[0.0, -0.04, 0.0]),
    "lean_in_cam": dict(lean=0.18, hips=[0.0, -0.01, 0.0]),        # peering into his own webcam
    "head_tilt": dict(head=[0.0, 0.0, 0.16]),
}

# ---------------------------------------------------------------- the performance
SEATED_FROM = -5.0
pose("seated", SEATED_FROM, 99.0)                                # until the stand-up (shortened below)
pose("hands_table", SEATED_FROM, 99.0)
look(LENS, SEATED_FROM, 99.0)                                     # talks to his stream camera
# 0-1: the hook -- a squinting extreme close-up through his own webcam, then "Hello?"
pose("lean_in_cam", SEATED_FROM, 3.0, ease_out=1.3)
face("squint", SEATED_FROM, 2.6, ease_out=0.4)
cursor[0] = 0.5
s, e = say("hello", 0.0)
face("raised", s + 0.6, e + 0.2)                                   # "Can anybody hear me?" -- brows up, listening
pose("head_tilt", s + 0.7, e + 0.3)
s, e = say("on", 0.15)
pose("tap_cam", s - 0.25, e + 0.35, ease=0.25)                    # taps the camera twice
T_TAP = [s + 0.28, s + 0.73]
for tt in T_TAP:
    sfx("tap", tt, 0.9)
POP = T_TAP[1] + 0.12                                              # ...and the block on top pops off
CUBE_OFF = rotz((0, -0.1, 0), LAP_YAW)                           # the cap cube sits 1 cell behind the laptop's root
LAND_XY = (0.0 - CUBE_OFF[0], 0.18 - CUBE_OFF[1])                # root position that puts the cube between his hands
cap0 = LAP_AT
T_FLY = 0.42
dz = TABLE_TOP - (LAP_AT[2] + 0.4)                                 # cap bottom: from the webcam top down onto the table
vz = (dz + 0.5 * 9.81 * T_FLY ** 2) / T_FLY
v0 = [round((LAND_XY[0] - cap0[0]) / T_FLY, 4), round((LAND_XY[1] - cap0[1]) / T_FLY, 4), round(vz, 4)]
act(type="fly", target="cam_cap", v0=v0, g=9.81, when=POP, until=POP + T_FLY, sound="none")
CAP_LANDED = [round(LAND_XY[0], 4), round(LAND_XY[1], 4), round(TABLE_TOP - 0.4, 4)]   # root (cell z=4 sits 0.4 above it)
sfx("clatter", POP + T_FLY - 0.01, 0.8)
face("surprised", POP - 0.05, POP + 0.9, ease=0.12)
look(add(add(CAP_LANDED, CUBE_OFF), (0, 0, 0.45)), POP + 0.15, POP + 1.5)
# "An old man talking to a box." -- fixes the box; "My grandfather..." -- leans back, shakes his head, side-eye
s, e = say("box", 0.35)
PICK, PLACE = s - 0.05, s + 1.15
face("side_eye", POP + 0.9, PLACE - 0.1, set=dict(gx=0.0))          # grumpy look at the runaway block
act(type="hold", target="cam_cap", hand="R", when=PICK, until=PLACE, reach=0.4, grip=[0.0, -0.05, 0.45],
    keys=[dict(t=PICK, at=CAP_LANDED, rot=[0, 0, LAP_YAW]), dict(t=PICK + 0.55, at=add(CAP_LANDED, (-0.05, -0.07, 0.26)), rot=[0, 0, LAP_YAW + 25]),
          dict(t=PLACE, at=list(LAP_AT), rot=[0, 0, LAP_YAW])])
pose("fix_lean", PICK - 0.4, PLACE + 0.3)
look(add(LAP_AT, (0, 0, 0.4)), PICK - 0.3, PLACE + 0.2)
sfx("click_block", PLACE - 0.02, 1.0)
s, e = say("committed", 0.2)
pose("lean_back", PLACE + 0.35, e + 0.2, ease=0.45)
pose("head_shake", PLACE + 0.4, PLACE + 1.3, ease=0.2)
face("side_eye", s + 0.25, e + 0.15)
# the viewer count: he notices, brows up, a pause, a shrug
look(SCREEN, e + 0.2, e + 1.9)
face("raised", e + 0.35, e + 1.8)
pose("peer", e + 0.25, e + 1.8)
s, e = say("viewers", 0.45)
s2, e2 = say("pharmacy", 0.3)
pose("shrug", s2 - 0.45, s2 + 0.5, ease=0.25)
face("confused", s2 - 0.4, s2 + 0.6)
face("smirk", s2 + 1.0, e2 + 0.2)
# "Anyway, welcome to Grandpa's Block Lab." -- relaxes, smiles, gestures at the room; someone joins (3 -> 4)
s, e = say("welcome", 0.3)
face("warm", s - 0.1, e + 0.4)
pose("present", s + 0.5, e + 0.25, ease=0.4)
JOIN = s + 0.65 * D["welcome"]
look(SCREEN, JOIN + 0.1, JOIN + 0.9)
face("smile", JOIN + 0.15, JOIN + 1.0, set=dict(smile=1.0, brow=0.6))
s, e = say("creator", 0.2)
pose("nod", s + 0.2, s + 1.0, ease=0.2)
face("smirk", s + 0.1, e + 0.2)
# "Ah, coffee." -- reaches for the mug (clink), sips; "...until I spill it." -- wobble, catch, relief
s, e = say("coffee", 0.3)
LIFT = s - 0.2
SIP0 = e + 0.1
SIP1 = SIP0 + 0.75
sfx("clink", LIFT + 0.02, 0.7)
s_r, e_r = (None, None)
cursor[0] = SIP1 + 0.05
s_r, e_r = say("reliable", 0.0)
s_s, e_s = say("spill", 0.1)
WOB = e_s + 0.05
DOWN = WOB + 0.95
HOLD_AT = add(ROOT, (0.15, -0.15, 0.63))                          # in front of his chest while he talks
act(type="hold", target="mug", hand="L", when=LIFT, until=DOWN, reach=0.4, grip=list(MUG_GRIP),
    keys=[dict(t=LIFT, at=list(MUG0)), dict(t=SIP0, at="mouth", off=[0.035, -0.075, -0.10], rot=[0, 0, 0]),
          dict(t=SIP0 + 0.25, at="mouth", off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
          dict(t=SIP1 - 0.15, at="mouth", off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
          dict(t=SIP1 + 0.35, at=HOLD_AT, rot=[0, 0, 0]), dict(t=WOB, at=HOLD_AT, rot=[0, 0, 0]),
          dict(t=WOB + 0.13, at=add(HOLD_AT, (0.01, 0, 0.01)), rot=[0, 28, 0]),
          dict(t=WOB + 0.27, at=add(HOLD_AT, (-0.01, 0, 0.0)), rot=[0, -22, 0]),
          dict(t=WOB + 0.4, at=HOLD_AT, rot=[0, 9, 0]), dict(t=WOB + 0.55, at=HOLD_AT, rot=[0, 0, 0]),
          dict(t=DOWN, at=list(MUG0), rot=[0, 0, 0])])
look(add(MUG0, (0, 0, 0.1)), LIFT - 0.4, LIFT + 0.2)
pose("reach_mug", LIFT - 0.45, LIFT + 0.35, ease=0.3)
pose("reach_mug", DOWN - 0.4, DOWN + 0.3, ease=0.3)
pose("sip", SIP0 - 0.1, SIP1 + 0.1, ease=0.25)
sfx("sip", SIP0 + 0.2, 0.8)
face("content", SIP0 + 0.15, s_r + 0.6, ease=0.3)
sfx("slosh", WOB, 0.7)
face("worried", WOB - 0.02, WOB + 0.45, ease=0.08)
pose("catch_mug", WOB + 0.02, DOWN - 0.15, ease=0.15)
look(add(HOLD_AT, (0, 0, 0.1)), WOB, WOB + 0.75)
face("relief", WOB + 0.45, DOWN + 0.5)
sfx("clink", DOWN - 0.02, 0.8)
# "All right, up we go." -- rises deliberately, chair scrapes back; "Oh!" -- hand to his back; "My back just filed a complaint."
cursor[0] = DOWN - 0.45                                           # "All right..." as the mug touches down
s, e = say("up", 0.0)
RISE0, RISE1 = DOWN + 0.1, DOWN + 1.4
A[0]["until"] = round(RISE1, 3); A[0]["ease_out"] = round(RISE1 - RISE0, 3)        # "seated" fades out over the rise
A[1]["until"] = round(RISE0 + 0.5, 3); A[1]["ease_out"] = 0.4                         # hands leave the table edge
pose("push_up", RISE0 - 0.1, RISE1 - 0.15, ease=0.3)
pose("rise", RISE0, RISE1 - 0.1, ease=0.6)
sfx("creak", RISE0 + 0.05, 0.9)
for name in CHAIR:
    act(type="slide", target=name, by=[0.0, 0.16, 0.0], when=RISE0 + 0.35, until=RISE0 + 0.95, sound="scrape" if name == "seat" else "none")
face("wince", RISE0 + 0.1, RISE0 + 0.6, ease=0.12, set=dict(lid=0.4))
cursor[0] = RISE1 - 0.45
s, e = say("back", 0.0)
pose("hand_on_back", s - 0.05, e + 0.25, ease=0.3)
face("wince", s - 0.05, s + 0.9, ease=0.1)
face("squint", s + 0.9, e + 0.1, set=dict(smile=-0.3))
pose("cap_adjust", e + 0.05, e + 0.85, ease=0.25)
# a distant CLUNK... CLUNK from the forest -- he freezes, turns toward the door: "...What was that?"
CLUNK = e + 0.15
sfx("clunk_far", CLUNK, 1.0)
face("alert", CLUNK + 0.12, 99.0, ease=0.15)
TURN = CLUNK + 0.35
A[2]["until"] = round(TURN, 3)                                     # stops talking to the camera
look(DOOR, TURN, 99.0, body=True, rate=0.06)
STEP_TO = [-0.42, 0.52, 0.0]                                       # a cautious step toward the door, out from behind the laptop
act(type="move", to=STEP_TO, via=[[0.0, 0.50, 0.0]], when=TURN, until=TURN + 1.25)   # back from the table first
cursor[0] = CLUNK + 0.6
s, e = say("what", 0.0)
END = e + 0.4
FILM = math.ceil(END * FPS) / FPS
for a in A:                                                        # open-ended actions run to the end of the scene
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# ---------------------------------------------------------------- lines -> bl_voice (each after the previous + pause)
lines = []
for i, (lid, text) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["what"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera: webcam close-up -> cabin; smooth moves, no cuts
def cam_key(t, eye, tgt):
    d = [eye[i] - tgt[i] for i in range(3)]
    dist = math.sqrt(sum(v * v for v in d))
    return dict(at=round(t, 3), target=[round(v, 3) for v in tgt], az=round(math.degrees(math.atan2(d[1], d[0])), 2),
                el=round(math.degrees(math.asin(d[2] / dist)), 2), dist=round(dist, 3))
def orbit(t, tgt, az, el, dist):
    return dict(at=round(t, 3), target=[round(v, 3) for v in tgt], az=az, el=el, dist=dist)
FACE_ECU = (-0.03, 0.42, 0.82)
ECU_EYE = add(LAP_AT, rotz((0.0, -0.20, 0.66), LAP_YAW))          # webcam POV, just above the cam: everything after rises clear
k_up = cam_key(POP + 0.45, add(FACE_ECU, (-0.05, -0.80, 0.32)), (-0.03, 0.36, 0.78))   # back first, then up: clears his cap
cam = [cam_key(0.0, ECU_EYE, FACE_ECU), cam_key(POP + 0.05, add(ECU_EYE, (0.0, -0.08, 0.02)), FACE_ECU), k_up,
       orbit(POP + 1.7, (-0.06, 0.32, 0.72), -62, 13, 1.75),
       orbit(LS["committed"] + 0.4, (-0.04, 0.36, 0.76), -66, 11, 1.55),
       orbit(LS["viewers"] - 0.2, (-0.04, 0.40, 0.80), -64, 9, 1.2),
       orbit(LE["pharmacy"], (-0.04, 0.40, 0.80), -66, 9, 1.15),
       orbit(LS["welcome"] + 2.2, (0.0, 0.6, 0.85), -80, 10, 2.55),
       orbit(LE["creator"] - 0.2, (0.02, 0.45, 0.78), -70, 10, 1.9),
       orbit(LS["coffee"] + 0.6, (0.06, 0.34, 0.74), -58, 10, 1.3),
       orbit(DOWN + 0.1, (0.04, 0.34, 0.76), -60, 10, 1.4),
       orbit(RISE1, (-0.05, 0.28, 0.85), -66, 8, 2.0),
       orbit(TURN + 0.2, (-0.15, 0.32, 0.88), -85, 13, 2.05),         # swing round with his turn: the laptop never
       orbit(FILM, (-0.75, 0.55, 0.9), -100, 11, 2.6)]                 # blocks his face, the door stays in frame
CARDS.append(dict(style="live", when=0.0, until="end", viewers=[[0.0, 3], [round(JOIN, 3), 4]]))
story = dict(title="Is This Thing On?", slug="grandpa_ep01_scene001", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["hello"], tail=round(tail, 4), seed=11, blink=True,
             target_duration=30, scene=dict(episode=1, scene=1, name="Is This Thing On?", next="ep01_scene002"),
             world=dict(ground="grass", time="morning", weather="clear", animals=["birds"], interior="cabin",
                        sun=[-0.96, -0.06, -0.27], exposure=0.15),
             lines=lines, grandpa=dict(start=list(ROOT), outfit=dict(hat="cap", shirt="rust", extras=[])),
             poses=POSES, structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=CARDS,
             qa=dict(close_ups=[[0.0, round(POP + 0.6, 3)]], rests_on=[["mug", "table_top"], ["cam_cap", "webcam"]],
                     seat="seat", seated_until=round(RISE0, 3), frame_points=["hat", "face", "chest"],
                     solid=["table_top", "table_legs", "seat", "chair_back", "laptop_base", "laptop_screen", "mug"]))
out = "/home/user/blocklab/stories/grandpa_ep01_scene001.json"
json.dump(story, open(out, "w"), indent=1)
print("film %.2f s (%d frames); speech %.2f s; lines:" % (FILM, round(FILM * FPS), sum(D[l] for l, _ in LINES)))
for lid, _ in LINES:
    print("  %-10s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("tap %s pop %.2f place %.2f lift %.2f sip %.2f wobble %.2f down %.2f rise %.2f-%.2f clunk %.2f join %.2f" %
      ([round(x, 2) for x in T_TAP], POP, PLACE, LIFT, SIP0, WOB, DOWN, RISE0, RISE1, CLUNK, JOIN))
