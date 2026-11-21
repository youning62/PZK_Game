## system.rpy —— 「纯爱致富系统」：状态、规则、界面
##
## 核心规则（见 docs/system_design.md）：
##   1. 只扫描成年女性；颜值评分 ≥ 90 才能成为攻略对象
##   2. 每个对象独立好感度 0~100%；≥ 90% 视为攻略成功，结算奖金
##   3. 攻略相关消费走「纯爱卡」预授权：审核通过由系统支付，驳回则刷卡失败
##   4. 成功攻略后发放奖金（基础奖金 × 任务完成度 × 真诚系数）
##   5. 纯爱封印：对已绑定对象，好感度 < 90% 时宿主对其持续"功能性失灵"
##   6. 系统不能控制任何人的感情；好感只能靠剧情与选择变化

## ---------------------------------------------------------------------------
## 状态
## ---------------------------------------------------------------------------

default sys_active = False           # 系统是否已觉醒
default money = 0                    # 宿主真实余额（元）
default credit_limit = 0             # 纯爱卡预授权额度上限
default credit_used = 0              # 本期已使用额度
default reimbursed_total = 0         # 累计通过审核的金额
default rejected_count = 0           # 被驳回的次数（成就用）
default task_income = 0              # 任务奖励累计
default targets = {}                 # 攻略对象档案：id -> dict
default current_target = None        # 当前攻略对象 id
default tasks = []                   # 任务列表（dict）
default sys_panel_tab = "profile"    # 系统面板当前页

define SYSTEM_NAME = "纯爱致富系统"
define FIRST_TARGET_BASE_BONUS = 10000000   # 第一个攻略对象的基础奖金：一千万


init -4 python:

    def fmt_money(v):
        """¥12,345"""
        return "¥{:,}".format(int(v))

    # ---------------- 攻略对象 ----------------

    def bind_target(tid, name, age, job, score, intro, base_bonus=None):
        if base_bonus is None:
            base_bonus = store.FIRST_TARGET_BASE_BONUS
        if score < 90:
            raise Exception("颜值评分不足 90 的对象不能绑定：%s" % name)
        store.targets[tid] = dict(
            name=name, age=age, job=job, score=score, intro=intro,
            aff=0, stage="重逢", sealed=True, status="攻略中",
            base_bonus=base_bonus, notes=[],
        )
        store.current_target = tid

    def tgt(tid=None):
        return store.targets.get(tid or store.current_target)

    def love(tid, delta, quiet=False):
        """修改某个攻略对象的好感度（%）。"""
        t = store.targets[tid]
        old = t["aff"]
        t["aff"] = max(0, min(100, old + delta))
        if quiet or delta == 0:
            return
        good = delta > 0
        renpy.sound.play(SFX_STAT_UP if good else SFX_STAT_DOWN, channel="audio")
        sign = "+" if delta > 0 else ""
        renpy.show_screen("stat_popup", text="{} 好感度 {}{}%".format(t["name"], sign, delta),
                          good=good, slot=0, _tag="stat_popup_love")

    def set_stage(tid, stage):
        store.targets[tid]["stage"] = stage

    def add_note(tid, note):
        store.targets[tid]["notes"].append(note)

    # ---------------- 任务 ----------------

    def add_task(task_id, tid, title, desc, reward, hidden=False):
        for t in store.tasks:
            if t["id"] == task_id:
                return
        store.tasks.append(dict(id=task_id, tid=tid, title=title, desc=desc,
                                reward=reward, status="进行中", hidden=hidden))
        renpy.show_screen("sys_toast", title="新任务", body=title, _tag="sys_toast")
        if renpy.loadable(SFX_SYS_DING):
            renpy.sound.play(SFX_SYS_DING, channel="audio")

    def task(task_id):
        for t in store.tasks:
            if t["id"] == task_id:
                return t
        return None

    def complete_task(task_id, grade="完成"):
        t = task(task_id)
        if t is None or t["status"] != "进行中":
            return
        t["status"] = grade
        reward = t["reward"] if grade == "完成" else t["reward"] // 2
        store.money += reward
        store.task_income += reward
        renpy.show_screen("sys_toast", title="任务" + grade, body="{}  奖励 {}".format(t["title"], fmt_money(reward)),
                          _tag="sys_toast")
        if renpy.loadable(SFX_COIN):
            renpy.sound.play(SFX_COIN, channel="audio")

    def fail_task(task_id):
        t = task(task_id)
        if t and t["status"] == "进行中":
            t["status"] = "失败"
            renpy.show_screen("sys_toast", title="任务失败", body=t["title"], _tag="sys_toast")
            if renpy.loadable(SFX_ERROR):
                renpy.sound.play(SFX_ERROR, channel="audio")

    def tasks_done(tid):
        return len([t for t in store.tasks if t["tid"] == tid and t["status"] == "完成"])

    def tasks_total(tid):
        return len([t for t in store.tasks if t["tid"] == tid and not t["hidden"]])

    # ---------------- 奖金 ----------------

    def bonus_estimate(tid):
        """预计奖金 = 基础奖金 × (1 + 0.1 × 已完成任务) × 真诚系数(0.8~1.5)"""
        t = store.targets[tid]
        sincerity = 0.8 + min(0.7, store.sincere / 100.0)
        return int(t["base_bonus"] * (1 + 0.1 * tasks_done(tid)) * sincerity)

    # ---------------- 纯爱卡 ----------------

    def credit_left():
        return max(0, store.credit_limit - store.credit_used)


## ---------------------------------------------------------------------------
## 演出用 label
## ---------------------------------------------------------------------------

## 报销 / 预授权审核。verdict: "approved" / "rejected"
## approved：系统从纯爱卡额度支付；rejected：刷卡失败，宿主自付（如果钱够）或放弃
label sys_audit(item, amount, category, verdict, comment, self_pay=False):
    $ renpy.sound.play(SFX_SYS_SCAN, channel="audio")
    call screen sys_audit_screen(item, amount, category, verdict, comment)
    if verdict == "approved":
        $ credit_used += amount
        $ reimbursed_total += amount
    else:
        $ rejected_count += 1
        if self_pay:
            $ money -= amount
    return

## 扫描一个人并显示档案卡（tid 已绑定时显示完整档案）
label sys_scan(tid):
    $ renpy.sound.play(SFX_SYS_SCAN, channel="audio")
    show screen scan_overlay
    pause 1.2
    hide screen scan_overlay
    call screen target_card(tid)
    return

## 纯爱封印触发
label seal_alarm(line=None):
    $ renpy.sound.play(SFX_SEAL_LOCK, channel="audio")
    show screen seal_flash
    with vpunch
    pause 0.8
    hide screen seal_flash
    if line:
        xt "[line]"
    return

## 系统启动动画
label sys_boot():
    $ renpy.sound.play(SFX_SYS_BOOT, channel="audio")
    show screen glitch_overlay
    pause 0.6
    hide screen glitch_overlay
    show screen boot_screen
    pause 2.2
    hide screen boot_screen
    return


## ---------------------------------------------------------------------------
## 界面
## ---------------------------------------------------------------------------

## 系统说话时的对话框：蓝色全息
define xt = Character("系统", color="#5ff3ff", what_color="#d8fbff", what_prefix="【", what_suffix="】",
                      window_background=Frame("gui/system/toast.png", 40, 30), window_ysize=220,
                      window_yalign=0.92, window_xsize=1500, window_xalign=0.5,
                      who_outlines=[(3, "#003344", 0, 0)])

style sys_text:
    font gui.text_font
    color "#d8fbff"
    size 28

style sys_title:
    font gui.text_font
    color "#5ff3ff"
    size 40
    outlines [(2, "#003344", 0, 0)]

style sys_small:
    font gui.text_font
    color "#8fd8e8"
    size 22

style sys_button:
    padding (24, 10, 24, 10)
    background Frame("gui/system/card.png", 20, 20)
    hover_background Frame(Transform("gui/system/card.png", matrixcolor=BrightnessMatrix(0.25)), 20, 20)
    hover_sound SFX_HOVER
    activate_sound SFX_CLICK

style sys_button_text:
    font gui.text_font
    size 26
    color "#bff6ff"
    hover_color "#ffffff"
    selected_color "#ffe066"


## 启动画面
screen boot_screen():
    zorder 120
    add Solid("#000814e0")
    vbox:
        at boot_anim
        xalign 0.5 yalign 0.45
        spacing 18
        text "SYSTEM BOOT" style "sys_small" xalign 0.5
        text SYSTEM_NAME style "sys_title" size 90 xalign 0.5
        text "绑定宿主：潘子恺 ……  成功" style "sys_text" xalign 0.5
    add "gui/system/scanlines.png"

transform boot_anim:
    alpha 0.0 zoom 1.1
    easeout 0.5 alpha 1.0 zoom 1.0
    linear 0.05 alpha 0.6
    linear 0.05 alpha 1.0

screen glitch_overlay():
    zorder 121
    add "gui/system/glitch.png" at glitch_anim

transform glitch_anim:
    alpha 1.0 xoffset 0
    linear 0.05 xoffset 18 alpha 0.6
    linear 0.05 xoffset -12 alpha 1.0
    linear 0.05 xoffset 6 alpha 0.4
    linear 0.1 xoffset 0 alpha 0.0


## 扫描框
screen scan_overlay():
    zorder 110
    add "gui/system/scan_frame.png" at scan_anim

transform scan_anim:
    xalign 0.5 yalign 0.45 alpha 0.0 zoom 1.2
    easeout 0.3 alpha 1.0 zoom 1.0
    linear 0.15 alpha 0.6
    linear 0.15 alpha 1.0
    linear 0.15 alpha 0.6
    linear 0.15 alpha 1.0


## 攻略对象档案卡
screen target_card(tid):
    modal True
    zorder 115
    $ t = targets[tid]
    add Solid("#00081488")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.45
        xsize 1100 ysize 700
        background Frame("gui/system/panel.png", 72, 90, 72, 72)
        padding (70, 40, 70, 40)
        vbox:
            spacing 16
            text "攻略对象档案" style "sys_title"
            null height 6
            hbox:
                spacing 40
                vbox:
                    spacing 12
                    text "姓名：[t['name']]" style "sys_text" size 34
                    text "年龄：[t['age']]" style "sys_text"
                    text "职业：[t['job']]" style "sys_text"
                    text "颜值评分：[t['score']] / 100" style "sys_text" color "#ffe066"
                    text "当前好感度：[t['aff']]%" style "sys_text" color "#ff9fc8"
                    text "攻略进度：[t['stage']]" style "sys_text"
                vbox:
                    spacing 10
                    if t["sealed"]:
                        add "gui/system/seal_icon.png" xalign 0.5
                        text "纯爱封印：生效中" style "sys_small" color "#ff9fc8" xalign 0.5
                    else:
                        add "gui/system/seal_icon_open.png" xalign 0.5
                        text "纯爱封印：已解除" style "sys_small" color "#ffe066" xalign 0.5
            null height 4
            text t["intro"] style "sys_small" xmaximum 960
            text ("预计攻略奖金：" + fmt_money(bonus_estimate(tid))) style "sys_text" color "#ffe066"
    textbutton "关闭档案" action Return() style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 880
    if AUTOTEST:
        timer 0.05 action Return()

transform sys_window_in:
    alpha 0.0 yoffset 30
    easeout 0.3 alpha 1.0 yoffset 0


## 报销审核结果
screen sys_audit_screen(item, amount, category, verdict, comment):
    modal True
    zorder 115
    add Solid("#00081488")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.42
        xsize 1000 ysize 560
        background Frame("gui/system/panel.png", 72, 90, 72, 72)
        padding (70, 40, 70, 40)
        vbox:
            spacing 14
            text "纯爱卡 · 预授权审核" style "sys_title"
            null height 6
            text "申报项目：[item]" style "sys_text" size 32
            text ("申报金额：" + fmt_money(amount)) style "sys_text"
            text "申报类别：[category]" style "sys_text"
            null height 8
            text "审核意见：[comment]" style "sys_small" size 26 xmaximum 860
    if verdict == "approved":
        add "gui/system/stamp_approved.png" at stamp_in xpos 1230 ypos 520
    else:
        add "gui/system/stamp_rejected.png" at stamp_in xpos 1230 ypos 520
    timer 0.45 action Play("audio", SFX_STAMP_OK if verdict == "approved" else SFX_STAMP_NG)
    textbutton "确认" action Return() style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 860
    if AUTOTEST:
        timer 0.05 action Return()

transform stamp_in:
    anchor (0.5, 0.5) alpha 0.0 zoom 2.2 rotate -18
    pause 0.35
    easein 0.12 alpha 1.0 zoom 1.0 rotate -12


## 纯爱封印闪屏
screen seal_flash():
    zorder 118
    add Solid("#ff4f9a33")
    vbox:
        at seal_anim
        xalign 0.5 yalign 0.4
        spacing 10
        add "gui/system/seal_icon.png" xalign 0.5 zoom 1.6
        text "纯爱封印 · 生效中" style "sys_title" color "#ff9fc8" xalign 0.5 size 56

transform seal_anim:
    alpha 0.0 zoom 1.5
    easein 0.15 alpha 1.0 zoom 1.0


## 系统通知横幅
screen sys_toast(title, body):
    zorder 112
    timer 2.6 action Hide()
    frame:
        at sys_toast_anim
        xalign 0.5 ypos 30
        xsize 900 ysize 110
        background Frame("gui/system/toast.png", 40, 30)
        padding (40, 14, 40, 14)
        vbox:
            text title style "sys_small" color "#5ff3ff"
            text body style "sys_text" size 30

transform sys_toast_anim:
    yoffset -160 alpha 0.0
    easeout 0.3 yoffset 0 alpha 1.0
    pause 1.9
    easein 0.3 yoffset -160 alpha 0.0


## 系统主面板（HUD 按钮打开）
screen system_panel():
    modal True
    zorder 116
    add Solid("#00081499")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.5
        xsize 1100 ysize 760
        background Frame("gui/system/panel.png", 72, 90, 72, 72)
        padding (60, 30, 60, 30)
        vbox:
            spacing 14
            hbox:
                spacing 18
                text SYSTEM_NAME style "sys_title"
                null width 40
                textbutton "档案" action SetVariable("sys_panel_tab", "profile") selected sys_panel_tab == "profile" style "sys_button" text_style "sys_button_text"
                textbutton "任务" action SetVariable("sys_panel_tab", "tasks") selected sys_panel_tab == "tasks" style "sys_button" text_style "sys_button_text"
                textbutton "钱包" action SetVariable("sys_panel_tab", "wallet") selected sys_panel_tab == "wallet" style "sys_button" text_style "sys_button_text"
                textbutton "规则" action SetVariable("sys_panel_tab", "rules") selected sys_panel_tab == "rules" style "sys_button" text_style "sys_button_text"
            null height 10
            if sys_panel_tab == "profile":
                if current_target:
                    $ t = targets[current_target]
                    text "当前攻略对象：[t['name']]（[t['age']]岁 · [t['job']]）" style "sys_text"
                    text "颜值评分 [t['score']]    好感度 [t['aff']]%    进度：[t['stage']]" style "sys_text" color "#ff9fc8"
                    text ("纯爱封印：" + ("生效中" if t["sealed"] else "已解除")) style "sys_text"
                    text ("预计攻略奖金：" + fmt_money(bonus_estimate(current_target))) style "sys_text" color "#ffe066"
                    null height 8
                    text "系统备注：" style "sys_small"
                    for nline in t["notes"][-5:]:
                        text "· " + nline style "sys_small"
                else:
                    text "暂无攻略对象。" style "sys_text"
            elif sys_panel_tab == "tasks":
                viewport:
                    ysize 560
                    scrollbars "vertical"
                    mousewheel True
                    vbox:
                        spacing 10
                        for tk in tasks:
                            if not tk["hidden"] or tk["status"] != "进行中":
                                frame:
                                    background Frame("gui/system/card.png", 20, 20)
                                    padding (24, 12, 24, 12)
                                    xsize 940
                                    vbox:
                                        text "[[" + tk["status"] + "] " + tk["title"] style "sys_text" color ("#ffe066" if tk["status"] == "完成" else "#d8fbff")
                                        text tk["desc"] style "sys_small" xmaximum 880
                                        text "奖励：" + fmt_money(tk["reward"]) style "sys_small" color "#ffe066"
            elif sys_panel_tab == "wallet":
                text ("真实余额：" + fmt_money(money)) style "sys_text" size 34
                text ("纯爱卡额度：" + fmt_money(credit_left()) + " / " + fmt_money(credit_limit)) style "sys_text"
                text ("累计报销通过：" + fmt_money(reimbursed_total)) style "sys_text"
                text ("累计被驳回：%d 次" % rejected_count) style "sys_text"
                text ("任务奖励累计：" + fmt_money(task_income)) style "sys_text"
                text ("今日外卖收入：" + fmt_money(delivery_income)) style "sys_text"
            else:
                text "一、只扫描成年女性。颜值评分 ≥ 90 方可成为攻略对象。" style "sys_small" size 24
                text "二、好感度 0~100%。达到 90% 视为攻略成功。" style "sys_small" size 24
                text "三、攻略相关消费可用纯爱卡预授权。与攻略无关的消费一律驳回。" style "sys_small" size 24
                text "四、攻略成功后发放奖金：基础奖金 × 任务完成度 × 真诚系数。" style "sys_small" size 24
                text "五、纯爱封印：对已绑定对象，好感度未达 90% 前，宿主对其保持功能性失灵。" style "sys_small" size 24
                text "六、本系统不提供任何精神控制服务。感情只能靠宿主自己挣。" style "sys_small" size 24
                text "七、本系统不支持七天无理由退货。" style "sys_small" size 24
    textbutton "关闭" action Hide("system_panel") style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 960
