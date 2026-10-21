"""Shared voxel kit: materials, box meshes, rig math and the voxel grandpa (armature + rigid-skinned mesh, jaw bone).

Extracted from the earlier grandpa shorts so every lesson uses the identical character.
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

L_UP, L_FORE, L_THIGH, L_SHIN = 0.20, 0.225, 0.22, 0.24
BONE_ORDER = ("hips", "spine", "head", "jaw", "upper_arm.R", "forearm.R", "upper_arm.L", "forearm.L",
              "thigh.R", "shin.R", "thigh.L", "shin.L")


def cl(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = cl(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = cl(x)
    return x ** 3 * (x * (6 * x - 15) + 10)


def mat(name, color, rough=0.8, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


def pixel_material(name, c_dark, c_light, px, per_object=False, voxel=None, rough=0.9, metal=0.0, bump=0.12):
    """Minecraft-style pixel texture: position snapped to a texel grid -> white noise -> colour ramp."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    p = N["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    tc = N.new("ShaderNodeTexCoord")
    geo = N.new("ShaderNodeNewGeometry")
    inset = N.new("ShaderNodeVectorMath"); inset.operation = "SCALE"; inset.inputs[3].default_value = -px * 0.45
    Lk.new(tc.outputs["Normal"] if per_object else geo.outputs["Normal"], inset.inputs[0])
    src = tc.outputs["Object"] if per_object else geo.outputs["Position"]
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"
    Lk.new(src, add.inputs[0]); Lk.new(inset.outputs[0], add.inputs[1])
    snap = N.new("ShaderNodeVectorMath"); snap.operation = "SNAP"; snap.inputs[1].default_value = (px, px, px)
    Lk.new(add.outputs[0], snap.inputs[0])
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"
    Lk.new(snap.outputs[0], wn.inputs["Vector"])
    fac = wn.outputs["Value"]
    if voxel:
        sv = N.new("ShaderNodeVectorMath"); sv.operation = "SNAP"; sv.inputs[1].default_value = (voxel, voxel, voxel)
        Lk.new(add.outputs[0], sv.inputs[0])
        wv = N.new("ShaderNodeTexWhiteNoise"); wv.noise_dimensions = "3D"
        Lk.new(sv.outputs[0], wv.inputs["Vector"])
        mix = N.new("ShaderNodeMix"); mix.data_type = "FLOAT"; mix.inputs["Factor"].default_value = 0.4
        Lk.new(fac, mix.inputs["A"]); Lk.new(wv.outputs["Value"], mix.inputs["B"])
        fac = mix.outputs["Result"]
    if per_object:
        oi = N.new("ShaderNodeObjectInfo")
        mix = N.new("ShaderNodeMix"); mix.data_type = "FLOAT"; mix.inputs["Factor"].default_value = 0.25
        Lk.new(fac, mix.inputs["A"]); Lk.new(oi.outputs["Random"], mix.inputs["B"])
        fac = mix.outputs["Result"]
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c_dark, 1)
    ramp.color_ramp.elements[1].color = (*c_light, 1)
    Lk.new(fac, ramp.inputs["Fac"])
    Lk.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    Lk.new(wn.outputs["Value"], bp.inputs["Height"])
    Lk.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def emission_material(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    N, Lk = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    Lk.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def add_box(bm, center, size, mi=0):
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r["verts"]:
        v.co = Vector((v.co.x * size[0] + center[0], v.co.y * size[1] + center[1], v.co.z * size[2] + center[2]))
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = mi
    return r["verts"]


def mesh_obj(name, boxes, mats, parent=None, coll=None):
    """boxes: list of (center, size, material index)."""
    bm = bmesh.new()
    for c, s, mi in boxes:
        add_box(bm, c, s, mi)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    if parent:
        o.parent = parent
    return o


def look_quat(eye, target):
    return (Vector(target) - Vector(eye)).to_track_quat("-Z", "Y")


def fcurves_of(o):
    ad = o.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


def set_interp(o, kind, frames=None):
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points:
            if frames is None or int(round(kp.co.x)) in frames:
                kp.interpolation = kind


def rx(a):
    return Matrix.Rotation(a, 3, "X")


def ry(a):
    return Matrix.Rotation(a, 3, "Y")


def rz(a):
    return Matrix.Rotation(a, 3, "Z")


def two_bone(S, T, l1, l2, pole):
    d = T - S
    dist = d.length
    u = d.normalized() if dist > 1e-6 else Vector((0, 0, -1))
    dc = min(max(dist, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-4)
    a = (l1 * l1 + dc * dc - l2 * l2) / (2 * dc)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    n = pole - u * pole.dot(u)
    n = n.normalized() if n.length > 1e-6 else Vector((0, 1, 0))
    return S + u * a + n * h, S + u * dc, dist / (l1 + l2)


def aim(Qparent, rest_dir, d):
    cur = Qparent @ rest_dir
    return cur.rotation_difference(d.normalized()).to_matrix() @ Qparent


def bump(t, a, b, e=0.35):
    e = min(e, (b - a) * 0.3)
    return smooth((t - a) / e) * (1 - smooth((t - (b - e)) / e))


SHIRTS = {"rust": (0.62, 0.30, 0.20), "red": (0.72, 0.12, 0.12), "blue": (0.20, 0.38, 0.68), "green": (0.22, 0.50, 0.25),
          "yellow": (0.90, 0.72, 0.20), "purple": (0.45, 0.25, 0.60), "white": (0.90, 0.90, 0.88), "striped": (0.16, 0.24, 0.48)}


FACE_BONES = [                                               # move grandpa's existing face blocks (bl_perform expressions)
    ("brow.R", (-0.06, -0.124, 1.008), (-0.06, -0.124, 1.028), "head"), ("brow.L", (0.06, -0.124, 1.008), (0.06, -0.124, 1.028), "head"),
    ("pupil.R", (-0.06, -0.1245, 0.968), (-0.06, -0.1245, 0.988), "head"), ("pupil.L", (0.06, -0.1245, 0.968), (0.06, -0.1245, 0.988), "head"),
    ("lid.R", (-0.06, -0.1265, 0.992), (-0.06, -0.1265, 0.972), "head"), ("lid.L", (0.06, -0.1265, 0.992), (0.06, -0.1265, 0.972), "head"),
    ("cheeks", (0, -0.12, 0.93), (0, -0.12, 0.95), "head"), ("smile", (0, -0.1405, 0.889), (0, -0.1405, 0.909), "jaw"),
]
FACE_ORDER = tuple(b[0] for b in FACE_BONES)


def build_grandpa(sc, parent, outfit=None):
    """outfit: {"hat": cap|hardhat|santa|beret|straw|beanie|none, "shirt": colour name, "extras": [goggles, scarf, vest]}"""
    outfit = dict(dict(hat="cap", shirt="rust", extras=[]), **(outfit or {}))
    arm_data = bpy.data.armatures.new("GrandpaRig")
    arm = bpy.data.objects.new("Grandpa", arm_data)
    sc.collection.objects.link(arm)
    arm.parent = parent
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    BONES = [
        ("hips", (0, 0, 0.46), (0, 0, 0.56), None), ("spine", (0, 0, 0.46), (0, 0, 0.82), "hips"),
        ("head", (0, 0, 0.82), (0, 0, 1.06), "spine"), ("jaw", (0, -0.1, 0.86), (0, -0.1, 0.82), "head"),
        ("upper_arm.R", (-0.19, 0, 0.77), (-0.19, 0, 0.57), "spine"), ("forearm.R", (-0.19, 0, 0.57), (-0.19, 0, 0.37), "upper_arm.R"),
        ("upper_arm.L", (0.19, 0, 0.77), (0.19, 0, 0.57), "spine"), ("forearm.L", (0.19, 0, 0.57), (0.19, 0, 0.37), "upper_arm.L"),
        ("thigh.R", (-0.07, 0, 0.46), (-0.07, 0, 0.24), "hips"), ("shin.R", (-0.07, 0, 0.24), (-0.07, 0, 0.0), "thigh.R"),
        ("thigh.L", (0.07, 0, 0.46), (0.07, 0, 0.24), "hips"), ("shin.L", (0.07, 0, 0.24), (0.07, 0, 0.0), "thigh.L"),
    ] + FACE_BONES
    for name, h, t, par in BONES:
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail, eb.roll = h, t, 0.0
        if par:
            eb.parent = arm_data.edit_bones[par]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    C = dict(skin=(0.86, 0.64, 0.50), skin2=(0.80, 0.52, 0.44), beard=(0.82, 0.82, 0.80), brow=(0.70, 0.70, 0.68),
             eye=(0.08, 0.06, 0.05), shirt=(0.62, 0.30, 0.20), denim=(0.20, 0.30, 0.46), boot=(0.28, 0.17, 0.10),
             belt=(0.18, 0.11, 0.07), cap=(0.36, 0.29, 0.20), cheek=(0.92, 0.50, 0.46), hair=(0.74, 0.74, 0.72),
             pouch=(0.48, 0.30, 0.15), smile=(0.45, 0.20, 0.18), white=(0.95, 0.95, 0.95),
             hard=(0.96, 0.74, 0.08), santa=(0.74, 0.06, 0.07), beret=(0.10, 0.10, 0.12), straw=(0.86, 0.73, 0.43),
             ribbon=(0.55, 0.12, 0.10), beanie=(0.18, 0.36, 0.70), beanie2=(0.28, 0.48, 0.82), scarf=(0.78, 0.14, 0.16),
             vest=(0.98, 0.45, 0.05), stripe=(0.85, 0.87, 0.88), lens=(0.35, 0.70, 0.85), frame=(0.12, 0.12, 0.13))
    C["shirt"] = SHIRTS.get(outfit["shirt"], SHIRTS["rust"])
    slot = {k: i for i, k in enumerate(C)}
    bm = bmesh.new()
    groups = {}

    def part(group, center, size, color):
        groups.setdefault(group, []).extend(add_box(bm, center, size, slot[color]))

    for s, x in (("R", -0.07), ("L", 0.07)):
        part("shin." + s, (x, -0.02, 0.04), (0.13, 0.17, 0.08), "boot")
        part("shin." + s, (x, 0, 0.165), (0.115, 0.115, 0.17), "denim")
        part("thigh." + s, (x, 0, 0.35), (0.12, 0.12, 0.22), "denim")
    part("hips", (0, 0, 0.51), (0.28, 0.15, 0.10), "denim")
    part("hips", (0, 0, 0.553), (0.29, 0.16, 0.026), "belt")
    part("hips", (-0.155, -0.01, 0.505), (0.05, 0.08, 0.075), "pouch")
    part("spine", (0, 0, 0.69), (0.28, 0.15, 0.26), "shirt")
    part("spine", (0, -0.078, 0.645), (0.16, 0.012, 0.15), "denim")
    for x in (-0.055, 0.055):
        part("spine", (x, -0.078, 0.765), (0.03, 0.012, 0.09), "denim")
        part("spine", (x, 0.078, 0.70), (0.03, 0.012, 0.22), "denim")
    part("head", (0, 0, 0.94), (0.24, 0.24, 0.24), "skin")
    part("jaw", (0, -0.125, 0.865), (0.244, 0.03, 0.09), "beard")
    part("head", (0, -0.1225, 0.8825), (0.10, 0.006, 0.045), "eye")
    part("head", (0, -0.13, 0.912), (0.13, 0.03, 0.03), "beard")
    for x in (-0.121, 0.121):
        part("head", (x, -0.03, 0.88), (0.012, 0.16, 0.12), "beard")
    part("smile", (0, -0.1405, 0.889), (0.06, 0.004, 0.012), "smile")
    part("head", (0, -0.132, 0.935), (0.045, 0.03, 0.05), "skin2")
    for x in (-0.06, 0.06):
        sd = "R" if x < 0 else "L"
        part("head", (x, -0.1215, 0.972), (0.04, 0.006, 0.04), "white")
        part("pupil." + sd, (x, -0.1245, 0.968), (0.022, 0.006, 0.03), "eye")
        part("lid." + sd, (x, -0.1265, 0.991), (0.044, 0.006, 0.002), "skin")    # a hairline at rest; scales down to blink
        part("brow." + sd, (x, -0.124, 1.008), (0.062, 0.01, 0.02), "brow")
        part("cheeks", (x * 1.42, -0.1215, 0.93), (0.035, 0.004, 0.022), "cheek")
        part("head", (math.copysign(0.13, x), 0, 0.95), (0.02, 0.045, 0.055), "skin2")
        part("head", (math.copysign(0.1215, x), 0.06, 0.995), (0.012, 0.11, 0.07), "hair")
    part("head", (0, 0.1215, 0.99), (0.244, 0.012, 0.11), "hair")
    hat = outfit["hat"]
    if hat == "cap":
        part("head", (0, 0.012, 1.078), (0.25, 0.25, 0.036), "cap")
        part("head", (0, -0.142, 1.064), (0.2, 0.06, 0.014), "cap")
    elif hat == "hardhat":
        part("head", (0, 0, 1.066), (0.31, 0.31, 0.014), "hard")
        part("head", (0, 0, 1.105), (0.26, 0.26, 0.07), "hard")
        part("head", (0, 0, 1.15), (0.18, 0.18, 0.03), "hard")
        part("head", (0, -0.16, 1.07), (0.24, 0.05, 0.016), "hard")
    elif hat == "santa":
        part("head", (0, 0, 1.075), (0.264, 0.264, 0.04), "white")
        part("head", (0, 0.01, 1.12), (0.22, 0.22, 0.06), "santa")
        part("head", (0, 0.05, 1.165), (0.15, 0.15, 0.05), "santa")
        part("head", (0, 0.10, 1.195), (0.09, 0.09, 0.04), "santa")
        part("head", (0, 0.145, 1.20), (0.06, 0.06, 0.06), "white")
    elif hat == "beret":
        part("head", (0.02, 0, 1.075), (0.27, 0.27, 0.03), "beret")
        part("head", (0.03, 0, 1.097), (0.2, 0.2, 0.02), "beret")
        part("head", (0.03, 0, 1.112), (0.02, 0.02, 0.02), "beret")
    elif hat == "straw":
        part("head", (0, 0, 1.068), (0.42, 0.42, 0.014), "straw")
        part("head", (0, 0, 1.11), (0.24, 0.24, 0.08), "straw")
        part("head", (0, 0, 1.085), (0.246, 0.246, 0.022), "ribbon")
    elif hat == "beanie":
        part("head", (0, 0, 1.085), (0.255, 0.255, 0.06), "beanie")
        part("head", (0, 0, 1.06), (0.26, 0.26, 0.03), "beanie2")
        part("head", (0, 0, 1.135), (0.06, 0.06, 0.045), "white")
    else:                                                    # bare head: short grey hair on top
        part("head", (0, 0.01, 1.066), (0.236, 0.21, 0.014), "hair")
    extras = outfit["extras"]
    if "goggles" in extras:
        part("head", (0, -0.1235, 1.045), (0.21, 0.008, 0.014), "frame")
        for x in (-0.055, 0.055):
            part("head", (x, -0.127, 1.045), (0.06, 0.01, 0.04), "frame")
            part("head", (x, -0.1325, 1.045), (0.045, 0.004, 0.028), "lens")
    if "scarf" in extras:
        part("spine", (0, 0, 0.835), (0.27, 0.17, 0.05), "scarf")
        part("spine", (0.07, -0.088, 0.76), (0.06, 0.02, 0.12), "scarf")
    if "vest" in extras:
        part("spine", (0, 0.081, 0.69), (0.292, 0.012, 0.25), "vest")
        part("spine", (0, 0.088, 0.66), (0.292, 0.003, 0.025), "stripe")
        for x in (-1, 1):
            part("spine", (0.1435 * x, 0, 0.69), (0.012, 0.164, 0.25), "vest")
            part("spine", (0.105 * x, -0.0835, 0.69), (0.065, 0.012, 0.25), "vest")
            part("spine", (0.105 * x, -0.0905, 0.66), (0.065, 0.003, 0.025), "stripe")
    if "hammer" in extras:                                   # held in the right hand, head forward
        part("forearm.R", (-0.19, -0.06, 0.335), (0.024, 0.13, 0.024), "pouch")
        part("forearm.R", (-0.19, -0.13, 0.335), (0.036, 0.04, 0.08), "frame")
    if outfit["shirt"] == "striped":
        for z in (0.61, 0.67, 0.73, 0.79):
            part("spine", (0, 0, z), (0.284, 0.154, 0.02), "stripe")
    for s, x in (("R", -0.19), ("L", 0.19)):
        part("upper_arm." + s, (x, 0, 0.67), (0.10, 0.10, 0.20), "shirt")
        if outfit["shirt"] == "striped":
            for z in (0.62, 0.68, 0.74):
                part("upper_arm." + s, (x, 0, z), (0.104, 0.104, 0.02), "stripe")
        part("forearm." + s, (x, 0, 0.535), (0.104, 0.104, 0.07), "shirt")
        part("forearm." + s, (x, 0, 0.45), (0.09, 0.09, 0.12), "skin")
        part("forearm." + s, (x, 0, 0.345), (0.085, 0.085, 0.07), "skin")
    bm.verts.index_update()
    gidx = {g: [v.index for v in vs] for g, vs in groups.items()}
    gm = bpy.data.meshes.new("GrandpaMesh")
    bm.to_mesh(gm); bm.free()
    for k, c in C.items():
        gm.materials.append(mat("G_" + k, c, rough=0.95 if k not in ("eye", "white") else 0.35))
    gob = bpy.data.objects.new("GrandpaMesh", gm)
    sc.collection.objects.link(gob)
    for g, ids in gidx.items():
        gob.vertex_groups.new(name=g).add(ids, 1.0, "REPLACE")
    gob.parent = arm
    gob.modifiers.new("Rig", "ARMATURE").object = arm
    return arm


