"""Compose finished frames for one piece of one scene with that scene's OWN (pinned) bl_overlay, and write them to stdout
as raw RGB24 (called by gbl_final.py, which pipes the pieces of a segment into one encoder).

    python3 gbl_compose.py SCENE_DIR FRAMES_DIR FROM TO FX_JSON

SCENE_DIR is the prepared scene (its engine files + build/). FROM/TO are the scene's own frame numbers (TO exclusive).
FX_JSON carries the episode transitions for this scene: {"nf": N, "fade_out": frames, "fade_in": frames,
"card": {"text": "...", "from": f, "to": f}}. A fade dims only the picture (the stream's LIVE badge and chat stay up, as
on a real stream); the card is drawn over everything.
"""
import json
import os
import shutil
import sys
import tempfile
from multiprocessing import Pool

SCENE_DIR, SRC, F0, F1, FX = sys.argv[1], os.path.abspath(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), json.loads(sys.argv[5])
os.chdir(SCENE_DIR)
sys.path.insert(0, SCENE_DIR)
import numpy as np                                         # noqa: E402
from PIL import Image, ImageDraw, ImageFont                 # noqa: E402
import bl_overlay as O                                     # noqa: E402  (the scene's pinned overlay: same graphics as approved)

TMP = tempfile.mkdtemp(prefix="gbl_fx_")


class BadFrame(Exception):
    """A frame that is missing or unreadable: the driver deletes it and renders it again."""


def smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def gain(f):
    g = 1.0
    if FX.get("fade_out"):
        g = min(g, smooth((FX["nf"] - 1 - f) / FX["fade_out"]))
    if FX.get("fade_in"):
        g = min(g, smooth(f / FX["fade_in"]))
    return g


def card_alpha(f):
    c = FX.get("card")
    if not c or not (c["from"] <= f < c["to"]):
        return 0.0
    return min(1.0, (f - c["from"] + 1) / 6.0, (c["to"] - f) / 6.0)


def frame(f):
    if not os.path.exists(os.path.join(SRC, "%04d.png" % f)):
        raise BadFrame("%d missing" % f)
    src, g = SRC, gain(f)
    try:
        if g < 1.0:                                    # dim only the camera picture, then let the overlay draw on top
            im = np.asarray(Image.open(os.path.join(SRC, "%04d.png" % f)).convert("RGB"), dtype=np.float32)
            Image.fromarray(np.clip(im * g + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(TMP, "%04d.png" % f), compress_level=1)
            src = TMP
        buf = O.compose((f, src))
    except (OSError, SyntaxError, ValueError) as e:     # PIL: truncated / unreadable PNG
        raise BadFrame("%d %s" % (f, e))
    if src == TMP:
        os.remove(os.path.join(TMP, "%04d.png" % f))
    a = card_alpha(f)
    if a > 0:
        img = Image.frombytes("RGB", (O.W, O.H), buf).convert("RGBA")
        ov = Image.new("RGBA", img.size)
        d = ImageDraw.Draw(ov)
        font = ImageFont.truetype(os.path.join(FONTS, "DejaVuSans-Bold.ttf"), int(O.H * 0.06))
        d.text((O.W // 2, int(O.H * FX["card"].get("y", 0.5))), FX["card"]["text"], font=font, fill=(255, 255, 255, int(255 * a)), anchor="mm",
               stroke_width=6, stroke_fill=(24, 20, 16, int(235 * a)))
        img.alpha_composite(ov)
        buf = img.convert("RGB").tobytes()
    return buf


FONTS = FX.get("fonts") or O.FD

if __name__ == "__main__":
    out = sys.stdout.buffer
    try:
        with Pool(max(1, os.cpu_count() or 2)) as pool:
            for buf in pool.imap(frame, range(F0, F1), chunksize=4):
                out.write(buf)
        out.flush()
    except BadFrame as e:
        sys.stderr.write("BADFRAME %s\n" % e)
        sys.exit(3)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
