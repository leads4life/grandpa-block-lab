# PRODUCTION BIBLE — Grandpa's Block Lab (engine truths)

## Rule 1: established elements drive later choices
Once something is on screen or in the soundtrack (a sound, a prop, a line, a rhythm, a number), it constrains every
later choice, and every reveal has to pay off what was set up, measurably:
- **Sounds keep their character and timing**: a sound heard off-screen is the same sound when its source is revealed, on the same beat.
  Example: the Scene 001 clunks (two strikes 0.55 s apart, then silence) set the trip hammer's design in Scene 002: 2 cams 60° apart, one turn every 3.3 s.
- **Props and set dressing stay where the continuity file says**, and they don't change without a reason shown on screen.
- **Story options are proposed together with how they pay off what's established.** Prefer the option that pays off most.

## Formats
- **Episode scenes**: `"format": "wide"`, so 1920×1080 landscape, 30 fps, H.264 yuv420p, AAC 48 kHz, −14 LUFS.
  The picture fills the frame edge to edge (verified: no black bars).
- **Shorts** (unchanged): vertical 1080×1920. `"loop": true` makes a seamless loop. Every existing Short still passes its checks.
- **Local previews** render at 34 % scale (652×367) and are encoded to **640×360**. Finals render in Colab at 1920×1080.

## A scene, end to end
1. **Story generator** (Python): `make_ep01_s001.py` writes `stories/<slug>.json`. Everything in it is placed against the measured narration.
2. **Voice pass 1**: run `bl_voice.py`, then save the per-line durations (`*_durations.json`).
3. **Fit pass**: the generator, run with `--fit`, re-times every action, camera move and card to the real durations.
   Lines are split at sentence breaks so each gesture keys to a real timestamp; the words never change.
4. **Build**:
   - `bl_scene.py` builds the Blender scene, keys every frame, and writes `build/continuity.json` and `build/perf.json`.
   - `bl_audio.py` makes the mix.
5. **Preview**: run `render.py --draft --scale 34 --samples 6`, then `bl_overlay.py`, then `bl_verify.py`. Then visual review and repair, at most a few rounds.
6. **Freeze**: copy the approved `voice.wav` (as FLAC) and `dialogue.json` into `frozen/<slug>/`, then regenerate the FINAL notebook.
7. **Final**: `grandpa_block_lab_FINAL_colab.ipynb`, Run all, produces `<slug>_FINAL.mp4`, `<slug>_continuity.json` and `verification.txt`.

## Story JSON: additions in this version (all backward-compatible)
- **Structures**:
  - `at` may be `[x, y, z]`
  - `yaw` (degrees)
  - `extras`: decor boxes `{"c", "s", "m"}`; `m` can be a palette material, or `screen` / `led` (glowing)
  - new materials: `planks`, `ceramic`, `coffee`, `steel`
- **World**: `interior: "cabin"`, `sun: [x, y, z]` (light travel direction), `exposure` (offset).
- **Actions**:
  - `pose`, `face`, `look`, `hold`, `sfx` (see `bl_perform.py`)
  - `fly` can take `sound: "none"`
  - `slide` can take `sound: "scrape" | "click" | "clunk"`
  - `pose` takes `ease_in` / `ease_out`
- **Top level**:
  - `poses` (story-specific poses)
  - `blink`
  - `seed`
  - `target_duration`
  - `scene` metadata
  - `qa` (see below)
- **Cards**: `style: "live"` with `viewers: [[t, n], ...]`.
- **sfx sounds**: tap, clink, sip, slosh, creak, scrape, clatter, click_block, clunk_far, settle.

## Automated QA (`bl_verify.py`)
- **Kept from before**:
  - block counts and grid cells
  - blocks hold still once placed
  - slides, spins and flies follow the script
  - world built correctly
  - mouth moves on every line and stays closed between lines
  - each block click lands on its frame
  - loop seam checks (Shorts)
  - MP4 format and length
  - loudness and peaks
- **New**:
  - **Grandpa in frame**, every frame: `qa.frame_points` (default hat to boots; episodes use hat, face and chest), with `qa.close_ups` windows where only his face needs to be in frame.
  - **Hand on held prop**: the hand stays on what it holds, every frame (< 3 cm).
  - **Props resting**: props end resting on their support (`qa.rests_on`, < 6 mm).
  - **Seated contact**: while seated, his hip joint is 4.5–8 cm above the seat (`qa.seat`, `qa.seated_until`).
  - **No mesh clipping**: his deformed mesh doesn't go into `qa.solid` structures by more than 8 mm (sampled every 3rd frame).
  - **Expressions**: each expression actually moves the face.
  - **Length**: within ±10 % of `target_duration`.
  - **No black bars**: landscape frames have picture at every edge.
  - **Continuity**: the saved continuity state matches the last frame.

## Continuity between scenes
- `continuity.json` holds:
  - Grandpa's root position and facing, hip position, the active body pose channels, face channels and wrist positions
  - every structure's final matrix and how many of its blocks are still standing
  - the camera position and last camera key
  - world settings
  - the LIVE viewer count
  - the ambience type and the last line
- The next scene starts its generator from that file: Grandpa's start position, facing, pose, prop positions, camera and viewer count.

## Known engine limits and next steps
- **Picking up exactly where a scene ended.** Scene 002's generator has to copy the end state across by hand. It reads the continuity file, then sets Grandpa's start position and each prop's position in its story JSON. A small helper that does this automatically is the planned next step.
- **Joining scenes into one episode.** Each scene is normalised to −14 LUFS on its own. That's fine for previews, but when scenes are joined the ambience level can jump at each seam.
  - Plan: use fixed mix levels for every segment, and normalise once on the assembled episode.
  - The wall-clock tick restarts its rhythm at 0.37 s in each scene; for seamless assembly, offset it by the scene's start time in the episode.
- **Speed.** A 1920×1080 frame of this cabin takes several seconds on a T4. A 33 s scene is roughly 45–75 min of GPU time.
