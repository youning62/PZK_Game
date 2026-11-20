## variables.rpy —— 游戏状态变量与数值系统
##
## 所有会随存档保存的状态都用 default 声明（保证读档兼容）。
## 数值改动统一走 stat() 函数：自动限幅、播放音效、弹出飘字提示。

## ---------------------------------------------------------------------------
## 核心数值
## ---------------------------------------------------------------------------

default yyl_aff = 0          # 杨永麟好感度（-50 ~ 100）
default zb = 0               # 装逼值（0 ~ 100）：越高越飘
default shesi = 0            # 社死值（0 ~ 100）：越高越想原地消失
default sincere = 0          # 真诚值（隐藏）：杨永麟真正在意的东西

default delivery_income = 0  # 今日外卖收入（元）——潘子恺人生中唯一的"真实收入"
default stats_visible = True # HUD 是否显示

define AUTOTEST = False       # 自动测试时由 tools/autotest 覆盖为 True

## ---------------------------------------------------------------------------
## 剧情标记
## ---------------------------------------------------------------------------

default yyl_name = "冲浪的女人"   # 知道名字前的显示名

default dream_reply = None       # 梦里拒绝她的方式
default mirror_pose = None       # 早上对镜子摆的姿势
default delivery_rating = 0      # 今日差评/好评累计（星）
default first_line = None        # 初遇时的第一句话
default surf_test = None         # 冲浪三秒挑战的方式：honest / stubborn / cheat
default outfit = "casual"        # 约会穿搭：casual(紧身背心) / suit(西装) / hawaii(花衬衫)
default suit_burst = False       # 西装扣子是否崩飞
default practiced_line = None    # 对镜练习的情话
default search_tip = None        # 搜索到的攻略：money / mystery / sincere
default studied_menu = False     # 是否研究过菜单
default ride = None              # 去餐厅的交通工具：lambo / ebike / walk
default ordered = None           # 点菜方式
default took_order = False       # 约会中是否接了外卖单
default told_truth = False       # 是否说出了送外卖的真实理由
default got_sea_glass = False    # 是否收到海玻璃
default noticed_k = False        # 伏笔：注意到她手机上的"K"
default took_photo = False      # 和网红合影（晚餐时会被认出）
default wait_style = None        # 等她上岸时做了什么：pose / pushup / straw
default fire_lane_used = False   # "消防通道"梗是否已用
default asked_k = False          # 是否追问了"K"
default ch1_ending = None        # 第一章结局：A / B / C

## 跨周目记录（结局收集）
default persistent.endings_seen = set()


init -5 python:

    STAT_LABELS = {
        "yyl_aff": "杨永麟好感度",
        "zb": "装逼值",
        "shesi": "社死值",
        "sincere": "真诚",
    }

    STAT_LIMITS = {
        "yyl_aff": (-50, 100),
        "zb": (0, 100),
        "shesi": (0, 100),
        "sincere": (0, 100),
    }

    def stat(name, delta, quiet=False):
        """修改数值。name: 变量名；delta: 增量。"""
        lo, hi = STAT_LIMITS.get(name, (-9999, 9999))
        old = getattr(store, name)
        new = max(lo, min(hi, old + delta))
        setattr(store, name, new)

        if quiet or name == "sincere":
            return

        # 好感上升、装逼上升都是"好事"（在潘子恺看来）；社死上升是坏事。
        good = (delta > 0) if name != "shesi" else (delta < 0)
        if renpy.loadable(SFX_STAT_UP):
            renpy.sound.play(SFX_STAT_UP if good else SFX_STAT_DOWN, channel="audio")
        sign = "+" if delta > 0 else ""
        slot = ["yyl_aff", "zb", "shesi"].index(name)
        renpy.show_screen("stat_popup", text="{} {}{}".format(STAT_LABELS[name], sign, delta), good=good,
                          slot=slot, _tag="stat_popup_" + name)

    def record_ending(code):
        persistent.endings_seen.add(code)
        renpy.save_persistent()
