# Revised Tesla storyboard — continuous 3D direction

Voice B: am_fenrir, synthesis speed 0.8. No static-image sections, music or burned-in narration captions. Timings for unbuilt chapters remain unmeasured.

**Decision:** Send to work pool, or reject with changes. Nothing queues automatically.

## Can smarter planning help older hardware?

**Visual:** Track the moving 3D EV and other road users; introduce the compute question with small source labels, no still plates.

Could smarter software give an older driving computer more breathing room? A Tesla patent published in April twenty twenty-six describes a way to make planning more selective. It organizes possible driving decisions into a graph, scores them, and stops developing branches that are poor choices. That is a useful engineering idea. The patent does not establish that Hardware Three receives every capability of newer cars. Let us separate the mechanism from that promise.

## What Tesla actually disclosed

**Visual:** Build the patent’s goal/interaction structure as an animated spatial graph; keep the citation a supporting label.

The application is called Artificial Intelligence Modeling Techniques for Joint Behavior Planning and Forecasting. Tesla is the named assignee. The method detects nearby agents, stores a hierarchical graph of goals and interactions, evaluates candidate trajectories, and selects a trajectory using scores. Think of the graph as a structured map of possible decisions. Our models and diagrams illustrate the idea; they are not a reconstruction of proprietary Tesla software.

## Why decision time matters

**Visual:** Animate actual 3D vehicle travel against a hypothetical distance/time ruler; keep sensing markers updating.

A driving computer has to keep updating its view of a changing world. A pedestrian takes another step. A truck gets closer. The useful answer has to arrive in time. At forty-five miles per hour, a vehicle travels sixty-six feet each second. In three-tenths of a second, it covers about twenty feet. That arithmetic illustrates why latency matters. It does not mean the vehicle stops sensing while it computes, and it is not a measured Tesla delay.

## How the search grows

**Visual:** Grow a 3D decision tree so its 3, 9 and 27 example sequences become visible in space.

Imagine a simplified planner considering three choices at each stage. After one stage, there are three sequences. After two, nine. After three, twenty-seven. Add more agents and possible reactions, and keeping useful alternatives organized becomes important. These numbers belong to our example, not a Tesla benchmark. The patent describes the processing burden of comparing many potential trajectories and proposes a more structured selection process.

## Start with the driving goal

**Visual:** Use the continuously animated intersection, pedestrian and oncoming vehicles; establish the target lane.

Consider an illustrative left turn. Our vehicle approaches the junction. A pedestrian is near the crossing, an oncoming truck is approaching, and a cyclist is farther to the side. The destination is a lane beyond the turn. That becomes the goal. Rather than displaying every imagined future as an equally important spaghetti line, we can organize the decisions around interactions that affect how the vehicle reaches that goal.

## Build a graph of interactions

**Visual:** Move through a 3D graph while linked candidate choices appear and propagate.

In the patent, a goal layer is followed by layers of interaction nodes. A node represents a possible interaction or non-interaction with an agent. For example, the vehicle might pass before an agent or wait and pass behind. Later choices depend on earlier choices. A path through the graph represents a candidate trajectory. The layers describe decision dependencies. They do not mean that every processor calculation has to run in a single file.

## Relevant does not mean invisible

**Visual:** Animate the cyclist continuously while candidate conflict corridors change; do not erase the road user.

Our cyclist may be outside the immediate turning conflict. That can make the cyclist less relevant to a particular candidate interaction. It does not justify saying the vehicle ignores the cyclist completely or spends zero computation on them. The system still needs to detect agents and respond when the situation changes. In this illustration, the cyclist remains visible. What changes is the candidate relationship we are evaluating, not whether that road user exists.

## Compare choices in context

**Visual:** Animate the yield/wait/left-turn example with rolling/steered wheels and camera tracking.

One candidate might yield to the pedestrian, wait for the truck, then complete the turn. Another might attempt to move earlier. The graph keeps those alternatives connected to their consequences. Our vehicle moves only after the illustrated crossing and opposing lane are clear. This sequence is an explanatory example, not a complete driving policy. The important idea is to compare coherent chains of decisions instead of treating every possibility as unrelated.

## What makes a candidate useful?

**Visual:** Animate scoring signals attached to relevant moving trajectories, with compact labels for the four factors.

The patent describes scores that may account for physics-based constraints, comfort, intervention likelihood, and a human-like discriminator. Physics-related terms help evaluate whether a maneuver satisfies relevant constraints. Comfort can distinguish a smooth turn from an abrupt one. Intervention likelihood concerns whether a human may need or want to take over. Human-like scoring adds another way to evaluate behavior. These are scoring factors, not a guarantee of zero collisions or proof of a fixed three-tier architecture.

## Stop expanding poor branches

**Visual:** Expand and visibly remove low-score 3D branches; retain and develop the selected candidate.

Now we reach pruning. The patent describes comparing node scores with a threshold and removing low-scoring nodes from the graph. A branch involving an undesirable interaction can be removed, while the planner expands more promising alternatives. That can avoid spending resources on trajectories that would not be selected. Our animation removes some example branches, but the patent gives us no basis for labeling this an eighty-percent measured saving. The amount depends on the actual problem and implementation.

## Software efficiency and hardware limits

**Visual:** Animate original compute-module components and changing workload streams; avoid invented benchmarks.

Why does that matter for a compute-limited vehicle? If a planner spends less effort on poor candidates, more of its budget can go toward useful decisions. But the planning method is only one part of the system. Perception, prediction, memory, timing, and the rest of the software also have requirements. Better search can be valuable without proving that two hardware generations become equivalent. A planning patent is not a hardware upgrade certificate.

## A patent is not a rollout announcement

**Visual:** Continue dynamic 3D vehicle/compute context while short labels distinguish patent evidence from product claims.

The document does not identify Hardware Three, version fourteen, or an eighty-percent saving. Those claims need separate evidence from the patent itself. Tesla currently describes Full Self-Driving Supervised as requiring active driver supervision. Its support information says available features vary with hardware, software, region, and vehicle configuration. So an owner should look for verified release information for the actual vehicle. This patent explains a planning technique; it does not settle a feature-parity promise.

## The useful engineering lesson

**Visual:** Follow the EV through the cleared turn while the explanatory 3D graph recedes; finish with the mechanism takeaway.

The useful lesson is selective effort. A planner can organize alternatives, score their consequences, and stop developing branches that are poor choices. That is how smarter search can reduce unnecessary work. Whether it delivers a particular feature on a particular Tesla still needs product evidence. Keep the mechanism and the promise separate, and the engineering becomes much easier to understand.

## Sources

- https://patents.google.com/patent/US20260105614A1/en
- https://www.tesla.com/support/fsd
- Distance/branching arithmetic is illustrative and reproducible, not Tesla performance data.
