# Dev tools (Grandpa's Block Lab)

Helper scripts used while making scenes. Not part of the engine: the render queue never runs these.

| Script | What it does |
|---|---|
| `qrun.py`, `qrun_parts.py` | Sandbox test of the render-queue notebook against a local copy of the repo (checks the plan and mix match the approved preview) |
| `stills.py` | Quick 25% stills of chosen frames, without a full render |
| `read7.py`, `read7fx.py` | Table reads: the voice alone, or the voice with the show's sound effects |
| `s5_probe.py`, `s6*.py`, `s7*.py`, `s8diag.py`, `s9diag.py` | Camera surveys per scene (clear air, framing, line of sight, clutter) |
| `dbg_*.py`, `bbox.py`, `gapprobe.py`, `head.py`, `bench.py` | Debugging probes (clipping, frames, bounding boxes, gaps, timing) |
| `s9_pass.sh`, `rebuild_fix*.sh` | Pipeline runners (voice pass 1, `--fit` pass 2; rebuild and verify fixed scenes) |

Paths inside some scripts point at the old cloud scratchpad; adjust them before reuse.
