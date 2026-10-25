"""Grandpa's Block Lab -- "Grandpa vs. the Raccoon Bandits: The Water-Balance Lift" (standalone), Scene 06
"Test 2: Stuck Halfway" (16:9, ~60 s). Script: scenes/raccoon_lift/scene06_script.md (standing authorization).
Straight on from Scene 05: the box hangs halfway; he finds the drip (water in = water out: BALANCED), plugs it, shuts the
gate. The build: a barrel for the bucket and a plank platform (on four ropes, like a swing) for the box. The agreed safety
beat: he steps onto the platform himself -- it rises about 1 m and stops; "I may have made a mistake"; the drain lets him
down gently; "Never ride a load lift." Then MEASURE: a stone-weight scale balances the crate against six stones.
Pass 1 synthesises the voice; pass 2 (--fit) re-times everything to the measured lines."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, "/home/user/blocklab")
from storykit import orbit, auto_frame, gp, fix_path
from forest_camkit import clear_air, solid_free, both, make_los
from propkit import STRAP
from raccoon_camkit import BLOCKERS as SIGHT_BLOCKERS
FPS = 30
SLUG = "raccoon_lift_scene06"
S5 = json.load(open("/home/user/blocklab/stories/raccoon_lift_scene05.json"))
S, A = {}, []
HIDE = [0.0, 0.0, -5.0]

# ---------------------------------------------------------------- the land as Scene 05 left it (Rule 1)
for name, st in S5["structures"].items():
    st = json.loads(json.dumps(st))
    st["prebuilt"] = True
    S[name] = st
FY = 7
BX, KX = -4.0, -4.45
PUL_Z, PUL_R = 2.25, 0.08
HALF = 0.6
S["liftbox"]["at"] = [0.0, 0.0, HALF]                                # stuck halfway (Scene 05's hook)
S["cabbages3"]["at"] = [0.0, 0.0, HALF - 0.005]
S["bucket"]["at"] = [0.0, 0.0, 1.2 - HALF]
S["gate"]["at"] = [S["gate"]["at"][0], 0.0, 0.03]                   # open a crack
S["cab_fly"]["at"] = [-5.2, -0.05, -0.04]                           # the swimmer, fished out onto the bank
S["stone_w"]["at"] = [KX + 0.2, 0.25, 0.04]

# ---------------------------------------------------------------- new: the barrel, the platform (and a crate for it), the scale
ZP0, ZK0 = 0.0, 1.2                                                 # platform down, barrel up
S["barrel"] = dict(cells=[[x, y, z] for x in (-46, -45, -44) for y in (6, 7, 8) for z in range(4)], at=[0.05, 0.0, ZK0 - 0.05],
                   centered=False, material="oldwood", expect_blocks=36)
S["barrel_bands"] = dict(cells=[[x, y, z] for x in (-46, -45, -44) for y in (6, 7, 8) for z in (0, 3) if x != -45 or y != 7],
                         at=[0.05, 0.0, ZK0 - 0.05], centered=False, material="darkiron", block_shape=[1.04, 1.04, 0.35], expect_blocks=16)
S["platform_l"] = dict(cells=[[x, y, 0] for x in range(-42, -38) for y in range(5, 9)], at=[0.05, 0.0, ZP0 - 0.03], centered=False,
                       material="planks", block_shape=[1, 1, 0.5], expect_blocks=16)   # 0.4 x 0.4 m, its top 0.05 m up
S["crate2"] = dict(cells=[[x, y, z] for x in range(-41, -39) for y in (6, 7) for z in range(2)], at=[0.05, 0.0, ZP0 + 0.05], centered=False,
                   material="planks", expect_blocks=8)
CRATE_SIDE = (-3.45, 0.12)                                          # where he sets the crate while he rides
S["crate_g"] = dict(cells=[[x, y, z] for x in range(2) for y in range(2) for z in range(2)], at=[CRATE_SIDE[0], CRATE_SIDE[1], 0.0],
                    centered=True, material="planks", expect_blocks=8)
SC = (-3.2, -0.15)                                                  # the stone-weight scale, on the path's south side
S["scale_base"] = dict(cells=[[0, 0, 0]], at=[SC[0], SC[1], 0.0], centered=True, material="stone", block_shape=[1.2, 1.2, 1.2], expect_blocks=1)
S["scale_plank"] = dict(cells=[[x, 0, 1] for x in range(-4, 5)], at=[SC[0], SC[1], 0.02], centered=True, material="planks",
                        block_shape=[1, 1.6, 0.35], expect_blocks=9)
S["scale_crate"] = dict(cells=[[x, y, z] for x in range(2) for y in range(2) for z in range(2)], at=[SC[0] - 0.33, SC[1], 0.135],
                        centered=True, material="planks", expect_blocks=8)
S["scale_stones"] = dict(cells=[[x, y, z] for x, y, z in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (1, 0, 1))],
                         at=[SC[0] + 0.33, SC[1], 0.135], centered=True, material="stone", block_shape=[0.85, 0.85, 0.85], expect_blocks=6)
TILT = -9.0                                                         # crate end down (about y: +x end rises for a negative turn)
FRAME_PTS = [(-4.7, 0.7, 0.02), (-3.7, 0.7, 0.02), (-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5)]
PL_C = (BX + 0.05, 0.7)                                             # the platform's centre (x -3.95)

# ---------------------------------------------------------------- lines
LINES = [("plug", "There! The plug's not in. Water in... water out. Same speed.", {}),
         ("balanced", "So the weight stays the same: balanced. Balanced things don't move.", {}),
         ("bigger", "Bigger box, bigger counterweight. Ready, chat? Blocks up!", {}),
         ("heavy", "Now. How heavy a load can it lift? Only one way to find out...", {}),
         ("whoa", "...Whoa. Whoa! Okay. Okay.", dict(lens=False, why="startled, hanging on as it rises")),
         ("mistake", "Chat... I may have made a mistake.", {}),
         ("never", "That was silly. Never ride a load lift. This lift is for cabbages. Never for people.", {}),
         ("measure", "The smart way: measure. Six stones of cabbage.", {}),
         ("tune", "So the barrel needs a little more than six stones of water. Tomorrow we tune it.", {})]
GUESS = dict(plug=4.6, balanced=4.6, bigger=4.2, heavy=4.4, whoa=2.4, mistake=2.6, never=6.0, measure=3.6, tune=5.0)
dur_file = os.path.join(HERE, "raccoon_s06_durations.json")
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
    to = list(to) + [0.0] * (3 - len(to))
    act(type="move", to=[to[0], to[1], to[2]], via=[list(v) + [0.0] * (3 - len(v)) for v in via], when=t0, until=t1, face="path")
def slide(names, t0, t1, dz):
    for n in names:
        act(type="slide", target=n, by=[0.0, 0.0, dz], when=round(t0, 3), until=round(t1, 3))
def turn(t0, t1, dz):
    for p in ("pulley_box", "pulley_bkt"):
        act(type="spin", target=p, axis="y", degrees=round(math.degrees(dz / PUL_R), 2), pivot=S[p]["cells"][0], when=round(t0, 3), until=round(t1, 3))
smoother = lambda u: (lambda v: v * v * v * (v * (v * 6 - 15) + 10))(max(0.0, min(1.0, u)))

POSES = {
    "point_low": dict(lean=0.2, hand_R={"char": [-0.12, -0.42, 0.55]}),
    "push_plug": dict(lean=0.25, hand_R={"world": [KX + 0.06, 0.6, 1.2 - HALF - 0.02]}),
    "pull_cord": dict(lean=0.1, hand_R={"world": [-4.7, 0.6, 0.95]}),
    "blocks_up": dict(lean=-0.1, hand_R={"char": [-0.22, -0.1, 1.3]}),
    "hold_ropes": dict(hand_R={"char": [-0.17, -0.12, 1.0]}, hand_L={"char": [0.17, -0.12, 1.0]}, shrug=0.3),
    "reach_drain": dict(hand_R={"char": [-0.3, 0.02, 0.95]}),
    "carry_box": dict(hand_R={"char": [-0.12, -0.3, 0.55]}, hand_L={"char": [0.12, -0.3, 0.55]}, lean=0.3),
}
G_CORD = (-4.62, 0.28)
G0 = (-3.6, 0.3)
for name in ("webcam", "cam_cap"):                                  # Rule 2: on the strap, hands free, all scene
    act(type="hold", target=name, hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[dict(t=-1.0, at={"char": STRAP}, rot=[0, 0, 0]), dict(t=99.0, at={"char": STRAP}, rot=[0, 0, 0])])

# 1. the drip: in = out, balanced
s, e = say("plug", 0.0, at=0.6)
pose("point_low", s, s + 1.4, ease=0.25)
look(-1.0, s + 1.4, pos=(KX + 0.06, 0.62, 0.3), body=True, rate=0.3)
to_lens(s + 1.5, e + 0.2)
face("raised", s, s + 1.2, set=dict(brow=1.1))
face("content", s + 1.2, e + 0.3)
PLUG = e + 0.4
walk(PLUG - 0.4, PLUG - 0.05, (KX + 0.05, 0.36))
pose("push_plug", PLUG, PLUG + 0.5, ease=0.15)
sfx("tap", PLUG + 0.25, 0.6)
s, e = say("balanced", 0.2, at=PLUG + 0.7)
LESSON0, LESSON1 = s, e
to_lens(s - 0.2, e + 0.2)
SHUT = e + 0.5
walk(e + 0.1, SHUT - 0.1, G_CORD)
pose("pull_cord", SHUT - 0.1, SHUT + 0.4, ease=0.12)
act(type="slide", target="gate", by=[0.0, 0.0, -0.03], when=round(SHUT, 3), until=round(SHUT + 0.15, 3))

# 2. the build: the barrel and the platform (the old box and bucket come down first)
s, e = say("bigger", 0.5)
to_lens(s - 0.3, e + 0.2)
pose("blocks_up", e - 0.9, e + 0.3, ease=0.2)
face("smile", s, e + 0.3, set=dict(smile=0.9))
B0 = e + 0.4
for name, d in (("cabbages3", 0.3), ("liftbox", 0.7), ("bucket", 0.5)):
    act(type="remove", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0])
    B0 += d + 0.05
for name, d in (("barrel", 1.4), ("barrel_bands", 0.4), ("platform_l", 0.9), ("crate2", 0.6)):
    act(type="build", target=name, when=round(B0, 3), until=round(B0 + d, 3), stand_at=[G0[0], G0[1], 0.0], order="z",
        **({"quiet": True} if name == "barrel_bands" else {}))
    B0 += d + 0.05
ROPES_ON = B0 - 2.0
look(LE["bigger"] + 0.3, B0, pos=(-4.2, 0.7, 1.0), body=True, rate=0.3)

# 3. the ride (about 1 m) -- the agreed safety beat
s, e = say("heavy", 0.4, at=B0 + 0.3)
to_lens(s - 0.3, e + 0.2)
face("smirk", s, e + 0.4)
LIFT_OFF = e + 0.6                                                  # he sets the crate down beside the lift...
walk(LIFT_OFF - 0.4, LIFT_OFF + 0.2, (PL_C[0] + 0.1, 0.3))
pose("carry_box", LIFT_OFF + 0.2, LIFT_OFF + 1.4, ease=0.2)
act(type="remove", target="crate2", when=round(LIFT_OFF + 0.3, 3), until=round(LIFT_OFF + 0.5, 3), stand_at=[PL_C[0] + 0.1, 0.3, 0.0], quiet=True)
act(type="build", target="crate_g", when=round(LIFT_OFF + 1.2, 3), until=round(LIFT_OFF + 1.4, 3), stand_at=[CRATE_SIDE[0] + 0.1, 0.32, 0.0], order="z")
OPEN = LIFT_OFF + 2.2                                               # ...opens the gate a little...
walk(LIFT_OFF + 1.5, OPEN - 0.1, G_CORD)
pose("pull_cord", OPEN - 0.1, OPEN + 0.4, ease=0.12)
act(type="slide", target="gate", by=[0.0, 0.0, 0.05], when=round(OPEN, 3), until=round(OPEN + 0.2, 3))
STEP = OPEN + 1.6                                                   # ...and steps onto the platform
PL_TOP = ZP0 + 0.05
walk(OPEN + 0.5, STEP, (PL_C[0], PL_C[1], PL_TOP), via=[(PL_C[0], 0.35, 0.0)])
CHAT = [(STEP - 0.6, "GardenGranny", "DEAR NO")]
RIDE0, RIDE1 = STEP + 1.2, STEP + 4.2
RIDE = 1.0
pose("hold_ropes", STEP + 0.2, 99.0, ease=0.3)
for q in range(1, 13):                                              # his feet stay on the planks as they rise
    t = RIDE0 + (RIDE1 - RIDE0) * q / 12
    act(type="move", to=[PL_C[0], PL_C[1], round(PL_TOP + RIDE * smoother(q / 12), 4)], via=[], when=round(t - (RIDE1 - RIDE0) / 12, 3), until=round(t, 3))
slide(["platform_l"], RIDE0, RIDE1, RIDE)
slide(["barrel", "barrel_bands"], RIDE0, RIDE1, -RIDE)
turn(RIDE0, RIDE1, RIDE)
sfx("creak", RIDE0 + 0.1, 0.5); sfx("creak", RIDE1 - 0.3, 0.35)
act(type="slide", target="gate", by=[0.0, 0.0, -0.05], when=round(RIDE1 - 0.2, 3), until=round(RIDE1, 3))   # (it shuts as the barrel brims)
s, e = say("whoa", 0.0, at=RIDE0 + 0.4)
face("surprised", RIDE0, e + 0.6, set=dict(brow=1.3))
look(RIDE0, e + 0.4, pos=(PL_C[0], PL_C[1] - 0.6, 0.0), body=False, rate=0.4)
s, e = say("mistake", 0.8, at=RIDE1 + 0.6)
to_lens(s - 0.3, e + 0.2)
face("worried", s, e + 0.4)
CHAT += [(e + 0.3, "TobiasBuilds", "grandpa that's a load lift")]
DRAIN0 = e + 1.2                                                    # the drain cord: down, gently
pose("reach_drain", DRAIN0 - 0.4, DRAIN0 + 0.4, ease=0.2)
DOWN0, DOWN1 = DRAIN0 + 0.8, DRAIN0 + 4.6
for q in range(1, 13):
    t = DOWN0 + (DOWN1 - DOWN0) * q / 12
    act(type="move", to=[PL_C[0], PL_C[1], round(PL_TOP + RIDE * (1 - smoother(q / 12)), 4)], via=[], when=round(t - (DOWN1 - DOWN0) / 12, 3), until=round(t, 3))
slide(["platform_l"], DOWN0, DOWN1, -RIDE)
slide(["barrel", "barrel_bands"], DOWN0, DOWN1, RIDE)
turn(DOWN0, DOWN1, -RIDE)
sfx("creak", DOWN0 + 0.2, 0.35)
OFF = DOWN1 + 0.5
act(type="pose", pose="hold_ropes", when=round(STEP + 0.2, 3), until=round(OFF, 3), ease=0.3)
for a in A:                                                         # (the ropes are let go of once he is off)
    if a["type"] == "pose" and a["pose"] == "hold_ropes" and a["until"] == 99.0:
        a["until"] = round(OFF, 3)
walk(OFF, OFF + 0.8, (PL_C[0] + 0.15, 0.25), via=[(PL_C[0], 0.4, 0.0)])

# 4. the plain safety line, then MEASURE
s, e = say("never", 0.4, at=OFF + 0.9)
to_lens(s - 0.3, e + 0.2)
face("content", s, e + 0.3)                                         # sincere: calm, no slang
SC0 = e + 0.4
walk(SC0, SC0 + 1.2, (SC[0], SC[1] + 0.35))
for name, d in (("scale_base", 0.3), ("scale_plank", 0.6), ("scale_crate", 0.5)):
    act(type="build", target=name, when=round(SC0 + 1.3, 3), until=round(SC0 + 1.3 + d, 3), stand_at=[SC[0], SC[1] + 0.35, 0.0], order="z")
    SC0 += d + 0.05
act(type="spin", target="scale_plank", axis="y", degrees=TILT, pivot=[0, 0, 1], when=round(SC0 + 1.3, 3), until=round(SC0 + 1.6, 3))
act(type="spin", target="scale_crate", axis="y", degrees=TILT, pivot=[3.8, 0.5, -0.15], when=round(SC0 + 1.3, 3), until=round(SC0 + 1.6, 3))
STONES = SC0 + 2.0
act(type="spin", target="scale_stones", axis="y", degrees=TILT, pivot=[-2.8, 0.5, -0.15], when=round(SC0 + 1.3, 3), until=round(SC0 + 1.6, 3))
act(type="build", target="scale_stones", when=round(STONES, 3), until=round(STONES + 2.4, 3), stand_at=[SC[0], SC[1] + 0.35, 0.0], order="z")
LEVEL = STONES + 2.4
act(type="spin", target="scale_plank", axis="y", degrees=-TILT, pivot=[0, 0, 1], when=round(LEVEL, 3), until=round(LEVEL + 0.4, 3))
act(type="spin", target="scale_crate", axis="y", degrees=-TILT, pivot=[3.8, 0.5, -0.15], when=round(LEVEL, 3), until=round(LEVEL + 0.4, 3))
act(type="spin", target="scale_stones", axis="y", degrees=-TILT, pivot=[-2.8, 0.5, -0.15], when=round(LEVEL, 3), until=round(LEVEL + 0.4, 3))
look(SC0 + 1.0, LEVEL + 0.5, pos=(SC[0], SC[1], 0.15), body=True, rate=0.3)
s, e = say("measure", 0.3, at=LEVEL + 0.3)
MEAS0, MEAS1 = s, e
to_lens(s - 0.3, e + 0.2)
face("smile", s, e + 0.3, set=dict(smile=0.7))
s, e = say("tune", 0.5)
look(s - 0.3, s + 1.2, pos=(KX, 0.7, 1.4), body=True, rate=0.3)
to_lens(s + 1.2, 99.0)
face("smirk", s + 1.2, 99.0)
END = e + 1.2
FILM = math.ceil(END * FPS) / FPS
for a in A:
    if a.get("until") == 99.0:
        a["until"] = round(FILM + 1.0, 3)
    for k in a.get("keys", []):
        if k["t"] == 99.0:
            k["t"] = round(FILM + 1.0, 3)

# ropes and water
BAR_TOP = [KX, 0.7, ZK0 + 0.35]
CORNERS = [(PL_C[0] + dx, PL_C[1] + dy) for dx in (-0.17, 0.17) for dy in (-0.17, 0.17)]
rig = dict(ropes=[dict(top=[BX, 0.7, PUL_Z], follow="liftbox", at=[BX, 0.7, HALF + 0.3], visible=[-1, LS["bigger"] + 1.5]),
                  dict(top=[KX, 0.7, PUL_Z], follow="bucket", at=[KX, 0.7, 1.2 - HALF + 0.3], visible=[-1, LS["bigger"] + 1.5]),
                  dict(top=[KX, 0.7, PUL_Z + PUL_R], follow="beam", at=[BX, 0.7, PUL_Z + PUL_R]),
                  dict(top=[-4.4, 0.95, 1.86], follow="frame_posts", at=[-4.7, 0.6, 0.95], width=0.008),
                  dict(top=[KX, 0.7, PUL_Z], follow="barrel", at=BAR_TOP, visible=[ROPES_ON, FILM + 1])]
                 + [dict(top=[BX, 0.7, PUL_Z - 0.05], follow="platform_l", at=[cx, cy, ZP0 + 0.05], width=0.01, visible=[ROPES_ON, FILM + 1])
                    for cx, cy in CORNERS],
           fills=[dict(follow="bucket", at=[KX, 0.7, 1.2 + 0.03 - HALF], size=[0.17, 0.17, 0.25], level=[[0.0, 0.55], [LS["bigger"] + 1.4, 0.55], [LS["bigger"] + 1.5, 0.0]]),
                  dict(follow="barrel", at=[KX + 0.05, 0.7, ZK0], size=[0.27, 0.27, 0.36], level=[[OPEN + 0.2, 0.0], [RIDE1, 1.0], [DRAIN0 + 0.4, 1.0], [DOWN1 + 0.5, 0.15]])],
           pours=[dict(**{"from": [-4.42, 0.9, 1.72]}, follow="bucket", at=[KX, 0.72, 1.2 - HALF + 0.3], on=[[-1.0, SHUT + 0.1]], width=0.012),
                  dict(**{"from": [KX + 0.06, 0.62, 1.2 - 0.01]}, from_follow="bucket", follow="frame_posts", at=[KX + 0.06, 0.62, -0.02], on=[[-1.0, PLUG + 0.3]], width=0.006),
                  dict(**{"from": [-4.42, 0.9, 1.72]}, follow="barrel", at=[KX + 0.05, 0.75, ZK0 + 0.36], on=[[OPEN + 0.1, RIDE1]], width=0.03),
                  dict(**{"from": [KX + 0.12, 0.6, ZK0 - 0.06]}, from_follow="barrel", follow="frame_posts", at=[KX + 0.12, 0.6, -0.02], on=[[DRAIN0 + 0.4, DOWN1 + 0.4]], width=0.025)])

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
tail = FILM - LE["tune"] - 0.5 / FPS
if "--fit" not in sys.argv:
    tail = max(tail, 2.0)

# ---------------------------------------------------------------- camera
def keyed(t0, t1, pts):
    seg = [math.dist(a[:2], b[:2]) for a, b in zip(pts, pts[1:])]
    out, tt = [[t0, pts[0][0], pts[0][1]]], t0
    for p, d in zip(pts[1:], seg):
        tt += (t1 - t0) * d / max(1e-9, sum(seg)) if sum(seg) > 1e-9 else (t1 - t0) / len(seg); out.append([tt, p[0], p[1]])
    return out
G_START = G_CORD
STOPS = [(0.0, G_START)]
pos_now = G_START
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
    return list(STOPS[-1][1]) if t > STOPS[-1][0] else list(G_START)
def who_at(t):
    x, y = g_at(t)
    z = 0.0
    if STEP <= t <= OFF:
        z = PL_TOP + RIDE * (smoother((t - RIDE0) / (RIDE1 - RIDE0)) if t < DOWN0 else 1 - smoother((t - DOWN0) / (DOWN1 - DOWN0)))
    return [(p[0], p[1], p[2] + z) for p in gp(x, y)]
WALL_FREE = lambda eye: eye[0] < -1.95
FRAME_BOX = ((-4.8, 0.6, 0.0), (-3.6, 0.8, 2.6))
FLUME_BOX = ((-4.9, 0.8, 0.0), (-4.3, 2.7, 2.0))
free = lambda B: (lambda eye: not all(B[0][i] - 0.2 <= eye[i] <= B[1][i] + 0.2 for i in range(3)))
AIR = both(clear_air, WALL_FREE, free(FRAME_BOX), free(FLUME_BOX))
PATH = both(solid_free, WALL_FREE, free(FRAME_BOX), free(FLUME_BOX))
LOS = make_los(SIGHT_BLOCKERS)
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
UP = lambda x, y: [(x, y, PL_TOP + RIDE + 0.75), (x, y, PL_TOP + RIDE + 1.18)]
SHOTS = [
    (0.0, (gp(*G_CORD)[1:] + [(BX, 0.7, HALF + 0.3), (KX + 0.06, 0.62, 0.05)], (-4.35, 0.45, 0.8), -40, 10, 2.2)),
    (LS["bigger"] + 1.0, (gp(*G0)[1:] + [(-4.7, 0.7, 2.5), (-3.7, 0.7, 2.5), (BX, 0.7, 0.0), (KX, 0.7, ZK0)], (-4.1, 0.6, 1.3), 80, 17, 4.6)),
    (LS["heavy"] - 0.3, (gp(*G0)[1:], (G0[0], G0[1], 0.85), -20, 8, 1.6)),
    (OPEN + 0.3, (gp(*PL_C) + UP(*PL_C) + [(KX, 0.7, ZK0 + 0.4), (KX, 0.7, 0.2)], (-4.15, 0.6, 1.2), -30, 10, 3.0)),
    (LS["mistake"] - 0.3, (UP(*PL_C) + [(PL_C[0], PL_C[1], PL_TOP + RIDE)], (PL_C[0], PL_C[1], PL_TOP + RIDE + 0.85), -30, 4, 1.9)),
    (DRAIN0 + 0.2, (gp(*PL_C) + UP(*PL_C) + [(KX, 0.7, 0.2)], (-4.15, 0.6, 1.2), -30, 10, 3.0)),
    (LS["never"] - 0.3, (gp(PL_C[0] + 0.15, 0.25)[1:], (PL_C[0] + 0.15, 0.25, 0.85), -20, 8, 1.6)),
    (LE["never"] + 0.6, (gp(SC[0], SC[1] + 0.35)[1:] + [(SC[0] - 0.45, SC[1], 0.05), (SC[0] + 0.45, SC[1], 0.05)], (SC[0], SC[1] + 0.15, 0.55), -40, 14, 2.0)),
]
for t, (must, tgt, az, el, d) in SHOTS:
    cam += cut(t, must, tgt, az, el, d, AIR, los=LOS)
cam, PATCHED = fix_path(cam, AIR, who_at, path_clear=PATH)

CHAT += [(LE["measure"] + 0.3, "lurker_77", "*writes down six*")]
cards = [dict(style="live", when=0.0, until="end", viewers=[[0.0, 4]]),
         dict(style="chat", when=0.0, until="end", msgs=[dict(at=round(t, 3), user=u, text=x) for t, u, x in CHAT],
              colors={"GardenGranny": "pink", "lurker_77": "grey", "BoarFan2009": "amber", "TobiasBuilds": "green"}),
         dict(style="inventory", when=0.0, until="end", items=[dict(icon="webcam", name="Webcam", live=True, **{"in": -1.0}),
                                                               dict(icon="map", name="Blueprint", **{"in": -1.0})]),
         dict(style="panel", y="top", border="amber", when=round(LESSON0, 3), until=round(LESSON1 + 0.4, 3), rows=[
             dict(text="BALANCED", color="white", at=round(LESSON0 + 0.1, 3), size=40),
             dict(text="equal weights don't move", color="cyan", at=round(LESSON0 + 1.2, 3), size=30)]),
         dict(style="panel", y="top", border="red", when=round(LS["never"] + 0.6, 3), until=round(LE["never"] + 0.4, 3), rows=[
             dict(text="NEVER RIDE A LOAD LIFT", color="white", at=round(LS["never"] + 0.7, 3), size=40),
             dict(text="lifts for things are not for people", color="amber", at=round(LS["never"] + 2.0, 3), size=30)]),
         dict(style="panel", y="top", border="amber", when=round(MEAS0, 3), until=round(MEAS1 + 0.4, 3), rows=[
             dict(text="MEASURE", color="white", at=round(MEAS0 + 0.1, 3), size=40),
             dict(text="a scale tells you how heavy", color="cyan", at=round(MEAS0 + 1.0, 3), size=30)])]
W = {k: v for k, v in S5["world"].items() if k not in ("clouds_pass", "critters", "rigging")}
W.update(time="morning", door_open=[-2.0, -1.0, 125.0], critters=[], rigging=rig)
story = dict(title="Test 2: Stuck Halfway", slug=SLUG, voice="am_santa", speed=0.95, format="wide", captions="srt",
             channel_tag="GRANDPA'S BLOCK LAB", start=LS["plug"], tail=round(tail, 4), seed=106, blink=True, target_duration=round(FILM),
             engine_rev=4, scene=dict(episode="raccoon_lift", scene=6, name="Test 2: Stuck Halfway", previous="raccoon_lift_scene05",
                                      next="raccoon_lift_scene07"),
             world=W, lines=lines, grandpa=dict(start=list(G_START), outfit=S5["grandpa"]["outfit"]),
             poses=dict(S5["poses"], **POSES), structures=S, actions=sorted(A, key=lambda a: a["when"]), camera=cam, cards=cards,
             qa=dict(frame_points=["hat", "face", "chest"],
                     solid=["frame_posts", "beam", "barrel", "flume", "trestles", "crate", "stump", "scale_base", "wheel", "anvil", "pivot_frame", "head"]))
json.dump(story, open("/home/user/blocklab/stories/%s.json" % SLUG, "w"), indent=1)
print("film %.2f s" % FILM)
for lid, *_ in LINES:
    print("  %-8s %6.2f-%6.2f" % (lid, LS[lid], LE[lid]))
print("plug %.2f build-end %.2f step %.2f ride %.2f-%.2f down %.2f-%.2f off %.2f level %.2f" % (PLUG, B0, STEP, RIDE0, RIDE1, DOWN0, DOWN1, OFF, LEVEL))
print("camera keys", [(k["at"], k["az"], k["el"], k["dist"]) for k in cam], "patched", PATCHED)
