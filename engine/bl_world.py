"""Block Lab: the world around the lesson -- ground style, sky / time of day, weather and a few block animals.

Story:  "world": {"ground": "grass", "time": "sunset", "weather": "clouds", "animals": ["birds", "cat"]}
Everything is voxels. Every loop (rain, snow, birds, wings, cat tail) is cyclic F-curve animation, so any frame
renders the same whatever order the frames are rendered in (resumable renders stay seamless).
"""
import json
import math
import os
import random

import bpy
import bmesh
from mathutils import Vector

import voxelkit as VK

rnd = random.Random(23)
V, R0 = 0.2, 2.7                                   # island voxel size and radius (m)
PROP_SPOTS = ((-2.0, 0.9), (1.9, -1.2), (-1.6, -1.7))

GROUND = {   # top, side and base texel colours (dark, light), plus the props that dress the island
    "desert": (((0.78, 0.60, 0.36), (0.95, 0.82, 0.56)), ((0.62, 0.45, 0.26), (0.80, 0.64, 0.40)),
               ((0.42, 0.30, 0.20), (0.58, 0.44, 0.30)), "cacti"),
    "grass": (((0.22, 0.45, 0.15), (0.40, 0.66, 0.26)), ((0.45, 0.31, 0.18), (0.60, 0.43, 0.26)),
              ((0.40, 0.40, 0.42), (0.55, 0.55, 0.57)), "trees"),
    "snow": (((0.80, 0.85, 0.92), (0.97, 0.98, 1.00)), ((0.50, 0.40, 0.32), (0.66, 0.56, 0.46)),
             ((0.40, 0.40, 0.44), (0.56, 0.56, 0.60)), "pines"),
    "beach": (((0.86, 0.74, 0.50), (0.98, 0.90, 0.68)), ((0.74, 0.62, 0.40), (0.88, 0.78, 0.56)),
              ((0.50, 0.42, 0.30), (0.66, 0.56, 0.42)), "palms"),
    "stone": (((0.46, 0.46, 0.48), (0.66, 0.66, 0.68)), ((0.36, 0.36, 0.38), (0.52, 0.52, 0.54)),
              ((0.30, 0.28, 0.26), (0.44, 0.42, 0.40)), "lamps"),
    "paris": (((0.55, 0.48, 0.37), (0.70, 0.63, 0.50)), ((0.45, 0.40, 0.33), (0.58, 0.53, 0.45)),
              ((0.40, 0.38, 0.35), (0.55, 0.53, 0.50)), "paris"),          # Champ de Mars gravel in a cobbled square
}
TIME = {     # light travel direction, sun energy / colour, sky horizon -> top, sky strength, exposure
    "day": dict(sun=(0.55, 0.62, -0.62), energy=4.2, color=(1.0, 0.90, 0.76), horizon=(0.96, 0.78, 0.56),
                top=(0.36, 0.60, 0.92), strength=0.8, exposure=-0.35),
    "morning": dict(sun=(-0.70, 0.55, -0.45), energy=3.4, color=(1.0, 0.86, 0.72), horizon=(0.98, 0.84, 0.70),
                    top=(0.48, 0.68, 0.95), strength=0.8, exposure=-0.3),
    "sunset": dict(sun=(0.75, 0.55, -0.22), energy=3.2, color=(1.0, 0.60, 0.36), horizon=(1.0, 0.56, 0.32),
                   top=(0.32, 0.32, 0.58), strength=0.75, exposure=-0.2),
    "night": dict(sun=(0.35, 0.55, -0.75), energy=0.45, color=(0.55, 0.65, 1.0), horizon=(0.07, 0.09, 0.18),
                  top=(0.01, 0.015, 0.04), strength=0.8, exposure=0.25),
}
OVERCAST = {"rain": (0.35, (0.50, 0.53, 0.58), 0.6), "snow": (0.6, (0.80, 0.83, 0.88), 0.5)}   # sun x, grey, mix


def _mix(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def _loop(o, path, index, v0, v1, frames):
    """Key o.<path>[index] from v0 (frame 0) to v1 (frame 'frames'), linear, repeating forever."""
    vec = getattr(o, path)
    vec[index] = v0; o.keyframe_insert(path, index=index, frame=0)
    vec[index] = v1; o.keyframe_insert(path, index=index, frame=frames)
    for fc in VK.fcurves_of(o):
        if fc.data_path == path and fc.array_index == index:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
            fc.modifiers.new("CYCLES")


def _wave(o, path, index, amp, period_frames, phase=0.0):
    """Add a sine (amp * sin) on top of o.<path>[index]; needs no keys of its own."""
    o.keyframe_insert(path, index=index, frame=0)
    for fc in VK.fcurves_of(o):
        if fc.data_path == path and fc.array_index == index:
            m = fc.modifiers.new("FNGENERATOR")
            m.function_type, m.use_additive = "SIN", True
            m.amplitude, m.phase_multiplier, m.phase_offset = amp, 2 * math.pi / period_frames, phase


def _no_shadow(o):
    o.visible_shadow = False
    return o


# ------------------------------------------------------------------ ground + props
EXTEND = [False]
FOREST_C, FOREST_R = (-6.0, 0.8), (4.6, 4.4)                 # the forest: an ellipse of land west of the cabin
STREAM_X = lambda y: -5.2 + 0.25 * math.sin(y * 0.7)          # stream centre line (runs north-south), 0.7 m wide


def forest_land(x, y, shrink=0.0):
    return ((x - FOREST_C[0]) / max(0.5, FOREST_R[0] - shrink)) ** 2 + ((y - FOREST_C[1]) / max(0.5, FOREST_R[1] - shrink)) ** 2 <= 1.0


PATH_PTS = [(-1.75, 0.62), (-2.3, 0.42), (-3.1, 0.45), (-3.85, 0.5)]   # door -> round the sapling -> the stream bank


def near_path(x, y, d):
    for (x0, y0), (x1, y1) in zip(PATH_PTS, PATH_PTS[1:]):
        vx, vy = x1 - x0, y1 - y0
        u = max(0.0, min(1.0, ((x - x0) * vx + (y - y0) * vy) / (vx * vx + vy * vy)))
        if math.hypot(x - (x0 + u * vx), y - (y0 + u * vy)) < d:
            return True
    return False


def forest_trees(r=None):
    """The forest's trees [(x, y, height, "oak"|"pine")], always the same (seed 41). Pure Python: story generators use it
    to find real trees (a rabbit hiding behind one, a camera kept clear of them)."""
    r = r or random.Random(41)
    keep_clear = lambda x, y: (near_path(x, y, 0.75) or abs(x - STREAM_X(y)) < 0.75 or
                               (-6.2 < x < -3.6 and -0.2 < y < 3.0) or math.hypot(x, y) < R0 + 0.4 or
                               (-3.7 < x < -2.0 and -0.8 < y < 3.4))         # where the cameras stand by the machine
    out = []
    for _ in range(900):
        x, y = r.uniform(-10.5, -2.6), r.uniform(-3.6, 5.2)
        if not forest_land(x, y, 0.5) or keep_clear(x, y):
            continue
        h = r.uniform(0.9, 1.9)
        out.append((x, y, h, "oak" if r.random() < 0.5 else "pine"))
        if len(out) >= 55:
            break
    return out


def build_forest_west(sc, fps):
    """Trees (oaks and pines), a path from the cabin door, a stream with banks of stones, flowing water."""
    px = 0.1 / 8
    trunk = VK.pixel_material("FTrunk", (0.28, 0.18, 0.10), (0.44, 0.30, 0.17), px)
    oak = VK.pixel_material("FOak", (0.13, 0.33, 0.11), (0.28, 0.52, 0.19), px)
    pine = VK.pixel_material("FPine", (0.07, 0.24, 0.12), (0.16, 0.38, 0.18), px)
    stone = VK.pixel_material("FStone", (0.40, 0.40, 0.42), (0.60, 0.60, 0.62), px)
    path = VK.pixel_material("FPath", (0.46, 0.36, 0.24), (0.62, 0.50, 0.34), px)
    r = random.Random(41)
    boxes = []
    for ix in range(int(-4.2 / 0.15), int(-1.6 / 0.15) + 1):      # a worn dirt path: non-overlapping 0.15 m tiles
        for iy in range(int(-0.3 / 0.15), int(1.4 / 0.15) + 1):    # (overlapping coplanar boxes render black)
            x, y = (ix + 0.5) * 0.15, (iy + 0.5) * 0.15
            if near_path(x, y, 0.2) and x < -1.75:
                boxes.append(((x, y, 0.003), (0.149, 0.149, 0.006), 4))
    for x, y, h, kind in forest_trees(r):
        if kind == "oak":                                       # oak: trunk + two leaf blocks
            boxes += [((x, y, h / 2), (0.14, 0.14, h), 0), ((x, y, h + 0.22), (0.75, 0.75, 0.5), 1),
                      ((x + 0.08, y - 0.05, h + 0.55), (0.48, 0.48, 0.3), 1)]
        else:                                                   # pine: trunk + four shrinking layers
            boxes.append(((x, y, 0.25), (0.12, 0.12, 0.5), 0))
            for k, w in enumerate((0.8, 0.6, 0.4, 0.2)):
                boxes.append(((x, y, 0.45 + h * 0.28 * k + 0.16), (w, w, 0.34), 2))
    for k in range(70):                                         # stones along both banks
        y = -3.4 + 8.4 * k / 70 + r.uniform(-0.05, 0.05)
        side = 1 if k % 2 else -1
        s_ = r.uniform(0.08, 0.16)
        boxes.append(((STREAM_X(y) + side * (0.38 + r.uniform(0, 0.08)), y, s_ / 2 - 0.02), (s_, s_ * 1.2, s_), 3))
    VK.mesh_obj("Forest", boxes, [trunk, oak, pine, stone, path], coll=sc.collection)
    water = VK.mat("Water", (0.10, 0.32, 0.42), rough=0.06)     # flowing water: a scrolling ripple bump
    N, Lk = water.node_tree.nodes, water.node_tree.links
    tc, mp = N.new("ShaderNodeTexCoord"), N.new("ShaderNodeMapping")
    noise, bump = N.new("ShaderNodeTexNoise"), N.new("ShaderNodeBump")
    noise.inputs["Scale"].default_value, bump.inputs["Strength"].default_value = 9.0, 0.35
    Lk.new(tc.outputs["Object"], mp.inputs["Vector"]); Lk.new(mp.outputs["Vector"], noise.inputs["Vector"])
    Lk.new(noise.outputs["Fac"], bump.inputs["Height"]); Lk.new(bump.outputs["Normal"], N["Principled BSDF"].inputs["Normal"])
    loc = mp.inputs["Location"]
    loc.default_value[1] = 0.0; loc.keyframe_insert("default_value", index=1, frame=0)
    loc.default_value[1] = -0.6; loc.keyframe_insert("default_value", index=1, frame=fps)    # flows south, 0.6 m/s
    for fc in VK.fcurves_of(water.node_tree):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
        fc.modifiers.new("CYCLES")
    wb = []
    for k in range(84):
        y = -3.5 + 0.1 * k
        wb.append(((STREAM_X(y), y, 0.012), (0.7, 0.104, 0.024), 0))
    VK.mesh_obj("Stream", wb, [water], coll=sc.collection)


def build_ground(sc, ground):
    top, side, base, props = GROUND[ground]
    mats = [VK.pixel_material("Ground", *top, V / 16, voxel=V), VK.pixel_material("GroundSide", *side, V / 16, voxel=V),
            VK.pixel_material("Bedrock", *base, V / 16, voxel=V)]
    bm = bmesh.new()
    for z0, r, mi in ((-0.2, R0, 0), (-0.4, R0 - 0.2, 1), (-0.6, R0 - 0.6, 2), (-0.8, R0 - 1.2, 2)):
        n = int(r / V) + 1
        for ix in range(-n, n):
            for iy in range(-n, n):
                cx, cy = (ix + 0.5) * V, (iy + 0.5) * V
                if math.hypot(cx, cy) <= r:
                    VK.add_box(bm, (cx, cy, z0 + V / 2), (V, V, V), mi)
    if EXTEND[0]:                                                # extra land to the west (forest), same layered look
        for z0, shrink, mi in ((-0.2, 0.0, 0), (-0.4, 0.2, 1), (-0.6, 0.6, 2), (-0.8, 1.2, 2)):
            for ix in range(int(-11.0 / V), int(-1.0 / V)):
                for iy in range(int(-5.0 / V), int(6.0 / V)):
                    cx, cy = (ix + 0.5) * V, (iy + 0.5) * V
                    if forest_land(cx, cy, shrink) and math.hypot(cx, cy) > R0 - (0.0 if mi == 0 else shrink) + 1e-6:
                        VK.add_box(bm, (cx, cy, z0 + V / 2), (V, V, V), mi)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new("Island")
    bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    sc.collection.objects.link(bpy.data.objects.new("Island", me))
    globals()["_props_" + props](sc)
    if ground == "beach":
        sea = VK.mat("Sea", (0.04, 0.30, 0.42), rough=0.08)
        VK.mesh_obj("Sea", [((0, 0, -0.13), (80, 80, 0.02), 0)], [sea], coll=sc.collection)


def _props_cacti(sc):
    cact = VK.pixel_material("Cactus", (0.16, 0.36, 0.14), (0.30, 0.55, 0.22), 0.1 / 8)
    boxes = []
    for (cx, cy), h in zip(PROP_SPOTS, (0.35, 0.28, 0.22)):
        boxes += [((cx, cy, h / 2), (0.1, 0.1, h), 0), ((cx + 0.08, cy, h * 0.55), (0.08, 0.06, 0.06), 0),
                  ((cx + 0.1, cy, h * 0.72), (0.05, 0.05, h * 0.3), 0)]
    VK.mesh_obj("Cacti", boxes, [cact], coll=sc.collection)


def _props_trees(sc):
    wood = VK.pixel_material("Trunk", (0.30, 0.19, 0.10), (0.46, 0.31, 0.17), 0.1 / 8)
    leaf = VK.pixel_material("Leaves", (0.12, 0.34, 0.10), (0.30, 0.56, 0.20), 0.1 / 8)
    petal = VK.mat("Petals", (0.95, 0.85, 0.20), rough=0.7)
    petal2 = VK.mat("Petals2", (0.90, 0.25, 0.30), rough=0.7)
    boxes = []
    for (cx, cy), h in zip(PROP_SPOTS, (0.45, 0.38, 0.32)):
        boxes += [((cx, cy, h / 2), (0.1, 0.1, h), 0), ((cx, cy, h + 0.08), (0.36, 0.36, 0.2), 1),
                  ((cx, cy, h + 0.24), (0.22, 0.22, 0.14), 1)]
    for k in range(26):
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(1.7, 2.5)
        boxes.append(((r * math.cos(a), r * math.sin(a), 0.02), (0.04, 0.04, 0.04), 2 + k % 2))
    VK.mesh_obj("Trees", boxes, [wood, leaf, petal, petal2], coll=sc.collection)


def _props_pines(sc):
    wood = VK.pixel_material("Trunk", (0.30, 0.19, 0.10), (0.46, 0.31, 0.17), 0.1 / 8)
    pine = VK.pixel_material("Pine", (0.06, 0.24, 0.12), (0.14, 0.38, 0.20), 0.1 / 8)
    snow = VK.mat("SnowCap", (0.95, 0.97, 1.0), rough=0.9)
    boxes = []
    for (cx, cy), s in zip(PROP_SPOTS, (1.0, 0.85, 0.7)):
        boxes.append(((cx, cy, 0.06 * s), (0.08, 0.08, 0.12 * s), 0))
        z = 0.12 * s
        for w in (0.40, 0.30, 0.20, 0.10):
            boxes += [((cx, cy, z + 0.05 * s), (w * s, w * s, 0.1 * s), 1), ((cx, cy, z + 0.1 * s + 0.006), (w * s * 0.8, w * s * 0.8, 0.012), 2)]
            z += 0.1 * s
    VK.mesh_obj("Pines", boxes, [wood, pine, snow], coll=sc.collection)


def _props_palms(sc):
    trunk = VK.pixel_material("PalmTrunk", (0.45, 0.33, 0.20), (0.62, 0.48, 0.30), 0.1 / 8)
    frond = VK.pixel_material("Frond", (0.14, 0.40, 0.12), (0.28, 0.60, 0.22), 0.1 / 8)
    nut = VK.mat("Coconut", (0.30, 0.20, 0.10), rough=0.8)
    boxes = []
    for (cx, cy), h in zip(PROP_SPOTS, (0.7, 0.6, 0.5)):
        n = int(h / 0.1)
        for k in range(n):
            boxes.append(((cx + 0.012 * k * k / n, cy, 0.05 + 0.1 * k), (0.08, 0.08, 0.1), 0))
        tx, tz = cx + 0.012 * n, 0.1 * n + 0.02
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            boxes += [((tx + 0.13 * dx, cy + 0.13 * dy, tz), (0.18 if dx else 0.07, 0.07 if dx else 0.18, 0.03), 1),
                      ((tx + 0.26 * dx, cy + 0.26 * dy, tz - 0.05), (0.1 if dx else 0.06, 0.06 if dx else 0.1, 0.03), 1)]
        boxes += [((tx + 0.04, cy - 0.04, tz - 0.06), (0.05, 0.05, 0.05), 2), ((tx - 0.04, cy + 0.03, tz - 0.06), (0.05, 0.05, 0.05), 2)]
    VK.mesh_obj("Palms", boxes, [trunk, frond, nut], coll=sc.collection)


def _props_paris(sc):
    """A cobbled square and a street of block Paris apartment buildings: cream stone, blue-grey mansard roofs,
    black balconies, chimney pots, a flag. Plus lamps, plane trees and a cafe table. Kept low and far back so the
    tower (in the story) stays the giant of the skyline."""
    cob = VK.pixel_material("Cobbles", (0.27, 0.27, 0.29), (0.43, 0.42, 0.41), 0.15, voxel=0.15)
    VK.mesh_obj("Square", [((0, 0, -0.015), (60, 60, 0.02), 0)], [cob], coll=sc.collection)
    stone = VK.pixel_material("Facade", (0.80, 0.74, 0.62), (0.93, 0.88, 0.77), 0.05)
    win, iron = VK.mat("Window", (0.10, 0.12, 0.16), 0.2), VK.mat("Balcony", (0.06, 0.06, 0.07), 0.5, 0.4)
    roof = VK.pixel_material("Zinc", (0.32, 0.36, 0.42), (0.46, 0.50, 0.57), 0.05)
    pot, door = VK.mat("ChimneyPot", (0.62, 0.32, 0.22), 0.8), VK.mat("Door", (0.18, 0.22, 0.30), 0.6)
    boxes = []
    x = -11.0
    while x < 11.0:
        w, floors = rnd.uniform(2.2, 3.4), rnd.choice((5, 5, 6))
        fh, y0, d = 0.36, rnd.uniform(9.0, 9.6), 1.6
        h = floors * fh
        cx = x + w / 2
        boxes.append(((cx, y0, h / 2), (w, d, h), 0))                                   # stone body
        fy = y0 - d / 2 - 0.006
        for f in range(floors):
            for k in range(int(w / 0.42)):
                wx = x + 0.25 + k * 0.42
                if wx > x + w - 0.2:
                    break
                if f == 0 and k == int(w / 0.42) // 2:
                    boxes.append(((wx, fy, 0.16), (0.2, 0.012, 0.3), 5))                # door
                else:
                    boxes.append(((wx, fy, f * fh + 0.2), (0.16, 0.012, 0.22), 1))     # window
            if f in (1, floors - 1):
                boxes.append(((cx, fy - 0.04, f * fh + 0.08), (w - 0.1, 0.08, 0.02), 2))   # balcony
                boxes.append(((cx, fy - 0.08, f * fh + 0.13), (w - 0.1, 0.01, 0.1), 2))
        boxes += [((cx, y0, h + 0.12), (w, d - 0.3, 0.24), 3), ((cx, y0, h + 0.34), (w - 0.2, d - 0.8, 0.2), 3)]   # mansard
        for k in range(2):
            boxes.append(((x + 0.4 + k * (w - 0.8), y0 + 0.2, h + 0.55), (0.18, 0.14, 0.22), 4))
        x += w + rnd.uniform(0.0, 0.6)
    VK.mesh_obj("ParisStreet", boxes, [stone, win, iron, roof, pot, door], coll=sc.collection)
    blue, white, red = VK.mat("FlagBlue", (0.0, 0.14, 0.52), 0.7), VK.mat("FlagWhite", (0.95, 0.95, 0.95), 0.7), VK.mat("FlagRed", (0.85, 0.08, 0.12), 0.7)
    VK.mesh_obj("Flag", [((2.0, 9.2, 2.6), (0.03, 0.03, 1.0), 3), ((2.17, 9.2, 2.95), (0.3, 0.01, 0.4), 0),
                         ((2.47, 9.2, 2.95), (0.3, 0.01, 0.4), 1), ((2.77, 9.2, 2.95), (0.3, 0.01, 0.4), 2)],
                [blue, white, red, iron], coll=sc.collection)
    # lamps and plane trees along the square, a cafe table with a striped umbrella on the island's edge
    glow = VK.emission_material("LampGlow", (1.0, 0.82, 0.55), 4.0)
    trunk = VK.pixel_material("PlaneTrunk", (0.42, 0.40, 0.33), (0.62, 0.60, 0.50), 0.05)
    leaf = VK.pixel_material("PlaneLeaves", (0.18, 0.38, 0.14), (0.34, 0.56, 0.24), 0.08)
    cloth_r, cloth_w = VK.mat("Awning", (0.80, 0.10, 0.12), 0.8), VK.mat("AwningW", (0.95, 0.94, 0.90), 0.8)
    st = []
    for lx in (-6.0, -3.2, 3.2, 6.0):
        st += [((lx, 4.2, 0.45), (0.05, 0.05, 0.9), 0), ((lx, 4.2, 0.95), (0.11, 0.11, 0.12), 1), ((lx, 4.2, 1.03), (0.14, 0.14, 0.03), 0)]
    for tx in (-7.5, -4.6, 4.6, 7.5):
        st += [((tx, 6.0, 0.4), (0.12, 0.12, 0.8), 2), ((tx, 6.0, 1.05), (0.9, 0.9, 0.55), 3), ((tx, 6.0, 1.4), (0.6, 0.6, 0.3), 3)]
    cx, cy = -2.1, 1.3
    st += [((cx, cy, 0.25), (0.04, 0.04, 0.5), 0), ((cx, cy, 0.5), (0.3, 0.3, 0.03), 0), ((cx, cy, 0.95), (0.03, 0.03, 0.9), 0)]
    for k in range(6):
        st.append(((cx - 0.375 + k * 0.15, cy, 1.38), (0.15, 0.75, 0.05), 4 + k % 2))
    for dx in (-0.32, 0.32):
        st += [((cx + dx, cy, 0.2), (0.16, 0.16, 0.03), 0), ((cx + dx, cy, 0.1), (0.03, 0.03, 0.2), 0), ((cx + dx * 1.3, cy, 0.32), (0.03, 0.16, 0.22), 0)]
    VK.mesh_obj("ParisSquare", st, [iron, glow, trunk, leaf, cloth_r, cloth_w], coll=sc.collection)


def _props_lamps(sc):
    iron = VK.mat("Iron", (0.08, 0.08, 0.09), rough=0.5, metal=0.6)
    glow = VK.emission_material("LampGlow", (1.0, 0.82, 0.55), 4.0)
    boxes = []
    for cx, cy in PROP_SPOTS:
        boxes += [((cx, cy, 0.30), (0.04, 0.04, 0.6), 0), ((cx, cy, 0.02), (0.1, 0.1, 0.04), 0),
                  ((cx, cy, 0.66), (0.09, 0.09, 0.1), 1), ((cx, cy, 0.725), (0.11, 0.11, 0.02), 0)]
    VK.mesh_obj("Lamps", boxes, [iron, glow], coll=sc.collection)


# ------------------------------------------------------------------ sky + light
def build_sky(sc, time, weather):
    T = dict(TIME[time])
    if weather in OVERCAST:
        k_sun, grey, k = OVERCAST[weather]
        if time == "night":
            grey = tuple(g * 0.15 for g in grey)
        T["energy"] *= k_sun
        T["horizon"], T["top"] = _mix(T["horizon"], grey, k), _mix(T["top"], grey, k)
    sun_d = bpy.data.lights.new("Sun", "SUN")
    sun_d.energy, sun_d.angle, sun_d.color = T["energy"], math.radians(4.0), T["color"]
    sun = bpy.data.objects.new("Sun", sun_d)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = Vector(T["sun"]).to_track_quat("-Z", "Y")
    sc.collection.objects.link(sun)
    w = bpy.data.worlds.new("Sky")
    sc.world = w
    w.use_nodes = True
    N, Lk = w.node_tree.nodes, w.node_tree.links
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (*T["horizon"], 1)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.55, (*T["top"], 1)
    Lk.new(sep.outputs["Z"], ramp.inputs["Fac"])
    Lk.new(ramp.outputs["Color"], N["Background"].inputs["Color"])
    N["Background"].inputs["Strength"].default_value = T["strength"]
    if time == "night":
        lamp = bpy.data.lights.new("Lantern", "POINT")              # warm fill so grandpa reads at night
        lamp.energy, lamp.color, lamp.shadow_soft_size = 75, (1.0, 0.76, 0.48), 0.4
        o = bpy.data.objects.new("Lantern", lamp); o.location = (0.0, -0.45, 1.9)
        sc.collection.objects.link(o)
        if weather not in OVERCAST:
            star = VK.emission_material("Stars", (1.0, 0.97, 0.9), 6.0)
            boxes = []
            for _ in range(420):
                a, e = rnd.uniform(0, 2 * math.pi), math.asin(rnd.uniform(0.12, 1.0))
                d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * 45
                s = rnd.choice((0.08, 0.1, 0.14))
                boxes.append((tuple(d), (s, s, s), 0))
            _no_shadow(VK.mesh_obj("Stars", boxes, [star], coll=sc.collection))
            moon = VK.emission_material("Moon", (0.92, 0.94, 1.0), 3.0)
            _no_shadow(VK.mesh_obj("Moon", [((9, 38, 15), (2.6, 0.2, 2.6), 0), ((9, 38.1, 15), (3.2, 0.2, 1.8), 0),
                                            ((9, 38.1, 15), (1.8, 0.2, 3.2), 0)], [moon], coll=sc.collection))
    return T["exposure"]


# ------------------------------------------------------------------ weather
def build_clouds(sc, nf, dark):
    m = VK.mat("Cloud", (0.55, 0.57, 0.60) if dark else (0.97, 0.97, 0.98), rough=1.0)
    for k in range(8):
        a = rnd.uniform(0.15 * math.pi, 0.85 * math.pi)             # mostly behind the island, where the camera looks
        r = rnd.uniform(6, 12)
        c = Vector((r * math.cos(a), r * math.sin(a), rnd.uniform(3.5, 6.5)))
        boxes = []
        for _ in range(rnd.randint(4, 7)):
            s = Vector((rnd.uniform(0.5, 1.1), rnd.uniform(0.4, 0.8), rnd.uniform(0.25, 0.45)))
            boxes.append(((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.1, 0.15)), tuple(s), 0))
        o = _no_shadow(VK.mesh_obj("Cloud_%d" % k, boxes, [m], coll=sc.collection))
        o.location = c
        _loop(o, "location", 0, c.x, c.x + 0.25, 30 * 30)              # slow drift, 0.25 m every 30 s


def build_precip(sc, kind, fps):
    """Rain streaks or snowflakes: one mesh, tiled twice in height, sliding down one tile per cycle forever."""
    H = 6.0
    if kind == "rain":
        n, size, speed = 1300, (0.008, 0.008, 0.16), 6.0
        m = VK.mat("Raindrop", (0.72, 0.78, 0.88), rough=0.1)
        m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.4
    else:
        n, size, speed = 900, (0.025, 0.025, 0.025), 0.7
        m = VK.mat("Snowflake", (0.97, 0.98, 1.0), rough=1.0)
    boxes = []
    for _ in range(n):
        x, y, z = rnd.uniform(-4, 4), rnd.uniform(-1.2, 5), rnd.uniform(0, H)     # none right at the lens
        boxes += [((x, y, z), size, 0), ((x, y, z + H), size, 0)]
    o = _no_shadow(VK.mesh_obj(kind.capitalize(), boxes, [m], coll=sc.collection))
    _loop(o, "location", 2, 0.0, -H, round(H / speed * fps))
    if kind == "snow":
        _wave(o, "location", 0, 0.08, 3.0 * fps)


# ------------------------------------------------------------------ animals
def build_birds(sc, fps, gulls, pigeons=False):
    body_c = (0.92, 0.92, 0.90) if gulls else (0.52, 0.54, 0.60) if pigeons else (0.22, 0.19, 0.17)
    wing_c = (0.55, 0.57, 0.60) if gulls else (0.38, 0.40, 0.46) if pigeons else (0.15, 0.13, 0.12)
    mb, mw, mk = VK.mat("BirdBody", body_c, 0.9), VK.mat("BirdWing", wing_c, 0.9), VK.mat("Beak", (0.95, 0.65, 0.10), 0.6)
    for k in range(4 if gulls else 5):
        piv = bpy.data.objects.new("BirdPivot_%d" % k, None)
        sc.collection.objects.link(piv)
        piv.location = (rnd.uniform(-1.5, 1.5), rnd.uniform(1.5, 4.0), rnd.uniform(2.6, 4.2))
        r, period, ccw = rnd.uniform(2.5, 4.5), rnd.uniform(9, 14), k % 2 == 0
        body = VK.mesh_obj("Bird_%d" % k, [((0, 0, 0), (0.05, 0.14, 0.045), 0), ((0, 0.08, 0.015), (0.045, 0.045, 0.04), 0),
                                           ((0, 0.11, 0.01), (0.015, 0.03, 0.012), 2), ((0, -0.08, 0.0), (0.04, 0.04, 0.012), 1)],
                           [mb, mw, mk], parent=piv, coll=sc.collection)
        body.location = (r, 0, 0)
        body.rotation_euler = (0, 0, 0 if ccw else math.pi)            # face along the circle
        for s in (-1, 1):
            wing = VK.mesh_obj("Wing_%d_%d" % (k, s), [((0.065 * s, 0, 0), (0.11, 0.07, 0.01), 0)], [mw], parent=body, coll=sc.collection)
            wing.location = (0.022 * s, 0, 0.012)
            _wave(wing, "rotation_euler", 1, 0.6 * s, fps / 3.2, phase=k)
        _loop(piv, "rotation_euler", 2, 0.0, 2 * math.pi * (1 if ccw else -1), round(period * fps))
        _wave(piv, "location", 2, 0.12, 4.0 * fps, phase=k * 1.3)


def build_cat(sc, fps, spot):
    fur, white = VK.mat("CatFur", (0.86, 0.50, 0.20), 0.95), VK.mat("CatWhite", (0.95, 0.93, 0.90), 0.95)
    eye, nose = VK.mat("CatEye", (0.30, 0.75, 0.25), 0.3), VK.mat("CatNose", (0.95, 0.55, 0.60), 0.6)
    root = bpy.data.objects.new("Cat", None)
    sc.collection.objects.link(root)
    root.location = (spot[0], spot[1], 0)
    root.rotation_euler = (0, 0, math.atan2(-spot[0], spot[1]) * 0.5)  # turned partly toward the middle of the island
    VK.mesh_obj("CatBody", [((0, 0, 0.06), (0.14, 0.18, 0.12), 0), ((0, -0.05, 0.16), (0.12, 0.10, 0.10), 0),
                            ((0, -0.101, 0.14), (0.07, 0.004, 0.08), 1), ((-0.04, -0.09, 0.015), (0.04, 0.05, 0.03), 1),
                            ((0.04, -0.09, 0.015), (0.04, 0.05, 0.03), 1)], [fur, white], parent=root, coll=sc.collection)
    head = VK.mesh_obj("CatHead", [((0, 0, 0), (0.12, 0.10, 0.10), 0), ((-0.035, 0, 0.065), (0.03, 0.02, 0.035), 0),
                                   ((0.035, 0, 0.065), (0.03, 0.02, 0.035), 0), ((-0.03, -0.051, 0.012), (0.022, 0.004, 0.02), 2),
                                   ((0.03, -0.051, 0.012), (0.022, 0.004, 0.02), 2), ((0, -0.052, -0.012), (0.016, 0.004, 0.012), 3),
                                   ((0, -0.051, -0.03), (0.05, 0.004, 0.03), 1)], [fur, white, eye, nose], parent=root, coll=sc.collection)
    head.location = (0, -0.06, 0.26)
    _wave(head, "rotation_euler", 2, 0.35, 7.0 * fps)                  # looks around slowly
    tail = VK.mesh_obj("CatTail", [((0, 0.06, 0.0), (0.03, 0.12, 0.03), 0), ((0, 0.11, 0.06), (0.03, 0.03, 0.1), 0)],
                       [fur], parent=root, coll=sc.collection)
    tail.location = (0, 0.08, 0.03)
    _wave(tail, "rotation_euler", 2, 0.5, 2.2 * fps)                   # tail swish


def cat_spot(P):
    """The spot on the island farthest from every block and from grandpa's path."""
    pts = [Vector(p[:2]) for p in P["path"][::10]]
    for b in P["blocks"]:
        st = P["structures"][b["struct"]]
        pts.append(Vector((st["at"][0] + b["pos"][0], st["at"][1] + b["pos"][1])))
    best, cand = None, []
    for k in range(24):
        a = 2 * math.pi * k / 24
        for r in (1.6, 1.9, 2.2):
            c = Vector((r * math.cos(a), r * math.sin(a)))
            if min((c - Vector(s)).length for s in PROP_SPOTS) < 0.4:
                continue
            score = min((c - p).length for p in pts) + (0.3 if c.y > 0 else 0)   # prefer the back half (in view)
            cand.append((score, tuple(c)))
    return max(cand)[1]


def build_cabin(sc, roof=False):
    """Grandpa's log cabin, open at the front (camera side) and the top (sky light): plank floor, log walls, a door in
    the left wall, a sunny window in the right wall and one in the back, a shelf of books, a clock, a rug and a plant.
    Floor x -1.6..1.4, y -0.9..1.6 (top at z = 0.004); everything is voxel boxes with pixel textures."""
    px = 0.1 / 8
    log = VK.pixel_material("Log", (0.42, 0.26, 0.13), (0.60, 0.40, 0.22), px)
    log2 = VK.pixel_material("Log2", (0.36, 0.22, 0.11), (0.53, 0.35, 0.19), px)
    plank = VK.pixel_material("FloorPlank", (0.55, 0.38, 0.22), (0.74, 0.55, 0.34), px)
    plank2 = VK.pixel_material("FloorPlank2", (0.50, 0.34, 0.19), (0.68, 0.49, 0.30), px)
    trim = VK.pixel_material("Trim", (0.80, 0.74, 0.62), (0.94, 0.90, 0.80), px)
    door = VK.pixel_material("Door", (0.30, 0.18, 0.09), (0.44, 0.28, 0.14), px)
    rug = VK.pixel_material("Rug", (0.50, 0.12, 0.10), (0.72, 0.24, 0.16), px)
    misc = [VK.mat("Book%d" % k, c, 0.8) for k, c in enumerate(((0.62, 0.15, 0.12), (0.16, 0.34, 0.58), (0.20, 0.45, 0.24),
                                                                (0.80, 0.62, 0.20), (0.40, 0.25, 0.50)))]
    steel = VK.mat("Knob", (0.75, 0.72, 0.62), 0.35, 0.8)
    leaf = VK.pixel_material("PlantLeaf", (0.12, 0.36, 0.12), (0.28, 0.58, 0.22), px)
    pot = VK.pixel_material("Pot", (0.62, 0.30, 0.16), (0.78, 0.42, 0.24), px)
    face = VK.mat("ClockFace", (0.95, 0.93, 0.86), 0.6)
    ink = VK.mat("ClockInk", (0.08, 0.07, 0.06), 0.6)
    X0, X1, Y0, Y1, TOP, T = -1.6, 1.4, -0.9, 1.6, 2.0, 0.12
    M = dict(log=0, log2=1, plank=2, plank2=3, trim=4, door=5, rug=6, steel=7, leaf=8, pot=9, face=10, ink=11)
    boxes = []
    add = lambda c, s, m: boxes.append((c, s, M[m] if isinstance(m, str) else m))
    for k, x in enumerate([X0 + 0.15 * i for i in range(int((X1 - X0) / 0.15) + 1)]):   # floor boards along y
        w = min(0.15, X1 - x)
        if w > 0.01:
            add((x + w / 2, (Y0 + Y1) / 2, 0.002), (w - 0.004, Y1 - Y0, 0.004), "plank" if k % 2 else "plank2")

    def wall(axis, fixed, lo, hi, holes):
        """Horizontal logs (0.2 m) along `axis` ("x": back wall at y = fixed, "y": side wall at x = fixed), cut around holes
        [(a0, a1, z0, z1)] (window / door openings)."""
        for r in range(int(TOP / 0.2)):
            z0, z1 = r * 0.2, r * 0.2 + 0.2
            cuts = [(a0, a1) for a0, a1, h0, h1 in holes if h0 < z1 - 1e-6 and h1 > z0 + 1e-6]
            segs, a = [], lo
            for a0, a1 in sorted(cuts):
                if a0 > a: segs.append((a, a0))
                a = max(a, a1)
            if a < hi: segs.append((a, hi))
            for s0, s1 in segs:
                c = ((s0 + s1) / 2, fixed, (z0 + z1) / 2) if axis == "x" else (fixed, (s0 + s1) / 2, (z0 + z1) / 2)
                sz = (s1 - s0, T, 0.206) if axis == "x" else (T, s1 - s0, 0.206)   # rows overlap: no light leaks
                add(c, sz, "log" if r % 2 else "log2")
            for a0, a1, h0, h1 in holes:                         # the log pieces above / below an opening in this row
                if not (h0 < z1 - 1e-6 and h1 > z0 + 1e-6):
                    continue
                for zz0, zz1 in ((z0, h0), (h1, z1)):
                    if zz1 - zz0 > 0.005:
                        c = ((a0 + a1) / 2, fixed, (zz0 + zz1) / 2) if axis == "x" else (fixed, (a0 + a1) / 2, (zz0 + zz1) / 2)
                        sz = (a1 - a0, T, zz1 - zz0 - 0.002) if axis == "x" else (T, a1 - a0, zz1 - zz0 - 0.002)
                        add(c, sz, "log" if r % 2 else "log2")

    BACK_WIN, RIGHT_WIN, DOOR = (0.35, 0.95, 0.75, 1.35), (0.15, 0.75, 0.6, 1.2), (0.45, 0.95, 0.0, 1.25)
    wall("x", Y1 + T / 2, X0 - T, X1 + T, [BACK_WIN])
    wall("y", X0 - T / 2, Y0, Y1, [DOOR])
    wall("y", X1 + T / 2, Y0, Y1, [RIGHT_WIN])
    for (a0, a1, z0, z1), axis, fixed in ((BACK_WIN, "x", Y1 + T / 2), (RIGHT_WIN, "y", X1 + T / 2)):   # window frames + cross
        fr = 0.04
        for cx, cz, w_, h_ in (((a0 + a1) / 2, z0, a1 - a0 + 2 * fr, fr), ((a0 + a1) / 2, z1, a1 - a0 + 2 * fr, fr),
                               (a0, (z0 + z1) / 2, fr, z1 - z0), (a1, (z0 + z1) / 2, fr, z1 - z0),
                               ((a0 + a1) / 2, (z0 + z1) / 2, 0.025, z1 - z0), ((a0 + a1) / 2, (z0 + z1) / 2, a1 - a0, 0.025)):
            c = (cx, fixed, cz) if axis == "x" else (fixed, cx, cz)
            sz = (w_, T + 0.03, h_) if axis == "x" else (T + 0.03, w_, h_)
            add(c, sz, "trim")
        sill = (a0 + a1) / 2
        add((sill, fixed - 0.08, z0 - 0.01) if axis == "x" else (fixed - 0.08, sill, z0 - 0.01),
            (a1 - a0 + 0.12, 0.08, 0.03) if axis == "x" else (0.08, a1 - a0 + 0.12, 0.03), "trim")
    a0, a1, z0, z1 = DOOR                                        # the door (own object, hinged), its frame and a brass knob
    door_boxes = [((X0 - T / 2 + 0.02, (a0 + a1) / 2, (z0 + z1) / 2), (0.05, a1 - a0, z1 - z0), M["door"])]
    for k in range(4):
        door_boxes.append(((X0 - T / 2 + 0.05, a0 + 0.06 + k * (a1 - a0 - 0.12) / 3, (z0 + z1) / 2), (0.012, 0.012, z1 - z0 - 0.1), M["log2"]))
    for c, sz in (((X0 + 0.01, a0 - 0.02, (z0 + z1) / 2 + 0.02), (0.04, 0.04, z1 - z0 + 0.04)),
                  ((X0 + 0.01, a1 + 0.02, (z0 + z1) / 2 + 0.02), (0.04, 0.04, z1 - z0 + 0.04)),
                  ((X0 + 0.01, (a0 + a1) / 2, z1 + 0.02), (0.04, a1 - a0 + 0.08, 0.04))):
        add(c, sz, "trim")
    door_boxes.append(((X0 + 0.03, a1 - 0.08, 0.6), (0.04, 0.035, 0.035), M["steel"]))           # knob (inside)
    door_boxes.append(((X0 - T / 2 - 0.035, a1 - 0.08, 0.6), (0.04, 0.035, 0.035), M["steel"]))   # knob (outside)
    add((-0.65, Y1 - 0.08, 1.15), (0.8, 0.16, 0.03), "trim")       # shelf of books and a jar
    xb = -1.0
    for k, (w_, h_) in enumerate(((0.05, 0.2), (0.04, 0.17), (0.06, 0.22), (0.05, 0.15), (0.045, 0.19), (0.05, 0.21), (0.04, 0.16))):
        add((xb + w_ / 2, Y1 - 0.08, 1.165 + h_ / 2), (w_ - 0.004, 0.13, h_), M["face"] + 1 + k % 5)
        xb += w_
    add((-0.45, Y1 - 0.08, 1.23), (0.09, 0.09, 0.13), "pot")
    add((1.12, Y1 - 0.01, 1.55), (0.2, 0.03, 0.2), "log2")          # clock
    add((1.12, Y1 - 0.03, 1.55), (0.16, 0.02, 0.16), "face")
    add((1.12, Y1 - 0.045, 1.58), (0.012, 0.01, 0.07), "ink")
    add((1.145, Y1 - 0.045, 1.55), (0.05, 0.01, 0.012), "ink")
    add((0.0, 0.25, 0.006), (1.5, 1.1, 0.006), "rug")               # rug under the table and chair
    add((1.15, 1.35, 0.12), (0.2, 0.2, 0.24), "pot")                 # potted plant in the back-right corner
    for c, sz in (((1.15, 1.35, 0.36), (0.26, 0.26, 0.2)), ((1.1, 1.3, 0.5), (0.16, 0.16, 0.14)), ((1.2, 1.4, 0.55), (0.12, 0.12, 0.12))):
        add(c, sz, "leaf")
    mats = [log, log2, plank, plank2, trim, door, rug, steel, leaf, pot, face, ink] + misc
    o = VK.mesh_obj("Cabin", boxes, mats, coll=sc.collection)
    hinge = (X0 - T / 2 + 0.02, a0, 0.0)                         # the door's west-wall edge at y = 0.45
    door = VK.mesh_obj("CabinDoor", [((c[0] - hinge[0], c[1] - hinge[1], c[2]), sz, mi) for c, sz, mi in door_boxes], mats,
                       coll=sc.collection)
    door.location = hinge
    if roof:                                                     # seen from outside only: casts no shadow, lights nothing
        rb = []
        for k, x in enumerate([X0 - 0.3 + 0.25 * i for i in range(14)]):
            rb.append(((x + 0.125, (Y0 + Y1) / 2 + 0.1, 2.06 + 0.02 * (k % 2)), (0.25, Y1 - Y0 + 0.6, 0.12), M["log2" if k % 2 else "log"]))
        r = VK.mesh_obj("CabinRoof", rb, mats, coll=sc.collection)
        for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
            setattr(r, attr, False)
    return o, door


def build_clouds_pass(sc, W, fps):
    """'clouds_pass': [[t_mid, half_width_s, depth]] -- a cloud slides over the sun: sunlight and sky dim, then recover."""
    sun, bg = sc.objects["Sun"].data, sc.world.node_tree.nodes["Background"].inputs["Strength"]
    e0, s0 = sun.energy, bg.default_value
    keys = [(0.0, 1.0)]
    for tm, hw, depth in W["clouds_pass"]:
        keys += [(tm - hw, 1.0), (tm - hw * 0.4, 1 - depth), (tm + hw * 0.4, 1 - depth), (tm + hw, 1.0)]
    for t, k in sorted(keys):
        f = max(0, round(t * fps))
        sun.energy = e0 * k; sun.keyframe_insert("energy", frame=f)
        bg.default_value = s0 * (0.55 + 0.45 * k); bg.keyframe_insert("default_value", frame=f)


def build_leaves(sc, L, fps, nf):
    """'leaves': {"at": [x, y], "r": m, "n": count, "t0": s, "t1": s} -- a breeze shakes leaves down: they flutter and land."""
    r = random.Random(77)
    mats = [VK.mat("LeafFall%d" % k, c, 0.8) for k, c in enumerate(((0.30, 0.55, 0.20), (0.62, 0.62, 0.18), (0.70, 0.42, 0.12)))]
    for k in range(L.get("n", 14)):
        o = VK.mesh_obj("Leaf_%02d" % k, [((0, 0, 0), (0.045, 0.03, 0.006), 0)], [mats[k % 3]], coll=sc.collection)
        a, rad = r.uniform(0, 2 * math.pi), r.uniform(0.2, L.get("r", 2.0))
        x0, y0, z0 = L["at"][0] + rad * math.cos(a), L["at"][1] + rad * math.sin(a), r.uniform(1.7, 2.6)
        ts = r.uniform(L["t0"], L["t1"])
        fall = r.uniform(3.0, 4.5)
        drift = (r.uniform(0.2, 0.6), r.uniform(-0.3, 0.3))
        ph = r.uniform(0, 6.3)
        for f in range(nf):
            t = f / fps
            if t < ts - 0.05:
                if f == 0:
                    o.scale = (0, 0, 0); o.keyframe_insert("scale", frame=0)
                continue
            u = min(1.0, (t - ts) / fall)
            o.scale = (1, 1, 1)
            o.location = (x0 + drift[0] * u + 0.08 * math.sin(2 * math.pi * 0.9 * (t - ts) + ph), y0 + drift[1] * u,
                          z0 + (0.012 - z0) * u)
            o.rotation_euler = ((0.9 * math.sin(2 * math.pi * 1.1 * (t - ts) + ph)) * (1 - u), (0.6 * math.cos(2 * math.pi * 0.8 * (t - ts))) * (1 - u), ph + 2 * u)
            for path in ("scale", "location", "rotation_euler"):
                o.keyframe_insert(path, frame=f)
            if u >= 1.0:
                break
        VK.set_interp(o, "LINEAR")


def build_rabbit(sc, c, fps, nf):
    """A voxel rabbit following a keyed path (bl_common.critter_state): hops, ears that twitch, sits and looks."""
    fur, belly = VK.mat("RabbitFur", (0.55, 0.45, 0.36), 0.95), VK.mat("RabbitBelly", (0.92, 0.90, 0.86), 0.95)
    eye, pink = VK.mat("RabbitEye", (0.05, 0.04, 0.04), 0.3), VK.mat("RabbitPink", (0.95, 0.62, 0.66), 0.6)
    root = bpy.data.objects.new("Rabbit", None)
    sc.collection.objects.link(root)
    VK.mesh_obj("RabbitBody", [((0, 0, 0.07), (0.10, 0.17, 0.11), 0), ((0, -0.085, 0.06), (0.07, 0.01, 0.07), 1),
                               ((0, 0.10, 0.08), (0.05, 0.04, 0.05), 1),                       # tail
                               ((-0.035, -0.07, 0.015), (0.03, 0.06, 0.03), 0), ((0.035, -0.07, 0.015), (0.03, 0.06, 0.03), 0)],
                [fur, belly], parent=root, coll=sc.collection)
    head = VK.mesh_obj("RabbitHead", [((0, 0, 0), (0.085, 0.085, 0.08), 0), ((-0.03, -0.044, 0.012), (0.014, 0.004, 0.016), 2),
                                      ((0.03, -0.044, 0.012), (0.014, 0.004, 0.016), 2), ((0, -0.045, -0.015), (0.014, 0.004, 0.01), 3)],
                       [fur, belly, eye, pink], parent=root, coll=sc.collection)
    head.location = (0, -0.11, 0.15)
    ears = []
    for sx in (-1, 1):
        e = VK.mesh_obj("RabbitEar", [((0, 0, 0.06), (0.022, 0.012, 0.12), 0), ((0, -0.007, 0.06), (0.012, 0.004, 0.09), 1)],
                        [fur, pink], parent=head, coll=sc.collection)
        e.location = (0.022 * sx, 0.01, 0.035); ears.append(e)
    import bl_common as Cm
    vis = c.get("visible", [-1e9, 1e9])                              # [t_in, t_out]: hidden in the bushes outside that
    for f in range(nf):
        t = f / fps
        x, y, z, hd, moving = Cm.critter_state(c, t)
        k = 1.0 if vis[0] <= t <= vis[1] else 0.0
        root.scale = (k, k, k); root.keyframe_insert("scale", frame=f)
        root.location = (x, y, z)
        root.rotation_euler = (0, 0, hd + math.pi / 2)              # the rabbit's nose is local -y
        root.keyframe_insert("location", frame=f); root.keyframe_insert("rotation_euler", frame=f)
        tw = 0.0 if moving else 0.25 * max(0.0, math.sin(2 * math.pi * 0.6 * t)) ** 8     # ear twitch while sitting
        for k, e in enumerate(ears):
            e.rotation_euler = (-0.35 if moving else 0.0 + tw * (1 if k else -1), 0, 0)
            e.keyframe_insert("rotation_euler", frame=f)
        head.rotation_euler = (0, 0, 0 if moving else 0.35 * math.sin(2 * math.pi * 0.25 * t)); head.keyframe_insert("rotation_euler", frame=f)
    for o in [root, head] + ears:
        VK.set_interp(o, "LINEAR")


def build_world(sc, P):
    """Ground, props, sky, light, weather and animals for P['world']. Returns the view exposure to use."""
    W = P["world"]
    fps = P["fps"]
    EXTEND[0] = W.get("terrain") == "forest_west"
    build_ground(sc, W["ground"])
    exposure = build_sky(sc, W["time"], W["weather"])
    if W.get("sun"):                                    # story override: the direction sunlight travels
        sc.objects["Sun"].rotation_quaternion = Vector(W["sun"]).normalized().to_track_quat("-Z", "Y")
    exposure += float(W.get("exposure", 0.0))
    if W.get("interior") == "cabin":
        _, door = build_cabin(sc, roof=bool(W.get("roof", False)))
        if W.get("door_open"):                                  # [t0, t1, degrees]: swings outward on its hinge
            t0, t1, deg = W["door_open"]
            if t1 <= 0:                                         # already open when the scene starts
                door.rotation_euler = (0, 0, math.radians(deg))
            else:
                door.rotation_euler = (0, 0, 0); door.keyframe_insert("rotation_euler", index=2, frame=max(0, round(t0 * fps)))
                door.rotation_euler = (0, 0, math.radians(deg)); door.keyframe_insert("rotation_euler", index=2, frame=round(t1 * fps))
    if W.get("terrain") == "forest_west":
        build_forest_west(sc, fps)
    if W.get("clouds_pass"):
        build_clouds_pass(sc, W, fps)
    if W.get("leaves"):
        build_leaves(sc, W["leaves"], fps, P["nf"])
    for c in W.get("critters", []):
        if c["kind"] == "rabbit":
            build_rabbit(sc, c, fps, P["nf"])
        elif c["kind"] in ("boar", "tobias"):                        # the cast beyond Grandpa (bl_cast)
            import bl_cast
            if c["kind"] == "boar":
                bl_cast.build_boar_actor(sc, c, fps, P["nf"])
            else:
                import bl_common as Cm
                dlg = os.path.join(Cm.BUILD, "dialogue.json")
                mouths = json.load(open(dlg)).get("mouths", {}) if os.path.exists(dlg) else {}
                bl_cast.build_tobias_actor(sc, c, fps, P["nf"], mouths.get("tobias"))
    if W["weather"] in ("clouds", "rain", "snow"):
        build_clouds(sc, P["nf"], dark=W["weather"] == "rain")
    if W["weather"] in ("rain", "snow"):
        build_precip(sc, W["weather"], fps)
    for a in W["animals"]:
        if a in ("birds", "seagulls", "pigeons"):
            build_birds(sc, fps, gulls=a == "seagulls", pigeons=a == "pigeons")
        elif a == "cat":
            build_cat(sc, fps, cat_spot(P))
    return exposure
