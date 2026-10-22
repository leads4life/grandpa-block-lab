import sys, runpy, contextlib, io, math, collections
sys.path.insert(0,'.'); sys.path.insert(0,'/home/user/blocklab'); sys.argv=['x','--fit']
T0_, T1_ = float(sys.argv_t0) if False else 19.8, 20.3
import storykit as K
real=K.auto_frame; box={}
def fake(*a, **k):
    if T0_ < a[0] < T1_: box['args']=(a,k)
    try: return real(*a, **k)
    except SystemExit: return real(*a, **{x:y for x,y in k.items() if x not in ('los','prev','path_clear','who','apart')})
K.auto_frame=fake
import forest_camkit as F
with contextlib.redirect_stdout(io.StringIO()):
    g=runpy.run_path('make_ep01_s005.py', run_name='x')
a,k=box['args']; t,must,tgt,az0,el0,d0,keep=a[:7]
c=collections.Counter()
for daz in range(-60,61,4):
  for el in range(8,34,3):
    for d in [d0*m for m in (0.9,1,1.1,1.25,1.4,1.6,1.8,2.0)]:
      e=K.eye_of(tgt,az0+daz,el,d)
      if not F.clear_air(e): c['air']+=1; continue
      if not keep(e): c['facing']+=1; continue
      pr=[K.project(e,tgt,p) for p in must]
      if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): c['frame']+=1; continue
      if k.get('apart'):
          qa,qb=K.project(e,tgt,k['apart'][0]),K.project(e,tgt,k['apart'][1])
          if math.hypot(qa[0]-qb[0],qa[1]-qb[1])<k.get('apart_min',0.42): c['apart']+=1; continue
      aim=[sum(p[i] for p in must)/len(must) for i in range(3)]
      if F.clutter(e,aim)>0.15: c['clutter']+=1; continue
      if not k["los"](e,must):
          tb=[p for p in must if any(F.seg_hits_box(e,p,lo,hi) for lo,hi in F.BLOCKERS)]
          c["los-blocked-%d" % len(tb)]+=1; continue
      c['ok']+=1
print(c)
