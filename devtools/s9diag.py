import sys, math
sys.argv=[sys.argv[0]]
src=open('make_ep01_s009.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
from forest_camkit import clutter
def diag(name, must, tgt, L):
  ok=[]
  for az in range(-180,180,10):
    for el in (8,12,16,22,28):
      for d in (1.6,2.0,2.4,2.8,3.4,4.0,4.6):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not L(e,must): continue
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        ok.append((round(clutter(e,aim),2),az,el,d))
  ok.sort(); best={}
  for o in ok: best.setdefault(o[1],o)
  print(name, sorted(best.values())[:10])
diag("fish", gp(*G_FISH)[1:] + [BOT_SNAG], (-4.6, 0.45, 0.5), make_los([box_at(G_FISH)]))
diag("talk", [(G_FISH[0], G_FISH[1], 0.75), (G_FISH[0], G_FISH[1], 1.12)], (G_FISH[0], G_FISH[1], 0.9), make_los([box_at(G_FISH)]))
diag("build", gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4), LG)
diag("test", gp(*G_BOX)[1:] + gp(*G_TEST)[1:] + [(BOX[0], BOX[1], 0.2), TIP], (-2.95, 1.1, 0.5), LG)
diag("alive", [(G_TEST[0], G_TEST[1], 0.75), (G_TEST[0], G_TEST[1], 1.12), TIP], (-3.5, 1.2, 0.75), LG)
diag("hook", gp(*G_TEST) + FENCE_PTS[:2], (-3.4, 1.6, 0.6), LG)
LM = make_los([box_at(G_FISH)], clutter_cast=MACHINE)
diag("fish2", gp(*G_FISH)[1:] + [BOT_SNAG], (-4.65, 0.4, 0.45), LM)
G_READ2 = (-3.25, 0.9)
diag("talk2", [(G_READ2[0], G_READ2[1], 0.75), (G_READ2[0], G_READ2[1], 1.12)], (G_READ2[0], G_READ2[1], 0.9), make_los([box_at(G_READ2)], clutter_cast=MACHINE))
