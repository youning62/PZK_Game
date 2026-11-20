"""CG compositions (sprites over generated backgrounds)."""
import sys
from artlib import *
import gen_beach
import gen_painted as gp
import car as carlib


def sprite(name, scale=1.0, angle=0.0, flip=False, crop_alpha=True):
    im = load(name, 'RGBA')
    if crop_alpha:
        im = im.crop(im.getbbox())
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    return im


def layer_of(im, x0, y0, w=W, h=H):
    """Place RGBA PIL image at (x0, y0) on a full-canvas RGBA float layer."""
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    canvas.paste(im, (int(round(x0)), int(round(y0))), im)
    a = np.asarray(canvas, np.float32) / 255.0
    return a[..., :3], a[..., 3]


def comp(img, im, x0, y0, opacity=1.0):
    rgb, a = layer_of(im, x0, y0)
    return lerp(img, rgb, a * opacity), a


def rgba_from(rgb, a):
    return Image.fromarray(np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8),
                                      (np.clip(a, 0, 1) * 255).astype(np.uint8)]), 'RGBA')


def foam_spray(img, cx, cy, spread_x, spread_y, n, seed, col=(255, 255, 255), size=(2, 9), alpha=0.9, dirx=0.0):
    r = rng0(seed)
    m = Mask(ss=2)
    for _ in range(n):
        dx = r.normal(0, spread_x)
        dy = -abs(r.normal(0, spread_y))
        s = r.uniform(*size) * (1 - min(1, abs(dy) / (spread_y * 3)) * 0.6)
        m.circle(cx + dx + dirx * abs(dy), cy + dy, s)
    a = m.get(0.8)
    img = screen(img, col, blur(a, 6) * 0.5)
    return lerp(img, np.array(col, np.float32) / 255 * np.ones_like(img), a * alpha)


rng0 = np.random.default_rng


# ------------------------------------------------------------------ dream_surf
def dream_surf():
    img = gen_beach.dream_beach()
    x, y = grid()
    # big swell rising from the right, cresting at upper-left
    xs = np.arange(W, dtype=np.float32)
    top = 820 - 420 * np.exp(-((xs - 380) / 520) ** 2) - 30 * np.sin(xs / 90)
    face = (y >= top[None, :]).astype(np.float32)
    face = blur(face, 1.0)
    depth = np.clip((y - top[None, :]) / 500, 0, 1)
    wc = gradient([(0, (150, 235, 235)), (0.25, (70, 200, 215)), (1, (30, 140, 190))], depth)
    tex = fbm(H, W, 50, 5, seed=91, sx=4)
    wc *= (0.9 + 0.2 * tex[..., None])
    # light streaks along the wave face
    streak = smooth(0.6, 0.85, fbm(H, W, 30, 4, seed=92, sx=8, sy=0.5)) * smooth(0, 0.6, depth)
    wc = screen(wc, (230, 255, 255), streak * 0.45)
    # translucent lip glow
    wc = screen(wc, (200, 255, 240), np.exp(-((y - top[None, :] - 40) / 40) ** 2) * 0.5)
    img = lerp(img, wc, face)
    # foam along crest
    cn = fbm(H, W, 18, 4, seed=93)
    crest = np.exp(-((y - top[None, :] + 4) / (14 + 18 * cn)) ** 2) * smooth(0.25, 0.5, cn + 0.15)
    img = lerp(img, np.ones_like(img), np.clip(crest * 1.3, 0, 1))
    # curling lip at the peak (white arc)
    lip = Mask()
    pts = bezier((80, 470), (260, 300), (560, 380), n=40)
    lip.tapered(pts, 70, 10)
    img = lerp(img, np.ones_like(img) * np.array([0.95, 1, 1], np.float32), lip.get(3) * 0.9)
    img = foam_spray(img, 380, 420, 260, 80, 420, 94, size=(2, 8), dirx=0.6)
    # surfer
    s = 0.62
    sp = sprite('pzk-surfing.png', s, angle=6)
    sx0, sy0 = 1060 - sp.width / 2, 900 - sp.height
    # board wake behind (left) of the surfer
    wake = Mask()
    for i in range(7):
        yy = 870 + i * 14
        wake.tapered([(sx0 + 420, yy), (sx0 + 100, yy + 6 + i * 2), (sx0 - 300 - i * 60, yy + 30 + i * 6)], 18 - i * 2, 2)
    img = lerp(img, np.ones_like(img), wake.get(2) * 0.85)
    img, a = comp(img, sp, sx0, sy0)
    # spray kicked up at the board tail and around
    img = foam_spray(img, sx0 + 300, 880, 160, 90, 380, 95, size=(2, 9), dirx=-0.8)
    img = foam_spray(img, sx0 + 620, 900, 120, 40, 160, 96, size=(2, 6), dirx=0.4)
    # motion lines
    ml = Mask()
    r = rng0(97)
    for _ in range(22):
        yy = r.uniform(200, 1000)
        x0 = r.uniform(1300, 1900)
        ml.tapered([(x0, yy), (x0 + r.uniform(120, 320), yy)], 3, 0.5)
    img = screen(img, (255, 255, 255), ml.get(0.6) * 0.7)
    img = sparkle_field(img, 50, (0, 0, W, H), seed=98, size=(6, 24))
    img = bloom(img, 0.7, 40, 0.6)
    img = screen(img, (255, 235, 250), smooth(0.6, 1.4, np.sqrt(((x - 960) / 960) ** 2 + ((y - 540) / 540) ** 2)) * 0.6)
    return img


# ------------------------------------------------------------------ yyl_surf
def surfboard_img(length=560, width=110):
    S = 4
    L, Wd = length * S, width * S
    im = Image.new('RGBA', (L + 40, Wd + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 20, 20 + Wd / 2
    top = bezier((cx, cy), (cx + L * 0.25, cy - Wd * 0.75), (cx + L, cy - Wd * 0.05), n=60)
    bot = bezier((cx + L, cy + Wd * 0.05), (cx + L * 0.25, cy + Wd * 0.75), (cx, cy), n=60)
    outline = top + bot
    d.polygon(outline, fill=(250, 252, 250, 255))
    # teal stripe along the centre
    st = bezier((cx + L * 0.04, cy), (cx + L * 0.5, cy - Wd * 0.05), (cx + L * 0.96, cy - Wd * 0.02), n=40)
    d.line(st, fill=(0, 170, 170, 255), width=int(Wd * 0.14))
    d.line([(p[0], p[1] + Wd * 0.13) for p in st[4:-6]], fill=(255, 200, 60, 255), width=int(Wd * 0.04))
    # rail shading
    d.line(bot[5:-5], fill=(180, 200, 205, 255), width=int(Wd * 0.08))
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return im


def yyl_surf():
    img = gen_beach.surf_beach()
    x, y = grid()
    # swell band behind her
    xs = np.arange(W, dtype=np.float32)
    top = 840 - 90 * np.exp(-((xs - 900) / 600) ** 2) - 12 * np.sin(xs / 70)
    face = blur((y >= top[None, :]).astype(np.float32), 1)
    depth = np.clip((y - top[None, :]) / 250, 0, 1)
    wc = gradient([(0, (120, 220, 225)), (1, (20, 120, 170))], depth) * (0.9 + 0.2 * fbm(H, W, 30, 4, seed=101, sx=5)[..., None])
    img = lerp(img, wc, face * 0.92)
    cn = fbm(H, W, 15, 4, seed=102)
    crest = np.exp(-((y - top[None, :]) / (10 + 14 * cn)) ** 2) * smooth(0.3, 0.55, cn + 0.1)
    img = lerp(img, np.ones_like(img), np.clip(crest * 1.2, 0, 1))
    # girl + board, tilted -8 deg (clockwise)
    gs = 0.5
    girl = sprite('yyl-girl.png', gs)
    board = surfboard_img(520, 100)
    grp = Image.new('RGBA', (900, girl.height + 120), (0, 0, 0, 0))
    gx = (grp.width - girl.width) // 2
    grp.alpha_composite(board, ((grp.width - board.width) // 2 + 20, girl.height - 60))
    grp.alpha_composite(girl, (gx, 0))
    grp = grp.rotate(-8, resample=Image.BICUBIC, expand=True)
    px0, py0 = 1080 - grp.width / 2, 1010 - grp.height
    # wake / foam under the board
    wake = Mask()
    for i in range(6):
        yy = 950 + i * 12
        wake.tapered([(px0 + 300, yy), (px0 + 60, yy + 10), (px0 - 400 - 60 * i, yy + 40 + i * 8)], 16 - i * 2, 2)
    img = lerp(img, np.ones_like(img), wake.get(2) * 0.85)
    img, a = comp(img, grp, px0, py0)
    img = foam_spray(img, px0 + 220, 975, 150, 90, 380, 103, size=(1.5, 6), dirx=-0.9)
    img = foam_spray(img, px0 + grp.width - 180, 995, 110, 40, 150, 104, size=(1.5, 5), dirx=0.5)
    # foam covering the bottom of the board slightly (in-water feel)
    fm = Mask(ss=2)
    r = rng0(105)
    for _ in range(140):
        fm.circle(r.uniform(px0 + 150, px0 + grp.width - 120), r.uniform(992, 1025), r.uniform(3, 10))
    img = lerp(img, np.ones_like(img), fm.get(1.2) * 0.85)
    img = sun_flare(img, 240, 90, 1.0)
    img = bloom(img, 0.8, 30, 0.45)
    return img


# ------------------------------------------------------------------ first_meet
def impact_star(img, cx, cy, r_out=190, r_in=90, n=14, seed=0):
    r = rng0(seed)
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n + r.uniform(-0.08, 0.08)
        rr = (r_out * r.uniform(0.8, 1.15)) if i % 2 == 0 else r_in * r.uniform(0.85, 1.1)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    outer = Mask().poly(pts).get()
    inner = Mask().poly([(cx + (px - cx) * 0.72, cy + (py - cy) * 0.72) for px, py in pts]).get()
    img = over(img, (20, 20, 20), outer)
    img = over(img, (255, 230, 60), np.clip(outer - 0.0, 0, 1) * 0)  # placeholder keeps API
    img = over(img, (255, 240, 90), inner)
    img = over(img, (255, 255, 255), Mask().poly([(cx + (px - cx) * 0.4, cy + (py - cy) * 0.4) for px, py in pts]).get())
    return img


def speed_lines(img, cx, cy, r0, r1, n, seed, col=(30, 30, 30), arc=(0, 2 * math.pi), width=6):
    r = rng0(seed)
    m = Mask()
    for _ in range(n):
        a = r.uniform(*arc)
        a0 = r0 * r.uniform(0.9, 1.2)
        a1 = r1 * r.uniform(0.8, 1.1)
        m.tapered([(cx + math.cos(a) * a0, cy + math.sin(a) * a0), (cx + math.cos(a) * a1, cy + math.sin(a) * a1)],
                  0.5, width * r.uniform(0.6, 1.3))
    return over(img, col, m.get())


def coconut(img, cx, cy, r, angle=0.0, half=False):
    x, y = grid()
    m = Mask().circle(cx, cy, r).get()
    tex = fbm(H, W, 6, 3, seed=int(cx))
    fib = 0.5 + 0.5 * np.sin((np.arctan2(y - cy, x - cx) + angle) * 40 + tex * 4)
    base = gradient([(0, (60, 36, 20)), (1, (125, 80, 45))], 0.4 * fib + 0.6 * tex)
    d = np.sqrt((x - cx + r * 0.3) ** 2 + (y - cy + r * 0.3) ** 2) / (r * 1.6)
    base *= np.clip(1.15 - d, 0.45, 1.2)[..., None]
    img = lerp(img, base, m)
    if half:
        # opened half shell: white flesh rim visible on top
        inner = Mask().ellipse((cx - r * 0.85, cy - r * 0.55, cx + r * 0.85, cy + r * 0.05)).get()
        img = over(img, (250, 248, 238), inner)
        img = over(img, (230, 225, 210), Mask().ellipse((cx - r * 0.68, cy - r * 0.42, cx + r * 0.68, cy - r * 0.02)).get())
    else:
        for a in (0.9, 1.6, 2.3):
            ex, ey = cx + math.cos(a + angle) * r * 0.35 - r * 0.1, cy - math.sin(a + angle) * r * 0.35 - r * 0.25
            img = over(img, (30, 18, 10), Mask().circle(ex, ey, r * 0.09).get())
    return img


def high_heels(img, cx, by, s=1.0):
    """A neat pair of black stilettos standing in the sand, seen from the side."""
    for k, dx in enumerate((-34 * s, 30 * s)):
        bx = cx + dx
        sh = 0.92 if k == 0 else 1.0
        m = Mask()
        # sole + vamp shape (toe at left, heel at right)
        pts = (bezier((bx - 70 * s, by), (bx - 82 * s, by - 26 * s), (bx - 40 * s, by - 34 * s), n=16)
               + bezier((bx - 40 * s, by - 34 * s), (bx + 10 * s, by - 40 * s), (bx + 40 * s, by - 92 * s), n=16)
               + [(bx + 62 * s, by - 96 * s), (bx + 64 * s, by - 80 * s)]
               + bezier((bx + 56 * s, by - 74 * s), (bx + 20 * s, by - 30 * s), (bx - 40 * s, by - 8 * s), n=16)
               + [(bx - 60 * s, by)])
        m.poly(pts)
        # stiletto heel
        m.poly([(bx + 52 * s, by - 80 * s), (bx + 64 * s, by - 82 * s), (bx + 58 * s, by), (bx + 53 * s, by)])
        a = m.get()
        img = lerp(img, img * 0.6, blur(Mask().ellipse((bx - 80 * s, by - 6 * s, bx + 75 * s, by + 10 * s)).get(), 6) * 0.6)
        col = np.array([0.05, 0.05, 0.06], np.float32) * sh
        img = lerp(img, col * np.ones_like(img), a)
        # glossy highlight
        hl = Mask().tapered(bezier((bx - 60 * s, by - 22 * s), (bx - 20 * s, by - 34 * s), (bx + 30 * s, by - 76 * s), n=12), 3 * s, 1).get()
        img = screen(img, (230, 230, 240), hl * 0.7)
        # inner sole (red)
        img = over(img, (170, 20, 30), Mask().tapered(bezier((bx - 30 * s, by - 34 * s), (bx + 10 * s, by - 44 * s), (bx + 52 * s, by - 86 * s), n=12), 4 * s, 3 * s).get())
    return img


def first_meet():
    img = gen_beach.beach_day()
    x, y = grid()
    # sand spray / dust cloud where he lands
    # PZK delivery guy, falling backward (head to the left)
    pz = sprite('pzk_angry.PNG', 0.40, angle=70)
    px0, py0 = 40, 1080 - pz.height + 140
    # shadow / dent in the sand
    img *= (1 - 0.35 * blur(Mask().ellipse((px0 + 40, 960, px0 + pz.width - 40, 1060)).get(), 20))[..., None]
    # impact star behind his head (head ends up at left/upper part of rotated sprite)
    hx, hy = 230, py0 + pz.height * 0.14
    img = speed_lines(img, hx, hy, 200, 520, 46, 111, col=(25, 25, 25), width=8)
    img = impact_star(img, hx, hy, 230, 110, 13, seed=112)
    img, a = comp(img, pz, px0, py0)
    # sand spray thrown up around him
    sand = (236, 214, 160)
    img = foam_spray(img, px0 + pz.width * 0.75, 1075, 200, 70, 260, 113, col=sand, size=(2, 7), alpha=0.95)
    img = foam_spray(img, px0 + pz.width * 0.35, 1075, 160, 60, 160, 114, col=(250, 235, 190), size=(2, 6), alpha=0.9)
    # broken coconut half on the sand near him
    img = coconut(img, px0 + pz.width + 40, 1010, 46, half=True)
    # little "dizzy" stars over his head
    dz = Mask()
    for i in range(5):
        a_ = i * 2 * math.pi / 5
        star4(dz, hx + math.cos(a_) * 150, hy - 60 + math.sin(a_) * 45, 20)
    img = over(img, (255, 230, 60), dz.get())
    # YYL standing at right
    gs = 0.64
    girl = sprite('yyl-girl.png', gs)
    gx0, gy0 = 1500 - girl.width / 2, 1060 - girl.height
    img *= (1 - 0.3 * blur(Mask().ellipse((gx0 + 20, 1030, gx0 + girl.width - 20, 1075)).get(), 10))[..., None]
    img, ga = comp(img, girl, gx0, gy0)
    # coconut flying in the air above her raised hand side (she catches it)
    ccx, ccy = gx0 + girl.width + 40, gy0 + 120
    arc = Mask()
    for k in range(3):
        pts = bezier((ccx - 520, ccy + 260 + k * 26), (ccx - 260, ccy - 120 + k * 26), (ccx - 60, ccy - 20 + k * 22), n=30)
        arc.tapered(pts, 1, 7)
    img = over(img, (255, 255, 255), arc.get(0.6) * 0.85)
    img = coconut(img, ccx, ccy, 52, angle=0.6)
    img = speed_lines(img, ccx, ccy, 64, 110, 10, 115, col=(30, 30, 30), arc=(-0.6, 0.6), width=5)
    # high heels standing neatly near the right edge
    img = high_heels(img, 1800, 1030, 0.95)
    # "!" by her head
    ex = Mask()
    exx, exy = gx0 - 40, gy0 + 40
    ex.poly([(exx - 16, exy - 70), (exx + 16, exy - 70), (exx + 8, exy + 10), (exx - 8, exy + 10)])
    ex.circle(exx, exy + 34, 12)
    exo = Mask()
    exo.poly([(exx - 24, exy - 78), (exx + 24, exy - 78), (exx + 14, exy + 16), (exx - 14, exy + 16)])
    exo.circle(exx, exy + 34, 19)
    img = over(img, (255, 255, 255), exo.get())
    img = over(img, (220, 30, 40), ex.get())
    img = bloom(img, 0.85, 20, 0.3)
    return img


# ------------------------------------------------------------------ lambo_beach
def lambo_beach():
    x, y = grid()
    HZ = 600
    sunx, suny = 380, HZ - 60
    img = vgrad([(0, (60, 60, 130)), (0.35, (180, 100, 130)), (0.7, (255, 160, 100)),
                 (1, (255, 210, 140))], y0=0, y1=HZ)
    img = sky_clouds(img, 80, HZ - 80, seed=121, color=(255, 190, 150), shade=(150, 80, 110), cover_=0.6, amount=0.7)
    img = screen(img, (255, 200, 120), radial(sunx, suny, 900, power=2.2, sy=0.6) * 0.7)
    img = screen(img, (255, 248, 220), np.clip(radial(sunx, suny, 50, power=0.25) * 1.5, 0, 1))
    img = sea(img, HZ, (230, 140, 100), (90, 70, 100), seed=122, streak=0.25, y1=800,
              glint=(sunx, 70, (255, 215, 150), 1.0))
    # wet sand / beach
    sand = vgrad([(0, (210, 150, 110)), (1, (150, 100, 75))], y0=780, y1=H)
    sand *= (0.92 + 0.12 * fbm(H, W, 10, 3, seed=123)[..., None])
    shore = 790 + 12 * np.sin(x / 120) + 6 * np.sin(x / 37)
    sm = blur((y > shore).astype(np.float32), 1.5)
    img = lerp(img, sand, sm)
    img = lerp(img, np.ones_like(img) * np.array([1, 0.95, 0.9], np.float32), np.exp(-((y - shore) / 4) ** 2) * 0.7)
    # road at the beach edge
    road_top = 860
    rm = Mask().rect((0, road_top, W, H)).get()
    asp = np.array([0.30, 0.27, 0.28], np.float32) * (0.92 + 0.12 * fbm(H, W, 5, 3, seed=124)[..., None])
    asp = screen(asp, (255, 170, 100), radial(sunx, road_top, 900, power=2, sy=0.25) * 0.5)
    img = lerp(img, asp, rm)
    img = over(img, (240, 225, 200), Mask().rect((0, road_top + 4, W, road_top + 10)).get())
    dash = Mask()
    for dx in range(0, W, 220):
        dash.rect((dx, 1010, dx + 120, 1020))
    img = over(img, (240, 200, 120), dash.get())
    # palm silhouettes
    specs = [dict(bx=1640, by=880, height=760, lean=-0.18, seed=31, fronds=12),
             dict(bx=1820, by=900, height=620, lean=-0.3, seed=32, fronds=11),
             dict(bx=90, by=880, height=520, lean=0.2, seed=33),
             dict(bx=1480, by=820, height=360, lean=-0.1, seed=34)]
    img, _ = gp.palm_layer(img, specs, (40, 22, 28))
    # car
    sc = 1.3
    gy = 990
    x0 = 1000 - 502 * sc
    y0 = gy - carlib.GROUND * sc
    crgb, ca = carlib.render(x0, y0, sc, 'golden', flip=True)
    rr, ra = carlib.reflect(crgb, ca, gy - 2, 0.25, 6)
    img = lerp(img, rr, ra)
    img *= (1 - 0.75 * np.clip(radial(1000, gy, 720, power=1.2, sy=0.05) * 2, 0, 1))[..., None]
    img = lerp(img, crgb, ca)
    # warm rim light on the sun side of the car
    edge = np.clip(ca - np.roll(ca, 6, axis=1), 0, 1)
    img = screen(img, (255, 200, 130), blur(edge, 2) * 1.2)
    img = screen(img, (255, 180, 110), radial(sunx, suny, 1400, power=2) * ca * 0.35)
    img = sun_flare(img, sunx, suny, 0.7, col=(255, 220, 170))
    img = bloom(img, 0.7, 30, 0.5)
    return img


# ------------------------------------------------------------------ first_dinner
def first_dinner():
    img = gp.restaurant(False, table=False)
    x, y = grid()
    s = 0.64
    pz = sprite('pzk-morning.png', s, crop_alpha=False)
    gl = sprite('yyl-girl.png', s, crop_alpha=False)
    # pzk left, yyl right; waists hidden behind the table
    img, _ = comp(img, pz, 560 - 450 * s, 110)
    gl = sprite('yyl-girl.png', 0.74, crop_alpha=False)
    img, _ = comp(img, gl, 1370 - 430 * 0.74, 190)
    TT = 790
    img = gp.draw_table(img, False, cx=960, ytop=TT, half=900, glasses=True, candles=(800, 1120),
                        plates=[(560, TT + 70), (1370, TT + 70)])
    # extra warm candle glow on faces
    img = screen(img, (255, 170, 90), radial(960, 700, 900, power=2.0) * 0.25)
    img = bloom(img, 0.65, 35, 0.55)
    img = blur(img, 1.2) * 0.35 + img * 0.65
    xx = np.sqrt(((x - 960) / 960) ** 2 + ((y - 540) / 540) ** 2)
    img *= (1 - 0.35 * smooth(0.6, 1.4, xx))[..., None]
    img = screen(img, (255, 140, 120), smooth(0.7, 1.4, xx) * 0.15)
    return img


SCENES = {'dream_surf': dream_surf, 'yyl_surf': yyl_surf, 'first_meet': first_meet,
          'lambo_beach': lambo_beach, 'first_dinner': first_dinner}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        save_rgb(SCENES[n](), os.path.join(CG, n + '.png'))
