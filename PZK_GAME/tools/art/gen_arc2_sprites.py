"""Arc 2 PZK expression variants (delivery uniform + sealed gag), same canvas/alignment as bases."""
from gen_sprites import *
import gen_sprites as gs
from gen_arc2_ui import padlock, cjk

D0, DH = 'sprites/pzk_delivery_normal.png', 'sprites/pzk_delivery_happy.png'
C0 = 'sprites/pzk_casual_normal.png'
HEADS[D0] = HEADS['外卖小哥pzk.PNG']
HEADS[DH] = HEADS['pzk_happy.PNG']
HEADS[C0] = HEADS['pzk-morning.png']


def mirrored_head(name, width):
    d = HEADS[name]
    bx = d['box']; fc = d['face']; (c1, c2) = d['cheeks']
    return dict(box=(width - bx[2], bx[1], width - bx[0], bx[3]), face=(width - fc[2], fc[1], width - fc[0], fc[3]),
                cheeks=((width - c2[0], c2[1]), (width - c1[0], c1[1])))


def on_left(fn, im, name):
    """Head sits near the right canvas edge: apply fn on the mirrored sprite so emotes land on the roomy left side."""
    key = name + '#flip'
    HEADS[key] = mirrored_head(name, im.width)
    out = fn(im.transpose(Image.FLIP_LEFT_RIGHT), key)
    return out.transpose(Image.FLIP_LEFT_RIGHT)


# ------------------------------------------------------------------ new fx
def fx_z(size=60, col=(90, 110, 200)):
    f = font(int(size * SS))
    im, d = canvas(int(size * 1.0) + 20, int(size * 1.2) + 20)
    d.text((10 * SS, 0), 'Z', font=f, fill=col + (255,), stroke_width=int(5 * SS), stroke_fill=(255, 255, 255, 255))
    return tight(down(im))


def fx_bandage(w=120, h=44):
    im, d = canvas(w + 10, h + 10)
    s = SS
    o = 5 * s
    d.rounded_rectangle((o, o, o + w * s, o + h * s), radius=h * 0.45 * s, fill=(225, 175, 140, 255),
                        outline=(170, 120, 95, 255), width=2 * s)
    pw = w * 0.36 * s
    cx = o + w * s / 2
    d.rectangle((cx - pw / 2, o + h * 0.18 * s, cx + pw / 2, o + h * 0.82 * s), fill=(248, 235, 220, 255))
    for i in range(3):
        for j in range(2):
            px = o + w * s * (0.12 + i * 0.05)
            py = o + h * s * (0.38 + j * 0.25)
            for qx in (px, o + w * s - (px - o)):
                d.ellipse((qx - 2 * s, py - 2 * s, qx + 2 * s, py + 2 * s), fill=(185, 135, 105, 255))
    return tight(down(im))


def talisman(w=220, h=520, seed=7):
    """Yellow Taoist paper charm with red brush characters 纯爱封印."""
    S2 = 3
    W2, H2 = w * S2, h * S2
    paper = np.zeros((H2 // S2, W2 // S2, 3), np.float32)
    tex = fbm(h, w, 20, 4, seed=seed)
    fib = fbm(h, w, 3, 2, seed=seed + 1, sx=0.2, sy=3)
    paper[:] = np.array([248, 214, 82], np.float32) / 255
    paper *= (0.9 + 0.1 * tex[..., None]) * (0.96 + 0.06 * fib[..., None])
    # slightly ragged outline
    m = Image.new('L', (W2, H2), 0)
    md = ImageDraw.Draw(m)
    r = np.random.default_rng(seed)
    pts = []
    for t in np.linspace(0, 1, 30):
        pts.append((W2 * t, r.uniform(0, 5) * S2))
    for t in np.linspace(0, 1, 60):
        pts.append((W2 - r.uniform(0, 4) * S2, H2 * t))
    for t in np.linspace(1, 0, 30):
        pts.append((W2 * t, H2 - r.uniform(0, 7) * S2))
    for t in np.linspace(1, 0, 60):
        pts.append((r.uniform(0, 4) * S2, H2 * t))
    md.polygon(pts, fill=255)
    a = np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255
    # red ink layer
    ink = Image.new('L', (W2, H2), 0)
    d = ImageDraw.Draw(ink)
    b = 12 * S2
    d.rectangle((b, b, W2 - b, H2 - b), outline=255, width=4 * S2)
    d.rectangle((b + 9 * S2, b + 9 * S2, W2 - b - 9 * S2, H2 - b - 9 * S2), outline=255, width=2 * S2)
    # top glyph-ish swirl (符头)
    cx = W2 / 2
    d.arc((cx - 40 * S2, b + 20 * S2, cx + 40 * S2, b + 70 * S2), 180, 360, fill=255, width=5 * S2)
    d.line([(cx - 46 * S2, b + 46 * S2), (cx + 46 * S2, b + 46 * S2)], fill=255, width=5 * S2)
    for dx in (-22, 0, 22):
        d.line([(cx + dx * S2, b + 50 * S2), (cx + dx * S2, b + 70 * S2)], fill=255, width=4 * S2)
    # vertical text
    txt = '纯爱封印'
    fs = int(min(w * 0.62, (h - 190) / 4.3))
    f = cjk(fs * S2)
    y = b + 82 * S2
    for ch in txt:
        bb = d.textbbox((0, 0), ch, font=f, stroke_width=2 * S2)
        d.text((cx - (bb[0] + bb[2]) / 2, y - bb[1]), ch, font=f, fill=255, stroke_width=2 * S2, stroke_fill=255)
        y += (bb[3] - bb[1]) + 10 * S2
    # brush tail squiggle at bottom
    tail = bezier((cx, y), (cx + 40 * S2, y + 20 * S2), (cx - 30 * S2, y + 40 * S2), (cx + 10 * S2, H2 - b - 16 * S2), n=30)
    d.line(tail, fill=255, width=5 * S2, joint='curve')
    ia = np.asarray(ink.resize((w, h), Image.LANCZOS), np.float32) / 255
    ia = ia * (0.75 + 0.25 * smooth(0.2, 0.5, fbm(h, w, 5, 3, seed=seed + 2)))
    red = np.array([200, 30, 30], np.float32) / 255
    rgb = paper * (1 - ia[..., None]) + red * ia[..., None]
    # slight crease + top shade
    yy = np.arange(h)[:, None] / h
    rgb *= (1 - 0.05 * np.exp(-((yy - 0.48) / 0.01) ** 2))[..., None]
    rgb *= (0.92 + 0.08 * smooth(0, 0.1, yy))[..., None]
    out = Image.fromarray(np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8), (a * 255).astype(np.uint8)]))
    return out


def e_sealed(im, cx, top, w, h, angle=-6):
    """Stick a talisman over the waist with a glowing blue padlock + a bit of tape."""
    t = talisman(w, h)
    t = t.rotate(angle, resample=Image.BICUBIC, expand=True)
    # drop shadow
    sh = Image.new('RGBA', t.size, (0, 0, 0, 0))
    sh.putalpha(t.getchannel('A').point(lambda v: int(v * 0.35)).filter(ImageFilter.GaussianBlur(8)))
    put(im, sh, cx + 8, top + t.height / 2 + 10)
    put(im, t, cx, top + t.height / 2)
    # tape strip on top
    tw, th = int(w * 0.55), int(w * 0.16)
    tape = Image.new('RGBA', (tw, th), (245, 245, 235, 170))
    put(im, tape, cx + math.sin(math.radians(angle)) * -h * 0.5 + 0, top + th * 0.6, angle=angle + 8)
    # glowing padlock near the lower right corner of the charm
    lk = padlock(False)
    ls = int(w * 0.75)
    lk = lk.resize((ls, ls), Image.LANCZOS)
    pad = Image.new('RGBA', (ls + 40, ls + 40), (0, 0, 0, 0)); pad.paste(lk, (20, 20))
    lk = glow_under(pad, (80, 200, 255), grow=2, radius=9, strength=0.7)
    put(im, lk, cx + w * 0.42, top + h * 0.78)
    return im


def e_z(im, name, k=3):
    """Floating Z's to the upper-left of the head."""
    d, x0, y0, x1, y1, hw, hh = H_(name)
    for i, (dx, dy, s) in enumerate(((0.10, 0.40, 0.26), (0.36, 0.20, 0.20), (0.56, 0.04, 0.15))[:k]):
        put(im, fx_z(int(hw * s)), x0 - hw * dx, y0 + hh * dy + hw * 0.08, angle=12 - i * 8)
    return im


def tired(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    im = grade_fig(im, (0.97, 0.97, 1.02), sat=0.72, bright=0.93)
    fx0, fy0, fx1, fy1 = d['face']
    # dark eye-bag tint under eyes
    for (cx, cy) in d['cheeks']:
        im = tint_region(im, (cx - hw * 0.09, cy - hh * 0.10, cx + hw * 0.09, cy - hh * 0.03), (90, 60, 110), 0.25, blur_r=6)
    # bandage on the right cheek (viewer's right)
    cx, cy = d['cheeks'][1]
    put(im, fx_bandage(int(hw * 0.2), int(hw * 0.075)), cx + hw * 0.01, cy + hh * 0.03, angle=-25)
    im = e_sweat(im, name, 1, side=-1)
    return e_z(im, name)


def smug(im, name):
    im = rim_light(im, (255, 240, 190), 6, 0.5)
    im = glow_under(im, (255, 225, 140), grow=6, radius=22, strength=0.55)
    return e_sparkles(im, name, 6, 9, col=(255, 255, 240), glow=(255, 210, 90), spread=1.1)


def build():
    save(on_left(e_gloom, base(D0), D0), 'pzk_delivery_gloom.png')
    save(on_left(e_shock, base(D0), D0), 'pzk_delivery_shock.png')
    save(on_left(lambda im, n: e_hearts(e_blush(im, n), n), base(D0), D0), 'pzk_delivery_shy.png')
    save(tired(base(D0), D0), 'pzk_delivery_tired.png')
    save(smug(base(DH), DH), 'pzk_delivery_smug.png')
    save(e_sealed(base(D0), 690, 1810, 260, 580), 'pzk_delivery_sealed.png')
    save(e_sealed(base(C0), 470, 1040, 150, 340, angle=5), 'pzk_casual_sealed.png')


if __name__ == '__main__':
    build()
