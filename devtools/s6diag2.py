import sys, math, collections
sys.argv=[sys.argv[0],'--fit']
src=open('make_ep01_s006.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
must=gp(*G_IN_VIA[1]) + kid(-6.36, 1.95) + [(-6.15, 1.5, 1.45)]
for tgt in ((-5.9,1.8,0.65),(-5.95,1.9,0.6)):
  ok=[]
  for az in range(-180,180,10):
    for el in (10,16,22,28):
      for d in (2.6,3.0,3.4,3.8,4.4):
        e=eye_of(tgt,az,el,d)
        if not AIR(e): continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): continue
        if not make_los([])(e,must): continue
        ok.append((az,el,d))
  print(tgt, ok[:40])
