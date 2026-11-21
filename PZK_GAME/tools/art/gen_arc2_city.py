"""Arc 2 city exteriors / night interiors: Chinese commercial street (day / night / rain),
roadside snack stall, claw-machine arcade, convenience store, and the rider_rain CG."""
import sys
from artlib import *
from PIL import ImageFont

rng0 = np.random.default_rng
CN_FONT = os.path.join(GAME, 'SourceHanSansLite.ttf')
_fc = {}


def cfont(size):
    size = max(6, int(size))
    if size not in _fc:
        _fc[size] = ImageFont.truetype(CN_FONT, size)
    return _fc[size]


def C(c):
    return np.array(c, np.float32) / 255.0


def full(c):
    return np.ones((H, W, 3), np.float32) * C(c)


# ------------------------------------------------------------------ text / sign images
def sign_img(txt, w, h, bg, fg, vertical=False, border=None, stroke=0, glow=False, fill=0.72, rr=0):
    """Rectangular sign board (RGBA PIL) with centred Chinese text, auto-fitted."""
    S = 2
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if bg is not None:
        d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=rr * S, fill=tuple(bg) + (255,))
    if border is not None:
        bw = max(2, int(min(w, h) * 0.06)) * S
        d.rounded_rectangle((bw // 2, bw // 2, w * S - bw // 2, h * S - bw // 2), radius=rr * S,
                            outline=tuple(border) + (255,), width=bw)
    n = len(txt)
    if vertical:
        sz = min(w * fill, h * fill / n) * S
        f = cfont(sz)
        tot = sz * n
        y0 = (h * S - tot) / 2
        for i, ch in enumerate(txt):
            bb = d.textbbox((0, 0), ch, font=f)
            cw = bb[2] - bb[0]
            d.text(((w * S - cw) / 2 - bb[0], y0 + i * sz - bb[1] + (sz - (bb[3] - bb[1])) / 2), ch, font=f,
                   fill=tuple(fg) + (255,), stroke_width=int(stroke * S), stroke_fill=tuple(fg) + (255,))
    else:
        sz = min(h * fill, w * 0.86 / max(1, n)) * S
        f = cfont(sz)
        bb = d.textbbox((0, 0), txt, font=f, stroke_width=int(stroke * S))
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((w * S - tw) / 2 - bb[0], (h * S - th) / 2 - bb[1]), txt, font=f, fill=tuple(fg) + (255,),
               stroke_width=int(stroke * S), stroke_fill=tuple(fg) + (255,))
    return im.resize((w, h), Image.LANCZOS)


def text_rgba(txt, size, col, stroke=0, stroke_col=None):
    f = cfont(size)
    bb = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), txt, font=f, stroke_width=stroke)
    im = Image.new('RGBA', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), txt, font=f, fill=tuple(col) + (255,), stroke_width=stroke,
                            stroke_fill=tuple(stroke_col or col) + (255,))
    return im


def paste_at(img, im, x0, y0, opacity=1.0):
    """Paste RGBA PIL image onto float img at (x0, y0); returns img, alpha."""
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(im, (int(round(x0)), int(round(y0))), im)
    a = np.asarray(canvas, np.float32) / 255.0
    return lerp(img, a[..., :3], a[..., 3] * opacity), a[..., 3]


def rect_m(x0, y0, x1, y1, b=0.0):
    return Mask().rect((x0, y0, x1, y1)).get(b)


# ------------------------------------------------------------------ street furniture / figures
SHOP_NAMES = ['兰州拉面', '蜜雪奶茶', '沙县小吃', '麻辣烫', '手机维修', '大药房', '黄焖鸡米饭', '烧烤夜宵',
              '便利店', '理发', '水饺', '炸鸡汉堡', '火锅', '超市', '足浴', '快餐']
BLADE = ['奶茶', '拉面', '足浴', '烧烤', '火锅', '药房', '饺子', '宾馆', '网吧', '麻辣烫', '小吃', '超市']
SIGN_COLS = [((200, 30, 35), (255, 235, 120)), ((20, 90, 170), (255, 255, 255)), ((250, 200, 40), (160, 20, 20)),
             ((30, 140, 70), (255, 255, 255)), ((230, 90, 30), (255, 255, 255)), ((240, 240, 235), (200, 30, 30)),
             ((120, 40, 140), (255, 230, 120)), ((30, 30, 35), (255, 200, 60))]
NEON = [(255, 60, 140), (60, 220, 255), (255, 210, 60), (140, 90, 255), (255, 90, 60), (90, 255, 160)]


def person(m, cx, by, hgt, r, umbrella=None, bag=False):
    """Draw a simple pedestrian silhouette into Mask m. Returns umbrella polygon if any."""
    s = hgt / 1.7
    head = 0.11 * s
    m.circle(cx, by - hgt + head, head)
    sh = 0.21 * s
    walk = r.uniform(-1, 1)
    # torso
    m.poly([(cx - sh, by - hgt + 2.1 * head), (cx + sh, by - hgt + 2.1 * head),
            (cx + sh * 0.8, by - hgt * 0.47), (cx - sh * 0.8, by - hgt * 0.47)])
    m.circle(cx - sh * 0.75, by - hgt + 2.4 * head, sh * 0.3)
    m.circle(cx + sh * 0.75, by - hgt + 2.4 * head, sh * 0.3)
    # arms
    m.tapered([(cx - sh * 0.9, by - hgt + 2.5 * head), (cx - sh * 1.05 - walk * 0.05 * s, by - hgt * 0.5)], 0.08 * s, 0.06 * s)
    m.tapered([(cx + sh * 0.9, by - hgt + 2.5 * head), (cx + sh * 1.05 + walk * 0.05 * s, by - hgt * 0.5)], 0.08 * s, 0.06 * s)
    # legs
    st = 0.07 * s * walk
    m.tapered([(cx - sh * 0.4, by - hgt * 0.48), (cx - sh * 0.45 - st, by)], 0.14 * s, 0.09 * s)
    m.tapered([(cx + sh * 0.4, by - hgt * 0.48), (cx + sh * 0.45 + st, by)], 0.14 * s, 0.09 * s)
    if bag:
        m.rect((cx + sh * 0.9, by - hgt * 0.55, cx + sh * 1.6, by - hgt * 0.38))
    if umbrella:
        uw = 0.55 * s
        uy = by - hgt - 0.15 * s
        pts = [(cx - uw, uy + 0.12 * s)] + bezier((cx - uw, uy + 0.12 * s), (cx, uy - 0.35 * s), (cx + uw, uy + 0.12 * s), n=20)
        m.line([(cx, uy), (cx + 0.02 * s, by - hgt * 0.55)], max(1, 0.025 * s))
        return pts
    return None


def scooter_rear(m, cx, by, sc, box=True, rider=True):
    """Rear view of an e-bike (optionally with a rider + yellow thermal box). sc = px per metre.
    Returns dict of part polygons for colouring."""
    parts = {}
    w = 0.12 * sc
    # wheel
    m.rect((cx - w / 2, by - 0.5 * sc, cx + w / 2, by))
    m.ellipse((cx - w / 2, by - 0.08 * sc, cx + w / 2, by + 0.02 * sc))
    # body
    m.poly([(cx - 0.22 * sc, by - 0.45 * sc), (cx + 0.22 * sc, by - 0.45 * sc), (cx + 0.18 * sc, by - 0.85 * sc),
            (cx - 0.18 * sc, by - 0.85 * sc)])
    parts['tail'] = (cx, by - 0.62 * sc, 0.09 * sc)
    if rider:
        m.poly([(cx - 0.24 * sc, by - 0.85 * sc), (cx + 0.24 * sc, by - 0.85 * sc), (cx + 0.2 * sc, by - 1.45 * sc),
                (cx - 0.2 * sc, by - 1.45 * sc)])
        m.circle(cx, by - 1.58 * sc, 0.14 * sc)
        # handlebar
        m.rect((cx - 0.38 * sc, by - 1.12 * sc, cx + 0.38 * sc, by - 1.08 * sc))
        parts['helmet'] = (cx, by - 1.6 * sc, 0.15 * sc)
    if box:
        parts['box'] = (cx - 0.27 * sc, by - 1.25 * sc, cx + 0.27 * sc, by - 0.8 * sc)
    return parts


def scooter_side(cx, by, sc, facing=1):
    """Side view e-bike. Returns (wheel_mask, body_mask, seat_mask, light_xy). cx = centre."""
    f = facing
    X = lambda u: cx + u * sc * f
    Yp = lambda v: by - v * sc
    wm, bm, sm = Mask(), Mask(), Mask()
    rw = 0.24
    for u in (-0.6, 0.62):
        wm.circle(X(u), Yp(rw), rw * sc)
    # body: rear fairing + floorboard + front apron
    bm.poly([(X(-0.85), Yp(0.55)), (X(-0.75), Yp(0.82)), (X(-0.15), Yp(0.8)), (X(-0.1), Yp(0.35)),
             (X(0.3), Yp(0.33)), (X(0.42), Yp(0.95)), (X(0.52), Yp(1.05)), (X(0.62), Yp(0.98)),
             (X(0.55), Yp(0.4)), (X(0.62), Yp(0.3)), (X(-0.4), Yp(0.3)), (X(-0.6), Yp(0.4))])
    # handlebar stem + bar
    bm.line([(X(0.5), Yp(1.0)), (X(0.4), Yp(1.18))], 0.05 * sc)
    bm.line([(X(0.32), Yp(1.2)), (X(0.56), Yp(1.17))], 0.05 * sc)
    sm.poly([(X(-0.8), Yp(0.82)), (X(-0.12), Yp(0.82)), (X(-0.16), Yp(0.92)), (X(-0.75), Yp(0.93))])
    return wm.get(), bm.get(), sm.get(), (X(0.6), Yp(0.9))


# ------------------------------------------------------------------ the street
class Street:
    F, VX, VY, EYE = 1000.0, 960.0, 600.0, 1.6
    XB, XR = 8.0, 5.0   # facade line, curb line

    def P(self, X, Y, Z):
        return (self.VX + X * self.F / Z, self.VY + (self.EYE - Y) * self.F / Z)


def facade_tex(L, Hm, ppm, night, r, shop_name, sign_col, upper_col):
    """Flat facade texture (RGBA + emissive RGB) for one shop unit: L metres long, Hm tall."""
    w, h = max(8, int(L * ppm)), max(8, int(Hm * ppm))
    im = Image.new('RGBA', (w, h), tuple(upper_col) + (255,))
    em = Image.new('RGB', (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    de = ImageDraw.Draw(em)
    Y = lambda m_: h - m_ * ppm   # metres up -> px
    # wall texture: subtle tile lines
    for yy in np.arange(4.8, Hm, 0.5):
        d.line([(0, Y(yy)), (w, Y(yy))], fill=tuple(int(c * 0.93) for c in upper_col), width=max(1, ppm // 40))
    # upper floors
    nwin = max(1, int(L / 2.6))
    for fl, y0 in enumerate(np.arange(5.4, Hm - 1.8, 3.0)):
        for i in range(nwin):
            cx = (i + 0.5) * w / nwin
            ww = ppm * 1.5
            x0, x1 = cx - ww / 2, cx + ww / 2
            ya, yb = Y(y0 + 1.6), Y(y0)
            if night:
                lit = r.random() < 0.45
                gc = [(255, 214, 150), (255, 240, 210), (190, 220, 255), (255, 190, 120)][r.integers(0, 4)] if lit else (22, 26, 40)
            else:
                lit = False
                gc = (120, 150, 175) if r.random() < 0.7 else (80, 95, 110)
            d.rectangle((x0 - ppm * 0.08, ya - ppm * 0.08, x1 + ppm * 0.08, yb + ppm * 0.08), fill=(200, 200, 200) if not night else (70, 70, 80))
            d.rectangle((x0, ya, x1, yb), fill=gc)
            if lit:
                de.rectangle((x0, ya, x1, yb), fill=tuple(int(c * 0.55) for c in gc))
                # curtain silhouette
                if r.random() < 0.5:
                    d.rectangle((x0, ya, x0 + ww * r.uniform(0.2, 0.45), yb), fill=tuple(int(c * 0.7) for c in gc))
            elif not night:
                d.polygon([(x0, ya), (x0 + ww * 0.35, ya), (x0, ya + (yb - ya) * 0.6)], fill=(170, 195, 215))
            d.line([(cx, ya), (cx, yb)], fill=(190, 190, 190) if not night else (60, 60, 70), width=max(1, ppm // 20))
            # security bars (防盗窗) / AC unit / laundry
            k = r.random()
            if k < 0.35:
                bc = (150, 150, 150) if not night else (50, 50, 58)
                d.rectangle((x0 - ppm * 0.15, ya - ppm * 0.15, x1 + ppm * 0.15, yb + ppm * 0.1), outline=bc, width=max(1, ppm // 18))
                for bx in np.linspace(x0, x1, 7):
                    d.line([(bx, ya - ppm * 0.15), (bx, yb + ppm * 0.1)], fill=bc, width=max(1, ppm // 25))
            if r.random() < 0.45:
                ax = x1 + ppm * 0.2 if r.random() < 0.5 else x0 - ppm * 0.95
                ac = (225, 225, 220) if not night else (60, 62, 70)
                d.rectangle((ax, Y(y0 + 0.1), ax + ppm * 0.75, Y(y0 - 0.45)), fill=ac)
                d.ellipse((ax + ppm * 0.3, Y(y0 + 0.02), ax + ppm * 0.68, Y(y0 - 0.38)), outline=tuple(int(c * 0.7) for c in ac), width=max(1, ppm // 30))
            if r.random() < 0.18:
                py = Y(y0 - 0.15)
                d.line([(x0 - ppm * 0.3, py), (x1 + ppm * 0.3, py)], fill=(90, 90, 90), width=max(1, ppm // 30))
                for lx in np.arange(x0, x1, ppm * 0.4):
                    lc = [(220, 80, 80), (80, 140, 220), (240, 240, 230), (240, 200, 80), (120, 180, 120)][r.integers(0, 5)]
                    if night:
                        lc = tuple(int(c * 0.35) for c in lc)
                    d.rectangle((lx, py, lx + ppm * 0.3, py + ppm * r.uniform(0.4, 0.8)), fill=lc)
    # parapet
    d.rectangle((0, 0, w, ppm * 0.35), fill=tuple(int(c * 0.82) for c in upper_col))
    # ground floor shopfront
    pc = (150, 150, 155) if not night else (45, 45, 52)
    d.rectangle((0, Y(4.9), w, h), fill=pc)
    gx0, gx1 = ppm * 0.4, w - ppm * 0.4
    shutter = (not night and r.random() < 0.12) or (night and r.random() < 0.15)
    if shutter:
        sc = (175, 178, 180) if not night else (55, 58, 64)
        d.rectangle((gx0, Y(3.4), gx1, h), fill=sc)
        for yy in np.arange(0.1, 3.4, 0.12):
            d.line([(gx0, Y(yy)), (gx1, Y(yy))], fill=tuple(int(c * 0.8) for c in sc), width=max(1, ppm // 40))
    else:
        if night:
            ic = [(225, 190, 140), (190, 210, 220), (230, 175, 120), (210, 160, 130)][r.integers(0, 4)]
            d.rectangle((gx0, Y(3.4), gx1, h), fill=ic)
            for k_ in range(3):
                lx = r.uniform(gx0, gx1)
                d.rectangle((lx, Y(3.3), lx + ppm * 0.6, Y(3.2)), fill=(255, 250, 235))
            de.rectangle((gx0, Y(3.4), gx1, h), fill=tuple(int(c * 0.12) for c in ic))
        else:
            d.rectangle((gx0, Y(3.4), gx1, h), fill=(95, 100, 105))
            for k_ in range(4):
                sx = gx0 + (gx1 - gx0) * r.uniform(0, 1)
                d.polygon([(sx, Y(3.4)), (sx + ppm * 0.8, Y(3.4)), (sx - ppm * 1.0, h), (sx - ppm * 1.8, h)], fill=(130, 140, 150))
        # interior stuff: shelves / tables
        for k_ in range(int(L * 1.2)):
            sx = r.uniform(gx0, gx1)
            sw_ = ppm * r.uniform(0.4, 1.0)
            sh_ = ppm * r.uniform(0.6, 1.6)
            cc = [(200, 80, 60), (80, 120, 180), (220, 190, 90), (120, 160, 110), (90, 80, 70)][r.integers(0, 5)]
            if not night:
                cc = tuple(int(c * 0.6) for c in cc)
            d.rectangle((sx, h - sh_, sx + sw_, h - ppm * 0.05), fill=cc)
        # door frame + mullions
        mc = (210, 210, 205) if not night else (90, 90, 95)
        for mx in np.linspace(gx0, gx1, 4):
            d.line([(mx, Y(3.4)), (mx, h)], fill=mc, width=max(2, ppm // 10))
        d.line([(gx0, Y(3.4)), (gx1, Y(3.4))], fill=mc, width=max(2, ppm // 8))
        # red door curtain strips / poster
        if r.random() < 0.4:
            d.rectangle((gx0 + ppm * 0.3, Y(2.6), gx0 + ppm * 1.2, Y(1.6)), fill=(230, 40, 40))
            d.text((gx0 + ppm * 0.35, Y(2.55)), '特价', font=cfont(ppm * 0.38), fill=(255, 240, 120))
    # sign band
    bg, fg = sign_col
    sw_, sh_ = int(w - ppm * 0.2), int(ppm * 1.15)
    sg = sign_img(shop_name, sw_, sh_, bg, fg, stroke=ppm * 0.02, fill=0.74)
    im.paste(sg, (int(ppm * 0.1), int(Y(4.75))), sg)
    if night:
        e = Image.new('RGB', sg.size, (0, 0, 0))
        e.paste(sg.convert('RGB'), (0, 0))
        e = Image.eval(e, lambda v: int(v * 0.8))
        em.paste(e, (int(ppm * 0.1), int(Y(4.75))))
    return im, em


def city_street(mode='day', add_rain=True):
    """mode: 'day', 'night', 'rain'."""
    night = mode != 'day'
    rain = mode == 'rain'
    st = Street()
    P, F, VX, VY, EYE, XB, XR = st.P, st.F, st.VX, st.VY, st.EYE, st.XB, st.XR
    x, y = grid()
    r = rng0(7)
    E = np.zeros((H, W, 3), np.float32)   # emissive (for glow)
    # ---- sky
    if mode == 'day':
        img = vgrad([(0, (70, 135, 215)), (0.65, (150, 195, 235)), (1, (215, 228, 238))], y0=0, y1=VY)
        img = sky_clouds(img, 20, VY - 60, seed=11, cover_=0.6, amount=0.75, shade=(190, 205, 225))
    elif mode == 'night':
        img = vgrad([(0, (8, 8, 26)), (0.6, (28, 20, 58)), (1, (70, 40, 80))], y0=0, y1=VY)
    else:
        img = vgrad([(0, (10, 16, 30)), (0.6, (25, 38, 62)), (1, (50, 66, 92))], y0=0, y1=VY)
        img = lerp(img, img * 1.25, fbm(H, W, 220, 4, seed=12, sx=2) * 0.5)
    # ---- skyscrapers behind
    towers = []
    rt = rng0(21)
    for i in range(16):
        tx = rt.uniform(560, 1360)
        tz = rt.uniform(380, 900)
        th = rt.uniform(120, 330)
        tw = rt.uniform(30, 70)
        towers.append((tz, tx, th, tw, i))
    towers.sort(key=lambda t: -t[0])
    for tz, tx, th, tw, i in towers:
        sc = F / tz
        gy = VY + EYE * sc
        x0, x1 = tx - tw * sc / 2, tx + tw * sc / 2
        y0 = gy - th * sc
        haze = smooth(380, 900, tz)
        m = Mask().rect((x0, y0, x1, gy)).get()
        top = rt.integers(0, 3)
        if top == 1:
            m = np.maximum(m, Mask().poly([(x0, y0 + 1), (x1, y0 + 1), (x1, y0 - tw * sc * 0.5)]).get())
        elif top == 2:
            m = np.maximum(m, Mask().rect(((x0 + x1) / 2 - 1.2, y0 - 25 * sc, (x0 + x1) / 2 + 1.2, y0)).get())
            m = np.maximum(m, Mask().rect((x0 + tw * sc * 0.2, y0 - 6 * sc, x1 - tw * sc * 0.2, y0)).get())
        if mode == 'day':
            tc = gradient([(0, (150, 180, 210)), (1, (90, 120, 150))], smooth(x0, x1, x))
            tc = lerp(tc, img * 1.0, (0.35 + 0.45 * haze))
            # vertical glass mullions + sky reflection
            ml = (np.sin((x - x0) / max(2, 3.0 * sc) * math.pi) ** 2 > 0.93).astype(np.float32)
            tc = lerp(tc, tc * 0.82, ml * 0.6)
            tc = screen(tc, (230, 240, 255), smooth(gy - th * sc * 0.4, y0, y) * smooth(x1, x0, x) * 0.25)
        else:
            base = (16, 18, 36) if mode == 'night' else (18, 26, 42)
            tc = full(base) * (0.8 + 0.4 * smooth(x0, x1, x))[..., None]
            tc = lerp(tc, img, 0.25 + 0.35 * haze)
            # lit window grid
            cw_, ch_ = max(3.0, 4.5 * sc), max(3.0, 4.2 * sc)
            ix, iy = np.floor((x - x0) / cw_), np.floor((y - y0) / ch_)
            hsh = (np.sin(ix * 12.9898 + iy * 78.233 + i * 3.1) * 43758.5453) % 1.0
            inside = ((x - x0) % cw_ > cw_ * 0.3) & ((y - y0) % ch_ > ch_ * 0.35)
            lit = (hsh > 0.78) & inside
            wc = np.where((hsh > 0.85)[..., None], C((190, 220, 255)), C((255, 205, 140)))
            tc = lerp(tc, wc * (0.45 + 0.35 * (1 - haze)), lit.astype(np.float32) * m * 0.8)
            E += wc * (lit * m)[..., None] * 0.08
            # red beacon
            bxy = ((x0 + x1) / 2, y0 - (25 * sc if top == 2 else 0) - 2)
            E += C((255, 40, 40)) * radial(bxy[0], bxy[1], 6, power=1)[..., None]
            img = screen(img, (255, 60, 50), radial(bxy[0], bxy[1], 3, power=0.5))
        img = lerp(img, tc, m)
    if mode == 'day':
        img = screen(img, (230, 235, 240), smooth(VY - 300, VY, y) * 0.35)
    else:
        glowc = (120, 60, 120) if mode == 'night' else (60, 90, 130)
        img = screen(img, glowc, smooth(VY - 350, VY, y) * 0.5)
    # ---- far cross-street buildings at Z=ZE
    wall_cols = [(225, 218, 205), (205, 205, 200), (230, 210, 185), (190, 200, 205), (235, 225, 215), (200, 180, 170)]
    ZE = 115.0
    sc = F / ZE
    gyE = VY + EYE * sc
    rx = -60.0
    while rx < 60:
        bw = r.uniform(8, 16)
        bh = r.uniform(10, 26)
        q = (VX + rx * sc, gyE - bh * sc, VX + (rx + bw) * sc, gyE)
        m = rect_m(*q)
        if mode == 'day':
            bc = lerp(C(wall_cols[r.integers(0, 6)]) * r.uniform(0.8, 1.0), C((200, 212, 225)), 0.35)
            img = lerp(img, full((0, 0, 0)) + bc, m)
            ix = np.floor((x - q[0]) / 3.5)
            iy = np.floor((y - q[1]) / 4.0)
            win = ((x - q[0]) % 3.5 > 1.4) & ((y - q[1]) % 4.0 > 1.8) & (y < gyE - 5 * sc)
            img = lerp(img, img * 0.55, win * m)
            nc = SIGN_COLS[r.integers(0, len(SIGN_COLS))][0]
            img = lerp(img, full(nc), rect_m(q[0] + 2, gyE - 5.0 * sc, q[2] - 2, gyE - 3.8 * sc))
        else:
            bc = C((30, 26, 44)) if mode == 'night' else C((26, 34, 48))
            img = lerp(img, full((0, 0, 0)) + bc, m)
            ix = np.floor((x - q[0]) / 3.5)
            iy = np.floor((y - q[1]) / 4.0)
            hsh = (np.sin(ix * 12.9898 + iy * 78.233 + rx) * 43758.5453) % 1.0
            lit = (hsh > 0.55) & ((x - q[0]) % 3.5 > 1.4) & ((y - q[1]) % 4.0 > 1.8)
            img = lerp(img, full((255, 210, 150)), lit * m * 0.7)
            # small neon at street level
            nc = NEON[r.integers(0, len(NEON))]
            nm = rect_m(q[0] + 2, gyE - 5.0 * sc, q[2] - 2, gyE - 3.8 * sc)
            img = lerp(img, full(nc), nm)
            E += C(nc) * nm[..., None] * 0.8
        rx += bw
    # ---- ground (road + sidewalk) base colours
    gm = (y >= gyE).astype(np.float32)
    zz = np.where(y > VY + 0.5, EYE * F / np.maximum(y - VY, 1e-3), 1e9)
    Xw = (x - VX) * zz / F
    aX = np.abs(Xw)
    if mode == 'day':
        road = C((88, 90, 96))
        tileA, tileB = C((182, 172, 160)), C((160, 150, 140))
    elif mode == 'night':
        road = C((20, 20, 28))
        tileA, tileB = C((30, 26, 33)), C((24, 22, 29))
    else:
        road = C((14, 18, 26))
        tileA, tileB = C((24, 28, 38)), C((20, 24, 33))
    atex = fbm(H, W, 30, 4, seed=31, sx=3)
    ground = road * (0.85 + 0.25 * atex[..., None])
    # sidewalk tiles 0.6m
    ti = (np.floor(Xw / 0.6) + np.floor(zz / 0.6)) % 2
    tile = lerp(full((0, 0, 0)) + tileA, full((0, 0, 0)) + tileB, ti * 0.6)
    jt = ((np.abs(Xw / 0.6 - np.round(Xw / 0.6)) < 0.025 * (zz / 4 + 0.4)) |
          (np.abs(zz / 0.6 - np.round(zz / 0.6)) < 0.03 * (zz / 4 + 0.4))).astype(np.float32)
    tile = lerp(tile, tile * 0.75, jt * 0.6)
    tile = lerp(tile, full((0, 0, 0)) + (tileA * 0.6 + tileB * 0.4) * 0.92, smooth(14, 30, zz))
    # tactile paving strip (盲道)
    tac = ((aX > 6.3) & (aX < 6.65)).astype(np.float32)
    tile = lerp(tile, full((215, 175, 50)) * (0.4 if night else 1.0), tac * 0.9)
    side = (aX > XR).astype(np.float32)
    ground = lerp(ground, tile, side)
    curb = ((aX > XR - 0.18) & (aX < XR)).astype(np.float32)
    ground = lerp(ground, full((200, 200, 195)) * (0.35 if night else 1.0), curb)
    # asphalt patches / tyre wear
    patch = smooth(0.62, 0.66, fbm(H, W, 120, 3, seed=33, sx=4))
    ground = lerp(ground, ground * 0.82, patch * (1 - side) * 0.7)
    wear = sum(np.exp(-((Xw - c) / 0.35) ** 2) for c in (-3.8, -1.3, 1.3, 3.8))
    ground = lerp(ground, ground * 0.9, np.clip(wear, 0, 1) * (1 - side) * smooth(60, 10, zz))
    mh = (((Xw + 1.6) ** 2 + (zz - 6.2) ** 2) < 0.36).astype(np.float32)
    mh_rim = mh * (((Xw + 1.6) ** 2 + (zz - 6.2) ** 2) > 0.27)
    ground = lerp(ground, ground * 0.55, mh)
    ground = lerp(ground, ground * 1.6, mh_rim * 0.7)
    ground = lerp(ground, ground * 0.75, mh * (np.sin(Xw * 25) > 0.3))
    # lane markings
    lanes = np.zeros((H, W), np.float32)
    lanes += ((np.abs(aX - 0.12) < 0.07)).astype(np.float32) * 1.0   # double yellow
    dash = ((zz % 9.0) < 4.5).astype(np.float32)
    lanes2 = (np.abs(aX - 2.5) < 0.07).astype(np.float32) * dash
    zebra = ((zz > 9) & (zz < 13.5) & (aX < XR - 0.4) & ((Xw % 1.0) < 0.5)).astype(np.float32)
    ground = lerp(ground, full((235, 190, 50)) * (0.55 if night else 1.0), lanes * (1 - zebra) * gm)
    ground = lerp(ground, full((235, 235, 230)) * (0.5 if night else 0.95), np.clip(lanes2 + zebra, 0, 1) * (1 - side) * 0.9)
    gm = gm * (y > VY + 1) * blur((aX < XB).astype(np.float32), 0.7)
    # ---- facades
    units = []
    for sd in (-1, 1):
        z = ZE - 6
        k = 0
        while z > 4.0:
            ln = r.uniform(6, 10)
            units.append((sd, max(z - ln, 3.0), z, k))
            z -= ln
            k += 1
    units.sort(key=lambda u: -u[2])
    wall_cols = [(225, 218, 205), (205, 205, 200), (230, 210, 185), (190, 200, 205), (235, 225, 215), (200, 180, 170)]
    names = list(SHOP_NAMES)
    rn = rng0(5)
    rn.shuffle(names)
    ni = 0
    for sd, z0, z1, k in units:
        X = XB * sd
        hm = r.uniform(13, 22)
        ppm = int(np.clip(1.15 * F / z0, 14, 110))
        uc = wall_cols[r.integers(0, len(wall_cols))]
        if night:
            uc = tuple(int(c * 0.28 + 6) for c in uc)
        sc_ = SIGN_COLS[r.integers(0, len(SIGN_COLS))]
        tex, em = facade_tex(z1 - z0, hm, ppm, night, r, names[ni % len(names)], sc_, uc)
        ni += 1
        if sd < 0:
            q = [P(X, hm, z0), P(X, hm, z1), P(X, 0, z1), P(X, 0, z0)]
        else:
            q = [P(X, hm, z1), P(X, hm, z0), P(X, 0, z0), P(X, 0, z1)]
        before = img
        img = paste_quad(img, tex, q)
        if night:
            ea = em.convert('RGBA')
            ea.putalpha(tex.getchannel('A'))
            E = paste_quad(E, ea, q)
        # side shading: right side facades slightly darker
        if sd > 0 and not night:
            diff = np.abs(img - before).sum(-1) > 0
            img = np.where(diff[..., None], img * 0.88, img)
    # ---- reflections on wet ground
    if night:
        yb = np.minimum(VY + EYE * np.abs(x[0] - VX) / XB, gyE)
        ys = 2 * yb[None, :] - y
        xs = x.copy()
        if rain:
            xs = xs + (fbm(H, W, 6, 3, seed=41, sx=0.3) - 0.5) * 10
            ys = ys + (fbm(H, W, 3, 2, seed=42, sx=4) - 0.5) * 6
        src = img * 0.45 + E * 1.1
        refl = np.stack([ndimage.map_coordinates(src[..., c], [np.clip(ys, 0, H - 1), xs], order=1, mode='nearest')
                         for c in range(3)], -1)
        refl = np.stack([ndimage.gaussian_filter(refl[..., c], (1.0, 2.5)) for c in range(3)], -1)
        # vertical smear
        refl = np.stack([ndimage.uniform_filter1d(refl[..., c], 31 if rain else 17, axis=0) for c in range(3)], -1)
        refl *= np.exp(-np.maximum(y - yb[None, :], 0) / 420)[..., None]
        wet = 0.45 if not rain else 0.7
        puddle = smooth(0.45, 0.6, fbm(H, W, 90, 4, seed=43, sx=3))
        wk = wet * (0.6 + 0.4 * puddle) * gm * (1 - 0.75 * side * (1 - puddle * 0.5))
        ground = ground * (1 - wk[..., None] * 0.5) + refl * wk[..., None]
    else:
        ground = ground
    img = lerp(img, ground, gm)
    # ---- objects (far to near): blade signs, lamps, people, scooters, stalls
    objs = []
    for zb in np.arange(14, ZE - 8, 9.0):
        for sd in (-1, 1):
            if r.random() < 0.75:
                objs.append(('blade', zb + r.uniform(-2, 2), sd))
    for zl in np.arange(10, ZE, 22.0):
        for sd in (-1, 1):
            objs.append(('lamp', zl + (0 if sd < 0 else 11), sd))
    npeople = 26
    for i in range(npeople):
        zp_, xp_ = r.uniform(6, 70), r.choice([-1, 1]) * r.uniform(5.6, 7.6)
        if night and xp_ > 0 and 6 < zp_ < 13:
            continue
        objs.append(('person', zp_, xp_))
    for i in range(7):
        objs.append(('rider', r.uniform(9, 60), r.uniform(-4.4, 4.4)))
    for zp in np.arange(8.0, 40, 0.75):
        if r.random() < 0.55:
            objs.append(('parked', zp, -1 if r.random() < 0.6 else 1))
    if night:
        objs.append(('stall', 10.5, 1))
    objs.sort(key=lambda o: -o[1])
    img_before_objs = img.copy()
    E_before_objs = E.copy()
    ped_cols = [(60, 70, 90), (120, 60, 60), (70, 90, 70), (40, 40, 45), (150, 130, 110), (90, 80, 120), (200, 200, 200)]
    steam_pts = []
    for kind, z, v in objs:
        sc = F / z
        if kind == 'blade':
            sd = v
            X0, X1 = XB * sd, (XB - 1.0) * sd
            yt = r.uniform(7.0, 10.5)
            hgt = r.uniform(3.5, 5.0)
            a_, b_ = P(X0, yt, z), P(X1, yt - hgt, z)
            x0, x1 = min(a_[0], b_[0]), max(a_[0], b_[0])
            bw_, bh_ = int(x1 - x0), int(b_[1] - a_[1])
            if bw_ < 4 or x1 < -50 or x0 > W + 50:
                continue
            if night:
                nc = NEON[r.integers(0, len(NEON))]
                sg = sign_img(BLADE[r.integers(0, len(BLADE))], bw_, bh_, (20, 15, 30), nc, vertical=True,
                              border=nc, fill=0.66, stroke=max(0, bw_ * 0.01))
                img, am = paste_at(img, sg, x0, a_[1])
                lay = np.zeros((H, W, 3), np.float32)
                lay, _ = paste_at(lay, sg, x0, a_[1])
                E = E * (1 - am[..., None]) + lay * am[..., None] * 1.0
            else:
                bg, fg = SIGN_COLS[r.integers(0, len(SIGN_COLS))]
                sg = sign_img(BLADE[r.integers(0, len(BLADE))], bw_, bh_, bg, fg, vertical=True,
                              border=(240, 240, 240), fill=0.66)
                img, am = paste_at(img, sg, x0, a_[1])
            # bracket
            img = over(img, (60, 60, 65), Mask().line([P(X0, yt + 0.2, z), P(X1, yt + 0.2, z)], max(1, 0.06 * sc)).get())
        elif kind == 'lamp':
            sd = v
            X = (XR + 0.3) * sd
            b = P(X, 0, z)
            t = P(X, 8.5, z)
            arm = P(X - sd * 1.8, 8.6, z)
            lm = Mask()
            lm.tapered([b, t], 0.22 * sc, 0.12 * sc)
            lm.tapered([t, arm], 0.1 * sc, 0.08 * sc)
            lm.ellipse((arm[0] - 0.45 * sc, arm[1] - 0.1 * sc, arm[0] + 0.45 * sc, arm[1] + 0.18 * sc))
            img = over(img, (70, 72, 78) if not night else (20, 20, 26), lm.get())
            if night:
                lc = (255, 200, 130) if not rain else (220, 230, 255)
                E += C(lc) * radial(arm[0], arm[1] + 0.1 * sc, 0.5 * sc, power=0.7)[..., None] * 1.5
                pool = radial(P(X - sd * 1.8, 0, z)[0], P(0, 0, z)[1], 4.0 * sc, power=1.6, sy=0.25)
                img = screen(img, lc, pool * gm * 0.22)
                cone = np.clip(1 - np.abs(x - arm[0]) / (0.3 * sc + (y - arm[1]) * 0.55), 0, 1) ** 2 * (y > arm[1]) * smooth(P(0, 0, z)[1], arm[1], y)
                img = screen(img, lc, cone * 0.04)
        elif kind == 'person':
            X = v
            b = P(X, 0, z)
            if b[0] < -80 or b[0] > W + 80:
                continue
            m = Mask()
            umb = person(m, b[0], b[1], 1.7 * sc * r.uniform(0.9, 1.06), r, umbrella=rain, bag=r.random() < 0.3)
            pm = m.get()
            if night:
                pc = C((14, 12, 20)) if not rain else C((10, 14, 22))
            else:
                pc = C(ped_cols[r.integers(0, len(ped_cols))]) * 0.55 + C((70, 75, 90)) * 0.2
                pc = lerp(pc, C((190, 200, 215)), smooth(6, 70, z) * 0.6)
            img = lerp(img, full((0, 0, 0)) + pc, pm)
            if umb:
                um = Mask().poly(umb).get()
                ucol = [(30, 40, 70), (150, 30, 40), (30, 30, 35), (40, 110, 120), (200, 190, 60)][r.integers(0, 5)]
                img = lerp(img, full(ucol) * 0.55, um)
                img = screen(img, (180, 200, 255), um * smooth(b[1] - 2.1 * sc, b[1] - 1.85 * sc, y) * 0.2)
                pm = np.maximum(pm, um)
            if night:
                # reflection of figure
                rows = np.arange(H)
                yb0 = b[1]
                sr = np.clip(2 * yb0 - rows, 0, H - 1).astype(int)
                rm = pm[sr, :] * (rows[:, None] > yb0)
                img = lerp(img, img * 0.45, blur(rm, 2) * 0.6)
            else:
                img *= (1 - 0.3 * radial(b[0], b[1], 0.5 * sc, power=1.0, sy=0.2))[..., None]
        elif kind == 'parked':
            X = v * (XR + 1.3)
            b = P(X, 0, z)
            if b[0] < -150 or b[0] > W + 150:
                continue
            wmk, bmk, smk, lxy = scooter_side(b[0], b[1], sc, facing=-v)
            bc = C([(225, 225, 230), (45, 45, 50), (200, 60, 60), (60, 120, 200), (240, 200, 60), (120, 200, 190)][r.integers(0, 6)])
            k_ = 0.22 if night else 0.9
            if not night:
                img *= (1 - 0.3 * radial(b[0], b[1], 0.9 * sc, power=1.0, sy=0.15))[..., None]
            img = lerp(img, full((25, 25, 28)), wmk * (0.75 if night else 1))
            img = lerp(img, full((0, 0, 0)) + bc * k_, bmk)
            img = screen(img, (255, 255, 255), bmk * smooth(b[1] - 0.6 * sc, b[1] - 1.0 * sc, y) * (0.05 if night else 0.18))
            img = lerp(img, full((30, 28, 30)), smk)
            continue
        elif kind == 'rider':
            if True:
                X = v
            b = P(X, 0, z)
            if b[0] < -80 or b[0] > W + 80:
                continue
            m = Mask()
            rider = kind == 'rider'
            box = rider and r.random() < 0.75
            parts = scooter_rear(m, b[0], b[1], sc, box=box, rider=rider)
            pm = m.get()
            if kind == 'parked':
                bc = C([(220, 220, 225), (40, 40, 45), (200, 60, 60), (60, 120, 200), (240, 200, 60)][r.integers(0, 5)])
                if night:
                    bc = bc * 0.18
                else:
                    bc = bc * 0.75
            else:
                bc = C((30, 30, 36)) if not night else C((10, 10, 14))
            img = lerp(img, full((0, 0, 0)) + bc, pm)
            if rider:
                jc = (245, 195, 30) if r.random() < 0.6 else (40, 120, 220)
                hx, hy, hr = parts['helmet']
                hm_ = Mask().circle(hx, hy, hr).get()
                torso = Mask().poly([(b[0] - 0.24 * sc, b[1] - 0.85 * sc), (b[0] + 0.24 * sc, b[1] - 0.85 * sc),
                                     (b[0] + 0.2 * sc, b[1] - 1.45 * sc), (b[0] - 0.2 * sc, b[1] - 1.45 * sc)]).get()
                k_ = 0.35 if night else 1.0
                img = lerp(img, full(jc) * k_ * 0.85, torso)
                img = lerp(img, full((255, 215, 40) if jc[2] < 100 else (40, 120, 220)) * k_, hm_)
                img = lerp(img, full((20, 20, 24)), rect_m(b[0] - 0.2 * sc, b[1] - 1.5 * sc, b[0] + 0.2 * sc, b[1] - 1.42 * sc) * (1 - hm_))
            if box:
                bx0, by0, bx1, by1 = parts['box']
                bm = rect_m(bx0, by0, bx1, by1)
                boxc = lerp(full((255, 205, 30)), full((200, 140, 10)), smooth(bx0, bx1, x) * 0.6)
                img = lerp(img, boxc * (0.45 if night else 1.0), bm)
                img = over(img, (255, 245, 200) if not night else (110, 100, 70), rect_m(bx0, by0, bx1, by0 + (by1 - by0) * 0.12) * bm)
                img = over(img, (60, 60, 60), rect_m(bx0 + (bx1 - bx0) * 0.3, by0 + (by1 - by0) * 0.45, bx1 - (bx1 - bx0) * 0.3, by0 + (by1 - by0) * 0.6) * bm)
            if night:
                tx, ty, tr_ = parts['tail']
                E += C((255, 30, 30)) * radial(tx, ty, tr_, power=0.6)[..., None] * 1.5
                if rider:
                    # long red streak reflection on wet road
                    streak = np.exp(-((x - tx) / (tr_ * 0.8)) ** 2) * (y > b[1]) * np.exp(-(y - b[1]) / (0.9 * sc))
                    img = screen(img, (255, 40, 40), streak * 0.6)
            else:
                img *= (1 - 0.35 * radial(b[0], b[1], 0.5 * sc, power=1.0, sy=0.2))[..., None]
        elif kind == 'stall':
            # late-night food cart on the right sidewalk, seen front-on
            X0, X1 = 5.5, 7.6
            a_, b_ = P(X0, 1.0, z), P(X1, 0.0, z)
            cart = rect_m(a_[0], a_[1], b_[0], b_[1])
            img = lerp(img, full((190, 190, 195)) * 0.45, cart)
            img = screen(img, (255, 170, 90), cart * smooth(b_[1], a_[1], y) * 0.4)
            # canopy
            c0, c1 = P(X0 - 0.3, 2.6, z), P(X1 + 0.3, 2.3, z)
            can = Mask().poly([(c0[0], c0[1]), (c1[0], c0[1]), (c1[0] + 0.2 * sc, c1[1]), (c0[0] - 0.2 * sc, c1[1])]).get()
            stripes = (np.sin((x - c0[0]) / (0.25 * sc) * math.pi) > 0).astype(np.float32)
            img = lerp(img, lerp(full((200, 40, 40)), full((240, 235, 225)), stripes) * 0.75, can)
            for px_ in (X0 - 0.2, X1 + 0.2):
                img = over(img, (40, 40, 45), Mask().line([P(px_, 2.3, z), P(px_, 0, z)], 0.06 * sc).get())
            # bulb + menu
            bp = P((X0 + X1) / 2, 2.15, z)
            E += C((255, 210, 140)) * radial(bp[0], bp[1], 0.15 * sc, power=0.6)[..., None] * 2
            img = screen(img, (255, 190, 110), radial(bp[0], bp[1] + 0.8 * sc, 2.2 * sc, power=2) * 0.6)
            mn = sign_img('炒粉 烤串', int(1.6 * sc), int(0.36 * sc), (240, 230, 200), (180, 30, 30), fill=0.7)
            img, _ = paste_at(img, mn, P(X0 + 0.25, 1.0, z)[0], P(0, 0.9, z)[1])
            # wok + steam
            img = over(img, (20, 20, 22), Mask().ellipse((a_[0] + 0.3 * sc, a_[1] - 0.12 * sc, a_[0] + 1.0 * sc, a_[1] + 0.05 * sc)).get())
            steam_pts.append((a_[0] + 0.65 * sc, a_[1] - 0.1 * sc, sc))
            # cook silhouette
            m = Mask()
            person(m, P(7.0, 0, z + 0.8)[0], P(7.0, 0, z + 0.8)[1], 1.7 * F / (z + 0.8), r)
            pm = m.get() * (1 - cart)
            img = lerp(img, full((15, 12, 18)), pm)
            # stools
            for sx in (5.6, 6.6):
                s0 = P(sx - 0.9, 0.45, z - 2.2)
                s1 = P(sx - 0.6, 0.0, z - 2.2)
                img = over(img, (40, 90, 170), Mask().rect((s0[0], s0[1], s1[0], s1[1])).get() * 0.85)
    occ = np.clip(np.abs(img - img_before_objs).sum(-1) * 25, 0, 1)
    changed = (np.abs(E - E_before_objs).sum(-1) > 1e-4)[..., None]
    E_occ = np.where(changed, E, E * (1 - occ[..., None] * 0.9))
    # ---- steam
    for sx, sy, sc in steam_pts:
        sm = np.zeros((H, W), np.float32)
        rs = rng0(55)
        n_ = fbm(H, W, 25, 3, seed=56)
        for i in range(18):
            t = i / 18
            sm += radial(sx + math.sin(t * 7) * 0.25 * sc + t * 0.5 * sc, sy - t * 2.4 * sc, (0.2 + t * 0.45) * sc, power=1.2) * (1 - t) ** 0.7
        sm = np.clip(sm, 0, 1) * (0.5 + 0.7 * n_)
        img = lerp(img, img * 0.6 + C((235, 228, 222)) * 0.6, np.clip(sm, 0, 1) * 0.55)
    # ---- overhead cables
    cm = Mask()
    for zc in (11, 19, 33):
        a_ = P(-XB, 9 + zc * 0.05, zc)
        b_ = P(XB, 8.5, zc + 4)
        cm.line(bezier(a_, ((a_[0] + b_[0]) / 2, max(a_[1], b_[1]) + 50 * 12 / zc), b_, n=40), max(1.0, 18 / zc))
        a2 = P(-XB, 7.8, zc + 2)
        cm.line(bezier(a2, ((a2[0] + b_[0]) / 2, max(a2[1], b_[1]) + 70 * 12 / zc), P(XB, 9.5, zc + 1), n=40), max(1.0, 14 / zc))
    img = over(img, (40, 40, 45) if not night else (8, 8, 12), cm.get() * 0.85)
    # ---- glow from emissive
    if night:
        E = E_occ
        img = 1 - (1 - img) * (1 - np.clip(E * 0.55, 0, 1))
        g = blur(E, 5) * 0.6 + blur(E, 20) * 0.5 + blur(E, 60) * 0.22
        img = 1 - (1 - img) * (1 - np.clip(g, 0, 1))
        img = bloom(img, 0.75, 18, 0.4)
    else:
        img = screen(img, (255, 248, 230), radial(1500, -100, 1300, power=2) * 0.25)
        img = bloom(img, 0.85, 30, 0.2)
    if rain:
        img = lerp(img, full((60, 80, 110)), smooth(VY + 40, 0, y) * 0.22)
        if add_rain:
            img = rain_layer(img, seed=77)
    return img


def rain_layer(img, seed=77, n=2600, strength=1.0, angle=0.18, splashes=True, ground_y=600):
    """Heavy rain: streaks in 3 depth layers, ground splashes, mist."""
    x, y = grid()
    r = rng0(seed)
    # mist
    mist = fbm(H, W, 260, 4, seed=seed, sx=2.5) * smooth(150, 800, y)
    img = screen(img, (90, 115, 150), mist * 0.22 * strength)
    for layer, (cnt, ln, wd, al, bl) in enumerate(((n, (18, 40), 1.0, 0.25, 0.6), (n // 3, (50, 110), 1.6, 0.3, 0.9),
                                                    (n // 12, (140, 260), 3.0, 0.22, 1.6))):
        m = Mask(ss=2)
        for _ in range(cnt):
            px, py = r.uniform(-100, W + 100), r.uniform(-50, H)
            L = r.uniform(*ln)
            m.line([(px, py), (px - L * angle, py + L)], wd * r.uniform(0.7, 1.2))
        a = m.get(bl)
        img = screen(img, (200, 215, 240), a * al * strength)
    if splashes:
        sm = Mask(ss=2)
        for _ in range(260):
            px, py = r.uniform(0, W), r.uniform(ground_y, H)
            s = (py - ground_y) / (H - ground_y) * 14 + 2
            sm.ellipse((px - s, py - s * 0.25, px + s, py + s * 0.25))
            sm.ellipse((px - s * 0.75, py - s * 0.19, px + s * 0.75, py + s * 0.19), v=0)
            # little crown
            for k in (-1, 1):
                sm.line([(px + k * s * 0.3, py - s * 0.1), (px + k * s * 0.5, py - s * 0.45)], max(1, s * 0.07))
        img = screen(img, (210, 225, 250), sm.get(0.8) * 0.25 * strength)
    return img


def city_street_day():
    return city_street('day')


def city_street_night():
    return city_street('night')


def city_rain_night():
    img = city_street('rain')
    # cool blue cast
    img = img * np.array([0.88, 0.96, 1.1], np.float32)
    return img


class Layer:
    """Many small coloured shapes on one supersampled RGBA layer; composite once (fast)."""

    def __init__(self, ss=2):
        self.ss = ss
        self.im = Image.new('RGBA', (W * ss, H * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _c(self, col, a=1.0):
        return tuple(int(v) for v in col[:3]) + (int(255 * a),)

    def ellipse(self, box, col, a=1.0):
        s = self.ss
        x0, y0, x1, y1 = box
        self.d.ellipse((x0 * s, y0 * s, x1 * s, y1 * s), fill=self._c(col, a))

    def circle(self, cx, cy, r, col, a=1.0):
        self.ellipse((cx - r, cy - r, cx + r, cy + r), col, a)

    def rect(self, box, col, a=1.0):
        s = self.ss
        x0, y0, x1, y1 = box
        self.d.rectangle((x0 * s, y0 * s, x1 * s, y1 * s), fill=self._c(col, a))

    def poly(self, pts, col, a=1.0):
        self.d.polygon([(px * self.ss, py * self.ss) for px, py in pts], fill=self._c(col, a))

    def line(self, pts, w, col, a=1.0):
        self.d.line([(px * self.ss, py * self.ss) for px, py in pts], fill=self._c(col, a), width=max(1, int(w * self.ss)))

    def comp(self, img, clip=None):
        im = self.im.resize((W, H), Image.LANCZOS)
        arr = np.asarray(im, np.float32) / 255.0
        a = arr[..., 3] if clip is None else arr[..., 3] * clip
        rgb = arr[..., :3] / np.maximum(arr[..., 3:4], 1e-3) if False else arr[..., :3]
        return lerp(img, rgb, a)


# ------------------------------------------------------------------ generic 3D helpers for interiors / stalls
class Cam:
    def __init__(self, F=1000.0, VX=960.0, VY=520.0, EYE=1.6, CX=0.0):
        self.F, self.VX, self.VY, self.EYE, self.CX = F, VX, VY, EYE, CX

    def P(self, X, Y, Z):
        return (self.VX + (X - self.CX) * self.F / Z, self.VY + (self.EYE - Y) * self.F / Z)

    def sc(self, Z):
        return self.F / Z


def quad(img, pts, col, blur_r=0.6, alpha=1.0):
    m = Mask().poly(pts).get(blur_r) * alpha
    c = np.asarray(col, np.float32)
    if c.ndim == 1:
        c = C(c) if c.max() > 1.0 else c
    return lerp(img, c if c.ndim == 3 else np.ones((H, W, 3), np.float32) * c, m), m


def box3(img, cam, X0, X1, Y0, Y1, Z0, Z1, col, shade=(1.0, 0.82, 0.66), front_col=None, top_col=None):
    """Axis aligned box; draws visible faces (top/bottom, side, front)."""
    P = cam.P
    c = C(col) if max(col) > 1.0 else np.array(col, np.float32)
    ms = []
    # side face
    if X0 > cam.CX:
        img, m = quad(img, [P(X0, Y1, Z0), P(X0, Y1, Z1), P(X0, Y0, Z1), P(X0, Y0, Z0)], c * shade[2]); ms.append(m)
    elif X1 < cam.CX:
        img, m = quad(img, [P(X1, Y1, Z0), P(X1, Y1, Z1), P(X1, Y0, Z1), P(X1, Y0, Z0)], c * shade[2]); ms.append(m)
    # top / bottom
    if Y1 < cam.EYE:
        img, m = quad(img, [P(X0, Y1, Z0), P(X1, Y1, Z0), P(X1, Y1, Z1), P(X0, Y1, Z1)], top_col if top_col is not None else c * shade[0]); ms.append(m)
    elif Y0 > cam.EYE:
        img, m = quad(img, [P(X0, Y0, Z0), P(X1, Y0, Z0), P(X1, Y0, Z1), P(X0, Y0, Z1)], c * shade[2] * 0.9); ms.append(m)
    img, m = quad(img, [P(X0, Y1, Z0), P(X1, Y1, Z0), P(X1, Y0, Z0), P(X0, Y0, Z0)], front_col if front_col is not None else c * shade[1]); ms.append(m)
    return img, np.clip(sum(ms), 0, 1)


def plastic_stool(img, cam, X, Z, col, s=1.0):
    """Classic Chinese plastic stool (trapezoid legs with arch cut-outs)."""
    P = cam.P
    h, tw, bw = 0.45 * s, 0.17 * s, 0.21 * s
    c = C(col)
    # shadow
    sc_ = cam.sc(Z)
    gx, gy = P(X, 0, Z)
    img *= (1 - 0.45 * radial(gx, gy, 0.32 * sc_, power=1.2, sy=0.25))[..., None]
    for face, (Zf, dark) in enumerate(((Z + bw, 0.55), (Z - bw, 0.85))):
        pts = [P(X - tw, h, Zf - (bw - tw) * (1 if face else -1)), P(X + tw, h, Zf - (bw - tw) * (1 if face else -1)),
               P(X + bw, 0, Zf), P(X - bw, 0, Zf)]
        m = Mask().poly(pts)
        ax, ay = P(X, 0.25 * s, Zf)
        r = 0.11 * s * cam.sc(Zf)
        m.ellipse((ax - r, ay - r * 1.1, ax + r, ay + r * 3), v=0)
        img = lerp(img, full((0, 0, 0)) + c * dark, m.get(0.6))
    # side face (toward camera)
    sd = -1 if X > cam.CX else 1
    Xs = X + sd * bw
    pts = [P(X + sd * tw, h, Z - tw), P(X + sd * tw, h, Z + tw), P(Xs, 0, Z + bw), P(Xs, 0, Z - bw)]
    m = Mask().poly(pts)
    ax, ay = P(X + sd * (tw + bw) / 2, 0.22 * s, Z)
    r = 0.09 * s * cam.sc(Z)
    m.ellipse((ax - r * 0.6, ay - r, ax + r * 0.6, ay + r * 3), v=0)
    img = lerp(img, full((0, 0, 0)) + c * 0.7, m.get(0.6))
    # seat top
    top = [P(X - tw - 0.01, h, Z - tw - 0.01), P(X + tw + 0.01, h, Z - tw - 0.01), P(X + tw + 0.01, h, Z + tw + 0.01), P(X - tw - 0.01, h, Z + tw + 0.01)]
    img, _ = quad(img, top, c * 1.08)
    img, _ = quad(img, [P(X - tw - 0.01, h, Z - tw - 0.01), P(X + tw + 0.01, h, Z - tw - 0.01), P(X + tw + 0.01, h - 0.03, Z - tw - 0.01), P(X - tw - 0.01, h - 0.03, Z - tw - 0.01)], c * 0.9)
    # little highlight
    a, b = P(X - tw * 0.7, h, Z - tw * 0.5), P(X + tw * 0.2, h, Z - tw * 0.5)
    img = screen(img, (255, 255, 255), Mask().line([a, b], max(1, 0.012 * cam.sc(Z))).get(1) * 0.35)
    return img


def bottle(img, cx, by, hgt, col=(40, 120, 60), label=(230, 220, 190), alpha=0.92):
    w = hgt * 0.26
    m = Mask()
    m.rect((cx - w / 2, by - hgt * 0.62, cx + w / 2, by))
    m.ellipse((cx - w / 2, by - hgt * 0.72, cx + w / 2, by - hgt * 0.52))
    m.poly([(cx - w / 2, by - hgt * 0.62), (cx + w / 2, by - hgt * 0.62), (cx + w * 0.17, by - hgt * 0.85), (cx - w * 0.17, by - hgt * 0.85)])
    m.rect((cx - w * 0.15, by - hgt, cx + w * 0.15, by - hgt * 0.84))
    bm = m.get()
    x, y = grid()
    bc = lerp(full(col) * 0.6, full(col) * 1.25, np.clip(1 - np.abs(x - (cx - w * 0.15)) / (w * 0.5), 0, 1))
    img = lerp(img, bc, bm * alpha)
    img = over(img, label, rect_m(cx - w / 2, by - hgt * 0.45, cx + w / 2, by - hgt * 0.2) * bm)
    img = over(img, (200, 40, 40), rect_m(cx - w / 2, by - hgt * 0.36, cx + w / 2, by - hgt * 0.3) * bm)
    img = screen(img, (255, 255, 255), Mask().line([(cx - w * 0.25, by - hgt * 0.58), (cx - w * 0.25, by - hgt * 0.05)], max(1, w * 0.08)).get(1) * bm * 0.6)
    return img


def handwritten(lines, w, h, bg=(245, 242, 230), cols=((30, 30, 35), (200, 30, 30)), seed=0, title=None, size=None):
    """Marker-on-board look: jittered characters."""
    r = rng0(seed)
    S = 2
    im = Image.new('RGBA', (w * S, h * S), tuple(bg) + (255,))
    d = ImageDraw.Draw(im)
    nl = len(lines) + (1.4 if title else 0)
    ml = max(len(l) for l in lines)
    sz = size or int(min(h * 0.8 / nl, w * 0.84 / ml))
    y = h * 0.08
    if title:
        f = cfont(sz * 1.25 * S)
        x = w * 0.12
        for ch in title:
            d.text((x * S, (y + r.uniform(-2, 2)) * S), ch, font=f, fill=cols[1] + (255,), stroke_width=int(sz * 0.05 * S), stroke_fill=cols[1] + (255,))
            x += sz * 1.25 * r.uniform(0.95, 1.08)
        y += sz * 1.55
        d.line([(w * 0.1 * S, (y - sz * 0.15) * S), (w * 0.9 * S, (y - sz * 0.25) * S)], fill=cols[1] + (255,), width=int(sz * 0.06 * S))
    for li, line in enumerate(lines):
        x = w * 0.08
        for ch in line:
            f = cfont(sz * r.uniform(0.9, 1.05) * S)
            c = cols[0] if not ch.isdigit() and ch != '元' else cols[1]
            chim = Image.new('RGBA', (int(sz * 1.6 * S), int(sz * 1.6 * S)), (0, 0, 0, 0))
            ImageDraw.Draw(chim).text((sz * 0.2 * S, sz * 0.1 * S), ch, font=f, fill=c + (255,), stroke_width=int(sz * 0.04 * S), stroke_fill=c + (255,))
            chim = chim.rotate(r.uniform(-8, 8), resample=Image.BICUBIC)
            im.alpha_composite(chim, (int(x * S), int((y + r.uniform(-2, 2)) * S)))
            x += sz * (0.62 if ch in ' .' else 1.0) * r.uniform(0.95, 1.07)
        y += sz * 1.18
    # board frame
    d.rectangle((0, 0, w * S - 1, h * S - 1), outline=(120, 90, 60, 255), width=int(max(3, w * 0.025) * S))
    return im.resize((w, h), Image.LANCZOS)


def string_bulbs(img, E, pts_list, every=3, r=7, col=(255, 200, 120), wire=(25, 20, 18)):
    wm = Mask()
    bulbs = []
    for pts in pts_list:
        wm.line(pts, 1.6)
        for i in range(1, len(pts) - 1, every):
            bulbs.append(pts[i])
    img = over(img, wire, wm.get() * 0.9)
    bm = Mask()
    for bx, by in bulbs:
        bm.ellipse((bx - r * 0.75, by + 2, bx + r * 0.75, by + r * 2.4))
    a = bm.get()
    img = lerp(img, full((255, 245, 215)), a)
    for bx, by in bulbs:
        E[...] += C(col) * radial(bx, by + r * 1.2, r * 5, power=2.0)[..., None] * 0.9
    return img, E


# ------------------------------------------------------------------ street food stall
def street_food_night():
    x, y = grid()
    cam = Cam(F=1000, VX=900, VY=500, EYE=1.55)
    P = cam.P
    E = np.zeros((H, W, 3), np.float32)
    r = rng0(301)
    # background: night sky + far buildings (soft focus)
    bg = vgrad([(0, (10, 10, 26)), (0.7, (30, 24, 52)), (1, (60, 40, 60))], y0=0, y1=cam.VY)
    bx = -40.0
    while bx < 40:
        bw = r.uniform(5, 12)
        bh = r.uniform(12, 40)
        Z = 45.0
        a_, b_ = P(bx, bh, Z), P(bx + bw, 0, Z)
        m = rect_m(a_[0], a_[1], b_[0], b_[1])
        bc = C((24, 22, 40)) * r.uniform(0.8, 1.2)
        bg = lerp(bg, full((0, 0, 0)) + bc, m)
        ix = np.floor((x - a_[0]) / 9)
        iy = np.floor((y - a_[1]) / 10)
        hsh = (np.sin(ix * 12.9898 + iy * 78.233 + bx) * 43758.5453) % 1.0
        lit = (hsh > 0.6) & ((x - a_[0]) % 9 > 4) & ((y - a_[1]) % 10 > 4)
        wc = np.where((hsh > 0.9)[..., None], C((170, 210, 255)), C((255, 200, 130)))
        bg = lerp(bg, wc * 0.8, lit * m)
        bx += bw + r.uniform(0, 2)
    # neon bokeh
    pts = [(r.uniform(0, W), r.uniform(250, 520)) for _ in range(60)]
    cols = [NEON[r.integers(0, len(NEON))] if r.random() < 0.4 else (255, 200, 130) for _ in pts]
    bg = blur(bg, 3)
    bg = bokeh(bg, pts, cols, [r.uniform(8, 26) for _ in pts], 0.55, 0.35)
    # road (dark asphalt, slightly wet)
    gyz = cam.VY + cam.EYE * cam.F / 45
    road = vgrad([(0, (30, 28, 34)), (1, (22, 20, 26))], y0=gyz, y1=H) * (0.85 + 0.3 * fbm(H, W, 30, 4, seed=302, sx=3))[..., None]
    img = lerp(bg, road, smooth(gyz - 1, gyz + 1, y))
    # a passing scooter tail-light streak & far street lamp
    img = screen(img, (255, 190, 120), radial(1500, 330, 14, power=0.6))
    E += C((255, 190, 120)) * radial(1500, 330, 120, power=2)[..., None] * 0.6
    # sidewalk (where the stall is): concrete slab from Z 2 to 14, curb at Z=14
    zz = np.where(y > cam.VY + 0.5, cam.EYE * cam.F / np.maximum(y - cam.VY, 1e-3), 1e9)
    Xw = (x - cam.VX) * zz / cam.F
    side = (zz < 14).astype(np.float32)
    tile = full((70, 64, 62)) * (0.8 + 0.3 * fbm(H, W, 40, 4, seed=303)[..., None])
    jt = ((np.abs(Xw / 1.0 - np.round(Xw / 1.0)) < 0.02 * zz / 3 + 0.004) | (np.abs(zz / 1.0 - np.round(zz / 1.0)) < 0.015 * zz / 3)).astype(np.float32)
    tile = lerp(tile, tile * 0.7, jt * 0.6)
    stains = smooth(0.6, 0.75, fbm(H, W, 25, 4, seed=304))
    tile = lerp(tile, tile * 0.75, stains * 0.4)
    img = lerp(img, tile, side * (y > cam.VY))
    img = over(img, (120, 115, 110), (np.abs(zz - 14) < 0.12).astype(np.float32) * (y > cam.VY) * 0.8)
    # back wall of a closed shop behind the stall (shutters) on the left
    img, _ = box3(img, cam, -9, -1.5, 0, 4.2, 11.0, 11.5, (90, 92, 98))
    shut = rect_m(*P(-8.5, 3.2, 11.0), *P(-2.0, 0, 11.0))
    a_, b_ = P(-8.5, 3.2, 11.0), P(-2.0, 0, 11.0)
    stripes = (np.sin((y - a_[1]) / 6 * math.pi) > 0.3).astype(np.float32)
    img = lerp(img, lerp(full((105, 108, 115)), full((80, 82, 90)), stripes), rect_m(a_[0], a_[1], b_[0], b_[1]))
    sg = sign_img('老王烧烤', int(b_[0] - a_[0]), int(0.8 * cam.sc(11)), (190, 25, 30), (255, 230, 120), stroke=1)
    img, sm = paste_at(img, sg, a_[0], P(0, 4.05, 11)[1])
    lay = np.zeros((H, W, 3), np.float32)
    lay, _ = paste_at(lay, sg, a_[0], P(0, 4.05, 11)[1])
    E += lay * sm[..., None] * 0.45
    # canopy poles + tarp
    tarp_c = C((40, 90, 170))
    for (px, pz) in ((-3.2, 7.5), (3.4, 7.5)):
        img, _ = box3(img, cam, px - 0.03, px + 0.03, 0, 2.5, pz, pz + 0.06, (150, 150, 155))
    # stall cart (stainless) centre-left
    X0, X1, Z0, Z1 = -2.6, 0.9, 5.0, 5.8
    img, cm = box3(img, cam, X0, X1, 0.12, 0.95, Z0, Z1, (175, 178, 185))
    a_, b_ = P(X0, 0.95, Z0), P(X1, 0.12, Z0)
    steel = gradient([(0, (200, 205, 212)), (0.5, (140, 145, 152)), (1, (90, 92, 98))], smooth(a_[1], b_[1], y))
    steel = screen(steel, (255, 255, 255), np.exp(-((x - (a_[0] + (b_[0] - a_[0]) * 0.3)) / 20) ** 2) * 0.35)
    fm = rect_m(a_[0], a_[1], b_[0], b_[1])
    img = lerp(img, steel, fm)
    img = over(img, (60, 62, 66), Mask().line([P(X0, 0.55, Z0), P(X1, 0.55, Z0)], 2).get())
    # wheels
    for wx in (X0 + 0.3, X1 - 0.3):
        cx, cy = P(wx, 0.1, Z0)
        img = over(img, (20, 20, 22), Mask().circle(cx, cy, 0.1 * cam.sc(Z0)).get())
    # red banner on cart front
    bn = sign_img('正宗新疆烤串', int((b_[0] - a_[0]) * 0.8), int(0.22 * cam.sc(Z0)), (200, 30, 35), (255, 240, 150), stroke=1)
    img, _ = paste_at(img, bn, a_[0] + (b_[0] - a_[0]) * 0.1, P(0, 0.85, Z0)[1])
    # grill trough on top
    G0, G1 = X0 + 0.15, X1 - 0.6
    img, gm_ = box3(img, cam, G0, G1, 0.95, 1.08, Z0 + 0.1, Z0 + 0.55, (60, 60, 64))
    coal = [P(G0 + 0.05, 1.06, Z0 + 0.15), P(G1 - 0.05, 1.06, Z0 + 0.15), P(G1 - 0.05, 1.06, Z0 + 0.5), P(G0 + 0.05, 1.06, Z0 + 0.5)]
    cmask = Mask().poly(coal).get()
    cn = fbm(H, W, 5, 3, seed=305)
    coalc = gradient([(0, (60, 10, 0)), (0.5, (230, 80, 10)), (1, (255, 210, 90))], cn)
    img = lerp(img, coalc, cmask)
    E += coalc * cmask[..., None] * 0.9
    # skewers across the trough
    sk = Mask()
    meat = Mask()
    n_sk = 16
    for i in range(n_sk):
        sx = G0 + 0.1 + (G1 - G0 - 0.2) * i / (n_sk - 1)
        a2, b2 = P(sx, 1.09, Z0 + 0.05), P(sx + 0.02, 1.09, Z0 + 0.62)
        sk.line([P(sx, 1.09, Z0 - 0.08), b2], 1.5)
        for k in range(4):
            mz = Z0 + 0.18 + k * 0.1
            mx, my = P(sx + 0.005 * k, 1.1, mz)
            rr = 0.022 * cam.sc(mz)
            meat.ellipse((mx - rr, my - rr * 1.1, mx + rr, my + rr * 0.5))
    img = over(img, (200, 170, 120), sk.get())
    mm = meat.get()
    img = lerp(img, lerp(full((110, 45, 20)), full((170, 80, 30)), fbm(H, W, 3, 2, seed=306)), mm)
    img = screen(img, (255, 150, 60), mm * 0.25)
    # condiment tray / boxes on the right of cart top
    img, _ = box3(img, cam, X1 - 0.5, X1 - 0.1, 0.95, 1.05, Z0 + 0.1, Z0 + 0.5, (220, 220, 225))
    for k, cc in enumerate(((190, 40, 30), (230, 190, 70), (90, 60, 40))):
        cx, cy = P(X1 - 0.42 + k * 0.12, 1.06, Z0 + 0.25)
        img = over(img, cc, Mask().ellipse((cx - 0.04 * cam.sc(Z0), cy - 0.015 * cam.sc(Z0), cx + 0.04 * cam.sc(Z0), cy + 0.015 * cam.sc(Z0))).get())
    # grill fire glow on surroundings
    gx, gy = P((G0 + G1) / 2, 1.1, Z0 + 0.3)
    img = screen(img, (255, 120, 40), radial(gx, gy, 520, power=2.2) * 0.35)
    # menu board on an easel to the right
    mb_w, mb_h = int(0.75 * cam.sc(5.2)), int(1.0 * cam.sc(5.2))
    menu = handwritten(['羊肉串 3元', '烤鸡翅 8元', '烤韭菜 2元', '金针菇 5元', '烤茄子 10元', '啤酒 6元'], mb_w, mb_h,
                       seed=307, title='菜单')
    mx0, my0 = P(1.35, 1.55, 5.2)
    # easel legs
    for (ax, bx2) in ((0.15, 0.0), (0.6, 0.75)):
        img = over(img, (110, 80, 50), Mask().line([(mx0 + ax * cam.sc(5.2), my0 + 20), P(1.35 + bx2, 0, 5.4)], 6).get())
    img, _ = paste_at(img, menu.rotate(2, resample=Image.BICUBIC, expand=True), mx0 - 4, my0)
    # tarp (underside) + valance with string bulbs
    tq = [P(-3.6, 2.5, 7.6), P(3.8, 2.5, 7.6), P(3.8, 2.56, 6.9), P(-3.6, 2.56, 6.9)]
    tm = Mask().poly(tq).get()
    tc = tarp_c * (0.55 + 0.25 * fbm(H, W, 80, 3, seed=308, sx=2)[..., None])
    tc = screen(tc, (255, 150, 70), smooth(P(0, 2.5, 7.6)[1], 0, y) * 0.3)
    img = lerp(img, tc, tm)
    # valance scallops along far edge
    vm = Mask()
    xa, ya = P(-3.6, 2.5, 7.6)
    xb, yb_ = P(3.8, 2.5, 7.6)
    vm.rect((xa, ya - 2, xb, ya + 22))
    nsc = 14
    for i in range(nsc):
        cx = xa + (xb - xa) * (i + 0.5) / nsc
        rr = (xb - xa) / nsc / 2
        vm.ellipse((cx - rr, ya + 10, cx + rr, ya + 36))
    vmm = vm.get()
    stripe = (np.floor((x - xa) / ((xb - xa) / nsc)) % 2).astype(np.float32)
    img = lerp(img, lerp(full((200, 40, 40)), full((240, 235, 225)), stripe) * 0.85, vmm)
    wires = [bezier(P(-3.5, 2.45, 7.6), (cam.VX - 100, P(0, 2.2, 7.6)[1] + 30), P(3.7, 2.45, 7.6), n=40),
             bezier((0, 120), (700, 300), (1920, 90), n=50)]
    img, E = string_bulbs(img, E, wires, every=3, r=7)
    # foreground tables with stools, bottles, skewer plates
    tables = [(-2.0, 3.0, (215, 40, 45)), (2.7, 3.3, (40, 110, 200))]
    for (tx, tz, tcol) in tables:
        gx_, gy_ = P(tx, 0, tz)
        img *= (1 - 0.5 * radial(gx_, gy_, 0.9 * cam.sc(tz), power=1.2, sy=0.22))[..., None]
        # stools behind / beside the table first
        img = plastic_stool(img, cam, tx - 0.15, tz + 0.75, (40, 120, 210) if tcol[0] > 100 else (220, 50, 50))
        img = plastic_stool(img, cam, tx + 0.85, tz + 0.1, (220, 50, 50) if tcol[0] > 100 else (40, 120, 210))
        # table legs
        for lx in (tx - 0.55, tx + 0.55):
            for lz in (tz - 0.35, tz + 0.35):
                img, _ = box3(img, cam, lx - 0.02, lx + 0.02, 0, 0.7, lz, lz + 0.04, (170, 170, 175))
        img, tm_ = box3(img, cam, tx - 0.6, tx + 0.6, 0.7, 0.74, tz - 0.4, tz + 0.4, tcol, top_col=C(tcol) * 1.05)
        # stuff on table
        cx, cy = P(tx - 0.3, 0.74, tz)
        img = bottle(img, cx, cy, 0.3 * cam.sc(tz), (40, 130, 70))
        cx, cy = P(tx - 0.15, 0.74, tz + 0.15)
        img = bottle(img, cx, cy, 0.3 * cam.sc(tz + 0.15), (40, 130, 70))
        # plate of skewers
        px_, py_ = P(tx + 0.2, 0.745, tz - 0.05)
        sc_ = cam.sc(tz)
        img = over(img, (235, 235, 240), Mask().ellipse((px_ - 0.2 * sc_, py_ - 0.05 * sc_, px_ + 0.2 * sc_, py_ + 0.05 * sc_)).get())
        skm, mtm = Mask(), Mask()
        for k in range(5):
            a3 = (px_ - 0.24 * sc_ + k * 0.02 * sc_, py_ + 0.02 * sc_ - k * 0.012 * sc_)
            b3 = (px_ + 0.16 * sc_ + k * 0.02 * sc_, py_ - 0.03 * sc_ - k * 0.012 * sc_)
            skm.line([a3, b3], max(1, 0.006 * sc_))
            for j in range(4):
                t = 0.35 + j * 0.15
                mtm.circle(a3[0] + (b3[0] - a3[0]) * t, a3[1] + (b3[1] - a3[1]) * t, 0.018 * sc_)
        img = over(img, (210, 180, 130), skm.get())
        img = lerp(img, full((140, 60, 25)), mtm.get())
        # plastic cup
        cx, cy = P(tx + 0.45, 0.74, tz + 0.2)
        cw = 0.04 * cam.sc(tz)
        img = lerp(img, full((240, 230, 200)), Mask().poly([(cx - cw, cy - cw * 2.6), (cx + cw, cy - cw * 2.6), (cx + cw * 0.75, cy), (cx - cw * 0.75, cy)]).get() * 0.7)
        img = over(img, (230, 170, 50), Mask().poly([(cx - cw * 0.95, cy - cw * 1.8), (cx + cw * 0.95, cy - cw * 1.8), (cx + cw * 0.75, cy), (cx - cw * 0.75, cy)]).get() * 0.7)
        # front stool
        img = plastic_stool(img, cam, tx - 0.2, tz - 0.8, (40, 120, 210) if tcol[0] > 100 else (220, 50, 50))
        # table shadow on ground
    # beer crate + empty bottles on ground, skewer sticks litter
    img, _ = box3(img, cam, 0.9, 1.4, 0, 0.3, 3.4, 3.75, (40, 120, 60))
    for k in range(4):
        cx, cy = P(0.98 + k * 0.11, 0.3, 3.55)
        img = bottle(img, cx, cy, 0.3 * cam.sc(3.55), (40, 130, 70))
    lit = Mask()
    for k in range(14):
        lx, lz = r.uniform(-3, 2.5), r.uniform(2.3, 4.5)
        a4 = P(lx, 0, lz)
        ang = r.uniform(0, math.pi)
        L = 0.25 * cam.sc(lz)
        lit.line([a4, (a4[0] + math.cos(ang) * L, a4[1] + math.sin(ang) * L * 0.25)], 1.6)
    img = over(img, (180, 150, 110), lit.get() * 0.9)
    # smoke plume from the grill, lit warm from below
    sm = np.zeros((H, W), np.float32)
    n_ = fbm(H, W, 40, 4, seed=309)
    for i in range(26):
        t = i / 26
        sx = gx + math.sin(t * 5.5) * 50 * t + t * 200
        sy = gy - t * 480
        sm += radial(sx, sy, 50 + t * 160, power=1.3) * (1 - t) ** 0.8 * 0.55
    sm = np.clip(sm * (0.4 + 0.9 * n_), 0, 1)
    smoke_c = lerp(full((255, 200, 150)), full((150, 140, 160)), smooth(gy, gy - 500, y))
    img = lerp(img, img * 0.5 + smoke_c * 0.55, sm * 0.7)
    # warm wash under the canopy
    img = screen(img, (255, 170, 90), radial(900, 520, 900, power=2.0, sy=0.7) * 0.18)
    g = blur(E, 4) * 0.6 + blur(E, 18) * 0.6 + blur(E, 50) * 0.35
    img = 1 - (1 - img) * (1 - np.clip(E * 0.6, 0, 1))
    img = 1 - (1 - img) * (1 - np.clip(g, 0, 1))
    # embers
    em = Mask(ss=2)
    for _ in range(40):
        ex, ey = gx + r.normal(0, 90), gy - abs(r.normal(0, 200))
        em.circle(ex, ey, r.uniform(1, 2.5))
    img = screen(img, (255, 170, 60), em.get(0.6))
    img = bloom(img, 0.7, 20, 0.45)
    return img


# ------------------------------------------------------------------ claw machine arcade
def claw_machine(img, E, cam, X, Z, col, r, plush_seed=0, glass_w=0.8):
    P = cam.P
    w = glass_w
    X0, X1 = X - w / 2, X + w / 2
    D = 0.8
    c = C(col)
    # base cabinet
    img, _ = box3(img, cam, X0, X1, 0, 0.95, Z, Z + D, col)
    # glass case frame (posts)
    img, _ = box3(img, cam, X0, X1, 0.95, 1.0, Z, Z + D, col)
    a_, b_ = P(X0 + 0.04, 2.0, Z), P(X1 - 0.04, 1.0, Z)
    gm = rect_m(a_[0], a_[1], b_[0], b_[1])
    x, y = grid()
    inner = lerp(full((255, 230, 245)), full((210, 200, 255)), smooth(a_[1], b_[1], y))
    img = lerp(img, inner * 0.85, gm)
    # plush pile
    rr = rng0(plush_seed)
    sc_ = cam.sc(Z + 0.4)
    pc = [(255, 170, 200), (255, 230, 120), (160, 220, 255), (190, 160, 255), (255, 255, 255), (255, 140, 120), (150, 230, 170)]
    lay = Layer()
    for k in range(int(28 * w)):
        px_ = rr.uniform(a_[0] + 8, b_[0] - 8)
        py_ = b_[1] - rr.uniform(0, 0.38) * sc_ - 4
        pr = rr.uniform(0.06, 0.1) * sc_
        cc = pc[rr.integers(0, len(pc))]
        lay.circle(px_, py_ + pr * 0.1, pr, tuple(int(v * 0.8) for v in cc))
        lay.circle(px_ - pr * 0.08, py_, pr * 0.9, cc)
        for ex in (-0.6, 0.6):
            lay.circle(px_ + ex * pr, py_ - pr * 0.8, pr * 0.35, cc)
        lay.circle(px_ - pr * 0.3, py_ - pr * 0.1, pr * 0.09, (40, 30, 40))
        lay.circle(px_ + pr * 0.3, py_ - pr * 0.1, pr * 0.09, (40, 30, 40))
    cx = a_[0] + (b_[0] - a_[0]) * rr.uniform(0.3, 0.7)
    cy = a_[1] + (b_[1] - a_[1]) * rr.uniform(0.25, 0.45)
    cc = (200, 200, 210)
    lay.line([(cx, a_[1]), (cx, cy)], 2, cc)
    lay.rect((cx - 0.04 * sc_, cy - 0.03 * sc_, cx + 0.04 * sc_, cy + 0.02 * sc_), cc)
    for sgn in (-1, 0, 1):
        lay.line([(cx, cy + 0.01 * sc_), (cx + sgn * 0.07 * sc_, cy + 0.08 * sc_), (cx + sgn * 0.04 * sc_, cy + 0.14 * sc_)], 0.015 * sc_, cc)
    img = lay.comp(img, gm)
    # glass reflection streaks
    img = screen(img, (255, 255, 255), gm * np.clip(1 - np.abs((x - a_[0]) - (y - a_[1]) * 0.5 - (b_[0] - a_[0]) * 0.25) / 12, 0, 1) * 0.35)
    # frame around glass
    fr = Mask()
    for (p0, p1) in ((P(X0, 2.0, Z), P(X0, 1.0, Z)), (P(X1, 2.0, Z), P(X1, 1.0, Z))):
        fr.line([p0, p1], 0.05 * cam.sc(Z))
    img = over(img, tuple(int(v * 0.8) for v in col), fr.get())
    # top marquee (lit)
    img, tm = box3(img, cam, X0, X1, 2.0, 2.35, Z, Z + D, col)
    ma, mb = P(X0 + 0.03, 2.32, Z), P(X1 - 0.03, 2.03, Z)
    txt = ['抓娃娃', '娃娃机', '幸运', '爱心', '萌宠'][rr.integers(0, 5)]
    sg = sign_img(txt, int(mb[0] - ma[0]), int(mb[1] - ma[1]), (255, 250, 255), tuple(int(v * 0.8) for v in col), fill=0.62, stroke=1, rr=6)
    img, sm = paste_at(img, sg, ma[0], ma[1])
    lay = np.zeros((H, W, 3), np.float32)
    lay, _ = paste_at(lay, sg, ma[0], ma[1])
    E = E + lay * sm[..., None] * 0.6
    # glass emissive
    E = E + inner * gm[..., None] * 0.18
    # neon edge strip on cabinet
    ea, eb = P(X0, 0.95, Z), P(X1, 0.95, Z)
    nm = Mask().line([ea, eb], 0.025 * cam.sc(Z)).get()
    img = lerp(img, full(col) * 1.3, nm)
    E = E + C(col) * nm[..., None] * 1.2
    # control panel + coin slot
    pa, pb = P(X0 + 0.08, 0.92, Z - 0.12), P(X1 - 0.08, 0.8, Z - 0.12)
    img = over(img, (40, 40, 50), rect_m(pa[0], pa[1], pb[0], pb[1]))
    jx, jy = P(X - 0.15, 0.95, Z - 0.08)
    img = over(img, (30, 30, 30), Mask().line([(jx, jy), (jx, jy - 0.1 * cam.sc(Z))], 4).get())
    img = over(img, (230, 40, 40), Mask().circle(jx, jy - 0.1 * cam.sc(Z), 0.035 * cam.sc(Z)).get())
    bx_, by_ = P(X + 0.15, 0.93, Z - 0.08)
    img = over(img, (255, 220, 60), Mask().circle(bx_, by_, 0.04 * cam.sc(Z)).get())
    E = E + C((255, 220, 60)) * Mask().circle(bx_, by_, 0.04 * cam.sc(Z)).get()[..., None] * 0.6
    # prize door hole
    da, db = P(X0 + 0.1, 0.6, Z), P(X0 + 0.35, 0.35, Z)
    img = over(img, (20, 15, 25), rect_m(da[0], da[1], db[0], db[1]))
    return img, E


def arcade_night():
    x, y = grid()
    cam = Cam(F=900, VX=960, VY=470, EYE=1.55)
    P = cam.P
    E = np.zeros((H, W, 3), np.float32)
    r = rng0(401)
    ZB, XW, CEIL = 16.0, 4.2, 4.0
    # back wall: dark with neon sign
    img = full((22, 16, 36))
    # ceiling
    cq = [P(-XW, CEIL, 1.0), P(XW, CEIL, 1.0), P(XW, CEIL, ZB), P(-XW, CEIL, ZB)]
    img, cm = quad(img, cq, (16, 12, 26))
    # ceiling light strips (pink / blue)
    for k, lx in enumerate((-2.0, 0.0, 2.0)):
        a_, b_ = P(lx, CEIL, 1.5), P(lx, CEIL, ZB)
        lm = Mask().tapered([a_, b_], 14, 3).get()
        lc = (255, 80, 190) if k != 1 else (80, 200, 255)
        img = lerp(img, full(lc), lm)
        E += C(lc) * lm[..., None] * 1.0
    # side walls
    for sd in (-1, 1):
        wq = [P(sd * XW, CEIL, 1.0), P(sd * XW, CEIL, ZB), P(sd * XW, 0, ZB), P(sd * XW, 0, 1.0)]
        img, _ = quad(img, wq, (35, 24, 55))
    bq = [P(-XW, CEIL, ZB), P(XW, CEIL, ZB), P(XW, 0, ZB), P(-XW, 0, ZB)]
    img, _ = quad(img, bq, (30, 20, 50))
    # neon sign on back wall
    sgw, sgh = int(4.0 * cam.sc(ZB)), int(0.8 * cam.sc(ZB))
    ns = text_rgba('24H 娃娃机', int(sgh * 0.7), (255, 120, 220), stroke=2, stroke_col=(255, 200, 245))
    sx0, sy0 = P(-0.4, 3.55, ZB)
    img, sm = paste_at(img, ns, sx0 - ns.width / 2, sy0)
    lay = np.zeros((H, W, 3), np.float32)
    lay, _ = paste_at(lay, ns, sx0 - ns.width / 2, sy0)
    E += lay * sm[..., None] * 1.3
    # heart neon
    hm = Mask()
    hx, hy, hr = sx0 + ns.width / 2 + 40, sy0 + ns.height / 2, 22
    pts = []
    for t in np.linspace(0, 2 * math.pi, 80):
        pts.append((hx + 16 * math.sin(t) ** 3 / 17 * hr, hy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17 * hr))
    hm.line(pts, 4)
    hmm = hm.get()
    img = lerp(img, full((120, 220, 255)), hmm)
    E += C((80, 200, 255)) * hmm[..., None] * 1.4
    # glossy floor (dark tiles) with reflections later
    zz = np.where(y > cam.VY + 0.5, cam.EYE * cam.F / np.maximum(y - cam.VY, 1e-3), 1e9)
    Xw = (x - cam.VX) * zz / cam.F
    fl = (y >= P(0, 0, ZB)[1]) * (np.abs(Xw) <= XW)
    ti = (np.floor(Xw / 0.6) + np.floor(zz / 0.6)) % 2
    floor = lerp(full((28, 22, 38)), full((40, 32, 52)), ti)
    jt = ((np.abs(Xw / 0.6 - np.round(Xw / 0.6)) < 0.02 * (zz / 3 + 0.3)) | (np.abs(zz / 0.6 - np.round(zz / 0.6)) < 0.02 * (zz / 3 + 0.3))).astype(np.float32)
    floor = lerp(floor, floor * 0.6, jt * 0.6 * smooth(12, 4, zz))
    floor = lerp(floor, full((34, 27, 45)), smooth(6, 12, zz))
    fl = fl.astype(np.float32)
    img = lerp(img, floor, fl)
    # rows of claw machines along both walls, far to near
    cols = [(255, 90, 170), (80, 190, 255), (255, 200, 60), (170, 110, 255), (255, 130, 110), (90, 230, 190)]
    machines = []
    for sd in (-1, 1):
        for k, z in enumerate(np.arange(2.4, ZB - 0.8, 1.0)):
            machines.append((z, sd * (XW - 0.55), cols[(k * 2 + (sd > 0)) % len(cols)], k * 10 + (sd > 0)))
    # centre island row (back)
    for k, xm in enumerate((-0.9, 0.0, 0.9)):
        machines.append((11.5, xm, cols[(k + 3) % len(cols)], 200 + k))
    machines.sort(key=lambda m: -m[0])
    # machines on the side walls face the aisle: draw them as boxes seen from the side with the glass on the aisle face
    for z, xm, col, seed in machines:
        if abs(xm) < 2:
            img, E = claw_machine(img, E, cam, xm, z, col, r, plush_seed=seed, glass_w=0.85)
        else:
            img, E = side_claw(img, E, cam, xm, z, col, seed)
    # floor reflections of everything (glossy)
    src = img * 0.5 + E * 1.0
    fy = P(0, 0, ZB)[1]
    yb = np.full(W, fy, np.float32)
    # per column base line: side machines sit at |X| = XW - 0.95 (aisle face)
    xa = np.abs(x[0] - cam.VX)
    zcol = (XW - 0.95) * cam.F / np.maximum(xa, 1)
    yb = np.where(zcol < ZB, cam.VY + cam.EYE * cam.F / np.maximum(zcol, 0.5), fy)
    ys = 2 * yb[None, :] - y
    refl = np.stack([ndimage.map_coordinates(src[..., c], [np.clip(ys, 0, H - 1), x], order=1, mode='nearest') for c in range(3)], -1)
    refl = np.stack([ndimage.gaussian_filter(refl[..., c], (3, 1.5)) for c in range(3)], -1)
    refl *= np.exp(-np.maximum(y - yb[None, :], 0) / 350)[..., None]
    below = (y > yb[None, :] + 1).astype(np.float32) * fl
    img = img + refl * below[..., None] * 0.55
    # a lone plush dropped on the floor + coin
    px_, py_ = P(0.4, 0.12, 3.2)
    pr = 0.12 * cam.sc(3.2)
    img = over(img, (255, 170, 200), Mask().circle(px_, py_, pr).get())
    for ex in (-0.6, 0.6):
        img = over(img, (255, 170, 200), Mask().circle(px_ + ex * pr, py_ - pr * 0.8, pr * 0.35).get())
    img = over(img, (40, 30, 40), Mask().circle(px_ - pr * 0.3, py_ - pr * 0.1, pr * 0.08).get() + Mask().circle(px_ + pr * 0.3, py_ - pr * 0.1, pr * 0.08).get())
    img *= (1 - 0.4 * radial(px_, py_ + pr, pr * 1.3, power=1, sy=0.25))[..., None]
    g = blur(E, 4) * 0.55 + blur(E, 16) * 0.55 + blur(E, 50) * 0.35
    img = 1 - (1 - img) * (1 - np.clip(E * 0.4, 0, 1))
    img = 1 - (1 - img) * (1 - np.clip(g, 0, 1))
    # haze glow pink/blue
    img = screen(img, (255, 80, 180), radial(300, 400, 900, power=2) * 0.12)
    img = screen(img, (60, 160, 255), radial(1650, 400, 900, power=2) * 0.12)
    img = bloom(img, 0.7, 20, 0.5)
    return img


def side_claw(img, E, cam, xm, z, col, seed):
    """Claw machine against a side wall, glass facing the aisle (seen at an angle)."""
    P = cam.P
    sd = 1 if xm > 0 else -1
    D = 0.8
    Xf = xm - sd * D / 2   # aisle face
    Xb = xm + sd * D / 2
    Z0, Z1 = z, z + 0.9
    c = C(col)
    x, y = grid()
    # base (aisle face)
    img, _ = quad(img, [P(Xf, 0.95, Z0), P(Xf, 0.95, Z1), P(Xf, 0, Z1), P(Xf, 0, Z0)], c * 0.7)
    # front edge face (towards camera, Z0)
    img, _ = quad(img, [P(Xf, 2.35, Z0), P(Xb, 2.35, Z0), P(Xb, 0, Z0), P(Xf, 0, Z0)], c * 0.55)
    # glass on aisle face
    gq = [P(Xf, 2.0, Z0 + 0.05), P(Xf, 2.0, Z1 - 0.05), P(Xf, 1.0, Z1 - 0.05), P(Xf, 1.0, Z0 + 0.05)]
    gm = Mask().poly(gq).get()
    inner = lerp(full((230, 170, 220)), full((120, 100, 190)), smooth(gq[0][1], gq[3][1], y))
    img = lerp(img, inner * 0.8, gm)
    # light at top of the glass case
    img = screen(img, (255, 240, 255), gm * smooth(gq[0][1] + 40, gq[0][1], y) * 0.5)
    # plush pile (projected), back to front
    rr = rng0(seed)
    pc = [(255, 170, 200), (255, 230, 120), (160, 220, 255), (190, 160, 255), (255, 255, 255), (255, 140, 120), (150, 230, 170)]
    pl = []
    for k in range(34):
        pl.append((rr.uniform(0.08, 0.62), rr.uniform(1.0, 1.0 + 0.4 * rr.random() ** 1.5), rr.uniform(Z0 + 0.1, Z1 - 0.1)))
    pl.sort(key=lambda t: -t[0])
    lay = Layer()
    for dx, py, pz in pl:
        cx, cy = P(Xf + sd * dx, py + 0.08, pz)
        pr = rr.uniform(0.08, 0.12) * cam.sc(pz)
        cc = pc[rr.integers(0, len(pc))]
        lay.ellipse((cx - pr * 0.8, cy - pr * 0.9, cx + pr * 0.8, cy + pr), tuple(int(v * 0.75) for v in cc))
        lay.ellipse((cx - pr * 0.72, cy - pr * 0.95, cx + pr * 0.6, cy + pr * 0.7), cc)
        for ex in (-0.5, 0.45):
            lay.circle(cx + ex * pr, cy - pr * 0.85, pr * 0.3, cc)
        lay.circle(cx - pr * 0.25, cy - pr * 0.2, pr * 0.08, (40, 30, 45))
        lay.circle(cx + pr * 0.2, cy - pr * 0.2, pr * 0.08, (40, 30, 45))
    cz = rr.uniform(Z0 + 0.3, Z1 - 0.3)
    top_ = P(Xf + sd * 0.35, 2.0, cz)
    bot_ = P(Xf + sd * 0.35, rr.uniform(1.55, 1.8), cz)
    s_ = cam.sc(cz)
    cc = (215, 215, 225)
    lay.line([top_, bot_], max(1, 0.01 * s_), cc)
    lay.rect((bot_[0] - 0.04 * s_, bot_[1] - 0.03 * s_, bot_[0] + 0.04 * s_, bot_[1] + 0.02 * s_), cc)
    for sg_ in (-1, 0, 1):
        lay.line([(bot_[0], bot_[1]), (bot_[0] + sg_ * 0.07 * s_, bot_[1] + 0.08 * s_), (bot_[0] + sg_ * 0.04 * s_, bot_[1] + 0.14 * s_)], 0.015 * s_, cc)
    img = lay.comp(img, gm)
    img = screen(img, (255, 255, 255), gm * np.clip(1 - np.abs(np.sin(x * 0.012 + y * 0.004)) * 6, 0, 1) * 0.18)
    E = E + inner * gm[..., None] * 0.12
    # marquee on aisle face
    mq = [P(Xf, 2.35, Z0), P(Xf, 2.35, Z1), P(Xf, 2.0, Z1), P(Xf, 2.0, Z0)]
    img, mm = quad(img, mq, c * 1.1)
    E = E + c * mm[..., None] * 0.35
    txt = ['抓娃娃', '娃娃机', '幸运星', '爱心机', '萌宠乐园', '一抓即中'][(seed // 10 * 7 + seed) % 6]
    sgi = sign_img(txt, 360, 120, (255, 245, 255), tuple(int(v * 0.55) for v in col), fill=0.6, stroke=3, rr=14)
    if sd < 0:
        tq_ = [P(Xf, 2.31, Z0 + 0.06), P(Xf, 2.31, Z1 - 0.06), P(Xf, 2.04, Z1 - 0.06), P(Xf, 2.04, Z0 + 0.06)]
    else:
        tq_ = [P(Xf, 2.31, Z1 - 0.06), P(Xf, 2.31, Z0 + 0.06), P(Xf, 2.04, Z0 + 0.06), P(Xf, 2.04, Z1 - 0.06)]
    before = img
    img = paste_quad(img, sgi, tq_)
    E = E + np.abs(img - before) * 0.4
    # neon edge lines
    for Yl in (2.0, 0.95):
        lm = Mask().line([P(Xf, Yl, Z0), P(Xf, Yl, Z1)], max(1.5, 0.02 * cam.sc(Z0))).get()
        img = lerp(img, full((255, 255, 255)) * 0.5 + c * 0.7, lm)
        E = E + c * lm[..., None] * 1.0
    # vertical post
    pm = Mask().line([P(Xf, 2.35, Z0), P(Xf, 0, Z0)], max(1.5, 0.04 * cam.sc(Z0))).get()
    img = lerp(img, full((0, 0, 0)) + c * 0.9, pm)
    return img, E


# ------------------------------------------------------------------ convenience store
def convenience_store_night():
    x, y = grid()
    cam = Cam(F=640, VX=1000, VY=520, EYE=1.6)
    P = cam.P
    E = np.zeros((H, W, 3), np.float32)
    r = rng0(501)
    ZB, XL, XR, CEIL = 10.0, -3.6, 4.6, 3.0
    img = full((214, 218, 222))
    # ceiling with light panels
    img, _ = quad(img, [P(XL, CEIL, 0.8), P(XR, CEIL, 0.8), P(XR, CEIL, ZB), P(XL, CEIL, ZB)], (200, 204, 210))
    for lz in (2.0, 4.0, 6.0, 8.0):
        for lx in (-1.5, 1.8):
            q = [P(lx - 0.6, CEIL, lz), P(lx + 0.6, CEIL, lz), P(lx + 0.6, CEIL, lz + 0.3), P(lx - 0.6, CEIL, lz + 0.3)]
            img, m = quad(img, q, (255, 255, 252))
            E += C((255, 255, 245)) * m[..., None] * 0.6
    # back wall
    img, _ = quad(img, [P(XL, CEIL, ZB), P(XR, CEIL, ZB), P(XR, 0, ZB), P(XL, 0, ZB)], (212, 214, 210))
    # back wall: beer / drink fridges + staff door + poster
    for i in range(4):
        xa, xb_ = -1.0 + i * 0.95, -1.0 + (i + 1) * 0.95 - 0.06
        a_, b_ = P(xa, 2.15, ZB - 0.05), P(xb_, 0.1, ZB - 0.05)
        dm = rect_m(a_[0], a_[1], b_[0], b_[1])
        img = lerp(img, full((230, 245, 255)), dm)
        E += C((200, 235, 255)) * dm[..., None] * 0.25
        lay = Layer()
        for sh in np.linspace(0.35, 2.0, 6):
            yy = P(0, sh, ZB)[1]
            for k in range(6):
                bx_ = a_[0] + (b_[0] - a_[0]) * (k + 0.5) / 6
                ww = (b_[0] - a_[0]) / 6 * 0.32
                cc = [(40, 120, 60), (200, 160, 40), (220, 40, 40), (60, 110, 200), (240, 240, 240)][(i + k + int(sh * 3)) % 5]
                lay.rect((bx_ - ww, yy - 0.2 * cam.sc(ZB), bx_ + ww, yy), cc)
            lay.line([(a_[0], yy), (b_[0], yy)], 2, (170, 180, 190))
        img = lay.comp(img, dm)
        img = over(img, (70, 75, 80), Mask().rect((a_[0] - 3, a_[1] - 3, b_[0] + 3, b_[1] + 3)).get() - dm * 1.0 if False else (Mask().rect((a_[0] - 3, a_[1] - 3, b_[0] + 3, b_[1] + 3)).get() * (1 - dm)))
    a_, b_ = P(-3.2, 2.1, ZB - 0.02), P(-2.2, 0, ZB - 0.02)
    img = over(img, (150, 155, 160), rect_m(a_[0], a_[1], b_[0], b_[1]))
    dsg = sign_img('员工通道', int(b_[0] - a_[0]), int(0.22 * cam.sc(ZB)), (60, 70, 80), (255, 255, 255), fill=0.6)
    img, _ = paste_at(img, dsg, a_[0], a_[1] + 0.2 * cam.sc(ZB))
    pst = sign_img('第二件半价', int(1.0 * cam.sc(ZB)), int(0.6 * cam.sc(ZB)), (230, 50, 50), (255, 240, 120), fill=0.55, stroke=1, rr=6)
    img, _ = paste_at(img, pst, P(3.0, 0, ZB)[0], P(0, 2.2, ZB)[1])
    # brand stripe along top of walls
    for (a, b) in ((P(XL, 2.75, ZB), P(XR, 2.5, ZB)),):
        img = over(img, (20, 150, 90), rect_m(a[0], a[1], b[0], b[1]))
        img = over(img, (240, 120, 30), rect_m(a[0], b[1], b[0], b[1] + 0.08 * cam.sc(ZB)))
    # left wall: big window to dark street
    img, _ = quad(img, [P(XL, CEIL, 0.8), P(XL, CEIL, ZB), P(XL, 0, ZB), P(XL, 0, 0.8)], (215, 218, 215))
    wq = [P(XL, 2.5, 1.0), P(XL, 2.5, 7.5), P(XL, 0.35, 7.5), P(XL, 0.35, 1.0)]
    wm = Mask().poly(wq).get()
    # street outside: dark, a lamp, a parked scooter, neon bokeh
    outside = vgrad([(0, (10, 12, 24)), (0.6, (18, 20, 36)), (1, (30, 28, 36))], y0=wq[0][1], y1=wq[3][1])
    pts = [(r.uniform(0, 700), r.uniform(150, 650)) for _ in range(40)]
    cols = [NEON[r.integers(0, len(NEON))] if r.random() < 0.5 else (255, 200, 130) for _ in pts]
    outside = bokeh(outside, pts, cols, [r.uniform(6, 22) for _ in pts], 0.6, 0.35)
    img = lerp(img, outside, wm)
    # reflection of interior in glass (faint)
    img = screen(img, (200, 220, 230), wm * smooth(wq[3][1], wq[0][1], y) * 0.12)
    # window mullions + 24h decal
    for z in (1.0, 3.2, 5.4, 7.5):
        img = over(img, (180, 185, 190), Mask().line([P(XL, 2.5, z), P(XL, 0.35, z)], max(2, 0.06 * cam.sc(z))).get())
    dec = sign_img('24小时营业', 360, 90, None, (240, 120, 30), fill=0.7, stroke=2)
    img = paste_quad(img, dec, [P(XL, 2.3, 2.0), P(XL, 2.3, 4.6), P(XL, 1.9, 4.6), P(XL, 1.9, 2.0)], 0.9)
    # floor
    zz = np.where(y > cam.VY + 0.5, cam.EYE * cam.F / np.maximum(y - cam.VY, 1e-3), 1e9)
    Xw = (x - cam.VX) * zz / cam.F + cam.CX
    fl = ((y >= P(0, 0, ZB)[1]) & (Xw > XL) & (Xw < XR)).astype(np.float32)
    ti = (np.floor(Xw / 0.5) + np.floor(zz / 0.5)) % 2
    floor = lerp(full((228, 228, 224)), full((210, 212, 210)), ti * 0.4)
    jt = ((np.abs(Xw / 0.5 - np.round(Xw / 0.5)) < 0.015 * (zz / 3 + 0.3)) | (np.abs(zz / 0.5 - np.round(zz / 0.5)) < 0.015 * (zz / 3 + 0.3))).astype(np.float32)
    floor = lerp(floor, floor * 0.85, jt * smooth(9, 3, zz))
    img = lerp(img, floor, fl)
    # ---- right wall: glowing drink fridges
    fz0, fz1 = 1.6, 9.6
    n_f = 6
    for i in range(n_f):
        za = fz0 + (fz1 - fz0) * i / n_f
        zb = fz0 + (fz1 - fz0) * (i + 1) / n_f
        Xf = XR - 0.05
        door = [P(Xf, 2.2, za + 0.04), P(Xf, 2.2, zb - 0.04), P(Xf, 0.15, zb - 0.04), P(Xf, 0.15, za + 0.04)]
        dm = Mask().poly(door).get()
        inside = full((200, 228, 242))
        img = lerp(img, inside, dm)
        E += C((200, 235, 255)) * dm[..., None] * 0.25
        # shelves of drinks
        lay = Layer()
        for sh in np.linspace(0.3, 2.0, 6):
            for k in range(7):
                bz = za + 0.08 + (zb - za - 0.16) * k / 6
                bx_, by_ = P(Xf - 0.03, sh, bz)
                hh = 0.24 * cam.sc(bz)
                ww = 0.13 * cam.sc(bz) * 0.6
                cc = [(220, 40, 40), (40, 120, 220), (250, 200, 40), (60, 180, 90), (240, 240, 240), (250, 120, 40), (150, 60, 160)][(i * 7 + k + int(sh * 3)) % 7]
                lay.rect((bx_ - ww / 2, by_ - hh, bx_ + ww / 2, by_), cc)
                lay.rect((bx_ - ww / 2, by_ - hh * 0.6, bx_ + ww / 2, by_ - hh * 0.4), (255, 255, 255), 0.7)
            a_, b_ = P(Xf, sh, za), P(Xf, sh, zb)
            lay.line([a_, b_], max(1.5, 0.02 * cam.sc(za)), (170, 180, 190))
        img = lay.comp(img, dm)
        # door frame + handle
        fr = Mask()
        fr.line([door[0], door[3]], max(2, 0.05 * cam.sc(za)))
        fr.line([door[0], door[1]], max(2, 0.05 * cam.sc(za)))
        img = over(img, (60, 64, 70), fr.get())
        ha, hb = P(Xf - 0.02, 1.4, za + 0.12), P(Xf - 0.02, 0.9, za + 0.12)
        img = over(img, (190, 195, 200), Mask().line([ha, hb], max(2, 0.03 * cam.sc(za))).get())
    # fridge header
    img, _ = quad(img, [P(XR, 2.6, fz0), P(XR, 2.6, fz1), P(XR, 2.2, fz1), P(XR, 2.2, fz0)], (30, 40, 55))
    # ---- shelves (gondolas) in the middle, running along Z
    goods = [(230, 60, 50), (250, 190, 40), (60, 140, 220), (240, 240, 230), (90, 180, 90), (240, 130, 50), (200, 80, 150)]
    for (gx0, gx1) in ((-0.6, 0.2), (1.8, 2.6)):
        Za, Zb = 3.2, 8.8
        hgt = 1.55
        img, _ = box3(img, cam, gx0, gx1, 0, hgt, Za, Zb, (200, 205, 210))
        # side face visible (the one facing camera axis)
        faceX = gx1 if gx1 < cam.CX + 0.0 else gx0
        lay = Layer()
        for sh in np.linspace(0.15, 1.35, 5):
            for zz_ in np.arange(Za + 0.05, Zb - 0.05, 0.12):
                bx_, by_ = P(faceX, sh, zz_)
                hh = r.uniform(0.15, 0.25) * cam.sc(zz_)
                ww = 0.1 * cam.sc(zz_) * 0.35
                cc = goods[r.integers(0, len(goods))]
                lay.rect((bx_ - ww, by_ - hh, bx_ + ww, by_), cc)
            lay.line([P(faceX, sh, Za), P(faceX, sh, Zb)], max(1.5, 0.025 * cam.sc(Za)), (160, 165, 170))
        img = lay.comp(img)
        # end cap facing camera with snacks
        a_, b_ = P(gx0, hgt, Za), P(gx1, 0, Za)
        lay = Layer()
        for sh in np.linspace(0.15, 1.35, 5):
            for k in range(6):
                bx_ = a_[0] + (b_[0] - a_[0]) * (k + 0.5) / 6
                by_ = P(0, sh, Za)[1]
                hh = 0.22 * cam.sc(Za)
                ww = (b_[0] - a_[0]) / 6 * 0.42
                cc = goods[(k * 3 + int(sh * 7)) % len(goods)]
                lay.rect((bx_ - ww, by_ - hh, bx_ + ww, by_), cc)
                lay.rect((bx_ - ww * 0.7, by_ - hh * 0.7, bx_ + ww * 0.7, by_ - hh * 0.5), (255, 255, 255), 0.6)
        img = lay.comp(img)
        # price tag strip / top sign
        tg = sign_img(['零食', '泡面'][int(gx0 > 0)], int((b_[0] - a_[0]) * 0.9), int(0.25 * cam.sc(Za)), (240, 120, 30), (255, 255, 255), fill=0.7)
        img, _ = paste_at(img, tg, a_[0] + (b_[0] - a_[0]) * 0.05, P(0, hgt + 0.35, Za)[1])
    # ---- cashier counter + oden pot (left foreground)
    cx0, cx1, cz0, cz1 = -3.4, -1.0, 2.0, 2.7
    img, _ = box3(img, cam, cx0, cx1, 0, 1.0, cz0, cz1, (240, 240, 238), top_col=C((200, 205, 210)))
    # brand stripe on counter front
    a_, b_ = P(cx0, 0.75, cz0), P(cx1, 0.62, cz0)
    img = over(img, (20, 150, 90), rect_m(a_[0], a_[1], b_[0], b_[1]))
    img = over(img, (240, 120, 30), rect_m(a_[0], b_[1], b_[0], b_[1] + 0.05 * cam.sc(cz0)))
    # oden pot: stainless tray with compartments + steam
    ox0, ox1, oz0, oz1 = -2.3, -1.2, 2.1, 2.55
    img, _ = box3(img, cam, ox0, ox1, 1.0, 1.08, oz0, oz1, (190, 195, 200))
    broth = [P(ox0 + 0.04, 1.08, oz0 + 0.04), P(ox1 - 0.04, 1.08, oz0 + 0.04), P(ox1 - 0.04, 1.08, oz1 - 0.04), P(ox0 + 0.04, 1.08, oz1 - 0.04)]
    bm = Mask().poly(broth).get()
    img = lerp(img, full((200, 150, 80)), bm)
    od = Mask()
    odc = Mask()
    for k in range(9):
        ex = ox0 + 0.1 + (k % 3) * 0.35 + r.uniform(-0.05, 0.05)
        ez = oz0 + 0.1 + (k // 3) * 0.12
        px_, py_ = P(ex, 1.1, ez)
        rr = 0.05 * cam.sc(ez)
        (od if k % 2 else odc).ellipse((px_ - rr, py_ - rr * 0.6, px_ + rr, py_ + rr * 0.4))
    img = lerp(img, full((240, 230, 200)), od.get())
    img = lerp(img, full((170, 110, 60)), odc.get())
    # skewer sticks out of oden
    sk = Mask()
    for k in range(6):
        px_, py_ = P(ox0 + 0.15 + k * 0.15, 1.1, oz0 + 0.2)
        sk.line([(px_, py_), (px_ + 4, py_ - 0.25 * cam.sc(oz0))], 2)
    img = over(img, (210, 180, 130), sk.get())
    sg = sign_img('关东煮', int(0.7 * cam.sc(oz0)), int(0.2 * cam.sc(oz0)), (200, 40, 40), (255, 255, 255), fill=0.7, rr=4)
    img, _ = paste_at(img, sg, P(ox0, 0, oz0)[0], P(0, 1.38, oz0)[1])
    # register + small hot showcase
    img, _ = box3(img, cam, -3.2, -2.85, 1.0, 1.22, 2.3, 2.55, (110, 115, 122))
    img, _ = box3(img, cam, -3.15, -2.9, 1.22, 1.42, 2.45, 2.5, (40, 44, 50))
    # steam over oden
    smk = np.zeros((H, W), np.float32)
    px_, py_ = P((ox0 + ox1) / 2, 1.1, (oz0 + oz1) / 2)
    n_ = fbm(H, W, 30, 3, seed=502)
    for i in range(16):
        t = i / 16
        smk += radial(px_ + math.sin(t * 6) * 30 + t * 40, py_ - t * 300, 30 + t * 110, power=1.3) * (1 - t) * 0.5
    smk = np.clip(smk * (0.4 + 0.8 * n_), 0, 1)
    img = lerp(img, img * 0.6 + 0.45, smk * 0.45)
    # floor reflection of fridges
    fz = np.abs(x[0] - cam.VX)
    img = screen(img, (210, 235, 255), fl * smooth(cam.VX + 100, W, x) * smooth(cam.VY + 50, H, y) * 0.12)
    # general cool fluorescent tint, slight bloom
    img = img * np.array([0.97, 1.0, 1.02], np.float32)
    g = blur(E, 6) * 0.3 + blur(E, 30) * 0.2
    img = 1 - (1 - img) * (1 - np.clip(g, 0, 1))
    img = bloom(img, 0.92, 25, 0.2)
    return img


# ------------------------------------------------------------------ CG: rider in the rain
def zoom_blur(img, cx, cy, amount=0.05, n=8):
    acc = np.zeros_like(img)
    for i in range(n):
        k = 1 + amount * i / (n - 1)
        # sample img at (c + (p - c) / k)
        x, y = grid()
        xs = cx + (x - cx) / k
        ys = cy + (y - cy) / k
        acc += np.stack([ndimage.map_coordinates(img[..., c], [ys, xs], order=1, mode='nearest') for c in range(3)], -1)
    return acc / n


def rider_rain():
    x, y = grid()
    bg = city_street('rain', add_rain=False) * np.array([0.88, 0.96, 1.1], np.float32)
    VX, VY = 960, 600
    bg = zoom_blur(bg, VX, VY - 60, 0.06, 9)
    bg = bg * 0.82
    img = bg
    # rider sprite
    im = load('props/ebike.png', 'RGBA')
    s = 0.6
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x0, y0 = 740, 1052 - 1526 * s
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(im, (int(x0), int(y0)), im)
    arr = np.asarray(canvas, np.float32) / 255.0
    rgb, a = arr[..., :3].copy(), arr[..., 3]
    # wet night grading of the figure: darker, cooler, high contrast
    rgb = rgb * np.array([0.72, 0.78, 0.92], np.float32)
    rgb = rgb + 0.06 * (rgb - lum(rgb)[..., None])
    # rim lights: pink from the left/back, cyan from the right
    af = ndimage.binary_fill_holes(ndimage.binary_closing(a > 0.5, iterations=12)).astype(np.float32)
    af = blur(af, 1.0)
    edgeL = np.clip(af - np.roll(af, 8, axis=1), 0, 1)
    edgeR = np.clip(af - np.roll(af, -8, axis=1), 0, 1)
    edgeT = np.clip(af - np.roll(af, 7, axis=0), 0, 1)
    rgb = screen(rgb, (255, 90, 190), blur(edgeL, 3) * a * 0.7)
    rgb = screen(rgb, (90, 220, 255), blur(edgeR, 3) * a * 0.65)
    rgb = screen(rgb, (200, 220, 255), blur(edgeT, 2.5) * a * 0.45)
    # wet sheen streaks on him
    sheen = smooth(0.7, 0.9, fbm(H, W, 6, 3, seed=601, sx=0.2, sy=3))
    rgb = screen(rgb, (210, 225, 255), sheen * a * 0.15)
    # contact shadow + reflection on the wet road
    fx_, fy_ = x0 + 1300 * s, y0 + 1526 * s
    rx_, ry_ = x0 + 385 * s, y0 + 1375 * s
    img *= (1 - 0.55 * radial((fx_ + rx_) / 2, (fy_ + ry_) / 2 + 10, 420, power=1.2, sy=0.12))[..., None]
    # reflection: flip about the line between the two contact points
    slope = (fy_ - ry_) / (fx_ - rx_)
    base = ry_ + (x[0] - rx_) * slope
    ys = 2 * base[None, :] - y
    rr_ = np.stack([ndimage.map_coordinates(rgb[..., c], [np.clip(ys, 0, H - 1), x], order=1) for c in range(3)], -1)
    ra = ndimage.map_coordinates(a, [np.clip(ys, 0, H - 1), x], order=1) * (y > base[None, :])
    rr_ = blur(rr_, 2.5)
    ra = blur(ra, 3) * np.exp(-np.maximum(y - base[None, :], 0) / 160) * 0.45
    img = lerp(img, rr_ * 0.8, ra)
    img = lerp(img, rgb, a)
    # headlight + beam forward (to the lower right)
    hx, hy = x0 + 1245 * s, y0 + 970 * s
    beam = Mask().poly([(hx, hy - 10), (W + 200, hy - 260), (W + 200, H + 300), (hx, hy + 14)]).get(30)
    beam *= np.clip(1 - np.hypot(x - hx, y - hy) / 1300, 0, 1) ** 1.2
    img = screen(img, (255, 248, 225), beam * 0.35)
    img = screen(img, (255, 250, 230), radial(hx, hy, 34, power=0.6))
    img = screen(img, (255, 240, 200), radial(hx, hy, 220, power=2.0) * 0.5)
    # rain lit inside the beam
    lay = Layer()
    r = rng0(602)
    for _ in range(900):
        px, py = r.uniform(hx, W), r.uniform(hy - 300, H)
        L = r.uniform(20, 55)
        lay.line([(px, py), (px - L * 0.35, py + L)], 1.6, (255, 250, 230), 0.8)
    st = lay.comp(np.zeros((H, W, 3), np.float32))
    img = 1 - (1 - img) * (1 - st * beam[..., None] * 1.6)
    # tail light glow
    tx, ty = x0 + 268 * s, y0 + 998 * s
    img = screen(img, (255, 40, 40), radial(tx, ty, 18, power=0.6))
    img = screen(img, (255, 40, 40), radial(tx, ty, 160, power=2.0) * 0.5)
    # water spray from the wheels: rooster tail behind the rear wheel, side spray at the front
    lay = Layer()
    for (cx, cy, n, sx, sy, dirx) in ((rx_ + 20, ry_, 700, 160, 230, -1.3), (fx_ - 30, fy_, 450, 130, 120, -0.6),
                                      (fx_ + 40, fy_, 220, 90, 70, 0.9)):
        for _ in range(n):
            t = r.random()
            dy = -abs(r.normal(0, sy)) * t
            dx = dirx * abs(dy) * r.uniform(0.6, 1.4) + r.normal(0, sx * 0.35)
            rad = r.uniform(0.8, 3.0) * (1 - t * 0.5)
            lay.circle(cx + dx, cy + dy, rad, (215, 230, 255), r.uniform(0.2, 0.6))
        # sheet of water
        for k in range(6):
            pts = bezier((cx, cy), (cx + dirx * sx * 0.6, cy - sy * 0.5 - k * 10), (cx + dirx * sx * 1.4 - k * 15, cy - sy * 0.2 + k * 12), n=20)
            lay.line(pts, 3 - k * 0.3, (200, 220, 250), 0.35)
    spr = lay.comp(np.zeros((H, W, 3), np.float32))
    img = 1 - (1 - img) * (1 - np.clip(spr + blur(spr, 10) * 1.5, 0, 1) * 0.8)
    # puddle ripples around the wheels
    lay = Layer()
    for (cx, cy) in ((rx_, ry_ + 8), (fx_, fy_ + 6)):
        for k in range(3):
            rw = 60 + k * 55
            lay.ellipse((cx - rw, cy - rw * 0.12, cx + rw, cy + rw * 0.12), (210, 225, 255), 0.35 - k * 0.09)
            rw2 = rw - 4
            lay.ellipse((cx - rw2, cy - rw2 * 0.12 + 1, cx + rw2, cy + rw2 * 0.12 - 1), (0, 0, 0), 0.0)
    ring = lay.comp(np.zeros((H, W, 3), np.float32))
    # hollow rings via difference of blurs
    img = screen(img, (1, 1, 1), np.clip((lum(ring) - blur(lum(ring), 3)) * 3, 0, 1) * 0)
    img = screen(img, (210, 225, 255), np.clip(lum(ring) * 0.8, 0, 1) * smooth(0.0, 1.0, 1 - a) * 0.6)
    # speed lines streaking behind him (to the left)
    lay = Layer()
    for _ in range(40):
        py = r.uniform(200, 1000)
        px = r.uniform(0, x0 + 300)
        L = r.uniform(120, 400)
        lay.line([(px, py), (px - L, py + L * 0.08)], r.uniform(1, 3), (220, 230, 255), r.uniform(0.2, 0.5))
    img = lay.comp(img, 1 - a)
    # heavy rain over everything, slanted by the motion
    img = rain_layer(img, seed=603, n=3000, strength=1.1, angle=0.32, splashes=True, ground_y=640)
    # drops bouncing off the helmet
    lay = Layer()
    hcx, hcy = x0 + 730 * s, y0 + 40 * s
    for _ in range(30):
        ang = r.uniform(-math.pi, 0)
        d = r.uniform(10, 70)
        lay.circle(hcx + math.cos(ang) * d * 1.6, hcy + math.sin(ang) * d, r.uniform(0.8, 2), (230, 240, 255), 0.45)
    img = lay.comp(img)
    img = bloom(img, 0.7, 22, 0.45)
    # cinematic letterbox-free vignette, cool
    xx = np.sqrt(((x - 960) / 960) ** 2 + ((y - 540) / 540) ** 2)
    img *= (1 - 0.35 * smooth(0.6, 1.4, xx))[..., None]
    return img


SCENES = {'street_food_night': street_food_night, 'arcade_night': arcade_night, 'convenience_store_night': convenience_store_night, 'city_street_day': city_street_day, 'city_street_night': city_street_night, 'city_rain_night': city_rain_night}
CGS = {'rider_rain': rider_rain}
GRADE = {'city_rain_night': dict(warm=0.25), 'rider_rain': dict(warm=0.2)}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES) + list(CGS)
    for n in names:
        if n in SCENES:
            save_rgb(SCENES[n](), os.path.join(BG, n + '.png'), **GRADE.get(n, {}))
        else:
            save_rgb(CGS[n](), os.path.join(CG, n + '.png'), **GRADE.get(n, {}))
