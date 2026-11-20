"""Sprite expression variants: manga emote overlays on the base sprites (same canvas/alignment)."""
import shutil
from artlib import *
from PIL import ImageFont

SS = 4  # supersampling for fx drawing

# head bounding boxes (canvas coords) located by visual inspection of the bases
DELIV = dict(box=(730, 10, 1250, 560), face=(830, 230, 1150, 560), cheeks=((885, 440), (1105, 440)))
HEADS = {
    'pzk-morning.png': dict(box=(360, 40, 640, 345), face=(395, 150, 605, 345), cheeks=((445, 262), (560, 258))),
    'pzk-morning-damn.png': dict(box=(420, 45, 660, 345), face=(440, 130, 640, 350), cheeks=((468, 238), (602, 232))),
    'pzk-surfing.png': dict(box=(355, 75, 585, 330), face=(390, 170, 575, 330), cheeks=((425, 270), (545, 265))),
    'pzk-surfing-laugh.png': dict(box=(350, 80, 580, 345), face=(385, 180, 570, 345), cheeks=((420, 280), (545, 275))),
    'yyl-girl.png': dict(box=(395, 75, 575, 290), face=(405, 130, 570, 290), cheeks=((430, 236), (545, 231)), fxscale=1.3),
    '外卖小哥pzk.PNG': DELIV, 'pzk_happy.PNG': DELIV, 'pzk_angry.PNG': DELIV,
}


def font(size):
    for p in ('/System/Library/Fonts/Supplemental/Arial Black.ttf',
              '/System/Library/Fonts/Supplemental/Arial Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def canvas(w, h):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def down(im):
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)


def tight(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


# ------------------------------------------------------------------ fx primitives (RGBA, tight)
def fx_sweat(size=80):
    w, h = int(size * 0.7), size
    im, d = canvas(w + 8, h + 8)
    s = SS
    cx = (w + 8) / 2 * s
    top = 4 * s
    r = w / 2 * s
    cy = (h + 4) * s - r
    pts = bezier((cx, top), (cx + r * 0.2, cy - r * 0.9), (cx + r, cy), n=30) + \
        [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, math.pi, 30)] + \
        bezier((cx - r, cy), (cx - r * 0.2, cy - r * 0.9), (cx, top), n=30)
    d.polygon(pts, fill=(70, 140, 220, 255))
    inner = [(cx + (px - cx) * 0.82, cy + (py - cy) * 0.86 + r * 0.08) for px, py in pts]
    d.polygon(inner, fill=(165, 220, 255, 255))
    d.ellipse((cx - r * 0.45, cy - r * 0.35, cx - r * 0.1, cy + r * 0.25), fill=(255, 255, 255, 235))
    d.ellipse((cx + r * 0.15, cy + r * 0.35, cx + r * 0.35, cy + r * 0.55), fill=(255, 255, 255, 200))
    return tight(down(im))


def fx_anger(size=90):
    im, d = canvas(size + 10, size + 10)
    s = SS
    c = (size + 10) / 2 * s
    R = size * 0.46 * s
    gap = size * 0.09 * s
    wid = int(size * 0.13 * s)
    for col, ww in (((120, 0, 10, 255), wid + int(size * 0.07 * s)), ((235, 40, 40, 255), wid)):
        for qx, qy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            # each quadrant: curved bracket bulging toward the centre
            p0 = (c + qx * gap, c + qy * R)
            p1 = (c + qx * gap * 1.2, c + qy * gap * 1.2)
            p2 = (c + qx * R, c + qy * gap)
            pts = bezier(p0, (c + qx * gap * 0.6, c + qy * gap * 0.6), p2, n=30)
            d.line(pts, fill=col, width=ww, joint='curve')
            for p in (pts[0], pts[-1]):
                d.ellipse((p[0] - ww / 2, p[1] - ww / 2, p[0] + ww / 2, p[1] + ww / 2), fill=col)
    return tight(down(im))


def fx_sparkle(size=60, col=(255, 255, 255), glow=(255, 230, 120)):
    n = size + 20
    im, d = canvas(n, n)
    s = SS
    c = n / 2 * s
    r = size / 2 * s
    g = Image.new('L', im.size, 0)
    gd = ImageDraw.Draw(g)
    gd.ellipse((c - r * 0.55, c - r * 0.55, c + r * 0.55, c + r * 0.55), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(r * 0.3))
    glow_l = Image.new('RGBA', im.size, glow + (0,))
    glow_l.putalpha(g.point(lambda v: int(v * 0.8)))
    im.alpha_composite(glow_l)
    t = r * 0.16
    star = [(c, c - r), (c + t, c - t), (c + r, c), (c + t, c + t), (c, c + r), (c - t, c + t), (c - r, c), (c - t, c - t)]
    d.polygon(star, fill=glow + (255,))
    star2 = [(c + (px - c) * 0.78, c + (py - c) * 0.78) for px, py in star]
    d.polygon(star2, fill=col + (255,))
    return tight(down(im))


def fx_heart(size=60, col=(255, 90, 140)):
    n = size + 8
    im, d = canvas(n, n)
    s = SS
    cx, cy = n / 2 * s, n / 2 * s
    r = size / 2 * s
    pts = []
    for t in np.linspace(0, 2 * math.pi, 120):
        xx = 16 * math.sin(t) ** 3
        yy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + xx / 17 * r, cy - yy / 17 * r))
    d.polygon(pts, fill=(200, 40, 90, 255))
    d.polygon([(cx + (px - cx) * 0.86, cy + (py - cy) * 0.86) for px, py in pts], fill=col + (255,))
    d.ellipse((cx - r * 0.62, cy - r * 0.55, cx - r * 0.28, cy - r * 0.2), fill=(255, 255, 255, 220))
    return tight(down(im))


def fx_blush(w=120, h=50):
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).ellipse((20, 20, 20 + w, 20 + h), fill=205)
    m = m.filter(ImageFilter.GaussianBlur(h * 0.25))
    col = Image.new('RGBA', im.size, (255, 105, 130, 0))
    col.putalpha(m)
    im.alpha_composite(col)
    # hatch lines
    big, d = canvas(w + 40, h + 40)
    s = SS
    for i in range(3):
        x0 = (20 + w * (0.28 + i * 0.2)) * s
        d.line([(x0 + h * 0.18 * s, (20 + h * 0.25) * s), (x0 - h * 0.18 * s, (20 + h * 0.75) * s)],
               fill=(235, 60, 100, 200), width=int(max(2, w * 0.035) * s))
    im.alpha_composite(down(big))
    return im


def fx_exclaim(size=110, col=(230, 30, 40)):
    w, h = int(size * 0.45), size
    im, d = canvas(w + 16, h + 16)
    s = SS
    cx = (w + 16) / 2 * s
    o = 8 * s
    bar = [(cx - w * 0.38 * s, o), (cx + w * 0.38 * s, o), (cx + w * 0.18 * s, o + h * 0.68 * s), (cx - w * 0.18 * s, o + h * 0.68 * s)]
    dot = (cx - w * 0.22 * s, o + h * 0.78 * s, cx + w * 0.22 * s, o + h * s)
    ow = 6 * s
    d.polygon([(bar[0][0] - ow, bar[0][1] - ow), (bar[1][0] + ow, bar[1][1] - ow), (bar[2][0] + ow, bar[2][1] + ow), (bar[3][0] - ow, bar[3][1] + ow)], fill=(255, 255, 255, 255))
    d.ellipse((dot[0] - ow, dot[1] - ow, dot[2] + ow, dot[3] + ow), fill=(255, 255, 255, 255))
    d.polygon(bar, fill=col + (255,))
    d.ellipse(dot, fill=col + (255,))
    return tight(down(im))


def fx_question(size=110, col=(40, 40, 50)):
    f = font(int(size * SS))
    im, d = canvas(int(size * 0.9) + 20, int(size * 1.3) + 20)
    d.text((10 * SS, 0), '?', font=f, fill=col + (255,), stroke_width=int(6 * SS), stroke_fill=(255, 255, 255, 255))
    return tight(down(im))


def fx_note(size=90, col=(200, 90, 220)):
    im, d = canvas(size + 20, size + 20)
    s = SS
    o = 10 * s
    sz = size * s
    hw = 6 * s
    # double note (beamed)
    for k, (hx, hy) in enumerate(((0.28, 0.82), (0.78, 0.70))):
        cx, cy = o + sz * hx, o + sz * hy
        rx, ry = sz * 0.16, sz * 0.11
        d.ellipse((cx - rx - hw, cy - ry - hw, cx + rx + hw, cy + ry + hw), fill=(255, 255, 255, 255))
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col + (255,))
        d.line([(cx + rx - 3 * s, cy), (cx + rx - 3 * s, o + sz * (0.12 if k == 0 else 0.02))], fill=col + (255,), width=int(sz * 0.06))
    d.polygon([(o + sz * 0.42, o + sz * 0.1), (o + sz * 0.92, o), (o + sz * 0.92, o + sz * 0.13), (o + sz * 0.42, o + sz * 0.23)], fill=col + (255,))
    return tight(down(im))


def fx_flower(size=70, petal=(255, 150, 190), centre=(255, 210, 80)):
    n = size + 10
    im, d = canvas(n, n)
    s = SS
    c = n / 2 * s
    r = size / 2 * s
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        px, py = c + math.cos(a) * r * 0.5, c + math.sin(a) * r * 0.5
        d.ellipse((px - r * 0.48, py - r * 0.48, px + r * 0.48, py + r * 0.48), fill=(230, 100, 150, 255))
        d.ellipse((px - r * 0.42, py - r * 0.42, px + r * 0.42, py + r * 0.42), fill=petal + (255,))
    d.ellipse((c - r * 0.26, c - r * 0.26, c + r * 0.26, c + r * 0.26), fill=centre + (255,))
    return tight(down(im))


def fx_dots(w=170, h=110):
    im, d = canvas(w + 40, h + 50)
    s = SS
    box = (8 * s, 8 * s, (w + 8) * s, (h + 8) * s)
    tail = [((w * 0.2 + 8) * s, (h * 0.75 + 8) * s), ((w * 0.38 + 8) * s, (h * 0.8 + 8) * s), (2 * s, (h + 40) * s)]
    d.polygon(tail, fill=(40, 40, 50, 255))
    d.ellipse((box[0] - 5 * s, box[1] - 5 * s, box[2] + 5 * s, box[3] + 5 * s), fill=(40, 40, 50, 255))
    d.ellipse(box, fill=(255, 255, 255, 255))
    d.polygon([(tail[0][0] + 6 * s, tail[0][1] - 6 * s), (tail[1][0] - 4 * s, tail[1][1] - 8 * s), (tail[2][0] + 7 * s, tail[2][1] - 9 * s)], fill=(255, 255, 255, 255))
    for i in range(3):
        cx = (8 + w * (0.3 + 0.2 * i)) * s
        cy = (8 + h * 0.52) * s
        rr = h * 0.08 * s
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(30, 30, 40, 255))
    return tight(down(im))


def fx_shock_lines(r0=150, r1=260, n=26, seed=3, col=(20, 20, 30)):
    size = int(r1 * 2 + 20)
    im, d = canvas(size, size)
    s = SS
    c = size / 2 * s
    r = np.random.default_rng(seed)
    for i in range(n):
        a = i * 2 * math.pi / n + r.uniform(-0.08, 0.08)
        a0 = r0 * r.uniform(0.95, 1.1) * s
        a1 = r1 * r.uniform(0.75, 1.0) * s
        wd = r.uniform(4, 9) * s
        p0 = (c + math.cos(a) * a0, c + math.sin(a) * a0)
        p1 = (c + math.cos(a) * a1, c + math.sin(a) * a1)
        nx, ny = -math.sin(a), math.cos(a)
        d.polygon([(p0[0], p0[1]), (p1[0] + nx * wd, p1[1] + ny * wd), (p1[0] - nx * wd, p1[1] - ny * wd)], fill=col + (255,))
    return down(im)


def fx_gloom_lines(w=200, h=160, col=(110, 60, 160)):
    im, d = canvas(w, h)
    s = SS
    r = np.random.default_rng(5)
    n = 9
    for i in range(n):
        x0 = (w * (i + 0.5) / n + r.uniform(-4, 4)) * s
        ln = h * r.uniform(0.55, 1.0) * s
        d.line([(x0, 0), (x0, ln)], fill=col + (230,), width=int(r.uniform(3, 6) * s))
    im = down(im)
    a = np.asarray(im, np.float32)
    fade = np.linspace(1, 0.15, im.height)[:, None]
    a[..., 3] *= fade
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


# ------------------------------------------------------------------ helpers
def put(base, fx, cx, cy, angle=0, opacity=1.0):
    """Paste fx centred at (cx, cy) onto base RGBA (in place)."""
    if angle:
        fx = fx.rotate(angle, resample=Image.BICUBIC, expand=True)
    if opacity < 1:
        a = fx.getchannel('A').point(lambda v: int(v * opacity))
        fx = fx.copy()
        fx.putalpha(a)
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer.paste(fx, (int(cx - fx.width / 2), int(cy - fx.height / 2)), fx)
    base.alpha_composite(layer)
    return base


def alpha_of(im):
    return np.asarray(im.getchannel('A'), np.float32) / 255.0


def glow_under(base, col, grow=10, radius=18, strength=0.9):
    a = alpha_of(base)
    g = ndimage.maximum_filter(a, size=grow * 2 + 1)
    g = ndimage.gaussian_filter(g, radius)
    g = np.clip(g * strength * 1.4, 0, 1)
    lay = np.zeros(a.shape + (4,), np.float32)
    lay[..., :3] = np.array(col, np.float32)
    lay[..., 3] = g * 255
    under = Image.fromarray(lay.astype(np.uint8), 'RGBA')
    under.alpha_composite(base)
    return under


def rim_light(base, col, width=6, strength=0.8):
    a = alpha_of(base)
    inner = ndimage.minimum_filter(a, size=width * 2 + 1)
    edge = np.clip(a - inner, 0, 1)
    edge = ndimage.gaussian_filter(edge, 2) * a
    arr = np.asarray(base, np.float32).copy()
    c = np.array(col, np.float32)
    k = (edge * strength)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - k) + c * k
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def tint_region(base, box, col, amount, vertical_fade=None, ellipse=True, blur_r=20):
    w, h = base.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    (d.ellipse if ellipse else d.rectangle)(box, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur_r))
    mm = np.asarray(m, np.float32) / 255.0
    if vertical_fade is not None:
        y0, y1 = vertical_fade
        yy = np.arange(h, dtype=np.float32)[:, None]
        mm = mm * np.clip((y1 - yy) / (y1 - y0), 0, 1)
    a = alpha_of(base)
    arr = np.asarray(base, np.float32).copy()
    k = (mm * amount)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - k) + np.array(col, np.float32) * k
    arr[..., 3] = a * 255
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def grade_fig(base, mul=(1, 1, 1), sat=1.0, bright=1.0):
    arr = np.asarray(base, np.float32).copy()
    rgb = arr[..., :3] / 255
    l = lum(rgb)[..., None]
    rgb = (l + (rgb - l) * sat) * bright * np.array(mul, np.float32)
    arr[..., :3] = np.clip(rgb, 0, 1) * 255
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')


def clip_to_fig(base, layer):
    """Composite layer over base, but only where base is opaque."""
    a = base.getchannel('A')
    la = np.asarray(layer.getchannel('A'), np.float32) * (np.asarray(a, np.float32) / 255)
    layer = layer.copy()
    layer.putalpha(Image.fromarray(la.astype(np.uint8)))
    out = base.copy()
    out.alpha_composite(layer)
    return out


# ------------------------------------------------------------------ effect appliers
def H_(name):
    d = HEADS[name]
    x0, y0, x1, y1 = d['box']
    k = d.get('fxscale', 1.0)
    return d, x0, y0, x1, y1, (x1 - x0) * k, (y1 - y0) * k


def e_sweat(im, name, n=1, side=1):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    s = int(hw * 0.26)
    put(im, fx_sweat(s), x1 + hw * 0.02 if side > 0 else x0 - hw * 0.02, y0 + hh * 0.30, angle=-12 * side)
    if n > 1:
        put(im, fx_sweat(int(s * 0.7)), x1 + hw * 0.16, y0 + hh * 0.58, angle=-18)
    return im


def e_anger(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    s = int(hw * 0.32)
    put(im, fx_anger(s), x1 - hw * 0.12, y0 + max(s * 0.55, hh * 0.15), angle=10)
    return tint_region(im, d['face'], (255, 60, 50), 0.16, blur_r=hw * 0.1)


def e_blush(im, name, alpha=1.0):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    bw, bh = int(hw * 0.3 / d.get('fxscale', 1.0)), int(hw * 0.14 / d.get('fxscale', 1.0))
    b = fx_blush(bw, bh)
    for cx, cy in d['cheeks']:
        put(im, b, cx, cy, opacity=alpha)
    return im


def e_sparkles(im, name, k=5, seed=0, col=(255, 255, 255), glow=(255, 230, 120), spread=1.0):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    r = np.random.default_rng(seed)
    cx = (x0 + x1) / 2
    W_, H_c = im.size
    spots = [(x0 - hw * 0.35, y0 + hh * 0.25, 0.45), (x1 + hw * 0.35, y0 + hh * 0.15, 0.55),
             (x1 + hw * 0.55, y0 + hh * 0.75, 0.3), (x0 - hw * 0.55, y0 + hh * 0.85, 0.32),
             (x1 + hw * 0.15, y0 - hh * 0.0, 0.25), (x0 - hw * 0.1, y1 + hh * 0.35, 0.22),
             (x1 + hw * 0.7, y1 + hh * 0.3, 0.38)]
    for i in range(min(k, len(spots))):
        sx, sy, sc = spots[i]
        sx = (sx - cx) * spread + cx
        half_ = hw * sc * 0.55
        sx = min(max(sx, half_), W_ - half_)
        sy = max(sy, half_)
        put(im, fx_sparkle(int(hw * sc), col, glow), sx, sy, angle=r.uniform(-10, 10))
    return im


def e_hearts(im, name, k=3):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    spots = [(x1 + hw * 0.25, y0 + hh * 0.2, 0.22, 12), (x1 + hw * 0.45, y0 + hh * 0.5, 0.16, -10),
             (x0 - hw * 0.25, y0 + hh * 0.35, 0.18, -14)]
    for sx, sy, sc, ang in spots[:k]:
        put(im, fx_heart(int(hw * sc)), sx, max(sy, hw * sc * 0.6), angle=ang)
    return im


def e_shock(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lines = fx_shock_lines(int(hw * 0.72), int(hw * 1.25), 28)
    under = Image.new('RGBA', im.size, (0, 0, 0, 0))
    put(under, lines, cx, cy)
    under.alpha_composite(im)
    im = under
    fx0, fy0, fx1, fy1 = d['face']
    im = tint_region(im, (fx0 - 20, y0, fx1 + 20, fy1), (70, 90, 200), 0.42,
                     vertical_fade=(y0, fy0 + (fy1 - fy0) * 0.55), ellipse=False, blur_r=hw * 0.06)
    # vertical shading lines on the forehead
    gl = fx_gloom_lines(int(fx1 - fx0), int((fy1 - fy0) * 0.45), col=(40, 50, 140))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    lay.paste(gl, (int(fx0), int(fy0 - (fy1 - fy0) * 0.1)), gl)
    im = clip_to_fig(im, lay)
    put(im, fx_exclaim(int(hw * 0.5)), min(x1 + hw * 0.3, im.width - hw * 0.15), y0 + hh * 0.25, angle=12)
    return im


def e_gloom(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    im = grade_fig(im, (0.95, 0.92, 1.05), sat=0.65, bright=0.85)
    fx0, fy0, fx1, fy1 = d['face']
    im = tint_region(im, (x0, y0, x1, fy0 + (fy1 - fy0) * 0.5), (80, 40, 120), 0.35,
                     vertical_fade=(y0, fy0 + (fy1 - fy0) * 0.6), ellipse=False, blur_r=hw * 0.06)
    gl = fx_gloom_lines(int(hw * 1.1), int(hh * 0.75), col=(150, 90, 215))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    lay.paste(gl, (int(x0 - hw * 0.05), int(y0 - hh * 0.05)), gl)
    im = clip_to_fig(im, lay)
    im = clip_to_fig(im, lay)
    # a small dark storm cloud with rain lines beside the head
    cl, dd = canvas(int(hw * 0.7), int(hw * 0.6))
    S_ = SS
    cw_ = hw * 0.7 * S_
    for cx_, cy_, rr in ((0.3, 0.3, 0.2), (0.55, 0.22, 0.24), (0.75, 0.33, 0.18), (0.5, 0.38, 0.22)):
        dd.ellipse((cw_ * (cx_ - rr), cw_ * (cy_ - rr * 0.8), cw_ * (cx_ + rr), cw_ * (cy_ + rr * 0.8)), fill=(90, 70, 120, 235))
    for i in range(5):
        xx = cw_ * (0.25 + i * 0.12)
        dd.line([(xx, cw_ * 0.55), (xx - cw_ * 0.05, cw_ * 0.8)], fill=(130, 110, 200, 220), width=int(3 * S_))
    put(im, tight(down(cl)), x1 + hw * 0.45, y0 + hh * 0.3)
    return im


def e_dots(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    b = fx_dots(int(hw * 0.8), int(hw * 0.5))
    put(im, b, x1 + hw * 0.5, y0 + hh * 0.1 + b.height * 0.3)
    return im


def e_note(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    put(im, fx_note(int(hw * 0.42)), x1 + hw * 0.32, y0 + hh * 0.12, angle=-10)
    put(im, fx_note(int(hw * 0.28), (240, 110, 170)), x1 + hw * 0.6, y0 + hh * 0.5, angle=12)
    return im


def e_flowers(im, name):
    d, x0, y0, x1, y1, hw, hh = H_(name)
    for sx, sy, s, c in ((x0 - hw * 0.35, y0 + hh * 0.2, 0.32, (255, 150, 190)),
                         (x1 + hw * 0.38, y0 + hh * 0.1, 0.36, (255, 200, 120)),
                         (x1 + hw * 0.6, y0 + hh * 0.7, 0.26, (180, 150, 255)),
                         (x0 - hw * 0.55, y0 + hh * 0.8, 0.24, (255, 170, 150))):
        put(im, fx_flower(int(hw * s), c), sx, sy)
    return im


def e_cold(im, name):
    im = grade_fig(im, (0.94, 0.98, 1.07), sat=0.9)
    im = rim_light(im, (190, 230, 255), 5, 0.6)
    im = glow_under(im, (110, 180, 255), grow=8, radius=16, strength=0.85)
    return im


def e_glow(im, name):
    im = rim_light(im, (255, 250, 220), 5, 0.55)
    return glow_under(im, (255, 240, 190), grow=6, radius=20, strength=0.6)


def silhouette(im):
    a = im.getchannel('A')
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    black = Image.new('RGBA', im.size, (8, 8, 12, 255))
    out.paste(black, (0, 0), a)
    out.putalpha(a)
    return out


# ------------------------------------------------------------------ build
def base(name):
    return load(name, 'RGBA')


def save(im, fname):
    p = os.path.join(SP, fname)
    im.save(p, optimize=True)
    print('saved sprites/' + fname, im.size)


def copy(src, fname):
    shutil.copyfile(os.path.join(IMG, src), os.path.join(SP, fname))
    print('copied', src, '->', fname)


def build():
    M, MD = 'pzk-morning.png', 'pzk-morning-damn.png'
    S0, SL, SD = 'pzk-surfing.png', 'pzk-surfing-laugh.png', 'pzk-surfing-damn.png'
    D0, DH, DA = '外卖小哥pzk.PNG', 'pzk_happy.PNG', 'pzk_angry.PNG'
    Y = 'yyl-girl.png'
    # casual
    copy(M, 'pzk_casual_normal.png')
    save(e_sparkles(e_glow(base(M), M), M, 6, 1), 'pzk_casual_narcissist.png')
    copy(MD, 'pzk_casual_smug.png')
    save(e_sparkles(base(MD), MD, 6, 2, spread=1.5), 'pzk_casual_proud.png')
    save(e_shock(base(M), M), 'pzk_casual_shock.png')
    save(e_sweat(base(M), M, 2), 'pzk_casual_awkward.png')
    save(e_anger(base(M), M), 'pzk_casual_angry.png')
    save(e_hearts(e_blush(base(M), M), M), 'pzk_casual_shy.png')
    save(e_gloom(base(M), M), 'pzk_casual_gloom.png')
    # surf
    copy(S0, 'pzk_surf_normal.png')
    copy(SL, 'pzk_surf_laugh.png')
    copy(SD, 'pzk_surf_damn.png')
    save(e_sweat(base(SL), SL, 2), 'pzk_surf_awkward.png')
    save(e_shock(base(S0), S0), 'pzk_surf_shock.png')
    save(silhouette(base(S0)), 'pzk_surf_silhouette.png')
    # delivery
    copy(D0, 'pzk_delivery_normal.png')
    copy(DH, 'pzk_delivery_happy.png')
    copy(DA, 'pzk_delivery_silly.png')
    save(e_anger(base(D0), D0), 'pzk_delivery_angry.png')
    save(e_sweat(base(D0), D0, 2, side=-1), 'pzk_delivery_awkward.png')
    save(e_sparkles(base(DH), DH, 6, 3, spread=0.9), 'pzk_delivery_proud.png')
    # yyl
    copy(Y, 'yyl_calm.png')
    save(e_cold(base(Y), Y), 'yyl_cool.png')
    save(e_sparkles(base(Y), Y, 4, 4, col=(255, 255, 245), glow=(255, 210, 230)), 'yyl_smile.png')
    save(e_sweat(e_dots(base(Y), Y), Y, 1, side=-1), 'yyl_speechless.png')
    save(e_note(base(Y), Y), 'yyl_tease.png')
    save(e_shock(base(Y), Y), 'yyl_surprised.png')
    save(e_sparkles(e_flowers(base(Y), Y), Y, 3, 6, glow=(255, 220, 120)), 'yyl_happy.png')
    save(e_hearts(e_blush(base(Y), Y), Y, 2), 'yyl_shy.png')
    save(silhouette(base(Y)), 'yyl_silhouette.png')
    # standalone fx
    fx = {'sweat': fx_sweat(160), 'anger': fx_anger(160), 'sparkle': fx_sparkle(140), 'heart': fx_heart(120),
          'blush': tight(fx_blush(200, 80)), 'exclaim': fx_exclaim(180), 'question': fx_question(180),
          'note': fx_note(150), 'flower': fx_flower(130), 'dots': fx_dots(260, 160),
          'shock_lines': tight(fx_shock_lines(220, 400)), 'gloom': tight(fx_gloom_lines(260, 220))}
    for k, v in fx.items():
        v.save(os.path.join(FX, k + '.png'), optimize=True)
        print('fx', k, v.size)


if __name__ == '__main__':
    build()
