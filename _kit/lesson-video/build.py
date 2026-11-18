import json, subprocess, sys, os, re
from PIL import Image, ImageDraw
src=open("frames.py").read().split('out="/home/claude/v008/frames"')[0]
exec(src)
VO=sys.argv[1]; HOOK="hook_clip.mp4"; OUT=sys.argv[2] if len(sys.argv)>2 else "V008-H1-B1-C0.mp4"
SPEED=1.12; FPS=30
subprocess.run(["ffmpeg","-v","error","-y","-i",VO,"-af",f"atempo={SPEED}","-ar","44100","-ac","1","vo.wav"],check=True)
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","vo.wav"]).decode())
PH=[("Do you know your ad budget?","Do you know your ad budget?"),
("I audited a cleaning business, and for the last three months they were spending four hundred fifty dollars a week and getting about ten leads.","I audited a cleaning business, and for the last 3 months they were spending $450 a week and getting about 10 leads."),
("Let's break this down.","Let's break this down."),
("That's forty-five dollars a lead.","That's $45 a lead."),
("They closed two of those ten.","They closed 2 of those 10."),
("That's a twenty percent close rate.","That's a 20% close rate."),
("So we take four hundred fifty and divide it by the two jobs they won, and we get two hundred twenty-five.","So we take $450 and divide it by the 2 jobs they won, and we get $225."),
("That means it costs two hundred twenty-five dollars to win one job.","That means it costs $225 to win 1 job."),
("They told me each job paid two hundred twenty.","They told me each job paid $220."),
("So they paid four hundred fifty and made four hundred forty.","So they paid $450 and made $440."),
("They lost ten dollars a week, and that's before supplies, gas, and their time.","They lost $10 a week, and that's before supplies, gas and their time."),
("To avoid this, track these three numbers: what you spend per lead, what you spend per job, and what each job pays.","To avoid this, track these 3 numbers: what you spend per lead, what you spend per job, and what each job pays."),
("If it costs more to win the job than the job pays, cut back until you find your real ad budget,","If it costs more to win the job than the job pays, cut back until you find your real ad budget,"),
("or you'll go out of business.","or you'll go out of business.")]
# word-level timing (ElevenLabs Scribe, adjusted for speed)
WJ=json.load(open("words.json"))
PW=[];k=0
for sp,_ in PH:
    n=len(sp.split()); PW.append(WJ[k:k+n]); k+=n
segs=[[p[0][1],p[-1][2]] for p in PW]
print("segments",len(segs),"phrases",len(PH))
def norm(x): return re.sub(r"[^a-z0-9'-]","",x.lower())
def at(i,key,occ=0):
    ks=[norm(x) for x in key.split()]; ws=[norm(x[0]) for x in PW[i]]; c=0
    for j in range(len(ws)-len(ks)+1):
        if ws[j:j+len(ks)]==ks:
            if c==occ: return PW[i][j][1]
            c+=1
    return segs[i][0]
ev=[] # (time, kind, payload)
def E(t,k,p=None): ev.append((t,k,p))
E(0,"scene","hook")
E(segs[1][0]-0.05,"scene","audit"); E(segs[1][0]-0.05,"sfx","whoosh")
E(at(1,"four hundred fifty")-0.1,"scene","big450"); E(at(1,"four hundred fifty")-0.1,"sfx","pop")
E(at(1,"ten leads")-0.1,"scene","big10"); E(at(1,"ten leads")-0.1,"sfx","pop")
E(segs[2][0],"scene","break"); E(segs[2][0],"sfx","whoosh")
E(segs[3][0]-0.05,"scene","board"); E(segs[3][0]-0.05,"sfx","whoosh")
E(segs[3][0],"show","r1a"); E(segs[3][0]+0.25,"show","r1b"); E(at(3,"forty-five"),"show","r1c")
E(at(4,"two"),"show","r2a"); E(at(4,"ten"),"show","r2b"); E(at(5,"twenty"),"show","r2c")
E(at(6,"four hundred fifty"),"show","r3a"); E(at(6,"two jobs"),"show","r3b"); E(at(6,"two hundred twenty-five"),"show","r3c")
E(at(7,"two hundred twenty-five"),"show","r4a"); E(at(8,"two hundred twenty"),"show","r4b"); E(at(8,"two hundred twenty")+0.25,"show","r4gold")
E(at(9,"four hundred fifty"),"show","r5a"); E(at(9,"four hundred forty"),"show","r5b"); E(at(10,"lost"),"show","r5c")
E(at(10,"before"),"scene","before"); E(at(10,"before"),"sfx","whoosh")
E(segs[11][0]-0.05,"scene","trackbig"); E(segs[11][0]-0.05,"sfx","whoosh")
E(at(11,"what you spend per lead")-0.05,"scene","lesson"); E(at(11,"what you spend per lead")-0.05,"sfx","whoosh")
E(at(11,"per lead"),"show","l1"); E(at(11,"per job"),"show","l2"); E(at(11,"each job pays"),"show","l3")
E(segs[12][0]-0.05,"scene","cut"); E(segs[12][0]-0.05,"sfx","whoosh"); E(at(12,"cut back"),"show","cutback")
E(segs[13][0]-0.05,"scene","end"); E(segs[13][0]-0.05,"sfx","thud")
for t,k,p in list(ev):
    if k=="show":
        E(t,"sfx",{"r4gold":"ding","r5c":"buzz"}.get(p,"pop"))
ev.sort(key=lambda e:e[0])
# captions: word-timed units, numbers shown as digits
REP=[("four hundred fifty dollars","$450"),("four hundred fifty","$450"),("four hundred forty","$440"),("two hundred twenty-five dollars","$225"),("two hundred twenty-five","$225"),("two hundred twenty","$220"),("forty-five dollars","$45"),("ten dollars","$10"),("three months","3 months"),("three numbers","3 numbers"),("twenty percent","20%"),("ten leads","10 leads"),("those ten","those 10"),("two of","2 of"),("two jobs","2 jobs"),("one job","1 job")]
caps=[]
for i in range(1,len(PW)):
    toks=PW[i]; units=[]; j=0
    while j<len(toks):
        hit=None
        for pat,dig in REP:
            ps=pat.split()
            if [norm(x[0]) for x in toks[j:j+len(ps)]]==ps:
                last=toks[j+len(ps)-1][0]; trail=re.sub(r"^.*?([.,:?]*)$",r"\1",last)
                hit=(dig+trail,toks[j][1],toks[j+len(ps)-1][2],len(ps)); break
        if hit: units.append(hit[:3]); j+=hit[3]
        else: units.append((toks[j][0],toks[j][1],toks[j][2])); j+=1
    chunks=[units[x:x+4] for x in range(0,len(units),4)]
    for ci,ch in enumerate(chunks):
        st=ch[0][1]; en=chunks[ci+1][0][1] if ci+1<len(chunks) else ch[-1][2]+0.25
        caps.append((st,en," ".join(u[0] for u in ch)))
END=segs[-1][1]+1.2
# drawing
def board_img(vis):
    im=base(); d=ImageDraw.Draw(im); pill(d,190,"THE MATH")
    d.rounded_rectangle((70,290,940,1440),28,fill=CARD,outline=BORDER,width=2)
    R=[315,540,765,990,1215]
    if "r1a" in vis: cell(d,COLS[0],R[0],"$450","spend")
    if "r1b" in vis: op(d,OPS[0],R[0],"÷"); cell(d,COLS[1],R[0],"10","leads")
    if "r1c" in vis: op(d,OPS[1],R[0],"="); cell(d,COLS[2],R[0],"$45","per lead",GOLD)
    if "r2a" in vis: cell(d,COLS[0],R[1],"2","jobs")
    if "r2b" in vis: op(d,OPS[0],R[1],"of"); cell(d,COLS[1],R[1],"10","leads")
    if "r2c" in vis: op(d,OPS[1],R[1],"="); cell(d,COLS[2],R[1],"20%","close rate",GOLD)
    if "r3a" in vis: cell(d,COLS[0],R[2],"$450","spend")
    if "r3b" in vis: op(d,OPS[0],R[2],"÷"); cell(d,COLS[1],R[2],"2","jobs")
    if "r3c" in vis: op(d,OPS[1],R[2],"="); cell(d,COLS[2],R[2],"$225","1 job booked",GOLD)
    g="r4gold" in vis
    if "r4a" in vis: cell(d,COLS[0],R[3],"$225","cost to win",RED,GOLD if g else None)
    if "r4b" in vis: op(d,515,R[3],"vs"); cell(d,COLS[2],R[3],"$220","job pays",WHITE,GOLD if g else None)
    if "r5a" in vis: cell(d,COLS[0],R[4],"$450","out")
    if "r5b" in vis: op(d,OPS[0],R[4],"−"); cell(d,COLS[1],R[4],"$440","in")
    if "r5c" in vis: op(d,OPS[1],R[4],"="); cell(d,COLS[2],R[4],"-$10","per week",RED)
    return im
def lesson_img(vis):
    im=base(); d=ImageDraw.Draw(im); y=560
    for k,n,t in [("l1","1","Per lead"),("l2","2","Per job"),("l3","3","Job pays")]:
        if k in vis:
            d.rounded_rectangle((220,y,860,y+170),28,fill=CARD,outline=BORDER,width=2)
            d.text((280,y+40),n,font=BLACK(80),fill=GOLD); d.text((390,y+48),t,font=BLACK(70),fill=WHITE)
        y+=200
    return im
def cut_img(vis):
    im=base(); d=ImageDraw.Draw(im); y=640
    for t,c in [("Costs more",WHITE),("than it pays?",WHITE)]:
        ctext(d,y,t,BLACK(120),c); y+=150
    if "cutback" in vis: ctext(d,y+30,"Cut back.",BLACK(140),GOLD)
    return im
def break_img():
    im=base(); d=ImageDraw.Draw(im)
    ctext(d,760,"Let's break",BLACK(130),WHITE); ctext(d,920,"it down.",BLACK(130),GOLD); return im
def end_img(dt=10):
    im=base(); d=ImageDraw.Draw(im)
    oy=-200
    d.polygon([(540,470+oy),(300,680+oy),(780,680+oy)],outline=NAVY,width=10)
    d.rectangle((340,680+oy,740,1000+oy),outline=NAVY,width=10)
    d.rectangle((380,730+oy,560,880+oy),fill=(225,236,246),outline=NAVY,width=8)
    d.rectangle((610,800+oy,700,1000+oy),outline=NAVY,width=8)
    p1=min(max(dt/0.18,0),1); p2=min(max((dt-0.18)/0.18,0),1)
    x0,y0,x1,y1=260,230,820,840
    if p1>0: d.line((x0,y0,x0+(x1-x0)*p1,y0+(y1-y0)*p1),fill=RED,width=34)
    if p2>0: d.line((x1,y0,x1-(x1-x0)*p2,y0+(y1-y0)*p2),fill=RED,width=34)
    y=930
    for t,c in [("Or you'll go",NAVY),("out of business.",RED)]:
        ctext(d,y,t,BLACK(110),c); y+=140
    pill(d,1260,"ENDURA LESSONS  #01"); return im
def hook_overlay(fr):
    from PIL import ImageFilter
    W_,H_=fr.size
    shade=Image.new("L",(W_,H_),0); sd=ImageDraw.Draw(shade); sd.rectangle((0,900,W_,1560),fill=150)
    shade=shade.filter(ImageFilter.GaussianBlur(60)); fr=Image.composite(Image.new("RGB",(W_,H_),(8,18,30)),fr,shade)
    d=ImageDraw.Draw(fr)
    pf=SEMI(30); t="ENDURA LESSONS  #01"; w=d.textlength(t,font=pf)+56; x=(W_-w)/2
    d.rounded_rectangle((x,960,x+w,1016),28,fill=(240,190,60)); d.text((x+28,969),t,font=pf,fill=(14,32,51))
    def big(y,txt,col,size):
        f=BLACK(size); w=d.textlength(txt,font=f)
        d.text(((W_-w)/2,y),txt,font=f,fill=col,stroke_width=6,stroke_fill=(8,18,30))
    big(1050,"DO YOU KNOW",(255,255,255),104)
    big(1175,"YOUR AD BUDGET?",(240,190,60),84)
    f=BLACK(52); t1="This will save you "; t2="$1,000s"; w1=d.textlength(t1,font=f); w2=d.textlength(t2,font=f); x=(W_-w1-w2)/2
    d.text((x,1300),t1,font=f,fill=(255,255,255),stroke_width=4,stroke_fill=(8,18,30))
    d.text((x+w1,1300),t2,font=f,fill=(60,200,120),stroke_width=4,stroke_fill=(8,18,30))
    return fr
def caption(im,text):
    d=ImageDraw.Draw(im); f=SEMI(46); w=d.textlength(text,font=f)
    if w>860:
        f=SEMI(40); w=d.textlength(text,font=f)
    x=(W-w)/2; d.rounded_rectangle((x-28,1448,x+w+28,1530),22,fill=(238,241,245)); d.text((x,1462),text,font=f,fill=NAVY)
    return im
# hook clip frames
os.makedirs("hk",exist_ok=True)
subprocess.run(["ffmpeg","-v","error","-y","-i",HOOK,"-vf",f"fps={FPS}","hk/%04d.png"],check=True)
hk=sorted(os.listdir("hk"))
cache={}
import math
def star(d,cx,cy,r,col):
    d.polygon([(cx,cy-r),(cx+r*0.28,cy-r*0.28),(cx+r,cy),(cx+r*0.28,cy+r*0.28),(cx,cy+r),(cx-r*0.28,cy+r*0.28),(cx-r,cy),(cx-r*0.28,cy-r*0.28)],fill=col)
def audit_img(t):
    im=base(); d=ImageDraw.Draw(im); pill(d,330,"THE AUDIT")
    # house
    d.polygon([(540,470),(300,680),(780,680)],outline=NAVY,width=10)
    d.rectangle((340,680,740,1000),outline=NAVY,width=10)
    d.rectangle((380,730,560,880),fill=(225,236,246),outline=NAVY,width=8)
    d.rectangle((610,800,700,1000),outline=NAVY,width=8)
    # sponge wiping the window
    p=(math.sin(t*5)+1)/2; sx=395+p*110; sy=760+((math.sin(t*10)+1)/2)*60
    d.rounded_rectangle((sx,sy,sx+56,sy+40),10,fill=GOLD)
    for i,(x,y) in enumerate([(410,750),(530,850),(470,800)]):
        a=(math.sin(t*6+i*2)+1)/2
        if a>0.4: star(d,x,y,10+14*a,(240,190,60))
    ctext(d,1080,"A cleaning business",BLACK(76),NAVY)
    f=SEMI(40); tt="Last 3 months"; w=d.textlength(tt,font=f)+60; x=(W-w)/2
    d.rounded_rectangle((x,1200,x+w,1270),35,fill=CARD,outline=BORDER,width=2); ctext(d,1212,tt,f,GRAY)
    return im
def bignum(num,lab):
    im=base(); d=ImageDraw.Draw(im)
    ctext(d,700,num,BLACK(260),NAVY); ctext(d,1010,lab,SEMI(70),GRAY); return im
BIG450=None; BIG10=None
HOOKW=["DO","YOU","KNOW","YOUR","AD","BUDGET?"]
def hook_frame(n,save):
    im=base(); d=ImageDraw.Draw(im); pill(d,640,"ENDURA LESSONS  #01")
    l1=" ".join(HOOKW[:3]); l2=" ".join(HOOKW[3:])
    f1=BLACK(104); f2=BLACK(84)
    w1=d.textlength(l1,font=f1); x=(W-w1)/2
    for i,wd in enumerate(HOOKW[:3]):
        if i<n: d.text((x,760),wd,font=f1,fill=WHITE)
        x+=d.textlength(wd+" ",font=f1)
    w2=d.textlength(l2,font=f2); x=(W-w2)/2
    for i,wd in enumerate(HOOKW[3:]):
        if i+3<n: d.text((x,885),wd,font=f2,fill=GOLD)
        x+=d.textlength(wd+" ",font=f2)
    if save:
        f=BLACK(52); t1="This will save you "; t2="$1,000s"; a=d.textlength(t1,font=f); b=d.textlength(t2,font=f); x=(W-a-b)/2
        d.text((x,1030),t1,font=f,fill=WHITE); d.text((x+a,1030),t2,font=f,fill=(30,150,80))
    return im
def make_hook_card():
    im=base(); d=ImageDraw.Draw(im); pill(d,640,"ENDURA LESSONS  #01")
    ctext(d,760,"DO YOU KNOW",BLACK(104),WHITE); ctext(d,885,"YOUR AD BUDGET?",BLACK(84),GOLD)
    f=BLACK(52); t1="This will save you "; t2="$1,000s"; w1=d.textlength(t1,font=f); w2=d.textlength(t2,font=f); x=(W-w1-w2)/2
    d.text((x,1030),t1,font=f,fill=WHITE); d.text((x+w1,1030),t2,font=f,fill=(30,150,80))
    return im
hook_card=make_hook_card()
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","silent.mp4"],stdin=subprocess.PIPE)
N=int(END*FPS)
for fi in range(N):
    t=fi/FPS; scene="hook"; vis=set(); sstart=0.0
    for et,k,pl in ev:
        if et>t: break
        if k=="scene":
            scene=pl; sstart=et
            if pl in("lesson","cut"): vis={v for v in vis if v.startswith("r")}
        elif k=="show": vis.add(pl)
    if scene=="hook":
        a0,b0=segs[0]; n=3 if t<a0+(b0-a0)*0.45 else 6; sv=False
        k=("hook",n,sv)
        if k not in cache: cache[k]=hook_frame(n,sv)
        fr=cache[k].copy()
    elif scene=="end" and t-sstart<0.5:
        fr=end_img(t-sstart)
    elif scene=="trackbig":
        if "tb" not in cache:
            im=base(); d=ImageDraw.Draw(im)
            ctext(d,720,"Track these",BLACK(130),NAVY); ctext(d,880,"3 numbers",BLACK(150),GOLD); cache["tb"]=im
        fr=cache["tb"].copy()
    elif scene=="audit":
        fr=audit_img(t)
    elif scene=="big450":
        fr=bignum("$450","a week").copy() if "b450" not in cache else cache["b450"].copy()
        cache["b450"]=fr
    elif scene=="big10":
        fr=bignum("10","leads").copy() if "b10" not in cache else cache["b10"].copy()
        cache["b10"]=fr
    else:
        key=(scene,frozenset(v for v in vis if (scene=="board" and v.startswith("r")) or (scene=="lesson" and v.startswith("l")) or (scene=="cut" and v=="cutback")))
        if key not in cache:
            cache[key]={"board":lambda:board_img(vis),"break":break_img,"before":lambda:before(),"lesson":lambda:lesson_img(vis),"cut":lambda:cut_img(vis),"end":lambda:end_img(10)}[scene]()
        fr=cache[key].copy()
    nxt=min([e[0] for e in ev if e[1]=="scene" and e[0]>sstart+1e-6]+[END])
    z=1+0.04*min((t-sstart)/max(nxt-sstart,0.5),1)
    if z>1.0005:
        zw,zh=int(W*z),int(H*z); big=fr.resize((zw,zh),Image.BILINEAR); ox,oy=(zw-W)//2,(zh-H)//2; fr=big.crop((ox,oy,ox+W,oy+H))
    for a,b,c in reversed(caps):
        if a<=t<b and scene not in("hook","end"): fr=caption(fr,c); break
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
# audio mix
inputs=["-i","vo.wav"]; flt=[]; k=1
for et,kind,pl in ev:
    if kind=="sfx":
        inputs+=["-i",f"sfx/{pl}.wav"]; ms=int(max(et,0)*1000); flt.append(f"[{k}]adelay={ms}|{ms}[s{k}]"); k+=1
mix="".join(f"[s{i}]" for i in range(1,k))
fc=";".join(flt)+f";[0]{mix}amix=inputs={k}:normalize=0:duration=first,apad=whole_dur={END}[a]"
subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",fc,"-map","[a]","-ac","2","-ar","44100","mix.wav"],check=True)
subprocess.run(["ffmpeg","-v","error","-y","-i","silent.mp4","-i","mix.wav","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",OUT],check=True)
json.dump({"segs":segs,"ev":[(e[0],e[1],str(e[2])) for e in ev]},open("timeline.json","w"),indent=1)
print("done",OUT,END)
