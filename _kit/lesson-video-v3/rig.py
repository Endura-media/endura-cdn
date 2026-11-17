import math, random, numpy as np
from PIL import Image, ImageDraw
S=3
def up(im,s=S): return im.resize((im.width*s,im.height*s),Image.LANCZOS)
def sample(im,xy): return im.getpixel(xy)[:3]

class Host:
    def __init__(self):
        im=up(Image.open('host.png').convert('RGBA'))
        a=np.array(im); a[50*S:116*S,228*S:275*S,3]=0     # drop speech lines
        im=Image.fromarray(a)
        self.skin=sample(im,(150*S,122*S))
        d=ImageDraw.Draw(im)
        d.rectangle((137*S,128*S,177*S,157*S),fill=self.skin+(255,))   # clear mouth
        # clear pupils -> repaint white
        for cx,cy in ((145,100),(163,98)): d.ellipse(((cx-6)*S,(cy-6)*S,(cx+6)*S,(cy+6)*S),fill=(255,255,255,255))
        self.base=im
        self.eyes=[(130*S,101*S,21*S,22*S),(172*S,100*S,21*S,22*S)]
        self.pup=[(145*S,100*S),(163*S,98*S)]
        self.mouth=(156*S,141*S)
        self.split=150*S
    def frame(self,t,amp,talking,seed=0):
        im=self.base.copy(); d=ImageDraw.Draw(im)
        # glance
        gx=2*S*math.sin(t*0.7+seed); gy=1*S*math.sin(t*0.5)
        for (px,py) in self.pup: d.ellipse((px-4*S+gx,py-4*S+gy,px+4*S+gx,py+4*S+gy),fill=(0,0,0,255))
        # blink every ~3.3s, 0.15s long
        ph=(t+seed)%3.3
        b=0
        if ph<0.16: b=math.sin(ph/0.16*math.pi)
        if b>0:
            for (ex,ey,rx,ry) in self.eyes:
                lid=Image.new('L',im.size,0); ld=ImageDraw.Draw(lid)
                ld.ellipse((ex-rx-5,ey-ry-5,ex+rx+5,ey+ry+5),fill=255)
                cut=Image.new('L',im.size,0); ImageDraw.Draw(cut).rectangle((0,0,im.width,ey-ry-6+int((2*ry+12)*b)),fill=255)
                m=Image.fromarray(np.minimum(np.array(lid),np.array(cut)))
                im.paste(Image.new('RGBA',im.size,self.skin+(255,)),(0,0),m)
                yy=ey-ry+int(2*ry*b)
                if b>0.85: d.arc((ex-rx*0.8,ey-ry*0.6,ex+rx*0.8,ey+ry*0.5),start=20,end=160,fill=(30,30,30,255),width=S*2)
                else: d.line((ex-rx+6,yy,ex+rx-6,yy),fill=(30,30,30,255),width=S*2)
        # mouth
        mx,my=self.mouth
        lvl=min(1,amp*2.2) if talking else 0
        if lvl<0.12:
            d.arc((mx-13*S,my-8*S,mx+13*S,my+6*S),start=20,end=160,fill=(30,30,30,255),width=S*2)
        else:
            w=(10+6*lvl)*S; h=(3+11*lvl)*S
            d.ellipse((mx-w,my-h*0.4,mx+w,my+h),fill=(120,30,40,255),outline=(30,30,30,255),width=S*2)
            d.ellipse((mx-w*0.6,my+h*0.35,mx+w*0.6,my+h*0.95),fill=(232,110,140,255))
            d.rectangle((mx-w*0.7,my-h*0.4+S*2,mx+w*0.7,my-h*0.4+S*5),fill=(255,255,255,255))
        # head / body split + motion
        head=im.crop((0,0,im.width,self.split+8*S)); body=im.copy()
        ang=(2.2*math.sin(t*1.7) + (3*lvl if talking else 0)*math.sin(t*6))*0.8
        nod=int((lvl*3*S)*abs(math.sin(t*5))) if talking else 0
        head=head.rotate(ang,resample=Image.BICUBIC,center=(150*S,self.split),expand=False)
        out=Image.new('RGBA',im.size,(0,0,0,0))
        breath=1+0.008*math.sin(t*2.2)
        bw,bh=body.size; bb=body.resize((bw,int(bh*breath)),Image.BILINEAR)
        out.alpha_composite(bb,(0,bh-bb.height))
        # cover old head area with new head
        out.paste(Image.new('RGBA',(im.width,self.split),(0,0,0,0)),(0,0))
        out.alpha_composite(head,(0,nod+(bh-bb.height)))
        return out

class SadRoofer:
    def __init__(self):
        im=Image.open('roof_sad.png').convert('RGBA'); im=im.crop(im.getbbox())
        self.skin=sample(im,(240,150))
        d=ImageDraw.Draw(im)
        for cx,cy in ((212,264),(266,264)): d.ellipse((cx-14,cy-14,cx+14,cy+14),fill=(255,255,255,255))
        d.rectangle((205,345,290,378),fill=self.skin+(255,))
        self.base=im; self.split=398
        self.eyes=[(191,252,49,50),(293,252,50,50)]
    def frame(self,t):
        im=self.base.copy(); d=ImageDraw.Draw(im)
        gy=6+2*math.sin(t*0.8)   # looking down
        for cx,cy in ((210,264),(264,264)): d.ellipse((cx-10,cy-10+gy,cx+10,cy+10+gy),fill=(0,0,0,255))
        # heavy droopy lids always half-ish + slow blink
        ph=t%2.6; b=0.28
        if ph<0.3: b=0.28+0.72*math.sin(ph/0.3*math.pi)
        for (ex,ey,rx,ry) in self.eyes:
            lid=Image.new('L',im.size,0); ImageDraw.Draw(lid).ellipse((ex-rx-6,ey-ry-6,ex+rx+6,ey+ry+6),fill=255)
            cut=Image.new('L',im.size,0); ImageDraw.Draw(cut).rectangle((0,0,im.width,ey-ry-6+int((2*ry+12)*b)),fill=255)
            m=Image.fromarray(np.minimum(np.array(lid),np.array(cut)))
            im.paste(Image.new('RGBA',im.size,self.skin+(255,)),(0,0),m)
            yy=ey-ry+int(2*ry*b)
            if b>0.85: d.arc((ex-rx*0.8,ey-ry*0.6,ex+rx*0.8,ey+ry*0.5),start=20,end=160,fill=(30,30,30,255),width=5)
            else: d.line((ex-rx+8,yy,ex+rx-8,yy),fill=(30,30,30,255),width=5)
        # quivering frown
        q=2*math.sin(t*14)
        d.arc((208,352+q,282,400+q),start=200,end=340,fill=(17,17,17,255),width=7)
        # tear
        tp=(t%2.2)/2.2
        tx=168; ty=300+tp*90
        if tp<0.9:
            d.ellipse((tx-7,ty-4,tx+7,ty+14),fill=(110,170,235,255)); d.polygon([(tx-6,ty),(tx+6,ty),(tx,ty-12)],fill=(110,170,235,255))
        head=im.crop((0,0,im.width,self.split+10))
        ang=-3-2.5*(0.5+0.5*math.sin(t*0.9))   # droop
        head=head.rotate(ang,resample=Image.BICUBIC,center=(237,self.split))
        out=Image.new('RGBA',im.size,(0,0,0,0))
        hammer_down(ImageDraw.Draw(out),432,650)
        sigh=1-0.012*(0.5+0.5*math.sin(t*1.1))
        bw,bh=im.size; bb=im.resize((bw,int(bh*sigh)),Image.BILINEAR)
        out.alpha_composite(bb,(0,bh-bb.height))
        out.paste(Image.new('RGBA',(bw,self.split),(0,0,0,0)),(0,bh-bb.height))
        out.alpha_composite(head,(0,bh-bb.height+4))
        return out

def cloud(d,cx,cy,t,k=0.7):
    for dx,dy,r in ((-60,0,48),(0,-22,60),(62,0,46),(-20,22,44),(30,20,44)):
        d.ellipse((cx+(dx-r)*k,cy+(dy-r)*k,cx+(dx+r)*k,cy+(dy+r)*k),fill=(150,158,170,255))
    for i in range(6):
        x=cx-55+i*22; p=((t*1.6+i*0.37)%1)
        y=cy+38+p*150
        d.line((x,y,x-6,y+22),fill=(110,160,230,255),width=6)

SKIN=(254,194,125); SHIRT=(30,30,30); OUTL=(40,40,40)
POSES={
 'rest':(10,5,10,5),
 'shrug':(35,95,35,95),
 'explain_r':(14,0,25,95),
 'explain_l':(25,95,14,0),
 'point_up':(12,0,165,0),
 'count':(14,0,40,125),
 'cheer':(150,10,150,10),
 'present':(70,40,14,0),
}
class HostFull:
    def __init__(self):
        im=Image.open('host_front.png').convert('RGBA')
        im=im.resize((im.width*S,im.height*S),Image.LANCZOS)
        a=np.array(im)
        # erase original arms (outside torso edges)
        a[160*S:265*S,0:30*S,3]=0; a[160*S:265*S,126*S:,3]=0
        im=Image.fromarray(a); d=ImageDraw.Draw(im)
        # patch torso edges straight
        d.rectangle((26*S,165*S,32*S,262*S),fill=SHIRT+(255,)); d.rectangle((123*S,165*S,129*S,262*S),fill=SHIRT+(255,))
        self.skin=sample(im,(78*S,125*S))
        d.rectangle((66*S,131*S,91*S,144*S),fill=self.skin+(255,))
        for cx,cy in ((66,98),(82,97)): d.ellipse(((cx-5)*S,(cy-5)*S,(cx+5)*S,(cy+5)*S),fill=(255,255,255,255))
        self.base=im; self.split=152*S
        self.eyes=[(57*S,100*S,17*S,18*S),(95*S,99*S,19*S,18*S)]
        self.pup=[(66*S,98*S),(82*S,97*S)]
        self.mouth=(78*S,136*S)
        self.sh=[(27*S,172*S),(128*S,172*S)]
        self.cur=list(POSES['rest'])
    def arm(self,d,sx,sy,a1,a2,side):
        L1,L2,Wd=36*S,34*S,19*S
        sgn=-1 if side==0 else 1
        r1=math.radians(a1); ex=sx+sgn*math.sin(r1)*L1; ey=sy+math.cos(r1)*L1
        r2=math.radians(a1+a2); hx=ex+sgn*math.sin(r2)*L2; hy=ey+math.cos(r2)*L2
        def seg(x1,y1,x2,y2,col,w):
            d.line((x1,y1,x2,y2),fill=OUTL,width=w+2*S); d.line((x1,y1,x2,y2),fill=col,width=w)
            for (x,y) in ((x1,y1),(x2,y2)):
                d.ellipse((x-w/2-S,y-w/2-S,x+w/2+S,y+w/2+S),fill=OUTL); d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2),fill=col)
        mx=sx+(ex-sx)*0.55; my=sy+(ey-sy)*0.55
        seg(mx,my,ex,ey,SKIN,Wd); seg(ex,ey,hx,hy,SKIN,Wd)
        seg(sx,sy,mx,my,SHIRT,Wd+6*S)
        hr=13*S; d.ellipse((hx-hr-S,hy-hr-S,hx+hr+S,hy+hr+S),fill=OUTL); d.ellipse((hx-hr,hy-hr,hx+hr,hy+hr),fill=SKIN)
        tx=hx+sgn*-1*8*S*math.cos(r2); ty=hy-8*S*math.sin(r2)*0
        d.ellipse((tx-5*S,ty-9*S,tx+5*S,ty+1*S),fill=SKIN,outline=OUTL,width=S)
    def set_pose(self,name,k=0.18):
        tgt=POSES[name]; self.cur=[c+(t-c)*k for c,t in zip(self.cur,tgt)]
    def frame(self,t,amp,talking,pose='rest',seed=0):
        self.set_pose(pose)
        im=self.base.copy(); d=ImageDraw.Draw(im)
        gx=2*S*math.sin(t*0.7+seed); gy=S*math.sin(t*0.5)
        for (px,py) in self.pup: d.ellipse((px-4*S+gx,py-4*S+gy,px+4*S+gx,py+4*S+gy),fill=(0,0,0,255))
        ph=(t+seed)%3.3; b=math.sin(ph/0.16*math.pi) if ph<0.16 else 0
        if b>0:
            for (ex,ey,rx,ry) in self.eyes:
                lid=Image.new('L',im.size,0); ImageDraw.Draw(lid).ellipse((ex-rx-5,ey-ry-5,ex+rx+5,ey+ry+5),fill=255)
                cut=Image.new('L',im.size,0); ImageDraw.Draw(cut).rectangle((0,0,im.width,ey-ry-6+int((2*ry+12)*b)),fill=255)
                im.paste(Image.new('RGBA',im.size,self.skin+(255,)),(0,0),Image.fromarray(np.minimum(np.array(lid),np.array(cut))))
                if b>0.85: d.arc((ex-rx*0.8,ey-ry*0.6,ex+rx*0.8,ey+ry*0.5),start=20,end=160,fill=(30,30,30,255),width=S*2)
        mx,my=self.mouth; lvl=min(1,amp*2.2) if talking else 0
        if lvl<0.12: d.arc((mx-10*S,my-7*S,mx+10*S,my+4*S),start=20,end=160,fill=(30,30,30,255),width=S*2)
        else:
            w=(8+5*lvl)*S; h=(3+9*lvl)*S
            d.ellipse((mx-w,my-h*0.4,mx+w,my+h),fill=(120,30,40,255),outline=(30,30,30,255),width=S*2)
            d.ellipse((mx-w*0.6,my+h*0.35,mx+w*0.6,my+h*0.95),fill=(232,110,140,255))
            d.rectangle((mx-w*0.7,my-h*0.4+S*2,mx+w*0.7,my-h*0.4+S*5),fill=(255,255,255,255))
        head=im.crop((0,0,im.width,self.split+8*S))
        ang=2.0*math.sin(t*1.7)+(2.5*lvl*math.sin(t*6) if talking else 0)
        nod=int(lvl*3*S*abs(math.sin(t*5))) if talking else 0
        head=head.rotate(ang,resample=Image.BICUBIC,center=(77*S,self.split))
        pad=90*S
        out=Image.new('RGBA',(im.width+2*pad,im.height+pad),(0,0,0,0))
        body=im.copy(); body.paste(Image.new('RGBA',(im.width,self.split),(0,0,0,0)),(0,0))
        breath=int(2*S*math.sin(t*2.2))
        out.alpha_composite(body,(pad,pad))
        out.alpha_composite(head,(pad,pad+nod+breath*0))
        od=ImageDraw.Draw(out)
        l1,l2,r1,r2=self.cur
        sw=4*math.sin(t*1.3)
        self.arm(od,self.sh[0][0]+pad,self.sh[0][1]+pad,l1+sw,l2,0)
        self.arm(od,self.sh[1][0]+pad,self.sh[1][1]+pad,r1-sw,r2,1)
        return out

def hammer_down(d,hx,hy):
    # handle hanging from hand at (hx,hy), head at bottom
    d.rounded_rectangle((hx-7,hy,hx+7,hy+150),5,fill=(176,120,70),outline=OUTL,width=3)
    d.rounded_rectangle((hx-34,hy+140,hx+30,hy+178),8,fill=(150,155,165),outline=OUTL,width=3)
    d.polygon([(hx-34,hy+142),(hx-58,hy+150),(hx-34,hy+160)],fill=(150,155,165),outline=OUTL)

class HostStill(HostFull):
    """Kui's real full-body art, arms down as drawn. Only blink + mouth."""
    def __init__(self):
        im=Image.open('host_front.png').convert('RGBA')
        im=im.resize((im.width*S,im.height*S),Image.LANCZOS)
        d=ImageDraw.Draw(im)
        self.skin=sample(im,(78*S,125*S))
        d.rectangle((66*S,131*S,91*S,144*S),fill=self.skin+(255,))
        for cx,cy in ((66,98),(82,97)): d.ellipse(((cx-5)*S,(cy-5)*S,(cx+5)*S,(cy+5)*S),fill=(255,255,255,255))
        self.base=im
        self.eyes=[(57*S,100*S,17*S,18*S),(95*S,99*S,19*S,18*S)]
        self.pup=[(66*S,98*S),(82*S,97*S)]
        self.mouth=(78*S,136*S)
    def frame(self,t,amp,talking,pose='rest',seed=0):
        im=self.base.copy(); d=ImageDraw.Draw(im)
        for (px,py) in self.pup: d.ellipse((px-4*S,py-4*S,px+4*S,py+4*S),fill=(0,0,0,255))
        ph=(t+seed)%3.3; b=math.sin(ph/0.16*math.pi) if ph<0.16 else 0
        if b>0:
            for (ex,ey,rx,ry) in self.eyes:
                lid=Image.new('L',im.size,0); ImageDraw.Draw(lid).ellipse((ex-rx-5,ey-ry-5,ex+rx+5,ey+ry+5),fill=255)
                cut=Image.new('L',im.size,0); ImageDraw.Draw(cut).rectangle((0,0,im.width,ey-ry-6+int((2*ry+12)*b)),fill=255)
                im.paste(Image.new('RGBA',im.size,self.skin+(255,)),(0,0),Image.fromarray(np.minimum(np.array(lid),np.array(cut))))
                if b>0.85: d.arc((ex-rx*0.8,ey-ry*0.6,ex+rx*0.8,ey+ry*0.5),start=20,end=160,fill=(30,30,30,255),width=S*2)
        mx,my=self.mouth; lvl=min(1,amp*2.2) if talking else 0
        if lvl<0.12: d.arc((mx-10*S,my-7*S,mx+10*S,my+4*S),start=20,end=160,fill=(30,30,30,255),width=S*2)
        else:
            w=(8+5*lvl)*S; h=(3+9*lvl)*S
            d.ellipse((mx-w,my-h*0.4,mx+w,my+h),fill=(120,30,40,255),outline=(30,30,30,255),width=S*2)
            d.ellipse((mx-w*0.6,my+h*0.35,mx+w*0.6,my+h*0.95),fill=(232,110,140,255))
            d.rectangle((mx-w*0.7,my-h*0.4+S*2,mx+w*0.7,my-h*0.4+S*5),fill=(255,255,255,255))
        pad=90*S
        out=Image.new('RGBA',(im.width+2*pad,im.height+pad),(0,0,0,0)); out.alpha_composite(im,(pad,pad))
        return out

class HostStill2(HostStill):
    """Clean blink: full eye swap to closed lids (no partial wipe)."""
    def __init__(self):
        super().__init__()
        im=self.base.copy(); d=ImageDraw.Draw(im)
        for (cx,cy,rx,ry) in ((61,99,23,22),(97,98,22,22)):
            d.ellipse(((cx-rx)*S,(cy-ry)*S,(cx+rx)*S,(cy+ry)*S),fill=self.skin+(255,))
        # restore brows/forehead above eyes from original
        im.paste(self.base.crop((0,0,im.width,79*S)),(0,0))
        for (cx,cy) in ((61,101),(97,100)):
            d.arc(((cx-14)*S,(cy-9)*S,(cx+14)*S,(cy+7)*S),start=15,end=165,fill=(30,30,30,255),width=S*2)
        self.closed=im
    def frame(self,t,amp,talking,pose='rest',seed=0):
        ph=(t+seed)%3.3
        im=(self.closed if ph<0.12 else self.base).copy(); d=ImageDraw.Draw(im)
        if ph>=0.12:
            for (px,py) in self.pup: d.ellipse((px-4*S,py-4*S,px+4*S,py+4*S),fill=(0,0,0,255))
        mx,my=self.mouth; lvl=min(1,amp*2.2) if talking else 0
        if lvl<0.12: d.arc((mx-10*S,my-7*S,mx+10*S,my+4*S),start=20,end=160,fill=(30,30,30,255),width=S*2)
        else:
            w=(8+5*lvl)*S; h=(3+9*lvl)*S
            d.ellipse((mx-w,my-h*0.4,mx+w,my+h),fill=(120,30,40,255),outline=(30,30,30,255),width=S*2)
            d.ellipse((mx-w*0.6,my+h*0.35,mx+w*0.6,my+h*0.95),fill=(232,110,140,255))
            d.rectangle((mx-w*0.7,my-h*0.4+S*2,mx+w*0.7,my-h*0.4+S*5),fill=(255,255,255,255))
        pad=90*S
        out=Image.new('RGBA',(im.width+2*pad,im.height+pad),(0,0,0,0)); out.alpha_composite(im,(pad,pad))
        return out

class HostStill3(HostStill2):
    """Pupils spaced like Kui's avatar: each pupil in its own eye, slightly inward, smaller."""
    def __init__(self):
        super().__init__()
        self.pup=[(67*S,102*S),(91*S,101*S)]
    def frame(self,t,amp,talking,pose='rest',seed=0):
        old=self.pup; self.pup=[]
        out=HostStill2.frame(self,t,amp,talking,pose,seed)
        self.pup=old
        if (t+seed)%3.3>=0.12:
            d=ImageDraw.Draw(out); pad=90*S; r=3.2*S
            for (px,py) in old: d.ellipse((px+pad-r,py+pad-r,px+pad+r,py+pad+r),fill=(10,10,10,255))
        return out
