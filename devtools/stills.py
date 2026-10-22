import bpy, sys
blend, out = sys.argv[1], sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene
sc.render.resolution_percentage = 25; sc.cycles.samples = 4
try: sc.cycles.use_denoising = True
except Exception: pass
for t in ts:
    sc.frame_set(int(round(t * 30)))
    sc.render.filepath = "%s/st_%05.1f.png" % (out, t)
    bpy.ops.render.render(write_still=True)
