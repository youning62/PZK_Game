"""Procedurally painted backgrounds."""
import sys
from artlib import *
import car as carlib

rng0 = np.random.default_rng


# =============================================================== garage
def garage():
    x, y = grid()
    FLOOR = 700
    # back wall: dark concrete panels
    img = vgrad([(0, (28, 30, 36)), (0.6, (52, 54, 60)), (1, (40, 42, 48))], y0=0, y1=FLOOR)
    tex = fbm(H, W, 120, 6, seed=21)
    img *= (0.88 + 0.2 * tex)[..., None]
    pan = Mask()
    for px in range(0, W, 320):
        pan.line([(px, 60), (px, FLOOR)], 2)
    pan.line([(0, 380), (W, 380)], 2)
    img = over(img, (20, 21, 25), pan.get() * 0.7)
    # ceiling band
    ceil = vgrad([(0, (10, 10, 13)), (1, (24, 25, 30))], y0=0, y1=60)
    img = lerp(img, ceil, (y < 60).astype(np.float32))
    # horizontal cool LED strip
    led = np.exp(-((y - 120) / 3) ** 2) * smooth(80, 200, x) * smooth(1840, 1720, x)
    img = screen(img, (200, 230, 255), led)
    img = screen(img, (90, 140, 220), blur(led, 30) * 1.6)
    # wall wash under the strip
    img = screen(img, (120, 150, 200), smooth(120, 400, y) * smooth(700, 400, y) * 0.08)
    # floor: polished concrete, perspective
    fl = vgrad([(0, (60, 62, 68)), (0.4, (44, 46, 52)), (1, (22, 23, 27))], y0=FLOOR, y1=H)
    ftex = fbm(H, W, 90, 5, seed=22, sx=3)
    fl *= (0.9 + 0.18 * ftex)[..., None]
    joints = Mask()
    vpx, vpy = 960, 300
    for k in range(-8, 9):
        bx = 960 + k * 420
        t = (FLOOR - vpy) / (H - vpy)
        joints.line([(vpx + (bx - vpx) * t, FLOOR), (bx, H)], 2)
    for yy in (760, 860, 1010):
        joints.line([(0, yy), (W, yy)], 2)
    fl = over(fl, (18, 18, 22), joints.get() * 0.5)
    fm = smooth(FLOOR - 1, FLOOR + 1, y)
    img = lerp(img, fl, fm)
    # skirting line
    img = over(img, (14, 14, 18), np.exp(-((y - FLOOR) / 2.5) ** 2))
    # side pillars
    for px0, px1 in ((60, 190), (1730, 1860)):
        m = Mask().rect((px0, 0, px1, FLOOR)).get()
        pc = vgrad([(0, (36, 38, 44)), (1, (60, 62, 70))], y0=0, y1=FLOOR)
        pc *= (0.85 + 0.25 * smooth(px0, px1, x))[..., None]
        img = lerp(img, pc, m)
    # wall shelf silhouettes: tyres rack at left, cabinet at right
    # glass wall with night-city bokeh (left)
    gw = Mask().rect((240, 150, 640, 640)).get()
    city = vgrad([(0, (8, 12, 30)), (1, (30, 30, 60))], y0=150, y1=640)
    r = rng0(31)
    pts = [(r.uniform(240, 640), r.uniform(300, 640)) for _ in range(70)]
    cols = [[(255, 200, 120), (255, 240, 200), (120, 180, 255), (255, 120, 160)][r.integers(0, 4)] for _ in pts]
    city = bokeh(city, pts, cols, [r.uniform(5, 18) for _ in pts], 0.7, 0.4)
    img = lerp(img, city, gw)
    frame = Mask()
    for fx_ in (240, 440, 640):
        frame.line([(fx_, 150), (fx_, 640)], 6)
    frame.line([(240, 150), (640, 150)], 6)
    frame.line([(240, 640), (640, 640)], 6)
    img = over(img, (70, 72, 80), frame.get())
    img = screen(img, (255, 255, 255), gw * np.clip(1 - np.abs((x - y * 0.5) - 260) / 60, 0, 1) * 0.08)
    # tool chest (right)
    cab = Mask().rect((1440, 440, 1680, FLOOR)).get()
    cabc = vgrad([(0, (150, 30, 36)), (1, (70, 14, 18))], y0=440, y1=FLOOR)
    img = lerp(img, cabc, cab)
    for yy in range(470, FLOOR - 20, 52):
        img = over(img, (40, 8, 12), Mask().rect((1446, yy, 1674, yy + 3)).get())
        img = over(img, (210, 210, 220), Mask().rect((1530, yy + 14, 1590, yy + 19)).get())
    # spotlights: ceiling fixtures + cones
    for sx in (520, 960, 1400):
        img = screen(img, (255, 248, 230), radial(sx, 62, 26, power=0.6))
        cone = np.clip(1 - np.abs(x - sx) / (40 + (y - 60) * 0.42), 0, 1) ** 1.6 * smooth(60, 140, y)
        cone *= smooth(1050, 600, y)
        img = screen(img, (255, 240, 215), cone * 0.12)
        img = screen(img, (255, 240, 215), radial(sx, 800, 520, power=2, sy=0.28) * 0.35)
    # car
    sc = 1.28
    gy = 880
    x0 = 960 - 502 * sc
    y0 = gy - carlib.GROUND * sc
    crgb, ca = carlib.render(x0, y0, sc, 'garage')
    rr, ra = carlib.reflect(crgb, ca, gy - 2, 0.45, 4)
    img = lerp(img, rr, ra)
    # contact shadow
    sh = radial(960, gy, 720, power=1.2, sy=0.05)
    img *= (1 - 0.8 * np.clip(sh * 2, 0, 1))[..., None]
    img = lerp(img, crgb, ca)
    # spot reflections on car top
    for sx in (520, 960, 1400):
        hl = radial(sx, y0 + 95 * sc, 60, power=2, sy=0.25) * ca
        img = screen(img, (255, 255, 255), hl * 0.6)
    # floor spot reflections streaks
    for sx in (520, 960, 1400):
        st = np.exp(-((x - sx) / 18) ** 2) * smooth(FLOOR, FLOOR + 60, y) * smooth(1080, 900, y) * (1 - ca)
        img = screen(img, (255, 245, 225), st * 0.18)
    img = bloom(img, 0.75, 20, 0.6)
    return img


# =============================================================== shared bits
def day_sky(hz, seed=1, top=(40, 110, 215), mid=(110, 180, 245), low=(205, 232, 250)):
    img = vgrad([(0, top), (0.6, mid), (1, low)], y0=0, y1=hz)
    img = sky_clouds(img, 40, hz - 10, seed=seed, cover_=0.58, amount=0.85, shade=(185, 205, 230))
    img = screen(img, (255, 255, 255), smooth(hz - 120, hz, grid()[1]) * 0.25)
    return img


def palm_layer(img, specs, col=(30, 50, 30), shade=None, blur_r=0):
    """specs: list of kwargs for palm(). Paints palms with trunk/crown tone."""
    m = Mask()
    tm = Mask()
    for sp in specs:
        palm(m, tmask=tm, **sp)
    a = m.get(blur_r)
    ta = tm.get(blur_r)
    x, y = grid()
    if shade is None:
        c = np.array(col, np.float32) / 255
        tex = fbm(H, W, 120, 3, seed=len(specs))
        cc = c[None, None, :] * (0.85 + 0.3 * tex[..., None])
        tc = np.array([0.36, 0.30, 0.22], np.float32) * c.sum() / 0.5
        tc = np.clip(tc, 0, 1)
        rings = 0.85 + 0.15 * (np.sin(y * 0.5) > 0.6)
        tcc = tc[None, None, :] * rings[..., None]
        img = lerp(img, tcc, ta)
    else:
        cc = shade
        img = lerp(img, cc, ta)
    return lerp(img, cc, a), np.clip(a + ta, 0, 1)


def hills(img, base_y, amp, seed, col, haze=None, x0=0, x1=W, scale=300):
    r = rng0(seed)
    xs = np.arange(W, dtype=np.float32)
    prof = np.zeros(W, np.float32)
    for k, f in enumerate((1 / scale, 2.3 / scale, 5.1 / scale, 11 / scale)):
        prof += np.sin(xs * f * 2 * math.pi + r.uniform(0, 6)) * amp / (1.8 ** k)
    top = base_y - amp - prof
    x, y = grid()
    m = (y >= top[None, :]).astype(np.float32) * (y <= base_y + 2) * (x >= x0) * (x < x1)
    m = blur(m, 0.8)
    c = np.array(col, np.float32) / 255
    tex = fbm(H, W, 40, 4, seed=seed)
    cc = c * (0.85 + 0.3 * tex[..., None])
    if haze is not None:
        cc = lerp(cc, np.array(haze, np.float32) / 255, 0.35)
    return lerp(img, cc, m), m


# =============================================================== coast road
def coast_road():
    x, y = grid()
    HZ = 430
    img = day_sky(HZ, seed=41)
    # distant islands / headland, hazy
    img, _ = hills(img, HZ, 28, 42, (120, 160, 175), x0=0, x1=700, scale=500)
    img = sea(img, HZ, (35, 110, 185), (40, 205, 205), seed=43, streak=0.16,
              glint=(500, 160, (255, 255, 240), 0.5))
    # turquoise shallows near shore at lower left
    shal = smooth(650, 1000, y) * smooth(1100, 600, x)
    img = lerp(img, img * np.array([0.8, 1.15, 1.05], np.float32), shal * 0.6)
    # land on the inland side of the road
    from scipy.interpolate import PchipInterpolator
    yy = np.arange(H, dtype=np.float32)
    t = np.clip((yy - 470) / (H - 470), 0, 1)
    cx = PchipInterpolator([0, 0.12, 0.4, 0.7, 1.0], [1330, 1130, 760, 770, 960])(t)
    inland = blur(((x > cx[:, None]) & (y >= 462)).astype(np.float32), 1)
    gtex = fbm(H, W, 50, 4, seed=47)
    img = lerp(img, gradient([(0, (70, 110, 50)), (1, (120, 150, 80))], gtex), inland)
    # cliffs on the right: far (hazy) then near (rock + vegetation)
    far = Mask().poly([(980, HZ + 2), (1080, 330), (1200, 250), (1320, 215), (1500, 170), (1700, 150),
                       (1920, 120), (1920, HZ + 2)]).get(1.0)
    fc = lerp(np.array([70, 120, 90], np.float32) / 255, np.array([150, 185, 200], np.float32) / 255, 0.45)
    tex = fbm(H, W, 50, 5, seed=44)
    img = lerp(img, fc * (0.85 + 0.3 * tex[..., None]), far)
    near_pts = [(1180, 1080), (1150, 800), (1230, 640), (1330, 520), (1420, 400), (1560, 320),
                (1700, 280), (1920, 240), (1920, 1080)]
    near = Mask().poly(near_pts).get(1.0)
    tex2 = fbm(H, W, 70, 6, seed=45)
    strata = 0.5 + 0.5 * np.sin((y * 0.08 + x * 0.03) + tex2 * 6)
    rock = gradient([(0, (95, 80, 65)), (0.5, (150, 125, 95)), (1, (190, 165, 130))], tex2 * 0.7 + strata * 0.3)
    rock *= (0.75 + 0.35 * smooth(1300, 1900, x))[..., None]
    veg_line = 330 + (x - 1300) * -0.12 + tex2 * 120
    veg = smooth(veg_line + 60, veg_line - 20, y)
    vcol = gradient([(0, (30, 70, 30)), (1, (80, 140, 60))], tex)
    rock = lerp(rock, vcol, veg)
    img = lerp(img, rock, near)
    # rocks/beach between sea and road (left of road)
    # road centre-line along y
    half = 6 + 560 * t ** 1.3
    L = cx - half
    R = cx + half
    road = ((x >= L[:, None]) & (x <= R[:, None]) & (y >= 470)).astype(np.float32)
    road = blur(road, 0.8)
    # verge (sand/grass) on sea side
    verge = ((x >= (L - 30 - 140 * t)[:, None]) & (x < L[:, None]) & (y >= 466)).astype(np.float32)
    verge = blur(verge, 1)
    img = lerp(img, np.array([0.86, 0.80, 0.66], np.float32) * (0.9 + 0.2 * tex[..., None]), verge)
    atex = fbm(H, W, 6, 3, seed=46)
    asp = np.array([0.36, 0.37, 0.40], np.float32) * (0.92 + 0.16 * atex[..., None])
    asp = asp * (0.9 + 0.15 * t[:, None, None])
    img = lerp(img, asp, road)
    # lines
    u = (x - L[:, None]) / (2 * half[:, None])  # 0..1 across road
    edge = (np.abs(u - 0.04) < 0.008 + 0.0) | (np.abs(u - 0.96) < 0.008)
    dist = 1.0 / (t + 0.02)
    dash = (np.sin(dist * 3.0) > 0)[:, None]
    centre = (np.abs(u - 0.5) < 0.009) & dash
    lines = ((edge | centre) & (road > 0.5)).astype(np.float32)
    img = over(img, (245, 245, 235), blur(lines, 0.6) * 0.9)
    # guard rail along the sea-side edge
    rail = Mask()
    pts = [(float(L[int(yv)] - 6), float(yv - 6 - 36 * t[int(yv)])) for yv in range(472, H, 8)]
    rail.line(pts, 3)
    pts2 = [(float(L[int(yv)] - 6), float(yv - 2 - 18 * t[int(yv)])) for yv in range(472, H, 8)]
    rail.line(pts2, 2)
    for yv in range(480, H, 28):
        tt = t[yv]
        rail.line([(float(L[yv] - 6), float(yv - 40 * tt - 4)), (float(L[yv] - 6), float(yv))], 1 + 4 * tt)
    img = over(img, (225, 228, 232), rail.get())
    # rock outcrop occluding the far end of the road
    occ = Mask().poly([(1170, 640), (1200, 560), (1260, 500), (1330, 455), (1420, 400), (1560, 380),
                       (1600, 700), (1300, 720)]).get(1.0)
    img = lerp(img, rock * 0.92, occ)
    # palms
    specs = [dict(bx=1600, by=900, height=560, lean=-0.28, seed=1, fronds=11),
             dict(bx=1760, by=980, height=720, lean=-0.18, seed=2, fronds=12),
             dict(bx=1430, by=640, height=280, lean=-0.2, seed=3),
             dict(bx=1340, by=560, height=170, lean=-0.15, seed=4),
             dict(bx=120, by=1150, height=900, lean=0.22, seed=5, fronds=12)]
    img, pa = palm_layer(img, specs, (40, 65, 35))
    img = screen(img, (255, 250, 220), radial(300, 0, 900, power=2) * 0.25)
    return img


# =============================================================== resort hotel
def resort_hotel():
    x, y = grid()
    HZ = 640
    img = day_sky(HZ, seed=51)
    img, _ = hills(img, 600, 90, 52, (90, 140, 110), haze=(170, 205, 220), scale=700)
    tex = fbm(H, W, 40, 4, seed=53)
    white = lambda v: np.array([v, v * 0.985, v * 0.955], np.float32)

    def block(x0, y0, x1, y1, shade=1.0, cols=8, rows=5, balcony=True):
        nonlocal img
        m = Mask().rect((x0, y0, x1, y1)).get()
        c = white(0.93 * shade)[None, None, :] * (0.96 + 0.06 * tex[..., None])
        c = c * (1 - 0.12 * smooth(y0, y1, y))[..., None]
        img = lerp(img, c, m)
        # cornice
        img = over(img, white(0.99 * shade) * 255, Mask().rect((x0 - 8, y0 - 10, x1 + 8, y0 + 6)).get())
        img = over(img, (150, 150, 145), Mask().rect((x0 - 8, y0 + 6, x1 + 8, y0 + 10)).get() * 0.5)
        cw = (x1 - x0) / cols
        rh = (y1 - y0 - 30) / rows
        for i in range(cols):
            for j in range(rows):
                wx0 = x0 + i * cw + cw * 0.18
                wx1 = x0 + (i + 1) * cw - cw * 0.18
                wy0 = y0 + 24 + j * rh + rh * 0.12
                wy1 = y0 + 24 + (j + 1) * rh - rh * 0.18
                wm = Mask().rect((wx0, wy0, wx1, wy1)).get()
                gc = gradient([(0, (90, 150, 200)), (1, (30, 70, 110))], smooth(wy0, wy1, y))
                gc = screen(gc, (220, 240, 255), np.clip(1 - np.abs((x - wx0) - (y - wy0) * 0.6 - cw * 0.3) / 6, 0, 1) * 0.5)
                img = lerp(img, gc, wm)
                if balcony:
                    img = over(img, (240, 240, 236), Mask().rect((wx0 - cw * 0.12, wy1 - 2, wx1 + cw * 0.12, wy1 + 6)).get())
                    img = over(img, (170, 210, 225), Mask().rect((wx0 - cw * 0.1, wy1 - rh * 0.28, wx1 + cw * 0.1, wy1 - 2)).get() * 0.35)
        # contact shadow under cornice
        img *= (1 - 0.15 * Mask().rect((x0, y0 + 10, x1, y0 + 30)).get(6))[..., None]

    block(140, 360, 720, 700, 0.93, 7, 5)
    block(1200, 360, 1780, 700, 0.93, 7, 5)
    block(700, 200, 1220, 700, 1.0, 6, 7)
    # roof crown on central tower
    img = over(img, (196, 120, 90), Mask().poly([(690, 192), (960, 120), (1230, 192)]).get())
    img = over(img, (160, 95, 70), Mask().poly([(960, 120), (1230, 192), (1180, 192)]).get() * 0.5)
    # porte-cochere canopy + columns
    can = Mask().rect((740, 560, 1180, 600)).get()
    img = over(img, (250, 250, 246), can)
    img = over(img, (120, 120, 118), Mask().rect((740, 600, 1180, 608)).get() * 0.6)
    sign = text_img('PARADISE RESORT', 60, (190, 150, 70, 255))
    img = paste_quad(img, sign, [(800, 566), (1120, 566), (1120, 596), (800, 596)])
    for cxx in (770, 870, 1050, 1150):
        cm = Mask().rect((cxx - 12, 606, cxx + 12, 720)).get()
        cc = gradient([(0, (200, 200, 196)), (0.5, (255, 255, 252)), (1, (190, 190, 186))], smooth(cxx - 12, cxx + 12, x))
        img = lerp(img, cc, cm)
    # lobby glow
    lob = Mask().rect((790, 615, 1130, 720)).get()
    img = lerp(img, gradient([(0, (255, 220, 160)), (1, (200, 150, 100))], smooth(615, 720, y)), lob * 0.85)
    # ground: driveway paving + lawn
    gr = vgrad([(0, (110, 160, 80)), (1, (70, 120, 50))], y0=700, y1=H)
    gr *= (0.9 + 0.15 * fbm(H, W, 60, 4, seed=54)[..., None])
    img = lerp(img, gr, smooth(699, 702, y))
    drive = Mask().poly([(820, 720), (1100, 720), (1500, 1080), (420, 1080)]).get(1)
    loop = Mask().ellipse((260, 760, 1660, 1180)).get(1)
    dm = np.clip(drive + loop, 0, 1)
    pave = np.array([0.86, 0.82, 0.74], np.float32) * (0.92 + 0.12 * fbm(H, W, 5, 3, seed=55)[..., None])
    img = lerp(img, pave, dm)
    # central fountain pool
    pool = Mask().ellipse((640, 820, 1280, 1000)).get(1)
    pc = gradient([(0, (60, 200, 220)), (1, (20, 140, 190))], smooth(820, 1000, y))
    pc = screen(pc, (255, 255, 255), smooth(0.6, 0.95, fbm(H, W, 8, 2, seed=56, sx=4)) * 0.3)
    rim = Mask().ellipse((626, 810, 1294, 1010)).get(1)
    img = lerp(img, white(0.95) * np.ones((H, W, 3), np.float32), rim)
    img = lerp(img, pc, pool)
    # fountain jet
    jet = np.exp(-((x - 960) / (6 + np.maximum(900 - y, 0) * 0.04)) ** 2) * smooth(700, 760, y) * smooth(920, 880, y)
    img = screen(img, (240, 250, 255), jet * 0.8)
    spray = radial(960, 760, 90, power=1.5, sy=0.6)
    img = screen(img, (240, 250, 255), spray * 0.5)
    # hedges
    hd = Mask()
    r = rng0(57)
    for hx in list(range(150, 720, 40)) + list(range(1220, 1790, 40)):
        hd.circle(hx + r.uniform(-8, 8), 705 + r.uniform(-6, 4), r.uniform(26, 36))
    hcol = gradient([(0, (40, 90, 40)), (1, (90, 150, 70))], fbm(H, W, 10, 3, seed=58))
    img = lerp(img, hcol, hd.get())
    # flowers on hedges
    img = sparkle_field(img, 0, (0, 0, 1, 1))
    specs = [dict(bx=120, by=1120, height=980, lean=0.12, seed=11, fronds=12),
             dict(bx=1800, by=1120, height=980, lean=-0.12, seed=13, fronds=12),
             dict(bx=620, by=740, height=360, lean=0.05, seed=15),
             dict(bx=1300, by=740, height=360, lean=-0.05, seed=16)]
    img, _ = palm_layer(img, specs, (40, 70, 35))
    img = screen(img, (255, 248, 220), radial(1500, 0, 1100, power=2) * 0.2)
    return img


# =============================================================== shopping street
def shopping_street():
    x, y = grid()
    F, VX, VY, EYE = 900.0, 960.0, 470.0, 3.2

    def P(X, Y, Z):  # Y up from ground (metres)
        return (VX + X * F / Z, VY + (EYE - Y) * F / Z)

    img = day_sky(VY, seed=61, top=(35, 105, 215))
    # sea glimpse at end of street
    img = sea(img, VY, (40, 120, 190), (60, 190, 210), seed=62, streak=0.1, glint=(960, 60, (255, 255, 240), 0.4))
    # far beach strip
    ZE = 80.0
    gy_end = P(0, 0, ZE)[1]
    img = over(img, (230, 215, 175), Mask().rect((0, gy_end - 6, W, gy_end + 1)).get())
    # ground: road + sidewalks
    zz = np.where(y > VY + 1, EYE * F / np.maximum(y - VY, 1e-3), 1e9)
    Xw = (x - VX) * zz / F
    gm = (y >= gy_end).astype(np.float32)
    road = np.array([0.62, 0.60, 0.58], np.float32)
    pav = (np.sin(Xw * 3.0) * np.sin(zz * 3.0) > 0).astype(np.float32)
    tile = lerp(np.array([0.88, 0.82, 0.74], np.float32) * np.ones((H, W, 3), np.float32),
                np.array([0.80, 0.70, 0.62], np.float32) * np.ones((H, W, 3), np.float32), pav * 0.5)
    side = (np.abs(Xw) > 4.5).astype(np.float32)
    ground = lerp(road * np.ones((H, W, 3), np.float32), tile, side)
    ground *= (0.95 + 0.06 * fbm(H, W, 40, 3, seed=63)[..., None])
    curb = (np.abs(np.abs(Xw) - 4.5) < 0.12).astype(np.float32)
    ground = lerp(ground, np.array([0.95, 0.95, 0.93], np.float32) * np.ones((H, W, 3), np.float32), curb)
    img = lerp(img, ground, gm)
    # buildings, far to near
    r = rng0(64)
    pal = [(250, 128, 114), (120, 210, 190), (255, 214, 102), (90, 180, 220), (250, 245, 235),
           (240, 150, 180), (170, 220, 120), (255, 180, 120)]
    names = ['SURF', 'CAFE', 'GELATO', 'BIKINI', 'COCO', 'JUICE', 'ALOHA', 'BOUTIQUE', 'TACO', 'SHELL']
    units = []
    for side_ in (-1, 1):
        z = ZE - 12
        k = 0
        while z > 3.5:
            ln = r.uniform(6, 9)
            units.append((side_, z - ln, z, k))
            z -= ln
            k += 1
    units.sort(key=lambda u: -u[2])
    XB = 8.0
    for side_, z0, z1, k in units:
        X = XB * side_
        col = np.array(pal[r.integers(0, len(pal))], np.float32) / 255
        top = r.uniform(7.5, 12)
        lit = 1.0 if side_ < 0 else 0.82
        quad = [P(X, top, z1), P(X, top, z0), P(X, 0, z0), P(X, 0, z1)]
        m = Mask().poly(quad).get()
        wall = col * lit * (0.94 + 0.08 * fbm(H, W, 30, 3, seed=int(z0 * 10))[..., None])
        img = lerp(img, wall, m)
        # cornice
        img = over(img, np.clip(col * 1.15 * 255 * lit, 0, 255),
                   Mask().poly([P(X, top + 0.3, z1), P(X, top + 0.3, z0), P(X, top - 0.2, z0), P(X, top - 0.2, z1)]).get())
        # upper windows
        for wz in np.arange(z0 + 1.0, z1 - 1.0, 2.2):
            for wy in np.arange(5.0, top - 1.2, 2.6):
                wq = [P(X, wy + 1.4, wz + 1.1), P(X, wy + 1.4, wz), P(X, wy, wz), P(X, wy, wz + 1.1)]
                img = over(img, (60, 90, 120), Mask().poly(wq).get())
                img = over(img, np.clip(col * 255 * 0.6, 0, 255),
                           Mask().poly([P(X, wy + 1.55, wz + 1.25), P(X, wy + 1.55, wz - 0.15), P(X, wy + 1.4, wz - 0.15), P(X, wy + 1.4, wz + 1.25)]).get())
        # shop window
        sq = [P(X, 3.0, z1 - 0.5), P(X, 3.0, z0 + 0.5), P(X, 0.3, z0 + 0.5), P(X, 0.3, z1 - 0.5)]
        sm = Mask().poly(sq).get()
        gl = gradient([(0, (150, 165, 175)), (0.5, (110, 105, 95)), (1, (80, 70, 60))], smooth(min(q[1] for q in sq), max(q[1] for q in sq), y))
        gl = screen(gl, (255, 220, 160), sm * 0.35)
        # merchandise blobs
        r2 = rng0(int(z0 * 100))
        for _ in range(6):
            mz = r2.uniform(z0 + 0.8, z1 - 0.8)
            my = r2.uniform(0.5, 1.8)
            cpt = P(X, my, mz)
            rad = r2.uniform(0.25, 0.5) * F / mz
            gl = lerp(gl, np.array(pal[r2.integers(0, len(pal))], np.float32) / 255 * 0.85,
                      radial(cpt[0], cpt[1], rad, power=0.3, sx=0.6))
        img = lerp(img, gl, sm)
        # door + mullions
        dz = z0 + (z1 - z0) * 0.7
        img = over(img, (60, 45, 35), Mask().poly([P(X, 2.4, dz + 0.6), P(X, 2.4, dz - 0.6), P(X, 0, dz - 0.6), P(X, 0, dz + 0.6)]).get())
        for mz in np.linspace(z0 + 0.5, z1 - 0.5, 4):
            img = over(img, (240, 240, 235), Mask().line([P(X, 3.0, mz), P(X, 0.3, mz)], max(1.0, 0.12 * F / mz)).get())
        # awning (striped)
        c2 = np.array(pal[(k * 3 + 1) % len(pal)], np.float32)
        stripes = 6
        for i in range(stripes):
            za = z0 + 0.3 + (z1 - z0 - 0.6) * i / stripes
            zb = z0 + 0.3 + (z1 - z0 - 0.6) * (i + 1) / stripes
            Xo = X - side_ * 1.6
            aq = [P(X, 3.6, zb), P(X, 3.6, za), P(Xo, 2.9, za), P(Xo, 2.9, zb)]
            cc = (255, 255, 250) if i % 2 else tuple(c2.tolist())
            img = over(img, np.array(cc, np.float32) * (1.0 if side_ < 0 else 0.85), Mask().poly(aq).get())
        # awning valance shadow
        img *= (1 - 0.25 * Mask().poly([P(X, 2.9, z1), P(X, 2.9, z0), P(X, 2.0, z0), P(X, 2.0, z1)]).get(3))[..., None]
        # sign board with text
        txt = names[(k * 7 + (0 if side_ < 0 else 3)) % len(names)]
        sb = text_img(txt, 90, (255, 255, 255, 255), bg=tuple(int(v) for v in (c2 * 0.55)) + (255,), pad=24)
        if side_ < 0:
            q = [P(X, 4.8, z1 - 1.0), P(X, 4.8, z0 + 1.0), P(X, 3.8, z0 + 1.0), P(X, 3.8, z1 - 1.0)]
            q = [q[1], q[0], q[3], q[2]]
        else:
            q = [P(X, 4.8, z1 - 1.0), P(X, 4.8, z0 + 1.0), P(X, 3.8, z0 + 1.0), P(X, 3.8, z1 - 1.0)]
            q = [q[0], q[1], q[2], q[3]]
            q = [q[1], q[0], q[3], q[2]]
            q = [q[1], q[0], q[3], q[2]]
        img = paste_quad(img, sb, q)
    # palms along the curbs + string of flags
    specs = []
    for i, zp in enumerate((9, 16, 26, 40, 58)):
        for sd in (-1, 1):
            bx, by = P(4.9 * sd, 0, zp)
            hgt = 9.0 * F / zp
            specs.append(dict(bx=bx, by=by, height=hgt, lean=-0.12 * sd, seed=i * 2 + (sd > 0), fronds=10))
    img, _ = palm_layer(img, specs, (40, 80, 40))
    # bunting across the street
    for zb in (12, 24, 40):
        a_ = P(-XB, 6.5, zb)
        b_ = P(XB, 6.5, zb)
        pts = bezier(a_, ((a_[0] + b_[0]) / 2, a_[1] + 60 * 12 / zb), b_, n=30)
        img = over(img, (80, 80, 80), Mask().line(pts, max(1, 24 / zb)).get())
        fm = Mask()
        for i in range(1, len(pts) - 1):
            px, py = pts[i]
            sz = 260 / zb
            fm.poly([(px - sz * 0.5, py), (px + sz * 0.5, py), (px, py + sz)])
        cols_ = np.array([pal[i % len(pal)] for i in range(len(pts))], np.float32) / 255
        bm = fm.get()
        img = lerp(img, np.array([0.95, 0.4, 0.4], np.float32) * (0.7 + 0.3 * np.sin(x * 0.05)[..., None]) + np.array([0, 0.4, 0.3], np.float32) * np.cos(x * 0.05)[..., None] ** 2, bm)
    img = screen(img, (255, 250, 225), radial(400, 0, 1000, power=2) * 0.2)
    return img


# =============================================================== villa bedroom
def villa_bedroom(night=False):
    x, y = grid()
    F, VX, VY = 820.0, 960.0, 520.0
    EYE = 1.5  # eye above floor
    CEIL = 3.4
    ZB = 7.0
    XW = 7.0

    def P(X, Y, Z):  # Y up from floor
        return (VX + X * F / Z, VY + (EYE - Y) * F / Z)

    bl, br = P(-XW, 0, ZB), P(XW, 0, ZB)
    tl, tr = P(-XW, CEIL, ZB), P(XW, CEIL, ZB)
    # window region (floor-to-ceiling)
    w_tl, w_br = P(-5.6, CEIL - 0.15, ZB), P(5.6, 0.0, ZB)
    wx0, wy0, wx1, wy1 = w_tl[0], w_tl[1], w_br[0], w_br[1]
    hz = wy0 + (wy1 - wy0) * 0.48
    if not night:
        view = vgrad([(0, (110, 180, 240)), (0.7, (190, 225, 248)), (1, (235, 245, 250))], y0=wy0, y1=hz)
        view = sky_clouds(view, wy0, hz - 5, seed=71, cover_=0.62, scale=200)
        view = sea(view, hz, (50, 130, 190), (70, 190, 210), seed=72, streak=0.12, glint=(1150, 80, (255, 255, 235), 0.5))
        view = screen(view, (255, 250, 230), radial(1200, wy0, 700, power=2) * 0.5)
    else:
        view = vgrad([(0, (6, 10, 30)), (0.7, (18, 34, 76)), (1, (40, 60, 110))], y0=wy0, y1=hz)
        view = stars(view, (y < hz).astype(np.float32), n=500, seed=73)
        view = screen(view, (230, 235, 255), radial(1250, wy0 + 120, 26, power=0.25))
        view = screen(view, (140, 170, 230), radial(1250, wy0 + 120, 160, power=2) * 0.6)
        view = sea(view, hz, (10, 22, 50), (20, 40, 80), seed=72, streak=0.12, glint=(1250, 30, (210, 220, 255), 0.7))
    # island silhouette on horizon
    isl = Mask().poly([(520, hz + 1), (600, hz - 22), (680, hz - 30), (760, hz - 12), (820, hz + 1)]).get(0.6)
    view = lerp(view, view * np.array([0.6, 0.75, 0.7], np.float32), isl)
    # balcony glass rail
    rail_y = P(0, 1.05, ZB)[1]
    view = screen(view, (210, 235, 240), ((y > rail_y) & (y < wy1)).astype(np.float32) * 0.12)
    view = over(view, (235, 235, 230) if not night else (60, 60, 70), np.exp(-((y - rail_y) / 2.5) ** 2))
    # walls
    if not night:
        wallc = np.array([0.93, 0.90, 0.85], np.float32)
        amb = 1.0
    else:
        wallc = np.array([0.30, 0.30, 0.40], np.float32)
        amb = 0.55
    img = np.ones((H, W, 3), np.float32) * wallc
    img *= (0.95 + 0.05 * fbm(H, W, 80, 3, seed=74)[..., None])
    # side walls darker
    lw = Mask().poly([(0, -2000), (tl[0], tl[1]), (bl[0], bl[1]), (0, 3000)]).get()
    rw = Mask().poly([(W, -2000), (tr[0], tr[1]), (br[0], br[1]), (W, 3000)]).get()
    img = lerp(img, img * 0.86, lw)
    img = lerp(img, img * 0.80, rw)
    # ceiling
    cm = Mask().poly([(-2000, -10), (W + 2000, -10), (tr[0], tr[1]), (tl[0], tl[1])]).get()
    img = lerp(img, img * 1.02, cm)
    img = over(img, (200, 190, 175) if not night else (50, 50, 60), Mask().line([tl, tr], 3).get())
    # floor (wood planks converging to VP)
    fm = Mask().poly([bl, br, (W + 4000, H + 2000), (-4000, H + 2000)]).get()
    zz = np.where(y > VY + 1, EYE * F / np.maximum(y - VY, 1e-3), 1e9)
    Xw = (x - VX) * zz / F
    plank = np.floor(Xw / 0.22)
    pr = (np.sin(plank * 12.9898) * 43758.5453) % 1.0
    seg = np.floor(zz / 1.6 + pr * 3)
    sr = (np.sin(plank * 7.1 + seg * 3.3) * 1000) % 1.0
    wood = gradient([(0, (150, 95, 60)), (0.5, (185, 125, 80)), (1, (205, 150, 100))], 0.3 + 0.5 * sr)
    gtex = fbm(H, W, 6, 3, seed=75, sx=0.15)
    wood *= (0.9 + 0.15 * gtex[..., None])
    seams = (np.abs((Xw / 0.22) - np.round(Xw / 0.22)) < 0.03 * (zz / 3 + 0.3)).astype(np.float32)
    wood = lerp(wood, wood * 0.65, seams * 0.6)
    img = lerp(img, wood, fm)
    # window: frame + view + mullions
    img = over(img, (240, 240, 236) if not night else (70, 70, 80), Mask().rect((wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 2)).get())
    wm = Mask().rect((wx0, wy0, wx1, wy1)).get()
    img = lerp(img, view, wm)
    mull = Mask()
    for i in range(1, 4):
        mx = wx0 + (wx1 - wx0) * i / 4
        mull.rect((mx - 5, wy0, mx + 5, wy1))
    img = over(img, (245, 245, 240) if not night else (60, 60, 70), mull.get())
    # floor reflection of the window
    refl = np.zeros((H, W), np.float32)
    rm = Mask().poly([(wx0, wy1), (wx1, wy1), (wx1 + 300, wy1 + 260), (wx0 - 300, wy1 + 260)]).get(12)
    refl = rm * smooth(wy1 + 260, wy1, y)
    img = screen(img, (255, 248, 230) if not night else (90, 110, 170), refl * (0.35 if not night else 0.25))
    # curtains (sheer, with folds)
    for (cx0, cx1) in ((wx0 - 40, wx0 + 190), (wx1 - 190, wx1 + 40)):
        cmask = Mask().poly([(cx0, wy0 - 20), (cx1, wy0 - 20), (cx1 + (30 if cx0 > 960 else -10), wy1 + 30),
                             (cx0 + (10 if cx0 > 960 else -30), wy1 + 30)]).get()
        folds = 0.5 + 0.5 * np.sin((x - cx0) * 0.09 + np.sin(y * 0.004) * 2)
        cc = np.array([1.0, 0.99, 0.97], np.float32) * (0.8 + 0.2 * folds[..., None])
        if night:
            cc = cc * np.array([0.45, 0.45, 0.55], np.float32)
        img = lerp(img, cc, cmask * (0.75 + 0.2 * folds))
    # curtain rod
    img = over(img, (180, 160, 120), Mask().rect((wx0 - 60, wy0 - 30, wx1 + 60, wy0 - 22)).get())
    # sunbeams
    if not night:
        beams = Mask()
        for i, bx in enumerate((620, 900, 1180, 1420)):
            beams.poly([(bx, wy0), (bx + 120, wy0), (bx - 260, H + 50), (bx - 520, H + 50)])
        bm = beams.get(30)
        img = screen(img, (255, 240, 200), bm * 0.18)
        patch = Mask()
        for i in range(4):
            px0 = wx0 + (wx1 - wx0) * i / 4 + 12
            px1 = wx0 + (wx1 - wx0) * (i + 1) / 4 - 12
            patch.poly([(px0 - 60, wy1 + 40), (px1 - 60, wy1 + 40), (px1 - 380, H - 60), (px0 - 520, H - 60)])
        img = screen(img, (255, 235, 190), patch.get(10) * fm * 0.28)
    # rug
    rug = Mask().poly([P(-3.2, 0, 3.4), P(1.6, 0, 3.4), P(1.6, 0, 5.8), P(-3.2, 0, 5.8)]).get(1)
    rugc = np.array([0.92, 0.88, 0.80], np.float32) * (0.92 + 0.1 * fbm(H, W, 3, 2, seed=76)[..., None])
    img = lerp(img, rugc * amb, rug)
    # bed (right), head at back
    X0, X1, Z0, Z1, TOPY = 2.2, 5.6, 2.3, 5.8, 0.62

    def quad(pts, col, blur_r=0.6):
        nonlocal img
        m = Mask().poly(pts).get(blur_r)
        img = lerp(img, col, m)
        return m

    # bed frame base (wood)
    frame_c = np.array([0.45, 0.30, 0.20], np.float32) * amb
    quad([P(X0, 0.3, Z0), P(X0, 0.3, Z1), P(X0, 0, Z1), P(X0, 0, Z0)], frame_c)
    quad([P(X0, 0.3, Z0), P(X1 + 3, 0.3, Z0), P(X1 + 3, 0, Z0), P(X0, 0, Z0)], frame_c * 0.8)
    # headboard
    quad([P(X0 - 0.2, 1.5, Z1), P(X1 + 2, 1.5, Z1), P(X1 + 2, 0, Z1), P(X0 - 0.2, 0, Z1)],
         np.array([0.80, 0.74, 0.66], np.float32) * amb)
    # mattress / duvet sides
    sheet = np.array([0.97, 0.97, 0.96], np.float32)
    shade = np.array([0.78, 0.82, 0.88], np.float32)
    if night:
        sheet, shade = sheet * np.array([0.5, 0.5, 0.62]), shade * np.array([0.4, 0.42, 0.55])
    folds = fbm(H, W, 60, 4, seed=77, sx=0.6)
    side_m = quad([P(X0, TOPY, Z0), P(X0, TOPY, Z1), P(X0, 0.25, Z1), P(X0, 0.22, Z0)],
                  lerp(shade * np.ones((H, W, 3), np.float32), sheet * 0.92, folds * 0.5))
    quad([P(X0, TOPY, Z0), P(X1 + 3, TOPY, Z0), P(X1 + 3, 0.22, Z0), P(X0, 0.22, Z0)],
         lerp(shade * np.ones((H, W, 3), np.float32), sheet * 0.85, folds * 0.4))
    topc = lerp(sheet * 0.9 * np.ones((H, W, 3), np.float32), sheet * np.ones((H, W, 3), np.float32), folds)
    quad([P(X0, TOPY, Z0), P(X0, TOPY, Z1), P(X1 + 3, TOPY, Z1), P(X1 + 3, TOPY, Z0)], topc)
    # duvet fold line + throw blanket
    quad([P(X0 - 0.02, TOPY + 0.03, 3.2), P(X0 - 0.02, TOPY + 0.03, 3.9), P(X1 + 3, TOPY + 0.03, 3.9), P(X1 + 3, TOPY + 0.03, 3.2)],
         np.array([0.35, 0.55, 0.65], np.float32) * amb)
    quad([P(X0 - 0.02, TOPY + 0.03, 3.2), P(X0 - 0.02, TOPY + 0.03, 3.9), P(X0 - 0.02, 0.2, 3.9), P(X0 - 0.02, 0.2, 3.2)],
         np.array([0.28, 0.46, 0.55], np.float32) * amb)
    # pillows
    for (pz, px0, px1) in ((5.45, 2.5, 3.9), (5.45, 4.0, 5.6)):
        a_, b_ = P(px0, TOPY + 0.32, pz), P(px1, TOPY + 0.05, pz - 0.35)
        pm = Mask().ellipse((a_[0], a_[1], b_[0], b_[1])).get(1.5)
        img = lerp(img, sheet * np.ones((H, W, 3), np.float32) * (0.92 + 0.08 * smooth(b_[1], a_[1], y))[..., None], pm)
    # soft shadow under bed side
    img *= (1 - 0.35 * Mask().poly([P(X0 - 0.3, 0, Z0), P(X0 - 0.3, 0, Z1), P(X0, 0, Z1), P(X0, 0, Z0)]).get(10))[..., None]
    # nightstand + lamp
    ns = [P(1.3, 0.55, 5.9), P(2.05, 0.55, 5.9), P(2.05, 0, 5.9), P(1.3, 0, 5.9)]
    quad(ns, np.array([0.50, 0.34, 0.22], np.float32) * amb)
    lx, ly = P(1.68, 0.55, 5.9)
    shade_top = P(1.68, 1.25, 5.9)
    img = over(img, (120, 100, 80), Mask().line([(lx, ly), (lx, shade_top[1] + 30)], 4).get())
    lamp = Mask().poly([(lx - 26, shade_top[1]), (lx + 26, shade_top[1]), (lx + 40, shade_top[1] + 50), (lx - 40, shade_top[1] + 50)]).get()
    img = lerp(img, np.array([1.0, 0.93, 0.80] if night else [0.96, 0.93, 0.86], np.float32) * np.ones((H, W, 3), np.float32), lamp)
    # potted monstera at left foreground
    pot = Mask().poly([P(-3.4, 0.7, 3.0), P(-2.5, 0.7, 3.0), P(-2.6, 0, 3.0), P(-3.3, 0, 3.0)]).get()
    img = lerp(img, np.array([0.85, 0.83, 0.78], np.float32) * amb * np.ones((H, W, 3), np.float32), pot)
    leaves = Mask()
    r = rng0(78)
    px, py = P(-2.95, 0.7, 3.0)
    for i in range(9):
        a = -math.pi / 2 + r.uniform(-1.2, 1.2)
        ln = r.uniform(160, 320)
        ex, ey = px + math.cos(a) * ln, py + math.sin(a) * ln
        leaves.line([(px, py), (ex, ey)], 4)
        leaves.ellipse((ex - ln * 0.28, ey - ln * 0.2, ex + ln * 0.28, ey + ln * 0.2))
    lcol = gradient([(0, (30, 80, 40)), (1, (70, 130, 60))], fbm(H, W, 40, 3, seed=79))
    img = lerp(img, lcol * amb, leaves.get())
    # painting on left wall
    pq = [P(-XW, 2.4, 3.6), P(-XW, 2.4, 5.4), P(-XW, 1.4, 5.4), P(-XW, 1.4, 3.6)]
    img = over(img, (200, 170, 110), Mask().poly(pq).get())
    inner = [(pq[0][0] + 10, pq[0][1] + 12), (pq[1][0] - 6, pq[1][1] + 8), (pq[2][0] - 6, pq[2][1] - 8), (pq[3][0] + 10, pq[3][1] - 12)]
    art = vgrad([(0, (240, 170, 120)), (0.5, (230, 120, 110)), (0.52, (60, 120, 160)), (1, (40, 80, 120))], y0=min(p[1] for p in inner), y1=max(p[1] for p in inner))
    img = lerp(img, art * amb, Mask().poly(inner).get())
    if not night:
        img = screen(img, (255, 245, 225), radial(VX, wy0 + 200, 1200, power=2) * 0.25)
        img = bloom(img, 0.85, 40, 0.5)
    else:
        # dark ambience + warm lamp pools
        img *= np.array([0.75, 0.78, 0.95], np.float32)
        img = screen(img, (255, 180, 100), radial(lx, shade_top[1] + 60, 700, power=2.2) * 0.65)
        img = screen(img, (255, 210, 140), radial(lx, shade_top[1] + 30, 120, power=1.5) * 0.8)
        # second lamp (floor lamp) on the left
        fx_, fy_ = P(-5.2, 1.7, 5.5)
        bx_, by_ = P(-5.2, 0, 5.5)
        img = over(img, (40, 35, 30), Mask().line([(fx_, fy_), (bx_, by_)], 4).get())
        img = lerp(img, np.array([1.0, 0.9, 0.7], np.float32) * np.ones((H, W, 3), np.float32),
                   Mask().poly([(fx_ - 30, fy_ - 40), (fx_ + 30, fy_ - 40), (fx_ + 45, fy_ + 10), (fx_ - 45, fy_ + 10)]).get())
        img = screen(img, (255, 170, 90), radial(fx_, fy_, 650, power=2.2) * 0.55)
        img = bloom(img, 0.7, 30, 0.7)
    return img


def villa_bedroom_night():
    return villa_bedroom(night=True)


# =============================================================== restaurant terrace
def string_lights(img, night, seed=81):
    x, y = grid()
    r = rng0(seed)
    wire = Mask()
    bulbs = []
    for (ax, ay, bx, by, sag) in ((-50, 60, 980, 120, 120), (940, 110, 1980, 50, 120), (-50, 230, 1980, 210, 90)):
        pts = bezier((ax, ay), ((ax + bx) / 2, (ay + by) / 2 + sag * 2), (bx, by), n=60)
        wire.line(pts, 2)
        for i in range(2, 58, 4):
            bulbs.append(pts[i])
    img = over(img, (30, 22, 20), wire.get() * 0.9)
    bm = Mask()
    for bx, by in bulbs:
        bm.ellipse((bx - 7, by + 2, bx + 7, by + 20))
    bmask = bm.get()
    g = np.zeros((H, W), np.float32)
    for bx, by in bulbs:
        g += radial(bx, by + 11, 70 if night else 50, power=2.2)
    k = 1.0 if night else 0.6
    img = screen(img, (255, 190, 110), np.clip(g, 0, 1) * 0.55 * k)
    img = lerp(img, np.array([1.0, 0.93, 0.75], np.float32) * np.ones((H, W, 3), np.float32), bmask)
    return img


def restaurant(night=False, table=True):
    x, y = grid()
    HZ = 560
    sunx, suny = 1300, HZ - 30
    if not night:
        img = vgrad([(0, (70, 50, 120)), (0.35, (170, 80, 120)), (0.65, (245, 130, 90)),
                     (0.9, (255, 185, 110)), (1, (255, 215, 150))], y0=0, y1=HZ)
        img = sky_clouds(img, 120, HZ - 60, seed=82, color=(255, 175, 140), shade=(140, 70, 110), cover_=0.6, amount=0.75)
        img = screen(img, (255, 200, 120), radial(sunx, suny, 800, power=2.2, sy=0.55) * 0.75)
        img = screen(img, (255, 248, 215), np.clip(radial(sunx, suny, 46, power=0.25) * 1.5, 0, 1))
        img = sea(img, HZ, (200, 110, 90), (60, 40, 70), seed=83, streak=0.25, glint=(sunx, 60, (255, 210, 140), 1.0))
    else:
        img = vgrad([(0, (4, 6, 22)), (0.6, (14, 24, 60)), (1, (34, 52, 100))], y0=0, y1=HZ)
        img = stars(img, (y < HZ - 20).astype(np.float32), n=900, seed=84)
        img = sky_clouds(img, 200, HZ - 60, seed=82, color=(70, 80, 120), shade=(20, 25, 50), cover_=0.66, amount=0.5)
        mx, my = 1350, 200
        img = screen(img, (120, 150, 220), radial(mx, my, 450, power=2.5) * 0.5)
        img = lerp(img, np.array([0.97, 0.96, 0.9], np.float32) * np.ones((H, W, 3), np.float32), np.clip(radial(mx, my, 40, power=0.2) * 1.6, 0, 1))
        img = sea(img, HZ, (20, 35, 70), (6, 12, 30), seed=83, streak=0.25, glint=(mx, 40, (210, 220, 255), 0.9))
    # distant headland
    isl = Mask().poly([(0, HZ + 1), (0, HZ - 40), (160, HZ - 55), (320, HZ - 30), (460, HZ - 12), (560, HZ + 1)]).get(0.8)
    img = lerp(img, np.array([0.25, 0.14, 0.2] if not night else [0.03, 0.05, 0.1], np.float32) * np.ones((H, W, 3), np.float32), isl)
    # deck floor
    DECK = 800
    zz = np.where(y > 470, 1.0 / np.maximum(y - 470, 1), 1e9)
    Xw = (x - 960) * zz
    plank = np.floor(Xw * 5)
    pr = (np.sin(plank * 12.9898) * 43758.5453) % 1.0
    wood = gradient([(0, (110, 65, 40)), (1, (160, 100, 60))], 0.3 + 0.6 * pr)
    wood *= (0.9 + 0.12 * fbm(H, W, 8, 3, seed=85, sx=0.2)[..., None])
    seams = (np.abs(Xw * 5 - np.round(Xw * 5)) < 0.05).astype(np.float32)
    wood = lerp(wood, wood * 0.6, seams)
    if night:
        wood *= np.array([0.45, 0.4, 0.45], np.float32)
    else:
        wood = screen(wood, (255, 170, 100), radial(sunx, DECK, 900, power=2, sy=0.3) * 0.35)
    img = lerp(img, wood, smooth(DECK - 1, DECK + 1, y))
    # railing: posts + top rail + balusters
    rc = np.array([0.95, 0.9, 0.85] if not night else [0.35, 0.3, 0.32], np.float32)
    rail = Mask()
    for bx in range(30, W, 46):
        rail.rect((bx - 4, 690, bx + 4, DECK))
    rail.rect((0, 760, W, 768))
    img = over(img, rc * 0.85 * 255, rail.get())
    top = Mask().rect((0, 676, W, 694)).get()
    topc = vgrad([(0, (255, 235, 210) if not night else (110, 90, 80)), (1, (170, 140, 120) if not night else (50, 40, 40))], y0=676, y1=694)
    img = lerp(img, topc, top)
    for px in (0, 640, 1280, 1920):
        img = over(img, rc * 0.75 * 255, Mask().rect((px - 14, 660, px + 14, DECK)).get())
    # pergola posts
    for px in (70, 1850):
        pm = Mask().rect((px - 24, 0, px + 24, DECK + 40)).get()
        pc = gradient([(0, (70, 45, 30)), (0.5, (120, 80, 50)), (1, (60, 38, 26))], smooth(px - 24, px + 24, x))
        if night:
            pc *= 0.5
        img = lerp(img, pc, pm)
    img = over(img, (60, 40, 28) if not night else (25, 18, 14), Mask().rect((0, 0, W, 26)).get())
    # potted palms / plants silhouettes at sides
    specs = [dict(bx=200, by=860, height=520, lean=0.1, seed=21, fronds=10),
             dict(bx=1720, by=860, height=560, lean=-0.1, seed=22, fronds=10)]
    pcol = (30, 30, 25) if not night else (8, 10, 12)
    img, _ = palm_layer(img, specs, pcol)
    for px in (200, 1720):
        img = over(img, (90, 60, 45) if not night else (35, 25, 22), Mask().poly([(px - 70, 820), (px + 70, 820), (px + 55, 940), (px - 55, 940)]).get())
    img = string_lights(img, night)
    # warm bokeh lights (out-of-focus lanterns)
    r = rng0(86)
    pts = [(r.uniform(0, W), r.uniform(250, 700)) for _ in range(26)]
    cols = [(255, 190, 110) if r.random() > 0.3 else (255, 230, 170) for _ in pts]
    img = bokeh(img, pts, cols, [r.uniform(12, 40) for _ in pts], 0.45 if night else 0.25, 0.5)
    if table:
        img = draw_table(img, night, cx=960, ytop=900, half=520, glasses=False, candles=(700, 1220))
    if night:
        img = screen(img, (255, 160, 80), smooth(500, 1080, y) * 0.12)
    img = bloom(img, 0.7, 30, 0.6 if night else 0.45)
    return img


def candle(img, cx, base_y, h=70, night=False):
    x, y = grid()
    holder = Mask().poly([(cx - 26, base_y), (cx + 26, base_y), (cx + 18, base_y - 14), (cx - 18, base_y - 14)]).get()
    img = over(img, (200, 170, 110), holder)
    body = Mask().rect((cx - 12, base_y - 14 - h, cx + 12, base_y - 14)).get()
    bc = gradient([(0, (220, 210, 190)), (0.4, (255, 250, 235)), (1, (200, 185, 160))], smooth(cx - 12, cx + 12, x))
    img = lerp(img, bc, body)
    fy = base_y - 14 - h
    flame = Mask().poly(bezier((cx, fy - 34), (cx + 14, fy - 4), (cx, fy + 2), n=20) + bezier((cx, fy + 2), (cx - 14, fy - 4), (cx, fy - 34), n=20)).get(0.8)
    img = lerp(img, np.array([1.0, 0.85, 0.45], np.float32) * np.ones((H, W, 3), np.float32), flame)
    img = screen(img, (255, 250, 220), radial(cx, fy - 8, 10, power=0.6))
    img = screen(img, (255, 170, 80), radial(cx, fy - 10, 260 if night else 180, power=2.0) * (0.9 if night else 0.6))
    return img


def wine_glass(img, cx, base_y, h=150, wine=True):
    x, y = grid()
    m = Mask()
    m.ellipse((cx - 30, base_y - 6, cx + 30, base_y + 4))
    m.rect((cx - 2.5, base_y - h * 0.5, cx + 2.5, base_y))
    bowl = bezier((cx - 36, base_y - h), (cx - 40, base_y - h * 0.45), (cx, base_y - h * 0.48), n=20) + \
        bezier((cx, base_y - h * 0.48), (cx + 40, base_y - h * 0.45), (cx + 36, base_y - h), n=20)
    bm = Mask().poly(bowl).get()
    img = screen(img, (255, 245, 235), m.get() * 0.55)
    img = lerp(img, img * 0.85 + np.array([0.12, 0.1, 0.1], np.float32), bm * 0.6)
    if wine:
        wm = Mask().poly([p for p in bowl if p[1] > base_y - h * 0.72]).get()
        img = lerp(img, np.array([0.45, 0.04, 0.10], np.float32) * np.ones((H, W, 3), np.float32), wm * bm * 0.9)
    # rim + highlight
    img = screen(img, (255, 255, 255), Mask().ellipse((cx - 36, base_y - h - 4, cx + 36, base_y - h + 4)).get() * 0.5)
    img = screen(img, (255, 255, 255), Mask().line([(cx - 24, base_y - h * 0.9), (cx - 26, base_y - h * 0.62)], 3).get() * 0.8)
    return img


def plate(img, cx, cy, rx=120, ry=30):
    x, y = grid()
    img = over(img, (120, 110, 105), Mask().ellipse((cx - rx, cy - ry + 6, cx + rx, cy + ry + 6)).get(4) * 0.3)
    img = over(img, (250, 250, 248), Mask().ellipse((cx - rx, cy - ry, cx + rx, cy + ry)).get())
    img = over(img, (225, 225, 222), Mask().ellipse((cx - rx * 0.62, cy - ry * 0.62, cx + rx * 0.62, cy + ry * 0.62)).get())
    # food: a little steak + garnish
    img = over(img, (120, 55, 35), Mask().ellipse((cx - rx * 0.35, cy - ry * 0.45, cx + rx * 0.2, cy + ry * 0.25)).get())
    img = over(img, (60, 140, 50), Mask().circle(cx + rx * 0.3, cy - ry * 0.1, ry * 0.3).get())
    img = over(img, (230, 60, 50), Mask().circle(cx + rx * 0.2, cy + ry * 0.2, ry * 0.18).get())
    return img


def draw_table(img, night, cx=960, ytop=900, half=520, glasses=True, candles=(760, 1160), plates=None):
    x, y = grid()
    # table top (ellipse-ish front edge) + cloth drape to bottom
    top = Mask().poly([(cx - half + 60, ytop), (cx + half - 60, ytop), (cx + half, ytop + 60),
                       (cx + half + 10, H + 10), (cx - half - 10, H + 10), (cx - half, ytop + 60)]).get(0.8)
    cl = vgrad([(0, (252, 250, 245)), (0.25, (240, 236, 228)), (1, (200, 192, 185))], y0=ytop, y1=H)
    folds = 0.5 + 0.5 * np.sin((x - cx) * 0.045 + np.sin(x * 0.01) * 2)
    drape = smooth(ytop + 60, ytop + 90, y)
    cl = cl * (1 - 0.12 * drape * folds)[..., None]
    if night:
        cl *= np.array([0.75, 0.68, 0.62], np.float32)
    else:
        cl = screen(cl, (255, 190, 130), radial(cx + 300, ytop, 700, power=2) * 0.35)
    img = lerp(img, cl, top)
    # table edge highlight
    img = screen(img, (255, 240, 220), Mask().line([(cx - half, ytop + 60), (cx + half, ytop + 60)], 3).get(1) * 0.5)
    if plates:
        for (px, py) in plates:
            img = plate(img, px, py)
    if glasses:
        img = wine_glass(img, cx - 180, ytop + 40)
        img = wine_glass(img, cx + 180, ytop + 40)
    for c in candles:
        img = candle(img, c, ytop + 46, night=night)
    # small flower vase
    img = over(img, (230, 240, 245), Mask().poly([(cx - 18, ytop + 40), (cx + 18, ytop + 40), (cx + 12, ytop - 30), (cx - 12, ytop - 30)]).get() * 0.6)
    fm = Mask()
    for dx, dy in ((-20, -60), (0, -80), (22, -62), (-8, -48), (12, -46)):
        fm.circle(cx + dx, ytop + dy, 14)
    img = over(img, (230, 70, 90), fm.get())
    img = over(img, (255, 220, 120), Mask().circle(cx, ytop - 80, 5).get())
    return img


def restaurant_sunset():
    return restaurant(False)


def restaurant_night():
    return restaurant(True)


SCENES = {'restaurant_sunset': restaurant_sunset, 'restaurant_night': restaurant_night, 'shopping_street': shopping_street, 'villa_bedroom': villa_bedroom, 'villa_bedroom_night': villa_bedroom_night, 'garage': garage, 'coast_road': coast_road, 'resort_hotel': resort_hotel}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        save_rgb(SCENES[n](), os.path.join(BG, n + '.png'))
