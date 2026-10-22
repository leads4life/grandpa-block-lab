"""Scene choreography, captions, transitions and the frame renderer."""
import math, os, sys, subprocess, time
from functools import lru_cache
from multiprocessing import Pool
from PIL import Image, ImageDraw

from paper import (C, W, H, G, P, eo, eio, eback, pop, lerp, lerpc, cl, hrand, wob, jit, place, wplace, comp,
                   zoom, font, piece, shadowed, Board)
import assets as A
from timeline import TL, FPS

TOTAL = TL["total"]
NF = TL["nframes"]
SC = TL["scenes"]
for s in SC:
    s["w"] = [w[1] for w in s["words"]]


def cam():
    return (16 * math.sin(2 * math.pi * G.T / 7.3) * G.le, 10 * math.sin(2 * math.pi * G.T / 9.1 + 1) * G.le)


def at(x, y, d=1.0):
    cx, cy = cam()
    return x + cx * d, y + cy * d


def draw_bg(cv, img, d=0.35):
    cx, cy = cam()
    comp(cv, img, int(-A.M + cx * d), int(-A.M + cy * d))


def header(cv, t, text, col, t0=0.1, out=None):
    s = pop(t, t0, 0.4)
    if out is not None:
        s *= 1 - eio(P(t, out, 0.25))
    wplace(cv, ("hdr", text), A.tag(text, col, 46), *at(540, 250, 0.6), s=s, amp=0.6)


def bezier(p0, p2, f, lift=220):
    p1 = ((p0[0] + p2[0]) / 2, min(p0[1], p2[1]) - lift)
    x = (1 - f) ** 2 * p0[0] + 2 * (1 - f) * f * p1[0] + f ** 2 * p2[0]
    y = (1 - f) ** 2 * p0[1] + 2 * (1 - f) * f * p1[1] + f ** 2 * p2[1]
    return x, y


# ======================= BEDROOM (hook / reward / cta) =======================
