# WORLD BIBLE — Grandpa's Block Lab

Only established facts. All coordinates are in metres: x is right and y is away from the camera's default side. One block is 0.1 m.

## The island
- A round voxel island, radius 2.7 m, with a grass top. Trees stand at (-2.0, 0.9), (1.9, -1.2) and (-1.6, -1.7).
- Birds circle overhead (`animals: ["birds"]`). Episode 1 is a clear morning.
- No Minecraft (or other third-party) assets, textures or branding. Everything is original procedural voxels.

## Grandpa's log cabin (`world.interior = "cabin"`)
- **Floor**: plank floor from x -1.6 to 1.4 and y -0.9 to 1.6, top at z = 0.004.
- **Walls**: 0.12 m thick horizontal logs, 2.0 m high. The rows overlap, so no light leaks through.
- **Open sides**: the front (camera side) and the top are open, like a doll's house; the camera never shows those edges.
- **Left (west) wall, x = -1.66**: the **door**, at y 0.45–0.95 and up to 1.25 m high. It is shut, with a brass knob and white trim.
  - Scene 002 begins here: the clunking is outside this door.
- **Right wall, x = 1.46**: a four-pane window at y 0.15–0.75, z 0.6–1.2. The low morning sun shines through it: sunlight travel direction is (-0.96, -0.06, -0.27).
- **Back wall, y = 1.66**: four-pane window at x 0.35–0.95, z 0.75–1.35.
  - A shelf at x -1.05 to -0.25, z 1.15, holding 7 coloured books and a small pot.
  - A clock at (1.12, 1.55).
- **Corners and floor**: a red rug under the table and chair; a potted plant in the back-right corner, around (1.15, 1.35).

## Furniture and props in Scene 001 (structures; their final positions are in `grandpa_ep01_scene001_continuity.json`)

| Name | What | Where |
|---|---|---|
| `table_top`, `table_legs` | plank table, top surface at 0.50 m | x -0.45..0.45, y -0.15..0.25 |
| `seat`, `chair_legs`, `chair_back` | wooden chair, seat top at 0.30 m | starts y 0.49..0.69; **pushed back 0.16 m** when he stands (ends y 0.65..0.85) |
| `laptop_base`, `laptop_screen` | steel laptop, glowing screen facing him | root (-0.12, 0.14, 0.42), turned -18° |
| `webcam` | home-made black block webcam with lens and red LED, on the laptop | same root |
| `cam_cap` | red block on top of the webcam | popped off and put back; ends on the webcam |
| `mug` | cream ceramic mug with coffee | ends where it started: root (0.22, 0.06, 0.48), resting on the table |

## Light and sound
- **Morning**: warm sun through the right window, sky light from above, view exposure +0.15 on top of the morning preset.
- **Indoor ambience**:
  - quiet room tone
  - wind muffled by the walls
  - birds heard through the window
  - the wall clock ticking once a second
- Indoor footsteps knock on floorboards.

## Stream overlay state
- Top-right badge `LIVE · N VIEWERS`, at **3 viewers**; it becomes **4** during "welcome to Grandpa's Block Lab" (with a "+1").
- **End of Scene 001: 4 viewers.** Still 4 at the end of Scene 002.
- The channel tag `GRANDPA'S BLOCK LAB` sits top-left.

## The forest west of the cabin (`world.terrain = "forest_west"`, from Scene 002)
- **Ground**: land extends west of the island as an ellipse centred at (-6.0, 0.8), radii 4.6 × 4.4 m.
- **Trees**: 55 voxel oaks and pines, from a fixed seed. The camera spots and the path are kept clear of them.
- **Sapling**: the small sapling at (-2.0, 0.9), just outside the door, has been there since Scene 001. The path curves round it.
- **Path**: dirt tiles from the door to the stream bank: (-1.75, 0.62) → (-2.3, 0.42) → (-3.1, 0.45) → (-3.85, 0.5).
- **Stream**: runs north–south along x = -5.2 + 0.25·sin(0.7·y), 0.7 m wide, flowing south. Stones line both banks, and you hear it babble, louder as he gets closer.
- **Cabin**: from outside it has a log roof, seen only from outside (it doesn't change the interior light).
- **The door**: hinged at its south edge (y 0.45). In Scene 002 it **opens outward 125° and is left open**.

## The water-powered trip hammer (Scene 002) — its design is set by the Scene 001 clunks (Rule 1)
- **Waterwheel**: radius 0.55 m, hub at (-5.0, 1.0, 0.55), in the stream. A rim, 4 spokes and 8 paddles, weathered `oldwood`.
- **Axle**: along x, from the wheel east to x -4.2, carrying **2 cams** at x -4.4.
- **Timing**: one turn every **3.3 s**. The cams are **60° apart**, so the hammer strikes twice 0.55 s apart, then rests for 2.75 s.
- **Strike times** continue Scene 001's: 30.98 and 31.53 s there, then every 3.3 s. In Scene 002 the pairs fall at 1.28 / 1.83 s + 3.3 k.
- **Lever**: a wooden arm (helve) on a pivot at (-4.4, 1.3, 0.75). The cams push its tail down, which lifts the **dark iron head**; then it drops onto a **stone anvil** at y 1.8–2.1 (top 0.5 m).
- **New repairs**: two bright `planks` blocks, among the old grey wood:
  - a **new axle post** at (-4.1, 1.0)
  - a **new pivot pin**

  Somebody fixed it recently. Who is not yet known.

## Open mysteries (established, unexplained)
- The distant **CLUNK… CLUNK** (Scene 001) is the trip hammer (Scene 002). **Who repaired it** is unknown (end of Scene 002).

## Scene 003 additions ("Rotten to the Core")
- **The old axle post is replaced.** The rotten post at (-4.7, 1.0) is gone. In its place: a 2-block **stone footing** (`footing`), then a 3-block fresh **planks post** (`post2`) on top. The axle is lifted back level, and both cams strike again.
- **Bank stone**: a flat 2×2 stone at (-3.75, 1.25), top 0.10 m. **The webcam sits on it**, pointed at the work (Rule 2).
- **Tiny boot prints** in the mud by the old post, leading down to the water (`footprints`, 6 prints). He notices: "And they're tiny."
- **A rabbit** pops out from behind the oak at (-4.08, 3.03), sits near the bank, then hops back behind the oak.
- **Weather**: a cloud passes over the sun during the rot lesson, and leaves fall during the rabbit beat.
- **Overlay**: still LIVE · 4 viewers.

## Planned (approved direction, NOT yet on screen)
- **Who fixed the trip hammer: his grandson** (user, 2026-10-21). This pays off the tiny boot prints, the prints leading to the water, the new planks, and the unexplained 4th viewer who joined at "welcome" in Scene 001. Grandpa doesn't know yet.
- **The boar.** Superseded idea (user had said "boar is a guard"): the boar guards the grandson's place. Approved: a wild boar that raids Tobias's garden, kept away by the trip hammer's clunk.
- **After the save**: the grandson scares the boar off, and Grandpa tells chat that his grandson "has aura".
- **Scene 004 micro-lesson (user, 2026-10-21): Tobias explains the machine and its purpose.**
  - The trip hammer is a **water-powered boar scarer**. Tobias fixed it so the clunk keeps the boar out of his garden.
  - Grandpa turning it off is what lets the boar come close.
  - Tobias re-engages it, and CLUNK sends the boar away unharmed.
  - Real-world link: the Japanese *shishi-odoshi* ("deer/boar scarer"), a water-powered clacker said to have been invented by farmers to scare off deer and wild boar. The origin is traditional and not firmly documented, so say "people say" / "it's said".
  - It must be an original, realistic voxel wild boar: bristly dark-brown coat, a ridge along the back, a long snout, small curved tusks. Nothing that looks like a game mob.
  - **Design APPROVED 2026-10-21** (`voxelchars.build_boar`, calm and agitated moods; sheet `bibles/DESIGN_tobias_and_boar.png`).
- **Possible micro-lesson**: a boar's lower tusks keep growing all its life, and the upper ones sharpen them like a knife sharpener.

## The blueprint book and its missing pages (approved 2026-10-21; planned from Scene 006)
- **The book**: an old, worn blueprint book in Grandpa's own handwriting. Years ago he designed the trip hammer in it, then
  stopped building. Tobias borrowed it from Grandpa's bookshelf "ages ago", which is how he could fix the machine.
- **Page twelve**: a garden gate with a lever (the Scene 007 Blueprint Build). When he opens it, the drawing lifts off the
  paper as a glowing blue 3D wireframe for 2–3 s, then settles back.
- **The mystery**:
  - **Pages are torn out** (13, 14, ...). They turn up around the land one at a time: in a bottle in the stream, under a
    stone, in a bird's nest, in the cabin's roof beams. Each page found is the next Blueprint Build.
  - Who tore them out and hid them is **unknown**. Grandpa's favourite theory, stated with total confidence, is **aliens**.
    It's a comic theory the show never confirms. The real answer is left open; it could later be touching (young Grandpa,
    or Tobias) or stay a running gag.
- **Saved for later**: Grandpa asking an AI assistant on his laptop at the cabin. Always an unbranded, made-up assistant.
