# AGREED DECISIONS & LESSONS LEARNED -- read this before every scene

One place for everything already decided, so nothing gets re-argued and no mistake gets made twice.
Settled = settled: change an item only when the user asks. Details live in the other bibles; this is the checklist.
(Compiled 2026-10-22, end of Episode 1. Add to it whenever something new is agreed or learned.)

## 0. Pre-flight checklist (every scene, before the full render)
1. Beat sheet approved by the user before building (table read with sound effects on request).
2. Story checked against STORY-OUTLINE and the bibles (Rule 1: established elements drive choices).
3. Every line to chat: Grandpa is square to the lens (see 4). Check a still of EVERY talking line.
4. Voice pass 1, then `--fit` pass 2. Quick geometric verify (bl_scene + bl_verify) before rendering.
5. Hands free: no map/page/webcam in his hand while he walks or works (pocket + inventory; webcam on the strap).
6. Test stills of every shot before the full render (walls, trees, machine, island edge, props in front of his face).
7. Preview -> ask "Send this to the workflow pool?" (Rule 3). Back up to GitHub (Rule 4).

## 1. Workflow and approvals
- **Rule 1:** established elements drive later choices.
- **Rule 2 (revised 2026-10-23, Episode 2 on):** hands free -- the webcam rides clipped to his overall strap and shows
  LIVE in the inventory hotbar's first slot. (Episode 1: he carried it and set it down to work.)
- **Rule 3:** after each preview ask "Send this to the workflow pool?". Yes = freeze the voice, queue it, verify in the
  sandbox (plan, story and mix byte-identical to the approved preview), publish the queue entry to main. No = ask what to change.
- **Rule 4:** back up to GitHub every run, to the working branch (`ep01-scene005`), never main. Only queue entries go to main.
- Beat sheet first, approval, then build. Previews are draft quality; finals come from the Colab render queue.
- Stitch previews into an episode preview when asked (stream copy, no re-encode).
- Keep working in this session (user: "do not adjust anything keep doing here"); GitHub rendering was only a question.
- Reviewer notes (ChatGPT/Gemini) are input, not orders: check them against the actual video -- they sometimes describe
  things that aren't there.
- Never claim a fix from test stills alone when the user reported it: check frames of the finished video.

## 2. Length and format
- Scenes ~60 s +-10% (the user is OK going over). Long scenes render in ~30-35 s parts in Colab.
- 16:9 1920x1080, 30 fps, -14 LUFS.
- Episode 1 = scenes 001-011, ~8.5 min. Episode 2 onward: lessons lead, a build in every segment (see 3).

## 2b. Shorts (user, 2026-10-24) -- see PRODUCTION-BIBLE "Shorts: built to be watched..."
- Hook at second 0 in the middle of the action; no setup, no countdown, no stage-building (builds: time-lapse <= 2 s).
- Something new every 2-3 s; a cutaway or graphic for every comparison; don't repeat a demo that already proved it.
- End with a playful debate prompt, no end card, no trailing pause; the last line loops into the first frame.
- Pick a world that fits the topic (not the default desert); vary it Short to Short; cutaways on the island, clear of trees.
- A/B: keep A, post B as its own Short; compare "viewed vs swiped away" + "average % viewed" after 48-72 h.

## 3. Story, lessons and episode format
- **Lessons lead; the story serves them.** Lessons can be about anything (Mister Rogers): feelings, nature, weather, safety,
  how things work. **Every segment teaches through a build** (it's Block Lab); one main build + small builds. Rituals excepted.
- Inspirations, for feel only (never their words, songs or trademarks): Dora (journey: map with 3 stops, a stress point at
  each, asking chat/viewers for help), Mister Rogers (calm lessons to camera, feelings named), Bob the Builder (build routine:
  plan, tool line-up, "Ready, chat? Blocks up!", build, test, fix, test).
- "Lessons, not lectures": about one card per scene.
- **Morning Ritual** (from Episode 2): hook first (5-8 s), then "Is this thing on?", coffee, regulars log in (fixed order), greeting.
- **Goodnight Ritual** (every episode end): home with webcam + lantern, lamp on, "Ahh. That's better.", recap card,
  sincere line, signature line ("You don't have to know everything. You just have to keep building." -- provisional),
  chat goodnights (GardenGranny, lurker_77, BoarFan2009, TobiasBuilds last), "Goodnight, chat.", lamp off, after-dark sting,
  lantern out, end card.
- **Mysteries:** the missing blueprint pages; who writes the red-ink pages. **Aliens are Grandpa's theory and are NEVER
  confirmed**; every alien "clue" has a real answer. Episode 2 picks up seconds after Episode 1's "...Aliens. I KNEW it."
- The boar is never harmed (the fence only startles). Scary -> understood -> neighbour. (Episode 2 draft: "he" is a mama.)
- Tension must be kid-safe, and Grandpa models the safe thing to do (back away from mama animals, get off high ground in storms).
- Variety: don't repeat the same device (no second stakeout/alarm right after Scene 010); vary settings, time of day and tone.

## 4. Characters, voice and chat
- Grandpa Tovi: warm, funny, brave-but-nervous. Slang **woven in where the moment calls, always a bit wrong, never in a
  sincere beat**. **"NO CAP, CHAT!"** only at real fear, at most once per stretch of scenes.
- Tobias: an occasional visitor (when his animal knowledge is needed); otherwise in chat as TobiasBuilds (viewer count +1).
- Chat regulars: GardenGranny (pink, "dear"), lurker_77 (grey, one dry word), BoarFan2009 (amber, team boar), TobiasBuilds (green).
  Chat box under the LIVE badge, max 3 messages, ~4.5 s each.
- Voice: Kokoro am_santa at 0.95 (Grandpa). Mispronounced words get a "speak" spelling (e.g. "lives" -> "livs").
  The voice system is backed up in `voice_system/` (offline install, byte-identical output).

## 5. On-screen cards
- **Lesson card** (amber panel, top). Never on screen with a Word Card.
- **Word Card** (green, top left): only words a younger viewer may not know -- a vocabulary micro-lesson. Max one per scene.
  Never slang, never everyday words.
- **Recap card** (Goodnight): builds a line at a time.
- **Slang Check** card: PROPOSED (shows what the slang really means); not yet approved.
- End card at the end of each episode (room for YouTube's end screen).

## 6. Camera and staging (lessons learned)
- **Talking to chat = square to the lens.** Put the talking camera in front of his BODY, and have him look "camera".
  Head-only turns toward a side camera read as "the side of his head" (user complaint, Scene 010).
- **Seated or still: anchor his heading** (`grandpa.hold_heading`, a body:true look covering frame 0). Without it his body
  drifts back toward south in every gap between looks.
- Don't put a prop between him and the talking camera (e.g. the webcam on the laptop): move the camera or the prop.
- No jump cuts between near-identical framings; insert shots are hard cuts; don't cut too often during talking.
- Keep cameras clear of the machine area, trees, fences, the gate and the cabin; use line-of-sight boxes for every blocker.
- **The world is a floating island:** the land ends just north/east of the garden. Keep actors on land; check the island edge.
- Night: lanterns must light the actors (place a lantern near the action; the boar is dark against dark).
- Wide shots when something arrives; close-ups for reactions; a punch-in for the key moment; hold on his face a beat before a reveal.
- Open spaces: the user wants builds in open areas with few trees, and (Episode 2) a bigger landscape.

## 7. Performance and props (lessons learned)
- Holds: start a hold when the hand arrives; leave >= 0.12 s between holds on the same object (the reach window steals time).
- Poses must not fight holds for the same hand. Use the free hand for gestures (e.g. left hand when the laptop is on his right).
- **Seated reach:** his shoulders sit ~0.22 m behind his feet -- hold props 0.1-0.15 m in front of the feet, no further.
- Don't carry objects through furniture: add a waypoint key (e.g. over the laptop screen).
- Standing at a table: stand a step back, then shuffle in as he sits (his legs clip the table edge otherwise).
- Never carry a spinning part's matrix across scenes (wheel, axle, cams); continue the spin from the machine's clock.
- Extras ride on their structure's root: hide a built-later prop's extras with a hold (the solar panel floated from frame 0).

- **Hands free (2026-10-23):** never walk or work with a map/page in hand. Show it to chat (Page Card), fold it, back
  pocket, inventory hotbar; take it out only when needed (`propkit`). The webcam rides on his strap.

## 8. Sound and music
- **Music: SHELVED (user, 2026-10-23)** until the channel shows monetization potential. No music in any episode for now.
  Tested and kept on file: ElevenLabs Music v2.5 (free-credit test: morning theme x2, tension sting; free-tier output is
  not cleared for commercial use -- a paid plan would be needed) and ACE-Step 1.5 (open source, commercial use OK, runs on
  Colab) as the free route. MusicGen is out (non-commercial weights).
- Each scene normalised to -14 LUFS. Scene sound design uses the engine's own procedural sounds.
- Music: **parked** (user, 2026-10-22). Original piano themes exist (`devtools/piano_parked/`); never copy real songs or their
  exact chords (copyright / Content ID). If used: Salamander Grand Piano needs a CC BY credit in the description.

## 9. Engine and pipeline gotchas (lessons learned)
- Voice pass 1 runs bl_voice BEFORE bl_common (the plan needs the dialogue timings).
- `render.py` skips frames that already exist: delete the frames you want re-rendered.
- After bl_overlay, bl_verify can race on the fresh mp4 (ffprobe); re-run verify standalone.
- Inline comments inside list literals have swallowed elements twice: keep comments out of list/dict literals.
- Engine changes must leave older scenes bit-identical: rebuild a queued scene and compare plan/perf md5 after every change.
- Queue entries pin the engine commit; commit the engine before send_to_pool.
- Night lantern lights don't move: place a light where the lantern ends up ("on"/"off" times).
- Cabin interior: the cabin's south side is open; camera bounds must allow the interior (forest clear_air forbids it).

## 10. Parked / decided against / open
- Engine upgrade (rev 4, `ENGINE-ROADMAP.md`): **on hold until Episode 1's final video is finished** (user, 2026-10-22).
- Piano themes: parked. Explainer-engine spin-off: handoff prompt in `handoff/`, a separate project.
- Open: Slang Check card (Episode 2 on?); signature line wording; Episode 2 outline approval; who writes the pages
  (proposed: GardenGranny, his childhood building friend).

## 11. Final production decisions (user, 2026-10-23)
- Final render: **native 1920x1080**, 30 fps, Cycles ~16 samples + adaptive + OpenImageDenoise (high quality); a 4K
  (upscaled, labelled as such) H.264 file for the YouTube upload; an archival master at native 1080p.
- Every scene renders on the exact engine version it was approved on (the per-scene pin), so finals match the previews.
- Episode-level fixes (no re-approval): fade through black + "Later that night..." at 009->010 and 010->011; one continuous
  ambience bed with crossfades at every join; loudness set once for the whole episode (-14 LUFS, -1 dBTP, 48 kHz/24-bit).
- Scene fixes (each comes back as a preview): face-the-lens for chat lines in 002, 003, 005, 009; jump-cut fixes in 006, 010, 011.
- Music: none (parked); the music stem is documented as intentionally empty.
- Render in ~1-minute (1800-frame) segments on one global timeline, with checkpoint/resume on Google Drive (T4).

- Final renderer (`production/`, 2026-10-23): one package ZIP (`GBL_EP01_PRODUCTION.zip`) + Colab notebook. Scenes render on
  their pinned engines; 1800-frame segments with a checkpoint manifest (PENDING/RENDERING/VALIDATING/COMPLETE/FAILED/
  NEEDS_REBUILD) on Drive; frames and segment files are staged (`.partial` -> verified -> renamed); damaged frames are
  detected and re-rendered. Segments: H.264 4:4:4 CRF 12 Rec.709. Masters: archival MKV (1080p, 24-bit PCM) + YouTube MP4
  (4K lanczos upscale, AAC 384k). The time-skip card sits in the upper third (not over Grandpa's face).
- Scene 003 "prints" line keeps its original camera: a front camera there puts the trip-hammer helve across his chin
  (he works facing the machine). Face-the-lens is for lines TO chat, not discovery beats looking at the ground.
