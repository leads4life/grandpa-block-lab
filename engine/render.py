"""Render frames from blocklab.blend (resumable: existing frames are skipped).

    python3 render.py                 # full 1080x1920 -> frames/0000.png ...  (bpy module)
    blender -b -P render.py           # same, with a downloaded Blender build
    python3 render.py --draft         # 270x480 quick motion check -> draft/
    python3 render.py --draft --scale 50 --samples 8   # sharper preview, still in draft/
Env: GPU=1 uses OptiX/CUDA if available (falls back to CPU); FRAMES_DIR=/path overrides the output folder.
"""
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
draft = "--draft" in sys.argv
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "build", "blocklab.blend"))
sc = bpy.context.scene
out = os.environ.get("FRAMES_DIR", os.path.join(HERE, "build", "draft" if draft else "frames"))
os.makedirs(out, exist_ok=True)

if os.environ.get("GPU") == "1":
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.get_devices()
        devs = [d for d in prefs.devices if d.type == kind]
        if devs:
            for d in prefs.devices:
                d.use = d.type == kind
            sc.cycles.device = "GPU"
            sc.cycles.denoising_use_gpu = True
            print("Rendering on GPU (%s): %s" % (kind, ", ".join(d.name for d in devs)), flush=True)
            break
    else:
        print("No CUDA/OptiX GPU found -- rendering on CPU", flush=True)

if draft:
    sc.render.resolution_percentage = 25
    sc.cycles.samples = 4
    sc.cycles.use_denoising = False
if "--scale" in sys.argv:                          # e.g. --scale 50 --samples 8: a sharper preview than --draft
    sc.render.resolution_percentage = int(sys.argv[sys.argv.index("--scale") + 1])
if "--samples" in sys.argv:
    sc.cycles.samples = int(sys.argv[sys.argv.index("--samples") + 1])
    sc.cycles.use_denoising = True                 # a chosen sample count means "clean it up"


def black_fraction(path):
    """Share of pixels that are exactly black: a sign of a glitched render (good frames have ~none)."""
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    px = np.empty(len(img.pixels), dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return float((px.reshape(-1, 4)[:, :3].sum(axis=1) == 0).mean())


t0 = time.time()
done = 0
for f in range(sc.frame_start, sc.frame_end + 1):
    path = os.path.join(out, "%04d.png" % f)
    if os.path.exists(path):
        continue
    sc.frame_set(f)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    prev = None
    for attempt in (1, 2):                         # re-render a glitched frame from scratch (caches dropped)
        bad = black_fraction(path)                 # a glitch blacks out a patch (> 0.5 %); dark pupils or shadows don't
        if bad < 0.005 or (prev is not None and abs(bad - prev) < 0.2 * prev):
            break                                  # ...and a re-render that comes back the same was never a glitch
        prev = bad
        print("RETRY frame %d (%.2f%% pure black), attempt %d" % (f, 100 * bad, attempt), flush=True)
        keep = sc.render.use_persistent_data
        sc.render.use_persistent_data = False
        bpy.ops.render.render(write_still=True)
        sc.render.use_persistent_data = keep
    done += 1
    if done % 10 == 0:
        el = time.time() - t0
        print("RENDERED %d (frame %d) %.1fs/frame" % (done, f, el / done), flush=True)
print("RENDER DONE", done, "frames in %.0fs" % (time.time() - t0), flush=True)
