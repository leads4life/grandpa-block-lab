# Tesla planning explainer — corrected re-cut storyboard

Draft for review. The supplied audit is an unverified editorial reference, not an authority for technical claims. Existing finished videos remain intact.

## Direction

Hardware stakes first; show combinatorial growth before revealing the graph, make pruning a sharp visible consequence, and resolve the hardware question with evidence. Preserve the selected narrator near 179wpm, continuously moving 3D, restrained mechanical cues, no music and no narration captions. Target about 4:15–4:45 only if measured narration warrants it. The clean environment remains the default; the gritty urban test is a separate direction choice.

Full draft: **755 spoken words**. Approximate continuous speech at 179wpm: **253.1s**, before natural pauses. All scene times below are editorial targets, not measured locks.

## S1: The hardware question (0:00–0:35)

### Narration (101 words)

Can smarter software give an older driving computer a second life? That's the Hardware Three question. A smarter search can reduce wasted work. That alone doesn't prove an upgrade. Look at this intersection. Our car could turn, creep forward, or wait. Each choice opens more choices, and developing every branch takes work. The useful trick is to stop developing a poor option before it grows into a whole family of bad options. Tesla's planning patent describes a way to do that. Follow one turn, and we'll separate that engineering idea from the much bigger claim that old hardware has been saved.

### Moving visual sequence

- 0–5s: Moving generic processor close-up, then hardware-versus-search split. Labels MORE HARDWARE? / LESS SEARCH?; no real HW3/AI4 specification comparison, utilization meter, capacity line or overloaded-chip effect.
- 5–13s: Street-level tracking reveals the pedestrian, bicycle and opposing car. Cut to three candidate actions tied to the same scene.
- 13–24s: Brief preview of a scored branch stopping while the remaining branch develops. Road users remain visibly represented. First useful answer is early rejection of further expansion.
- 24–35s: Return to the question over the moving street scene; label DISCLOSURE ≠ DEPLOYMENT briefly, then hand off to branching.

**Hook and reward:** Hardware question → visible unnecessary branch expansion → promise to distinguish search efficiency from hardware eligibility.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## S2: The combinatorial trap (0:35–1:15)

### Narration (118 words)

Start with three possible actions. Give each action three follow-up choices and there are nine sequences. Add one more stage: twenty-seven. Add another: eighty-one. Nothing at a single step became complicated. The combinations did the growing. Those counts belong to our teaching example, not Tesla's software. Now add road users whose actions change which choices make sense. Turning before a crossing pedestrian is different from waiting and turning behind them. Draw every hypothetical future and the screen quickly becomes a tangled web. The problem is deciding where more exploration is useful. It isn't evidence that this particular bottleneck causes phantom braking, or that every current driving system searches this way. So how can the planner organize that web?

### Moving visual sequence

- Grow a counted three-way tree: 3 → 9 → 27 → 81 complete sequences. Pair each count with the actual visible combinatorial stage. Technical banner THE COMBINATORIAL TRAP.
- Use amber/cyan interaction links around actual road users; red marks an explicitly poor candidate, not a dangerous person.
- Camera moves from street-level interaction to a frontal spatial tree; do not add steering jerk, phantom-braking diagnosis, 45mph driving footage or fake latency meters.

**Hook and reward:** Why branches multiply → actual 3^n example → need a representation tied to a driving goal.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## S3: Reveal the goal and linked interactions (1:15–2:05)

### Narration (133 words)

Tesla's application describes a hierarchical nodal graph. Think of a graph as linked choices, arranged in layers. Start with a goal: reach the lane beyond the turn. Then connect possible interactions that could lead there. Pass in front of another road user, or wait and pass behind them. An interaction in one layer changes which later choices are available. Following those links produces a candidate trajectory: one possible way our car could move through the situation. That is different from drawing an isolated line and calling it a plan. The graphic is our simplified explanation, not a display taken from Tesla's software. And organizing the choices is only the beginning. To decide which branches deserve more work, the system needs a way to evaluate them. Watch what happens when one candidate scores poorly.

### Moving visual sequence

- Controlled wipe separates the tangled teaching example from a layered graph. Onscreen identifier US20260105614A1, source DOCUMENTED APPLICATION. Do not fabricate a patent figure or rename the method Sequential Nodal Graph.
- Goal pin appears in the actual destination lane; visible leader connects it to the goal layer.
- Trace before/after interaction alternatives and then one linked candidate. Use a street inset to preserve the physical meaning of the graph.

**Hook and reward:** Tangled alternatives → goal and dependent interactions → clear meaning of a candidate trajectory.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## S4: Prune the candidate, keep the road user (2:05–2:55)

### Narration (149 words)

The patent describes comparing node scores with a threshold. A node below that threshold can be removed, or marked so it isn't expanded further. Here is the payoff: its descendants don't keep multiplying while more promising candidates receive further development. We make the rejected branch snap out of the teaching model so the change is easy to see. But notice the cyclist. They're still on the road, still moving, and still represented in our illustration. Removing an option from a search is different from erasing a person from the world. We cannot label that person ignored or claim they cost zero computation. The processor has already done work to detect the situation and evaluate candidates. The potential saving comes from avoiding more work on poor continuations. It doesn't mean a branch was rejected before any processor ever touched it. Which raises the next question: what makes an option poor?

### Moving visual sequence

- Make the threshold decision readable before removal: candidate amber/red → node rejected → its further expansion stops. Mechanical cut and short debris-free graphic separation, not arbitrary lasers or an 80% destruction count.
- Cyclist retains material/color and motion; supporting label ROAD USER STILL REPRESENTED. Two-column comparison CANDIDATE REMOVED / ROAD USER REMAINS.
- Keep the physical street context visible during pruning and show the promising branch extending at least one further layer. No numerical savings or FLOPS badges.

**Hook and reward:** Poor node → halted expansion → visible distinction between search choices and road users.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## S5: Four evaluation factors (2:55–3:45)

### Narration (145 words)

Avoiding a collision is one consideration. It doesn't automatically make a maneuver comfortable or sensible. Compare two illustrative cars covering the same distance in the same time. One changes speed abruptly; the other changes it more gradually. The patent lists factors including physics-based constraints, comfort, intervention likelihood, and a human-like discriminator. That last term asks, in effect, whether a human driver would make a similar decision. Intervention likelihood concerns the prospect of a person taking over. Those are four considerations, not a documented three-tier panic detector. We don't have Tesla's actual weights, thresholds, or production scores, so our graphics won't invent them. The motion comparison simply makes the idea of comfort visible. Scores can guide which nodes are expanded and which are stopped. A planner can therefore spend its search effort more selectively without proving anything about the capabilities of a particular generation of computer.

### Moving visual sequence

- Build a layered, four-part physical evaluation assembly: PHYSICS / COMFORT / INTERVENTION / HUMAN-LIKE BEHAVIOR. No vertical ordering implying guaranteed priority or actual software architecture.
- Match cuts to equal-distance/time abrupt versus gradual motion. Labels describe behavior; no invented G-force numbers, panic meter, numeric weights or zero-collision guarantee.
- Return one evaluated candidate to the graph; the score-to-threshold decision, not decoration, triggers its continuation.

**Hook and reward:** Safe-looking path → differing behavior quality → named evaluation considerations that guide expansion.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## S6: The verdict and final turn (3:45–~4:30)

### Narration (109 words)

Back to the chip. Selective search can stop developing poor candidates. It isn't proof that Hardware Three can run a newer feature, that version fourteen has shipped to those vehicles, or that computation fell by eighty percent. Planning also sits alongside perception, prediction, memory, and timing requirements. Tesla says its Full Self-Driving Supervised features require active driver supervision, and availability depends on the vehicle's hardware and software. With the crossing and opposing lane clear, our car completes the illustrated turn. The lesson isn't to ignore more of the world. It's to organize the choices and stop developing poor ones. Judge a hardware promise by evidence for your actual vehicle.

### Moving visual sequence

- Rejoin physical processor and spatial graph without a capacity bar or fabricated successful HW3 deployment. Useful comparison: LESS SEARCH WORK? / VEHICLE ELIGIBILITY REQUIRES EVIDENCE.
- Vehicle completes the same turn with clear sightlines, wheel detail and destination-lane payoff. Apply the prior roof/close-camera obstruction checks.
- No link to an unbuilt driving-mode video. Last moving shot may reserve space for a real end-screen destination if supplied later; no held-card padding.

**Hook and reward:** Potential method benefit → boundary of hardware evidence → payoff of the original driving situation.

**Audio:** Selected am_fenrir narrator near 179 wpm; restrained action-linked mechanical clicks only; no music, alarms, bass drops or narration captions.

## Production gates

Measure and freeze narration, fit reveals to actual spoken events, create a short internally checked moving preview, then collect current-version storyboard and preview decisions before full production. No approval is implied by this document. No YouTube publication.

## Sources

- Tesla-assigned patent application [US20260105614A1](https://patents.google.com/patent/US20260105614A1/en), retained text reviewed for graph structure, scoring and pruning.
- [Tesla FSD support](https://www.tesla.com/support/fsd): supervision and hardware/software-dependent feature availability.
- 3^n arithmetic is an explicit teaching example, not a benchmark. No basis is claimed for four million owners, two years, zero FLOPS, hardware parity, actual latency or 80% savings.
