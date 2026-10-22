import sys, math, collections
sys.argv=[sys.argv[0]]
src=open('make_ep01_s007.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
def diag(name, must, tgt, L=None):
  L=L or make_los([])
  c=collections.Counter(); ok=[]
  for az in range(-180,180,10):
    for el in (8,12,16,22,28):
      for d in (1.6,2.0,2.4,2.8,3.4,4.0,4.6):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): c['air']+=1; continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): c['frame']+=1; continue
        if not L(e,must): c['los']+=1; continue
        ok.append((az,el,d))
  best={}
  for o in ok: best.setdefault(o[0],o)
  print(name, "->", list(best.values()))
diag("walk", gp(*OUT_VIA[3]), (-5.5, 2.8, 0.6))
diag("stones", gp(*STONES[1]) + gp(*STONES[-1])[1:], (-4.95, 2.45, 0.55))
diag("set", gp(*P_SET) + [(CUBE[0], CUBE[1], 0.1), (BOOK_AT[0], BOOK_AT[1], BOOK_TOP)], (-3.65, 1.1, 0.55))
diag("fence", gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4))
diag("freeze", gp(*STAND["w"])[1:] + [(-3.8, 1.6, 0.4), (-3.8, 2.9, 0.4)], (-3.95, 2.45, 0.8))
diag("fast", gp(*STAND["n"]) + gp(*STAND["e"]) + FENCE_PTS, (-3.0, 2.25, 0.4))
diag("gap", gp(*G_GAP) + [(-3.3, 1.5, 0.45), (-2.8, 1.5, 0.45)], (-3.05, 1.3, 0.75))
