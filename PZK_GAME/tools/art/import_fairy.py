"""系统小精灵：绿幕抠图 → game/images/fairy/fairy_<表情>.png（520x520 透明画布，统一大小与位置）。
fairy_default 导出为 fairy_idle。
用法：python3 import_fairy.py [fairy_名字 ...]   （默认导入 ref/genai_fairy/ 下所有 fairy_*（不含 master））
"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ref', 'genai_fairy')
DST = os.path.join(HERE, '..', '..', 'game', 'images', 'fairy')
os.makedirs(DST, exist_ok=True)
SIZE = 520
FILL = 0.92        # 人物最长边占画布比例


def key_green(im):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # greenness: catches pure green and the yellow-green fringe in hair, but not the cyan wings (b ≈ g there)
    ref = np.maximum(b, (r + b) / 2)
    spill = g - ref
    alpha = 1.0 - np.clip((spill - 12.0) / 45.0, 0, 1)
    # keep only the main blob (drop stray specks)
    lab, n = ndimage.label(alpha > 0.5)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
        keep = ndimage.binary_dilation(lab == (int(np.argmax(sizes)) + 1), iterations=6)
        # keep sparkles/wings near the main blob
        keep = ndimage.binary_dilation(keep, iterations=40)
        alpha = alpha * keep
    # despill: pull green down to max(r,b) where it exceeds it
    g2 = np.where(spill > 0, ref + np.minimum(spill, 0) , g)
    out = np.dstack([r, g2, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    o = Image.fromarray(out)
    a_ch = o.split()[3].filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    o.putalpha(a_ch)
    return o


def to_canvas(o):
    bb = o.getbbox()
    o = o.crop(bb)
    s = SIZE * FILL / max(o.size)
    o = o.resize((max(1, round(o.size[0] * s)), max(1, round(o.size[1] * s))), Image.LANCZOS)
    c = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    c.alpha_composite(o, ((SIZE - o.size[0]) // 2, SIZE - o.size[1] - int(SIZE * (1 - FILL) / 2)))
    return c


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(SRC)
                                   if f.startswith('fairy_') and f.endswith('.png') and 'master' not in f)
    for n in names:
        out_name = 'fairy_idle' if n == 'fairy_default' else n
        to_canvas(key_green(Image.open(os.path.join(SRC, n + '.png')))).save(os.path.join(DST, out_name + '.png'), optimize=True)
        print('imported', out_name)
