"""潘子恺：用 Gemini 生成新穿搭（黑色卫衣 + 帽子戴头上 + 黑色 W 口罩）及表情。
基准：现有立绘 pzk-morning.png（同一个人、同一副眼镜、同样的全身构图）。

用法（tools/art 目录，key 同 genai_lxx.py）：
    PZK_GEMINI_MODEL=gemini-3-pro-image PZK_IMAGE_SIZE=2K python3 genai_pzk.py master --n 3
    （用户审核通过后把选中的改名为 ref/genai_pzk/hoodie_master.png）
    ... python3 genai_pzk.py variants [pzk_hoodie_xxx ...]
"""
import os, sys
from PIL import Image
import genai_lxx as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'ref', 'genai_pzk')
os.makedirs(OUT, exist_ok=True)
G.OUT = OUT

SRC = os.path.join(HERE, '..', '..', 'game', 'images', 'pzk-morning.png')
REF_WHITE = os.path.join(OUT, '_ref_white.png')

OUTFIT = ("an oversized plain black pullover hoodie with the HOOD PULLED UP over his head, a black cloth face mask covering "
          "his nose and mouth with one big bold white letter 'W' printed in the middle of the mask (simple geometric W, no "
          "other logos), his same black-rimmed glasses worn over the mask, black jogger pants, black sneakers")
FRAME = ("Photorealistic full-body photo from the top of the hood to the shoes, standing, centered, same camera distance and "
         "body proportions as the reference, plain pure white background, soft even studio light, no props, no text other "
         "than the W on the mask.")

MASTER = ("The reference image shows one man. Create a new photo of EXACTLY the same man (same face, same hairline, same "
          f"glasses, same muscular build and height) wearing {OUTFIT}. Pose: relaxed and cool, one hand in the hoodie pocket, "
          f"like a masked DJ. Eyes calm and confident. {FRAME}")

EXPR = {
    'pzk_hoodie_normal': "calm, cool eyes looking at the camera, one hand in the hoodie pocket",
    'pzk_hoodie_proud': "extremely proud and smug: eyes squinting with a smile behind the mask, one hand raised making a DJ 'W' hand sign",
    'pzk_hoodie_awkward': "awkward and embarrassed: eyes looking away, one hand scratching the back of the hood, visible sweat drop on the forehead",
    'pzk_hoodie_shy': "shy and flustered: eyes looking down, light blush visible on the cheeks above the mask, hands fidgeting",
    'pzk_hoodie_shock': "shocked: eyes wide open behind the glasses, eyebrows raised high, body leaning back",
    'pzk_hoodie_gloom': "dejected: eyes half closed, shoulders slumped, head hanging slightly down",
}


# ---------------- 其他穿搭（按经济状况和场景设计）----------------
OUTFITS = {
    # 破产后，出租屋里的居家装
    'home': ("a washed-out, slightly stretched grey cotton T-shirt with a small hole near the hem, faded navy basketball "
             "shorts, cheap blue plastic flip-flops; messy just-woke-up hair, same glasses. NO face mask, NO hood: his whole face is visible"),
    # 破产后，系统批准租来的西装：按四年前的尺码，偏小，袖子短一截
    'rentsuit': ("a cheap rented dark grey business suit that is comically TWO sizes too small: the jacket sleeves stop halfway "
                 "down the forearms (clearly 'three-quarter sleeves'), the single button strains and pulls across his big chest "
                 "with visible tension wrinkles, the trousers end well above the ankles showing white socks, white shirt, a plain "
                 "dark tie crooked to one side, worn black shoes; same glasses; NO face mask, whole face visible"),
}
OUTFIT_MASTER = ("The reference image shows one man. Create a new photo of EXACTLY the same man (same face, hairline, glasses, "
                 "muscular build and height) wearing {outfit}. Neutral, slightly self-satisfied expression, standing naturally. "
                 + FRAME)


def variant_prompt(expr):
    return ("The FIRST image is the approved character look. Create a new photo of exactly the same man in exactly the same "
            f"outfit ({OUTFIT}), same framing. The hood stays up and the W mask stays on. Change the expression and pose to: "
            f"{EXPR[expr]}. Only the eyes, eyebrows and body language can show the emotion. {FRAME}")


def ref_white():
    if not os.path.exists(REF_WHITE):
        im = Image.open(SRC).convert('RGBA')
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
        bg.convert('RGB').save(REF_WHITE)
    return REF_WHITE


if __name__ == '__main__':
    argv = sys.argv[1:]
    prov = G.pick_provider(argv)
    cmd = argv[0] if argv else 'master'
    if cmd == 'master':
        n = int(argv[argv.index('--n') + 1]) if '--n' in argv else 3
        for i in range(1, n + 1):
            G.generate(prov, MASTER, [ref_white()], f'hoodie_master_{i}')
    elif cmd == 'variants':
        m = os.path.join(OUT, 'hoodie_master.png')
        if not os.path.exists(m):
            sys.exit('先审核定妆照，把选中的改名为 ref/genai_pzk/hoodie_master.png')
        names = [a for a in argv[1:] if a in EXPR] or list(EXPR)
        for n in names:
            G.generate(prov, variant_prompt(n), [m, ref_white()], n)


# ---------------- 居家装 / 租来的西装：表情 ----------------
OUTFIT_EXPR = {
    'home': {
        'normal': "neutral, slightly groggy, scratching his head",
        'shock': "shocked: eyes wide, mouth open, leaning back",
        'gloom': "miserable and broke: slumped shoulders, dead eyes, holding an empty wallet open",
        'smug': "suddenly smug and pumped: grinning, flexing one bicep",
    },
    'rentsuit': {
        'normal': "trying to look professional and serious, standing straight, tugging his too-short sleeve",
        'proud': "confident, presenting with one hand open like in a meeting, small proud smile",
        'awkward': "awkward: noticing his sleeves are too short, looking down at his exposed wrists, sweat drop",
    },
}


def outfit_variant_prompt(outfit, expr_text):
    return ("The FIRST image is the approved look of this man. Create a new photo of exactly the same man in exactly the same "
            f"outfit ({OUTFITS[outfit]}), same framing. Change only the expression and pose to: {expr_text}. {FRAME}")
