"""把 genai_lxx.py 生成的李轩翔白底全身图导入游戏立绘。

每张图：macOS Vision 抠图（person_mask.swift）→ 按人物包围盒统一身高与脚底基线 → 1024x1536 透明画布
→ game/images/sprites/<同名>.png。另外由 lxx_cold 生成 lxx_silhouette。

用法：python3 import_lxx_genai.py [lxx_名字 ...]   （默认导入 ref/genai/ 下所有 lxx_*.png）
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'ref', 'genai')
DST = os.path.join(HERE, '..', '..', 'game', 'images', 'sprites')
CW, CH = 1024, 1536
LIKE = None
TOP, FEET = 55, 1880          # 头顶 / 脚底（脚底在画布外：与潘子恺立绘的头部大小一致，裁到小腿）


def mask_for(path, tmp):
    prefix = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0])
    subprocess.run(['swift', os.path.join(HERE, 'person_mask.swift'), path, prefix], check=True,
                   stdout=subprocess.DEVNULL)
    m = np.array(Image.open(prefix + '_all.png').convert('L'), float) / 255
    lab, n = ndimage.label(m > 0.5)
    if n > 1:  # keep the biggest person blob
        sizes = ndimage.sum(np.ones_like(m), lab, range(1, n + 1))
        keep = ndimage.binary_dilation(lab == (int(np.argmax(sizes)) + 1), iterations=4)
        m = m * keep
    return m


def to_sprite(path, tmp):
    im = Image.open(path).convert('RGB')
    m = mask_for(path, tmp)
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).resize(im.size, Image.LANCZOS), float) / 255
    ys, xs = np.where(m > 0.4)
    y0, y1 = ys.min(), ys.max()
    cx = (xs.min() + xs.max()) / 2
    s = (FEET - TOP) / (y1 - y0)
    if LIKE is not None:            # reuse another image's scale, align by the feet
        s = LIKE
        y0 = y1 - (FEET - TOP) / s
    rgba = Image.fromarray(np.dstack([np.array(im), (m * 255).astype(np.uint8)]))
    rgba = rgba.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    out.alpha_composite(rgba, (round(CW / 2 - cx * s), round(TOP - y0 * s)))
    return out


def main(names):
    if not names:
        names = sorted(f[:-4] for f in os.listdir(SRC) if f.startswith('lxx_') and f.endswith('.png'))
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            sp = to_sprite(os.path.join(SRC, name + '.png'), tmp)
            sp.save(os.path.join(DST, name + '.png'), optimize=True)
            print('imported', name)
            if name == 'lxx_cold':
                a = sp.split()[3]
                sil = Image.new('RGBA', sp.size, (8, 8, 12, 255)); sil.putalpha(a)
                sil.save(os.path.join(DST, 'lxx_silhouette.png'), optimize=True)
                print('imported lxx_silhouette')


if __name__ == '__main__':
    # 通用参数（给其他角色用）：--src <目录>  --top <头顶y>  --feet <脚底y>
    args = sys.argv[1:]
    if '--like' in args:
        i = args.index('--like'); like_name = args[i + 1]; del args[i:i + 2]
    else:
        like_name = None
    for flag in ('--src', '--top', '--feet'):
        if flag in args:
            i = args.index(flag); val = args[i + 1]; del args[i:i + 2]
            if flag == '--src':
                SRC = os.path.join(HERE, val) if not os.path.isabs(val) else val
            elif flag == '--top':
                TOP = int(val)
            else:
                FEET = int(val)
    if like_name:
        import tempfile as _t
        with _t.TemporaryDirectory() as tmp:
            p = os.path.join(SRC, like_name + '.png')
            im = Image.open(p)
            m = mask_for(p, tmp)
            m = np.array(Image.fromarray((m * 255).astype(np.uint8)).resize(im.size), float) / 255
            ys, _ = np.where(m > 0.4)
            LIKE = (FEET - TOP) / (ys.max() - ys.min())
    main(args)
