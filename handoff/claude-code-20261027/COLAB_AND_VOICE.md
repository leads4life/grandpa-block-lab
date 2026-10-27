# Colab, JSON, voice and required files

Upload this complete ZIP to Tesla_Claude_Handoff_Colab.ipynb. It extracts repository/, verifies the original v2 frozen source/voice hashes, installs the render-only runtime, tests the actual selected device and can regenerate all base-v2 chapters. No video files are included. Expect full rendering, not instant stitching. Actual Google Colab/GPU execution is untested here; notebook syntax and local source/voice integrity were checked.

The master JSON is repository/explainer/projects/tesla-hw3/build/full-v2/tesla-project-v2.json. The original plan, latest corrected re-cut draft, all bibles, renderer/prop source, audits and other project metadata are also included. Historical JSON paths referring to MP4s are provenance; those files are deliberately absent.

Actual frozen v1/v2 speech WAVs and the current v3 opening speech are included, together with voice metadata/settings and offline Kokoro engine code. Voice B is am_fenrir. Rebuilding base v2 uses the included speech without voice weights or an AI API key. A revised script needs new speech; documented upstream Kokoro weights are runtime dependencies, not bundled here. No music or narration captions.

A base-v2 render uses its original camera. The delivered final had an isolated r8 camera correction. Read handoff/PROJECT_STATE.md, repository/explainer/progress_media/final_camera_repair.py and final_camera_occlusion_repair.py. A portable assembly helper is in handoff/tools/assemble_v2_camera_repair.py; read it before use. Those helpers regenerate47 native frames and one near-plane visibility correction, then preserve original main audio while replacing the chapter. They do not claim final visual review. A new premium re-cut should author its own clean cameras and coherent frozen version rather than silently inheriting or bypassing source checks.

The proposed corrected v3/v4 film is NOT implemented by the base-v2 notebook. Claude must audit the written information and source, create the revised complete producer/assets/narration and build a matching new notebook/package for that final. Do not present the existing test opening as that new final.
