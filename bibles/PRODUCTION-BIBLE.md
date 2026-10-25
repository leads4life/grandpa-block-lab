# PRODUCTION BIBLE — Grandpa's Block Lab (engine truths)

> **Read `AGREED-DECISIONS-AND-LESSONS.md` first**: every agreed rule and lesson learned, with the pre-flight checklist.

## Rule 1: established elements drive later choices
Once something is on screen or in the soundtrack (a sound, a prop, a line, a rhythm, a number), it constrains every
later choice, and every reveal has to pay off what was set up, measurably:
- **Sounds keep their character and timing**: a sound heard off-screen is the same sound when its source is revealed, on the same beat.
  Example: the Scene 001 clunks (two strikes 0.55 s apart, then silence) set the trip hammer's design in Scene 002: 2 cams 60° apart, one turn every 3.3 s.
- **Props and set dressing stay where the continuity file says**, and they don't change without a reason shown on screen.
- **Story options are proposed together with how they pay off what's established.** Prefer the option that pays off most.

## Rule 2: the stream camera (Grandpa's block webcam)
- **REVISED (user, 2026-10-23; Episode 2 on -- Episode 1 stays as approved):** hands free. Travelling, the webcam rides
  **clipped to his right overall strap** (`propkit.clip_webcam`), and the inventory hotbar's first slot shows it **LIVE**
  (selected slot, pulsing red dot). He no longer walks with it in his hand. He may still set it down on a stump/rock
  for a steady wide view of a build, then clip it back on to leave.
- *(Episode 1 rule, kept for reference:)*
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

## Talking to chat = face the lens (user, 2026-10-22; learned in Scene 010)
- When Grandpa talks to chat, the shot must be square in front of his body and he looks into that camera. A head-only turn
  toward a side camera still reads as "the side of his head".
- Seated (or standing still with head-only looks): add one body:false "look" spanning the whole scene, after a body:true
  look that covers frame 0. Otherwise his body drifts back toward facing south in every gap between looks.
- Check a still of every talking line before the full render.

## The Goodnight Ritual: how every episode ends (user, 2026-10-22; first built in Scene 011)
Same beats, same order, every episode; only the recap and the sting change. Calm pace, no slang.
1. Home: in the cabin door with the webcam (Rule 2) and the lantern; the lamp clicks on. Webcam back on the laptop, lantern on the table.
2. He sits: "Ahh. That's better."
3. "Today we learned..." -- the recap card builds a line at a time (one line per lesson of the episode).
4. One sincere line about the episode's heart (no slang).
5. The signature line, word for word: "You don't have to know everything. You just have to keep building." (provisional; user may change it)
6. Chat says goodnight, always in this order: GardenGranny, lurker_77, BoarFan2009, TobiasBuilds (last).
7. "Goodnight, chat." Click: the lamp goes off; only the lantern glows.
8. The after-dark sting: the episode's mystery hook (kids learn to wait for it). Then he blows out the lantern.
9. End card (room for YouTube's end screen): show title, episode title, "Next time: ...", subscribe.
A matching Morning Ritual opens episodes from Episode 2 (hook first, then "Is this thing on?", coffee, regulars log in, greeting).

## Engine features for these (2026-10-22)
- look "pos": "camera" -- his head looks into whichever camera is live (use for every line to chat).
- grandpa "hold_heading": true -- his body keeps its heading between looks (no drift while seated); "face": [x, y] sets frame 0.
- world "lantern": [{"at", "energy", "on": t, "off": t}, ...] -- outdoor lanterns and lamps that click on/off.
- qa "seated_from": t -- he sits down partway through (seat check starts then).
- cards: "word" (Word Card), "panel" rows that build a line at a time (recap), "end" (end card).
- sfx: switch, blow, drone, owl, snore, spark, zip, fizzle; boar: sniffs, grunts, roots.
- Seated reach: his shoulders sit ~0.22 m behind his feet -- hold props about 0.1-0.15 m in front of the feet ({"char"}), not further.

## Lessons lead; a build in every segment (user, 2026-10-22)
- The story serves the lessons, not the other way round. Lessons can be about anything (Mister Rogers): feelings, nature,
  weather, safety, how things work -- not only engineering.
- It's Block Lab: every segment teaches its lesson THROUGH a build (small and quick is fine). One main build per episode plus
  small builds along the way. The Morning and Goodnight Rituals are the only segments without a build.
- Inspirations (the feel, never their words, songs or trademarks): Dora the Explorer for the journey (a map with three stops,
  a stress point at each, asking chat/viewers for help); Mister Rogers for the lessons (calm, to camera, feelings named);
  Bob the Builder for the building (the same routine: plan, tool line-up, "Ready, chat? Blocks up!", build, test, fix, test).
- Card types: Lesson card (amber), Word Card (green, vocabulary), Slang Check (playful; proposed), recap card (Goodnight).


## Hands free: maps, pages and the inventory (user, 2026-10-23; Episode 2 on)
- **He never walks or works with a map, page or note in his hand** (he needs both hands). The move is always:
  pick it up -> **hold it up to chat** -> the **Page Card** shows it big on screen -> he **folds it** and tucks it in his
  **back pocket** (it rides along with him) -> it **pops into the inventory hotbar**. When he needs it again he
  **takes it out of the pocket** (`propkit.take_out`), uses it, and puts it back.
- **Page Card** (`"style": "page"`): parchment with a fold crease, slides up beside him (right by default), slightly
  tilted; a title, text lines, or a **map** (dashed red route, stops with names, an X, a star, ticks on stops done,
  a bobbing green "you are here" arrow). Never on screen with a Lesson or Word card.
- **Inventory hotbar** (`"style": "inventory"`, Minecraft-style, bottom right, clear of the captions): items pop in
  with their name shown above for a moment; taking one out flashes the slot and lifts it out. Slot 1 = the webcam,
  LIVE. Icons: map, page, webcam, hammer, key, lantern, or a block colour. The build routine's **tool line-up** can
  be items popping into the hotbar. Show it only while he carries things; keep it out of sit-down scenes.
- Engine: a hold key's `"scale"` folds a prop; `"pocket": true` on a hold records it in the continuity file
  (`"pocketed"`), so the next scene starts with it in his pocket. Helpers: `engine/generators/propkit.py`
  (`show_and_pocket`, `take_out`, `clip_webcam`).

## Shorts: built to be watched, rewatched and shared (user, 2026-10-24; from YouTube's feedback on the ant Short)
Shorts follow these on top of the bibles (Grandpa, kindness, kid safety, honest science, face the lens).
1. **Hook in the first 2 seconds, in the middle of the action.** Open on the payoff moment (the drop, the crack, the
   splash) at second 0, then ask "Wait, what? Why did that just happen?". A counterintuitive line beats a question
   setup ("Drop an ant from a plane... nothing happens."). No intro, no title card, no walking into position.
2. **Relentless pacing.** Cut the setup: no countdowns, no building the stage, no getting into position. Every 2-3 s
   something new: a new camera angle, a cutaway, a pop-up graphic, a new fact. Hold on Grandpa only while he says
   something that needs his face. Don't repeat a demo that proved the point already (the ant Short's parachute test).
   Builds in a Short are fast (time-lapse, <= 2 s) or already done; the long-form keeps the full Bob-the-Builder routine.
3. **Show every comparison.** Never leave numbers on a static shot: a quick cutaway or graphic for each one
   (a walking shoe for "walking speed", a block car for "car speed", a falling silhouette for a person).
4. **Shareable utility.** Pick questions people have wondered about but never looked up; explain it so a viewer could
   repeat it at dinner (one idea, one plain sentence, one picture).
5. **A friendly debate prompt at the end** instead of "subscribe": a playful hypothetical on screen
   (e.g. "An elephant with an ant-sized parachute... what happens?"). Comments keep people on the video.
6. **Seamless loop.** No end card and no trailing pause in a Short; the last line runs straight into the first frame
   (last line "...and that's exactly why, when you drop an ant..." -> first frame: the drop). Rewatches count.
7. **A world that fits the topic, varied from Short to Short** (the default is the desert because a story without a
   "world" gets it): ants -> grass meadow; snow science -> snow; water/tides -> beach; city topics -> paris/stone;
   and a time of day / weather that suits it. Cutaway props go on the island (radius ~2.7 m), clear of its trees
   (grass: (-2.0, 0.9), (1.9, -1.2), (-1.6, -1.7)) and out of the main shots' view; hide them after their shot.
8. **A/B testing.** Keep the original (A) up; post the new cut (B) as its own Short with its own title; after 48-72 h
   compare "Viewed vs. swiped away" and "Average percentage viewed" in YouTube Studio, and keep what wins as the
   template. (YouTube's built-in Test & Compare only tests titles/thumbnails, not the video itself.)

## Captions: one set only (user, 2026-10-25; new builds from the raccoon episode on)
- **Long episodes (16:9): no captions burned into the picture.** The story sets `"captions": "srt"`; `bl_overlay.py` then
  draws none and writes `<slug>.srt` beside the MP4 (exact text and timings from the voice, names spelled right, other
  speakers labelled e.g. `TOBIAS:`). Upload that file in YouTube Studio → Subtitles. It beats auto-captions (words like
  "dexterous" come out right), viewers can turn it on or off, and it never collides with the Word Cards, Page Card,
  chat or hotbar. Only one caption set ever shows.
- **Shorts (9:16): keep burned-in captions** (unset, or `"captions": "burned"`). Most Shorts are watched muted, and the
  big captions hold attention. Do not upload an .srt for a Short (that would make two sets).
- Unset means `"burned"`, so every older scene rebuilds byte-identical.
- Episode 1 is already rendered with burned-in captions: upload no caption file for it.

## Face the lens, automatically (rev 4, 2026-10-25)
- Pipeline step after `bl_scene.py`: `bl_lens.py --fix`, then `bl_common.py` + `bl_scene.py` again, then `bl_lens.py`.
  It measures, frame by frame, the angle between where his face points and the lens on every chat line (limit 45 deg
  median). For each side-on line it adds a camera square in front of his body (clear air by ray tests, his framing
  points in the picture, nothing between lens and face) and a look into the lens. Report: `build/lens.json`.
- A line is a chat line unless it has `"who"`, `"to": "<name>"` (talking to someone in the scene) or `"lens": false`
  with a `"why"`. `bl_verify` (engine_rev >= 4) fails every side-on chat line and every `"lens": false` with no reason.
- When it says **restage**, rewrite the moment: he stops walking to say the line, or turns to chat first. Lines he says
  while walking into a wall can't be shot face-on (first tested on Ep 1 Scene 002: 3/8 face-on became 7/8 in one pass).

## Standing authorization: Raccoon Lift episode (user, 2026-10-25)
"I authorize you to finish all scenes that you create in our plan." For the standalone episode "Grandpa vs. the Raccoon
Bandits: The Water-Balance Lift", Scenes 02-10: Claude writes each script from the approved beat sheet, builds it,
reviews the contact sheet itself, renders the preview, and on passing every check (no accepted fails) freezes the voice,
queues it, verifies the queue entry is identical to the preview and pushes the queue entry to main -- without waiting for
approval at each gate. Scripts, contact sheets and previews are still sent to the user as they are made; the user can stop,
redirect or reopen any scene. Creative choices outside the beat sheet take the conservative option and are logged in
scenes/raccoon_lift/DECISIONS.md. This authorization covers this episode only.
