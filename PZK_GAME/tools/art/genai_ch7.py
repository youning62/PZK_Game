"""第六章（Chapter7.rpy）：丁虹依（替换周沫）、沈眠、李轩翔晚宴长裙、宴会厅背景。
所有表情按暴走漫画风格：真人脸 + 极度夸张扭曲（不照搬任何现成梗图角色）。
用法（tools/art 目录）：
    python3 genai_ch7.py masters | bgs | variants <dhy|shen|lxxg>
输出：ref/genai_ch7/
"""
import os, sys
import genai_ch6 as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'ref', 'genai_ch7')
os.makedirs(OUT, exist_ok=True)
C.OUT = OUT
C.G.OUT = OUT
FRAME = C.FRAME
LXX_MASTER = os.path.join(HERE, 'ref', 'genai', 'master.png')
DHY_REFS = [os.path.join(HERE, 'ref', f) for f in ('dhy_ref_1.jpg', 'dhy_ref_2.jpg', 'dhy_ref_3.jpg')]

RAGE = {   # 暴走漫画式表情（每个角色从中取用）
    'jaw_drop': "extreme shock: eyes bulging out like ping-pong balls, jaw dropped absurdly low, both hands on cheeks",
    'mock_laugh': "mocking laugh: eyes squeezed into two lines, an enormous closed-mouth grin with puffed cheeks, chin up",
    'grimace': "whole face scrunched as tight as possible, teeth clenched in a giant grimace, deep wrinkles",
    'side_eye': "ultimate contempt: heavy-lidded side-eye, one corner of the mouth pulled way down, nostrils flared",
    'rage': "volcanic rage: mouth opened impossibly wide screaming, forehead veins, face bright red, steam from the ears",
    'cry_laugh': "crying with laughter: streams of tears, mouth wide open, red face, clutching the stomach",
    'evil_grin': "evil scheming grin: eyes narrowed to slits, toothy grin stretching ear to ear, fingers steepled",
    'soul_leave': "dead inside: empty eyes looking up, mouth hanging open, a tiny translucent ghost of themself floating out of the mouth",
    'blush_melt': "overwhelmed with embarrassment: face bright red to the ears, eyes spiralling, steam rising, hands covering half the face",
    'smug': "insufferably smug: one eyebrow raised extremely high, chin up, looking down the nose, smirk",
}

CHARS = {
    # 丁虹依：脸来自参考照片（照片是男性，按其五官设计成女性），三中校花，精品店柜姐，想做服装设计
    'dhy': dict(
        refs=DHY_REFS,
        master=("The reference photos show one young man. Create a NEW photo of a young WOMAN about 26 whose HEAD is an "
                "exact match of this person: identical face (same eyes, eyelids, nose, lips, round face shape, skin tone) and the "
                "SAME messy dark-brown hairstyle as in the photos, unchanged. Add one big cute pink satin bow clipped in the hair "
                "so players can tell she is a girl. Only the BODY and CLOTHES are feminine: a slim female figure wearing a fitted "
                "black luxury-boutique uniform dress with a white collar, a small gold name badge (no readable text), sheer black "
                "tights, black low heels, a measuring tape hanging around her neck. Light lip tint only. Bright, cheeky smile. "
                + FRAME),
        expr=['jaw_drop', 'mock_laugh', 'side_eye', 'blush_melt', 'evil_grin', 'cry_laugh', 'smug']),
    # 沈眠：虚构人物。28 岁，投资机构创始合伙人，元气、话多、什么都想投
    'shen': dict(
        refs=[],
        master=("A fictional energetic, very pretty Chinese woman about 28, founding partner of a venture capital firm: "
                "glossy short black bob with a side clip, big lively eyes, bright red lips, a champagne-gold sequined cocktail "
                "dress to the knee, a thin black blazer over the shoulders, gold heels, holding a champagne glass. Big, "
                "excited, mischievous grin. " + FRAME),
        expr=['jaw_drop', 'mock_laugh', 'evil_grin', 'smug', 'rage', 'cry_laugh']),
    # 李轩翔：沈眠晚宴，穿第五章买的深蓝色真丝长裙
    'lxxg': dict(
        refs=[LXX_MASTER],
        master=("The reference image shows a woman. Create a new photo of EXACTLY the same woman (identical face, honey-blonde "
                "short hair, rimless light-brown tinted glasses, red lipstick, same body) wearing an elegant floor-length "
                "deep navy-blue silk evening gown with thin straps and a low back, a slim silver bracelet, black stiletto "
                "heels, a small black clutch. Cool, composed, powerful expression. " + FRAME),
        expr=['side_eye', 'smug', 'jaw_drop', 'blush_melt', 'rage', 'mock_laugh']),
}

BGS = {
    'ballroom': "Photorealistic interior of a luxurious five-star hotel ballroom during an evening investment-industry gala: crystal chandeliers, round tables with white cloths and candles, a small stage with a screen (no readable text), warm golden light, blurred well-dressed guests holding champagne. Wide 16:9 composition, eye level, no logos.",
    'hotel_terrace': "Photorealistic rooftop terrace of a luxury hotel at night: glass railing, city skyline lights, string lights, a couple of lounge chairs, a small bar in the corner, deep blue sky. Wide 16:9 composition, eye level, nobody in the foreground, no logos.",
}

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'masters':
        for k, c in CHARS.items():
            C.gen(c['master'], c['refs'], f'{k}_master')
    elif cmd == 'bgs':
        for k, p in BGS.items():
            C.gen(p, [], k, aspect='16:9')
    elif cmd == 'variants':
        k = sys.argv[2]; c = CHARS[k]
        m = os.path.join(OUT, f'{k}_master.png')
        for e in (sys.argv[3:] or c['expr']):
            prompt = ("The FIRST image is the approved look of this character. Create a new photo of exactly the same person in "
                      "exactly the same outfit and hair, same framing. Change only the facial expression and pose to this "
                      f"rage-comic (暴走漫画) style reaction, photorealistic but distorted to an absurd extreme while clearly the "
                      f"same person: {RAGE[e]}. Nothing sexual, no gore. " + FRAME)
            C.gen(prompt, [m] + c['refs'], f'{k}_{e}')
