"""Episode audio master: one continuous, dialogue-first soundtrack for a whole episode, from each scene's own stems.

    python3 episode_audio.py EPISODE_AUDIO.json OUT_DIR

EPISODE_AUDIO.json: {"fps": 30, "scenes": [{"id", "build_dir", "frames", "environment"}, ...],
                     "joins": {"<id>": {"crossfade_s": 1.2}}}      (joins keyed by the scene AFTER the join)
Each build_dir is a scene's engine build (build/audio/stem_build|stem_fx|stem_ambience.wav, voice.wav; build/story.json;
build/dialogue.json), made by bl_audio.py exactly as for the approved previews.

What it does (agreed 2026-10-23), in order:
1. Rebuilds every scene's bed with the engine's own balance (0.8 build + 0.9 fx + 0.12 ambience, 30 Hz high-pass) and its
   dialogue lift (each line >= 9 dB over the ducked bed) -- but WITHOUT the per-scene loudness normalisation, which is what
   made the background jump at every join.
2. Ambience: levels matched within each environment (cabin day, forest day, forest night, cabin night), and an equal-power
   crossfade across every join (the outgoing bed continues under the incoming one), so it never restarts.
3. Dialogue: line levels evened out across the episode (lines more than 2 dB from the median are brought to within 2 dB;
   shouted/whispered performance kept), then gentle polish: 70 Hz high-pass, light de-essing, 2:1 compression.
4. Ducking under dialogue, one loudness pass for the whole episode: -14 LUFS integrated, -1 dBTP ceiling.
5. Writes 48 kHz 24-bit WAVs: final_mix, dialogue, sfx, ambience (stems at their final gains; they sum to the mix before
   the limiter), and audio_qa_report.json.  No music in Episode 1 (decision 2026-10-22): no music file is written.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import butter, sosfilt

SR = 48000


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "highpass", fs=SR, output="sos"), x)


def read(path):
    sr, x = wav.read(path)
    assert sr == SR, (path, sr)
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x / 32768.0


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def write24(path, x):
    """Lossless 48 kHz 24-bit stereo WAV (via ffmpeg, from float)."""
    x = np.asarray(x, dtype=np.float32)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    wav.write(tmp, SR, st)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:a", "pcm_s24le", "-ar", str(SR), path], check=True)
    os.remove(tmp)


def loudness(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    summ = p[p.rindex("Summary:"):]
    get = lambda key: float(summ.split(key)[1].split()[0])
    return dict(integrated_lufs=get("I:"), lra=get("LRA:"), true_peak_dbtp=get("Peak:"))


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    fps = cfg.get("fps", 30); spf = SR // fps
    scenes = cfg["scenes"]
    total = sum(s["frames"] for s in scenes) * spf
    E = {k: np.zeros(total) for k in ("sfx", "amb", "voice", "bed")}
    qa = dict(scenes=[], joins=[], lines=[])
    lines_all = []
    pos = 0
    amb_parts = []
    for s in scenes:
        a = os.path.join(s["build_dir"], "build", "audio")
        n = s["frames"] * spf
        st = {k: read(os.path.join(a, "stem_%s.wav" % k)) / 0.7 for k in ("build", "fx", "ambience")}   # back to the engine's norm()
        for k in st:
            st[k] = np.pad(st[k], (0, max(0, n - len(st[k]))))[:n]
        v = read(os.path.join(a, "voice.wav")); v = np.pad(v, (0, max(0, n - len(v))))[:n]
        sfx = 0.8 * st["build"] + 0.9 * st["fx"]
        amb = 0.12 * st["ambience"]
        amb_parts.append((s, pos, n, amb))
        story = json.load(open(os.path.join(s["build_dir"], "build", "story.json")))
        who = {l["id"]: l.get("who") for l in story["lines"]}
        dl = json.load(open(os.path.join(s["build_dir"], "build", "dialogue.json")))["lines"]
        E["sfx"][pos:pos + n] = sfx
        E["voice"][pos:pos + n] = v
        for l in dl:
            lines_all.append(dict(scene=s["id"], id=l["id"], who=who.get(l["id"]) or "grandpa",
                                  a=pos + int(l["start"] * SR), z=pos + int(l["end"] * SR)))
        qa["scenes"].append(dict(id=s["id"], start_frame=pos // spf, frames=s["frames"], start_s=round(pos / SR, 4)))
        pos += n
    # 2. ambience: match levels within each environment, then crossfade across every join
    groups = {}
    for s, p0, n, amb in amb_parts:
        groups.setdefault(s["environment"], []).append(rms_db(amb))
    for s, p0, n, amb in amb_parts:
        target = float(np.median(groups[s["environment"]]))
        g = float(np.clip(target - rms_db(amb), -6, 6))
        E["amb"][p0:p0 + n] = amb * 10 ** (g / 20)
    for (sa, pa, na, _), (sb, pb, nb, _) in zip(amb_parts, amb_parts[1:]):
        L = int(cfg.get("joins", {}).get(sb["id"], {}).get("crossfade_s", 1.0) * SR)
        L = min(L, na // 2, nb // 2)
        T = pb
        A_tail, B_head = E["amb"][T - L:T].copy(), E["amb"][T:T + L].copy()
        w = np.linspace(0, np.pi / 2, 2 * L)
        A_ext = np.concatenate([A_tail, A_tail[::-1]])               # the outgoing bed carries on (mirrored noise)
        B_ext = np.concatenate([B_head[::-1], B_head])               # the incoming bed fades up under it
        E["amb"][T - L:T + L] = A_ext * np.cos(w) + B_ext * np.sin(w)
        qa["joins"].append(dict(before=sa["id"], after=sb["id"], crossfade_s=round(2 * L / SR, 2)))
    bed = hp(E["sfx"] + E["amb"], 30)
    # 1. dialogue lift (engine rule) + 3. even line levels across the episode
    # 3. dialogue: even the VOICE itself across the episode (each line to within 2 dB of the median; no clarity is lost here --
    #    clarity is guaranteed below by lowering the background, never by pushing a line into the limiter)
    lv = [rms_db(E["voice"][l["a"]:l["z"]]) for l in lines_all]
    med = float(np.median(lv))
    for l, d in zip(lines_all, lv):
        g = (med + 2) - d if d > med + 2 else ((med - 2) - d if d < med - 2 else 0.0)
        E["voice"][l["a"]:l["z"]] *= 10 ** (g / 20)
        l["evened_db"] = g
    # gentle dialogue polish (ffmpeg): 70 Hz high-pass, light de-essing, 2:1 compression
    tmp = tempfile.mkdtemp()
    write24(os.path.join(tmp, "v.wav"), E["voice"] * 0.5)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "v.wav"), "-af",
                    "highpass=f=70,deesser=i=0.3:m=0.5:f=0.5,acompressor=threshold=-24dB:ratio=2:attack=8:release=160:makeup=1",
                    "-c:a", "pcm_f32le", os.path.join(tmp, "vp.wav")], check=True)
    sr_, vp = wav.read(os.path.join(tmp, "vp.wav")); vp = vp.astype(np.float64).mean(axis=1)[:total] / 0.5
    vp = np.pad(vp, (0, total - len(vp)))
    # 4. the background ducks under every line (engine: -6 dB), and further where needed so each line sits >= 9 dB over it
    active = lp((np.abs(vp) > 0.02).astype(float), 3)
    duck = 1 - 0.5 * np.clip(active / max(1e-9, active.max()), 0, 1)
    sfx_f, amb_f = hp(E["sfx"], 30) * duck, hp(E["amb"], 30) * duck
    extra = np.ones(total); ramp = int(0.12 * SR); pad = int(0.15 * SR)
    for l in lines_all:
        a, z = l["a"], l["z"]
        short = 9.0 - (rms_db(vp[a:z]) - rms_db(sfx_f[a:z] + amb_f[a:z]))
        l["extra_duck_db"] = 0.0
        if short > 0:
            depth = min(short, 12.0); l["extra_duck_db"] = round(-depth, 1)
            a0, z0 = max(0, a - pad - ramp), min(total, z + pad + ramp)
            env = np.ones(z0 - a0); r_ = min(ramp, len(env) // 2)
            env[:r_] = np.linspace(0, 1, r_); env[-r_:] = np.linspace(1, 0, r_)
            extra[a0:z0] = np.minimum(extra[a0:z0], 1 - (1 - 10 ** (-depth / 20)) * env)
    sfx_f *= extra; amb_f *= extra
    # 5. loudness: one gain for the whole episode; the loudest effect hits are tamed in the EFFECTS stem only (gentle
    #    compression + a ceiling 6 dB under the final one), so the final limiter is only a safety net and dialogue is untouched
    ceil = 10 ** (-1.5 / 20)
    sfx_l = sfx_f.copy()
    for _ in range(3):
        pre = sfx_l + amb_f + vp
        k = 0.5 / np.abs(pre).max()
        write24(os.path.join(tmp, "pre.wav"), pre * k)
        gain_db = -14.0 - loudness(os.path.join(tmp, "pre.wav"))["integrated_lufs"]
        G = k * 10 ** (gain_db / 20)
        write24(os.path.join(tmp, "fx_in.wav"), sfx_f * G / ceil * 0.5)          # 0.5 here == the final ceiling
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "fx_in.wav"), "-af",
                        "acompressor=threshold=-14dB:ratio=3:attack=2:release=90:makeup=1,alimiter=limit=0.25:attack=1:release=60:level=false:latency=1",
                        "-c:a", "pcm_f32le", os.path.join(tmp, "fx_out.wav")], check=True)
        sr_, fo = wav.read(os.path.join(tmp, "fx_out.wav")); fo = fo.astype(np.float64).mean(axis=1)[:total]
        sfx_l = np.pad(fo, (0, total - len(fo))) / 0.5 * ceil / G
    pre = sfx_l + amb_f + vp
    k = 0.5 / np.abs(pre).max()
    write24(os.path.join(tmp, "pre.wav"), pre * k)
    gain_db = -14.0 - loudness(os.path.join(tmp, "pre.wav"))["integrated_lufs"]
    final = os.path.join(out, "final_mix.wav")
    for _ in range(4):                                           # settle on -14 LUFS through the safety limiter
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "pre.wav"), "-af",
                        "volume=%.3fdB,alimiter=limit=%.4f:attack=3:release=80:level=false:latency=1" % (gain_db, ceil),
                        "-c:a", "pcm_s24le", "-ar", str(SR), final], check=True)
        m = loudness(final)
        if abs(m["integrated_lufs"] + 14.0) < 0.2:
            break
        gain_db += -14.0 - m["integrated_lufs"]
    g = k * 10 ** (gain_db / 20)
    sp = max(np.abs(vp).max(), np.abs(sfx_l).max(), np.abs(amb_f).max()) * g
    trim = min(1.0, 0.98 / sp)                                   # stems are pre-limiter: one shared trim keeps them unclipped
    write24(os.path.join(out, "dialogue.wav"), vp * g * trim)
    write24(os.path.join(out, "sfx.wav"), sfx_l * g * trim)
    write24(os.path.join(out, "ambience.wav"), amb_f * g * trim)
    qa_stem_trim_db = round(20 * np.log10(trim), 2)
    for l in lines_all:                                          # per-line QA: level, evening, extra duck, final clarity
        a, z = l["a"], l["z"]
        qa["lines"].append(dict(scene=l["scene"], id=l["id"], who=l["who"], evened_db=round(l["evened_db"], 1),
                                extra_duck_db=l["extra_duck_db"],
                                dialogue_over_background_db=round(rms_db(vp[a:z]) - rms_db(sfx_l[a:z] + amb_f[a:z]), 1)))
    # QA
    fm = loudness(final)
    sr_, fx = wav.read(final)
    n_samples = fx.shape[0]
    fxf = fx.astype(np.float64) / 2 ** 31 if fx.dtype == np.int32 else fx.astype(np.float64)
    clipped = int((np.abs(fxf) >= 0.999).sum())
    ref = (vp + sfx_l + amb_f) * g; fm1 = fxf.mean(axis=1) if fxf.ndim > 1 else fxf
    w = int(0.01 * SR); grs = []
    for i in range(0, min(len(ref), len(fm1)) - w, w):
        pk = np.abs(ref[i:i + w]).max()
        if pk > 1e-4:
            grs.append(20 * np.log10(np.abs(fm1[i:i + w]).max() / pk + 1e-12))
    grs = np.array(grs)
    limiter = dict(share_blocks_over_1db=round(float((grs < -1).mean() * 100), 2), share_blocks_over_3db=round(float((grs < -3).mean() * 100), 2),
                   max_reduction_db=round(float(-grs.min()), 1))
    beds = []
    km = lp(hp(sfx_f + amb_f, 60), 8000)
    for j in qa["joins"]:
        T = next(s["start_s"] for s in qa["scenes"] if s["id"] == j["after"])
        def bedlvl(a, b):
            seg = km[int(a * SR):int(b * SR)]; w = int(0.4 * SR)
            return 20 * np.log10(min(np.sqrt(np.mean(seg[i:i + w] ** 2)) for i in range(0, len(seg) - w, w // 2)) + 1e-12)
        j["bed_change_3s_db"] = round(bedlvl(T, T + 3) - bedlvl(T - 3, T), 1)
        amb_only = hp(E["amb"], 60)                               # the bed itself, before ducking under dialogue
        sl = [rms_db(amb_only[int((T + d) * SR):int((T + d + 0.2) * SR)]) for d in np.arange(-2.0, 2.0, 0.2)]
        j["ambience_max_step_db"] = round(max(abs(b - a) for a, b in zip(sl, sl[1:])), 1)      # abruptness: the ear hears this
    qa.update(final=fm, samples=n_samples, expected_samples=total, duration_s=round(n_samples / SR, 4),
              sample_accurate=n_samples == total, clipped_samples=clipped, sample_rate=SR, bit_depth=24, channels=2,
              music="none (Episode 1 decision, 2026-10-22)", stems_trim_db=qa_stem_trim_db,
              dialogue_line_spread_raw_db=round(max(lv) - min(lv), 1), dialogue_median_db=round(med, 1), final_limiter=limiter,
              min_dialogue_over_background_db=min(x["dialogue_over_background_db"] for x in qa["lines"]))
    json.dump(qa, open(os.path.join(out, "audio_qa_report.json"), "w"), indent=1)
    print("limiter:", limiter, "| min dialogue over background: %.1f dB" % qa["min_dialogue_over_background_db"])
    print("final: %.2f LUFS, %.2f dBTP, LRA %.1f, %d samples (%s), clipped %d" % (
        fm["integrated_lufs"], fm["true_peak_dbtp"], fm["lra"], n_samples, "sample-accurate" if n_samples == total else "LENGTH MISMATCH", clipped))
    print("joins (3 s change / largest 200 ms step, dB):", [(j["after"], j["bed_change_3s_db"], j["ambience_max_step_db"]) for j in qa["joins"]])


if __name__ == "__main__":
    main()
