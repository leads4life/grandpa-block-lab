"""Face-the-lens patch for an approved scene (agreed 2026-10-22/23): for chosen Grandpa lines, cut to a camera square in front
of his body and have him look into it, then cut back to the scene's own camera. Everything else stays as it was.

    python3 face_patch.py STORY.json PERF.json DIALOGUE.json OUT.json line_id [line_id ...]

PERF.json is the scene's own build (build/perf.json) -- his position and heading per frame. The camera rules (clear air,
line of sight) are the forest/meadow ones outdoors and the cabin's (open south side, walls, furniture) indoors.
"""
import json, math, os, sys
sys.path.insert(0, "/home/user/blocklab")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine", "generators"))
from storykit import auto_frame, gp
from forest_camkit import clear_air, solid_free, both, make_los

FPS = 30
CABIN = (-1.6, 1.4, -0.9, 1.6)                                   # x0, x1, y0, y1 (south side open)
FURN = [((-0.45, -0.15, 0.0), (0.45, 0.25, 0.5)), ((-0.15, 0.5, 0.0), (0.15, 0.8, 0.7)), ((-0.27, -0.02, 0.44), (0.03, 0.2, 0.92))]


def cabin_air(eye):
    x, y, z = eye
    if not (CABIN[0] + 0.15 < x < CABIN[1] - 0.15 and -3.0 < y < CABIN[3] - 0.15 and 0.25 < z < 1.85):
        return False
    return not any(all(lo[i] - 0.06 <= eye[i] <= hi[i] + 0.06 for i in range(3)) for lo, hi in FURN)


def cabin_view(eye, pts):
    for p in pts:
        for k in range(1, 30):
            q = [eye[i] + (p[i] - eye[i]) * k / 30 for i in range(3)]
            if any(all(lo[i] <= q[i] <= hi[i] for i in range(3)) for lo, hi in FURN):
                return False
    return True


def smoother(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (u * 6 - 15) + 10)


def cam_at(keys, t):
    """The engine's own camera interpolation (bl_scene.cam_at), returned as a key dict."""
    if t <= keys[0]["at"]:
        return dict(keys[0])
    for a, b in zip(keys, keys[1:]):
        if a["at"] <= t <= b["at"]:
            u = smoother((t - a["at"]) / max(1e-6, b["at"] - a["at"]))
            return dict(at=t, target=[a["target"][i] + (b["target"][i] - a["target"][i]) * u for i in range(3)],
                        az=a["az"] + (b["az"] - a["az"]) * u, el=a["el"] + (b["el"] - a["el"]) * u,
                        dist=a["dist"] * (b["dist"] / a["dist"]) ** u)
    return dict(keys[-1])


def main():
    story_p, perf_p, dlg_p, out_p, ids = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
    S = json.load(open(story_p)); perf = json.load(open(perf_p))
    L = {l["id"]: l for l in json.load(open(dlg_p))["lines"]}
    cam = [dict(k) for k in S["camera"]]
    wins = sorted([[L[i]["start"] - 0.25, L[i]["end"] + 0.3] for i in ids])
    cuts = [b["at"] for a, b in zip(cam, cam[1:]) if 0 < b["at"] - a["at"] <= 1.0 / FPS + 1e-3]
    def travel(a, b):
        pa, pb = perf[int(a * FPS)]["root"], perf[min(len(perf) - 1, int(b * FPS))]["root"]
        return math.hypot(pb[0] - pa[0], pb[1] - pa[1])
    merged = []
    for w in wins:                       # lines close together share one shot -- unless an original cut or a walk lies between
        if merged and (w[0] - merged[-1][1] < 1.2 and travel(merged[-1][0], w[1]) < 0.6 or w[0] < merged[-1][1] + 0.1):
            merged[-1][1] = max(merged[-1][1], w[1])                # (overlapping lines always share one shot)
        else:
            merged.append(w)
    keep = []
    for w in merged:                     # a line that spans one of the scene's own cuts, or a long walk, keeps its original shots
        if travel(w[0], w[1]) > 2.5:
            print("%.2f-%.2f: a long walk -- left as it was" % tuple(w)); continue
        keep.append(w)
    merged = keep
    log = []
    for t0, t1 in merged:
        t0 = math.ceil(t0 * FPS) / FPS; t1 = math.ceil(t1 * FPS) / FPS
        times = [t0] + [t0 + k for k in range(1, int(t1 - t0))] + [t1]
        keys_out = []
        for t in times:
            p = perf[min(len(perf) - 1, int(round(t * FPS)))]
            x, y = p["root"][0], p["root"][1]; yaw = p["yaw"]
            az0 = math.degrees(math.atan2(-math.cos(yaw), math.sin(yaw)))     # straight out of his chest
            inside = CABIN[0] < x < CABIN[1] and CABIN[2] < y < CABIN[3]
            air = cabin_air if inside else both(clear_air, solid_free)
            los = cabin_view if inside else make_los([((x - 0.2, y - 0.2, 0.0), (x + 0.2, y + 0.2, 1.2))])
            k = None
            for el0, d0 in ((10, 1.5), (14, 1.9), (18, 2.4), (22, 3.0), (26, 3.6)):
                try:
                    k = auto_frame(t, gp(x, y)[1:], (x, y, 0.9), round(az0), el0, d0, air, los=los, margin=0.8)
                    break
                except (Exception, SystemExit):
                    continue
            keys_out.append(k)
        if None in keys_out:
            log.append("%.2f-%.2f: no clear front camera -- left as it was" % (t0, t1)); continue
        for a, b in zip(keys_out, keys_out[1:]):                 # follow him the short way round, same framing size
            b["az"] = a["az"] + ((b["az"] - a["az"]) + 180) % 360 - 180
        swing = max(k["az"] for k in keys_out) - min(k["az"] for k in keys_out)
        if swing > 70:
            log.append("%.2f-%.2f: he turns %d deg during it -- left as it was (no whirling camera)" % (t0, t1, swing)); continue
        if all(abs(k["az"] - keys_out[0]["az"]) < 10 and math.dist(k["target"], keys_out[0]["target"]) < 0.15 for k in keys_out):
            keys_out = [keys_out[0], dict(keys_out[0])]          # standing still: one steady framing
            times = [t0, t1]
        else:
            d0 = max(k["dist"] for k in keys_out); e0 = max(k["el"] for k in keys_out)
            for k in keys_out:
                k["dist"], k["el"] = d0, e0
        before = cam_at(cam, t0 - 1.0 / FPS); after = cam_at(cam, t1 + 1.0 / FPS)
        cam = [k for k in cam if not (t0 - 1.0 / FPS - 1e-6 <= k["at"] <= t1 + 1.0 / FPS + 1e-6)]
        new = [dict(before, at=round(t0 - 1.0 / FPS, 4))] + [dict(k, at=round(t, 4)) for t, k in zip(times, keys_out)] + \
              [dict(after, at=round(t1 + 1.0 / FPS, 4))]
        cam = sorted(cam + new, key=lambda k: k["at"])
        S["actions"].append(dict(type="look", when=round(t0 + 0.05, 3), until=round(t1 - 0.05, 3), body=False, pos="camera", rate=0.3))
        log.append("%.2f-%.2f: front camera, %d keys, az %s..%s el %s dist %s" % (t0, t1, len(keys_out), round(keys_out[0]["az"]), round(keys_out[-1]["az"]), keys_out[0]["el"], keys_out[0]["dist"]))
    S["camera"] = [dict(k, target=[round(v, 4) for v in k["target"]], az=round(k["az"], 3), el=round(k["el"], 3), dist=round(k["dist"], 4))
                   for k in cam]
    S["actions"] = sorted(S["actions"], key=lambda a: a["when"])
    json.dump(S, open(out_p, "w"), indent=1)
    print("\n".join(log))


if __name__ == "__main__":
    main()
