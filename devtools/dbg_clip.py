import bpy, json, os, sys
from mathutils import Vector
sys.path.insert(0, "/home/user/blocklab")
import bl_common as C
bpy.ops.wm.open_mainfile(filepath="/home/user/blocklab/build/blocklab.blend")
sc = bpy.context.scene
P = C.load_plan()
objs = [o for o in sc.objects if "settle_frame" in o]
solid = [o for o in objs if o["struct"] in P["qa"]["solid"]]
gm = bpy.data.objects["GrandpaMesh"]
def wb(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])
groups = {i: g.name for i, g in enumerate(gm.vertex_groups)}
from collections import Counter
hits = Counter()
for f in range(0, P["nf"], 3):
    sc.frame_set(f)
    ev = gm.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    for v, vo in zip(me.vertices, gm.data.vertices):
        p = ev.matrix_world @ v.co
        for o in solid:
            lo, hi = wb(o)
            d = min(p.x - lo.x, hi.x - p.x, p.y - lo.y, hi.y - p.y, p.z - lo.z, hi.z - p.z)
            if d > 0.008:
                hits[(f, o["struct"], groups[vo.groups[0].group] if vo.groups else "?")] = max(hits[(f, o["struct"], groups[vo.groups[0].group] if vo.groups else "?")], round(d, 3))
    ev.to_mesh_clear()
for k, v in sorted(hits.items()):
    print(k, v)
sc.frame_set(P["nf"] - 1)
cj = json.load(open("/home/user/blocklab/build/continuity.json"))
print("grandpa", cj["grandpa"]["root"], tuple(bpy.data.objects["Grandpa"].matrix_world.translation))
for k, v in cj["structures"].items():
    t = Vector([r[3] for r in v["root"][:3]]); w = bpy.data.objects["S_" + k].matrix_world.translation
    if (t - w).length > 0.002: print("struct", k, tuple(t), tuple(w))
