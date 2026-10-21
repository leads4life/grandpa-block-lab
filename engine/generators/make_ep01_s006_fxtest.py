"""Scene 006 effects test (~14 s, NOT an episode scene): Grandpa alone in Tobias's garden, as Scene 005 left him.
Tests the untested Scene 006 pieces before the full scene: the TV dream ripple, the memory cloud with the mini boar,
the echoing "You kinda bussin'!" (Scene 004's frozen voice), a dreamy murmur (aecho), the snap-out, and the 3D blueprint.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, make_los
FPS = 30
S5 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene005.json"))
C5 = json.load(open(os.path.join(HERE, "s5work/build/continuity.json")))
S, A = {}, []
for name, st in S5["structures"].items():
    if C5["structures"][name]["blocks_standing"] == 0:
        continue
    S[name] = json.loads(json.dumps(st))
PROP_OUT = [round(C5["structures"]["prop"]["root"][i][3], 4) for i in range(3)]

LINES = [("me", "...Just me, then.", None, None),
         ("murmur", "You kinda bussin'... you kinda bussin'...", 0.8, dict(aecho="0.8:0.7:180|360:0.35|0.22")),
         ("nope", "Nope. Nope nope nope.", 1.05, None),
         ("fancy", "Ooh. Fancy.", None, None)]
GUESS = dict(me=1.4, murmur=3.6, nope=1.8, fancy=1.1)
dur_file = os.path.join(HERE, "ep01_s006fx_durations.json")
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

POSES = {"dreamy": dict(head=(0.0, 0.16, 0.10), lean=-0.04),           # chin up, head tilted: lost in the memory
         "peer_down": dict(lean=0.3, head=(0.0, -0.22, 0.0))}
CARRY = {"char": [-0.17, -0.18, 0.40]}
G = C5["grandpa"]["root"]                                            # (-5.43, 2.42)
HEAD_TOP = (G[0], G[1], 1.12)
CAM_AZ = 68                                                          # camera north-east of him: the machine stays behind, out of the way
R_ = math.radians(CAM_AZ + 90)                                       # screen-right of him, a little toward us, at bench height
HOLO = (G[0] + 0.42 * math.cos(R_) + 0.2 * math.cos(math.radians(CAM_AZ)), G[1] + 0.42 * math.sin(R_) + 0.2 * math.sin(math.radians(CAM_AZ)), 0.45)

face("content", -5.0, 0.2, set=dict(C5["grandpa"]["face"]))
act(type="face_camera", when=0.0, until=99.0)
s, e = say("me", 0.0, at=0.4)
face("worried", s, e + 0.5)
# the flashback: the picture ripples, the cloud drifts in, the memory echoes, he drifts off with it
DREAM0 = e + 0.5
ECHO_T = DREAM0 + 0.5
ECHO_REPS = 4
s, e = say("murmur", 0.0, at=ECHO_T + 2.5)              # he hears it twice, then drifts in and says it along with it
pose("dreamy", DREAM0 + 0.2, e + 1.0, ease=0.5)
face("content", DREAM0 + 0.2, e + 1.0, set=dict(lid=0.45, smile=0.45))
DREAM1 = max(e + 0.9, ECHO_T + 1.25 * (ECHO_REPS - 1) + 1.2)
sfx_ = dict(type="sfx", sound="echo|grandpa_ep01_scene004|bussin|%d" % ECHO_REPS, when=round(ECHO_T, 3), gain=0.9)
A.append(sfx_)
CLOUD = dict(kind="memory_cloud", at=[HEAD_TOP[0], HEAD_TOP[1], HEAD_TOP[2] + 0.46], visible=[round(DREAM0 + 0.3, 3), round(DREAM1, 3)],
             face=CAM_AZ + 90, yaw=180.0,
             boar=dict(huffs=[round(ECHO_T + 0.4 + 1.25 * k, 3) for k in range(ECHO_REPS)],
                       stomps=[round(ECHO_T + 0.9 + 1.25 * k, 3) for k in range(ECHO_REPS - 1)],
                       clacks=[round(ECHO_T + 1.6, 3)]))
# snap out of it
s, e = say("nope", 0.15, at=DREAM1 + 0.1)
pose("head_shake", s - 0.05, e + 0.1)
face("alert", s - 0.1, e + 0.5)
# the 3D blueprint lifts off "the page" in front of him
H0 = e + 0.6
HOLO_C = dict(kind="hologram", model="lever_gate", at=[round(v, 3) for v in HOLO], visible=[round(H0, 3), round(H0 + 3.0, 3)], yaw=CAM_AZ + 90)
pose("peer_down", H0 - 0.3, H0 + 3.2, ease=0.4)
act(type="look", when=round(H0 - 0.4, 3), until=round(H0 + 3.4, 3), body=False, pos=[round(v, 3) for v in HOLO])
s, e = say("fancy", 0.0, at=H0 + 0.9)
face("raised", s - 0.2, e + 0.6, set=dict(smile=0.5))
END = max(e, H0 + 3.0) + 0.7
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
for name in ("webcam", "cam_cap"):                                   # still carrying the stream (Rule 2)
    act(type="hold", target=name, hand="R", when=-1.0, until=round(FILM + 1.0, 3), reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CARRY, rot=[0, 0, 0]), dict(t=round(FILM + 1.0, 3), at=CARRY, rot=[0, 0, 0])])
act(type="hold", target="prop", hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
    keys=[dict(t=-1.0, at=PROP_OUT, rot=[0, 90, 0]), dict(t=round(FILM + 1.0, 3), at=PROP_OUT, rot=[0, 90, 0])])
# the machine keeps its clock (as in Scene 005)
PERIOD, CAM_GAP = 3.3, 0.55
TRIP5 = [a for a in S5["actions"] if a["type"] == "trip"][0]
FIRST = TRIP5["first"] - C5["film"]
FIRST = round(FIRST + PERIOD * math.ceil(-FIRST / PERIOD) - PERIOD, 4)
T0_ = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": [-4.4, 1.95, 0.6]} if name == "head" else {}))

lines = []
for i, (lid, text, speed, fx) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if speed: ln["speed"] = speed
    if fx: ln["fx"] = fx
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["fancy"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

who_at = lambda t: gp(G[0], G[1])
L = make_los([((G[0] - 0.17, G[1] - 0.17, 0.0), (G[0] + 0.17, G[1] + 0.17, 1.2))])
cam = [orbit(0.0, [G[0], G[1], 1.0], CAM_AZ, 10, 2.4), orbit(DREAM0, [G[0], G[1], 1.0], CAM_AZ, 10, 2.4),
       orbit(DREAM1 - 0.5, [G[0], G[1], 1.3], CAM_AZ - 3, 11, 2.15),             # a slow push in while he's lost in it
       orbit(LS["nope"] + 0.2, [G[0], G[1], 1.0], CAM_AZ, 10, 2.4),              # (and back out as he snaps out of it)
       orbit(H0 - 0.6, [G[0], G[1], 1.0], CAM_AZ, 10, 2.4), orbit(H0 + 0.8, [HOLO[0] * 0.5 + G[0] * 0.5, HOLO[1] * 0.5 + G[1] * 0.5, 0.8], CAM_AZ + 4, 14, 2.1)]
cam, PATCHED = fix_path(cam, clear_air, who_at, path_clear=solid_free)
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C5["overlay"]["live_viewers"]]]),
         dict(style="dream", when=round(DREAM0, 3), until=round(DREAM1 + 0.1, 3))]
W = {k: v for k, v in S5["world"].items() if k != "critters"}
W["critters"] = [CLOUD, HOLO_C]
story = dict(title="Scene 006 effects test", slug="grandpa_ep01_s006fx", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["me"], tail=round(tail, 4), seed=23, blink=True, target_duration=14,
             engine_rev=3, scene=dict(episode=1, scene=6, name="effects test", previous="ep01_scene005", next=""),
             world=W, lines=lines, grandpa=dict(start=list(G), outfit=S5["grandpa"]["outfit"]),
             poses=dict(S5["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=S5["qa"])
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_s006fx.json", "w"), indent=1)
print("film %.2f s | dream %.2f-%.2f echo %.2f | holo %.2f" % (FILM, DREAM0, DREAM1, ECHO_T, H0))
for lid, *_ in LINES:
    print("  %-7s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
