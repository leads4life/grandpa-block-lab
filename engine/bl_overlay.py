"""Block Lab: draw the story's cards + captions over the rendered frames and encode the MP4 (vertical 1080x1920 inside the
Shorts safe zone, or "format": "wide" 1920x1080). Card styles: title, bubble ({count:STRUCT} = live block count), tag, panel, impact, end.

    python bl_overlay.py [--frames DIR] [--out NAME.mp4] [--still 60 300 ...]
"""
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import bl_common as C

P = C.load_plan()
FPS, NF, W, H = P["fps"], P["nf"], P["w"], P["h"]
ANCH = json.load(open(os.path.join(C.BUILD, "anchors.json")))
smooth = C.smooth
COL = {"white": (255, 255, 255), "amber": (255, 196, 64), "cyan": (110, 225, 255), "red": (255, 80, 64),
       "green": (120, 230, 120), "pink": (255, 130, 190)}
INK = (24, 20, 16)
WIDE = W > H                                   # "format": "wide" stories are 1920x1080
CX = W // 2
LAY = dict(tag=(60, 50), cap_y=H - 115, cap_size=56, cap_chars=30, clamp=(120, W - 120, 150, H - 190),
           end=(H * 0.36, H * 0.48, H * 0.57, H * 0.64), panel_w=520) if WIDE else \
      dict(tag=(90, 250), cap_y=1330, cap_size=64, cap_chars=16, clamp=(120, 960, 280, 1400),
           end=(760, 890, 1010, 1090), panel_w=450)
SETTLES = {}
for b in P["blocks"]:
    SETTLES.setdefault(b["struct"], []).append(b["settle"])


def font_dir():
    try:
        import matplotlib
        return os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
    except ImportError:
        return "/usr/share/fonts/truetype/dejavu"


FD, _fc = font_dir(), {}


def F(kind, size):
    size = max(8, int(size))
    if (kind, size) not in _fc:
        _fc[(kind, size)] = ImageFont.truetype(os.path.join(FD, {"bold": "DejaVuSans-Bold.ttf", "reg": "DejaVuSans.ttf"}[kind]), size)
    return _fc[(kind, size)]


def env(t, a, b, fi=0.25, fo=0.25):
    return smooth((t - a) / fi) * (1 - smooth((t - (b - fo)) / fo))


def pop(t, a):
    u = max(0.0, min(1.0, (t - a) / 0.22))
    return 0.6 + 0.4 * u + 0.18 * math.sin(math.pi * u) if u < 1 else 1.0


def outlined(d, xy, s, font, fill, a=1.0, anchor="mm", stroke=6):
    if a > 0.01:
        d.text(xy, s, font=font, fill=fill + (int(255 * a),), anchor=anchor, stroke_width=stroke, stroke_fill=INK + (int(235 * a),))


def anchor(f, key, dy=0):
    a = ANCH[str(min(f, NF - 1))].get(key)
    if not a or not a[2]:
        return None
    x0, x1, y0, y1 = LAY["clamp"]
    return min(x1, max(x0, a[0])), min(y1, max(y0, a[1] + dy))


def fill_text(s, f):
    """{count:NAME} = blocks of NAME placed so far; {count:NAME*} sums every structure whose name starts with NAME."""
    out = s
    for key in set(__import__("re").findall(r"\{count:([^}]+)\}", s)):
        names = [n for n in SETTLES if (n.startswith(key[:-1]) if key.endswith("*") else n == key)]
        out = out.replace("{count:%s}" % key, str(sum(1 for n in names for x in SETTLES[n] if x <= f)))
    return out


def card(d, ov, c, t, f):
    style = c.get("style", "title")
    col = COL.get(c.get("color", "white"), COL["white"])
    if style == "end":
        k = smooth((t - c["t0"]) / 0.4)
        if k <= 0:
            return
        ov.alpha_composite(Image.new("RGBA", (W, H), (12, 14, 18, int(200 * k))))
        d = ImageDraw.Draw(ov)
        fit = lambda s_: F("bold", min(110, 110 * 940 / max(1.0, F("bold", 110).getlength(s_))))   # shrink long titles to the safe width
        e1, e2, e3, e4 = LAY["end"]
        outlined(d, (CX, e1), c.get("title1", ""), fit(c.get("title1", "")), COL["white"], k)
        outlined(d, (CX, e2), c.get("title2", ""), fit(c.get("title2", "")), COL["amber"], k)
        d.text((CX, e3), c.get("sub", ""), font=F("reg", 30), fill=(210, 214, 220, int(255 * k)), anchor="mm")
        d.text((CX, e4), c.get("cta", ""), font=F("bold", 40), fill=COL["cyan"] + (int(255 * k),), anchor="mm")
        return
    if style == "live":                                        # "LIVE · 3 VIEWERS" badge, top right, on the whole time
        if not c["t0"] <= t <= c["t1"]:
            return
        vs = c.get("viewers", [[c["t0"], 0]])
        n, since = vs[0][1], vs[0][0]
        for tv, nv in vs:
            if t >= tv:
                n, since = nv, tv
        sz = 30 if WIDE else 34
        s_ = "LIVE \u00b7 %d VIEWER%s" % (n, "" if n == 1 else "S")
        fnt = F("bold", sz)
        tw = fnt.getlength(s_)
        x1, y0 = W - LAY["tag"][0], LAY["tag"][1]
        x0 = x1 - tw - 78
        k = pop(t, since) if since > c["t0"] else 1.0
        d.rounded_rectangle((x0, y0, x1, y0 + 62), radius=30, fill=(200, 30, 36, 235))
        dot = 0.65 + 0.35 * math.sin(2 * math.pi * t / 1.6) ** 2
        d.ellipse((x0 + 20, y0 + 22, x0 + 38, y0 + 40), fill=(255, 255, 255, int(255 * dot)))
        d.text((x0 + 50 + tw / 2, y0 + 31), s_, font=F("bold", sz * k), fill=(255, 255, 255, 255), anchor="mm")
        if since > c["t0"] and t - since < 1.2 and n > vs[0][1]:   # "+1" floats up when someone joins
            u = (t - since) / 1.2
            outlined(d, (x0 + 50 + tw * 0.75, y0 + 92 - 40 * u), "+1", F("bold", 40), COL["green"], 1 - smooth((u - 0.6) / 0.4), stroke=5)
        return
    a = env(t, c["t0"], c["t1"], fi=0.2 if style != "impact" else 0.06, fo=0.25 if style != "impact" else 0.35)
    if a <= 0.01:
        return
    if style == "title":
        outlined(d, (CX, c.get("y", 470)), fill_text(c["text"], f), F("bold", c.get("size", 96) * pop(t, c["t0"])), col, a)
    elif style == "impact":
        jx = 8 * math.sin(t * 90) * math.exp(-(t - c["t0"]) * 5)
        outlined(d, (CX + jx, c.get("y", 640)), c["text"], F("bold", c.get("size", 150) * pop(t, c["t0"])), col, a, stroke=8)
    elif style in ("bubble", "tag"):
        p = anchor(f, c["anchor"], c.get("dy", -40 if style == "bubble" else 0))
        if not p:
            return
        x, y = p
        size = c.get("size", 40 if style == "bubble" else 34) * (pop(t, c["t0"]) if style == "bubble" else 1)
        s = fill_text(c["text"], f)
        fnt = F("bold", size)
        tw = fnt.getlength(s)
        if style == "bubble":
            box = (x - tw / 2 - 24, y - size * 0.9 - 26, x + tw / 2 + 24, y - 26)
        else:
            box = (x - tw / 2 - 20, y - size * 0.6, x + tw / 2 + 20, y + size * 0.6)
        d.rounded_rectangle(box, radius=18, fill=(255, 250, 238, int(240 * a)), outline=col + (int(255 * a),), width=5)
        if style == "bubble":
            d.polygon([(x - 14, y - 28), (x + 14, y - 28), (x, y - 6)], fill=col + (int(255 * a),))
        d.text((x, (box[1] + box[3]) / 2), s, font=fnt, fill=INK + (int(255 * a),), anchor="mm")
    elif style == "panel":
        vis = [r for r in c["rows"] if t >= r["t"]]
        if not vis:
            return
        y0 = c.get("y", 300)
        half = LAY["panel_w"]
        if y0 == "top":                                         # on the line of the two top pills, between them, text-wide
            y0 = LAY["tag"][1]
            tag_r = LAY["tag"][0] + F("bold", 28).getlength(P["channel_tag"] or "") + 50
            half = min(half, CX - tag_r - 40, max(F("bold", r.get("size", 46)).getlength(fill_text(r["text"], f)) for r in c["rows"]) / 2 + 40)
        heights = [int(r.get("size", 46) * 1.6) for r in vis]
        hgt = 30 + sum(heights)
        border = COL.get(c.get("border", "cyan"), COL["cyan"])
        d.rounded_rectangle((CX - half, y0, CX + half, y0 + hgt), radius=26, fill=(16, 22, 30, int(200 * a)), outline=border + (int(200 * a),), width=4)
        yy = y0 + 15
        for r, hh in zip(vis, heights):
            aa = smooth((t - r["t"]) / 0.25) * a
            d.text((CX, yy + hh / 2), fill_text(r["text"], f), font=F("bold", r.get("size", 46)),
                   fill=COL.get(r.get("color", "white"), COL["white"]) + (int(255 * aa),), anchor="mm")
            yy += hh


def captions(d, t):
    for ln in P["lines"]:
        if ln["start"] - 0.05 <= t <= ln["end"] + 0.2:
            chunks, cur = [], []
            for w_ in ln["text"].split():
                cur.append(w_)
                if len(" ".join(cur)) > LAY["cap_chars"] or w_.endswith((".", ",", "?", "!")):
                    chunks.append(" ".join(cur)); cur = []
            if cur:
                chunks.append(" ".join(cur))
            n = sum(len(c) for c in chunks)
            t0 = ln["start"]
            for c in chunks:
                dur = (ln["end"] - ln["start"]) * len(c) / n
                if t0 - 0.05 <= t < t0 + dur + 0.12:
                    outlined(d, (CX, LAY["cap_y"]), c.replace("...", "…"), F("bold", LAY["cap_size"]), COL["white"], 1.0, stroke=7)
                    return
                t0 += dur


def dream(base, c, t):
    """The TV dream / flashback look: the picture ripples, softens and glows, with hazy edges -- fading in and out."""
    import numpy as np
    from PIL import ImageFilter
    w = env(t, c["t0"], c["t1"], fi=c.get("fade_in", 0.7), fo=c.get("fade_out", 0.35))
    if w <= 0:
        return base
    a = np.asarray(base).astype(np.float32)
    ys = np.arange(H)
    shift = (c.get("amp", 14) * w * np.sin(2 * np.pi * (ys / c.get("period", 120.0) + t * c.get("speed", 0.9)))).astype(int)
    idx = (np.arange(W)[None, :] - shift[:, None]) % W
    a = a[ys[:, None], idx]
    soft = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 + 5 * w))).astype(np.float32)
    a = a * (1 - 0.55 * w) + soft * 0.55 * w                              # softened
    a = a + (255 - a) * 0.12 * w                                          # a little hazy glow
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    edge = np.clip((r - 0.62) / 0.5, 0, 1)[..., None] * w                 # dreamy white-blue edges
    a = a * (1 - 0.85 * edge) + np.array([236, 242, 255], np.float32) * 0.85 * edge
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def compose(args):
    f, src = args
    t = f / FPS
    base = Image.open(os.path.join(src, "%04d.png" % f)).convert("RGB")
    if base.size != (W, H):
        base = base.resize((W, H), Image.BICUBIC)
    for c in P["cards"]:                                                  # "dream" cards act on the picture itself
        if c.get("style") == "dream":
            base = dream(base, c, t)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(ov)
    tag = P["channel_tag"]
    if tag:
        tw = F("bold", 28).getlength(tag)
        tx, ty = LAY["tag"]
        d.rounded_rectangle((tx, ty, tx + tw + 50, ty + 62), radius=30, fill=(255, 196, 64, 235))
        d.text((tx + (tw + 50) / 2, ty + 31), tag, font=F("bold", 28), fill=INK + (255,), anchor="mm")
    end_t = min([c["t0"] for c in P["cards"] if c.get("style") == "end"] + [P["film"] + 1])
    for c in P["cards"]:
        if c.get("style") == "dream":
            continue
        card(d, ov, c, t, f)
        d = ImageDraw.Draw(ov)
    if t < end_t:
        captions(d, t)
    img.alpha_composite(ov)
    return img.convert("RGB").tobytes()


def main():
    args = sys.argv[1:]
    src = os.path.abspath(args[args.index("--frames") + 1]) if "--frames" in args else os.path.join(C.BUILD, "frames")
    out = args[args.index("--out") + 1] if "--out" in args else os.path.join(C.HERE, P["slug"] + ".mp4")
    if "--still" in args:
        os.makedirs(os.path.join(C.BUILD, "stills"), exist_ok=True)
        for f in [int(a) for a in args[args.index("--still") + 1:] if a.isdigit()]:
            Image.frombytes("RGB", (W, H), compose((f, src))).save(os.path.join(C.BUILD, "stills", "%04d.png" % f))
        return
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                           "-r", str(FPS), "-i", "-", "-i", os.path.join(C.BUILD, "audio", "mix.wav"), "-map", "0:v", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    with Pool(max(1, os.cpu_count() or 2)) as pool:
        for buf in pool.imap(compose, [(f, src) for f in range(NF)], chunksize=4):
            ff.stdin.write(buf)
    ff.stdin.close(); ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
