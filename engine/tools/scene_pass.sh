#!/bin/sh
# One scene, end to end, up to the approval sheet (rev 4 order):
#   generator --fit -> voice -> build -> face the lens (fix + rebuild if needed) -> sound -> checks -> contact sheet
#   sh scene_pass.sh GENERATOR.py SLUG WORKDIR
set -e
GEN=$1; SLUG=$2; W=$3
ENGINE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$W/build" "$W/stories"
cp "$ENGINE"/*.py "$ENGINE"/tools/contact_sheet.py "$W/"
python3 "$GEN" --fit > "$W/gen.log"
cp /home/user/blocklab/stories/$SLUG.json "$W/build/story.json"
cd "$W"
python3 bl_voice.py > vo.log 2>&1
python3 bl_scene.py > scene.log 2>&1
python3 bl_lens.py --fix > lens.log 2>&1
if grep -q "story updated" lens.log; then
    python3 bl_common.py > c.log 2>&1; python3 bl_scene.py > scene.log 2>&1; python3 bl_lens.py > lens.log 2>&1
fi
python3 bl_audio.py > audio.log 2>&1
python3 bl_verify.py > verify.log 2>&1 || true
rm -rf build/contact
python3 contact_sheet.py build "$W/contact.png" > sheet.log 2>&1
grep "face-the-lens" lens.log; grep "^\[FAIL\]" verify.log || true; tail -1 sheet.log
