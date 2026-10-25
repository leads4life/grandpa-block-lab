"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 03
"Up High, But..." (16:9, ~60 s). Script: scenes/raccoon_lift/scene03_script.md (standing authorization, 2026-10-25).
Morning by the stream: a tall tower (four posts, a platform 1.5 m up) with the food box built on top. Ladder rule.
That evening the mama and her kits climb it like trees (lesson: CLIMBERS -- claws, back feet that turn round), a clap from
far away and they climb down head first and trot off. "Up isn't enough." Hook: "unless the box only comes down when I
want it to." The tower stands by the stream, clear of the pines (raccoons jump from branches).
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene03"
S2 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene02.json"))
S, A = {}, []

# ---------------------------------------------------------------- the land as Scene 02 left it (Rule 1)
for name, st in S2["structures"].items():
    if name in ("lid", "leaves"):                                   # the stone lid and the leaves went in Scene 02
        continue
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
# (the hinged lid was left open in Scene 02; he has closed it again: it is simply shut here)

# ---------------------------------------------------------------- the tower by the stream (cells absolute, 0.1 m)
TX, TY = range(-47, -42), range(3, 8)                               # footprint x -4.7..-4.3, y 0.3..0.7
TOWER_C = (-4.5, 0.5)
POSTS = [(-47, 3), (-43, 3), (-47, 7), (-43, 7)]
def ring(z):
    return [[x, y, z] for x in TX for y in TY if (x in (TX[0], TX[-1]) or y in (TY[0], TY[-1])) and (x, y) not in POSTS]
S["posts"] = dict(cells=[[x, y, z] for x, y in POSTS for z in range(15)], at=[0.0, 0.0, 0.0], centered=False, material="wood",
                  block_shape=[0.8, 0.8, 1], expect_blocks=60)
S["braces"] = dict(cells=ring(5) + ring(10), at=[0.0, 0.0, 0.0], centered=False, material="planks", block_shape=[0.9, 0.9, 0.4],
                   expect_blocks=2 * len(ring(5)))
S["platform"] = dict(cells=[[x, y, 15] for x in TX for y in TY], at=[0.0, 0.0, -0.025], centered=False, material="planks",
                     block_shape=[1, 1, 0.5], expect_blocks=25)
S["foodbox"] = dict(cells=[[x, y, z] for x in range(-46, -43) for y in range(4, 7) for z in (16, 17)], at=[0.0, 0.0, -0.05],
                    centered=False, material="planks", expect_blocks=18)
PLAT_TOP = 1.55                                                     # 15.5 cells less 0.025 + half a block of 0.05
POST_SE = (-4.3, 0.3)                                               # the post the mama climbs (its east face at x -4.26)

# ---------------------------------------------------------------- lines
LINES = [("up", "Yesterday's lesson: they can open anything. So today... we go UP.", {}),
         ("ready", "Ready, chat? Blocks up!", {}),
         ("five", "Five feet up. Let's see those little hands reach THAT.", {}),
         ("ladder", "...With a ladder. And a grown-up holding the bottom. Always.", {}),
         ("climb", "No. No no no. They CLIMB?", dict(lens=False, why="said as they climb: the wide shot keeps them in view")),
         ("claws", "Sharp claws. And look -- they can turn their back feet around, and climb down head first.", {}),
         ("shoo", "Shoo. Go on.", dict(lens=False, why="called out to the raccoons, from far away")),
         ("enough", "Up was a good idea. But up isn't enough. They're better climbers than I am.", {}),
         ("unless", "...Unless the box only comes down when I want it to.", {})]
GUESS = dict(up=4.6, ready=2.1, five=3.4, ladder=4.2, climb=2.6, claws=6.0, shoo=1.3, enough=5.0, unless=3.4)
dur_file = os.path.join(HERE, "raccoon_s03_durations.json")
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
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "hands_hips": dict(hand_R={"char": [-0.24, 0.0, 0.62]}, hand_L={"char": [0.24, 0.0, 0.62]}, lean=-0.06),
    "look_up": dict(lean=-0.12, head=[0.0, 0.35, 0.0]),
    "crouch_watch": dict(lean=0.22, hips=[0.0, 0.0, -0.12]),
    "clap": dict(hand_R={"char": [-0.03, -0.32, 0.92]}, hand_L={"char": [0.03, -0.32, 0.92]}),
    "clap_open": dict(hand_R={"char": [-0.2, -0.3, 0.95]}, hand_L={"char": [0.2, -0.3, 0.95]}),
    "aghast": dict(lean=-0.08, shrug=0.5, elbows=0.5),
}
G0 = (-3.75, 0.48)                                                  # at the end of the path, east of the tower
G_FAR = (-3.25, 0.95)                                               # that evening: well back, by the garden
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. morning: "we go UP"; the tower goes up
s, e = say("up", 0.0, at=0.6)
to_lens(-1.0, e + 0.2)
face("content", s, s + 2.0)
face("smirk", e - 1.2, e + 0.4)
s, e = say("ready", 0.4)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", s + 0.6, e + 0.4, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=1.0))
B0 = e + 0.4
for name, d in (("posts", 2.6), ("braces", 1.6), ("platform", 1.4), ("foodbox", 1.4)):
    act(type="build", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0], order="z")
    B0 += d + 0.1
look(LE["ready"] + 0.3, B0, pos=(TOWER_C[0], TOWER_C[1], 0.9), body=True, rate=0.3)
s, e = say("five", 0.3, at=B0 + 0.2)
pose("hands_hips", s - 0.3, s + 1.5, ease=0.25)
look(s - 0.3, s + 1.3, pos=(TOWER_C[0], TOWER_C[1], 1.6), body=True, rate=0.3)
pose("look_up", s - 0.3, s + 1.3, ease=0.25)
to_lens(s + 1.4, e + 0.2)
face("smirk", s, e + 0.4)
CHAT = [(e + 0.4, "GardenGranny", "how do YOU get up there dear?")]
s, e = say("ladder", 1.6)
to_lens(s - 0.3, e + 0.2)
face("raised", s, s + 1.0, set=dict(brow=0.8))
face("content", s + 1.0, e + 0.3)

# 2. that evening: they climb it like a tree
TC = e + 1.0
walk(TC - 0.2, TC + 1.5, G_FAR, via=[(-3.45, 0.62)])
pose("crouch_watch", TC + 1.6, 99.0, ease=0.4)
look(TC + 1.5, 99.0, pos=(TOWER_C[0], TOWER_C[1], 0.8), body=True, rate=0.12)
IN = TC + 1.9                                                       # the family trots out of the woods
AT_POST = IN + 1.9
CLIMB1 = AT_POST + 1.6                                              # she is up
s, e = say("climb", 0.0, at=AT_POST + 0.7)
face("surprised", s - 0.2, e + 0.4, set=dict(brow=1.2))
pose("aghast", s, e + 0.2, ease=0.15)
CHAT += [(e + 0.3, "TobiasBuilds", "raccoons climb trees for fun grandpa")]
s, e = say("claws", 1.6)
LESSON0, LESSON1 = s, e
to_lens(s - 0.3, e + 0.2)
face("raised", s, e + 0.2, set=dict(brow=0.7, smile=0.2))
CLAP = e + 0.5
pose("clap_open", CLAP - 0.35, CLAP - 0.05, ease=0.1)
for k in range(2):
    pose("clap", CLAP + 0.3 * k - 0.08, CLAP + 0.3 * k + 0.08, ease=0.05)
    sfx("clap", CLAP + 0.3 * k, 1.0)
s, e = say("shoo", 0.0, at=CLAP + 0.7)
face("alert", CLAP - 0.2, e + 0.3)
DOWN0 = CLAP + 0.4                                                  # head first down the posts...
DOWN1 = DOWN0 + 1.4
GONE = DOWN1 + 1.8                                                  # ...and off to the stream
s, e = say("enough", 0.8, at=DOWN1 + 0.6)
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)
s, e = say("unless", 0.8)
look(s - 0.5, s + 1.4, pos=(TOWER_C[0], TOWER_C[1], 1.0), body=True, rate=0.25)
to_lens(s + 1.4, 99.0)
face("raised", s, s + 1.2, set=dict(brow=1.0))
face("smirk", s + 1.2, 99.0)
END = e + 1.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# the raccoons: up the posts (belly to the post), sit on the platform, then down head first and away
def climber(name, post, k, delay, seat):
    px, py = post
    face_x = px + 0.04 + 0.002                                      # the post's east face
    t_in, t_post = IN + delay, AT_POST + delay
    t_up = t_post + 1.3 * k + 0.3                                   # bigger legs, quicker climb
    top = PLAT_TOP + 0.005
    box_top = 1.755                                                 # they hop up and sit on the food box
    d0 = DOWN0 + delay * 0.6
    return dict(kind="raccoon", name=name, k=k, visible=[t_in, GONE + 0.5], heading=math.pi,
                path=[[t_in, -3.9, -0.95], [t_post - 0.6, face_x + 0.15, py], [t_post, face_x, py], [t_up, face_x, py],
                      [t_up + 0.5, seat[0], seat[1]], [d0 - 0.1, seat[0], seat[1]], [d0 + 0.3, face_x, py],
                      [d0 + 1.3, face_x, py], [d0 + 1.6, face_x + 0.15, py], [GONE + 0.5, -4.9, -0.6]],
                z=[[t_post, 0.0], [t_up, top], [t_up + 0.25, top], [t_up + 0.5, box_top], [d0 - 0.1, box_top], [d0 + 0.3, top],
                   [d0 + 1.2, 0.28], [d0 + 1.45, 0.0]],
                yaw=[[t_post, 180.0], [t_up + 0.6, 0.0]],                           # down: facing the post, nose first
                pitch=[[t_post - 0.1, 0.0], [t_post + 0.2, -90.0], [t_up - 0.1, -90.0], [t_up + 0.3, 0.0],
                       [d0 + 0.2, 0.0], [d0 + 0.45, 90.0], [d0 + 1.2, 90.0], [d0 + 1.45, 0.0]],
                poses=[[t_post + 0.1, t_up, "climb"], [t_up + 0.7, d0 - 0.1, "sit"], [d0 + 0.4, d0 + 1.3, "climb"]],
                chitters=[t_in + 0.3, t_up + 0.8], stride=0.09)
fam = [climber("Mama", POST_SE, 1.0, 0.0, (-4.52, 0.47)),
       climber("Kit0", (-4.3, 0.7), 0.6, 0.5, (-4.44, 0.6)),
       climber("Kit1", (-4.3, 0.7), 0.6, 1.1, (-4.6, 0.38))]

# the trip hammer keeps its clock by the stream (Rule 1)
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
for a in A:                                                         # every hold ends on a key at its end
    if a["type"] == "hold" and a["keys"][-1]["t"] < a["until"]:
        a["keys"].append(dict(a["keys"][-1], t=a["until"]))

lines = []
for i, (lid, text, extra) in enumerate(LINES):
    lines.append(dict(id=lid, text=text, pause=0.0, **extra))
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["unless"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (east of the tower, looking toward the stream)
def keyed(t0, t1, pts):
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)); out.append([tt, p[0], p[1]])
    return out
STOPS = [(0.0, G0)]
pos_now = G0
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
WALL_FREE = lambda eye: eye[0] < -1.95
TOWER_BOX = ((-4.75, 0.25, 0.0), (-4.25, 0.75, 1.8))
TOWER_FREE = lambda eye: not all(TOWER_BOX[0][i] - 0.15 <= eye[i] <= TOWER_BOX[1][i] + 0.15 for i in range(3))
AIR = both(clear_air, WALL_FREE, TOWER_FREE)
PATH = both(solid_free, WALL_FREE, TOWER_FREE)
LOS = make_los([TOWER_BOX] + SIGHT_BLOCKERS)
cam = []
def framed(t, must, tgt, az, el, d, *a, **kw):
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
TOWER_PTS = [(-4.7, 0.3, 0.02), (-4.3, 0.3, 0.02), (-4.3, 0.3, 1.62), (-4.7, 0.7, 1.62), (TOWER_C[0], TOWER_C[1], 1.78)]
SHOTS = [
    (0.0, (gp(*G0)[1:] + [(-4.3, 0.3, 0.8)], (G0[0] - 0.2, G0[1], 0.85), -20, 8, 1.8)),
    (LS["ready"] + 1.0, (gp(*G0) + TOWER_PTS, (-4.2, 0.45, 0.85), -30, 10, 3.2)),
    (LS["five"] - 0.3, (gp(*G0) + TOWER_PTS, (-4.2, 0.45, 0.9), -15, 6, 3.0)),
    (LS["ladder"] - 0.3, (gp(*G0)[1:], (G0[0], G0[1], 0.85), -10, 8, 1.5)),
    # that evening: wide -- the tower, the woods they come out of, him far back
    (TC, (TOWER_PTS + [(-3.9, -0.9, 0.05)] + gp(*G_FAR)[1:], (-4.0, 0.2, 0.75), -45, 12, 3.4)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
INS = (AT_POST + 0.1, AT_POST + 2.3)                                # insert: up the post, claws and all (a cutaway)
tc = math.ceil(INS[0] * FPS - 1e-6) / FPS
tc1 = math.ceil(INS[1] * FPS - 1e-6) / FPS
cam += [dict(cam[-1], at=round(tc - 1.0 / FPS, 4)), orbit(tc, (POST_SE[0], POST_SE[1], 0.5), -40, 10, 1.3),
        orbit(tc1 - 1.0 / FPS, (POST_SE[0], POST_SE[1], 1.3), -40, 14, 1.4)]
SHOTS2 = [
    (INS[1], (TOWER_PTS + gp(*G_FAR)[1:], (-4.0, 0.55, 0.9), -30, 10, 3.0)),
    (LS["claws"] - 0.3, (gp(*G_FAR)[1:], (G_FAR[0], G_FAR[1], 0.75), -20, 8, 1.6)),
    (CLAP - 0.4, (TOWER_PTS + gp(*G_FAR)[1:], (-4.0, 0.45, 0.9), -30, 10, 3.0)),
    (LS["enough"] - 0.3, (gp(*G_FAR)[1:], (G_FAR[0], G_FAR[1], 0.75), -20, 8, 1.6)),
]
for t, (must, tgt, az, el, d) in SHOTS2:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["shoo"] + 0.6, "BoarFan2009", "team raccoon 3, grandpa 0"), (LE["enough"] + 0.4, "GardenGranny", "ooh I know that look")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0})]),
         dict(style="title", text="THAT EVENING...", color="amber", y=185, size=80, when=round(TC, 3), until=round(TC + 2.4, 3)),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="CLIMBERS", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="sharp claws + back feet that turn around", color="cyan", at=round(LESSON0 + 1.4, 3), size=30)])]
W = {k: v for k, v in S2["world"].items() if k not in ("clouds_pass", "critters")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=fam,
         clouds_pass=[[round(TC + 1.6, 3), 2.0, 0.55, [1.0, 0.62, 0.32], True]])
story = dict(title="Up High, But...", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["up"], tail=round(tail, 4), seed=103, blink=True, target_duration=60,
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=3, name="Up High, But...", previous="raccoon_lift_scene02",
                                      next="raccoon_lift_scene04"),
             world=W, lines=lines, grandpa=dict(start=list(G0), outfit=S2["grandpa"]["outfit"]),
             poses=dict(S2["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"], cutaways=[[math.floor(tc * 1000) / 1000 - 0.001, math.ceil(tc1 * 1000) / 1000 + 0.001]],
                     solid=["posts", "braces", "platform", "crate", "stump", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("card %.2f in %.2f post %.2f clap %.2f down %.2f-%.2f" % (TC, IN, AT_POST, CLAP, DOWN0, DOWN1))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
