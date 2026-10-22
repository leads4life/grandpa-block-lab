import sys, math, collections
sys.argv=[sys.argv[0],'--fit']
src=open('make_ep01_s006.py').read(); src=src[:src.index('SHOTS = [')]
exec(src)
from storykit import eye_of, project
from forest_camkit import clutter, los as flos
def diag(name, must, tgt, keep, L):
  c=collections.Counter(); ok=[]
  for az in range(40,141,5):
    for el in range(5,34,3):
      for d in (1.3,1.5,1.7,1.9,2.1,2.4,2.8,3.2):
        e=eye_of(tgt,az,el,d)
        if not clear_air(e): c['air']+=1; continue
        if not lean_free(e): c['lean']+=1; continue
        if not keep(e): c['facing']+=1; continue
        pr=[project(e,tgt,p) for p in must]
        if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): c['frame']+=1; continue
        aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
        if clutter(e,aim)>0.15: c['clutter']+=1; continue
        if not flos(e,must): c['blockers']+=1; continue
        if not L(e,must): c['cast']+=1; continue
        ok.append((az,el,d))
  print(name, dict(c), ok[:12])
diag("bench+tob", g_in(*G_WORK)+kid_in(*T_SPOT)+[(-5.93,1.68,0.55)], (-6.3,1.5,0.75), NORTH, L_BENCH)
diag("bench", g_in(*G_WORK)+BOOK_PTS, (-6.15,1.45,0.82), NORTH, L_BENCH)
