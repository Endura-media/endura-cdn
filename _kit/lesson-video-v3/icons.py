from PIL import Image, ImageDraw, ImageFont
NAVY=(14,32,51); GOLD=(184,134,11); GREEN=(46,139,87); OUTL=(20,20,24)
K=4; T=260*K
def tile(bg):
    im=Image.new('RGBA',(T,T),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse((0,0,T-1,T-1),fill=bg); return im,d
def s(v): return int(v*K)
# people
im,d=tile((228,234,242,255))
for cx,cy,r,col in ((80,118,26,(70,90,120)),(180,118,26,(70,90,120)),(130,104,32,NAVY)):
    sh=r*1.9
    d.rounded_rectangle((s(cx-sh),s(cy+r+6),s(cx+sh),s(cy+r+6+sh*1.6)),s(sh),fill=col)
    d.ellipse((s(cx-r),s(cy-r),s(cx+r),s(cy+r)),fill=col)
mask=Image.new('L',(T,T),0); ImageDraw.Draw(mask).ellipse((0,0,T-1,T-1),fill=255)
def fin(im,name):
    out=Image.new('RGBA',(T,T),(0,0,0,0)); out.paste(im,(0,0),mask); out.resize((260,260),Image.LANCZOS).save(f'icons/{name}.png')
fin(im,'people')
# chat bubbles
im,d=tile((248,238,214,255))
d.rounded_rectangle((s(40),s(60),s(170),s(140)),s(26),fill=(220,180,90))
d.polygon([(s(70),s(136)),(s(60),s(170)),(s(100),s(138))],fill=(220,180,90))
d.rounded_rectangle((s(95),s(110),s(222),s(190)),s(26),fill=GOLD)
d.polygon([(s(190),s(186)),(s(204),s(218)),(s(166),s(188))],fill=GOLD)
for x in (128,158,188): d.ellipse((s(x-8),s(142),s(x+8),s(158)),fill=(255,255,255))
fin(im,'bubbles')
# money stacks
im,d=tile((222,240,228,255))
for i in range(5):
    y=180-i*16; d.rounded_rectangle((s(42),s(y),s(168),s(y+26)),s(6),fill=(58,160,100),outline=(30,100,60),width=s(3))
for i in range(3):
    y=180-i*16; d.rounded_rectangle((s(120),s(y+8),s(220),s(y+34)),s(6),fill=(58,160,100),outline=(30,100,60),width=s(3))
d.ellipse((s(150),s(52),s(222),s(124)),fill=(240,190,40),outline=(170,120,10),width=s(4))
d.text((s(186),s(88)),'$',font=ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',s(52)),fill=(150,100,0),anchor='mm')
fin(im,'money')
