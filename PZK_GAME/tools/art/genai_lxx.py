"""李轩翔立绘：用云端图像模型，以参考照片的脸生成新穿搭 + 新表情。

API key 从本地文件读取（不放进仓库、不出现在对话里）：
    ~/.config/pzk/openai_key   或   ~/.config/pzk/gemini_key
两个都存在时默认用 Gemini（可用 --provider 指定）。

用法（在 tools/art 目录下）：
    python3 genai_lxx.py probe                 # 检查 key、列出可用的图像模型
    python3 genai_lxx.py master                # 生成"定妆照"（职业装，冷淡表情）——先人工确认像不像
    python3 genai_lxx.py variants [名字...]     # 以定妆照为基准生成全部 / 指定表情和穿搭
输出：tools/art/ref/genai/<名字>.png（原始生成图，白底），之后由 gen_lxx_photo.py 抠图入游戏。
"""
import base64, io, json, os, sys, time
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref')
OUT = os.path.join(REF, 'genai')
os.makedirs(OUT, exist_ok=True)
KEYDIR = os.path.expanduser('~/.config/pzk')

REF_PHOTOS = [os.path.join(REF, 'lxx_ref_front.jpg'), os.path.join(REF, 'lxx_ref_side.jpg')]

LOOK = ("short tousled golden honey-blonde hair with slightly darker roots, exactly the same colour and cut as in the reference photos, rimless light-brown tinted "
        "glasses like the reference, small silver stud earrings, natural makeup with red lipstick")
WORK = ("a tailored black blazer with a nipped waist over a white silk blouse, black pencil skirt just above the knee, "
        "sheer black stockings, black stiletto heels, a slim silver watch")
CASUAL = ("the same oversized burgundy-red leather jacket as in the reference photos (zip front, snap buttons, metal eyelets), "
          "a black turtleneck underneath, a thin silver necklace, loose light-grey wide-leg jeans, black ankle boots")
FRAME = ("Photorealistic full-body fashion photo, entire figure visible from the top of the hair to the shoes with a little margin, "
         "standing, centered, body at a slight three-quarter angle toward the camera, arms relaxed (one hand on hip). "
         "Plain pure white seamless studio background, soft even lighting, no shadows on the background, no props, no text, no logos.")

MASTER_PROMPT = (
    "The reference photos show one person. Create a NEW photo of a woman of about 30 who has this person's face: "
    "keep the same face shape, eyes, eyebrows, nose, lips, jawline and skin tone so she is clearly recognisable as the same "
    "face (like the person's twin sister). She is a powerful investment-bank managing director: tall, slim, elegant, confident. "
    f"Hair and accessories: {LOOK}. Outfit: {WORK}. Expression: calm, cool and slightly intimidating, lips closed. {FRAME}")

EXPR = {
    'cold': "calm, cool and slightly intimidating, lips closed, eyes looking straight at the camera",
    'smirk': "a confident smirk: one corner of the mouth raised, one eyebrow slightly raised",
    'angry': "visibly annoyed: furrowed brows, sharp narrowed eyes, mouth pressed tight",
    'surprised': "genuinely surprised: eyes wide, eyebrows raised, lips slightly parted",
    'speechless': "deadpan and unimpressed: half-lidded flat stare, flat mouth, as if hearing something ridiculous",
    'smile': "a small, soft, genuine smile with relaxed eyes",
    'laugh': "laughing out loud: eyes crinkled, mouth open in a real laugh",
    'blush': "shy and flustered: looking slightly away from the camera, a light blush on the cheeks, a small pout",
    'tired': "exhausted after an all-nighter: drooping eyelids, faint dark circles, collar slightly loosened",
    'tongue': ("sticking her tongue out at the camera in a cheeky, childish way, one eye slightly squinted, "
               "a rare goofy moment from an otherwise cool woman; same pose"),
}

# name -> (outfit, expression)
VARIANTS = {f'lxx_{e}': ('work', e) for e in EXPR}
VARIANTS.update({
    'lxx_casual_cold': ('casual', 'cold'),
    'lxx_casual_smile': ('casual', 'smile'),
    'lxx_casual_blush': ('casual', 'blush'),
    'lxx_casual_surprised': ('casual', 'surprised'),
    'lxx_casual_tongue': ('casual', 'tongue'),
})


def variant_prompt(outfit, expr):
    clothes = WORK if outfit == 'work' else CASUAL
    return ("The FIRST image is the character sheet of a woman. Create a new photo of exactly the same woman: identical face, "
            "identical hair, glasses, makeup, body shape and height, same camera distance and framing. "
            f"Outfit: {clothes}. Change her facial expression to: {EXPR[expr]}. Keep the face clearly the same person. {FRAME}")


# ---------------------------------------------------------------- providers

def key(name):
    p = os.path.join(KEYDIR, name + '_key')
    if os.path.exists(p):
        return open(p).read().strip()
    return None


def pick_provider(argv):
    if '--provider' in argv:
        return argv[argv.index('--provider') + 1]
    if key('gemini'):
        return 'gemini'
    if key('openai'):
        return 'openai'
    sys.exit('没有找到 API key：请先把 key 存到 ~/.config/pzk/gemini_key 或 ~/.config/pzk/openai_key')


def as_png_bytes(path, max_side=1536):
    im = Image.open(path).convert('RGB')
    im.thumbnail((max_side, max_side))
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()


def gen_gemini(prompt, images, model=None):
    model = model or os.environ.get('PZK_GEMINI_MODEL', 'gemini-2.5-flash-image')
    parts = [{'inline_data': {'mime_type': 'image/png', 'data': base64.b64encode(as_png_bytes(p)).decode()}} for p in images]
    parts.append({'text': prompt})
    body = {'contents': [{'parts': parts}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '2:3', **({'imageSize': os.environ['PZK_IMAGE_SIZE']} if os.environ.get('PZK_IMAGE_SIZE') else {})}}}
    r = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                      headers={'x-goog-api-key': key('gemini'), 'Content-Type': 'application/json'},
                      data=json.dumps(body), timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f'Gemini {r.status_code}: {r.text[:800]}')
    j = r.json()
    for c in j.get('candidates', []):
        for part in c.get('content', {}).get('parts', []):
            d = part.get('inlineData') or part.get('inline_data')
            if d:
                return base64.b64decode(d['data'])
    raise RuntimeError('Gemini 没有返回图片：' + json.dumps(j, ensure_ascii=False)[:800])


def gen_openai(prompt, images, model=None):
    model = model or os.environ.get('PZK_OPENAI_MODEL', 'gpt-image-1')
    files = [('image[]', (os.path.basename(p) + '.png', as_png_bytes(p), 'image/png')) for p in images]
    data = {'model': model, 'prompt': prompt, 'size': '1024x1536', 'quality': 'high', 'n': '1'}
    r = requests.post('https://api.openai.com/v1/images/edits',
                      headers={'Authorization': 'Bearer ' + key('openai')}, data=data, files=files, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f'OpenAI {r.status_code}: {r.text[:800]}')
    return base64.b64decode(r.json()['data'][0]['b64_json'])


def generate(provider, prompt, images, out_name, tries=2):
    fn = gen_gemini if provider == 'gemini' else gen_openai
    for i in range(tries):
        try:
            png = fn(prompt, images)
            p = os.path.join(OUT, out_name + '.png')
            Image.open(io.BytesIO(png)).save(p)
            print('saved', p, Image.open(p).size, flush=True)
            return p
        except Exception as e:
            print(f'[{out_name}] attempt {i + 1} failed: {e}', flush=True)
            time.sleep(3)
    return None


def probe(provider):
    if provider == 'gemini':
        r = requests.get('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200',
                         headers={'x-goog-api-key': key('gemini')}, timeout=60)
        print('status', r.status_code)
        if r.ok:
            for m in r.json().get('models', []):
                if 'image' in m['name'].lower():
                    print(' ', m['name'])
        else:
            print(r.text[:500])
    else:
        r = requests.get('https://api.openai.com/v1/models', headers={'Authorization': 'Bearer ' + key('openai')}, timeout=60)
        print('status', r.status_code)
        if r.ok:
            for m in r.json()['data']:
                if 'image' in m['id']:
                    print(' ', m['id'])
        else:
            print(r.text[:500])


if __name__ == '__main__':
    argv = sys.argv[1:]
    cmd = argv[0] if argv else 'probe'
    prov = pick_provider(argv)
    print('provider:', prov)
    if cmd == 'probe':
        probe(prov)
    elif cmd == 'master':
        n = int(argv[argv.index('--n') + 1]) if '--n' in argv else 1
        start = int(argv[argv.index('--start') + 1]) if '--start' in argv else 1
        for i in range(start, start + n):
            generate(prov, MASTER_PROMPT, REF_PHOTOS, 'master' if n == 1 and start == 1 else f'master_{i}')
    elif cmd == 'variants':
        master = os.path.join(OUT, 'master.png')
        if not os.path.exists(master):
            sys.exit('先运行 master，并把满意的一张命名为 ref/genai/master.png')
        names = [a for a in argv[1:] if a.startswith('lxx_')] or list(VARIANTS)
        cmaster = os.path.join(OUT, 'casual_master.png')
        for name in names:
            outfit, expr = VARIANTS[name]
            if outfit == 'casual':
                if not os.path.exists(cmaster):
                    print('跳过', name, '：皮衣定妆照还没审核通过（ref/genai/casual_master.png）'); continue
                refs = [cmaster, master] + REF_PHOTOS
            else:
                refs = [master] + REF_PHOTOS
            generate(prov, variant_prompt(outfit, expr), refs, name)
    elif cmd == 'casual_master':
        # 皮衣定妆照候选：需用户审核后改名为 casual_master.png
        master = os.path.join(OUT, 'master.png')
        n = int(argv[argv.index('--n') + 1]) if '--n' in argv else 3
        for i in range(1, n + 1):
            generate(prov, variant_prompt('casual', 'cold'), [master] + REF_PHOTOS, f'casual_master_{i}')
