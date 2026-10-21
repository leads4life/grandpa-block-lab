"""Camera rules for the forest scenes (lifted unchanged from make_ep01_s004.py): clear air, solid-free moves, line of
sight, clutter (trees, walls, the cast), faces toward camera."""
import math
import bl_world as BW
from storykit import TAN_H, TAN_V

TREES = BW.forest_trees()
def clear_air(eye):
    x, y, z = eye
    if -2.0 < x < 1.8 and -1.25 < y < 2.0 and z < 2.8:
        return False
    if -5.6 < x < -3.95 and 0.3 < y < 2.3 and z < 1.3:
        return False
    for tx, ty, h, k in TREES + [(-2.0, 0.9, 0.45, "sapling")]:
        if math.hypot(x - tx, y - ty) < (1.0 if k != "sapling" else 0.4) and z < h + 1.2:
            return False
    return z > 0.3
def solid_free(eye):
    x, y, z = eye
    if -2.0 < x < 1.8 and -1.25 < y < 2.0 and z < 2.8:
        return False
    if -5.6 < x < -3.95 and 0.3 < y < 2.3 and z < 1.3:
        return False
    for tx, ty, h, k in TREES + [(-2.0, 0.9, 0.45, "sapling")]:
        half, top = {"oak": (0.375, h + 0.7), "pine": (0.4, 0.45 + h * 0.84 + 0.33), "sapling": (0.25, 0.8)}[k]
        if max(abs(x - tx), abs(y - ty)) < half + 0.25 and z < top + 0.25:
            return False
    return z > 0.3
BLOCKERS = [((-1.72, -0.9, 0.0), (-1.6, 1.72, 2.6)), ((-1.72, 1.6, 0.0), (1.52, 1.72, 2.6)), ((-1.9, -1.1, 2.0), (1.7, 1.9, 2.9))]
for tx, ty, h, k in TREES:
    if k == "oak":
        BLOCKERS += [((tx - 0.07, ty - 0.07, 0), (tx + 0.07, ty + 0.07, h)), ((tx - 0.375, ty - 0.375, h - 0.03), (tx + 0.375, ty + 0.375, h + 0.47))]
    else:
        BLOCKERS += [((tx - 0.06, ty - 0.06, 0), (tx + 0.06, ty + 0.06, 0.5))] + [
            ((tx - w / 2, ty - w / 2, 0.45 + h * 0.28 * j - 0.01), (tx + w / 2, ty + w / 2, 0.45 + h * 0.28 * j + 0.33)) for j, w in enumerate((0.8, 0.6, 0.4, 0.2))]
def seg_hits_box(p, q, lo, hi):
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = q[i] - p[i]
        if abs(d) < 1e-9:
            if p[i] < lo[i] or p[i] > hi[i]: return False
            continue
        a, b = (lo[i] - p[i]) / d, (hi[i] - p[i]) / d
        if a > b: a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1: return False
    return True
def clutter(eye, aim, extra=()):
    f = [aim[i] - eye[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]; rn = math.hypot(r[0], r[1]); r = [v / rn for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    near = [(lo, hi) for lo, hi in list(BLOCKERS) + list(extra) if math.dist(eye, [(lo[i] + hi[i]) / 2 for i in range(3)]) < n + 1.0]
    hits = 0
    for ix in range(-3, 4):
        for iy in range(-2, 3):
            dx, dy = ix / 3 * TAN_H * 0.9, iy / 2 * TAN_V * 0.9
            q = [eye[i] + (f[i] + dx * r[i] + dy * u[i]) * n for i in range(3)]
            hits += any(seg_hits_box(eye, q, lo, hi) for lo, hi in near)
    return hits / 35.0
def los(eye, pts):
    aim = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    if clutter(eye, aim) > 0.15:
        return False
    for p in pts:
        d = math.dist(eye, p); q = [p[i] + (eye[i] - p[i]) * min(0.25, d) / d for i in range(3)]
        if any(seg_hits_box(eye, q, lo, hi) for lo, hi in BLOCKERS):
            return False
    return True
def inside(p, box, m=0.02):
    return all(box[0][i] - m <= p[i] <= box[1][i] + m for i in range(3))
def make_los(cast, clutter_cast=()):                                 # the cast block the view too (but not their own points)
    def f(eye, pts):
        if not los(eye, pts):
            return False
        if clutter_cast:                                            # ...and no cast member looms in the foreground
            aim = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
            own = [b for b in clutter_cast if any(inside(p, b) for p in pts)]
            if clutter(eye, aim, [b for b in clutter_cast if b not in own]) - clutter(eye, aim) > 0.08:
                return False
        return not any(seg_hits_box(eye, p, *b) for p in pts for b in cast if not inside(p, b))
    return f
def facing(pos, heading_deg, max_deg):                               # the camera stands in front of this face
    def f(eye):
        a = math.degrees(math.atan2(eye[1] - pos[1], eye[0] - pos[0])) - heading_deg
        return abs((a + 180) % 360 - 180) <= max_deg
    return f
def both(*fs):
    return lambda eye: all(f(eye) for f in fs)
