# Grandpa's Block Lab: Episode 1 "The Boar Next Door": production package

This folder is everything needed to render the final episode. Nothing else has to be downloaded except Blender (the notebook does that).

## How to run it (Google Colab, T4 GPU)
1. Open `GBL_EP01_FINAL_RENDER.ipynb` in Colab (File → Upload notebook).
2. Runtime → Change runtime type → **T4 GPU**. Runtime → **Run all**.
3. Step 1 shows a **Choose Files** button: pick `GBL_EP01_PRODUCTION.zip` from your computer. The notebook keeps it in
   Google Drive (`MyDrive/block_lab/final/`), so later sessions don't ask again.
4. When a session ends (Colab limits), open it again and **Run all**. It carries on where it stopped.
5. When step 8 says **RESULT: PASS**, upload `masters/GBL_EP01_The_Boar_Next_Door_YOUTUBE_4K_UPSCALED_from1080p.mp4` to YouTube.

Expect a total render time of roughly 10–18 hours on a T4 (step 4 measures your GPU and prints its own estimate). The time
is spread over a few sessions. Google Drive needs about 10 GB free while rendering.

## What comes out (`MyDrive/block_lab/final/masters/`)
| File | What it is |
|---|---|
| `*_ARCHIVAL_MASTER_1080p30_444_PCM24.mkv` | Keep forever. Native 1920×1080, 30 fps, H.264 4:4:4 visually lossless (CRF 12), Rec.709, 24-bit PCM audio |
| `*_YOUTUBE_4K_UPSCALED_from1080p.mp4` | For upload. 3840×2160 lanczos **upscale** of the 1080p render, H.264 High, AAC-LC 384 kb/s 48 kHz, fast start |
| `AUDIO/*_final_mix.wav` + `dialogue / sfx / ambience` | 48 kHz / 24-bit stems; the final mix is −14 LUFS, ≤ −1 dBTP |
| `AUDIO/*_music_NONE.txt` | There is no music stem: music is parked for Episode 1 |
| `QA/final_qa_report.md/.json` | Every automatic check, PASS/FAIL |

Why 4K for YouTube when the render is 1080p: YouTube gives 4K uploads its better codec (VP9/AV1) and a higher bitrate,
so even viewers watching at 1080p see a cleaner picture. The file name says it is upscaled; it is not a native 4K render.

## How the render is organised
* **One global timeline**: 11 scenes, 15,422 frames (8:34.07). `episode.json` lists every scene's start frame, engine and checksums.
* **Every scene renders on the exact engine version it was approved on** (`engines/<hash>/`, checked against the
  approval hash before anything runs), so the final matches the approved previews.
* **Segments of 1,800 frames (1 minute)**. Each segment goes PENDING → RENDERING → VALIDATING → COMPLETE, recorded in
  `work/manifest.json`. A segment that keeps failing becomes FAILED (re-run with `--retry-failed`); a finished segment whose
  file disappears or is damaged, or whose scene changes, becomes NEEDS_REBUILD and is rendered again automatically.
* **Safe staging**: frames are written as `.partial` and renamed when complete; segment files are encoded locally,
  checked (frame count, size, Rec.709 tags, a full decode), copied to Drive as `.partial`, checksum-verified, then renamed.
* **Render settings** (`config/render_settings.json`): Cycles 16 samples + adaptive sampling + OpenImageDenoise
  (high quality, accurate prefilter), OptiX on the GPU. Glitch-black frames are detected and re-rendered.
* **Episode transitions** (added at assembly; no scene changed): a 0.6 s dip of the camera picture to black with a
  "Later that night..." card at the two time skips (009→010, 010→011). The LIVE badge and chat stay up, as on a real stream.
* **Audio**: one episode master made from every scene's own sound (`audio_master/`, lossless FLAC, decoded to WAV
  bit-exactly at the end): one continuous ambience bed with crossfades at every join, dialogue cleaned (de-ess,
  gentle compression) and kept ≥ 8 dB above the background, loudness set once for the whole episode. See
  `audio_master/audio_qa_report.json`.

## Folder map
| Folder | Contents |
|---|---|
| `episode.json` | the global timeline (scene order, frames, start frames, engines, transitions, checksums) |
| `scenes/<id>/` | approved story, dialogue, frozen voice (`voice.flac`), queue manifest (and `frozen/` remembered lines) |
| `engines/<hash>/` | the engine files each scene was approved on |
| `audio_master/` | final mix + dialogue/sfx/ambience stems (FLAC 24-bit) + audio QA report |
| `config/` | render settings, dependencies, the package recipe |
| `tools/` | `gbl_final.py` (validate, prepare, benchmark, render, status, assemble, qa) and its helpers |
| `notebook/` | the Colab notebook |
| `fonts/` | DejaVu Sans (the overlay font) |
| `QA/audit/` | the pre-render audit: face-the-lens, cuts, joins, audio, engine parity |
| `CHECKSUMS.sha256` | sha256 of every file (checked by step 1) |

## Running without Colab
Any Linux machine with an NVIDIA GPU, Blender 5.2 and ffmpeg:
```
python3 tools/gbl_final.py validate --pkg .
python3 tools/gbl_final.py render   --pkg . --work WORK --blender /path/to/blender
python3 tools/gbl_final.py assemble --pkg . --work WORK --out MASTERS
python3 tools/gbl_final.py qa       --pkg . --work WORK --out MASTERS
```
