import bpy, sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="/home/user/blocklab/build/blocklab.blend")
sc = bpy.context.scene
gm = bpy.data.objects["GrandpaMesh"]; groups = {i: g.name for i, g in enumerate(gm.vertex_groups)}
tt = [o for o in sc.objects if o.get("struct") == "table_top"]
lo = Vector([min((o.matrix_world @ Vector(c))[i] for o in tt for c in o.bound_box) for i in range(3)])
hi = Vector([max((o.matrix_world @ Vector(c))[i] for o in tt for c in o.bound_box) for i in range(3)])
print("table", tuple(round(v,3) for v in lo), tuple(round(v,3) for v in hi))
for f in (114, 120, 123):
    sc.frame_set(f)
    ev = gm.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    pts = [(ev.matrix_world @ v.co, groups[vo.groups[0].group]) for v, vo in zip(me.vertices, gm.data.vertices) if vo.groups]
    bad = [(tuple(round(c,3) for c in p), g) for p, g in pts if g.startswith("forearm.R") and all(lo[i] + 0.008 < p[i] < hi[i] - 0.008 for i in range(3))]
    print(f, len(bad), bad[:4])
    fl = [p for p, g in pts if g == "forearm.R"]
    print("  forearm.L z range", round(min(p.z for p in fl),3), round(max(p.z for p in fl),3), "y", round(min(p.y for p in fl),3), round(max(p.y for p in fl),3))
    ev.to_mesh_clear()
