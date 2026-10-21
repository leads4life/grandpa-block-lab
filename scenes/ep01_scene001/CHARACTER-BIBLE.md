# CHARACTER BIBLE — Grandpa (Grandpa's Block Lab)

Only established facts. "Engine" = what the renderer can actually do today.

## Look (fixed — never redesign)
- Built by `voxelkit.build_grandpa` from voxel boxes. About 1.1 m tall to the top of his cap (head top 1.06 m).
- Default outfit, used in Episode 1: brown **cap**, **rust** shirt, **denim overalls** with a belt and side pouch, brown boots.
- Face: big white beard and moustache, grey side hair, grey brows, dark eyes on white, pink cheeks, a skin-tone nose block.
- Other outfits exist for Shorts (hard hat, santa, beret, straw, beanie; goggles, scarf, vest, hammer). Episodes keep the default unless the story calls for a change.
- The face rig moves his *existing* face blocks only. The one addition is a hairline-thin skin-coloured eyelid strip, invisible when his eyes are open.

## Voice
- Kokoro TTS, voice **`am_santa`**, speed **0.95**, generated offline. Lines are measured, never sped up to fit.
- Episode scenes freeze the approved voice track (`frozen/<slug>/voice.flac` and `dialogue.json`), so finals match previews exactly.

## Personality (series direction)
- Lovable, warm, vulnerable, clumsy. Sometimes grumpy; sarcastic but never cruel.
- Prone to overconfidence. Complains, with humour, about being old and about streaming.
- Has surprising scientific knowledge and real affection for his viewers.
- Talks like a real streamer talking to his audience. Not a textbook narrator, not a stand-up routine.
- Physicality is age-aware without being stereotypically frail: a deliberate stand-up, a stiff back, careful hands.

## Performance vocabulary the engine supports (`bl_perform.py`)
- **Expressions** (`face`): neutral, squint, raised, surprised, confused, side_eye, smirk, smile, warm, content, worried, relief, wince, alert.
  - Automatic blinks every 2.2–4.8 s when `"blink": true`.
  - Each expression is a mix of channels: brows (raise or furrow, plus per-side), brow tilt (worried or furrowed), eyelids (squint or blink), gaze (pupils), smile (cheeks lift). Channels can be overridden per use with `"set"`.
- **Body poses** (`pose`): seated, lean_in, lean_back, head_shake, nod, shrug, rise, hand_on_back, cap_adjust, present, sip.
  - Stories can define their own poses, e.g. hands on the table, tapping the camera, scooting forward to reach, pushing up from the table.
  - Pose channels: lean, twist, hips offset, head yaw/up/roll, shake, nod, shrug, elbows (lifted out), hand targets (in character space, or relative to an object, with an optional tap).
- **Looking** (`look`): head only (seated), or head and body, with an adjustable turn speed.
- **Holding** (`hold`): one hand carries a structure along a keyed path, which can include "to his mouth". The hand reaches the grip, carries, puts down and lets go. Contact is verified every frame.
- **Existing actions** still work: walk/move (with ladder climbing), build and remove blocks, point, shrug, face_camera, startle.
- **Talking**: the jaw follows the voice; his mouth stays shut between lines (verified).

## Known limits (engine truths)
- Hands are single blocks: no fingers, no finger grips.
- He can't sit and also walk; standing up uses a blend from `seated`, with feet planted.
- Hand-to-table contact can graze up to about 1.5 cm at the moment he presses on or picks something off a surface. The QA report lists every frame where this happens.

## Established story facts (Episode 1)
- This is his **first livestream**. He streams from his log cabin, using a laptop and a **home-made block webcam with a red block on top**. The red block pops off when he taps the camera; he clicks it back on.
- His coffee mug is cream ceramic. Coffee is "the one reliable thing" in his life.
- His back "files complaints" when he stands up.
- At the end of Scene 001 he hears distant clunking from the forest and turns toward the cabin door.
