"""杨永麟：用 Gemini 生成夸张 / 猎奇表情（基于现有立绘 yyl-girl.png，人物和服装保持不变）。

用法（tools/art 目录下，key 同 genai_lxx.py：~/.config/pzk/gemini_key）：
    PZK_GEMINI_MODEL=gemini-3-pro-image PZK_IMAGE_SIZE=2K python3 genai_yyl.py [yyl_名字 ...]
输出：tools/art/ref/genai_yyl/<名字>.png（白底原图，未入游戏）
审核通过后：python3 import_lxx_genai.py --src ref/genai_yyl --top 73 --feet 1532 yyl_...
"""
import os, sys
from PIL import Image
import genai_lxx as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'ref', 'genai_yyl')
os.makedirs(OUT, exist_ok=True)
G.OUT = OUT

SRC = os.path.join(HERE, '..', '..', 'game', 'images', 'yyl-girl.png')
REF_WHITE = os.path.join(OUT, '_ref_white.png')

BASE = ("The reference image shows one character. Create a new photo of EXACTLY the same person: identical face, "
        "identical two short pigtails, identical blue floral Hawaiian shirt and matching floral shorts, barefoot, "
        "same body and height. Photorealistic, full body from the top of the hair to the feet, standing, centered, "
        "same camera distance as the reference. Plain pure white background, soft even studio light, no props unless "
        "described, no text. This is a comedy game: make the expression EXTREMELY exaggerated, cartoonish and absurd, "
        "like an over-the-top anime 'face fault', but keep it photorealistic and clearly the same person. "
        "Nothing sexual, no blood, no gore. Expression and pose: ")

EXPR = {
    'yyl_jaw_drop': "jaw dropped absurdly low in shock, mouth a huge open 'O', eyes bulging wide, both hands on cheeks like 'The Scream'",
    'yyl_derp': "cross-eyed, cheeks puffed out like a blowfish, lips pursed, completely goofy",
    'yyl_bleh': "pulling down one lower eyelid with a finger and sticking the tongue far out, mocking 'akanbe' face",
    'yyl_villain': "head tilted back in an evil villain laugh, mouth wide open, one hand spread over half the face, eyes glinting",
    'yyl_creepy_smile': "an unsettling, impossibly wide grin stretching ear to ear, eyes wide open and unblinking, head slightly tilted — eerie and funny",
    'yyl_waterfall_cry': "crying hysterically: two exaggerated streams of tears, a snot bubble from the nose, mouth wailing open, fists clenched",
    'yyl_rage': "furious: veins popping on the forehead, nostrils flared, teeth clenched in a snarl, face flushed red, steam-like rage",
    'yyl_dead_fish': "completely dead inside: dull half-closed 'dead fish' eyes, mouth hanging slightly open, shoulders slumped, soul leaving the body",
    'yyl_smug_chad': "insufferably smug: one eyebrow raised very high, chin up, side-eye looking down at the viewer, smirk, arms crossed",
    'yyl_brain_lag': "brain lagging: eyes looking in two different directions, mouth twisted to one side, finger on chin, total confusion",
}


def ref_white():
    if not os.path.exists(REF_WHITE):
        im = Image.open(SRC).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        bg.convert('RGB').save(REF_WHITE)
    return REF_WHITE


# ---------------- 其他服装（晚餐 / 仙人跳之夜）----------------
OUTFITS = {
    'dinner': ("an elegant black satin slip dress (midi length, thin straps), a light cream knit shawl over the shoulders, "
               "a thin gold necklace, and black stiletto heels"),
    'night': ("a long deep wine-red satin evening dress, a small black clutch in one hand, silver earrings, "
              "and black stiletto heels"),
}
OUTFIT_MASTER = ("The reference image shows one character. Create a new photo of EXACTLY the same person: identical face, "
                 "identical two short pigtails, same body and height, wearing {outfit}. Calm, confident, slightly cool "
                 "expression with a faint smile. Photorealistic, full body from the top of the hair to the shoes, standing, "
                 "centered, plain pure white background, soft even studio light, no text.")
# 普通表情（服装套装用）
CALM_EXPR = {
    'calm': "calm, cool, faint smile",
    'cool': "cool and aloof, chin slightly up, unreadable eyes",
    'smile': "a soft genuine smile",
    'tease': "a teasing smirk, one eyebrow raised",
    'speechless': "deadpan, unimpressed half-lidded stare",
    'surprised': "surprised, eyes wide, lips parted",
    'happy': "laughing happily, eyes crinkled",
    'shy': "shy, looking aside with a light blush",
}


def outfit_variant_prompt(outfit, expr_text):
    return ("The FIRST image is the approved look of this character. Create a new photo of exactly the same person in "
            f"exactly the same outfit ({OUTFITS[outfit]}), same hair, same framing (full body, plain white background). "
            f"Change only the expression and pose to: {expr_text}. If the expression is extreme, make it cartoonishly "
            "exaggerated like an anime face fault but keep it photorealistic. Nothing sexual, no gore.")


if __name__ == '__main__':
    argv = sys.argv[1:]
    prov = G.pick_provider(argv)
    ref = ref_white()
    if argv and argv[0] == 'outfit_master':          # outfit_master <dinner|night> --n 2
        o = argv[1]; n = int(argv[argv.index('--n') + 1]) if '--n' in argv else 2
        for i in range(1, n + 1):
            G.generate(prov, OUTFIT_MASTER.format(outfit=OUTFITS[o]), [ref], f'{o}_master_{i}')
    elif argv and argv[0] == 'outfit_variants':      # outfit_variants <dinner|night> [表情...]
        o = argv[1]
        m = os.path.join(OUT, f'{o}_master.png')
        if not os.path.exists(m):
            sys.exit(f'先审核 {o} 定妆照并改名为 ref/genai_yyl/{o}_master.png')
        wanted = argv[2:] or list(CALM_EXPR)
        for e in wanted:
            text = CALM_EXPR.get(e) or EXPR['yyl_' + e]
            G.generate(prov, outfit_variant_prompt(o, text), [m, ref], f'yyl_{o}_{e}')
    else:
        names = [a for a in argv if a in EXPR] or list(EXPR)
        for n in names:
            G.generate(prov, BASE + EXPR[n] + ".", [ref], n)
