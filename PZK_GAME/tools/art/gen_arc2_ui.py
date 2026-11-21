"""Arc 2 system UI (纯爱致富系统): holographic frames, stamps, icons, overlays -> game/gui/system/."""
import sys
from artlib import *
from PIL import ImageFont

OUT = os.path.join(GAME, 'gui', 'system')
os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(GAME, 'SourceHanSansLite.ttf')

CYAN = np.array([90, 230, 255], np.float32) / 255
CYAN_HI = np.array([210, 250, 255], np.float32) / 255
NAVY = np.array([8, 22, 48], np.float32) / 255


def cjk(size):
    return ImageFont.truetype(FONT, size)


def rgba(rgb, a):
    return Image.fromarray(np.dstack([(np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8),
                                      (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)]))


def comp_layers(layers, h, w):
    """layers: list of (rgb (3,) or HxWx3, alpha HxW), painted in order (normal over)."""
    rgb = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    for c, m in layers:
        c = np.broadcast_to(np.asarray(c, np.float32), (h, w, 3))
        na = m + a * (1 - m)
        rgb = (c * m[..., None] + rgb * a[..., None] * (1 - m[..., None])) / np.maximum(na, 1e-6)[..., None]
        a = na
    return rgb, a


def glow_stack(m, col, radii=((0, 1.0), (3, 0.7), (10, 0.45)), hi=None):
    """Return list of layers for a glowing line mask m."""
    out = []
    for r, k in reversed(radii):
        if r == 0:
            continue
        g = blur(m, r) * k * 2.2
        out.append((col, np.clip(g, 0, 1)))
    out.append((col, np.clip(m, 0, 1)))
    if hi is not None:
        out.append((hi, np.clip(ndimage.grey_erosion(m, size=(2, 2)) * 0.9, 0, 1)))
    return out


def holo_frame(w, h, header=0, bracket=60, border_w=2.2, fill_a=0.80, radius=0, cut=26, seed=1, ticks=True):
    """Holographic translucent window."""
    pad = 0
    x, y = grid(h, w)
    # body shape: rectangle with cut corners (top-left & bottom-right chamfer)
    inset = 14
    c = cut
    pts = [(inset + c, inset), (w - inset, inset), (w - inset, h - inset - c), (w - inset - c, h - inset),
           (inset, h - inset), (inset, inset + c)]
    body = Mask(w, h).poly(pts).get()
    # fill: navy vertical gradient + faint noise + scanlines
    fill = vgrad([(0, (14, 34, 70)), (0.5, (8, 22, 50)), (1, (6, 16, 38))], h, w)
    fill *= (0.92 + 0.12 * fbm(h, w, 80, 3, seed=seed))[..., None]
    scan = (np.sin(y * math.pi / 2.0) > 0.4).astype(np.float32) * 0.035
    fill = fill + scan[..., None] * CYAN
    # inner edge glow
    edge_d = ndimage.distance_transform_edt(body > 0.5)
    inner = np.exp(-edge_d / 18.0) * 0.35
    fill = fill + inner[..., None] * CYAN * 0.5
    # subtle diagonal sheen
    sheen = np.clip(1 - np.abs((x - y * 0.8) - w * 0.25) / (w * 0.18), 0, 1) ** 2 * 0.06
    fill = fill + sheen[..., None]
    alpha_fill = body * (fill_a + inner * 0.3)
    layers = [(fill, alpha_fill)]
    # header band
    if header:
        hb = Mask(w, h).poly([(inset + c, inset), (w - inset, inset), (w - inset, inset + header),
                              (inset, inset + header), (inset, inset + c)]).get() * body
        hcol = vgrad([(0, (30, 90, 150)), (1, (14, 50, 100))], h, w, y0=inset, y1=inset + header)
        layers.append((hcol, hb * 0.55))
        hl = Mask(w, h).line([(inset + 8, inset + header), (w - inset - 8, inset + header)], 1.6).get()
        layers += glow_stack(hl, CYAN, ((0, 1), (4, 0.4)))
        # header decorations: small blocks at right
        dm = Mask(w, h)
        for i in range(4):
            bx = w - inset - 40 - i * 22
            dm.rect((bx, inset + header / 2 - 5, bx + 14, inset + header / 2 + 5))
        layers.append((CYAN, dm.get() * 0.55))
        # a left accent bar
        am = Mask(w, h).rect((inset + c + 10, inset + header * 0.3, inset + c + 16, inset + header * 0.7)).get()
        layers += glow_stack(am, CYAN_HI, ((0, 1), (4, 0.5)))
    # border
    bm = Mask(w, h).line(pts + [pts[0]], border_w).get()
    layers += glow_stack(bm, CYAN, ((0, 1), (3, 0.6), (9, 0.35)))
    # corner brackets (thicker, outside the border)
    br = Mask(w, h)
    o = 4
    L = bracket
    t = 5
    for (cx, cy, sx, sy) in ((o, o, 1, 1), (w - o, o, -1, 1), (o, h - o, 1, -1), (w - o, h - o, -1, -1)):
        br.poly([(cx, cy), (cx + sx * L, cy), (cx + sx * L, cy + sy * t), (cx + sx * t, cy + sy * t),
                 (cx + sx * t, cy + sy * L), (cx, cy + sy * L)])
    layers += glow_stack(br.get(), CYAN_HI, ((0, 1), (4, 0.6), (12, 0.35)))
    # tick marks along bottom edge & sides (small, inside the frame margin region so Frame keeps them near edges)
    if ticks:
        tm = Mask(w, h)
        for i in range(6):
            tx = w * 0.5 - 50 + i * 20
            tm.rect((tx, h - inset - 7, tx + 10, h - inset - 4))
        layers.append((CYAN, tm.get() * 0.7))
    rgb, a = comp_layers(layers, h, w)
    return rgba(rgb, a)


def panel():
    return holo_frame(1100, 760, header=70, bracket=64, cut=30, seed=3)


def card():
    return holo_frame(520, 140, header=0, bracket=30, cut=16, seed=4, fill_a=0.78)


def toast():
    im = holo_frame(900, 110, header=0, bracket=28, cut=18, seed=5, fill_a=0.82, ticks=False)
    # left icon slot: glowing chevrons
    w, h = im.size
    m = Mask(w, h)
    for i in range(3):
        x0 = 34 + i * 14
        m.poly([(x0, 38), (x0 + 8, 38), (x0 + 20, 55), (x0 + 8, 72), (x0, 72), (x0 + 12, 55)])
    rgb, a = comp_layers(glow_stack(m.get(), CYAN_HI, ((0, 1), (4, 0.6))), h, w)
    im.alpha_composite(rgba(rgb, a))
    return im


# ------------------------------------------------------------------ stamps
def stamp(text, w=420, h=220, angle=-8, seed=11, crack=False, size=None):
    S = 3
    big = Image.new('L', (w * S, h * S), 0)
    d = ImageDraw.Draw(big)
    m = 26 * S
    rect = (m, m + 6 * S, w * S - m, h * S - m - 6 * S)
    d.rounded_rectangle(rect, radius=18 * S, outline=255, width=11 * S)
    d.rounded_rectangle((rect[0] + 18 * S, rect[1] + 18 * S, rect[2] - 18 * S, rect[3] - 18 * S),
                        radius=10 * S, outline=255, width=3 * S)
    fs = size or (110 if len(text) <= 2 else 74)
    f = cjk(fs * S)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=3 * S)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    spacing = 0
    if len(text) == 2:
        spacing = 30 * S
    # draw chars individually for spacing
    chars = list(text)
    cw = [d.textbbox((0, 0), ch, font=f, stroke_width=3 * S) for ch in chars]
    total = sum(b[2] - b[0] for b in cw) + spacing * (len(chars) - 1)
    cx = (w * S - total) / 2
    cy = (h * S - th) / 2 - bb[1]
    for ch, b in zip(chars, cw):
        d.text((cx - b[0], cy), ch, font=f, fill=255, stroke_width=3 * S, stroke_fill=255)
        cx += (b[2] - b[0]) + spacing
    if crack:
        r = np.random.default_rng(seed + 5)
        pts = [(w * S * 0.62, rect[1] - 4 * S)]
        yy = rect[1]
        xx = w * S * 0.62
        while yy < rect[3] + 6 * S:
            yy += r.uniform(18, 34) * S
            xx += r.uniform(-26, 26) * S
            pts.append((xx, yy))
        d.line(pts, fill=0, width=10 * S, joint='curve')
        # branch
        k = len(pts) // 2
        d.line([pts[k], (pts[k][0] + 40 * S, pts[k][1] + 18 * S), (pts[k][0] + 62 * S, pts[k][1] + 44 * S)], fill=0, width=6 * S)
    big = big.rotate(angle, resample=Image.BICUBIC)
    a = np.asarray(big.resize((w, h), Image.LANCZOS), np.float32) / 255
    # rough ink: noise erosion + speckles
    n1 = fbm(h, w, 6, 3, seed=seed)
    n2 = fbm(h, w, 40, 3, seed=seed + 1)
    ink = a * smooth(0.18, 0.32, n1 * 0.6 + n2 * 0.4)
    ink = ink * (0.78 + 0.22 * n2)
    rng = np.random.default_rng(seed + 2)
    speck = (rng.random((h, w)) < 0.004).astype(np.float32)
    speck = blur(speck, 0.8) * 3 * smooth(0.2, 0.0, ndimage.distance_transform_edt(a < 0.3) / 30)
    ink = np.clip(ink + speck * 0.6, 0, 1)
    ink = blur(ink, 0.5)
    col = np.array([205, 30, 40], np.float32) / 255
    rgb = np.broadcast_to(col, (h, w, 3)) * (0.85 + 0.15 * n1[..., None])
    return rgba(rgb, ink * 0.95)


# ------------------------------------------------------------------ padlock icons
def padlock(open_=False, w=160, h=160):
    x, y = grid(h, w)
    body = Mask(w, h, 4)
    bx0, by0, bx1, by1 = 34, 72, 126, 142
    body.d.rounded_rectangle((bx0 * 4, by0 * 4, bx1 * 4, by1 * 4), radius=14 * 4, fill=255)
    bm = body.get()
    sh = Mask(w, h, 4)
    lift = -15 if open_ else 0
    sx = 0
    # shackle: arc + legs
    cx = 80
    r = 27
    top = 46 + lift
    arc = [(cx + r * math.cos(t), top + r * -math.sin(t) * 1.0) for t in np.linspace(0, math.pi, 40)]
    leg_r = [(cx + r, top), (cx + r, by0 + 6 if not open_ else top + 14)]
    leg_l = [(cx - r, by0 + 6), (cx - r, top)]
    if open_:
        # rotate shackle slightly open, right leg lifted out
        pts = leg_l + arc[::-1] + [(cx + r, top), (cx + r, top + 12)]
        pts = arc[::-1]
        sh.line([(cx - r, by0 + 4), (cx - r, top)], 12)
        sh.line(pts, 12)
        sh.line([(cx + r, top), (cx + r, top + 10)], 12)
    else:
        sh.line([(cx - r, by0 + 4), (cx - r, top)], 12)
        sh.line(arc[::-1], 12)
        sh.line([(cx + r, top), (cx + r, by0 + 4)], 12)
    shm = sh.get()
    # heart keyhole
    hm = Mask(w, h, 4)
    hp = []
    hcx, hcy, hr = 80, 104, 17
    for t in np.linspace(0, 2 * math.pi, 100):
        xx = 16 * math.sin(t) ** 3
        yy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        hp.append((hcx + xx / 17 * hr, hcy - yy / 17 * hr))
    hm.poly(hp)
    heart = hm.get()
    if not open_:
        main, glowc, hi = CYAN, np.array([60, 200, 255], np.float32) / 255, CYAN_HI
        heartc = np.array([255, 110, 170], np.float32) / 255
    else:
        main = np.array([255, 205, 90], np.float32) / 255
        glowc = np.array([255, 180, 60], np.float32) / 255
        hi = np.array([255, 245, 200], np.float32) / 255
        heartc = np.array([255, 120, 160], np.float32) / 255
    # body fill: translucent with gradient, outlined
    fillc = vgrad([(0, tuple(int(v * 255 * 0.55) for v in main)), (1, tuple(int(v * 255 * 0.25) for v in main))], h, w, y0=by0, y1=by1)
    outline = np.clip(bm - ndimage.grey_erosion(bm, size=(5, 5)), 0, 1)
    layers = []
    shape = np.clip(bm + shm, 0, 1)
    layers.append((glowc, np.clip(blur(shape, 10) * 1.3, 0, 0.75)))
    layers.append((glowc, np.clip(blur(shape, 4) * 1.0, 0, 0.8)))
    layers.append((main * 0.9, shm))
    layers.append((hi, np.clip(shm - ndimage.grey_erosion(shm, size=(5, 5)), 0, 1) * 0.0 + ndimage.grey_erosion(shm, size=(7, 7)) * 0.5))
    layers.append((fillc, bm * 0.92))
    layers.append((hi, outline))
    # scanlines on body
    sl = ((np.sin(y * math.pi / 3) > 0.5) * bm * 0.18).astype(np.float32)
    layers.append((hi, sl))
    layers.append((heartc, np.clip(blur(heart, 5) * 1.6, 0, 0.8)))
    layers.append((heartc, heart))
    layers.append((np.array([1, 1, 1], np.float32), Mask(w, h, 4).circle(75, 98, 3.5).get() * 0.9))
    # body highlight
    layers.append((np.array([1, 1, 1], np.float32), Mask(w, h, 4).rect((bx0 + 8, by0 + 8, bx0 + 13, by1 - 16)).get() * 0.35))
    if open_:
        # sparkles
        sp = Mask(w, h, 4)
        for (px, py, s) in ((128, 34, 13), (24, 52, 9), (140, 74, 7)):
            star4(sp, px, py, s)
        spm = sp.get()
        layers.append((glowc, np.clip(blur(spm, 3) * 1.5, 0, 1)))
        layers.append((hi, spm))
    rgb, a = comp_layers(layers, h, w)
    return rgba(rgb, a)


# ------------------------------------------------------------------ scan frame
def scan_frame(w=700, h=900):
    x, y = grid(h, w)
    m = Mask(w, h)
    L, t, o = 110, 6, 10
    for (cx, cy, sx, sy) in ((o, o, 1, 1), (w - o, o, -1, 1), (o, h - o, 1, -1), (w - o, h - o, -1, -1)):
        m.poly([(cx, cy), (cx + sx * L, cy), (cx + sx * L, cy + sy * t), (cx + sx * t, cy + sy * t),
                (cx + sx * t, cy + sy * L), (cx, cy + sy * L)])
    br = m.get()
    tk = Mask(w, h)
    # tick marks along edges
    for i in range(1, 20):
        ty = o + (h - 2 * o) * i / 20
        ln = 22 if i % 5 == 0 else 10
        tk.rect((o + 2, ty - 1.2, o + 2 + ln, ty + 1.2))
        tk.rect((w - o - 2 - ln, ty - 1.2, w - o - 2, ty + 1.2))
    for i in range(1, 14):
        tx = o + (w - 2 * o) * i / 14
        ln = 22 if i % 7 == 0 else 10
        tk.rect((tx - 1.2, o + 2, tx + 1.2, o + 2 + ln))
        tk.rect((tx - 1.2, h - o - 2 - ln, tx + 1.2, h - o - 2))
    # centre crosshair (small, open)
    cx, cy = w / 2, h * 0.28
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        tk.line([(cx + dx * 18, cy + dy * 18), (cx + dx * 42, cy + dy * 42)], 2.4)
    ring = Mask(w, h)
    ring.d.ellipse(((cx - 30) * 3, (cy - 30) * 3, (cx + 30) * 3, (cy + 30) * 3), outline=255, width=6)
    # dashed arc segments of a larger circle
    for k in range(8):
        a0 = k * 45 + 8
        ring.d.arc(((cx - 64) * 3, (cy - 64) * 3, (cx + 64) * 3, (cy + 64) * 3), a0, a0 + 26, fill=255, width=5)
    # scan line with fading trail above
    sy = h * 0.62
    line = np.exp(-((y - sy) / 1.6) ** 2) * smooth(20, 80, x) * smooth(w - 20, w - 80, x)
    trail = np.clip((sy - y) / 140, 0, 1)
    trail = np.where(y < sy, (1 - trail) ** 2, 0) * 0.22 * smooth(20, 80, x) * smooth(w - 20, w - 80, x)
    # small readout blocks
    rb = Mask(w, h)
    for i in range(5):
        rb.rect((w - o - 120 + i * 20, h - o - 40, w - o - 106 + i * 20, h - o - 32))
    for i, ln in enumerate((90, 60, 75)):
        rb.rect((o + 30, o + 34 + i * 14, o + 30 + ln, o + 38 + i * 14))
    layers = []
    layers.append((CYAN, trail.astype(np.float32)))
    layers += glow_stack(br, CYAN_HI, ((0, 1), (4, 0.6), (12, 0.35)))
    layers += glow_stack(tk.get(), CYAN, ((0, 0.9), (3, 0.4)))
    layers += glow_stack(ring.get() * 0.85, CYAN, ((0, 1), (3, 0.4)))
    layers.append((CYAN, rb.get() * 0.6))
    layers += glow_stack(np.clip(line, 0, 1), CYAN_HI, ((0, 1), (3, 0.7), (10, 0.4)))
    rgb, a = comp_layers(layers, h, w)
    return rgba(rgb, a * 0.95)


# ------------------------------------------------------------------ overlays
def scanlines(w=W, h=H):
    x, y = grid(h, w)
    lines = (np.sin(y * math.pi / 2.0) > 0.3).astype(np.float32)
    a = lines * 0.055
    # occasional brighter band
    band = np.exp(-((y - h * 0.37) / 26) ** 2) * 0.04
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    vig = smooth(0.45, 1.0, d) ** 1.4 * 0.28
    rgb_lines = np.broadcast_to(np.array([0.0, 0.03, 0.08], np.float32), (h, w, 3))
    layers = [(np.array([0.0, 0.02, 0.06], np.float32), vig), (rgb_lines, a),
              (np.array([0.5, 0.9, 1.0], np.float32), band)]
    rgb, al = comp_layers(layers, h, w)
    return rgba(rgb, al)


def glitch(w=W, h=H, seed=21):
    r = np.random.default_rng(seed)
    rgb = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    cols = [(1.0, 0.1, 0.3), (0.1, 1.0, 0.9), (0.2, 0.4, 1.0), (1, 1, 1)]
    # horizontal bars (full or partial width), RGB-split: same bar in R offset and C offset
    for _ in range(46):
        y0 = int(r.uniform(0, h))
        bh = int(r.choice([2, 3, 4, 6, 10, 18, 30, 50]) * r.uniform(0.6, 1.3)) + 1
        x0 = int(r.uniform(-200, w * 0.8))
        bw = int(r.uniform(120, w * 0.9))
        off = int(r.uniform(8, 30))
        al = r.uniform(0.15, 0.5) if bh > 8 else r.uniform(0.35, 0.8)
        for k, c in ((0, (1.0, 0.1, 0.35)), (1, (0.1, 0.95, 1.0))):
            xs = max(0, x0 + (off if k else -off))
            xe = min(w, xs + bw)
            if xe <= xs:
                continue
            sl = (slice(y0, min(h, y0 + bh)), slice(xs, xe))
            # internal stripes texture
            seg = a[sl]
            val = al * (0.6 + 0.4 * r.random((1, xe - xs)))
            cc = np.array(c, np.float32) * (0.75 + 0.25 * r.random((1, xe - xs, 1)))
            na = val + seg * (1 - val)
            rgb[sl] = (cc * val[..., None] + rgb[sl] * (seg * (1 - val))[..., None]) / np.maximum(na, 1e-6)[..., None]
            a[sl] = na
    # blocks
    for _ in range(40):
        bw, bh = int(r.uniform(20, 220)), int(r.uniform(8, 70))
        x0, y0 = int(r.uniform(0, w - bw)), int(r.uniform(0, h - bh))
        c = np.array(cols[r.integers(0, 4)], np.float32)
        al = r.uniform(0.25, 0.7)
        sl = (slice(y0, y0 + bh), slice(x0, x0 + bw))
        rgb[sl] = c
        a[sl] = np.maximum(a[sl], al)
        # pixel noise inside block
    noise = (r.random((h // 4, w // 4)) < 0.012).astype(np.float32)
    noise = np.kron(noise, np.ones((4, 4), np.float32))[:h, :w]
    rgb = rgb * (1 - noise[..., None]) + noise[..., None]
    a = np.maximum(a, noise * 0.6)
    # thin full-width scan bands
    yy = np.arange(h)[:, None]
    bands = ((yy % 3) == 0).astype(np.float32) * 0.06
    rgb = rgb * (1 - bands[..., None]) + np.array([0.3, 0.9, 1.0]) * bands[..., None]
    a = np.maximum(a, np.broadcast_to(bands, (h, w)))
    return rgba(rgb, a)


def coin(w=96, h=96):
    x, y = grid(h, w)
    c = w / 2
    outer = Mask(w, h, 4).circle(c, c, 44).get()
    rim_in = Mask(w, h, 4).circle(c, c, 36).get()
    d = np.sqrt((x - c + 12) ** 2 + (y - c + 14) ** 2) / 70
    gold = gradient([(0, (255, 240, 160)), (0.45, (245, 190, 50)), (1, (170, 105, 20))], np.clip(d, 0, 1))
    gold_in = gradient([(0, (250, 210, 80)), (0.6, (225, 160, 35)), (1, (190, 120, 25))], np.clip(1 - d * 0.9, 0, 1))
    f = cjk(58)
    tm = Image.new('L', (w * 4, h * 4), 0)
    td = ImageDraw.Draw(tm)
    ff = cjk(58 * 4)
    bb = td.textbbox((0, 0), '¥', font=ff, stroke_width=8)
    td.text((w * 2 - (bb[0] + bb[2]) / 2, h * 2 - (bb[1] + bb[3]) / 2), '¥', font=ff, fill=255, stroke_width=8, stroke_fill=255)
    t = np.asarray(tm.resize((w, h), Image.LANCZOS), np.float32) / 255
    tsh = np.roll(np.roll(t, 2, 0), 2, 1)
    layers = [((0.55, 0.32, 0.05), Mask(w, h, 4).circle(c + 1, c + 2, 45).get()),
              (gold, outer), (gold_in, rim_in),
              ((0.55, 0.33, 0.05), np.clip(rim_in - Mask(w, h, 4).circle(c, c, 34.5).get(), 0, 1) * 0.7),
              ((0.6, 0.36, 0.05), tsh * 0.8), ((1.0, 0.93, 0.6), t),
              ((1, 1, 1), Mask(w, h, 4).ellipse((22, 14, 46, 28)).get(2) * 0.55)]
    rgb, a = comp_layers(layers, h, w)
    # little shine star
    return rgba(rgb, a)


ITEMS = {
    'panel': panel, 'card': card, 'toast': toast,
    'stamp_approved': lambda: stamp('报销通过', angle=-8, seed=11),
    'stamp_rejected': lambda: stamp('驳回', angle=7, seed=13, crack=True),
    'seal_icon': lambda: padlock(False), 'seal_icon_open': lambda: padlock(True),
    'scan_frame': scan_frame, 'scanlines': scanlines, 'glitch': glitch, 'coin': coin,
}

if __name__ == '__main__':
    names = sys.argv[1:] or list(ITEMS)
    for n in names:
        im = ITEMS[n]()
        p = os.path.join(OUT, n + '.png')
        im.save(p, optimize=True)
        print('saved gui/system/' + n + '.png', im.size, im.mode, '%.2f MB' % (os.path.getsize(p) / 1e6))
