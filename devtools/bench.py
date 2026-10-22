import bpy, time
bpy.ops.wm.open_mainfile(filepath="/home/user/blocklab/build/blocklab.blend")
sc = bpy.context.scene
for pct, smp in ((50, 8), (34, 6)):
    sc.render.resolution_percentage, sc.cycles.samples = pct, smp
    for f in (300, 600):
        sc.frame_set(f); sc.render.filepath = "/tmp/claude-0/-home-user/3ffe6a42-e20c-59ee-a796-ce8de686e5e0/scratchpad/t_%d_%d_%d.png" % (pct, smp, f)
        t0 = time.time(); bpy.ops.render.render(write_still=True); print("T", pct, smp, f, round(time.time() - t0, 1), flush=True)
