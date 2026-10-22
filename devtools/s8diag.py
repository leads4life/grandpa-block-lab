import sys, math
sys.argv=[sys.argv[0]]
src=open('make_ep01_s008.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
from forest_camkit import clutter
def diag(name, must, tgt, L):
  ok=[]
  for az in range(-180,180,10):
    for el in (8,12,16,22,28):
      for d in (1.8,2.2,2.6,3.0,3.6,4.2,5.0):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not L(e,must): continue
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        ok.append((round(clutter(e,aim),2),az,el,d))
  ok.sort(); best={}
  for o in ok: best.setdefault(o[1],o)
  print(name, sorted(best.values())[:12])
diag("proof", gp(*G_BACK) + [(-3.8, 3.0, 0.5), (-2.3, 1.5, 0.05), (-2.3, 3.0, 0.5)], (-3.0, 1.9, 0.5), make_los([box_at(G_BACK)]) if 'box_at' in dir() else make_los([]))
diag("cloud", gp(*G_BACK)[1:] + [(G_BACK[0]+0.2, G_BACK[1], 1.75)], (G_BACK[0] + 0.05, G_BACK[1], 1.15), make_los([]))
diag("hook", gp(*G_BACK)[1:] + [(STREAM_X(3.0) + 0.1, 3.0, 0.03), (STREAM_X(3.6) + 0.1, 3.6, 0.03)], (-3.9, 1.9, 0.5), make_los([]))
LG=make_los([((-3.33, 1.38, 0.1), (-2.57, 1.42, 0.9)), ((-2.84, 1.36, 0.0), (-2.76, 1.44, 0.8))])   # the gate arm + panel + pivot post block the view
diag("build_hi", gp(*G_GATE)[1:] + [(-3.3, 1.4, 0.05), (-2.6, 1.4, 0.9)], (-2.95, 1.3, 0.6), LG)
diag("oops_hi", gp(*G_LIFT)[1:] + [ARM_END, (-2.8, 1.4, 0.75)], (-3.1, 1.25, 0.8), LG)
diag("fix_hi", gp(*G_ROCK)[1:] + gp(*G_LIFT)[1:] + [(-3.3, 1.4, 0.05), (-2.6, 1.4, 0.9), (-3.3, 1.4, 1.25)], (-2.95, 1.3, 0.6), LG)
diag("hook2", gp(*G_BACK) + [(STREAM_X(3.0) + 0.1, 3.0, 0.03), (STREAM_X(3.6) + 0.1, 3.6, 0.03)], (-3.6, 1.7, 0.6), make_los([]))
LG2=make_los([((-2.84, 1.36, 0.0), (-2.76, 1.44, 0.8))])
diag("rizz", [(G_LIFT[0], G_LIFT[1], 0.75), (G_LIFT[0], G_LIFT[1], 1.12), (-3.3, 1.4, 1.25), (-3.25, 1.4, 0.1)], (-3.2, 1.25, 0.75), LG2)
