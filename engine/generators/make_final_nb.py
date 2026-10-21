"""Builds grandpa_block_lab_FINAL_colab.ipynb: the engine + stories as %%writefile cells, plus the frozen (approved)
voice track and timings of the episode scenes, so Colab renders exactly what was previewed -- at 1920x1080."""
import base64
import hashlib
import json
import os
import subprocess

SRC = "/home/user/blocklab"
OUT = os.path.join(SRC, "grandpa_block_lab_FINAL_colab.ipynb")
ENGINE = ("voxelkit.py", "bl_common.py", "bl_world.py", "bl_voice.py", "bl_perform.py", "bl_scene.py", "bl_overlay.py",
          "bl_audio.py", "render.py", "bl_verify.py")
STORIES = sorted(f for f in os.listdir(os.path.join(SRC, "stories")) if f.endswith(".json"))
FROZEN = os.path.join(SRC, "frozen")                      # frozen/<slug>/voice.flac + dialogue.json
EXAMPLE = "grandpa_ep01_scene002"
cells = []


def md(text):
    cells.append(dict(cell_type="markdown", metadata={}, source=text.strip("\n").splitlines(True)))


def code(text):
    cells.append(dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=text.strip("\n").splitlines(True)))


sha = hashlib.sha1()
for name in ENGINE:                                        # newline-insensitive: %%writefile drops the final newline
    sha.update(open(os.path.join(SRC, name), "rb").read().rstrip(b"\n"))
ENGINE_SHA = sha.hexdigest()[:12]

md("""
# 🧱 Grandpa's Block Lab: FINAL render (Episode scenes, 1920×1080)

This notebook renders the **approved** scene at full quality: landscape **1920×1080, 30 fps**, picture edge to edge
(no bars), with captions, the `LIVE` badge, procedural ASMR sound and −14 LUFS audio, then runs the automatic checks.

* Default: **Episode 1, Scene 002, "Clunk, Clunk... Rest."** → `grandpa_ep01_scene002_FINAL.mp4` (+ its continuity state). Set `EXAMPLE = "grandpa_ep01_scene001"` for Scene 001.
* Grandpa's voice and timings for both scenes are **frozen** (embedded below), so the final matches the approved preview
  exactly. Set `USE_FROZEN_VOICE = False` to re-synthesise with Kokoro (`am_santa`) instead.
* Any other story still works, including the vertical 1080×1920 **Shorts** (e.g. `lock_key`, `trebuchet`): upload it in
  section 2, or set `EXAMPLE`.

**How to run**: *Runtime → Change runtime type → GPU (T4 is fine)*, then *Runtime → Run all*. Rendering is the long step
(roughly 45–75 min on a T4 for a 33 s scene) and is resumable: re-run section 7 after a disconnect.

Engine version `%s` (SHA-1 of the engine files; section 1 prints it again so you can confirm nothing changed).
""" % ENGINE_SHA)

code('''
# ---- settings ----
EXAMPLE = "%s"   # used when you don't upload a story (any file in stories/)
USE_FROZEN_VOICE = True       # True: use the approved voice track + timings embedded below (when the story has one)
USE_GPU = True
QUICK_DRAFT = False           # True: fast low-res 3D test (graphics + captions still full size)
USE_DRIVE = True              # True: keep the engine, stories and MP4s in Google Drive (MyDrive/block_lab)
SAVE_FRAMES_TO_DRIVE = True   # True: keep rendered frames in Drive (resume after a disconnect)

import os
if USE_DRIVE or SAVE_FRAMES_TO_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
WORK = "/content/drive/MyDrive/block_lab" if USE_DRIVE else "/content/block_lab"
os.makedirs(WORK + "/stories", exist_ok=True)
os.chdir(WORK)
print("engine folder:", WORK)
!nvidia-smi --query-gpu=name,memory.total --format=csv 2>/dev/null || echo "No GPU runtime: rendering will use the CPU"
''' % EXAMPLE)

md("## 1. The engine (same every time), the stories and the frozen voice tracks")
for name in ENGINE:
    code("%%writefile " + name + "\n" + open(os.path.join(SRC, name)).read())
for name in STORIES:
    code("%%writefile stories/" + name + "\n" + open(os.path.join(SRC, "stories", name)).read())
frozen = {}
for slug in sorted(os.listdir(FROZEN)) if os.path.isdir(FROZEN) else []:
    d = os.path.join(FROZEN, slug)
    frozen[slug] = dict(voice_flac=base64.b64encode(open(os.path.join(d, "voice.flac"), "rb").read()).decode(),
                        dialogue=json.load(open(os.path.join(d, "dialogue.json"))))
code('''
# frozen, approved voice tracks: {slug: {"voice_flac": base64 FLAC, "dialogue": timings + mouth curve}}
import base64, hashlib, json
FROZEN = json.loads(%r)
for slug, fz in FROZEN.items():
    os.makedirs("frozen/" + slug, exist_ok=True)
    open("frozen/%%s/voice.flac" %% slug, "wb").write(base64.b64decode(fz["voice_flac"]))
    json.dump(fz["dialogue"], open("frozen/%%s/dialogue.json" %% slug, "w"))
h = hashlib.sha1()
for name in %r:
    h.update(open(name, "rb").read().rstrip(b"\\n"))
print("engine version", h.hexdigest()[:12], "(expected %s)")
print("frozen voice tracks:", ", ".join(FROZEN) or "none")
''' % (json.dumps(frozen), list(ENGINE), ENGINE_SHA))

md("""
## 2. ⬆️ Upload a story (optional)
Click **Choose files** to render a different story. Upload nothing (or cancel) to render the `EXAMPLE`.
""")
code('''
import json, shutil
from google.colab import files
STORY = "stories/%s.json" % EXAMPLE
try:
    up = files.upload()
except Exception as e:
    up = {}
    print("upload skipped:", e)
for fn, data in up.items():
    if fn.lower().endswith(".json"):
        dst = os.path.join("stories", os.path.basename(fn))
        open(dst, "wb").write(data)
        STORY = dst
story = json.load(open(STORY))                    # fails here (with the line number) if the JSON is malformed
SLUG = story.get("slug", os.path.splitext(os.path.basename(STORY))[0])
WIDE = story.get("format", "vertical") == "wide"
print("story:", STORY, "|", story.get("title"), "|", len(story["lines"]), "lines,", len(story["structures"]), "structures |",
      "1920x1080 landscape" if WIDE else "1080x1920 Short")
shutil.rmtree("build", ignore_errors=True)        # fresh build folder for this story
FRAMES_DIR = ("/content/drive/MyDrive/block_lab/frames_" + SLUG) if SAVE_FRAMES_TO_DRIVE else "/content/frames_" + SLUG
if QUICK_DRAFT:
    FRAMES_DIR = WORK + "/build/draft"
os.makedirs(FRAMES_DIR, exist_ok=True)
''')

md("## 3. Install Blender 5.2 (and Kokoro TTS if needed) -- first run only")
code(r'''
import glob, re, subprocess, urllib.request
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
print("BLENDER =", BLENDER)
FROZEN_OK = USE_FROZEN_VOICE and os.path.exists("frozen/%s/voice.flac" % SLUG)
if not FROZEN_OK:
    !pip -q install kokoro-onnx soundfile
    KOKORO_DIR = "/content/kokoro"
    os.makedirs(KOKORO_DIR, exist_ok=True)
    rel = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
    for fn in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        if not os.path.exists(os.path.join(KOKORO_DIR, fn)):
            !wget -q {rel + fn} -O {KOKORO_DIR}/{fn}
    os.environ["KOKORO_MODEL"] = KOKORO_DIR + "/kokoro-v1.0.onnx"
    os.environ["KOKORO_VOICES"] = KOKORO_DIR + "/voices-v1.0.bin"
''')

md("## 4. Grandpa's voice + the plan (the whole edit follows his timing)")
code('''
os.makedirs("build/audio", exist_ok=True)
if FROZEN_OK:                                     # the approved track: same words, same timing as the preview
    shutil.copy(STORY, "build/story.json")
    !ffmpeg -v error -y -i frozen/{SLUG}/voice.flac -ar 48000 -ac 1 -c:a pcm_s16le build/audio/voice.wav
    shutil.copy("frozen/%s/dialogue.json" % SLUG, "build/dialogue.json")
    print("using the frozen voice track for", SLUG)
else:
    !python bl_voice.py --story {STORY}
!python bl_common.py
from IPython.display import Audio
Audio("build/audio/voice.wav")
''')

md("## 5. Build the scene + preview stills with the graphics")
code('''
plan = json.load(open("build/plan.json"))
FR = [int(plan["nf"] * k / 8) for k in range(8)]
!{BLENDER} -b --factory-startup -P bl_scene.py -- --preview {" ".join(map(str, FR))} 2>&1 | grep -E "Error|Traceback|Saved as"
os.makedirs("build/stillsrc", exist_ok=True)
for f in FR:
    shutil.copy("build/previews/%04d.png" % f, "build/stillsrc/%04d.png" % f)
!python bl_overlay.py --frames build/stillsrc --still {" ".join(map(str, FR))}
from PIL import Image
from IPython.display import display
tw, th = (384, 216) if plan["w"] > plan["h"] else (270, 480)
sheet = Image.new("RGB", (tw * 4, th * 2))
for i, f in enumerate(FR):
    sheet.paste(Image.open("build/stills/%04d.png" % f).resize((tw, th)), (tw * (i % 4), th * (i // 4)))
display(sheet)
''')

md("## 6. Sound + mix (ASMR foley, room ambience, voice; −14 LUFS)")
code('''
!python bl_audio.py
Audio("build/audio/mix.wav")
''')

md("""
## 7. Render all frames (full 1920×1080 for landscape stories)
The long step. Resumable: re-running it skips frames that already exist.
""")
code('''
gpu = "1" if USE_GPU else "0"
draft = "--draft" if QUICK_DRAFT else ""
!GPU={gpu} FRAMES_DIR={FRAMES_DIR} {BLENDER} -b -P render.py -- {draft} 2>&1 | grep -E --line-buffered "Rendering on|No CUDA|RENDERED|RENDER DONE|RETRY|Error"
print(len(os.listdir(FRAMES_DIR)), "of", plan["nf"], "frames rendered")
''')

md("## 8. Graphics, captions + encode")
code('''
!python bl_overlay.py --frames {FRAMES_DIR}
!ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate:format=duration -of compact {SLUG}.mp4
''')

md("## 9. Verify (motion, contact, clipping, frame coverage, sync, loudness, continuity)")
code('''
!{BLENDER} -b -P bl_verify.py 2>&1 | grep -E "PASS|FAIL|OVERALL"
''')

md("## 10. Watch / download the FINAL and its continuity state")
code('''
from IPython.display import Video
FINAL = SLUG + "_FINAL.mp4" if not QUICK_DRAFT else SLUG + "_DRAFT.mp4"
shutil.copy(SLUG + ".mp4", FINAL)
if os.path.exists("build/continuity.json"):
    shutil.copy("build/continuity.json", SLUG + "_continuity.json")
    files.download(SLUG + "_continuity.json")
display(Video(FINAL, embed=True, width=640 if plan["w"] > plan["h"] else 360))
files.download(FINAL)
files.download("build/verification.txt")
''')

nb = dict(cells=cells, metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3"),
                                     language_info=dict(name="python"), accelerator="GPU", colab=dict(provenance=[])),
          nbformat=4, nbformat_minor=5)
json.dump(nb, open(OUT, "w"), indent=1)
print("wrote", OUT, len(cells), "cells; engine", ENGINE_SHA, "; frozen:", list(frozen))
