# Handoff: an engineering-style explainer engine (new project)

Paste everything below the line into a new Claude Code session that has the `leads4life/grandpa-block-lab` repo attached.

---

I want to build a second video engine for **engineering explainer videos aimed at an older, technical audience**, as a
separate project from my kids' series *Grandpa's Block Lab*. Reuse that series' engine where it fits, but do not change
anything Grandpa's Block Lab depends on.

## Where things are
- Repo: `leads4life/grandpa-block-lab`. The latest work is on branch **`ep01-scene005`** (not `main`); start from it.
- `engine/`: the Block Lab engine. `bl_common` (story JSON → plan), `bl_voice` (Kokoro TTS, two-pass timing),
  `bl_scene` / `bl_world` / `bl_perform` / `bl_cast` (Blender + Cycles scene), `bl_audio` (sfx and mix), `bl_overlay`
  (cards, lower thirds, chat), `bl_verify` (automated QA), `render.py` (draft or final, part rendering via
  FRAME_FROM/FRAME_TO), `engine/generators/storykit.py` (auto-framing cameras with line-of-sight checks),
  `engine/tools/send_to_pool.py` and `engine/generators/make_queue_nb.py` (Colab render queue).
- `voice_system/`: an offline backup of the voice (Kokoro-82M q8 with a `duration` output for lip sync, all 54 voices,
  pinned wheels). Restore with `sh voice_system/setup_voice.sh`. Good explainer voices to audition: `bm_george`,
  `am_michael`, `bm_lewis`, `af_sarah`.
- Blender runs as the Python module `bpy` 5.2.2 (`pip install bpy==5.2.2` if it is missing), with Python 3.13. ffmpeg
  with rubberband is needed.
- `README.md` and `bibles/` explain the Block Lab pipeline and its rules; read them first, for the process.

## What the new engine should look like
- **Technical-drawing style**: clean line art (Blender Freestyle or Line Art), a light blueprint or white-paper look,
  subtle flat or toon shading. Real proportions with smooth parts (gears, shafts, cams, beams, pistons, circuits); no voxels.
- **Explainer tools**: exploded views (parts slide apart and back), cutaways, dimension lines with real units, arrows
  for force, motion and flow, labels that track parts, simple graphs and formulas on screen, slow orbiting cameras.
- **Pacing for adults**: calm, precise narration, one idea at a time, on-screen text held long enough to read. No chat
  overlay, no kid slang.
- 16:9, 1080p, about -14 LUFS, same as Block Lab.

## How to structure it
- A new folder, `explainer/` (its own engine files, generators, stories, bibles), and a **new branch**, e.g.
  `explainer-engine`. Don't edit `engine/` in place; copy what you reuse into `explainer/`, so Block Lab renders stay
  identical.
- Keep the Block Lab workflow: story JSON → voice pass 1 → `--fit` pass 2 → scene → audio → draft render → overlay →
  verify. Adapt `bl_verify` checks to the new style (e.g. labels stay on screen, parts don't intersect).

## First deliverable: a 45-60 s pilot
"How a cam turns rotation into a hammer blow": the water-powered trip hammer from Block Lab Scene 002, redrawn as an
engineering explainer.
1. The waterwheel turns the axle.
2. A cam on the axle lifts the hammer's handle (helve).
3. The cam slips off and the hammer drops under gravity.
4. An exploded view, then reassembled.
5. A one-line takeaway card.

## Working rules (same as my Block Lab sessions)
1. Write a short beat sheet first and wait for my approval before building.
2. After each preview, ask me "Send this to the workflow pool?". If yes: freeze the voice, queue it, verify in the
   sandbox. If no: ask what to change.
3. Back up to GitHub every run, to the working branch, never `main`.
4. Self-review code before running it; report check results honestly, including failures.
