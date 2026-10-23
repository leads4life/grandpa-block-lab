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

## Rev 4 additions: "bake it all in" (user, 2026-10-23, after Episode 1)
Episode 1 stays as approved (it renders on its pinned engines). All of this is for Episode 2 on.
1. **Automatic face-the-lens**: every line addressed to chat gets a camera in front of his body + a look into the lens,
   built in (the `face_patch` logic as the default), and a bl_verify check that fails any chat line seen side-on/back.
2. **Fix at the source, not "accepted fails"**: collision-aware holds and staging so hand grazes and props in front of
   his face don't happen; accepted_fails should be empty by default and need a written reason.
3. **Music**: original score per scene -- a theme under the Morning/Goodnight rituals, light tension stings at the
   stress points, quiet beds under builds; mixed under dialogue (ducked), never over a lesson line. Source: see
   music decision (ElevenLabs Music / Video-to-Music, or an open model on Colab). The piano experiment did not land.
4. **Less talk, more show**: fewer lines per scene; reaction shots, hands-on building, silences where the picture tells it.
5. **Bigger world**: open landscape beyond the island edge for Episode 2's journey (distance, new places, the map's stops).
6. **Approve before preview**: a contact sheet of every talking line + the camera plan for the user, before any preview render.
7. **YouTube package**: hook in the first 5-8 s, chapters, thumbnail, end screen to the next episode.
Done already (2026-10-23): hands free -- Page Card, inventory hotbar, fold-and-pocket, webcam on the strap.
