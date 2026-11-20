"""Backgrounds derived from beach-1.png and pzk-closet.png."""
import sys
from artlib import *

HZ = 515  # horizon row in beach-1 source


def beach_src():
    return to_f(load('beach-1.png'))


def masks(a):
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    x, y = grid(h, w)
    l = lum(a)
    mx, mn = a.max(-1), a.min(-1)
    sky = ((b > r + 0.06) & (b > 0.5) & (b >= g - 0.02)) | ((l > 0.72) & (mx - mn < 0.25))
    sky &= (y < HZ + 1)
    sky &= ~((x < 520) & (y > 478))
    sky = ndimage.binary_opening(sky, iterations=1)
    sky = ndimage.binary_closing(sky, iterations=2)
    skyf = blur(sky.astype(np.float32), 1.0)
    above = (y < HZ + 1).astype(np.float32)
    land_up = np.clip(above - skyf, 0, 1)  # trees / hills
    seam = smooth(0.02, 0.16, b - r) * (y > HZ - 1)
    seam = blur(seam, 2.0) * (y > HZ - 1)
    ground = np.clip(1 - skyf - land_up - seam, 0, 1)
    # cloudiness inside sky
    cloud = smooth(0.30, 0.08, b - r) * skyf
    sun0 = radial(1215, 114, 230, h, w, power=1.0)
    cloud = cloud * (1 - smooth(0.0, 0.4, sun0))
    return skyf, land_up, seam, ground, cloud, l


def crop169(a):
    return to_f(cover(to_im(a), W, H, 0.5, 0.5))


def beach_day():
    a = beach_src()
    out = crop169(a)
    out = saturate(out, 1.05)
    return out


def dream_beach():
    a = crop169(beach_src())
    a = saturate(a, 0.75)
    a = a * 0.78 + 0.24
    pink = np.array([1.04, 0.97, 1.02], np.float32)
    a = a * pink
    a = bloom(a, 0.6, 30, 0.9)
    a = bloom(a, 0.75, 90, 0.6)
    x, y = grid()
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    haze = smooth(0.55, 1.35, d)
    a = screen(a, (255, 240, 250), haze * 0.85)
    a = blur(a, 1.2) * 0.5 + a * 0.5
    a = sparkle_field(a, 70, (0, 0, W, H), seed=11, col=(255, 250, 235), size=(5, 20))
    a = sparkle_field(a, 30, (200, 400, 1800, 900), seed=12, col=(220, 245, 255), size=(8, 26))
    # soft floating orbs
    rng = np.random.default_rng(4)
    pts = [(rng.uniform(0, W), rng.uniform(0, H)) for _ in range(40)]
    cols = [(255, 230, 245) if rng.random() > 0.5 else (230, 250, 255) for _ in pts]
    rads = [rng.uniform(8, 40) for _ in pts]
    a = bokeh(a, pts, cols, rads, 0.35, 0.6)
    return a


def surf_beach():
    a = beach_src()
    im = to_im(a).crop((620, 170, 1536, 685)).resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    out = to_f(im)
    out = saturate(out, 1.08)
    # extra sparkle on water
    x, y = grid()
    l = lum(out)
    glint = smooth(0.78, 0.95, l) * (y > 330)
    out = screen(out, (255, 250, 230), blur(glint, 2.5) * 0.8)
    return out


def sunset_coast():
    a = beach_src()
    h, w = a.shape[:2]
    skyf, land_up, seam, ground, cloud, l = masks(a)
    x, y = grid(h, w)
    sunx, suny = 1060, HZ - 18
    # sky gradient
    sky = vgrad([(0, (52, 36, 98)), (0.35, (150, 70, 120)), (0.62, (240, 120, 95)),
                 (0.85, (255, 170, 95)), (1.0, (255, 214, 140))], h, w, 0, HZ)
    sky = screen(sky, (255, 200, 120), radial(sunx, suny, 700, h, w, power=2.2, sy=0.6) * 0.8)
    cl_col = lerp(np.array([120, 60, 100], np.float32) / 255, np.array([255, 175, 135], np.float32) / 255,
                  smooth(0.55, 0.95, l)[..., None])
    cl_col = screen(cl_col, (255, 200, 140), radial(sunx, suny, 600, h, w, power=1.5) * 0.6)
    sky = lerp(sky, cl_col, cloud * 0.9)
    # sun disc + glow
    sun = radial(sunx, suny, 34, h, w, power=0.25)
    sky = screen(sky, (255, 245, 210), np.clip(sun * 1.5, 0, 1))
    sky = screen(sky, (255, 190, 110), radial(sunx, suny, 220, h, w, power=2.5) * 0.9)
    # silhouetted trees/hills (rim lit warm)
    tree = a * np.array([0.22, 0.13, 0.15], np.float32) + np.array([0.05, 0.02, 0.05], np.float32)
    tree = screen(tree, (255, 140, 80), radial(sunx, suny, 900, h, w, power=3) * 0.25)
    # sea
    sl = lum(a)
    sea_c = gradient([(0, (40, 25, 60)), (0.35, (110, 50, 80)), (0.6, (220, 110, 80)), (0.85, (255, 190, 120)),
                      (1, (255, 240, 200))], np.clip(sl * 0.95, 0, 1))
    near = smooth(HZ, h, y)
    sea_c = sea_c * (1 - 0.5 * near[..., None])
    gl = np.exp(-((x - sunx) / (40 + (y - HZ) * 0.55)) ** 2) * smooth(0.25, 0.75, sl)
    gl *= (y >= HZ)
    sea_c = screen(sea_c, (255, 215, 140), np.clip(gl * 1.2, 0, 1))
    sea_c = screen(sea_c, (255, 160, 100), radial(sunx, HZ, 500, h, w, power=2, sy=0.35) * 0.5)
    # ground (sand, people) warm & dark
    gr = a * np.array([0.62, 0.42, 0.36], np.float32)
    gr = screen(gr, (255, 150, 90), smooth(0.45, 0.95, sl) * 0.25)
    out = sky * skyf[..., None] + tree * land_up[..., None] + sea_c * seam[..., None] + gr * ground[..., None]
    tot = (skyf + land_up + seam + ground)[..., None]
    out = out / np.maximum(tot, 1e-3)
    out = bloom(out, 0.7, 30, 0.5)
    return crop169(out)


def night_beach():
    a = beach_src()
    h, w = a.shape[:2]
    skyf, land_up, seam, ground, cloud, l = masks(a)
    x, y = grid(h, w)
    mx, my = 1150, 170
    sky = vgrad([(0, (4, 8, 26)), (0.6, (12, 26, 62)), (1.0, (34, 58, 104))], h, w, 0, HZ)
    sky = stars(sky, (1 - cloud) * smooth(HZ, HZ - 120, y), n=1400, seed=7, h=h, w=w)
    sky = screen(sky, (120, 150, 210), radial(mx, my, 520, h, w, power=2.5) * 0.45)
    cl = lerp(np.array([20, 28, 55], np.float32) / 255, np.array([110, 125, 160], np.float32) / 255,
              smooth(0.6, 1.0, l)[..., None])
    sky = lerp(sky, cl, cloud * 0.75)
    moon = radial(mx, my, 36, h, w, power=0.2)
    mtex = fbm(h, w, 12, 3, seed=8)
    mc = np.stack([0.96 - 0.08 * mtex, 0.95 - 0.08 * mtex, 0.88 - 0.06 * mtex], -1)
    sky = lerp(sky, mc, np.clip(moon * 1.6, 0, 1))
    sky = screen(sky, (190, 210, 255), radial(mx, my, 140, h, w, power=2.2) * 0.7)
    tree = a * np.array([0.05, 0.07, 0.12], np.float32) + np.array([0.01, 0.015, 0.03], np.float32)
    sl = lum(a)
    sea_c = gradient([(0, (3, 8, 22)), (0.5, (12, 30, 66)), (0.8, (40, 70, 120)), (1, (120, 150, 200))],
                     np.clip(sl, 0, 1))
    sea_c *= 0.8
    gl = np.exp(-((x - mx) / (25 + (y - HZ) * 0.45)) ** 2) * smooth(0.35, 0.8, sl) * (y >= HZ)
    sea_c = screen(sea_c, (220, 230, 255), np.clip(gl * 1.1, 0, 1))
    gr = a * np.array([0.13, 0.16, 0.26], np.float32)
    gr = screen(gr, (120, 140, 200), smooth(0.6, 1.0, sl) * 0.15)
    out = sky * skyf[..., None] + tree * land_up[..., None] + sea_c * seam[..., None] + gr * ground[..., None]
    out = out / np.maximum((skyf + land_up + seam + ground)[..., None], 1e-3)
    out = bloom(out, 0.55, 20, 0.6)
    return crop169(out)


def villa_closet():
    a = to_f(cover(load('pzk-closet.png', 'RGB')))
    a = a * 1.04 + 0.01
    a = screen(a, (255, 220, 170), radial(1100, 80, 900, power=2) * 0.25)
    return a


SCENES = {
    'beach_day': beach_day, 'dream_beach': dream_beach, 'surf_beach': surf_beach,
    'sunset_coast': sunset_coast, 'night_beach': night_beach, 'villa_closet': villa_closet,
}

if __name__ == '__main__':
    names = sys.argv[1:] or list(SCENES)
    for n in names:
        save_rgb(SCENES[n](), os.path.join(BG, n + '.png'))
