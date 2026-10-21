"""Grandpa's Block Lab, Episode 1, Scene 005 -- "The 4th Viewer" (16:9, ~30 s). Approved beat sheet (2026-10-21).
Starts from Scene 004's end. Rule 2: Grandpa picks the webcam back up before he goes anywhere. Rule 1: the 4th viewer who
joined at "welcome" (Scene 001) was Tobias, watching on his tablet; the tiny boot prints lead to the water -- across it
is his garden; the boar wants in because boars root for roots and grubs (micro-lesson). Hook: "And that's not even the
best thing I fixed." -- "...There's more?"
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, facing, both, BLOCKERS
from forest_camkit import make_los as _make_los
MACHINE = [((-4.45, 0.95, 0.70), (-4.35, 1.85, 0.80)),                       # the machine blocks the view of them: hammer arm,
             ((-4.55, 1.75, 0.0), (-4.25, 2.15, 0.5)), ((-4.55, 1.85, 0.5), (-4.25, 2.05, 0.7)),   # anvil and head,
             ((-5.05, 0.42, -0.05), (-4.95, 1.58, 1.15)), ((-4.55, 1.25, 0.0), (-4.45, 1.35, 0.8))]  # wheel, pivot post
make_los = lambda cast, **kw: _make_los(list(cast) + MACHINE, **kw)            # (sight lines only: not foreground clutter)
FPS = 30
S4 = json.load(open("/home/user/blocklab/stories/grandpa_ep01_scene004.json"))
C4 = json.load(open(os.path.join(HERE, "s4work/build/continuity.json")))
F4 = C4["film"]
S, A = {}, []

# ---------------------------------------------------------------- the world exactly as Scene 004 left it
for name, st in S4["structures"].items():
    cs = C4["structures"][name]
    if cs["blocks_standing"] == 0:
        continue
    st = json.loads(json.dumps(st))
    if name in ("webcam", "cam_cap"):
        r = cs["root"]
        st["at"] = [round(r[0][3], 4), round(r[1][3], 4), round(r[2][3], 4)]
        st["yaw"] = round(math.degrees(math.atan2(r[1][0], r[0][0])), 2)
    S[name] = st
CAM_ROOT = list(S["webcam"]["at"]); CAM_YAW = S["webcam"]["yaw"]
S["webcam"]["at"] = S["cam_cap"]["at"] = [0.0, 0.0, 0.0]; S["webcam"]["yaw"] = S["cam_cap"]["yaw"] = 0.0   # the holds place them
PROP_OUT = [round(C4["structures"]["prop"]["root"][i][3], 4) for i in range(3)]
# stepping stones across the stream, north of the machine (y 2.45), and Tobias's garden on the far bank
S["stones"] = dict(cells=[[-47, 24, 0], [-50, 24, 0], [-52, 24, 0]], at=[0.0, 0.05, -0.03], centered=False, material="stone",
                   block_shape=[1.6, 1.4, 0.5], expect_blocks=3, prebuilt=True)
S["garden_soil"] = dict(cells=[[x, y, 0] for x in range(-61, -55) for y in range(20, 28)], at=[0.0, 0.0, -0.045], centered=False,
                        material="soil", block_shape=[1, 1, 0.3], expect_blocks=48, prebuilt=True)
SPROUTS = [[x, y, 0] for y in (20, 21) for x in range(-60, -55)] + [[-60, 26, 0], [-58, 26, 0], [-57, 26, 0]]   # rows; a few survivors
S["sprouts"] = dict(cells=SPROUTS, at=[0.0, 0.0, 0.0], centered=False, material="sprout", block_shape=[0.35, 0.35, 0.7],
                    expect_blocks=len(SPROUTS), prebuilt=True)
HOLES = [[-59, 23, 0], [-58, 23, 0], [-57, 23, 0], [-58, 24, 0], [-60, 24, 0], [-59, 24, 0], [-56, 24, 0]]   # rooted: dark churned pits
S["holes"] = dict(cells=HOLES, at=[0.0, 0.0, -0.04], centered=False, material="coffee", block_shape=[1.0, 1.0, 0.3],
                  expect_blocks=len(HOLES), prebuilt=True)
CLODS = [[-59, 22, 0], [-56, 23, 0], [-58, 22, 0], [-60, 23, 0], [-57, 24, 0], [-61, 24, 0], [-59, 25, 0], [-57, 25, 0], [-55, 24, 0], [-61, 22, 0]]
S["clods"] = dict(cells=CLODS, at=[0.03, 0.04, -0.02], centered=False, material="soil", block_shape=[0.45, 0.45, 0.4],
                  expect_blocks=len(CLODS), prebuilt=True)
HOLES_PT = (-5.8, 2.38, 0.02)

# ---------------------------------------------------------------- lines (who: tobias -> his voice, his jaw)
LINES = [("saw", "Chat... you all saw that, right?", None),
         ("since", "I saw it too. I've been watching since 'welcome'.", "tobias"),
         ("fourth", "...You're my fourth viewer?", None),
         ("dayone", "So you're my... day one!", None),
         ("isday", "Grandpa. It IS day one.", "tobias"),
         ("garden", "Come see my garden.", "tobias"),
         ("knees", "Whoa... my knees did not agree to this.", None),
         ("holes", "See those holes? That's rooting. Boars dig with their snouts for roots... and grubs.", "tobias"),
         ("grubs", "Grubs? ...He can have those.", None),
         ("best", "And that's not even the best thing I fixed.", "tobias"),
         ("more", "...There's more?", None)]
GUESS = dict(saw=2.2, since=3.0, fourth=1.7, dayone=1.8, isday=1.5, garden=1.2, knees=2.3, holes=5.2, grubs=2.3, best=2.3, more=1.1)
dur_file = os.path.join(HERE, "ep01_s005_durations.json")
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

POSES = {
    "set_down": dict(lean=0.55, hips=[0.0, 0.0, -0.06]),
    "wobble_a": dict(hand_L=dict(char=(0.46, -0.04, 0.92)), twist=0.14, lean=-0.06),       # arms out on the stones
    "wobble_b": dict(hand_L=dict(char=(0.42, 0.02, 1.02)), twist=-0.14, lean=0.04),
    "peer_down": dict(lean=0.3, head=(0.0, -0.22, 0.0)),
}
CARRY = {"char": [-0.17, -0.18, 0.40]}                              # how he carries the webcam (Scenes 002-003)
G0 = C4["grandpa"]["root"]                                          # (-4.06, 1.56)
T0 = (-4.12, 2.18)                                                  # Tobias, by the anvil
P_SET = (-3.68, 0.92)                                               # where he stood to set the webcam down (Scene 003)
G_TALK = (-3.82, 1.86)                                              # facing Tobias
STONES = [(-4.7, 2.45), (-4.98, 2.45), (-5.18, 2.45)]
G_GARDEN, T_GARDEN = (-5.43, 2.42), (-6.0, 2.84)                     # Grandpa: east edge (off the stones); Tobias: north edge
face("warm", -5.0, 0.4, set=dict(C4["grandpa"]["face"]))
# 1. Rule 2: the webcam comes with him -- "Chat... you all saw that, right?"
walk(0.15, 1.45, P_SET, via=[(-3.75, 1.66), (-3.38, 1.45), (-3.4, 0.9), (-3.6, 0.72)])   # wide round the bank stone; in from the south
look(1.25, 2.5, pos=(CAM_ROOT[0], CAM_ROOT[1] + 0.03, 0.1), body=True, rate=0.2)
PICK = 1.75
pose("set_down", PICK - 0.5, PICK + 0.35, ease=0.3)
for name in ("webcam", "cam_cap"):
    act(type="hold", target=name, hand="R", when=round(PICK - 0.3, 3), until=round(99.0, 3), reach=0.3, grip=[0.0, -0.1, 0.48],
        keys=[dict(t=-1.0, at=CAM_ROOT, rot=[0, 0, CAM_YAW]), dict(t=round(PICK, 3), at=CAM_ROOT, rot=[0, 0, CAM_YAW]),
              dict(t=round(PICK + 0.55, 3), at=CARRY, rot=[0, 0, 0])])
sfx("settle", PICK + 0.05, 0.4)
s, e = say("saw", 0.0, at=PICK + 0.45)
face("raised", s, e + 0.2)
# 2. Tobias holds up his tablet: the stream, LIVE 4 viewers
walk(e - 0.2, e + 1.5, G_TALK, via=[(-3.42, 0.98), (-3.38, 1.42), (-3.58, 1.72)])
TAB0 = e + 0.3
s, e = say("since", 0.25)
LOOK_T = len(A); look(s - 0.3, 99.0, pos=(T0[0], T0[1], 0.55), body=True, rate=0.12)
s, e = say("fourth", 0.35)
face("surprised", s - 0.2, e + 0.1, set=dict(brow=1.1, smile=0.0))
s, e = say("dayone", 0.25)
face("smile", s - 0.1, e + 0.6)
TAB1 = e + 0.2
s, e = say("isday", 0.15)
# 3. across the stream on the stepping stones
s, e = say("garden", 0.3)
T_GO = e + 0.1
T_ARR = T_GO + 2.6
G_GO = T_GO + 0.5
G_ARR = G_GO + 3.4
A[LOOK_T]["until"] = round(G_GO, 3)
walk(G_GO, G_ARR, G_GARDEN, via=[(-4.02, 2.42), (-4.4, 2.45)] + STONES)
ON0 = G_GO + 3.4 * 0.33
ON1 = G_GO + 3.4 * 0.72
for k in range(int((ON1 - ON0) / 0.35)):                           # wobbling from stone to stone
    pose("wobble_a" if k % 2 == 0 else "wobble_b", ON0 + 0.35 * k, ON0 + 0.35 * (k + 1) + 0.15, ease=0.12)
s, e = say("knees", 0.0, at=ON0 + 0.25)
face("worried", s - 0.2, e + 0.3)
# 4. the garden: rooting (micro-lesson)
look(G_ARR - 0.3, 99.0, pos=HOLES_PT, body=True, rate=0.12)
s, e = say("holes", 0.25, at=max(T_ARR + 0.3, G_ARR - 0.6))
H_POINT = s + 0.2
pose("peer_down", s + 1.0, e - 0.4, ease=0.3)
face("confused", s + 1.4, e)
s, e = say("grubs", 0.25)
face("wince", s, s + 1.0)
face("content", s + 1.0, e + 0.3)
# 5. the hook
s, e = say("best", 0.3)
LOOK_END = len(A); look(s - 0.2, 99.0, pos=(T_GARDEN[0], T_GARDEN[1], 0.6), body=False)
s, e = say("more", 0.35)
act(type="face_camera", when=round(s - 0.25, 3), until=99.0)
face("surprised", s - 0.2, 99.0, set=dict(brow=1.2, smile=0.25))
END = e + 0.6
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)

# the machine keeps running on its clock; the prop stays where Tobias tossed it
PERIOD, CAM_GAP = 3.3, 0.55
TRIP4 = [a for a in S4["actions"] if a["type"] == "trip"][0]
FIRST = TRIP4["first"] - F4
FIRST = round(FIRST + PERIOD * math.ceil(-FIRST / PERIOD) - PERIOD, 4)
T0_ = FIRST - PERIOD * 3
TURN_DEG = -360.0 * (FILM + 1.0 - T0_) / PERIOD
for name, t0 in (("wheel", T0_), ("axle", T0_), ("cam1", T0_), ("cam2", T0_ + CAM_GAP)):
    act(type="spin", target=name, axis="x", degrees=round(TURN_DEG, 3), pivot=[-50, 10, 5], when=round(t0, 4), until=round(FILM + 1.0, 3),
        ease=False, ticks_per_turn=0)
HAMMER_HEAD = (-4.4, 1.95, 0.6)
for name in ("helve", "head"):
    act(type="trip", target=name, axis="x", pivot=[-44, 13, 7], degrees=16.0, period=PERIOD, first=FIRST, cams=[0.0, CAM_GAP],
        rise=0.45, drop=0.07, when=-10.0, until=round(FILM + 1.0, 3), **({"sound_at": list(HAMMER_HEAD)} if name == "head" else {}))
act(type="hold", target="prop", hand="none", when=-1.0, until=round(FILM + 1.0, 3), reach=0.05,
    keys=[dict(t=-1.0, at=PROP_OUT, rot=[0, 90, 0]), dict(t=round(FILM + 1.0, 3), at=PROP_OUT, rot=[0, 90, 0])])

# ---------------------------------------------------------------- Tobias (bl_cast)
deg = lambda a, b: round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 1)
T_PATH = [(-4.3, 2.42)] + STONES + [(-5.38, 2.74), T_GARDEN]
seg = [math.dist(a, b) for a, b in zip([T0] + T_PATH, T_PATH)]
tt, path = T_GO, [[0.0, T0[0], T0[1]], [round(T_GO, 3), T0[0], T0[1]]]
for p, d in zip(T_PATH, seg):
    tt += (T_ARR - T_GO) * d / sum(seg); path.append([round(tt, 3), p[0], p[1]])
tobias = dict(kind="tobias", stride=0.16, seed=11, path=path, hops=[[round(path[2][0], 3), round(path[5][0] + 0.2, 3)]],
              yaw=[[-1.0, deg(T0, G0)], [round(TAB0 - 0.4, 3), deg(T0, G_TALK)], [round(T_ARR, 3), deg(T_GARDEN, HOLES_PT)],
                   [round(LS["best"] - 0.2, 3), deg(T_GARDEN, G_GARDEN)]],
              tablet=[[round(TAB0, 3), round(TAB1, 3)]],
              poses=[[-1.0, round(FILM + 1.0, 3), "notebook_L"], [round(TAB0, 3), round(TAB1, 3), "hold_tablet"],
                     [round(LS["garden"], 3), round(LE["garden"] + 0.3, 3), "point_R"],
                     [round(H_POINT, 3), round(H_POINT + 2.0, 3), "point_down"]],
              faces=[[-1.0, "calm"], [round(LS["isday"], 3), "deadpan"], [round(LE["isday"] + 0.3, 3), "smile"],
                     [round(LS["holes"], 3), "calm"], [round(LS["best"], 3), "smile"]],
              look=[[round(LS["holes"], 3), round(LE["holes"], 3), list(HOLES_PT)]],
              visible=[-1.0, round(FILM + 1.0, 3)])

# ---------------------------------------------------------------- lines -> bl_voice
lines = []
for i, (lid, text, who) in enumerate(LINES):
    ln = dict(id=lid, text=text, pause=0.0)
    if who:
        ln["who"] = who
    lines.append(ln)
    if i:
        lines[i - 1]["pause"] = round(LS[lid] - LE[LINES[i - 1][0]], 3)
tail = FILM - LE["more"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera (forest rules, as in Scene 004)
def box_at(p, r=0.17, h=1.2):
    return ((p[0] - r, p[1] - r, 0.0), (p[0] + r, p[1] + r, h))
def kid(x, y):
    return [(x, y, 0.05), (x, y, 0.45), (x, y, 0.80)]
def g_at(t):                                                        # Grandpa's position (straight legs between his stops)
    stops = [(0.0, G0[:2]), (0.15, G0[:2]), (1.45, P_SET), (LE["saw"] - 0.2, P_SET), (LE["saw"] + 1.5, G_TALK), (G_GO, G_TALK), (G_ARR, G_GARDEN)]
    for (t0, a), (t1, b) in zip(stops, stops[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); return [a[i] + (b[i] - a[i]) * u for i in range(2)]
    return list(stops[-1][1]) if t > stops[-1][0] else list(G0[:2])
def who_at(t):
    return gp(*g_at(t))
L_TALK = make_los([box_at(G_TALK), box_at(T0, 0.12, 0.85)])
L_GARDEN = make_los([box_at(G_GARDEN), box_at(T_GARDEN, 0.12, 0.85)])
last = C4["camera"]["last_key"]
cam = [orbit(0.0, last["target"], last["az"], last["el"], last["dist"])]
TOB_TO_G = deg(T0, G_TALK); G_TO_TOB = deg(G_TALK, T0)
SHOTS = [
    lambda: auto_frame(PICK, gp(*P_SET) + [(CAM_ROOT[0], CAM_ROOT[1], 0.1)] + kid(*T0), (-3.85, 1.5, 0.5), -40, 14, 2.4, clear_air,
                       prev=cam, path_clear=solid_free, los=make_los([box_at(P_SET), box_at(T0, 0.12, 0.85)]), who=who_at),
    lambda: auto_frame(LS["since"] + 0.6, gp(*G_TALK) + kid(*T0), (-3.98, 2.0, 0.6), 10, 12, 1.9,
                       both(clear_air, facing(T0, TOB_TO_G, 70)), prev=cam, path_clear=solid_free, los=L_TALK, who=who_at),
    lambda: auto_frame(LS["fourth"] + 0.2, gp(*G_TALK) + [(T0[0], T0[1], 0.8)], (-3.97, 2.02, 0.75), round(G_TO_TOB - 90), 8, 1.9,
                       both(clear_air, facing(G_TALK, G_TO_TOB, 100)), apart=((G_TALK[0], G_TALK[1], 0.95), (T0[0], T0[1], 0.68)), apart_min=0.45,
                       prev=cam, path_clear=solid_free, los=L_TALK, who=who_at),          # side-on two-shot: both faces in profile
    lambda: auto_frame(G_GO + 0.3, gp(*G_TALK) + kid(-4.3, 2.42) + [(STONES[1][0], STONES[1][1], 0.05)], (-4.4, 2.3, 0.5), 15, 14, 2.3,
                       clear_air, prev=cam, path_clear=solid_free, los=make_los([]), who=who_at),
    lambda: auto_frame(LS["holes"] + 1.2, gp(*G_GARDEN) + kid(*T_GARDEN) + [HOLES_PT, (-5.95, 2.1, 0.05)], (-5.7, 2.5, 0.45), -70, 14, 2.6,
                       both(clear_air, facing(T_GARDEN, -90, 75)), apart=((G_GARDEN[0], G_GARDEN[1], 0.75), (T_GARDEN[0], T_GARDEN[1], 0.45)), apart_min=0.2,
                       prev=cam, path_clear=solid_free, los=L_GARDEN, who=who_at),
    lambda: auto_frame(LS["more"], gp(*G_GARDEN) + kid(*T_GARDEN), (-5.5, 2.35, 0.7), -60, 10, 1.9,
                       both(clear_air, facing(G_GARDEN, -40, 75)), prev=cam, path_clear=solid_free, los=L_GARDEN, who=who_at),
]
for shot in SHOTS:
    k = shot()
    cam += k if isinstance(k, list) else [k]
cam, PATCHED = fix_path(cam, clear_air, who_at, path_clear=solid_free)
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, C4["overlay"]["live_viewers"]]]),
         dict(style="panel", y="top", border="amber", when=round(LS["holes"] + 1.0, 3), until=round(LE["grubs"] + 0.2, 3), rows=[
             dict(text="ROOTING", color="white", at=round(LS["holes"] + 1.1, 3), size=40),
             dict(text="boars dig with their snouts for roots & grubs", color="cyan", at=round(LS["holes"] + 2.2, 3), size=32)])]
W5 = {k: v for k, v in S4["world"].items() if k != "critters"}
W5["critters"] = [tobias]
story = dict(title="The 4th Viewer", slug="grandpa_ep01_scene005", voice="am_santa", speed=0.95, format="wide",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["saw"], tail=round(tail, 4), seed=19, blink=True, target_duration=30,
             engine_rev=3, scene=dict(episode=1, scene=5, name="The 4th Viewer", previous="ep01_scene004", next="ep01_scene006"),
             world=W5, lines=lines, grandpa=dict(start=list(G0), outfit=S4["grandpa"]["outfit"]),
             poses=dict(S4["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(rests_on=[["mug", "table_top"], ["post2", "footing"]], frame_points=["hat", "face", "chest"],
                     solid=["wheel", "anvil", "pivot_frame", "head", "new_post", "footing", "post2", "rock", "helve"]))
json.dump(story, open("/home/user/blocklab/stories/grandpa_ep01_scene005.json", "w"), indent=1)
print("film %.2f s" % FILM)
for lid, _, who in LINES:
    print("  %-7s %-7s %6.2f-%6.2f" % (lid, who or "grandpa", LS[lid], LE[lid]))
print("pick %.2f tablet %.2f-%.2f tobias go %.2f arrive %.2f grandpa go %.2f arrive %.2f stones %.2f-%.2f" % (PICK, TAB0, TAB1, T_GO, T_ARR, G_GO, G_ARR, ON0, ON1))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
