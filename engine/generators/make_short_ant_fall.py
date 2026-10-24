"""Short: "Can an ant survive falling from a plane?" (vertical, ~60 s) -- the sequel to "Why giants can't exist".

    python3 make_short_ant_fall.py            -> stories/ant_fall.json

Grandpa builds a drop tower with a trapdoor, drops a stone block and Antony (a toy block ant) side by side, then builds
his cousin Andy a parachute -- and finds out Andy never needed it: for tiny things the air is already a parachute.
Falls are keyed frame by frame: the stone in free fall, the ants at their terminal velocity (walking pace) after a
fraction of a second of speeding up, Andy slower under the canopy. Kindness rule: the ants are toys.
"""
import json
import math
import os

FPS = 30
G = 9.81
B = 0.1
TOWER_AT = [0.0, -0.1]          # corner cell of the tower (centered: false); the tower is 3 x 3 x 13 blocks
TOP = 1.3                       # top of the tower and of the trapdoor boards
ANT_SCALE = 0.4                 # the toy ants: 4 cm blocks
STONE0 = [0.55, 0.0, TOP]       # roots of the things standing on the trapdoor (Antony in front, nearer the camera)
ANTONY0 = [0.47, -0.1, TOP]
ANDY0 = [0.75, -0.05, TOP]
BUTTON = [-0.1, -0.1, 0.975]    # red button on the tower's left face
GP = [-0.42, -0.05]             # where grandpa stands

ANT = [[0, 0, 1], [1, 0, 1], [2, 0, 1], [3, 0, 1], [4, 0, 1], [4, 0, 2],          # abdomen, thorax, head (+ top)
       [1, -1, 0], [1, 1, 0], [2, -1, 0], [2, 1, 0], [3, -1, 0], [3, 1, 0],         # six legs
       [5, -1, 3], [5, 1, 3]]                                                       # antennae
CANOPY = [[x, y, 7] for x in range(-1, 6) for y in range(-2, 3)] + \
         [[x, y, 6] for x in range(-1, 6) for y in (-2, 2)] + [[x, y, 6] for x in (-1, 5) for y in range(-1, 2)]
LINES = [[x, y, z] for x in (0, 4) for y in (-1, 1) for z in (3, 4, 5)]


DLG = {}                        # the measured line timings (build/dialogue.json), when known: cuts snap to whole frames


def ref(line, edge, off):
    return [line, edge, round(off, 4)]


def cut_at(line, edge, off):
    """A camera cut on a frame boundary: (time of the hold key, time of the new shot). Needs the measured timings."""
    if not DLG:
        return ref(line, edge, off - 1.0 / FPS), ref(line, edge, off)
    f = round((DLG[line][edge] + off) * FPS)
    return round((f - 1) / FPS, 4), round(f / FPS, 4)


def fall_keys(line, edge, t0, p0, vt=None, tau=0.15, sway=0.0, tumble=0.0, yaw=0.0, scale=None, bounce=0.0):
    """Keys for something let go at (line edge + t0) from p0: free fall (vt None) or speeding up to terminal velocity
    vt over ~tau seconds, landing on the floor (root z = 0). Returns (keys, landing time offset)."""
    keys, t, z = [], 0.0, p0[2]
    sc = {} if scale is None else {"scale": scale}
    while True:
        if vt is None:
            z = p0[2] - 0.5 * G * t * t
        else:
            z = p0[2] - vt * (t - tau * (1 - math.exp(-t / tau)))
        if z <= 0:
            break
        x = p0[0] + sway * math.sin(2 * math.pi * 0.8 * t)
        rot = [tumble * math.sin(2 * math.pi * 1.3 * t), tumble * 0.6 * math.sin(2 * math.pi * 0.9 * t + 1), yaw]
        keys.append(dict(t=ref(line, edge, t0 + t), at=[round(x, 4), p0[1], round(z, 4)], rot=[round(r, 2) for r in rot], **sc))
        t += 1.0 / FPS
    tl = t0 + t
    keys.append(dict(t=ref(line, edge, tl), at=[p0[0], p0[1], 0.0], rot=[0, 0, yaw], **sc))
    if bounce:
        keys.append(dict(t=ref(line, edge, tl + 0.12), at=[p0[0], p0[1], bounce], rot=[0, 0, yaw], **sc))
        keys.append(dict(t=ref(line, edge, tl + 0.26), at=[p0[0], p0[1], 0.0], rot=[0, 0, yaw], **sc))
    return keys, tl


def parked(p, scale=None):
    sc = {} if scale is None else {"scale": scale}
    return [dict(t=-1.0, at=list(p), rot=[0, 0, 0], **sc)]


def main():
    dp = os.path.join(os.getcwd(), "build", "dialogue.json")
    if os.path.exists(dp):                                      # 2nd pass: snap the camera cuts to whole frames
        DLG.update({l["id"]: l for l in json.load(open(dp))["lines"]})
        print("cuts snapped to frames from", dp)
    S = {}
    S["tower"] = dict(box=[3, 3, 13], at=TOWER_AT, centered=False, material="stone", stand="left", expect_blocks=117)
    door = [[x, y, 12] for x in range(3, 10) for y in range(0, 3)]
    S["door"] = dict(cells=door, at=TOWER_AT, centered=False, material="planks", block_shape=[1, 1, 0.35], expect_blocks=21)
    S["door2"] = dict(cells=door, at=TOWER_AT, centered=False, material="planks", block_shape=[1, 1, 0.35], expect_blocks=21)
    S["button"] = dict(cells=[[-1, 0, 9]], at=TOWER_AT, centered=False, material="red", block_shape=[0.5, 0.5, 0.5], expect_blocks=1)
    S["stone"] = dict(box=[2, 2, 2], at=STONE0[:2], centered=False, material="sandstone", expect_blocks=8)
    S["antony"] = dict(cells=ANT, at=ANTONY0[:2], centered=False, material="red", eyes=True, expect_blocks=len(ANT))
    S["andy"] = dict(cells=ANT, at=ANDY0[:2], centered=False, material="blue", eyes=True, expect_blocks=len(ANT))
    S["chute"] = dict(cells=CANOPY, at=ANDY0[:2], centered=False, material="red", block_shape=[1, 1, 0.5], expect_blocks=len(CANOPY))
    S["lines"] = dict(cells=LINES, at=ANDY0[:2], centered=False, material="paper", block_shape=[0.15, 0.15, 1], expect_blocks=len(LINES))

    L = [dict(id="hook", text="Chat asked me... if an ant fell out of an airplane... would it survive?", pause=0.4),
         dict(id="tower", text="Let's find out. Ready, chat? Blocks up!", pause=2.4),
         dict(id="antony", text="This is Antony. He's a toy ant. Real bugs, we just watch.", pause=0.4),
         dict(id="count", text="One stone block. One Antony. Three... two... one!", pause=2.0),
         dict(id="landing", text="Same height. Very different landing.", pause=0.5),
         dict(id="chute", text="Safety first! His cousin Andy gets a parachute. Blocks up!", pause=1.9),
         dict(id="go", text="And... go!", pause=2.7),
         dict(id="surprise", text="Soft landing. But wait... Antony landed soft too. No parachute!", pause=0.5),
         dict(id="lesson", text="When you're tiny, you're so light that the air pushes back almost as hard as gravity pulls.", pause=0.4),
         dict(id="word", text="That's called terminal velocity. The fastest you can fall.", pause=0.5),
         dict(id="ladder", text="An ant falls about as fast as you walk. A cat, as fast as a car. A person, even faster. "
                                "So we keep our feet on the ground!", pause=0.5),
         dict(id="plane", text="And from an airplane? The fall won't hurt an ant. But the cold up there? Brrr.", pause=0.4),
         dict(id="payoff", text="Giants? Gravity is the boss. Ants? The air is.", pause=0.0)]

    A = []
    act = lambda **k: A.append(k)
    # ---- talking to chat; the builds
    act(type="face_camera", when=0.0, until=ref("tower", "start", 0.6))
    act(type="build", target="tower", order="z", stand_at=GP, when=ref("tower", "start", 0.9), until=ref("tower", "end", 1.6))
    act(type="build", target="door", order="x", stand_at=GP, when=ref("tower", "end", 1.6), until=ref("tower", "end", 2.2))
    act(type="build", target="button", stand_at=GP, when=ref("tower", "end", 2.2), until=ref("tower", "end", 2.35))
    act(type="build", target="antony", order="x", stand_at=GP, when=ref("antony", "start", 0.0), until=ref("antony", "start", 1.4))
    act(type="face_camera", when=ref("antony", "start", 1.5), until=ref("antony", "end", 0.3))
    act(type="build", target="stone", order="z", stand_at=GP, when=ref("count", "start", 0.0), until=ref("count", "start", 0.9))
    act(type="point", pos=BUTTON, when=ref("count", "end", -0.5), until=ref("count", "end", 0.5))
    act(type="remove", target="door", quiet=True, when=ref("count", "end", 0.12), until=ref("count", "end", 0.2))
    act(type="sfx", sound="switch", when=ref("count", "end", 0.1), gain=0.6)
    act(type="face_camera", when=ref("landing", "start", -0.2), until=ref("landing", "end", 0.3))
    act(type="build", target="door2", order="x", stand_at=GP, when=ref("chute", "start", 0.0), until=ref("chute", "start", 0.6))
    act(type="build", target="andy", order="x", stand_at=GP, when=ref("chute", "start", 0.7), until=ref("chute", "start", 1.8))
    act(type="build", target="lines", order="z", stand_at=GP, when=ref("chute", "end", 0.0), until=ref("chute", "end", 0.6))
    act(type="build", target="chute", order="z", stand_at=GP, when=ref("chute", "end", 0.6), until=ref("chute", "end", 1.6))
    act(type="point", pos=BUTTON, when=ref("go", "end", -0.4), until=ref("go", "end", 0.5))
    act(type="remove", target="door2", quiet=True, when=ref("go", "end", 0.12), until=ref("go", "end", 0.2))
    act(type="sfx", sound="switch", when=ref("go", "end", 0.1), gain=0.6)
    act(type="face_camera", when=ref("surprise", "start", -0.2), until="end")
    act(type="shrug", when=ref("plane", "start", 1.4), until=ref("plane", "start", 2.6))

    # ---- the drops (keyed paths, no hand on them)
    stone_fall, t_stone = fall_keys("count", "end", 0.15, STONE0)
    ant_fall, t_ant = fall_keys("count", "end", 0.15, ANTONY0, vt=1.5, tau=0.15, tumble=25, scale=ANT_SCALE, bounce=0.03)
    andy_fall, t_andy = fall_keys("go", "end", 0.15, ANDY0, vt=0.65, tau=0.1, sway=0.03, tumble=6, scale=ANT_SCALE)
    act(type="hold", target="stone", hand="none", when=-1.0, until=99.0, reach=0.05, keys=parked(STONE0) + stone_fall)
    act(type="hold", target="antony", hand="none", when=-1.0, until=99.0, reach=0.05, keys=parked(ANTONY0, ANT_SCALE) + ant_fall)
    act(type="hold", target="andy", hand="none", when=-1.0, until=99.0, reach=0.05, keys=parked(ANDY0, ANT_SCALE) + andy_fall)
    land = andy_fall[-1]["t"][2]                               # after Andy lands, the canopy drifts down beside him
    drape = [dict(t=ref("go", "end", land + 0.15), at=[ANDY0[0], ANDY0[1], 0.0], rot=[0, 0, 0], scale=ANT_SCALE),
             dict(t=ref("go", "end", land + 0.9), at=[ANDY0[0] + 0.14, ANDY0[1], -0.012], rot=[0, 75, 0], scale=ANT_SCALE)]
    act(type="hold", target="chute", hand="none", when=-1.0, until=99.0, reach=0.05, keys=parked(ANDY0, ANT_SCALE) + andy_fall + drape)
    gone = [dict(t=ref("go", "end", land + 0.25), at=[0.0, 0.0, -5.0], rot=[0, 0, 0], scale=ANT_SCALE)]
    act(type="hold", target="lines", hand="none", when=-1.0, until=99.0, reach=0.05, keys=parked(ANDY0, ANT_SCALE) + andy_fall + gone)
    act(type="sfx", sound="clatter", when=ref("count", "end", t_stone), gain=1.0)
    act(type="sfx", sound="tap", when=ref("count", "end", t_ant), gain=0.5)
    act(type="sfx", sound="tap", when=ref("go", "end", t_andy), gain=0.4)
    act(type="sfx", sound="rustle", when=ref("go", "end", 0.3), gain=0.35)

    # ---- camera (vertical frame: tall subjects fit; cuts are a hold key 1/30 s before)
    def cam(at, tgt, az, el, dist):
        return dict(at=at, target=tgt, az=az, el=el, dist=dist)
    MED = ([-0.4, -0.05, 1.12], -90, 6, 1.75)                   # grandpa to the lens
    WIDE = ([0.08, -0.02, 0.8], -86, 8, 3.1)                    # grandpa + tower + drop zone
    TOPC = ([0.6, 0.02, 1.36], -97, 16, 1.05)                   # the trapdoor close-up
    FLOOR = ([0.66, 0.0, 0.12], -96, 14, 1.05)                  # where things land
    DROP = ([0.42, 0.0, 0.72], -90, 5, 2.4)                     # the whole fall
    def cutto(line, edge, off, prev, shot):              # hold the previous framing, then the new shot one frame later
        a, b = cut_at(line, edge, off)
        return [cam(a, *prev), cam(b, *shot)]
    TOPC2 = (TOPC[0], -100, 17, 1.0)
    FLOOR2 = (FLOOR[0], -100, 15, 1.0)
    WIDE2 = (WIDE[0], -84, 9, 3.2)
    ANDYL = ([0.66, 0.02, 0.12], -96, 13, 1.1)
    C = [cam(0.0, *MED), cam(ref("hook", "end", 0.0), *MED[:-1], 1.65),
         cam(ref("tower", "start", 0.6), *WIDE), cam(ref("tower", "end", 2.3), *WIDE2)]
    C += cutto("antony", "start", 0.0, WIDE2, TOPC) + [cam(ref("antony", "end", 0.2), *TOPC2)]
    C += cutto("count", "start", 0.0, TOPC2, WIDE) + [cam(ref("count", "end", 0.0), *DROP), cam(ref("count", "end", 1.3), *DROP)]
    C += cutto("count", "end", 1.3 + 1 / FPS, DROP, FLOOR) + [cam(ref("landing", "end", 0.3), *FLOOR2)]
    C += cutto("chute", "start", 0.0, FLOOR2, TOPC) + [
         cam(ref("chute", "end", 1.7), [0.72, 0.0, 1.45], -100, 15, 1.1),
         cam(ref("go", "end", 0.1), [0.72, 0.0, 1.45], -100, 14, 1.15),
         cam(ref("go", "end", t_andy), [0.74, 0.0, 0.2], -98, 12, 1.15),
         cam(ref("surprise", "start", 1.2), *ANDYL)]
    C += cutto("surprise", "start", 1.2 + 1 / FPS, ANDYL, MED) + [
         cam(ref("lesson", "end", 0.0), MED[0], -90, 6, 1.6), cam(ref("ladder", "start", 0.0), MED[0], -88, 6, 1.7),
         cam(ref("plane", "start", 0.0), *WIDE)]
    C += cutto("payoff", "start", 0.0, WIDE, (MED[0], -90, 6, 1.6)) + [cam("end", MED[0], -90, 6, 1.5)]

    # ---- cards (vertical layout, like the giants Short)
    K = [dict(style="title", text="IF AN ANT FELL", color="white", y=430, size=96, when=0.3, until=ref("hook", "end", 0.2)),
         dict(style="title", text="FROM A PLANE...", color="amber", y=550, size=96, when=1.4, until=ref("hook", "end", 0.2)),
         dict(style="title", text="WOULD IT SURVIVE?", color="cyan", y=430, size=84, when=ref("hook", "end", 0.2), until=ref("tower", "start", 0.9)),
         dict(style="bubble", text="{count:tower} BLOCKS", anchor="tower:top", color="amber", when=ref("tower", "start", 1.0), until=ref("tower", "end", 2.3)),
         dict(style="tag", text="ANTONY (TOY)", anchor="antony:top", dy=-60, color="red", when=ref("antony", "start", 1.4), until=ref("antony", "end", 0.3)),
         dict(style="impact", text="THUD!", color="red", y=700, when=ref("count", "end", t_stone), until=ref("count", "end", t_stone + 0.9)),
         dict(style="bubble", text="boop.", anchor="antony:top", color="green", when=ref("count", "end", t_ant + 0.1), until=ref("count", "end", t_ant + 1.2)),
         dict(style="title", text="SAME HEIGHT", color="white", y=430, size=92, when=ref("landing", "start", -0.1), until=ref("landing", "end", 0.4)),
         dict(style="title", text="DIFFERENT LANDING", color="amber", y=550, size=86, when=ref("landing", "start", 1.0), until=ref("landing", "end", 0.4)),
         dict(style="tag", text="ANDY", anchor="andy:top", dy=-60, color="cyan", when=ref("chute", "start", 1.8), until=ref("chute", "end", 0.6)),
         dict(style="bubble", text="boop.", anchor="andy:top", color="green", when=ref("go", "end", t_andy + 0.1), until=ref("go", "end", t_andy + 1.2)),
         dict(style="panel", y=300, border="cyan", when=ref("surprise", "start", 0.3), until=ref("surprise", "end", 0.4),
              rows=[dict(text="ANDY + PARACHUTE: SOFT", color="cyan", at=ref("surprise", "start", 0.3), size=52),
                    dict(text="ANTONY, NO PARACHUTE:", color="white", at=ref("surprise", "start", 1.6), size=52),
                    dict(text="SOFT TOO!", color="green", at=ref("surprise", "start", 2.4), size=64)]),
         dict(style="panel", y=300, border="amber", when=ref("lesson", "start", 0.2), until=ref("lesson", "end", 0.3),
              rows=[dict(text="TINY = LIGHT", color="amber", at=ref("lesson", "start", 0.2), size=60),
                    dict(text="AIR PUSHES UP", color="cyan", at=ref("lesson", "start", 2.0), size=52),
                    dict(text="≈ GRAVITY PULLS DOWN", color="white", at=ref("lesson", "start", 2.8), size=52)]),
         dict(style="word", word="terminal velocity", say="ter·mi·nal ve·loc·i·ty",
              meaning="The fastest something can fall: when the air pushes back as hard as gravity pulls.",
              when=ref("word", "start", 0.0), until=ref("word", "end", 0.6)),
         dict(style="panel", y=300, border="amber", when=ref("ladder", "start", 0.0), until=ref("ladder", "end", 0.3),
              rows=[dict(text="FASTEST FALL", color="amber", at=ref("ladder", "start", 0.0), size=56),
                    dict(text="ANT  ≈ 6 km/h", color="green", at=ref("ladder", "start", 0.3), size=52),
                    dict(text="CAT  ≈ 100 km/h", color="white", at=ref("ladder", "start", 2.4), size=52),
                    dict(text="PERSON  ≈ 200 km/h", color="red", at=ref("ladder", "start", 4.0), size=52)]),
         dict(style="panel", y=300, border="cyan", when=ref("plane", "start", 0.2), until=ref("plane", "end", 0.3),
              rows=[dict(text="FROM A PLANE?", color="white", at=ref("plane", "start", 0.2), size=56),
                    dict(text="THE FALL: FINE", color="green", at=ref("plane", "start", 1.6), size=52),
                    dict(text="THE COLD: BRRR", color="cyan", at=ref("plane", "start", 3.2), size=52)]),
         dict(style="panel", y=300, border="amber", when=ref("payoff", "start", 0.0), until=ref("payoff", "end", 0.2),
              rows=[dict(text="GIANTS: GRAVITY WINS", color="red", at=ref("payoff", "start", 0.0), size=52),
                    dict(text="ANTS: THE AIR WINS", color="green", at=ref("payoff", "start", 1.6), size=52)]),
         dict(style="end", title1="WHY ANTS", title2="SURVIVE BIG FALLS", sub="J.B.S. Haldane, \"On Being the Right Size\" (1926)",
              cta="Watch next: Why Giants Can't Exist", when=ref("payoff", "end", 0.2))]

    story = dict(title="Can an ant survive falling from a plane?", slug="ant_fall", voice="am_santa", speed=0.95,
                 start=0.3, tail=2.2, channel_tag="GRANDPA'S BLOCK LAB", engine_rev=2, lines=L,
                 grandpa=dict(start=GP), structures=S, actions=sorted(A, key=lambda a: json.dumps(a["when"])), camera=C, cards=K)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "stories", "ant_fall.json")
    json.dump(story, open(out, "w"), indent=1)
    print("wrote", os.path.normpath(out), "| %d lines, %d actions, %d camera keys, %d cards" % (len(L), len(A), len(C), len(K)))


if __name__ == "__main__":
    main()
