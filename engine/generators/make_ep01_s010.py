"""Grandpa's Block Lab, Episode 1, Scene 010 -- "Night Shift" (16:9, ~60 s). Approved beat sheet (2026-10-22).
Grandpa solo (Tobias only in chat). Later that night, out at the meadow garden: he has propped the trip hammer up (it's
quiet: tonight the fence works alone), hung a lantern on the fence's corner post and sits on a stump by the webcam with
a thermos. Stakeout (Word Card: STAKEOUT). He nods off; an owl wakes him ("Eyes like an eagle"). A huff: the boar
crosses the stream on the stepping stones -- the one "NO CAP, CHAT!" of 007-011. Its nose touches the wire: a tick, a
spark, it hops back, startled but fine ("...Sorry, buddy."). It doesn't leave: it roots in the soft ground outside the
fence. He works it out himself: "He doesn't want the garden. He wants grubs." It grunts happily and trots off.
"Chat... I think we just met our neighbour." Chat: "u should give him his own spot". "...His own spot."
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, fix_path
from forest_camkit import clear_air, solid_free, both
from forest_camkit import make_los as _make_los
FPS = 30
S9 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene009.json"))
C9 = json.load(open(os.path.join(HERE, "s9work/build/continuity.json")))
F9 = C9["film"]
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the world as Scene 009 left it (later that night)
def root_of(name):
    r = C9["structures"][name]["root"]
    return [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)]
for name, st in S9["structures"].items():
    if C9["structures"][name]["blocks_standing"] == 0:
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True                                           # everything from before is already there
    S[name] = st
for name in ("book", "pages", "page13", "bottle", "tester", "tester_led", "pulse"):   # put away (holds keep them out of sight)
    S[name]["at"] = [0.0, 0.0, 0.0]; S[name]["yaw"] = 0.0
PROP_IN = [-4.3, 1.88, 0.55]                                        # the hammer is propped up, as in Scene 004
S["solar_panel"]["at"] = [0.0, 0.0, 0.0]

# ---------------------------------------------------------------- new props: the stump he sits on, a thermos, the lantern
G_SIT = (-3.2, 1.0)
FACE_AT = (-3.8, 1.9)                                               # he faces north-west: the webcam to his left, the garden ahead-right
_h = math.atan2(FACE_AT[1] - G_SIT[1], FACE_AT[0] - G_SIT[0])
STUMP_C = (G_SIT[0] - 0.25 * math.cos(_h), G_SIT[1] - 0.25 * math.sin(_h))   # right under his hips (they sit back 0.22)
S["stump"] = dict(cells=[[x, y, z] for x in (0, 1, 2) for y in (0, 1, 2) for z in (-1, 0, 1)],
                  at=[round(STUMP_C[0] - 0.1, 3), round(STUMP_C[1] - 0.1, 3), 0.09],
                  centered=False, material="oldwood", block_shape=[1, 1, 1], expect_blocks=27, prebuilt=True)
S["thermos"] = dict(cells=[[0, 0, 0]], at=[0.0, 0.0, 0.0], centered=False, material="red", block_shape=[0.55, 0.55, 1.4], expect_blocks=1,
                    extras=[dict(c=[0.0, 0.0, 0.125], s=[0.06, 0.06, 0.02], m="steel")])          # its cup-lid
LANT = (-3.8, 1.37, 0.40)                                           # hung on the south face of the corner post
S["lantern"] = dict(cells=[[0, 0, 0]], at=[LANT[0], LANT[1], LANT[2] - 0.05], centered=False, material="darkiron",
                    block_shape=[0.5, 0.5, 0.15], expect_blocks=1, prebuilt=True,
                    extras=[dict(c=[0.0, 0.0, 0.09], s=[0.04, 0.04, 0.06], m="flame"),            # the glowing glass
                            dict(c=[0.0, 0.0, 0.13], s=[0.055, 0.055, 0.012], m="darkiron"),     # its cap
                            dict(c=[0.0, 0.025, 0.155], s=[0.008, 0.05, 0.008], m="darkiron")])  # the hook on the post
LANT2 = (-2.8, 3.13, 0.40)                                          # a second one on the north fence: "so we see him coming"
S["lantern2"] = json.loads(json.dumps(S["lantern"]))
S["lantern2"]["at"] = [LANT2[0], LANT2[1], LANT2[2] - 0.05]
S["lantern2"]["extras"][2]["c"] = [0.0, -0.025, 0.155]
STREAM_X = lambda y: -5.2 + 0.25 * math.sin(0.7 * y)
FENCE_BOXES = [((-3.9, 1.4, 0.0), (-2.2, 1.56, 0.5)), ((-3.9, 1.4, 0.0), (-3.74, 3.1, 0.5)),
               ((-3.9, 2.94, 0.0), (-2.2, 3.1, 0.5)), ((-2.36, 1.4, 0.0), (-2.2, 3.1, 0.5)), ((-3.33, 1.36, 0.0), (-2.57, 1.44, 0.9))]
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)), ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),
           ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.2)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8)),
           ((-4.6, 1.75, 0.5), (-4.2, 2.15, 0.95)), ((-4.5, 0.9, 0.6), (-4.3, 1.9, 0.95)),       # the hammer, propped up
           ((-3.35, 1.35, 0.0), (-2.55, 1.45, 0.8))]                                             # the lift gate
STUMP_BOX = ((STUMP_C[0] - 0.15, STUMP_C[1] - 0.15, 0.0), (STUMP_C[0] + 0.15, STUMP_C[1] + 0.15, 0.3))
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE, **kw)
def boxes_free(eye):
    return not any(all(lo[i] - 0.08 <= eye[i] <= hi[i] + 0.08 for i in range(3)) for lo, hi in FENCE_BOXES + [STUMP_BOX])
AIR = both(clear_air, boxes_free)
PATH = both(solid_free, boxes_free)

# ---------------------------------------------------------------- lines
LINES = [("stake", "Chat... we're whispering now. Hammer's off. Tonight, the fence works alone.", 0.9),
         ("stakeout", "This is a stakeout.", 0.9),
         ("hat", "I AM wearing a hat.", None),
         ("awake", "Awake! Totally awake. Eyes like an eagle.", 1.0),
         ("medium", "Chat, I'm not scared. I'm... medium-key nervous.", None),
         ("nocap", "NO CAP, CHAT!", 1.05),
         ("sorry", "...Sorry, buddy.", 0.85),
         ("seedlings", "He's not even looking at the seedlings...", 0.9),
         ("grubs", "He doesn't want the garden. He wants grubs.", 0.88),
         ("neighbour", "Chat... I think we just met our neighbour.", 0.9),
         ("spot", "...His own spot.", 0.88)]
GUESS = dict(stake=4.6, stakeout=1.4, hat=1.3, awake=3.3, medium=3.8, nocap=1.2, sorry=1.2, seedlings=2.3, grubs=3.0, neighbour=2.3, spot=1.4)
dur_file = os.path.join(HERE, "ep01_s010_durations.json")
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
    act(type="look", when=t0, until=t1, body=body, pos=[round(v, 3) for v in pos], **kw)
def sfx(sound, t, gain=1.0): act(type="sfx", sound=sound, when=t, gain=gain)

POSES = {
    "doze": dict(head=(0.0, -0.32, 0.12), lean=0.06, elbows=0.3),
    "jolt": dict(lean=-0.12, head=(0.0, 0.12, 0.0), shrug=0.5),
    "lean_watch": dict(lean=0.18, head=(0.0, -0.04, 0.0)),
    "freeze_seated": dict(shrug=0.7, elbows=0.25, lean=-0.08),
}
WEBCAM = (-3.81, 1.07, 0.18)                                        # on the bank stone, looking back at him
LAP = {"char": [-0.14, -0.2, 0.58]}                                # the thermos, held in his lap
for name in ("book", "pages", "page13", "bottle", "tester", "tester_led"):
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=99.0, at=HIDE, rot=[0, 0, 0])])
act(type="hold", target="prop", hand="none", when=-1.0, until=99.0, reach=0.05,
    keys=[dict(t=-1.0, at=PROP_IN, rot=[0, 0, 0]), dict(t=99.0, at=PROP_IN, rot=[0, 0, 0])])
act(type="hold", target="solar_panel", hand="none", when=-1.0, until=99.0, reach=0.05,
    keys=[dict(t=-1.0, at=[-2.4, 1.3, 0.0], rot=[0, 0, 0]), dict(t=99.0, at=[-2.4, 1.3, 0.0], rot=[0, 0, 0])])
pose("seated", -5.0, 99.0)
look(-5.0, -0.5, (FACE_AT[0], FACE_AT[1], 0.9), body=True, rate=0.5)   # (settled before we cut in)
face("content", -5.0, 0.6, ease_out=0.4)
TH = len(A)
act(type="hold", target="thermos", hand="R", when=-1.0, until=99.0, reach=0.05, grip=[0.0, 0.0, 0.05],
    keys=[dict(t=-1.0, at=LAP, rot=[0, 0, 0])])

# 1. the stakeout: whispering; the hammer's off; STAKEOUT (Word Card); "wear a hat dear"
s, e = say("stake", 0.0, at=1.0)
look(0.0, e + 0.2, WEBCAM)
face("side_eye", s + 0.2, s + 1.8)
face("content", s + 1.8, e + 0.3)
s, e = say("stakeout", 0.4)
WORD0 = s + 0.5
pose("lean_watch", s - 0.1, e + 0.4, ease=0.3)
face("smirk", s, e + 0.4)
HAT_CHAT = e + 0.3
s, e = say("hat", 1.5)
face("raised", s - 0.1, e + 0.4, set=dict(brow=0.9))
pose("nod", s + 0.3, e + 0.1, ease=0.15)
SIP0 = e + 0.7; SIP1 = SIP0 + 0.8
A[TH]["keys"] += [dict(t=round(SIP0 - 0.4, 3), at=LAP, rot=[0, 0, 0]), dict(t=round(SIP0, 3), at="mouth", off=[0.035, -0.075, -0.10], rot=[0, 0, 0]),
                  dict(t=round(SIP0 + 0.25, 3), at="mouth", off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
                  dict(t=round(SIP1 - 0.15, 3), at="mouth", off=[0.035, -0.07, -0.095], rot=[-22, 0, 0]),
                  dict(t=round(SIP1 + 0.35, 3), at=LAP, rot=[0, 0, 0])]
pose("sip", SIP0 - 0.1, SIP1 + 0.1, ease=0.25)
sfx("sip", SIP0 + 0.2, 0.7)
face("content", SIP0 + 0.1, SIP1 + 0.5)
# 2. he nods off (snores); an owl; he jolts awake
DOZE = SIP1 + 0.9
pose("doze", DOZE, DOZE + 5.6, ease=0.8)
face("content", DOZE, DOZE + 5.6, set=dict(lid=1.0, smile=0.1))
sfx("snore", DOZE + 0.7, 0.55); sfx("snore", DOZE + 3.1, 0.6)
OWL = DOZE + 5.0
sfx("owl", OWL, 0.55)
JOLT = DOZE + 5.6
pose("jolt", JOLT, JOLT + 0.6, ease=0.1)
sfx("settle", JOLT, 0.6)
face("surprised", JOLT, JOLT + 0.5, set=dict(brow=1.2))
s, e = say("awake", 0.0, at=JOLT + 0.35)
face("squint", s + 1.4, e + 0.3)                                    # eyes like an eagle
look(JOLT, e + 0.2, WEBCAM)
s, e = say("medium", 1.0)
face("worried", s, e + 0.3)
pose("shrug", s + 0.9, s + 1.8, ease=0.2)

# 3. a rustle... a huff, close: the boar comes over the stepping stones -- "NO CAP, CHAT!"
RUSTLE = e + 0.3
sfx("rustle", RUSTLE, 0.7)
BOAR_IN = (-5.6, 4.7)                                               # out of the forest to the north-west (the land ends east of x -3)
APPROACH = (-3.3, 3.95)
NOSE_STOP = (-3.05, 3.5)                                            # the boar's centre when its nose meets the north wire (y 3.06)
HUFF1 = RUSTLE + 1.0
look(RUSTLE + 0.2, HUFF1 + 0.3, (-4.3, 4.2, 0.3), rate=0.3)
face("alert", RUSTLE + 0.2, HUFF1 + 0.5, set=dict(brow=1.0))
s, e = say("nocap", 0.0, at=HUFF1 + 0.45)
NOCAP = s
pose("freeze_seated", s - 0.15, s + 2.6, ease=0.12)
face("surprised", s, e + 0.4, set=dict(brow=1.3, smile=-0.4))
JOIN = e + 0.6                                                      # TobiasBuilds logs in (3 -> 4)
B_ARR = e + 1.9
# 4. the fence works: sniff, sniff -- the nose touches the wire: tick, a spark; it hops back
SNIFF = B_ARR + 0.15
ZAP = B_ARR + 1.0
NOSE = (NOSE_STOP[0], NOSE_STOP[1] - 0.44, 0.3)
act(type="hold", target="pulse", hand="none", when=-1.0, until=99.0, reach=0.05,     # the pulse flashes at the wet nose
    keys=[dict(t=-1.0, at=HIDE, rot=[0, 0, 0]), dict(t=round(ZAP - 0.02, 3), at=HIDE, rot=[0, 0, 0]),
          dict(t=round(ZAP, 3), at=[NOSE[0], NOSE[1], NOSE[2] - 0.05], rot=[0, 0, 0]),
          dict(t=round(ZAP + 0.13, 3), at=[NOSE[0], NOSE[1], NOSE[2] - 0.05], rot=[0, 0, 0]),
          dict(t=round(ZAP + 0.15, 3), at=HIDE, rot=[0, 0, 0]), dict(t=99.0, at=HIDE, rot=[0, 0, 0])])
sfx("spark", ZAP, 0.9)
BACK = (-3.15, 3.88)
look(B_ARR - 0.8, ZAP + 1.2, (NOSE_STOP[0], NOSE_STOP[1] - 0.3, 0.25), rate=0.25)
pose("lean_watch", ZAP - 0.6, ZAP + 0.1, ease=0.2)
face("worried", ZAP - 0.2, ZAP + 0.8)
s, e = say("sorry", 0.0, at=ZAP + 1.3)
face("worried", s, e + 0.6, set=dict(tilt=0.9, smile=-0.1))
SORRY_E = e
# 5. it doesn't leave: it trots round to the soft ground outside the fence and roots there
ROOT_AT = (-3.7, 3.62)                                              # soft ground outside the north-west corner
LEAVE0 = ZAP + 2.6
ROOT0 = LEAVE0 + 1.4
look(LEAVE0, ROOT0 + 0.5, (ROOT_AT[0], ROOT_AT[1], 0.2), rate=0.2)
s, e = say("seedlings", 0.0, at=max(SORRY_E + 1.6, ROOT0 + 0.9))
face("confused", s, e + 0.4)
pose("lean_watch", s - 0.2, e + 0.3, ease=0.3)
s, e = say("grubs", 0.8)
face("raised", s, s + 1.2, set=dict(brow=0.8))
face("warm", s + 1.2, e + 0.8)                                      # sincere: he gets it
ROOT1 = e + 0.8
GRUNT = ROOT1 + 0.2
OUT0 = GRUNT + 0.8
OUT1 = OUT0 + 3.4
look(ROOT1, OUT0 + 1.5, (-4.8, 4.4, 0.25), rate=0.2)
# 6. "...our neighbour." chat; "...His own spot."
s, e = say("neighbour", 0.0, at=OUT0 + 0.9)
look(s - 0.3, e + 0.3, WEBCAM)
face("smile", s, e + 0.6, set=dict(smile=0.7))
CHAT_END = e
s, e = say("spot", 0.0, at=e + 3.0)
look(s - 0.6, 99.0, (ROOT_AT[0], ROOT_AT[1], 0.05), rate=0.15)
face("content", s - 0.4, 99.0, set=dict(smile=0.5, brow=0.3))
pose("lean_watch", s - 0.6, 99.0, ease=0.4)
sfx("huff_far", e + 0.9, 0.35)
END = e + 2.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)
A[TH]["keys"].append(dict(t=round(FILM + 1.0, 3), at=LAP, rot=[0, 0, 0]))

# the machine: the wheel keeps turning; the hammer stays propped up (no strikes all night)
PERIOD, CAM_GAP = 3.3, 0.55
T0_ = -PERIOD * 4
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="spin", target=name, axis="x", degrees=16.0, pivot=[-44, 13, 7], when=-3.0, until=-2.5)

# the boar (bl_cast): over the stepping stones, to the fence, a spark, back off, round to the soft ground, root, away
deg = lambda a, b: round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 1)
boar = dict(kind="boar", stride=0.17,
            path=[[0.0, BOAR_IN[0], BOAR_IN[1]], [round(HUFF1 - 1.4, 3), BOAR_IN[0], BOAR_IN[1]],
                  [round(HUFF1 + 0.6, 3), APPROACH[0], APPROACH[1]],
                  [round(B_ARR, 3), NOSE_STOP[0], NOSE_STOP[1]], [round(ZAP + 0.05, 3), NOSE_STOP[0], NOSE_STOP[1]],
                  [round(ZAP + 0.6, 3), BACK[0], BACK[1]], [round(LEAVE0, 3), BACK[0], BACK[1]],
                  [round(ROOT0, 3), ROOT_AT[0], ROOT_AT[1]], [round(OUT0, 3), ROOT_AT[0], ROOT_AT[1]],
                  [round(OUT0 + 1.6, 3), -4.6, 4.3], [round(OUT1, 3), -6.0, 4.75]],
            backing=[[round(ZAP + 0.05, 3), round(ZAP + 0.6, 3)]],
            yaw=[[round(ZAP + 0.6, 3), -90.0], [round(LEAVE0 - 0.05, 3), -90.0],      # (still facing the fence after backing off)
                 [round(ROOT0 + 0.01, 3), deg(BACK, ROOT_AT)], [round(ROOT0 + 0.5, 3), -60.0]],
            mood=[[-1.0, "calm"], [round(ZAP, 3), "agitated"], [round(ZAP + 2.4, 3), "calm"]],
            huffs=[round(HUFF1, 3), round(ZAP + 0.8, 3)], clacks=[round(ZAP + 1.4, 3)], stomps=[round(ZAP + 1.9, 3)],
            sniffs=[round(SNIFF, 3), round(ROOT0 + 0.1, 3)], grunts=[round(GRUNT, 3)], roots=[[round(ROOT0 + 0.5, 3), round(ROOT1, 3)]],
            startle=round(ZAP, 3), visible=[round(HUFF1 - 1.4, 3), round(OUT1 - 0.2, 3)])

lines = []
for i, (lid, text, speed) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if speed: ln["speed"] = speed
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["spot"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera
SP = [(G_SIT[0], G_SIT[1], 0.05), (G_SIT[0], G_SIT[1], 0.66), (G_SIT[0], G_SIT[1], 1.08)]   # seated: boots, chest, hat
def boar_box(p):
    return ((p[0] - 0.3, p[1] - 0.18, 0.0), (p[0] + 0.3, p[1] + 0.18, 0.4))
def bp_(p, z=0.25):
    return (p[0], p[1], z)
GBOX = ((G_SIT[0] - 0.2, G_SIT[1] - 0.2, 0.0), (G_SIT[0] + 0.2, G_SIT[1] + 0.2, 1.1))
LG = make_los([GBOX])
cam = []
def cut(t, *a, **kw):
    tc = math.ceil(t * FPS - 1e-6) / FPS
    return lambda: ([dict(cam[-1], at=round(tc - 1.0 / FPS, 4))] if cam else []) + [auto_frame(tc, *a, **kw)]
SHOTS = [
    # open: the lantern-lit stakeout, him on his stump, the garden behind him
    cut(0.0, SP + [LANT], (-3.4, 1.2, 0.6), 190, 10, 2.4, AIR, los=LG),
    # the nap: closer
    cut(DOZE - 0.3, SP[1:], (G_SIT[0], G_SIT[1], 0.85), 170, 12, 1.5, AIR, los=LG),
    # "medium-key nervous", then the rustle: wide to the stream -- the boar on the stepping stones
    cut(RUSTLE - 0.2, SP[1:] + [bp_(APPROACH, 0.2), bp_(NOSE_STOP, 0.2)], (-3.0, 2.6, 0.4), -100, 18, 3.5, AIR,
        los=make_los([GBOX])),
    # the fence: the boar's nose meets the wire; Grandpa beyond
    cut(B_ARR - 0.6, [bp_(NOSE_STOP, 0.05), bp_(NOSE_STOP, 0.35), NOSE, (BACK[0], BACK[1], 0.3)],
        (-3.0, 3.55, 0.3), 0, 14, 1.9, AIR, los=make_los([boar_box(NOSE_STOP)])),
    # "...Sorry, buddy.": on him
    cut(LS["sorry"] - 0.3, SP[1:], (G_SIT[0], G_SIT[1], 0.85), 145, 8, 1.6, AIR, los=LG),
    # rooting outside the fence; him watching
    cut(ROOT0 + 0.3, SP[1:] + [bp_(ROOT_AT, 0.05), bp_(ROOT_AT, 0.35)], (-3.4, 2.5, 0.4), 60, 22, 3.4, AIR,
        los=make_los([boar_box(ROOT_AT)])),
    # "He wants grubs.": on him (sincere)
    cut(LS["grubs"] - 0.2, SP[1:], (G_SIT[0], G_SIT[1], 0.85), 140, 6, 1.5, AIR, los=LG),
    # the grunt, away into the woods; "our neighbour"; "His own spot."
    cut(GRUNT - 0.3, SP[1:] + [bp_(ROOT_AT, 0.3), (-4.6, 4.3, 0.3)], (-3.6, 2.8, 0.4), 60, 22, 3.8, AIR,
        los=make_los([boar_box(ROOT_AT)])),
    cut(LS["neighbour"] - 0.3, SP[1:], (G_SIT[0], G_SIT[1], 0.85), 155, 10, 2.0, AIR, los=LG),
]
for shot in SHOTS:
    cam += shot()
who_at = lambda t: SP
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)
CHAT = [(HAT_CHAT, "GardenGranny", "wear a hat dear, its cold"),
        (DOZE + 1.6, "lurker_77", "zzz"),
        (NOCAP + 1.0, "BoarFan2009", "HES HERE!!!"),
        (JOIN + 0.4, "TobiasBuilds", "dont move grandpa"),
        (ZAP + 1.9, "TobiasBuilds", "hes fine. just surprised"),
        (CHAT_END + 0.2, "BoarFan2009", "TEAM BOAR"),
        (CHAT_END + 1.0, "TobiasBuilds", "u should give him his own spot")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 3], [round(JOIN, 3), 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="word", word="stakeout", say="stake-out", meaning="watching quietly, waiting for something to happen",
              when=round(WORD0, 3), until=round(WORD0 + 3.8, 3))]
W10 = {k: v for k, v in S9["world"].items() if k not in ("critters", "clouds_pass", "sun", "exposure")}
W10.update(time="night", animals=[], critters=[boar], lantern=[dict(at=[LANT[0], LANT[1], LANT[2] + 0.04], energy=22),
                                                              dict(at=[LANT2[0], LANT2[1], LANT2[2] + 0.04], energy=30)])
story = dict(title="Night Shift", slug="grandpa_ep01_scene010", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["stake"], tail=round(tail, 4), seed=43, blink=True, target_duration=60,
             engine_rev=3, scene=dict(episode=1, scene=10, name="Night Shift", previous="ep01_scene009", next="ep01_scene011"),
             world=W10, lines=lines, grandpa=dict(start=list(G_SIT), outfit=S9["grandpa"]["outfit"]),
             poses=dict(S9["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"], ["jar", "bench"], ["webcam", "rock"]],
                     frame_points=["hat", "face", "chest"], seat="stump", seated_until=round(FILM, 3),
                     solid=["wheel", "anvil", "pivot_frame", "new_post", "footing", "post2", "rock", "lean_posts", "bench_legs",
                            "pivot_post", "energizer"] + ["fence_posts_" + k for k in "swne"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene010.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-10s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("doze %.2f owl %.2f huff %.2f nocap %.2f arrive %.2f zap %.2f root %.2f-%.2f grunt %.2f out %.2f" % (DOZE, OWL, HUFF1, NOCAP, B_ARR, ZAP, ROOT0, ROOT1, GRUNT, OUT0))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
