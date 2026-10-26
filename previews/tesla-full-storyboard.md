# Full-film production storyboard

User: go ahead and send to pool and run the entire process, look is ok dress it up more on blank canvas going forward

Measured runtime: 309.6 seconds. The approved opening is reused byte-for-byte.

## 1. Opening

How does a car's computer choose its next move without wasting effort on poor choices? A Tesla patent application describes one approach: score the choices, cut poor branches early, and develop more promising ones. Here's how that search works—and what it actually proves.

Moving 3D scene: opening. Duration: 15.10s.

## 2. What Tesla disclosed

The application is called Artificial Intelligence Modeling Techniques for Joint Behavior Planning and Forecasting. Tesla is the named assignee. The method detects nearby agents, stores a hierarchical graph of goals and interactions, evaluates candidate trajectories, and selects a trajectory using scores. Think of the graph as a structured map of possible decisions. Our models and diagrams illustrate the idea; they are not a reconstruction of proprietary Tesla software.

Moving 3D scene: graph. Duration: 24.03s.

## 3. Why decision time matters

A driving computer has to keep updating its view of a changing world. A pedestrian takes another step. A vehicle gets closer. The useful answer has to arrive in time. At forty-five miles per hour, a vehicle travels sixty-six feet each second. In three-tenths of a second, it covers about twenty feet. That arithmetic illustrates why latency matters. It does not mean the vehicle stops sensing while it computes, and it is not a measured Tesla delay.

Moving 3D scene: latency. Duration: 27.13s.

## 4. How search grows

Imagine a simplified planner considering three choices at each stage. After one stage, there are three sequences. After two, nine. After three, twenty-seven. Add more agents and possible reactions, and keeping useful alternatives organized becomes important. These numbers belong to our example, not a Tesla benchmark. The patent describes the processing burden of comparing many potential trajectories and proposes a more structured selection process.

Moving 3D scene: growth. Duration: 22.30s.

## 5. Start with a goal

Consider an illustrative left turn. Our vehicle approaches the junction. A pedestrian is near the crossing, an oncoming vehicle is approaching, and a cyclist is farther to the side. The destination is a lane beyond the turn. That becomes the goal. Rather than displaying every imagined future as an equally important spaghetti line, we can organize the decisions around interactions that affect how the vehicle reaches that goal.

Moving 3D scene: traffic. Duration: 22.77s.

## 6. Layers of interaction

In the patent, a goal layer is followed by layers of interaction nodes. A node represents a possible interaction or non-interaction with an agent. For example, the vehicle might pass before an agent or wait and pass behind. Later choices depend on earlier choices. A path through the graph represents a candidate trajectory. The layers describe decision dependencies. They do not mean that every processor calculation has to run in a single file.

Moving 3D scene: layers. Duration: 25.20s.

## 7. Relevant agents remain visible

Our cyclist may be outside the immediate turning conflict. That can make the cyclist less relevant to a particular candidate interaction. It does not justify saying the vehicle ignores the cyclist completely or spends zero computation on them. The system still needs to detect agents and respond when the situation changes. In this illustration, the cyclist remains visible. What changes is the candidate relationship we are evaluating, not whether that road user exists.

Moving 3D scene: attention. Duration: 25.27s.

## 8. Compare coherent choices

One candidate might yield to the pedestrian, wait for the vehicle, then complete the turn. Another might attempt to move earlier. The graph keeps those alternatives connected to their consequences. Our vehicle moves only after the illustrated crossing and opposing lane are clear. This sequence is an explanatory example, not a complete driving policy. The important idea is to compare coherent chains of decisions instead of treating every possibility as unrelated.

Moving 3D scene: traffic. Duration: 23.70s.

## 9. What scores can consider

The patent describes scores that may account for physics-based constraints, comfort, intervention likelihood, and a human-like discriminator. Physics-related terms help evaluate whether a maneuver satisfies relevant constraints. Comfort can distinguish a smooth turn from an abrupt one. Intervention likelihood concerns whether a human may need or want to take over. Human-like scoring adds another way to evaluate behavior. These are scoring factors, not a guarantee of zero collisions or proof of a fixed three-tier architecture.

Moving 3D scene: scores. Duration: 26.47s.

## 10. Prune poor branches

Now we reach pruning. The patent describes comparing node scores with a threshold and removing low-scoring nodes from the graph. A branch involving an undesirable interaction can be removed, while the planner expands more promising alternatives. That can avoid spending resources on trajectories that would not be selected. Our animation removes some example branches, but the patent gives us no basis for labeling this an eighty-percent measured saving. The amount depends on the actual problem and implementation.

Moving 3D scene: pruning. Duration: 26.77s.

## 11. Efficiency and hardware limits

Why does that matter for a compute-limited vehicle? If a planner spends less effort on poor candidates, more of its budget can go toward useful decisions. But the planning method is only one part of the system. Perception, prediction, memory, timing, and the rest of the software also have requirements. Better search can be valuable without proving that two hardware generations become equivalent. A planning patent is not a hardware upgrade certificate.

Moving 3D scene: compute. Duration: 24.27s.

## 12. Application versus deployment

The document does not identify Hardware Three, version fourteen, or an eighty-percent saving. Those claims need separate evidence from the patent itself. Tesla currently describes Full Self-Driving Supervised as requiring active driver supervision. Its support information says available features vary with hardware, software, region, and vehicle configuration. So an owner should look for verified release information for the actual vehicle. This patent explains a planning technique; it does not settle a feature-parity promise.

Moving 3D scene: evidence. Duration: 25.97s.

## 13. Selective effort

The useful lesson is selective effort. A planner can organize alternatives, score their consequences, and stop developing branches that are poor choices. That is how smarter search can reduce unnecessary work. Whether it delivers a particular feature on a particular Tesla still needs product evidence. Keep the mechanism and the promise separate, and the engineering becomes much easier to understand.

Moving 3D scene: graph. Duration: 20.63s.
