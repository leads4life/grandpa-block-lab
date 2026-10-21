# QA REPORT — Episode 1, Scene 001 "Is This Thing On?"

## What was produced, and what wasn't
- **Done here:**
  - `grandpa_ep01_scene001_PREVIEW.mp4`: 640×360, 16:9, 30 fps, 33.00 s, AAC audio. Encoded from the 1920×1080 overlaid master, whose 3-D frames were rendered at 34 % (652×367), Cycles, 6 samples plus denoise.
  - the scene JSON, the continuity state, this report, the three bibles, and the FINAL Colab notebook.
- **Not done here:** `grandpa_ep01_scene001_FINAL.mp4` (1920×1080) **does not exist yet**. Colab produces it when you run `grandpa_block_lab_FINAL_colab.ipynb`.

## Inputs checked
| Input named in the brief | Status |
|---|---|
| `grandpa_block_lab_colab (5).ipynb` | **Not supplied.** Used the current engine and notebook from this project instead (`grandpa_block_lab_colab.ipynb`, the latest sent). |
| `lock_key.json` | Present. Used as the format reference and regression test. |
| `grandpa_ep01_part_01_colab_ready.json` | **Not present.** The scene JSON was built from scratch. |
| ElevenLabs | Not used, by your decision. Grandpa's established voice is offline Kokoro `am_santa`, speed 0.95. |

## Dialogue and timing (measured, not assumed)
- **Script**: all 7 lines of dialogue from the brief, word for word, plus the agreed cliffhanger "...What was that?". Nothing was trimmed, at your direction ("ok if you go over by 10 %, don't remove").
- **Split lines**: lines were split at sentence breaks into 14 voice clips, so every gesture keys to a measured timestamp.
- **Measured speech**: 27.52 s. Scene length **33.00 s** (target 30 s, within the agreed +10 %).
  - The fit came from tightening pauses and beat spacing only. The voice is never sped up.
- **Approved voice frozen**: the voice track and timings are embedded in the Colab notebook (`frozen/grandpa_ep01_scene001/`). In a sandbox run of the notebook, the plan came out identical: same frames, lines, actions and mouth curve.

## Automated checks (executed: `bl_verify.py` on the preview build and MP4) — 72 PASS, 1 FAIL
| Area | Result |
|---|---|
| Structures, blocks, grid, blocks hold still | PASS |
| Chair slides back as scripted; the camera block flies on its true arc | PASS, error 0.0000 |
| Grandpa in frame every frame (hat, face, chest; face only during the opening close-up) | PASS: 0 frames out, closest 5.9 % from the edge |
| Right hand on the camera block while carrying it (4.2–5.4 s) | PASS: largest gap 0.0 mm |
| Left hand on the mug while carrying it (20.7–27.3 s) | PASS: largest gap 0.0 mm |
| Mug rests on the table at the end; block back on the webcam | PASS: gap 0.3 mm / 0.4 mm |
| Sitting on the seat (hip joint 4.5–8 cm above it) | PASS: 5.6–6.4 cm |
| Each of the 18 expression cues actually moves the face | PASS (18 of 18) |
| Mouth moves on all 14 clips, closed between them | PASS |
| Continuity file matches the last frame | PASS |
| Length 30 s, −10 % to +10 % | PASS: 33.00 s |
| MP4 (master): 1920×1080 H.264 yuv420p 30 fps, AAC, full length | PASS: 990 frames |
| Loudness / peaks | PASS: −14.3 LUFS, peak −2.0 dBFS |
| **No black bars**: picture at all 4 edges, 12 frames sampled | PASS |
| **Mesh clipping into furniture (8 mm tolerance)** | **FAIL: 4 of 330 sampled frames, deepest 1.4 cm** |

- **The clipping failure, in detail:**
  - Frame 129 (4.3 s): fingers on the table top as he picks the red block up.
  - Frames around 850 (28.3 s): hands pressing the table edge as he pushes himself up.
  - Both are deliberate contact moments where the block hand sinks slightly into the table. Earlier rounds fixed elbows, the mug against his beard, the arm against the mug, and the pelvis against the table (291 sampled frames → 4).
  - **Unresolved.** Fixing it properly needs hand IK that aims at the palm instead of the wrist (planned engine change).

## Visual review (executed: stills plus 6 motion strips of 6 frames each, from the MP4)
- **Fixed during review**, then re-rendered and re-checked:
  1. A tall black monitor read as a pillar and hid him at the end. Replaced with a low laptop with his block webcam stacked on top.
  2. The opening webcam close-up was too close (only part of his face). Pulled back.
  3. The camera pull-back passed through props. It now rises above everything.
  4. A light leak line between wall logs. The log rows now overlap.
  5. He stood up while still holding the mug. Re-sequenced: mug down, then rise.
  6. During "...What was that?" the laptop and webcam hid his face. He now steps back toward the door, and the camera swings round to his front-left.
  7. The camera skimmed his cap at about 3.9 s. Softened.
- **Accepted, minor:**
  - About 0.2 s at 3.85 s where the top of the frame is mostly cap, as he lurches toward the lens right after the block pops. It reads as part of the gag.
  - At 31.5–31.7 s the red webcam block briefly overlaps his beard while the camera swings. His face is clear from 31.8 s, through "...What was that?" to the last frame.
- **Re-render splice check**: the re-rendered ranges (frames 0–160 and 862–989) join the rest invisibly. Difference at the joins is 0.13–0.8 out of 255, against 1.5 for normal motion.

## Audio (executed: per-stem waveform with event markers, loudness via ffmpeg ebur128)
- **Foley on its action**: every sound lands on its action. The sounds are: taps ×2, block clatter, block click-on, mug clink ×2, sip, slosh, chair creak and scrape, wooden footsteps ×2, LIVE blip at the viewer join, and the distant clunk ×2.
- **Ambience**: cabin room tone, muffled outdoor birds and the wall clock run the whole scene. The voice is kept at least 9 dB above the bed while he talks.

## Regression (executed)
- `lock_key` (looping Short) was rebuilt from scratch with the new engine in an isolated copy and checked against its MP4: **all 105 checks pass**. These include the loop seam, the in-frame check and loudness. Vertical 1080×1920 Shorts mode is intact.
- Blinking is opt-in (`"blink": true`), so older stories animate exactly as before.

## Frozen for the final
- Scene JSON, voice track (FLAC) and timings, seed 11, 30 fps, camera keys in the JSON.
- Engine version `69c1f49176c7`: SHA-1 of the engine files, ignoring a missing final newline. The notebook prints it in section 1.
- Continuity state: `grandpa_ep01_scene001_continuity.json`.
  - Grandpa standing at (-0.42, 0.52), facing the door (yaw -94°), alert expression.
  - Mug on the table; chair pushed back 0.16 m.
  - 4 viewers; camera key target (-0.75, 0.55, 0.9), az -100, el 11, dist 2.6.

## Not verified here (planned / unverifiable locally)
- The full-resolution 1920×1080 render itself (Colab). The notebook was executed here up to the render step, with the local Blender module standing in.
- Exact T4 render time. The estimate is 45–75 min, scaled from local CPU timings.
- Scene-to-scene assembly: loudness continuity and the clock-tick phase across segments. Noted as next steps in PRODUCTION-BIBLE.md.
