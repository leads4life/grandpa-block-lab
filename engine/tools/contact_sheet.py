"""Approve before preview (rev 4): one still for every talking line (mid-line) and every new camera shot, labelled,
on one sheet for the user -- the camera plan and every face to chat, before a preview is rendered.

    python3 contact_sheet.py BUILD_DIR OUT.png [--scale 30] [--samples 10] [--cols 4]

Run from the engine folder (needs bpy). Stills are the raw camera picture (no overlay cards); labels say what is said.
"""
import json
import os
import sys

import bpy
from PIL import Image, ImageDraw, ImageFont

build, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
SCALE, SAMPLES, COLS = arg("--scale", 30), arg("--samples", 10), arg("--cols", 4)
P = json.load(open(os.path.join(build, "plan.json")))
lens = json.load(open(os.path.join(build, "lens.json"))) if os.path.exists(os.path.join(build, "lens.json")) else {"lines": []}
verdict = {r["id"]: r for r in lens["lines"]}
FPS = P["fps"]

shots = []                                                     # (frame, label): every cut, then every line
cam = P["camera"]
for a, b in zip(cam, cam[1:]):
    if 0 < b["t"] - a["t"] <= 1.5 / FPS:                       # a one-frame step = a cut: show the new shot
        shots.append((int(round(b["t"] * FPS)) + 3, "SHOT  az %d  el %d  %.1f m" % (b["az"], b["el"], b["dist"])))
shots.insert(0, (3, "SHOT  az %d  el %d  %.1f m (opening)" % (cam[0]["az"], cam[0]["el"], cam[0]["dist"])))
for ln in P["lines"]:
    r = verdict.get(ln["id"])
    tag = "" if r is None else ("  [lens %s]" % ("OK" if r["ok"] else "SIDE-ON")) if r["median_deg"] is not None else "  [voice-over]"
    shots.append((int((ln["start"] + ln["end"]) / 2 * FPS), '"%s"%s' % (ln["text"], tag)))
shots.sort()

bpy.ops.wm.open_mainfile(filepath=os.path.join(build, "blocklab.blend"))
sc = bpy.context.scene
sc.render.resolution_percentage, sc.cycles.samples = SCALE, SAMPLES
tmp = os.path.join(build, "contact")
os.makedirs(tmp, exist_ok=True)
ims = []
for f, label in shots:
    p = os.path.join(tmp, "%04d.png" % f)
    if not os.path.exists(p):
        sc.frame_set(min(f, P["nf"] - 1))
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
    ims.append((Image.open(p).convert("RGB"), f, label))

w, h = ims[0][0].size
FD = "/usr/share/fonts/truetype/dejavu"
fb, fs = ImageFont.truetype(os.path.join(FD, "DejaVuSans-Bold.ttf"), 17), ImageFont.truetype(os.path.join(FD, "DejaVuSans.ttf"), 15)
LAB = 46
rows = (len(ims) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * w, 50 + rows * (h + LAB)), "white")
d = ImageDraw.Draw(sheet)
d.text((10, 12), "%s  --  %d stills (every shot + every line)  --  %.1f s" % (P["title"], len(ims), P["film"]), fill="black", font=fb)
for i, (im, f, label) in enumerate(ims):
    x, y = (i % COLS) * w, 50 + (i // COLS) * (h + LAB)
    sheet.paste(im, (x, y))
    d.text((x + 6, y + h + 3), "%.1f s" % (f / FPS), fill=(180, 60, 0) if label.startswith("SHOT") else "black", font=fb)
    words, line, lines = label.split(), "", []
    for wd in words:
        if fs.getlength(line + " " + wd) > w - 70:
            lines.append(line); line = wd
        else:
            line = (line + " " + wd).strip()
    lines.append(line)
    for k, t in enumerate(lines[:2]):
        d.text((x + 62, y + h + 3 + 19 * k), t, fill="black", font=fs)
sheet.save(out)
print("contact sheet:", out, sheet.size, len(ims), "stills")
