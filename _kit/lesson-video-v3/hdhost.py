import math
from PIL import Image, ImageDraw
import numpy as np
SRC='art/ORIGINAL_APPROVED_ENDURA_HOST.png'
SKIN=(253,184,114,255)
def cutout():
    im=Image.open(SRC).convert('RGB')
    W,H=im.size
    rgb=Image.new('RGB',(W+2,H+2),(255,255,255)); rgb.paste(im,(1,1))
    ImageDraw.floodfill(rgb,(0,0),(255,0,255),thresh=40)
    m=np.array(rgb)[1:-1,1:-1]
    mask=~((m[:,:,0]==255)&(m[:,:,1]==0)&(m[:,:,2]==255))
    out=im.convert('RGBA'); a=np.array(out); a[:,:,3]=np.where(mask,255,0).astype(np.uint8)
    out=Image.fromarray(a); return out
class HostHD:
    def __init__(self):
        base=cutout()
        self.box=base.getbbox()
        self.base=base
        # closed-eye variant
        cl=base.copy(); d=ImageDraw.Draw(cl)
        for (cx,cy,rx,ry) in ((492.5,441.5,73.5,78.5),(640.5,442,72.5,79)):
            d.ellipse((cx-rx-7,cy-ry-7,cx+rx+7,cy+ry+7),fill=SKIN)
        cl.paste(base.crop((0,0,base.width,356)),(0,0))
        for cx in (497,636):
            d.arc((cx-52,420,cx+52,470),start=15,end=165,fill=(25,25,25,255),width=6)
        self.closed=cl
        # mouth-cleared variant for talking
    def frame(self,t,amp,talking,pose='rest',seed=0):
        ph=(t+seed)%3.3
        im=(self.closed if ph<0.12 else self.base).copy(); d=ImageDraw.Draw(im)
        lvl=min(1,amp*2.2) if talking else 0
        if lvl>=0.12:
            d.rectangle((524,586,612,606),fill=SKIN)
            mx,my=567,592
            w=26+14*lvl; h=8+28*lvl
            d.ellipse((mx-w,my-h*0.35,mx+w,my+h),fill=(120,30,40,255),outline=(25,25,25,255),width=5)
            d.ellipse((mx-w*0.6,my+h*0.35,mx+w*0.6,my+h*0.95),fill=(232,110,140,255))
            d.rectangle((mx-w*0.7,my-h*0.35+5,mx+w*0.7,my-h*0.35+12),fill=(255,255,255,255))
        return im.crop(self.box)
