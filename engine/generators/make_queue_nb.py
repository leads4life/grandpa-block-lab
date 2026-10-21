"""Builds notebooks/grandpa_block_lab_RENDER_QUEUE.ipynb (Rule 3: approve -> queue -> render one scene -> pool -> stitch).

Each run: pull the render queue from GitHub (private repo: a token in Colab Secrets), take the next approved scene that is
not yet in the pool, check out the exact engine it was approved on, render it at 1920x1080 (frames kept in Drive, so a
disconnect only costs the frame in progress), run every automatic check, and put the finished clip in MyDrive/block_lab/pool.
"""
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/grandpa-block-lab/notebooks/grandpa_block_lab_RENDER_QUEUE.ipynb"
cells = []


def md(text):
    cells.append(dict(cell_type="markdown", metadata={}, source=text.strip("\n").splitlines(True)))


def code(text):
    cells.append(dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=text.strip("\n").splitlines(True)))


md("""
# 🧱 Grandpa's Block Lab: render queue (one 30 s scene per run)

**Each run renders one approved scene** from the queue and puts the finished clip in the **pool** in your Google Drive
(`MyDrive/block_lab/pool`). Episodes are stitched from the pool later with `grandpa_block_lab_STITCH.ipynb`.

**First time only:**
* Colab → 🔑 **Secrets** (left sidebar) → add `GITHUB_TOKEN` with a GitHub token that can read `leads4life/grandpa-block-lab`.
  Then switch on **Notebook access** for it.

**Every time:**
* *Runtime → Change runtime type → GPU (T4 is fine)*, then *Runtime → Run all*.
* It takes the next scene in the queue that isn't in the pool yet. To pick one yourself, set `ONLY_SCENE`.
* Rendering is the long step (roughly 45–75 min on a T4) and is **resumable**: if Colab disconnects, run everything again.
  Frames already in Drive are skipped.
""")

code('''
# ---- settings ----
REPO = "leads4life/grandpa-block-lab"
BRANCH = "main"                 # the branch whose queue/ folder holds the approved scenes
ONLY_SCENE = ""                 # e.g. "grandpa_ep01_scene004" to render that one; "" = the next one not yet in the pool
USE_GPU = True
PART_SECONDS = 35               # long scenes render in parts of at most this many seconds, one part per run of step 5
CLEAN_FRAMES_AFTER = True       # delete a scene's frames from Drive once its clip is safely in the pool

import os, json, glob, shutil, subprocess, hashlib, datetime
from google.colab import drive
drive.mount("/content/drive")
DRIVE = "/content/drive/MyDrive/block_lab"
for d in ("pool", "failed", "frames", "work"):
    os.makedirs(os.path.join(DRIVE, d), exist_ok=True)
!nvidia-smi --query-gpu=name,memory.total --format=csv 2>/dev/null || echo "No GPU runtime: rendering will use the CPU (very slow)"
''')

md("## 1. Pull the queue from GitHub and pick the next scene")
code('''
from google.colab import userdata
TOKEN = userdata.get("GITHUB_TOKEN")
REPO_DIR = "/content/repo"
url = "https://x-access-token:%s@github.com/%s.git" % (TOKEN, REPO)
if os.path.isdir(REPO_DIR + "/.git"):
    subprocess.run(["git", "-C", REPO_DIR, "fetch", "-q", "--depth", "1", "origin", BRANCH], check=True)
    subprocess.run(["git", "-C", REPO_DIR, "reset", "-q", "--hard", "FETCH_HEAD"], check=True)
else:
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", BRANCH, url, REPO_DIR], check=True)

queue = []
for m in sorted(glob.glob(REPO_DIR + "/queue/*/manifest.json")):
    man = json.load(open(m)); man["dir"] = os.path.dirname(m); queue.append(man)
in_pool = {os.path.basename(p)[:-4] for p in glob.glob(DRIVE + "/pool/*.mp4")}
print("queue:")
for man in queue:
    print("  %-26s %-24s %s" % (man["slug"], man["title"][:24], "in pool" if man["slug"] in in_pool else "waiting"))
todo = [m for m in queue if (m["slug"] == ONLY_SCENE if ONLY_SCENE else m["slug"] not in in_pool)]
assert todo, "Nothing to render: every queued scene is already in the pool." if not ONLY_SCENE else ONLY_SCENE + " is not in the queue."
SCENE = todo[0]
SLUG = SCENE["slug"]
print("\\nrendering:", SLUG, "|", SCENE["title"], "| approved on engine", SCENE["engine_commit"][:10], "(" + SCENE["engine_sha"] + ")")
''')

md("## 2. The exact engine this scene was approved on, its story and its frozen voice")
code('''
WORK = os.path.join(DRIVE, "work", SLUG)          # in Drive: survives a disconnect
os.makedirs(WORK, exist_ok=True)
os.chdir(WORK)
c = SCENE["engine_commit"]
subprocess.run(["git", "-C", REPO_DIR, "fetch", "-q", "--depth", "1", "origin", c], check=True)
names = subprocess.run(["git", "-C", REPO_DIR, "ls-tree", "--name-only", c, "engine/"], check=True, capture_output=True, text=True).stdout.split()
for n in names:
    if n.endswith(".py"):
        data = subprocess.run(["git", "-C", REPO_DIR, "show", "%s:%s" % (c, n)], check=True, capture_output=True).stdout
        open(os.path.basename(n), "wb").write(data)
h = hashlib.sha1()
for n in SCENE["engine_files"]:
    h.update(open(n, "rb").read().rstrip(b"\\n"))
assert h.hexdigest()[:12] == SCENE["engine_sha"], "engine files differ from the approved version (%s vs %s)" % (h.hexdigest()[:12], SCENE["engine_sha"])
print("engine verified:", SCENE["engine_sha"])
shutil.rmtree("build", ignore_errors=True)
os.makedirs("build/audio", exist_ok=True)
shutil.copy(SCENE["dir"] + "/story.json", "build/story.json")
shutil.copy(SCENE["dir"] + "/dialogue.json", "build/dialogue.json")
PKG = SCENE["dir"]
if os.path.isdir(PKG + "/frozen"):                   # remembered lines a flashback echoes (earlier scenes' frozen voices)
    shutil.copytree(PKG + "/frozen", "frozen", dirs_exist_ok=True)
!ffmpeg -v error -y -i {PKG}/voice.flac -ar 48000 -ac 1 -c:a pcm_s16le build/audio/voice.wav
story = json.load(open("build/story.json"))
print("story:", story["title"], "|", len(story["lines"]), "lines | frozen voice", SCENE["film"], "s")
''')

md("## 3. Install Blender 5.2 (first run in a session only)")
code(r'''
import re, urllib.request
BLENDER_SERIES = "5.2"
base = "https://download.blender.org/release/Blender%s/" % BLENDER_SERIES
if not glob.glob("/content/blender-*/blender"):
    req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0"})   # blender.org refuses Python's default agent
    html = urllib.request.urlopen(req).read().decode()
    builds = sorted(set(re.findall(r"blender-%s\.(\d+)-linux-x64\.tar\.xz" % re.escape(BLENDER_SERIES), html)), key=int)
    tarball = "blender-%s.%s-linux-x64.tar.xz" % (BLENDER_SERIES, builds[-1])
    print("downloading", base + tarball)
    !wget -q --user-agent="Mozilla/5.0" {base + tarball} -O /content/blender.tar.xz
    assert os.path.getsize("/content/blender.tar.xz") > 100e6, "Blender download failed - check " + base
    !tar -xf /content/blender.tar.xz -C /content && rm /content/blender.tar.xz
!apt-get -qq install -y libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 > /dev/null 2>&1
BLENDER = sorted(glob.glob("/content/blender-*/blender"))[-1]
BPY = sorted(glob.glob(os.path.join(os.path.dirname(BLENDER), "*", "python", "bin", "python3*")))[0]
!{BPY} -m ensurepip -q > /dev/null 2>&1
!{BPY} -m pip install -q scipy
!{BLENDER} --version | head -1
''')

md("## 4. Plan, scene and sound")
code('''
!python bl_common.py
!{BLENDER} -b --factory-startup -P bl_scene.py 2>&1 | grep -E "Error|Traceback" || true
!python bl_audio.py
plan = json.load(open("build/plan.json"))
print(plan["nf"], "frames,", plan["w"], "x", plan["h"])
''')

md("""
## 5. Render the frames (1920×1080), one part at a time
The long step. A scene longer than `PART_SECONDS` renders in parts of about 30 s: each run of this cell renders the
next part, so a session never has to last the whole scene. Resumable: frames already in Drive are skipped. Once every
part is done, carry on to step 6 (one clip per scene goes to the pool).
""")
code('''
import math
FRAMES_DIR = os.path.join(DRIVE, "frames", SLUG)
os.makedirs(FRAMES_DIR, exist_ok=True)
gpu = "1" if USE_GPU else "0"
nf = plan["nf"]
n_parts = max(1, math.ceil(nf / (PART_SECONDS * 30)))
bounds = [round(nf * k / n_parts) for k in range(n_parts + 1)]
have = lambda a, b: sum(os.path.exists(os.path.join(FRAMES_DIR, "%04d.png" % f)) for f in range(a, b))
todo = [k for k in range(n_parts) if have(bounds[k], bounds[k + 1]) < bounds[k + 1] - bounds[k]]
if todo:
    k = todo[0]
    print("rendering part %d of %d: frames %d-%d (%.1f-%.1f s)" % (k + 1, n_parts, bounds[k], bounds[k + 1] - 1, bounds[k] / 30, bounds[k + 1] / 30))
    a, b = bounds[k], bounds[k + 1] - 1
    !GPU={gpu} FRAMES_DIR={FRAMES_DIR} FRAME_FROM={a} FRAME_TO={b} {BLENDER} -b -P render.py 2>&1 | grep -E --line-buffered "Rendering on|No CUDA|RENDERED|RENDER DONE|RETRY|Error"
done = have(0, nf)
print(done, "of", nf, "frames rendered;", "parts done: %d of %d" % (sum(have(bounds[k], bounds[k + 1]) == bounds[k + 1] - bounds[k] for k in range(n_parts)), n_parts))
assert done >= nf, "Not all parts are rendered yet: run this cell again for the next part."
''')

md("## 6. Graphics, captions, encode and every automatic check")
code('''
!python bl_overlay.py --frames {FRAMES_DIR}
out = subprocess.run([BLENDER, "-b", "-P", "bl_verify.py"], capture_output=True, text=True).stdout
report = [l for l in out.splitlines() if l.startswith(("[PASS]", "[FAIL]", "OVERALL"))]
print("\\n".join(report))
open("build/verification.txt", "w").write("\\n".join(report) + "\\n")
fails = [l for l in report if l.startswith("[FAIL]")]
accepted = SCENE.get("accepted_fails", [])           # exceptions you approved with the preview, e.g. a 1 cm hand graze
unexpected = [l for l in fails if not any(l.startswith("[FAIL] " + a) for a in accepted)]
print("\\n%d checks failed; %d of them were accepted at approval" % (len(fails), len(fails) - len(unexpected)))
''')

md("## 7. Into the pool (or into failed/, with the reason)")
code('''
stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
if unexpected:
    dst = os.path.join(DRIVE, "failed", SLUG); os.makedirs(dst, exist_ok=True)
    shutil.copy("build/verification.txt", dst + "/verification.txt")
    open(dst + "/reason.txt", "w").write(stamp + "\\nNew failures (not accepted at approval):\\n" + "\\n".join(unexpected) + "\\n")
    print("NOT pooled -- see", dst)
else:
    pool = os.path.join(DRIVE, "pool")
    shutil.copy(SLUG + ".mp4", pool + "/%s.mp4" % SLUG)
    for src, name in (("build/continuity.json", "_continuity.json"), ("build/verification.txt", "_verification.txt"),
                      (SCENE["dir"] + "/story.json", "_story.json"), (SCENE["dir"] + "/manifest.json", "_manifest.json")):
        if os.path.exists(src):
            shutil.copy(src, pool + "/" + SLUG + name)
    with open(pool + "/POOL_LOG.txt", "a") as f:
        f.write("%s  %s  %s  engine %s  %s\\n" % (stamp, SLUG, SCENE["title"], SCENE["engine_sha"], "accepted: " + "; ".join(accepted) if accepted else "all checks passed"))
    print("in the pool:", pool + "/%s.mp4" % SLUG)
    if CLEAN_FRAMES_AFTER:
        shutil.rmtree(FRAMES_DIR, ignore_errors=True)
from IPython.display import Video
Video(SLUG + ".mp4", embed=True, width=640)
''')

nb = dict(cells=cells, metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3"),
                                     language_info=dict(name="python"), accelerator="GPU", colab=dict(provenance=[])),
          nbformat=4, nbformat_minor=5)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(nb, open(OUT, "w"), indent=1)
print("wrote", OUT, len(cells), "cells")
