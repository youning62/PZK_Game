"""潘子恺卫衣：缺少的表情（震惊 / 沮丧）先用漫画符号叠加生成（基于已审核的 pzk_hoodie_normal）。
Gemini 额度恢复后可用 genai_pzk.py variants pzk_hoodie_shock pzk_hoodie_gloom 生成真实表情替换。"""
import os
from PIL import Image
import gen_sprites as G

G.HEADS['pzk_hoodie'] = dict(box=(355, 40, 650, 430), face=(380, 180, 630, 400), cheeks=((430, 300), (580, 300)))
base = Image.open(os.path.join(G.SP, 'pzk_hoodie_normal.png')).convert('RGBA')
G.e_shock(base.copy(), 'pzk_hoodie').save(os.path.join(G.SP, 'pzk_hoodie_shock.png'), optimize=True)
G.e_gloom(base.copy(), 'pzk_hoodie').save(os.path.join(G.SP, 'pzk_hoodie_gloom.png'), optimize=True)
print('ok')
