import sys, runpy, contextlib, io, math
sys.path.insert(0,'.'); sys.argv=['x','--fit']
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path('make_ep01_s003.py')
from storykit import cam_eye, TAN_H, TAN_V
cam=g['cam']; sf=g['solid_free']; los=g['los']; at_t=g['at_t']; B=g['BLOCKERS']; hit=g['seg_hits_box']
def blocked_frac(eye, tgt):
    f=[tgt[i]-eye[i] for i in range(3)]; n=math.sqrt(sum(v*v for v in f)); f=[v/n for v in f]
    r=[f[1],-f[0],0]; rn=math.hypot(r[0],r[1]); r=[v/rn for v in r]
    u=[r[1]*f[2]-r[2]*f[1], r[2]*f[0]-r[0]*f[2], r[0]*f[1]-r[1]*f[0]]
    c=0; tot=0
    for ix in range(-3,4):
        for iy in range(-2,3):
            dx,dy=ix/3*TAN_H*0.9, iy/2*TAN_V*0.9
            q=[eye[i]+(f[i]+dx*r[i]+dy*u[i])*n for i in range(3)]
            tot+=1; c+=any(hit(eye,q,lo,hi) for lo,hi in B)
    return c/tot
print([(k['at'],k['az'],k['el'],k['dist']) for k in cam])
F=int(32.87*30); bad=[]
for i in range(0,F+1,3):
    e,tgt,*_=cam_eye(cam,i/30)
    bf=blocked_frac(e,tgt); l=los(e,at_t(i/30)); s_=sf(e)
    if bf>0.2 or not l or not s_: bad.append((round(i/30,1), round(bf,2), l, s_))
print("problems (t, blocked frac, grandpa visible, cam clear):", bad)
