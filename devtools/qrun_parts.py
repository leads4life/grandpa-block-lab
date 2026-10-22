import json, re, subprocess, sys, os
S = "/tmp/claude-0/-home-user/3ffe6a42-e20c-59ee-a796-ce8de686e5e0/scratchpad"
sys.path.insert(0, S + "/nbtest/mock")
nb = json.load(open(sys.argv[1])); stop_at = sys.argv[2]; Q = os.getcwd()
ns = {}
def __sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    print("  $", cmd[:100]); print("   ", "\n    ".join(out[-5:]))
ns["__sh"] = __sh
sec = "0"
for c in nb["cells"]:
    src = "".join(c["source"])
    if c["cell_type"] == "markdown":
        m = re.match(r"## (\d+)\.", src)
        if m: sec = m.group(1)
        if sec == stop_at: break
        continue
    if "BLENDER_SERIES" in src:
        src = 'BLENDER = %r; BPY = "python3"\n' % (S + "/nbtest/fake_blender_parts")
    src = (src.replace('DRIVE = "/content/drive/MyDrive/block_lab"', 'DRIVE = %r' % (Q + "/drive"))
              .replace('REPO_DIR = "/content/repo"', 'REPO_DIR = %r' % (Q + "/repo"))
              .replace('url = "https://x-access-token:%s@github.com/%s.git" % (TOKEN, REPO)', 'url = %r' % (Q + "/origin"))
              .replace('BRANCH = "main"', 'BRANCH = "ep01-scene005"').replace("!python ", "!python3 "))
    lines = []
    for ln in src.splitlines():
        m = re.match(r"^(\s*)!(.*)$", ln)
        lines.append(m.group(1) + "__sh(f" + repr(m.group(2)).replace("\\\\", "\\") + ")" if m else ln)
    code = "\n".join(lines)
    print("[sec %s] %s" % (sec, code.strip().splitlines()[0][:70]))
    exec(compile(code, "cell", "exec"), ns)
print("OK up to section", stop_at)
