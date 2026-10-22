#!/bin/sh
# Install Grandpa's voice system from this folder alone (no internet needed).
# Puts the model where bl_voice.py expects it, or set KOKORO_MODEL / KOKORO_VOICES to this folder instead.
set -e
D=$(cd "$(dirname "$0")" && pwd)
sha256sum -c "$D/SHA256SUMS"
pip install --no-index --find-links "$D/wheels" kokoro-onnx==0.6.1
mkdir -p /home/user/tts
cp "$D/kokoro-q8-timed.onnx" /home/user/tts/
cp "$D/voices-v1.0.bin" /home/user/tts/voices.bin
python3 -c "from kokoro_onnx import Kokoro; k = Kokoro('/home/user/tts/kokoro-q8-timed.onnx', '/home/user/tts/voices.bin'); a, sr = k.create('Hello, chat.', voice='am_santa', speed=0.95)[:2]; print('voice ok', sr, len(a))"
