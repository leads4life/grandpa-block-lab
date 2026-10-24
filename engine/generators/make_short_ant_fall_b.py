"""Short, version B (A/B test): "Can an ant survive falling from a plane?" -- cut to the Shorts rules (2026-10-24):
action at second 0 (the drop is already happening), no setup, something new every 2-3 s, a block-built cutaway for
every speed comparison, a debate prompt, and a seamless loop (the last line runs into the first frame).

    cd <work dir> && python3 make_short_ant_fall_b.py      -> stories/ant_fall_b.json (2nd run: cuts snap to frames)
"""
import json
import math
import os

FPS = 30
G = 9.81
TOWER_AT = [0.0, -0.1]
TOP = 1.3
ANT_SCALE = 0.4
STONE0 = [0.55, 0.0, TOP]
ANTONY0 = [0.47, -0.1, TOP]
BUTTON = [-0.1, -0.1, 0.975]
GP = [-0.42, -0.05]
DROP_T = 0.15                   # the trapdoor opens this many seconds into the video
ANT = [[0, 0, 1], [1, 0, 1], [2, 0, 1], [3, 0, 1], [4, 0, 1], [4, 0, 2],
       [1, -1, 0], [1, 1, 0], [2, -1, 0], [2, 1, 0], [3, -1, 0], [3, 1, 0], [5, -1, 3], [5, 1, 3]]
DLG = {}


def T(line, edge="start", off=0.0):
    """A line-relative time; with the measured timings known, an absolute time on a whole frame."""
    if not DLG:
        return [line, edge, round(off, 4)]
    return round(round((DLG[line][edge] + off) * FPS) / FPS, 4)


def fall(t0, p0, vt=None, tau=0.15, tumble=0.0, scale=None):
    """Keys (absolute times) for something let go at t0 from p0, down to the floor. Returns (keys, landing time)."""
    keys, t = [], 0.0
    sc = {} if scale is None else {"scale": scale}
    while True:
        z = p0[2] - (0.5 * G * t * t if vt is None else vt * (t - tau * (1 - math.exp(-t / tau))))
        if z <= 0:
            break
        rot = [tumble * math.sin(2 * math.pi * 1.3 * t), tumble * 0.6 * math.sin(2 * math.pi * 0.9 * t + 1), 0]
        keys.append(dict(t=round(t0 + t, 4), at=[p0[0], p0[1], round(z, 4)], rot=[round(r, 2) for r in rot], **sc))
        t += 1.0 / FPS
    keys.append(dict(t=round(t0 + t, 4), at=[p0[0], p0[1], 0.0], rot=[0, 0, 0], **sc))
    return keys, t0 + t


def k(t, at, rot=(0, 0, 0), scale=None):
    d = dict(t=t, at=[round(v, 4) for v in at], rot=list(rot))
    if scale is not None:
        d["scale"] = scale
    return d


def main():
    dp = os.path.join(os.getcwd(), "build", "dialogue.json")
    if os.path.exists(dp):
        DLG.update({l["id"]: l for l in json.load(open(dp))["lines"]})
        print("cuts snapped to frames from", dp)
    S = {}
    S["tower"] = dict(box=[3, 3, 13], at=TOWER_AT, centered=False, material="stone", expect_blocks=117)
    door = [[x, y, 12] for x in range(3, 10) for y in range(0, 3)]
    S["door"] = dict(cells=door, at=TOWER_AT, centered=False, material="planks", block_shape=[1, 1, 0.35], expect_blocks=21)
    S["door2"] = dict(cells=door, at=TOWER_AT, centered=False, material="planks", block_shape=[1, 1, 0.35], expect_blocks=21)
    S["button"] = dict(cells=[[-1, 0, 9]], at=TOWER_AT, centered=False, material="red", block_shape=[0.5, 0.5, 0.5], expect_blocks=1)
    S["stone"] = dict(box=[2, 2, 2], at=STONE0[:2], centered=False, material="sandstone", expect_blocks=8)
    S["antony"] = dict(cells=ANT, at=ANTONY0[:2], centered=False, material="red", eyes=True, expect_blocks=len(ANT))
    # cutaway props, all block-built, on the island (radius ~2.7 m) but where the main shots never look: the sneaker at the
    # south-west edge, the car parked at the south edge (it drives across the front), the skydiver and plane high up
    SHOE_AT, CAR_AT, DIVER_AT, PLANE_AT = [0.9, -2.05], [-1.4, -1.0], [2.0, 1.0], [-7.0, 0.0]   # clear of the trees
    S["shoe_sole"] = dict(cells=[[x, y, 0] for x in range(0, 4) for y in range(0, 2)], at=SHOE_AT, centered=False,
                          material="rubber", block_shape=[1, 1, 0.5], expect_blocks=8)
    S["shoe_top"] = dict(cells=[[x, y, 1] for x in range(0, 3) for y in range(0, 2)] + [[x, y, 2] for x in range(0, 2) for y in range(0, 2)],
                         at=SHOE_AT, centered=False, material="blue", expect_blocks=10)
    S["car_body"] = dict(cells=[[x, y, z] for x in range(0, 6) for y in range(0, 3) for z in (1, 2)], at=CAR_AT, centered=False,
                         material="red", expect_blocks=36)
    S["car_glass"] = dict(cells=[[x, y, 3] for x in range(1, 4) for y in range(0, 3)], at=CAR_AT, centered=False,
                          material="glass", expect_blocks=9)
    S["car_wheels"] = dict(cells=[[x, y, 0] for x in (1, 4) for y in (0, 2)], at=CAR_AT, centered=False,
                           material="rubber", expect_blocks=4)
    suit = [[x, 0, 0] for x in range(0, 4)] + [[2, y, 0] for y in (-2, -1, 1, 2)] + [[x, y, 0] for x in (-2, -1) for y in (-1, 1)]
    S["diver_suit"] = dict(cells=suit, at=DIVER_AT, centered=False, material="red", expect_blocks=len(suit))
    S["diver_head"] = dict(cells=[[4, 0, 0]], at=DIVER_AT, centered=False, material="sandstone", expect_blocks=1)
    plane = [[x, 0, 0] for x in range(0, 10)] + [[x, y, 0] for x in (4, 5) for y in range(-5, 6) if y != 0] + \
            [[0, 0, 1], [0, 0, 2]] + [[x, y, 0] for x in (0, 1) for y in (-2, -1, 1, 2)]
    S["plane"] = dict(cells=plane, at=PLANE_AT, centered=False, material="paper", expect_blocks=len(plane))

    L = [dict(id="wait", text="Wait, what? The stone goes thud... and the ant just walks away?", pause=0.3),
         dict(id="secret", text="Here's the secret. When you're tiny, you're so light, the air pushes back almost as hard as gravity pulls.", pause=0.3),
         dict(id="walk", text="So an ant can't fall faster than you walk. That's terminal velocity.", pause=0.3),
         dict(id="cat", text="A cat? About as fast as a car.", pause=0.3),
         dict(id="person", text="A person? Twice that. So we keep our feet on the ground!", pause=0.3),
         dict(id="plane", text="From an airplane? The fall won't hurt an ant. The cold might... brrr.", pause=0.3),
         dict(id="loop", text="And that's exactly why, when you drop an ant...", pause=0.0)]

    A = []
    act = lambda **kw: A.append(kw)
    # ---- the drop, already happening at second 0
    act(type="point", pos=BUTTON, when=-0.6, until=0.45)
    act(type="remove", target="door", quiet=True, when=round(DROP_T - 0.03, 3), until=round(DROP_T + 0.05, 3))
    act(type="sfx", sound="switch", when=0.05, gain=0.6)
    stone_fall, t_stone = fall(DROP_T + 0.05, STONE0)
    ant_fall, t_ant = fall(DROP_T + 0.05, ANTONY0, vt=1.5, tau=0.15, tumble=25, scale=ANT_SCALE)
    act(type="sfx", sound="clatter", when=round(t_stone, 3), gain=1.0)
    act(type="sfx", sound="tap", when=round(t_ant, 3), gain=0.5)
    # Antony walks away: little hops toward the camera, then he looks at us
    walk = [k(round(t_ant + 0.12, 4), [ANTONY0[0], ANTONY0[1], 0.03], scale=ANT_SCALE),
            k(round(t_ant + 0.26, 4), [ANTONY0[0], ANTONY0[1], 0.0], scale=ANT_SCALE)]
    x, y, t = ANTONY0[0], ANTONY0[1], t_ant + 0.9
    for i in range(6):
        x, y = x + 0.035, y - 0.03
        walk.append(k(round(t + 0.12, 4), [x - 0.017, y + 0.015, 0.012], (0, 0, -20), ANT_SCALE))
        walk.append(k(round(t + 0.24, 4), [x, y, 0.0], (0, 0, -20), ANT_SCALE))
        act(type="sfx", sound="tap", when=round(t + 0.24, 3), gain=0.12)
        t += 0.26
    END = T("loop", "end", 0.35)                                  # the video's last frame (story tail 0.4 s)
    RESET = T("loop", "end", 0.05)                                # hidden by the cut: everything back on the trapdoor
    reset = lambda p, sc=None: [k(RESET, p, scale=sc)] if DLG else []
    act(type="hold", target="stone", hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[k(-1.0, STONE0)] + stone_fall + ([k(round(RESET - 0.034, 4), [STONE0[0], STONE0[1], 0.0])] if DLG else []) + reset(STONE0))
    act(type="hold", target="antony", hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[k(-1.0, ANTONY0, scale=ANT_SCALE)] + ant_fall + walk +
             ([k(round(RESET - 0.034, 4), [x, y, 0.0], (0, 0, -20), ANT_SCALE)] if DLG else []) + reset(ANTONY0, ANT_SCALE))
    act(type="build", target="door2", quiet=True, order="x", when=T("loop", "end", -0.25), until=T("loop", "end", -0.15))
    act(type="point", pos=BUTTON, when=T("loop", "end", -0.25), until=99.0)
    act(type="face_camera", when=T("wait", "start", -0.3), until=T("loop", "end", -0.3))
    act(type="shrug", when=T("plane", "end", -1.2), until=T("plane", "end", 0.1))

    # ---- cutaway motions
    sole0 = [SHOE_AT[0], SHOE_AT[1], 0.0]
    st = []
    for i in range(5):                                            # four steps across the frame, heel-toe
        t0 = T("walk", "start", 0.1 + 0.5 * i) if DLG else None
        if t0 is None:
            break
        xx = SHOE_AT[0] + 0.15 * i
        st += [k(t0, [xx, SHOE_AT[1], 0.0], (0, 0, 0)), k(round(t0 + 0.2, 4), [xx + 0.075, SHOE_AT[1], 0.08], (0, -12, 0)),
               k(round(t0 + 0.42, 4), [xx + 0.15, SHOE_AT[1], 0.0], (0, 0, 0))]
    for n in ("shoe_sole", "shoe_top"):
        act(type="hold", target=n, hand="none", when=-1.0, until=99.0, reach=0.05, keys=[k(-1.0, sole0)] + st)
    if DLG:
        act(type="sfx", sound="tap", when=T("walk", "start", 0.52), gain=0.3)
        act(type="sfx", sound="tap", when=T("walk", "start", 1.02), gain=0.3)
    car0, north = [CAR_AT[0], CAR_AT[1], 0.0], (0, 0, 90)          # it drives north along the west side, filmed side-on
    car = [k(-1.0, car0, north)] + ([k(T("cat", "start", 0.3), car0, north),
                                     k(T("cat", "start", 1.1), [CAR_AT[0], CAR_AT[1] + 1.5, 0.0], north),
                                     k(T("cat", "end", 0.4), [CAR_AT[0], CAR_AT[1] + 1.5, -5.0], north)] if DLG else [])
    for n in ("car_body", "car_glass", "car_wheels"):
        act(type="hold", target=n, hand="none", when=-1.0, until=99.0, reach=0.05, keys=car)
    act(type="sfx", sound="zip", when=T("cat", "start", 0.6), gain=0.7)
    dv0 = [DIVER_AT[0], DIVER_AT[1], 10.5]
    spread = (90, 0, 0)                                           # stood up to face the camera: arms and legs spread
    dive = [k(-1.0, dv0, spread)]
    if DLG:                                                       # a steady streak down through the frame (frame by frame)
        t0 = T("person", "start", 0.0)
        for i in range(int(1.4 * FPS) + 1):
            dive.append(k(round(t0 + i / FPS, 4), [DIVER_AT[0], DIVER_AT[1], 10.5 - 5.6 * i / FPS], spread))
        dive.append(k(round(t0 + 1.5, 4), [DIVER_AT[0], DIVER_AT[1], -5.0], spread))
    for n in ("diver_suit", "diver_head"):
        act(type="hold", target=n, hand="none", when=-1.0, until=99.0, reach=0.05, keys=dive)
    act(type="sfx", sound="zip", when=T("person", "start", 0.2), gain=0.6)
    pl0 = [PLANE_AT[0], PLANE_AT[1], 9.0]
    act(type="hold", target="plane", hand="none", when=-1.0, until=99.0, reach=0.05,
        keys=[k(-1.0, pl0, scale=2.5)] + ([k(T("plane", "start", 0.0), pl0, scale=2.5),
                                            k(T("plane", "start", 2.6), [PLANE_AT[0] + 9.0, PLANE_AT[1], 9.0], scale=2.5)] if DLG else []))
    act(type="sfx", sound="drone", when=T("plane", "start", 0.0), gain=0.35)

    # ---- camera: a new picture every 2-3 s; every cut is a hold key one frame before
    def cam(at, shot):
        tgt, az, el, dist = shot
        return dict(at=at, target=tgt, az=az, el=el, dist=dist)

    def cut(t, prev, shot):
        if isinstance(t, list):
            return [cam([t[0], t[1], round(t[2] - 1.0 / FPS, 4)], prev), cam(t, shot)]
        return [cam(round(t - 1.0 / FPS, 4), prev), cam(t, shot)]
    DROP = ([0.3, 0.0, 0.72], -88, 5, 2.6)
    FLOOR = ([0.62, -0.08, 0.1], -98, 14, 0.95)
    FLOOR2 = ([0.68, -0.18, 0.08], -102, 13, 0.8)
    MED = ([-0.4, -0.05, 1.12], -90, 6, 1.6)
    MED2 = ([-0.4, -0.05, 1.18], -86, 5, 1.35)
    ANTC = ([0.62, -0.25, 0.08], -95, 10, 0.7)
    SHOE = ([1.2, -1.95, 0.34], -94, 9, 1.05)
    CAR = ([-1.55, -0.3, 0.25], 180, 5, 2.4)
    DIVER = ([2.15, 1.0, 7.0], -90, 0, 2.6)
    PLANE = ([-2.0, 0.0, 9.0], -90, -28, 9.0)
    t_floor = round(round((t_stone + 0.12) * FPS) / FPS, 4)
    C = [cam(0.0, DROP), cam(round(t_floor - 1.0 / FPS, 4), DROP), cam(t_floor, FLOOR), cam(T("wait", "end", 0.0), FLOOR2)]
    C += cut(T("wait", "end", 0.15), FLOOR2, MED) + [cam(T("secret", "start", 2.2), MED)]
    C += cut(T("secret", "start", 2.3), MED, ANTC) + [cam(T("secret", "start", 4.6), ANTC)]
    C += cut(T("secret", "start", 4.7), ANTC, MED2) + [cam(T("walk", "start", -0.05), MED2)]
    C += cut(T("walk", "start", 0.0), MED2, SHOE) + [cam(T("walk", "end", 0.2), SHOE)]
    C += cut(T("cat", "start", 0.0), SHOE, CAR) + [cam(T("cat", "end", 0.2), CAR)]
    C += cut(T("person", "start", 0.0), CAR, DIVER) + [cam(T("person", "start", 1.3), DIVER)]
    C += cut(T("person", "start", 1.4), DIVER, MED) + [cam(T("plane", "start", -0.05), MED)]
    C += cut(T("plane", "start", 0.0), MED, PLANE) + [cam(T("plane", "start", 2.7), PLANE)]
    C += cut(T("plane", "start", 2.8), PLANE, MED2) + [cam(T("loop", "end", 0.0), MED2)]
    C += cut(T("loop", "end", 0.1), MED2, DROP) + [cam("end", DROP)]

    # ---- cards
    K = [dict(style="impact", text="THUD!", color="red", y=700, when=round(t_stone, 3), until=round(t_stone + 0.9, 3)),
         dict(style="bubble", text="boop.", anchor="antony:top", color="green", when=round(t_ant + 0.1, 3), until=round(t_ant + 1.0, 3)),
         dict(style="title", text="WAIT... WHAT?", color="amber", y=430, size=100, when=T("wait", "start", 0.0), until=T("wait", "end", 0.2)),
         dict(style="panel", y=300, border="amber", when=T("secret", "start", 0.3), until=T("secret", "end", 0.2),
              rows=[dict(text="TINY = LIGHT", color="amber", at=T("secret", "start", 0.3), size=60),
                    dict(text="AIR PUSHES UP", color="cyan", at=T("secret", "start", 3.0), size=54),
                    dict(text="≈ GRAVITY PULLS DOWN", color="white", at=T("secret", "start", 3.8), size=54)]),
         dict(style="word", word="terminal velocity", say="ter·mi·nal ve·loc·i·ty",
              meaning="The fastest something can fall: when the air pushes back as hard as gravity pulls.",
              when=T("walk", "start", 1.4), until=T("walk", "end", 0.3)),
         dict(style="title", text="ANT ≈ 6 km/h", color="green", y=780, size=96, when=T("walk", "start", 0.1), until=T("walk", "end", 0.3)),
         dict(style="title", text="(WALKING SPEED)", color="white", y=890, size=60, when=T("walk", "start", 0.4), until=T("walk", "end", 0.3)),
         dict(style="title", text="CAT ≈ 100 km/h", color="amber", y=430, size=96, when=T("cat", "start", 0.1), until=T("cat", "end", 0.3)),
         dict(style="title", text="(CAR SPEED)", color="white", y=550, size=60, when=T("cat", "start", 0.5), until=T("cat", "end", 0.3)),
         dict(style="title", text="PERSON ≈ 200 km/h", color="red", y=430, size=90, when=T("person", "start", 0.1), until=T("person", "start", 1.4)),
         dict(style="panel", y=300, border="cyan", when=T("plane", "start", 0.2), until=T("plane", "end", 0.2),
              rows=[dict(text="FROM A PLANE?", color="white", at=T("plane", "start", 0.2), size=56),
                    dict(text="THE FALL: FINE", color="green", at=T("plane", "start", 1.6), size=54),
                    dict(text="THE COLD: BRRR", color="cyan", at=T("plane", "start", 3.0), size=54)]),
         dict(style="panel", y=300, border="amber", when=T("loop", "start", 0.0), until=T("loop", "end", 0.1),
              rows=[dict(text="AN ELEPHANT WITH AN", color="white", at=T("loop", "start", 0.0), size=50),
                    dict(text="ANT-SIZED PARACHUTE...", color="amber", at=T("loop", "start", 0.0), size=50),
                    dict(text="WHAT HAPPENS? COMMENT!", color="cyan", at=T("loop", "start", 0.6), size=50)])]

    story = dict(title="Can an ant survive falling from a plane? (B)", slug="ant_fall_b", voice="am_santa", speed=0.95,
                 start=1.9, tail=0.4, channel_tag="GRANDPA'S BLOCK LAB", engine_rev=2, lines=L,
                 world=dict(ground="grass", time="morning", weather="clouds"),
                 grandpa=dict(start=GP), structures=S, actions=A, camera=C, cards=K)
    out = os.path.join(os.getcwd(), "stories", "ant_fall_b.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(story, open(out, "w"), indent=1)
    print("wrote", out, "| %d lines, %d actions, %d camera keys, %d cards" % (len(L), len(A), len(C), len(K)))


if __name__ == "__main__":
    main()
