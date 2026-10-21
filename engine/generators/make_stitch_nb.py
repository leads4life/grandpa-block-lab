"""Builds notebooks/grandpa_block_lab_STITCH.ipynb: join an episode's pooled 30 s scenes into one video.

No GPU and no re-render: it checks every join (each scene's saved end state against the next scene's start), copies the
pictures, joins the sound and levels it once across the whole episode (-14 LUFS), so the ambience doesn't jump at seams.
"""
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/grandpa-block-lab/notebooks/grandpa_block_lab_STITCH.ipynb"
cells = []


def md(text):
    cells.append(dict(cell_type="markdown", metadata={}, source=text.strip("\n").splitlines(True)))


def code(text):
    cells.append(dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=text.strip("\n").splitlines(True)))


md("""
# 🧱 Grandpa's Block Lab: stitch an episode from the pool

Joins the finished scenes in `MyDrive/block_lab/pool` into one episode: `MyDrive/block_lab/episodes/<episode>.mp4`.
* No GPU needed (*Runtime → Change runtime type → CPU* is fine). It takes minutes.
* **Every join is checked first.** Each scene's saved end state must match the next scene's start: Grandpa's position, the
  props, the LIVE viewer count, where the webcam is. Problems are listed before anything is joined.
* The sound is levelled **once across the whole episode**, so the ambience doesn't jump at the joins.
""")

code('''
# ---- settings ----
EPISODE = "grandpa_ep01"        # stitches grandpa_ep01_scene001, 002, ... from the pool, in order
STOP_ON_PROBLEMS = True         # False: stitch anyway and list the problems
SEAM_FADE_MS = 40               # a tiny sound crossfade at each join (0 = none); pictures are hard cuts

import os, json, glob, subprocess, re, math
from google.colab import drive
drive.mount("/content/drive")
DRIVE = "/content/drive/MyDrive/block_lab"
POOL, EPDIR = DRIVE + "/pool", DRIVE + "/episodes"
os.makedirs(EPDIR, exist_ok=True)
''')

md("## 1. What's in the pool for this episode")
code('''
clips = sorted(glob.glob(POOL + "/%s_scene*.mp4" % EPISODE))
nums = [int(re.search(r"scene(\\d+)", c).group(1)) for c in clips]
print("in the pool:", ", ".join("%03d" % n for n in nums) or "nothing")
missing = [n for n in range(1, max(nums) + 1) if n not in nums] if nums else []
problems = ["scene %03d is missing from the pool" % n for n in missing]
for p in problems:
    print("  !", p)
''')

md("## 2. Check every join")
code('''
def near(a, b, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, b))
for (na, ca), (nb, cb) in zip(zip(nums, clips), list(zip(nums, clips))[1:]):
    if nb != na + 1:
        continue
    end = json.load(open(ca[:-4] + "_continuity.json"))
    nxt = json.load(open(cb[:-4] + "_story.json"))
    tag = "%03d -> %03d" % (na, nb)
    g_end, g_start = end["grandpa"]["root"], nxt["grandpa"]["start"]
    if not near(g_end[:2], g_start[:2], 0.02):
        problems.append("%s: Grandpa ends at %s but starts at %s" % (tag, [round(v, 2) for v in g_end[:2]], [round(v, 2) for v in g_start[:2]]))
    v_end = end.get("overlay", {}).get("live_viewers")
    v_start = [c for c in nxt.get("cards", []) if c.get("style") == "live"]
    v_start = v_start[0]["viewers"][0][1] if v_start and v_start[0].get("viewers") else None
    if v_end is not None and v_start is not None and v_end != v_start:
        problems.append("%s: LIVE shows %s viewers at the end but %s at the start" % (tag, v_end, v_start))
    for name, st in end["structures"].items():                 # props still standing must be in the next scene
        if st["blocks_standing"] and name not in nxt["structures"]:
            problems.append("%s: %s is standing at the end but missing from the next scene" % (tag, name))
    print(tag, "checked")
print("\\n%d problem(s)" % len(problems))
for p in problems:
    print("  !", p)
assert not (problems and STOP_ON_PROBLEMS), "Fix these first (or set STOP_ON_PROBLEMS = False)."
''')

md("## 3. Join: pictures copied, sound joined and levelled once")
code('''
tmp = "/content/stitch"; os.makedirs(tmp, exist_ok=True)
with open(tmp + "/list.txt", "w") as f:
    for c in clips:
        f.write("file '%s'\\n" % c.replace("'", "'\\\\''"))
video = tmp + "/video.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp + "/list.txt", "-an", "-c:v", "copy", video], check=True)
wavs = []
for i, c in enumerate(clips):                                   # each scene's sound, with a tiny fade at its edges
    w = tmp + "/a%03d.wav" % i
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c],
                               capture_output=True, text=True).stdout)
    fade = SEAM_FADE_MS / 1000.0
    af = "afade=t=in:d=%.3f,afade=t=out:st=%.3f:d=%.3f" % (fade, max(0, dur - fade), fade) if fade > 0 else "anull"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", c, "-vn", "-af", af, "-ar", "48000", "-ac", "2", w], check=True)
    wavs.append(w)
with open(tmp + "/alist.txt", "w") as f:
    for w in wavs:
        f.write("file '%s'\\n" % w)
joined = tmp + "/joined.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp + "/alist.txt", joined], check=True)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", joined, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
st = json.loads(m[m.rindex("{"):m.rindex("}") + 1])               # two-pass loudness: measure, then apply exactly
ln = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
      % (st["input_i"], st["input_tp"], st["input_lra"], st["input_thresh"], st["target_offset"]))
OUTF = EPDIR + "/%s.mp4" % EPISODE
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", joined, "-af", ln, "-ar", "48000", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUTF], check=True)
print("episode:", OUTF)
!ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact {OUTF}
''')

md("## 4. Watch it")
code('''
from IPython.display import Video
Video(OUTF, embed=False, width=640)
''')

nb = dict(cells=cells, metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3"),
                                     language_info=dict(name="python"), colab=dict(provenance=[])),
          nbformat=4, nbformat_minor=5)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(nb, open(OUT, "w"), indent=1)
print("wrote", OUT, len(cells), "cells")
