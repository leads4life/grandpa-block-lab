# ENGINE ROADMAP -- the next upgrade (engine_rev 4)

Goal: build the show's format into the engine, so every episode follows it by default and bl_verify checks it.

## 1. Episode format in the story JSON
- New top-level "segments": [{"id", "t0", "t1", "kind": "ritual_morning" | "stop" | "build" | "night" | "ritual_goodnight",
  "lesson": {"title", "line", "type": "lesson" | "word" | "feelings" | "safety"}, "build": ["structure names"], "map_stop": n}].
- bl_verify checks: every non-ritual segment has a lesson AND at least one structure built during it; at most one Word Card
  per scene; lesson/Word Card never overlap; talking-to-chat lines use look "camera".

## 2. Ritual templates (generators, reused every episode)
- storykit.morning_ritual(...): cold-open hook slot, "Is this thing on?", coffee, regulars log in (fixed order), greeting.
- storykit.goodnight_ritual(...): cabin set, webcam home, lantern, "Ahh", recap card from the episode's segments,
  sincere line, signature line, chat goodnights (fixed order), lamp off, sting slot, lantern out, end card.

## 3. New cards (bl_overlay)
- "map": the episode map with its stops, checked off as he goes (Dora-style).
- "slang": Slang Check (what it really means vs. how Grandpa used it).
- "connection_lost": the stream freezes/breaks up, viewer count drops, chat panics.
- "chat_prompt": Grandpa asks chat/viewers a question; a short pause; answers pop in.

## 4. Build routine helpers (Bob-the-Builder feel)
- storykit.build_routine(plan, tools, steps, test, mistake, fix): tool line-up shot, "Ready, chat? Blocks up!", step builds,
  test, the mistake, the fix, test again.

## 5. World
- "valley" terrain: rolling voxel hills, a ridge, lake, far mountains as layered backdrops, atmospheric haze; multiple
  locations joined by walking cuts.
- Storm weather with lightning flashes (light before thunder sound, timed).
- Boar piglets (scaled boar, follow-the-mother path).

## 6. Already in (rev 3, 2026-10-22)
look "camera"; grandpa hold_heading/face; outdoor lanterns and lamps on/off; Word Cards; recap panel rows; end card;
qa seated_from; boar sniffs/grunts/roots; sfx owl/snore/spark/drone/switch/blow/zip/fizzle.
