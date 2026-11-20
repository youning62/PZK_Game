## assets.rpy —— 图像与音频资源登记
##
## 所有资源路径集中在这里，剧本里只用名字。
## 立绘命名规则：<角色> <服装> <表情>，例如 show pzk casual smug

## ---------------------------------------------------------------------------
## 音频
## ---------------------------------------------------------------------------

init -10 python:
    def A(name):
        """返回实际存在的音频路径（优先 ogg，其次 wav / mp3）。"""
        for ext in (".ogg", ".wav", ".mp3"):
            path = "audio/" + name + ext
            if renpy.loadable(path):
                return path
        return "audio/" + name + ".ogg"

## BGM
define audio.bgm_title = "audio/main_song.mp3"
define audio.bgm_island = "audio/Beach_Song.mp3"     # 海岛探索（原有）
define audio.bgm_luxury = "audio/pzk-rich.mp3"       # 豪华生活（原有）
define audio.bgm_rap = "audio/pzk_rap.mp3"           # 潘子恺主题说唱（原有）
define audio.bgm_dream = A("bgm/dream")              # 梦境冲浪
define audio.bgm_comedy = A("bgm/comedy")            # 搞笑日常
define audio.bgm_heroine = A("bgm/heroine")          # 女主登场
define audio.bgm_awkward = A("bgm/awkward")          # 尴尬事件
define audio.bgm_dinner = A("bgm/dinner")            # 浪漫晚餐
define audio.bgm_tender = A("bgm/tender")            # 温柔情感
define audio.bgm_delivery = A("bgm/delivery")        # 外卖狂飙
define audio.bgm_tension = A("bgm/tension")          # 轻悬疑

## 音效
define audio.sfx_alarm_old = "audio/alarm.mp3"       # 原有闹钟
define audio.sfx_wakeup = "audio/wake-up.mp3"        # 原有起床声
define audio.sfx_waves = A("sfx/waves")
define audio.sfx_wind = A("sfx/wind")
define audio.sfx_phone = A("sfx/phone_ding")
define audio.sfx_vibrate = A("sfx/phone_vibrate")
define audio.sfx_engine = A("sfx/engine_start")
define audio.sfx_drive = A("sfx/engine_drive")
define audio.sfx_steps = A("sfx/footsteps_sand")
define audio.sfx_heels = A("sfx/footsteps_heels")
define audio.sfx_splash = A("sfx/splash")
define audio.sfx_thud = A("sfx/thud")
define audio.sfx_boing = A("sfx/boing")
define audio.sfx_scratch = A("sfx/record_scratch")
define audio.sfx_sparkle = A("sfx/sparkle")
define audio.sfx_shock = A("sfx/shock")
define audio.sfx_heart = A("sfx/heartbeat")
define audio.sfx_crickets = A("sfx/crickets")
define audio.sfx_door = A("sfx/door")
define audio.sfx_cash = A("sfx/cash")
define audio.sfx_clink = A("sfx/glass_clink")
define audio.sfx_mirror = A("sfx/mirror_ding")
define audio.sfx_doorbell = A("sfx/doorbell")
define audio.sfx_alarm = A("sfx/alarm_soft")

define audio.sfx_stat_up = A("sfx/stat_up")
define audio.sfx_stat_down = A("sfx/stat_down")
define SFX_STAT_UP = A("sfx/stat_up")
define SFX_STAT_DOWN = A("sfx/stat_down")
define SFX_CLICK = A("sfx/ui_click")
define SFX_HOVER = A("sfx/ui_hover")

## 环境音单独开一个循环声道，可与 BGM 叠加
init python:
    renpy.music.register_channel("ambient", mixer="sfx", loop=True)


## ---------------------------------------------------------------------------
## 背景（1920x1080）
## ---------------------------------------------------------------------------

image bg dream_beach = "images/bg/dream_beach.png"
image bg beach_day = "images/bg/beach_day.png"
image bg surf_beach = "images/bg/surf_beach.png"
image bg sunset_coast = "images/bg/sunset_coast.png"
image bg night_beach = "images/bg/night_beach.png"
image bg villa_bedroom = "images/bg/villa_bedroom.png"
image bg villa_bedroom_night = "images/bg/villa_bedroom_night.png"
image bg villa_closet = "images/bg/villa_closet.png"
image bg garage = "images/bg/garage.png"
image bg coast_road = "images/bg/coast_road.png"
image bg shopping_street = "images/bg/shopping_street.png"
image bg resort_hotel = "images/bg/resort_hotel.png"
image bg restaurant_sunset = "images/bg/restaurant_sunset.png"
image bg restaurant_night = "images/bg/restaurant_night.png"
image bg black = Solid("#000")
image bg white = Solid("#fff")

## CG
image cg dream_surf = "images/cg/dream_surf.png"
image cg yyl_surf = "images/cg/yyl_surf.png"
image cg first_meet = "images/cg/first_meet.png"
image cg lambo_beach = "images/cg/lambo_beach.png"
image cg first_dinner = "images/cg/first_dinner.png"


## ---------------------------------------------------------------------------
## 道具 / 手机画面
## ---------------------------------------------------------------------------

image phone time = Transform("images/phone-time.png", zoom=0.66)
image phone money = Transform("images/phone-money.png", zoom=0.66)
image ebike = Transform("images/props/ebike.png", zoom=0.62)


## ---------------------------------------------------------------------------
## 立绘
## ---------------------------------------------------------------------------

init -1 python:
    SPRITE_ZOOM = 0.70          # 1024x1536 画布
    DELIVERY_ZOOM = 0.43        # 1383x2508 画布

    def sprite(path, zoom=SPRITE_ZOOM):
        return Transform("images/sprites/" + path, zoom=zoom)

## 潘子恺 · 紧身背心（日常 / 约会）
image pzk casual normal = sprite("pzk_casual_normal.png")
image pzk casual narcissist = sprite("pzk_casual_narcissist.png")
image pzk casual smug = sprite("pzk_casual_smug.png")
image pzk casual proud = sprite("pzk_casual_proud.png")
image pzk casual shock = sprite("pzk_casual_shock.png")
image pzk casual awkward = sprite("pzk_casual_awkward.png")
image pzk casual angry = sprite("pzk_casual_angry.png")
image pzk casual shy = sprite("pzk_casual_shy.png")
image pzk casual gloom = sprite("pzk_casual_gloom.png")

## 潘子恺 · 花衬衫（冲浪）
image pzk surf normal = sprite("pzk_surf_normal.png")
image pzk surf laugh = sprite("pzk_surf_laugh.png")
image pzk surf damn = sprite("pzk_surf_damn.png")
image pzk surf awkward = sprite("pzk_surf_awkward.png")
image pzk surf shock = sprite("pzk_surf_shock.png")
image pzk surf silhouette = sprite("pzk_surf_silhouette.png")

## 潘子恺 · 外卖制服
image pzk delivery normal = sprite("pzk_delivery_normal.png", DELIVERY_ZOOM)
image pzk delivery happy = sprite("pzk_delivery_happy.png", DELIVERY_ZOOM)
image pzk delivery silly = sprite("pzk_delivery_silly.png", DELIVERY_ZOOM)
image pzk delivery angry = sprite("pzk_delivery_angry.png", DELIVERY_ZOOM)
image pzk delivery awkward = sprite("pzk_delivery_awkward.png", DELIVERY_ZOOM)
image pzk delivery proud = sprite("pzk_delivery_proud.png", DELIVERY_ZOOM)

## 杨永麟
image yyl calm = sprite("yyl_calm.png")
image yyl cool = sprite("yyl_cool.png")
image yyl smile = sprite("yyl_smile.png")
image yyl speechless = sprite("yyl_speechless.png")
image yyl tease = sprite("yyl_tease.png")
image yyl surprised = sprite("yyl_surprised.png")
image yyl happy = sprite("yyl_happy.png")
image yyl shy = sprite("yyl_shy.png")
image yyl silhouette = sprite("yyl_silhouette.png")

## 梦里尖叫的路人（用剪影表示）
image crowd = Transform("images/sprites/yyl_silhouette.png", zoom=0.5, alpha=0.55)
