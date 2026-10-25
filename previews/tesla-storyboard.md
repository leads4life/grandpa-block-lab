# Tesla video: revised storyboard

**Status:** Source-backed editorial revision. First chapter is being previewed; remaining timings are not yet measured.

Voice: am_michael. Narrator only. No music or burned-in narration captions. Original illustrative 3D props plus technical diagrams.

## Review decision

After viewing the first preview: **Send to work pool** to approve the direction, or **Reject** with specific changes. Nothing queues automatically.

## Chapters

### Can smarter planning help older hardware?

**Visual:** 3D EV approaches a crosswalk; reveal a generic compute module. Introduce the question without a hardware-parity promise.

Could smarter software give an older driving computer more breathing room? A Tesla patent published in April twenty twenty-six describes a way to make planning more selective. It organizes possible driving decisions into a graph, scores them, and stops developing branches that are poor choices. That is a useful engineering idea. The patent does not establish that Hardware Three receives every capability of newer cars. Let us separate the mechanism from that promise.

### What Tesla actually disclosed

**Visual:** Original patent-title card and 3D decision graph. Show the genuine identifier and publication date.

The application is called Artificial Intelligence Modeling Techniques for Joint Behavior Planning and Forecasting. Tesla is the named assignee. The method detects nearby agents, stores a hierarchical graph of goals and interactions, evaluates candidate trajectories, and selects a trajectory using scores. Think of the graph as a structured map of possible decisions. Our models and diagrams illustrate the idea; they are not a reconstruction of proprietary Tesla software.

### Why decision time matters

**Visual:** Illustrative distance ruler and continuously updating perception markers. Label 0.3 s as a hypothetical interval, not Tesla telemetry.

A driving computer has to keep updating its view of a changing world. A pedestrian takes another step. A truck gets closer. The useful answer has to arrive in time. At forty-five miles per hour, a vehicle travels sixty-six feet each second. In three-tenths of a second, it covers about twenty feet. That arithmetic illustrates why latency matters. It does not mean the vehicle stops sensing while it computes, and it is not a measured Tesla delay.

### How the search grows

**Visual:** Animate three-choice branching: 3, 9, 27. Explicit example labels; no invented benchmark.

Imagine a simplified planner considering three choices at each stage. After one stage, there are three sequences. After two, nine. After three, twenty-seven. Add more agents and possible reactions, and keeping useful alternatives organized becomes important. These numbers belong to our example, not a Tesla benchmark. The patent describes the processing burden of comparing many potential trajectories and proposes a more structured selection process.

### Start with the driving goal

**Visual:** Original 3D intersection, pedestrian, truck and cyclist. Establish the turn destination.

Consider an illustrative left turn. Our vehicle approaches the junction. A pedestrian is near the crossing, an oncoming truck is approaching, and a cyclist is farther to the side. The destination is a lane beyond the turn. That becomes the goal. Rather than displaying every imagined future as an equally important spaghetti line, we can organize the decisions around interactions that affect how the vehicle reaches that goal.

### Build a graph of interactions

**Visual:** Goal and interaction layers; multiple coherent candidate paths remain visible.

In the patent, a goal layer is followed by layers of interaction nodes. A node represents a possible interaction or non-interaction with an agent. For example, the vehicle might pass before an agent or wait and pass behind. Later choices depend on earlier choices. A path through the graph represents a candidate trajectory. The layers describe decision dependencies. They do not mean that every processor calculation has to run in a single file.

### Relevant does not mean invisible

**Visual:** Keep cyclist visible while highlighting the current conflict corridor; no zero-FLOPS claim.

Our cyclist may be outside the immediate turning conflict. That can make the cyclist less relevant to a particular candidate interaction. It does not justify saying the vehicle ignores the cyclist completely or spends zero computation on them. The system still needs to detect agents and respond when the situation changes. In this illustration, the cyclist remains visible. What changes is the candidate relationship we are evaluating, not whether that road user exists.

### Compare choices in context

**Visual:** Show yield/wait/turn as one illustrative candidate sequence; compare another alternative.

One candidate might yield to the pedestrian, wait for the truck, then complete the turn. Another might attempt to move earlier. The graph keeps those alternatives connected to their consequences. Our vehicle moves only after the illustrated crossing and opposing lane are clear. This sequence is an explanatory example, not a complete driving policy. The important idea is to compare coherent chains of decisions instead of treating every possibility as unrelated.

### What makes a candidate useful?

**Visual:** Four scoring factors: physics, comfort, intervention likelihood, human-like evaluation.

The patent describes scores that may account for physics-based constraints, comfort, intervention likelihood, and a human-like discriminator. Physics-related terms help evaluate whether a maneuver satisfies relevant constraints. Comfort can distinguish a smooth turn from an abrupt one. Intervention likelihood concerns whether a human may need or want to take over. Human-like scoring adds another way to evaluate behavior. These are scoring factors, not a guarantee of zero collisions or proof of a fixed three-tier architecture.

### Stop expanding poor branches

**Visual:** Prune poor-scoring example branches, preserving useful alternatives. No 80% performance number.

Now we reach pruning. The patent describes comparing node scores with a threshold and removing low-scoring nodes from the graph. A branch involving an undesirable interaction can be removed, while the planner expands more promising alternatives. That can avoid spending resources on trajectories that would not be selected. Our animation removes some example branches, but the patent gives us no basis for labeling this an eighty-percent measured saving. The amount depends on the actual problem and implementation.

### Software efficiency and hardware limits

**Visual:** Generic compute module with distinct perception/prediction/planning workloads, without invented hardware equivalence.

Why does that matter for a compute-limited vehicle? If a planner spends less effort on poor candidates, more of its budget can go toward useful decisions. But the planning method is only one part of the system. Perception, prediction, memory, timing, and the rest of the software also have requirements. Better search can be valuable without proving that two hardware generations become equivalent. A planning patent is not a hardware upgrade certificate.

### A patent is not a rollout announcement

**Visual:** Separate a patent application from release evidence; accurately state supervised-use status.

The document does not identify Hardware Three, version fourteen, or an eighty-percent saving. Those claims need separate evidence from the patent itself. Tesla currently describes Full Self-Driving Supervised as requiring active driver supervision. Its support information says available features vary with hardware, software, region, and vehicle configuration. So an owner should look for verified release information for the actual vehicle. This patent explains a planning technique; it does not settle a feature-parity promise.

### The useful engineering lesson

**Visual:** Return to the intersection and recap selective computation. No unsupported upgrade promise or nonexistent next-video link.

The useful lesson is selective effort. A planner can organize alternatives, score their consequences, and stop developing branches that are poor choices. That is how smarter search can reduce unnecessary work. Whether it delivers a particular feature on a particular Tesla still needs product evidence. Keep the mechanism and the promise separate, and the engineering becomes much easier to understand.

## Primary sources

- Tesla patent application: https://patents.google.com/patent/US20260105614A1/en
- Tesla FSD (Supervised) documentation: https://www.tesla.com/support/fsd
- Distance and branching figures are reproducible illustrative arithmetic, not Tesla performance measurements.
