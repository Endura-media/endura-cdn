from PIL import Image, ImageDraw, ImageFont
import os
EU='/home/claude/eu/'
OUT=os.environ.get('OUTDIR','/home/claude/lesson/frames/'); os.makedirs(OUT,exist_ok=True)
W,H=1080,1920
NAVY=(14,32,51); GOLD=(184,134,11); RED=(205,50,50); GREY=(110,118,128); LIGHT=(242,239,232); WHITE=(255,255,255); GREEN=(46,139,87)
F='/usr/share/fonts/opentype/inter/'
def f(n,s): return ImageFont.truetype(F+n,s)
BLK=lambda s:f('InterDisplay-Black.otf',s); XB=lambda s:f('InterDisplay-ExtraBold.otf',s); SB=lambda s:f('Inter-SemiBold.otf',s); MD=lambda s:f('Inter-Medium.otf',s)

def cut(sheet,box):
    im=Image.open(EU+sheet).convert('RGBA').crop(box)
    w,h=im.size
    mask=Image.new('L',(w+2,h+2),0)
    rgb=Image.new('RGB',(w+2,h+2),(255,255,255)); rgb.paste(im.convert('RGB'),(1,1))
    ImageDraw.floodfill(rgb,(0,0),(255,0,255),thresh=38)
    px=rgb.load(); a=im.split()[3].load()
    out=im.copy(); op=out.load()
    for y in range(h):
        for x in range(w):
            if px[x+1,y+1]==(255,0,255): op[x,y]=(255,255,255,0)
    bb=out.getbbox(); return out.crop(bb)
C={
 'roof_sad':(lambda im:im.crop(im.getbbox()))(Image.open('/home/claude/lesson/roof_sad.png').convert('RGBA')),
 'host_talk':cut('endura_media_host_character_bible.png',(828,790,1142,1040)),
 'host_point':cut('endura_media_host_character_bible.png',(888,415,1108,745)),
 'roof_front':cut('roofer_character_bible_sheet.png',(383,8,557,362)),
 'roof_hammer':cut('roofer_character_bible_sheet.png',(868,412,1097,738)),
 'roof_phone':cut('roofer_character_bible_sheet.png',(438,783,692,1040)),
 'mom_phone':cut('endura_media_character_cast_sheet.png',(548,8,768,318)),
 'owner_cheer':cut('endura_media_character_cast_sheet.png',(1092,742,1322,1018)),
}
NOCHAR=os.environ.get('NOCHAR')=='1'
def place(img,key,h,cx,bottom):
    if NOCHAR: return
    c=C[key]; r=h/c.height; c=c.resize((int(c.width*r),h),Image.LANCZOS)
    img.alpha_composite(c,(int(cx-c.width/2),int(bottom-h)))
NOHOST=os.environ.get('NOHOST')=='1'
def base(n):
    CUR[0]=n
    im=Image.new('RGBA',(W,H),WHITE+(255,)); d=ImageDraw.Draw(im)
    # pill
    t='ENDURA LESSONS'; fo=SB(30); tw=d.textlength(t,font=fo)
    d.rounded_rectangle((60,70,60+tw+48,124),27,fill=NAVY); d.text((84,80),t,font=fo,fill=WHITE)
    d.text((W-60,80),f'{n:02d}',font=SB(30),fill=GREY,anchor='ra')
    return im,d
def center(d,y,text,fo,fill=NAVY,maxw=940,lh=1.12):
    words=text.split(); lines=[]; cur=''
    for w_ in words:
        t=(cur+' '+w_).strip()
        if d.textlength(t,font=fo)<=maxw: cur=t
        else: lines.append(cur); cur=w_
    lines.append(cur)
    for l in lines:
        d.text((W/2,y),l,font=fo,fill=fill,anchor='ma'); y+=int(fo.size*lh)
    return y
HOSTF=set()
CUR=[0]
def corner(im,key='host_talk'):
    HOSTF.add(CUR[0])
    if not NOHOST: place(im,key,420,290,1660)
def save(im,n,name): im.convert('RGB').save(f'{OUT}{n:02d}-{name}.jpg',quality=90)

# 1 hook
im,d=base(1)
y=center(d,230,'Struggling to',BLK(108)); y=center(d,y,'find work?',BLK(108),fill=RED)
d.text((W/2,500),'If you\'re a contractor, watch this.',font=SB(42),fill=GREY,anchor='ma')
place(im,'roof_sad',780,330,1420)
# empty calendar
d.rounded_rectangle((600,640,990,1010),28,fill=WHITE,outline=(210,205,195),width=4)
d.rounded_rectangle((600,640,990,720),28,fill=RED); d.rectangle((600,690,990,720),fill=RED)
d.text((795,655),'THIS WEEK',font=XB(36),fill=WHITE,anchor='ma')
for r in range(3):
    for c in range(5):
        x=630+c*70; yy=745+r*70; d.rounded_rectangle((x,yy,x+50,yy+50),8,outline=(225,225,225),width=3)
d.text((795,960),'0 jobs booked',font=XB(36),fill=RED,anchor='ma')
# phone no calls
d.rounded_rectangle((660,1060,930,1400),36,fill=NAVY); d.rounded_rectangle((680,1100,910,1360),18,fill=WHITE)
d.text((795,1150),'Calls',font=SB(32),fill=GREY,anchor='ma'); d.text((795,1210),'0',font=BLK(90),fill=RED,anchor='ma'); d.text((795,1320),'new today',font=MD(28),fill=GREY,anchor='ma')
save(im,1,'hook')
# 2 stat
im,d=base(2)
d.text((W/2,220),'5 out of 10',font=BLK(130),fill=GOLD,anchor='ma')
center(d,380,'people use AI like ChatGPT to find local services',XB(60))
# 10 people icons
for i in range(10):
    x=140+i*88; col=GOLD if i<5 else (215,215,215)
    d.ellipse((x-24,620,x+24,668),fill=col); d.rounded_rectangle((x-34,676,x+34,770),26,fill=col)
corner(im); save(im,2,'stat')
# 3 price question
im,d=base(3)
center(d,220,'A lot of what they ask',XB(66)); center(d,300,'is about price.',XB(66),fill=GOLD)
d.rounded_rectangle((110,450,970,640),44,fill=LIGHT,outline=(220,215,205),width=3)
d.text((150,480),'ChatGPT',font=SB(30),fill=GREY)
center(d,530,'"How much does interior demolition cost?"',SB(44),maxw=780)
corner(im); save(im,3,'price-question')
# 4 AI quotes whoever did
im,d=base(4)
center(d,220,'No price on your site?',XB(68)); center(d,310,'AI quotes whoever did.',XB(68),fill=RED)
d.rounded_rectangle((110,460,970,960),40,fill=WHITE,outline=(220,215,205),width=3)
d.text((150,495),'AI answer',font=SB(32),fill=GREY)
for i,(w_,c) in enumerate([(700,(225,225,225)),(620,(225,225,225)),(680,(225,225,225))]):
    d.rounded_rectangle((150,560+i*60,150+w_,590+i*60),15,fill=c)
d.rounded_rectangle((150,760,930,900),24,fill=(253,236,236),outline=RED,width=3)
d.text((185,790),'Source: a competitor\'s price page',font=SB(38),fill=RED)
d.text((185,845),'Not you.',font=XB(38),fill=NAVY)
corner(im); save(im,4,'ai-quotes-competitor')
# 5 one way
im,d=base(5)
d.text((W/2,300),'1 way to',font=BLK(110),fill=NAVY,anchor='ma')
d.text((W/2,430),'show up',font=BLK(110),fill=GOLD,anchor='ma')
center(d,600,'when people search for pricing',XB(62))
place(im,'host_point',640,W/2+120,1400)
save(im,5,'one-way')
# 6-8 steps on a mock page
def page(d,top=420):
    d.rounded_rectangle((90,top,990,top+680),36,fill=WHITE,outline=(210,205,195),width=4)
    d.rounded_rectangle((90,top,990,top+70),36,fill=LIGHT); d.rectangle((90,top+40,990,top+70),fill=LIGHT)
    for i,c in enumerate([(236,106,94),(244,191,79),(98,197,84)]): d.ellipse((125+i*42,top+22,151+i*42,top+48),fill=c)
    d.text((280,top+20),'yoursite.com/your-service',font=MD(28),fill=GREY)
def step(n,title):
    im,d=base(5+n)
    d.text((90,200),f'STEP {n}',font=BLK(44),fill=GOLD)
    center(d,262,title,XB(56),maxw=900)
    page(d); return im,d
im,d=step(1,'Add a section to your main service page')
d.rounded_rectangle((130,540,950,720),20,fill=(255,247,224),outline=GOLD,width=4)
center(d,565,'How much does [your service] cost in [your city]?',XB(46),maxw=760)
for i in range(4): d.rounded_rectangle((140,780+i*60,140+[760,700,740,600][i],806+i*60),13,fill=(230,230,230))
corner(im); save(im,6,'step1-section')
im,d=step(2,'Answer in the first sentence')
d.text((140,540),'How much does [your service] cost?',font=XB(38),fill=NAVY)
d.rounded_rectangle((130,610,950,760),20,fill=(255,247,224),outline=GOLD,width=4)
center(d,635,'"Most jobs in [your city] run [your real price range]."',SB(42),maxw=760)
for i in range(3): d.rounded_rectangle((140,810+i*60,140+[740,680,560][i],836+i*60),13,fill=(230,230,230))
d.text((W/2,1050),'Use YOUR real prices',font=XB(40),fill=RED,anchor='ma')
corner(im); save(im,7,'step2-first-sentence')
im,d=step(3,'Add a small price table')
cols=['Job type','Price range','What changes it']; xs=[130,400,650]; y0=540
d.rectangle((130,y0,950,y0+80),fill=NAVY)
for x,c in zip(xs,cols): d.text((x+18,y0+24),c,font=SB(29),fill=WHITE)
for i,r in enumerate(['Repair','Partial replacement','Full replacement']):
    y=y0+80+i*110; d.rectangle((130,y,950,y+110),fill=WHITE if i%2 else LIGHT,outline=(220,215,205))
    d.text((148,y+20),r,font=SB(32),fill=NAVY) if len(r)<12 else [d.text((148,y+14),r.split()[0],font=SB(32),fill=NAVY),d.text((148,y+54),r.split()[1],font=SB(32),fill=NAVY)]
    d.text((418,y+36),'[your range]',font=MD(30),fill=GREY); d.text((668,y+36),'[size, materials]',font=MD(28),fill=GREY)
d.text((W/2,1000),'Example: a roofer',font=SB(36),fill=GREY,anchor='ma')
place(im,'roof_hammer',420,W-230,1640)
corner(im); save(im,8,'step3-table')
# 9 goal flow
im,d=base(9)
center(d,220,'The goal is simple.',XB(70))
labels=[('More eyeballs',NAVY),('More conversations',GOLD),('More jobs',GREEN)]
for i,(t,c) in enumerate(labels):
    y=420+i*230; d.rounded_rectangle((200,y,880,y+150),75,fill=c); d.text((W/2,y+45),t,font=BLK(56),fill=WHITE,anchor='ma')
    if i<2: d.polygon([(W/2-30,y+165),(W/2+30,y+165),(W/2,y+215)],fill=(200,200,200))
place(im,'owner_cheer',430,W-230,1640)
corner(im); save(im,9,'goal')
# 10 proof (screenshot slot open)
im,d=base(10)
center(d,220,'A business we work with got a lead from ChatGPT',XB(56))
d.text((W/2,400),'$5,370',font=BLK(150),fill=GREEN,anchor='ma')
d.text((W/2,570),'PAID',font=BLK(46),fill=GREEN,anchor='ma')
d.rounded_rectangle((110,660,970,1110),30,outline=GREY,width=5)

center(d,820,'WHATCONVERTS SCREENSHOT',BLK(46),fill=GREY); center(d,890,'(source: chatgpt.com, blurred)',MD(34),fill=GREY)
corner(im); save(im,10,'proof-SLOT-OPEN')
# 11 still not worth it
im,d=base(11)
y=center(d,300,'Still don\'t think',BLK(104)); center(d,y,'it\'s worth it?',BLK(104),fill=RED)
place(im,'host_talk',620,W/2,1350)
save(im,11,'still-not-worth-it')
# 12 end
im,d=base(12)
center(d,300,'Follow for more tactics on',XB(66)); center(d,390,'showing up online',BLK(84),fill=GOLD)
place(im,'roof_phone',620,W/2,1330)
d.rounded_rectangle((340,1420,740,1500),40,fill=NAVY); d.text((W/2,1440),'ENDURA LESSONS',font=SB(36),fill=WHITE,anchor='ma')
save(im,12,'end')
print('ok',sorted(HOSTF))
