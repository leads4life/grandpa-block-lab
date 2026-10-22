import bpy, json, sys, math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="build/blocklab.blend")
P = json.load(open("build/plan.json")); perf = json.load(open("build/perf.json")); FPS = P["fps"]
sc = bpy.context.scene
for a in [h for h in P["actions"] if h["type"] == "hold" and h.get("hand") != "none" and h["target"] in sys.argv[1:]]:
    rows = []
    for f in range(max(0, int(math.ceil(a["t0"] * FPS))), min(P["nf"], int(a["t1"] * FPS) + 1), 1):
        sc.frame_set(f)
        g = bpy.data.objects["S_" + a["target"]].matrix_world @ Vector(a.get("grip", (0, 0, 0)))
        w = Vector(perf[f]["wrist_" + a.get("hand", "R")])
        rows.append((round(f / FPS, 2), round((w - g).length, 3), [round(v, 2) for v in g], [round(v, 2) for v in w]))
    print(a["target"]); [print("  ", r) for r in sorted(rows, key=lambda r: -r[1])[:6]]
