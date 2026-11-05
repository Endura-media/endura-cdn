import json, math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersample
W, H = 1080 * S, 1920 * S
FPS = 30
TEMPO = 1.12               # audio speed-up
F = "/home/claude/vid6x/fonts/"
INTER = "/usr/share/fonts/opentype/inter/"

PAPER = (250, 248, 243); NAVY = (14, 32, 51); GOLD = (184, 134, 11); GOLDL = (240, 190, 60)
GRAY = (110, 122, 138); SHADOW = (222, 227, 234); RED = (205, 50, 50); WATER = (120, 160, 200)
WHITE = (255, 255, 255); GREEN = (46, 140, 87)

def font(path, size): return ImageFont.truetype(path, int(size * S))
cap_sans = font(INTER + "Inter-SemiBold.otf", 78)
cap_serif = font(F + "InstrumentSerif-Italic.ttf", 92)
mono = font(F + "JetBrainsMono-Medium.ttf", 30)
mono_s = font(F + "JetBrainsMono-Medium.ttf", 24)
bold = lambda s: font(INTER + "Inter-Bold.otf", s)
xbold = lambda s: font(INTER + "Inter-ExtraBold.otf", s)
serif = lambda s: font(F + "InstrumentSerif-Italic.ttf", s)

segs = json.load(open("/home/claude/vid6x/segs.json"))
segs = [(a / TEMPO, b / TEMPO, t) for a, b, t in segs]
DUR = segs[-1][1] + 0.6

# ---------- captions: (segment index, phrase, accent word) ----------
CAP = [
 (0, "Here's how to", None), (0, "6x your money", "6x"), (0, "with our revenue system.", "revenue"),
 (1, "Last month", "month"), (1, "my client put in $3,400", "$3,400"), (1, "and booked $23,000", "$23,000"), (1, "in jobs.", "jobs."),
 (2, "For every $1", "$1"), (2, "he put in,", None),
 (3, "he got about", None), (3, "$6 back.", "$6"),
 (4, "Here's how it works.", "works."),
 (5, "First, we build his", None), (5, "local visibility:", "visibility:"),
 (6, "his Google profile,", "Google"), (6, "website and tracking.", "tracking."),
 (7, "Think of it as", None), (7, "the plumbing.", "plumbing."),
 (8, "Then we run ads", "ads"), (8, "on his main service.", "main"),
 (9, "That's the", None), (9, "water pressure.", "pressure."),
 (10, "Turn up the pressure", "pressure"), (10, "on leaky pipes", "leaky"), (10, "and you flood", "flood"), (10, "the basement.", None),
 (11, "Fix the pipes first,", "first,"), (11, "and every drop", "drop"), (11, "goes where it should.", "should."),
 (12, "And this isn't", None), (12, "one lucky month.", "lucky"),
 (13, "Since he started", None), (13, "with us,", "us,"),
 (14, "every $1 he's put in", "$1"), (14, "has brought back", None), (14, "about $6", "$6"), (14, "in new revenue.", "revenue."),
 (15, "Because this system", None), (15, "is built to last.", "last."),
]
captions = []
WORDS = json.load(open("/home/claude/vid6x/words.json"))
SPOKEN = {"6x": 2, "$3,400": 5, "$23,000": 4, "$1": 2, "$6": 2}
def nspoken(phrase):
    return sum(SPOKEN.get(w.strip(",.:"), 1) for w in phrase.split())
for si in range(len(segs)):
    items = [c for c in CAP if c[0] == si]
    wl = WORDS[si]
    idx = 0
    starts = []
    for c in items:
        starts.append(wl[min(idx, len(wl) - 1)][1] / TEMPO - 0.05)
        idx += nspoken(c[1])
    seg_end = (wl[-1][1] + 0.55) / TEMPO
    for j, c in enumerate(items):
        e = starts[j + 1] if j + 1 < len(items) else seg_end
        captions.append((starts[j], e, c[1], c[2]))

HEADER = [(0, "HOW TO 6X"), (1, "PROOF · OCTOBER"), (4, "STEP 1 · THE PIPES"),
          (8, "STEP 2 · THE WATER"), (10, "WHY ORDER MATTERS"), (12, "BUILT TO LAST")]
def seg_t(i): return segs[i][0]

# ---------- helpers ----------
def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def p(v): return int(v * S)
def prog(t, start, dur): return clamp((t - start) / dur)

random.seed(4)
GRAIN = Image.effect_noise((W // 4, H // 4), 18).resize((W, H)).convert("L")
BG = Image.new("RGB", (W, H), PAPER)
BG = Image.composite(Image.new("RGB", (W, H), (238, 235, 228)), BG, GRAIN.point(lambda v: 40 if v > 140 else 0))

def card(d, x, y, w, h, outline=NAVY, fill=WHITE, r=22, width=4):
    d.rounded_rectangle([p(x + 10), p(y + 12), p(x + w + 10), p(y + h + 12)], p(r), fill=SHADOW)
    d.rounded_rectangle([p(x), p(y), p(x + w), p(y + h)], p(r), fill=fill, outline=outline, width=p(width))

def text(d, xy, s, f, fill=NAVY, anchor="la"):
    d.text((p(xy[0]), p(xy[1])), s, font=f, fill=fill, anchor=anchor)

def money(v): return "${:,.0f}".format(v)

def stamp(img, t, start, label, cx, cy, size=200, color=GOLD, rot=-8, sub=None):
    k = prog(t, start, 0.35)
    if k <= 0: return
    sc = 2.2 - 1.2 * ease(k)
    f = xbold(size)
    bx = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), label, font=f)
    tmp = Image.new("RGBA", (bx[2] - bx[0] + p(140), bx[3] - bx[1] + p(200 if sub else 120)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tw, th = bx[2] - bx[0], bx[3] - bx[1]
    pad = p(30)
    ox = (tmp.width - tw) // 2; oy = p(60) - bx[1]
    td.rounded_rectangle([ox - pad, oy + bx[1] - pad, ox + tw + pad, oy + bx[3] + pad], p(24), outline=color + (255,), width=p(9))
    td.text((ox, oy), label, font=f, fill=color + (255,))
    if sub:
        td.text((tmp.width // 2, oy + bx[3] + pad + p(40)), sub, font=mono, fill=NAVY + (255,), anchor="mt")
    tmp = tmp.rotate(rot, resample=Image.BICUBIC, expand=True)
    tmp = tmp.resize((max(1, int(tmp.width * sc)), max(1, int(tmp.height * sc))), Image.BICUBIC)
    alpha = tmp.split()[3].point(lambda a: int(a * ease(k * 1.5)))
    tmp.putalpha(alpha)
    img.paste(tmp, (p(cx) - tmp.width // 2, p(cy) - tmp.height // 2), tmp)

# ---------- scenes ----------
VX0, VY0 = 90, 640   # visual area top-left

def scene_hook(img, d, t):
    s = seg_t(0)
    # rising coins
    for i in range(7):
        k = prog(t, s + 0.1 + i * 0.12, 1.2)
        if k <= 0: continue
        x = 180 + i * 120; y = 1500 - 250 * ease(k)
        d.ellipse([p(x - 38), p(y - 38), p(x + 38), p(y + 38)], fill=GOLDL, outline=GOLD, width=p(4))
        text(d, (x, y), "$", bold(42), GOLD, "mm")
    stamp(img, t, s + 1.0, "6x", 520, 950, 260, GOLD, -8, "YOUR MONEY")

def board(img, d, t, s):
    # pipeline board card
    x, y, w, h = 90, 690, 860, 600
    k = ease(prog(t, s, 0.4))
    y += (1 - k) * 80
    card(d, x, y, w, h)
    text(d, (x + 30, y + 28), "GHL PIPELINE · OCTOBER LEADS", mono_s, GRAY)
    text(d, (x + w - 30, y + 28), "names hidden", mono_s, GRAY, "ra")
    cols = [("WON / PAID", 13065, 13, GREEN), ("INVOICED", 5950, 1, GOLD), ("SCHEDULED", 4040, 3, NAVY)]
    cw = (w - 80) / 3
    for i, (lab, val, n, col) in enumerate(cols):
        cx = x + 30 + i * (cw + 10)
        text(d, (cx + 8, y + 80), lab, mono_s, col)
        kk = ease(prog(t, s + 0.4 + i * 0.35, 0.8))
        text(d, (cx + 8, y + 115), money(val * kk), bold(40), NAVY)
        rows = min(n, 6)
        for r in range(rows):
            kr = prog(t, s + 0.5 + i * 0.35 + r * 0.08, 0.3)
            if kr <= 0: continue
            ry = y + 185 + r * 58
            d.rounded_rectangle([p(cx), p(ry), p(cx + cw - 10), p(ry + 46)], p(10), fill=(244, 246, 249), outline=SHADOW, width=p(2))
            d.rounded_rectangle([p(cx + 12), p(ry + 14), p(cx + 12 + (cw - 60) * (0.5 + 0.3 * ((r * 7 + i) % 3) / 2)), p(ry + 32)], p(6), fill=(205, 212, 222))
        if n > 6:
            text(d, (cx + 8, y + 185 + 6 * 58 + 6), f"+{n-6} more", mono_s, GRAY)

def scene_proof(img, d, t):
    s1, s2, s3 = seg_t(1), seg_t(2), seg_t(3)
    if t < s2:
        k1 = back(prog(t, s1 + 0.6, 0.4)); c1 = ease(prog(t, s1 + 0.6, 1.0))
        if k1 > 0:
            card(d, 190, 720 + (1 - k1) * 60, 700, 230, GRAY)
            text(d, (540, 770 + (1 - k1) * 60), "PUT IN", mono, GRAY, "mm")
            text(d, (540, 870 + (1 - k1) * 60), money(3400 * c1), xbold(110), NAVY, "mm")
        ka = ease(prog(t, s1 + 1.8, 0.4))
        if ka > 0:
            d.line([p(540), p(990), p(540), p(990 + 90 * ka)], fill=GOLD, width=p(10))
            if ka > 0.9: d.polygon([(p(512), p(1075)), (p(540), p(1115)), (p(568), p(1075))], fill=GOLD)
        k2 = back(prog(t, s1 + 2.4, 0.4)); c2 = ease(prog(t, s1 + 2.4, 1.6))
        if k2 > 0:
            card(d, 190, 1150 + (1 - k2) * 60, 700, 250, GOLD, width=7)
            text(d, (540, 1200 + (1 - k2) * 60), "BOOKED IN JOBS", mono, GOLD, "mm")
            text(d, (540, 1305 + (1 - k2) * 60), money(23000 * c2), xbold(120), GOLD, "mm")
    else:
        # $1 -> $6
        k = ease(prog(t, s2, 0.4))
        cx, cy = 230, 1000
        d.ellipse([p(cx - 110), p(cy - 110), p(cx + 110), p(cy + 110)], fill=WHITE, outline=NAVY, width=p(6))
        text(d, (cx, cy), "$1", xbold(90), NAVY, "mm")
        ka = ease(prog(t, s2 + 0.5, 0.6))
        d.line([p(380), p(cy), p(380 + 120 * ka), p(cy)], fill=GOLD, width=p(10))
        if ka > 0.9: d.polygon([(p(500), p(cy - 26)), (p(540), p(cy)), (p(500), p(cy + 26))], fill=GOLD)
        for i in range(6):
            kc = back(prog(t, s3 + i * 0.12, 0.35))
            if kc <= 0: continue
            col, row = i % 3, i // 3
            x, y = 640 + col * 120, 920 + row * 150
            r = 52 * kc
            d.ellipse([p(x - r), p(y - r), p(x + r), p(y + r)], fill=(120, 200, 150), outline=GREEN, width=p(4))
            text(d, (x, y), "$1", bold(34 * max(kc, .1)), (20, 90, 50), "mm")
        if t > s3 + 0.9:
            stamp(img, t, s3 + 0.9, "6x BACK", 520, 1330, 110, GREEN, -5)

def scene_how(img, d, t):
    s = seg_t(4)
    for i, (n, lab) in enumerate([("1", "LOCAL VISIBILITY"), ("2", "ADS")]):
        k = back(prog(t, s + i * 0.3, 0.45))
        y = 820 + i * 300
        x = 90 - (1 - k) * 600
        card(d, x, y, 860, 220, NAVY if i == 0 else GOLD, width=5)
        d.ellipse([p(x + 40), p(y + 50), p(x + 160), p(y + 170)], fill=NAVY if i == 0 else GOLD)
        text(d, (x + 100, y + 110), n, xbold(70), WHITE, "mm")
        text(d, (x + 200, y + 80), lab, xbold(58), NAVY)
        text(d, (x + 200, y + 150), "the pipes" if i == 0 else "the water", serif(52), GOLD)

NODES = [(250, 860, "gbp"), (700, 860, "web"), (475, 1230, "track")]
def pipes(d, t, flow=0.0, s=0, gold=False, drawk=1.0):
    col = GOLD if gold else NAVY
    pts = [(NODES[0][0], NODES[0][1]), (NODES[1][0], NODES[1][1]), (NODES[2][0], NODES[2][1])]
    segs_ = [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])]
    for i, (a, b) in enumerate(segs_):
        k = clamp(drawk * 3 - i)
        if k <= 0: continue
        ex, ey = a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d.line([p(a[0]), p(a[1]), p(ex), p(ey)], fill=col, width=p(26))
        d.line([p(a[0]), p(a[1]), p(ex), p(ey)], fill=PAPER, width=p(12))
        if flow > 0 and k >= 1:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            for j in range(int(L // 60)):
                u = ((j * 60 + flow * 300) % L) / L
                x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
                d.ellipse([p(x - 11), p(y - 11), p(x + 11), p(y + 11)], fill=WATER)

def node(d, t, x, y, kind, k):
    if k <= 0: return
    y = y + (1 - k) * 60
    w, h = 300, 200
    card(d, x - w / 2, y - h / 2, w, h)
    if kind == "gbp":
        d.ellipse([p(x - 100), p(y - 60), p(x - 50), p(y - 10)], outline=NAVY, width=p(4))
        for i in range(5):
            cx = x - 100 + i * 42; cy = y + 40
            pts = []
            for j in range(10):
                r = 18 if j % 2 == 0 else 8
                a = -math.pi / 2 + j * math.pi / 5
                pts.append((p(cx + r * math.cos(a)), p(cy + r * math.sin(a))))
            d.polygon(pts, fill=GOLDL)
        text(d, (x - 30, y - 50), "Google", bold(30), NAVY)
    elif kind == "web":
        d.line([p(x - 130), p(y - 50), p(x + 130), p(y - 50)], fill=NAVY, width=p(4))
        for i in range(3): d.ellipse([p(x - 120 + i * 22), p(y - 78), p(x - 108 + i * 22), p(y - 66)], fill=NAVY)
        d.rounded_rectangle([p(x - 110), p(y - 30), p(x + 40), p(y - 10)], p(6), fill=NAVY)
        d.rounded_rectangle([p(x - 110), p(y + 5), p(x + 100), p(y + 20)], p(6), fill=SHADOW)
        d.rounded_rectangle([p(x - 110), p(y + 40), p(x - 20), p(y + 70)], p(8), fill=GOLD)
    else:
        for i, hh in enumerate([40, 70, 55, 100]):
            d.rectangle([p(x - 100 + i * 55), p(y + 60 - hh), p(x - 60 + i * 55), p(y + 60)], fill=NAVY if i < 3 else GOLD)
        text(d, (x, y - 60), "TRACKING", mono_s, GRAY, "mm")

def scene_step1(img, d, t):
    s5, s6, s7 = seg_t(5), seg_t(6), seg_t(7)
    dk = ease(prog(t, s6, 2.0))
    pipes(d, t, 0, s5, gold=t > s7 + 0.3, drawk=dk)
    for i, (x, y, kind) in enumerate(NODES):
        node(d, t, x, y, kind, back(prog(t, seg_t(4) + 0.2 + i * 0.5, 0.4)))
    if t > s7 + 0.3:
        stamp(img, t, s7 + 0.3, "PLUMBING", 520, 1470, 70, GOLD, -4)

def valve(d, x, y, open_k):
    card(d, x - 120, y - 70, 240, 140, GOLD, width=6)
    text(d, (x, y - 25), "ADS", xbold(54), GOLD, "mm")
    a = open_k * math.pi / 2
    cx, cy = x, y + 35
    d.line([p(cx - 60 * math.cos(a)), p(cy - 60 * math.sin(a) * 0.3), p(cx + 60 * math.cos(a)), p(cy + 60 * math.sin(a) * 0.3)], fill=NAVY, width=p(10))

def scene_step2(img, d, t):
    s8, s9 = seg_t(8), seg_t(9)
    ok = ease(prog(t, s8 + 0.4, 0.8))
    pipes(d, t, flow=(t - s8) * ok, drawk=1.0)
    for x, y, kind in NODES: node(d, t, x, y, kind, 1)
    # feed pipe from valve to gbp node
    d.line([p(250), p(700), p(250), p(760)], fill=GOLD, width=p(26))
    valve(d, 250, 680, ok)

def scene_why(img, d, t):
    s10, s11 = seg_t(10), seg_t(11)
    fixed = t >= s11
    py = 900
    # pipe
    d.line([p(90), p(py), p(950), p(py)], fill=NAVY, width=p(40))
    d.line([p(90), p(py), p(950), p(py)], fill=PAPER, width=p(22))
    # basement box
    bx0, by0, bx1, by1 = 120, 1080, 920, 1480
    d.rectangle([p(bx0), p(by0), p(bx1), p(by1)], outline=NAVY, width=p(5))
    text(d, (bx0 + 20, by0 + 18), "BASEMENT" if not fixed else "BOOKED JOBS", mono_s, GRAY if not fixed else GREEN)
    flow = t * 3
    for j in range(14):
        x = 90 + ((j * 62 + flow * 120) % 860)
        d.ellipse([p(x - 8), p(py - 8), p(x + 8), p(py + 8)], fill=WATER)
    if not fixed:
        k = prog(t, s10, segs[10][1] - s10)
        for hx in (330, 560, 760):
            d.line([p(hx - 14), p(py - 14), p(hx + 14), p(py + 14)], fill=RED, width=p(6))
            for i in range(6):
                u = ((t * 2 + i / 6 + hx) % 1)
                dx = (i - 2.5) * 22 * u; dy = 170 * u
                d.ellipse([p(hx + dx - 9), p(py + 20 + dy - 9), p(hx + dx + 9), p(py + 20 + dy + 9)], fill=WATER)
        lvl = min(by1 - 6, by1 - 300 * ease(k))
        d.rectangle([p(bx0 + 3), p(lvl), p(bx1 - 3), p(by1 - 3)], fill=(190, 210, 228))
        if k > 0.55:
            stamp(img, t, s10 + 0.55 * (segs[10][1] - s10), "WASTED $", 520, 1300, 90, RED, -6)
    else:
        k = prog(t, s11, 0.6)
        for hx in (330, 560, 760):
            d.rounded_rectangle([p(hx - 34), p(py - 30), p(hx + 34), p(py + 30)], p(8), fill=GOLD)
        # spout + drops into bucket
        d.line([p(950), p(py), p(950), p(py + 120)], fill=NAVY, width=p(40))
        for i in range(5):
            u = ((t * 1.6 + i / 5) % 1)
            d.ellipse([p(950 - 10), p(py + 140 + 230 * u - 10), p(950 + 10), p(py + 140 + 230 * u + 10)], fill=WATER)
        # job cards stack
        n = int(1 + 6 * ease(prog(t, s11 + 0.3, segs[11][1] - s11 - 0.3)))
        for i in range(n):
            y = by1 - 70 - i * 52
            d.rounded_rectangle([p(170), p(y), p(620), p(y + 42)], p(10), fill=WHITE, outline=GREEN, width=p(3))
            text(d, (195, y + 21), "✓", bold(30), GREEN, "lm") if False else d.line([p(190), p(y + 22), p(202), p(y + 32), p(222), p(y + 10)], fill=GREEN, width=p(5))
            d.rounded_rectangle([p(240), p(y + 14), p(470), p(y + 28)], p(6), fill=(205, 212, 222))
            text(d, (600, y + 21), "PAID", mono_s, GREEN, "rm")

def scene_last(img, d, t):
    s12, s13, s14, s15 = seg_t(12), seg_t(13), seg_t(14), seg_t(15)
    if t < s14 + 0.2:
        months = ["MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT"]
        for i, m in enumerate(months):
            k = back(prog(t, s12 + 0.15 + i * 0.22, 0.3))
            if k <= 0: continue
            col, row = i % 4, i // 4
            x, y = 150 + col * 200, 820 + row * 230
            card(d, x, y + (1 - k) * 40, 170, 180, GOLD if i == 7 else NAVY, width=5)
            text(d, (x + 85, y + 60 + (1 - k) * 40), m, bold(44), NAVY, "mm")
            d.line([p(x + 55), p(y + 120), p(x + 78), p(y + 142), p(x + 118), p(y + 98)], fill=GOLD, width=p(8))
    else:
        stamp(img, t, s14 + 0.2, "$1 → $6", 520, 900, 140, GREEN, -6, "SINCE HE STARTED")
    if t > s15:
        stamp(img, t, s15 + 0.2, "BUILT TO LAST", 520, 1300, 80, NAVY, 4)

SCENES = [(0, scene_hook), (1, scene_proof), (4, scene_step1), (8, scene_step2), (10, scene_why), (12, scene_last)]

def draw_captions(d, t):
    cur = [c for c in captions if c[0] <= t < c[1] + 0.02]
    # show up to 2 lines: previous + current within same segment
    idx = None
    for i, c in enumerate(captions):
        if c[0] <= t: idx = i
    if idx is None: return
    lines = [captions[idx]]
    y = 330
    for li, (a, b, s, acc) in enumerate(lines):
        k = ease(prog(t, a, 0.15))
        lw = 0
        for wd in s.split(" "):
            ff = cap_serif if (acc and wd == acc) else cap_sans
            lw += d.textlength(wd + " ", font=ff) / S
        lw -= d.textlength(" ", font=cap_sans) / S
        x = (1080 - lw) / 2
        yy = y + li * 110 + (1 - k) * 20
        col_main = NAVY if li == len(lines) - 1 else (150, 160, 172)
        for wd in s.split(" "):
            if acc and wd == acc:
                f, colr = cap_serif, (GOLD if li == len(lines) - 1 else (200, 175, 120))
                off = -6
            else:
                f, colr, off = cap_sans, col_main, 0
            d.text((p(x), p(yy + off)), wd, font=f, fill=colr)
            x += d.textlength(wd + " ", font=f) / S
def seg_of(c):
    for i, (a, b, _) in enumerate(segs):
        if a <= c[0] < b: return i
    return -1

def draw_header(d, t):
    text(d, (60, 170), "// endura revenue system", mono, GRAY)
    lab = HEADER[0][1]
    for si, l in HEADER:
        if t >= seg_t(si): lab = l
    text(d, (1020, 170), lab, mono, GOLD, "ra")
    d.line([p(60), p(222), p(1020), p(222)], fill=SHADOW, width=p(3))
    # progress bar
    d.line([p(60), p(222), p(60 + 960 * t / DUR), p(222)], fill=GOLD, width=p(3))

def wipe(img, t):
    for si, _ in SCENES[1:]:
        s = seg_t(si)
        k = (t - (s - 0.18)) / 0.36
        if 0 <= k <= 1:
            d = ImageDraw.Draw(img)
            for gy in range(0, 1920, 60):
                for gx in range(0, 1080, 60):
                    dist = (gx + gy) / 3000
                    r = 46 * clamp(1 - abs((k * 1.4 - dist) - 0.2) * 3)
                    if r > 1:
                        d.ellipse([p(gx - r), p(gy + 640 - r) if False else p(gy - r), p(gx + r), p(gy + r)], fill=NAVY)

def frame(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    draw_header(d, t)
    cur = SCENES[0][1]
    for si, fn in SCENES:
        if t >= seg_t(si): cur = fn
    cur(img, d, t)
    draw_captions(d, t)
    wipe(img, t)
    return img.resize((1080, 1920), Image.LANCZOS)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        for tt in [float(x) for x in sys.argv[2:]]:
            frame(tt).save(f"/home/claude/vid6x/still_{tt:05.1f}.png")
        sys.exit()
    n = int(DUR * FPS)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS), "-i", "-",
                             "-i", "/home/claude/vid6x/vo.mp3", "-filter:a", f"atempo={TEMPO},apad", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{n/FPS:.2f}", "/home/claude/vid6x/endura_6x_draft_v1.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        proc.stdin.write(frame(i / FPS).tobytes())
    proc.stdin.close(); proc.wait()
    print("done", n)
