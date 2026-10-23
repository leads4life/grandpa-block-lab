"""Writes GBL_EP01_FINAL_RENDER.ipynb (the Colab notebook for the final render). Run after editing the cells below."""
import json
import os

CELLS = []


def md(s):
    CELLS.append(dict(cell_type="markdown", metadata={}, source=s.strip("\n")))


def code(s):
    CELLS.append(dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=s.strip("\n")))


md("""
# 🧱 Grandpa's Block Lab: Episode 1 FINAL RENDER

Renders the whole episode at **native 1920×1080, 30 fps** from the production package, then builds the **archival master**
and the **YouTube master** (4K upscale), and runs the final QA.

**Before the first run**
1. *Runtime → Change runtime type →* **A100 GPU** (or L4; T4 works but is slow).
2. *Runtime → Run all.*
3. Step 1 shows a **Choose Files** button: pick `GBL_EP01_PRODUCTION_v2.zip` from your computer. The notebook saves it
   in Google Drive (`MyDrive/block_lab/final/`), so later sessions don't ask again.

**It is resumable.** The render is long (the benchmark in step 3 prints the estimate for your GPU). Colab sessions end
after several hours: when that happens, just open the notebook again and *Run all*. Every finished ~1-minute segment
and every finished frame is kept in Drive; nothing is rendered twice.

**Several workers (optional, faster).** Make a copy of this notebook (*File → Save a copy in Drive*), open the copy,
set `WORKER = "B"` in its first cell, choose a GPU and *Run all*. The workers share the segments out by themselves
through the files in `work/` and never do the same one twice; if one session dies, another takes over its segment
after 15 minutes. Each copy needs a **different letter** (A, B, C...). Close any older version of this notebook first.

**Where things go** (`MyDrive/block_lab/final/`)
* `RENDER_STATUS.txt`: a small file to check from the Drive app -- which segments are COMPLETE, who is on what
* `work/`: the checkpoint (`manifest.json` + `claims/`, `done/`), prepared scenes, frames in progress, finished segments
* `masters/`: the archival master, the YouTube master, `AUDIO/` (final mix + stems, 48 kHz / 24-bit WAV), `QA/`
""")

code("""
# ---- settings ----
DRIVE_DIR = "/content/drive/MyDrive/block_lab/final"
ZIP_NAME = "GBL_EP01_PRODUCTION_v2.zip"   # v2: several workers + RENDER_STATUS.txt
WORKER = "A"                 # this session's letter: "A" here; a second copy of the notebook uses "B", a third "C"...
HOURS_THIS_SESSION = 20      # stop cleanly before Colab ends the session (Colab Pro: up to ~24 h)
RUN_BENCHMARK = True         # worker A only: renders 3 heavy frames first and prints the time estimate (2-3 minutes)

import os, json, glob, shutil, subprocess, hashlib, sys, uuid
SESSION = uuid.uuid4().hex[:8]                    # this notebook session (tells the workers' files apart)
print("worker", WORKER, "| session", SESSION)
from google.colab import drive
drive.mount("/content/drive")
WORK, OUT, PKG = DRIVE_DIR + "/work", DRIVE_DIR + "/masters", "/content/pkg/GBL_EP01_PRODUCTION"
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
print("GPU:", gpu or "NONE -- Runtime > Change runtime type > T4 GPU (on CPU this would take days)")
free = shutil.disk_usage("/content/drive/MyDrive").free / 1e9
print("Google Drive free: %.1f GB (needs about 10 GB while rendering)" % free)
if free < 10:
    print("WARNING: Drive is nearly full -- free some space first, or the render will stop when Drive fills up.")
""")

md("## 1. Unpack and check the production package")
code("""
zp = os.path.join(DRIVE_DIR, ZIP_NAME)
if not os.path.exists(zp):                       # first run: pick the zip on your computer; it is kept in Drive for later sessions
    from google.colab import files
    print("Click 'Choose Files' below and pick %s from your computer (about 158 MB: takes a few minutes)." % ZIP_NAME)
    up = files.upload()
    zips = [n for n in up if n.lower().endswith(".zip")]
    assert zips, "That was not a .zip file -- run this cell again and pick %s" % ZIP_NAME
    with open(zp + ".partial", "wb") as f:
        f.write(up[zips[0]])
    os.replace(zp + ".partial", zp)
    os.remove(zips[0]) if os.path.exists(zips[0]) else None
    del up
    print("saved to Drive:", zp)
stamp = "%d-%d" % (os.path.getsize(zp), int(os.path.getmtime(zp)))
if not os.path.exists(PKG + "/.unpacked") or open(PKG + "/.unpacked").read() != stamp:
    shutil.rmtree("/content/pkg", ignore_errors=True)
    shutil.unpack_archive(zp, "/content/pkg")
    open(PKG + "/.unpacked", "w").write(stamp)
TOOL = [sys.executable, PKG + "/tools/gbl_final.py"]
def gbl(*args):
    p = subprocess.Popen(TOOL + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(line, end="")
    assert p.wait() == 0, "stopped -- see the messages above"
gbl("validate", "--pkg", PKG)
""")

md("## 2. Install Blender 5.2 (once per session)")
code("""
import re, urllib.request
WANT = "5.2.2"                                   # the version every scene was approved on
base = "https://download.blender.org/release/Blender5.2/"
if not glob.glob("/content/blender-*/blender"):
    req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})   # blender.org refuses Python's default agent
    html = urllib.request.urlopen(req).read().decode()
    builds = sorted(set(re.findall(r"blender-5\\.2\\.(\\d+)-linux-x64\\.tar\\.xz", html)), key=int)
    ver = WANT if ("blender-%s-linux-x64.tar.xz" % WANT) in html else "5.2." + builds[-1]
    if ver != WANT:
        print("NOTE: %s is not on the server; using %s (same LTS series)" % (WANT, ver))
    !wget -q --user-agent="Mozilla/5.0" {base}blender-{ver}-linux-x64.tar.xz -O /content/blender.tar.xz
    assert os.path.getsize("/content/blender.tar.xz") > 100e6, "Blender download failed - check " + base
    !tar -xf /content/blender.tar.xz -C /content && rm /content/blender.tar.xz
!apt-get -qq install -y libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 > /dev/null 2>&1
BLENDER = sorted(glob.glob("/content/blender-*/blender"))[-1]
BPY = sorted(glob.glob(os.path.join(os.path.dirname(BLENDER), "*", "python", "bin", "python3*")))[0]
!{BPY} -m ensurepip -q > /dev/null 2>&1
!{BPY} -m pip install -q scipy
!{BLENDER} --version | head -1
""")

md("""
## 3. Benchmark (optional): how long will the render take on this GPU?
Each scene is prepared when a worker first needs it: it gets the **exact engine it was approved on**, its approved
story and its frozen voice, and is built in Blender (the plan is checked against the approved one).
""")
code("""
W_ARGS = ["--pkg", PKG, "--work", WORK, "--blender", BLENDER, "--worker", WORKER, "--session", SESSION]
if RUN_BENCHMARK and WORKER == "A" and not os.path.exists(WORK + "/plan.json") and not os.path.exists(WORK + "/manifest.json"):
    gbl("benchmark", *W_ARGS)
else:
    print("skipped (already rendering, another worker, or RUN_BENCHMARK = False)")
""")

md("""
## 4. Render (the long step, resumable)
Each worker claims the next free ~1-minute segment: frames → overlay graphics → a visually lossless segment file,
checked and then moved into `work/segments/`. Stops cleanly after `HOURS_THIS_SESSION`. **If the session ends, Run all
again** (same letter): it carries on with its own unfinished segment.
""")
code("""
gbl("render", *W_ARGS, "--hours", str(HOURS_THIS_SESSION))
""")

md("## 5. Status")
code("""
gbl("status", *W_ARGS)
m = json.load(open(WORK + "/manifest.json"))
ALL_DONE = all(x["state"] == "COMPLETE" for x in m["segments"])
print("\\nready to assemble" if ALL_DONE else "\\nnot finished yet: the other workers are still on it, or Run all again (a new session if this one is ending)")
""")

md("""
## 6. Masters
* **Archival master**: the segments joined without re-encoding (1080p, 4:4:4, Rec.709) + 24-bit PCM audio (.mkv)
* **YouTube master**: 4K (3840×2160) lanczos upscale of the 1080p render (labelled as upscaled), H.264 High,
  AAC-LC 384 kb/s, Rec.709, fast start. The 4K upload makes YouTube serve its higher-quality stream.
""")
code("""
MINE = False
if ALL_DONE:
    gbl("assemble", *W_ARGS, "--out", OUT)            # with several workers, only one builds the masters
    asm = json.load(open(OUT + "/ASSEMBLY.json")) if os.path.exists(OUT + "/ASSEMBLY.json") else {}
    MINE = asm.get("session") == SESSION
    if not MINE:
        print("another worker is building the masters -- its notebook runs the QA step")
""")

md("## 7. Final QA")
code("""
if ALL_DONE and MINE:
    gbl("qa", *W_ARGS, "--out", OUT)
    rep = json.load(open(OUT + "/QA/final_qa_report.json"))
    print("\\nRESULT:", rep["result"])
    print("Upload this file to YouTube:", OUT + "/" + rep["youtube"])
""")

md("## 8. Look at a moment (720p clip, 20 s)")
code("""
START = "8:30"   # m:ss into the episode
if ALL_DONE and MINE:
    rep = json.load(open(OUT + "/QA/final_qa_report.json"))
    !ffmpeg -v error -y -ss {START} -t 20 -i "{OUT}/{rep['youtube']}" -vf scale=1280:-2 -c:v libx264 -crf 20 -c:a aac /content/look.mp4
    from IPython.display import Video
    display(Video("/content/look.mp4", embed=True, width=720))
""")

nb = dict(cells=CELLS, metadata=dict(accelerator="GPU", colab=dict(provenance=[], gpuType="T4"),
                                     kernelspec=dict(display_name="Python 3", name="python3"), language_info=dict(name="python")),
          nbformat=4, nbformat_minor=0)
for c in nb["cells"]:
    lines = c["source"].split("\n")
    c["source"] = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
json.dump(nb, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "GBL_EP01_FINAL_RENDER.ipynb"), "w"), indent=1)
print("wrote GBL_EP01_FINAL_RENDER.ipynb")
