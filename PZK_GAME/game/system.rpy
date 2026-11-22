## system.rpy —— 「纯爱致富系统」：状态、规则、演出、界面
##
## 规则（数据在 system_data.rpy）：
##   0. 系统分三档：none（未出现）→ primary（初级扫描）→ active（正式激活）。
##      正式激活条件：向一名颜值 ≥ 90 的成年女性完成一次被接受的真实赠与。
##   1. 扫描自由：任何人都能扫。陌生人只显示姓名、年龄、颜值评分。
##   2. 成年女性且评分 ≥ 90 才符合攻略条件。
##   3. 对符合条件的女性成功赠与 → 解锁人物特点、当前好感度、攻略奖励、攻略状态；
##      拒收 / 未完成不解锁。赠礼不改变好感度。
##   4. 好感度每人独立；≥ 90% 攻略成功 → 解除对她的纯爱封印 + 发放她的专属奖励。
##   5. 纯爱封印：每个已解锁档案的对象单独生效。
##   6. 舔狗基金：激活后用真钱充值，1 元 = 10,000 元基金，不可退、不设上限。
##      只能花在评分 ≥ 90 的成年女性身上（对方收到的是真钱）；自购、套现、无关消费一律驳回。
##      基金余额不是宿主的个人财富；首次激活的赠与不算充值。
##   7. 多目标从一开始就支持；系统不指定攻略对象，不提供精神控制。

## ---------------------------------------------------------------------------
## 状态（存档）
## ---------------------------------------------------------------------------

default sys_stage = "none"           # none / primary / active
default sys_active = False           # 正式激活（HUD、飘字以此为准）
default money = 0                    # 宿主真实余额（元）
default fund = 0                     # 舔狗基金余额
define FUND_RATE = 10000             # 1 元 = 10,000 元基金
default fund_recharged_rmb = 0       # 累计充值（真钱）
default fund_spent = 0               # 累计通过审核的基金消费
default fund_log = []                # [{item, amount, payee, verdict}]
default rejected_count = 0
default people_state = {}            # pid -> {scanned, unlocked, aff, sealed, success, gifts[]}
default focus_target = None          # HUD 显示谁（宿主在系统面板里自己选）
default owned_rewards = []
default sys_pending_announce = []
default sys_panel_tab = "profile"
default sys_panel_sel = None

define SYSTEM_NAME = "纯爱致富系统"
define SCORE_THRESHOLD = 90
define AFF_SUCCESS = 90
define GIFT_RESULT_TEXT = {"unlocked": "档案解锁", "recorded": "已记录", "refused": "被拒收",
                           "incomplete": "未完成", "ineligible": "不符合条件", "not_scanned": "未扫描"}


init -4 python:

    def fmt_money(v):
        return "¥{:,}".format(int(v)) if v == int(v) else "¥{:,.2f}".format(v)

    def ps(pid):
        st = store.people_state.get(pid)
        if st is None:
            st = dict(scanned=False, unlocked=False, aff=0, sealed=False, success=False, gifts=[])
            store.people_state[pid] = st
        return st

    def eligible(pid):
        p = PEOPLE[pid]
        return p["gender"] == "女" and p["age"] >= 18 and p["score"] >= SCORE_THRESHOLD

    def unlocked(pid):
        return ps(pid)["unlocked"]

    def sealed(pid):
        return ps(pid)["sealed"]

    def pursuing():
        return [k for k in PEOPLE if k in store.people_state
                and store.people_state[k]["unlocked"] and not store.people_state[k]["success"]]

    def scanned_people():
        return [k for k in PEOPLE if k in store.people_state and store.people_state[k]["scanned"]]

    def status_text(pid):
        st = ps(pid)
        if not eligible(pid):
            return "不符合攻略条件"
        if st["success"]:
            return "攻略成功"
        if st["unlocked"]:
            return "攻略进行中"
        return "未解锁"

    def reward_name(pid):
        rid = PEOPLE[pid]["reward"]
        return REWARDS[rid]["name"] if rid in REWARDS else "待定"

    def scan(pid):
        ps(pid)["scanned"] = True

    def give_gift(pid, item, value=0, kind="礼物", accepted=True, completed=True):
        """记录一次赠与并判定。返回 unlocked / recorded / refused / incomplete / ineligible / not_scanned。
        系统处于初级扫描时，第一次 unlocked 同时让系统正式激活（剧情里 call sys_activate 演出）。"""
        st = ps(pid)
        if not st["scanned"]:
            result = "not_scanned"
        elif not eligible(pid):
            result = "ineligible"
        elif not accepted:
            result = "refused"
        elif not completed:
            result = "incomplete"
        elif st["unlocked"]:
            result = "recorded"
        else:
            result = "unlocked"
        st["gifts"].append(dict(item=item, value=value, kind=kind, result=result))
        if result == "unlocked":
            st["unlocked"] = True
            st["sealed"] = True
            if store.focus_target is None:
                store.focus_target = pid
            _check_success(pid)
        return result

    def love(pid, delta, quiet=False):
        """好感度（%）。档案未解锁时也记录但不显示。达到 90% → 成功，播报排队（call sys_flush）。"""
        st = ps(pid)
        st["aff"] = max(0, min(100, st["aff"] + delta))
        if st["unlocked"] and store.sys_active and not quiet and delta != 0:
            good = delta > 0
            renpy.sound.play(SFX_STAT_UP if good else SFX_STAT_DOWN, channel="audio")
            renpy.show_screen("stat_popup", text="{} 好感度 {}{}%".format(PEOPLE[pid]["name"], "+" if good else "", delta),
                              good=good, slot=0, _tag="stat_popup_love")
        _check_success(pid)

    def _check_success(pid):
        st = ps(pid)
        if st["unlocked"] and not st["success"] and st["aff"] >= AFF_SUCCESS:
            st["success"] = True
            st["sealed"] = False
            rid = PEOPLE[pid]["reward"]
            if rid and rid not in store.owned_rewards:
                store.owned_rewards.append(rid)
            store.sys_pending_announce.append(pid)

    # ---------------- 舔狗基金 ----------------

    def fund_recharge(rmb):
        """用真钱充值。返回到账的基金数额。不可退。"""
        rmb = max(0, min(rmb, store.money))
        store.money -= rmb
        store.fund_recharged_rmb += rmb
        store.fund += rmb * FUND_RATE
        return rmb * FUND_RATE

    def fund_check(amount, payee, cashout=False):
        """消费审核。返回 (verdict, 理由)。payee：PEOPLE 里的 pid，或 None（不是给人的消费）。"""
        if store.sys_stage != "active":
            return ("rejected", "系统未激活。")
        if cashout:
            return ("rejected", "检测到套现意图。宿主的小算盘声音太大了。")
        if payee is None:
            return ("rejected", "收款方不是任何女性。与攻略无关的消费一律驳回。")
        if payee == "pzk":
            return ("rejected", "检测到收款人为宿主本人。颜值评分：-250。")
        if payee not in PEOPLE or not eligible(payee):
            return ("rejected", "收款方不是颜值 90 分以上的成年女性。")
        if amount > store.fund:
            return ("rejected", "基金余额不足。")
        return ("approved", "符合攻略消费条件。")


## ---------------------------------------------------------------------------
## 演出用 label
## ---------------------------------------------------------------------------

## 扫描（任何人；照片也行）：call sys_scan("dhy")
label sys_scan(pid, photo=False):
    $ renpy.sound.play(SFX_SYS_SCAN, channel="audio")
    show screen scan_overlay
    pause 1.0
    hide screen scan_overlay
    $ scan(pid)
    call screen person_card(pid, photo)
    return

## 赠与：call sys_gift("dhy", "红包", 10, "微信红包")
label sys_gift(pid, item, value=0, kind="礼物", accepted=True, completed=True):
    $ _gift_result = give_gift(pid, item, value, kind, accepted, completed)
    if _gift_result == "unlocked" and sys_stage == "active":
        $ renpy.sound.play(SFX_SEAL_LOCK, channel="audio")
        $ renpy.show_screen("sys_toast", title="档案解锁", body=PEOPLE[pid]["name"] + "  ·  纯爱封印 +1", _tag="sys_toast")
        call screen person_card(pid)
    return

## 好感度 + 成功播报：call sys_love("dhy", 5)
label sys_love(pid, delta):
    $ love(pid, delta)
    call sys_flush
    return

label sys_flush:
    while sys_pending_announce:
        $ _ann = sys_pending_announce.pop(0)
        call sys_reward_announce(_ann)
    return

label sys_reward_announce(pid):
    $ _aname = PEOPLE[pid]["name"]
    $ _rname = reward_name(pid)
    play sound sfx_sys_ding
    xt jaw_drop "叮——！！[_aname]好感度达到百分之九十。攻略成功！"
    $ renpy.sound.play(SFX_SEAL_LOCK, channel="audio")
    xt cry_laugh "对[_aname]的纯爱封印：解除。"
    xt evil_grin "发放专属奖励：「[_rname]」。"
    call screen person_card(pid)
    return

## 充值：call sys_recharge(100)
label sys_recharge(rmb):
    $ _got = fund_recharge(rmb)
    $ renpy.sound.play(SFX_COIN, channel="audio")
    call screen fund_recharge_screen(rmb, _got)
    return

## 舔狗基金消费审核：call sys_spend("小蓝", 3000000, None, "车辆")
## payee = 收款女性的 pid；approved 时扣基金，若 gift=True 同时记一次赠与（她收到的是真钱）
label sys_spend(item, amount, payee, category="攻略消费", cashout=False, comment=None, gift=False):
    $ _v, _why = fund_check(amount, payee, cashout)
    $ renpy.sound.play(SFX_SYS_SCAN, channel="audio")
    call screen sys_audit_screen(item, amount, category, _v, comment or _why)
    $ fund_log.append(dict(item=item, amount=amount, payee=payee, verdict=_v))
    if _v == "approved":
        $ fund -= amount
        $ fund_spent += amount
        if gift:
            call sys_gift(payee, item, amount, category)
    else:
        $ rejected_count += 1
    return

## 纯爱封印触发
label seal_alarm(line=None):
    $ renpy.sound.play(SFX_SEAL_LOCK, channel="audio")
    show screen seal_flash
    with vpunch
    pause 0.8
    hide screen seal_flash
    if line:
        xt soul_leave "[line]"
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
define xt = Character("系统", image="fairy", color="#5ff3ff", what_color="#d8fbff", what_prefix="【", what_suffix="】",
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
    use fairy_badge("jaw_drop", 560, 260, 1.2)


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


## 人物档案卡（扫描结果）。初级扫描时其余字段显示「系统未激活」，激活后显示「未解锁」
screen person_card(pid, photo=False):
    modal True
    zorder 115
    add Solid("#00081488")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.45
        xsize 1100 ysize 680
        background Frame("gui/system/panel.png", 72, 90, 72, 72)
        padding (70, 40, 70, 40)
        use person_fields(pid, photo)
    textbutton "关闭" action Return() style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 880
    if AUTOTEST:
        timer 0.05 action Return()
    use fairy_badge("evil_grin" if unlocked(pid) else "side_eye", 400, 40)

screen person_fields(pid, photo=False):
    $ p = PEOPLE[pid]
    $ st = ps(pid)
    $ _open = st["unlocked"] and sys_stage == "active"
    $ _lock = "未解锁" if sys_stage == "active" else "系统未激活"
    $ _dim = "#7f9fb2"
    vbox:
        spacing 12
        hbox:
            spacing 20
            text ("攻略对象档案" if _open else ("初级扫描" if sys_stage != "active" else "扫描结果")) style "sys_title"
            if photo:
                text "（照片扫描）" style "sys_small" yalign 0.5
        null height 4
        hbox:
            spacing 40
            vbox:
                spacing 10
                xsize 640
                text "姓名：[p['name']]" style "sys_text" size 34
                text "年龄：[p['age']]" style "sys_text"
                text "颜值评分：[p['score']]" style "sys_text" color ("#ffe066" if p["score"] >= 0 else "#ff6b6b") size (28 if p["score"] >= 0 else 40)
                text ("人物特点：" + (p["traits"] or "—") if _open else "人物特点：" + _lock) style "sys_text" color ("#d8fbff" if _open else _dim) xmaximum 640
                text ("当前好感度：%d%%" % st["aff"] if _open else "当前好感度：" + _lock) style "sys_text" color ("#ff9fc8" if _open else _dim)
                text ("攻略奖励：「%s」" % reward_name(pid) if _open else "攻略奖励：" + _lock) style "sys_text" color ("#ffe066" if _open else _dim)
                text ("攻略状态：" + status_text(pid) if _open else "攻略状态：" + _lock) style "sys_text" color ("#d8fbff" if _open else _dim)
            vbox:
                spacing 10
                if _open:
                    add ("gui/system/seal_icon.png" if st["sealed"] else "gui/system/seal_icon_open.png") xalign 0.5
                    text ("纯爱封印：生效中" if st["sealed"] else "纯爱封印：已解除") style "sys_small" color ("#ff9fc8" if st["sealed"] else "#ffe066") xalign 0.5


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
            text "舔狗基金 · 消费审核" style "sys_title"
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
    use fairy_badge("mock_laugh" if verdict == "approved" else "eyeroll", 440, 90)


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
    use fairy_badge("evil_grin", 1380, 260, 1.1)


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
    use fairy_badge("side_eye", 470, 0, 0.55)


transform sys_toast_anim:
    yoffset -160 alpha 0.0
    easeout 0.3 yoffset 0 alpha 1.0
    pause 1.9
    easein 0.3 yoffset -160 alpha 0.0


## 舔狗基金银行卡
screen fund_card():
    modal True
    zorder 115
    add Solid("#00081499")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.42 xsize 860 ysize 520
        background Frame(Solid("#c9a227"), 0, 0)
        padding (8, 8, 8, 8)
        frame:
            xfill True yfill True
            background Solid("#1a1206")
            padding (50, 40, 50, 40)
            vbox:
                spacing 18
                hbox:
                    text "舔狗基金银行卡" style "sys_title" color "#ffd34d" size 46
                    null width 60
                    text "PURE LOVE" style "sys_small" color "#c9a227" yalign 0.5
                frame:
                    xsize 110 ysize 80
                    background Solid("#d8b44a")
                text "6666  8888  5200  1314" style "sys_text" size 44 color "#fff6d0"
                hbox:
                    spacing 60
                    text "持卡人：潘子恺" style "sys_text" color "#fff6d0"
                    text "信用等级：-250" style "sys_text" color "#ff6b6b"
                text ("余额：" + fmt_money(fund)) style "sys_text" size 36 color "#ffd34d"
    textbutton "收下" action Return() style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 860
    if AUTOTEST:
        timer 0.05 action Return()
    use fairy_badge("evil_grin", 380, 120)

## 充值到账
screen fund_recharge_screen(rmb, got):
    modal True
    zorder 115
    add Solid("#00081499")
    vbox:
        at sys_window_in
        xalign 0.5 yalign 0.4
        spacing 24
        text "舔狗基金 · 充值成功" style "sys_title" xalign 0.5
        text (fmt_money(rmb)) style "sys_text" size 60 xalign 0.5
        text "× 10,000" style "sys_small" size 36 xalign 0.5
        text (fmt_money(got)) style "sys_title" size 110 color "#ffd34d" xalign 0.5 at stamp_in
        text "本充值不可退。" style "sys_small" xalign 0.5
    textbutton "确认" action Return() style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 880
    if AUTOTEST:
        timer 0.05 action Return()
    use fairy_badge("jaw_drop", 420, 120)


## 系统主面板（HUD「系统」按钮打开）
screen system_panel():
    modal True
    zorder 116
    add Solid("#00081499")
    frame:
        at sys_window_in
        xalign 0.5 yalign 0.5
        xsize 1240 ysize 800
        background Frame("gui/system/panel.png", 72, 90, 72, 72)
        padding (60, 30, 60, 30)
        vbox:
            spacing 14
            hbox:
                spacing 18
                text SYSTEM_NAME style "sys_title"
                null width 40
                for _tab, _lab in (("profile", "档案"), ("gifts", "赠与"), ("wallet", "钱包"), ("rules", "规则")):
                    textbutton _lab action SetVariable("sys_panel_tab", _tab) selected sys_panel_tab == _tab style "sys_button" text_style "sys_button_text"
            null height 6
            if sys_panel_tab == "profile":
                $ _seen = scanned_people()
                if not _seen:
                    text "还没有扫描过任何人。" style "sys_text"
                else:
                    $ _sel = sys_panel_sel if sys_panel_sel in _seen else _seen[0]
                    hbox:
                        box_wrap True
                        spacing 10
                        for _pid in _seen:
                            textbutton PEOPLE[_pid]["name"] action SetVariable("sys_panel_sel", _pid) selected (_sel == _pid) style "sys_button" text_style "sys_button_text"
                    use person_fields(_sel)
                    if unlocked(_sel) and not ps(_sel)["success"]:
                        textbutton ("HUD 显示中" if focus_target == _sel else "在 HUD 显示她") action SetVariable("focus_target", _sel) selected (focus_target == _sel) style "sys_button" text_style "sys_button_text"
            elif sys_panel_tab == "gifts":
                $ _rows = [(k, g) for k in scanned_people() for g in ps(k)["gifts"]]
                if not _rows:
                    text "暂无赠与记录。" style "sys_text"
                for _k, _g in _rows:
                    text ("%s ← %s（%s %s）→ %s" % (PEOPLE[_k]["name"], _g["item"], _g["kind"], fmt_money(_g["value"]), GIFT_RESULT_TEXT.get(_g["result"], _g["result"]))) style "sys_small" size 24
            elif sys_panel_tab == "wallet":
                text ("真实余额：" + fmt_money(money)) style "sys_text" size 34
                text ("舔狗基金余额：" + fmt_money(fund)) style "sys_text" color "#ffe066" size 34
                text "（基金不是宿主的个人财富，只能花在 90 分以上的成年女性身上）" style "sys_small"
                text ("累计充值：" + fmt_money(fund_recharged_rmb) + "（兑换比例 1 : 10,000，不可退）") style "sys_text"
                text ("累计基金消费：" + fmt_money(fund_spent)) style "sys_text"
                text ("累计被驳回：%d 次" % rejected_count) style "sys_text"
                text ("已获得奖励：" + ("、".join("「%s」" % REWARDS[r]["name"] for r in owned_rewards) or "无")) style "sys_text" color "#ffe066"
            else:
                text "一、扫描自由：任何人都能扫。陌生人只显示姓名、年龄、颜值评分。" style "sys_small" size 24
                text "二、成年女性且颜值评分 ≥ 90，才符合攻略条件。" style "sys_small" size 24
                text "三、向符合条件的女性成功赠与（红包/转账/礼物/请客等），解锁她的完整档案。拒收或未完成，不解锁。" style "sys_small" size 24 xmaximum 1100
                text "四、赠礼不等于好感。好感度只看对方的真实反应。" style "sys_small" size 24
                text "五、每位攻略对象好感度独立。达到 90% 即攻略成功，发放她的专属奖励。" style "sys_small" size 24
                text "六、纯爱封印：对每一位已解锁档案的对象单独生效，攻略成功后解除。" style "sys_small" size 24
                text "七、舔狗基金：1 元充值 = 10,000 元基金，不可退。只能花在 90 分以上的成年女性身上，自购、套现、无关消费一律驳回。" style "sys_small" size 24 xmaximum 1100
                text "八、可以同时攻略多位。攻略谁，宿主自己决定。本系统不提供精神控制服务。" style "sys_small" size 24
                text "九、本系统不支持七天无理由退货。" style "sys_small" size 24
    textbutton "关闭" action Hide("system_panel") style "sys_button" text_style "sys_button_text" xalign 0.5 ypos 980


## ---------------------------------------------------------------------------
## 系统小精灵
## ---------------------------------------------------------------------------
## 说话时：xt <表情> "台词"，精灵以侧边头像出现在系统对话框左上角（screens.rpy 的 say 屏幕）。
## 弹窗时：use fairy_badge("表情")。
## 表情：idle（默认嘟嘴斜眼）/ mock_laugh / grimace / side_eye / rage_scream / jaw_drop /
##       cry_laugh / soul_leave / evil_grin / eyeroll

define FAIRY_MOODS = ["idle", "mock_laugh", "grimace", "side_eye", "rage_scream", "jaw_drop",
                      "cry_laugh", "soul_leave", "evil_grin", "eyeroll"]

init python:
    for _fm in FAIRY_MOODS:
        renpy.image(("side", "fairy", _fm), Transform("images/fairy/fairy_%s.png" % _fm, zoom=0.62))
        renpy.image(("fairy", _fm), Transform("images/fairy/fairy_%s.png" % _fm, zoom=0.5))

transform fairy_float:
    yoffset 0
    ease 1.2 yoffset -10
    ease 1.2 yoffset 0
    repeat

transform fairy_pop:
    zoom 0.4 alpha 0.0
    easeout 0.25 zoom 1.0 alpha 1.0
    block:
        ease 1.2 yoffset -8
        ease 1.2 yoffset 0
        repeat

## 弹窗里的精灵角标
screen fairy_badge(mood="idle", x=250, y=60, z=1.0):
    add Transform("fairy " + mood, zoom=z) at fairy_pop xpos x ypos y xanchor 0.5 yanchor 0.0
