"""Grandpa's Block Lab, Episode 1, Scene 002 -- "Clunk, Clunk... Rest." (16:9, ~30 s).
Starts from Scene 001's continuity file. Rule 1: the Scene 001 clunks (two strikes 0.55 s apart, then silence) set the
machine: a water-powered trip hammer, 2 cams 60 deg apart, one turn every 3.3 s, so every strike lands on the established
beat (scene-001 strikes at 30.98 s and 31.53 s; Scene 001 lasts 33.00 s).
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, B = 30, 0.1
FILM_GUESS = 40.0
S1 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene001.json"))
C1 = json.load(open("/home/user/blocklab/ep01_scene001/grandpa_ep01_scene001_continuity.json"))
S, A = {}, []

def add(p, q):
    return [round(p[i] + q[i], 4) for i in range(3)]
def rotz(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2])

# ---------------------------------------------------------------- the cabin exactly as Scene 001 left it
for name, st in S1["structures"].items():
    st = json.loads(json.dumps(st))
    root = C1["structures"][name]["root"]
    t = [root[0][3], root[1][3], root[2][3]]
    if name in ("webcam", "cam_cap", "laptop_base", "laptop_screen", "mug"):
        st["at"] = [round(v, 4) for v in t]
    else:
        st["at"] = [round(t[0], 4), round(t[1], 4), round(t[2], 4)]
    S[name] = st
LAP_AT, LAP_YAW = S["webcam"]["at"], S["webcam"].get("yaw", 0.0)
CUBE_OFF = (0.0, -0.1, 0.35)                                       # webcam cell centre in its own frame

# ---------------------------------------------------------------- the trip hammer by the stream (cells absolute, 0.1 m)
def st(name, cells, mat, shape=None, **kw):
    cells = sorted(set(tuple(c) for c in cells))
    S[name] = dict(cells=[list(c) for c in cells], at=[0.0, 0.0, 0.0], centered=False, material=mat, expect_blocks=len(cells),
                   prebuilt=True, **kw)
    if shape:
        S[name]["block_shape"] = shape
WX, WY, WZ = -50, 10, 5                                            # wheel hub cell: (-5.0, 1.0, 0.55) m, in the stream
wheel = []
for dy in range(-5, 6):
    for dz in range(-5, 6):
        r = math.hypot(dy, dz)
        if 4.5 <= r < 5.5 or (r < 4.5 and (dy == 0 or dz == 0)):   # rim + 4 spokes
            wheel.append((WX, WY + dy, WZ + dz))
for k in range(8):                                                 # 8 paddles on the rim
    a = 2 * math.pi * k / 8
    wheel.append((WX, WY + round(5.6 * math.cos(a)), WZ + round(5.6 * math.sin(a))))
st("wheel", wheel, "oldwood")
st("axle", [(x, WY, WZ) for x in range(WX + 1, -41)], "wood", [1, 0.6, 0.6])
CAM_X = -44
st("cam1", [(CAM_X, WY, WZ + 1)], "wood", [0.6, 0.6, 1], parts={"cam": "z > 0"})
st("cam2", [(CAM_X, WY, WZ + 1)], "wood", [0.6, 0.6, 1], parts={"cam": "z > 0"})
st("axle_posts", [(-47, WY, z) for z in range(0, WZ)] + [(-47, WY + 1, z) for z in range(0, 2)], "oldwood", [0.7, 0.7, 1])
st("new_post", [(-41, WY, z) for z in range(0, WZ)], "planks", [0.7, 0.7, 1])               # fresh repair (bright)
PIV_Y, HELVE_Z = 13, 7
st("helve", [(CAM_X, y, HELVE_Z) for y in range(WY, 19)], "wood", [1, 0.7, 0.7])                # the arm
st("head", [(CAM_X + dx, y, z) for dx in (-1, 0, 1) for y in (19, 20) for z in (5, 6)], "darkiron")   # the hammer head
st("anvil", [(CAM_X + dx, y, z) for dx in (-1, 0, 1) for y in (18, 19, 20, 21) for z in range(0, 5)], "stone")   # top 0.5 m
st("pivot_frame", [(CAM_X - 1, PIV_Y, z) for z in range(0, 8)], "oldwood", [0.7, 0.7, 1])              # one post, far side
st("new_pin", [(CAM_X + 1, PIV_Y, HELVE_Z)], "planks", [0.8, 0.8, 0.8])                                   # fresh pin, near side
HAMMER_HEAD = (CAM_X * B, 1.95, 0.6)
WHEEL_C, WHEEL_TOP, CAM_PT = (WX * B, WY * B, (WZ + 0.5) * B), (WX * B, WY * B, (WZ + 6) * B), (CAM_X * B, WY * B, (WZ + 1.5) * B)
NEW_POST_FACE = (-4.05, 1.0, 0.6)                                   # the bright new post he touches (east face)

# ---------------------------------------------------------------- lines (approved hook; the rest grows out of the clunk)
LINES = [("again", "There it is again."),
         ("chat", "Chat, I'm going AFK. That's away from keyboard. You're coming with me."),
         ("avenge", "If something eats me... at least it's good content."),
         ("count", "Hear that? Clunk, clunk... then a rest."),
         ("trip", "Ha! A trip hammer!"),
         ("how", "Water turns the wheel... and two bumps, called cams, lift the hammer... and drop it."),
         ("broken", "This thing's been broken for years..."),
         ("who", "These blocks are brand new... so who fixed it?")]
GUESS = dict(again=1.3, chat=5.5, avenge=3.6, count=2.8, machine=1.2, trip=1.5, how=5.0, broken=2.2, who=3.0)
dur_file = os.path.join(HERE, "ep01_s002_durations.json")
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

# the clunk clock: Scene 001 strikes at 30.98 / 31.53 s of a 33.00 s scene -> here, pairs at 1.28 / 1.83 + 3.3 k
PERIOD, CAM_GAP = 3.3, 0.55
FIRST = round(30.98 - 33.0 + PERIOD, 3)                            # 1.28
STRIKES = [round(FIRST + PERIOD * k + o, 3) for k in range(-1, 11) for o in (0.0, CAM_GAP)]
POSES = {
    "reach_cam": dict(lean=0.38, elbows=0.9),
    "hand_up_R": dict(hand_R=dict(char=[-0.2, -0.12, 0.88])),      # lift the hand first, then reach over the table
    "door_hand": dict(hand_L=dict(world=[-1.57, 0.87, 0.62])),
    "touch_post": dict(hand_L=dict(world=list(NEW_POST_FACE)), lean=0.12),
    "lean_listen": dict(head=[0.0, 0.0, 0.22], lean=0.05),
}
G0 = C1["grandpa"]["root"]
face("alert", -5.0, 3.0, ease_out=0.6, set=dict(C1["grandpa"]["face"]))       # exactly the face Scene 001 ended on
look(-5.0, 2.6, pos=(-1.6, 0.70, 0.95), body=True, rate=0.06)                  # still facing the door
pose("lean_listen", 0.9, 2.3, ease=0.35)
s, e = say("again", 0.0, at=STRIKES[3] + 0.2)                     # right after the second clunk (1.83)
# turns back for his webcam, picks it up (cap and all), talks into it
P1 = [-0.27, 0.47, 0.0]                                            # an arm's length back from the table edge
walk(e - 0.2, e + 0.75, P1)
look(e - 0.2, e + 1.4, obj="webcam", off=CUBE_OFF, body=True, rate=0.12)
PICK = e + 0.85
pose("reach_cam", PICK - 0.45, PICK + 0.4, ease=0.3)
pose("hand_up_R", PICK - 1.0, PICK - 0.15, ease=0.3)
CARRY = {"char": [-0.17, -0.18, 0.40]}                             # webcam root, so the cam sits at his chest, lens toward him
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R", when=PICK, until=99.0, reach=0.4, grip=[0.0, -0.1, 0.48],   # by the top
        keys=[dict(t=PICK, at=list(LAP_AT), rot=[0, 0, LAP_YAW]), dict(t=PICK + 0.6, at=CARRY, rot=[0, 0, 0])])
sfx("clink", PICK + 0.02, 0.4)
s, e = say("chat", 0.15, at=PICK + 0.35)
look(PICK + 0.5, 99.0, obj="webcam", off=CUBE_OFF)                 # talks to his stream from now on (head only)
face("smirk", s + 0.2, e + 0.2)
# "If I'm not back in five minutes... avenge me." -- heads for the door
D_IN = [-1.33, 0.60, 0.0]
WALK1 = (e + 0.1, e + 1.5)
walk(*WALK1, D_IN, via=[(-0.40, 0.58, 0.0)])                       # back from the table first
s, e = say("avenge", 0.2)
face("worried", s + 0.1, s + 1.3)
face("side_eye", e - 1.0, e + 0.4)
OPEN = max(WALK1[1] + 0.05, e - 0.5)
pose("door_hand", OPEN - 0.35, OPEN + 0.6, ease=0.3)
DOOR = [round(OPEN, 3), round(OPEN + 0.9, 3), 125.0]                 # wide open: the doorway is clear
sfx("door_creak", OPEN + 0.02, 0.8)
# out of the door, round the sapling, along the path; the clunks get clearer
OUT = [-2.25, 0.40, 0.0]
WALK2 = (OPEN + 0.55, OPEN + 2.0)
walk(*WALK2, OUT, via=[(-1.95, 0.50, 0.0)])                        # clear of the sapling (canopy at y 0.72+)
CUT = round(math.ceil((WALK2[0] + 0.35) * FPS) / FPS, 4)           # match cut on him stepping through the door
after = lambda t: [s_ for s_ in STRIKES if s_ > t]
pair_after = lambda t: [s_ for i, s_ in enumerate(STRIKES) if i % 2 == 0 and s_ > t][0]   # first clunk of the next pair
# "Hear that? Clunk, clunk... then a rest." -- ends just before a pair lands, proving it
P_COUNT = pair_after(max(CUT, LE["avenge"] + 0.2) + D["count"] - 0.4 + 0.25)
s, e = say("count", 0.2, at=P_COUNT - 0.25 - D["count"])
pose("lean_listen", e - 0.3, P_COUNT + 0.8, ease=0.25)
REVEAL = P_COUNT                                                   # the pair after "...then a rest." lands on screen
CUT2 = round(math.ceil((REVEAL - 1.7) * FPS) / FPS, 4)             # cut: behind him, the machine coming into view
V = [-3.85, 0.45, 0.0]                                             # south-east of the machine: it stays in view beside him
WALK3 = (max(WALK2[1], s - 0.2), REVEAL - 0.15)
walk(*WALK3, V, via=[(-3.05, 0.45, 0.0)])
look(REVEAL - 1.0, 99.0, pos=HAMMER_HEAD, body=True, rate=0.1)    # eyes on the hammer (overrides the webcam look)
face("raised", REVEAL + 0.05, REVEAL + 1.0, ease=0.1)
face("surprised", REVEAL - 0.05, REVEAL + 0.7, ease=0.1)
s, e = say("trip", 0.0, at=REVEAL + CAM_GAP + 0.3)
face("warm", s, e + 0.4)
# "...and drop it." lands on a strike
DROP_WORD = 0.45                                                   # "drop" is said about 0.45 s before the line ends
DROP = [s_ for s_ in STRIKES if s_ + DROP_WORD - D["how"] >= e + 0.15 - 0.15][0]   # "drop" within 0.15 s of a strike
s, e = say("how", 0.15, at=DROP + DROP_WORD - D["how"])
DROP_ERR = round(s + D["how"] - DROP_WORD - DROP, 3)
look(s - 0.2, s + 1.4, pos=(-5.0, 1.0, 0.4), body=False)          # the wheel
look(s + 1.4, s + 3.0, pos=(CAM_X * B, 1.0, 0.6), body=False)      # the cams on the shaft
look(s + 3.0, e + 0.4, pos=HAMMER_HEAD, body=False)
act(type="point", target="helve", pos=[CAM_X * B, 1.0, 0.62], when=round(s + 1.5, 3), until=round(s + 3.0, 3))
for cam_name in ("cam1", "cam2"):                                    # glow on the cams as he names them
    act(type="highlight", target=cam_name, part="cam", when=round(s + 1.9, 3), until=round(s + 3.4, 3))
LS["stream"], LS["cams"], LE["cams"] = s, s + 1.4, e                 # (camera / card hooks)
# "This thing's been broken for years..." -- then he spots the bright new blocks
s, e = say("broken", 0.3)
face("content", s, e - 0.3)
STEP = (e - 0.4, e + 0.4)
walk(*STEP, [-3.84, 0.80, 0.0])
look(e - 0.5, 99.0, pos=(-4.1, 1.0, 0.5), body=True, rate=0.1)
pose("touch_post", e + 0.1, 99.0, ease=0.4)
face("confused", e - 0.1, e + 1.6)
s, e = say("who", 0.2)
face("alert", s + 1.6, 99.0, ease=0.25)
act(type="face_camera", when=round(s + 1.3, 3), until=round(FILM_GUESS + 2.0, 3))      # "...so who fixed it?" -- to us
sfx("tap", s + 0.05, 0.6)                                          # knuckles on the fresh wood
END = e + 0.6
for a in A:
    if a["type"] == "face_camera":
        a["until"] = 99.0
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# the machine runs the whole scene (started before it, so it is mid-turn at frame 0)
T0 = round(FIRST - PERIOD * 2, 4)
TURN_DEG = -360.0 * (FILM + 1.0 - T0) / PERIOD
for name, t0 in (("wheel", T0), ("axle", T0), ("cam1", T0), ("cam2", T0 + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[WX, WY, WZ], when=t0, until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[CAM_X, PIV_Y, HELVE_Z], degrees=16.0, period=PERIOD, first=FIRST,
        cams=[0.0, CAM_GAP], rise=0.45, drop=0.07, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": list(HAMMER_HEAD)} if name == "head" else {}))

# ---------------------------------------------------------------- lines -> bl_voice
lines = []
for i, (lid, text) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["who"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera: Scene 001's last shot -> match cut outside -> reveal
TAN_H = 18.0 / 35.0                                                # 35 mm lens, 36 mm sensor fit horizontal, 16:9
TAN_V = TAN_H * 9.0 / 16.0
def project(eye, tgt, p):
    f = [tgt[i] - eye[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]; rn = math.hypot(r[0], r[1]); r = [v / rn for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    d = [p[i] - eye[i] for i in range(3)]
    depth = sum(d[i] * f[i] for i in range(3))
    if depth <= 0.05:
        return None
    return (sum(d[i] * r[i] for i in range(3)) / depth / TAN_H, sum(d[i] * u[i] for i in range(3)) / depth / TAN_V)
def auto_frame(t, must, tgt, az0, el0, dist0, keep_clear, margin=0.82, apart=None):
    """Nearest camera (az, el, dist around tgt) to the wanted one that keeps every point of `must` inside the frame,
    stands in clear air (keep_clear(eye) is True) and, if `apart` = (a, b), keeps a and b at least 0.25 frame apart."""
    best = None
    for daz in range(-60, 61, 4):
        for el in range(8, 34, 3):
            for dist in [dist0 * k for k in (0.9, 1.0, 1.1, 1.25, 1.4, 1.6)]:
                az = az0 + daz
                ce = math.cos(math.radians(el))
                eye = (tgt[0] + dist * ce * math.cos(math.radians(az)), tgt[1] + dist * ce * math.sin(math.radians(az)),
                       tgt[2] + dist * math.sin(math.radians(el)))
                if not keep_clear(eye):
                    continue
                pr = [project(eye, tgt, p) for p in must]
                if any(q is None or abs(q[0]) > margin or abs(q[1]) > margin for q in pr):
                    continue
                if apart:
                    qa, qb = project(eye, tgt, apart[0]), project(eye, tgt, apart[1])
                    if qa is None or qb is None or math.hypot(qa[0] - qb[0], qa[1] - qb[1]) < 0.5:
                        continue
                cost = abs(daz) / 30 + abs(el - el0) / 10 + abs(dist / dist0 - 1) * 2
                if best is None or cost < best[0]:
                    best = (cost, az, el, round(dist, 3))
    if best is None:
        raise SystemExit("auto_frame: no clear camera for t=%.2f" % t)
    return orbit(t, tgt, best[1], best[2], best[3])
def clear_air(eye):                                                 # camera positions known to be free of trees / walls
    x, y, z = eye
    in_cabin = -1.72 < x < 1.52 and -0.9 < y < 1.72
    camera_zone = (-3.7 < x < -2.0 and -0.8 < y < 3.4) or (-6.2 < x < -3.6 and -0.2 < y < 3.0 and z > 1.2)
    return (not in_cabin) and camera_zone and z > 0.3
def gp(x, y):                                                       # grandpa standing at (x, y): boots, chest, hat
    return [(x, y, 0.05), (x, y, 0.75), (x, y, 1.18)]


def orbit(t, tgt, az, el, dist):
    return dict(at=round(t, 4), target=[round(v, 3) for v in tgt], az=az, el=el, dist=dist)
last = C1["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"]),
       orbit(LS["again"] + 0.3, last["target"], last["az"], last["el"], last["dist"]),
       orbit(PICK - 0.2, (-0.35, 0.40, 0.85), -95, 10, 2.0),
       orbit(LS["avenge"], (-0.75, 0.55, 0.88), -85, 9, 2.2),
       orbit(CUT - 1.0 / FPS, (-1.15, 0.62, 0.9), -72, 9, 2.1),      # inside, looking at the door (camera stays in the room)
       orbit(CUT, (-1.9, 0.6, 0.85), -152, 9, 2.0),               # outside, looking back at the door: the match cut
       orbit(WALK2[1], (-2.5, 0.48, 0.85), -165, 10, 1.9),
       orbit(CUT2 - 1.0 / FPS, (-3.0, 0.5, 0.85), -192, 10, 1.9),    # walking toward us (-192 = 168: turn the short way)
       auto_frame(CUT2, gp(-3.25, 0.45), (-3.9, 0.7, 0.75), 14, 10, 1.8, clear_air),         # cut: behind him, nearing the stream
       auto_frame(REVEAL - 0.5, gp(*V[:2]) + [WHEEL_C, HAMMER_HEAD], (-4.3, 0.95, 0.62), 20, 16, 2.2, clear_air),
       auto_frame(REVEAL + 0.4, gp(*V[:2]) + [WHEEL_C, WHEEL_TOP, HAMMER_HEAD, CAM_PT], (-4.35, 1.1, 0.55), 30, 24, 2.5,
                  clear_air, apart=(V[:2] + [0.8], WHEEL_C)),       # the reveal: Grandpa beside the whole machine
       auto_frame(LS["cams"] + 0.3, gp(*V[:2]) + [CAM_PT, (-4.4, 1.3, 0.75)], (-4.3, 0.85, 0.65), 25, 20, 1.7, clear_air),
       auto_frame(LE["cams"] - 0.6, gp(*V[:2]) + [WHEEL_C, HAMMER_HEAD, CAM_PT], (-4.35, 1.1, 0.55), 30, 22, 2.4, clear_air,
                  apart=(V[:2] + [0.8], WHEEL_C)),
       orbit(LS["who"], (-3.95, 0.8, 0.82), -30, 10, 1.65),
       orbit(FILM, (-3.95, 0.78, 0.85), -40, 10, 1.55)]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C1["overlay"]["live_viewers"]]]),
         dict(style="title", text="TRIP HAMMER", color="amber", y=185, size=88, when=round(LS["trip"] + 0.2, 3), until=round(LS["how"] + 0.4, 3)),
         dict(style="panel", y="top", border="cyan", when=round(LS["cams"] + 0.6, 3), until=round(LE["cams"] + 0.6, 3), rows=[
             dict(text="CAM: round and round", color="white", at=round(LS["cams"] + 0.7, 3), size=40),
             dict(text="becomes up and down", color="amber", at=round(LS["cams"] + 2.0, 3), size=40)])]
W1 = dict(S1["world"])
W1.update(terrain="forest_west", roof=True, door_open=DOOR)
story = dict(title="Clunk, Clunk... Rest.", slug="grandpa_ep01_scene002", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["again"], tail=round(tail, 4), seed=12, blink=True, target_duration=30, engine_rev=2,
             scene=dict(episode=1, scene=2, name="Clunk, Clunk... Rest.", previous="ep01_scene001", next="ep01_scene003"),
             world=W1, lines=lines, grandpa=dict(start=list(G0), outfit=S1["grandpa"]["outfit"]),
             poses=dict(S1["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"]], frame_points=["hat", "face", "chest"],
                     solid=["table_top", "table_legs", "seat", "chair_back", "laptop_base", "laptop_screen", "mug",
                            "wheel", "axle_posts", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene002.json", "w"), indent=1)
print("film %.2f s; speech %.2f s; strikes %s" % (FILM, sum(D[l] for l, _ in LINES), [s_ for s_ in STRIKES if 0 <= s_ <= FILM]))
for lid, _ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("pick %.2f open %.2f cut %.3f reveal %.2f; 'drop' lands %.2f s after its strike" % (PICK, OPEN, CUT, REVEAL, DROP_ERR))
