"""仙人跳小游戏的美术（俯视角）：地图、角色 Q 版头像棋子、投掷物、图标。
输出 game/images/minigame/。头像从已有立绘裁出。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', '..', 'game')
SP = os.path.join(G, 'images', 'sprites')
OUT = os.path.join(G, 'images', 'minigame')
os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(G, 'SourceHanSansLite.ttf')
SS = 4
W, H = 1600, 900

# 地图障碍物（与 minigame.rpy 里的 OBSTACLES 保持一致，单位：地图像素）
OBSTACLES = [
    (120, 520, 360, 820),    # 大床
    (520, 80, 760, 200),     # 沙发
    (880, 420, 1000, 560),   # 茶几
    (1180, 600, 1300, 900),  # 隔断墙
    (1180, 0, 1300, 330),    # 隔断墙（上半）
    (1380, 520, 1600, 620),  # 走廊里的推车
]
EXIT = (1480, 40, 1590, 170)


def floor():
    img = Image.new('RGB', (W, H), (70, 40, 38))
    d = ImageDraw.Draw(img)
    # 套房地毯（左）+ 走廊木地板（右）
    rng = np.random.default_rng(3)
    carpet = (rng.normal(0, 6, (H, 1180, 3)) + np.array([98, 38, 44])).clip(0, 255).astype(np.uint8)
    img.paste(Image.fromarray(carpet), (0, 0))
    for x in range(1300, W, 60):
        d.rectangle((x, 0, x + 58, H), fill=(120 + (x // 60) % 3 * 6, 86, 58))
        d.line((x + 58, 0, x + 58, H), fill=(80, 56, 38), width=2)
    # 地毯花纹
    for y in range(40, H, 120):
        for x in range(40, 1180, 120):
            d.ellipse((x, y, x + 26, y + 26), outline=(150, 70, 70), width=2)
    # 家具
    def box(r, fill, edge, label=None):
        d.rounded_rectangle(r, 14, fill=fill, outline=edge, width=5)
        if label:
            f = ImageFont.truetype(FONT, 30)
            tw = d.textlength(label, font=f)
            d.text(((r[0] + r[2] - tw) / 2, (r[1] + r[3]) / 2 - 18), label, fill=(255, 255, 255), font=f)
    box(OBSTACLES[0], (235, 230, 225), (150, 30, 40), '床')
    for i in range(14):                                   # 床上的玫瑰花瓣
        x, y = rng.integers(140, 340), rng.integers(540, 800)
        d.ellipse((x, y, x + 14, y + 10), fill=(200, 20, 40))
    box(OBSTACLES[1], (90, 60, 50), (40, 25, 20), '沙发')
    box(OBSTACLES[2], (60, 40, 30), (30, 20, 15), '茶几')
    box(OBSTACLES[3], (200, 190, 175), (120, 110, 100))
    box(OBSTACLES[4], (200, 190, 175), (120, 110, 100))
    box(OBSTACLES[5], (180, 180, 190), (90, 90, 100), '推车')
    # 入口（大哥们破门而入的门）
    d.rectangle((0, 280, 18, 420), fill=(30, 20, 15))
    # 安全出口
    d.rectangle(EXIT, fill=(20, 140, 60), outline=(200, 255, 200), width=6)
    f = ImageFont.truetype(FONT, 26)
    d.text((EXIT[0] + 6, EXIT[1] + 40), '安全', fill='white', font=f)
    d.text((EXIT[0] + 6, EXIT[1] + 76), '出口', fill='white', font=f)
    # 暗角
    a = np.array(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = Image.fromarray((a * v[..., None]).clip(0, 255).astype(np.uint8))
    img.save(os.path.join(OUT, 'floor.png'), optimize=True)


def head_crop(sprite, box):
    im = Image.open(os.path.join(SP, sprite)).convert('RGBA').crop(box)
    return im


def token(name, head, body_col, ring_col, label=None, accessory=None):
    S = 140
    big = Image.new('RGBA', (S * SS, (S + 30) * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    # 影子
    d.ellipse((25 * SS, (S + 2) * SS, (S - 25) * SS, (S + 24) * SS), fill=(0, 0, 0, 90))
    # 身体
    d.ellipse((28 * SS, 70 * SS, (S - 28) * SS, (S + 12) * SS), fill=body_col + (255,), outline=(20, 20, 20, 255), width=3 * SS)
    big = big.resize((S, S + 30), Image.LANCZOS)
    # 头像（圆形）
    hs = 92
    h = head.resize((hs, hs), Image.LANCZOS)
    m = Image.new('L', (hs * SS, hs * SS), 0)
    ImageDraw.Draw(m).ellipse((0, 0, hs * SS, hs * SS), fill=255)
    m = m.resize((hs, hs), Image.LANCZOS)
    hm = Image.new('RGBA', (hs, hs), (0, 0, 0, 0))
    hm.paste(h, (0, 0), Image.composite(h.split()[3], Image.new('L', (hs, hs), 0), m) if h.mode == 'RGBA' else m)
    ring = Image.new('RGBA', (hs + 10, hs + 10), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, hs + 9, hs + 9), fill=ring_col + (255,))
    big.alpha_composite(ring, ((S - hs - 10) // 2, 2))
    bg = Image.new('RGBA', (hs, hs), (235, 225, 215, 255)); bg.putalpha(m)
    big.alpha_composite(bg, ((S - hs) // 2, 7))
    big.alpha_composite(hm, ((S - hs) // 2, 7))
    d = ImageDraw.Draw(big)
    if accessory == 'chain':
        d.arc((44, 88, 96, 130), 20, 160, fill=(240, 200, 60), width=6)
    if accessory == 'towel':
        d.rectangle((34, 118, 106, 140), fill=(250, 250, 250), outline=(180, 180, 180), width=2)
    if accessory == 'brief':
        d.rectangle((92, 120, 124, 142), fill=(70, 45, 25), outline=(20, 10, 5), width=2)
    if label:
        f = ImageFont.truetype(FONT, 20)
        tw = d.textlength(label, font=f)
        d.rounded_rectangle(((S - tw) / 2 - 6, S + 4, (S + tw) / 2 + 6, S + 28), 6, fill=(0, 0, 0, 170))
        d.text(((S - tw) / 2, S + 4), label, fill='white', font=f)
    big.save(os.path.join(OUT, f'tok_{name}.png'))


def silhouette_head(col):
    im = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((20, 10, 180, 190), fill=col + (255,))
    d.ellipse((60, 70, 85, 95), fill=(255, 255, 255, 255)); d.ellipse((115, 70, 140, 95), fill=(255, 255, 255, 255))
    d.ellipse((68, 78, 80, 90), fill=(0, 0, 0, 255)); d.ellipse((123, 78, 135, 90), fill=(0, 0, 0, 255))
    d.arc((70, 110, 130, 160), 200, 340, fill=(0, 0, 0, 255), width=6)
    return im


def props():
    # 和解协议（纸）
    im = Image.new('RGBA', (60, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((6, 4, 54, 66), fill=(250, 250, 245), outline=(120, 120, 120), width=2)
    for y in range(16, 60, 9):
        d.line((12, y, 48, y), fill=(150, 150, 150), width=2)
    d.text((10, 4), '协议', fill=(200, 0, 0), font=ImageFont.truetype(FONT, 14))
    im.save(os.path.join(OUT, 'proj_paper.png'))
    # 黑色高跟鞋
    im = Image.new('RGBA', (70, 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(4, 36), (40, 18), (64, 20), (66, 30), (30, 42)], fill=(15, 15, 15))
    d.line((60, 28, 64, 48), fill=(15, 15, 15), width=5)
    d.polygon([(40, 22), (62, 22), (62, 26), (42, 28)], fill=(170, 0, 20))
    im.save(os.path.join(OUT, 'proj_heel.png'))
    # 心
    for name, col in (('heart_full', (230, 40, 70)), ('heart_empty', (90, 90, 90))):
        im = Image.new('RGBA', (48 * SS, 44 * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        s = SS
        d.ellipse((2 * s, 2 * s, 26 * s, 26 * s), fill=col); d.ellipse((22 * s, 2 * s, 46 * s, 26 * s), fill=col)
        d.polygon([(3 * s, 18 * s), (45 * s, 18 * s), (24 * s, 42 * s)], fill=col)
        im.resize((48, 44), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))
    # 挥拳特效（月牙）
    im = Image.new('RGBA', (160 * SS, 160 * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc((10 * SS, 10 * SS, 150 * SS, 150 * SS), -60, 60, fill=(255, 255, 255, 230), width=18 * SS)
    d.arc((30 * SS, 30 * SS, 130 * SS, 130 * SS), -45, 45, fill=(255, 230, 120, 200), width=8 * SS)
    im.resize((160, 160), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1)).save(os.path.join(OUT, 'swing.png'))


if __name__ == '__main__':
    floor()
    token('pzk', head_crop('pzk_casual_shock.png', (360, 30, 650, 330)), (240, 240, 240), (60, 160, 255), '我', 'towel')
    token('thug1', silhouette_head((210, 150, 120)), (210, 60, 60), (220, 60, 60), '花衬衫大哥')
    token('thug2', silhouette_head((200, 140, 110)), (40, 40, 40), (220, 60, 60), '金链子大哥', 'chain')
    token('lawyer', silhouette_head((220, 170, 140)), (60, 70, 110), (220, 60, 60), '律师老公', 'brief')
    token('yyl', head_crop('yyl_night_calm.png', (380, 60, 640, 320)), (120, 10, 30), (255, 60, 120), '杨永麟')
    props()
    print('ok')
