import sys
sys.argv=[sys.argv[0],'--fit']
import io, contextlib, runpy
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path('make_ep01_s006.py')
from storykit import cam_eye, project
cam=g['cam']; who=g['who_at']
out=[]
for f in range(0,1911):
    t=f/30; e,tgt=cam_eye(cam,t)[:2]
    x,y=g["g_at"](t); pts=[(x,y,0.75),(x,y,1.0),(x,y,1.12)]
    pr=[project(e,tgt,p) for p in pts]
    if any(q is None or abs(q[0])>1 or abs(q[1])>1 for q in pr): out.append(round(t,2))
# group
grp=[]; 
for t in out:
    if grp and t-grp[-1][1]<0.05: grp[-1][1]=t
    else: grp.append([t,t])
print(grp)
