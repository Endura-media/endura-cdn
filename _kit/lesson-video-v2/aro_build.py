"""Lesson #02 (V009) in the ARO Command look: dark #07090C + warm gold glow, glass cards,
Archivo display, IBM Plex Sans/Mono, gold #FBC550, ok #5CCB98, crit #EC6B62, ARO orb.
python3 aro_build.py stills          -> contact sheet of key moments
python3 aro_build.py video [vo.mp3]  -> MP4 (voice sped up 1.12x like V006)
Scene functions take t in SOURCE voice seconds.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(os.path.dirname(HERE), "fonts", "use") + "/"
SFX = "/home/claude/endura-media/endura-cdn/_kit/lesson-video/sfx/"
W, H, FPS, SPEED = 1080, 1920, 30, 1.12

_fc = {}
def font(kind, size):
    name = {"d8": "archivo-latin-800-normal.woff", "d7": "archivo-latin-700-normal.woff",
            "d6": "archivo-latin-600-normal.woff", "b4": "ibm-plex-sans-latin-400-normal.woff",
            "b5": "ibm-plex-sans-latin-500-normal.woff", "b6": "ibm-plex-sans-latin-600-normal.woff",
            "b7": "ibm-plex-sans-latin-700-normal.woff", "m5": "ibm-plex-mono-latin-500-normal.woff",
            "m6": "ibm-plex-mono-latin-600-normal.woff"}[kind]
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, size)
    return _fc[k]

BG = (10, 24, 40); INK = (242, 239, 231); MUTED = (168, 163, 150); FAINT = (111, 107, 98)
GOLD = (251, 197, 80); GOLD_DEEP = (201, 144, 44); OK = (92, 203, 152); CRIT = (236, 107, 98)
BLUE = (127, 178, 224)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def prog(t, a, d): return ease((t - a) / d) if d > 0 else (1.0 if t >= a else 0.0)

# ---------- background: dark with warm gold glow (like the dashboard) ----------
def _bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32); img[:] = BG
    def glow(cx, cy, rx, ry, col, a):
        d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
        k = np.clip(1 - d, 0, 1) ** 2 * a
        for c in range(3): img[..., c] += (col[c] - img[..., c]) * k
    glow(200, 260, 900, 760, GOLD, 0.16)
    glow(900, 1560, 700, 600, GOLD, 0.09)
    glow(540, 2200, 1200, 900, (18, 40, 64), 0.7)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
BGIMG = None
def new_bg():
    return BGIMG.copy()

def centered(d, y, text, f, fill, cx=W / 2):
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)

def tracked(d, x, y, text, f, fill, track=0.14, center=False):
    sp = f.size * track
    total = sum(d.textlength(ch, font=f) for ch in text) + sp * (len(text) - 1)
    if center: x = x - total / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + sp

def glass(img, box, r=44, fill_a=16, edge=(255, 245, 225, 40), hi=True, tint=None):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = box
    # soft drop shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x0, y0 + 24, x1, y1 + 24], r, fill=(0, 0, 0, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)))
    base = tint if tint else (255, 250, 238)
    od.rounded_rectangle(box, r, fill=base + (fill_a,), outline=edge, width=2)
    if hi: od.line([(x0 + r, y0 + 2), (x1 - r, y0 + 2)], fill=(255, 255, 255, 30), width=2)
    img.alpha_composite(ov)

def rr(img, box, r, fill=None, outline=None, width=0):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)
    img.alpha_composite(ov)

def pill(d, cx, y, text, fg=GOLD, bg=(64, 52, 24), size=28, outline=None, filled=None):
    f = font("b7", size); w = d.textlength(text, font=f) + size * 1.4; h = size * 1.9
    box = [cx - w / 2, y, cx + w / 2, y + h]
    if filled: d.rounded_rectangle(box, h / 2, fill=filled)
    elif outline: d.rounded_rectangle(box, h / 2, outline=outline, width=4)
    else: d.rounded_rectangle(box, h / 2, fill=bg)
    centered(d, y + (h - size * 1.25) / 2, text, f, fg, cx)

def eyebrow(d, y, text):
    tracked(d, W / 2, y, text.upper(), font("d7", 30), MUTED, 0.14, center=True)

def orb(img, cx, cy, R, t=0.0, a=1.0):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    g = Image.new("RGBA", img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=GOLD + (int(110 * a),))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(R * 0.35)))
    def ring(r, w, col, dash, gap, rot):
        circ = 2 * math.pi * r; n = int(circ / (dash + gap))
        for i in range(n):
            a0 = rot + i * (dash + gap) / r; a1 = a0 + dash / r
            od.arc([cx - r, cy - r, cx + r, cy + r], math.degrees(a0), math.degrees(a1), fill=col, width=w)
    ring(R * .88, 3, GOLD + (int(90 * a),), 4, 12, t * 0.2)
    ring(R * .74, 6, GOLD + (int(255 * a),), 70 * R / 100, 30 * R / 100, -t * 0.29)
    ring(R * .58, 4, GOLD + (int(180 * a),), 40 * R / 100, 10 * R / 100, t * 0.45)
    ring(R * .44, 3, (255, 231, 174, int(150 * a)), 6, 6, -t * 0.7)
    od.ellipse([cx - R * .28, cy - R * .28, cx + R * .28, cy + R * .28], fill=GOLD + (int(255 * a),))
    od.ellipse([cx - R * .14, cy - R * .14, cx + R * .14, cy + R * .14], fill=(255, 244, 214, int(255 * a)))
    img.alpha_composite(ov)

def brand(img, d, t):
    # footer: small ARO-style mark + ENDURA, like the dashboard top bar
    orb(img, W / 2 - 112, 1858, 26, t)
    tracked(d, W / 2 - 74, 1840, "ENDURA", font("d8", 34), INK, 0.1)

# ---------- captions (glass pill, active word gold) ----------
words = json.load(open(os.path.join(HERE, "words.json")))
CHUNKS = [(0, 8), (8, 14), (14, 18), (18, 29), (29, 33), (33, 36), (36, 40),
          (40, 45), (45, 53), (53, 58), (58, 60), (60, 71)]
NO_CAP = [(10.5, 14.3), (22.0, 99)]
def caption(img, t):
    if any(a <= t < b for a, b in NO_CAP): return
    ws = None
    for a, b in CHUNKS:
        if words[a]["start"] - 0.05 <= t < (words[b]["start"] if b < len(words) else 99):
            ws = words[a:b]; break
    if not ws: return
    ws = [dict(w, _d=w.get("disp", w["text"])) for w in ws if w.get("disp", w["text"]) != ""]
    d = ImageDraw.Draw(img); f = font("b6", 44)
    txt = [w["_d"] for w in ws]
    if d.textlength(" ".join(txt), font=f) > 700:
        k = (len(txt) + 1) // 2; lines = [txt[:k], txt[k:]]
    else:
        lines = [txt]
    lh = 58; bw = max(d.textlength(" ".join(l), font=f) for l in lines) + 64; bh = lh * len(lines) + 34
    x0 = SAFE_CX - bw / 2; y0 = 1272
    glass(img, [x0, y0, x0 + bw, y0 + bh], r=36, fill_a=22, tint=(14, 32, 51))
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 36, fill=(7, 18, 31, 190))
    img.alpha_composite(ov); d = ImageDraw.Draw(img)
    i = 0
    for li, l in enumerate(lines):
        x = SAFE_CX - d.textlength(" ".join(l), font=f) / 2; y = y0 + 17 + li * lh
        for wt in l:
            w = ws[i]; i += 1
            col = GOLD if w["start"] <= t < w["end"] + 0.12 else INK
            d.text((x, y), wt, font=f, fill=col); x += d.textlength(wt + " ", font=f)

# ---------- scene A: phone, quotes stream in, QUIET status slams, $800 ----------
def scene_phone(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    px0, py0, px1, py1 = 210, 150, 870, 1340
    glass(img, [px0, py0, px1, py1], r=70, fill_a=14)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W / 2 - 70, py0 + 26, W / 2 + 70, py0 + 58], 16, fill=(0, 0, 0))
    tracked(d, px0 + 56, py0 + 92, "SENT QUOTES", font("d7", 28), MUTED, 0.14)
    # 4 quotes on screen at frame 1, then one new quote every 0.12s, each easing in (slide + fade)
    QA = 1.4  # question mark lands after the last quote settles
    for i in range(14):
        at = -1 if i < 4 else (i - 4) * 0.12
        if t < at: continue
        p = 1.0 if at < 0 else prog(t, at, 0.28)
        y = py0 + 140 + i * 72 + 40 * (1 - p)
        mix = lambda c: tuple(int(14 + (c[k] - 14) * p) if k == 0 else int((28, 44)[k - 1] + (c[k] - (28, 44)[k - 1]) * p) for k in range(3))
        rr(img, [px0 + 36, y, px1 - 36, y + 60], 16, fill=(255, 250, 238, int(12 * p)), outline=(255, 245, 225, int(40 * p)), width=2); d = ImageDraw.Draw(img)
        d.text((px0 + 62, y + 12), "Quote sent", font=font("b5", 30), fill=mix(INK))
        d.text((px0 + 250, y + 13), "$400", font=font("m6", 30), fill=mix(GOLD))
        d.text((px1 - 190, y + 17), "no reply", font=font("b4", 25), fill=mix(FAINT))
    if t >= QA:
        t = t - QA + 1.0   # reuse the timing below as if the mark landed at 1.0
        a = prog(t, 1.0, 0.2)
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle([px0, py0, px1, py1], 70, fill=(8, 20, 34, int(150 * a)))
        img.alpha_composite(ov); d = ImageDraw.Draw(img)
        # big red question mark pops in over the 14 unanswered quotes, then breathes
        s = (1.4 - 0.4 * prog(t, 1.0, 0.16)) * (1 + 0.03 * math.sin((t - 1.16) * 5) if t > 1.16 else 1)
        R = 190 * s; cx, cy = W / 2, 745
        rr(img, [cx - R, cy - R, cx + R, cy + R], int(R), fill=(52, 22, 30, 235), outline=CRIT + (255,), width=5)
        d = ImageDraw.Draw(img)
        f = font("d8", int(290 * s)); bb = d.textbbox((0, 0), "?", font=f)
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), "?", font=f, fill=CRIT)
    return img

# ---------- quote grid (glass cards with status pills) ----------
def grid(img, t, appear_at, paid_at=None, title="Say you have 14 quotes", y0=430, ch=136, stagger=True, cw=292):
    d = ImageDraw.Draw(img)
    eyebrow(d, y0 - 230, "Example")
    centered(d, y0 - 170, title, font("d8", 68), INK)
    gap = 22; gx = (W - (3 * cw + 2 * gap)) / 2
    for i in range(14):
        a = appear_at + (i * 0.05 if stagger else 0)
        if t < a: continue
        p = prog(t, a, 0.22)
        r, c = divmod(i, 3); x = gx + c * (cw + gap); y = y0 + r * (ch + gap) + 30 * (1 - p)
        if i == 12: x = gx + 0.5 * (cw + gap)
        if i == 13: x = gx + 1.5 * (cw + gap)
        paid = bool(paid_at) and i in paid_at and t >= paid_at[i]
        glass(img, [x, y, x + cw, y + ch], r=28, fill_a=40 if paid else 14,
              tint=OK if paid else None, edge=(OK + (220,)) if paid else (255, 245, 225, 40))
        d = ImageDraw.Draw(img)
        d.text((x + 24, y + 18), "Quote", font=font("b5", 28), fill=MUTED)
        d.text((x + cw - 24 - d.textlength("$400", font=font("m6", 30)), y + 18), "$400", font=font("m6", 30), fill=INK)
        lab, col = ("PAID", OK) if paid else ("QUIET", CRIT)
        f = font("b7", 24); lw = d.textlength(lab, font=f) + 34
        d.rounded_rectangle([x + 24, y + ch - 60, x + 24 + lw, y + ch - 20], 20, outline=col, width=3)
        tracked(d, x + 24 + 17, y + ch - 54, lab, f, col, 0.06)

def scene_grid14(t):
    img = new_bg(); grid(img, t, 2.24); return img

def scene_text(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, 200, "Your follow-up system")
    centered(d, 260, "One text each", font("d8", 68), INK)
    p = prog(t, 4.5, 0.3); off = 160 * (1 - p)
    glass(img, [120 + off, 400, 960 + off, 720], r=44, fill_a=40, tint=GOLD, edge=(251, 197, 80, 140))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(["Hi Sarah, it's Mike with Brightline.", "You asked about the job a few", "weeks back. Still on your list?"]):
        d.text((168 + off, 446 + i * 80), l, font=font("b5", 42), fill=INK)
    for at, yy in ((6.32, 790), (6.88, 960)):
        if t < at: continue
        q = prog(t, at, 0.18); dx = -80 * (1 - q)
        glass(img, [120 + dx, yy, 700 + dx, yy + 130], r=40, fill_a=18)
        d = ImageDraw.Draw(img)
        d.text((160 + dx, yy + 36), "Yes, still need it!", font=font("b6", 46), fill=INK)
        cx, cy = 770 + dx, yy + 65
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=OK, width=5)
        d.line([(cx - 17, cy + 2), (cx - 4, cy + 15), (cx + 19, cy - 14)], fill=OK, width=8)
    return img

PAID_AT = {4: 7.55, 9: 7.95}
def scene_paid(t):
    img = new_bg()
    grid(img, t, 7.2, PAID_AT, title="Same 14 quotes", y0=360, ch=108, stagger=False, cw=272)
    d = ImageDraw.Draw(img)
    # the math, built piece by piece: $400 (first yes) + $400 (second yes) = $800
    f = font("d8", 96); y = 1080
    parts = [(7.55, "$400", INK), (7.95, " + ", MUTED), (7.95, "$400", INK)]
    if t >= 7.55:
        full = "$400 + $400" if t >= 7.95 else "$400"
        x = (W - d.textlength(full, font=f)) / 2
        for (at, txt, col) in parts:
            if t < at: break
            p = prog(t, at, 0.18)
            d.text((x, y + 18 * (1 - p)), txt, font=f, fill=col)
            x += d.textlength(txt, font=f)
    if t >= 8.84:
        val = int(800 * prog(t, 8.84, 0.75) / 10) * 10
        p = prog(t, 8.84, 0.2)
        centered(d, 1200 + 20 * (1 - p), f"= ${val}", font("d8", 170), OK)
    return img

def scene_zero(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    p1 = prog(t, 10.56, 0.18); p2 = prog(t, 11.04, 0.18)
    s = 1.25 - 0.25 * p1
    if t >= 10.56: centered(d, 700 - (300 * s - 300) / 2, "$0", font("d8", int(300 * s)), OK)
    if t >= 11.04: centered(d, 1050 + 24 * (1 - p2), "added spend.", font("d8", 110), INK)
    return img

def scene_quiet(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    p1 = prog(t, 12.24, 0.18); p2 = prog(t, 13.2, 0.18)
    if t >= 12.24: centered(d, 740 + 24 * (1 - p1), "Quiet doesn't", font("d8", 120), INK)
    if t >= 13.2: centered(d, 880 + 24 * (1 - p2), "mean no.", font("d8", 120), GOLD)
    return img

def scene_proof(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, 200, "Real · my business")
    centered(d, 260, "Last month", font("d8", 68), INK)
    for k, y in enumerate((420, 820)):
        a = 14.6 + k * 0.2
        if t < a: continue
        p = prog(t, a, 0.22); yy = y + 30 * (1 - p)
        paid = t >= 21.12 + k * 0.18
        glass(img, [120, yy, 960, yy + 320], r=40, fill_a=36 if paid else 14,
              tint=OK if paid else None, edge=(OK + (200,)) if paid else (255, 245, 225, 40))
        d = ImageDraw.Draw(img)
        rr(img, [168, yy + 48, 520, yy + 92], 14, fill=(255, 250, 238, 34)); d = ImageDraw.Draw(img)  # blurred client name
        d.text((168, yy + 130), "Past client · quote sent", font=font("b5", 38), fill=MUTED)
        if t >= 19.04 + k * 0.15:
            d.text((168, yy + 196), "Follow-up system checked in", font=font("b5", 38), fill=BLUE)
        lab, col = ("PAID", OK) if paid else ("QUIET", CRIT) if t >= 17.44 + k * 0.12 else ("SENT", MUTED)
        f = font("b7", 34); lw = d.textlength(lab, font=f) + 50
        d.rounded_rectangle([912 - lw, yy + 44, 912, yy + 100], 28, outline=col, width=4)
        tracked(d, 912 - lw + 25, yy + 52, lab, f, col, 0.06)
    return img

RULE = [(22.04, "FOLLOW UP", GOLD), (23.44, "BEFORE", INK), (24.04, "YOU SPEND.", GOLD)]
def scene_rule(t):
    img = new_bg(); d = ImageDraw.Draw(img)
    cur = [r for r in RULE if t >= r[0]][-1]
    s = 1.2 - 0.2 * prog(t, cur[0], 0.14)
    f = font("d8", int(140 * s)); centered(d, 860 - (140 * s - 140) / 2, cur[1], f, cur[2])
    return img

def scene_end(t):
    img = new_bg()
    orb(img, W / 2, 520, 190, t, a=prog(t, 22.0, 0.4))
    d = ImageDraw.Draw(img)
    for y, l, c in ((800, "Follow up with the leads", INK), (890, "you have before you", INK), (980, "spend on more.", GOLD)):
        centered(d, y, l, font("d8", 70), c)
    if t >= 22.4:
        pill(d, W / 2, 1130, "ENDURA LESSONS #02", size=32)
    return img

SCENES = [(0.0, scene_phone), (2.24, scene_grid14), (4.48, scene_text), (7.2, scene_paid), (10.56, scene_zero),
          (12.24, scene_quiet), (14.32, scene_proof), (22.0, scene_end)]

def zoomed(img, t, a, amt=0.025, dur=4.0):
    s = 1 + amt * min(1, max(0, (t - a) / dur))
    if s <= 1.0005: return img
    nw, nh = int(W * s), int(H * s)
    big = img.resize((nw, nh), Image.BILINEAR); l, tp = (nw - W) // 2, (nh - H) // 2
    return big.crop((l, tp, l + W, tp + H))

# TikTok safe zone (1080x1920): keep everything inside x 60-880 (right rail of like/comment/share
# buttons starts ~x 900), below y 260 (search bar) and above y ~1430 (username + caption).
# Each scene is still designed on the full 1080x1920 board; its content band (y 150-1430) is scaled
# into the safe box, and the background stays full-bleed.
SAFE_X0, SAFE_X1, SAFE_Y0 = 60, 880, 270
SAFE_CX = (SAFE_X0 + SAFE_X1) / 2
BAND = (0, 150, 1080, 1430)
_SC = (SAFE_X1 - SAFE_X0) / (BAND[2] - BAND[0])
CW, CH = int(BAND[2] * _SC), int((BAND[3] - BAND[1]) * _SC)
TRANSPARENT = None
def render(t):
    global BGIMG, TRANSPARENT
    if TRANSPARENT is None: TRANSPARENT = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    start, fn = [s for s in SCENES if t >= s[0]][-1]
    real = BGIMG; BGIMG = TRANSPARENT
    try: layer = zoomed(fn(t), t, start)
    finally: BGIMG = real
    content = layer.crop(BAND).resize((CW, CH), Image.LANCZOS)
    img = BGIMG.copy(); img.alpha_composite(content, (SAFE_X0, SAFE_Y0))
    caption(img, t)
    return img.convert("RGB")

STILLS = [(0.45, "01 0.4s quotes stream in"), (1.2, "02 1.0s QUIET slams"), (2.05, "03 2.0s $800 lands"),
          (3.9, "04 14 sitting quiet"), (7.1, "05 text sent, 2 yes"), (11.5, "06 2 PAID, $800"),
          (13.9, "07 Quiet doesn't mean no"), (18.5, "08 proof: went quiet"), (21.7, "09 proof: both paid"),
          (22.6, "10 FOLLOW UP"), (24.3, "11 YOU SPEND."), (26.2, "12 end card")]

def stills():
    os.makedirs(os.path.join(HERE, "aro_frames"), exist_ok=True)
    tw_, th_ = 270, 480
    sheet = Image.new("RGB", (4 * tw_ + 5 * 16, 3 * (th_ + 46) + 4 * 16), (240, 240, 240))
    sd = ImageDraw.Draw(sheet); lf = font("b6", 17)
    for i, (t, lab) in enumerate(STILLS):
        im = render(t); im.save(os.path.join(HERE, "aro_frames", f"{i + 1:02d}.png"))
        r, c = divmod(i, 4); x = 16 + c * (tw_ + 16); y = 16 + r * (th_ + 46 + 16)
        sheet.paste(im.resize((tw_, th_), Image.LANCZOS), (x, y)); sd.text((x, y + th_ + 10), lab, font=lf, fill=(30, 30, 30))
    out = os.path.join(HERE, "V009_ARO_stills_contact_sheet.png"); sheet.save(out); print(out)

# ---------- sound kit (source seconds) ----------
EVENTS = [("pop", 0.12 * k) for k in range(0, 10, 2)] + [
    ("thud", 1.4), ("whoosh", 2.2)] + [("pop", 2.24 + 0.1 * k) for k in range(0, 14, 3)] + [
    ("whoosh", 4.45), ("pop", 6.32), ("pop", 6.88), ("whoosh", 7.15), ("ding", 7.55), ("ding", 7.95),
    ("ding", 9.6), ("whoosh", 10.5), ("thud", 10.56), ("whoosh", 12.2), ("whoosh", 14.3), ("pop", 14.6), ("pop", 14.8), ("buzz", 17.44),
    ("pop", 19.04), ("ding", 21.12), ("ding", 21.3), ("whoosh", 22.0), ("thud", 24.48)]
VOL = {"pop": 0.45, "whoosh": 0.35, "ding": 0.45, "buzz": 0.25, "thud": 0.6}
END_SRC = 26.6

def video(vo=None):
    dur = END_SRC / SPEED
    out = os.path.join(HERE, "V009_follow-up-quotes_FINAL.mp4" if vo else "V009_preview_novoice.mp4")
    silent = os.path.join(HERE, "_video.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for k in range(int(dur * FPS) + 1):
        p.stdin.write(render((k / FPS) * SPEED).tobytes())
    p.stdin.close(); p.wait()
    inputs, filt, labels, idx = [], [], [], 1          # input 0 = the video
    if vo:
        inputs += ["-i", vo]; filt.append(f"[{idx}:a]atempo={SPEED}[v]"); labels.append("[v]"); idx += 1
    for j, (name, ts) in enumerate(EVENTS):
        inputs += ["-i", SFX + name + ".wav"]; ms = int(ts / SPEED * 1000)
        filt.append(f"[{idx}:a]volume={VOL[name]},adelay={ms}|{ms}[s{j}]"); labels.append(f"[s{j}]"); idx += 1
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{dur:.3f}[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent] + inputs + ["-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out], check=True)
    os.remove(silent); print(out, f"{dur:.2f}s")

if __name__ == "__main__":
    BGIMG = _bg()
    if sys.argv[1] == "stills": stills()
    else: video(sys.argv[2] if len(sys.argv) > 2 else None)
