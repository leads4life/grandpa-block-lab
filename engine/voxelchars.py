"""New cast for Episode 1 (designs awaiting approval): Tobias (Grandpa Tovi's grandson) and the wild boar.

Same voxel language as voxelkit.build_grandpa: plain boxes, flat matte colours, a pixel texture only where fur needs it.
Tobias uses Grandpa's bone names (scaled to a kid) so bl_perform poses and expressions can drive him later.
voxelkit itself is untouched, so approved scenes render exactly as before.
"""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

import voxelkit as VK

# ---------------------------------------------------------------------------------------------------------------- Tobias
KID_FACE_BONES = [
    ("brow.R", (-0.05, -0.114, 0.72), (-0.05, -0.114, 0.74), "head"), ("brow.L", (0.05, -0.114, 0.72), (0.05, -0.114, 0.74), "head"),
    ("pupil.R", (-0.05, -0.1145, 0.668), (-0.05, -0.1145, 0.688), "head"), ("pupil.L", (0.05, -0.1145, 0.668), (0.05, -0.1145, 0.688), "head"),
    ("lid.R", (-0.05, -0.1165, 0.706), (-0.05, -0.1165, 0.686), "head"), ("lid.L", (0.05, -0.1165, 0.706), (0.05, -0.1165, 0.686), "head"),
    ("cheeks", (0, -0.111, 0.635), (0, -0.111, 0.655), "head"), ("smile", (0, -0.1135, 0.604), (0, -0.1135, 0.624), "jaw"),
]
KID_BONES = [
    ("hips", (0, 0, 0.30), (0, 0, 0.37), None), ("spine", (0, 0, 0.30), (0, 0, 0.54), "hips"),
    ("head", (0, 0, 0.54), (0, 0, 0.78), "spine"), ("jaw", (0, -0.09, 0.60), (0, -0.09, 0.57), "head"),
    ("upper_arm.R", (-0.145, 0, 0.52), (-0.145, 0, 0.40), "spine"), ("forearm.R", (-0.145, 0, 0.40), (-0.145, 0, 0.27), "upper_arm.R"),
    ("upper_arm.L", (0.145, 0, 0.52), (0.145, 0, 0.40), "spine"), ("forearm.L", (0.145, 0, 0.40), (0.145, 0, 0.27), "upper_arm.L"),
    ("thigh.R", (-0.055, 0, 0.30), (-0.055, 0, 0.16), "hips"), ("shin.R", (-0.055, 0, 0.16), (-0.055, 0, 0.0), "thigh.R"),
    ("thigh.L", (0.055, 0, 0.30), (0.055, 0, 0.16), "hips"), ("shin.L", (0.055, 0, 0.16), (0.055, 0, 0.0), "thigh.L"),
] + KID_FACE_BONES
KID_C = dict(skin=(0.88, 0.67, 0.53), skin2=(0.82, 0.56, 0.46), freckle=(0.62, 0.36, 0.24), cheek=(0.94, 0.52, 0.48),
             hair=(0.36, 0.22, 0.12), brow=(0.30, 0.18, 0.10), eye=(0.07, 0.05, 0.04), white=(0.96, 0.96, 0.96),
             shirt=(0.30, 0.52, 0.28), shirt2=(0.40, 0.62, 0.36), khaki=(0.66, 0.56, 0.36), khaki2=(0.52, 0.43, 0.27),
             hat=(0.58, 0.55, 0.34), band=(0.30, 0.26, 0.16), patch=(0.95, 0.90, 0.78), boot=(0.38, 0.23, 0.12),
             sock=(0.94, 0.94, 0.92), black=(0.07, 0.07, 0.08), lens=(0.35, 0.70, 0.85), pack=(0.92, 0.48, 0.12),
             book=(0.78, 0.16, 0.14), page=(0.97, 0.95, 0.88), pencil=(0.98, 0.80, 0.12), eraser=(0.95, 0.55, 0.62),
             smile=(0.45, 0.20, 0.18))


TOBIAS_SCALE = 1.0                                                 # user approved the larger version (hat ~0.83 m)


def build_tobias(sc, parent=None, name="Tobias", k=TOBIAS_SCALE):
    """Tobias: about 0.83 m to the top of his bucket hat (k scales the whole build), about Grandpa's chest height. Big head and eyes (a kid), field-scientist kit: bucket hat with a
    paw-print patch, green field shirt with pockets, binoculars, a notebook in his left hand, a pencil behind his ear,
    an orange backpack, khaki shorts and small brown boots (the tiny boot prints in Scene 003)."""
    arm_data = bpy.data.armatures.new(name + "Rig")
    arm = bpy.data.objects.new(name, arm_data)
    sc.collection.objects.link(arm)
    arm.parent = parent
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for bn, h, t, par in KID_BONES:
        eb = arm_data.edit_bones.new(bn)
        eb.head, eb.tail, eb.roll = [v * k for v in h], [v * k for v in t], 0.0
        if par:
            eb.parent = arm_data.edit_bones[par]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    slot = {c: i for i, c in enumerate(KID_C)}
    bm = bmesh.new()
    groups = {}

    def part(group, center, size, color):
        groups.setdefault(group, []).extend(VK.add_box(bm, [v * k for v in center], [v * k for v in size], slot[color]))

    for s, x in (("R", -0.055), ("L", 0.055)):
        part("shin." + s, (x, -0.015, 0.03), (0.10, 0.14, 0.06), "boot")
        part("shin." + s, (x, -0.06, 0.062), (0.104, 0.03, 0.012), "khaki2")         # boot toe cap
        part("shin." + s, (x, 0, 0.078), (0.082, 0.082, 0.036), "sock")
        part("shin." + s, (x, 0, 0.125), (0.074, 0.074, 0.07), "skin")
        part("thigh." + s, (x, 0, 0.225), (0.10, 0.10, 0.15), "khaki")
    part("hips", (0, 0, 0.33), (0.22, 0.13, 0.08), "khaki")
    part("hips", (0, 0, 0.368), (0.224, 0.134, 0.016), "band")
    part("spine", (0, 0, 0.455), (0.22, 0.13, 0.17), "shirt")
    for x in (-0.05, 0.05):                                            # chest pockets with flaps
        part("spine", (x, -0.067, 0.47), (0.05, 0.006, 0.045), "shirt2")
        part("spine", (x, -0.069, 0.493), (0.054, 0.006, 0.012), "shirt")
    part("spine", (0, -0.066, 0.53), (0.09, 0.006, 0.02), "shirt2")             # collar
    for x in (-0.034, 0.034):                                          # binocular strap round his neck
        part("spine", (x, -0.068, 0.505), (0.012, 0.006, 0.06), "black")
    for x in (-0.022, 0.022):                                          # binoculars, hanging on his chest
        part("spine", (x, -0.088, 0.43), (0.032, 0.036, 0.055), "black")
        part("spine", (x, -0.107, 0.43), (0.022, 0.004, 0.022), "lens")
    part("spine", (0, -0.088, 0.442), (0.014, 0.024, 0.014), "black")
    part("spine", (0, 0.092, 0.45), (0.17, 0.055, 0.16), "pack")                  # backpack
    part("spine", (0, 0.122, 0.42), (0.12, 0.008, 0.07), "khaki2")
    for x in (-0.06, 0.06):
        part("spine", (x, 0.0, 0.542), (0.024, 0.13, 0.008), "pack")             # straps over the shoulders
    # head: a big kid head, big eyes
    part("head", (0, 0, 0.66), (0.22, 0.22, 0.22), "skin")
    for x in (-0.05, 0.05):
        sd = "R" if x < 0 else "L"
        part("head", (x, -0.1115, 0.675), (0.06, 0.006, 0.062), "white")                # big kid eyes
        part("pupil." + sd, (x, -0.1145, 0.668), (0.032, 0.006, 0.04), "eye")
        part("pupil." + sd, (x + 0.008, -0.117, 0.68), (0.011, 0.004, 0.011), "white")   # catch-light
        part("lid." + sd, (x, -0.1165, 0.706), (0.064, 0.006, 0.002), "skin")
        part("brow." + sd, (x, -0.114, 0.72), (0.052, 0.008, 0.013), "brow")
        part("cheeks", (x * 1.75, -0.1112, 0.635), (0.03, 0.004, 0.016), "cheek")
        for fx, fz in ((0.07, 0.632), (0.082, 0.64), (0.094, 0.63)):              # freckles (just in front of the cheeks)
            part("head", (math.copysign(fx, x), -0.1122, fz), (0.009, 0.004, 0.009), "freckle")
        part("head", (math.copysign(0.115, x), 0, 0.655), (0.014, 0.04, 0.052), "skin2")    # ears
    part("head", (0, -0.12, 0.645), (0.03, 0.02, 0.028), "skin2")                # nose
    part("smile", (0, -0.1135, 0.604), (0.05, 0.004, 0.01), "smile")                  # a smile with upturned corners
    for mx in (-0.03, 0.03):
        part("smile", (mx, -0.1135, 0.611), (0.012, 0.004, 0.01), "smile")
    part("jaw", (0, -0.1118, 0.588), (0.07, 0.003, 0.01), "skin")                 # chin line (moves when he talks)
    part("head", (0, 0.111, 0.70), (0.224, 0.012, 0.12), "hair")
    for x in (-0.111, 0.111):
        part("head", (x, 0.05, 0.712), (0.012, 0.12, 0.09), "hair")
    part("head", (0, -0.104, 0.759), (0.21, 0.02, 0.022), "hair")                # fringe under the hat
    for hx in (-0.07, 0.035):                                          # two messy locks
        part("head", (hx, -0.1145, 0.753), (0.035, 0.006, 0.014), "hair")
    for hx in (-0.118, 0.118):
        part("head", (hx, -0.03, 0.735), (0.012, 0.06, 0.05), "hair")             # tufts over the ears
    part("head", (0.09, 0.07, 0.80), (0.02, 0.02, 0.05), "hair")                  # a cowlick that won't stay down
    part("head", (0.10, 0.07, 0.83), (0.03, 0.02, 0.02), "hair")
    part("head", (0, 0, 0.776), (0.31, 0.31, 0.014), "hat")                       # bucket hat
    part("head", (0, 0.005, 0.79), (0.228, 0.228, 0.014), "band")
    part("head", (0, 0.005, 0.818), (0.225, 0.225, 0.045), "hat")
    part("head", (0, -0.1145, 0.818), (0.042, 0.004, 0.038), "patch")             # paw-print patch: a pad and four toes
    part("head", (0, -0.117, 0.811), (0.016, 0.003, 0.012), "band")
    for px, pz in ((-0.013, 0.824), (-0.0045, 0.829), (0.0045, 0.829), (0.013, 0.824)):
        part("head", (px, -0.117, pz), (0.006, 0.003, 0.006), "band")
    part("head", (0.124, 0.0, 0.69), (0.008, 0.075, 0.008), "pencil")             # pencil behind his ear
    part("head", (0.124, 0.04, 0.69), (0.009, 0.012, 0.009), "eraser")
    for s, x in (("R", -0.145), ("L", 0.145)):
        part("upper_arm." + s, (x, 0, 0.48), (0.076, 0.076, 0.09), "shirt")      # short sleeves
        part("upper_arm." + s, (x, 0, 0.415), (0.066, 0.066, 0.05), "skin")
        part("forearm." + s, (x, 0, 0.34), (0.066, 0.066, 0.12), "skin")
        part("forearm." + s, (x, 0, 0.275), (0.072, 0.072, 0.05), "skin")
    part("forearm.L", (0.145, -0.055, 0.275), (0.018, 0.075, 0.095), "book")      # field notebook in his left hand
    part("forearm.L", (0.145, -0.055, 0.275), (0.022, 0.068, 0.088), "page")
    bm.verts.index_update()
    gidx = {g: [v.index for v in vs] for g, vs in groups.items()}
    me = bpy.data.meshes.new(name + "Mesh")
    bm.to_mesh(me); bm.free()
    for cn, c in KID_C.items():
        me.materials.append(VK.mat("T_" + cn, c, rough=0.95 if cn not in ("eye", "white", "lens") else 0.35))
    ob = bpy.data.objects.new(name + "Mesh", me)
    sc.collection.objects.link(ob)
    for g, ids in gidx.items():
        ob.vertex_groups.new(name=g).add(ids, 1.0, "REPLACE")
    ob.parent = arm
    ob.modifiers.new("Rig", "ARMATURE").object = arm
    return arm


def pose_bone(arm, bone, rot=(0, 0, 0), off=(0, 0, 0), S=(1, 1, 1)):
    """Static pose: rotate (degrees, XYZ about the bone's rest head, in the rig's rest space), move and scale a bone."""
    pb, rest4 = arm.pose.bones[bone], arm.data.bones[bone].matrix_local
    h = rest4.translation
    R = (Matrix.Rotation(math.radians(rot[2]), 3, "Z") @ Matrix.Rotation(math.radians(rot[1]), 3, "Y") @
         Matrix.Rotation(math.radians(rot[0]), 3, "X"))
    D = Matrix.Translation(Vector(off) + h) @ R.to_4x4() @ Matrix.Diagonal((*S, 1.0)) @ Matrix.Translation(-h)
    pb.rotation_mode = "QUATERNION"
    pb.location, pb.rotation_quaternion, pb.scale = (rest4.inverted() @ D @ rest4).decompose()


# ---------------------------------------------------------------------------------------------------------------- the boar
BOAR_C = dict(coat=((0.08, 0.06, 0.05), (0.22, 0.16, 0.11)), coat2=((0.05, 0.04, 0.03), (0.13, 0.10, 0.07)),
              pale=((0.42, 0.36, 0.30), (0.62, 0.56, 0.48)))


def build_boar(sc, mood="calm", name="Boar"):
    """An original voxel wild boar (deliberately unlike any game mob: no pink cube head). Wedge silhouette: tall bristly
    shoulders and mane, back sloping down to a lean rump, thin dark legs, a long tapering dark snout, pale whiskery cheeks,
    small eyes, pointed ears, curved tusks that show, a thin tufted tail. Faces +x.
    mood "calm": head level, ears up, mane flat. mood "agitated": head down to charge, ears pinned back, mane and hackles
    up, angry brows, a huff of breath from the nose, tail straight up, front legs planted wide, dust at the hooves.
    Returns the root object (body); the head is a child pivoting at the neck."""
    px = 0.012
    M = [VK.pixel_material("B_coat", *BOAR_C["coat"], px, bump=0.35), VK.pixel_material("B_coat2", *BOAR_C["coat2"], px, bump=0.35),
         VK.pixel_material("B_pale", *BOAR_C["pale"], px, bump=0.3), VK.mat("B_disc", (0.36, 0.28, 0.27)),
         VK.mat("B_dark", (0.03, 0.03, 0.03)), VK.mat("B_tusk", (0.96, 0.93, 0.82), rough=0.35),
         VK.mat("B_hoof", (0.10, 0.10, 0.10)), VK.mat("B_eyering", (0.55, 0.40, 0.25)),
         VK.mat("B_puff", (0.95, 0.95, 0.95)), VK.mat("B_dust", (0.62, 0.52, 0.38)), VK.mat("B_angry", (0.75, 0.12, 0.08))]
    COAT, COAT2, PALE, DISC, DARK, TUSK, HOOF, RING, PUFF, DUST, ANGRY = range(11)
    ag = mood == "agitated"
    body = [((0.13, 0, 0.385), (0.36, 0.34, 0.33), COAT),            # deep chest and shoulders
            ((-0.16, 0, 0.36), (0.26, 0.29, 0.25), COAT),            # leaner hindquarters: the back slopes down
            ((-0.32, 0, 0.36), (0.07, 0.25, 0.20), COAT),
            ((0.05, 0, 0.215), (0.44, 0.24, 0.03), COAT2)]           # belly shadow
    spread = 0.05 if ag else 0.0
    for lx, ly in ((0.20 + spread, -0.10), (0.20 + spread, 0.10), (-0.22, -0.09), (-0.22, 0.09)):
        body += [((lx, ly, 0.13), (0.065, 0.065, 0.20), COAT2), ((lx, ly, 0.02), (0.075, 0.075, 0.04), HOOF)]
    up = 1.8 if ag else 0.7                                          # the mane: tallest at the neck, down the spine
    for rx, rh in ((0.29, 0.11), (0.23, 0.13), (0.17, 0.12), (0.11, 0.11), (0.05, 0.09), (-0.01, 0.07), (-0.07, 0.05),
                   (-0.13, 0.05), (-0.19, 0.04), (-0.25, 0.03)):
        z0 = 0.55 if rx > -0.03 else 0.485
        body.append(((rx, 0, z0 + rh * up / 2), (0.055, 0.05 if rx > 0.0 else 0.04, rh * up), COAT2))
        if rx > 0.08:
            for y in (-0.05, 0.05):                                  # shaggy shoulder bristles
                body.append(((rx, y, z0 + rh * up * 0.3), (0.05, 0.03, rh * up * 0.6), COAT2))
    if ag:
        body += [((-0.36, 0, 0.47), (0.022, 0.022, 0.14), COAT2), ((-0.36, 0, 0.555), (0.04, 0.035, 0.04), COAT2)]  # tail up
        for dx, dy, s in ((0.33, -0.17, 0.05), (0.29, 0.18, 0.04), (0.37, 0.15, 0.035), (0.36, -0.22, 0.03), (0.25, -0.2, 0.025)):
            body.append(((dx, dy, s / 2), (s, s, s), DUST))
    else:
        body += [((-0.37, 0, 0.36), (0.022, 0.022, 0.12), COAT2), ((-0.37, 0, 0.29), (0.035, 0.035, 0.04), COAT2)]  # tail down
    root = VK.mesh_obj(name, body, M)
    head = [((0.08, 0, 0.0), (0.18, 0.26, 0.26), COAT),             # skull
            ((0.20, 0, -0.04), (0.10, 0.20, 0.17), COAT),            # the snout tapers in steps...
            ((0.29, 0, -0.06), (0.10, 0.15, 0.12), COAT2),
            ((0.365, 0, -0.065), (0.06, 0.12, 0.095), COAT2),
            ((0.398, 0, -0.065), (0.008, 0.10, 0.075), DISC)]        # ...to a small dark disc, not a pink square
    for y in (-0.025, 0.025):
        head.append(((0.403, y, -0.07), (0.004, 0.018, 0.026), DARK))
    for y in (-0.125, 0.125):                                        # pale whiskery cheeks and jowls
        head += [((0.13, y, -0.075), (0.10, 0.026, 0.065), PALE), ((0.21, y * 0.86, -0.1), (0.07, 0.02, 0.04), PALE)]
    for y in (-0.072, 0.072):                                        # tusks: curve out and up past the snout
        s = math.copysign(1, y)
        head += [((0.30, y + s * 0.012, -0.115), (0.035, 0.022, 0.025), TUSK),
                 ((0.335, y + s * 0.02, -0.09), (0.03, 0.022, 0.04), TUSK),
                 ((0.345, y + s * 0.03, -0.05), (0.024, 0.02, 0.04), TUSK),
                 ((0.335, y + s * 0.035, -0.022), (0.02, 0.018, 0.02), TUSK)]
    for s_ in (-1, 1):                                               # small eyes, high on the sides of the head
        y = s_ * 0.13
        head += [((0.12, y + s_ * 0.0025, 0.055), (0.04, 0.006, 0.032), RING), ((0.125, y + s_ * 0.0055, 0.055), (0.022, 0.006, 0.022), DARK)]
        if ag:
            head.append(((0.128, y + s_ * 0.0085, 0.05), (0.008, 0.004, 0.008), ANGRY))     # a red glint
            head += [((0.142, y + s_ * 0.0035, 0.074), (0.026, 0.008, 0.014), COAT2),       # angry brows, slanting down
                     ((0.112, y + s_ * 0.0035, 0.087), (0.026, 0.008, 0.014), COAT2)]       # toward the snout
            head.append(((-0.02, s_ * 0.105, 0.13), (0.11, 0.035, 0.035), COAT2))          # ears pinned back
        else:
            head.append(((0.12, y + s_ * 0.0035, 0.08), (0.044, 0.008, 0.01), COAT2))
            head += [((0.02, s_ * 0.105, 0.16), (0.05, 0.035, 0.08), COAT2), ((0.03, s_ * 0.105, 0.215), (0.03, 0.025, 0.04), COAT2)]
    if ag:                                                           # HUFF: breath blasting from the nose
        for dx, dz, sz, k in ((0.44, -0.07, 0.035, 1.0), (0.49, -0.06, 0.03, 1.5), (0.535, -0.08, 0.022, 2.0)):
            for y in (-0.025, 0.025):
                head.append(((dx, y * k, dz), (sz, sz, sz), PUFF))
    hd = VK.mesh_obj(name + "Head", head, M, parent=root)
    hd.location = (0.31, 0, 0.42)
    hd.rotation_euler = (0, math.radians(26 if ag else 2), 0)        # nose down, ready to charge
    return root
