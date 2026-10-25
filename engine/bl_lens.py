"""Block Lab: face the lens (rev 4). Every line Grandpa says to chat is said into the lens.

    python3 bl_lens.py           # measure -> build/lens.json (per chat line: median angle from his face to the lens)
    python3 bl_lens.py --fix     # ...and give each side-on chat line a camera in front of his body + a look into the lens,
                                 #    written to build/story.json (and stories/<slug>.json); then run bl_common.py,
                                 #    bl_scene.py and bl_lens.py again (it should then change nothing)
Run after bl_scene.py, and after the generator's last (--fit) pass: the fix writes the camera with plain times.
A line is a chat line unless the story line has "who" (someone else says it), "to" (he talks to someone in the scene)
or "lens": false plus a "why" (the writer's choice). bl_verify (engine_rev >= 4) fails any chat line seen side-on.
"""
import json
import math
import os
import statistics
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C

LIMIT = 45.0                                                  # median degrees between where his face points and the lens
FPS = C.FPS
AXES6 = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]


def chat_lines(P, story):
    meta = {l["id"]: l for l in story["lines"]}
    out = []
    for ln in P["lines"]:
        m = meta.get(ln["id"], {})
        if not (ln.get("who") or m.get("who") or m.get("to") or m.get("lens") is False):
            out.append(ln)
    return out


def face_pose(arm):
    """(where his face points, the middle of his face), world space. The rig faces -Y at rest."""
    pb, b = arm.pose.bones["head"], arm.data.bones["head"]
    R = (arm.matrix_world @ pb.matrix).to_3x3() @ b.matrix_local.to_3x3().inverted()
    return (R @ Vector((0, -1, 0))).normalized(), arm.matrix_world @ pb.head.lerp(pb.tail, 0.5)


def cutaways(P):
    return [(float(a), float(b)) for a, b in P.get("qa", {}).get("cutaways", [])]


def measure(sc, arm, P, story):
    """Per chat line: median angle over the frames where his face is in the picture (not in a cutaway)."""
    cuts, rows = cutaways(P), []
    for ln in chat_lines(P, story):
        ang = []
        for f in range(int(ln["start"] * FPS), min(P["nf"], int(ln["end"] * FPS) + 1)):
            if any(a <= f / FPS <= b for a, b in cuts):
                continue
            sc.frame_set(f)
            fwd, face = face_pose(arm)
            v = world_to_camera_view(sc, sc.camera, face)
            if v.z <= 0 or not (0 <= v.x <= 1 and 0 <= v.y <= 1):
                continue
            to_lens = (sc.camera.matrix_world.translation - face).normalized()
            ang.append(math.degrees(fwd.angle(to_lens)))
        if not ang:
            rows.append(dict(id=ln["id"], text=ln["text"], start=ln["start"], end=ln["end"], median_deg=None,
                             verdict="voice-over", ok=True))
            continue
        med = statistics.median(ang)
        rows.append(dict(id=ln["id"], text=ln["text"], start=ln["start"], end=ln["end"], median_deg=round(med, 1),
                         verdict="face-on" if med <= LIMIT else "side-on" if med <= 110 else "back-on", ok=med <= LIMIT))
    return rows


# ---------------------------------------------------------------- the fix: a front camera
def smoother(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (u * 6 - 15) + 10)


def cam_key_at(keys, t):
    """The engine's own camera interpolation (bl_scene.cam_at), returned as a key."""
    if t <= keys[0]["t"]:
        return dict(keys[0])
    for a, b in zip(keys, keys[1:]):
        if a["t"] <= t <= b["t"]:
            u = smoother((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
            return dict(target=[a["target"][i] + (b["target"][i] - a["target"][i]) * u for i in range(3)],
                        az=a["az"] + (b["az"] - a["az"]) * u, el=a["el"] + (b["el"] - a["el"]) * u,
                        dist=a["dist"] * (b["dist"] / a["dist"]) ** u)
    return dict(keys[-1])


def eye_of(tgt, az, el, dist):
    ce = math.cos(math.radians(el))
    return Vector((tgt[0] + dist * ce * math.cos(math.radians(az)), tgt[1] + dist * ce * math.sin(math.radians(az)),
                   tgt[2] + dist * math.sin(math.radians(el))))


class Shot:
    """The scene as it stands at one frame: solid boxes, his framing points, the lens shape."""

    def __init__(self, sc, arm, P, f, held):
        sc.frame_set(f)
        self.sc, self.arm, self.held = sc, arm, held
        self.deps = bpy.context.evaluated_depsgraph_get()
        self.big = set()                                          # the ground, water, sky: never "inside" them
        for o in sc.objects:
            if o.type == "MESH":
                ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
                if max(w.x for w in ws) - min(w.x for w in ws) > 3.5 and max(w.y for w in ws) - min(w.y for w in ws) > 3.5:
                    self.big.add(o.name)
        pb = arm.pose.bones
        head = arm.matrix_world @ pb["head"].tail
        named = {"hat": head + Vector((0, 0, 0.1)), "face": face_pose(arm)[1], "boots": arm.matrix_world.translation.copy(),
                 "middle": (head + arm.matrix_world.translation) / 2, "hips": arm.matrix_world @ pb["hips"].head,
                 "chest": arm.matrix_world @ pb["spine"].head.lerp(pb["spine"].tail, 0.6)}
        self.root = named["boots"]
        self.must = [named[k] for k in P.get("qa", {}).get("frame_points", ["hat", "boots", "middle"])]
        self.sight = [named["face"], named["chest"]]
        fr = sc.camera.data.view_frame(scene=sc)
        self.tan_h = max(abs(v.x) for v in fr) / abs(fr[0].z)
        self.tan_v = max(abs(v.y) for v in fr) / abs(fr[0].z)

    def own(self, o):                                             # held props (the webcam on the strap...) never block
        prop = o.get("struct") or (o.name[2:].split(".")[0] if o.name.startswith(("X_", "S_")) else None)
        return prop in self.held

    def hit(self, eye, d, dist):
        hit, _, nrm, _, ob, _ = self.sc.ray_cast(self.deps, eye, d, distance=dist)
        if not hit or ob is None or ob.name in ("GrandpaMesh", "Grandpa") or self.own(ob):
            return None
        return nrm, ob

    def clear(self, eye):                                         # open air: nothing solid within 15 cm, not inside a wall
        if eye.z < 0.3 or any(self.hit(eye, d, 0.15) for d in AXES6):
            return False
        up = self.hit(eye, Vector((0, 0, 1)), 60.0)
        return not (up and up[0].z > 0 and up[1].name not in self.big)   # the first face above seen from behind: inside

    def project(self, eye, tgt, p):
        q = (Vector(tgt) - eye).to_track_quat("-Z", "Y")
        loc = q.inverted() @ (p - eye)
        if loc.z > -0.05:
            return None
        return loc.x / -loc.z / self.tan_h, loc.y / -loc.z / self.tan_v

    def seen(self, eye):                                          # bl_verify's own rule: nothing between lens and face / chest
        for p in self.sight:
            d = p - eye
            hit, _, _, _, ob, _ = self.sc.ray_cast(self.deps, eye, d.normalized(), distance=d.length - 0.16)
            if hit and ob is not None and ob.name not in ("GrandpaMesh", "Grandpa") and not self.own(ob):
                return False
        return True

    def front(self, az0, subject=None, margin=0.82):
        """Nearest camera square in front of him. subject: what the scene's own shot was looking at (the wheel he talks
        about...): kept in the picture too, when it can be, so the line keeps its context."""
        if subject is not None and (Vector(subject) - self.root).xy.length > 0.5:
            keep = self.must
            self.must = keep + [Vector(subject)]
            k = self.front(az0, None, margin)
            self.must = keep
            if k:
                return k
        zs = [p.z for p in self.must]
        xs, ys = [p.x for p in self.must], [p.y for p in self.must]
        tgt = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, round((min(zs) + max(zs)) / 2 + 0.08, 3))
        best = None
        for daz in range(-40, 41, 5):
            for el in range(4, 29, 3):
                for dist in (1.25, 1.4, 1.6, 1.8, 2.05, 2.35, 2.7, 3.1, 3.6, 4.2):
                    score = abs(daz) / 30 + abs(el - 12) / 10 + (dist - 1.25) * 0.8
                    if best and score >= best[0]:
                        continue
                    eye = eye_of(tgt, az0 + daz, el, dist)
                    if not self.clear(eye):
                        continue
                    pr = [self.project(eye, tgt, p) for p in self.must]
                    if any(q is None or abs(q[0]) > margin or abs(q[1]) > margin for q in pr) or not self.seen(eye):
                        continue
                    best = (score, dict(target=[round(v, 4) for v in tgt], az=az0 + daz, el=el, dist=dist))
        return best[1] if best else None


def fix(sc, arm, P, story, rows):
    perf = json.load(open(os.path.join(C.BUILD, "perf.json")))
    held = {a["target"] for a in P["actions"] if a["type"] == "hold"}
    root = lambda t: perf[max(0, min(len(perf) - 1, int(round(t * FPS))))]
    travel = lambda a, b: math.hypot(root(b)["root"][0] - root(a)["root"][0], root(b)["root"][1] - root(a)["root"][1])
    wins = sorted([r["start"] - 0.25, r["end"] + 0.3] for r in rows if not r["ok"])
    merged = []
    for w in wins:                       # lines close together share one shot -- unless he walks off between them
        if merged and (w[0] - merged[-1][1] < 1.2 and travel(merged[-1][0], w[1]) < 0.6 or w[0] < merged[-1][1] + 0.1):
            merged[-1][1] = max(merged[-1][1], w[1])
        else:
            merged.append(w)
    cam, log, looks = [dict(k) for k in P["camera"]], [], []
    for t0, t1 in merged:
        t0, t1 = math.ceil(max(0.0, t0) * FPS) / FPS, math.ceil(min(P["film"] - 2.0 / FPS, t1) * FPS) / FPS
        if travel(t0, t1) > 2.5:
            log.append("%.2f-%.2f: a long walk -- left as it was (give the line \"lens\": false + \"why\", or restage it)" % (t0, t1))
            continue
        times = [t0] + [t0 + k for k in range(1, int(t1 - t0))] + [t1]
        keys = []
        for t in times:
            yaw = root(t)["yaw"]
            k = Shot(sc, arm, P, int(round(t * FPS)), held).front(round(math.degrees(math.atan2(-math.cos(yaw), math.sin(yaw)))),
                                                                  cam_key_at(P["camera"], t)["target"])
            keys.append(k)
            if k is None:
                break
        if None in keys:
            log.append("%.2f-%.2f: no clear camera in front of him -- restage the line (move him or the clutter)" % (t0, t1))
            continue
        for a, b in zip(keys, keys[1:]):                          # follow him the short way round
            b["az"] = a["az"] + ((b["az"] - a["az"]) + 180) % 360 - 180
        swing = max(k["az"] for k in keys) - min(k["az"] for k in keys)
        if swing > 70:
            log.append("%.2f-%.2f: he turns %d deg during it -- restage it (a front camera would whirl)" % (t0, t1, swing))
            continue
        if all(abs(k["az"] - keys[0]["az"]) < 10 and math.dist(k["target"], keys[0]["target"]) < 0.15 for k in keys):
            keys, times = [keys[0], dict(keys[0])], [t0, t1]          # standing still: one steady framing
        else:
            d0, e0 = max(k["dist"] for k in keys), max(k["el"] for k in keys)
            for k in keys:
                k["dist"], k["el"] = d0, e0
        before, after = cam_key_at(cam, t0 - 1.0 / FPS), cam_key_at(cam, t1 + 1.0 / FPS)
        cam = [k for k in cam if not (t0 - 1.0 / FPS - 1e-6 <= k["t"] <= t1 + 1.0 / FPS + 1e-6)]
        cam += [dict(before, t=t0 - 1.0 / FPS)] + [dict(k, t=t) for t, k in zip(times, keys)] + [dict(after, t=t1 + 1.0 / FPS)]
        cam.sort(key=lambda k: k["t"])
        looks.append(dict(type="look", when=round(t0 + 0.05, 3), until=round(t1 - 0.05, 3), body=False, pos="camera", rate=0.3))
        log.append("%.2f-%.2f: front camera, %d keys, az %d..%d el %d dist %.2f" % (t0, t1, len(keys), keys[0]["az"], keys[-1]["az"],
                                                                                keys[0]["el"], keys[0]["dist"]))
    if looks:
        story["camera"] = [dict({k: v for k, v in key.items() if k not in ("t", "at")}, at=round(key["t"], 4),
                                target=[round(v, 4) for v in key["target"]], az=round(key["az"], 3), el=round(key["el"], 3),
                                dist=round(key["dist"], 4)) for key in cam]
        story["actions"] = story.get("actions", []) + looks
        story.setdefault("lens_fixes", []).extend(looks)
    return looks, log


def main():
    story = C.load_story(os.path.join(C.BUILD, "story.json"))
    P = C.load_plan()
    bpy.ops.wm.open_mainfile(filepath=os.path.join(C.BUILD, "blocklab.blend"))
    sc, arm = bpy.context.scene, bpy.data.objects["Grandpa"]
    rows = measure(sc, arm, P, story)
    for r in rows:
        print("[%s] %-9s %5s deg  %s" % ("PASS" if r["ok"] else "FAIL", r["verdict"], r["median_deg"], r["text"][:60]))
    rep = dict(limit_deg=LIMIT, lines=rows)
    if "--fix" in sys.argv and not all(r["ok"] for r in rows):
        looks, log = fix(sc, arm, P, story, rows)
        print("\n".join(log))
        rep["fix_log"] = log
        if looks:
            json.dump(story, open(os.path.join(C.BUILD, "story.json"), "w"), indent=1)
            src = os.path.join(C.HERE, "stories", story["slug"] + ".json")
            if os.path.exists(src):
                json.dump(story, open(src, "w"), indent=1)
            print("story updated (%d front camera shot(s)): now run bl_common.py, bl_scene.py, bl_lens.py" % len(looks))
    json.dump(rep, open(os.path.join(C.BUILD, "lens.json"), "w"), indent=1)
    n_ok = sum(r["ok"] for r in rows)
    print("face-the-lens: %d / %d chat lines face-on" % (n_ok, len(rows)))


if __name__ == "__main__":
    main()
