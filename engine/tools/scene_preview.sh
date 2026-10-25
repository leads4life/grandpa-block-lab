#!/bin/sh
# After the contact sheet is approved (or self-reviewed under a standing authorization): the preview video.
#   draft render (Episode 1 preview quality) -> overlays + sound -> MP4 (+ .srt) -> full checks
#   sh scene_preview.sh WORKDIR SLUG
set -e
W=$1; SLUG=$2
cd "$W"
rm -rf build/draft
python3 render.py --draft --scale 34 --samples 6 > render.log 2>&1
python3 bl_overlay.py --frames build/draft > overlay.log 2>&1
python3 bl_verify.py > verify_final.log 2>&1 || true
grep "^\[FAIL\]\|OVERALL" verify_final.log; ls -la "$SLUG.mp4" "$SLUG.srt" 2>/dev/null | awk '{print $5, $9}'
