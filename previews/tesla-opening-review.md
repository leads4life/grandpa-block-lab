# Tesla opening preview: review draft

This 15.1-second preview is the actual opening, starting at 00:00. It is a short direction review, not the completed video. Storyboard and preview approval remain pending; nothing is queued automatically.

## Exact narration

> How does a car's computer choose its next move without wasting effort on poor choices? A Tesla patent application describes one approach: score the choices, cut poor branches early, and develop more promising ones. Here's how that search works—and what it actually proves.

The narrator is the selected Kokoro `am_fenrir` voice. Measured delivery is about 178 words per minute, matching the faster delivery the user preferred. There are no burned-in narration captions or music.

## Visual teaching intent

The opening establishes a moving car approaching a junction, then reveals miniature traffic worlds connected as a search tree. Each world represents a conditional alternative: an early turn, creeping forward, or waiting. They are alternative possible states, not simultaneous events or separate physical road branches.

Candidate branches receive different illustrative rankings. The early turn approaches the oncoming route; creeping forward intrudes into the crosswalk. Both models stop before contacting another actor. Those lower-ranked branches disappear; the retained waiting branch develops further alternatives. The teaching purpose is to connect search and pruning to concrete driving choices, while keeping actors and the camera moving. Brief technical labels identify choices and the visible concerns without reproducing the spoken narration.

The models, roads, timing and rankings are original schematic examples. They do not reconstruct Tesla's actual software, proprietary models, hardware or numeric scores. A lower ranking in this scene is not a verified Tesla driving policy. The illustration does not establish measured processing savings, an 80% reduction, Hardware Three feature parity, a V14 rollout, or any deployment or safety guarantee.

## Primary evidence

[US20260105614A1 — Artificial intelligence modeling techniques for joint behavior planning and forecasting](https://patents.google.com/patent/US20260105614A1/en), Tesla Inc., published April 16, 2026. This is a published patent application, not evidence that a product implements the disclosed method.

The application describes a hierarchical graph of goals and interactions, node and trajectory scores, and trajectory selection. Its description explains that a processor can compare node scores with a threshold, remove low-scoring nodes, and expand other higher-scoring nodes to avoid spending resources on trajectories it would not select. Those passages support the opening's scoring, pruning and further-development explanation. They do not establish the particular candidate rankings used in this animation.

The retrieved primary text is preserved in [sources/patent.txt](sources/patent.txt); research qualifications are recorded in [sources/RESEARCH-FINDINGS.md](sources/RESEARCH-FINDINGS.md).

## Decision

After the preview passes internal visual and media checks, the user chooses **Send to work pool** or **Reject with changes**. This document records no approval. Sending the direction to the work pool would authorize the remaining production preparation and review steps; it would not declare the unbuilt full film complete or render-ready.
