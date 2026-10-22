import bpy, sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
sc=bpy.context.scene
for f in [int(x) for x in sys.argv[2:]]:
    sc.frame_set(f); pre={}
    for ob in sc.objects:
        k=ob.name.split("_")[0]
        if ob.type!="MESH" or k not in ("wheel","axle","cam1"): continue
        for c in ob.bound_box:
            w=ob.matrix_world@Vector(c); lo,hi=pre.get(k,([9e9]*3,[-9e9]*3))
            pre[k]=([min(a,b) for a,b in zip(lo,w)],[max(a,b) for a,b in zip(hi,w)])
    print(f,{k:([round(v,2) for v in lo][2],[round(v,2) for v in hi][2]) for k,(lo,hi) in pre.items()})
