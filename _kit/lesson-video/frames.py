from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
W,H=1080,1920
BG=(255,255,255); NAVY=(14,32,51); GOLD=(184,134,11); WHITE=(14,32,51); GRAY=(110,122,138)
CARD=(246,247,249); BORDER=(222,227,234); RED=(205,50,50); GREEN=(60,200,120)
F="/usr/share/fonts/opentype/inter/"
def f(n,s): return ImageFont.truetype(F+n,s)
BLACK=lambda s:f("InterDisplay-Black.otf",s)
SEMI=lambda s:f("Inter-SemiBold.otf",s)
REG=lambda s:f("Inter-Regular.otf",s)
BOLD=lambda s:f("InterDisplay-Bold.otf",s)
def base():
    return Image.new("RGB",(W,H),BG)
def ctext(d,y,t,font,fill,track=0):
    w=d.textlength(t,font=font); d.text(((W-w)/2,y),t,font=font,fill=fill)
def pill(d,y,t):
    font=SEMI(30); w=d.textlength(t,font=font)+60
    x=(W-w)/2; d.rounded_rectangle((x,y,x+w,y+62),31,outline=GOLD,width=3)
    ctext(d,y+13,t,font,GOLD)
def cell(d,cx,cy,num,lab,col=WHITE,box=None):
    nf=BLACK(80); lf=REG(34)
    if box:
        d.rounded_rectangle((cx-125,cy-20,cx+125,cy+160),24,outline=box,width=4)
    w=d.textlength(num,font=nf); d.text((cx-w/2,cy),num,font=nf,fill=col)
    w=d.textlength(lab,font=lf); d.text((cx-w/2,cy+102),lab,font=lf,fill=GRAY)
def op(d,cx,cy,t):
    of=BLACK(52); w=d.textlength(t,font=of); d.text((cx-w/2,cy+18),t,font=of,fill=GRAY)
COLS=[215,515,800]; OPS=[365,660]
ROWS=[330,610,890,1170]
def board(step):
    im=base(); d=ImageDraw.Draw(im); pill(d,190,"THE MATH")
    d.rounded_rectangle((70,290,940,1420),28,fill=CARD,outline=BORDER,width=2)
    if step>=1:
        cell(d,COLS[0],ROWS[0],"$450","spend"); op(d,OPS[0],ROWS[0],"÷")
        cell(d,COLS[1],ROWS[0],"10","leads"); op(d,OPS[1],ROWS[0],"=")
        cell(d,COLS[2],ROWS[0],"$45","per lead",GOLD)
    if step>=2:
        cell(d,COLS[0],ROWS[1],"2","jobs"); op(d,OPS[0],ROWS[1],"of")
        cell(d,COLS[1],ROWS[1],"10","leads"); op(d,OPS[1],ROWS[1],"=")
        cell(d,COLS[2],ROWS[1],"20%","close rate",GOLD)
    if step>=3:
        cell(d,COLS[0],ROWS[2],"$225","cost to win",RED,GOLD); op(d,515,ROWS[2],"vs")
        cell(d,COLS[2],ROWS[2],"$220","job pays",WHITE,GOLD)
    if step>=4:
        cell(d,COLS[0],ROWS[3],"$450","out"); op(d,OPS[0],ROWS[3],"−")
        cell(d,COLS[1],ROWS[3],"$440","in"); op(d,OPS[1],ROWS[3],"=")
        cell(d,COLS[2],ROWS[3],"-$10","per week",RED)
    return im
def brk():
    im=base(); d=ImageDraw.Draw(im)
    ctext(d,780,"Let's break",BLACK(130),WHITE); ctext(d,940,"it down.",BLACK(130),GOLD)
    return im
def hook():
    im=base(); d=ImageDraw.Draw(im); pill(d,560,"ENDURA LESSONS  #01")
    ctext(d,680,"Your",BLACK(170),WHITE); ctext(d,880,"true cost",BLACK(170),GOLD)
    return im
def before():
    im=base(); d=ImageDraw.Draw(im)
    ctext(d,600,"-$10",BLACK(220),RED); ctext(d,860,"a week",SEMI(64),GRAY)
    ctext(d,1010,"before supplies,",BLACK(76),WHITE); ctext(d,1105,"gas and their time",BLACK(76),WHITE)
    return im
def lesson():
    im=base(); d=ImageDraw.Draw(im); pill(d,420,"TRACK 3 NUMBERS")
    y=540
    for n,t in [("1","Per lead"),("2","Per job"),("3","Job pays")]:
        d.rounded_rectangle((220,y,860,y+170),28,fill=CARD,outline=BORDER,width=2)
        d.text((280,y+40),n,font=BLACK(80),fill=GOLD); d.text((390,y+48),t,font=BLACK(70),fill=WHITE); y+=200
    return im
def cut():
    im=base(); d=ImageDraw.Draw(im); y=700
    for t,c in [("Costs more",WHITE),("than it pays?",WHITE),("Cut back.",GOLD)]:
        ctext(d,y,t,BLACK(120),c); y+=150
    return im
def end():
    im=base(); d=ImageDraw.Draw(im); y=640
    for t,c in [("Or you'll go",WHITE),("out of",GOLD),("business.",GOLD)]:
        ctext(d,y,t,BLACK(130),c); y+=160
    pill(d,1180,"ENDURA LESSONS  #01")
    return im
out="/home/claude/v008/frames"; os.makedirs(out,exist_ok=True)
frames=[("01_hook",hook()),("01b_break",brk())]+[(f"0{i+1}_board{i}",board(i)) for i in range(1,5)]+[("06_before",before()),("07_lesson",lesson()),("08_cut",cut()),("09_end",end())]
for n,im in frames: im.save(f"{out}/{n}.png")
# contact sheet
tw,th=270,480; sheet=Image.new("RGB",(tw*5+60,th*2+30),(120,120,120))
for i,(n,im) in enumerate(frames):
    t=im.resize((tw,th)); sheet.paste(t,(10+(i%5)*(tw+10),10+(i//5)*(th+10)))
sheet.save("/home/claude/v008/sheet.png")
