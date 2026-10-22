"""Block Lab: build the Blender scene for the active story (build/plan.json) and key every frame.

    blender -b -P bl_scene.py [-- --preview 60 300 ...]     |   python3 bl_scene.py  (bpy module)
Writes build/blocklab.blend and build/anchors.json.
"""
import json
import math
import os
import random
import sys

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C
import bl_world as BW
import bl_perform as PF
import voxelkit as VK
from voxelkit import aim, cl, rx, ry, rz, smooth, smoother, two_bone

P = C.load_plan()
FPS, NF, B = P["fps"], P["nf"], P["block"]
W_PX, H_PX = P["w"], P["h"]
HIDE = Vector((0, 0, -6))
JAW_DROP = 0.04
rnd = random.Random(11)
PALETTE = {                                    # (dark, light) texel colours
    "sandstone": ((0.66, 0.50, 0.29), (0.90, 0.76, 0.50)),
    "stone": ((0.36, 0.37, 0.39), (0.62, 0.63, 0.65)),
    "wood": ((0.36, 0.22, 0.11), (0.58, 0.40, 0.22)),
    "brick": ((0.46, 0.14, 0.09), (0.72, 0.30, 0.20)),
    "gold": ((0.70, 0.50, 0.08), (1.00, 0.84, 0.30)),
    "grass": ((0.20, 0.42, 0.14), (0.40, 0.66, 0.26)),
    "blue": ((0.12, 0.28, 0.62), (0.30, 0.52, 0.90)),
    "iron": ((0.27, 0.20, 0.14), (0.47, 0.37, 0.27)),          # Eiffel Tower brown
    "rubber": ((0.05, 0.05, 0.06), (0.15, 0.15, 0.17)),        # tyres
    "red": ((0.55, 0.04, 0.05), (0.86, 0.13, 0.12)),           # car paint
    "steel": ((0.52, 0.55, 0.60), (0.82, 0.85, 0.90)),         # keys, springs, tools
    "planks": ((0.50, 0.33, 0.18), (0.68, 0.48, 0.28)),        # furniture
    "ceramic": ((0.80, 0.76, 0.68), (0.96, 0.93, 0.86)),       # mugs, plates
    "coffee": ((0.13, 0.07, 0.04), (0.24, 0.14, 0.07)),
    "oldwood": ((0.28, 0.25, 0.20), (0.44, 0.40, 0.32)),       # weathered, grey-brown (old machines, fences)
    "darkiron": ((0.15, 0.15, 0.17), (0.30, 0.30, 0.33)),      # hammer heads, tools
    "soil": ((0.24, 0.15, 0.08), (0.38, 0.25, 0.14)),          # tilled garden earth
    "sprout": ((0.24, 0.56, 0.12), (0.46, 0.80, 0.24)),        # young garden plants
    "paper": ((0.80, 0.77, 0.66), (0.96, 0.93, 0.84)),         # old book pages
    "leather": ((0.27, 0.12, 0.07), (0.44, 0.22, 0.12)),       # book covers
    "glass": ((0.55, 0.66, 0.62), (0.78, 0.88, 0.84)),         # jars (opaque voxel glass)
}
GLOW = {"screen": ((0.62, 0.80, 1.0), 2.2), "led": ((1.0, 0.12, 0.08), 8.0), "spark": ((1.0, 0.85, 0.25), 14.0), "flame": ((1.0, 0.62, 0.22), 10.0)}   # emissive extras



def acts(kind):
    return [a for a in P["actions"] if a["type"] == kind]


# ============================================================ scene pieces
def block_material(name, kind, crack=False):
    d, l = PALETTE.get(kind, PALETTE["sandstone"])
    m = VK.pixel_material(name, d, l, B / 16, per_object=True)
    if not crack:
        return m, None
    N, Lk = m.node_tree.nodes, m.node_tree.links
    p = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    vor = N.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 28
    Lk.new(tc.outputs["Object"], vor.inputs["Vector"])
    edge = N.new("ShaderNodeMath"); edge.operation = "LESS_THAN"; edge.inputs[1].default_value = 0.035
    Lk.new(vor.outputs["Distance"], edge.inputs[0])
    amount = N.new("ShaderNodeValue"); amount.name = "Crack"
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    Lk.new(edge.outputs[0], mul.inputs[0]); Lk.new(amount.outputs[0], mul.inputs[1])
    s = N.new("ShaderNodeMath"); s.operation = "MULTIPLY"; s.inputs[1].default_value = 12.0
    Lk.new(mul.outputs[0], s.inputs[0])
    p.inputs["Emission Color"].default_value = (1.0, 0.25, 0.06, 1)
    Lk.new(s.outputs[0], p.inputs["Emission Strength"])
    return m, amount


def block_mesh(name, m, shape=(1, 1, 1)):
    """One block. shape scales it inside its cell (e.g. [1, 1, 0.35] = a plank, [0.15, 0.15, 1] = a rope), top kept flush."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=B * 0.996)
    sx, sy, sz = shape
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, (1 - sz) / 2 * B * 0.996), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=B * 0.03 * min(shape), segments=2, affect="EDGES", profile=0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(m)
    return me


def components(cells):
    """Connected groups of cells (by x/y adjacency within the part) -> list of cell lists."""
    left, out = set(map(tuple, cells)), []
    while left:
        stack, comp = [left.pop()], []
        while stack:
            c = stack.pop()
            comp.append(c)
            for n in ((c[0] + 1, c[1], c[2]), (c[0] - 1, c[1], c[2]), (c[0], c[1] + 1, c[2]), (c[0], c[1] - 1, c[2]),
                      (c[0], c[1], c[2] + 1), (c[0], c[1], c[2] - 1)):
                if n in left:
                    left.remove(n); stack.append(n)
        out.append(comp)
    return out


def key_visible(o, t0, t1):
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for f, v in ((0, 0), (f0 - 1, 0), (f0, 1), (f1, 1), (f1 + 1, 0)):
        if 0 <= f < NF:
            o.scale = (v, v, v)
            o.keyframe_insert("scale", frame=f)
    VK.set_interp(o, "CONSTANT")


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, NF - 1
    exposure = BW.build_world(sc, P)                    # ground, props, sky, sun, weather, animals
    roots, objs, crack_vals = {}, [], {}
    for name, st in P["structures"].items():
        r = bpy.data.objects.new("S_" + name, None)
        sc.collection.objects.link(r)
        r.location = (st["at"][0], st["at"][1], st["at"][2] if len(st["at"]) > 2 else 0.0)
        roots[name] = r
        m, _ = block_material("M_" + name, st["material"])
        me = block_mesh("Block_" + name, m, st["block_shape"])
        crack_cells, me_c = set(), None
        for a in acts("crack"):
            if a["target"] == name:
                crack_cells |= set(map(tuple, st["parts"][a["part"]]))
                mc, val = block_material("MC_" + name, st["material"], crack=True)
                me_c = block_mesh("CrackBlock_" + name, mc, st["block_shape"])
                crack_vals[name] = (val, a)
        for b in [b for b in P["blocks"] if b["struct"] == name]:
            o = bpy.data.objects.new("%s_%d_%d_%d" % ((name,) + tuple(b["cell"])), me_c if tuple(b["cell"]) in crack_cells else me)
            sc.collection.objects.link(o)
            o.parent = r
            o.rotation_mode = "XYZ"
            o["settle_frame"], o["struct"] = b["settle"], name
            pos = Vector(b["pos"])
            if b["prebuilt"]:
                o.location = pos
            else:
                o.location = HIDE; o.keyframe_insert("location", frame=0)
                if b["appear"] > 1:
                    o.keyframe_insert("location", frame=b["appear"] - 1)
                o.location = pos + Vector((0, 0, 0.35 * B)); o.keyframe_insert("location", frame=b["appear"])
                o.location = pos + Vector((0, 0, 0.08 * B)); o.keyframe_insert("location", frame=b["appear"] + 1)
                o.location = pos; o.keyframe_insert("location", frame=b["settle"])
            if b.get("vanish"):
                v = b["vanish"]
                o.location = pos; o.keyframe_insert("location", frame=v - 1)
                o.location = pos + Vector((0, 0, 0.3 * B)); o.keyframe_insert("location", frame=v)
                o.location = HIDE; o.keyframe_insert("location", frame=v + 1)
            objs.append((o, b))
        if st["extras"]:                                # decor boxes that ride on the structure: [{"c", "s", "m"}]
            names = sorted({e["m"] for e in st["extras"]})
            mats = [VK.emission_material("X_%s_%s" % (name, m_), *GLOW[m_]) if m_ in GLOW else block_material("X_%s_%s" % (name, m_), m_)[0]
                    for m_ in names]
            VK.mesh_obj("X_" + name, [(tuple(e["c"]), tuple(e["s"]), names.index(e["m"])) for e in st["extras"]], mats,
                        parent=r, coll=sc.collection)
        if st["eyes"]:                                  # two eyes on the front of the top row
            eye_m = VK.mat("Eye_" + name, (0.03, 0.03, 0.04), 0.3)
            top = max(c[2] for c in st["cells"])
            front = min(c[1] for c in st["cells"] if c[2] == top)
            row = sorted([c for c in st["cells"] if c[2] == top and c[1] == front], key=lambda c: c[0])
            hb = [(o, b) for o, b in objs if b["struct"] == name and tuple(b["cell"]) in set(map(tuple, row))]
            hb.sort(key=lambda ob: ob[1]["cell"][0])
            if len(hb) == 1:
                for ex in (-0.22 * B, 0.22 * B):
                    VK.mesh_obj("eye", [((ex, -0.51 * B, 0.08 * B), (0.16 * B, 0.04 * B, 0.2 * B), 0)], [eye_m], parent=hb[0][0])
            else:
                mid = len(hb) // 2
                for (o, b), ex in ((hb[mid - 1], 0.2 * B), (hb[mid], -0.2 * B)):
                    VK.mesh_obj("eye", [((ex, -0.51 * B, -0.3 * B), (0.3 * B, 0.04 * B, 0.35 * B), 0)], [eye_m], parent=o)
    # highlight rings (cross-sections)
    glow = VK.emission_material("Highlight", (0.25, 0.85, 1.0), 6.0)
    for a in acts("highlight"):
        st = P["structures"][a["target"]]
        for comp in components(st["parts"][a["part"]]):
            xs = [c[0] for c in comp]; ys = [c[1] for c in comp]; zs = [c[2] for c in comp]
            p0 = Vector(C.local_pos((min(xs), min(ys), min(zs)), st["cells"], st["centered"]))
            p1 = Vector(C.local_pos((max(xs), max(ys), max(zs)), st["cells"], st["centered"]))
            cx, cy, cz = (p0.x + p1.x) / 2, (p0.y + p1.y) / 2, (p0.z + p1.z) / 2
            w, d = (max(xs) - min(xs) + 1) * B * 1.12, (max(ys) - min(ys) + 1) * B * 1.12
            t, h = max(w, d) * 0.08, 0.012 * (1 + 0.3 * (len(comp) > 2))
            boxes = [((0, d / 2, 0), (w + t, t, h), 0), ((0, -d / 2, 0), (w + t, t, h), 0),
                     ((w / 2, 0, 0), (t, d + t, h), 0), ((-w / 2, 0, 0), (t, d + t, h), 0)]
            o = VK.mesh_obj("ring_" + a["target"], boxes, [glow], parent=roots[a["target"]])
            o.location = (cx, cy, cz)
            key_visible(o, a["t0"], a["t1"])
    for name, (val, a) in crack_vals.items():
        val.outputs[0].default_value = 0.0
        val.outputs[0].keyframe_insert("default_value", frame=0)
        val.outputs[0].keyframe_insert("default_value", frame=int(a["t0"] * FPS))
        val.outputs[0].default_value = 1.0
        val.outputs[0].keyframe_insert("default_value", frame=int(a["t1"] * FPS))
        if a.get("c0") is not None:                             # "cool_from" / "cool_until": the glow fades away again
            val.outputs[0].keyframe_insert("default_value", frame=int(a["c0"] * FPS))
            val.outputs[0].default_value = 0.0
            val.outputs[0].keyframe_insert("default_value", frame=int(a["c1"] * FPS))

    arm = VK.build_grandpa(sc, None, P["outfit"])
    dust_m = VK.pixel_material("Dust", (0.80, 0.66, 0.46), (0.93, 0.82, 0.62), 0.05)
    cube = bpy.data.meshes.new("Puff")
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(cube); bm.free()
    cube.materials.append(dust_m)
    puffs = []
    for k in range(46 * len(acts("collapse"))):
        o = bpy.data.objects.new("dust_%02d" % k, cube)
        sc.collection.objects.link(o)
        puffs.append(o)

    cam_d = bpy.data.cameras.new("Camera")
    cam_d.lens, cam_d.sensor_fit, cam_d.sensor_width, cam_d.clip_start = 35, "HORIZONTAL", 36, 0.05
    cam = bpy.data.objects.new("Camera", cam_d)
    cam.rotation_mode = "QUATERNION"
    sc.collection.objects.link(cam)
    sc.camera = cam
    r = sc.render
    r.engine = "CYCLES"
    r.resolution_x, r.resolution_y, r.resolution_percentage = W_PX, H_PX, 100
    r.image_settings.file_format = "PNG"
    r.use_persistent_data = True
    cy = sc.cycles
    cy.device, cy.samples, cy.adaptive_threshold = "CPU", 16, 0.05
    cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
    cy.denoising_quality, cy.denoising_prefilter = "FAST", "FAST"
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 2, 1, 0
    cy.transmission_bounces = cy.transparent_max_bounces = cy.volume_bounces = 0
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "Medium High Contrast"
    sc.view_settings.exposure = exposure
    animate(sc, arm, roots, objs, puffs, cam)
    return sc


# ============================================================ animation
def cam_at(t):
    keys = P["camera"] or [dict(t=0.0, target=[0, 0.1, 0.4], az=-60, el=20, dist=3.0)]
    if t <= keys[0]["t"]:
        k0 = k1 = keys[0]; u = 0.0
    else:
        k0 = k1 = keys[-1]; u = 0.0
        for a, b in zip(keys, keys[1:]):
            if a["t"] <= t <= b["t"]:
                k0, k1, u = a, b, smoother((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
                break
    lerp = lambda p, q: p + (q - p) * u
    tgt = Vector(k0["target"]).lerp(Vector(k1["target"]), u)
    az, el = math.radians(lerp(k0["az"], k1["az"])), math.radians(lerp(k0["el"], k1["el"]))
    d = k0["dist"] * (k1["dist"] / k0["dist"]) ** u
    eye = tgt + d * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    for a in acts("collapse"):
        tc = a["t0"]
        if tc <= t < tc + 0.9:
            k = math.exp(-(t - tc) * 4.5)
            eye += Vector((math.sin(t * 57), math.sin(t * 43), math.sin(t * 51))) * 0.05 * k
    return eye, tgt


MOTIONS = ("slide", "spin", "swing", "fly")
AXES = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}


def motion_pivot(a):
    """Pivot in the structure's own (unscaled) frame: centre of block 'pivot' [x,y,z], else the structure's centroid."""
    st = P["structures"][a["target"]]
    if a.get("pivot") is not None:
        return Vector(C.local_pos(a["pivot"], st["cells"], st["centered"]))
    ps = [Vector(C.local_pos(c, st["cells"], st["centered"])) for c in st["cells"]]
    return sum(ps, Vector()) / len(ps)


def motion_offset(name, t, local=False):
    """World offset of a structure; local=True: the slides marked \"local\", which turn with its spins and swings."""
    off = Vector()
    for a in acts("slide"):
        if a["target"] == name and bool(a.get("local")) == local:
            off += Vector(a["by"]) * smoother((t - a["t0"]) / max(1e-6, a["t1"] - a["t0"]))
    if local:
        return off
    for a in acts("fly"):
        if a["target"] == name:
            off += Vector(C.fly_offset(a, t))
    return off


def motion_rotation(name, t):
    R = Matrix.Identity(4)
    for a in acts("spin") + acts("swing") + acts("trip"):
        if a["target"] == name:
            p = motion_pivot(a)
            R = R @ Matrix.Translation(p) @ Matrix.Rotation(math.radians(C.motion_angle(a, t)), 4, AXES[a.get("axis", "z")]) @ Matrix.Translation(-p)
    return R


def set_bone(pbone, rest4, f, off=(0, 0, 0), R3=None, S=(1, 1, 1)):
    """Pose a face bone by a change D given in the rig's rest space about the bone's head: basis = rest^-1 @ D @ rest."""
    h = rest4.translation
    Sm = Matrix.Diagonal((S[0], S[1], S[2], 1.0))
    D = Matrix.Translation(Vector(off) + h) @ (R3 or Matrix.Identity(3)).to_4x4() @ Sm @ Matrix.Translation(-h)
    loc, rot, sca = (rest4.inverted() @ D @ rest4).decompose()
    pbone.location, pbone.rotation_quaternion, pbone.scale = loc, rot, sca
    for path in ("location", "rotation_quaternion", "scale"):
        pbone.keyframe_insert(path, frame=f)


def set_face(pb, rest, c, f):
    """bl_perform face channels -> brows (raise, tilt), pupils (gaze), eyelids (blink / squint), cheeks and smile."""
    for sd, sign in (("R", -1), ("L", 1)):
        up = 0.008 * cl(c["brow"] + c["brow_" + sd], -1.2, 1.2)
        set_bone(pb["brow." + sd], rest["brow." + sd], f, (0, 0, up), Matrix.Rotation(sign * 0.30 * cl(c["tilt"], -1, 1), 3, "Y"))
        set_bone(pb["pupil." + sd], rest["pupil." + sd], f, (0.008 * cl(c["gx"], -1, 1), 0, 0.005 * cl(c["gz"], -1, 1)))
        set_bone(pb["lid." + sd], rest["lid." + sd], f, S=(1, 1, 1 + 19 * cl(c["lid"], 0, 1)))
    sm = cl(c["smile"], -1, 1)
    set_bone(pb["cheeks"], rest["cheeks"], f, (0, 0, 0.007 * max(sm, 0)))
    set_bone(pb["smile"], rest["smile"], f, (0, 0, 0.003 * sm), S=(1 + (0.5 if sm > 0 else 0.25) * sm, 1, 1 + 0.4 * max(sm, 0)))


def write_continuity(arm, roots, cam, perf_log):
    """The state the next scene starts from: grandpa (place, facing, pose, face), every structure, camera, overlay.
    (Roots have no parent, so matrix_basis is their world matrix -- and, unlike matrix_world, it is current here.)"""
    last = perf_log[-1]
    st = {}
    for name, r in roots.items():
        mine = [b for b in P["blocks"] if b["struct"] == name]
        st[name] = dict(root=[list(map(lambda v: round(v, 5), row)) for row in r.matrix_basis], material=P["structures"][name]["material"],
                        blocks_standing=sum(1 for b in mine if not b.get("vanish")), blocks=len(mine))
    live = [c for c in P["cards"] if c.get("style") == "live"]
    t_end = (NF - 1) / FPS
    carried = {}                                                  # what he is holding at the end, and in which hand
    for name in {a["target"] for a in PF.holds(P)}:
        ha = PF.active_hold(P, name, t_end)
        if ha is not None and ha.get("hand") != "none" and PF.hold_weight(ha, t_end) > 0.5:
            carried[name] = ha.get("hand", "R")
    stream_cam = None
    if "webcam" in roots:                                         # Rule 2: where the stream camera is
        w = roots["webcam"].matrix_basis.translation
        stream_cam = dict(state="carried", hand=carried["webcam"]) if "webcam" in carried else \
            dict(state="set_down", at=[round(v, 4) for v in w])
    out = dict(scene=P.get("scene", {}), slug=P["slug"], fps=FPS, frames=NF, film=P["film"], seed=P.get("seed", 11),
               world=P["world"], outfit=P["outfit"],
               grandpa=dict(root=[round(v, 4) for v in last["root"]], yaw_deg=round(math.degrees(last["yaw"]), 2),
                            hips=[round(v, 4) for v in last["hips"]], body=last["body"], face=last["face"],
                            wrist_R=[round(v, 4) for v in last["wrist_R"]], wrist_L=[round(v, 4) for v in last["wrist_L"]]),
               structures=st, camera=dict(eye=[round(v, 4) for v in cam.location],
                                          last_key={k: v for k, v in P["camera"][-1].items() if k != "t"} if P["camera"] else None),
               holding=carried, stream_cam=stream_cam,
               overlay=dict(live_viewers=live[-1]["viewers"][-1][1] if live and live[-1].get("viewers") else None),
               audio=dict(ambience=P["world"].get("interior", "none"), last_line=P["lines"][-1]["id"] if P["lines"] else None))
    json.dump(out, open(os.path.join(C.BUILD, "continuity.json"), "w"), indent=1)
    json.dump(perf_log, open(os.path.join(C.BUILD, "perf.json"), "w"))


def collapse_plan(objs):
    plan = {}
    for a in acts("collapse"):
        tc = a["t0"]
        for o, b in objs:
            if b["struct"] != a["target"]:
                continue
            p0 = Vector(b["pos"])
            k = b["cell"][2]
            delay = 0.03 * k + rnd.uniform(0, 0.06)
            out = Vector((rnd.gauss(0, 0.09) + p0.x * 0.4, rnd.gauss(0, 0.09), 0))
            rest_z = 0.05 + max(0.0, 0.22 - 0.5 * (abs(p0.x + out.x) + abs(p0.y + out.y))) * rnd.uniform(0.4, 1.0)
            rest = Vector((p0.x + out.x, p0.y + out.y, min(rest_z, p0.z)))      # rubble never rises
            rot = Euler((rnd.uniform(-1.2, 1.2), rnd.uniform(-1.2, 1.2), rnd.uniform(-0.6, 0.6)))
            plan[o.name] = (tc + delay, p0, rest, rot, a["target"])
    for a in acts("melt"):                                     # straight down into a flat slab, bottom blocks first
        st, tgt = P["structures"][a["target"]], P["melt"][a["target"]]
        for o, b in objs:
            if b["struct"] == a["target"]:
                rest = Vector(C.local_pos(tgt[str(b["id"])], st["cells"], st["centered"]))
                plan[o.name] = (a["t0"] + 0.025 * b["cell"][2] + rnd.uniform(0, 0.05), Vector(b["pos"]), rest, Euler((0, 0, 0)), a["target"])
    return plan


def animate(sc, arm, roots, objs, puffs, cam):
    path, phase, amp = P["path"], P["phase"], P["amp"]
    blocks = P["blocks"]
    S = P["structures"]
    pb = arm.pose.bones
    rest = {b_.name: b_.matrix_local.copy() for b_ in arm.data.bones}
    for p in pb:
        p.rotation_mode = "QUATERNION"
    arm.rotation_mode = "XYZ"
    grows = acts("grow")
    moving = {a["target"] for a in P["actions"] if a["type"] in MOTIONS + ("hold", "trip")}
    for r in roots.values():
        r.rotation_mode = "QUATERNION"
    plan = collapse_plan(objs)
    scale_at = {}
    # focus windows: what grandpa faces / looks at
    focus_acts = [a for a in P["actions"] if a["type"] in ("face_camera", "build", "point", "look", "grow", "crack", "collapse", "melt") + MOTIONS]
    for i, a in enumerate(focus_acts):
        a["_t1"] = a["t1"] if a["type"] in ("face_camera", "build", "point", "look") + MOTIONS else \
            (focus_acts[i + 1]["t0"] if i + 1 < len(focus_acts) else P["film"])
    yaw_prev = 0.0
    look_point = lambda a: Vector(a["pos"]) if a.get("pos") else roots[a["obj"]].matrix_world @ Vector(a.get("off", (0, 0, 0)))
    blink_times = PF.blinks(P)
    face_rest = {n: arm.data.bones[n].matrix_local.copy() for n in VK.FACE_ORDER}
    perf_log = []
    BREATH = P["film"] / max(1, round(P["film"] / 3.2)) if P.get("loop") else 3.2   # a loop breathes a whole number of times
    for f in range(NF):
        t = f / FPS
        # ---- structures: grow (scale about the base, optionally moving), slide / spin / swing, collapse
        for name, r in roots.items():
            base = Vector((S[name]["at"][0], S[name]["at"][1], S[name]["at"][2] if len(S[name]["at"]) > 2 else 0.0))
            loc, s = base, 1.0
            for g in grows:                                     # several grows on one structure multiply in order
                if g["target"] != name:
                    continue
                u = smoother((t - g["t0"]) / max(1e-6, g["t1"] - g["t0"]))
                if g.get("to"):
                    loc = loc.lerp(Vector((g["to"][0], g["to"][1], 0)), u)
                s *= 1 + (g["factor"] - 1) * u
            M = (Matrix.Translation(loc + motion_offset(name, t)) @ Matrix.Rotation(math.radians(S[name]["yaw"]), 4, "Z")
                 @ Matrix.Scale(s, 4) @ motion_rotation(name, t)
                 @ Matrix.Translation(motion_offset(name, t, local=True)))
            r.matrix_basis = M
            scale_at[name] = s
            if grows or name in moving:
                r.keyframe_insert("location", frame=f); r.keyframe_insert("scale", frame=f)
                r.keyframe_insert("rotation_quaternion", frame=f)
        for o, b in objs:
            pl = plan.get(o.name)
            if not pl or t < pl[0] - 2 / FPS:
                continue
            ts, p0, pr, rot, tgt_name = pl
            g_local = 9.81 / max(1.0, scale_at[tgt_name]) * 0.8
            tau = max(0.0, t - ts)
            h = p0.z - pr.z
            tf = math.sqrt(2 * max(1e-6, h) / g_local)
            v = min(1.0, tau / tf) if h > 1e-6 else min(1.0, tau / 0.4)
            z = max(pr.z, p0.z - 0.5 * g_local * tau * tau)
            bounce = 0.02 * math.exp(-(tau - tf) * 9) * abs(math.sin((tau - tf) * 18)) if tau > tf else 0.0
            o.location = Vector((p0.x + (pr.x - p0.x) * smooth(v), p0.y + (pr.y - p0.y) * smooth(v), z + bounce))
            o.rotation_euler = Euler((rot.x * smooth(v), rot.y * smooth(v), rot.z * smooth(v)))
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_euler", frame=f)

        # ---- grandpa: what is he doing?
        x, y, zg = path[f]                                     # zg: standing height (ground, scaffold or ladder)
        vz = (path[min(NF - 1, f + 1)][2] - path[max(0, f - 1)][2]) * FPS / 2
        c_w = smooth((abs(vz) - 0.05) / 0.15)                   # climbing weight: moving up or down a ladder
        phc = 2 * math.pi * zg / 0.24                           # one hand-over-hand cycle every two rungs
        r_sw, aimp = 0.0, None
        for sw in P["swings"]:
            if sw["s"] - 0.05 <= t <= sw["e"] + 0.05:
                uu = (t - sw["s"]) / (sw["e"] - sw["s"])
                r_sw = smooth(uu / 0.22) * (1 - smooth((uu - 0.80) / 0.20))
                pa = Vector(roots[sw["target"]].location) + Vector(blocks[sw["ids"][0]]["pos"]) * scale_at[sw["target"]]
                pbb = Vector(roots[sw["target"]].location) + Vector(blocks[sw["ids"][-1]]["pos"]) * scale_at[sw["target"]]
                aimp = pa.lerp(pbb, cl((uu - 0.22) / 0.58))
        for a in acts("point"):
            w_pt = smooth((t - a["t0"]) / 0.4) * (1 - smooth((t - (a["t1"] - 0.4)) / 0.4))
            if w_pt > 0:
                if a.get("pos"):
                    aimp = Vector(a["pos"])
                else:
                    off = Vector(a.get("offset", [0, 0, 0.2]))
                    aimp = Vector(roots[a["target"]].location) + off * scale_at[a["target"]]
                aimp = aimp + Vector((0, 0, 0.02 * math.sin(t * 5)))
                r_sw = max(r_sw, w_pt) if aimp is not None else r_sw
        w_sh = max([smooth((t - a["t0"]) / 0.3) * (1 - smooth((t - (a["t1"] - 0.35)) / 0.35)) for a in acts("shrug")] + [0.0])
        pch, phands = PF.body_at(P, t)                          # performance layer: timed poses
        w_sh = max(w_sh, pch["shrug"])
        startle = max([smooth((t - a["t0"]) / 0.15) * (1 - smooth((t - a["t0"] - 0.9) / 0.6)) for a in acts("collapse")] + [0.0])
        active = [a for a in focus_acts if a["t0"] <= t <= a["_t1"]]
        fa = active[-1] if active else None
        eye_now = Vector(cam_at(t)[0])
        if fa is None:
            focus = Vector((x, y - 1, 0))
        elif fa["type"] == "face_camera":
            focus = eye_now
        elif fa["type"] in ("build",):
            focus = Vector(roots[fa["target"]].location)
        elif fa["type"] == "point":
            focus = Vector(fa["pos"]) if fa.get("pos") else Vector(roots[fa["target"]].location)
        elif fa["type"] == "look":                              # body: false -> only the head turns (e.g. seated)
            focus = look_point(fa) if fa.get("body", True) else Vector((x, y, 0)) + rz(yaw_prev) @ Vector((0, -1, 0))
        else:
            focus = Vector(roots[fa["target"]].location)
        walking = [a for a in acts("move") if a.get("face") == "path" and a["t0"] <= t <= a["t1"]]
        if walking:                                             # walking somewhere: the body faces the way he is going
            ahead = path[min(NF - 1, f + 12)]
            if math.hypot(ahead[0] - x, ahead[1] - y) > 0.03:
                focus = Vector((ahead[0], ahead[1], 0))
        if c_w > 0.3:
            mv = [a for a in acts("move") if a.get("face") and a["t0"] - 0.5 <= t <= a["t1"] + 0.5]
            if mv:
                focus = Vector((mv[-1]["face"][0], mv[-1]["face"][1], zg))
        fx, fy = focus.x - x, focus.y - y
        yaw_t = math.atan2(fx, -fy) if math.hypot(fx, fy) > 0.05 else yaw_prev
        while yaw_t - yaw_prev > math.pi:
            yaw_t -= 2 * math.pi
        while yaw_t - yaw_prev < -math.pi:
            yaw_t += 2 * math.pi
        rate = fa.get("rate", 0.15) if fa is not None and fa["type"] == "look" else 0.15
        yaw = yaw_prev + (yaw_t - yaw_prev) * (rate if f else 1.0)
        yaw_prev = yaw
        Rw = rz(yaw)
        Wroot = Matrix.Translation((x, y, zg)) @ Rw.to_4x4()
        Winv = Wroot.inverted()
        to_char = lambda p: Winv @ p
        arm.location, arm.rotation_euler = (x, y, zg), (0, 0, yaw)
        arm.keyframe_insert("location", frame=f)
        arm.keyframe_insert("rotation_euler", frame=f)
        a_walk = amp[f]
        cyc = 2 * math.pi * phase[f]
        lean = (0.18 + 0.10 * r_sw - 0.16 * startle - 0.06 * w_sh) * (1 - 0.8 * c_w)
        H = Vector((0, 0.03 * startle, 0.46 - 0.010 * a_walk * (1 - math.cos(2 * cyc)) + 0.004 * math.sin(2 * math.pi * t / BREATH)))
        lean += pch["lean"]
        H = H + Vector(pch["hips"])
        twist = 0.0
        if aimp is not None:
            ac = to_char(aimp)
            twist = 0.3 * math.atan2(ac.x, -ac.y) * r_sw
        twist += pch["twist"]
        Qs = rz(twist) @ rx(lean)
        S_R, S_L = H + Qs @ Vector((-0.19, 0, 0.31)), H + Qs @ Vector((0.19, 0, 0.31))
        neck = H + Qs @ Vector((0, 0, 0.36))
        if aimp is not None and r_sw > 0.05:
            look = aimp
        elif fa is not None and fa["type"] in ("grow", "crack", "collapse", "melt"):
            sz = S[fa["target"]]["size"][2] * scale_at[fa["target"]]
            look = Vector(roots[fa["target"]].location) + Vector((0, 0, sz * (0.55 if fa["type"] != "collapse" else 0.2)))
        elif fa is not None and fa["type"] in MOTIONS:
            look = Vector(roots[fa["target"]].location) + motion_pivot(fa) * scale_at[fa["target"]]
        elif fa is not None and fa["type"] == "face_camera":
            look = eye_now
        elif fa is not None and fa["type"] == "look":
            look = look_point(fa)
        else:
            look = focus + Vector((0, 0, 0.3))
        lc = to_char(look) - (neck + Qs @ Vector((0, 0, 0.12)))
        hy = max(-1.1, min(1.1, math.atan2(lc.x, -lc.y)))
        hp = max(-0.6, min(0.45, 0.6 * math.atan2(-lc.z, math.hypot(lc.x, lc.y)))) + 0.12 * w_sh
        hy += pch["head"][0] + pch["shake"] * math.sin(2 * math.pi * 3.2 * t)
        hp += -pch["head"][1] + pch["nod"] * math.sin(2 * math.pi * 2.6 * t)
        Qh = rz(hy) @ rx(hp) @ ry(pch["head"][2])
        mouth_w = Wroot @ (neck + Qh @ Vector((0, -0.14, 0.05)))
        hold_hand = {}
        for name in {a["target"] for a in PF.holds(P)}:        # a held prop follows its keyed path (or his mouth)
            ha = PF.active_hold(P, name, t)
            if ha is None:
                continue
            a0, a1, u, off, rot = PF.hold_key(ha, t)
            where = lambda k_: mouth_w if k_ == "mouth" else (Wroot @ Vector(k_["char"])) if isinstance(k_, dict) else Vector(k_)
            carried = (isinstance(a0, dict)) * (1 - u) + (isinstance(a1, dict)) * u      # char keys turn with his body
            Mh = (Matrix.Translation(where(a0).lerp(where(a1), u) + Vector(off)) @ Matrix.Rotation(yaw * carried, 4, "Z")
                  @ Euler([math.radians(v) for v in rot], "XYZ").to_matrix().to_4x4())
            roots[name].matrix_basis = Mh
            roots[name].keyframe_insert("location", frame=f); roots[name].keyframe_insert("rotation_quaternion", frame=f)
            w_h = PF.hold_weight(ha, t)
            if w_h > 0 and ha.get("hand") != "none":           # "hand": "none" -- a keyed path no hand of his grips
                hold_hand[ha.get("hand", "R")] = (Mh @ Vector(ha.get("grip", (0, 0, 0))), w_h)
        sw_off = 0.06 * a_walk * math.sin(cyc)
        TR = S_R + Vector((0.01, -0.05 - sw_off, -0.405))
        TL_ = S_L + Vector((-0.01, -0.05 + sw_off, -0.405))
        poleR, poleL = Vector((-0.4, 1.0, 0.0)), Vector((0.4, 1.0, 0.0))
        if aimp is not None and r_sw > 0:
            ac = to_char(aimp)
            TR = TR.lerp(S_R + (ac - S_R).normalized() * (VK.L_UP + VK.L_FORE - 0.01), r_sw)
        shR, shL = H + Qs @ Vector((-0.30, -0.14, 0.30)), H + Qs @ Vector((0.30, -0.14, 0.30))
        TR, TL_ = TR.lerp(shR, w_sh), TL_.lerp(shL, w_sh)
        poleR, poleL = poleR.lerp(Vector((-1, 0.2, -0.6)), w_sh), poleL.lerp(Vector((1, 0.2, -0.6)), w_sh)
        upR, upL = H + Qs @ Vector((-0.22, -0.16, 0.48)), H + Qs @ Vector((0.22, -0.16, 0.48))
        TR, TL_ = TR.lerp(upR, startle * 0.7), TL_.lerp(upL, startle * 0.7)
        if "hammer" in P["outfit"]["extras"] and r_sw > 0:       # little hammer taps while placing
            TR = TR + Vector((0, 0, 0.03 * abs(math.sin(2 * math.pi * 3.5 * t)))) * r_sw
        if c_w > 0:                                             # hand over hand on the rungs in front of him
            rungR = S_R + Vector((0.02, -0.17, 0.12 + 0.07 * math.sin(phc)))
            rungL = S_L + Vector((-0.02, -0.17, 0.12 - 0.07 * math.sin(phc)))
            TR, TL_ = TR.lerp(rungR, c_w), TL_.lerp(rungL, c_w)
        if pch["elbows"] > 0:                                  # elbows out and up (arms resting on a table)
            poleR = poleR.lerp(Vector((-0.8, 0.5, 0.6)), pch["elbows"]); poleL = poleL.lerp(Vector((0.8, 0.5, 0.6)), pch["elbows"])
        for sd, specs in phands.items():                       # posed hands, then a hand holding something
            for spec, w_p in specs:
                if "obj" in spec:
                    tg = to_char(roots[spec["obj"]].matrix_world @ Vector(spec.get("off", (0, 0, 0))))
                elif "world" in spec:
                    tg = to_char(Vector(spec["world"]))
                else:
                    tg = Vector(spec["char"])
                if spec.get("tap"):
                    tg = tg + Vector((0, 0, spec["tap"][1] * abs(math.sin(math.pi * spec["tap"][0] * t))))
                if spec.get("wave"):                           # [Hz, metres]: a side-to-side wave
                    tg = tg + Vector((spec["wave"][1] * math.sin(2 * math.pi * spec["wave"][0] * t), 0, 0))
                if sd == "R":
                    TR = TR.lerp(tg, w_p)
                else:
                    TL_ = TL_.lerp(tg, w_p)
        for sd, (gw, w_h) in hold_hand.items():
            if sd == "R":
                TR = TR.lerp(to_char(gw), w_h)
            else:
                TL_ = TL_.lerp(to_char(gw), w_h)
        E_R, W_R, _ = two_bone(S_R, TR, VK.L_UP, VK.L_FORE, poleR)
        E_L, W_L, _ = two_bone(S_L, TL_, VK.L_UP, VK.L_FORE, poleL)
        fn = min(NF - 1, f + 1)
        vel = Vector((path[fn][0] - path[max(0, fn - 2)][0], path[fn][1] - path[max(0, fn - 2)][1], 0))
        vc = Rw.inverted() @ vel
        vdir = vc.normalized() if vc.length > 1e-6 else Vector((0, -1, 0))
        feet = {}
        for s_, xo, off in (("R", -0.07, 0.0), ("L", 0.07, 0.5)):
            ph = cyc + 2 * math.pi * off
            p = Vector((xo, 0.0, 0.0)) + vdir * (C.STRIDE / 2 * -math.cos(ph) * a_walk)
            feet[s_] = p + Vector((0, 0, 0.05 * a_walk * max(0.0, math.sin(ph))))
            if c_w > 0:                                         # alternate feet stepping up the rungs
                step = 0.07 * max(0.0, math.sin(phc + (0 if s_ == "R" else math.pi)))
                feet[s_] = feet[s_].lerp(Vector((xo, -0.06, step)), c_w)
        hipR, hipL = H + Vector((-0.07, 0, 0)), H + Vector((0.07, 0, 0))
        K_R, F_R, _ = two_bone(hipR, feet["R"], VK.L_THIGH, VK.L_SHIN, Vector((0, -1, 0.2)))
        K_L, F_L, _ = two_bone(hipL, feet["L"], VK.L_THIGH, VK.L_SHIN, Vector((0, -1, 0.2)))
        Qid, dn = Matrix.Identity(3), Vector((0, 0, -1))
        Qu_R = aim(Qs, dn, E_R - S_R); Qf_R = aim(Qu_R, dn, W_R - E_R)
        Qu_L = aim(Qs, dn, E_L - S_L); Qf_L = aim(Qu_L, dn, W_L - E_L)
        Qt_R = aim(Qid, dn, K_R - hipR); Qn_R = aim(Qt_R, dn, F_R - K_R)
        Qt_L = aim(Qid, dn, K_L - hipL); Qn_L = aim(Qt_L, dn, F_L - K_L)
        mouth = P["mouth"][min(f, len(P["mouth"]) - 1)]
        want = {"hips": (H, Qid), "spine": (H, Qs), "head": (neck, Qh),
                "jaw": (neck + Qh @ Vector((0, -0.1, 0.04 - JAW_DROP * mouth)), Qh),
                "upper_arm.R": (S_R, Qu_R), "forearm.R": (E_R, Qf_R), "upper_arm.L": (S_L, Qu_L), "forearm.L": (E_L, Qf_L),
                "thigh.R": (hipR, Qt_R), "shin.R": (K_R, Qn_R), "thigh.L": (hipL, Qt_L), "shin.L": (K_L, Qn_L)}
        Mw = {}
        for name in VK.BONE_ORDER:
            p_, Q = want[name]
            M = Matrix.Translation(p_) @ (Q @ rest[name].to_3x3()).to_4x4()
            Mw[name] = M
            par = arm.data.bones[name].parent
            basis = ((Mw[par.name] @ rest[par.name].inverted() @ rest[name]).inverted() @ M) if par else rest[name].inverted() @ M
            loc, rot, _ = basis.decompose()
            pb[name].location, pb[name].rotation_quaternion = loc, rot
            pb[name].keyframe_insert("location", frame=f)
            pb[name].keyframe_insert("rotation_quaternion", frame=f)
        fc_ = PF.face_at(P, t, blink_times)                     # face: brows, eyelids, gaze, smile (head-space offsets)
        set_face(pb, face_rest, fc_, f)
        perf_log.append(dict(f=f, root=[x, y, zg], yaw=yaw, hips=list(Wroot @ Mw["hips"].translation), face=fc_,
                             wrist_R=list(Wroot @ W_R), wrist_L=list(Wroot @ W_L), body=pch))
        eye, tgt = cam_at(t)
        cam.location, cam.rotation_quaternion = eye, (tgt - eye).to_track_quat("-Z", "Y")
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)

    k = 0
    for a in acts("collapse"):
        st, tc = S[a["target"]], a["t0"]
        sc_ = scale_at[a["target"]]
        base = Vector(roots[a["target"]].location)
        for _ in range(46):
            o = puffs[k]; k += 1
            ts = tc + 0.15 + rnd.uniform(0, 0.9)
            f0 = int(ts * FPS)
            src = base + Vector((rnd.uniform(-0.6, 0.6) * st["size"][0] * sc_, rnd.uniform(-0.6, 0.6) * max(0.2, st["size"][1]) * sc_, 0.1))
            size = rnd.uniform(0.18, 0.45) * min(1.0, sc_ / 5)
            o.rotation_euler = (rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0, 3))
            for fk, loc, s_ in ((0, src, 0), (f0 - 1, src, 0), (f0, src, size * 0.3),
                                (f0 + 12, src + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0.35)), size),
                                (f0 + 40, src + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), 0.7)), 0)):
                if 0 <= fk < NF:
                    o.location, o.scale = loc, (s_, s_, s_)
                    o.keyframe_insert("location", frame=fk); o.keyframe_insert("scale", frame=fk)
    for o, b in objs:
        for fc in VK.fcurves_of(o):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT" if ((not b["prebuilt"] and int(round(kp.co.x)) in (0, b["appear"] - 1))
                                                  or int(round(kp.co.x)) == b.get("vanish", -9)) else "LINEAR"
    for o in [arm, cam] + list(roots.values()) + puffs:
        VK.set_interp(o, "LINEAR")
    write_continuity(arm, roots, cam, perf_log)

    # ---- screen anchors for the overlay
    pts = {"grandpa": lambda: arm.matrix_world @ arm.pose.bones["head"].tail}
    for name, st in S.items():
        hz = st["size"][2]
        if st["centered"]:
            fc = Vector((0, 0, 0))
        else:                                                     # footprint centre of a corner-anchored structure
            xs, ys = [c[0] for c in st["cells"]], [c[1] for c in st["cells"]]
            fc = Vector(((min(xs) + max(xs)) / 2 * B, (min(ys) + max(ys)) / 2 * B, 0))
        pts[name + ":top"] = (lambda r=roots[name], hz=hz, fc=fc: r.matrix_world @ (fc + Vector((0, 0, hz + 0.05))))
        pts[name + ":center"] = (lambda r=roots[name], hz=hz, fc=fc: r.matrix_world @ (fc + Vector((0, 0, hz * 0.5))))
        for pn, cells in st["parts"].items():
            if not cells:
                continue
            comp = sorted(components(cells), key=lambda c: -sum(cc[0] for cc in c) / len(c))[0]
            ctr = sum((Vector(C.local_pos(c, st["cells"], st["centered"])) for c in comp), Vector()) / len(comp)
            front = ctr + Vector((0, -st["size"][1] / 2 - 0.01, 0))
            pts["%s:part:%s" % (name, pn)] = (lambda r=roots[name], p=front: r.matrix_world @ p)
    anchors = {}
    for f in range(NF):
        sc.frame_set(f)
        a = {}
        for k_, fn_ in pts.items():
            v = world_to_camera_view(sc, cam, fn_())
            a[k_] = [round(v.x * W_PX, 1), round((1 - v.y) * H_PX, 1), 1 if v.z > 0 else 0]
        anchors[f] = a
    json.dump(anchors, open(os.path.join(C.BUILD, "anchors.json"), "w"))


def preview(frames, scale=25, samples=8):
    sc = bpy.context.scene
    sc.render.resolution_percentage, sc.cycles.samples = scale, samples
    os.makedirs(os.path.join(C.BUILD, "previews"), exist_ok=True)
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(C.BUILD, "previews", "%04d.png" % f)
        bpy.ops.render.render(write_still=True)
    sc.render.resolution_percentage, sc.cycles.samples = 100, 16


if __name__ == "__main__":
    build_scene()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(C.BUILD, "blocklab.blend"))
    if "--preview" in sys.argv:
        preview([int(a) for a in sys.argv[sys.argv.index("--preview") + 1:]])
