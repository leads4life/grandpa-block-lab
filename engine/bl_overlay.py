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


CHAT_COL = {"pink": (255, 150, 200), "grey": (185, 188, 198), "amber": (255, 196, 64), "green": (130, 235, 130), "cyan": (110, 225, 255)}


def wrap(s, font, width):
    lines, cur = [], ""
    for w in s.split():
        if cur and font.getlength(cur + " " + w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + ([cur] if cur else [])


def chat(d, c, t):
    """The stream's chat: a small semi-transparent box under the LIVE badge; each comment pops in, stays, fades (max 3)."""
    dur, sz = c.get("stay", 4.5), (32 if WIDE else 36)
    msgs = [m for m in c["msgs"] if m["t"] <= t < m["t"] + dur][-3:]
    if not msgs:
        return
    fn, fb = F("reg", sz), F("bold", sz)
    x1 = W - LAY["tag"][0]
    bw = 600 if WIDE else 640
    x0, y = x1 - bw, LAY["tag"][1] + 62 + 14
    for m in msgs:
        a = env(t, m["t"], m["t"] + dur, 0.25, 0.6)
        slide = (1 - smooth((t - m["t"]) / 0.25)) * 14
        name = m["user"] + ":"
        col = CHAT_COL.get(c.get("colors", {}).get(m["user"], "grey"), CHAT_COL["grey"])
        indent = fb.getlength(name + " ")
        words = wrap(m["text"], fn, bw - 28 - indent)
        h = 14 + len(words) * (sz + 8) + 6
        d.rounded_rectangle((x0, y + slide, x1, y + slide + h), radius=14, fill=(14, 16, 22, int(150 * a)))
        d.text((x0 + 14, y + slide + 12), name, font=fb, fill=col + (int(255 * a),))
        for i, ln in enumerate(words):
            d.text((x0 + 14 + indent, y + slide + 12 + i * (sz + 8)), ln, font=fn, fill=(240, 242, 246, int(255 * a)))
        y += h + 8


def word(d, c, t):
    """A Word Card: a bigger word Grandpa just used, its syllables and a plain meaning; top left, under the channel tag."""
    k = env(t, c["t0"], c["t1"], 0.25, 0.4)
    if k <= 0:
        return
    sz = 30 if WIDE else 34
    fw, fs, fm = F("bold", sz + 10), F("reg", sz - 4), F("reg", sz)
    head, syl = c["word"].upper(), "  ·  " + c.get("say", "")
    lines = wrap(c["meaning"], fm, 560)
    bw = max(fw.getlength(head) + fs.getlength(syl), max(fm.getlength(s_) for s_ in lines)) + 40
    x0, y0 = LAY["tag"][0], LAY["tag"][1] + 62 + 14 - (1 - smooth((t - c["t0"]) / 0.25)) * 14
    h = 22 + sz + 10 + len(lines) * (sz + 8) + 16
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + h), radius=14, fill=(14, 16, 22, int(185 * k)),
                        outline=CHAT_COL["green"] + (int(255 * k),), width=3)
    d.text((x0 + 20, y0 + 16), head, font=fw, fill=COL["white"] + (int(255 * k),))
    d.text((x0 + 20 + fw.getlength(head), y0 + 16 + 10), syl, font=fs, fill=CHAT_COL["green"] + (int(255 * k),))
    for i, ln in enumerate(lines):
        d.text((x0 + 20, y0 + 22 + sz + 14 + i * (sz + 8)), ln, font=fm, fill=(232, 236, 240, int(255 * k)))


PAPER, PAPER_EDGE, INK_BROWN, INK_RED = (238, 224, 190), (150, 118, 78), (70, 52, 34), (190, 52, 40)


def page(ov, c, t):
    """A Page Card: the map / book page / note Grandpa is holding, shown big so viewers can read it, then away.
    {"style": "page", "when", "until", "title", "side": "auto"|"right"|"left"|"center", "tilt": deg,
     "map": {"route": [[u, v], ...], "stops": [{"at": [u, v], "name", "mark": "dot"|"x"|"star"}], "here": i, "done": [i]},
     "lines": ["...", ...], "ink": "brown"|"red"}       (u, v from 0 to 1 across / down the page)"""
    k = env(t, c["t0"], c["t1"], 0.35, 0.35)
    if k <= 0:
        return
    ph0 = int(H * (0.62 if WIDE else 0.36)); pw = int(ph0 * 1.25)
    ph = ph0
    if not c.get("map"):                                     # text only: as tall as the words need
        fl_ = F("reg", ph0 * 0.06)
        n_ = sum(len(wrap(ln, fl_, pw * 0.84)) for ln in c.get("lines", []))
        ph = int(min(ph0, max(ph0 * 0.4, 36 + (ph0 * 0.085 + 18 if c.get("title") else 0) + n_ * fl_.size * 1.35 + 34)))
    pg = Image.new("RGBA", (pw + 40, ph + 40))
    d = ImageDraw.Draw(pg)
    d.rounded_rectangle((26, 30, pw + 26, ph + 30), radius=10, fill=(0, 0, 0, 90))                  # shadow
    d.rounded_rectangle((14, 14, pw + 14, ph + 14), radius=10, fill=PAPER + (255,), outline=PAPER_EDGE + (255,), width=4)
    for fx_ in (0.5,):                                                                               # fold creases
        d.line((14 + pw * fx_, 18, 14 + pw * fx_, ph + 10), fill=PAPER_EDGE + (70,), width=2)
    d.line((18, 14 + ph * 0.5, pw + 10, 14 + ph * 0.5), fill=PAPER_EDGE + (70,), width=2)
    ink = INK_RED if c.get("ink") == "red" else INK_BROWN
    y = 14 + 22
    if c.get("title"):
        ft = F("bold", ph0 * 0.085)
        d.text((14 + pw / 2, y + ft.size / 2), c["title"], font=ft, fill=ink + (255,), anchor="mm")
        y += ft.size + 18
    m = c.get("map")
    if m:
        x0, y0, x1, y1 = 14 + pw * 0.08, y + 10, 14 + pw * 0.92, 14 + ph * 0.94
        P_ = lambda uv: (x0 + (x1 - x0) * uv[0], y0 + (y1 - y0) * uv[1])
        pts = [P_(q) for q in m.get("route", [])]
        for a_, b_ in zip(pts, pts[1:]):                                                            # dashed route
            n = max(1, int(math.dist(a_, b_) / 18))
            for i in range(0, n, 2):
                u0, u1 = i / n, min(1.0, (i + 1) / n)
                d.line((a_[0] + (b_[0] - a_[0]) * u0, a_[1] + (b_[1] - a_[1]) * u0,
                        a_[0] + (b_[0] - a_[0]) * u1, a_[1] + (b_[1] - a_[1]) * u1), fill=INK_RED + (230,), width=5)
        fs = F("bold", ph0 * 0.055)
        for i, st in enumerate(m.get("stops", [])):
            x, y_ = P_(st["at"])
            mk, r = st.get("mark", "dot"), ph * 0.035
            if mk == "x":
                d.line((x - r, y_ - r, x + r, y_ + r), fill=INK_RED + (255,), width=7)
                d.line((x - r, y_ + r, x + r, y_ - r), fill=INK_RED + (255,), width=7)
            elif mk == "star":
                pts_ = [(x + r * 1.3 * math.cos(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45),
                         y_ - r * 1.3 * math.sin(math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
                d.polygon(pts_, fill=COL["amber"] + (255,), outline=ink + (255,))
            else:
                d.ellipse((x - r, y_ - r, x + r, y_ + r), fill=PAPER + (255,), outline=ink + (255,), width=5)
                if i in m.get("done", []):
                    d.line((x - r * 0.6, y_, x - r * 0.1, y_ + r * 0.5, x + r * 0.7, y_ - r * 0.6), fill=(40, 130, 60, 255), width=5)
            if st.get("name"):
                d.text((x, y_ + r + 8), st["name"], font=fs, fill=ink + (255,), anchor="ma")
        if m.get("here") is not None:                                                               # "you are here"
            x, y_ = P_(m["stops"][m["here"]]["at"]) if isinstance(m["here"], int) else P_(m["here"])
            bob = 6 * math.sin(2 * math.pi * 1.2 * t)
            d.polygon([(x, y_ - ph * 0.05 + bob), (x - 14, y_ - ph * 0.10 + bob), (x + 14, y_ - ph * 0.10 + bob)],
                      fill=COL["green"] + (255,), outline=INK + (255,))
    fl = F("reg", ph0 * 0.06)
    for ln in c.get("lines", []):
        for w_ in wrap(ln, fl, pw * 0.84):
            d.text((14 + pw * 0.08, y), w_, font=fl, fill=ink + (255,))
            y += fl.size * 1.35
    if c.get("tilt", -2.5):
        pg = pg.rotate(c.get("tilt", -2.5), resample=Image.BICUBIC, expand=True)
    side = c.get("side", "auto")
    if side == "auto":                                      # the side of the screen he isn't on (where he is as it opens)
        g = ANCH[str(min(int(c["t0"] * FPS), NF - 1))].get("grandpa")
        side = "left" if g and g[2] and g[0] > W / 2 else "right"
    cx = {"left": W * 0.27, "center": W * 0.5, "right": W * 0.73}[side] if WIDE else W * 0.5
    cy = H * 0.52 + (1 - smooth((t - c["t0"]) / 0.35)) * H * 0.35 + smooth((t - (c["t1"] - 0.35)) / 0.35) * H * 0.35
    if k < 1:
        a_ = pg.getchannel("A").point(lambda v: int(v * k))
        pg.putalpha(a_)
    ov.alpha_composite(pg, (int(cx - pg.width / 2), int(cy - pg.height / 2)))


def icon(d, kind, x, y, s, a):
    """A little pixel-art item icon (Minecraft-style) centred at (x, y), s pixels across."""
    u = s / 8.0
    A = lambda col: col + (int(255 * a),)
    px = lambda i, j, col, w=1, h=1: d.rectangle((x - 4 * u + i * u, y - 4 * u + j * u, x - 4 * u + (i + w) * u - 1,
                                                   y - 4 * u + (j + h) * u - 1), fill=A(col))
    if kind in ("map", "page"):
        px(1, 1, PAPER_EDGE, 6, 6)
        px(1.5, 1.5, PAPER, 5, 5)
        if kind == "map":
            for i, j in ((2, 5), (3, 4), (4, 4)):
                px(i, j, INK_RED)
            px(5, 2, INK_RED); px(4.5, 2.5, INK_RED); px(5.5, 2.5, INK_RED); px(5, 3, INK_RED)
        else:
            for j in (2.5, 3.5, 4.5):
                px(2, j, INK_BROWN, 4, 0.5)
    elif kind == "webcam":
        px(1, 2, (60, 64, 72), 6, 4); px(3, 3, (20, 22, 26), 2, 2); px(3.5, 3.5, (110, 225, 255)); px(3, 6, (60, 64, 72), 2, 1)
    elif kind == "hammer":
        px(2, 1, (150, 155, 165), 5, 2); px(4, 3, (140, 96, 52), 1, 4)
    elif kind == "key":
        px(1, 2, (230, 190, 70), 3, 3); px(1.8, 2.8, (40, 40, 40), 1.4, 1.4); px(4, 3, (230, 190, 70), 3, 1); px(6, 4, (230, 190, 70)); px(5, 4, (230, 190, 70))
    elif kind == "lantern":
        px(3, 1, (60, 60, 60), 2, 1); px(2, 2, (60, 60, 60), 4, 5); px(2.5, 2.5, (255, 200, 90), 3, 4)
    else:                                                   # a plain block in the item's colour
        col = tuple(kind) if isinstance(kind, (list, tuple)) else (150, 110, 70)
        px(1, 1, col, 6, 6); px(1, 1, tuple(min(255, v + 40) for v in col), 6, 1); px(1, 1, tuple(min(255, v + 20) for v in col), 1, 6)


def inventory(d, c, t):
    """A Minecraft-style hotbar (bottom right): an item pops into the next slot when he puts it away (its name shows
    above it for a moment) and the slot lights up and empties when he takes it out.
    {"style": "inventory", "when", "until", "slots": 5, "items": [{"icon": "map", "name": "Map", "in": t, "out": t}]}"""
    k = env(t, c["t0"], c["t1"], 0.3, 0.3)
    if k <= 0:
        return
    n = c.get("slots", 5)
    sz = 64 if WIDE else 76
    x1 = W - LAY["tag"][0]
    y1 = H - (40 if WIDE else 260)
    x0 = x1 - n * sz - 8
    d.rectangle((x0, y1 - sz - 8, x1, y1), fill=(20, 20, 24, int(170 * k)), outline=(10, 10, 12, int(230 * k)), width=3)
    slot = {}
    for it in sorted(c["items"], key=lambda i: i["t_in"]):    # each item takes the first free slot when it goes in
        if t < it["t_in"] - 0.6:
            continue
        busy = {s_ for s_, j in slot.items() if j["t_out"] is None or t < j["t_out"] + 0.5}
        free = [i for i in range(n) if i not in busy]
        if free:
            slot[free[0]] = it
    for i in range(n):
        sx = x0 + 4 + i * sz
        d.rectangle((sx + 3, y1 - sz - 1, sx + sz - 3, y1 - 7), outline=(120, 120, 128, int(200 * k)), width=2)
        it = slot.get(i)
        if not it:
            continue
        cx_, cy_ = sx + sz / 2, y1 - 4 - sz / 2
        if t < it["t_in"]:                                  # flying in from above
            u = smooth((t - (it["t_in"] - 0.6)) / 0.6)
            icon(d, it.get("icon", "map"), cx_, cy_ - (1 - u) * 160, sz * 0.62 * (0.6 + 0.4 * u), k * u)
            continue
        out = it["t_out"] is not None and t >= it["t_out"]
        if out:                                             # lifted out: slot flashes, icon rises and fades
            u = (t - it["t_out"]) / 0.5
            if u >= 1:
                continue
            d.rectangle((sx + 3, y1 - sz - 1, sx + sz - 3, y1 - 7), outline=(255, 255, 255, int(255 * k * (1 - u))), width=4)
            icon(d, it.get("icon", "map"), cx_, cy_ - u * 60, sz * 0.62, k * (1 - u))
            continue
        if it.get("live"):                                  # the stream webcam: the selected slot, with a REC dot
            d.rectangle((sx + 1, y1 - sz - 3, sx + sz - 1, y1 - 5), outline=(255, 255, 255, int(235 * k)), width=4)
            pulse = 0.6 + 0.4 * math.sin(2 * math.pi * t / 1.6) ** 2
            d.ellipse((sx + sz - 22, y1 - sz + 4, sx + sz - 10, y1 - sz + 16), fill=(230, 40, 40, int(255 * k * pulse)))
        bump = 1 + 0.25 * math.sin(math.pi * min(1.0, (t - it["t_in"]) / 0.25))
        if t - it["t_in"] < 0.5:
            d.rectangle((sx + 3, y1 - sz - 1, sx + sz - 3, y1 - 7), outline=(255, 255, 255, int(255 * k)), width=4)
        icon(d, it.get("icon", "map"), cx_, cy_, sz * 0.62 * bump, k)
        if it.get("name") and t - it["t_in"] < 2.0:          # the item's name above the bar, like Minecraft
            a_ = k * (1 - smooth((t - it["t_in"] - 1.4) / 0.6))
            outlined(d, (cx_, y1 - sz - 34), it["name"], F("bold", 30), COL["white"], a_, stroke=4)


def card(d, ov, c, t, f):
    style = c.get("style", "title")
    col = COL.get(c.get("color", "white"), COL["white"])
    if style == "chat":
        if c["t0"] <= t <= c["t1"]:
            chat(d, c, t)
        return
    if style == "word":                                        # a Word Card: {"word", "say", "meaning", "when", "until"}
        word(d, c, t)
        return
    if style == "page":                                        # a Page Card: the map / page he holds up, shown big
        page(ov, c, t)
        return
    if style == "inventory":                                   # a Minecraft-style hotbar of what he has put away
        inventory(d, c, t)
        return
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
        was = n
        for tv, nv in vs:
            if t >= tv:
                was, n, since = n, nv, tv
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
        elif since > c["t0"] and t - since < 1.4 and n < was:      # "-1" sinks away when someone leaves
            u = (t - since) / 1.4
            outlined(d, (x0 + 50 + tw * 0.75, y0 + 82 + 30 * u), "-1", F("bold", 40), (200, 200, 205), 1 - smooth((u - 0.6) / 0.4), stroke=5)
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
    # exactly NF frames: the sound is padded with silence (apad) and cut at the film's length, so no frame is dropped
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                           "-r", str(FPS), "-i", "-", "-i", os.path.join(C.BUILD, "audio", "mix.wav"), "-map", "0:v", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "%.6f" % (NF / FPS), "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    with Pool(max(1, os.cpu_count() or 2)) as pool:
        for buf in pool.imap(compose, [(f, src) for f in range(NF)], chunksize=4):
            ff.stdin.write(buf)
    ff.stdin.close(); ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
