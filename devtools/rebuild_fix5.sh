set -e
S=/tmp/claude-0/-home-user/3ffe6a42-e20c-59ee-a796-ce8de686e5e0/scratchpad
for n in 5; do
  W=$S/s${n}work; slug=grandpa_ep01_scene00$n
  md5sum $W/build/audio/mix.wav > $S/mix_before_$n.md5
  cp /home/user/blocklab/*.py $W/
  cd $W
  cp /home/user/blocklab/stories/$slug.json stories/ && cp stories/$slug.json build/story.json
  cp /home/user/blocklab/frozen/$slug/dialogue.json build/dialogue.json
  ffmpeg -v error -y -i /home/user/blocklab/frozen/$slug/voice.flac -ar 48000 -ac 1 -c:a pcm_s16le build/audio/voice.wav
  python3 bl_common.py > c.log 2>&1
  python3 bl_scene.py > s.log 2>&1
  python3 bl_audio.py > a.log 2>&1
  rm -rf build/draft && python3 render.py --draft --scale 17 --samples 2 > r.log 2>&1
  python3 bl_overlay.py --frames build/draft > o.log 2>&1
  python3 bl_verify.py $slug.mp4 > v.log 2>&1 || true
  echo "scene $n: $(md5sum build/audio/mix.wav | cut -c1-32) vs $(cut -c1-32 $S/mix_before_$n.md5)"
  grep -E "^\[FAIL\]|OVERALL" v.log | cut -c1-200
done
echo ALLDONE
