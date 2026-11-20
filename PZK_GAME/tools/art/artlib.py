"""Shared helpers for procedural art generation (PIL + numpy + scipy)."""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, '..', '..', 'game'))
IMG = os.path.join(GAME, 'images')
BG = os.path.join(IMG, 'bg')
CG = os.path.join(IMG, 'cg')
SP = os.path.join(IMG, 'sprites')
FX = os.path.join(SP, 'fx')
for d in (BG, CG, SP, FX):
    os.makedirs(d, exist_ok=True)

W, H = 1920, 1080


# ---------------------------------------------------------------- basic io
def load(name, mode=None):
    im = Image.open(os.path.join(IMG, name))
    if mode:
        im = im.convert(mode)
    return im


def to_f(im):
    return np.asarray(im.convert('RGB'), dtype=np.float32) / 255.0


def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def cover(im, w=W, h=H, fx=0.5, fy=0.5):
    """Cover-crop image to w:h aspect then resize."""
    sw, sh = im.size
    tr = w / h
    if sw / sh > tr:
        cw, ch = int(sh * tr), sh
    else:
        cw, ch = sw, int(sw / tr)
    x0 = int((sw - cw) * fx)
    y0 = int((sh - ch) * fy)
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- math
def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def grid(h=H, w=W):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x, y


def gradient(stops, t):
    """stops: list of (pos, (r,g,b) 0-255). t: array. returns (...,3) float."""
    t = np.asarray(t, dtype=np.float32)
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([s[1] for s in stops], np.float32) / 255.0
    out = np.empty(t.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(t, pos, cols[:, c])
    return out


def vgrad(stops, h=H, w=W, y0=0, y1=None):
    y1 = h if y1 is None else y1
    t = (np.arange(h, dtype=np.float32) - y0) / max(1, (y1 - y0))
    g = gradient(stops, np.clip(t, 0, 1))
    return np.broadcast_to(g[:, None, :], (h, w, 3)).copy()


def fbm(h, w, scale=200.0, octaves=5, seed=0, sx=1.0, sy=1.0, persist=0.5):
    """Fractal value noise in [0,1]. sx/sy stretch the features."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    s = scale
    for _ in range(octaves):
        gh = max(2, int(h / (s * sy)) + 3)
        gw = max(2, int(w / (s * sx)) + 3)
        g = rng.random((gh, gw)).astype(np.float32)
        z = ndimage.zoom(g, ((h + 2 * s * sy) / gh, (w + 2 * s * sx) / gw), order=3)
        z = z[:h, :w]
        if z.shape != (h, w):
            z = np.pad(z, ((0, h - z.shape[0]), (0, w - z.shape[1])), mode='edge')
        out += amp * z
        tot += amp
        amp *= persist
        s /= 2.0
        if s < 1.5:
            break
    out /= tot
    lo, hi = np.percentile(out, 1), np.percentile(out, 99)
    return np.clip((out - lo) / (hi - lo + 1e-9), 0, 1)


def blur(a, r):
    if r <= 0:
        return a
    if a.ndim == 3:
        return np.stack([ndimage.gaussian_filter(a[..., c], r) for c in range(a.shape[2])], -1)
    return ndimage.gaussian_filter(a, r)


def lerp(a, b, t):
    if np.ndim(t) == 2 and np.ndim(a) == 3:
        t = t[..., None]
    return a + (b - a) * t


def over(base, color, mask):
    """Composite flat color or image onto base using mask (HxW float)."""
    color = np.asarray(color, np.float32)
    if color.ndim == 1 and color.max() > 1.0:
        color = color / 255.0
    return base * (1 - mask[..., None]) + color * mask[..., None]


def add(base, color, mask):
    color = np.asarray(color, np.float32)
    if color.ndim == 1 and color.max() > 1.0:
        color = color / 255.0
    return base + color * mask[..., None]


def screen(base, color, mask):
    color = np.asarray(color, np.float32)
    if color.ndim == 1 and color.max() > 1.0:
        color = color / 255.0
    c = color * mask[..., None]
    return 1 - (1 - base) * (1 - c)


def radial(cx, cy, r, h=H, w=W, power=2.0, sx=1.0, sy=1.0):
    x, y = grid(h, w)
    d = np.sqrt(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2) / r
    return np.clip(1 - d, 0, 1) ** power


def lum(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def saturate(a, s):
    l = lum(a)[..., None]
    return l + (a - l) * s


# ---------------------------------------------------------------- masks
class Mask:
    """Draw anti-aliased shapes at SS x supersampling, get float mask."""

    def __init__(self, w=W, h=H, ss=3):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new('L', (w * ss, h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        s = self.ss
        return [(x * s, y * s) for x, y in pts]

    def poly(self, pts, v=255):
        self.d.polygon(self._p(pts), fill=v)
        return self

    def ellipse(self, box, v=255):
        s = self.ss
        x0, y0, x1, y1 = box
        self.d.ellipse((x0 * s, y0 * s, x1 * s, y1 * s), fill=v)
        return self

    def circle(self, cx, cy, r, v=255):
        return self.ellipse((cx - r, cy - r, cx + r, cy + r), v)

    def rect(self, box, v=255):
        s = self.ss
        x0, y0, x1, y1 = box
        self.d.rectangle((x0 * s, y0 * s, x1 * s, y1 * s), fill=v)
        return self

    def line(self, pts, width, v=255):
        s = self.ss
        self.d.line(self._p(pts), fill=v, width=max(1, int(width * s)), joint='curve')
        for (x, y) in (pts[0], pts[-1]):
            r = width * s / 2
            self.d.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=v)
        return self

    def tapered(self, pts, w0, w1, v=255):
        """Polyline with width tapering from w0 to w1 (as a polygon)."""
        pts = np.asarray(pts, np.float32)
        n = len(pts)
        left, right = [], []
        for i in range(n):
            if i == 0:
                d = pts[1] - pts[0]
            elif i == n - 1:
                d = pts[-1] - pts[-2]
            else:
                d = pts[i + 1] - pts[i - 1]
            d = d / (np.linalg.norm(d) + 1e-9)
            nrm = np.array([-d[1], d[0]])
            wd = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
            left.append(tuple(pts[i] + nrm * wd))
            right.append(tuple(pts[i] - nrm * wd))
        self.poly(left + right[::-1], v)
        return self

    def get(self, blur_r=0):
        im = self.im.resize((self.w, self.h), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255.0
        return blur(a, blur_r) if blur_r else a


def bezier(p0, p1, p2, p3=None, n=40):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(lambda p: np.array(p, np.float32), (p0, p1, p2))
    if p3 is None:
        pts = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
    else:
        p3 = np.array(p3, np.float32)
        pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
    return [tuple(p) for p in pts]


# ---------------------------------------------------------------- scenery
def sky_clouds(img, y0, y1, seed=1, color=(255, 255, 255), amount=0.8, shade=(200, 210, 230),
               cover_=0.55, scale=260, h=H, w=W):
    """Soft cumulus-ish clouds between y0..y1, brighter tops."""
    n = fbm(h, w, scale=scale, octaves=6, seed=seed, sx=2.6, sy=1.0)
    yy = np.arange(h, dtype=np.float32)[:, None]
    band = smooth(y0, y0 + (y1 - y0) * 0.3, yy) * (1 - smooth(y0 + (y1 - y0) * 0.6, y1, yy))
    c = smooth(cover_, cover_ + 0.25, n) * band
    # shading: compare with shifted noise for top lighting
    sh = np.roll(n, -18, axis=0)
    lit = np.clip(0.5 + (n - sh) * 4, 0, 1)
    col = lerp(np.array(shade, np.float32) / 255, np.array(color, np.float32) / 255, lit[..., None])
    return img * (1 - c[..., None] * amount) + col * (c[..., None] * amount)


def sea(img, horizon, top_col, bot_col, seed=3, streak=0.12, glint=None, y1=None, h=H, w=W,
        x0=0, x1=None):
    """Perspective sea from horizon to y1. glint = (cx, width, color, strength)."""
    y1 = h if y1 is None else y1
    x1 = w if x1 is None else x1
    x, y = grid(h, w)
    t = np.clip((y - horizon) / (y1 - horizon), 0, 1)
    base = lerp(np.array(top_col, np.float32) / 255, np.array(bot_col, np.float32) / 255, (t ** 0.6)[..., None])
    # perspective streak texture
    tex = fbm(512, 2048, scale=60, octaves=5, seed=seed, sx=6.0, sy=0.6)
    dy = np.maximum(y - horizon, 0.5)
    v = (2400.0 / dy)
    u = ((x - w / 2) * (dy / 300.0 + 0.15) * 0.6 + 1024)
    s = ndimage.map_coordinates(tex, [v.ravel(), u.ravel()], order=1, mode='mirror').reshape(h, w)
    s = s - 0.5
    nearf = fbm(h, w, 40, 4, seed=seed + 1, sx=3.0) - 0.5
    k = smooth(0.25, 0.8, t)
    s = s * (1 - k) + nearf * k
    out = base * (1 + s[..., None] * streak * 2)
    if glint is not None:
        cx, gw, gcol, gs = glint
        spread = gw * (0.3 + 1.4 * t)
        g = np.exp(-((x - cx) / spread) ** 2) * smooth(0.45, 0.85, s + 0.5 + 0.15 * (1 - t))
        g += 0.35 * np.exp(-((x - cx) / (spread * 1.6)) ** 2) * (1 - t) ** 2
        out = screen(out, gcol, np.clip(g * gs, 0, 1))
    m = ((y >= horizon) & (y < y1) & (x >= x0) & (x < x1)).astype(np.float32)
    m = blur(m, 0.7)
    return img * (1 - m[..., None]) + out * m[..., None]


def palm(mask, bx, by, height, lean=0.25, fronds=9, size=1.0, seed=0, trunk_w=None, tmask=None):
    """Draw a palm tree silhouette into Mask (trunk optionally into tmask). Returns crown position."""
    rng = np.random.default_rng(seed)
    tw = trunk_w or height * 0.045
    top = (bx + lean * height, by - height)
    ctrl = (bx + lean * height * 0.2, by - height * 0.55)
    pts = bezier((bx, by), ctrl, top, n=30)
    (tmask or mask).tapered(pts, tw * 1.3, tw * 0.7)
    cx, cy = top
    L = height * 0.42 * size
    for i in range(fronds):
        a = -math.pi / 2 + (i / (fronds - 1) - 0.5) * math.pi * 1.9 + rng.normal(0, 0.12)
        ln = L * rng.uniform(0.75, 1.1)
        droop = ln * rng.uniform(0.25, 0.5)
        ex = cx + math.cos(a) * ln
        ey = cy + math.sin(a) * ln * 0.55 + droop
        mx = cx + math.cos(a) * ln * 0.55
        my = cy + math.sin(a) * ln * 0.55 - ln * 0.12
        spine = bezier((cx, cy), (mx, my), (ex, ey), n=24)
        mask.tapered(spine, tw * 0.9, 1.0)
        # leaflets
        for j in range(3, 22):
            px, py = spine[j]
            qx, qy = spine[j + 1] if j + 1 < len(spine) else spine[j]
            dx, dy = qx - px, qy - py
            dl = math.hypot(dx, dy) + 1e-6
            nx, ny = -dy / dl, dx / dl
            ll = ln * 0.16 * math.sin(math.pi * j / 24) + 3
            for sgn in (1, -1):
                lx = px + nx * ll * sgn + dx / dl * ll * 0.6
                ly = py + ny * ll * sgn + dy / dl * ll * 0.6 + ll * 0.35
                mask.tapered([(px, py), ((px + lx) / 2, (py + ly) / 2 + 1), (lx, ly)], max(2.0, ll * 0.22), 0.8)
    mask.circle(cx, cy, tw * 0.9)
    return top


def bokeh(img, pts, cols, rads, strength=0.6, soft=0.25):
    h, w = img.shape[:2]
    layer = np.zeros_like(img)
    for (px, py), c, r in zip(pts, cols, rads):
        x0, x1 = int(max(0, px - r - 3)), int(min(w, px + r + 3))
        y0, y1 = int(max(0, py - r - 3)), int(min(h, py + r + 3))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2) / r
        m = np.clip((1 - d) / soft, 0, 1) * (0.7 + 0.3 * d)
        cc = np.array(c, np.float32) / 255
        layer[y0:y1, x0:x1] += m[..., None] * cc
    return 1 - (1 - img) * (1 - np.clip(layer * strength, 0, 1))


def bloom(img, thresh=0.7, radius=25, strength=0.6):
    l = lum(img)
    m = smooth(thresh, 1.0, l)[..., None] * img
    b = blur(m, radius)
    return 1 - (1 - img) * (1 - np.clip(b * strength, 0, 1))


def stars(img, maskfn, n=600, seed=5, h=H, w=W):
    rng = np.random.default_rng(seed)
    layer = np.zeros((h, w), np.float32)
    xs = rng.integers(0, w, n)
    ys = rng.integers(0, h, n)
    br = rng.random(n) ** 3
    layer[ys, xs] = br
    bigl = np.zeros((h, w), np.float32)
    big = rng.random(n) > 0.93
    bigl[ys[big], xs[big]] = br[big] + 0.3
    layer = blur(layer, 0.6) * 3 + blur(bigl, 2.0) * 25
    layer *= maskfn
    return screen(img, (235, 240, 255), np.clip(layer, 0, 1))


def sun_flare(img, cx, cy, strength=1.0, col=(255, 240, 210)):
    h, w = img.shape[:2]
    g = radial(cx, cy, 700, h, w, power=3) * 0.9 + radial(cx, cy, 160, h, w, power=1.5)
    out = screen(img, col, np.clip(g * strength, 0, 1))
    # star streaks
    x, y = grid(h, w)
    dx, dy = x - cx, y - cy
    r = np.sqrt(dx * dx + dy * dy) + 1
    ang = np.arctan2(dy, dx)
    rays = (np.cos(ang * 6) ** 40 + 0.6 * np.cos(ang * 6 + 0.5) ** 60) * np.clip(1 - r / 600, 0, 1) ** 2
    out = screen(out, col, np.clip(rays * 0.5 * strength, 0, 1))
    # ghosts along the line through the center
    ccx, ccy = w / 2, h / 2
    for k, (t, rr, c) in enumerate([(0.5, 40, (120, 255, 200)), (0.8, 90, (255, 180, 120)),
                                    (1.25, 60, (150, 170, 255)), (1.6, 130, (255, 220, 150)),
                                    (1.9, 30, (200, 255, 255))]):
        gx = cx + (ccx - cx) * t * 2
        gy = cy + (ccy - cy) * t * 2
        ring = radial(gx, gy, rr, h, w, power=0.6) * 0.18
        out = screen(out, c, np.clip(ring * strength, 0, 1))
    return out


def sparkle_field(img, n, box, seed=0, col=(255, 255, 240), size=(6, 22)):
    """Glowing 4-point sparkles scattered in box."""
    rng = np.random.default_rng(seed)
    h, w = img.shape[:2]
    m = Mask(w, h, ss=2)
    glow = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = box
    for i in range(n):
        px, py = rng.uniform(x0, x1), rng.uniform(y0, y1)
        s = rng.uniform(*size) * (rng.random() ** 1.5 * 0.8 + 0.2)
        star4(m, px, py, s)
        if 0 <= int(py) < h and 0 <= int(px) < w:
            glow[int(py), int(px)] += s / 4
    sm = m.get()
    g = blur(glow, 8) * 40
    out = screen(img, col, np.clip(g, 0, 1) * 0.7)
    out = screen(out, col, sm)
    return out


def star4(mask, cx, cy, s, thin=0.18):
    t = s * thin
    mask.poly([(cx, cy - s), (cx + t, cy - t), (cx + s, cy), (cx + t, cy + t),
               (cx, cy + s), (cx - t, cy + t), (cx - s, cy), (cx - t, cy - t)])


# ---------------------------------------------------------------- final grade
def grade(a, warm=1.0, vignette=0.22, grain=0.012, seed=99):
    """Shared final look for every background / CG."""
    a = np.clip(a, 0, 1).astype(np.float32)
    h, w = a.shape[:2]
    # gentle S-curve
    a = a + 0.06 * (a - 0.5) * (1 - np.abs(2 * a - 1))
    # warm tropical tint, more in highlights; lifted warm shadows
    l = lum(a)[..., None]
    tint = np.array([1.035, 1.01, 0.955], np.float32)
    a = a * (1 + (tint - 1) * warm * (0.5 + 0.5 * l))
    a = a + np.array([0.012, 0.006, 0.0], np.float32) * warm * (1 - l)
    # vignette
    x, y = grid(h, w)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / math.sqrt(2)
    v = 1 - vignette * smooth(0.35, 1.0, d) ** 1.3
    a = a * v[..., None]
    # grain (luminance)
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (h, w)).astype(np.float32)
    g = blur(g, 0.55) * 1.6
    a = a + g[..., None] * grain * (0.6 + 0.4 * (1 - l))
    return np.clip(a, 0, 1)


def save_rgb(a, path, do_grade=True, limit_mb=3.0, **kw):
    """Grade + save; if the file is too big, retry with lighter grain / softening."""
    tries = [(kw.get('grain', 0.012), 0), (0.008, 0), (0.006, 0.45), (0.004, 0.7)]
    for gr, pre in tries:
        b = blur(a, pre) if pre else a
        if do_grade:
            kw2 = dict(kw)
            kw2['grain'] = gr
            b = grade(b, **kw2)
        im = to_im(b)
        im.save(path, optimize=True, compress_level=9)
        mb = os.path.getsize(path) / 1e6
        if mb <= limit_mb or not do_grade:
            break
    print('saved', os.path.relpath(path, GAME), im.size, '%.2f MB' % mb)
    return im


# ---------------------------------------------------------------- perspective paste
def _coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, np.float64), np.array(B, np.float64)).tolist()


def paste_quad(img, src, quad, opacity=1.0):
    """Warp RGBA PIL image src onto float img at quad (tl, tr, br, bl)."""
    h, w = img.shape[:2]
    sw, sh = src.size
    c = _coeffs(quad, [(0, 0), (sw, 0), (sw, sh), (0, sh)])
    warped = src.transform((w, h), Image.PERSPECTIVE, c, Image.BICUBIC)
    a = np.asarray(warped, np.float32) / 255.0
    return lerp(img, a[..., :3], a[..., 3] * opacity)


def text_img(txt, size=80, col=(255, 255, 255), bg=None, pad=20, font=None):
    from PIL import ImageFont
    f = None
    for p in (font, '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf',
              '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf'):
        if p and os.path.exists(p):
            f = ImageFont.truetype(p, size)
            break
    if f is None:
        f = ImageFont.load_default()
    bb = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), txt, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('RGBA', (tw + pad * 2, th + pad * 2), bg or (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), txt, font=f, fill=col)
    return im
