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

## 潘子恺 · 黑卫衣 + W 口罩（第一次晚餐的穿搭选项，帽子全程戴着）
image pzk hoodie normal = sprite("pzk_hoodie_normal.png")
image pzk hoodie proud = sprite("pzk_hoodie_proud.png")
image pzk hoodie awkward = sprite("pzk_hoodie_awkward.png")
image pzk hoodie shy = sprite("pzk_hoodie_shy.png")
image pzk hoodie shock = sprite("pzk_hoodie_shock.png")
image pzk hoodie gloom = sprite("pzk_hoodie_gloom.png")

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

## 杨永麟 · 第一次晚餐（黑色缎面吊带裙 + 披肩 + 黑色细高跟）
image yyl dinner calm = sprite("yyl_dinner_calm.png")
image yyl dinner cool = sprite("yyl_dinner_cool.png")
image yyl dinner smile = sprite("yyl_dinner_smile.png")
image yyl dinner tease = sprite("yyl_dinner_tease.png")
image yyl dinner speechless = sprite("yyl_dinner_speechless.png")
image yyl dinner surprised = sprite("yyl_dinner_surprised.png")
image yyl dinner happy = sprite("yyl_dinner_happy.png")
image yyl dinner shy = sprite("yyl_dinner_shy.png")
image yyl dinner jaw_drop = sprite("yyl_dinner_jaw_drop.png")
image yyl dinner brain_lag = sprite("yyl_dinner_brain_lag.png")
image yyl dinner dead_fish = sprite("yyl_dinner_dead_fish.png")
image yyl dinner creepy_smile = sprite("yyl_dinner_creepy_smile.png")
image yyl dinner smug_chad = sprite("yyl_dinner_smug_chad.png")

## 杨永麟 · 仙人跳之夜（酒红色长礼服）
image yyl night calm = sprite("yyl_night_calm.png")
image yyl night smile = sprite("yyl_night_smile.png")
image yyl night cool = sprite("yyl_night_cool.png")

## 潘子恺 · 破产后居家（洗旧 T 恤 + 大裤衩 + 人字拖）
image pzk home normal = sprite("pzk_home_normal.png")
image pzk home shock = sprite("pzk_home_shock.png")
image pzk home gloom = sprite("pzk_home_gloom.png")
image pzk home smug = sprite("pzk_home_smug.png")

## 潘子恺 · 租来的西装（小两号，九分袖）
image pzk rentsuit normal = sprite("pzk_rentsuit_normal.png")
image pzk rentsuit proud = sprite("pzk_rentsuit_proud.png")
image pzk rentsuit awkward = sprite("pzk_rentsuit_awkward.png")

## 杨永麟 · 夸张表情（Gemini 生成，用户已审核）
image yyl jaw_drop = sprite("yyl_jaw_drop.png")
image yyl derp = sprite("yyl_derp.png")
image yyl bleh = sprite("yyl_bleh.png")
image yyl villain = sprite("yyl_villain.png")
image yyl creepy_smile = sprite("yyl_creepy_smile.png")
image yyl waterfall_cry = sprite("yyl_waterfall_cry.png")
image yyl rage = sprite("yyl_rage.png")
image yyl dead_fish = sprite("yyl_dead_fish.png")
image yyl smug_chad = sprite("yyl_smug_chad.png")
image yyl brain_lag = sprite("yyl_brain_lag.png")

## 梦里尖叫的路人（用剪影表示）
image crowd = Transform("images/sprites/yyl_silhouette.png", zoom=0.5, alpha=0.55)


## ===========================================================================
## 第二部：破产 & 纯爱致富系统
## ===========================================================================

## BGM
define audio.bgm_scam = A("bgm/scam")              # 仙人跳之夜
define audio.bgm_broke = A("bgm/broke")            # 破产搞笑
define audio.bgm_rider = A("bgm/rider")            # 外卖员日常
define audio.bgm_system = A("bgm/system")          # 系统觉醒
define audio.bgm_lxx = A("bgm/lxx_theme")          # 李轩翔登场
define audio.bgm_office = A("bgm/office")          # 投行职场
define audio.bgm_city_date = A("bgm/city_date")    # 城市夜约会
define audio.bgm_lxx_soft = A("bgm/lxx_soft")      # 李轩翔的另一面

## 音效
define audio.sfx_rain = A("sfx/rain")
define audio.sfx_city = A("sfx/city_ambience")
define audio.sfx_office = A("sfx/office_ambience")
define audio.sfx_typing = A("sfx/typing")
define audio.sfx_elevator = A("sfx/elevator_ding")
define audio.sfx_ebike_horn = A("sfx/ebike_horn")
define audio.sfx_ebike_start = A("sfx/ebike_start")
define audio.sfx_claw = A("sfx/claw_machine")
define audio.sfx_door_burst = A("sfx/door_burst")
define audio.sfx_flash = A("sfx/camera_flash")
define audio.sfx_knock = A("sfx/knock")
define audio.sfx_call = A("sfx/phone_call")
define audio.sfx_sad = A("sfx/sad_trombone")
define audio.sfx_sting = A("sfx/dramatic_sting")
define audio.sfx_money_rain = A("sfx/money_rain")
define audio.sfx_glitch = A("sfx/glitch")
define audio.sfx_seal_unlock = A("sfx/seal_unlock")
define audio.sfx_sys_ding = A("sfx/system_ding")
define audio.sfx_coin = A("sfx/coin")

define SFX_SYS_BOOT = A("sfx/system_boot")
define SFX_SYS_DING = A("sfx/system_ding")
define SFX_SYS_SCAN = A("sfx/system_scan")
define SFX_STAMP_OK = A("sfx/stamp_approve")
define SFX_STAMP_NG = A("sfx/stamp_reject")
define SFX_ERROR = A("sfx/error_buzz")
define SFX_COIN = A("sfx/coin")
define SFX_SEAL_LOCK = A("sfx/seal_lock")

## 背景
image bg hotel_suite_night = "images/bg/hotel_suite_night.png"
image bg rental_room = "images/bg/rental_room.png"
image bg rental_room_night = "images/bg/rental_room_night.png"
image bg city_street_day = "images/bg/city_street_day.png"
image bg city_street_night = "images/bg/city_street_night.png"
image bg city_rain_night = "images/bg/city_rain_night.png"
image bg office_lobby = "images/bg/office_lobby.png"
image bg ib_office_night = "images/bg/ib_office_night.png"
image bg ib_trading_floor = "images/bg/ib_trading_floor.png"
image bg meeting_room = "images/bg/meeting_room.png"
image bg elevator = "images/bg/elevator.png"
image bg arcade_night = "images/bg/arcade_night.png"
image bg convenience_night = "images/bg/convenience_store_night.png"
image bg rooftop_night = "images/bg/rooftop_night.png"
image bg street_food_night = "images/bg/street_food_night.png"

## CG
image cg scam_night = "images/cg/scam_night.png"
image cg system_awaken = "images/cg/system_awaken.png"
image cg rider_rain = "images/cg/rider_rain.png"
image cg reunion = "images/cg/cg_reunion.png"
image cg claw_machine = "images/cg/cg_claw_machine.png"

## 潘子恺 · 破产后（外卖制服）新表情
image pzk delivery gloom = sprite("pzk_delivery_gloom.png", DELIVERY_ZOOM)
image pzk delivery shock = sprite("pzk_delivery_shock.png", DELIVERY_ZOOM)
image pzk delivery shy = sprite("pzk_delivery_shy.png", DELIVERY_ZOOM)
image pzk delivery tired = sprite("pzk_delivery_tired.png", DELIVERY_ZOOM)
image pzk delivery smug = sprite("pzk_delivery_smug.png", DELIVERY_ZOOM)
image pzk delivery sealed = sprite("pzk_delivery_sealed.png", DELIVERY_ZOOM)
image pzk casual sealed = sprite("pzk_casual_sealed.png")

## 李轩翔 · 职业装
image lxx cold = sprite("lxx_cold.png")
image lxx smirk = sprite("lxx_smirk.png")
image lxx angry = sprite("lxx_angry.png")
image lxx surprised = sprite("lxx_surprised.png")
image lxx speechless = sprite("lxx_speechless.png")
image lxx smile = sprite("lxx_smile.png")
image lxx laugh = sprite("lxx_laugh.png")
image lxx blush = sprite("lxx_blush.png")
image lxx tired = sprite("lxx_tired.png")
image lxx tongue = sprite("lxx_tongue.png")
image lxx silhouette = sprite("lxx_silhouette.png")
## 李轩翔 · 深夜卫衣
image lxx casual cold = sprite("lxx_casual_cold.png")
image lxx casual smile = sprite("lxx_casual_smile.png")
image lxx casual blush = sprite("lxx_casual_blush.png")
image lxx casual surprised = sprite("lxx_casual_surprised.png")
image lxx casual tongue = sprite("lxx_casual_tongue.png")

## 系统叠加层
image sys_scanlines = "gui/system/scanlines.png"


## ===========================================================================
## 第五章（Chapter6.rpy）
## ===========================================================================
image bg mall_atrium = "images/bg/mall_atrium.png"
image bg boutique = "images/bg/boutique.png"
image bg food_court = "images/bg/food_court.png"

## 李轩翔 · 周末便装（米色针织开衫 + 白T + 牛仔裤 + 小白鞋）
image lxx weekend cold = sprite("lxx_weekend_cold.png")
image lxx weekend smile = sprite("lxx_weekend_smile.png")
image lxx weekend smirk = sprite("lxx_weekend_smirk.png")
image lxx weekend angry = sprite("lxx_weekend_angry.png")
image lxx weekend blush = sprite("lxx_weekend_blush.png")
image lxx weekend laugh = sprite("lxx_weekend_laugh.png")
image lxx weekend surprised = sprite("lxx_weekend_surprised.png")
image lxx weekend tongue = sprite("lxx_weekend_tongue.png")

## 秦受 · 富二代追求者
image qin smug = sprite("qin_smug.png")
image qin sneer = sprite("qin_sneer.png")
image qin angry = sprite("qin_angry.png")
image qin shock = sprite("qin_shock.png")
image qin pale = sprite("qin_pale.png")

## 周沫 · 高中校花 / 精品店柜姐
image zhou pro_smile = sprite("zhou_pro_smile.png")
image zhou surprised = sprite("zhou_surprised.png")
image zhou grin = sprite("zhou_grin.png")
image zhou awkward = sprite("zhou_awkward.png")
image zhou tease = sprite("zhou_tease.png")
