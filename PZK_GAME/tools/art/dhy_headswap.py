"""丁虹依默认立绘：把参考照片里的脸（ref/dhy_face_exact.png）原样贴到生成的身体上（ref/genai_ch7/dhy_master.png），
脸部像素不做任何修改，只在边缘羽化；粉色蝴蝶结从生成图里抠出，放回头发上。
输出：ref/genai_ch7/dhy_base_swap.png（白底，之后由 import_lxx_genai.py 抠图入游戏）
需要先运行：swift person_mask.swift ref/dhy_face_exact.png <dir>/face
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MASKDIR = sys.argv[1]
body = Image.open(os.path.join(HERE, 'ref', 'genai_ch7', 'dhy_master.png')).convert('RGB')
face = Image.open(os.path.join(HERE, 'ref', 'dhy_face_exact.png')).convert('RGB')
fw, fh = face.size

# ---- 头部遮罩：人像分割 ∩ 手画的头部轮廓（去掉背景里的栏杆和衣领）
vis = Image.open(os.path.join(MASKDIR, 'face_all.png')).convert('L').resize(face.size)
shape = Image.new('L', face.size, 0)
d = ImageDraw.Draw(shape)
d.ellipse((55, 28, 560, 360), fill=255)                                  # 头发
d.polygon([(95, 230), (520, 230), (500, 400), (430, 500), (370, 530), (370, 600), (230, 600), (230, 530), (165, 490), (110, 400)], fill=255)  # 脸、下巴、照片里的脖子
m = np.minimum(np.array(vis, float), np.array(shape, float))
# 脸的中心区域一定保留（防止分割把脸抠掉一块）
core = Image.new('L', face.size, 0)
ImageDraw.Draw(core).ellipse((150, 200, 460, 530), fill=255)
m = np.maximum(m, np.array(core.filter(ImageFilter.GaussianBlur(8)), float))
mask = Image.fromarray(m.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))

# ---- 对齐：眼睛中心 → 生成身体的眼睛中心；眼睛到下巴的距离 → 同比例
FACE_EYES, FACE_CHIN = (300, 290), 528
BODY_EYES, BODY_CHIN = (848, 430), 562
s = (BODY_CHIN - BODY_EYES[1]) / (FACE_CHIN - FACE_EYES[1])
fs = face.resize((round(fw * s), round(fh * s)), Image.LANCZOS)
ms = mask.resize(fs.size, Image.LANCZOS)
ox = round(BODY_EYES[0] - FACE_EYES[0] * s)
oy = round(BODY_EYES[1] - FACE_EYES[1] * s)

# ---- 蝴蝶结：在生成图里按粉色抠出
b = np.array(body).astype(float)
r, g, bl = b[..., 0], b[..., 1], b[..., 2]
pink = (r > 150) & (r - g > 25) & (bl > g - 10) & (r > bl)
pink[:, :700] = False; pink[480:, :] = False
from scipy import ndimage
lab, n = ndimage.label(pink)
if n:
    sizes = ndimage.sum(pink, lab, range(1, n + 1))
    pink = lab == (int(np.argmax(sizes)) + 1)
pink = ndimage.binary_closing(pink, iterations=4)
pink = ndimage.binary_fill_holes(pink)
bow_mask = Image.fromarray((pink * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))

# ---- 抹掉生成的头（白底），保留脖子以下
out = body.copy()
erase = Image.new('L', body.size, 0)
ImageDraw.Draw(erase).ellipse((680, 180, 1095, 600), fill=255)
erase = erase.filter(ImageFilter.GaussianBlur(4))
bgcol = tuple(int(v) for v in np.median(np.array(body)[20:120, 20:120].reshape(-1, 3), axis=0))
out.paste(Image.new('RGB', body.size, bgcol), (0, 0), erase)


# ---- 贴上原样的脸，再把蝴蝶结放到新头发的右上方
out.paste(fs, (ox, oy), ms)
bx = ox + fs.size[0] - 230 - 830 + 640       # 蝴蝶结水平位置：靠在头发右上
by = oy - 70 - 190
bow = body.copy(); bow.putalpha(bow_mask)
bb = bow.getbbox()
bow = bow.crop(bb)
BOW_XY = (round(ox + 0.78 * fs.size[0] - bow.size[0] / 2), round(oy + 0.24 * fs.size[1] - bow.size[1] / 2))
out.paste(bow, BOW_XY, bow)

out.save(os.path.join(HERE, 'ref', 'genai_ch7', 'dhy_base_swap.png'))
print('saved', out.size, 'scale', round(s, 3), 'offset', ox, oy)


# ---------------------------------------------------------------------------
# 直接合成透明立绘（不再对合成图做自动抠图，避免把抹掉的区域当成人）
# alpha = 原身体轮廓 − 原头部 + 新头部 + 蝴蝶结；然后按 import_lxx_genai 的规则放到 1024x1536 画布
# 需要：swift person_mask.swift ref/genai_ch7/dhy_master.png <dir>/body
body_m = np.array(Image.open(os.path.join(MASKDIR, 'body_all.png')).convert('L').resize(body.size), float)
head_cut = np.array(erase, float)
alpha = body_m * (1 - head_cut / 255.0)
hm = Image.new('L', body.size, 0); hm.paste(ms, (ox, oy))
alpha = np.maximum(alpha, np.array(hm, float))
bm = Image.new('L', body.size, 0); bm.paste(bow.split()[3], BOW_XY)
alpha = np.maximum(alpha, np.array(bm, float))
rgba = out.copy(); rgba.putalpha(Image.fromarray(alpha.clip(0, 255).astype(np.uint8)))

CW, CH, TOP, FEET = 1024, 1536, 55, 1880
ys, xs = np.where(alpha > 100)
y0, y1 = ys.min(), ys.max(); cx = (xs.min() + xs.max()) / 2
sc = (FEET - TOP) / (y1 - y0)
r2 = rgba.resize((round(rgba.size[0] * sc), round(rgba.size[1] * sc)), Image.LANCZOS)
canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
canvas.alpha_composite(r2, (round(CW / 2 - cx * sc), round(TOP - y0 * sc)))
dst = os.path.join(HERE, '..', '..', 'game', 'images', 'sprites', 'dhy_base.png')
canvas.save(dst, optimize=True)
print('sprite saved', dst)
