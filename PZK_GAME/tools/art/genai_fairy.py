"""纯爱致富系统 · 系统小精灵：以参考照片的脸生成 Q 版全息小精灵，及其表情。

用法（tools/art 目录，key 同 genai_lxx.py）：
    PZK_GEMINI_MODEL=gemini-3-pro-image PZK_IMAGE_SIZE=2K python3 genai_fairy.py master --n 3
    （用户审核通过后，把选中的改名为 ref/genai_fairy/fairy_master.png）
    ... python3 genai_fairy.py variants [fairy_名字 ...]
背景统一为纯绿色（#00FF00），方便抠图：import_fairy.py
"""
import os, sys
import genai_lxx as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'ref', 'genai_fairy')
os.makedirs(OUT, exist_ok=True)
G.OUT = OUT
REFS = [os.path.join(HERE, 'ref', f) for f in ('fairy_ref_default.jpg', 'fairy_ref_neutral.jpg', 'fairy_ref_wide.jpg')]

LOOK = ("a tiny floating digital fairy / game-system mascot with chibi proportions (huge head about half of the height, "
        "tiny body). The HEAD is a photorealistic copy of this young man's head from the reference photos: same face, "
        "same very messy, frizzy, puffed-up brown hair with blond highlights, same small silver earrings. The BODY has NO "
        "clothes at all: it is a smooth, solid pure-black silhouette body (like a shadow figure, no details, no skin), tiny "
        "arms and legs. Two translucent glowing cyan holographic circuit-pattern wings, a faint cyan glow outline around the "
        "whole figure, tiny sparkles. Floating in mid-air, whole figure visible, centered, facing the camera.")
BG = ("Background: one flat solid pure green colour (#00FF00) everywhere, no gradient, no shadow, no floor, no text.")

MASTER = (f"The reference photos show one young man. Create {LOOK} Facial expression: EXACTLY the expression of the FIRST "
          "reference photo — eyes squinting and looking sideways, lips pushed out into a lopsided duck face, nose scrunched. "
          f"{BG}")

# 全部是暴走漫画式的极度夸张表情（真人脸 + 扭曲到荒诞），不使用任何现成的网络梗角色形象
EXPR = {
    'fairy_default': "EXACTLY the first reference photo's expression: squinting sideways, lopsided duck-face lips, scrunched nose",
    'fairy_mock_laugh': "mocking laugh: eyes squeezed shut into lines, an enormous closed-mouth grin with bunched-up cheeks, chin up, absolutely smug",
    'fairy_grimace': "extreme grimace: whole face scrunched as tight as possible, eyes shut, mouth stretched super wide showing clenched teeth, deep wrinkles",
    'fairy_side_eye': "ultimate contempt: face turned slightly away, eyes looking sideways with heavy lids, one corner of the mouth pulled way down, nostrils flared",
    'fairy_rage_scream': "volcanic rage, but it MUST stay clearly the same young man's face (same eyes, nose, face shape, same frizzy brown-blond hair as the first image): mouth wide open screaming, forehead veins, face turned red, small steam puffs from the ears",
    'fairy_jaw_drop': "shock: eyes bulging out like ping-pong balls, jaw dropped absurdly low, face pale",
    'fairy_cry_laugh': "crying with laughter: eyes squeezed, streams of tears, mouth wide open laughing, red face",
    'fairy_soul_leave': "completely dead inside: eyes empty and unfocused looking up, mouth hanging open, a small translucent ghost of himself floating out of his mouth",
    'fairy_evil_grin': "evil scheming grin: eyes narrowed to slits, a huge sharp toothy grin stretching ear to ear, fingers steepled",
    'fairy_eyeroll': "exasperated eye-roll: eyes rolled up showing mostly whites, mouth a flat line, one hand on the forehead",
}


def variant_prompt(e):
    return ("The FIRST image is the approved design of this little fairy. Create a new image of exactly the same fairy (same "
            "face, same frizzy hair, same earrings, same pure-black clothes-less silhouette body, same wings, same proportions "
            "and size in frame). Change only "
            f"the expression and pose to: {EXPR[e]}. Make the face photorealistic but distorted to an absurd, meme-like extreme, "
            f"like a rage-comic reaction face. {BG}")


if __name__ == '__main__':
    argv = sys.argv[1:]
    prov = G.pick_provider(argv)
    cmd = argv[0] if argv else 'master'
    if cmd == 'master':
        n = int(argv[argv.index('--n') + 1]) if '--n' in argv else 3
        for i in range(1, n + 1):
            G.generate(prov, MASTER, REFS, f'fairy_master_{i}')
    else:
        m = os.path.join(OUT, 'fairy_master.png')
        if not os.path.exists(m):
            sys.exit('先审核定妆照，把选中的改名为 ref/genai_fairy/fairy_master.png')
        names = [a for a in argv[1:] if a in EXPR] or list(EXPR)
        for n in names:
            G.generate(prov, variant_prompt(n), [m] + REFS, n)
