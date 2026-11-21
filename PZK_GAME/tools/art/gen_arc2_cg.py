"""Arc 2 CGs: scam_night (honey-trap reveal), system_awaken (the system boots in the rental room).
rider_rain lives in gen_arc2_city.py (python3 gen_arc2_city.py rider_rain).
Run: python3 gen_arc2_cg.py [names...]
"""
import sys
from artlib import *
from gen_cg import sprite, comp, layer_of, high_heels
from gen_sprites import rim_light, grade_fig
from gen_arc2_city import C, full, cfont, text_rgba, paste_at, rect_m
import gen_arc2_bg as bg2

rng0 = np.random.default_rng
GUI_SYS = os.path.join(GAME, 'gui', 'system')


# ------------------------------------------------------------------ helpers
def towel_on(im, box, seed=0, keep=None):
    """Draw a white bath towel wrapped around the waist onto sprite im (RGBA PIL, canvas coords)."""
    x0, y0, x1, y1 = box
    w, h = im.size
    S = 3
    m = Image.new('L', (w * S, h * S), 0)
    d = ImageDraw.Draw(m)
    top = bezier((x0, y0 + 30), ((x0 + x1) / 2, y0 - 20), (x1, y0 + 24), n=30)
    right = bezier((x1, y0 + 10), (x1 + 30, (y0 + y1) / 2), (x1 + 45, y1), n=20)
    bottom = bezier((x1 + 45, y1), ((x0 + x1) / 2, y1 + 40), (x0 - 40, y1 - 15), n=30)
    left = bezier((x0 - 40, y1 - 15), (x0 - 25, (y0 + y1) / 2), (x0, y0 + 18), n=20)
    pts = top + right + bottom + left
    d.polygon([(px * S, py * S) for px, py in pts], fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    a = np.asarray(m, np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # terry texture + cylindrical shading + vertical folds
    n = fbm(h, w, 2, 2, seed=seed)
    folds = 0.5 + 0.5 * np.sin((xx - x0) * 0.06 + np.sin(yy * 0.02) * 1.5)
    cyl = np.clip(1 - ((xx - (x0 + x1) / 2) / ((x1 - x0) * 0.62)) ** 2, 0, 1) ** 0.4
    sh = (0.72 + 0.26 * cyl + 0.08 * folds + 0.12 * (n - 0.5))
    sh = sh * (1 - 0.25 * np.clip(1 - (yy - y0) / 40, 0, 1))  # shadow under the shirt hem
    col = np.array([248, 248, 244], np.float32)[None, None, :] * sh[..., None]
    # tucked corner (overlap flap) on the hip
    flap = Image.new('L', (w * S, h * S), 0)
    fx = x0 + (x1 - x0) * 0.68
    ImageDraw.Draw(flap).polygon([(fx * S, (y0 + 4) * S), ((x1 + 40) * S, (y0 + 6) * S), ((x1 + 50) * S, (y1 + 4) * S), ((fx - 60) * S, (y1 + 22) * S)], fill=255)
    fa = np.asarray(flap.resize((w, h), Image.LANCZOS), np.float32) / 255 * a
    edge = np.clip(fa - ndimage.grey_erosion(fa, size=(5, 5)), 0, 1)
    col = col * (1 - 0.35 * blur(edge, 1.5)[..., None])
    col = col * (1 - 0.12 * ndimage.shift(fa, (0, -10), order=1)[..., None] * (1 - fa[..., None]))
    # diagonal tuck crease + folds radiating from the tuck
    cr = Image.new('L', (w * S, h * S), 0)
    dcr = ImageDraw.Draw(cr)
    tx, ty = x0 + (x1 - x0) * 0.72, y0 + 25
    dcr.line([(tx * S, ty * S), ((tx - 70) * S, (y1 + 10) * S)], fill=255, width=5 * S)
    for k, (ex, ey) in enumerate(((tx - 200, y1 - 40), (tx - 320, y1 - 120), (tx + 30, y1 - 30))):
        dcr.line([(tx * S, ty * S), (ex * S, ey * S)], fill=140, width=3 * S)
    cra = np.asarray(cr.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255 * a
    col = col * (1 - 0.3 * cra[..., None])
    # top rolled hem line
    hem = np.clip(1 - np.abs(yy - (y0 + 12 + (xx - x0) * 0) ) / 6, 0, 1) * a
    col = col * (1 - 0.15 * hem[..., None])
    arr = np.asarray(im, np.float32).copy()
    # keep the forearms/hands in front (hands look tucked into the towel)
    skin = keep if keep is not None else np.zeros((h, w), np.float32)
    a = a * (1 - skin)
    # rolled hem band at the top
    hem2 = np.clip(1 - np.abs(yy - (y0 + 22 - 30 * np.clip(1 - ((xx - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2, 0, 1) * 0.0)) / 14, 0, 1)
    col = col * (1 + 0.08 * hem2[..., None]) * (1 - 0.18 * np.clip(1 - np.abs(yy - (y0 + 40)) / 6, 0, 1)[..., None])
    # contact shadow of arms on the towel
    sh_arm = ndimage.gaussian_filter(np.roll(skin, 8, axis=1), 6) * (1 - skin)
    col = col * (1 - 0.35 * sh_arm[..., None])
    arr[..., :3] = arr[..., :3] * (1 - a[..., None]) + col * a[..., None]
    arr[..., 3] = np.maximum(arr[..., 3], a * 255)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def skin_mask(im, boxes):
    arr = np.asarray(im, np.float32)
    r_, g_, b_, a_ = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
    sk = (r_ > g_ + 4) & (g_ >= b_ - 4) & (r_ - b_ > 22) & (r_ > 70) & (a_ > 200)
    reg = np.zeros_like(sk)
    for (x0, x1, y0, y1) in boxes:
        reg[y0:y1, x0:x1] = True
    sk = sk & reg
    sk = ndimage.binary_closing(sk, iterations=4)
    sk = ndimage.binary_fill_holes(sk)
    sk = ndimage.binary_opening(sk, iterations=2)
    lab, n = ndimage.label(sk)
    if n:
        sizes = ndimage.sum(sk, lab, range(1, n + 1))
        sk = np.isin(lab, 1 + np.where(sizes > 800)[0])
    return ndimage.gaussian_filter(sk.astype(np.float32), 1.0)


def silhouette_man(L, cx, by, hgt, pose='stand', seed=0, col=(10, 10, 16)):
    """Stocky man silhouette (jacket, cap optional) into a Layer. Returns anchor points."""
    s = hgt / 1.8
    hr = 0.115 * s
    sh_w = 0.24 * s
    hy = by - hgt + hr
    L.ellipse((cx - hr * 0.95, hy - hr, cx + hr * 0.95, hy + hr * 1.15), col)
    if seed % 2 == 0:  # cap
        L.ellipse((cx - hr * 1.05, hy - hr * 1.1, cx + hr * 1.05, hy + hr * 0.1), col)
        L.poly([(cx, hy - hr * 0.2), (cx + hr * 1.8, hy - hr * 0.05), (cx + hr * 1.6, hy + hr * 0.2), (cx, hy + hr * 0.1)], col)
    L.rect((cx - 0.06 * s, hy + hr * 0.6, cx + 0.06 * s, hy + hr + 0.1 * s), col)
    ty = hy + hr + 0.07 * s
    # shoulders (rounded) + jacket torso flaring slightly at the hem
    L.ellipse((cx - sh_w - 0.05 * s, ty - 0.04 * s, cx - sh_w + 0.15 * s, ty + 0.16 * s), col)
    L.ellipse((cx + sh_w - 0.15 * s, ty - 0.04 * s, cx + sh_w + 0.05 * s, ty + 0.16 * s), col)
    L.poly([(cx - sh_w - 0.03 * s, ty + 0.06 * s), (cx - sh_w * 0.5, ty - 0.03 * s), (cx + sh_w * 0.5, ty - 0.03 * s), (cx + sh_w + 0.03 * s, ty + 0.06 * s),
            (cx + sh_w * 0.95, by - 0.82 * s), (cx - sh_w * 0.95, by - 0.82 * s)], col)
    # legs apart (stance), shoes
    L.poly([(cx - sh_w * 0.85, by - 0.86 * s), (cx - 0.01 * s, by - 0.86 * s), (cx - 0.07 * s, by - 0.03 * s), (cx - sh_w * 1.05, by - 0.03 * s)], col)
    L.poly([(cx + 0.01 * s, by - 0.86 * s), (cx + sh_w * 0.85, by - 0.86 * s), (cx + sh_w * 1.1, by - 0.03 * s), (cx + 0.08 * s, by - 0.03 * s)], col)
    L.ellipse((cx - sh_w * 1.25, by - 0.06 * s, cx - 0.04 * s, by + 0.01 * s), col)
    L.ellipse((cx + 0.05 * s, by - 0.06 * s, cx + sh_w * 1.3, by + 0.01 * s), col)
    if pose == 'stand':
        L.line([(cx - sh_w - 0.0 * s, ty + 0.08 * s), (cx - sh_w - 0.06 * s, by - 0.95 * s)], 0.1 * s, col)
    return dict(head=(cx, hy), shoulder_r=(cx + sh_w - 0.02 * s, ty + 0.07 * s), shoulder_l=(cx - sh_w + 0.02 * s, ty + 0.07 * s), s=s)


def arm(L, p0, p1, wd, col=(10, 10, 16)):
    L.line([p0, p1], wd, col)
    L.circle(p1[0], p1[1], wd * 0.6, col)


def beam(img, p0, p1, w0, w1, col, strength=0.35, blur_r=18):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dl = math.hypot(dx, dy)
    nx, ny = -dy / dl, dx / dl
    m = Mask().poly([(p0[0] + nx * w0, p0[1] + ny * w0), (p1[0] + nx * w1, p1[1] + ny * w1),
                     (p1[0] - nx * w1, p1[1] - ny * w1), (p0[0] - nx * w0, p0[1] - ny * w0)]).get(blur_r)
    x, y = grid()
    t = np.clip(((x - p0[0]) * dx + (y - p0[1]) * dy) / (dl * dl), 0, 1)
    return screen(img, col, m * (1 - 0.6 * t) * strength)


def flash_burst(img, cx, cy, r=260, n=16, seed=0):
    rr = rng0(seed)
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n + rr.uniform(-0.05, 0.05)
        rad = r * rr.uniform(0.75, 1.15) if i % 2 == 0 else r * 0.22
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    m = Mask().poly(pts).get(2)
    img = screen(img, (255, 255, 240), radial(cx, cy, r * 3.5, power=2.6) * 0.6)
    img = screen(img, (255, 255, 255), m * 0.95)
    img = screen(img, (255, 255, 255), radial(cx, cy, r * 0.35, power=0.6))
    # anamorphic streak
    x, y = grid()
    st = np.exp(-((y - cy) / 6) ** 2) * np.clip(1 - np.abs(x - cx) / 1100, 0, 1) ** 2
    img = screen(img, (200, 230, 255), st * 0.8)
    return img


def sfx_text(txt, size, fill, stroke, sw, angle=0):
    t = text_rgba(txt, size, fill, stroke=sw, stroke_col=stroke)
    return t.rotate(angle, resample=Image.BICUBIC, expand=True)


# ------------------------------------------------------------------ scam_night
def scam_night():
    img = bg2.hotel_suite(door_open=True, dim=0.75)
    img = img * 0.5
    x, y = grid()
    cam = Cam_ = bg2.Cam(F=900.0, VX=880.0, VY=500.0, EYE=1.5)
    P = cam.P
    # doorway glow restored (corridor spill), haze
    dcx, dcy = P(-3.6, 1.1, 5.25)
    img = screen(img, (255, 235, 200), radial(dcx, dcy, 800, power=2.2) * 0.35)
    # high heels neatly by the bed (the clue) with a little moonlit spotlight
    hx, hy = P(2.75, 0, 3.25)
    img = screen(img, (170, 190, 240), radial(hx, hy - 20, 230, power=2, sy=0.45) * 0.45)
    img = high_heels(img, hx, hy, s=0.95)
    # three men silhouettes entering from the door (left), backlit
    Lm = bg2.Layer(ss=2)
    men = []
    for k, (X, Z, hgt, pose) in enumerate(((-3.0, 4.4, 1.85, 'stand'), (-2.0, 3.4, 1.78, 'camera'), (-1.05, 2.75, 1.75, 'point'))):
        cx, by = P(X, 0, Z)
        hp = hgt * cam.sc(Z)
        info = silhouette_man(Lm, cx, by, hp, 'stand' if pose == 'stand' else 'none', seed=k)
        info['pose'] = pose
        info['Z'] = Z
        men.append(info)
    # camera man: both arms raised holding a camera at the face
    m2 = men[1]
    s2 = m2['s']
    hx2, hy2 = m2['head']
    cam_pt = (hx2 + 0.18 * s2, hy2 + 0.02 * s2)
    arm(Lm, m2['shoulder_r'], (cam_pt[0], cam_pt[1] + 0.08 * s2), 0.09 * s2)
    arm(Lm, m2['shoulder_l'], (cam_pt[0] - 0.06 * s2, cam_pt[1] + 0.1 * s2), 0.09 * s2)
    Lm.rect((cam_pt[0] - 0.1 * s2, cam_pt[1] - 0.07 * s2, cam_pt[0] + 0.12 * s2, cam_pt[1] + 0.08 * s2), (10, 10, 16))
    Lm.rect((cam_pt[0] + 0.1 * s2, cam_pt[1] - 0.03 * s2, cam_pt[0] + 0.18 * s2, cam_pt[1] + 0.05 * s2), (10, 10, 16))
    # pointing man: right arm stretched toward PZK, left hand with a flashlight
    m3 = men[2]
    s3 = m3['s']
    tip = (m3['shoulder_r'][0] + 0.75 * s3, m3['shoulder_r'][1] - 0.12 * s3)
    arm(Lm, m3['shoulder_r'], tip, 0.1 * s3)
    Lm.poly([(tip[0], tip[1] - 0.025 * s3), (tip[0] + 0.12 * s3, tip[1] - 0.03 * s3), (tip[0] + 0.12 * s3, tip[1]), (tip[0], tip[1] + 0.03 * s3)], (10, 10, 16))
    fl3 = (m3['shoulder_l'][0] - 0.05 * s3, m3['shoulder_l'][1] + 0.45 * s3)
    arm(Lm, m3['shoulder_l'], fl3, 0.1 * s3)
    # first man: flashlight raised
    m1 = men[0]
    s1 = m1['s']
    fl1 = (m1['shoulder_r'][0] + 0.35 * s1, m1['shoulder_r'][1] - 0.05 * s1)
    arm(Lm, m1['shoulder_r'], fl1, 0.09 * s1)
    # flashlight beams (under the silhouettes) aimed at PZK
    target = (1150, 520)
    img = beam(img, fl1, target, 10, 190, (255, 250, 220), 0.55)
    img = beam(img, fl3, (1180, 760), 10, 210, (255, 250, 220), 0.5)
    for fp in (fl1, fl3):
        img = screen(img, (255, 255, 235), radial(fp[0], fp[1], 40, power=1.2))
    # backlit rim on the silhouettes
    lay = Lm.im.resize((W, H), Image.LANCZOS)
    la = np.asarray(lay, np.float32)[..., 3] / 255
    img = lerp(img, full((12, 12, 20)), la)
    rim = np.clip(la - ndimage.shift(la, (2, 4), order=1), 0, 1)
    img = screen(img, (255, 230, 190), blur(rim, 1.2) * 0.8)
    # PZK frozen with a towel (sprite + towel), lit by the flash from the left
    pz = load('sprites/pzk_casual_shock.png', 'RGBA')
    keep = skin_mask(pz, [(200, 360, 980, 1200), (590, 760, 980, 1300)])
    pz = grade_fig(pz, (0.9, 0.92, 1.05), sat=0.85, bright=0.8)
    pz = towel_on(pz, (215, 1030, 755, 1480), seed=3, keep=keep)
    pz = rim_light(pz, (255, 255, 245), 8, 0.7)
    sc = 0.72
    pz = pz.resize((int(pz.width * sc), int(pz.height * sc)), Image.LANCZOS)
    px0, py0 = 1180 - pz.width / 2, 70
    # flash light on him: brighten his left side
    img, pa = comp(img, pz, px0, py0)
    img = screen(img, (255, 255, 250), pa * smooth(px0 + pz.width * 0.75, px0 + pz.width * 0.25, x) * 0.35)
    # camera flash burst
    img = flash_burst(img, cam_pt[0] + 0.22 * s2, cam_pt[1] + 0.01 * s2, r=150, seed=5)
    # comic SFX
    t = sfx_text('咔嚓!', 120, (255, 245, 120), (30, 20, 20), 9, angle=12)
    img, _ = paste_at(img, t, 90, 90)
    t = sfx_text('别动!', 96, (255, 80, 70), (255, 255, 255), 8, angle=-6)
    img, _ = paste_at(img, t, 560, 330)
    # speed/impact lines from the door
    ml = Mask()
    r = rng0(9)
    for _ in range(40):
        a = r.uniform(-0.9, 0.9)
        r0, r1 = r.uniform(500, 650), r.uniform(1100, 1500)
        ml.tapered([(dcx + math.cos(a) * r0, dcy + math.sin(a) * r0), (dcx + math.cos(a) * r1, dcy + math.sin(a) * r1)], 1, r.uniform(4, 9))
    img = screen(img, (255, 250, 230), ml.get(0.5) * 0.25 * (1 - pa))
    img = bloom(img, 0.75, 30, 0.5)
    xx = np.sqrt(((x - 960) / 960) ** 2 + ((y - 540) / 540) ** 2)
    img *= (1 - 0.35 * smooth(0.7, 1.4, xx))[..., None]
    return img


# ------------------------------------------------------------------ system_awaken
def holo_text(txt, size, col=(170, 245, 255), glow=(40, 180, 255)):
    t = text_rgba(txt, size, col)
    pad = int(size * 0.5)
    im = Image.new('RGBA', (t.width + pad * 2, t.height + pad * 2), (0, 0, 0, 0))
    a = t.getchannel('A')
    g = Image.new('L', im.size, 0)
    g.paste(a, (pad, pad))
    g = g.filter(ImageFilter.GaussianBlur(size * 0.12))
    gl = Image.new('RGBA', im.size, glow + (0,))
    gl.putalpha(g.point(lambda v: min(255, int(v * 1.6))))
    im.alpha_composite(gl)
    im.alpha_composite(t, (pad, pad))
    return im


def system_awaken():
    img = bg2.rental_room(night=True)
    x, y = grid()
    # dim pre-dawn blue: desaturate + cool the warm bulb room
    l = lum(img)[..., None]
    img = lerp(img, l * C((90, 140, 230)) * 1.15, 0.7) * 0.88
    # PZK sitting up in bed (left), blanket over legs
    pz = load('sprites/pzk_casual_shock.png', 'RGBA')
    pz = grade_fig(pz, (0.85, 0.95, 1.12), sat=0.8, bright=0.85)
    pz = rim_light(pz, (150, 220, 255), 9, 0.9)
    sc = 0.6
    pz = pz.resize((int(pz.width * sc), int(pz.height * sc)), Image.LANCZOS)
    px0, py0 = 470 - pz.width / 2, 250
    img, pa = comp(img, pz, px0, py0)
    # blanket heap over his lap / legs
    bl = Mask()
    wy = py0 + 1060 * sc
    pts = [(-40, wy + 40), (60, wy - 20), (200, wy - 50), (330, wy - 25), (480, wy - 60), (640, wy - 35), (760, wy + 10),
           (900, wy + 70), (980, wy + 200), (940, H + 20), (-40, H + 20)]
    bl.poly(bezier(pts[0], pts[1], pts[2], n=10) + bezier(pts[2], pts[3], pts[4], n=10) + bezier(pts[4], pts[5], pts[6], n=10) +
            bezier(pts[6], pts[7], pts[8], n=10) + pts[9:])
    bm = bl.get(1.5)
    bc = full((230, 150, 160)) * (0.6 + 0.6 * fbm(H, W, 45, 5, seed=901)[..., None])
    flor = ((np.sin(x * 0.12) * np.sin(y * 0.15 + x * 0.03)) > 0.82).astype(np.float32)
    bc = lerp(bc, full((255, 235, 120)), flor * 0.6)
    l2 = lum(bc)[..., None]
    bc = lerp(bc, l2 * C((90, 140, 230)) * 1.1, 0.65) * 0.75
    img = lerp(img, bc, bm)
    # holographic panel (perspective quad, floating right of him)
    quadp = [(860, 150), (1830, 95), (1850, 790), (880, 760)]
    panel = Image.open(os.path.join(GUI_SYS, 'panel.png')).convert('RGBA')
    pw, ph = panel.size
    # content drawn on the panel canvas
    con = panel.copy()
    t1 = holo_text('纯爱致富系统', 120)
    con.alpha_composite(t1, ((pw - t1.width) // 2, 200))
    t2 = holo_text('PURE-LOVE WEALTH SYSTEM  v1.0', 34, (120, 210, 240))
    con.alpha_composite(t2, ((pw - t2.width) // 2, 360))
    t3 = holo_text('绑定中…', 64, (210, 250, 255))
    con.alpha_composite(t3, ((pw - t3.width) // 2, 450))
    d = ImageDraw.Draw(con)
    bx0, by0, bx1, by1 = 180, 590, pw - 180, 625
    d.rectangle((bx0, by0, bx1, by1), outline=(90, 220, 255, 255), width=3)
    d.rectangle((bx0 + 6, by0 + 6, bx0 + 6 + (bx1 - bx0 - 12) * 0.68, by1 - 6), fill=(90, 220, 255, 230))
    for k in range(int((bx1 - bx0) / 24)):
        xx = bx0 + 6 + k * 24
        if xx < bx0 + (bx1 - bx0) * 0.68:
            d.line([(xx, by1 - 6), (xx + 14, by0 + 6)], fill=(200, 250, 255, 255), width=4)
    t4 = holo_text('68%   宿主: 潘子恺', 36, (150, 230, 255))
    con.alpha_composite(t4, (bx0 - 10, by1 + 10))
    # scanlines over content
    sl = np.asarray(con, np.float32).copy()
    sl[::4, :, 3] *= 0.65
    con = Image.fromarray(sl.astype(np.uint8), 'RGBA')
    # warp and composite (slightly transparent)
    c = bg2.paste_quad  # noqa
    rgb_before = img.copy()
    coeffs = None
    from artlib import _coeffs
    cf = _coeffs(quadp, [(0, 0), (pw, 0), (pw, ph), (0, ph)])
    warped = con.transform((W, H), Image.PERSPECTIVE, cf, Image.BICUBIC)
    wa = np.asarray(warped, np.float32) / 255
    a = wa[..., 3] * 0.88
    # glow from the panel
    pm = Mask().poly(quadp).get()
    img = screen(img, (40, 140, 255), blur(pm, 60) * 0.55)
    img = lerp(img, wa[..., :3], a)
    img = screen(img, (120, 220, 255), np.clip(blur(wa[..., 3] * (lum(wa[..., :3]) > 0.55), 3), 0, 1) * 0.6)
    # room lit by the hologram: blue wash falling to the left
    img = screen(img, (40, 120, 255), radial(1350, 450, 1500, power=1.6) * 0.25)
    # his face/torso catches blue light on the right side
    img = screen(img, (90, 180, 255), pa * smooth(px0 + pz.width * 0.35, px0 + pz.width * 0.8, x) * 0.3)
    # light particles drifting up
    r = rng0(902)
    Lp = bg2.Layer(ss=2)
    gl = np.zeros((H, W), np.float32)
    for _ in range(260):
        px, py = r.uniform(700, 1920), r.uniform(0, H)
        rr = r.uniform(1, 4) * (1 if r.random() > 0.1 else 2.2)
        Lp.circle(px, py, rr, (180, 240, 255), r.uniform(0.4, 1))
        gl[int(py) % H, int(px) % W] += rr
    for _ in range(40):  # little square bits (data)
        px, py = r.uniform(800, 1900), r.uniform(50, 1000)
        s = r.uniform(3, 8)
        Lp.rect((px, py, px + s, py + s), (120, 220, 255), r.uniform(0.3, 0.8))
    img = screen(img, (80, 190, 255), np.clip(blur(gl, 6) * 18, 0, 1) * 0.7)
    lay = Lp.im.resize((W, H), Image.LANCZOS)
    la = np.asarray(lay, np.float32) / 255
    img = screen(img, (1, 1, 1), np.zeros((H, W), np.float32))
    img = 1 - (1 - img) * (1 - la[..., :3] * la[..., 3:4])
    # global scanlines + slight chromatic split near the panel
    img = img * (1 - 0.06 * ((np.arange(H) % 4) < 1)[:, None, None])
    img = bloom(img, 0.6, 30, 0.6)
    # exclamation at him (shock emote already on sprite) + vignette
    xx = np.sqrt(((x - 960) / 960) ** 2 + ((y - 540) / 540) ** 2)
    img *= (1 - 0.4 * smooth(0.6, 1.4, xx))[..., None]
    return img


SCENES = {'scam_night': scam_night, 'system_awaken': system_awaken}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        save_rgb(SCENES[n](), os.path.join(CG, n + '.png'), warm=0.4 if n == 'system_awaken' else 1.0)
