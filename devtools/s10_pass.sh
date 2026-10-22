set -e
S=/tmp/claude-0/-home-user/3ffe6a42-e20c-59ee-a796-ce8de686e5e0/scratchpad
W=$S/s10work; slug=grandpa_ep01_scene010
cp /home/user/blocklab/*.py $W/
cd $S && python3 make_ep01_s010.py $1 > $W/gen.log
cd $W && cp /home/user/blocklab/stories/$slug.json stories/ && cp stories/$slug.json build/story.json
python3 bl_voice.py > vo.log 2>&1
python3 bl_common.py > c.log 2>&1
python3 -c "
import json;d=json.load(open('build/dialogue.json'))
json.dump({l['id']: round(l['end']-l['start'],3) for l in d['lines']}, open('$S/ep01_s010_durations.json','w'))"
tail -3 gen.log | cut -c1-300
