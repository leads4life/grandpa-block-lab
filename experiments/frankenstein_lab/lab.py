"""Frankenstein lab -- a standalone look test (NOT part of the Grandpa engine; it only borrows voxelkit's block helpers).
Mary Shelley, Frankenstein (1818), chapter 5. The Creature follows the book (yellowish skin, black hair, black lips,
watery eyes), not the 1931 film.

    python3 lab.py                      # builds lab.blend (bpy module)
    python3 lab.py --render 40 10       # + renders frames/NNNN.png at 40 % with 10 samples
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, "/home/user/blocklab")
import voxelkit as VK  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
V = json.load(open(os.path.join(HERE, "voice.json")))
P = {p["id"]: p for p in V["parts"]}
NF = int(V["total"] * FPS)
T_OPEN = P["eye"]["end"] - 0.55            # "...the dull yellow eye of the creature open"
T_BREATH = P["limbs"]["start"]
T_RECOIL = P["limbs"]["start"] + 3.0
FLASHES = [1.0, 5.3, 16.2, 22.1, T_OPEN - 0.1, 36.4, 41.0, 41.35]
rnd = random.Random(1818)
f = lambda t: int(round(t * FPS))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 0, NF - 1

# ------------------------------------------------------------------ materials
stone = VK.pixel_material("Stone", (0.20, 0.19, 0.18), (0.36, 0.34, 0.31), 0.1 / 8, voxel=0.1)
floor = VK.pixel_material("Floor", (0.16, 0.14, 0.12), (0.30, 0.27, 0.23), 0.1 / 8, voxel=0.1)
wood = VK.pixel_material("Wood", (0.17, 0.10, 0.05), (0.32, 0.20, 0.10), 0.1 / 8)
beam = VK.pixel_material("Beam", (0.10, 0.06, 0.03), (0.20, 0.12, 0.06), 0.1 / 8)
glass = VK.mat("Glass", (0.55, 0.70, 0.65), rough=0.08)
glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.9
copper = VK.mat("Copper", (0.72, 0.38, 0.20), rough=0.35, metal=1.0)
brass = VK.mat("Brass", (0.70, 0.55, 0.25), rough=0.3, metal=1.0)
iron = VK.mat("Iron", (0.12, 0.12, 0.13), rough=0.5, metal=0.8)
paper = VK.mat("Paper", (0.80, 0.74, 0.60), rough=0.9)
book_cols = [VK.mat("Book%d" % i, c, rough=0.8) for i, c in enumerate([(0.35, 0.06, 0.05), (0.08, 0.18, 0.10), (0.10, 0.10, 0.25), (0.30, 0.22, 0.08)])]
jar_cols = [VK.emission_material("Jar%d" % i, c, 0.4) for i, c in enumerate([(0.3, 0.8, 0.3), (0.9, 0.6, 0.2), (0.4, 0.5, 0.9)])]
wax = VK.mat("Wax", (0.90, 0.86, 0.72), rough=0.6)
flame = VK.emission_material("Flame", (1.0, 0.62, 0.22), 25.0)
spark = VK.emission_material("Spark", (0.65, 0.80, 1.0), 40.0)
bolt_m = VK.emission_material("Bolt", (0.85, 0.90, 1.0), 60.0)
rain_m = VK.emission_material("Rain", (0.55, 0.62, 0.75), 0.6)
cloth = VK.pixel_material("Sheet", (0.55, 0.53, 0.48), (0.72, 0.70, 0.64), 0.05 / 8)
# Victor
coat = VK.mat("Coat", (0.06, 0.07, 0.13), rough=0.7)
shirt = VK.mat("Shirt", (0.88, 0.86, 0.80), rough=0.8)
trousers = VK.mat("Trousers", (0.16, 0.15, 0.14), rough=0.8)
boots = VK.mat("Boots", (0.04, 0.03, 0.03), rough=0.5)
skin_v = VK.mat("SkinV", (0.86, 0.68, 0.56), rough=0.7)
hair_v = VK.mat("HairV", (0.22, 0.13, 0.07), rough=0.8)
dark = VK.mat("Dark", (0.02, 0.02, 0.02), rough=0.5)
white = VK.mat("EyeWhite", (0.90, 0.88, 0.82), rough=0.4)
# the Creature, as Shelley describes him
skin_c = VK.pixel_material("SkinC", (0.62, 0.55, 0.26), (0.78, 0.70, 0.38), 0.05 / 8, rough=0.75)
hair_c = VK.mat("HairC", (0.02, 0.02, 0.03), rough=0.35)
lips_c = VK.mat("LipsC", (0.04, 0.03, 0.04), rough=0.4)
iris_c = VK.mat("IrisC", (0.72, 0.62, 0.20), rough=0.3)
eyew_c = VK.mat("EyeWhiteC", (0.80, 0.78, 0.66), rough=0.15)
rags = VK.pixel_material("Rags", (0.10, 0.09, 0.08), (0.20, 0.18, 0.15), 0.05 / 8)


def obj(name, boxes, mats, parent=None, loc=(0, 0, 0)):
    o = VK.mesh_obj(name, boxes, mats, parent=parent)
    o.location = loc
    return o


def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    sc.collection.objects.link(e)
    e.location = loc
    if parent:
        e.parent = parent
    return e


def key(o, path, frame, value, index=-1):
    setattr(o, path, value) if index < 0 else getattr(o, path).__setitem__(index, value)
    o.keyframe_insert(path, frame=frame, index=index)


def show(o, frame, on):
    o.hide_render = not on
    o.keyframe_insert("hide_render", frame=frame)
    o.hide_viewport = not on
    o.keyframe_insert("hide_viewport", frame=frame)


# ------------------------------------------------------------------ the room
W, D, H = 5.0, 4.4, 3.4                     # x from -2.5 to 2.5, y from -2.5 to 1.9 (back wall), height
BACK = 1.9
WIN = (0.55, 1.65, 1.35, 2.55)              # window x0, x1, z0, z1 in the back wall
room = [((0, -0.3, -0.05), (W, D, 0.1), 0)]                                       # floor
for zz in (0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.15):                              # back wall in courses, around the window
    h = 0.5 if zz < 3.0 else 0.3
    if WIN[2] < zz < WIN[3]:
        room += [(((-2.5 + WIN[0]) / 2, BACK + 0.1, zz), (WIN[0] + 2.5, 0.2, h), 1), (((WIN[1] + 2.5) / 2, BACK + 0.1, zz), (2.5 - WIN[1], 0.2, h), 1)]
    else:
        room.append(((0, BACK + 0.1, zz), (W, 0.2, h), 1))
room += [((-2.6, -0.3, H / 2), (0.2, D, H), 1), ((2.6, -0.3, H / 2), (0.2, D, H), 1), ((0, -0.3, H + 0.05), (W + 0.4, D, 0.1), 1)]
obj("Room", room, [floor, stone])
beams = [((x, -0.3, H - 0.1), (0.18, D, 0.2), 0) for x in (-1.6, -0.2, 1.2)]
win_frame = [((sum(WIN[:2]) / 2, BACK, WIN[2]), (WIN[1] - WIN[0] + 0.1, 0.25, 0.08), 0), ((sum(WIN[:2]) / 2, BACK, WIN[3]), (WIN[1] - WIN[0] + 0.1, 0.25, 0.08), 0),
             ((WIN[0], BACK, sum(WIN[2:]) / 2), (0.08, 0.25, WIN[3] - WIN[2]), 0), ((WIN[1], BACK, sum(WIN[2:]) / 2), (0.08, 0.25, WIN[3] - WIN[2]), 0),
             ((sum(WIN[:2]) / 2, BACK, sum(WIN[2:]) / 2), (0.05, 0.12, WIN[3] - WIN[2]), 0), ((sum(WIN[:2]) / 2, BACK, sum(WIN[2:]) / 2), (WIN[1] - WIN[0], 0.12, 0.05), 0)]
obj("Beams", beams + win_frame, [beam])
pane = obj("Pane", [((sum(WIN[:2]) / 2, BACK + 0.02, sum(WIN[2:]) / 2), (WIN[1] - WIN[0], 0.01, WIN[3] - WIN[2]), 0)], [glass])

# outside: the storm sky, rain, lightning
sky_m = VK.emission_material("Sky", (0.05, 0.07, 0.14), 1.0)
sky = obj("Sky", [((1.1, 6.0, 2.0), (12, 0.1, 9), 0)], [sky_m])
sky_strength = sky_m.node_tree.nodes["Emission"].inputs["Strength"] if "Emission" in sky_m.node_tree.nodes else None
streaks = []
for i in range(2600):
    x = rnd.uniform(WIN[0] - 0.5, WIN[1] + 0.5)
    z = rnd.uniform(-1.0, 46.0)
    streaks.append(((x, rnd.uniform(2.3, 3.6), z), (0.008, 0.008, rnd.uniform(0.12, 0.25)), 0))
rain = obj("Rain", streaks, [rain_m])
rain.location = (0, 0, 0)
key(rain, "location", 0, (0, 0, 0)); key(rain, "location", NF, (0, 0, -NF / FPS * 9.0))
for fc in VK.fcurves_of(rain):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
pts, x, z = [], 1.0, 9.0                    # a jagged bolt
while z > -1:
    nx, nz = x + rnd.uniform(-0.6, 0.6), z - rnd.uniform(0.5, 1.0)
    for k in range(6):
        u = k / 6
        pts.append(((x + (nx - x) * u, 5.8, z + (nz - z) * u), (0.07, 0.05, 0.22), 0))
    x, z = nx, nz
bolt = obj("Bolt", pts, [bolt_m])
flash = bpy.data.lights.new("Flash", "AREA")
flash.size, flash.color = 2.0, (0.75, 0.82, 1.0)
fl = bpy.data.objects.new("FlashLight", flash)
sc.collection.objects.link(fl)
fl.location = (1.1, 1.3, 2.0)
fl.rotation_euler = (math.radians(100), 0, math.radians(180))
show(bolt, 0, False)
flash.energy = 0
flash.keyframe_insert("energy", frame=0)
for tf in FLASHES:                         # two quick pulses per strike
    for dt, e, b in ((0.0, 0, False), (0.03, 900, True), (0.1, 150, True), (0.16, 700, True), (0.3, 0, False)):
        flash.energy = e
        flash.keyframe_insert("energy", frame=f(tf + dt))
        show(bolt, f(tf + dt), b)
        if sky_strength is not None:
            sky_strength.default_value = 1.0 + e / 60.0
            sky_strength.keyframe_insert("default_value", frame=f(tf + dt))

# ------------------------------------------------------------------ furniture and apparatus
TABLE = (0.0, 0.35)
tbl = [((TABLE[0], TABLE[1], 0.82), (2.5, 1.0, 0.1), 0)] + [((TABLE[0] + sx * 1.1, TABLE[1] + sy * 0.4, 0.39), (0.1, 0.1, 0.78), 0)
                                                              for sx in (-1, 1) for sy in (-1, 1)]
obj("Table", tbl, [wood])
bench = [((-1.85, 1.35, 0.78), (1.2, 0.7, 0.08), 0)] + [((-1.85 + sx * 0.52, 1.35 + sy * 0.28, 0.37), (0.08, 0.08, 0.74), 0)
                                                        for sx in (-1, 1) for sy in (-1, 1)]
obj("Bench", bench, [wood])
app = []
for i, xx in enumerate((-2.25, -2.05, -1.85)):                                   # Leyden jars: glass, copper caps and rods
    app += [((xx, 1.45, 0.98), (0.14, 0.14, 0.32), 0), ((xx, 1.45, 1.16), (0.15, 0.15, 0.04), 1), ((xx, 1.45, 1.26), (0.02, 0.02, 0.18), 1),
            ((xx, 1.45, 1.36), (0.06, 0.06, 0.06), 2)]
for k in range(9):                                                              # the coil
    app.append(((-1.5, 1.35, 0.86 + k * 0.05), (0.26, 0.26, 0.025), 1))
app += [((-1.5, 1.35, 0.82 + 0.25), (0.08, 0.08, 0.5), 3), ((-1.5, 1.35, 1.38), (0.12, 0.12, 0.12), 2),   # core + brass ball
        ((-1.28, 1.35, 1.38), (0.1, 0.1, 0.1), 2), ((-1.28, 1.35, 1.1), (0.03, 0.03, 0.5), 3)]
app += [((-1.28 + (0.0 + 1.28) * u, 1.35 + (TABLE[1] + 0.3 - 1.35) * u, 0.86), (0.04, 0.04, 0.04), 3) for u in [k / 24 for k in range(25)]]   # a cable to the table
obj("Apparatus", app, [glass, copper, brass, iron])
sparks = []
for k in range(4):
    s = obj("Spark%d" % k, [((-1.39 + 0.02 * k, 1.35, 1.38 + rnd.uniform(-0.03, 0.03)), (0.11, 0.015, 0.015), 0)], [spark])
    sparks.append(s)
spark_l = bpy.data.lights.new("SparkLight", "POINT")
spark_l.color, spark_l.shadow_soft_size = (0.6, 0.75, 1.0), 0.05
slo = bpy.data.objects.new("SparkLightO", spark_l)
sc.collection.objects.link(slo)
slo.location = (-1.39, 1.25, 1.4)
spark_times = [t for t in [P["spark"]["start"] + 3.4 + 0.11 * k for k in range(60)] if rnd.random() < 0.55] + \
              [T_OPEN + 0.04 * k for k in range(12) if rnd.random() < 0.7]
for s in sparks:
    show(s, 0, False)
spark_l.energy = 0
spark_l.keyframe_insert("energy", frame=0)
for t in spark_times:
    s = rnd.choice(sparks)
    show(s, f(t), True); show(s, f(t) + 2, False)
    spark_l.energy = 60; spark_l.keyframe_insert("energy", frame=f(t))
    spark_l.energy = 0; spark_l.keyframe_insert("energy", frame=f(t) + 2)
shelf = []
for zz in (1.2, 1.7, 2.2):                                                       # shelves on the left wall, jars and books
    shelf.append(((-2.38, -0.6, zz), (0.24, 1.6, 0.05), 0))
obj("Shelves", shelf, [wood])
jars, books = [], []
for zz in (1.2, 1.7, 2.2):
    y = -1.3
    while y < 0.1:
        if rnd.random() < 0.5:
            h = rnd.uniform(0.14, 0.26)
            jars.append(((-2.38, y, zz + 0.025 + h / 2), (0.12, 0.12, h), rnd.randrange(3)))
            y += 0.18
        else:
            for b in range(rnd.randint(3, 6)):
                h = rnd.uniform(0.18, 0.26)
                books.append(((-2.36, y, zz + 0.025 + h / 2), (0.18, 0.045, h), rnd.randrange(4)))
                y += 0.05
            y += 0.06
obj("Jars", jars, jar_cols)
obj("Books", books, book_cols)
obj("Papers", [((0.9, -0.05, 0.875), (0.3, 0.22, 0.01), 0), ((-0.9, 0.7, 0.875), (0.28, 0.2, 0.01), 0)], [paper])

# the candle, nearly burnt out, at the head of the table
CANDLE = (1.0, -0.05)
obj("Candle", [((CANDLE[0], CANDLE[1], 0.9), (0.06, 0.06, 0.06), 0), ((CANDLE[0], CANDLE[1], 0.875), (0.14, 0.14, 0.015), 1)], [wax, brass])
fl_o = obj("Flame", [((0, 0, 0), (0.025, 0.025, 0.05), 0)], [flame], loc=(CANDLE[0], CANDLE[1], 0.965))
cl = bpy.data.lights.new("CandleLight", "POINT")
cl.color, cl.shadow_soft_size = (1.0, 0.62, 0.30), 0.03
clo = bpy.data.objects.new("CandleLightO", cl)
sc.collection.objects.link(clo)
clo.location = (CANDLE[0], CANDLE[1] - 0.05, 1.02)
for fr in range(0, NF, 3):                  # flicker, getting weaker as it burns out
    dim = 1.0 - 0.35 * fr / NF
    cl.energy = (24 + rnd.uniform(-7, 7)) * dim
    cl.keyframe_insert("energy", frame=fr)
    s = 1 + rnd.uniform(-0.25, 0.25)
    fl_o.scale = (1, 1, s * dim)
    fl_o.keyframe_insert("scale", frame=fr)
fill = bpy.data.lights.new("Fill", "AREA")
fill.energy, fill.size, fill.color = 10, 3.0, (0.40, 0.50, 0.85)
fo = bpy.data.objects.new("FillO", fill)
sc.collection.objects.link(fo)
fo.location = (0.5, -2.2, 2.6)
fo.rotation_euler = (math.radians(55), 0, 0)
world = bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.025, 0.05, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.06

# ------------------------------------------------------------------ Victor Frankenstein
vic = empty("Victor", (-1.15, -0.45, 0))
vic.rotation_euler = (0, 0, math.radians(50))                                    # facing the table, three-quarters to us
obj("VicBody", [((-0.08, 0, 0.42), (0.13, 0.15, 0.62), 0), ((0.08, 0, 0.42), (0.13, 0.15, 0.62), 0),
                ((-0.08, -0.01, 0.06), (0.15, 0.2, 0.12), 1), ((0.08, -0.01, 0.06), (0.15, 0.2, 0.12), 1),
                ((0, 0, 0.82), (0.44, 0.26, 0.36), 2), ((0, 0, 1.12), (0.42, 0.24, 0.44), 2),
                ((0, -0.122, 1.18), (0.12, 0.01, 0.32), 3), ((0, -0.125, 1.33), (0.15, 0.02, 0.07), 3),
                ((-0.13, -0.122, 1.22), (0.1, 0.01, 0.2), 2), ((0.13, -0.122, 1.22), (0.1, 0.01, 0.2), 2)],
    [trousers, boots, coat, shirt], parent=vic)
vhead = obj("VicHead", [((0, 0, 0.14), (0.26, 0.26, 0.28), 0), ((0, 0.02, 0.29), (0.28, 0.28, 0.07), 1), ((0, 0.12, 0.17), (0.28, 0.06, 0.24), 1),
                        ((-0.06, -0.131, 0.16), (0.045, 0.01, 0.045), 2), ((0.06, -0.131, 0.16), (0.045, 0.01, 0.045), 2),
                        ((-0.06, -0.131, 0.21), (0.06, 0.01, 0.015), 1), ((0.06, -0.131, 0.21), (0.06, 0.01, 0.015), 1),
                        ((0, -0.131, 0.05), (0.08, 0.01, 0.02), 2)], [skin_v, hair_v, dark], parent=vic, loc=(0, 0, 1.36))
arms = {}
for side, sx in (("L", 0.27), ("R", -0.27)):
    sh = empty("VicSh" + side, (sx, 0, 1.3), parent=vic)
    obj("VicArm" + side, [((0, 0, -0.27), (0.13, 0.14, 0.56), 0), ((0, 0, -0.6), (0.1, 0.1, 0.1), 1)], [coat, skin_v], parent=sh)
    arms[side] = sh
# anxious waiting, then the recoil: a step back, a hand up to his face, his head turned away a little
key(vic, "location", 0, (-1.15, -0.45, 0)); key(vic, "location", f(T_RECOIL), (-1.15, -0.45, 0))
key(vic, "location", f(T_RECOIL + 0.6), (-1.55, -0.75, 0))
key(arms["R"], "rotation_euler", 0, (0, 0, 0)); key(arms["R"], "rotation_euler", f(T_RECOIL), (0, 0, 0))
key(arms["R"], "rotation_euler", f(T_RECOIL + 0.5), (math.radians(-150), 0, math.radians(-25)))
key(arms["L"], "rotation_euler", 0, (math.radians(-35), 0, 0)); key(arms["L"], "rotation_euler", f(P["spark"]["start"] + 3.0), (math.radians(-35), 0, 0))
key(arms["L"], "rotation_euler", f(P["spark"]["start"] + 3.6), (math.radians(-70), 0, math.radians(15)))
key(arms["L"], "rotation_euler", f(T_RECOIL), (math.radians(-70), 0, math.radians(15)))
key(arms["L"], "rotation_euler", f(T_RECOIL + 0.4), (math.radians(-20), 0, math.radians(-10)))
key(vhead, "rotation_euler", 0, (0, 0, 0)); key(vhead, "rotation_euler", f(T_OPEN + 0.4), (math.radians(8), 0, 0))
key(vhead, "rotation_euler", f(T_RECOIL), (math.radians(8), 0, 0)); key(vhead, "rotation_euler", f(T_RECOIL + 0.5), (math.radians(-6), 0, math.radians(18)))

# ------------------------------------------------------------------ the Creature (lying on the table, head toward the candle)
cre = empty("Creature", (TABLE[0], TABLE[1], 0.87))
torso = obj("CreTorso", [((0.15, 0, 0.13), (0.78, 0.5, 0.26), 0), ((0.15, 0, 0.16), (0.8, 0.52, 0.2), 1)], [skin_c, rags], parent=cre)
obj("CreLegs", [((-0.62, -0.12, 0.11), (0.85, 0.2, 0.22), 0), ((-0.62, 0.12, 0.11), (0.85, 0.2, 0.22), 0), ((-1.1, -0.12, 0.13), (0.12, 0.2, 0.26), 1),
                ((-1.1, 0.12, 0.13), (0.12, 0.2, 0.26), 1), ((-0.45, 0, 0.17), (1.2, 0.56, 0.2), 2)], [rags, skin_c, cloth], parent=cre)
chead = empty("CreHeadPivot", (0.62, 0, 0.14), parent=cre)
obj("CreHead", [((0.18, 0, 0.0), (0.36, 0.36, 0.30), 0),                                       # head, face up (+z), crown at +x
                ((0.13, 0, 0.165), (0.07, 0.05, 0.04), 0),                                                  # nose
                ((0.33, 0, 0.06), (0.08, 0.38, 0.2), 1), ((0.2, 0.2, -0.06), (0.3, 0.05, 0.14), 1), ((0.2, -0.2, -0.06), (0.3, 0.05, 0.14), 1),
                ((0.5, 0, -0.12), (0.32, 0.56, 0.035), 1), ((0.66, 0, -0.3), (0.05, 0.42, 0.36), 1),       # long black hair: on the table, over the edge
                ((0.28, -0.075, 0.156), (0.03, 0.1, 0.014), 1), ((0.28, 0.075, 0.156), (0.03, 0.1, 0.014), 1),   # brows
                ((0.05, 0, 0.152), (0.035, 0.13, 0.014), 2)],                                              # straight black lips
    [skin_c, hair_c, lips_c], parent=chead)
eyes = obj("CreEyes", [((0.22, -0.075, 0.152), (0.065, 0.085, 0.01), 0), ((0.22, 0.075, 0.152), (0.065, 0.085, 0.01), 0),
                       ((0.22, -0.075, 0.156), (0.04, 0.045, 0.01), 1), ((0.22, 0.075, 0.156), (0.04, 0.045, 0.01), 1),
                       ((0.22, -0.075, 0.158), (0.018, 0.02, 0.01), 2), ((0.22, 0.075, 0.158), (0.018, 0.02, 0.01), 2)],
           [eyew_c, iris_c, dark], parent=chead)
lids = obj("CreLids", [((0.0, -0.075, 0.0), (0.075, 0.095, 0.014), 0), ((0.0, 0.075, 0.0), (0.075, 0.095, 0.014), 0)], [skin_c],
           parent=chead, loc=(0.22, 0, 0.162))
key(lids, "location", 0, (0.22, 0, 0.162)); key(lids, "location", f(T_OPEN), (0.22, 0, 0.162))
key(lids, "location", f(T_OPEN + 0.35), (0.255, 0, 0.162))                    # the lids slide up toward the brow...
key(lids, "scale", 0, (1, 1, 1)); key(lids, "scale", f(T_OPEN), (1, 1, 1)); key(lids, "scale", f(T_OPEN + 0.35), (0.15, 1, 1))
carm = {}
for side, sy in (("N", -0.3), ("F", 0.3)):
    sh = empty("CreSh" + side, (0.45, sy, 0.12), parent=cre)
    obj("CreArm" + side, [((-0.35, 0, 0.0), (0.7, 0.16, 0.16), 0), ((-0.75, 0, 0.0), (0.12, 0.14, 0.1), 0)], [skin_c], parent=sh)
    carm[side] = sh
# "it breathed hard": the chest heaves; "a convulsive motion agitated its limbs": jerks of the arm, legs and head
for fr in range(0, NF):
    t = fr / FPS
    if fr % 2:
        continue
    b = 0.0 if t < T_BREATH - 0.6 else min(1.0, (t - (T_BREATH - 0.6)) / 0.8)
    s = 1 + b * 0.09 * (0.5 + 0.5 * math.sin(2 * math.pi * 1.1 * t))
    torso.scale = (1, 1 + b * 0.03, s); torso.keyframe_insert("scale", frame=fr)
for t0 in (T_BREATH + 0.9, T_BREATH + 1.7, T_BREATH + 2.3, T_BREATH + 3.4):
    for part, ax, amt in ((carm["N"], 0, -25), (chead, 1, 9), (carm["F"], 0, 18)):
        r0 = list(part.rotation_euler)
        key(part, "rotation_euler", f(t0) - 1, tuple(r0))
        r1 = list(r0); r1[ax] = math.radians(amt * rnd.uniform(0.6, 1.2))
        key(part, "rotation_euler", f(t0) + 2, tuple(r1))
        key(part, "rotation_euler", f(t0) + 7, tuple(r0))
key(chead, "rotation_euler", f(T_OPEN), (0, 0, 0)); key(chead, "rotation_euler", f(T_OPEN + 0.5), (0, 0, math.radians(-14)))   # turns toward Victor

# ------------------------------------------------------------------ camera: vertical shots, a cut on each phrase
cam_d = bpy.data.cameras.new("Cam")
cam_d.lens, cam_d.sensor_fit, cam_d.sensor_width, cam_d.clip_start = 32, "HORIZONTAL", 36, 0.02
cam = bpy.data.objects.new("Camera", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
tgt = empty("CamTarget")
con = cam.constraints.new("TRACK_TO")
con.target, con.track_axis, con.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
HEAD = Vector((TABLE[0] + 0.80, TABLE[1], 1.01))
SHOTS = [  # (start time, eye from, eye to, target from, target to)
    (0.0, (0.2, -2.35, 1.5), (0.1, -1.85, 1.4), (0.3, 1.0, 1.55), (0.2, 0.6, 1.25)),                  # the lab, the storm window
    (P["spark"]["start"], (-1.0, 0.3, 1.25), (-1.05, 0.55, 1.3), (-1.7, 1.4, 1.15), (-1.6, 1.4, 1.2)),   # the apparatus
    (P["spark"]["start"] + 6.4, (-0.55, -1.25, 1.62), (-0.62, -1.15, 1.62), (-1.05, -0.45, 1.5), (-1.08, -0.45, 1.52)),  # Victor
    (P["candle"]["start"], (1.05, 0.6, 1.75), (1.05, 0.9, 1.8), (1.1, 1.9, 1.9), (1.1, 1.9, 1.95)),     # the rain on the panes
    (P["candle"]["start"] + 4.0, (1.25, -0.45, 1.02), (1.2, -0.38, 1.0), (1.0, -0.05, 0.93), (1.0, -0.05, 0.93)),  # the candle
    (P["eye"]["start"], tuple(HEAD + Vector((-0.85, -0.3, 0.62))), tuple(HEAD + Vector((-0.7, -0.22, 0.55))), HEAD + Vector((0, 0, 0.12)), HEAD + Vector((0.02, 0, 0.12))),   # his face, seen from his feet (upright)
    (T_OPEN - 0.9, tuple(HEAD + Vector((-0.42, -0.06, 0.4))), tuple(HEAD + Vector((-0.38, -0.05, 0.37))), HEAD + Vector((0.06, -0.02, 0.15)), HEAD + Vector((0.06, -0.02, 0.15))),  # the eye
    (T_BREATH, (0.6, -1.3, 1.7), (0.5, -1.2, 1.6), (0.2, 0.35, 0.95), (0.1, 0.35, 0.95)),             # breathing, convulsing
    (T_RECOIL - 0.6, (0.1, -2.6, 1.55), (0.0, -2.9, 1.6), (-0.4, 0.2, 1.1), (-0.4, 0.2, 1.15))]       # Victor recoils
for i, (t0, e0, e1, g0, g1) in enumerate(SHOTS):
    t1 = SHOTS[i + 1][0] - 1 / FPS if i + 1 < len(SHOTS) else NF / FPS
    for fr, e, g in ((f(t0), e0, g0), (f(t1), e1, g1)):
        cam.location = e; cam.keyframe_insert("location", frame=fr)
        tgt.location = g; tgt.keyframe_insert("location", frame=fr)
for o in (cam, tgt):
    for fc in VK.fcurves_of(o):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
for o in bpy.data.objects:                  # every on/off key steps (no fading hide states)
    for fc in VK.fcurves_of(o):
        if fc.data_path.startswith("hide"):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------ render settings
r = sc.render
r.engine = "CYCLES"
r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
cy = sc.cycles
cy.device, cy.samples, cy.adaptive_threshold = "CPU", 16, 0.05
cy.use_denoising, cy.denoiser = True, "OPENIMAGEDENOISE"
cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 4, 2, 2, 4
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.view_settings.exposure = 0.45
r.use_persistent_data = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "lab.blend"))
print("built lab.blend: %d frames (%.1f s), eye opens at %.2f s" % (NF, NF / FPS, T_OPEN))

if "--render" in sys.argv:
    a = sys.argv[sys.argv.index("--render") + 1:]
    r.resolution_percentage, cy.samples = int(a[0]), int(a[1])
    frames = [int(x) for x in a[2:]] or list(range(NF))
    os.makedirs(os.path.join(HERE, "frames"), exist_ok=True)
    for fr in frames:
        p = os.path.join(HERE, "frames", "%04d.png" % fr)
        if os.path.exists(p):
            continue
        sc.frame_set(fr)
        r.filepath = p
        bpy.ops.render.render(write_still=True)
    print("rendered", len(frames), "frames")
