# PRODUCTION BIBLE — Grandpa's Block Lab (engine truths)

## Rule 1: established elements drive later choices
Once something is on screen or in the soundtrack (a sound, a prop, a line, a rhythm, a number), it constrains every
later choice, and every reveal has to pay off what was set up, measurably:
- **Sounds keep their character and timing**: a sound heard off-screen is the same sound when its source is revealed, on the same beat.
  Example: the Scene 001 clunks (two strikes 0.55 s apart, then silence) set the trip hammer's design in Scene 002: 2 cams 60° apart, one turn every 3.3 s.
- **Props and set dressing stay where the continuity file says**, and they don't change without a reason shown on screen.
- **Story options are proposed together with how they pay off what's established.** Prefer the option that pays off most.

## Rule 2: the stream camera (Grandpa's block webcam)
- **Traveling**: he carries it (`hold` with a `{"char": ...}` key, right hand) and talks to chat.
- **Working** (building, repairing, taking apart, any two-handed job): he first **sets it down** on something nearby, such as a stump, rock or post, pointed at himself and the work, with a line ("Hang on, chat... Grandpa needs both hands."). Then both hands are free.
- **Leaving**: when he leaves, he picks it back up (or deliberately leaves it, as a gag).
- **Where it is** goes in the continuity file every scene: carried, or set down at a position. The next scene starts from that.

## Rule 3: the approval gate (user, 2026-10-21)
Every scene is **60 s ±10%** from Scene 006 on (user, 2026-10-21): one complete comic arc (setup, escalation, punchline,
button) with room for pauses and the micro-lesson. Scenes 001–005 stay at their approved ~30 s. Each scene is **rendered in
two ~30 s parts** (one Colab run each, so a disconnect still costs very little), and the parts are joined back into the scene.
Finished scenes are **pooled**, and episodes are **stitched later**. After each preview:
- **Always ask: "Send this to the workflow pool?"**
  - **Yes**:
    1. Freeze the voice.
    2. Export the scene package (`story.json` + `voice.flac` + `dialogue.json`) to the render **queue**.
    3. The Colab render notebook renders one scene per run, and puts the finished clip in the **pool**.
  - **No**: ask for further instructions, fix the scene, show a new preview, and ask again.
- Nothing enters the queue without the user's yes.
- Stitching an episode from the pool is a separate step. It checks that each scene's end state matches the next one's start, and it levels the audio once across the whole episode.

## Rule 4: back up after every run (user, 2026-10-21)
The working machine is temporary. **After every run** (each preview, fix round or approval), the whole project goes to
GitHub with `engine/tools/backup_to_github.py`:
- **What it copies**: the engine, the generators and tools, the bibles and designs, the stories, the frozen voices,
  every scene folder (story, generator, continuity, previews, QA) and the notebooks.
- It commits and pushes to the current working branch, then confirms that GitHub has the same commit.
- **Only** a backup goes to the working branch. A scene enters the render queue only through Rule 3's yes.

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

## Added for Scene 002 (all reusable; old stories render unchanged)
- **World**: `terrain: "forest_west"` (forest and stream), `roof: true`, `door_open: [t0, t1, degrees]`.
- **Materials**: `oldwood`, `darkiron`.
- **Actions**:
  - `trip`: a cam-driven hammer with `period`, `first`, `cams` (offsets in s), `rise`, `drop`, `degrees`, `pivot` and `sound_at`. It produces a clunk at every strike, timed exactly.
  - `hold` keys at `{"char": ...}`: carried things.
  - `look` at `obj`.
  - `move` with `"face": "path"`.
  - Hand targets at `{"world": ...}`.
  - sfx `door_creak`.
- **Sound by place**:
  - Clunks and other off-screen sources are heard from Grandpa's position (his webcam is the stream mic). They get louder and brighter as he nears, and indoors they're muffled through the walls (Scene 001's exact clunk) until the door opens.
  - Indoor and outdoor ambience crossfade as he walks out.
  - The stream babbles by distance.
  - Footsteps are wood on the cabin floor and grass outside.
- **`engine_rev: 2`** in a story turns on fixes that would change already-approved scenes. The first is that a hold's reach-in ramp now plays, so the hand travels to the object first. Approved scenes keep rev 1, and verified rebuilds of Scene 001 are identical to its continuity file.
- **Auto-framing** (in the scene generator, `auto_frame`): for each camera key it searches angle, height and distance so Grandpa (hat, chest, boots) and the named story points are all in frame, from clear air (no trees, no walls). It also keeps him from covering the subject. It's planned to move into the engine.
- **Camera cuts**: two camera keys one frame apart make a hard cut. Use them for motivated cuts only (through a door, after a beat).
  The cut must land on a frame boundary, otherwise one frame shows the half-way interpolation.
- **Camera rules learned in Scene 003** (`storykit.auto_frame`, built one key at a time with `prev=`). Every key and every frame of every move must pass:
  - **Never inside anything**: no wall, roof, canopy or machine (`solid_free`, using the trees' real built sizes).
  - **Clear line of sight**: from the lens to Grandpa (hat, chest, boots) and to the story points (`los`).
  - **Little foreground clutter**: no more than 15% of the frame covered by something in front of the subject (a 7×5 ray grid).
  - **Clear of the cabin**: wide shots keep about 0.8 m from it (`clear_far`), or its corner logs and roof beams poke into the frame.
  - **Smooth or cut**: if no smooth move is clean, the framer cuts to the best clean framing. Keep cuts to story beats and avoid near-identical angles across a cut (jump cut).
  - **Moving critters**: their entry, rest and exit points all go into the shot's required points, so they stay in frame.
  - **Always check stills**: around every move and cut, before rendering.

## Continuity between scenes
- `continuity.json` holds:
  - Grandpa's root position and facing, hip position, the active body pose channels, face channels and wrist positions
  - every structure's final matrix and how many of its blocks are still standing
  - the camera position and last camera key
  - world settings
  - the LIVE viewer count
  - the ambience type and the last line
- The next scene starts its generator from that file: Grandpa's start position, facing, pose, prop positions, camera and viewer count.
- **Never carry a spinning part's matrix** (wheel, axle, cams). Its stored matrix is rotated about the pivot, so its
  translation is not a position. Keep the part's own `at`, and continue the spin from the machine's clock. (Bug found 2026-10-21:
  Scenes 003–005 had the waterwheel and axle floating about 1.5 m up in the trees. Fixed in the Scene 003 generator, with
  003–005 regenerated. Only those four parts moved.)

## Known engine limits and next steps
- **Picking up exactly where a scene ended.** Scene 002's generator has to copy the end state across by hand. It reads the continuity file, then sets Grandpa's start position and each prop's position in its story JSON. A small helper that does this automatically is the planned next step.
- **Joining scenes into one episode.** Each scene is normalised to −14 LUFS on its own. That's fine for previews, but when scenes are joined the ambience level can jump at each seam.
  - Plan: use fixed mix levels for every segment, and normalise once on the assembled episode.
  - The wall-clock tick restarts its rhythm at 0.37 s in each scene; for seamless assembly, offset it by the scene's start time in the episode.
- **Speed.** A 1920×1080 frame of this cabin takes several seconds on a T4. A 33 s scene is roughly 45–75 min of GPU time.

## Added for Scene 004 (all reusable; older scenes rebuild bit-identical, which is verified)
- **The cast beyond Grandpa** (`bl_cast.py`, approved designs in `voxelchars.py`), as `world.critters` entries:
  - **`boar`**: walks a keyed `path` with a trotting gait. It also takes:
    - `yaw` keys while standing
    - `backing` windows (backs away, still facing them)
    - `mood` calm/agitated (switched on a huff)
    - `huffs` (breath puffs, snout jerk), `clacks` (head shake), `stomps` (front leg lifts and slams, dust)
    - `startle` (a jump and a squeal)
  - **`tobias`**: walks with arm and leg swing. It also takes:
    - `yaw`, `look`, `visible`
    - `poses` (point_R, easy_R, notebook_L, write_R, kick_R, lean_in)
    - `faces` (calm, smile, deadpan)
    - his own blinks
    - his jaw driven by his own voice (`dialogue.json` `mouths.tobias`)
- **Voices**: a line's `"who": "tobias"` uses `bl_voice.CAST`. A line can also carry its own `speed` and `fx`; "NO CAP, CHAT!" is 1.3× and pitched up for panic.
- **Hand-free holds** (`"hand": "none"`): a keyed path no hand grips. Use it for props someone else moves (Tobias yanks the prop and tosses it), or for a prop lying still before it's picked up.
- **Machine off and on**:
  - **Off**: a `spin` lifts the hammer arm onto a prop, and `skip` windows silence both cams.
  - **On again**: a −16° spin over the 0.45 s rise before a scheduled strike, so the cam takes the weight and the strike lands on the clock.
- **Camera rules added** (generator):
  - **The cast block the view too**: Grandpa (widened for raised arms), the boar and Tobias.
  - **Faces toward camera** for the lines that live on a face (`facing(...)`).
  - **No cast member looming in the foreground**: at most 5% of the frame.
  - **Every body point in frame**: an animal's nose, middle and rump all stay in.

## Recurring segment: Blueprint Builds (user, 2026-10-21)
Grandpa's "Mister Rogers moment": now and then (about once every 2–3 scenes) a blueprint turns up in the adventure and he
builds it, talking chat through it.
- **The ritual**:
  1. The find (paper-crinkle ASMR; he reads it upside down first).
  2. The build, block by block (clicks), while he guesses, grumbles and jokes.
  3. The oops: his overconfidence makes the first try fail. This is where the lesson lives.
  4. He works out why, fixes it and tests it. One short "aha" card.
  5. The button.
- **A lesson, not a lecture**:
  - At most 2–3 science sentences; the build shows the idea and the mistake teaches it.
  - Grandpa learns too.
  - The habit on show is always try → fail → look closer → fix.
- **Rule 1 applies**: the blueprint comes from something already set up, and the build stays in the world.
- **One build per 60 s scene.**
- **Grandpa solo**: Tobias exits gracefully before the build, so the focus is Grandpa, the build and his commentary.
- **Animals are never hurt.** Deterrents are humane (gates, fences that give a short harmless jolt).
- **Kids watch**: Grandpa never touches live wires, and nothing in a build is unsafe to copy.

## Added for Scene 006 (all reusable; older scenes rebuild bit-identical)
- **Flashback kit**: a `"dream"` card ripples and softens the picture. A `memory_cloud` critter puts a puffy cloud over
  his head, with a mini agitated boar on its ledge; its `face` turns the ledge toward the camera.
  - `"echo|<frozen slug>|<line id>|<repeats>"` sfx replays an earlier scene's frozen line, fainter and slower each time.
    `send_to_pool` copies that frozen voice into the queue package, and the render notebook puts it in place.
  - A line's `fx.aecho` gives a dreamy murmur.
- **3D blueprint**: a `hologram` critter, a glowing blue wireframe that lifts off the page and turns. Use `size` to fit it
  to the book.
- The **LIVE badge** shows "-1" when the count drops.
- Structure `extras` draw ink on paper (the blueprint grid and drawings).
- New materials `paper`, `leather` and `glass`; new sfx `buzz` (tablet) and `page` (page turn).

## Word Cards: vocabulary micro-lessons (user, 2026-10-22; from Scene 010 on)
- Only for a word a younger viewer may not know (e.g. STAKEOUT, CARDIO, ALLEGEDLY). A tiny vocabulary lesson, not a caption.
- Never for slang (he uses it wrong on purpose) or everyday words.
- At most one per scene. Shown right after he says the word, about 3.5-4 s, top left under the channel tag, green border.
- The word, its syllables, and a plain meaning of about 8 words a kid understands. Never on screen together with a lesson card.
- Story JSON: {"style": "word", "word": ..., "say": "stake-out", "meaning": ..., "when": t, "until": t}.
