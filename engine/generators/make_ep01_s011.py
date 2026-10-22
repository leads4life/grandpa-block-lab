"""Grandpa's Block Lab, Episode 1, Scene 011 -- "Goodnight, Chat" (16:9, ~60 s). The episode's close: the Goodnight Ritual
(user, 2026-10-22: a predictable, Mister-Rogers-feel wrap-up -- the same beats every episode).
The same night, back at the cabin: he comes in the door with the webcam (Rule 2) and a lantern, clicks the lamp on, sets the
webcam back on the laptop and the lantern on the table, sits ("Ahh. That's better."). "Today we learned..." -- the recap card
builds a line at a time (cams, rot, scale, counterweight, circuit), "thank you, sun", and the sincere one: "the scariest thing
in the woods... was just hungry." His signature line. Chat says goodnight (Tobias last). "Goodnight, chat." Click: the lamp
goes off; only the lantern glows. He closes the book -- a torn page slips out, in someone else's handwriting.
"...Aliens. I KNEW it." He blows out the lantern. End card.
Talking to chat = square to the lens (engine: look "camera", grandpa "hold_heading").
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, fix_path
FPS = 30
S10 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene010.json"))
C10 = json.load(open(os.path.join(HERE, "s10work/build/continuity.json")))
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the world as Scene 010 left it; we're home
for name, st in S10["structures"].items():
    if C10["structures"][name]["blocks_standing"] == 0:
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
for name in ("book", "pages", "page13", "bottle", "tester", "tester_led", "pulse", "thermos", "webcam", "cam_cap", "prop", "solar_panel"):
    if name in S:
        S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
TABLE_TOP = 0.475
SEAT_AT = (0.0, 0.34)                                               # where he sits (Scene 001)
CAM_HOME = [-0.12, 0.14, 0.42]                                      # the webcam's root on the laptop, as in Scene 001
BOOK_AT = [0.06, -0.04, round(TABLE_TOP + 0.0075 - 0.05, 4)]       # lying flat on the table
PAGES_AT = [0.06, -0.04, round(BOOK_AT[2] + 0.0125, 4)]
LANT_T = [0.34, -0.05, round(TABLE_TOP - 0.0425, 4)]               # the hand lantern, set on the table
S["hand_lantern"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="darkiron", block_shape=[0.5, 0.5, 0.15],
                         expect_blocks=1,
                         extras=[dict(c=[0.0, 0.0, 0.09], s=[0.04, 0.04, 0.06], m="flame"),
                                 dict(c=[0.0, 0.0, 0.13], s=[0.055, 0.055, 0.012], m="darkiron"),
                                 dict(c=[0.0, 0.0, 0.17], s=[0.05, 0.006, 0.006], m="darkiron"),         # the bail handle
                                 dict(c=[-0.025, 0.0, 0.15], s=[0.004, 0.006, 0.04], m="darkiron"),
                                 dict(c=[0.025, 0.0, 0.15], s=[0.004, 0.006, 0.04], m="darkiron")])
INK = []                                                            # the torn page: someone else's hand -- red ink, a jagged edge
for k, (a, b, c_, d) in enumerate(((-0.05, 0.03, 0.04, 0.03), (-0.05, 0.012, 0.03, 0.012), (-0.05, -0.006, 0.045, -0.006),
                                   (-0.03, -0.03, 0.02, -0.03), (0.02, -0.03, 0.035, -0.015), (0.035, -0.015, 0.02, 0.0))):
    INK.append(dict(c=[round((a + c_) / 2, 4), round((b + d) / 2, 4), 0.1008], s=[round(max(abs(c_ - a), 0.003), 4), round(max(abs(d - b), 0.003), 4), 0.0014], m="red"))
INK += [dict(c=[0.068, y, 0.1002], s=[0.006, 0.012, 0.0014], m="paper") for y in (-0.04, -0.015, 0.01, 0.035)]   # (torn teeth)
S["page14"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="paper", block_shape=[1.4, 0.95, 0.1], expect_blocks=1,
                   extras=INK)
S["webcam"]["prebuilt"] = S["cam_cap"]["prebuilt"] = True

# keep the camera out of the furniture, the walls and the roof beams; the south side of the cabin is open
FURN = [((-0.45, -0.15, 0.0), (0.45, 0.25, 0.5)), ((-0.15, 0.5, 0.0), (0.15, 0.8, 0.7)), ((-1.7, -1.0, 0.0), (-1.5, 1.7, 2.0)),
        ((1.3, -1.0, 0.0), (1.55, 1.7, 2.0)), ((-1.7, 1.5, 0.0), (1.55, 1.7, 2.0))]
def AIR(eye):
    x, y, z = eye
    if not (-1.45 < x < 1.25 and -3.0 < y < 1.45 and 0.25 < z < 1.85):
        return False
    return not any(all(lo[i] - 0.06 <= eye[i] <= hi[i] + 0.06 for i in range(3)) for lo, hi in FURN)

DESK = [((-0.27, -0.02, 0.44), (0.03, 0.2, 0.92)), ((LANT_T[0] - 0.04, LANT_T[1] - 0.04, 0.43), (LANT_T[0] + 0.04, LANT_T[1] + 0.04, 0.67)),
        ((0.18, 0.02, 0.47), (0.27, 0.1, 0.6))]
def clear_view(eye, pts):
    for p in pts:
        for k in range(1, 40):
            u = k / 40; q = [eye[i] + (p[i] - eye[i]) * u for i in range(3)]
            if any(all(lo[i] <= q[i] <= hi[i] for i in range(3)) for lo, hi in DESK):
                return False
    return True

# ---------------------------------------------------------------- lines
SIGNATURE = "You don't have to know everything. You just have to keep building."
LINES = [("home", "Home sweet home. Chat... we made it.", 0.92),
         ("better", "Ahh. That's better.", 0.88),
         ("learned", "So. Today we learned...", 0.9),
         ("cams", "Cams turn spinning into lifting.", 0.92),
         ("rot", "Wet wood, plus fungi, makes rot.", 0.92),
         ("scale", "A small drawing can make a big build.", 0.92),
         ("counter", "A counterweight does the heavy lifting.", 0.92),
         ("circuit", "And electricity needs a loop.", 0.92),
         ("sun", "Oh, and... thank you, sun.", 0.9),
         ("hungry", "And the scariest thing in the woods... was just hungry.", 0.86),
         ("signature", SIGNATURE, 0.86),
         ("night", "Goodnight, chat.", 0.86),
         ("hand", "...Huh. That's not my handwriting.", 0.9),
         ("aliens", "...Aliens. I KNEW it.", 0.95)]
GUESS = dict(home=2.6, better=1.4, learned=1.8, cams=2.2, rot=2.2, scale=2.4, counter=2.5, circuit=1.9, sun=2.0, hungry=3.8,
             signature=4.4, night=1.3, hand=2.4, aliens=1.9)
dur_file = os.path.join(HERE, "ep01_s011_durations.json")
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
def look(t0, t1, pos, body=False, **kw):
    act(type="look", when=t0, until=t1, body=body, pos=pos if pos == "camera" else [round(v, 3) for v in pos], **kw)
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)
def walk(t0, t1, to, via=()):
    act(type="move", to=[to[0], to[1], 0.0], via=[[v[0], v[1], 0.0] for v in via], when=t0, until=t1, face="path")

POSES = {
    "set_cam": dict(lean=0.12),                                      # (the holds steer his hands)
    "set_lantern": dict(lean=0.1),
    "count": dict(hand_L={"char": [0.17, -0.22, 0.72]}, head=(0.0, 0.04, 0.0)),      # (the left hand: the laptop is on his right)
    "close_book": dict(lean=0.1, hand_L={"world": [BOOK_AT[0] + 0.08, BOOK_AT[1] + 0.09, 0.57]}),
    "pick_page": dict(lean=0.16),
    "blow": dict(lean=0.3, head=(0.0, -0.12, 0.0)),
}
PCARRY = {"char": [-0.1, -0.1, 0.64]}                             # a page held to read, seated (below his chin)
CAM_CARRY = {"char": [-0.17, -0.12, 0.25]}                           # (the webcam's root: its body sits 0.35 above it)
LANT_CARRY = {"char": [0.24, -0.08, 0.44]}                           # hanging from his left hand by the bail
DOOR_OUT, DOOR_IN = (-2.05, 0.7), (-1.25, 0.7)

# 1. home: in through the door with the webcam and the lantern; the lamp clicks on
STAND = (0.05, 0.45)                                                # a step back from the table to set things down
walk(0.2, 3.0, STAND, via=[DOOR_IN, (-0.6, 0.52)])
DOOR_OPEN = [0.05, 0.6, 105.0]
LAMP_ON = 1.25
sfx("door_creak", 0.05, 0.6)
sfx("switch", LAMP_ON, 0.7)
s, e = say("home", 0.0, at=1.4)
face("content", s, e + 0.4)
T_ARR = 3.0
CAM_SET = T_ARR + 0.5
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R" if name == "webcam" else "none", when=-1.0, until=round(CAM_SET + 0.05, 3), reach=0.05,
        grip=[0.0, -0.1, 0.35],
        keys=[dict(t=-1.0, at=CAM_CARRY, rot=[0, 0, 0]), dict(t=round(CAM_SET - 0.6, 3), at=CAM_CARRY, rot=[0, 0, 0]),
              dict(t=round(CAM_SET - 0.25, 3), at=[CAM_HOME[0], CAM_HOME[1] + 0.12, CAM_HOME[2] + 0.12], rot=[0, 0, 0]),   # up over the screen...
              dict(t=round(CAM_SET, 3), at=CAM_HOME, rot=[0, 0, 0])])                                                 # ...and down on top
    act(type="hold", target=name, hand="none", when=round(CAM_SET + 0.17, 3), until=99.0, reach=0.05,
        keys=[dict(t=round(CAM_SET + 0.17, 3), at=CAM_HOME, rot=[0, 0, 0]), dict(t=99.0, at=CAM_HOME, rot=[0, 0, 0])])
pose("set_cam", CAM_SET - 0.45, CAM_SET + 0.15, ease=0.2)
sfx("clink", CAM_SET, 0.4)
LANT_SET = CAM_SET + 0.9
act(type="hold", target="hand_lantern", hand="L", when=-1.0, until=round(LANT_SET + 0.05, 3), reach=0.05, grip=[0.0, 0.0, 0.17],
    keys=[dict(t=-1.0, at=LANT_CARRY, rot=[0, 0, 0]), dict(t=round(LANT_SET - 0.5, 3), at=LANT_CARRY, rot=[0, 0, 0]),
          dict(t=round(LANT_SET, 3), at=LANT_T, rot=[0, 0, 0])])
act(type="hold", target="hand_lantern", hand="none", when=round(LANT_SET + 0.17, 3), until=99.0, reach=0.05,
    keys=[dict(t=round(LANT_SET + 0.17, 3), at=LANT_T, rot=[0, 0, 0]), dict(t=99.0, at=LANT_T, rot=[0, 0, 0])])
pose("set_lantern", LANT_SET - 0.45, LANT_SET + 0.15, ease=0.2)
sfx("clink", LANT_SET, 0.35)
look(T_ARR - 0.2, LANT_SET + 0.3, (-0.12, 0.04, 0.7), body=True, rate=0.35)      # he turns to the desk (south) as he arrives
SQUARE = (SEAT_AT[0] + 0.33, SEAT_AT[1] - 0.9, 0.85)               # then settles square to the talking camera (20 deg east of south)
look(LANT_SET + 0.31, LANT_SET + 0.85, SQUARE, body=True, rate=0.25)
SIT = LANT_SET + 0.45
pose("seated", SIT, 99.0, ease_in=0.6)
act(type="move", to=[SEAT_AT[0], SEAT_AT[1], 0.0], via=[], when=round(SIT, 3), until=round(SIT + 0.5, 3))   # shuffles in as he sits
sfx("settle", SIT + 0.4, 0.7)
s, e = say("better", 0.0, at=SIT + 0.75)
face("content", s, e + 0.4, set=dict(lid=0.5, smile=0.7))
pose("lean_back", s, e + 0.3, ease=0.3)
look(SIT + 0.41, 99.0, SQUARE)                                      # underneath it all: head-only looks from here (body holds)

# 2. "Today we learned..." -- the recap card builds a line at a time
s, e = say("learned", 0.6)
look(s - 0.2, e + 0.2, "camera", rate=0.35)
face("smile", s, e + 0.3)
RECAP0 = s
ROWS = []
for lid, txt in (("cams", "CAMS turn spinning into lifting"), ("rot", "ROT: wet wood + fungi"), ("scale", "SCALE: small drawing, big build"),
                 ("counter", "a COUNTERWEIGHT lifts for you"), ("circuit", "a CIRCUIT needs a complete loop")):
    s, e = say(lid, 0.35)
    look(s - 0.2, e + 0.2, "camera", rate=0.35)
    pose("count", s - 0.1, e + 0.1, ease=0.2)
    face("content" if lid != "circuit" else "smirk", s, e + 0.2)
    ROWS.append((s + 0.1, txt))
RECAP1 = e + 0.6
s, e = say("sun", 0.6)
look(s - 0.3, s + 0.9, (-0.3, -1.2, 1.9), rate=0.3)                 # up, toward the window: the sun's gone down
look(s + 0.9, e + 0.2, "camera", rate=0.35)
face("smile", s, e + 0.3, set=dict(smile=0.8))
s, e = say("hungry", 0.8)                                           # sincere: no slang
look(s - 0.2, e + 0.2, "camera", rate=0.3)
face("warm", s + 0.4, e + 0.6)
s, e = say("signature", 0.9)
look(s - 0.2, e + 0.3, "camera", rate=0.3)
face("warm", s, e + 0.5, set=dict(smile=0.9))
pose("nod", e - 0.6, e + 0.1, ease=0.15)
SIG_E = e
# 3. chat says goodnight (always the same order; Tobias last); "Goodnight, chat."; the lamp clicks off
CHAT0 = SIG_E + 0.5
s, e = say("night", 0.0, at=CHAT0 + 3.6)
look(s - 0.3, e + 0.3, "camera", rate=0.3)
face("warm", s - 0.3, e + 0.5, set=dict(lid=0.45))
pose("wave_L", s + 0.1, e + 0.5, ease=0.25)
LAMP_OFF = e + 0.8
sfx("switch", LAMP_OFF, 0.7)
# 4. after dark: he closes the book -- a torn page slips out; someone else's handwriting
CLOSE = LAMP_OFF + 1.0
pose("close_book", CLOSE - 0.3, CLOSE + 0.5, ease=0.2)
look(LAMP_OFF + 0.4, CLOSE + 1.6, (BOOK_AT[0], BOOK_AT[1] - 0.05, TABLE_TOP), rate=0.25)
sfx("page", CLOSE, 0.6)
SLIP = CLOSE + 0.15
SLID = [BOOK_AT[0] + 0.02, BOOK_AT[1] + 0.21, round(TABLE_TOP - 0.05 + 0.005, 4)]   # out of the book, right to his edge of the table
PICK = SLIP + 1.2
act(type="hold", target="page14", hand="none", when=-1.0, until=round(PICK - 0.3, 3), reach=0.05,
    keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(SLIP - 0.02, 3), at=HIDE, rot=[0, 0, 0]),
          dict(t=round(SLIP, 3), at=[BOOK_AT[0], BOOK_AT[1], PAGES_AT[2] + 0.004], rot=[0, 0, 0]),
          dict(t=round(SLIP + 0.5, 3), at=SLID, rot=[0, 0, 12])])
sfx("page", SLIP + 0.3, 0.5)
P_HOLD = len(A)
act(type="hold", target="page14", hand="R", when=round(PICK, 3), until=99.0, reach=0.35, grip=[0.0, -0.04, 0.1],
    keys=[dict(t=round(PICK, 3), at=SLID, rot=[0, 0, 12]), dict(t=round(PICK + 0.6, 3), at=PCARRY, rot=[0, 0, 0])])
face("confused", PICK + 0.4, PICK + 2.0)
pose("pick_page", PICK - 0.4, PICK + 0.5, ease=0.2)
look(PICK + 0.5, PICK + 1.5, (0.0, -0.2, 0.75), rate=0.3)          # down at the page in his hand
s, e = say("hand", 0.0, at=PICK + 1.1)
face("squint", s, e + 0.4)
s, e = say("aliens", 0.7)
look(s - 0.3, e + 0.4, "camera", rate=0.4)
face("raised", s + 0.6, e + 0.6, set=dict(brow=1.2, smile=0.3))
BLOW = e + 1.0
pose("blow", BLOW - 0.3, BLOW + 0.6, ease=0.2)
look(BLOW - 0.5, BLOW + 0.8, (LANT_T[0], LANT_T[1], 0.55), rate=0.3)
sfx("blow", BLOW - 0.2, 0.8)
LANT_OFF = BLOW + 0.25
sfx("huff_far", LANT_OFF + 1.1, 0.3)                                 # far off in the dark: a friendly huff
END_CARD = LANT_OFF + 1.6
END = END_CARD + 4.5
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)
A[P_HOLD]["keys"].append(dict(t=round(FILM + 1.0, 3), at=PCARRY, rot=[0, 0, 0]))
# everything else from before: still, where it was put away
for name in ("book", "pages"):
    at_ = BOOK_AT if name == "book" else PAGES_AT
    act(type="hold", target=name, hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
        keys=[dict(t=-1.0, at=at_, rot=[0, 0, 0]), dict(t=round(FILM + 1.0, 3), at=at_, rot=[0, 0, 0])])
for name in ("page13", "bottle", "tester", "tester_led", "pulse", "thermos"):
    if name in S:
        act(type="hold", target=name, hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
            keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(FILM + 1.0, 3), at=HIDE, rot=[0, 0, 0])])
for name, at_ in (("prop", [-4.3, 1.88, 0.55]), ("solar_panel", [-2.4, 1.3, 0.0])):
    act(type="hold", target=name, hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
        keys=[dict(t=-1.0, at=at_, rot=[0, 0, 0]), dict(t=round(FILM + 1.0, 3), at=at_, rot=[0, 0, 0])])
PERIOD, CAM_GAP = 3.3, 0.55                                         # the waterwheel turns on outside; the hammer stays propped
T0_ = -PERIOD * 4
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="spin", target=name, axis="x", degrees=16.0, pivot=[-44, 13, 7], when=-3.0, until=-2.5)

lines = []
for i, (lid, text, speed) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if speed: ln["speed"] = speed
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["aliens"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (south side open: the front of the set)
SEATED = [(SEAT_AT[0], SEAT_AT[1], 0.66), (SEAT_AT[0], SEAT_AT[1], 1.05)]
cam = []
def cut(t, *a, **kw):
    tc = math.ceil(t * FPS - 1e-6) / FPS
    return lambda: ([dict(cam[-1], at=round(tc - 1.0 / FPS, 4))] if cam else []) + [auto_frame(tc, *a, **kw)]
SHOTS = [
    # in the door: wide across the cabin
    cut(0.0, [(DOOR_IN[0], DOOR_IN[1], 1.15), (DOOR_IN[0], DOOR_IN[1], 0.05), (SEAT_AT[0], SEAT_AT[1], 1.1), (LANT_T[0], LANT_T[1], 0.5)],
        (-0.6, 0.5, 0.7), -70, 14, 2.4, AIR),
    # sat down: square on, the desk between us
    cut(SIT + 0.6, SEATED + [(LANT_T[0], LANT_T[1], 0.5)], (0.08, 0.3, 0.8), -62, 10, 1.4, AIR, los=clear_view, margin=0.75),
    # the recap: a touch closer (the card builds above him)
    cut(RECAP0 - 0.3, SEATED, (0.0, 0.32, 0.88), -60, 8, 1.25, AIR, los=clear_view, margin=0.72),
    # the sincere bit and the signature line: close
    cut(LS["hungry"] - 0.3, SEATED, (0.0, 0.33, 0.9), -58, 6, 1.0, AIR, los=clear_view, margin=0.75),
    # chat says goodnight: back a little, the lamp and the lantern in frame
    cut(CHAT0 + 0.2, SEATED + [(LANT_T[0], LANT_T[1], 0.5)], (0.08, 0.3, 0.8), -64, 10, 1.5, AIR, los=clear_view, margin=0.75),
    # after dark: the book and the page, close
    cut(CLOSE - 0.2, [(BOOK_AT[0] - 0.12, BOOK_AT[1] - 0.1, TABLE_TOP), (BOOK_AT[0] + 0.14, BOOK_AT[1] + 0.08, TABLE_TOP), (SLID[0], SLID[1], TABLE_TOP)],
        (BOOK_AT[0], BOOK_AT[1] - 0.04, TABLE_TOP), -90, 48, 0.55, AIR),
    # reading it by lantern light; "Aliens. I KNEW it."; he blows the lantern out
    cut(PICK + 0.4, SEATED + [(LANT_T[0], LANT_T[1], 0.55)], (0.08, 0.3, 0.85), -60, 8, 1.2, AIR, los=clear_view, margin=0.75),
]
for shot in SHOTS:
    cam += shot()
cam, PATCHED = fix_path(cam, AIR, lambda t: SEATED)
CHAT = [(CHAT0, "GardenGranny", "night night dear"), (CHAT0 + 0.8, "lurker_77", "gn"),
        (CHAT0 + 1.6, "BoarFan2009", "night grandpa!! night boar!!"), (CHAT0 + 2.5, "TobiasBuilds", "night grandpa")]
cards = [dict(style="live", when=0.0, until=round(END_CARD, 3), viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until=round(END_CARD, 3), msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}, stay=5.5),
         dict(style="panel", y="top", border="amber", when=round(RECAP0, 3), until=round(RECAP1, 3),
              rows=[dict(text="TODAY WE LEARNED", color="white", at=round(RECAP0 + 0.1, 3), size=34)]
                   + [dict(text=txt, color="cyan", at=round(t, 3), size=24) for t, txt in ROWS]),
         dict(style="end", when=round(END_CARD, 3), until="end", title1="GRANDPA'S BLOCK LAB", title2="Episode 1: The Boar Next Door",
              sub="Next time: his own spot", cta="Subscribe for Episode 2")]
W11 = {k: v for k, v in S10["world"].items() if k not in ("critters", "lantern", "roof", "door_open")}
W11.update(time="night", animals=[], critters=[], door_open=DOOR_OPEN,
           lantern=[dict(at=[0.0, -0.45, 1.9], energy=55, on=LAMP_ON, off=LAMP_OFF),                        # the cabin lamp
                    dict(at=[LANT_T[0], LANT_T[1], LANT_T[2] + 0.13], energy=12, on=LANT_SET, off=LANT_OFF)])   # the lantern
story = dict(title="Goodnight, Chat", slug="grandpa_ep01_scene011", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["home"], tail=round(tail, 4), seed=47, blink=True, target_duration=60,
             engine_rev=3, scene=dict(episode=1, scene=11, name="Goodnight, Chat", previous="ep01_scene010", next="ep02_scene001"),
             world=W11, lines=lines, grandpa=dict(start=list(DOOR_OUT), outfit=S10["grandpa"]["outfit"], hold_heading=True),
             poses=dict(S10["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"]],
                     frame_points=["hat", "face", "chest"], seat="seat", seated_until=round(FILM, 3), seated_from=round(SIT + 0.7, 3),
                     solid=["table_top", "table_legs", "chair_back", "laptop_base", "laptop_screen", "mug"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene011.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-10s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("arrive %.2f sit %.2f recap %.2f-%.2f lamp off %.2f slip %.2f pick %.2f blow %.2f end card %.2f" % (T_ARR, SIT, RECAP0, RECAP1, LAMP_OFF, SLIP, PICK, BLOW, END_CARD))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
