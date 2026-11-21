"""李轩翔 CGs rebuilt with the photo-based sprites.
cg_reunion: her office at night; she stands behind the desk, he waits in the doorway in the delivery uniform.
cg_claw_machine: 2 a.m. arcade; she leans at the glowing claw machine (machine reused from the earlier CG).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from artlib import to_f, cover, save_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', '..', 'game', 'images')
W, H = 1920, 1080


def spr(name, h, flip=False):
    im = Image.open(os.path.join(G, 'sprites', name)).convert('RGBA')
    im = im.crop(im.getbbox())
    s = h / im.size[1]
    im = im.resize((round(im.size[0] * s), round(h)), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def tint(im, col, amount):
    a = np.array(im).astype(float)
    a[..., :3] = a[..., :3] * (1 - amount) + np.array(col) * amount
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def rim(im, col, width=10, strength=0.8):
    """coloured edge light on a cut-out"""
    al = im.split()[3]
    inner = al.filter(ImageFilter.MinFilter(width | 1))
    edge = np.clip(np.array(al, float) - np.array(inner, float), 0, 255) / 255 * strength
    a = np.array(im).astype(float)
    for c in range(3):
        a[..., c] = a[..., c] * (1 - edge) + col[c] * edge
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def reunion():
    bg = Image.open(os.path.join(G, 'bg', 'ib_office_night.png')).convert('RGBA').resize((W, H))
    canvas = bg.copy()
    # her: front photo, cool monitor light from the right
    lxx = tint(spr('lxx_cold.png', 1000), (120, 160, 230), 0.12)
    lxx = rim(lxx, (150, 200, 255), 5, 0.22)
    canvas.alpha_composite(lxx, (1080, 120))
    # desk in front of her (hides the lower body)
    d = ImageDraw.Draw(canvas)
    d.polygon([(820, 760), (1820, 760), (1880, 1080), (760, 1080)], fill=(22, 24, 32, 255))
    d.polygon([(820, 752), (1820, 752), (1830, 772), (810, 772)], fill=(70, 78, 98, 255))
    # monitor seen from behind + glow on desk
    d.rectangle((1500, 560, 1760, 752), fill=(14, 16, 22, 255))
    d.rectangle((1615, 752, 1645, 770), fill=(30, 32, 40, 255))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((1380, 640, 1860, 860), fill=(120, 170, 255, 70))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    # coffee cup + papers
    d.rectangle((1180, 790, 1230, 850), fill=(240, 236, 228, 255))
    d.polygon([(900, 800), (1080, 790), (1100, 830), (920, 842)], fill=(225, 228, 235, 255))
    # doorway on the left with him in it
    d.rectangle((60, 120, 520, 1080), fill=(40, 38, 46, 255))
    door_light = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(door_light).rectangle((80, 140, 500, 1080), fill=(255, 220, 160, 60))
    canvas.alpha_composite(door_light.filter(ImageFilter.GaussianBlur(20)))
    pzk = spr('pzk_delivery_awkward.png', 980)
    canvas.alpha_composite(pzk, (290 - pzk.size[0] // 2, 1080 - 980 + 40))
    save_rgb(to_f(canvas.convert('RGB')), os.path.join(G, 'cg', 'cg_reunion.png'))


def claw():
    bg = Image.open(os.path.join(G, 'bg', 'arcade_night.png')).convert('RGBA').resize((W, H))
    canvas = bg.copy()
    # machine with the claw holding the pink cat, from the earlier CG (right part)
    machine = Image.open(os.path.join(HERE, 'ref', 'claw_machine_part.png')).convert('RGBA')
    m = Image.new('L', machine.size, 0)
    ImageDraw.Draw(m).rectangle((30, 20, 770, 1080), fill=255)
    machine.putalpha(m.filter(ImageFilter.GaussianBlur(14)))
    canvas.alpha_composite(machine, (1150, 0))
    # her: side photo, leaning in, pink/blue neon on her
    lxx = spr('lxx_casual_cold.png', 1040)
    lxx = tint(lxx, (255, 110, 200), 0.10)
    lxx = rim(lxx, (120, 220, 255), 5, 0.25)
    canvas.alpha_composite(lxx, (720, 80))
    # him at the left edge
    pzk = tint(spr('pzk_delivery_happy.png', 900), (255, 120, 210), 0.08)
    canvas.alpha_composite(pzk, (40, 1080 - 900 + 60))
    save_rgb(to_f(canvas.convert('RGB')), os.path.join(G, 'cg', 'cg_claw_machine.png'))


if __name__ == '__main__':
    reunion(); claw(); print('ok')
