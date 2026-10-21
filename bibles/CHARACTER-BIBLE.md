# CHARACTER BIBLE — Grandpa Tovi (Grandpa's Block Lab)

**Names (user, 2026-10-21):** Grandpa is **Grandpa Tovi**. His grandson is **Tobias**.

## Tobias (design APPROVED 2026-10-21; first appears in Scene 004)
- Grandpa Tovi's elementary-school-aged grandson. **Size (user-approved 2026-10-21): the larger version**, about 0.83 m to the top of his bucket hat, around Grandpa's chest. (A smaller 0.62 m version was tried and rejected.) Design: `voxelchars.build_tobias`, sheet `bibles/DESIGN_tobias_and_boar.png`. Intelligent, observant, fascinated by animals. Studies animal behaviour, instincts and characteristics.
- He often knows more about animals than Grandpa, and turns up unexpectedly just when his knowledge is needed.
- **Calm confidence**, a deliberate contrast to Grandpa's panic.
- **Voice (user-picked "G4", 2026-10-21)**: Grandpa's own voice (Kokoro `am_santa`), made a young kid's: speed 1.12, tone ×1.33 (a smaller voice box), pitch ×1.203 on top (so ×1.60 in all), high-pass 150 Hz. About 270–300 Hz.
  - Defined once in `bl_voice.CAST["tobias"]`. A story line with `"who": "tobias"` uses it, and his jaw follows only his own lines (`dialogue.json` gains `mouths`).
  - Lines without `who` are Grandpa, exactly as before (verified: Scene 003's voice rebuilds bit-identical).
- **Story role**: he secretly fixed the trip hammer (tiny boot prints, new planks). Probably the 4th viewer.

Only established facts. "Engine" = what the renderer can actually do today.

## Look (fixed — never redesign)
- Built by `voxelkit.build_grandpa` from voxel boxes. About 1.1 m tall to the top of his cap (head top 1.06 m).
- Default outfit, used in Episode 1: brown **cap**, **rust** shirt, **denim overalls** with a belt and side pouch, brown boots.
- Face: big white beard and moustache, grey side hair, grey brows, dark eyes on white, pink cheeks, a skin-tone nose block.
- Other outfits exist for Shorts (hard hat, santa, beret, straw, beanie; goggles, scarf, vest, hammer). Episodes keep the default unless the story calls for a change.
- The face rig moves his *existing* face blocks only. The one addition is a hairline-thin skin-coloured eyelid strip, invisible when his eyes are open.

## Running gag: Grandpa's slang
- Now and then, **at most once per scene**, he tries new-generation slang and **gets it a bit wrong**: aimed at the wrong thing (calling a tree "bruh"), or with the wrong meaning ("no cap" while touching his cap, "slay" about a sandwich).
- He's proud of himself every time, and it's warm, never mean.
- **Fear catchphrase: "NO CAP, CHAT!"** (user-defined recurring trait).
  - He blurts it only when he is **genuinely scared**, especially around boars.
  - It's his own slang gag, separate from the once-per-scene rule above, but rarer: **only at real moments of fear, at most once in a scene, and not in most scenes**, so it stays funny. A fear scene may chain the two: casual slang causes the trouble, then panic slang.
  - **The performance** (engine vocabulary):
    - Confident face (`smirk` / `smile`) snaps to `surprised` (eyes wide).
    - He **freezes**: a hold pose, no head motion. Then he blurts the line fast and high.
  - **First use, planned for the boar encounter:**
    1. He looks at the boar and casually says "You kinda bussin'!"
    2. The boar gets agitated: it snorts, stomps its hooves and lowers its head to charge.
    3. His confidence turns instantly to panic. He freezes, eyes wide: "NO CAP, CHAT!"
- **So far:**
  - Scene 002: "Chat, I'm going AFK. That's away from keyboard. You're coming with me." (He's AFK and takes everyone along.)
  - Scene 003: "...Don't forget to subscribe... bruh." Said to a tree after the rabbit has hopped behind it.

## Voice
- Kokoro TTS, voice **`am_santa`**, speed **0.95**, generated offline. Lines are measured, never sped up to fit.
- Episode scenes freeze the approved voice track (`frozen/<slug>/voice.flac` and `dialogue.json`), so finals match previews exactly.

## Personality (series direction)
- Lovable, warm, vulnerable, clumsy. Sometimes grumpy; sarcastic but never cruel.
- **Impulsive.** He uses Gen Z slang at unexpected moments, especially when **frightened or impressed** ("No cap, chat!" when scared; "a thousand aura points!" when impressed).
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
- **Looking** (`look`): head only (seated), or head and body, with an adjustable turn speed. It can follow a moving object (`obj`). While walking with `"face": "path"`, his body faces where he's going and his head looks elsewhere.
- **Holding** (`hold`): one hand carries a structure along a keyed path, which can include "to his mouth" or `{"char": ...}`, which is carried in front of him and turns with him. The hand reaches the grip, carries, puts down and lets go. Contact is verified every frame.
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
- **Scene 002**:
  - He takes his block webcam (red block and all) off the laptop and carries it, talking into it ("If I'm not back in five minutes... avenge me.").
  - He walks out to the stream and works out the machine from its rhythm.
  - He names it ("A trip hammer!") and explains cams.
  - He ends facing us, holding the webcam, alert: "...so who fixed it?"
  - He is standing at about (-3.84, 0.80), by the new post, **still holding the webcam** (right hand).
- **Scene 003 opens** with him setting the webcam down so he can work with both hands (Production Bible, Rule 2).
- **Scene 003**:
  - He sets the webcam on a bank stone, then replaces the rotten post with a stone footing and a new post (micro-lesson: wet wood + fungi = rot; stone keeps the post dry).
  - He greets a rabbit ("Morning!"), asks it to subscribe, then says "bruh" to the tree it vanished behind.
  - He finds tiny boot prints: "Rabbits don't fix machines."

## Tobias: a recurring character, not a constant one (user, 2026-10-21)
- He appears when his animal knowledge or his deadpan is needed, then **leaves gracefully**, always for a real reason that
  is already part of the story: homework or a school night (he's in elementary school), checking his garden fence,
  dinner, the school bus.
- Episodes centre on Grandpa: his builds, his commentary, his chat.

## Grandpa's boar worry (planned from Scene 006)
- He isn't over the boar. Now and then a small grey **memory cloud** pops up over his head: a mini voxel boar snorting at
  him, replaying the "You kinda bussin'!" moment. It always comes at the worst moment.
- It's played for warm laughs. The real point is a feelings beat in his own voice: being scared is normal, and building
  something helps.

## Scene 006 (preview)
- Alone after Tobias leaves, his worry speaks first: "Alone. In the woods. Where the boar... lives." That sets off the memory
  cloud: the real "You kinda bussin'!" echoes three times, and he dreamily murmurs it along with it. Then "Nope. Nope nope nope."
- He learns he designed the trip hammer years ago: "I built that? ...I built that! Why'd I ever stop?" Tobias: "You stopped
  building. So I started."
- **Episode 1, Scenes 007–010 (user, 2026-10-21)**: Grandpa streams alone. Tobias is an occasional visitor and does not appear (not even in chat).
