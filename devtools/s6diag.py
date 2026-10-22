import sys, math, collections
sys.argv=[sys.argv[0]]
src=open('make_ep01_s006.py').read()
src=src[:src.index('for shot in SHOTS:')]
exec(src)
from storykit import eye_of, project
def diag(must, tgt, az0, el0, d0, keep, los_):
    c=collections.Counter(); ok=[]
    for daz in range(-60,61,4):
        for el in range(8,34,3):
            for dist in [d0*k for k in (0.9,1.0,1.1,1.25,1.4,1.6,1.8,2.0)]:
                eye=eye_of(tgt,az0+daz,el,dist)
                if not clear_air(eye): c['air']+=1; continue
                if not lean_free(eye): c['lean']+=1; continue
                if not NORTH(eye): c['north']+=1; continue
                pr=[project(eye,tgt,p) for p in must]
                if any(q is None or abs(q[0])>0.82 or abs(q[1])>0.82 for q in pr): c['frame']+=1; continue
                if not los_(eye,must): c['los']+=1; continue
                ok.append((az0+daz,el,round(dist,2)))
    print(c, ok[:6])
diag(gp(*G_WORK)+kid(*T_SPOT)+[(-5.93,1.68,0.55)], (-6.3,1.5,0.75), 75,12,2.2, None, L_BENCH)
diag(gp(*G_WORK), (-6.15,1.4,0.85), 90,12,1.8, None, make_los([]))
diag(gp(*G_WORK), (-6.15,1.4,0.85), 90,12,1.8, None, lambda e,p: True)
