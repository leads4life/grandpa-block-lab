# Episode 1: pre-render audit and director's polish (2026-10-23)

## Engine parity
Every queued scene was rebuilt on today's engine and compared with its approved build.
001–006, 010, 011: identical. 007, 008, 009: differ only by the left wrist (≤ 1 cm).
**Decision:** every scene renders on the exact engine it was approved on (`engines/<hash>/`).

## Face-the-lens (lines Grandpa says to chat), face-on / total lines
| Scene | Before | After | Change |
|---|---|---|---|
| 002 | 1 / 8 | 6 / 8 | front camera on again, count, how, broken |
| 003 | 3 / 10 | 5 / 10 | front camera on rot, stone ("prints" keeps its camera: the hammer helve crossed his chin, and he is looking at the ground) |
| 006 | 11 / 14 | 11 / 14 | unchanged |
| 009 | 9 / 16 | 12 / 16 | front camera on mail/page, spools |
| 005 | 2 / 6 | 2 / 6 | left as approved: its "day one" line is addressed to Tobias |

Lines left on their original cameras are walks, turns of more than 70° (a front camera would whirl), or lines addressed to someone in the scene.
Details: `face_and_geometry_before_fixes.json`, `face_and_geometry_after_fixes.json`.

## Cuts
73 transitions reviewed (`cuts_reviewed.json`). Jump cuts between near-identical framings smoothed into camera moves:
006 at 11.87 s and 23.93 s, 010 at 27.6 s, 011 at 26.47 s.
Time skips 009→010 and 010→011: a 0.6 s dip of the picture to black + "Later that night..." card, added at assembly.

## Re-approval
All six changed scenes came back as previews, were approved by the user, rebuilt from their queue entries and found
byte-identical (story, plan, sound mix) to the approved previews, then queued on main (`a4d3630`, `9370ead`).
Their automatic checks fail only in the categories accepted when each scene was first approved; 003 passes everything.

## Audio
One episode master (`audio_qa_report.json`): −14.2 LUFS, −1.3 dBTP, LRA 3.6, 24,675,200 samples (= 15,422 frames exactly),
0 clipped, dialogue ≥ 8.1 dB over the background, continuous ambience with crossfades at every join (largest 200 ms step at
a join 2.4–3.8 dB, below the natural mid-scene 5.2 dB). Rebuilt from the final scene builds: byte-identical.

## Renderer test (sandbox, tiny resolution, frames 11700–13999 across both time skips)
Killed mid-segment, resumed without re-rendering finished frames; a deliberately damaged frame was detected, deleted and
re-rendered; a changed input marked the finished segment NEEDS_REBUILD; both masters built; every QA check PASS.
