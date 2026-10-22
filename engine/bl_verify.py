"""Block Lab: automatic checks for the active story (build/) and its MP4. Writes build/verification.txt.

    blender -b -P bl_verify.py       |   python3 bl_verify.py (bpy module)     (needs scipy)
"""
import json
import math
import os
import subprocess
import sys

import bpy
import numpy as np
import scipy.io.wavfile as wav
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C

P = C.load_plan()
FPS, NF = P["fps"], P["nf"]
out, ok_all = [], True


def check(name, ok, detail=""):
    global ok_all
    ok_all &= bool(ok)
    out.append("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" -- " + detail) if detail else ""))
    print(out[-1], flush=True)


acts = lambda k: [a for a in P["actions"] if a["type"] == k]
for name, st in P["structures"].items():
    n = sum(1 for b in P["blocks"] if b["struct"] == name)
    if st["expect"] is not None:
        check("%s has %d blocks" % (name, st["expect"]), n == st["expect"], "%d built" % n)
    cells = [tuple(b["cell"]) for b in P["blocks"] if b["struct"] == name]
    check("%s: every block in its own grid cell" % name, len(set(cells)) == len(cells))

bpy.ops.wm.open_mainfile(filepath=os.path.join(C.BUILD, "blocklab.blend"))
sc = bpy.context.scene
objs = [o for o in sc.objects if "settle_frame" in o]
vanish = {"%s_%d_%d_%d" % ((b["struct"],) + tuple(b["cell"])): b["vanish"] for b in P["blocks"] if b.get("vanish")}
collapse_at = {a["target"]: int(a["t0"] * FPS) for a in acts("collapse") + acts("melt")}
loc = {o.name: [] for o in objs}
wz = {o.name: [] for o in objs}
for f in range(NF):
    sc.frame_set(f)
    for o in objs:
        loc[o.name].append(o.location.copy())
        wz[o.name].append(o.matrix_world.translation.z)
moved = 0
for o in objs:
    s = o["settle_frame"]
    end = min(collapse_at.get(o["struct"], NF), vanish.get(o.name, NF)) - 2
    seg = loc[o.name][s:max(s + 1, end)]
    moved += max((p - seg[0]).length for p in seg) > 1e-6
check("blocks hold still once placed%s" % (" (until the collapse)" if collapse_at else ""), moved == 0, "%d moved" % moved)
for g in acts("grow"):
    r = bpy.data.objects["S_" + g["target"]]
    sc.frame_set(min(NF - 1, int(g["t1"] * FPS) + 1))
    want = 1.0                                                     # grows on one structure multiply in order
    for g2 in acts("grow"):
        if g2["target"] == g["target"] and g2["t1"] <= g["t1"]:
            want *= g2["factor"]
    nxt = [g2["t0"] for g2 in acts("grow") if g2["target"] == g["target"] and g2["t0"] > g["t1"]]
    if not nxt or nxt[0] * FPS > int(g["t1"] * FPS) + 1:
        check("%s grows x%g" % (g["target"], g["factor"]), abs(r.scale.x - want) < 1e-3, "scale %.3f (expected %.3f)" % (r.scale.x, want))
def root_at(name, t):
    sc.frame_set(max(0, min(NF - 1, int(round(t * FPS)))))
    return bpy.data.objects["S_" + name].matrix_world.copy()


def scripted(name, t):
    """Where the story says structure `name` should be at time t: grows, slides, spins and swings combined."""
    from mathutils import Matrix
    st = P["structures"][name]
    loc, s = Vector((st["at"][0], st["at"][1], st["at"][2] if len(st["at"]) > 2 else 0.0)), 1.0
    for g in acts("grow"):
        if g["target"] == name:
            u = C.smoother((t - g["t0"]) / max(1e-6, g["t1"] - g["t0"]))
            if g.get("to"):
                loc = loc.lerp(Vector((g["to"][0], g["to"][1], 0)), u)
            s *= 1 + (g["factor"] - 1) * u
    loc_l = Vector()                                               # "local" slides turn with the structure
    for a in acts("slide"):
        if a["target"] == name:
            d = Vector(a["by"]) * C.smoother((t - a["t0"]) / max(1e-6, a["t1"] - a["t0"]))
            if a.get("local"):
                loc_l = loc_l + d
            else:
                loc = loc + d
    for a in acts("fly"):
        if a["target"] == name:
            loc = loc + Vector(C.fly_offset(a, t))
    R = Matrix.Identity(4)
    for a in acts("spin") + acts("swing") + acts("trip"):
        if a["target"] == name:
            if a.get("pivot") is not None:
                p = Vector(C.local_pos(a["pivot"], st["cells"], st["centered"]))
            else:
                p = sum((Vector(C.local_pos(c, st["cells"], st["centered"])) for c in st["cells"]), Vector()) / len(st["cells"])
            axis = {"x": "X", "y": "Y", "z": "Z"}[a.get("axis", "z")]
            R = R @ Matrix.Translation(p) @ Matrix.Rotation(math.radians(C.motion_angle(a, t)), 4, axis) @ Matrix.Translation(-p)
    return Matrix.Translation(loc) @ Matrix.Rotation(math.radians(st.get("yaw", 0.0)), 4, "Z") @ Matrix.Scale(s, 4) @ R @ Matrix.Translation(loc_l)


slide_err = {}
for a in acts("slide"):                                           # each slide follows the script at its start, middle and end
    worst = 0.0
    for tt_ in (a["t0"], (a["t0"] + a["t1"]) / 2, a["t1"]):
        f = max(0, min(NF - 1, int(round(tt_ * FPS))))
        sc.frame_set(f)
        got = bpy.data.objects["S_" + a["target"]].matrix_world
        want = scripted(a["target"], f / FPS)
        worst = max(worst, (got.translation - want.translation).length, max(abs(got[i][j] - want[i][j]) for i in range(3) for j in range(3)))
    slide_err.setdefault(a["target"], []).append(worst)
for name, errs in slide_err.items():
    check("%s slides as scripted (%d moves)" % (name, len(errs)), max(errs) < 2e-3, "worst difference %.4f" % max(errs))
move_err = {}
for a in acts("fly"):                                              # a thrown object follows its arc
    worst = 0.0
    for k in range(5):
        f = max(0, min(NF - 1, int(round((a["t0"] + (a["t1"] - a["t0"]) * k / 4) * FPS))))
        sc.frame_set(f)
        worst = max(worst, (bpy.data.objects["S_" + a["target"]].matrix_world.translation - scripted(a["target"], f / FPS).translation).length)
    check("%s flies on its arc" % a["target"], worst < 2e-3, "worst difference %.4f" % worst)
for a in acts("trip"):                                             # a trip hammer follows its cams (sampled through each lift and drop)
    worst = 0.0
    for sk in C.trip_strikes(a, a["t0"], a["t1"])[:6]:
        for tt_ in (sk - a.get("rise", 0.45) / 2, sk - 1.0 / FPS, sk + 2.0 / FPS):
            f = max(0, min(NF - 1, int(round(tt_ * FPS))))
            sc.frame_set(f)
            got = bpy.data.objects["S_" + a["target"]].matrix_world
            want = scripted(a["target"], f / FPS)
            worst = max(worst, (got.translation - want.translation).length, max(abs(got[i][j] - want[i][j]) for i in range(3) for j in range(3)))
    check("%s strikes as scripted (%d strikes)" % (a["target"], len(C.trip_strikes(a, a["t0"], a["t1"]))), worst < 2e-3, "worst difference %.4f" % worst)
for a in acts("spin") + acts("swing"):                            # every turn follows the script at its start, middle and end
    worst = 0.0
    for tt_ in (a["t0"], (a["t0"] + a["t1"]) / 2, a["t1"]):
        f = max(0, min(NF - 1, int(round(tt_ * FPS))))
        sc.frame_set(f)
        got = bpy.data.objects["S_" + a["target"]].matrix_world
        want = scripted(a["target"], f / FPS)
        worst = max(worst, (got.translation - want.translation).length, max(abs(got[i][j] - want[i][j]) for i in range(3) for j in range(3)))
    move_err.setdefault((a["target"], a["type"]), []).append((worst, a["degrees"]))
for (name, kind), errs in move_err.items():
    total = sum(d for _, d in errs) if kind == "spin" else max(abs(d) for _, d in errs)
    check("%s %s as scripted (%d %s, %g deg %s)" % (name, "spins" if kind == "spin" else "swings", len(errs), "turns" if kind == "spin" else "swings",
          total, "in all" if kind == "spin" else "peak"), max(e for e, _ in errs) < 2e-3, "worst difference %.4f" % max(e for e, _ in errs))
Wd = P.get("world", {})
if Wd:
    def moves(obj_name, attr):
        o = bpy.data.objects.get(obj_name)
        if o is None:
            return False
        vals = []
        for f in (0, min(NF - 1, 15)):
            sc.frame_set(f)
            vals.append(tuple(getattr(o, attr)))
        return vals[0] != vals[1]
    need = ["Island"] + (["Stars"] if Wd["time"] == "night" and Wd["weather"] not in ("rain", "snow") else [])
    missing = [n for n in need if n not in bpy.data.objects]
    check("world built: %s ground, %s, %s" % (Wd["ground"], Wd["time"], Wd["weather"]), not missing, "missing %s" % missing if missing else "")
    if Wd["weather"] in ("rain", "snow"):
        check("%s keeps falling" % Wd["weather"], moves(Wd["weather"].capitalize(), "location"))
    for a in Wd["animals"]:
        if a in ("birds", "seagulls", "pigeons"):
            check("%s fly" % a, moves("BirdPivot_0", "rotation_euler"))
        elif a == "cat":
            cat = bpy.data.objects.get("Cat")
            gap = min((Vector((cat.location.x, cat.location.y)) - Vector((P["structures"][b["struct"]]["at"][0] + b["pos"][0],
                       P["structures"][b["struct"]]["at"][1] + b["pos"][1]))).length for b in P["blocks"]) if cat else 0
            check("cat sits clear of the build", cat is not None and gap > 0.3, "%.2f m from the nearest block" % gap)
for a in acts("melt"):                                            # every block lands exactly on its own slab cell
    st, tgt = P["structures"][a["target"]], P["melt"][a["target"]]
    sc.frame_set(NF - 1)
    off = 0.0
    ids = {tuple(b["cell"]): b["id"] for b in P["blocks"] if b["struct"] == a["target"]}
    for o in objs:
        if o["struct"] == a["target"]:
            cell = tuple(int(v) for v in o.name.split("_")[-3:])
            want = Vector(C.local_pos(tgt[str(ids[cell])], st["cells"], st["centered"]))
            off = max(off, (o.location - want).length)
    layers = 1 + max(c[2] for c in tgt.values())
    cells_used = {tuple(c) for c in tgt.values()}
    check("%s melts into a flat slab" % a["target"], off < 2e-3 and len(cells_used) == len(tgt),
          "%d blocks in %d layer(s), worst landing error %.4f m" % (len(tgt), layers, off))
for a in acts("remove"):                                          # taken apart: every block gone by the end
    sc.frame_set(NF - 1)
    left = sum(1 for o in objs if o["struct"] == a["target"] and o.location.z > -1)
    check("%s is taken down" % a["target"], left == 0, "%d blocks left" % left)
if any(abs(p[2]) > 0.01 for p in P["path"]):                      # grandpa never hangs in the air
    float_frames = 0
    for f in range(0, NF, 5):
        x, y, z = P["path"][f]
        vz = abs(P["path"][min(NF - 1, f + 1)][2] - P["path"][max(0, f - 1)][2]) * FPS / 2
        if z < 0.02 or vz > 0.05:
            continue                                               # on the ground, or on the ladder
        sc.frame_set(f)
        under = [o for o in objs if o.location.z > -1 and abs(o.matrix_world.translation.x - x) < 0.16
                 and abs(o.matrix_world.translation.y - y) < 0.16 and abs(o.matrix_world.translation.z + C.B / 2 - z) < 0.06]
        float_frames += not under
    check("grandpa always stands on something when up high", float_frames == 0, "%d sampled frames floating" % float_frames)
for name, fc in collapse_at.items():
    low = min(z for o in objs if o["struct"] == name for z in wz[o.name][fc:])
    check("%s's rubble stays on the ground" % name, low > -0.01, "lowest block centre %.3f m" % low)

arm = bpy.data.objects["Grandpa"]
from bpy_extras.object_utils import world_to_camera_view
out_frames, worst = [], 1.0
QA = P.get("qa", {})
exempt = [(C.Clock(P["lines"], P["film"])(a), C.Clock(P["lines"], P["film"])(b)) for a, b in QA.get("close_ups", [])]
cutaway = [(float(a), float(b)) for a, b in QA.get("cutaways", [])]   # "cutaways": [[t0, t1]] -- shots of someone else
in_cut = lambda f: any(a <= f / FPS <= b for a, b in cutaway)
for f in [f for f in range(NF) if not in_cut(f)]:                 # grandpa never leaves the picture: hat to boots, every frame
    sc.frame_set(f)                                                # (a story's "qa": {"close_ups": [[t0, t1]]}: his face only)
    head = arm.matrix_world @ arm.pose.bones["head"].tail
    face = arm.matrix_world @ arm.pose.bones["head"].head.lerp(arm.pose.bones["head"].tail, 0.5)
    close = any(a <= f / FPS <= b for a, b in exempt)
    named = {"hat": head + Vector((0, 0, 0.1)), "face": face, "boots": arm.matrix_world.translation,
             "middle": (head + arm.matrix_world.translation) / 2, "hips": arm.matrix_world @ arm.pose.bones["hips"].head,
             "chest": arm.matrix_world @ arm.pose.bones["spine"].head.lerp(arm.pose.bones["spine"].tail, 0.6)}
    want = QA.get("frame_points", ["hat", "boots", "middle"])     # e.g. ["hat", "face", "hips"] for waist-up landscape shots
    for p in ((face,) if close else tuple(named[k] for k in want)):
        v = world_to_camera_view(sc, sc.camera, p)
        m = min(v.x, 1 - v.x, v.y, 1 - v.y) if v.z > 0 else -1.0
        worst = min(worst, m)
        if m < 0.03:
            out_frames.append(f)
            break
check("grandpa stays in the picture every frame (%s%s%s)" % ("hat to boots" if "frame_points" not in QA else ", ".join(QA["frame_points"]),
      ", face in close-ups" if exempt else "", ", except %d cutaway(s)" % len(cutaway) if cutaway else ""), not out_frames,
      "%d frames out%s; closest to the edge %.1f%% of the frame" % (len(out_frames), (" from frame %d" % out_frames[0]) if out_frames else "", worst * 100))
held = {a["target"] for a in P["actions"] if a["type"] == "hold"}
blocked, deps = [], bpy.context.evaluated_depsgraph_get()
for f in [f for f in range(0, NF, 2) if not in_cut(f)]:             # nothing stands between the camera and his face / chest
    sc.frame_set(f)
    deps = bpy.context.evaluated_depsgraph_get()
    eye = sc.camera.matrix_world.translation
    pb_ = arm.pose.bones
    for p in (arm.matrix_world @ pb_["head"].head.lerp(pb_["head"].tail, 0.5), arm.matrix_world @ pb_["spine"].head.lerp(pb_["spine"].tail, 0.6)):
        d = p - eye
        hit, loc_, _, _, ob, _ = sc.ray_cast(deps, eye, d.normalized(), distance=d.length - 0.16)
        if not hit or ob is None:
            continue
        prop = ob.get("struct") or (ob.name[2:].split(".")[0] if ob.name.startswith("X_") else None)   # X_<name>: a prop's decor
        if ob.name not in ("GrandpaMesh", "Grandpa") and prop not in held:
            blocked.append((f, ob.name))
            break
runs = []
for f, ob in blocked:
    if runs and f - runs[-1][1] <= 2:
        runs[-1][1] = f; runs[-1][2].add(ob.split(".")[0])
    else:
        runs.append([f, f, {ob.split(".")[0]}])
check("nothing hides grandpa from the camera (face / chest, every 2nd frame)", not blocked,
      "; ".join("%.1f-%.1f s by %s" % (a / FPS, b / FPS, ", ".join(sorted(o))) for a, b, o in runs[:6]) if runs else "")
cam_dirs = []
for f in range(NF):
    sc.frame_set(f)
    cam_dirs.append((sc.camera.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized())
turns = [math.degrees(cam_dirs[f].angle(cam_dirs[f + 1])) for f in range(NF - 1)]
whips = [f for f in range(1, NF - 2) if turns[f] > 6.0 and not (turns[f - 1] < 3.0 and turns[f + 1] < 3.0)]   # one-frame jumps are cuts
check("camera never whips round (except clean one-frame cuts)", not whips,
      "%d frames turn faster than 6 deg/frame%s" % (len(whips), (" from %.1f s" % (whips[0] / FPS)) if whips else "") if whips else
      "fastest turn %.1f deg/frame outside cuts" % max([t for f, t in enumerate(turns) if not (0 < f < NF - 2 and turns[f] > 6 and turns[f - 1] < 3 and turns[f + 1] < 3)] or [0]))
perf = json.load(open(os.path.join(C.BUILD, "perf.json"))) if os.path.exists(os.path.join(C.BUILD, "perf.json")) else []
holds = [a for a in P["actions"] if a["type"] == "hold"]
for a in [h for h in holds if h.get("hand") != "none"]:            # the hand is on the prop the whole time it carries it
    worst = 0.0
    for f in range(max(0, int(math.ceil(a["t0"] * FPS))), min(NF, int(a["t1"] * FPS) + 1)):   # holds carried in start before frame 0
        sc.frame_set(f)
        grip = bpy.data.objects["S_" + a["target"]].matrix_world @ Vector(a.get("grip", (0, 0, 0)))
        worst = max(worst, (Vector(perf[f]["wrist_" + a.get("hand", "R")]) - grip).length)
    check("%s hand stays on the %s while holding it (%.1f-%.1f s)" % (a.get("hand", "R"), a["target"], a["t0"], a["t1"]),
          worst < 0.03, "largest gap %.1f mm" % (worst * 1000))


def blocks_of(name):
    return [o for o in objs if o["struct"] == name]


def world_box(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(c[i] for c in cs) for i in range(3)]), Vector([max(c[i] for c in cs) for i in range(3)])


sc.frame_set(NF - 1)
for obj, under in QA.get("rests_on", []):                          # props end the scene resting on something, not floating
    lo = min(world_box(o)[0].z for o in blocks_of(obj))
    top = max(world_box(o)[1].z for o in blocks_of(under))
    check("%s rests on the %s at the end" % (obj, under), abs(lo - top) < 0.006, "gap %.1f mm" % ((lo - top) * 1000))
if QA.get("seat") and perf:                                        # sitting on the seat, not sinking into it or hovering
    seat_top = max(world_box(o)[1].z for o in blocks_of(QA["seat"]))
    until = C.Clock(P["lines"], P["film"])(QA.get("seated_until", 0))
    gaps = [perf[f]["hips"][2] - seat_top for f in range(0, min(NF, int(until * FPS)))]
    check("seated on the %s (hip joint 4.5-8 cm above the seat)" % QA["seat"], gaps and all(0.045 <= g <= 0.08 for g in gaps),
          "%.1f-%.1f cm" % (min(gaps) * 100, max(gaps) * 100) if gaps else "no seated frames")
if QA.get("solid"):                                                # grandpa's mesh never sinks into furniture
    gm = bpy.data.objects["GrandpaMesh"]
    deps = bpy.context.evaluated_depsgraph_get()
    tol, bad, deepest, hit_by = 0.008, [], 0.0, {}
    solid = [o for o in objs if o["struct"] in QA["solid"]]
    for f in range(0, NF, 3):
        sc.frame_set(f)
        deps = bpy.context.evaluated_depsgraph_get()
        ev = gm.evaluated_get(deps)
        me = ev.to_mesh()
        vs = [ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
        boxes = [(world_box(o), o["struct"]) for o in solid if o.location.z > -1 and o.scale.x > 0.01]
        for (lo, hi), sname in boxes:
            for v in vs:
                d = min(v.x - lo.x, hi.x - v.x, v.y - lo.y, hi.y - v.y, v.z - lo.z, hi.z - v.z)
                if d > tol:
                    bad.append(f); deepest = max(deepest, d); hit_by.setdefault(sname, []).append(f)
                    break
            else:
                continue
            break
    check("no clipping into %s (sampled every 3rd frame)" % ", ".join(QA["solid"]), not bad,
          "%d frames, deepest %.1f cm%s%s" % (len(bad), deepest * 100, (" (first frame %d)" % bad[0]) if bad else "",
                                             "".join("; %s at frames %s" % (k, v) for k, v in hit_by.items())))
if P.get("target_duration"):
    T_ = float(P["target_duration"])
    check("length about %g s (within -10%%..+10%%)" % T_, 0.9 * T_ <= P["film"] <= 1.1 * T_, "%.2f s" % P["film"])
for a in [a for a in P["actions"] if a["type"] == "face" and a["expr"] != "blink"]:   # each expression actually shows
    f = int((a["t0"] + a["t1"]) / 2 * FPS)
    sc.frame_set(f)
    pbs = arm.pose.bones
    amt = sum(pbs[n].location.length + abs(pbs[n].scale.y - 1) * 0.002 + abs(pbs[n].scale.x - 1) * 0.01 +
              pbs[n].rotation_quaternion.angle * 0.01 for n in ("brow.R", "brow.L", "pupil.R", "pupil.L", "lid.R", "lid.L", "smile", "cheeks"))
    check("face shows \"%s\" at %.1f s" % (a["expr"], f / FPS), amt > 0.004, "face offset %.4f" % amt)
cont = os.path.join(C.BUILD, "continuity.json")
if perf:
    ok_c = os.path.exists(cont)
    if ok_c:
        cj = json.load(open(cont))
        sc.frame_set(NF - 1)
        ok_c = (Vector(cj["grandpa"]["root"]) - arm.matrix_world.translation).length < 0.002 and all(
            (Vector([r[3] for r in v["root"][:3]]) - bpy.data.objects["S_" + k].matrix_world.translation).length < 0.002 for k, v in cj["structures"].items())
    check("continuity state saved and matches the last frame", ok_c)
jr = (arm.data.bones["head"].matrix_local.inverted() @ arm.data.bones["jaw"].matrix_local).translation
jaw = []
for f in range(NF):
    sc.frame_set(f)
    pb = arm.pose.bones
    jaw.append(((pb["head"].matrix.inverted() @ pb["jaw"].matrix).translation - jr).length)
spoken = set()
for ln in [l for l in P["lines"] if not l.get("who")]:            # Grandpa's own lines (other speakers: below)
    fs = range(int(ln["start"] * FPS), int(ln["end"] * FPS) + 1)
    spoken |= set(range(fs.start - 2, fs.stop + 3))
    check("mouth moves on: \"%s\"" % ln["text"][:44], max(jaw[f] for f in fs) > 0.02)
check("mouth closed between lines" + (" (and while others speak)" if any(l.get("who") for l in P["lines"]) else ""),
      max(jaw[f] for f in range(NF) if f not in spoken) < 1e-4)
for who in sorted({l["who"] for l in P["lines"] if l.get("who")}):  # e.g. Tobias: his jaw, on his lines only
    rig = bpy.data.objects.get(who.capitalize())
    if rig is None:
        check("%s is in the scene to speak his lines" % who, False)
        continue
    ang = []
    for f in range(NF):
        sc.frame_set(f)
        q = rig.pose.bones["jaw"].rotation_quaternion
        ang.append(math.degrees(2 * math.acos(min(1.0, abs(q.w)))))
    mine = set()
    for ln in [l for l in P["lines"] if l.get("who") == who]:
        fs = range(int(ln["start"] * FPS), int(ln["end"] * FPS) + 1)
        mine |= set(range(fs.start - 2, fs.stop + 3))
        check("%s's mouth moves on: \"%s\"" % (who, ln["text"][:38]), max(ang[f] for f in fs) > 4.0)
    check("%s's mouth closed between his lines" % who, max(ang[f] for f in range(NF) if f not in mine) < 0.5)

sr, x = wav.read(os.path.join(C.BUILD, "audio", "stem_build.wav"))
x = x.astype(float)
e = np.convolve(x ** 2, np.ones(48) / 48, mode="same")
d = np.diff(e, prepend=0)
offs = []
for b in P["blocks"]:
    if b["prebuilt"]:
        continue
    ts = b["settle"] / FPS
    j0, j1 = int((ts - 0.015) * sr), int((ts + 0.015) * sr)
    offs.append(abs((j0 + np.argmax(d[j0:j1])) / sr - ts) * 1000)
if offs:
    check("every block click lands on its settle frame", max(offs) < 16.7, "median %.1f ms, max %.1f ms" % (np.median(offs), max(offs)))

mp4 = os.path.join(C.HERE, P["slug"] + ".mp4")
if P.get("loop") and os.path.exists(mp4):                         # a looping Short: the last frame flows into the first
    def grab(n):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "select=eq(n\\,%d),scale=108:192" % n, "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
        return np.frombuffer(raw, np.uint8).astype(float)
    first, last = grab(0), grab(NF - 1)
    d = float(np.abs(first - last).mean()) if len(first) == len(last) > 0 else 999.0
    check("loops seamlessly (last frame matches the first)", d < 4.0, "mean difference %.2f of 255" % d)
    _, mx = wav.read(os.path.join(C.BUILD, "audio", "mix.wav"))
    mx = mx.astype(float)[:, 0] / 32768
    jump, step = abs(mx[0] - mx[-1]), float(np.abs(np.diff(mx)).mean())
    check("sound flows across the loop (no click)", jump < 4 * step + 1e-4, "jump %.4f vs typical step %.4f" % (jump, step))
if os.path.exists(mp4):
    for _try in range(6):                                            # (a just-finished encode can need a moment to settle)
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4],
                                       capture_output=True, text=True).stdout or "{}")
        if pr.get("streams"):
            break
        __import__("time").sleep(2)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
    check("MP4 %dx%d H.264 yuv420p 30 fps" % (P["w"], P["h"]), (v["width"], v["height"], v["codec_name"], v["pix_fmt"], v["r_frame_rate"]) ==
          (P["w"], P["h"], "h264", "yuv420p", "30/1"))
    check("MP4 AAC audio, full length", bool(a) and abs(float(pr["format"]["duration"]) - P["film"]) < 0.1 and int(v.get("nb_frames", 0)) == NF,
          "%.2f s, %s frames" % (float(pr["format"]["duration"]), v.get("nb_frames")))
    lo = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(lo.split("I:")[-1].split("LUFS")[0]); pk = float(lo.split("Peak:")[-1].split("dBFS")[0])
    check("loudness about -14 LUFS, no clipping", abs(I + 14) < 1 and pk < -1.0, "%.1f LUFS, peak %.1f dBFS" % (I, pk))
    if P["w"] > P["h"]:                                            # landscape: picture to every edge, no bars or borders
        edge_bad = []
        for n in np.linspace(0, NF - 1, 12).astype(int):
            raw = b""
            for _try in range(4):
                raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "select=eq(n\\,%d)" % n, "-frames:v", "1",
                                  "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
                if raw:
                    break
                __import__("time").sleep(2)
            im = np.frombuffer(raw, np.uint8).reshape(P["h"], P["w"]).astype(float)
            for strip in (im[:6], im[-6:], im[:, :6], im[:, -6:]):
                if strip.mean() < 12 or strip.std() < 1.0:
                    edge_bad.append(int(n)); break
        check("fills the 16:9 frame edge to edge (no black bars)", not edge_bad, "bad frames %s" % edge_bad if edge_bad else "12 frames sampled")
else:
    check("final MP4 exists", False, mp4)
out.append("\nOVERALL: %s" % ("ALL CHECKS PASSED" if ok_all else "SOME CHECKS FAILED"))
open(os.path.join(C.BUILD, "verification.txt"), "w").write("\n".join(out) + "\n")
print(out[-1])
