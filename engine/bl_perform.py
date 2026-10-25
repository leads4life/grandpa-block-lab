"""Block Lab: grandpa's performance layer -- body poses, facial expressions, blinks and props held in a hand, all blended
over time on top of the walk / build / point animation in bl_scene. Pure Python (no bpy), so bl_verify can use it too.

Story actions:
  {"type": "pose", "pose": "lean_in", "when": t0, "until": t1, "ease": 0.3}     a body pose
        ("ease_in" / "ease_out" override "ease"; start before 0 to be in the pose from the first frame) (POSES, or story "poses")
  {"type": "face", "expr": "squint", "when": t0, "until": t1, "ease": 0.2}      a facial expression (EXPR)
  {"type": "look", "pos": [x, y, z] | "camera", "when": t0, "until": t1, "body": false, "rate": 0.15}
        ("camera": into the lens of whichever camera is live -- use it whenever he talks to chat)
        look at a point (or "obj": a structure, "off": [x, y, z] in its frame -- follows it); body: false turns only
        the head (seated), rate = how fast the body turns (0..1 per frame).  A "move" with "face": "path" turns his body
        the way he walks while the head keeps looking where the "look" says.
  {"type": "hold", "target": "mug", "hand": "R", "when": t0, "until": t1, "reach": 0.35, "grip": [x, y, z],
   "keys": [{"t": t, "at": [x, y, z] | "mouth" | {"char": [x, y, z]}, "off": [x, y, z], "rot": [rx, ry, rz]}, ...]}
        ({"char": ...} = a point in his own space, e.g. carried in front of him while he walks; it turns with him)
        a key's optional "scale" (1 = full size) folds a map or page smaller as he puts it away; after the last key the
        object stays there -- a last key at his back pocket ({"char": [-0.10, 0.13, 0.50]}) rides along with him.
        "pocket": true on the hold records it as pocketed in the continuity file (see propkit.show_and_pocket)
        the hand reaches the grip (offset in the object's own frame) during [t0 - reach, t0], the object then follows
        the keyed path (root position, or grandpa's mouth + off) and stays at the last key; the hand lets go after t1
  {"type": "sfx", "sound": "clink", "when": t, "gain": 1.0}                    a one-off sound (see bl_audio.SFX)
A pose is a dict of channels: lean, twist (rad), hips [dx, dy, dz] (m, character space: +y = behind him),
head [yaw, up, roll] (rad), shake / nod (rad, a quick head shake or nod), shrug (0..1), elbows (0..1: lift the
elbows out and up, e.g. arms on a table), hand_R / hand_L:
{"char": [x, y, z]} (character space, origin between his feet), {"world": [x, y, z]} or {"obj": name, "off": [x, y, z]},
optional "tap": [Hz, m] (up and down) or "wave": [Hz, m] (side to side).
"""
import math
import random

BODY0 = dict(lean=0.0, twist=0.0, hips=(0.0, 0.0, 0.0), head=(0.0, 0.0, 0.0), shake=0.0, nod=0.0, shrug=0.0, elbows=0.0)
POSES = {
    "seated": dict(hips=(0.0, 0.22, -0.10), elbows=0.6),     # hips back over the chair seat, feet stay put
    "lean_in": dict(lean=0.30, hips=(0.0, -0.02, 0.0)),
    "lean_back": dict(lean=-0.14, head=(0.0, 0.06, 0.0)),
    "head_shake": dict(shake=0.24),
    "nod": dict(nod=0.14),
    "shrug": dict(shrug=1.0),
    "rise": dict(lean=0.52),                                  # weight forward to get up out of a chair
    "hand_on_back": dict(lean=-0.12, head=(0.0, 0.10, 0.0), hand_L=dict(char=(0.10, 0.13, 0.56))),
    "cap_adjust": dict(head=(0.0, -0.06, 0.0), hand_R=dict(char=(-0.05, -0.17, 1.10))),
    "present": dict(twist=-0.10, hand_R=dict(char=(-0.42, -0.22, 0.80))),
    "sip": dict(head=(0.0, 0.14, 0.0)),
    "wave_L": dict(hand_L=dict(char=(0.30, -0.12, 1.12), wave=(1.8, 0.07))),
    "wave_R": dict(hand_R=dict(char=(-0.30, -0.12, 1.12), wave=(1.8, 0.07))),
}
FACE0 = dict(brow=0.0, brow_R=0.0, brow_L=0.0, tilt=0.0, lid=0.0, gx=0.0, gz=0.0, smile=0.0)
EXPR = {        # brow: up/down, tilt: + inner ends up (worried) / - furrowed, lid: 0 open .. 1 shut, gx/gz: gaze, smile: -1..1
    "neutral": {},
    "squint": dict(lid=0.55, brow=-0.6, tilt=-0.45),
    "raised": dict(brow=1.0),
    "surprised": dict(brow=1.0, smile=-0.35, gz=0.2),
    "confused": dict(brow_R=0.9, brow_L=-0.5, tilt=0.15),
    "side_eye": dict(gx=-0.9, lid=0.38, brow=-0.25, brow_L=0.35, smile=0.2),
    "smirk": dict(smile=0.45, lid=0.25, brow_L=0.4),
    "smile": dict(smile=0.8, lid=0.22, brow=0.2),
    "warm": dict(smile=1.0, lid=0.3, brow=0.35, tilt=0.25),
    "content": dict(smile=0.55, lid=0.65, brow=0.25),
    "worried": dict(brow=0.3, tilt=0.8, smile=-0.4, lid=0.1),
    "relief": dict(brow=0.45, tilt=0.55, lid=0.45, smile=0.5),
    "wince": dict(lid=0.78, brow=-0.45, tilt=0.65, smile=-0.6),
    "alert": dict(brow=0.85, gz=0.1, smile=-0.15),
}


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def smoother(x):
    x = min(1.0, max(0.0, x))
    return x ** 3 * (x * (6 * x - 15) + 10)


def envelope(a, t):
    """0..1 weight of a timed action: eases in over 'ease' s from t0, out over 'ease' s before t1."""
    e = a.get("ease", 0.3)
    ei, eo = max(1e-3, a.get("ease_in", e)), max(1e-3, a.get("ease_out", e))
    return smooth((t - a["t0"]) / ei) * (1 - smooth((t - (a["t1"] - eo)) / eo))


def _mix(cur, target, w):
    return tuple(c + (x - c) * w for c, x in zip(cur, target)) if isinstance(cur, tuple) else cur + (target - cur) * w


def body_at(P, t):
    """Body channels at time t: the timed poses blended in story order (later poses win where they overlap).
    Returns (channels, hands) with hands = {"R": [(spec, weight), ...], "L": [...]}."""
    lib = dict(POSES, **P.get("poses", {}))
    ch, hands = dict(BODY0), {"R": [], "L": []}
    for a in P["actions"]:
        if a["type"] != "pose":
            continue
        w = envelope(a, t)
        if w <= 0:
            continue
        p = lib[a["pose"]]
        for k, v in p.items():
            if k in ("hand_R", "hand_L"):
                hands[k[-1]].append((v, w))
            elif k in ("shake", "nod", "shrug", "elbows"):
                ch[k] = max(ch[k], v * w)
            else:
                cur = ch[k]
                ch[k] = tuple(c + x * w for c, x in zip(cur, v)) if isinstance(cur, tuple) else cur + v * w
    return ch, hands


def blinks(P):
    """Blink times: every 2.2-4.8 s (seeded), plus the story's explicit "blink" face actions."""
    if not P.get("blink", True):
        return []
    r, out, t = random.Random(P.get("seed", 11) * 7 + 3), [], 1.3
    while t < P["film"] - 0.3:
        out.append(t)
        t += r.uniform(2.2, 4.8)
    return out


def face_at(P, t, blink_times):
    ch = dict(FACE0)
    for a in P["actions"]:
        if a["type"] != "face" or a["expr"] == "blink":
            continue
        w = envelope(dict(a, ease=a.get("ease", 0.2)), t)
        if w > 0:
            tgt = dict(FACE0, **EXPR[a["expr"]])
            tgt.update(a.get("set", {}))
            ch = {k: _mix(ch[k], tgt[k], w) for k in ch}
    bl = [b for b in blink_times] + [a["t0"] for a in P["actions"] if a["type"] == "face" and a["expr"] == "blink"]
    for b in bl:                                              # 0.16 s: shut fast, open a little slower
        u = (t - b) / 0.16
        if 0 <= u <= 1:
            ch["lid"] = max(ch["lid"], smooth(u / 0.4) if u < 0.4 else 1 - smooth((u - 0.4) / 0.6))
    return ch


def holds(P):
    return [a for a in P["actions"] if a["type"] == "hold"]


def hold_pair(a, t):
    """The two keys hold_key(a, t) is blending between (the same key twice before the first / after the last)."""
    ks = a["keys"]
    if t <= ks[0]["t"]:
        return ks[0], ks[0]
    if t >= ks[-1]["t"]:
        return ks[-1], ks[-1]
    for k0, k1 in zip(ks, ks[1:]):
        if t <= k1["t"]:
            return k0, k1
    return ks[-1], ks[-1]


def hold_key(a, t):
    """(at, off, rot) of the keyed path at time t (smoothly between keys, held after the last)."""
    ks = a["keys"]
    if t <= ks[0]["t"]:
        k0 = k1 = ks[0]; u = 0.0
    elif t >= ks[-1]["t"]:
        k0 = k1 = ks[-1]; u = 0.0
    else:
        for k0, k1 in zip(ks, ks[1:]):
            if t <= k1["t"]:
                break
        u = smoother((t - k0["t"]) / max(1e-6, k1["t"] - k0["t"]))
    rot = tuple(r0 + (r1 - r0) * u for r0, r1 in zip(k0.get("rot", (0, 0, 0)), k1.get("rot", (0, 0, 0))))
    off = tuple(o0 + (o1 - o0) * u for o0, o1 in zip(k0.get("off", (0, 0, 0)), k1.get("off", (0, 0, 0))))
    return k0["at"], k1["at"], u, off, rot


def hold_scale(a, t):
    """Uniform scale of the held object at time t from the keys' "scale" (1.0 when no key has one)."""
    ks = a["keys"]
    sc = lambda k: k.get("scale", 1.0)
    if t <= ks[0]["t"]:
        return sc(ks[0])
    for k0, k1 in zip(ks, ks[1:]):
        if t <= k1["t"]:
            return sc(k0) + (sc(k1) - sc(k0)) * smoother((t - k0["t"]) / max(1e-6, k1["t"] - k0["t"]))
    return sc(ks[-1])


def hold_weight(a, t):
    r = a.get("reach", 0.35)
    return smooth((t - (a["t0"] - r)) / r) * (1 - smooth((t - a["t1"]) / r))


def active_hold(P, name, t):
    """The hold that controls structure `name` at time t (the latest one already started), or None."""
    cur = None
    lead = (lambda a: a.get("reach", 0.35)) if P.get("engine_rev", 1) >= 2 else (lambda a: 0.0)   # rev 2: the reach-in counts
    for a in holds(P):
        if a["target"] == name and t >= a["keys"][0]["t"] - lead(a) - 1e-9:
            cur = a
    return cur
