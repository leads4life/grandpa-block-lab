"""Rule 4: back up the whole project to GitHub after every run (the working machine is temporary).

    python3 engine/tools/backup_to_github.py "what changed"   [--branch ep01-scene005]

Copies the working copies (engine, generators, tools, bibles, stories, frozen voices, scene folders, notebooks) into
the repo, commits, pushes, and checks that GitHub has the commit. Sources are the session's working folders below.
"""
import argparse
import glob
import os
import shutil
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = "/home/user/blocklab"                                       # the engine and scene packages as built
GEN = os.environ.get("BLOCKLAB_GEN", "/tmp/claude-0/-home-user/3ffe6a42-e20c-59ee-a796-ce8de686e5e0/scratchpad")
ENGINE = ["bl_*.py", "render.py", "voxelkit.py", "voxelchars.py"]
GENERATORS = ["make_ep01_s0*.py", "storykit.py", "forest_camkit.py", "make_final_nb.py", "make_queue_nb.py", "make_stitch_nb.py"]
TOOLS = ["s3_camcheck.py"]


def copy(patterns, src, dst):
    os.makedirs(dst, exist_ok=True)
    n = 0
    for pat in patterns:
        for f in glob.glob(os.path.join(src, pat)):
            if os.path.isfile(f):
                shutil.copy2(f, dst); n += 1
    return n


def tree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def git(*a, check=True):
    return subprocess.run(["git", "-C", REPO] + list(a), check=check, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message")
    ap.add_argument("--branch", default=None, help="push to this branch (default: the current one)")
    a = ap.parse_args()
    branch = a.branch or git("branch", "--show-current").stdout.strip()
    if branch in ("", "main"):
        raise SystemExit("backups go to a working branch, not main -- pass --branch")
    if git("branch", "--show-current").stdout.strip() != branch:
        git("checkout", "-B", branch)
    counts = dict(engine=copy(ENGINE, WORK, os.path.join(REPO, "engine")),
                  generators=copy(GENERATORS, GEN, os.path.join(REPO, "engine", "generators")),
                  tools=copy(TOOLS, GEN, os.path.join(REPO, "engine", "tools")))
    for d in ("bibles", "stories", "frozen"):
        tree(os.path.join(WORK, d), os.path.join(REPO, d))
    for d in sorted(glob.glob(os.path.join(WORK, "ep*_scene*"))):
        tree(d, os.path.join(REPO, "scenes", os.path.basename(d)))
    if os.path.isdir(os.path.join(GEN, "designs")):
        copy(["*.png", "*.py"], os.path.join(GEN, "designs"), os.path.join(REPO, "bibles", "designs"))
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        print("nothing new to back up on", branch)
        return
    msg = "Backup: %s\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n" \
          "Claude-Session: https://claude.ai/code/session_01XXsv4pkPu7sKngaaDVjEYS" % a.message
    git("commit", "-q", "-m", msg)
    push = git("push", "-u", "origin", branch, check=False)
    if push.returncode != 0:
        raise SystemExit("push failed:\n" + push.stderr)
    local = git("rev-parse", "HEAD").stdout.strip()
    remote = git("ls-remote", "origin", branch).stdout.split()[0]
    print("backed up to %s: %s | GitHub has it: %s | %s" % (branch, local[:10], remote == local, counts))


if __name__ == "__main__":
    main()
