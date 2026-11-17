import json,math,subprocess,glob,os,sys,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'.')
from rig import SadRoofer
from hdhost import HostHD
exec(open('frames.py').read().split("def place")[0])   # gives C dict of cutouts
W,H=1080,1920; FPS=30
words=json.load(open('words.json'))
scenes=[(1,0.0),(2,3.70),(3,9.10),(4,14.55),(5,18.45),(6,21.65),(7,27.95),(8,32.6),(9,43.05),(10,50.35),(11,57.15),(12,58.7)]
END=61.4
bases={n:Image.open(sorted(glob.glob(f'bases2/{n:02d}-*.jpg'))[0]).convert('RGB') for n,_ in scenes}
# audio envelope
wf=wave.open('vo.wav'); a=np.frombuffer(wf.readframes(wf.getnframes()),np.int16).astype(float); sr=wf.getframerate()
hop=sr//FPS; env=np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)) if i*hop<len(a) else 0 for i in range(int(END*FPS)+2)])
env=env/np.percentile(env[env>0],95); env=np.clip(env,0,1.2)
host=HostHD()
ICON={k:Image.open(f'icons/{k}.png').convert('RGBA') for k in ('people','bubbles','money')}; sad=SadRoofer()
def scl(img,h): r=h/img.height; return img.resize((int(img.width*r),h),Image.BILINEAR)
HOSTPOS={k:(520,260,1745) for k in (2,3,4,6,7,8,9,10)}
HOSTPOS[5]=(600,W/2,1430); HOSTPOS[11]=(680,W/2,1400); HOSTPOS[12]=(620,W/2,1380)
capy={1:1450,5:1450,11:1420,12:1420}
CAPX={k:735 for k in (2,3,4,6,7,8,9,10)}
CAPY2={k:1230 for k in (2,3,4,6,7,8,9,10)}
fo=ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',54)
chunks=[];cur=[];_d=ImageDraw.Draw(Image.new('RGB',(10,10)))
for w in words:
    if cur and _d.textlength(' '.join(x['text'] for x in cur+[w]),font=fo)>560: chunks.append(cur);cur=[]
    cur.append(w)
    if len(cur)>=4 or w['text'][-1] in '.,?:!"': chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def scene_at(t):
    s=scenes[0]
    for sc in scenes:
        if t>=sc[1]: s=sc
    return s
def speaking(t): return any(w['start']-0.05<=t<=w['end']+0.05 for w in words)
POSEW=[(3.7,5.6,'point_up'),(5.6,9.1,'explain_r'),(9.1,11.7,'shrug'),(11.7,14.5,'present'),(14.5,16.6,'explain_l'),(16.6,18.3,'shrug'),(18.4,21.5,'point_up'),(21.7,27.6,'count'),(27.9,32.4,'count'),(32.6,38.3,'count'),(38.5,43.0,'explain_r'),(43.0,44.5,'present'),(44.5,47.6,'explain_l'),(47.7,49.1,'explain_r'),(49.1,50.4,'cheer'),(50.4,53.7,'present'),(53.7,57.1,'explain_r'),(57.1,58.7,'shrug'),(58.7,61.4,'point_up')]
def pose_at(t):
    for a_,b_,p_ in POSEW:
        if a_<=t<b_: return p_
    return 'rest'
def put(fr,img,cx,bottom,dy=0): fr.alpha_composite(img,(int(cx-img.width/2),int(bottom-img.height+dy)))
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','vo.mp3','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','lesson-v12.mp4'],stdin=subprocess.PIPE)
for i in range(int(END*FPS)):
    t=i/FPS; n,st=scene_at(t); dt=t-st
    nxt=[sc[1] for sc in scenes if sc[1]>st]; dur=(nxt[0] if nxt else END)-st
    z=1.0+0.03*min(dt/dur,1); b=bases[n]; cw,ch=int(W/z),int(H/z)
    fr=b.crop(((W-cw)//2,(H-ch)//2,(W-cw)//2+cw,(H-ch)//2+ch)).resize((W,H),Image.BILINEAR).convert('RGBA')
    if dt<0.22 and n>1:
        a_=dt/0.22; fr2=Image.new('RGBA',(W,H),(255,255,255,255)); fr2.paste(fr,(0,int((1-a_)*50))); fr=Image.blend(Image.new('RGBA',(W,H),(255,255,255,255)),fr2,a_)
    d=ImageDraw.Draw(fr)
    if n==1:
        put(fr,scl(sad.frame(t),780),330,1420)
        # phone buzz with 0 calls
    if n in HOSTPOS:
        h,cx,bt=HOSTPOS[n]
        img=scl(host.frame(t,float(env[i]),speaking(t),pose_at(t)),int(h))
        put(fr,img,cx,bt)
    if n==9:
        for (cx,t0,ic) in ((200,44.64,'people'),(540,46.4,'bubbles'),(880,49.2,'money')):
            if t>=t0:
                k=min(1,(t-t0)/0.25); sc=0.6+0.4*k+0.08*math.sin(min(1,k)*math.pi)
                im_=ICON[ic].resize((int(260*sc),int(260*sc)),Image.LANCZOS)
                fr.alpha_composite(im_,(int(cx-im_.width/2),int(640-im_.height/2)))
    ch_=None
    for c in chunks:
        if c[0]['start']-0.05<=t<=c[-1]['end']+0.15: ch_=c
    if ch_:
        line=' '.join(w['text'] for w in ch_); tw=d.textlength(line,font=fo); y=CAPY2.get(n,capy.get(n,1150)); x0=CAPX.get(n,W/2)-tw/2; x0=min(max(x0,40),W-40-tw)
        d.rounded_rectangle((x0-30,y-14,x0+tw+30,y+76),24,fill=(20,20,24,235)); x=x0
        for w in ch_:
            d.text((x,y),w['text'],font=fo,fill=(251,197,80) if w['start']<=t<=w['end']+0.05 else (255,255,255)); x+=d.textlength(w['text']+' ',font=fo)
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('done')
