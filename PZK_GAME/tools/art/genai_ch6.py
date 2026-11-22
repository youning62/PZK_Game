"""第五章（Chapter6.rpy）用的新人物 / 新穿搭 / 背景（Gemini）。
用法（tools/art 目录）：
    PZK_GEMINI_MODEL=gemini-3-pro-image PZK_IMAGE_SIZE=2K python3 genai_ch6.py masters
    PZK_GEMINI_MODEL=gemini-3-pro-image PZK_IMAGE_SIZE=2K python3 genai_ch6.py bgs
    ... python3 genai_ch6.py variants <lxxw|qin|zhou>        （定妆照通过后）
输出：ref/genai_ch6/
"""
import os, sys, json, base64, requests
import genai_lxx as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'ref', 'genai_ch6')
os.makedirs(OUT, exist_ok=True)
G.OUT = OUT

FRAME = ("Photorealistic full-body photo from the top of the head to the shoes, standing, centered, plain pure white "
         "background, soft even studio light, no props unless described, no text, no logos.")

LXX_MASTER = os.path.join(HERE, 'ref', 'genai', 'master.png')     # 已审核的李轩翔职业装定妆照

CHARS = {
    # 李轩翔 · 周末便装（第三套：既不是西装，也不是红色皮衣）
    'lxxw': dict(
        refs=[LXX_MASTER],
        master=("The reference image shows a woman. Create a new photo of EXACTLY the same woman (identical face, honey-blonde "
                "short hair, rimless light-brown tinted glasses, red lipstick, same body) in a relaxed weekend outfit: a cream "
                "chunky-knit cardigan over a fitted white T-shirt, high-waisted light-wash wide-leg jeans, clean white sneakers, "
                "small gold hoop earrings, a small black leather shoulder bag. Calm, cool expression, one hand on the bag strap. "
                + FRAME),
        expr={'cold': "calm and cool, unimpressed", 'smile': "a small genuine smile", 'smirk': "a confident smirk, one eyebrow raised",
              'angry': "coldly furious: narrowed eyes, tight lips", 'blush': "flustered, looking aside, light blush",
              'laugh': "laughing out loud, eyes crinkled", 'surprised': "surprised, eyes wide", 'tongue': "sticking her tongue out cheekily, one eye squinted"}),
    # 秦受 · 富二代追求者（虚构人物）
    'qin': dict(
        refs=[],
        master=("A fictional arrogant rich heir: an East Asian (Han Chinese) man about 30, clearly Chinese facial features, black hair, slicked-back hair, handsome in a smug way, a flashy "
                "tailored royal-blue suit with a black silk shirt unbuttoned at the collar, a chunky gold watch, pointed "
                "patent leather shoes, a car key dangling from one finger. Smug, condescending expression, chin up. " + FRAME),
        expr={'smug': "smug and condescending, chin up, looking down his nose", 'sneer': "sneering mockingly, pointing a finger",
              'angry': "furious, face red, jabbing a finger", 'shock': "shocked, mouth open, eyes wide, car key falling",
              'pale': "humiliated and pale, sweating, forced stiff smile"}),
    # 周沫 · 高中校花，如今在奢侈品店做柜姐（虚构人物）
    'zhou': dict(
        refs=[],
        master=("A fictional very pretty Chinese woman about 26, bright friendly eyes, long dark hair in a neat high ponytail, "
                "light natural makeup, working as a luxury boutique sales associate: a fitted black uniform dress with a white "
                "collar, a small gold name badge (no readable text), black low heels, hands clasped in front in a professional "
                "pose, a professional polite smile. " + FRAME),
        expr={'pro_smile': "professional polite sales smile", 'surprised': "genuinely surprised, hand over mouth",
              'grin': "a big bright cheeky grin, the girl-next-door school-belle smile", 'awkward': "awkward smile, sweat drop, glancing away",
              'tease': "teasing, one eye winking, finger on lips"}),
}

BGS = {
    'mall_atrium': "Photorealistic interior of a luxurious modern Chinese shopping mall atrium on a weekend afternoon: multiple floors with glass railings, escalators, high-end shop fronts with blank or abstract signage, polished marble floor, skylight, a few blurred shoppers. Wide 16:9 composition, eye level, no readable brand names or logos.",
    'boutique': "Photorealistic interior of a high-end women's fashion boutique: elegant dresses on rails and mannequins, a central display table, warm spotlights, a beige sofa, a long mirror, a cash counter at the side, marble and brass details. Wide 16:9 composition, eye level, empty of people, no readable brand names or logos.",
    'food_court': "Photorealistic, slightly shabby but cosy shopping-mall basement food court: noodle and rice stalls with menu boards (no readable text), plastic trays, small tables, warm fluorescent light, a few blurred diners. Wide 16:9 composition, eye level, no logos.",
}


def gen(prompt, refs, name, aspect='2:3'):
    model = os.environ.get('PZK_GEMINI_MODEL', 'gemini-3-pro-image')
    parts = [{'inline_data': {'mime_type': 'image/png', 'data': base64.b64encode(G.as_png_bytes(p)).decode()}} for p in refs]
    parts.append({'text': prompt})
    body = {'contents': [{'parts': parts}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': aspect, 'imageSize': '2K'}}}
    for attempt in range(2):
        r = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                          headers={'x-goog-api-key': G.key('gemini'), 'Content-Type': 'application/json'},
                          data=json.dumps(body), timeout=300)
        if r.status_code == 200:
            for c in r.json().get('candidates', []):
                for part in c.get('content', {}).get('parts', []):
                    d = part.get('inlineData') or part.get('inline_data')
                    if d:
                        p = os.path.join(OUT, name + '.png')
                        open(p, 'wb').write(base64.b64decode(d['data']))
                        print('saved', p, flush=True)
                        return p
        print(f'[{name}] attempt {attempt + 1} failed: {r.status_code} {r.text[:200]}', flush=True)
    return None


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'masters':
        for k, c in CHARS.items():
            gen(c['master'], c['refs'], f'{k}_master')
    elif cmd == 'bgs':
        for k, prompt in BGS.items():
            gen(prompt, [], k, aspect='16:9')
    elif cmd == 'variants':
        k = sys.argv[2]; c = CHARS[k]
        m = os.path.join(OUT, f'{k}_master.png')
        for e, t in c['expr'].items():
            prompt = ("The FIRST image is the approved look of this character. Create a new photo of exactly the same person in "
                      f"exactly the same outfit, same framing. Change only the expression and pose to: {t}. " + FRAME)
            gen(prompt, [m] + c['refs'], f'{k}_{e}')
