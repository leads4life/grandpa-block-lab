# Grandpa's Block Lab

A voxel YouTube series about **Grandpa Tovi**, a lovable first-time streamer with surprising science knowledge, and later his
grandson **Tobias**. Long-form episodes are built from ~30 s scenes; there are Shorts too. Everything is procedural
(Blender + Cycles, original voxel art: no third-party assets) and voiced offline with Kokoro TTS.

## Layout

| Folder | What |
|---|---|
| `bibles/` | **Read first.** Character, World and Production bibles: rules (Rule 1: established elements drive later choices; Rule 2: the stream camera), established facts, approved designs |
| `engine/` | The engine: `bl_common` (plan), `bl_scene` (Blender scene), `bl_perform` (poses, faces, holds), `bl_world`, `bl_audio`, `bl_voice`, `bl_overlay`, `bl_verify` (automated QA), `render.py`, `voxelkit` (Grandpa), `voxelchars` (Tobias, the boar) |
| `engine/generators/` | Scene generators `make_ep01_s00N.py` (write the story JSON, timed to the measured voice), `storykit.py` (auto-framing camera with path, line-of-sight and clutter checks), `make_final_nb.py` (builds the Colab notebook) |
| `engine/tools/` | Check scripts |
| `stories/` | Story JSON for every scene and Short |
| `frozen/` | Approved voice tracks for episode scenes (finals match previews) |
| `notebooks/` | `grandpa_block_lab_FINAL_colab.ipynb`: renders 1920×1080 finals in Colab (Drive saving on) |
| `scenes/ep01_sceneNNN/` | **Backup of each scene**: story JSON, generator, approved voice, continuity JSON, previews, QA report |
| `shorts/` | Finished Shorts |

## Pipeline (per scene)

1. `python3 engine/generators/make_ep01_s00N.py`, then `bl_voice.py`, then the generator again with `--fit` (re-times everything to the real voice).
2. `bl_scene.py` (build), `bl_audio.py`, `render.py --draft --scale 34 --samples 6`, `bl_overlay.py --frames build/draft`, `bl_verify.py <mp4>`.
3. Freeze the approved voice into `frozen/<slug>/`, then rebuild the notebook with `make_final_nb.py`.
4. Final: open the notebook in Colab, set `EXAMPLE`, then Run all.

`build/` (render frames) is regenerated every run and is not tracked.
