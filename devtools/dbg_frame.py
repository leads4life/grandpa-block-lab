import bpy, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, "/home/user/blocklab"); import bl_common as C
bpy.ops.wm.open_mainfile(filepath="/home/user/blocklab/build/blocklab.blend")
sc = bpy.context.scene; arm = bpy.data.objects["Grandpa"]; P = C.load_plan()
runs, cur = [], None
for f in range(P["nf"]):
    sc.frame_set(f)
    head = arm.matrix_world @ arm.pose.bones["head"].tail
    pts = {"hat": head + Vector((0, 0, 0.1)), "face": arm.matrix_world @ arm.pose.bones["head"].head.lerp(arm.pose.bones["head"].tail, .5),
           "chest": arm.matrix_world @ arm.pose.bones["spine"].head.lerp(arm.pose.bones["spine"].tail, .6)}
    bad = [k for k, p in pts.items() if (lambda v: v.z <= 0 or min(v.x, 1 - v.x, v.y, 1 - v.y) < 0.03)(world_to_camera_view(sc, sc.camera, p))]
    if bad:
        if cur and cur[1] == f - 1: cur[1] = f; cur[2] |= set(bad)
        else: cur = [f, f, set(bad)]; runs.append(cur)
for a, b, k in runs: print("frames %d-%d (%.2f-%.2f s): %s" % (a, b, a / 30, b / 30, sorted(k)))
