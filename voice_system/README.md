# Voice system backup

Everything needed to make Grandpa's (and Tobias's) voice, kept here so it never depends on outside downloads.

| File | What it is |
|---|---|
| `kokoro-q8-timed.onnx` | Kokoro-82M v1.0, 8-bit, plus one extra output (`duration`) used for lip sync. Apache-2.0. |
| `voices-v1.0.bin` | All 54 Kokoro voices. Grandpa is `am_santa` at speed 0.95; Tobias's settings are in `engine/bl_voice.py` (CAST). |
| `wheels/` | The exact Python packages (kokoro-onnx 0.6.1, onnxruntime 1.29.0, espeakng-loader 0.2.4, phonemizer 3.4.0, ...), for Python 3.13 on Linux x86-64. |
| `setup_voice.sh` | Checks the hashes, installs offline, copies the model to `/home/user/tts/`, and speaks a test line. |
| `make_timed_model.py` | How the timed model was made from the public one, if it ever has to be rebuilt. |
| `SHA256SUMS` | Hashes of every file here. |

Restore: `sh voice_system/setup_voice.sh`

Approved scenes don't need this at all: their voices are frozen in `frozen/<scene>/voice.flac`, and the render queue uses those.
The voice sound also depends on ffmpeg with rubberband (Tobias's voice effect), which comes with the system ffmpeg.
