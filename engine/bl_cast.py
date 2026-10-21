"""The cast beyond Grandpa: the wild boar and Tobias, animated from their world "critters" entries (approved designs in
voxelchars). Pure keyframes, built after the world, so scenes without them are untouched.

boar:   {"kind": "boar", "path": [[t, x, y], ...], "yaw": [[t, deg], ...], "visible": [t_in, t_out], "stride": m,
         "mood": [[t, "calm" | "agitated"], ...], "huffs": [t], "clacks": [t], "stomps": [t], "startle": t}
tobias: {"kind": "tobias", "path": ..., "yaw": ..., "visible": [t_in, t_out], "rise": [t0, t1] (stands up from a crouch),
         "poses": [[t0, t1, name], ...], "faces": [[t, name], ...], "look": [[t0, t1, [x, y, z]], ...], "blink": true}
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

import bl_common as C
import voxelchars as CH
import voxelkit as VK


def _key(o, *paths, f):
    for p in paths:
        o.keyframe_insert(p, frame=f)


def _recentre(o, centre):
    """Move an object's origin to `centre` (its parent's frame) without moving its boxes, so it scales about that point."""
    o.data.transform(Matrix.Translation(-Vector(centre)))
    o.location = Vector(o.location) + Vector(centre)


def _env(t, t0, t1, ramp=0.2):
    """0 -> 1 -> 0 over [t0, t1], eased in and out over `ramp` s."""
    if t <= t0 or t >= t1:
        return 0.0
    return C.smooth((t - t0) / ramp) * C.smooth((t1 - t) / ramp)


# ------------------------------------------------------------------------------------------------------------------ boar
def build_boar_actor(sc, c, fps, nf):
    root = bpy.data.objects.new("BoarActor", None)
    sc.collection.objects.link(root)
    moods = {}
    for m in ("calm", "agitated"):
        parts = CH.build_boar(sc, m, "Boar_" + m, parts=True)
        parts["body"].parent = root
        parts["pitch"] = parts["head"].rotation_euler[1]
        if parts["puff"]:
            _recentre(parts["puff"], (0.42, 0, -0.065))           # breath blasts out of the nose
        if parts["dust"]:
            _recentre(parts["dust"], (0.31, 0, 0.0))
        moods[m] = parts
    vis = c.get("visible", [-1e9, 1e9])
    mk = sorted(c.get("mood", [[-1e9, "calm"]]), key=lambda k: k[0])
    huffs, clacks, stomps, startle = c.get("huffs", []), c.get("clacks", []), c.get("stomps", []), c.get("startle")
    stride, dist, prev = c.get("stride", 0.18), 0.0, None
    walk = dict(c, hop=0.0)
    for f in range(nf):
        t = f / fps
        x, y, _, _, moving = C.critter_state(walk, t)
        if prev is not None:
            dist += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
        ph = math.pi * dist / stride                                  # a full gait cycle every two strides
        mood = ([m for tk, m in mk if tk <= t] or [mk[0][1]])[-1]
        on = vis[0] <= t <= vis[1]
        z = 0.012 * abs(math.sin(ph)) if moving else 0.0
        if startle is not None and startle <= t < startle + 0.32:     # jumps out of its skin at the CLUNK
            z += 0.12 * math.sin(math.pi * (t - startle) / 0.32)
        root.location = (x, y, z)
        root.rotation_euler = (0, 0, C.actor_heading(c, t))           # the boar's nose is local +x
        _key(root, "location", "rotation_euler", f=f)
        for m, parts in moods.items():
            k = 1.0 if (on and m == mood) else 0.0
            parts["body"].scale = (k, k, k)
            _key(parts["body"], "scale", f=f)
            for i, lg in enumerate(parts["legs"]):
                a = 28.0 * math.sin(ph + (math.pi if i in (1, 2) else 0.0)) if moving else 0.0   # diagonal pairs
                for j, ts in enumerate(stomps):                       # front legs take turns: lift... and STOMP
                    if i == j % 2 and ts - 0.30 <= t < ts:
                        if t < ts - 0.12:
                            a = -38.0 * C.smooth((t - (ts - 0.30)) / 0.18)
                        elif t < ts - 0.05:
                            a = -38.0
                        else:
                            a = -38.0 * (1 - ((t - (ts - 0.05)) / 0.05) ** 2)
                lg.rotation_euler = (0, math.radians(a), 0)
                _key(lg, "rotation_euler", f=f)
            hp, hy = parts["pitch"], 0.0
            for th in huffs:                                          # the snout jerks up with each huff
                hp -= math.radians(9) * _env(t, th - 0.05, th + 0.35, 0.12)
            for tc in clacks:                                         # tusks clacking: a quick head shake
                if tc <= t < tc + 0.36:
                    hy = math.radians(7) * math.sin(2 * math.pi * (t - tc) / 0.12) * (1 - (t - tc) / 0.36)
            parts["head"].rotation_euler = (0, hp, hy)
            _key(parts["head"], "rotation_euler", f=f)
            if parts["puff"]:
                s_ = 0.0
                for th in huffs:
                    if th <= t < th + 0.55:
                        u = (t - th) / 0.55
                        s_ = max(s_, C.smooth(u / 0.1) * (1 - u) ** 0.6 * (1 + 0.9 * u))
                parts["puff"].scale = (s_, s_, s_)
                _key(parts["puff"], "scale", f=f)
            if parts["dust"]:
                s_ = 0.0
                for ts in stomps:
                    if ts <= t < ts + 0.8:
                        u = (t - ts) / 0.8
                        s_ = max(s_, C.smooth(u / 0.08) * (1 - u) ** 0.7 * (1 + 0.5 * u))
                parts["dust"].scale = (s_, s_, s_)
                _key(parts["dust"], "scale", f=f)
    return root


# ---------------------------------------------------------------------------------------------------------------- Tobias
POSES = {                                                             # bone: (rx, ry, rz) degrees in his rest frame
    "point_R": {"upper_arm.R": (-82, 12, 0), "forearm.R": (-6, 0, 0)},
    "easy_R": {"upper_arm.R": (-55, 22, 0), "forearm.R": (-25, 0, 0)},       # palm out: "easy..."
    "notebook_L": {"upper_arm.L": (-38, 0, 0), "forearm.L": (-62, 0, 0)},
    "write_R": {"upper_arm.R": (-40, -18, 0), "forearm.R": (-62, 0, 0)},     # pencil to the notebook
    "kick_R": {"thigh.R": (-62, 0, 0), "shin.R": (18, 0, 0), "spine": (6, 0, 0)},
    "crouch": {"thigh.R": (-80, 0, 0), "shin.R": (110, 0, 0), "thigh.L": (-80, 0, 0), "shin.L": (110, 0, 0), "spine": (-25, 0, 0)},
    "lean_in": {"spine": (-10, 0, 0)},
    "hold_tablet": {"upper_arm.R": (-48, -10, 0), "forearm.R": (-55, 0, 0), "upper_arm.L": (-48, 10, 0), "forearm.L": (-55, 0, 0)},
    "point_down": {"upper_arm.R": (-55, 8, 0), "forearm.R": (12, 0, 0), "spine": (-8, 0, 0)},
}
FACES = {                                                             # face bone: dict(off=..., S=...)
    "neutral": {},
    "calm": {"brow.L": dict(off=(0, 0, 0.012)), "brow.R": dict(off=(0, 0, -0.003)), "lid.R": dict(S=(1, 1, 5)),
             "lid.L": dict(S=(1, 1, 5)), "smile": dict(off=(0.008, 0, 0.003), S=(0.9, 1, 1.0))},
    "smile": {"smile": dict(S=(1.2, 1, 1.3)), "cheeks": dict(off=(0, 0, 0.004))},
    "deadpan": {"lid.R": dict(S=(1, 1, 10)), "lid.L": dict(S=(1, 1, 10)), "smile": dict(S=(0.7, 1, 0.6))},
}
FACE_BONES = [b[0] for b in CH.KID_FACE_BONES]
BODY_BONES = ["hips", "spine", "head", "jaw", "upper_arm.R", "forearm.R", "upper_arm.L", "forearm.L",
              "thigh.R", "shin.R", "thigh.L", "shin.L"]


def _face_mix(faces, t, blend=0.15):
    """{bone: (off, S)} at t: the latest face key, blended from the previous one over `blend` s."""
    def of(name):
        return {b: (Vector(v.get("off", (0, 0, 0))), Vector(v.get("S", (1, 1, 1)))) for b, v in FACES[name].items()}
    ks = [k for k in sorted(faces, key=lambda k: k[0]) if k[0] <= t]
    if not ks:
        return {}
    cur = of(ks[-1][1])
    if len(ks) < 2 or t - ks[-1][0] >= blend:
        return cur
    old, u = of(ks[-2][1]), C.smooth((t - ks[-1][0]) / blend)
    out = {}
    for b in set(cur) | set(old):
        o0, s0 = old.get(b, (Vector(), Vector((1, 1, 1))))
        o1, s1 = cur.get(b, (Vector(), Vector((1, 1, 1))))
        out[b] = (o0.lerp(o1, u), s0.lerp(s1, u))
    return out


def build_tablet(sc):
    """Tobias's block tablet: a dark slab with a glowing screen showing Grandpa's stream (the LIVE badge, him in frame).
    Built facing -y (his front), centred on its own origin."""
    M = [VK.mat("Tab_body", (0.12, 0.12, 0.14), rough=0.4), VK.emission_material("Tab_screen", (0.55, 0.75, 0.95), 2.0),
         VK.emission_material("Tab_live", (1.0, 0.15, 0.1), 6.0), VK.emission_material("Tab_white", (1.0, 1.0, 1.0), 3.0),
         VK.emission_material("Tab_grandpa", (0.85, 0.45, 0.30), 2.0)]
    boxes = [((0, 0, 0), (0.15, 0.014, 0.11), 0), ((0, -0.0075, 0), (0.13, 0.002, 0.09), 1),
             ((-0.045, -0.009, 0.032), (0.026, 0.002, 0.012), 2), ((0.0, -0.009, 0.032), (0.05, 0.002, 0.008), 3),    # LIVE badge
             ((0.0, -0.009, -0.012), (0.03, 0.002, 0.05), 4), ((0.0, -0.009, 0.016), (0.026, 0.002, 0.022), 3)]          # him, beard
    return VK.mesh_obj("TobiasTablet", boxes, M)


def build_tobias_actor(sc, c, fps, nf, mouth=None):
    root = bpy.data.objects.new("TobiasActor", None)
    sc.collection.objects.link(root)
    arm = CH.build_tobias(sc, parent=root)
    tablet = build_tablet(sc) if c.get("tablet") else None
    vis, rise = c.get("visible", [-1e9, 1e9]), c.get("rise")
    stride, dist, prev = c.get("stride", 0.16), 0.0, None
    walk = dict(c, hop=0.0)
    rng = random.Random(c.get("seed", 7))
    blinks, tb = [], -1.0
    while tb < nf / fps:                                              # his own blink rhythm
        tb += rng.uniform(2.6, 4.4); blinks.append(tb)
    for f in range(nf):
        t = f / fps
        x, y, _, _, moving = C.critter_state(walk, t)
        if prev is not None:
            dist += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
        ph = math.pi * dist / stride
        hd = C.actor_heading(c, t)
        z = 0.0
        for h0, h1 in c.get("hops", []):                              # hopping from stone to stone, one hop per stride
            if h0 <= t <= h1 and moving:
                z = max(z, 0.07 * abs(math.sin(ph)))
        if rise and t < rise[1]:                                      # stands up from behind something
            z = -0.30 * (1 - C.smooth((t - rise[0]) / max(1e-6, rise[1] - rise[0])))
        k = 1.0 if vis[0] <= t <= vis[1] else 0.0
        root.location, root.scale = (x, y, z), (k, k, k)
        root.rotation_euler = (0, 0, hd + math.pi / 2)                # his front is local -y; heading 0 = facing +x
        _key(root, "location", "rotation_euler", "scale", f=f)
        if tablet is not None:                                       # held up in front of his chest, screen facing out
            tw = max([_env(t, t0, t1, 0.2) for t0, t1 in c["tablet"]] + [0.0])
            fwd = Vector((math.cos(hd), math.sin(hd), 0.0))
            tablet.location = Vector((x, y, z)) + fwd * 0.17 + Vector((0, 0, 0.47))
            tablet.rotation_euler = (math.radians(-12), 0, hd + math.pi / 2)    # its -y (the screen) along his facing: away from him
            tablet.scale = (tw, tw, tw)
            _key(tablet, "location", "rotation_euler", "scale", f=f)
        rot = {b: Vector((0.0, 0.0, 0.0)) for b in BODY_BONES}
        if moving:                                                    # walking: legs and arms swing
            sw = math.sin(ph)
            rot["thigh.R"] += Vector((-24 * sw, 0, 0)); rot["thigh.L"] += Vector((24 * sw, 0, 0))
            rot["shin.R"] += Vector((20 * max(0.0, sw), 0, 0)); rot["shin.L"] += Vector((20 * max(0.0, -sw), 0, 0))
            rot["upper_arm.R"] += Vector((16 * sw, 0, 0)); rot["upper_arm.L"] += Vector((-16 * sw, 0, 0))
        for t0, t1, name in c.get("poses", []):
            w = _env(t, t0, t1, 0.12 if name == "kick_R" else 0.22)
            for b, r in POSES[name].items():
                rot[b] += Vector(r) * w
        for t0, t1, p in c.get("look", []):                           # turn his head toward a point
            w = _env(t, t0, t1, 0.25)
            if w > 0:
                ang = math.degrees(math.atan2(p[1] - y, p[0] - x) - hd)
                ang = (ang + 180) % 360 - 180
                rot["head"] += Vector((0, 0, max(-60.0, min(60.0, ang)) * w))
        m = mouth[f] if mouth is not None and f < len(mouth) else 0.0
        rot["jaw"] += Vector((18.0 * m, 0, 0))
        for b in BODY_BONES:
            CH.pose_bone(arm, b, rot=tuple(rot[b]))
            _key(arm.pose.bones[b], "location", "rotation_quaternion", "scale", f=f)
        fm = _face_mix(c.get("faces", []), t)
        blink = max([C.smooth(1 - abs(t - b_) / 0.07) for b_ in blinks if abs(t - b_) < 0.07] or [0.0]) if c.get("blink", True) else 0.0
        for b in FACE_BONES:
            off, S = fm.get(b, (Vector(), Vector((1, 1, 1))))
            S = Vector(S)
            if b.startswith("lid."):
                S.z = max(S.z, 1 + 31 * blink)                        # the lid strip covers the whole eye when he blinks
            if b == "smile":
                S.z *= 1 + 2.2 * m                                    # mouth opens with his voice
            CH.pose_bone(arm, b, off=tuple(off), S=tuple(S))
            _key(arm.pose.bones[b], "location", "rotation_quaternion", "scale", f=f)
    return root


# ---------------------------------------------------------------------------------------------------- memory cloud
def build_memory_cloud(sc, c, fps, nf):
    """A TV-style memory cloud over someone's head: a puffy grey cloud (small puffs trailing down to the head) with a mini
    agitated boar inside replaying the moment. {"kind": "memory_cloud", "at": [x, y, z], "visible": [t_in, t_out],
    "yaw": degrees (the boar faces this way), "boar": {"huffs": [...], "stomps": [...], "clacks": [...]}} -- times absolute."""
    root = bpy.data.objects.new("MemoryCloud", None)
    sc.collection.objects.link(root)
    M = [VK.mat("Cloud_lit", (0.93, 0.94, 0.97), rough=1.0), VK.mat("Cloud_shade", (0.78, 0.80, 0.86), rough=1.0)]
    puffs = [((0, 0, 0.02), (0.62, 0.30, 0.30), 0), ((-0.24, 0, 0.12), (0.34, 0.28, 0.30), 0), ((0.22, 0, 0.14), (0.38, 0.28, 0.30), 0),
             ((0.02, 0, 0.2), (0.40, 0.26, 0.24), 0), ((0, 0, -0.1), (0.52, 0.26, 0.10), 1)]
    tail = [((0.07, 0, -0.26), (0.08, 0.08, 0.08), 0), ((0.11, 0, -0.38), (0.05, 0.05, 0.05), 0)]   # little puffs down to the head
    cloud = VK.mesh_obj("MemoryCloudPuffs", puffs + tail, M, parent=root)
    spec = dict(kind="boar", path=[[-1.0, 0.0, -0.02], [nf / fps + 1, 0.0, -0.02]], mood=[[-9.0, "agitated"]],
                yaw=[[-9.0, c.get("yaw", 180.0)]], **{k: v for k, v in c.get("boar", {}).items()})
    boar = build_boar_actor(sc, spec, fps, nf)
    boar.parent = root
    boar.scale = (0.26, 0.26, 0.26)
    # (the boar keys its own location in its parent's space: it stands on the cloud's floor; scale it into the cloud)
    for fc in (boar.animation_data.action.fcurves if boar.animation_data and boar.animation_data.action else []):
        if fc.data_path == "location" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.co.y = kp.co.y * 0.26 - 0.08
    vis = c.get("visible", [-1e9, 1e9])
    x0, y0, z0 = c["at"]
    for f in range(nf):
        t = f / fps
        k = 0.0
        if vis[0] <= t <= vis[1]:
            k = C.smooth((t - vis[0]) / 0.45)                       # drifts in...
            if t > vis[1] - 0.18:                                   # ...and POPS
                u = (t - (vis[1] - 0.18)) / 0.18
                k = (1 + 0.35 * math.sin(math.pi * min(u, 0.5) * 2)) if u < 0.5 else (1.35 * (1 - (u - 0.5) / 0.5))
        bob = 0.025 * math.sin(2 * math.pi * 0.45 * t)
        root.location = (x0 + 0.015 * math.sin(2 * math.pi * 0.3 * t), y0, z0 + bob)
        root.scale = (k, k, k)
        root.rotation_euler = (0, 0, math.radians(c.get("face", 0.0)))
        _key(root, "location", "scale", "rotation_euler", f=f)
    return root


# ------------------------------------------------------------------------------------------------- 3D blueprint
def build_hologram(sc, c, fps, nf):
    """A blueprint drawing lifting off the page as a glowing blue 3D wireframe that turns slowly, then settles back.
    {"kind": "hologram", "model": "lever_gate", "at": [x, y, z], "visible": [t_in, t_out]}"""
    root = bpy.data.objects.new("Hologram", None)
    sc.collection.objects.link(root)
    glow = VK.emission_material("Holo_line", (0.35, 0.75, 1.0), 4.0)
    e = 0.008                                                       # line thickness
    def frame_box(cx, cy, cz, sx, sy, sz):                          # the 12 edges of a box
        out = []
        for dx in (-sx / 2, sx / 2):
            for dy in (-sy / 2, sy / 2):
                out.append(((cx + dx, cy + dy, cz), (e, e, sz), 0))
        for dy in (-sy / 2, sy / 2):
            for dz in (-sz / 2, sz / 2):
                out.append(((cx, cy + dy, cz + dz), (sx, e, e), 0))
        for dx in (-sx / 2, sx / 2):
            for dz in (-sz / 2, sz / 2):
                out.append(((cx + dx, cy, cz + dz), (e, sy, e), 0))
        return out
    lines = []
    if c.get("model", "lever_gate") == "lever_gate":                # posts, a stone gate panel, the lever beam on its pivot
        for x in (-0.16, 0.16):
            lines += frame_box(x, 0, 0.12, 0.03, 0.03, 0.24)
        lines += frame_box(0.0, 0, 0.08, 0.26, 0.02, 0.14)
        lines += frame_box(0.04, 0, 0.27, 0.42, 0.02, 0.02) + frame_box(-0.06, 0, 0.245, 0.03, 0.03, 0.03)
        lines += [((0.0, 0, 0.0), (0.46, 0.18, e), 0)]               # the drawing's ground line
    holo = VK.mesh_obj("HologramLines", lines, [glow], parent=root)
    vis = c.get("visible", [-1e9, 1e9])
    x0, y0, z0 = c["at"]
    for f in range(nf):
        t = f / fps
        k = 0.0
        if vis[0] <= t <= vis[1]:
            k = C.smooth((t - vis[0]) / 0.35) * C.smooth((vis[1] - t) / 0.35)
        root.location = (x0, y0, z0 + 0.12 * k)                     # lifts off the page...
        root.rotation_euler = (0, 0, math.radians(c.get("yaw", 0.0)) + 0.9 * max(0.0, t - vis[0]))   # ...turning slowly
        s_ = max(k, 1e-3) if k > 0 else 0.0
        root.scale = (s_ * 1.4, s_ * 1.4, s_ * 1.4)
        _key(root, "location", "rotation_euler", "scale", f=f)
    return root
