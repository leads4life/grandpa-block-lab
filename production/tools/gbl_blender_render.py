"""Render a range of one scene's frames at the final settings (run inside Blender, called by gbl_final.py).

    blender -b --factory-startup -P gbl_blender_render.py -- BLEND OUT_DIR FROM TO SETTINGS.json [DEADLINE_EPOCH]

FROM/TO are the scene's own frame numbers (TO exclusive). Frames that already exist in OUT_DIR are skipped. Each frame is
rendered to a local temp file, checked for glitch-black patches (re-rendered once from scratch if found), then copied in
as NNNN.png.partial and renamed -- so a frame in OUT_DIR is always complete, even if the session dies mid-copy.
Stops cleanly (exit 0, "DEADLINE") once DEADLINE_EPOCH has passed.
"""
import json
import os
import shutil
import sys
import tempfile
import time

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
blend, out, f0, f1, settings = argv[0], argv[1], int(argv[2]), int(argv[3]), json.load(open(argv[4]))
deadline = float(argv[5]) if len(argv) > 5 else 0.0
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene
os.makedirs(out, exist_ok=True)
tmp = tempfile.mkdtemp(prefix="gbl_render_")

r, cy = sc.render, sc.cycles
r.resolution_x, r.resolution_y = settings["width"], settings["height"]
r.resolution_percentage = settings.get("test_scale", 100)
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
r.image_settings.color_depth = "8"
r.image_settings.compression = settings["png_compression"]
cy.samples = settings["samples"]
cy.use_adaptive_sampling = True
cy.adaptive_threshold = settings["adaptive_threshold"]
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.denoising_quality = settings["denoising_quality"]
cy.denoising_prefilter = settings["denoising_prefilter"]

device = "CPU"
if settings.get("gpu", True):
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
            cy.device = "GPU"
            cy.denoising_use_gpu = True
            device = "%s (%s)" % (kind, ", ".join(d.name for d in devs))
            break
print("DEVICE %s | %dx%d @ %d%% | %d samples, adaptive %.3f, OIDN %s/%s" % (
    device, r.resolution_x, r.resolution_y, r.resolution_percentage, cy.samples, cy.adaptive_threshold,
    cy.denoising_quality, cy.denoising_prefilter), flush=True)


def black_fraction(path):
    """Share of pixels that are exactly black: a sign of a glitched render (good frames have ~none)."""
    import numpy as np
    img = bpy.data.images.load(path, check_existing=False)
    px = np.empty(len(img.pixels), dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return float((px.reshape(-1, 4)[:, :3].sum(axis=1) == 0).mean())


t0, done = time.time(), 0
for f in range(f0, f1):
    final = os.path.join(out, "%04d.png" % f)
    if os.path.exists(final):
        continue
    if deadline and time.time() > deadline:
        print("DEADLINE reached -- stopping cleanly before frame %d" % f, flush=True)
        break
    ts = time.time()
    path = os.path.join(tmp, "%04d.png" % f)
    sc.frame_set(f)
    r.filepath = path
    bpy.ops.render.render(write_still=True)
    prev = None
    for attempt in (1, 2):                         # re-render a glitched frame from scratch (caches dropped)
        bad = black_fraction(path)                 # a glitch blacks out a patch (> 0.5 %); dark pupils or shadows don't
        if bad < 0.005 or (prev is not None and abs(bad - prev) < 0.2 * prev):
            break                                  # ...and a re-render that comes back the same was never a glitch
        prev = bad
        print("RETRY frame %d (%.2f%% pure black), attempt %d" % (f, 100 * bad, attempt), flush=True)
        keep = r.use_persistent_data
        r.use_persistent_data = False
        bpy.ops.render.render(write_still=True)
        r.use_persistent_data = keep
    shutil.copyfile(path, final + ".partial")
    os.replace(final + ".partial", final)
    os.remove(path)
    done += 1
    print("FRAME %d %.2fs" % (f, time.time() - ts), flush=True)
shutil.rmtree(tmp, ignore_errors=True)
print("RENDER DONE %d frames in %.0fs" % (done, time.time() - t0), flush=True)
