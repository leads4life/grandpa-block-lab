"""Shared helpers for Grandpa's Block Lab scene generators: camera keys and auto-framing (pure Python)."""
import math

TAN_H = 18.0 / 35.0                                                # 35 mm lens, 36 mm sensor fit horizontal, 16:9
TAN_V = TAN_H * 9.0 / 16.0


def orbit(t, tgt, az, el, dist):
    return dict(at=round(t, 4), target=[round(v, 3) for v in tgt], az=az, el=el, dist=dist)


def eye_of(tgt, az, el, dist):
    ce = math.cos(math.radians(el))
    return (tgt[0] + dist * ce * math.cos(math.radians(az)), tgt[1] + dist * ce * math.sin(math.radians(az)),
            tgt[2] + dist * math.sin(math.radians(el)))


def project(eye, tgt, p):
    f = [tgt[i] - eye[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]; rn = math.hypot(r[0], r[1]); r = [v / rn for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    d = [p[i] - eye[i] for i in range(3)]
    depth = sum(d[i] * f[i] for i in range(3))
    if depth <= 0.05:
        return None
    return (sum(d[i] * r[i] for i in range(3)) / depth / TAN_H, sum(d[i] * u[i] for i in range(3)) / depth / TAN_V)


def auto_frame(t, must, tgt, az0, el0, dist0, keep_clear, margin=0.82, apart=None, prev=None, path_clear=None, fps=30,
               los=None, who=None, apart_min=0.42):
    """Nearest camera (az, el, dist around tgt) to the wanted one that keeps every point of `must` inside the frame,
    stands in clear air (keep_clear(eye) is True) and, if `apart` = (a, b), keeps a and b at least 0.21 frame apart.
    With `prev` (the camera keys so far), the move from the last of them must pass path_clear on every frame; if no
    candidate allows that, a list [hold, key] is returned: a hard cut on the frame before t.
    los(eye, pts) -> True when nothing solid blocks the view of pts: checked for `must` at the key and, during the move,
    for who(time) (Grandpa's points then)."""
    best, cands = None, []
    for daz in range(-60, 61, 4):
        for el in range(8, 34, 3):
            for dist in [dist0 * k for k in (0.9, 1.0, 1.1, 1.25, 1.4, 1.6, 1.8, 2.0)]:
                az = az0 + daz
                eye = eye_of(tgt, az, el, dist)
                if not keep_clear(eye):
                    continue
                pr = [project(eye, tgt, p) for p in must]
                if any(q is None or abs(q[0]) > margin or abs(q[1]) > margin for q in pr):
                    continue
                if apart:
                    qa, qb = project(eye, tgt, apart[0]), project(eye, tgt, apart[1])
                    if qa is None or qb is None or math.hypot(qa[0] - qb[0], qa[1] - qb[1]) < apart_min:
                        continue
                if los and not los(eye, must):
                    continue
                cands.append((abs(daz) / 30 + abs(el - el0) / 10 + abs(dist / dist0 - 1) * 2, az, el, round(dist, 3)))
    for c in sorted(cands):
        if prev:
            k = orbit(t, tgt, c[1], c[2], c[3]); ks = prev + [k]; a = prev[-1]["at"]
            n = max(2, int(round((t - a) * fps)))
            pc = path_clear or keep_clear
            def ok(tt):
                e = cam_eye(ks, tt)[0]
                return pc(e) and (not los or not who or los(e, who(tt)))
            if not all(ok(a + (t - a) * i / n) for i in range(1, n)):
                continue
        best = c; break
    if best is None and prev and cands:                             # no clean move exists: hard-cut to the best framing
        c = sorted(cands)[0]
        tc = math.ceil(t * fps - 1e-6) / fps                        # cut lands on a frame boundary
        return [dict(prev[-1], at=round(tc - 1.0 / fps, 4)), orbit(tc, tgt, c[1], c[2], c[3])]
    if best is None:
        raise SystemExit("auto_frame: no clear camera for t=%.2f (target %s, wanted az %s el %s dist %s)" % (t, tgt, az0, el0, dist0))
    return orbit(t, tgt, best[1], best[2], best[3])


def gp(x, y):                                                       # grandpa standing at (x, y): boots, chest, hat
    return [(x, y, 0.05), (x, y, 0.75), (x, y, 1.18)]


def cam_eye(keys, t):
    """Camera eye at time t, interpolated exactly like bl_scene.cam_at (target lerp, az/el lerp, distance geometric)."""
    if t <= keys[0]["at"]:
        k0 = k1 = keys[0]; u = 0.0
    elif t >= keys[-1]["at"]:
        k0 = k1 = keys[-1]; u = 0.0
    else:
        for k0, k1 in zip(keys, keys[1:]):
            if t <= k1["at"]:
                break
        u = (t - k0["at"]) / max(1e-6, k1["at"] - k0["at"])
        u = u ** 3 * (u * (6 * u - 15) + 10)                       # bl_scene smoother (quintic)
    tgt = [k0["target"][i] + (k1["target"][i] - k0["target"][i]) * u for i in range(3)]
    az, el = k0["az"] + (k1["az"] - k0["az"]) * u, k0["el"] + (k1["el"] - k0["el"]) * u
    d = k0["dist"] * (k1["dist"] / k0["dist"]) ** u
    return eye_of(tgt, az, el, d), tgt, az, el, d


def fix_path(keys, keep_clear, must_at, fps=30, path_clear=None):
    """Check every camera move frame by frame. A move whose camera passes through something (a wall, a canopy) first
    gets one steering key at its middle, framed by auto_frame; if either half still collides the move becomes a hard
    cut (hold the first key, jump on the last frame). path_clear tests the moving camera (default keep_clear); new
    keys are placed with keep_clear. Returns the keys and a list of (time, "steer" | "cut")."""
    path_clear = path_clear or keep_clear
    def hits(ks, a, b):
        n = max(2, int(round((b - a) * fps)))
        return any(not path_clear(cam_eye(ks, a + (b - a) * i / n)[0]) for i in range(1, n))
    out, fixes = [keys[0]], []
    for k1 in keys[1:]:
        k0 = out[-1]
        trial = out + [k1]
        if k1["at"] - k0["at"] <= 1.5 / fps or not hits(trial, k0["at"], k1["at"]):
            out.append(k1); continue
        tm = 0.5 * (k0["at"] + k1["at"])
        _, tgt, az, el, d = cam_eye(trial, tm)
        try:
            km = auto_frame(tm, must_at(tm), tgt, round(az), round(el), d, keep_clear)
            trial = out + [km, k1]
            if not hits(trial, k0["at"], km["at"]) and not hits(trial, km["at"], k1["at"]):
                out += [km, k1]; fixes.append((round(tm, 2), "steer")); continue
        except SystemExit:
            pass
        hold = dict(k0, at=round(k1["at"] - 1.0 / fps, 4))
        out += [hold, k1]; fixes.append((round(k1["at"], 2), "cut"))
    return out, fixes
