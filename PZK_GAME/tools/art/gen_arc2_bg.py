"""Arc 2 interiors / city-high-rise backgrounds:
hotel_suite_night, rental_room(+_night), office_lobby, ib_office_night, ib_trading_floor,
meeting_room, elevator, rooftop_night.

Uses the one-point-perspective Cam / quad / box3 helpers from gen_arc2_city and the shared artlib grade.
Run: python3 gen_arc2_bg.py [names...]
"""
import sys
from artlib import *
from gen_arc2_city import (Cam, quad, box3, C, full, cfont, sign_img, text_rgba, paste_at, rect_m,
                           plastic_stool, Layer)

rng0 = np.random.default_rng


# ====================================================================== surface coordinates
class Room:
    """Axis-aligned box room seen by a Cam. Gives world coords per pixel on each surface."""

    def __init__(self, cam, XL, XR, CEIL, ZB):
        self.cam, self.XL, self.XR, self.CEIL, self.ZB = cam, XL, XR, CEIL, ZB
        c = cam
        x, y = grid()
        self.x, self.y = x, y
        P = c.P
        zn = 0.05
        self.m_back = Mask().rect((*P(XL, CEIL, ZB), *P(XR, 0, ZB))).get()
        self.m_floor = Mask().poly([P(XL, 0, ZB), P(XR, 0, ZB), P(XR, 0, zn), P(XL, 0, zn)]).get()
        self.m_ceil = Mask().poly([P(XL, CEIL, ZB), P(XR, CEIL, ZB), P(XR, CEIL, zn), P(XL, CEIL, zn)]).get()
        self.m_left = Mask().poly([P(XL, CEIL, ZB), P(XL, 0, ZB), P(XL, 0, zn), P(XL, CEIL, zn)]).get()
        self.m_right = Mask().poly([P(XR, CEIL, ZB), P(XR, 0, ZB), P(XR, 0, zn), P(XR, CEIL, zn)]).get()
        F, VX, VY, E = c.F, c.VX, c.VY, c.EYE
        dy = y - VY
        dx = x - VX
        # floor
        zf = np.where(dy > 0.5, E * F / np.maximum(dy, 0.5), 1e3)
        self.floor = ((dx * zf / F + c.CX), np.zeros_like(x), zf)
        zc = np.where(dy < -0.5, (CEIL - E) * F / np.maximum(-dy, 0.5), 1e3)
        self.ceil = ((dx * zc / F + c.CX), np.full_like(x, CEIL), zc)
        self.back = ((dx * ZB / F + c.CX), E - dy * ZB / F, np.full_like(x, ZB))
        zl = np.where(dx < -0.5, (XL - c.CX) * F / np.minimum(dx, -0.5), 1e3)
        self.left = (np.full_like(x, XL), E - dy * zl / F, zl)
        zr = np.where(dx > 0.5, (XR - c.CX) * F / np.maximum(dx, 0.5), 1e3)
        self.right = (np.full_like(x, XR), E - dy * zr / F, zr)

    def paint(self, img, surf, col):
        m = getattr(self, 'm_' + surf)
        return lerp(img, col, m)


def point_light(coords, L, power=1.0, rad=2.0, normal=None):
    """Soft inverse-square falloff of a point light L=(X,Y,Z) on surface coords."""
    X, Y, Z = coords
    d2 = (X - L[0]) ** 2 + (Y - L[1]) ** 2 + (Z - L[2]) ** 2
    v = power / (1 + d2 / (rad * rad))
    if normal is not None:
        nx, ny, nz = normal
        dot = ((L[0] - X) * nx + (L[1] - Y) * ny + (L[2] - Z) * nz) / np.sqrt(d2 + 1e-6)
        v = v * np.clip(0.35 + 0.65 * dot, 0, 1)
    return v


def tiles(u, v, su, sv, grout=0.02, seed=0):
    """Tile pattern: returns (per-tile random 0..1, grout mask)."""
    iu, iv = np.floor(u / su), np.floor(v / sv)
    rnd = (np.sin(iu * 12.9898 + iv * 78.233 + seed) * 43758.5453) % 1.0
    fu, fv = u / su - iu, v / sv - iv
    g = ((fu < grout / su) | (fu > 1 - grout / su) | (fv < grout / sv) | (fv > 1 - grout / sv)).astype(np.float32)
    return rnd, g


def hash2(a, b, s=0.0):
    return (np.sin(a * 12.9898 + b * 78.233 + s * 37.719) * 43758.5453) % 1.0


# ====================================================================== skyline
def skyline(box, hz, night, seed=0, haze_col=None, dusk=False, low_view=False):
    """Painted city view for windows. box=(x0,y0,x1,y1) region; returns full-frame image."""
    x, y = grid()
    r = rng0(seed)
    x0, y0, x1, y1 = box
    if night:
        sky = vgrad([(0, (6, 10, 28)), (0.7, (24, 30, 70)), (1, (70, 55, 95))], y0=y0, y1=hz)
        img = sky
        img = stars(img, (y < hz - 40).astype(np.float32) * 0.5, n=260, seed=seed + 1)
    else:
        img = vgrad([(0, (95, 160, 225)), (0.75, (175, 210, 240)), (1, (225, 235, 245))], y0=y0, y1=hz)
        img = sky_clouds(img, y0, hz - 20, seed=seed + 2, cover_=0.62, scale=180, amount=0.7)
    below = vgrad([(0, (60, 55, 80) if night else (170, 185, 200)), (1, (25, 22, 40) if night else (120, 135, 150))], y0=hz, y1=max(hz + 1, y1))
    img = lerp(img, below, (y >= hz).astype(np.float32))
    layers = [  # (top spread above hz, width range, darkness/haze, window size)
        (0.10, (40, 110), 0.55, (5, 7)),
        (0.22, (60, 160), 0.35, (8, 11)),
        (0.40, (90, 230), 0.15, (12, 16)),
    ]
    span = (y1 - y0)
    for li, (top, wr, haze, (wx, wy)) in enumerate(layers):
        edges = [x0 - 60]
        while edges[-1] < x1 + 60:
            edges.append(edges[-1] + r.uniform(*wr))
        edges = np.array(edges, np.float32)
        nb = len(edges)
        hts = r.uniform(0.15, 1.0, nb) ** 1.4 * span * top + span * (0.02 + 0.03 * li)
        if low_view:
            hts = hts * 0.9
        bid = np.clip(np.searchsorted(edges, x[0]) - 1, 0, nb - 2)
        topy = (hz - hts[bid])[None, :]
        gap = 3 + li * 2
        left = edges[bid][None, :]
        right = edges[bid + 1][None, :]
        inb = (x >= left + gap * 0.5) & (x < right - gap * 0.5)
        m = ((y >= topy) & inb).astype(np.float32)
        m = blur(m, 0.6)
        u = x - left
        v = y - topy
        win = ((u % wx) < wx * 0.55) & ((v % wy) < wy * 0.5) & (u > wx * 0.6) & (u < right - left - wx * 0.8) & (v > wy)
        lit = hash2(np.floor(u / wx) + bid[None, :] * 31.0, np.floor(v / wy), li + seed) > (0.55 if night else 0.0)
        tone = hash2(bid[None, :] * 1.0, li + 0.5, seed) * np.ones_like(y)
        if night:
            bc = lerp(full((14, 16, 30)), full((30, 32, 52)), tone)
            bc = lerp(bc, full((60, 50, 85)), haze * 0.6)
            wc = lerp(full((255, 210, 140)), full((210, 230, 255)), (hash2(np.floor(u / wx), np.floor(v / wy), 3) > 0.7).astype(np.float32))
            img = lerp(img, bc, m)
            img = lerp(img, wc * (0.55 + 0.45 * (1 - haze)), (win & lit).astype(np.float32) * m * (0.9 - haze * 0.5))
        else:
            bc = gradient([(0, (110, 135, 160)), (0.5, (150, 170, 190)), (1, (195, 200, 205))], tone)
            bc = lerp(bc, full((205, 218, 232)), haze)
            img = lerp(img, bc, m)
            img = lerp(img, bc * 0.82 + C((0, 10, 25)), win.astype(np.float32) * m * 0.6)
            # glass sky reflection on the sunny side
            img = screen(img, (255, 255, 255), m * smooth(left + (right - left) * 0.7, right, x) * 0.15 * (1 - haze))
        # antenna on a few tall towers
        for b in range(nb - 1):
            if hts[b] > span * top * 0.75 and r.random() < 0.4:
                cx = (edges[b] + edges[b + 1]) / 2
                ty = hz - hts[b]
                img = over(img, (20, 20, 30) if night else (90, 100, 110), Mask().rect((cx - 1.5, ty - 30, cx + 1.5, ty)).get())
                if night:
                    img = screen(img, (255, 60, 60), radial(cx, ty - 30, 10, power=1.5))
    if night:
        # warm city glow at the horizon / street level
        img = screen(img, (255, 150, 90), smooth(hz - 160, y1, y) * 0.18)
        img = bokeh(img, [(r.uniform(x0, x1), r.uniform(hz + 10, y1)) for _ in range(120)],
                    [[(255, 200, 120), (255, 240, 210), (255, 120, 100)][r.integers(0, 3)] for _ in range(120)],
                    [r.uniform(1.5, 4) for _ in range(120)], 0.8, 0.5)
    else:
        img = screen(img, (255, 255, 255), smooth(hz - 200, hz + 40, y) * 0.12)
    return img


# ====================================================================== screens / charts
def chart_img(w, h, seed=0, kind='candle', title=None, light=False):
    """Trading-terminal screen (PIL RGB)."""
    r = rng0(seed)
    S = 2
    im = Image.new('RGB', (w * S, h * S), (10, 14, 24) if not light else (235, 238, 242))
    d = ImageDraw.Draw(im)
    gc = (30, 40, 60) if not light else (205, 210, 220)
    for i in range(1, 6):
        d.line([(0, h * S * i / 6), (w * S, h * S * i / 6)], fill=gc, width=S)
    for i in range(1, 8):
        d.line([(w * S * i / 8, 0), (w * S * i / 8, h * S)], fill=gc, width=S)
    top = 0.14 * h * S
    if kind == 'candle':
        n = max(12, w // 9)
        p = 0.5
        prices = []
        for i in range(n):
            o = p
            p = np.clip(p + r.normal(0.012 if r.random() < 0.55 else -0.01, 0.05), 0.08, 0.92)
            hi = max(o, p) + abs(r.normal(0, 0.02))
            lo = min(o, p) - abs(r.normal(0, 0.02))
            prices.append((o, p, hi, lo))
        cw = w * S / n
        Y = lambda v: top + (1 - v) * (h * S * 0.62)
        for i, (o, c, hi, lo) in enumerate(prices):
            col = (235, 60, 60) if c >= o else (40, 200, 110)
            cx = cw * (i + 0.5)
            d.line([(cx, Y(hi)), (cx, Y(lo))], fill=col, width=max(1, S))
            d.rectangle((cx - cw * 0.32, min(Y(o), Y(c)), cx + cw * 0.32, max(Y(o), Y(c)) + 1), fill=col)
        ma = np.convolve([q[1] for q in prices], np.ones(5) / 5, mode='same')
        d.line([(cw * (i + 0.5), Y(v)) for i, v in enumerate(ma)], fill=(255, 200, 60), width=S)
        # volume bars
        for i, (o, c, hi, lo) in enumerate(prices):
            vh = r.uniform(0.03, 0.16) * h * S
            col = (150, 50, 50) if c >= o else (30, 130, 80)
            d.rectangle((cw * (i + 0.18), h * S - vh, cw * (i + 0.82), h * S), fill=col)
    elif kind == 'line':
        n = 60
        v = np.cumsum(r.normal(0.004, 0.03, n)) + 0.5
        v = (v - v.min()) / (v.max() - v.min() + 1e-6) * 0.6 + 0.2
        pts = [(w * S * i / (n - 1), top + (1 - q) * h * S * 0.8) for i, q in enumerate(v)]
        d.polygon(pts + [(w * S, h * S), (0, h * S)], fill=(20, 60, 90) if not light else (190, 215, 240))
        d.line(pts, fill=(60, 200, 255) if not light else (30, 110, 200), width=2 * S)
    elif kind == 'table':
        rows = max(4, int(h / 14))
        for i in range(rows):
            yy = top + i * (h * S - top) / rows
            for j in range(4):
                tw = r.uniform(0.08, 0.18) * w * S
                xx = w * S * (0.04 + j * 0.24)
                col = [(200, 210, 220), (235, 70, 70), (50, 210, 120), (200, 210, 220)][j if j < 3 else 0]
                if j == 0:
                    col = (150, 170, 200)
                d.rectangle((xx, yy + 2 * S, xx + tw, yy + 2 * S + max(2, h * S / rows * 0.4)), fill=col)
    # header bar
    d.rectangle((0, 0, w * S, top * 0.8), fill=(20, 30, 50) if not light else (40, 70, 130))
    if title and h > 60:
        f = cfont(top * 0.55)
        d.text((w * S * 0.03, top * 0.1), title, font=f, fill=(220, 230, 255))
    else:
        for k in range(3):
            d.rectangle((w * S * (0.03 + k * 0.12), top * 0.25, w * S * (0.12 + k * 0.12), top * 0.55),
                        fill=(120, 140, 180))
    return im.resize((w, h), Image.LANCZOS)


def screen_quad(img, pts, src, glow_col=(90, 150, 255), glow=0.25, bezel=(14, 15, 18), bz=0.04):
    """Monitor: bezel quad + warped screen image + a soft glow."""
    tl, tr, br, bl = [np.array(p, np.float32) for p in pts]
    img, m = quad(img, [tuple(p) for p in (tl, tr, br, bl)], bezel)

    def L(a, b, t):
        return a + (b - a) * t
    # inset quad
    itl = L(L(tl, br, bz), L(tl, br, bz), 0)
    itr = L(tr, bl, bz)
    ibr = L(br, tl, bz)
    ibl = L(bl, tr, bz)
    img = paste_quad(img, src.convert('RGBA'), [tuple(p) for p in (itl, itr, ibr, ibl)])
    if glow:
        cx, cy = (tl + br) / 2
        rr = np.linalg.norm(tr - tl) * 1.1
        img = screen(img, glow_col, radial(cx, cy, rr, power=2) * glow)
    return img, m


def rect3(cam, X, Y, Z, w, h, yaw=0.0):
    """Vertical rectangle centred at (X, Y+h/2, Z), width w, rotated yaw radians about Y. Returns tl,tr,br,bl."""
    c, s = math.cos(yaw), math.sin(yaw)
    dx, dz = c * w / 2, s * w / 2
    P = cam.P
    return [P(X - dx, Y + h, Z - dz), P(X + dx, Y + h, Z + dz), P(X + dx, Y, Z + dz), P(X - dx, Y, Z - dz)]


def downlight(img, cam, X, Y, Z, r=0.08, col=(255, 248, 230), glow=1.0):
    cx, cy = cam.P(X, Y, Z)
    rr = r * cam.sc(Z)
    img = over(img, col, Mask().ellipse((cx - rr, cy - rr * 0.35, cx + rr, cy + rr * 0.35)).get(0.5))
    img = screen(img, col, radial(cx, cy, rr * 6, power=2.5) * 0.35 * glow)
    return img


def reflect_down(img, m, y_axis, strength=0.3, blur_r=6, fade=250, tint=(1, 1, 1)):
    """Mirror the image above y_axis into the floor region m (glossy floor)."""
    yy = np.arange(H)
    src = np.clip(2 * y_axis - yy, 0, H - 1).astype(int)
    ref = img[src]
    ref = blur(ref, blur_r) * np.array(tint, np.float32)
    k = np.clip(1 - (yy - y_axis) / fade, 0, 1)[:, None] * (yy > y_axis)[:, None]
    return lerp(img, 1 - (1 - img) * (1 - ref), m * k * strength)


# ====================================================================== rental room
def rental_room(night=False):
    x, y = grid()
    cam = Cam(F=880.0, VX=1010.0, VY=500.0, EYE=1.35)
    P = cam.P
    XL, XR, CEIL, ZB = -1.45, 1.35, 2.55, 3.0
    R = Room(cam, XL, XR, CEIL, ZB)
    r = rng0(11)
    BULB = (0.0, 2.05, 1.9)
    WIN = (0.15, 1.05, 1.05, 1.95)  # X0, Y0, X1, Y1 on back wall
    # ---------------- walls: dirty off-white paint, stains, peeling
    tex = fbm(H, W, 90, 5, seed=12)
    tex2 = fbm(H, W, 30, 4, seed=13)
    wall = lerp(full((214, 206, 180)), full((232, 226, 204)), tex[..., None] * 0.8)
    img = full((190, 184, 165))
    for name, coords, nrm, dark in (('back', R.back, (0, 0, -1), 1.0), ('left', R.left, (1, 0, 0), 0.88),
                                    ('right', R.right, (-1, 0, 0), 0.8), ('ceil', R.ceil, (0, -1, 0), 0.95)):
        X_, Y_, Z_ = coords
        # surface uv (for stains)
        u = X_ + Z_ * (1 if name in ('left', 'right') else 0)
        v = Y_ + (Z_ if name == 'ceil' else 0)
        col = wall * dark
        # grime toward the floor + water stain blotches
        grime = smooth(0.9, 0.0, Y_) * 0.25 if name != 'ceil' else 0
        col = col * (1 - grime)[..., None] if name != 'ceil' else col
        img = R.paint(img, name, col)
    # water stains (rings) on back wall upper-left corner and ceiling corner
    stain = Mask()
    for (sx, sy, sr) in ((470, 150, 85), (520, 210, 50), (1480, 70, 70)):
        stain.ellipse((sx - sr * 1.3, sy - sr * 0.8, sx + sr * 1.3, sy + sr * 0.8))
    st = stain.get(25) * (0.6 + 0.6 * tex2)
    ring = np.clip(st * 4, 0, 1) * np.clip((1 - st) * 4, 0, 1)
    img = lerp(img, img * C((170, 150, 110)) * 1.1, np.clip(st * 0.3 + ring * 0.45, 0, 1) * (R.m_back + R.m_ceil + R.m_left))
    # stamped small-ad graffiti (classic urban-village wall)
    for (txt, X0_, Y0_, col, ang) in (('开锁 138****0000', -1.05, 1.62, (40, 60, 150), 4), ('疏通下水道', 0.65, 0.85, (30, 30, 35), -3),
                                     ('办证 刻章', -0.95, 0.75, (40, 60, 150), -6)):
        tim = text_rgba(txt, 26, col).rotate(ang, resample=Image.BICUBIC, expand=True)
        tx, ty = P(X0_, Y0_, ZB)
        img, _ = paste_at(img, tim, tx, ty, 0.6)
    # peeling patches: irregular blobs with exposed grey plaster + bright curled edge
    peel = np.zeros((H, W), np.float32)
    for (px, py, pr, sd) in ((1230, 300, 80, 1), (700, 620, 60, 2), (1600, 520, 110, 3), (330, 780, 70, 4), (870, 250, 45, 5)):
        n = fbm(H, W, 30, 4, seed=40 + sd)
        d = np.sqrt(((x - px) / pr) ** 2 + ((y - py) / (pr * 0.7)) ** 2)
        peel = np.maximum(peel, smooth(1.0, 0.75, d + (n - 0.5) * 0.9))
    walls_m = np.clip(R.m_back + R.m_left + R.m_right, 0, 1)
    peel *= walls_m
    plaster = lerp(full((160, 158, 150)), full((185, 182, 172)), tex2[..., None])
    img = lerp(img, plaster, peel)
    edge = np.clip(peel - ndimage.grey_erosion(peel, size=(5, 5)), 0, 1)
    img = screen(img, (255, 252, 240), edge * 0.6)
    img = lerp(img, img * 0.7, np.clip(ndimage.shift(peel, (4, 3), order=1) - peel, 0, 1) * 0.8)
    # a crack
    cr = Mask()
    pts = [(1120, 0)]
    for i in range(12):
        pts.append((pts[-1][0] + r.uniform(-20, 25), pts[-1][1] + r.uniform(18, 34)))
    cr.line(pts, 2)
    img = lerp(img, img * 0.55, cr.get(0.5) * R.m_back)
    # corner edge shading (room seams)
    for a, b in ((P(XL, CEIL, ZB), P(XL, 0, ZB)), (P(XR, CEIL, ZB), P(XR, 0, ZB)), (P(XL, CEIL, ZB), P(XR, CEIL, ZB))):
        img = lerp(img, img * 0.7, Mask().line([a, b], 3).get(6))
    # ---------------- floor: cheap beige ceramic tiles with grime
    FX_, _, FZ = R.floor
    rnd, gr = tiles(FX_ + 3, FZ, 0.4, 0.4, 0.012)
    fl = lerp(full((180, 160, 130)), full((205, 188, 160)), rnd[..., None] * 0.7)
    fl *= (0.85 + 0.2 * fbm(H, W, 40, 4, seed=14))[..., None]
    fl = lerp(fl, full((95, 85, 70)), gr * 0.8)
    img = lerp(img, fl, R.m_floor)
    # skirting grime line
    for a, b in ((P(XL, 0, ZB), P(XR, 0, ZB)), (P(XL, 0, ZB), P(XL, 0, 0.3)), (P(XR, 0, ZB), P(XR, 0, 0.3))):
        img = lerp(img, img * 0.6, Mask().line([a, b], 4).get(3))
    # ---------------- window on back wall + view of neighbour wall 1 m away
    wx0, wy0 = P(WIN[0], WIN[3], ZB)
    wx1, wy1 = P(WIN[2], WIN[1], ZB)
    ZN = ZB + 1.0
    vx = (x - cam.VX) * ZN / cam.F
    vy = cam.EYE - (y - cam.VY) * ZN / cam.F
    nb_rnd, nb_g = tiles(vx + 5, vy, 0.24, 0.06, 0.006)
    nb = lerp(full((150, 140, 125)), full((175, 165, 148)), nb_rnd[..., None])
    nb = lerp(nb, full((110, 100, 90)), nb_g * 0.5)
    nb *= (0.8 + 0.3 * fbm(H, W, 30, 4, seed=15))[..., None]
    # light falling from above in the narrow gap
    nb *= (0.55 + 0.6 * smooth(0.6, 2.8, vy))[..., None]
    # neighbour's window
    nwx0, nwy0 = P(0.05, 1.85, ZN)
    nwx1, nwy1 = P(0.75, 1.05, ZN)
    nwin = rect_m(nwx0, nwy0, nwx1, nwy1)
    if night:
        nb = nb * C((60, 62, 90)) * 0.55
        nwc = vgrad([(0, (255, 200, 120)), (1, (230, 150, 80))], y0=nwy0, y1=nwy1)
        nb = lerp(nb, nwc, nwin)
        # neighbour's curtain half-drawn + a silhouette shape
        nb = lerp(nb, full((170, 70, 60)), rect_m(nwx0, nwy0, nwx0 + (nwx1 - nwx0) * 0.38, nwy1) * 0.95)
        nb = lerp(nb, full((90, 50, 40)), Mask().ellipse((nwx0 + 120, nwy0 + 40, nwx0 + 170, nwy0 + 100)).get(2) * 0.8)
        nb = lerp(nb, full((90, 50, 40)), Mask().ellipse((nwx0 + 95, nwy0 + 95, nwx0 + 195, nwy1 + 20)).get(2) * 0.8 * nwin)
        nb = screen(nb, (255, 170, 90), radial((nwx0 + nwx1) / 2, nwy1, 160, power=2, sy=0.5) * 0.4)
    else:
        nwc = vgrad([(0, (70, 80, 90)), (1, (40, 45, 55))], y0=nwy0, y1=nwy1)
        nb = lerp(nb, nwc, nwin)
        nb = screen(nb, (200, 220, 240), rect_m(nwx0 + 6, nwy0 + 6, nwx0 + 40, nwy1 - 6, 3) * 0.25)
    nb = over(nb, (90, 85, 80) if not night else (30, 30, 40), Mask().rect((nwx0 - 6, nwy0 - 6, nwx1 + 6, nwy0)).get())
    nb = over(nb, (90, 85, 80) if not night else (30, 30, 40), Mask().rect((nwx0 - 6, nwy1, nwx1 + 6, nwy1 + 6)).get())
    # rusty anti-theft grille + a drain pipe on the neighbour wall
    pp0 = P(1.0, 3.0, ZN)[0]
    nb = over(nb, (120, 120, 115) if not night else (40, 40, 50), rect_m(pp0, 0, pp0 + 18, H))
    # laundry on a bamboo pole between the buildings
    ZL = ZB + 0.45
    la, lb = P(-0.4, 1.78, ZL), P(1.6, 1.86, ZL)
    lay = Mask().line([la, lb], 5).get()
    nb = over(nb, (130, 100, 60) if not night else (35, 30, 30), lay)
    items = [(0.25, 0.35, 0.45, (60, 120, 200), 'shirt'), (0.62, 0.22, 0.55, (230, 230, 225), 'pants'),
             (0.86, 0.16, 0.2, (240, 120, 150), 'sock'), (0.98, 0.16, 0.2, (240, 120, 150), 'sock')]
    for (Xc, wdt, ln, col, kind) in items:
        t = (Xc + 0.4) / 2.0
        top = la[1] + (lb[1] - la[1]) * t
        cxp = P(Xc, 0, ZL)[0]
        sc = cam.sc(ZL)
        ww, hh = wdt * sc, ln * sc
        m = Mask()
        if kind == 'shirt':
            m.poly([(cxp - ww / 2, top), (cxp + ww / 2, top), (cxp + ww * 0.75, top + hh * 0.3), (cxp + ww * 0.45, top + hh * 0.35),
                    (cxp + ww * 0.42, top + hh), (cxp - ww * 0.42, top + hh), (cxp - ww * 0.45, top + hh * 0.35), (cxp - ww * 0.75, top + hh * 0.3)])
        elif kind == 'pants':
            m.poly([(cxp - ww / 2, top), (cxp + ww / 2, top), (cxp + ww * 0.55, top + hh), (cxp + ww * 0.08, top + hh),
                    (cxp, top + hh * 0.3), (cxp - ww * 0.08, top + hh), (cxp - ww * 0.55, top + hh)])
        else:
            m.poly([(cxp - ww / 2, top), (cxp + ww / 2, top), (cxp + ww / 2, top + hh * 0.7), (cxp + ww * 1.1, top + hh * 0.85),
                    (cxp + ww * 1.1, top + hh), (cxp - ww / 2, top + hh)])
        mm = m.get(0.8)
        cc = full(col) * (0.75 + 0.25 * fbm(H, W, 12, 3, seed=int(Xc * 100))[..., None])
        if night:
            cc = cc * C((70, 75, 110)) * 0.6
        nb = lerp(nb, cc, mm)
        nb = over(nb, (230, 60, 60) if not night else (60, 30, 30), Mask().rect((cxp - 4, top - 6, cxp + 4, top + 8)).get())
    # sky sliver at the very top
    gl = vgrad([(0, (240, 245, 250) if not night else (30, 40, 80)), (1, (200, 210, 220) if not night else (20, 25, 50))], y0=wy0, y1=wy0 + 40)
    nb = lerp(nb, gl, (y < wy0 + 22 + 10 * np.sin(x * 0.02)).astype(np.float32))
    # reveal (wall thickness) + frame
    wm = rect_m(wx0, wy0, wx1, wy1)
    img = over(img, (150, 140, 120) if not night else (60, 55, 60), rect_m(wx0 - 16, wy0 - 16, wx1 + 16, wy1 + 16) * R.m_back)
    img = lerp(img, nb, wm)
    fr = Mask()
    for k in (0, 0.5, 1):
        xx = wx0 + (wx1 - wx0) * k
        fr.rect((xx - 6, wy0, xx + 6, wy1))
    fr.rect((wx0, wy0 - 6, wx1, wy0 + 6)).rect((wx0, wy1 - 6, wx1, wy1 + 6))
    img = over(img, (200, 200, 195) if not night else (70, 70, 80), fr.get())
    # glass sheen + grime
    if not night:
        img = screen(img, (255, 255, 255), wm * np.clip(1 - np.abs((x - wx0) - (y - wy0) * 0.6 - 80) / 50, 0, 1) * 0.25)
    # anti-theft bars
    bars = Mask()
    for k in range(1, 7):
        xx = wx0 + (wx1 - wx0) * k / 7
        bars.rect((xx - 3, wy0 - 10, xx + 3, wy1 + 10))
    img = over(img, (60, 55, 50) if not night else (20, 20, 25), bars.get())
    win_snap = img.copy()
    # cheap curtain (half pulled) - floral polyester
    cx0, cx1 = wx1 - 40, wx1 + 110
    folds = 0.5 + 0.5 * np.sin((x - cx0) * 0.15)
    cm = Mask().poly([(cx0, wy0 - 40), (cx1, wy0 - 40), (cx1 + 10, wy1 + 70), (cx0 + 20, wy1 + 60)]).get()
    ccol = full((120, 170, 160)) * (0.75 + 0.3 * folds[..., None])
    dots = ((np.sin(x * 0.35) * np.sin(y * 0.35)) > 0.75).astype(np.float32)
    ccol = lerp(ccol, full((240, 220, 150)), dots * 0.6)
    img = lerp(img, ccol, cm)
    img = over(img, (80, 80, 80), Mask().line([(wx0 - 30, wy0 - 42), (cx1 + 20, wy0 - 42)], 3).get())
    # ---------------- wall stuff: calendar, socket + charger, hook with jacket
    # calendar on left wall (perspective)
    cal = [P(XL, 1.85, 1.5), P(XL, 1.85, 1.9), P(XL, 1.3, 1.9), P(XL, 1.3, 1.5)]
    img, _ = quad(img, cal, (235, 232, 222))
    img, _ = quad(img, [cal[0], cal[1], P(XL, 1.72, 1.9), P(XL, 1.72, 1.5)], (200, 40, 40))
    img, _ = quad(img, [P(XL, 1.69, 1.54), P(XL, 1.69, 1.86), P(XL, 1.52, 1.86), P(XL, 1.52, 1.54)], (120, 170, 120))
    gm = Mask()
    for k in range(5):
        gm.line([P(XL, 1.5 - k * 0.04, 1.54), P(XL, 1.5 - k * 0.04, 1.86)], 1.5)
    for k in range(8):
        gm.line([P(XL, 1.5, 1.54 + k * 0.045), P(XL, 1.34, 1.54 + k * 0.045)], 1.5)
    img = over(img, (150, 150, 150), gm.get())
    # socket on back wall low-left with charger + cable to the bed
    sx, sy = P(-0.25, 0.42, ZB)
    img = over(img, (235, 232, 220), rect_m(sx - 26, sy - 26, sx + 26, sy + 26, 0.8))
    img = over(img, (150, 145, 135), rect_m(sx - 26, sy - 26, sx + 26, sy + 26, 0.8) - rect_m(sx - 23, sy - 23, sx + 23, sy + 23, 0.8))
    img = over(img, (250, 250, 248), rect_m(sx - 12, sy - 18, sx + 12, sy + 10, 0.6))
    cab = bezier((sx, sy + 10), (sx - 40, sy + 120), (sx - 200, sy + 60), (sx - 330, sy + 120), n=50)
    img = over(img, (245, 245, 245), Mask().line(cab, 3).get(0.6))
    # power strip on the floor
    # jacket hook on right wall
    hx, hy = P(XR, 2.0, 1.2)
    img = over(img, (120, 120, 120), Mask().circle(hx, hy, 7).get())
    jk = Mask().poly([(hx - 10, hy), (hx + 6, hy), (hx + 40, hy + 80), (hx + 46, hy + 330), (hx - 50, hy + 360), (hx - 60, hy + 90)]).get(1)
    img = lerp(img, full((245, 200, 40)) * (0.75 + 0.25 * fbm(H, W, 20, 3, seed=16)[..., None]), jk)
    img = over(img, (200, 200, 200), Mask().line([(hx - 52, hy + 240), (hx + 45, hy + 225)], 8).get() * jk)
    # ---------------- bed along the left wall (metal frame, thin mattress, crumpled sheets)
    BX0, BX1, BZ0, BZ1, BT = XL, -0.42, 0.9, ZB, 0.48
    frame = (70, 80, 95)
    # legs/frame side (facing +X)
    img, _ = quad(img, [P(BX1, BT - 0.12, BZ0), P(BX1, BT - 0.12, BZ1), P(BX1, 0.0, BZ1), P(BX1, 0.0, BZ0)], (40, 38, 36))
    img = over(img, frame, Mask().line([P(BX1, 0.3, BZ0), P(BX1, 0.3, BZ1)], 6).get())
    for zz in (BZ0 + 0.05, BZ1 - 0.05):
        img = over(img, frame, Mask().line([P(BX1, 0.3, zz), P(BX1, 0.0, zz)], 7).get())
    # head rail at the back
    img = over(img, frame, Mask().line([P(BX0, 0.95, BZ1 - 0.02), P(BX1, 0.95, BZ1 - 0.02)], 8).get())
    for k in range(5):
        xx = BX0 + (BX1 - BX0) * (k + 0.5) / 5
        img = over(img, frame, Mask().line([P(xx, 0.95, BZ1 - 0.02), P(xx, BT, BZ1 - 0.02)], 4).get())
    # mattress side + top (sheet)
    sheet_base = full((150, 185, 215))
    chk = ((np.floor(x / 26 + y / 60) + np.floor(y / 26 - x / 120)) % 2).astype(np.float32)
    sheet = lerp(sheet_base, full((175, 205, 230)), chk * 0.5)
    crum = fbm(H, W, 50, 5, seed=17)
    crum2 = fbm(H, W, 18, 4, seed=18, sx=1.5)
    sh_ = 0.72 + 0.5 * crum[..., None] + 0.12 * crum2[..., None]
    sheet = sheet * sh_
    img, _ = quad(img, [P(BX1, BT, BZ0), P(BX1, BT, BZ1), P(BX1, BT - 0.14, BZ1), P(BX1, BT - 0.14, BZ0)], sheet * 0.75)
    img, _ = quad(img, [P(BX0, BT, BZ0), P(BX1, BT, BZ0), P(BX1, BT - 0.14, BZ0), P(BX0, BT - 0.14, BZ0)], sheet * 0.85)
    top_m = Mask().poly([P(BX0, BT, BZ0), P(BX1, BT, BZ0), P(BX1, BT, BZ1), P(BX0, BT, BZ1)]).get(0.6)
    img = lerp(img, sheet, top_m)
    # crumpled thin blanket in a heap (pinkish floral) with hanging corner
    bl = Mask()
    pts = [P(BX0, BT + 0.05, 1.05), P(-0.6, BT + 0.18, 1.2), P(-0.38, BT + 0.05, 1.5), P(-0.32, BT - 0.25, 1.55),
           P(-0.4, BT - 0.3, 1.9), P(-0.38, BT + 0.08, 2.1), P(-0.7, BT + 0.22, 2.3), P(BX0, BT + 0.12, 2.4)]
    bl.poly(pts)
    blm = bl.get(1.2)
    bc = full((230, 150, 160)) * (0.65 + 0.55 * fbm(H, W, 35, 5, seed=19)[..., None])
    flor = ((np.sin(x * 0.12) * np.sin(y * 0.15 + x * 0.03)) > 0.82).astype(np.float32)
    bc = lerp(bc, full((255, 235, 120)), flor * 0.7)
    img = lerp(img, bc, blm)
    # pillow (flat, yellowed)
    pa, pb = P(BX0 + 0.05, BT + 0.15, BZ1 - 0.08), P(BX1 - 0.08, BT, BZ1 - 0.45)
    img = lerp(img, full((235, 230, 210)) * (0.85 + 0.15 * crum[..., None]), Mask().ellipse((pa[0], pa[1], pb[0], pb[1])).get(2))
    # phone on the bed at end of cable
    px_, py_ = P(-0.75, BT, 1.6)
    ph = Mask().poly([(px_ - 50, py_ - 4), (px_ + 30, py_ - 14), (px_ + 52, py_ + 14), (px_ - 30, py_ + 26)]).get(0.8)
    img = over(img, (20, 20, 25), ph)
    if night:
        img = screen(img, (120, 170, 255), radial(px_, py_ + 5, 90, power=2) * 0.4)
    # ---------------- floor clutter: thermal box, stool + noodles, slippers, bottles
    TX0, TX1, TZ0, TZ1, TH = 0.72, 1.32, 2.35, 2.95, 0.5
    img, bm = box3(img, cam, TX0, TX1, 0, TH, TZ0, TZ1, (250, 200, 30), shade=(1.0, 0.92, 0.7), top_col=C((255, 220, 70)))
    # lid seam on top
    img = over(img, (180, 140, 20), Mask().line([P(TX0, TH, TZ0 + 0.04), P(TX1, TH, TZ0 + 0.04)], 3).get())
    lx0, ly0 = P(TX0 + 0.12, TH - 0.12, TZ0)
    lx1, ly1 = P(TX1 - 0.12, TH - 0.32, TZ0)
    logo = sign_img('美团团', int(lx1 - lx0), int(ly1 - ly0), None, (40, 40, 40))
    img, _ = paste_at(img, logo, lx0, ly0, 0.85)
    # strap
    img = over(img, (40, 40, 40), Mask().line([P(TX0 + 0.05, TH, TZ0), P(TX0 + 0.05, TH * 0.4, TZ0)], 6).get())
    img = over(img, (200, 200, 190), Mask().line([P(TX0, 0.08, TZ0), P(TX1, 0.08, TZ0)], 5).get())
    # plastic stool with noodle cups
    img = plastic_stool(img, cam, 0.42, 1.95, (215, 45, 45), s=1.0)
    sxc, syc = P(0.42, 0.45, 1.95)
    sc = cam.sc(1.95)

    def cup(img, cx, by, s, lid=False, fork=False, col=(220, 40, 40)):
        w0, w1, h = 0.05 * s, 0.065 * s, 0.11 * s
        m = Mask().poly([(cx - w0, by), (cx + w0, by), (cx + w1, by - h), (cx - w1, by - h)]).get(0.6)
        cc = lerp(full((245, 240, 230)), full(col), (np.abs(grid()[1] - (by - h * 0.55)) < h * 0.2).astype(np.float32))
        img = lerp(img, cc * (0.8 + 0.25 * smooth(cx - w1, cx + w1, grid()[0]))[..., None], m)
        img = over(img, (250, 235, 200) if lid else (200, 150, 70), Mask().ellipse((cx - w1, by - h - w1 * 0.25, cx + w1, by - h + w1 * 0.25)).get(0.6))
        if fork:
            img = over(img, (240, 240, 240), Mask().line([(cx + w0 * 0.2, by - h - w1 * 0.1), (cx + w1 * 0.9, by - h * 1.9)], max(2, s * 0.006)).get(0.5))
        return img
    img = cup(img, sxc - 0.06 * sc, syc + 0.03 * sc, sc, fork=True)
    img = cup(img, sxc + 0.08 * sc, syc + 0.05 * sc, sc * 0.95, lid=True, col=(230, 140, 30))
    # stacked empty cups on the floor by the box
    for k, (Xc, Zc) in enumerate(((0.35, 2.6), (0.42, 2.45), (0.2, 2.75))):
        cx_, by_ = P(Xc, 0, Zc)
        img = cup(img, cx_, by_, cam.sc(Zc), lid=k == 1, col=[(220, 40, 40), (230, 140, 30), (40, 140, 60)][k])
    # slippers
    for k, (Xc, Zc) in enumerate(((-0.25, 1.15), (-0.08, 1.05))):
        cx_, cy_ = P(Xc, 0, Zc)
        s_ = cam.sc(Zc)
        img = over(img, (50, 110, 200), Mask().ellipse((cx_ - 0.05 * s_, cy_ - 0.02 * s_, cx_ + 0.05 * s_, cy_ + 0.13 * s_)).get(1))
        img = over(img, (30, 70, 150), Mask().ellipse((cx_ - 0.055 * s_, cy_ - 0.0 * s_, cx_ + 0.055 * s_, cy_ + 0.05 * s_)).get(1))
    # ---------------- bare bulb on a wire
    bx, by = P(*BULB)
    cx_top = P(BULB[0], CEIL, BULB[2])
    img = over(img, (30, 30, 30), Mask().line([cx_top, (bx, by - 14)], 2.5).get())
    img = over(img, (60, 60, 60), rect_m(bx - 7, by - 22, bx + 7, by - 8, 0.6))
    # ---------------- lighting
    if not night:
        # cool overcast morning: gentle light from the window
        L = (0.6, 1.6, ZB - 0.2)
        lt = np.zeros((H, W), np.float32)
        for name, nrm in (('floor', (0, 1, 0)), ('left', (1, 0, 0)), ('right', (-1, 0, 0)), ('ceil', (0, -1, 0))):
            lt += getattr(R, 'm_' + name) * point_light(getattr(R, name), L, 1.0, 1.6, nrm)
        img = img * (0.72 + 0.45 * np.clip(lt, 0, 1.2))[..., None]
        img = img * np.array([0.97, 1.0, 1.04], np.float32)
        img = lerp(img, win_snap, wm * (1 - cm))
        img = screen(img, (230, 240, 255), radial((wx0 + wx1) / 2, (wy0 + wy1) / 2, 520, power=2) * 0.18)
        # unlit bulb: glass
        img = over(img, (225, 225, 215), Mask().ellipse((bx - 16, by - 12, bx + 16, by + 26)).get(0.8))
        img = screen(img, (255, 255, 255), Mask().ellipse((bx - 9, by - 6, bx - 2, by + 8)).get(1) * 0.8)
        # window light patch on floor
        patch = Mask().poly([P(WIN[0], 0, ZB - 0.1), P(WIN[2], 0, ZB - 0.1), P(WIN[2] - 0.1, 0, ZB - 1.0), P(WIN[0] - 0.2, 0, ZB - 1.0)]).get(18)
        img = screen(img, (230, 235, 245), patch * R.m_floor * 0.18)
    else:
        lt = np.zeros((H, W), np.float32)
        for name, nrm in (('floor', (0, 1, 0)), ('left', (1, 0, 0)), ('right', (-1, 0, 0)), ('ceil', (0, -1, 0)), ('back', (0, 0, -1))):
            lt += getattr(R, 'm_' + name) * point_light(getattr(R, name), BULB, 1.0, 0.9, nrm)
        lt = np.clip(lt + (1 - np.clip(R.m_floor + R.m_left + R.m_right + R.m_ceil + R.m_back, 0, 1)) * 0.0, 0, 1.3)
        # objects (not on room surfaces) get light based on screen distance to bulb
        obj = radial(bx, by + 250, 1100, power=1.3)
        surf = np.clip(R.m_floor + R.m_left + R.m_right + R.m_ceil + R.m_back, 0, 1)
        # back wall pixels covered by objects are approximated by screen falloff
        L_ = lt * surf * 0.65 + obj * 0.6
        dark = img * C((55, 60, 95)) * 0.5
        lit_ = img * C((255, 205, 140)) * 1.15
        img = lerp(dark, lit_, np.clip(L_, 0, 1)[..., None])
        img = lerp(img, win_snap, wm * (1 - cm))
        # bulb glow
        img = over(img, (255, 236, 180), Mask().ellipse((bx - 16, by - 12, bx + 16, by + 26)).get(0.8))
        img = screen(img, (255, 250, 230), radial(bx, by + 7, 26, power=0.7))
        img = screen(img, (255, 190, 110), radial(bx, by + 7, 300, power=2.2) * 0.65)
        img = bloom(img, 0.8, 25, 0.6)
    return img


def rental_room_night():
    return rental_room(True)


# ====================================================================== shared lighting
def light_map(R, lights, surfaces=('floor', 'left', 'right', 'ceil', 'back')):
    nrm = {'floor': (0, 1, 0), 'left': (1, 0, 0), 'right': (-1, 0, 0), 'ceil': (0, -1, 0), 'back': (0, 0, -1)}
    lt = np.zeros((H, W), np.float32)
    for name in surfaces:
        m = getattr(R, 'm_' + name)
        for (L, pw, rad) in lights:
            lt += m * point_light(getattr(R, name), L, pw, rad, nrm[name])
    return lt


def candle_s(img, cam, X, Y, Z, hgt=0.14, glow=1.0, holder=True):
    """Candle at world pos (base); scaled by distance. Returns img."""
    s = cam.sc(Z)
    cx, by = cam.P(X, Y, Z)
    w = 0.035 * s
    h = hgt * s
    x, y = grid()
    if holder:
        img = over(img, (190, 160, 100), Mask().ellipse((cx - w * 1.8, by - w * 0.5, cx + w * 1.8, by + w * 0.5)).get(0.6))
    bc = gradient([(0, (200, 180, 150)), (0.4, (255, 245, 225)), (1, (190, 170, 140))], smooth(cx - w, cx + w, x))
    img = lerp(img, bc, Mask().rect((cx - w, by - h, cx + w, by)).get(0.6))
    img = over(img, (255, 250, 235), Mask().ellipse((cx - w, by - h - w * 0.3, cx + w, by - h + w * 0.3)).get(0.6))
    fh = max(6, 0.05 * s)
    fy = by - h
    flame = Mask().poly(bezier((cx, fy - fh), (cx + fh * 0.4, fy - fh * 0.1), (cx, fy + 1), n=16) +
                        bezier((cx, fy + 1), (cx - fh * 0.4, fy - fh * 0.1), (cx, fy - fh), n=16)).get(0.6)
    img = lerp(img, full((255, 210, 110)), flame)
    img = screen(img, (255, 250, 225), radial(cx, fy - fh * 0.35, fh * 0.35, power=0.7))
    img = screen(img, (255, 160, 70), radial(cx, fy - fh * 0.4, fh * 7, power=2.0) * 0.8 * glow)
    img = screen(img, (255, 130, 60), radial(cx, fy, fh * 22, power=2.5) * 0.35 * glow)
    return img


def petal(m, cx, cy, s, ang):
    pts = []
    for t in np.linspace(0, 2 * math.pi, 18):
        rr = s * (0.55 + 0.45 * math.cos(t)) if False else s
        px = math.cos(t) * s
        py = math.sin(t) * s * 0.6 * (1 - 0.35 * math.cos(t))
        ca, sa = math.cos(ang), math.sin(ang)
        pts.append((cx + px * ca - py * sa, cy + (px * sa + py * ca) * 0.55))
    m.poly(pts)


def night_sea_view(box, hz, moon=(0.62, 0.22), seed=73):
    x, y = grid()
    x0, y0, x1, y1 = box
    view = vgrad([(0, (6, 10, 30)), (0.7, (18, 34, 76)), (1, (40, 60, 110))], y0=y0, y1=hz)
    view = stars(view, (y < hz).astype(np.float32), n=500, seed=seed)
    mx, my = x0 + (x1 - x0) * moon[0], y0 + (hz - y0) * moon[1] + 40
    view = screen(view, (235, 240, 255), radial(mx, my, 28, power=0.25))
    view = screen(view, (140, 170, 230), radial(mx, my, 200, power=2) * 0.6)
    view = sea(view, hz, (10, 22, 50), (20, 40, 80), seed=seed - 1, streak=0.14, glint=(mx, 26, (210, 220, 255), 0.85))
    return view


# ====================================================================== hotel suite
def hotel_suite(door_open=False, dim=1.0):
    x, y = grid()
    cam = Cam(F=900.0, VX=880.0, VY=500.0, EYE=1.5)
    P = cam.P
    XL, XR, CEIL, ZB = -3.6, 4.6, 3.2, 7.0
    R = Room(cam, XL, XR, CEIL, ZB)
    BAL = (-2.9, 0.7, 2.75)  # balcony door X0, X1, top
    # ---------------- albedo
    wtex = fbm(H, W, 120, 4, seed=201)
    wall = lerp(full((205, 180, 150)), full((225, 200, 168)), wtex[..., None])
    img = full((200, 180, 150))
    for name, dk in (('back', 1.0), ('left', 0.9), ('right', 0.85), ('ceil', 0.95)):
        img = R.paint(img, name, wall * dk)
    # wainscot panels on back wall + side walls (lower 1 m)
    pm = Mask()
    for X0_ in np.arange(XL + 0.2, XR, 0.9):
        if BAL[0] - 0.2 < X0_ < BAL[1]:
            continue
        pm.rect((*P(X0_, 0.95, ZB), *P(X0_ + 0.7, 0.15, ZB)))
    img = lerp(img, img * 0.86, np.clip(pm.get(1) - ndimage.grey_erosion(pm.get(1), size=(7, 7)), 0, 1))
    img = over(img, (160, 130, 100), Mask().line([P(XL, 1.0, ZB), P(XR, 1.0, ZB)], 3).get())
    img = over(img, (160, 130, 100), Mask().line([P(XL, 1.0, ZB), P(XL, 1.0, 0.5)], 4).get())
    img = over(img, (160, 130, 100), Mask().line([P(XR, 1.0, ZB), P(XR, 1.0, 0.5)], 4).get())
    # crown moulding
    img = lerp(img, img * 0.8, Mask().line([P(XL, CEIL - 0.05, ZB), P(XR, CEIL - 0.05, ZB)], 6).get(2))
    # floor: dark walnut planks
    FX_, _, FZ = R.floor
    plank = np.floor(FX_ / 0.2)
    pr = hash2(plank, 0.0, 3)
    seg = np.floor(FZ / 1.8 + pr * 3)
    sr = hash2(plank, seg, 5)
    wood = gradient([(0, (70, 42, 28)), (0.5, (95, 60, 38)), (1, (115, 75, 48))], 0.3 + 0.5 * sr)
    wood *= (0.88 + 0.16 * fbm(H, W, 6, 3, seed=202, sx=0.15)[..., None])
    seams = (np.abs(FX_ / 0.2 - np.round(FX_ / 0.2)) < 0.03 * (FZ / 3 + 0.3)).astype(np.float32)
    wood = lerp(wood, wood * 0.6, seams * 0.6)
    img = lerp(img, wood, R.m_floor)
    # rug under the bed
    rug = Mask().poly([P(0.2, 0, 2.6), P(4.4, 0, 2.6), P(4.4, 0, 6.6), P(0.2, 0, 6.6)]).get(1)
    rugc = full((150, 40, 50)) * (0.85 + 0.2 * fbm(H, W, 4, 2, seed=203)[..., None])
    border = Mask().poly([P(0.35, 0, 2.75), P(4.25, 0, 2.75), P(4.25, 0, 6.45), P(0.35, 0, 6.45)]).get(1)
    rugc = lerp(rugc, full((200, 150, 80)), np.clip(rug - border, 0, 1) * 0.0 + (border - ndimage.grey_erosion(border, size=(5, 5))).clip(0, 1))
    img = lerp(img, rugc, rug)
    # ---------------- balcony door with moonlit sea
    bx0, by0 = P(BAL[0], BAL[2], ZB)
    bx1, by1 = P(BAL[1], 0, ZB)
    hz = by0 + (by1 - by0) * 0.5
    view = night_sea_view((bx0, by0, bx1, by1), hz, moon=(0.7, 0.18))
    isl = Mask().poly([(bx0 + 20, hz + 1), (bx0 + 80, hz - 18), (bx0 + 150, hz - 24), (bx0 + 220, hz - 8), (bx0 + 260, hz + 1)]).get(0.6)
    view = lerp(view, view * 0.6, isl)
    # balcony railing silhouette outside
    ry = P(0, 1.05, ZB + 1.2)[1]
    view = over(view, (25, 28, 45), np.exp(-((y - ry) / 3) ** 2))
    rb = Mask()
    for xx in np.arange(bx0, bx1, 34):
        rb.rect((xx, ry, xx + 4, by1))
    view = over(view, (25, 28, 45), rb.get() * 0.9)
    img = over(img, (60, 45, 35), rect_m(bx0 - 16, by0 - 16, bx1 + 16, by1))
    bm = rect_m(bx0, by0, bx1, by1)
    img = lerp(img, view, bm)
    mid = (bx0 + bx1) / 2
    img = over(img, (55, 42, 34), rect_m(mid - 7, by0, mid + 7, by1))
    img = over(img, (55, 42, 34), rect_m(bx0, by1 - 30, bx1, by1))
    img = screen(img, (180, 200, 255), bm * np.clip(1 - np.abs((x - bx0) - (y - by0) * 0.5 - 140) / 40, 0, 1) * 0.12)
    # sheer curtains + heavy drapes
    for (cx0, cx1, side) in ((bx0 - 160, bx0 + 70, -1), (bx1 - 70, bx1 + 170, 1)):
        folds = 0.5 + 0.5 * np.sin((x - cx0) * 0.11 + np.sin(y * 0.004) * 2)
        cm = Mask().poly([(cx0, by0 - 50), (cx1, by0 - 50), (cx1 + 20 * side, by1 + 10), (cx0 + 20 * side, by1 + 10)]).get(1)
        img = lerp(img, full((130, 25, 40)) * (0.55 + 0.5 * folds[..., None]), cm)
    img = over(img, (170, 140, 80), rect_m(bx0 - 200, by0 - 62, bx1 + 210, by0 - 50))
    # ---------------- entry door on the left wall
    DZ0, DZ1, DH = 4.7, 5.8, 2.3
    door_pts = [P(XL, DH, DZ0), P(XL, DH, DZ1), P(XL, 0, DZ1), P(XL, 0, DZ0)]
    img, _ = quad(img, [P(XL, DH + 0.1, DZ0 - 0.1), P(XL, DH + 0.1, DZ1 + 0.1), P(XL, 0, DZ1 + 0.1), P(XL, 0, DZ0 - 0.1)], (90, 60, 40))
    if not door_open:
        img, dm = quad(img, door_pts, (75, 45, 30))
        pn = [P(XL, DH - 0.15, DZ0 + 0.12), P(XL, DH - 0.15, DZ1 - 0.12), P(XL, 1.25, DZ1 - 0.12), P(XL, 1.25, DZ0 + 0.12)]
        img, _ = quad(img, pn, (85, 52, 35))
        pn = [P(XL, 1.1, DZ0 + 0.12), P(XL, 1.1, DZ1 - 0.12), P(XL, 0.15, DZ1 - 0.12), P(XL, 0.15, DZ0 + 0.12)]
        img, _ = quad(img, pn, (85, 52, 35))
        hx, hy = P(XL, 1.0, DZ1 - 0.12)
        img = over(img, (220, 190, 110), rect_m(hx - 4, hy - 30, hx + 4, hy + 30))
        # 'do not disturb' card
        img, _ = quad(img, [P(XL, 1.22, DZ1 - 0.16), P(XL, 1.22, DZ1 - 0.06), P(XL, 0.95, DZ1 - 0.06), P(XL, 0.95, DZ1 - 0.16)], (200, 40, 50))
    else:
        # doorway: bright corridor beyond
        cor = vgrad([(0, (255, 245, 220)), (1, (230, 210, 170))], y0=P(XL, DH, DZ0)[1], y1=P(XL, 0, DZ0)[1])
        img, dm = quad(img, door_pts, cor)
        # corridor far wall hint
        img, _ = quad(img, [P(XL - 1.6, DH, DZ0 + 0.2), P(XL - 1.6, DH, DZ1 - 0.2), P(XL - 1.6, 0, DZ1 - 0.2), P(XL - 1.6, 0, DZ0 + 0.2)], (235, 220, 190), alpha=0.6)
        # door leaf swung into the room (hinge at far edge DZ1)
        ang = math.radians(70)
        lx, lz = XL + 1.0 * math.sin(ang), DZ1 - 1.0 * math.cos(ang)
        leaf = [P(XL, DH, DZ1), P(lx, DH, lz), P(lx, 0, lz), P(XL, 0, DZ1)]
        img, _ = quad(img, leaf, (60, 36, 24))
        img = over(img, (40, 24, 16), Mask().line([P(lx, DH, lz), P(lx, 0, lz)], 10).get(1))
        hx, hy = P(lx - 0.05, 1.0, lz + 0.05)
        img = over(img, (230, 200, 120), rect_m(hx - 18, hy - 5, hx + 6, hy + 5))
        # chain lock snapped (comedy)
    # ---------------- bed (headboard on back wall)
    X0, X1, Z0, Z1, TOP = 1.1, 4.0, 4.6, ZB, 0.62
    hb = [P(X0 - 0.3, 1.75, ZB - 0.02), P(X1 + 0.3, 1.75, ZB - 0.02), P(X1 + 0.3, 0, ZB - 0.02), P(X0 - 0.3, 0, ZB - 0.02)]
    img, _ = quad(img, hb, (110, 30, 45))
    # tufted pattern
    tm = Mask()
    for i in range(1, 9):
        for j in range(1, 4):
            cx, cy = P(X0 - 0.3 + (X1 - X0 + 0.6) * i / 9, 0.62 + 1.1 * j / 4, ZB - 0.02)
            tm.circle(cx, cy, 3)
    img = over(img, (60, 10, 20), tm.get())
    img, _ = quad(img, [P(X0 - 0.35, 1.8, ZB - 0.02), P(X1 + 0.35, 1.8, ZB - 0.02), P(X1 + 0.35, 1.72, ZB - 0.02), P(X0 - 0.35, 1.72, ZB - 0.02)], (200, 160, 90))
    for (nx0, nx1) in ((0.35, 0.95), (4.15, 4.55)):
        img, _ = box3(img, cam, nx0, nx1, 0, 0.55, ZB - 0.5, ZB - 0.05, (80, 50, 32), shade=(1.0, 0.9, 0.7))
    sheet = full((245, 240, 235))
    folds = fbm(H, W, 60, 4, seed=204, sx=0.6)
    side = sheet * (0.72 + 0.12 * folds[..., None])
    img, _ = quad(img, [P(X0, TOP, Z0), P(X0, TOP, Z1), P(X0, 0.15, Z1), P(X0, 0.12, Z0)], side * 0.85)
    img, _ = quad(img, [P(X0, TOP, Z0), P(X1, TOP, Z0), P(X1, 0.12, Z0), P(X0, 0.12, Z0)], side)
    topc = sheet * (0.88 + 0.12 * folds[..., None])
    img, tmask = quad(img, [P(X0, TOP, Z0), P(X0, TOP, Z1), P(X1, TOP, Z1), P(X1, TOP, Z0)], topc)
    # bed runner (deep red) across the foot
    img, _ = quad(img, [P(X0 - 0.02, TOP + 0.01, Z0 + 0.15), P(X1 + 0.02, TOP + 0.01, Z0 + 0.15), P(X1 + 0.02, TOP + 0.01, Z0 + 0.6), P(X0 - 0.02, TOP + 0.01, Z0 + 0.6)], (140, 25, 40))
    img, _ = quad(img, [P(X0 - 0.02, TOP + 0.01, Z0 + 0.15), P(X0 - 0.02, TOP + 0.01, Z0 + 0.6), P(X0 - 0.02, 0.25, Z0 + 0.6), P(X0 - 0.02, 0.25, Z0 + 0.15)], (110, 18, 30))
    img, _ = quad(img, [P(X0 - 0.02, TOP + 0.01, Z0 + 0.15), P(X1 + 0.02, TOP + 0.01, Z0 + 0.15), P(X1 + 0.02, 0.25, Z0 + 0.15), P(X0 - 0.02, 0.25, Z0 + 0.15)], (125, 22, 35))
    # pillows
    for (px0, px1) in ((1.3, 2.5), (2.6, 3.8)):
        a_, b_ = P(px0, TOP + 0.35, Z1 - 0.15), P(px1, TOP + 0.02, Z1 - 0.5)
        img = lerp(img, sheet * (0.85 + 0.15 * smooth(b_[1], a_[1], y))[..., None], Mask().ellipse((a_[0], a_[1], b_[0], b_[1])).get(1.5))
    # rose-petal heart on the duvet + scattered petals
    pm = Mask(ss=3)
    r = rng0(205)
    hcx, hcz = (X0 + X1) / 2, 5.55
    for t in np.linspace(0, 2 * math.pi, 46, endpoint=False):
        hx_ = 16 * math.sin(t) ** 3
        hz_ = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        X_ = hcx + hx_ / 17 * 0.75
        Z_ = hcz + hz_ / 17 * 0.55
        px, py = P(X_, TOP + 0.01, Z_)
        petal(pm, px + r.normal(0, 2), py + r.normal(0, 1), 0.05 * cam.sc(Z_), r.uniform(0, 6.28))
    for _ in range(40):
        X_, Z_ = r.uniform(X0 + 0.1, X1 - 0.1), r.uniform(Z0 + 0.1, Z1 - 0.6)
        px, py = P(X_, TOP + 0.01, Z_)
        petal(pm, px, py, 0.045 * cam.sc(Z_), r.uniform(0, 6.28))
    for _ in range(25):  # petals on the floor/rug
        X_, Z_ = r.uniform(-0.5, 4.2), r.uniform(2.2, 4.5)
        px, py = P(X_, 0.005, Z_)
        petal(pm, px, py, 0.045 * cam.sc(Z_), r.uniform(0, 6.28))
    pma = pm.get(0.5)
    img = lerp(img, full((190, 20, 40)) * (0.8 + 0.3 * fbm(H, W, 3, 2, seed=206)[..., None]), pma)
    # towel swan on the bed (white)
    sx_, sy_ = P(hcx, TOP + 0.02, hcz)
    s_ = cam.sc(hcz)
    sw = Mask().ellipse((sx_ - 0.16 * s_, sy_ - 0.07 * s_, sx_ + 0.16 * s_, sy_ + 0.03 * s_))
    sw.tapered(bezier((sx_ - 0.1 * s_, sy_ - 0.03 * s_), (sx_ - 0.22 * s_, sy_ - 0.2 * s_), (sx_ - 0.08 * s_, sy_ - 0.28 * s_), n=20), 0.05 * s_, 0.025 * s_)
    img = lerp(img, full((250, 250, 248)), sw.get(0.8))
    # champagne bucket on a side table
    img, _ = box3(img, cam, -1.1, -0.5, 0, 0.6, 3.6, 4.1, (90, 60, 40), shade=(1.0, 0.85, 0.7))
    bcx, bcy = P(-0.8, 0.6, 3.85)
    s3 = cam.sc(3.85)
    img = over(img, (200, 200, 205), Mask().poly([(bcx - 0.1 * s3, bcy), (bcx + 0.1 * s3, bcy), (bcx + 0.12 * s3, bcy - 0.2 * s3), (bcx - 0.12 * s3, bcy - 0.2 * s3)]).get(0.7))
    img = over(img, (20, 50, 30), Mask().poly([(bcx - 0.03 * s3, bcy - 0.18 * s3), (bcx + 0.03 * s3, bcy - 0.18 * s3), (bcx + 0.06 * s3, bcy - 0.42 * s3), (bcx + 0.03 * s3, bcy - 0.48 * s3)]).get(0.7))
    img = over(img, (220, 190, 100), Mask().rect((bcx + 0.025 * s3, bcy - 0.52 * s3, bcx + 0.07 * s3, bcy - 0.44 * s3)).get(0.7))
    for gx in (-0.55, -1.0):
        gx_, gy_ = P(gx, 0.6, 3.7)
        img = screen(img, (230, 235, 255), Mask().poly([(gx_ - 3, gy_), (gx_ + 3, gy_), (gx_ + 2, gy_ - 0.12 * s3), (gx_ + 0.04 * s3, gy_ - 0.2 * s3), (gx_ - 0.04 * s3, gy_ - 0.2 * s3), (gx_ - 2, gy_ - 0.12 * s3)]).get(0.6) * 0.5)
    # ---------------- lighting: dark night ambient + warm candle pools + moonlight
    candles = [(0.5, 0.55, ZB - 0.3, 0.16), (0.8, 0.55, ZB - 0.25, 0.1), (4.3, 0.55, ZB - 0.3, 0.14),
               (0.6, 0.0, 4.0, 0.2), (0.9, 0.0, 3.9, 0.12), (-0.7, 0.6, 3.75, 0.1), (3.9, 0.0, 3.6, 0.16), (4.2, 0.0, 3.8, 0.1),
               (-1.3, 0.0, 6.6, 0.18)]
    lights = [((cx_, cy_ + h_ + 0.05, cz_), 1.0, 1.2) for cx_, cy_, cz_, h_ in candles]
    lt = light_map(R, lights)
    surf = np.clip(R.m_floor + R.m_left + R.m_right + R.m_ceil + R.m_back, 0, 1)
    obj = np.zeros((H, W), np.float32)
    for cx_, cy_, cz_, h_ in candles:
        px, py = P(cx_, cy_ + h_, cz_)
        obj += radial(px, py, 600, power=1.6) * 0.7
    L_ = np.clip(lt * 0.6 * surf + obj * (1 - 0.5 * surf), 0, 1.2) * dim
    dark = img * C((40, 45, 85)) * 0.45
    lit_ = img * C((255, 190, 130)) * 1.05
    view_snap = img.copy()
    img = lerp(dark, lit_, np.clip(L_, 0, 1)[..., None])
    img = lerp(img, view_snap * 0.95, bm * (1 - np.clip(Mask().rect((mid - 7, by0, mid + 7, by1)).get(), 0, 1)) * (y < by1 - 30))
    # moonlight beam on the floor
    beam = Mask().poly([P(BAL[0], 0, ZB), P(BAL[1], 0, ZB), P(BAL[1] + 0.8, 0, 3.2), P(BAL[0] + 0.3, 0, 3.2)]).get(20)
    img = screen(img, (120, 150, 230), beam * R.m_floor * 0.22)
    img = screen(img, (110, 140, 220), radial((bx0 + bx1) / 2, by1, 700, power=2, sy=0.4) * 0.12)
    if door_open:
        dcx, dcy = P(XL, 1.1, (DZ0 + DZ1) / 2)
        img = screen(img, (255, 240, 210), radial(dcx, dcy, 900, power=2.2) * 0.5)
        fl = Mask().poly([P(XL, 0, DZ0), P(XL, 0, DZ1), P(XL + 3.5, 0, DZ1 + 0.4), P(XL + 3.2, 0, DZ0 - 0.6)]).get(25)
        img = screen(img, (255, 235, 200), fl * 0.4)
    for cx_, cy_, cz_, h_ in candles:
        img = candle_s(img, cam, cx_, cy_, cz_, h_, glow=dim)
    img = bloom(img, 0.7, 25, 0.5)
    return img


def hotel_suite_night():
    return hotel_suite(False)


# ====================================================================== corporate helpers
def marble(seed, base=(232, 228, 220), vein=(150, 145, 140), scale=160):
    n = fbm(H, W, scale, 6, seed=seed)
    n2 = fbm(H, W, scale * 0.5, 5, seed=seed + 1)
    v = np.exp(-((np.sin((n * 6 + n2 * 3) * math.pi)) ** 2) / 0.01)
    col = full(base) * (0.94 + 0.08 * n2[..., None])
    return lerp(col, full(vein), np.clip(v * 0.5, 0, 1))


def mullions(img, box, nx, ny, col, wd=6, top_band=None):
    x0, y0, x1, y1 = box
    m = Mask()
    for i in range(nx + 1):
        xx = x0 + (x1 - x0) * i / nx
        m.rect((xx - wd / 2, y0, xx + wd / 2, y1))
    for j in range(ny + 1):
        yy = y0 + (y1 - y0) * j / ny
        m.rect((x0, yy - wd / 2, x1, yy + wd / 2))
    return over(img, col, m.get())


def glass_wall_back(img, cam, R, X0, X1, Y0, Y1, view, nx=6, ny=3, col=(60, 65, 75), wd=8):
    P = cam.P
    a, b = P(X0, Y1, R.ZB), P(X1, Y0, R.ZB)
    m = rect_m(a[0], a[1], b[0], b[1])
    img = lerp(img, view, m)
    img = mullions(img, (a[0], a[1], b[0], b[1]), nx, ny, col, wd)
    return img, m, (a[0], a[1], b[0], b[1])


def side_glass(img, R, side, view, z0, z1, y0, y1, nz=4, col=(60, 65, 75), wd=6, alpha=1.0):
    """Glass on a side wall between z0..z1, y0..y1, showing view (flat image)."""
    cam = R.cam
    P = cam.P
    X = R.XL if side == 'left' else R.XR
    m = Mask().poly([P(X, y1, z1), P(X, y1, z0), P(X, y0, z0), P(X, y0, z1)]).get()
    img = lerp(img, view, m * alpha)
    mm = Mask()
    for k in range(nz + 1):
        z = z0 + (z1 - z0) * k / nz
        mm.line([P(X, y1, z), P(X, y0, z)], max(1.5, wd * 3 / z))
    mm.line([P(X, y1, z0), P(X, y1, z1)], 4).line([P(X, y0, z0), P(X, y0, z1)], 4)
    img = over(img, col, mm.get())
    return img, m


def office_chair_back(img, cam, X, Z, col=(30, 30, 34), s=1.0, facing=-1):
    """Simple office chair seen from behind/front: backrest + seat + base."""
    P = cam.P
    sc = cam.sc(Z)
    cx, cy = P(X, 0, Z)
    # base star + gas lift
    img = over(img, (20, 20, 22), Mask().ellipse((cx - 0.3 * sc * s, cy - 0.04 * sc, cx + 0.3 * sc * s, cy + 0.04 * sc)).get(1) * 0.6)
    img = over(img, (40, 40, 44), Mask().rect((cx - 0.025 * sc, cy - 0.45 * sc * s, cx + 0.025 * sc, cy)).get(0.6))
    for dx in (-0.28, -0.1, 0.1, 0.28):
        img = over(img, (30, 30, 32), Mask().line([(cx, cy - 0.05 * sc), (cx + dx * sc * s, cy)], 0.03 * sc).get(0.6))
    # seat
    sy = cy - 0.47 * sc * s
    img = over(img, col, Mask().ellipse((cx - 0.26 * sc * s, sy - 0.05 * sc, cx + 0.26 * sc * s, sy + 0.05 * sc)).get(0.8))
    # backrest
    bm = Mask()
    bm.poly(bezier((cx - 0.24 * sc * s, sy - 0.05 * sc), (cx - 0.3 * sc * s, sy - 0.45 * sc * s), (cx - 0.2 * sc * s, sy - 0.65 * sc * s), n=16) +
            bezier((cx + 0.2 * sc * s, sy - 0.65 * sc * s), (cx + 0.3 * sc * s, sy - 0.45 * sc * s), (cx + 0.24 * sc * s, sy - 0.05 * sc), n=16))
    x, y = grid()
    bc = full(col) * (0.85 + 0.3 * smooth(cx - 0.25 * sc, cx + 0.25 * sc, x) * smooth(sy, sy - 0.6 * sc, y))[..., None]
    img = lerp(img, bc, bm.get(0.8))
    return img


_chart_cache = {}


def chart(w, h, seed, kind='candle', title=None):
    k = (w, h, seed, kind, title)
    if k not in _chart_cache:
        _chart_cache[k] = chart_img(w, h, seed, kind, title)
    return _chart_cache[k]


# ====================================================================== office lobby
def office_lobby():
    x, y = grid()
    cam = Cam(F=820.0, VX=960.0, VY=600.0, EYE=1.6)
    P = cam.P
    XL, XR, CEIL, ZB = -10.0, 10.0, 10.0, 24.0
    R = Room(cam, XL, XR, CEIL, ZB)
    img = full((200, 195, 185))
    # walls: warm travertine
    trav = marble(301, (215, 200, 178), (180, 165, 140), 120)
    for name, dk in (('left', 0.92), ('right', 0.86), ('back', 1.0)):
        img = R.paint(img, name, trav * dk)
    # stone joints on side walls
    for side, X in (('left', XL), ('right', XR)):
        jm = Mask()
        for yy in np.arange(0, CEIL, 1.2):
            jm.line([P(X, yy, 1.0), P(X, yy, ZB)], 2)
        for zz in np.arange(2, ZB, 2.4):
            jm.line([P(X, 0, zz), P(X, CEIL, zz)], 1.5)
        img = lerp(img, img * 0.75, jm.get(0.8) * getattr(R, 'm_' + side))
    # ceiling: coffered with downlight grid
    CX_, _, CZ = R.ceil
    rnd, gr = tiles(CX_ + 50, CZ, 2.0, 2.0, 0.08)
    ceil = lerp(full((235, 232, 226)), full((205, 200, 192)), gr)
    img = lerp(img, ceil, R.m_ceil)
    # back wall: full glass curtain wall
    view = skyline((0, 0, W, P(0, 0, ZB)[1]), P(0, 0, ZB)[1] - 10, False, seed=302)
    # plaza trees outside
    tm = Mask()
    r = rng0(303)
    gy = P(0, 0, ZB + 8)[1]
    for i in range(14):
        tx = r.uniform(300, 1650)
        tw = r.uniform(30, 60)
        tm.ellipse((tx - tw, gy - tw * 2.6, tx + tw, gy - tw * 0.6)).rect((tx - 3, gy - tw, tx + 3, gy))
    view = over(view, (70, 110, 70), tm.get(1) * 0.85)
    view = lerp(view, full((185, 185, 180)), (y > gy).astype(np.float32))
    img, gm, gbox = glass_wall_back(img, cam, R, -7.5, 7.5, 0, 8.2, view, nx=8, ny=4, col=(70, 72, 80), wd=7)
    img = screen(img, (255, 255, 255), gm * 0.12)
    # side wall glass at the right (towards the back)
    img, _ = side_glass(img, R, 'right', view * 0.95, 13, ZB, 0, 8.2, nz=4)
    # floor: polished marble, big tiles
    FX_, _, FZ = R.floor
    rnd, gr = tiles(FX_ + 50, FZ, 1.2, 1.2, 0.01)
    fl = marble(304, (238, 234, 226), (170, 160, 150), 90)
    fl = lerp(fl, fl * (0.94 + 0.06 * rnd[..., None]), 1.0)
    # inlay band
    band = ((np.abs(FX_) < 1.0) & (np.abs(FX_) > 0.85)).astype(np.float32)
    fl = lerp(fl, full((60, 55, 55)), band)
    fl = lerp(fl, fl * 0.8, gr)
    img = lerp(img, fl, R.m_floor)
    # columns
    for Xc in (-6.0, 6.0):
        for Zc in (9.0, 17.0):
            img, _ = box3(img, cam, Xc - 0.5, Xc + 0.5, 0, CEIL, Zc, Zc + 1.0, (210, 205, 198), shade=(1, 0.95, 0.78))
    # reception desk (left) + logo wall
    lw = [P(XL, 6.0, 9.0), P(XL, 6.0, 15.0), P(XL, 1.4, 15.0), P(XL, 1.4, 9.0)]
    img, _ = quad(img, lw, (60, 50, 45))
    logo = sign_img('鼎峰资本', 600, 160, None, (220, 190, 120), fill=0.8)
    img = paste_quad(img, logo, [P(XL, 4.8, 9.8), P(XL, 4.8, 14.2), P(XL, 3.2, 14.2), P(XL, 3.2, 9.8)])
    sub = sign_img('DINGFENG CAPITAL', 700, 70, None, (200, 180, 130), fill=0.7)
    img = paste_quad(img, sub, [P(XL, 3.0, 10.4), P(XL, 3.0, 13.6), P(XL, 2.6, 13.6), P(XL, 2.6, 10.4)])
    img, _ = box3(img, cam, -8.2, -5.8, 0, 1.15, 10.0, 14.0, (235, 232, 226), shade=(1.0, 0.95, 0.8), top_col=C((60, 50, 45)))
    img = over(img, (200, 170, 100), Mask().line([P(-5.8, 1.0, 10.0), P(-5.8, 1.0, 14.0)], 3).get())
    # receptionist silhouette-ish head + monitor
    hx, hy = P(-7.0, 1.45, 12.5)
    s_ = cam.sc(12.5)
    img = over(img, (40, 40, 45), Mask().ellipse((hx - 0.11 * s_, hy - 0.14 * s_, hx + 0.11 * s_, hy + 0.12 * s_)).get(1))
    img = over(img, (230, 230, 235), Mask().poly([(hx - 0.3 * s_, hy + 0.12 * s_), (hx + 0.3 * s_, hy + 0.12 * s_), (hx + 0.35 * s_, hy + 0.45 * s_), (hx - 0.35 * s_, hy + 0.45 * s_)]).get(1))
    img = over(img, (30, 30, 34), Mask().rect((*P(-6.6, 1.55, 11.3), *P(-6.0, 1.15, 11.3))).get())
    # turnstiles (security gates) across the lobby
    ZT = 13.0
    for k, Xc in enumerate(np.arange(-4.2, 4.3, 1.2)):
        img, _ = box3(img, cam, Xc - 0.12, Xc + 0.12, 0, 1.0, ZT, ZT + 1.5, (200, 202, 208), shade=(1.05, 0.9, 0.7), top_col=C((60, 62, 70)))
        # status lights
        lx, ly = P(Xc, 1.0, ZT + 0.1)
        img = screen(img, (60, 255, 140) if k % 3 else (255, 60, 60), radial(lx, ly, 14, power=1.2))
        # glass flaps
        if Xc < 4.0:
            img, _ = quad(img, [P(Xc + 0.12, 1.25, ZT + 0.5), P(Xc + 0.55, 1.25, ZT + 0.5), P(Xc + 0.55, 0.45, ZT + 0.5), P(Xc + 0.12, 0.45, ZT + 0.5)], (190, 225, 240), alpha=0.35)
            img = over(img, (230, 250, 255), Mask().line([P(Xc + 0.12, 1.25, ZT + 0.5), P(Xc + 0.55, 1.25, ZT + 0.5)], 2).get())
    # glass barrier panels to the sides of the turnstiles
    for (xa, xb) in ((-9.9, -4.4), (4.4, 9.9)):
        img, _ = quad(img, [P(xa, 1.1, ZT + 0.75), P(xb, 1.1, ZT + 0.75), P(xb, 0, ZT + 0.75), P(xa, 0, ZT + 0.75)], (190, 220, 235), alpha=0.25)
        img = over(img, (180, 180, 185), Mask().line([P(xa, 1.1, ZT + 0.75), P(xb, 1.1, ZT + 0.75)], 3).get())
    # potted trees
    for (Xc, Zc) in ((-3.0, 19.5), (3.0, 19.5), (8.5, 7.0)):
        img, _ = box3(img, cam, Xc - 0.4, Xc + 0.4, 0, 0.7, Zc - 0.4, Zc + 0.4, (60, 60, 64), shade=(1, 0.9, 0.7))
        tx, ty = P(Xc, 0.7, Zc)
        s_ = cam.sc(Zc)
        img = over(img, (70, 50, 35), Mask().rect((tx - 0.04 * s_, ty - 1.2 * s_, tx + 0.04 * s_, ty)).get())
        fm = Mask()
        rr = rng0(int(Zc * 10 + Xc))
        for _ in range(18):
            fm.circle(tx + rr.normal(0, 0.35) * s_, ty - (1.6 + rr.normal(0, 0.3)) * s_, rr.uniform(0.15, 0.3) * s_)
        fa = fm.get(1)
        img = lerp(img, full((50, 105, 55)) * (0.75 + 0.4 * fbm(H, W, 8, 3, seed=305)[..., None]), fa)
    # lighting: daylight from the glass, warm downlights
    img = screen(img, (255, 250, 240), radial(960, gbox[3], 1400, power=2, sy=0.45) * 0.25 * R.m_floor)
    for Xc in np.arange(-8, 9, 4.0):
        for Zc in np.arange(3, ZB, 4.0):
            img = downlight(img, cam, Xc, CEIL - 0.01, Zc, r=0.15, glow=0.6)
    # floor reflection of the glass wall + columns
    img = reflect_down(img, R.m_floor, gbox[3], strength=0.35, blur_r=5, fade=420)
    img = bloom(img, 0.85, 30, 0.4)
    return img


# ====================================================================== IB executive office at night
def ib_office_night():
    x, y = grid()
    cam = Cam(F=900.0, VX=900.0, VY=470.0, EYE=1.3)
    P = cam.P
    XL, XR, CEIL, ZB = -3.6, 4.2, 3.0, 6.0
    R = Room(cam, XL, XR, CEIL, ZB)
    img = full((40, 38, 40))
    # walnut left wall with shelf, dark ceiling, carpet
    wl = full((70, 48, 34)) * (0.85 + 0.2 * fbm(H, W, 8, 3, seed=401, sy=8)[..., None])
    img = R.paint(img, 'left', wl)
    img = R.paint(img, 'ceil', full((32, 32, 38)))
    FX_, _, FZ = R.floor
    carpet = full((48, 48, 55)) * (0.9 + 0.15 * fbm(H, W, 3, 2, seed=402)[..., None])
    img = lerp(img, carpet, R.m_floor)
    # back + right walls: floor-to-ceiling glass with night skyline
    hz = cam.VY + 60
    view = skyline((0, 0, W, H), hz, True, seed=403)
    a, b = P(XL, CEIL, ZB), P(XR, 0, ZB)
    img = lerp(img, view, R.m_back)
    img = mullions(img, (a[0], a[1], b[0], b[1]), 4, 1, (25, 25, 30), 9)
    view2 = skyline((0, 0, W, H), hz, True, seed=404) * 0.85
    img = lerp(img, view2, R.m_right)
    mm = Mask()
    for z in (1.5, 3.0, 4.5):
        mm.line([P(XR, CEIL, z), P(XR, 0, z)], 10 * 3 / z)
    img = over(img, (25, 25, 30), mm.get() * R.m_right)
    # window sill line + reflections in glass
    img = over(img, (20, 20, 24), Mask().line([P(XL, 0.05, ZB), P(XR, 0.05, ZB)], 8).get())
    img = over(img, (20, 20, 24), Mask().line([P(XR, 0.05, ZB), P(XR, 0.05, 0.5)], 8).get())
    # bookshelf on left wall
    for yy in (0.9, 1.4, 1.9, 2.4):
        img = over(img, (45, 30, 22), Mask().poly([P(XL, yy, 2.0), P(XL, yy, 4.5), P(XL + 0.3, yy, 4.5), P(XL + 0.3, yy, 2.0)]).get())
        r = rng0(int(yy * 10))
        z = 2.1
        while z < 4.4:
            bw = r.uniform(0.04, 0.09)
            bh = r.uniform(0.25, 0.4)
            col = [(120, 30, 30), (30, 50, 90), (180, 160, 120), (40, 70, 50), (20, 20, 25)][r.integers(0, 5)]
            img, _ = quad(img, [P(XL + 0.02, yy + bh, z), P(XL + 0.02, yy + bh, z + bw), P(XL + 0.02, yy, z + bw), P(XL + 0.02, yy, z)], col)
            z += bw + (r.uniform(0.2, 0.4) if r.random() < 0.08 else 0.005)
    # abstract art frame on left wall near
    img, _ = quad(img, [P(XL, 2.3, 4.8), P(XL, 2.3, 5.7), P(XL, 1.2, 5.7), P(XL, 1.2, 4.8)], (200, 190, 175))
    img, _ = quad(img, [P(XL, 2.15, 4.9), P(XL, 2.15, 5.6), P(XL, 1.35, 5.6), P(XL, 1.35, 4.9)], (180, 40, 40))
    # desk (glossy black slab on steel legs)
    DX0, DX1, DZ0, DZ1, DT = -1.5, 1.7, 2.7, 3.5, 0.76
    for Xl in (DX0 + 0.08, DX1 - 0.08):
        for Zl in (DZ1 - 0.08, DZ0 + 0.08):
            img, _ = quad(img, [P(Xl - 0.03, DT - 0.05, Zl), P(Xl + 0.03, DT - 0.05, Zl), P(Xl + 0.03, 0, Zl), P(Xl - 0.03, 0, Zl)], (120, 122, 128) if Zl < DZ1 - 0.1 else (70, 72, 78))
    img, _ = box3(img, cam, DX0, DX1, DT - 0.05, DT, DZ0, DZ1, (22, 20, 22), shade=(1.0, 1.0, 1.0), top_col=C((30, 30, 36)))
    img = screen(img, (170, 185, 230), Mask().line([P(DX0, DT, DZ0), P(DX1, DT, DZ0)], 2).get() * 0.7)
    # monitors (facing the camera), slightly arced
    mons = [(-1.0, 3.3, 0.3), (0.1, 3.4, 0.0), (1.2, 3.3, -0.3)]
    for i, (Xm, Zm, yaw) in enumerate(mons):
        pts = rect3(cam, Xm, DT + 0.17, Zm, 1.0, 0.6, yaw)
        src = chart(620, 370, 410 + i, ['candle', 'candle', 'line'][i], ['沪深300  4,012.6 ▲', 'HSI  19,850 ▼', None][i])
        img, _ = screen_quad(img, pts, src, glow=0.35)
        bx, by = P(Xm, DT, Zm)
        img = over(img, (20, 20, 22), Mask().rect((bx - 6, by - 0.17 * cam.sc(Zm), bx + 6, by)).get())
        img = over(img, (20, 20, 22), Mask().ellipse((bx - 0.12 * cam.sc(Zm), by - 6, bx + 0.12 * cam.sc(Zm), by + 4)).get())
    # desk props: lamp, whisky glass, nameplate, phone
    lx, ly = P(1.55, DT, 2.85)
    s_ = cam.sc(2.85)
    img = screen(img, (255, 200, 130), radial(lx - 0.25 * s_, ly - 0.05 * s_, 0.5 * s_, power=1.8, sy=0.45) * 0.5)
    gx, gy = P(-1.25, DT, 2.85)
    img = lerp(img, img * 0.6 + C((140, 80, 20)) * 0.5, rect_m(gx - 0.035 * s_, gy - 0.08 * s_, gx + 0.035 * s_, gy, 0.6))
    img = screen(img, (255, 255, 255), rect_m(gx - 0.035 * s_, gy - 0.09 * s_, gx + 0.035 * s_, gy, 0.6) * 0.18)
    npx, npy = P(0.75, DT, 2.8)
    img = over(img, (190, 160, 90), Mask().poly([(npx - 0.18 * s_, npy), (npx + 0.18 * s_, npy), (npx + 0.17 * s_, npy - 0.06 * s_), (npx - 0.17 * s_, npy - 0.06 * s_)]).get(0.6))
    # lighting: dark room, cool monitor + city glow
    img = img * np.where(R.m_back[..., None] + R.m_right[..., None] > 0.5, 1.0, 0.85)
    for (Xm, Zm, yaw) in mons:
        mx, my = P(Xm, DT + 0.4, Zm)
        img = screen(img, (80, 130, 255), radial(mx, my + 200, 700, power=2.2) * 0.18 * (1 - R.m_back))
    img = screen(img, (60, 70, 140), smooth(cam.VY, H, y) * R.m_floor * 0.1)
    # downlights (dimmed)
    for Xc in (-2.0, 0.0, 2.0):
        img = downlight(img, cam, Xc, CEIL - 0.01, 4.5, r=0.06, col=(255, 220, 170), glow=0.5)
    # executive chair (high back, black leather, back to camera)
    cx, cy = P(0.1, 0, 1.75)
    s_ = cam.sc(1.75)
    x, y = grid()
    leather = full((26, 24, 26))
    bm = Mask()
    top = cy - 1.25 * s_
    bm.poly(bezier((cx - 0.27 * s_, cy - 0.52 * s_), (cx - 0.33 * s_, cy - 0.95 * s_), (cx - 0.24 * s_, top), n=20) +
            bezier((cx - 0.24 * s_, top), (cx, top - 0.06 * s_), (cx + 0.24 * s_, top), n=12) +
            bezier((cx + 0.24 * s_, top), (cx + 0.33 * s_, cy - 0.95 * s_), (cx + 0.27 * s_, cy - 0.52 * s_), n=20))
    bma = bm.get(1)
    shade_ = 0.75 + 0.6 * smooth(cx - 0.3 * s_, cx + 0.3 * s_, x) * smooth(cy - 0.5 * s_, top, y)
    lc = leather * shade_[..., None]
    # horizontal stitched channels
    ch = np.abs(((y - top) / (0.16 * s_)) % 1 - 0.5) < 0.05
    lc = lerp(lc, lc * 0.5, ch.astype(np.float32) * 0.9)
    img = lerp(img, lc, bma)
    # monitor-blue rim on the chair edge + city glow
    edge = np.clip(bma - ndimage.grey_erosion(bma, size=(9, 9)), 0, 1)
    img = screen(img, (110, 150, 255), edge * 0.35)
    # armrests
    for sd in (-1, 1):
        ax0 = cx + sd * 0.27 * s_
        img = over(img, (20, 20, 22), Mask().poly([(ax0, cy - 0.62 * s_), (ax0 + sd * 0.1 * s_, cy - 0.66 * s_), (ax0 + sd * 0.1 * s_, cy - 0.58 * s_), (ax0, cy - 0.5 * s_)]).get(0.8))
    img = over(img, (35, 35, 38), Mask().rect((cx - 0.03 * s_, cy - 0.52 * s_, cx + 0.03 * s_, cy - 0.05 * s_)).get())
    for dx in (-0.34, -0.14, 0.14, 0.34):
        img = over(img, (40, 40, 44), Mask().line([(cx, cy - 0.08 * s_), (cx + dx * s_, cy - 0.01 * s_)], 0.035 * s_).get())
        img = over(img, (15, 15, 15), Mask().circle(cx + dx * s_, cy, 0.03 * s_).get())
    img = bloom(img, 0.7, 20, 0.5)
    return img


# ====================================================================== trading floor (day)
def ib_trading_floor():
    x, y = grid()
    cam = Cam(F=900.0, VX=960.0, VY=430.0, EYE=1.7)
    P = cam.P
    XL, XR, CEIL, ZB = -9.0, 9.0, 3.4, 34.0
    R = Room(cam, XL, XR, CEIL, ZB)
    img = full((220, 222, 226))
    # ceiling: light panels grid
    CX_, _, CZ = R.ceil
    rnd, gr = tiles(CX_ + 50, CZ, 1.2, 1.2, 0.03)
    panel = ((np.abs((CX_ + 0.6) % 2.4 - 1.2) < 0.3) & (np.abs(CZ % 3.0 - 1.5) < 0.6)).astype(np.float32)
    ceil = lerp(full((228, 230, 232)), full((200, 202, 206)), gr)
    ceil = lerp(ceil, full((255, 255, 252)), panel)
    img = lerp(img, ceil, R.m_ceil)
    # floor: grey carpet tiles
    FX_, _, FZ = R.floor
    rnd, gr = tiles(FX_ + 50, FZ, 0.6, 0.6, 0.006)
    fl = lerp(full((110, 115, 125)), full((125, 130, 140)), rnd[..., None])
    fl *= (0.92 + 0.1 * fbm(H, W, 3, 2, seed=501)[..., None])
    img = lerp(img, fl, R.m_floor)
    # back + right: windows with daytime skyline; left: glass meeting rooms
    view = skyline((0, 0, W, H), cam.VY + 30, False, seed=502)
    img = lerp(img, view, R.m_back)
    a, b = P(XL, CEIL, ZB), P(XR, 0, ZB)
    img = mullions(img, (a[0], a[1], b[0], b[1]), 10, 1, (90, 95, 105), 3)
    img = lerp(img, view * 0.95, R.m_right)
    mm = Mask()
    for z in np.arange(3, ZB, 3.0):
        mm.line([P(XR, CEIL, z), P(XR, 0, z)], 8 * 3 / z + 1)
    img = over(img, (90, 95, 105), mm.get() * R.m_right)
    # left: frosted glass meeting-room walls
    lw = lerp(full((200, 210, 218)), full((235, 240, 244)), smooth(0.9, 1.1, R.left[1]) * (1 - smooth(1.7, 1.9, R.left[1])))
    img = lerp(img, lw, R.m_left)
    mm = Mask()
    for z in np.arange(2, ZB, 4.0):
        mm.line([P(XL, CEIL, z), P(XL, 0, z)], 8 * 3 / z + 1)
    img = over(img, (120, 125, 135), mm.get() * R.m_left)
    # LED ticker band along the top of the back wall
    tk_a, tk_b = P(XL, CEIL - 0.05, ZB - 0.1), P(XR, CEIL - 0.45, ZB - 0.1)
    tw, th = int(tk_b[0] - tk_a[0]), int(tk_b[1] - tk_a[1])
    tick = Image.new('RGBA', (tw * 2, th * 2), (10, 10, 14, 255))
    d = ImageDraw.Draw(tick)
    f = cfont(th * 1.4)
    xx = 10
    for name, val, up in (('上证指数', '3,312.45', True), ('深证成指', '10,488.2', False), ('恒生指数', '19,850.7', False),
                          ('沪深300', '4,012.6', True), ('创业板', '2,105.9', True), ('科创50', '985.3', False)):
        col = (255, 70, 70) if up else (60, 230, 120)
        d.text((xx, th * 0.2), name, font=f, fill=(255, 210, 80))
        xx += d.textlength(name, font=f) + 12
        t2 = val + (' ▲' if up else ' ▼')
        d.text((xx, th * 0.2), t2, font=f, fill=col)
        xx += d.textlength(t2, font=f) + 50
    tick = tick.resize((tw, th), Image.LANCZOS)
    img, _ = paste_at(img, tick, tk_a[0], tk_a[1])
    # desk rows with monitors facing the camera
    lay_far = Layer(ss=2)
    rows = [3.2, 5.6, 8.0, 10.4, 13.0, 15.6, 18.5, 21.5, 24.5, 27.5]
    r = rng0(503)
    for zi in reversed(range(len(rows))):
        Zr = rows[zi]
        for (xa, xb) in ((-8.2, -0.9), (0.9, 8.2)):
            # desk top + front panel
            img, _ = quad(img, [P(xa, 0.75, Zr), P(xb, 0.75, Zr), P(xb, 0.75, Zr + 0.8), P(xa, 0.75, Zr + 0.8)], (235, 236, 238))
            img, _ = quad(img, [P(xa, 0.75, Zr), P(xb, 0.75, Zr), P(xb, 0.0, Zr), P(xa, 0.0, Zr)], (175, 180, 188))
            img = over(img, (120, 125, 135), Mask().line([P(xa, 0.74, Zr), P(xb, 0.74, Zr)], max(1, 6 / Zr)).get())
            # monitors: 2 tiers per seat
            nseat = int((xb - xa) / 1.6)
            for si in range(nseat):
                sx = xa + (si + 0.5) * (xb - xa) / nseat
                for (dx, ty_, ww, hh) in ((-0.5, 0.0, 0.5, 0.32), (0.0, 0.0, 0.5, 0.32), (0.5, 0.0, 0.5, 0.32),
                                          (-0.25, 0.36, 0.5, 0.32), (0.25, 0.36, 0.5, 0.32)):
                    Zm = Zr + 0.55
                    pts = rect3(cam, sx + dx, 0.95 + ty_, Zm, ww - 0.03, hh)
                    if Zr < 9:
                        kind = ['candle', 'line', 'table', 'candle'][(si + int(dx * 4) + zi) % 4]
                        pw = int(abs(pts[1][0] - pts[0][0]))
                        ph = int(abs(pts[3][1] - pts[0][1]))
                        img, _ = screen_quad(img, pts, chart(max(40, pw), max(24, ph), (zi * 7 + si * 3 + int(dx * 8)) % 9, kind), glow=0.0)
                    else:
                        lay_far.poly(pts, (16, 18, 24))
                        cxm = (pts[0][0] + pts[1][0]) / 2
                        cym = (pts[0][1] + pts[3][1]) / 2
                        ww_ = (pts[1][0] - pts[0][0]) * 0.4
                        hh_ = (pts[3][1] - pts[0][1]) * 0.3
                        lay_far.rect((cxm - ww_, cym - hh_, cxm + ww_, cym + hh_), [(40, 90, 160), (160, 50, 50), (40, 140, 90)][r.integers(0, 3)])
                # stand
                bx, by = P(sx, 0.75, Zr + 0.6)
                img = over(img, (60, 62, 68), Mask().rect((bx - 3, by - 0.22 * cam.sc(Zr), bx + 3, by)).get()) if Zr < 9 else img
            if zi == 0 or Zr >= 9:
                pass
        if Zr >= 9 and zi == 4:
            img = lay_far.comp(img)
            lay_far = Layer(ss=2)
    img = lay_far.comp(img)
    # chairs in the aisle-facing rows (empty-ish floor feel): a few chairs in front of the nearest rows
    for Xc in (-6.2, -3.0, 3.8, 6.6):
        img = office_chair_back(img, cam, Xc, 2.6, col=(40, 42, 48))
    # daylight wash from the windows
    img = screen(img, (255, 252, 240), radial(1800, 400, 1500, power=2) * 0.2)
    img = bloom(img, 0.9, 25, 0.3)
    return img


# ====================================================================== glass meeting room
def slide_img(w, h):
    S = 2
    im = Image.new('RGB', (w * S, h * S), (248, 249, 252))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w * S, int(h * S * 0.17)), fill=(18, 40, 90))
    f = cfont(h * S * 0.085)
    d.text((w * S * 0.04, h * S * 0.035), '项目尽调 — 阶段汇报', font=f, fill=(255, 255, 255))
    f2 = cfont(h * S * 0.04)
    d.text((w * S * 0.04, h * S * 0.2), 'Project Aurora  |  Due Diligence  Q3', font=f2, fill=(90, 100, 120))
    # bar chart
    x0, y0, x1, y1 = w * S * 0.08, h * S * 0.3, w * S * 0.6, h * S * 0.88
    d.line([(x0, y1), (x1, y1)], fill=(120, 120, 130), width=S * 2)
    d.line([(x0, y0), (x0, y1)], fill=(120, 120, 130), width=S * 2)
    vals = [0.45, 0.62, 0.55, 0.8, 0.95]
    for i, v in enumerate(vals):
        bx = x0 + (x1 - x0) * (i + 0.25) / len(vals)
        bw = (x1 - x0) / len(vals) * 0.5
        d.rectangle((bx, y1 - (y1 - y0) * v, bx + bw, y1), fill=(30, 90, 200) if i < 4 else (220, 60, 60))
        d.text((bx, y1 + S * 4), '%dQ' % (i + 1), font=f2, fill=(90, 90, 100))
    # bullet points
    f3 = cfont(h * S * 0.045)
    for i, t in enumerate(['营收增速 +32%', '现金流 风险可控', '关联交易 待核查', '估值区间 18-22x']):
        yy = h * S * (0.36 + i * 0.12)
        d.ellipse((w * S * 0.66, yy + 6 * S, w * S * 0.66 + 10 * S, yy + 16 * S), fill=(30, 90, 200) if i != 2 else (220, 60, 60))
        d.text((w * S * 0.69, yy), t, font=f3, fill=(40, 40, 50) if i != 2 else (200, 40, 40))
    d.text((w * S * 0.86, h * S * 0.92), 'CONFIDENTIAL', font=cfont(h * S * 0.03), fill=(200, 60, 60))
    return im.resize((w, h), Image.LANCZOS)


def meeting_room():
    x, y = grid()
    cam = Cam(F=860.0, VX=820.0, VY=470.0, EYE=1.55)
    P = cam.P
    XL, XR, CEIL, ZB = -3.0, 3.6, 3.0, 9.0
    R = Room(cam, XL, XR, CEIL, ZB)
    img = full((230, 230, 228))
    img = R.paint(img, 'back', full((225, 222, 216)) * (0.95 + 0.05 * fbm(H, W, 100, 3, seed=601)[..., None]))
    img = R.paint(img, 'ceil', full((238, 238, 236)))
    # wood slat accent on the back wall
    BX_, BY_, _ = R.back
    slat = (np.abs((BX_ * 12) % 1 - 0.5) < 0.12).astype(np.float32)
    img = lerp(img, full((150, 110, 75)), R.m_back * 0.0 + R.m_back * slat * 0.0)
    img = lerp(img, full((165, 125, 85)) * (0.85 + 0.2 * slat[..., None]), R.m_back * (np.abs(BX_) > 2.2))
    # floor: dark carpet
    FX_, _, FZ = R.floor
    rnd, gr = tiles(FX_ + 50, FZ, 0.5, 0.5, 0.005)
    fl = lerp(full((60, 62, 70)), full((72, 74, 82)), rnd[..., None])
    img = lerp(img, fl, R.m_floor)
    # right: floor-to-ceiling glass to the city (day)
    view = skyline((0, 0, W, H), cam.VY + 60, False, seed=602)
    img = lerp(img, view, R.m_right)
    mm = Mask()
    for z in np.arange(1.0, ZB, 2.0):
        mm.line([P(XR, CEIL, z), P(XR, 0, z)], 10 * 2 / z + 1)
    img = over(img, (80, 85, 95), mm.get() * R.m_right)
    img = screen(img, (255, 255, 255), R.m_right * 0.08)
    # left: glass partition with frosted band to corridor
    cor = full((200, 205, 210)) * (0.9 + 0.1 * smooth(0, 3, R.left[1])[..., None])
    img = lerp(img, cor, R.m_left)
    band = ((R.left[1] > 1.0) & (R.left[1] < 1.6)).astype(np.float32)
    img = lerp(img, full((240, 243, 246)), band * R.m_left * 0.85)
    mm = Mask()
    for z in np.arange(1.0, ZB, 2.4):
        mm.line([P(XL, CEIL, z), P(XL, 0, z)], 8 * 2 / z + 1)
    img = over(img, (150, 155, 165), mm.get() * R.m_left)
    # wall screen with slide
    sa, sb = P(-1.6, 2.55, ZB - 0.02), P(1.6, 0.75, ZB - 0.02)
    img = over(img, (20, 20, 22), rect_m(sa[0] - 8, sa[1] - 8, sb[0] + 8, sb[1] + 8))
    sl = slide_img(int(sb[0] - sa[0]), int(sb[1] - sa[1]))
    img, _ = paste_at(img, sl.convert('RGBA'), sa[0], sa[1])
    img = screen(img, (200, 220, 255), radial((sa[0] + sb[0]) / 2, (sa[1] + sb[1]) / 2, 600, power=2) * 0.12)
    # credenza under the screen
    img, _ = box3(img, cam, -2.0, 2.0, 0, 0.55, ZB - 0.45, ZB - 0.02, (120, 85, 55), shade=(1.0, 0.92, 0.75))
    # long table
    TX0, TX1, TZ0, TZ1, TT = -1.0, 1.0, 2.6, 7.8, 0.75
    img, _ = box3(img, cam, TX0, TX1, TT - 0.06, TT, TZ0, TZ1, (110, 75, 50), shade=(1.0, 0.85, 0.7), top_col=None)
    # table top gloss reflection
    tm = Mask().poly([P(TX0, TT, TZ0), P(TX1, TT, TZ0), P(TX1, TT, TZ1), P(TX0, TT, TZ1)]).get()
    img = screen(img, (255, 255, 255), tm * smooth(P(0, TT, TZ1)[1], P(0, TT, TZ0)[1], y) * 0.15)
    img, _ = quad(img, [P(-0.12, TT - 0.06, TZ0 + 0.8), P(0.12, TT - 0.06, TZ0 + 0.8), P(0.12, 0, TZ0 + 0.8), P(-0.12, 0, TZ0 + 0.8)], (45, 45, 50))
    img = lerp(img, img * 0.6, Mask().poly([P(TX0, 0, TZ0 + 0.3), P(TX1, 0, TZ0 + 0.3), P(TX1, 0, TZ1), P(TX0, 0, TZ1)]).get(15))
    # chairs both sides (far ones first)
    for Zc in np.arange(7.2, 2.6, -1.15):
        for Xc in (-1.45, 1.45):
            img = office_chair_back(img, cam, Xc, Zc, col=(35, 36, 40), s=0.9)
    # items on table: laptops, water bottles, folders
    for (Xc, Zc) in ((-0.55, 3.5), (0.6, 4.8), (-0.6, 6.0)):
        img, _ = quad(img, [P(Xc - 0.18, TT + 0.005, Zc - 0.12), P(Xc + 0.18, TT + 0.005, Zc - 0.12), P(Xc + 0.18, TT + 0.005, Zc + 0.12), P(Xc - 0.18, TT + 0.005, Zc + 0.12)], (190, 192, 198))
        img, _ = quad(img, [P(Xc - 0.18, TT + 0.005, Zc + 0.12), P(Xc + 0.18, TT + 0.005, Zc + 0.12), P(Xc + 0.18, TT + 0.24, Zc + 0.16), P(Xc - 0.18, TT + 0.24, Zc + 0.16)], (60, 62, 70))
    for (Xc, Zc) in ((0.4, 3.2), (-0.3, 4.3), (0.5, 6.4)):
        bx, by = P(Xc, TT, Zc)
        s_ = cam.sc(Zc)
        img = lerp(img, img * 0.7 + C((60, 120, 200)) * 0.3, rect_m(bx - 0.03 * s_, by - 0.2 * s_, bx + 0.03 * s_, by, 0.6))
        img = over(img, (240, 240, 245), rect_m(bx - 0.03 * s_, by - 0.23 * s_, bx + 0.03 * s_, by - 0.2 * s_, 0.6))
    # ceiling linear lights
    for Xc in (-0.6, 0.6):
        img, _ = quad(img, [P(Xc - 0.04, CEIL - 0.01, 2.0), P(Xc + 0.04, CEIL - 0.01, 2.0), P(Xc + 0.04, CEIL - 0.01, 8.0), P(Xc - 0.04, CEIL - 0.01, 8.0)], (255, 255, 250))
    img = screen(img, (255, 255, 250), radial(*P(0, 0.75, 5.0), 700, power=2, sy=0.4) * 0.15)
    img = screen(img, (255, 250, 235), radial(W, 300, 1300, power=2) * 0.2)
    img = bloom(img, 0.92, 25, 0.3)
    return img


# ====================================================================== elevator
def brushed(seed, base=(175, 178, 182), vertical=True):
    n = fbm(H, W, 40, 4, seed=seed, sx=0.03 if vertical else 30, sy=30 if vertical else 0.03)
    return full(base) * (0.9 + 0.18 * n[..., None])


def elevator():
    x, y = grid()
    cam = Cam(F=700.0, VX=960.0, VY=420.0, EYE=1.55)
    P = cam.P
    XL, XR, CEIL, ZB = -1.15, 1.15, 2.6, 2.1
    R = Room(cam, XL, XR, CEIL, ZB)
    steel = brushed(701)
    img = full((150, 150, 150))
    # side walls: steel panels with mirror strip
    for side, dk in (('left', 0.88), ('right', 0.8)):
        X_, Y_, Z_ = getattr(R, side)
        wcol = lerp(full((185, 188, 192)), full((140, 145, 152)), smooth(0, 2.6, Y_)[..., None]) * (0.92 + 0.15 * fbm(H, W, 30, 4, seed=702, sx=0.02, sy=40)[..., None])
        img = R.paint(img, side, wcol * dk)
        # panel seams
        mm = Mask()
        for z in (0.7, 1.4):
            mm.line([P(X_[0, 0], 0, z), P(X_[0, 0], CEIL, z)], 2)
        img = lerp(img, img * 0.55, mm.get(0.6) * getattr(R, 'm_' + side))
    # mirror panel on the left wall (reflects a dim blur of the right wall)
    mirror = [P(XL, 2.2, 0.2), P(XL, 2.2, 1.9), P(XL, 1.0, 1.9), P(XL, 1.0, 0.2)]
    mref = blur(img[:, ::-1], 6) * C((215, 222, 235)) * 1.05 + 0.04
    img, mm_ = quad(img, mirror, mref)
    img = screen(img, (255, 255, 255), mm_ * np.clip(1 - np.abs((x - 200) + (y - 300) * 0.3) / 120, 0, 1) * 0.25)
    # back wall: doors (steel) with frame
    BX_, BY_, _ = R.back
    img = R.paint(img, 'back', full((160, 160, 165)))
    da, db = P(-0.55, 2.15, ZB), P(0.55, 0, ZB)
    fa, fb = P(-0.7, 2.3, ZB), P(0.7, 0, ZB)
    img = over(img, (120, 105, 70), rect_m(fa[0], fa[1], fb[0], fb[1]))
    door = brushed(703, (195, 197, 200))
    door *= (0.85 + 0.2 * smooth(da[0], db[0], x))[..., None]
    img = lerp(img, door, rect_m(da[0], da[1], db[0], db[1]))
    mid = (da[0] + db[0]) / 2
    img = over(img, (40, 40, 45), rect_m(mid - 2, da[1], mid + 2, db[1]))
    img = screen(img, (255, 255, 255), rect_m(mid + 3, da[1], mid + 8, db[1], 2) * 0.3)
    # back-wall side panels (beside doors): darker steel
    img = lerp(img, brushed(704, (150, 152, 158)), R.m_back * (1 - rect_m(fa[0], fa[1], fb[0], fb[1])) * (y < fb[1]))
    img = over(img, (120, 105, 70), rect_m(fa[0], fa[1], fb[0], fb[1]) - rect_m(da[0], da[1], db[0], db[1]))
    # indicator panel above the doors
    ia, ib = P(-0.35, 2.48, ZB), P(0.35, 2.33, ZB)
    img = over(img, (15, 15, 18), rect_m(ia[0], ia[1], ib[0], ib[1], 0.8))
    num = text_rgba('▲ 38', int((ib[1] - ia[1]) * 0.8), (255, 60, 40))
    img, nm = paste_at(img, num, (ia[0] + ib[0]) / 2 - num.width / 2, ia[1] + (ib[1] - ia[1] - num.height) / 2)
    img = screen(img, (255, 60, 40), blur(nm, 5) * 0.7)
    # button panel on right wall, near the door
    bp = [P(XR, 1.45, 1.55), P(XR, 1.45, 1.85), P(XR, 0.85, 1.85), P(XR, 0.85, 1.55)]
    img, bpm = quad(img, bp, (200, 202, 206))
    img = over(img, (150, 125, 70), np.clip(bpm - ndimage.grey_erosion(bpm, size=(5, 5)), 0, 1))
    for row in range(6):
        for col_ in range(2):
            yy = 1.38 - row * 0.085
            zz = 1.62 + col_ * 0.14
            bx, by = P(XR, yy, zz)
            rr = 0.018 * cam.sc(zz)
            lit = (row, col_) == (1, 1)
            img = over(img, (190, 160, 90), Mask().ellipse((bx - rr * 0.5, by - rr, bx + rr * 0.5, by + rr)).get(0.5))
            if lit:
                img = screen(img, (255, 180, 80), radial(bx, by, rr * 2.5, power=1.2))
    # brass handrails on both side walls
    for X in (XL + 0.05, XR - 0.05):
        img = over(img, (200, 165, 90), Mask().line([P(X, 0.92, 0.3), P(X, 0.92, ZB - 0.15)], 6).get(0.8))
        img = screen(img, (255, 240, 190), Mask().line([P(X, 0.935, 0.3), P(X, 0.935, ZB - 0.15)], 2).get(0.8) * 0.7)
    img = over(img, (200, 165, 90), Mask().line([P(XL + 0.1, 0.92, ZB - 0.05), P(-0.75, 0.92, ZB - 0.05)], 5).get(0.8))
    img = over(img, (200, 165, 90), Mask().line([P(0.75, 0.92, ZB - 0.05), P(XR - 0.1, 0.92, ZB - 0.05)], 5).get(0.8))
    # floor: dark granite with speckle + steel threshold
    FX_, _, FZ = R.floor
    spk = (np.random.default_rng(705).random((H, W)) > 0.985).astype(np.float32)
    gran = full((45, 44, 48)) * (0.85 + 0.25 * fbm(H, W, 6, 3, seed=706)[..., None])
    gran = lerp(gran, full((150, 150, 155)), blur(spk, 0.6) * 0.6)
    img = lerp(img, gran, R.m_floor)
    img, _ = quad(img, [P(-0.7, 0.002, ZB - 0.12), P(0.7, 0.002, ZB - 0.12), P(0.7, 0.002, ZB), P(-0.7, 0.002, ZB)], (170, 172, 176))
    # ceiling: dark panel with LED ring + downlights
    img = R.paint(img, 'ceil', full((50, 50, 56)))
    for (Xc, Zc) in ((-0.5, 0.8), (0.5, 0.8), (-0.5, 1.6), (0.5, 1.6)):
        img = downlight(img, cam, Xc, CEIL - 0.005, Zc, r=0.05, glow=1.2)
    # light from above on walls
    for side in ('left', 'right', 'back'):
        X_, Y_, Z_ = getattr(R, side)
        img = lerp(img, img * 1.12, getattr(R, 'm_' + side) * smooth(1.2, 2.6, Y_) * 0.6)
    # floor reflection of the doors
    img = reflect_down(img, R.m_floor, db[1], strength=0.35, blur_r=4, fade=250)
    img = bloom(img, 0.85, 20, 0.4)
    return img


# ====================================================================== rooftop at night
def rooftop_night():
    x, y = grid()
    cam = Cam(F=900.0, VX=960.0, VY=420.0, EYE=1.6)
    P = cam.P
    hz = cam.VY
    r = rng0(801)
    sky = vgrad([(0, (8, 10, 30)), (0.6, (25, 30, 70)), (0.9, (70, 55, 100)), (1, (120, 80, 100))], y0=0, y1=hz)
    img = stars(sky, smooth(hz - 60, 0, y) * 0.8, n=500, seed=802)
    img = screen(img, (235, 240, 255), radial(1500, 140, 22, power=0.3))
    img = screen(img, (120, 140, 220), radial(1500, 140, 200, power=2) * 0.5)
    # thin cloud wisps lit by the city
    cl = smooth(0.62, 0.85, fbm(H, W, 200, 5, seed=803, sx=4)) * smooth(150, hz, y) * (y < hz)
    img = lerp(img, full((90, 70, 110)), cl * 0.35)
    # city below: light carpet towards the horizon
    below = vgrad([(0, (70, 50, 70)), (0.3, (35, 28, 50)), (1, (15, 15, 30))], y0=hz, y1=H)
    img = lerp(img, below, (y >= hz).astype(np.float32))
    zz = np.where(y > hz + 0.5, 200 * cam.F / np.maximum(y - hz, 0.5), 1e5)  # ground 200 m below
    Xw = (x - cam.VX) * zz / cam.F
    gx = np.floor(Xw / 40)
    gz = np.floor(zz / 40)
    # street grid lines (glowing)
    road = (np.abs((Xw / 120) % 1 - 0.5) > 0.47) | (np.abs((zz / 150) % 1 - 0.5) > 0.47)
    roadm = road.astype(np.float32) * (y > hz + 2)
    img = screen(img, (255, 170, 90), roadm * smooth(hz, hz + 300, y) * 0.55)
    # window lights speckle
    spk = r.random((H, W)).astype(np.float32)
    dens = smooth(hz, hz + 40, y) * (0.02 + 0.04 * fbm(H, W, 60, 4, seed=804))
    lit = (spk < dens).astype(np.float32)
    lit = blur(lit, 0.6) * 2
    img = screen(img, (255, 220, 160), np.clip(lit, 0, 1) * (y > hz))
    img = screen(img, (255, 150, 90), smooth(hz + 120, hz, y) * (y >= hz - 30) * 0.3)
    # a few skyscrapers rising above the horizon (silhouettes with windows)
    for i in range(9):
        bx = r.uniform(100, 1820)
        bw = r.uniform(40, 110)
        bh = r.uniform(40, 260)
        m = rect_m(bx, hz - bh, bx + bw, hz + 120)
        img = lerp(img, full((18, 18, 34)), m)
        u, v = x - bx, y - (hz - bh)
        win = ((u % 9) < 4) & ((v % 11) < 5) & (hash2(np.floor(u / 9) + i * 13, np.floor(v / 11), 1) > 0.6)
        img = lerp(img, full((255, 215, 150)) * 0.8, win.astype(np.float32) * m * 0.8)
        img = screen(img, (255, 50, 50), radial(bx + bw / 2, hz - bh - 6, 8, power=1.2))
    img = bloom(img, 0.6, 20, 0.6)
    # ---------------- terrace
    RZ = 5.0
    # deck
    FZ = np.where(y > cam.VY + 0.5, cam.EYE * cam.F / np.maximum(y - cam.VY, 0.5), 1e3)
    FX_ = (x - cam.VX) * FZ / cam.F
    deck_m = Mask().poly([P(-20, 0, RZ), P(20, 0, RZ), P(20, 0, 0.1), P(-20, 0, 0.1)]).get()
    plank = np.floor(FZ / 0.15)
    pr = hash2(plank, 1.0, 7)
    seg = np.floor(FX_ / 2.0 + pr * 3)
    sr = hash2(plank, seg, 9)
    wood = gradient([(0, (60, 45, 38)), (1, (90, 65, 50))], 0.3 + 0.6 * sr)
    seams = (np.abs(FZ / 0.15 - np.round(FZ / 0.15)) < 0.06 * (FZ / 2)).astype(np.float32)
    wood = lerp(wood, wood * 0.5, seams * 0.7)
    img = lerp(img, wood, deck_m)
    # parapet + glass railing
    img, _ = quad(img, [P(-20, 0.25, RZ), P(20, 0.25, RZ), P(20, 0, RZ), P(-20, 0, RZ)], (50, 50, 60))
    glass = [P(-20, 1.15, RZ), P(20, 1.15, RZ), P(20, 0.25, RZ), P(-20, 0.25, RZ)]
    gm = Mask().poly(glass).get()
    img = lerp(img, img * C((170, 200, 210)) + C((10, 18, 25)), gm * 0.4)
    img = over(img, (150, 155, 165), Mask().line([P(-20, 1.15, RZ), P(20, 1.15, RZ)], 7).get())
    img = screen(img, (220, 230, 255), Mask().line([P(-20, 1.17, RZ), P(20, 1.17, RZ)], 2).get() * 0.6)
    pm = Mask()
    for Xp in np.arange(-12, 12.1, 1.5):
        pm.line([P(Xp, 1.15, RZ), P(Xp, 0.25, RZ)], 5)
    img = over(img, (120, 125, 135), pm.get())
    # side wall of the stair housing (left) with a door + wall lamp
    img, _ = box3(img, cam, -9.0, -3.2, 0, 3.0, 1.0, 4.2, (70, 70, 80), shade=(1, 0.9, 0.78))
    dp = [P(-3.2, 2.1, 2.2), P(-3.2, 2.1, 3.1), P(-3.2, 0, 3.1), P(-3.2, 0, 2.2)]
    img, _ = quad(img, dp, (45, 48, 55))
    lx, ly = P(-3.2, 2.35, 2.65)
    img = over(img, (255, 235, 190), rect_m(lx - 6, ly - 10, lx + 10, ly + 10, 0.8))
    img = screen(img, (255, 190, 120), radial(lx, ly + 150, 380, power=2) * 0.55)
    img = screen(img, (255, 200, 140), radial(lx + 60, ly, 60, power=1))
    # planters with plants
    for Xc in (-2.4, 4.6):
        img, _ = box3(img, cam, Xc - 0.5, Xc + 0.5, 0, 0.5, RZ - 0.8, RZ - 0.1, (85, 85, 92), shade=(1, 0.9, 0.75))
        tx, ty = P(Xc, 0.5, RZ - 0.45)
        s_ = cam.sc(RZ - 0.45)
        fm = Mask()
        rr = rng0(int(Xc * 10 + 50))
        for _ in range(26):
            a = rr.uniform(-1.3, 1.3)
            ln = rr.uniform(0.35, 0.8) * s_
            fm.tapered([(tx + rr.normal(0, 0.1) * s_, ty), (tx + math.sin(a) * ln * 0.6, ty - ln * 0.7), (tx + math.sin(a) * ln, ty - ln * math.cos(a) * 0.8)], 0.05 * s_, 1)
        img = over(img, (25, 55, 40), fm.get(0.8))
    # bench (back to camera, facing the view)
    BX0, BX1, BZ = 0.9, 2.9, 4.1
    # shadow
    img = lerp(img, img * 0.6, Mask().poly([P(BX0, 0, BZ - 0.3), P(BX1, 0, BZ - 0.3), P(BX1 + 0.1, 0, BZ + 0.3), P(BX0 - 0.1, 0, BZ + 0.3)]).get(6))
    for Xl in (BX0 + 0.12, BX1 - 0.12):  # cast-iron side frames
        img, _ = quad(img, [P(Xl - 0.03, 0.45, BZ + 0.2), P(Xl + 0.03, 0.45, BZ + 0.2), P(Xl + 0.03, 0, BZ + 0.2), P(Xl - 0.03, 0, BZ + 0.2)], (30, 30, 34))
    for k in range(4):  # seat slats
        z0 = BZ - 0.2 + k * 0.11
        img, _ = quad(img, [P(BX0, 0.45, z0), P(BX1, 0.45, z0), P(BX1, 0.45, z0 + 0.08), P(BX0, 0.45, z0 + 0.08)], (150, 105, 65))
        img, _ = quad(img, [P(BX0, 0.45, z0), P(BX1, 0.45, z0), P(BX1, 0.42, z0), P(BX0, 0.42, z0)], (95, 65, 40))
    for Xl in (BX0 + 0.12, BX1 - 0.12):
        img, _ = quad(img, [P(Xl - 0.03, 0.45, BZ - 0.22), P(Xl + 0.03, 0.45, BZ - 0.22), P(Xl + 0.03, 0, BZ - 0.22), P(Xl - 0.03, 0, BZ - 0.22)], (35, 35, 40))
        img, _ = quad(img, [P(Xl - 0.035, 0.95, BZ - 0.26), P(Xl + 0.035, 0.95, BZ - 0.26), P(Xl + 0.035, 0.45, BZ - 0.22), P(Xl - 0.035, 0.45, BZ - 0.22)], (35, 35, 40))
    for yy in (0.56, 0.7, 0.84):  # backrest slats (seen from behind)
        img, _ = quad(img, [P(BX0, yy + 0.09, BZ - 0.28), P(BX1, yy + 0.09, BZ - 0.28), P(BX1, yy, BZ - 0.27), P(BX0, yy, BZ - 0.27)], (125, 88, 55))
        img = screen(img, (255, 200, 150), Mask().line([P(BX0, yy + 0.09, BZ - 0.28), P(BX1, yy + 0.09, BZ - 0.28)], 1.5).get(0.6) * 0.5)
    # deck bollard lights
    for Xc in (-1.8, 0.0, 3.6, 6.0):
        bx, by = P(Xc, 0, RZ - 0.3)
        s_ = cam.sc(RZ - 0.3)
        img = over(img, (40, 40, 45), rect_m(bx - 0.04 * s_, by - 0.35 * s_, bx + 0.04 * s_, by))
        img = over(img, (255, 230, 180), rect_m(bx - 0.04 * s_, by - 0.33 * s_, bx + 0.04 * s_, by - 0.28 * s_))
        img = screen(img, (255, 190, 120), radial(bx, by, 0.9 * s_, power=2, sy=0.35) * 0.5)
    # overall: cool night tone on the terrace, city glow on the rail
    img = lerp(img, img * C((150, 160, 220)), deck_m * 0.35)
    img = screen(img, (255, 150, 100), radial(960, P(0, 1.15, RZ)[1], 1300, power=2, sy=0.2) * 0.15)
    return img


SCENES = {'office_lobby': office_lobby, 'ib_office_night': ib_office_night, 'ib_trading_floor': ib_trading_floor,
          'meeting_room': meeting_room, 'elevator': elevator, 'rooftop_night': rooftop_night,
          'hotel_suite_night': hotel_suite_night, 'rental_room': rental_room, 'rental_room_night': rental_room_night}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        save_rgb(SCENES[n](), os.path.join(BG, n + '.png'))
