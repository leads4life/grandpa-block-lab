"""Block Lab engine -- shared, pure-Python core: story loading, time references, structures and the full plan.

A story is a JSON file (see stories/). Structures: "cells" | "copy_of"+"scale" | "box" [nx,ny,nz] | "gnomon" k |
"pyramid" [9,7,5,...]; "centered": false puts cell (0,0) at "at" (so separate structures can interlock).
Times anywhere in a story can be:
    1.3                         seconds
    ["line_id", 0.62]           62 % of the way through that line
    ["line_id", "start", -0.25] start (or "end") of a line, plus/minus seconds
    "end"                       end of the film
Everything the scene, overlay and audio need is written once to build/plan.json.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
FPS, B, STRIDE = 30, 0.1, 0.2
W_PX, H_PX = 1080, 1920


def story_path(argv=None):
    argv = sys.argv if argv is None else argv
    if "--story" in argv:
        return os.path.abspath(argv[argv.index("--story") + 1])
    if os.environ.get("STORY"):
        return os.path.abspath(os.environ["STORY"])
    p = os.path.join(BUILD, "story.json")
    if os.path.exists(p):
        return p
    raise SystemExit("no story: pass --story path/to/story.json (or set STORY)")


def load_story(path=None):
    path = path or story_path()
    s = json.load(open(path))
    s.setdefault("slug", os.path.splitext(os.path.basename(path))[0])
    s.setdefault("voice", "am_santa"); s.setdefault("speed", 0.95)
    s.setdefault("start", 0.3); s.setdefault("tail", 1.6)
    s.setdefault("channel_tag", "GRANDPA'S BLOCK LAB")
    return s


WORLD_OPTIONS = {                                  # story "world": {...}; anything left out keeps today's look
    "ground": ("desert", "grass", "snow", "beach", "stone", "paris"),
    "time": ("day", "morning", "sunset", "night"),
    "weather": ("clear", "clouds", "rain", "snow"),
    "animals": ("birds", "seagulls", "pigeons", "cat"),
    "interior": ("none", "cabin"),                 # "cabin": grandpa's log cabin around the middle of the island
    "terrain": ("island", "forest_west"),          # "forest_west": a forest with a stream joins the island to the west
}
WORLD_FREE = ("sun", "exposure", "roof", "door_open", "clouds_pass", "leaves", "critters", "lantern", "rigging")   # roof: true (seen from outside only); door_open: [t0, t1, deg]                   # free values: "sun" light travel direction [x,y,z], "exposure" offset
OUTFIT_OPTIONS = {                                 # story "grandpa": {"outfit": {...}}
    "hat": ("cap", "hardhat", "santa", "beret", "straw", "beanie", "none"),
    "shirt": ("rust", "red", "blue", "green", "yellow", "purple", "white", "striped"),
    "extras": ("goggles", "scarf", "vest", "hammer"),
}


def world_settings(story):
    w = dict(ground="desert", time="day", weather="clear", animals=[])
    w.update(story.get("world", {}))
    o = dict(hat="cap", shirt="rust", extras=[])
    o.update(story.get("grandpa", {}).get("outfit", {}))
    for opts, d, what in ((WORLD_OPTIONS, w, "world"), (OUTFIT_OPTIONS, o, "outfit")):
        for k, v in d.items():
            if what == "world" and k in WORLD_FREE:
                continue
            if k not in opts:
                raise SystemExit("story %s: unknown setting %r (use %s)" % (what, k, ", ".join(opts)))
            for item in (v if isinstance(v, list) else [v]):
                if item not in opts[k]:
                    raise SystemExit("story %s %s: unknown %r (use %s)" % (what, k, item, ", ".join(opts[k])))
    return w, o


def cl(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = cl(x)
    return x * x * (3 - 2 * x)


def slide_offset(P, name, t):
    """World offset of structure `name` at t from its (non-local) "slide" actions -- what the rigging follows."""
    off = [0.0, 0.0, 0.0]
    for a in P["actions"]:
        if a["type"] == "slide" and a["target"] == name and not a.get("local"):
            u = smoother((t - a["t0"]) / max(1e-6, a["t1"] - a["t0"]))
            off = [off[i] + a["by"][i] * u for i in range(3)]
    return off


def smoother(x):
    x = cl(x)
    return x ** 3 * (x * (6 * x - 15) + 10)


def motion_angle(a, t):
    """Degrees of a spin (eased from 0 to 'degrees', or linear with 'ease': false) or a swing (sine, faded in and out)."""
    if a["type"] == "trip":
        return trip_angle(a, t)
    if a["type"] == "spin":
        u = cl((t - a["t0"]) / max(1e-6, a["t1"] - a["t0"]))
        return a["degrees"] * (smoother(u) if a.get("ease", True) else u)
    if t <= a["t0"] or t >= a["t1"]:
        return 0.0
    fade = smooth((t - a["t0"]) / 0.4) * (1 - smooth((t - (a["t1"] - 0.4)) / 0.4))
    return a["degrees"] * fade * math.sin(2 * math.pi * (t - a["t0"]) / a.get("period", 1.6))


def trip_strikes(a, t0=-1e9, t1=1e9):
    """'trip': strike times of a cam-driven hammer: first + k*period + each cam's offset, within [t0, t1]."""
    P, out = a["period"], []
    k0 = math.floor((t0 - a["first"] - max(a.get("cams", [0.0]))) / P) - 1
    k1 = math.ceil((t1 - a["first"]) / P) + 1
    for k in range(k0, k1 + 1):
        for ci, off in enumerate(a.get("cams", [0.0])):
            s = a["first"] + k * P + off
            if any(w[0] <= s <= w[1] and ci == w[2] for w in a.get("skip", [])):
                continue                                  # "skip": [[t0, t1, cam]] -- that cam misses (e.g. a sagging axle)
            if t0 <= s <= t1 and a["t0"] <= s <= a["t1"]:
                out.append(s)
    return sorted(out)


def trip_angle(a, t):
    """Degrees of a trip hammer: lifted smoothly by a cam over 'rise' s, then dropped (gravity) over 'drop' s at each strike."""
    rise, drop, deg = a.get("rise", 0.45), a.get("drop", 0.07), a["degrees"]
    best = 0.0
    for s in trip_strikes(a, t - drop - 1e-6, t + rise + 1e-6):
        if s - rise <= t < s:
            best = max(best, deg * smooth((t - (s - rise)) / rise))
        elif s <= t < s + drop:
            best = max(best, deg * (1 - ((t - s) / drop) ** 2))
    return best


def critter_state(c, t):
    """A critter on a keyed path {"path": [[t, x, y], ...], "hop": height, "hop_len": metres per hop}: where it is at t.
    -> (x, y, z, heading_rad, moving). It hops while it moves (one hop per hop_len), sits still between keys that repeat."""
    ks = c["path"]
    if t <= ks[0][0]:
        k0 = k1 = ks[0]; u = 0.0
    elif t >= ks[-1][0]:
        k0 = k1 = ks[-1]; u = 0.0
    else:
        for k0, k1 in zip(ks, ks[1:]):
            if t <= k1[0]:
                break
        u = (t - k0[0]) / max(1e-6, k1[0] - k0[0])
    x, y = k0[1] + (k1[1] - k0[1]) * u, k0[2] + (k1[2] - k0[2]) * u
    seg = math.hypot(k1[1] - k0[1], k1[2] - k0[2])
    moving = seg > 1e-4 and 0.0 < u < 1.0
    hl = c.get("hop_len", 0.22)
    z = c.get("hop", 0.10) * abs(math.sin(math.pi * u * seg / hl)) if moving else 0.0
    if seg > 1e-4:
        heading = math.atan2(k1[2] - k0[2], k1[1] - k0[1])
    else:                                                  # sitting: keep the last heading
        prev = [(a, b) for a, b in zip(ks, ks[1:]) if b[0] <= t and math.hypot(b[1] - a[1], b[2] - a[2]) > 1e-4]
        heading = math.atan2(prev[-1][1][2] - prev[-1][0][2], prev[-1][1][1] - prev[-1][0][1]) if prev else c.get("heading", 0.0)
    return x, y, z, heading, moving


def actor_heading(c, t):
    """Heading (radians) of a walking actor (boar, Tobias): along the path while moving; while standing, the story's
    "yaw" keys [[t, degrees], ...] (eased, the short way round) once the first one has passed, else the last heading."""
    x, y, z, hd, moving = critter_state(dict(c, hop=0.0), t)
    if moving and any(w[0] <= t <= w[1] for w in c.get("backing", [])):
        return hd + math.pi                                # "backing": [[t0, t1]] -- backs away, still facing us
    ks = c.get("yaw", [])
    if moving or not ks or t < ks[0][0]:
        return hd
    if t >= ks[-1][0]:
        return math.radians(ks[-1][1])
    for k0, k1 in zip(ks, ks[1:]):
        if t <= k1[0]:
            u = smooth((t - k0[0]) / max(1e-6, k1[0] - k0[0]))
            d = (k1[1] - k0[1] + 180) % 360 - 180
            return math.radians(k0[1] + d * u)
    return hd


def actor_steps(c):
    """Footfall times of a walking actor: one per "stride" metres along its path (for footstep sounds)."""
    return critter_landings(dict(c, hop_len=c.get("stride", 0.18)))


def critter_landings(c):
    """Times its feet touch down (one per hop) -- for the hop sounds."""
    out, hl = [], c.get("hop_len", 0.22)
    for k0, k1 in zip(c["path"], c["path"][1:]):
        seg = math.hypot(k1[1] - k0[1], k1[2] - k0[2])
        n = int(seg / hl)
        out += [k0[0] + (k1[0] - k0[0]) * (i * hl / seg) for i in range(1, n + 1)] if seg > 1e-4 else []
    return out


def fly_offset(a, t):
    """'fly': a thrown object on a true arc. Offset of the structure's root at time t:
    origin + v0*tau + 1/2*g*tau^2 (down) - anchor, with tau = tau0 + time since the throw (held after it lands)."""
    tau = a.get("tau0", 0.0) + min(max(t - a["t0"], 0.0), a["t1"] - a["t0"])
    v, g = a["v0"], a.get("g", 9.81)
    p = (v[0] * tau, v[1] * tau, v[2] * tau - 0.5 * g * tau * tau)
    o, an = a.get("origin", [0, 0, 0]), a.get("anchor", [0, 0, 0])
    return tuple(o[i] + p[i] - an[i] for i in range(3))


def fr(t):
    return int(round(t * FPS))


class Clock:
    """Resolves story time references once the narration timings exist."""

    def __init__(self, lines, film):
        self.L = {l["id"]: l for l in lines}
        self.film = film

    def __call__(self, ref):
        if ref is None:
            return None
        if isinstance(ref, (int, float)):
            return float(ref)
        if ref == "end":
            return self.film
        lid, where = ref[0], ref[1]
        off = ref[2] if len(ref) > 2 else 0.0
        ln = self.L[lid]
        if where == "start":
            t = ln["start"]
        elif where == "end":
            t = ln["end"]
        else:
            t = ln["start"] + (ln["end"] - ln["start"]) * float(where)
        return t + off


# ---------------------------------------------------------------- structures
def _part_fn(expr):
    code = compile(expr, "<part>", "eval")
    return lambda c: bool(eval(code, {"__builtins__": {}, "abs": abs, "min": min, "max": max}, {"x": c[0], "y": c[1], "z": c[2]}))


def structure_cells(name, structs, cache=None):
    cache = {} if cache is None else cache
    if name in cache:
        return cache[name]
    s = structs[name]
    if "cells" in s:
        cells = [tuple(c) for c in s["cells"]]
    elif "copy_of" in s:
        k = int(s.get("scale", 1))
        cells = [(k * x + dx, k * y + dy, k * z + dz) for x, y, z in structure_cells(s["copy_of"], structs, cache)
                 for dx in range(k) for dy in range(k) for dz in range(k)]
    elif "box" in s:
        nx, ny, nz = s["box"]
        cells = [(x, y, z) for z in range(nz) for y in range(ny) for x in range(nx)]
    elif "gnomon" in s:                                     # L-shaped row that turns a k x k square into (k+1) x (k+1)
        k = int(s["gnomon"])
        cells = [(x, y, 0) for x in range(k + 1) for y in range(k + 1) if max(x, y) == k]
    elif "pyramid" in s:                                    # e.g. [9, 7, 5, 3, 1]
        big = s["pyramid"][0]
        cells = [(x + (big - n) // 2, y + (big - n) // 2, z) for z, n in enumerate(s["pyramid"]) for y in range(n) for x in range(n)]
    else:
        raise ValueError("structure %s needs cells, copy_of, box or pyramid" % name)
    cache[name] = sorted(set(cells), key=lambda c: (c[2], c[1], c[0]))
    return cache[name]


def local_pos(cell, cells, centered=True):
    """Block centre relative to the structure's 'at' point: bbox-centred, or (centered=false) cell (0,0) at 'at'."""
    if not centered:
        return (cell[0] * B, cell[1] * B, (cell[2] + 0.5) * B)
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return ((cell[0] - cx) * B, (cell[1] - cy) * B, (cell[2] + 0.5) * B)


def extent(cells):
    xs, ys, zs = [c[0] for c in cells], [c[1] for c in cells], [c[2] for c in cells]
    return ((max(xs) - min(xs) + 1) * B, (max(ys) - min(ys) + 1) * B, (max(zs) + 1) * B)


# ---------------------------------------------------------------- plan
def make_plan(story=None):
    story = story or load_story()
    D = json.load(open(os.path.join(BUILD, "dialogue.json")))
    lines, film, nf = D["lines"], D["film"], D["nf"]
    T = Clock(lines, film)
    structs = story["structures"]
    cache = {}
    S = {}
    for name, s in structs.items():
        cells = structure_cells(name, structs, cache)
        parts = {pn: [c for c in cells if _part_fn(expr)(c)] for pn, expr in s.get("parts", {}).items()}
        S[name] = dict(name=name, cells=cells, at=list(s.get("at", [0, 0])), material=s.get("material", "sandstone"),
                       eyes=bool(s.get("eyes", False)), stand=s.get("stand", "right"), parts=parts,
                       size=extent(cells), expect=s.get("expect_blocks"), prebuilt=bool(s.get("prebuilt", False)),
                       centered=bool(s.get("centered", True)), block_shape=list(s.get("block_shape", [1, 1, 1])),
                       yaw=float(s.get("yaw", 0.0)), extras=s.get("extras", []))
    acts = []
    for a in story.get("actions", []):
        a = dict(a)
        a["t0"] = T(a.get("when", 0.0))
        a["t1"] = T(a.get("until")) if a.get("until") is not None else a["t0"]
        if a.get("cool_from") is not None:
            a["c0"], a["c1"] = T(a["cool_from"]), T(a.get("cool_until", a["cool_from"]))
        if a["type"] == "hold":                                  # keyed path of a held object
            a["keys"] = [dict(k, t=T(k["t"])) for k in a["keys"]]
        acts.append(a)
    acts.sort(key=lambda a: a["t0"])

    # ---- blocks + build swings
    blocks, swings = [], []
    built = set()
    for a in acts:
        if a["type"] != "build":
            continue
        st = S[a["target"]]
        built.add(st["name"])
        order = a.get("order", "z")
        key = {"x": lambda c: c[0], "y": lambda c: c[1], "z": lambda c: c[2]}[order]
        groups = {}
        for c in st["cells"]:
            groups.setdefault(key(c), []).append(c)
        gk = sorted(groups)
        T_sw = (a["t1"] - a["t0"]) / max(1, len(gk))
        for gi, g in enumerate(gk):
            cs = sorted(groups[g], key=lambda c: (c[2], c[1], c[0]))
            s0 = a["t0"] + gi * T_sw
            sw = dict(s=s0, e=s0 + T_sw, target=st["name"], ids=[])
            for q, c in enumerate(cs):
                ta = s0 + T_sw * (0.2 + 0.6 * (q / max(1, len(cs) - 1)))
                b = dict(id=len(blocks), struct=st["name"], cell=list(c), pos=local_pos(c, st["cells"], st["centered"]),
                         appear=fr(ta), settle=fr(ta) + 2, prebuilt=False)
                blocks.append(b); sw["ids"].append(b["id"])
            swings.append(sw)
    for name, st in S.items():                                  # structures that are simply there from the start
        if name not in built:
            for c in st["cells"]:
                blocks.append(dict(id=len(blocks), struct=name, cell=list(c), pos=local_pos(c, st["cells"], st["centered"]),
                                   appear=0, settle=0, prebuilt=True))
    for a in acts:                                              # 'remove': take a built structure apart, top first
        if a["type"] != "remove":
            continue
        mine = [b for b in blocks if b["struct"] == a["target"]]
        groups = {}
        for b in mine:
            groups.setdefault(-b["cell"][2], []).append(b)
        gk = sorted(groups)
        T_sw = (a["t1"] - a["t0"]) / max(1, len(gk))
        for gi, g in enumerate(gk):
            s0 = a["t0"] + gi * T_sw
            sw = dict(s=s0, e=s0 + T_sw, target=a["target"], ids=[])
            for q, b in enumerate(groups[g]):
                b["vanish"] = fr(s0 + T_sw * (0.2 + 0.6 * (q / max(1, len(groups[g]) - 1))))
                sw["ids"].append(b["id"])
            if not a.get("quiet"):
                swings.append(sw)

    # ---- grandpa's walk: stand beside whatever he builds, walk where the story says
    def stand_point(st):
        w, d, _ = st["size"]
        x, y = st["at"][:2]
        if not st["centered"]:                                   # 'at' is the corner: use the footprint centre
            xs, ys = [c[0] for c in st["cells"]], [c[1] for c in st["cells"]]
            x += (min(xs) + max(xs)) / 2 * B
            y += (min(ys) + max(ys)) / 2 * B
        return {"right": (x + w / 2 + 0.28, y + 0.18), "left": (x - w / 2 - 0.28, y + 0.18),
                "behind": (x + 0.12, y + d / 2 + 0.36), "front": (x + 0.15, y - d / 2 - 0.38)}[st["stand"]]

    xyz = lambda p: (p[0], p[1], p[2] if len(p) > 2 else 0.0)     # positions may give a height (scaffold, ladder)
    keys = [(0.0,) + xyz(story.get("grandpa", {}).get("start", [0.0, 0.5]))]
    for a in sorted(acts, key=lambda a: a["t0"]):
        if a["type"] in ("build", "remove") and not a.get("quiet"):     # quiet: happens on its own, grandpa stays put
            p = xyz(a.get("stand_at") or stand_point(S[a["target"]]))  # optional [x, y(, z)] override per build
            keys.append((a["t0"] - 0.05,) + p)
            keys.append((a["t1"],) + p)
        elif a["type"] == "move":
            last = keys[-1]
            keys.append((a["t0"],) + last[1:])
            for k, wp in enumerate(a.get("via", [])):                 # optional waypoints, evenly timed
                keys.append((a["t0"] + (a["t1"] - a["t0"]) * (k + 1) / (len(a["via"]) + 1),) + xyz(wp))
            keys.append((a["t1"],) + xyz(a["to"]))
    keys.sort(key=lambda k: k[0])
    keys.append((film + 1,) + keys[-1][1:])
    path = _root_path(keys, nf)
    phase, amp, steps = _gait(path, nf)

    melt = {}
    for a in acts:
        if a["type"] == "melt":
            melt[a["target"]] = melt_targets([b for b in blocks if b["struct"] == a["target"]], S[a["target"]]["cells"])
    world, outfit = world_settings(story)
    plan = dict(slug=story["slug"], title=story.get("title", story["slug"]), fps=FPS, nf=nf, film=film, block=B,
                world=world, outfit=outfit, melt=melt, loop=bool(story.get("loop", False)),
                w=W_PX if story.get("format", "vertical") == "vertical" else H_PX,
                h=H_PX if story.get("format", "vertical") == "vertical" else W_PX, voice=D["voice"], lines=lines, mouth=D["mouth"], channel_tag=story["channel_tag"],
                structures=S, blocks=blocks, swings=swings, actions=acts, path=path, phase=phase, amp=amp, steps=steps,
                camera=[dict(k, t=T(k["at"])) for k in story.get("camera", [])],
                poses=story.get("poses", {}), seed=int(story.get("seed", 11)), blink=bool(story.get("blink", False)),
                engine_rev=int(story.get("engine_rev", 1)),     # 2: fixes that would change already-approved scenes
                target_duration=story.get("target_duration"), qa=story.get("qa", {}), scene=story.get("scene", {}),
                cards=[_resolve_card(c, T) for c in story.get("cards", [])])
    if "captions" in story:                                     # "srt": no captions in the picture, a .srt file for YouTube
        plan["captions"] = story["captions"]                    # (left out when unset, so older plans stay byte-identical)
    return plan


def melt_targets(blocks, cells):
    """'melt': the structure's blocks settle into a flat slab over its footprint, bottom layer first.
    Lowest blocks take the lowest layer; within a layer each block takes the nearest free cell. -> {block id: cell}"""
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    slab = [(x, y) for y in range(min(ys), max(ys) + 1) for x in range(min(xs), max(xs) + 1)]
    out, layer, free = {}, 0, list(slab)
    for b in sorted(blocks, key=lambda b: (b["cell"][2], b["cell"][0], b["cell"][1])):
        if not free:
            layer, free = layer + 1, list(slab)
        bx, by = b["cell"][0], b["cell"][1]
        k = min(range(len(free)), key=lambda i: (free[i][0] - bx) ** 2 + (free[i][1] - by) ** 2)
        x, y = free.pop(k)
        out[str(b["id"])] = [x, y, layer]
    return out


def _resolve_card(c, T):
    c = dict(c)
    c["t0"] = T(c.get("when", 0.0))
    c["t1"] = T(c.get("until", "end"))
    if "viewers" in c:
        c["viewers"] = [[T(tv), n] for tv, n in c["viewers"]]
    if "rows" in c:
        c["rows"] = [dict(r, t=T(r.get("at", c.get("when", 0.0)))) for r in c["rows"]]
    if "items" in c:                                         # "inventory": items going in / coming out [{"in", "out"}]
        c["items"] = [dict(i, t_in=T(i["in"]), t_out=T(i["out"]) if i.get("out") is not None else None) for i in c["items"]]
    if "msgs" in c:                                          # "chat": viewer comments [{"at", "user", "text"}]
        c["msgs"] = [dict(m, t=T(m["at"])) for m in c["msgs"]]
    return c


def _root_path(keys, nf):
    def lin(t):
        if t <= keys[0][0]:
            return keys[0][1:]
        for k0, k1 in zip(keys, keys[1:]):
            if t <= k1[0]:
                u = (t - k0[0]) / max(1e-9, k1[0] - k0[0])
                return tuple(a + (b - a) * u for a, b in zip(k0[1:], k1[1:]))
        return keys[-1][1:]
    sub, sig = 4, 0.15 * FPS * 4
    raw = [lin((n / sub - 30) / FPS) for n in range((nf + 60) * sub)]
    rad = int(3 * sig)
    w = [math.exp(-0.5 * (q / sig) ** 2) for q in range(-rad, rad + 1)]
    out = []
    for f in range(nf):
        c = (f + 30) * sub
        sx = sy = sz = sw = 0.0
        for q, wq in zip(range(-rad, rad + 1), w):
            n = min(len(raw) - 1, max(0, c + q))
            sx += raw[n][0] * wq; sy += raw[n][1] * wq; sz += raw[n][2] * wq; sw += wq
        out.append((sx / sw, sy / sw, sz / sw))
    return out


def _gait(path, nf):
    phase, amp, steps = [], [], []
    ph = 0.0
    for f in range(nf):
        p0, p1 = path[max(0, f - 1)], path[f]
        ds = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        new = ph + ds / (2 * STRIDE)
        speed = ds * FPS
        a = cl(speed / 0.12)
        if a > 0.25:
            for foot, off in (("R", 0.5), ("L", 0.0)):
                if math.floor(new + off - 0.5) > math.floor(ph + off - 0.5):
                    steps.append(dict(frame=f, foot=foot, speed=round(speed, 3)))
        ph = new
        phase.append(ph); amp.append(a)
    sm = [sum(amp[max(0, f - 5):f + 6]) / len(amp[max(0, f - 5):f + 6]) for f in range(nf)]
    return phase, sm, steps


def save_plan(plan):
    os.makedirs(BUILD, exist_ok=True)
    json.dump(plan, open(os.path.join(BUILD, "plan.json"), "w"))


def load_plan():
    return json.load(open(os.path.join(BUILD, "plan.json")))


if __name__ == "__main__":
    st = load_story()
    p = make_plan(st)
    save_plan(p)
    print("plan: %s  %.2f s  %d frames" % (p["slug"], p["film"], p["nf"]))
    for n, s in p["structures"].items():
        n_b = sum(1 for b in p["blocks"] if b["struct"] == n)
        print("  %-8s %3d blocks  parts %s" % (n, n_b, {k: len(v) for k, v in s["parts"].items()}))
    print("  actions:", ", ".join("%s@%.2f" % (a["type"], a["t0"]) for a in p["actions"]))
