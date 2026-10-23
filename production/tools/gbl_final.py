"""Grandpa's Block Lab -- final episode renderer: one global timeline, ~1-minute segments, checkpoint/resume.

    python3 gbl_final.py validate  --pkg PKG
    python3 gbl_final.py prepare   --pkg PKG --work WORK --blender BLENDER
    python3 gbl_final.py benchmark --pkg PKG --work WORK --blender BLENDER
    python3 gbl_final.py render    --pkg PKG --work WORK --blender BLENDER [--hours H] [--segments N] [--retry-failed]
    python3 gbl_final.py status    --pkg PKG --work WORK
    python3 gbl_final.py assemble  --pkg PKG --work WORK --out OUT
    python3 gbl_final.py qa        --pkg PKG --work WORK --out OUT

PKG  = the unzipped production package (episode.json at its root).
WORK = a folder that survives a disconnect (Google Drive in Colab): prepared scenes, the frames of the segment in
       progress, finished segments and manifest.json (the checkpoint).
OUT  = where the masters, the audio deliverables and the QA report go.

Segment states: PENDING -> ACTIVE (a worker has claimed it: rendering, then validating) -> COMPLETE. A segment that keeps
failing becomes FAILED (re-run with --retry-failed); a COMPLETE segment whose file is missing or damaged, or whose scene
inputs changed, becomes NEEDS_REBUILD; a claim whose worker stopped answering becomes STALLED and is taken over.
Everything is resumable: run the same command again and it carries on where it stopped.

Several workers: run render in more than one Colab session against the same WORK folder, each with its own
--worker letter (A, B, C...). They share the segments out between them through the files in WORK (see "workers" below).

Sandbox-test options (never for the final): --scale PCT --samples N --span A B --segment-frames N, fixed at the first
render into a WORK folder (the manifest remembers them).
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------------------------------------------- helpers
def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha256(path, block=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def write_json(path, data):
    """Atomic: a crash mid-write never leaves a half-written file (the temp name is unique, so two writers never clash)."""
    tmp = "%s.%d.%s.partial" % (path, os.getpid(), os.urandom(3).hex())
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def probe(path, stream="v:0", entries="stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_packets,color_space,"
                                      "color_primaries,color_transfer,color_range,sample_rate,channels,sample_fmt,"
                                      "bits_per_raw_sample,profile"):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-count_packets", "-show_entries",
                          entries, "-of", "json", path], check=True, capture_output=True, text=True).stdout
    s = json.loads(out).get("streams", [])
    return s[0] if s else {}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def load_pkg(pkg):
    ep = json.load(open(os.path.join(pkg, "episode.json")))
    st = json.load(open(os.path.join(pkg, "config", "render_settings.json")))
    return ep, st


def engine_hash(folder, files):
    h = hashlib.sha1()
    for n in files:
        h.update(open(os.path.join(folder, n), "rb").read().rstrip(b"\n"))
    return h.hexdigest()[:12]


# --------------------------------------------------------------------------------------------------------------- validate
def cmd_validate(a):
    pkg = a.pkg
    ep, st = load_pkg(pkg)
    bad = []
    for line in open(os.path.join(pkg, "CHECKSUMS.sha256")):
        want, name = line.rstrip("\n").split("  ", 1)
        p = os.path.join(pkg, name)
        if not os.path.exists(p):
            bad.append("missing " + name)
        elif sha256(p) != want:
            bad.append("damaged " + name)
    total = 0
    for s in ep["scenes"]:
        if s["start_frame"] != total:
            bad.append("%s starts at %d, expected %d" % (s["id"], s["start_frame"], total))
        total += s["frames"]
        eng = os.path.join(pkg, s["engine"])
        if engine_hash(eng, s["engine_files"]) != s["engine_sha"]:
            bad.append("%s: engine files differ from the approved version" % s["id"])
    if total != ep["total_frames"]:
        bad.append("scene frames add up to %d, episode says %d" % (total, ep["total_frames"]))
    mix = os.path.join(pkg, ep["audio"]["final_mix"])
    a_ = probe(mix, "a:0", "stream=sample_rate,channels")
    n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration_ts",
                            "-of", "csv=p=0", mix], capture_output=True, text=True).stdout.strip() or 0)
    if int(a_.get("sample_rate", 0)) != 48000 or n != ep["total_frames"] * 48000 // ep["fps"]:
        bad.append("final mix: %s Hz, %d samples (expected 48000 Hz, %d)" % (a_.get("sample_rate"), n, ep["total_frames"] * 1600))
    print("package:", ep["title"], "|", len(ep["scenes"]), "scenes |", total, "frames (%.2f s) | %dx%d @ %d fps" % (
        total / ep["fps"], st["width"], st["height"], ep["fps"]))
    if bad:
        print("PACKAGE PROBLEMS:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("package OK: every file matches its checksum, every scene's engine matches its approval, audio length matches")


# ---------------------------------------------------------------------------------------------------------------- workers
# Several Colab sessions can render one episode together. They share WORK (Google Drive) but never write the same file:
#   claims/<seg>__<worker>.json   "I am rendering this segment" + a heartbeat every minute (only that worker writes it)
#   done/<seg>__<worker>.json     a finished, verified segment: segments/<seg>__<worker>.mp4 (only that worker writes it)
#   failed/<seg>__<worker>.json   attempts that failed on that worker
#   manifest.json                 a status view rebuilt from the files above (PENDING / ACTIVE / COMPLETE / ...)
# Google Drive shows one machine's writes to another after a delay, so a worker claims a segment, waits SETTLE seconds,
# and backs off if someone claimed it first. If two still end up on the same segment, nothing breaks: each writes its own
# files and the first finished one is used. A claim whose heartbeat stops for STALE seconds (the session died) is
# taken over by another worker. Worker "A" uses the original single-worker folders, so an earlier run carries on.
STATES = ("PENDING", "ACTIVE", "STALLED", "COMPLETE", "FAILED", "NEEDS_REBUILD")
BEAT = 60.0


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None                                        # missing, or caught mid-sync on Drive


def wdir(a, wid=None):
    wid = wid or a.worker
    return a.work if wid == "A" else os.path.join(a.work, "workers", wid)


def scene_dir(a, s, wid=None):
    return os.path.join(wdir(a, wid), "scenes", s["dir_name"])


def frames_dir(a, s, wid=None):
    return os.path.join(wdir(a, wid), "frames", s["dir_name"])


class Superseded(Exception):
    """Another worker finished this segment first: stop working on it."""


# ---------------------------------------------------------------------------------------------------------------- prepare
def prepare_scene(a, s):
    """Copy the scene's pinned engine + approved story + frozen voice into this worker's folder, build plan and Blender
    scene. Skipped when already prepared from the same inputs."""
    d = scene_dir(a, s)
    mark = os.path.join(d, "PREPARED.json")
    mk = read_json(mark)
    if mk and mk.get("inputs") == s["inputs_sha"] and os.path.exists(os.path.join(d, "build", "blocklab.blend")):
        return "ready"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "build", "audio"))
    os.makedirs(os.path.join(d, "stories"))
    eng = os.path.join(a.pkg, s["engine"])
    for n in s["engine_files"]:
        shutil.copy(os.path.join(eng, n), d)
    src = os.path.join(a.pkg, s["dir"])
    shutil.copy(os.path.join(src, "story.json"), os.path.join(d, "build", "story.json"))
    shutil.copy(os.path.join(src, "story.json"), os.path.join(d, "stories", s["slug"] + ".json"))
    shutil.copy(os.path.join(src, "dialogue.json"), os.path.join(d, "build", "dialogue.json"))
    if os.path.isdir(os.path.join(src, "frozen")):
        shutil.copytree(os.path.join(src, "frozen"), os.path.join(d, "frozen"))
    run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(src, "voice.flac"), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
         os.path.join(d, "build", "audio", "voice.wav")])
    log = open(os.path.join(d, "prepare.log"), "w")
    run([sys.executable, "bl_common.py"], cwd=d, stdout=log, stderr=subprocess.STDOUT)
    plan_sha = sha256(os.path.join(d, "build", "plan.json"))
    if plan_sha != s["plan_sha256"]:
        raise SystemExit("%s: the plan built here differs from the approved one -- stop and report this" % s["id"])
    run([a.blender, "-b", "--factory-startup", "-P", "bl_scene.py"], cwd=d, stdout=log, stderr=subprocess.STDOUT)
    if not os.path.exists(os.path.join(d, "build", "blocklab.blend")):
        raise SystemExit("%s: Blender did not build the scene -- see %s/prepare.log" % (s["id"], d))
    perf = os.path.join(d, "build", "perf.json")
    perf_ok = os.path.exists(perf) and sha256(perf) == s.get("perf_sha256")
    write_json(mark, dict(inputs=s["inputs_sha"], plan_sha256=plan_sha, perf_identical=perf_ok, at=now()))
    return "built" + ("" if perf_ok else " (note: animation differs by float rounding from the approval build -- normal "
                                         "on another Blender build/CPU; the plan itself is identical)")


def cmd_prepare(a):
    ep, st = load_pkg(a.pkg)
    for s in ep["scenes"]:
        t = time.time()
        r = prepare_scene(a, s)
        print("%s %-26s %s%s" % (s["id"], s["slug"], r, "" if r == "ready" else " in %.0fs" % (time.time() - t)), flush=True)
    print("all %d scenes prepared (worker %s)" % (len(ep["scenes"]), a.worker))


# ------------------------------------------------------------------------------------------------------- timeline/manifest
def settings_for(a, st, ep):
    """Final settings, plus the sandbox-test overrides (fixed for the life of a WORK folder)."""
    s = dict(st)
    if a.scale:
        s["test_scale"] = a.scale
    if a.samples:
        s["samples"] = a.samples
    span = a.span or [0, ep["total_frames"]]
    s["span"] = [int(span[0]), int(span[1])]
    if a.segment_frames:
        s["segment_frames"] = a.segment_frames
    s["test"] = bool(a.scale or a.samples or a.span or a.segment_frames)
    return s


def pieces(ep, g0, g1):
    """The scene pieces covering global frames [g0, g1): (scene, local_from, local_to)."""
    out = []
    for s in ep["scenes"]:
        a, b = max(g0, s["start_frame"]), min(g1, s["start_frame"] + s["frames"])
        if a < b:
            out.append((s, a - s["start_frame"], b - s["start_frame"]))
    return out


def seg_inputs(ep, settings, g0, g1):
    h = hashlib.sha256(json.dumps([settings, [(s["id"], s["inputs_sha"], f0, f1, fx_for(ep, s))
                                              for s, f0, f1 in pieces(ep, g0, g1)]], sort_keys=True).encode())
    return h.hexdigest()[:16]


def fx_for(ep, s):
    fx = {"nf": s["frames"]}
    for t in ep.get("transitions", []):
        if t["after"] == s["id"]:
            fx["fade_out"] = t["fade_out_frames"]
        if t["before"] == s["id"]:
            fx["fade_in"] = t["fade_in_frames"]
            if t.get("card"):
                fx["card"] = t["card"]
    return fx


def load_plan(a, ep, st):
    """The segment plan (settings + segments), fixed for the life of a WORK folder. Imports a single-worker run."""
    for d in ("segments", "claims", "done", "failed"):
        os.makedirs(os.path.join(a.work, d), exist_ok=True)
    plan_p, man_p = os.path.join(a.work, "plan.json"), os.path.join(a.work, "manifest.json")
    plan, legacy = read_json(plan_p), read_json(man_p)
    legacy = legacy if legacy and "segments" in legacy and not legacy.get("view") else None
    tested = a.scale or a.samples or a.span or a.segment_frames
    if plan:
        settings = plan["settings"]
    elif legacy:
        settings = legacy["settings"]
    else:
        settings = settings_for(a, st, ep)
    if (plan or legacy) and tested and settings_for(a, st, ep) != settings:
        raise SystemExit("This WORK folder was started with other settings: use a new WORK folder for a different test.")
    g0, g1 = settings["span"]
    n = settings["segment_frames"]
    segs = [dict(index=k, name="seg_%02d" % k, start=s0, end=min(g1, s0 + n), frames=min(g1, s0 + n) - s0,
                 inputs=seg_inputs(ep, settings, s0, min(g1, s0 + n))) for k, s0 in enumerate(range(g0, g1, n))]
    new = dict(episode=ep["title"], package=ep["package_id"], fps=ep["fps"], settings=settings, segments=segs)
    if plan != new:
        write_json(plan_p, new)
    if legacy:                                             # a single-worker run: its finished segments count, as worker A's
        for x in legacy["segments"]:
            f = os.path.join(a.work, "segments", x.get("file") or "-")
            dp = os.path.join(a.work, "done", "%s__A.json" % x["name"])
            if x.get("state") == "COMPLETE" and os.path.exists(f) and not os.path.exists(dp):
                write_json(dp, dict(worker="A", session="single-worker run", file=x["file"], sha256=x["sha256"],
                                    bytes=x["bytes"], inputs=x["inputs"], at=now()))
        print("carried on from the earlier single-worker run (its finished segments count)")
    return new


def records(a, kind):
    """{segment name: [record, ...]} from claims/, done/ or failed/ (each record also gets its "path")."""
    out = {}
    d = os.path.join(a.work, kind)
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if fn.endswith(".json") and "__" in fn:
            r = read_json(os.path.join(d, fn))
            if r:
                r["path"] = os.path.join(d, fn)
                out.setdefault(fn.split("__")[0], []).append(r)
    return out


def mine(a, c):
    """A claim of this worker's from an earlier session counts as its own (to resume); a claim under the same letter that
    is beating right now from another session is someone else (two notebooks set to the same WORKER)."""
    return c["worker"] == a.worker and (c.get("session") == a.session or time.time() - c["heartbeat"] > 3 * BEAT)


def scan(a, plan):
    """Every segment's state, from the files of all workers."""
    claims, dones, fails = records(a, "claims"), records(a, "done"), records(a, "failed")
    t = time.time()
    view = []
    for x in plan["segments"]:
        v = dict(name=x["name"], start=x["start"], end=x["end"], frames=x["frames"], inputs=x["inputs"], workers=[])
        good = [d for d in dones.get(x["name"], []) if d["inputs"] == x["inputs"] and
                os.path.exists(os.path.join(a.work, "segments", d["file"])) and
                os.path.getsize(os.path.join(a.work, "segments", d["file"])) == d["bytes"]]
        cl = [c for c in claims.get(x["name"], []) if c["inputs"] == x["inputs"]]
        fresh = [c for c in cl if t - c["heartbeat"] < a.stale]
        failed = [f for f in fails.get(x["name"], []) if f["inputs"] == x["inputs"] and f["attempts"] >= plan["settings"]["max_attempts"]]
        if good:
            v.update(state="COMPLETE", done=good[0], workers=[good[0]["worker"]])
        elif fresh:
            v.update(state="ACTIVE", workers=sorted({c["worker"] for c in fresh}), claims=fresh,
                     detail=", ".join("%s %s" % (c["worker"], c.get("state", "")) for c in fresh))
        elif failed:
            v.update(state="FAILED", workers=[f["worker"] for f in failed], detail=failed[0].get("last_error", "")[:200])
        elif dones.get(x["name"]):
            v.update(state="NEEDS_REBUILD", detail="its file is missing or changed, or a scene in it changed")
        elif cl:
            v.update(state="STALLED", claims=cl, workers=sorted({c["worker"] for c in cl}),
                     detail="worker %s stopped answering -- another worker will take it over" % "/".join(sorted({c["worker"] for c in cl})))
        else:
            v.update(state="PENDING")
        v["claims"] = v.get("claims", cl)
        view.append(v)
    return view


def write_view(a, plan, view):
    """manifest.json: the combined status (any worker may rewrite it; it is rebuilt from the files every time)."""
    segs = [dict(name=v["name"], start=v["start"], end=v["end"], frames=v["frames"], state=v["state"], workers=v["workers"],
                 file=v["done"]["file"] if v.get("done") else None, detail=v.get("detail", "")) for v in view]
    try:
        write_json(os.path.join(a.work, "manifest.json"), dict(view=True, episode=plan["episode"], settings=plan["settings"],
                                                               segments=segs, updated=now(), by=a.worker))
    except OSError:
        pass
    write_status_txt(a, plan, view)


def write_status_txt(a, plan, view):
    """RENDER_STATUS.txt beside the work folder (in Colab: MyDrive/block_lab/final/): a small file to check from the
    Drive app -- which segments are COMPLETE, which worker is on what. Nothing is downloaded anywhere."""
    fps = plan.get("fps", 30)
    mmss = lambda f: "%d:%02d" % (f // fps // 60, f // fps % 60)
    n_done = sum(v["state"] == "COMPLETE" for v in view)
    words = dict(COMPLETE="COMPLETE", ACTIVE="ACTIVE", PENDING="waiting", STALLED="STALLED", FAILED="FAILED",
                 NEEDS_REBUILD="to redo")
    lines = ["%s -- render status" % plan["episode"],
             "updated %s by worker %s" % (now(), a.worker), "",
             "%d of %d segments COMPLETE (%d%%)%s" % (n_done, len(view), 100 * n_done // max(1, len(view)),
                                                     "  -- ALL DONE: run the masters + QA steps" if n_done == len(view) else ""), ""]
    for v in view:
        who = ""
        if v["state"] == "COMPLETE":
            who = "(worker %s)" % v["workers"][0]
        elif v["state"] == "ACTIVE":
            who = "worker %s %s" % ("/".join(v["workers"]), "rendering" if "RENDERING" in v.get("detail", "") else "finishing")
        elif v.get("detail"):
            who = v["detail"][:70]
        lines.append("%s  %s-%s  %-9s %s" % (v["name"], mmss(v["start"]), mmss(v["end"]), words[v["state"]], who))
    path = os.path.join(os.path.dirname(a.work.rstrip("/")), "RENDER_STATUS.txt")
    tmp = "%s.%s.partial" % (path, a.session)
    try:
        with open(tmp, "w") as f:
            f.write("\n".join(lines) + "\n")
        os.replace(tmp, path)
    except OSError:
        pass


def settings_file(a, settings):
    p = os.path.join(wdir(a), "render_settings.active.json")
    os.makedirs(wdir(a), exist_ok=True)
    write_json(p, settings)
    return p


# ----------------------------------------------------------------------------------------------------------------- claims
def claim_path(a, x):
    return os.path.join(a.work, "claims", "%s__%s.json" % (x["name"], a.worker))


def claim(a, plan, x):
    """Claim segment x; after SETTLE seconds, back off if another worker claimed it earlier. True if it is ours."""
    old = read_json(claim_path(a, x))
    t = time.time()
    c = dict(worker=a.worker, session=a.session, inputs=x["inputs"], state="CLAIMED", heartbeat=t,
             claimed_at=old["claimed_at"] if old and old.get("inputs") == x["inputs"] else t)
    write_json(claim_path(a, x), c)
    if a.settle:
        time.sleep(a.settle)
    v = next(v for v in scan(a, plan) if v["name"] == x["name"])
    if v["state"] == "COMPLETE":
        release(a, x)
        return False
    rivals = [r for r in v.get("claims", []) if not mine(a, r) and time.time() - r["heartbeat"] < a.stale]
    if any((r["claimed_at"], r["worker"]) < (c["claimed_at"], a.worker) for r in rivals):
        release(a, x)
        print("  %s was claimed first by worker %s -- leaving it to them" % (x["name"], "/".join(r["worker"] for r in rivals)))
        return False
    return True


def release(a, x):
    try:
        os.remove(claim_path(a, x))
    except OSError:
        pass


def make_beat(a, plan, x):
    """A heartbeat for segment x: refreshes our claim at most once a minute; raises Superseded if another worker has
    finished the segment meanwhile."""
    last = [0.0]

    def beat(state, force=False):
        t = time.time()
        if not force and t - last[0] < BEAT:
            return
        last[0] = t
        c = read_json(claim_path(a, x)) or dict(worker=a.worker, inputs=x["inputs"], claimed_at=t)
        c.update(session=a.session, heartbeat=t, state=state)
        try:
            write_json(claim_path(a, x), c)
        except OSError:
            pass
        v = next(v for v in scan(a, plan) if v["name"] == x["name"])
        if v["state"] == "COMPLETE" and v["done"]["worker"] != a.worker:
            raise Superseded("%s was finished by worker %s" % (x["name"], v["done"]["worker"]))
    return beat


# ----------------------------------------------------------------------------------------------------------------- render
def render_piece(a, settings, s, f0, f1, deadline, beat):
    out = frames_dir(a, s)
    stamp = os.path.join(out, "INPUTS")                  # frames rendered from other inputs/settings are never reused
    key = s["inputs_sha"] + " " + hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:16]
    if os.path.isdir(out) and (not os.path.exists(stamp) or open(stamp).read() != key):
        shutil.rmtree(out)
    if not os.path.isdir(out):
        os.makedirs(out)
        open(stamp, "w").write(key)
    missing = [f for f in range(f0, f1) if not os.path.exists(os.path.join(out, "%04d.png" % f))]
    if not missing:
        return True
    print("  rendering %s frames %d-%d (%d to do)" % (s["id"], f0, f1 - 1, len(missing)), flush=True)
    d = scene_dir(a, s)
    cmd = [a.blender, "-b", "--factory-startup", "-P", os.path.join(TOOLS, "gbl_blender_render.py"), "--",
           os.path.join(d, "build", "blocklab.blend"), out, str(min(missing)), str(max(missing) + 1),
           settings_file(a, settings), "%.0f" % deadline]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=d)
    n, t0 = 0, time.time()
    try:
        for line in p.stdout:
            if line.startswith("FRAME"):
                n += 1
                beat("RENDERING")
                if n % 25 == 0:
                    rate = (time.time() - t0) / n
                    print("    %s: %d/%d frames, %.1f s/frame, ~%.0f min left in this piece" % (
                        s["id"], n, len(missing), rate, rate * (len(missing) - n) / 60), flush=True)
            elif line.startswith(("DEVICE", "RETRY", "DEADLINE", "RENDER DONE")) or ("Error" in line and "WARNING" not in line):
                print("    " + line.rstrip(), flush=True)
    except Superseded:
        p.kill(); p.wait()
        raise
    p.wait()
    if p.returncode != 0:
        raise RuntimeError("Blender stopped with code %d while rendering %s" % (p.returncode, s["id"]))
    return all(os.path.exists(os.path.join(out, "%04d.png" % f)) for f in range(f0, f1))


def encode_segment(a, ep, settings, x, tmp_mp4, beat):
    """Compose every frame of the segment (each scene with its own overlay) and encode one visually lossless file."""
    W, H, fps = settings["width"], settings["height"], ep["fps"]
    v = settings["segment_video"]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                           "-r", str(fps), "-i", "-",
                           "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=" + v["pix_fmt"],
                           "-c:v", "libx264", "-preset", v["preset"], "-crf", str(v["crf"]), "-g", str(fps), "-bf", "2",
                           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                           "-an", "-movflags", "+faststart", tmp_mp4], stdin=subprocess.PIPE)
    written = 0
    for s, f0, f1 in pieces(ep, x["start"], x["end"]):
        fx = fx_for(ep, s)
        fx["fonts"] = os.path.join(a.pkg, "fonts")
        errf = tempfile.TemporaryFile()
        p = subprocess.Popen([sys.executable, os.path.join(TOOLS, "gbl_compose.py"), scene_dir(a, s), frames_dir(a, s),
                              str(f0), str(f1), json.dumps(fx)], stdout=subprocess.PIPE, stderr=errf)
        try:
            while True:
                b = p.stdout.read(W * H * 3 * 8)
                if not b:
                    break
                ff.stdin.write(b)
                written += len(b)
                beat("VALIDATING")
        except (BrokenPipeError, Superseded) as e:
            p.kill(); p.wait()
            ff.kill(); ff.wait()
            if isinstance(e, Superseded):
                raise
            raise RuntimeError("the encoder stopped early")
        p.wait()
        errf.seek(0)
        err = errf.read().decode(errors="replace")
        if p.returncode != 0:
            ff.stdin.close(); ff.wait()
            bad = [ln for ln in err.splitlines() if ln.startswith("BADFRAME")]
            if bad:                                          # a damaged frame: delete it so the retry renders it again
                f = int(bad[0].split()[1])
                path = os.path.join(frames_dir(a, s), "%04d.png" % f)
                if os.path.exists(path):
                    os.remove(path)
                raise RuntimeError("%s frame %d was damaged -- deleted, it will be rendered again" % (s["id"], f))
            raise RuntimeError("composing %s failed:\n%s" % (s["id"], err[-2000:]))
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("the encoder failed")
    if written != x["frames"] * W * H * 3:
        raise RuntimeError("composed %d frames, expected %d" % (written // (W * H * 3), x["frames"]))


def validate_segment(ep, settings, x, path):
    s = probe(path)
    want = dict(width=settings["width"], height=settings["height"], pix_fmt=settings["segment_video"]["pix_fmt"])
    for k, v in want.items():
        if s.get(k) != v:
            raise RuntimeError("%s is %s=%s, expected %s" % (x["name"], k, s.get(k), v))
    if int(s.get("nb_read_packets", -1)) != x["frames"]:
        raise RuntimeError("%s has %s frames, expected %d" % (x["name"], s.get("nb_read_packets"), x["frames"]))
    if s.get("color_space") != "bt709" or s.get("color_primaries") != "bt709" or s.get("color_transfer") != "bt709":
        raise RuntimeError("%s is not tagged Rec.709" % x["name"])
    err = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"], capture_output=True, text=True).stderr
    if err.strip():
        raise RuntimeError("%s does not decode cleanly: %s" % (x["name"], err[:300]))


def do_segment(a, ep, plan, x, deadline):
    """Render, compose, encode, validate and stage one segment. Returns "complete" or "stopped" (time budget)."""
    settings = plan["settings"]
    beat = make_beat(a, plan, x)
    beat("RENDERING", force=True)
    for s, f0, f1 in pieces(ep, x["start"], x["end"]):
        r = prepare_scene(a, s)                              # (quick when this worker has prepared it already)
        if r != "ready":
            print("  prepared %s: %s" % (s["id"], r), flush=True)
        beat("RENDERING", force=True)
        if not render_piece(a, settings, s, f0, f1, deadline, beat):
            if deadline and time.time() >= deadline:
                return "stopped"
            raise RuntimeError("Blender finished but %s frames are missing" % s["id"])
    beat("VALIDATING", force=True)
    print("  %s: frames rendered; composing + encoding" % x["name"], flush=True)
    tmpd = tempfile.mkdtemp(prefix="gbl_seg_")
    tmp_mp4 = os.path.join(tmpd, x["name"] + ".mp4")
    t0 = time.time()
    name = "%s__%s.mp4" % (x["name"], a.worker)
    dst = os.path.join(a.work, "segments", name)
    try:
        encode_segment(a, ep, settings, x, tmp_mp4, beat)
        validate_segment(ep, settings, x, tmp_mp4)
        h = sha256(tmp_mp4)
        part = "%s.%s.partial" % (dst, a.session)
        shutil.copyfile(tmp_mp4, part)                         # staged: only a verified copy gets the real name
        if sha256(part) != h:
            raise RuntimeError("the copy into WORK does not match -- storage problem")
        os.replace(part, dst)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    write_json(os.path.join(a.work, "done", "%s__%s.json" % (x["name"], a.worker)),
               dict(worker=a.worker, session=a.session, file=name, sha256=h, bytes=os.path.getsize(dst), inputs=x["inputs"], at=now()))
    release(a, x)
    try:
        os.remove(os.path.join(a.work, "failed", "%s__%s.json" % (x["name"], a.worker)))
    except OSError:
        pass
    print("  %s -> COMPLETE (worker %s, %.1f MB, composed+encoded in %.0fs)" % (x["name"], a.worker, os.path.getsize(dst) / 1e6,
                                                                             time.time() - t0), flush=True)
    if not a.keep_frames:                                    # free the space: this segment's frames are in the file now
        for s, f0, f1 in pieces(ep, x["start"], x["end"]):
            for f in range(f0, f1):
                p = os.path.join(frames_dir(a, s), "%04d.png" % f)
                if os.path.exists(p):
                    os.remove(p)
    return "complete"


def pick(a, view):
    """The segments this worker should try next, in order: its own unfinished ones (resume), then PENDING /
    NEEDS_REBUILD, then STALLED ones whose worker died (and FAILED ones with --retry-failed)."""
    own = [v for v in view if v["state"] in ("ACTIVE", "STALLED") and any(mine(a, c) for c in v.get("claims", []))]
    others_active = {v["name"] for v in view if v["state"] == "ACTIVE" and v not in own}
    fresh = [v for v in view if v["state"] in ("PENDING", "NEEDS_REBUILD")]
    stalled = [v for v in view if v["state"] == "STALLED" and v not in own]
    failed = [v for v in view if v["state"] == "FAILED"] if a.retry_failed else []
    return [v for v in own + fresh + stalled + failed if v["name"] not in others_active]


def cmd_render(a):
    ep, st = load_pkg(a.pkg)
    plan = load_plan(a, ep, st)
    segs = {x["name"]: x for x in plan["segments"]}
    deadline = time.time() + a.hours * 3600 if a.hours else 0.0
    print("worker %s (session %s) joining the render" % (a.worker, a.session), flush=True)
    did = 0
    while True:
        if a.segments and did >= a.segments:
            break
        if deadline and time.time() > deadline - 60:
            print("time budget used up -- stopping here; run again to continue")
            break
        view = scan(a, plan)
        write_view(a, plan, view)
        todo = pick(a, view)
        if not todo:
            busy = [v for v in view if v["state"] == "ACTIVE"]
            if busy:
                print("nothing left for worker %s: %s still being rendered by %s" % (
                    a.worker, ", ".join(v["name"] for v in busy), ", ".join(sorted({w for v in busy for w in v["workers"]}))))
            break
        x = None
        for v in todo:
            if claim(a, plan, segs[v["name"]]):
                x = segs[v["name"]]
                break
        if x is None:
            continue                                           # every candidate went to another worker: look again
        print("%s: global frames %d-%d (%.1f-%.1f s), %d frames -- worker %s" % (
            x["name"], x["start"], x["end"] - 1, x["start"] / ep["fps"], x["end"] / ep["fps"], x["frames"], a.worker), flush=True)
        fpath = os.path.join(a.work, "failed", "%s__%s.json" % (x["name"], a.worker))
        fr = read_json(fpath)
        attempts = fr["attempts"] if fr and fr.get("inputs") == x["inputs"] and not a.retry_failed else 0
        result = None
        while result is None:                                  # a failed attempt is retried at once, up to max_attempts
            try:
                result = do_segment(a, ep, plan, x, deadline)
            except Superseded as e:
                print("  " + str(e) + " -- moving on", flush=True)
                release(a, x)
                result = "superseded"
            except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
                attempts += 1
                write_json(fpath, dict(worker=a.worker, session=a.session, attempts=attempts, last_error=str(e)[:2000],
                                       inputs=x["inputs"], at=now()))
                print("  %s attempt %d failed: %s" % (x["name"], attempts, str(e)[:300]), flush=True)
                if attempts >= plan["settings"]["max_attempts"]:
                    release(a, x)
                    result = "failed"
                elif deadline and time.time() > deadline - 60:
                    result = "failed"
        if result == "stopped":
            print("  stopped inside %s (time budget); its frames are saved -- run again to continue" % x["name"])
            break
        did += result == "complete"
    cmd_status(a)


def cmd_status(a):
    ep, st = load_pkg(a.pkg)
    plan = read_json(os.path.join(a.work, "plan.json"))
    if not plan:
        legacy = read_json(os.path.join(a.work, "manifest.json"))
        if not legacy:
            print("nothing rendered yet in", a.work)
            return
        plan = load_plan(a, ep, st)
    view = scan(a, plan)
    write_view(a, plan, view)
    c = {k: 0 for k in STATES}
    for v in view:
        c[v["state"]] += 1
    done = sum(v["frames"] for v in view if v["state"] == "COMPLETE")
    tot = sum(v["frames"] for v in view)
    print("\n%s: %d of %d segments COMPLETE (%d of %d frames, %.0f%%)%s" % (
        plan["episode"], c["COMPLETE"], len(view), done, tot, 100.0 * done / max(1, tot),
        "  [SANDBOX TEST SETTINGS]" if plan["settings"].get("test") else ""))
    for v in view:
        who = ("by " + "/".join(v["workers"])) if v["workers"] else ""
        print("  %s %6d-%6d  %-13s %-8s %s" % (v["name"], v["start"], v["end"] - 1, v["state"], who, v.get("detail", "")[:80]))
    if c["COMPLETE"] == len(view):
        print("ALL SEGMENTS COMPLETE -- next: assemble")


# -------------------------------------------------------------------------------------------------------------- benchmark
def cmd_benchmark(a):
    """Render a few of the heaviest frames at the final settings and estimate the whole render."""
    ep, st = load_pkg(a.pkg)
    settings = dict(st)
    tmp = tempfile.mkdtemp(prefix="gbl_bench_")
    times = []
    for sid, frac in ep["benchmark_frames"]:
        s = next(x for x in ep["scenes"] if x["id"] == sid)
        prepare_scene(a, s)
        f = int(s["frames"] * frac)
        out = os.path.join(tmp, sid)
        p = subprocess.run([a.blender, "-b", "--factory-startup", "-P", os.path.join(TOOLS, "gbl_blender_render.py"), "--",
                            os.path.join(scene_dir(a, s), "build", "blocklab.blend"), out, str(f), str(f + 2),
                            settings_file(a, settings)], capture_output=True, text=True, cwd=scene_dir(a, s))
        fr = [float(ln.split()[2][:-1]) for ln in p.stdout.splitlines() if ln.startswith("FRAME")]
        dev = [ln for ln in p.stdout.splitlines() if ln.startswith("DEVICE")]
        if len(fr) < 2:
            print(p.stdout[-1500:]); raise SystemExit("benchmark render failed")
        times.append(fr[1])                                # the 2nd frame: the scene is loaded and warm, as in a real run
        print("%s frame %d: first %.1fs (loads the scene), then %.1fs per frame | %s" % (sid, f, fr[0], fr[1], dev[0] if dev else ""))
    shutil.rmtree(tmp, ignore_errors=True)
    per = sum(times) / len(times)
    comp = 0.25                                           # compose + encode, per frame (measured on Colab's 2 CPUs)
    hrs = ep["total_frames"] * (per + comp) / 3600
    print("\nestimate: %.1f s/frame render + ~%.2f s/frame compose/encode -> about %.1f hours for %d frames"
          " (heaviest-frame sample; most scenes are lighter)" % (per, comp, hrs, ep["total_frames"]))


# --------------------------------------------------------------------------------------------------------------- assemble
def cmd_assemble(a):
    ep, st = load_pkg(a.pkg)
    plan = read_json(os.path.join(a.work, "plan.json"))
    view = scan(a, plan)
    settings = plan["settings"]
    if any(v["state"] != "COMPLETE" for v in view):
        raise SystemExit("not every segment is COMPLETE yet -- run render again first")
    os.makedirs(os.path.join(a.out, "AUDIO"), exist_ok=True)
    lock = os.path.join(a.out, "ASSEMBLY.lock")              # with several workers, only one assembles
    lk = read_json(lock)
    if lk and lk.get("session") != a.session and time.time() - lk.get("t", 0) < 3 * 3600:
        print("worker %s is already assembling the masters (since %s) -- nothing to do here" % (lk.get("worker"), lk.get("at")))
        return
    write_json(lock, dict(worker=a.worker, session=a.session, t=time.time(), at=now()))
    for v in view:
        f = os.path.join(a.work, "segments", v["done"]["file"])
        if sha256(f) != v["done"]["sha256"]:
            os.remove(os.path.join(a.work, "done", "%s__%s.json" % (v["name"], v["done"]["worker"])))
            os.remove(lock)
            raise SystemExit("%s is damaged (checksum) -- it is marked for re-rendering: run render again" % v["name"])
    tmpd = tempfile.mkdtemp(prefix="gbl_asm_")
    g0, g1 = settings["span"]
    tag = ep["file_tag"] + ("_SANDBOX_TEST" if settings.get("test") else "")

    # audio deliverables: lossless FLAC in the package -> 48 kHz / 24-bit WAV (bit-exact; checked against the package)
    for k, rel in ep["audio"]["stems"].items():
        dst = os.path.join(a.out, "AUDIO", "%s_%s.wav" % (tag, k))
        trim = ["-af", "atrim=start_sample=%d:end_sample=%d" % (g0 * 1600, g1 * 1600)] if settings.get("test") else []
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(a.pkg, rel)] + trim + ["-c:a", "pcm_s24le", "-ar", "48000", dst + ".partial.wav"])
        os.replace(dst + ".partial.wav", dst)
    open(os.path.join(a.out, "AUDIO", "%s_music_NONE.txt" % tag), "w").write(
        "No music stem: music is parked for Episode 1 (decision 2026-10-22). The final mix is dialogue + sound effects + ambience.\n")
    mix = os.path.join(a.out, "AUDIO", "%s_final_mix.wav" % tag)

    # video: the segments joined without re-encoding, then the two masters
    lst = os.path.join(tmpd, "segments.txt")
    with open(lst, "w") as f:
        for v in view:
            f.write("file '%s'\n" % os.path.join(a.work, "segments", v["done"]["file"]).replace("'", "'\\''"))
    arch = os.path.join(a.out, "%s_ARCHIVAL_MASTER_1080p30_444_PCM24.mkv" % tag)
    tmp_arch = os.path.join(tmpd, "archival.mkv")
    print("archival master (stream copy + 24-bit PCM)...", flush=True)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", mix, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "pcm_s24le", "-metadata", "title=" + ep["title"], "-metadata:s:a:0", "language=eng",
         tmp_arch])
    shutil.copyfile(tmp_arch, arch + "." + a.session + ".partial")
    os.replace(arch + "." + a.session + ".partial", arch)

    y = st["youtube"]
    enc = ["-c:v", "libx264", "-preset", y["x264_preset"], "-crf", str(y["x264_crf"]), "-maxrate", y["maxrate"], "-bufsize", y["bufsize"],
           "-profile:v", "high", "-level", "5.1"]
    if not settings.get("test") and subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=3840x2160:d=0.1", "-c:v", "h264_nvenc",
                                                    "-f", "null", "-"], capture_output=True).returncode == 0:
        enc = ["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", str(y["nvenc_cq"]), "-b:v", y["bitrate"],
               "-maxrate", y["maxrate"], "-bufsize", y["bufsize"], "-profile:v", "high", "-spatial-aq", "1", "-temporal-aq", "1"]
    W, H = (3840, 2160) if not settings.get("test") else (st["width"], st["height"])
    yt = os.path.join(a.out, "%s_YOUTUBE_4K_UPSCALED_from1080p.mp4" % tag if not settings.get("test") else "%s_YOUTUBE.mp4" % tag)
    tmp_yt = os.path.join(tmpd, "youtube.mp4")
    print("YouTube master (%dx%d, %s)..." % (W, H, enc[1]), flush=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp_arch, "-map", "0:v", "-map", "0:a",
         "-vf", "scale=%d:%d:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:out_color_matrix=bt709:"
                "in_range=tv:out_range=tv,format=yuv420p" % (W, H)] + enc +
        ["-g", "15", "-bf", "2", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "384k", "-ar", "48000", "-ac", "2", "-metadata", "title=" + ep["title"],
         "-movflags", "+faststart", tmp_yt])
    shutil.copyfile(tmp_yt, yt + "." + a.session + ".partial")
    os.replace(yt + "." + a.session + ".partial", yt)
    shutil.rmtree(tmpd, ignore_errors=True)
    write_json(os.path.join(a.out, "ASSEMBLY.json"), dict(at=now(), archival=os.path.basename(arch), youtube=os.path.basename(yt),
                                                         encoder=enc[1], worker=a.worker, session=a.session,
                                                         segments=[v["done"]["file"] for v in view]))
    os.remove(lock)
    print("wrote\n  %s\n  %s\n  AUDIO/ (final mix + stems)" % (arch, yt))


# --------------------------------------------------------------------------------------------------------------------- qa
def loudness(path):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    tail = err[err.rfind("Summary:"):]
    val = lambda key: float(tail.split(key)[1].split()[0])
    return dict(lufs=val("I:"), true_peak_dbtp=val("Peak:"), lra=val("LRA:"))


def black_spans(path):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-map", "0:v:0", "-vf", "blackdetect=d=0.1:pix_th=0.06:pic_th=0.98",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    out = []
    for ln in err.splitlines():
        if "black_start:" in ln:
            p = dict(kv.split(":") for kv in ln.split("]")[-1].split() if ":" in kv)
            out.append((float(p["black_start"]), float(p["black_end"])))
    return out


def moov_first(path):
    with open(path, "rb") as f:
        while True:
            h = f.read(8)
            if len(h) < 8:
                return False
            size, kind = int.from_bytes(h[:4], "big"), h[4:8]
            if kind == b"moov":
                return True
            if kind == b"mdat":
                return False
            if size == 1:
                size = int.from_bytes(f.read(8), "big") - 8
            f.seek(size - 8, 1)


def cmd_qa(a):
    ep, st = load_pkg(a.pkg)
    plan = read_json(os.path.join(a.work, "plan.json"))
    m = dict(segments=scan(a, plan))
    settings = plan["settings"]
    asm = json.load(open(os.path.join(a.out, "ASSEMBLY.json")))
    g0, g1 = settings["span"]
    nf, fps = g1 - g0, ep["fps"]
    checks = []

    test = bool(settings.get("test"))

    def check(name, ok, detail):
        r = "SKIP (test span)" if ok is None else ("PASS" if ok else "FAIL")
        checks.append(dict(check=name, result=r, detail=detail))
        print("[%s] %s -- %s" % (r, name, detail), flush=True)

    arch, yt = os.path.join(a.out, asm["archival"]), os.path.join(a.out, asm["youtube"])
    check("every segment COMPLETE", all(x["state"] == "COMPLETE" for x in m["segments"]), "%d segments" % len(m["segments"]))
    check("segments add up to the timeline", sum(x["frames"] for x in m["segments"]) == nf, "%d frames" % nf)
    for path, label, W, H, pf in ((arch, "archival", st["width"], st["height"], settings["segment_video"]["pix_fmt"]),
                                  (yt, "YouTube", 3840 if not settings.get("test") else st["width"],
                                   2160 if not settings.get("test") else st["height"], "yuv420p")):
        v, au = probe(path), probe(path, "a:0")
        check("%s: frame count" % label, int(v.get("nb_read_packets", -1)) == nf, "%s of %d" % (v.get("nb_read_packets"), nf))
        check("%s: picture" % label, (v.get("width"), v.get("height"), v.get("pix_fmt"), v.get("r_frame_rate")) == (W, H, pf, "%d/1" % fps),
              "%sx%s %s %s fps" % (v.get("width"), v.get("height"), v.get("pix_fmt"), v.get("r_frame_rate")))
        check("%s: Rec.709 tagged" % label, (v.get("color_space"), v.get("color_primaries"), v.get("color_transfer"), v.get("color_range")) ==
              ("bt709", "bt709", "bt709", "tv"), "%s/%s/%s %s" % (v.get("color_space"), v.get("color_primaries"),
                                                                 v.get("color_transfer"), v.get("color_range")))
        check("%s: audio 48 kHz stereo" % label, (int(au.get("sample_rate", 0)), int(au.get("channels", 0))) == (48000, 2),
              "%s %s Hz %s ch" % (au.get("codec_name"), au.get("sample_rate"), au.get("channels")))
        dur = duration(path)
        check("%s: length matches the picture (sync)" % label, abs(dur - nf / fps) < 1.5 / fps, "%.3f s (picture %.3f s)" % (dur, nf / fps))
        err = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"], capture_output=True, text=True).stderr
        check("%s: decodes cleanly end to end" % label, not err.strip(), err.strip()[:200] or "no errors")
    check("archival: 24-bit PCM audio", probe(arch, "a:0").get("codec_name") == "pcm_s24le", probe(arch, "a:0").get("codec_name"))
    check("YouTube: moov atom first (fast start)", moov_first(yt), "streams before fully downloaded")
    mix = os.path.join(a.out, "AUDIO", "%s_final_mix.wav" % (ep["file_tag"] + ("_SANDBOX_TEST" if settings.get("test") else "")))
    L = loudness(mix)
    check("final mix loudness", None if test else abs(L["lufs"] + 14) <= 0.5, "%.1f LUFS (target -14)" % L["lufs"])
    check("final mix true peak", None if test else L["true_peak_dbtp"] <= -1.0, "%.1f dBTP (limit -1.0)" % L["true_peak_dbtp"])
    Ly = loudness(yt)
    check("YouTube file loudness after AAC", None if test else abs(Ly["lufs"] + 14) <= 0.5,
          "%.1f LUFS, %.1f dBTP" % (Ly["lufs"], Ly["true_peak_dbtp"]))
    allowed = []                                            # the planned dips to black at the time-skip joins
    for t in ep.get("transitions", []):
        s = next(x for x in ep["scenes"] if x["id"] == t["before"])
        j = (s["start_frame"] - g0) / fps
        allowed.append((j - t["fade_out_frames"] / fps - 0.2, j + t["fade_in_frames"] / fps + 0.2))
    blacks = black_spans(arch)
    stray = [b for b in blacks if not any(lo <= b[0] and b[1] <= hi for lo, hi in allowed)]
    check("no unplanned black frames", not stray, "black at %s; planned dips at %s" % (
        [(round(x, 2), round(y, 2)) for x, y in blacks], [(round(x, 2), round(y, 2)) for x, y in allowed]))
    rep = dict(episode=ep["title"], at=now(), sandbox_test=bool(settings.get("test")), span=[g0, g1], archival=asm["archival"],
               youtube=asm["youtube"], youtube_encoder=asm["encoder"], mix_loudness=L, youtube_loudness=Ly, checks=checks,
               result="FAIL" if any(c["result"] == "FAIL" for c in checks) else "PASS")
    os.makedirs(os.path.join(a.out, "QA"), exist_ok=True)
    write_json(os.path.join(a.out, "QA", "final_qa_report.json"), rep)
    with open(os.path.join(a.out, "QA", "final_qa_report.md"), "w") as f:
        f.write("# %s -- final QA (%s)\n\nResult: **%s**%s\n\n| check | result | detail |\n|---|---|---|\n" % (
            ep["title"], rep["at"], rep["result"], " (sandbox test settings)" if rep["sandbox_test"] else ""))
        for c in checks:
            f.write("| %s | %s | %s |\n" % (c["check"], c["result"], c["detail"].replace("|", "/")))
    print("\nQA %s -- report in %s" % (rep["result"], os.path.join(a.out, "QA")))
    if rep["result"] != "PASS":
        sys.exit(1)


# ------------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["validate", "prepare", "benchmark", "render", "status", "assemble", "qa"])
    ap.add_argument("--pkg", required=True)
    ap.add_argument("--work")
    ap.add_argument("--out")
    ap.add_argument("--blender", default="blender")
    ap.add_argument("--hours", type=float, default=0.0, help="stop cleanly after this many hours (Colab session limits)")
    ap.add_argument("--segments", type=int, default=0, help="finish at most this many segments in this run")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--keep-frames", action="store_true", help="keep each segment's frames after it is COMPLETE")
    ap.add_argument("--worker", default="A", help="this worker's letter when several Colab sessions render together (A, B, C...)")
    ap.add_argument("--session", default=os.urandom(4).hex(), help="this notebook session's id (the notebook sets it)")
    ap.add_argument("--stale", type=float, default=900.0, help="seconds without a heartbeat before a claim is taken over")
    ap.add_argument("--settle", type=float, default=45.0, help="seconds to wait after claiming before checking for rivals")
    ap.add_argument("--scale", type=int, default=0, help=argparse.SUPPRESS)
    ap.add_argument("--samples", type=int, default=0, help=argparse.SUPPRESS)
    ap.add_argument("--span", type=int, nargs=2, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--segment-frames", type=int, default=0, help=argparse.SUPPRESS)
    a = ap.parse_args()
    a.pkg = os.path.abspath(a.pkg)
    a.worker = "".join(ch for ch in a.worker.upper() if ch.isalnum())[:8] or "A"
    for k in ("work", "out"):
        if getattr(a, k):
            setattr(a, k, os.path.abspath(getattr(a, k)))
    {"validate": cmd_validate, "prepare": cmd_prepare, "benchmark": cmd_benchmark, "render": cmd_render,
     "status": cmd_status, "assemble": cmd_assemble, "qa": cmd_qa}[a.command](a)


if __name__ == "__main__":
    main()
