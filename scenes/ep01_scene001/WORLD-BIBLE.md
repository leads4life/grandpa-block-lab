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
- **End of Scene 001: 4 viewers.**
- The channel tag `GRANDPA'S BLOCK LAB` sits top-left.

## Open mysteries (established, unexplained)
- A distant, heavy, wooden **CLUNK… CLUNK** comes from the forest outside (Scene 001, about 31.0 s).
