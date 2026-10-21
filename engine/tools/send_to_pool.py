"""Rule 3, "send this to the workflow pool": put an approved scene in the render queue.

    python3 engine/tools/send_to_pool.py grandpa_ep01_scene004 [--accept "no clipping into"] [--repo .]

Writes queue/<EE><SSS>_<slug>/ with the story, the frozen (approved) voice and its timings, and a manifest that pins the
exact engine commit the scene was approved on -- the render notebook checks out that engine, so Colab renders what you saw.
Needs: stories/<slug>.json and frozen/<slug>/{voice.flac, dialogue.json} in the repo, and the engine committed (no local edits).
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), check=True, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--accept", action="append", default=[], help="a check (start of its name) approved as an exception")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    a = ap.parse_args()
    repo, slug = a.repo, a.slug
    story_p = os.path.join(repo, "stories", slug + ".json")
    voice_p, dlg_p = (os.path.join(repo, "frozen", slug, n) for n in ("voice.flac", "dialogue.json"))
    for p in (story_p, voice_p, dlg_p):
        if not os.path.exists(p):
            raise SystemExit("missing " + p + " (freeze the approved voice and copy the story into the repo first)")
    if subprocess.run(["git", "-C", repo, "diff", "--quiet", "HEAD", "--", "engine"]).returncode != 0:
        raise SystemExit("engine/ has uncommitted changes: commit them first, so the scene points at an engine on GitHub")
    commit = git(repo, "log", "-1", "--format=%H", "--", "engine")
    files = sorted(n for n in os.listdir(os.path.join(repo, "engine")) if n.endswith(".py"))
    h = hashlib.sha1()
    for n in files:
        h.update(open(os.path.join(repo, "engine", n), "rb").read().rstrip(b"\n"))
    story = json.load(open(story_p))
    dlg = json.load(open(dlg_p))
    sc = story.get("scene", {})
    order = "%02d%03d" % (sc.get("episode", 0), sc.get("scene", 0))
    dst = os.path.join(repo, "queue", "%s_%s" % (order, slug))
    os.makedirs(dst, exist_ok=True)
    shutil.copy(story_p, os.path.join(dst, "story.json"))
    shutil.copy(voice_p, os.path.join(dst, "voice.flac"))
    shutil.copy(dlg_p, os.path.join(dst, "dialogue.json"))
    man = dict(slug=slug, title=story.get("title", slug), episode=sc.get("episode"), scene=sc.get("scene"), film=dlg["film"],
               engine_commit=commit, engine_files=files, engine_sha=h.hexdigest()[:12], accepted_fails=a.accept,
               approved=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    json.dump(man, open(os.path.join(dst, "manifest.json"), "w"), indent=1)
    print("queued:", os.path.relpath(dst, repo), "| engine", commit[:10], man["engine_sha"], "| accepted:", a.accept or "none")


if __name__ == "__main__":
    main()
