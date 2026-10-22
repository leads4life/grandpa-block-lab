import sys, math
sys.argv=[sys.argv[0],'--fit']
src=open('make_ep01_s007.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
from forest_camkit import clutter
def diag(name, must, tgt):
  L=make_los([]); ok=[]
  for az in range(-180,180,10):
    for el in (18,22,26,30,33):
      for d in (3.4,4.0,4.6,5.2,6.0):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not L(e,must): continue
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        ok.append((round(clutter(e,aim),2),az,el,d))
  ok.sort()
  print(name, ok[:10])
diag("fence", gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4))
diag("fast", gp(*STAND["n"]) + gp(*STAND["e"]) + FENCE_PTS, (-3.0, 2.25, 0.4))
def diag2(name, must, tgt):
  L=make_los([]); ok=[]
  for az in range(-180,180,5):
    for el in (18,22,26,30,33):
      for d in (3.4,4.0,4.6,5.2,6.0):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not L(e,must): continue
        tr=[project(e,tgt,(-4.08,3.03,z)) for z in (0.2,0.8,1.3)]
        if any(q is not None and abs(q[0])<0.5 and abs(q[1])<1.0 for q in tr): continue   # the oak trunk: keep it out of frame
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        ok.append((round(clutter(e,aim),2),az,el,d))
  ok.sort(); print(name, ok[:10])
diag2("fence2", gp(*STAND["s"]) + FENCE_PTS, (-3.05, 2.2, 0.4))
diag2("fast2", gp(*STAND["n"]) + gp(*STAND["e"]) + FENCE_PTS, (-3.0, 2.25, 0.4))
def diag3(name, must, tgt):
  L=make_los([]); ok=[]
  for az in range(-180,180,5):
    for el in (12,16,20,24):
      for d in (2.2,2.6,3.0,3.4):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not L(e,must): continue
        tr=[project(e,tgt,(-4.08,3.03,z)) for z in (0.2,0.8,1.3)]
        if any(q is not None and abs(q[0])<0.5 and abs(q[1])<1.0 for q in tr): continue
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        ok.append((round(clutter(e,aim),2),az,el,d))
  ok.sort(); print(name, ok[:12])
diag3("south", gp(*STAND["s"]) + [(-3.8, 1.5, 0.05), (-2.3, 1.5, 0.5)], (-3.05, 1.45, 0.55))
