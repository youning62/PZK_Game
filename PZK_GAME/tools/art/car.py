"""Stylized bright-blue wedge supercar (side view), no logos."""
from artlib import *

FW = (205, 270)  # front wheel centre (local units)
RW = (795, 270)
TR = 70          # tyre radius
GROUND = 340


def arch(c, r, base=300):
    """Angular (hexagonal) arch outline around wheel c, from rear base point to front base point."""
    cx, cy = c
    return [(cx + r * 1.12, base), (cx + r * 1.08, cy - r * 0.55), (cx + r * 0.55, cy - r * 1.08),
            (cx - r * 0.55, cy - r * 1.08), (cx - r * 1.08, cy - r * 0.55), (cx - r * 1.12, base)]


TOP = [(0, 246), (8, 226), (210, 172), (400, 130), (565, 84), (690, 78), (830, 98),
       (960, 124), (1004, 130), (1000, 170), (992, 250), (970, 292), (885, 296)]
BODY = TOP + arch(RW, 84, 296) + [(332, 298)] + arch(FW, 80, 298) + [(30, 290), (6, 268)]
FULL = TOP + [(30, 298)]
GLASS = [(415, 150), (566, 92), (690, 86), (770, 108), (735, 150)]
SCOOP = [(300, 262), (560, 196), (712, 168), (712, 290), (332, 296)]
INTAKE = [(600, 196), (712, 170), (712, 250), (640, 252)]
SKIRT = [(332, 284), (712, 284), (712, 298), (332, 300)]
SPLIT = [(14, 282), (112, 290), (112, 299), (30, 297)]


def render(x0, y0, sc, mode='garage', flip=False, w=W, h=H):
    """Returns (rgb, alpha) full-canvas layers. mode: 'garage' or 'golden'."""
    def T(pts):
        out = []
        for u, v in pts:
            if flip:
                u = 1004 - u
            out.append((x0 + u * sc, y0 + v * sc))
        return out

    x, y = grid(h, w)
    v = (y - y0) / sc
    u = (x - x0) / sc
    if flip:
        u = 1004 - u
    rgb = np.zeros((h, w, 3), np.float32)
    alpha = np.zeros((h, w), np.float32)

    def put(mask, col):
        nonlocal rgb, alpha
        col = np.asarray(col, np.float32)
        if col.ndim == 1:
            col = col / 255.0 if col.max() > 1 else col
        rgb = rgb * (1 - mask[..., None]) + col * mask[..., None]
        alpha = alpha + mask * (1 - alpha)

    def wheel_pts(c, r, n=48):
        return [(c[0] + r * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]

    # wheel-well darkness
    for c in (FW, RW):
        put(Mask(w, h).poly(T(arch(c, 90, 300))).get() * Mask(w, h).poly(T(FULL)).get(), (6, 8, 14))
    # body
    body = Mask(w, h).poly(T(BODY)).get()
    if mode == 'garage':
        col = gradient([(60, (130, 200, 255)), (110, (40, 130, 255)), (175, (20, 95, 245)),
                        (200, (12, 70, 215)), (260, (6, 45, 160)), (300, (3, 20, 80))], v)
        hl = (235, 245, 255)
    else:
        col = gradient([(60, (255, 200, 150)), (100, (120, 170, 255)), (170, (25, 105, 245)),
                        (200, (14, 75, 210)), (260, (8, 45, 150)), (300, (20, 20, 60))], v)
        hl = (255, 215, 160)
    # long horizontal reflections
    shoulder = np.exp(-((v - (150 + (u - 700) * 0.0)) / 3.5) ** 2) * smooth(700, 760, u) * smooth(990, 900, u)
    col = screen(col, hl, shoulder * 0.9)
    upper = np.exp(-((v - (88 + np.maximum(u - 690, 0) * 0.27)) / 6) ** 2) * smooth(600, 700, u) * smooth(990, 900, u)
    col = screen(col, hl, upper * 0.55)
    hood = np.exp(-((v - (226 - u * 0.25)) / 6) ** 2) * smooth(20, 120, u) * smooth(400, 330, u)
    col = screen(col, hl, hood * 0.7)
    put(body, col)
    sc_m = Mask(w, h).poly(T(SCOOP)).get() * body
    put(sc_m, col * 0.62)
    put(Mask(w, h).line(T([(300, 262), (560, 196), (712, 168)]), 2.5 * sc).get() * body, hl)
    # glass
    g = Mask(w, h).poly(T(GLASS)).get()
    gcol = gradient([(80, (40, 60, 90)), (120, (12, 18, 30)), (156, (5, 8, 14))], v)
    streak = smooth(0.0, 1.0, np.clip(1 - np.abs((u - v * 0.9) - 520) / 40, 0, 1))
    gcol = screen(gcol, (190, 220, 255) if mode == 'garage' else (255, 200, 150), streak * 0.35)
    put(g * body, gcol)
    # pillar line
    put(Mask(w, h).line(T([(640, 88), (650, 150)]), 5 * sc).get(), (8, 40, 120))
    # intake with slats
    it = Mask(w, h).poly(T(INTAKE)).get()
    slats = (np.sin(v * 0.6) > 0.3).astype(np.float32) * 0.25
    put(it, np.stack([0.02 + slats * 0.3, 0.03 + slats * 0.3, 0.05 + slats * 0.35], -1))
    # skirt + splitter
    put(Mask(w, h).poly(T(SKIRT)).get(), (8, 10, 16))
    put(Mask(w, h).poly(T(SPLIT)).get(), (8, 10, 16))
    # panel / door lines
    for pts in ([(420, 160), (430, 280)], [(735, 150), (760, 112)]):
        put(Mask(w, h).line(T(pts), 2.2 * sc).get() * 0.7, (4, 25, 90))
    # headlight + taillight
    put(Mask(w, h).poly(T([(18, 236), (150, 205), (168, 212), (36, 244)])).get(), (215, 240, 255))
    put(Mask(w, h).poly(T([(950, 136), (1003, 140), (1001, 156), (945, 150)])).get(), (230, 20, 30))
    # side mirror
    put(Mask(w, h).poly(T([(425, 146), (465, 138), (472, 152), (432, 158)])).get(), (14, 80, 220))
    # wheels
    for c in (FW, RW):
        put(Mask(w, h).poly(T(wheel_pts(c, TR))).get(), (12, 12, 14))
        rim = Mask(w, h).poly(T(wheel_pts(c, 54))).get()
        cx, cy = T([c])[0]
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (54 * sc)
        rimc = gradient([(0, (60, 64, 72)), (0.7, (30, 32, 38)), (0.95, (120, 126, 140)), (1, (40, 40, 45))], d)
        put(rim, rimc)
        sp = Mask(w, h)
        for k in range(5):
            a = k * 2 * math.pi / 5 + 0.3
            for da in (-0.13, 0.13):
                sp.line(T([(c[0] + 10 * math.cos(a), c[1] + 10 * math.sin(a)),
                           (c[0] + 51 * math.cos(a + da), c[1] + 51 * math.sin(a + da))]), 7 * sc)
        spc = (190, 196, 210) if mode == 'garage' else (230, 200, 170)
        put(sp.get(), spc)
        # caliper
        put(Mask(w, h).poly(T([(c[0] - 42, c[1] - 24), (c[0] - 27, c[1] - 40), (c[0] - 18, c[1] - 33),
                                (c[0] - 31, c[1] - 16)])).get() * 0.95, (250, 200, 20))
        put(Mask(w, h).circle(cx, cy, 9 * sc).get(), (25, 25, 30))
    return rgb, alpha


def reflect(rgb, alpha, ground_y, strength=0.35, blur_r=6):
    """Mirror the car layer below ground_y (for glossy floors / wet sand)."""
    h = rgb.shape[0]
    gy = int(ground_y)
    rr = np.zeros_like(rgb)
    ra = np.zeros_like(alpha)
    n = min(gy, h - gy)
    rr[gy:gy + n] = rgb[gy - n:gy][::-1]
    ra[gy:gy + n] = alpha[gy - n:gy][::-1]
    yy = np.arange(h, dtype=np.float32)[:, None]
    fade = np.clip(1 - (yy - gy) / 260.0, 0, 1) ** 1.5 * (yy >= gy)
    ra = blur(ra, blur_r) * fade * strength
    rr = blur(rr, blur_r)
    return rr, ra
