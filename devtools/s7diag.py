import sys, math, collections
sys.argv=[sys.argv[0]]
src=open('make_ep01_s007.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
from forest_camkit import clutter, los as flos
def diag(name, must, tgt, keep=None, L=None):
  keep=keep or AIR; L=L or LOS
  c=collections.Counter(); ok=[]
  for az in range(-180,180,10):
    for el in (8,12,16,22,28):
      for d in (1.4,1.7,2.0,2.4,2.8,3.4,4.0):
        e=eye_of(tgt,az,el,d)
        if not keep(e): c['air']+=1; continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): c['frame']+=1; continue
        if not L(e,must): c['los']+=1; continue
        ok.append((az,el,d))
  azs=sorted(set(o[0] for o in ok))
  print(name, dict(c), "azimuths:", azs, "eg", ok[:3])
diag("walk", gp(*OUT_VIA[3]) + gp(*G_SET)[1:], (-5.6, 2.8, 0.6))
diag("set", gp(*G_SET) + [(CUBE[0], CUBE[1], 0.1), (BOOK_AT[0], BOOK_AT[1], 0.1)], (-5.85, 4.25, 0.5))
diag("build", gp(*G_BUILD) + GATE_PTS, (-5.85, 3.35, 0.5))
diag("push", gp(*G_PUSH) + [(-6.0, 3.0, 0.4), BEAM_END], (-5.85, 3.7, 0.65))
diag("book", [(BOOK_AT[0]-0.11, BOOK_AT[1]-0.07, STONE_TOP), (BOOK_AT[0]+0.11, BOOK_AT[1]+0.07, STONE_TOP)], (BOOK_AT[0], BOOK_AT[1], STONE_TOP))
diag("lesson", gp(*G_BOOK), (G_BOOK[0], G_BOOK[1], 0.85))
diag("slide", gp(*G_SLIDE0)[1:] + GATE_PTS, (-5.85, 3.4, 0.5))
diag("lift", gp(*G_PUSH) + GATE_PTS[:2] + [(-6.0, 2.9, 0.62)], (-5.9, 3.5, 0.6))
diag("cloud", gp(*G_PUSH)[1:] + [(G_PUSH[0]+0.2, G_PUSH[1], 1.75)], (G_PUSH[0] + 0.05, G_PUSH[1], 1.15))
diag("bottle", gp(*G_PUSH)[1:] + [(STREAM_X(3.8) - 0.12, 3.8, 0.03), (STREAM_X(4.4) - 0.12, 4.4, 0.03)], (-5.5, 3.95, 0.5))
for tgt in ((-5.45,2.4,0.6),(-5.5,2.8,0.6),(-5.45,2.0,0.6)):
    diag("walk2 %s"%(tgt,), gp(*OUT_VIA[3]), tgt, L=make_los([]))
