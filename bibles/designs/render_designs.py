"""Design sheets for approval: Tobias and the boar, next to Grandpa Tovi (unchanged), plus the Scene 004 standoff beat."""
import math, os, sys
sys.path.insert(0, "/home/user/blocklab")
import bpy
from mathutils import Vector
import voxelkit as VK
import voxelchars as CH

OUT = os.path.dirname(os.path.abspath(__file__))
SAMPLES = int(os.environ.get("SAMPLES", "48"))
RES = (1600, 900)


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device, cy.samples, cy.use_denoising, cy.denoiser = "CPU", SAMPLES, True, "OPENIMAGEDENOISE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = RES[0], RES[1], 100
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.80, 0.86, 0.93, 1); bg.inputs[1].default_value = 0.75
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy, sun.data.angle = 2.7, math.radians(8); sun.data.color = (1.0, 0.95, 0.86)
    sun.rotation_euler = (math.radians(52), math.radians(-8), math.radians(-35))
    grass = VK.pixel_material("Grass", (0.26, 0.48, 0.18), (0.36, 0.60, 0.24), 0.1 / 8)
    VK.mesh_obj("Ground", [((0, 2, -0.05), (14, 14, 0.1), 0)], [grass])
    return sc


def camera(sc, eye, target, lens=50):
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.location = eye
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = VK.look_quat(eye, target)
    sc.camera = cam


def place(arm_or_root, x, y, yaw):
    arm_or_root.location = (x, y, 0)
    arm_or_root.rotation_euler = (0, 0, math.radians(yaw))


def grandpa(sc, x, y, yaw, panic=False):
    a = VK.build_grandpa(sc, None)
    place(a, x, y, yaw)
    if panic:                                                      # FROZEN: hands up, leaning back, eyes huge, mouth open
        CH.pose_bone(a, "spine", rot=(-9, 0, 0))
        CH.pose_bone(a, "head", rot=(-6, 0, 0))
        CH.pose_bone(a, "upper_arm.R", rot=(0, 62, 0)); CH.pose_bone(a, "forearm.R", rot=(0, 78, 0))
        CH.pose_bone(a, "upper_arm.L", rot=(0, -62, 0)); CH.pose_bone(a, "forearm.L", rot=(0, -78, 0))
        for sd in ("R", "L"):
            CH.pose_bone(a, "brow." + sd, off=(0, 0, 0.014))
            CH.pose_bone(a, "pupil." + sd, S=(0.65, 1, 0.65))
        CH.pose_bone(a, "jaw", rot=(16, 0, 0))
        CH.pose_bone(a, "smile", S=(0.6, 1, 2.6), off=(0, 0, -0.004))
    return a


def tobias(sc, x, y, yaw, mood="calm"):
    a = CH.build_tobias(sc)
    place(a, x, y, yaw)
    if mood == "calm":                                             # calm confidence: notebook up, other hand out, "easy..."
        CH.pose_bone(a, "upper_arm.L", rot=(-38, 0, 0)); CH.pose_bone(a, "forearm.L", rot=(-62, 0, 0))
        CH.pose_bone(a, "upper_arm.R", rot=(-55, 22, 0)); CH.pose_bone(a, "forearm.R", rot=(-25, 0, 0))
        CH.pose_bone(a, "brow.L", off=(0, 0, 0.012))               # one eyebrow way up: "I've read about this"
        CH.pose_bone(a, "brow.R", off=(0, 0, -0.003))
        for sd in ("R", "L"):
            CH.pose_bone(a, "lid." + sd, S=(1, 1, 5))              # focused, not sleepy
        CH.pose_bone(a, "smile", S=(0.9, 1, 1.0), off=(0.008, 0, 0.003))   # a small, sure, one-sided smile
    return a


def render(name):
    path = os.path.join(OUT, name + ".png")
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("WROTE", path)


which = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["lineup", "tobias", "boar", "standoff"]
if "lineup" in which:                                              # scale: Grandpa Tovi, Tobias, the boar
    sc = fresh()
    grandpa(sc, -0.85, 0, 0)
    tobias(sc, 0.05, -0.05, 0, mood="rest")
    b = CH.build_boar(sc, "calm"); place(b, 1.05, 0.15, -62)
    camera(sc, (0.1, -4.4, 0.95), (0.1, 0, 0.5))
    render("01_lineup")
if "tobias" in which:                                              # turnaround: front, three-quarter, side, back
    sc = fresh()
    for i, yaw in enumerate((0, -35, -90, 180)):
        tobias(sc, -0.75 + 0.5 * i, 0, yaw, mood="calm" if i == 0 else "rest")
    camera(sc, (0.0, -2.9, 0.62), (0.0, 0, 0.42))
    render("02_tobias_turnaround")
if "boar" in which:                                                # calm vs agitated, side on
    sc = fresh()
    b1 = CH.build_boar(sc, "calm", "BoarCalm"); place(b1, -0.62, 0, -20)
    b2 = CH.build_boar(sc, "agitated", "BoarAngry"); place(b2, 0.42, 0, -20)
    camera(sc, (-0.02, -3.6, 0.75), (-0.02, 0, 0.34))
    render("03_boar_calm_vs_agitated")
if "standoff" in which:                                            # the Scene 004 beat: "NO CAP, CHAT!" ... Tobias steps in
    sc = fresh()
    b = CH.build_boar(sc, "agitated"); place(b, 0.95, 0.35, 195)
    grandpa(sc, -0.05, 0.1, 62, panic=True)
    tobias(sc, -0.72, -0.35, 30, mood="calm")
    camera(sc, (-0.25, -3.1, 0.62), (0.15, 0.1, 0.5), lens=40)
    render("04_standoff")
