"""Generate the tropical-themed UI images (textbox, namebox, choice buttons).

Run from anywhere:  python3 tools/ui/make_ui.py
Writes into game/gui/.
"""
import os
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GUI = os.path.join(HERE, "..", "..", "game", "gui")
SS = 4  # supersampling


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def vgrad(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    top = np.array(top, float)[None, None, :]
    bottom = np.array(bottom, float)[None, None, :]
    arr = top + (bottom - top) * t
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def rounded_mask(w, h, r):
    m = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), r * SS, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def textbox():
    W, H = 1920, 278
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # panel: inset from edges, rounded
    px, py, pw, ph = 230, 34, W - 460, H - 50
    panel = vgrad(pw, ph, (10, 34, 60, 215), (6, 18, 34, 235))
    panel.putalpha(Image.fromarray(
        (np.array(rounded_mask(pw, ph, 28), float) * np.array(panel.split()[3], float) / 255).astype(np.uint8)))
    # glow behind
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((px - 6, py - 6, px + pw + 6, py + ph + 6), 34, fill=(60, 180, 255, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow)
    img.alpha_composite(panel, (px, py))
    # border lines (supersampled)
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((px * SS, py * SS, (px + pw) * SS, (py + ph) * SS), 28 * SS,
                        outline=(140, 215, 255, 200), width=3 * SS)
    # little wave ornament on the top-right edge
    import math
    pts = []
    x0, x1, yb = (px + pw - 420) * SS, (px + pw - 60) * SS, (py + 2) * SS
    for i in range(200):
        x = x0 + (x1 - x0) * i / 199
        y = yb + math.sin(i / 199 * math.pi * 6) * 7 * SS
        pts.append((x, y))
    d.line(pts, fill=(255, 210, 120, 230), width=4 * SS)
    big = big.resize((W, H), Image.LANCZOS)
    img.alpha_composite(big)
    img.save(os.path.join(GUI, "textbox.png"))


def namebox():
    W, H = 450, 54
    g = vgrad(W, H, (255, 160, 70, 245), (240, 100, 120, 245))
    mask = rounded_mask(W, H, 16)
    g.putalpha(mask)
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle((0, 0, W * SS - 1, H * SS - 1), 16 * SS,
                                          outline=(255, 240, 210, 230), width=3 * SS)
    g.alpha_composite(big.resize((W, H), Image.LANCZOS))
    g.save(os.path.join(GUI, "namebox.png"))


def choice(name, top, bottom, outline):
    W, H = 1185, 90
    g = vgrad(W, H, top, bottom)
    g.putalpha(Image.fromarray((np.array(rounded_mask(W, H, 30), float) *
                                np.array(g.split()[3], float) / 255).astype(np.uint8)))
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle((2 * SS, 2 * SS, (W - 2) * SS, (H - 2) * SS), 28 * SS,
                                          outline=outline, width=3 * SS)
    g.alpha_composite(big.resize((W, H), Image.LANCZOS))
    g.save(os.path.join(GUI, "button", name))


if __name__ == "__main__":
    textbox()
    namebox()
    choice("choice_idle_background.png", (14, 44, 78, 220), (8, 26, 48, 230), (120, 200, 255, 170))
    choice("choice_hover_background.png", (255, 150, 70, 240), (235, 90, 120, 240), (255, 240, 210, 255))
    print("ok")
