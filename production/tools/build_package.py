"""Build the portable production package for one episode (run here, in the build session -- not in Colab).

    python3 build_package.py --repo REPO --queue QUEUE_DIR --audio AUDIO_MASTER_DIR --config production/ep01/package.json --out DIR [--zip]

Everything the final render needs, nothing it doesn't: each scene's approved story, dialogue and frozen voice; the exact
engine files each scene was approved on (taken from the git commit its queue manifest pins, and checked against the
manifest's engine hash); the episode audio master (lossless FLAC, 48 kHz / 24-bit); fonts; render settings; the tools;
the Colab notebook; the QA reports; and a checksum for every file.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gbl_final import engine_hash, sha256  # noqa: E402


def git_show(repo, commit, path):
    return subprocess.run(["git", "-C", repo, "show", "%s:%s" % (commit, path)], check=True, capture_output=True).stdout


def plan_of(engine_dir, files, scene_src, slug):
    """Build the scene's plan with its own engine (pure Python, fast) and return its sha256 -- Colab must get the same."""
    d = tempfile.mkdtemp(prefix="gbl_plan_")
    try:
        for n in files:
            shutil.copy(os.path.join(engine_dir, n), d)
        os.makedirs(os.path.join(d, "build", "audio")); os.makedirs(os.path.join(d, "stories"))
        shutil.copy(os.path.join(scene_src, "story.json"), os.path.join(d, "build", "story.json"))
        shutil.copy(os.path.join(scene_src, "story.json"), os.path.join(d, "stories", slug + ".json"))
        shutil.copy(os.path.join(scene_src, "dialogue.json"), os.path.join(d, "build", "dialogue.json"))
        if os.path.isdir(os.path.join(scene_src, "frozen")):
            shutil.copytree(os.path.join(scene_src, "frozen"), os.path.join(d, "frozen"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(scene_src, "voice.flac"), "-ar", "48000", "-ac", "1",
                        "-c:a", "pcm_s16le", os.path.join(d, "build", "audio", "voice.wav")], check=True)
        subprocess.run([sys.executable, "bl_common.py"], cwd=d, check=True, capture_output=True)
        return sha256(os.path.join(d, "build", "plan.json")), json.load(open(os.path.join(d, "build", "plan.json")))["nf"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--queue", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--perf", default="", help="optional: folder of approval builds <queue id>/build/perf.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    root = os.path.join(a.out, cfg["package_name"])
    shutil.rmtree(root, ignore_errors=True)
    for d in ("engines", "scenes", "audio_master", "fonts", "config", "tools", "notebook", "QA"):
        os.makedirs(os.path.join(root, d))

    scenes, start = [], 0
    for qid in cfg["scenes"]:
        qdir = next(os.path.join(a.queue, n) for n in sorted(os.listdir(a.queue)) if n.startswith(qid + "_"))
        man = json.load(open(os.path.join(qdir, "manifest.json")))
        name = os.path.basename(qdir)
        sdir = os.path.join(root, "scenes", name)
        os.makedirs(sdir)
        for n in ("story.json", "dialogue.json", "voice.flac", "manifest.json"):
            shutil.copy(os.path.join(qdir, n), sdir)
        if os.path.isdir(os.path.join(qdir, "frozen")):
            shutil.copytree(os.path.join(qdir, "frozen"), os.path.join(sdir, "frozen"))
        edir = os.path.join(root, "engines", man["engine_sha"])
        if not os.path.isdir(edir):
            os.makedirs(edir)
            for n in man["engine_files"]:
                open(os.path.join(edir, n), "wb").write(git_show(a.repo, man["engine_commit"], "engine/" + n))
        got = engine_hash(edir, man["engine_files"])
        if got != man["engine_sha"]:
            raise SystemExit("%s: engine at %s hashes to %s, manifest says %s" % (qid, man["engine_commit"][:8], got, man["engine_sha"]))
        plan_sha, nf = plan_of(edir, man["engine_files"], sdir, man["slug"])
        perf = os.path.join(a.perf, name, "build", "perf.json") if a.perf else ""
        h = hashlib.sha256()
        for n in ("story.json", "dialogue.json", "voice.flac"):
            h.update(open(os.path.join(sdir, n), "rb").read())
        h.update(man["engine_sha"].encode())
        scenes.append(dict(id=qid, slug=man["slug"], title=man.get("title", ""), dir="scenes/" + name, dir_name=name,
                           engine="engines/" + man["engine_sha"], engine_commit=man["engine_commit"], engine_sha=man["engine_sha"],
                           engine_files=man["engine_files"], frames=nf, start_frame=start, plan_sha256=plan_sha,
                           perf_sha256=sha256(perf) if perf and os.path.exists(perf) else None,
                           inputs_sha=h.hexdigest()[:16], accepted_fails=man.get("accepted_fails", [])))
        print("%s %-28s engine %s  %5d frames  from %6d" % (qid, man["slug"], man["engine_sha"], nf, start), flush=True)
        start += nf

    stems = {}
    for k in ("final_mix", "dialogue", "sfx", "ambience"):
        dst = os.path.join(root, "audio_master", k + ".flac")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(a.audio, k + ".wav"), "-c:a", "flac", "-compression_level", "8",
                        "-sample_fmt", "s32", "-bits_per_raw_sample", "24", dst], check=True)
        pcm = lambda p: subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s32le", "-acodec", "pcm_s32le", "-"],
                                       check=True, capture_output=True).stdout
        if hashlib.md5(pcm(dst)).digest() != hashlib.md5(pcm(os.path.join(a.audio, k + ".wav"))).digest():
            raise SystemExit("FLAC of %s is not bit-exact" % k)
        stems[k] = "audio_master/%s.flac" % k
    shutil.copy(os.path.join(a.audio, "audio_qa_report.json"), os.path.join(root, "audio_master"))

    ep = dict(cfg["episode"])
    ep.update(package_id=cfg["package_name"], total_frames=start, scenes=scenes,
              audio=dict(final_mix=stems["final_mix"], stems=stems, report="audio_master/audio_qa_report.json"))
    json.dump(ep, open(os.path.join(root, "episode.json"), "w"), indent=1)
    json.dump(cfg["render_settings"], open(os.path.join(root, "config", "render_settings.json"), "w"), indent=1)
    json.dump(cfg["dependencies"], open(os.path.join(root, "config", "dependencies.json"), "w"), indent=1)
    for src, dst in cfg["copy"]:
        s = os.path.join(a.repo, src) if not os.path.isabs(src) else src
        d = os.path.join(root, dst)
        (shutil.copytree if os.path.isdir(s) else shutil.copy)(s, d)
    for f in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"):
        shutil.copy(os.path.join(cfg["fonts_from"], f), os.path.join(root, "fonts"))

    with open(os.path.join(root, "CHECKSUMS.sha256"), "w") as out:
        for dp, dn, fn in sorted(os.walk(root)):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, root)
                if rel != "CHECKSUMS.sha256" and "__pycache__" not in rel:
                    out.write("%s  %s\n" % (sha256(p), rel))
    print("package: %s (%d scenes, %d frames, %.2f s)" % (root, len(scenes), start, start / ep["fps"]))
    if a.zip:
        z = shutil.make_archive(root, "zip", a.out, cfg["package_name"])
        print("zip: %s (%.1f MB)" % (z, os.path.getsize(z) / 1e6))


if __name__ == "__main__":
    main()
