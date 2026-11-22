## hud.rpy —— 游戏内界面：数值 HUD、飘字、章节标题卡、结算画面、UI 风格覆盖

## ---------------------------------------------------------------------------
## 数值 HUD（右上角）
## ---------------------------------------------------------------------------

screen stat_hud():
    zorder 90
    # 系统觉醒之前不显示任何数值；觉醒后显示系统 HUD
    if sys_active and stats_visible and not _menu:
        use sys_hud

init python:
    config.overlay_screens.append("stat_hud")

## 系统觉醒后的 HUD：余额 / 纯爱卡 / 当前目标好感 / 封印状态
screen sys_hud():
    frame:
        style "hud_frame"
        background Frame("gui/system/card.png", 20, 20)
        vbox:
            spacing 6
            hbox:
                spacing 10
                text "¥" style "hud_icon" color "#ffe066"
                text "余额" style "hud_label"
                text fmt_money(money) style "hud_num" min_width 180
            hbox:
                spacing 10
                text "◆" style "hud_icon" color "#5ff3ff"
                text "纯爱卡" style "hud_label"
                text fmt_money(credit_left()) style "hud_num" min_width 156
            if current_target:
                $ _t = targets[current_target]
                hbox:
                    spacing 10
                    text "♥" style "hud_icon" color "#ff7fae"
                    text _t["name"] style "hud_label"
                    bar value StaticValue(_t["aff"], 100) style "hud_bar_aff" xsize 140
                    text "[_t['aff']]%" style "hud_num"
                text ("纯爱封印：生效中" if _t["sealed"] else "纯爱封印：已解除") style "hud_label" size 18 color ("#ff9fc8" if _t["sealed"] else "#ffe066")
            hbox:
                spacing 10
                text "★" style "hud_icon" color "#ffd34d"
                text "装逼 [zb]" style "hud_label" size 18
    textbutton "系统" action Show("system_panel") style "hud_toggle" text_style "hud_toggle_text" xpos 1890 xanchor 1.0 ypos 238

style hud_frame:
    xpos 1890 xanchor 1.0 ypos 12
    padding (20, 14, 20, 14)
    background Frame(Solid("#0b1e33cc"), 0, 0)

style hud_icon:
    font gui.text_font
    size 24
    yalign 0.5
    min_width 26

style hud_label:
    font gui.text_font
    size 22
    color "#e8f4ff"
    yalign 0.5

style hud_num:
    font gui.text_font
    size 22
    color "#ffffff"
    min_width 44
    text_align 1.0
    yalign 0.5

style hud_bar_base:
    xsize 200
    ysize 12
    yalign 0.5
    left_bar Solid("#ffffff")
    right_bar Solid("#ffffff22")

style hud_bar_aff is hud_bar_base:
    left_bar Solid("#ff7fae")
style hud_bar_zb is hud_bar_base:
    left_bar Solid("#ffd34d")

style hud_toggle:
    padding (10, 4, 10, 4)
    background Solid("#0b1e3399")
    hover_background Solid("#1f4a7acc")

style hud_toggle_text:
    font gui.text_font
    size 18
    color "#cfe6ff"
    hover_color "#ffffff"


## ---------------------------------------------------------------------------
## 数值变化飘字
## ---------------------------------------------------------------------------

screen stat_popup(text, good=True, slot=0):
    zorder 95
    timer 1.8 action Hide()
    frame:
        at stat_popup_anim
        xalign 0.5
        ypos 160 + slot * 62
        padding (26, 8, 26, 8)
        background Solid("#2b7a4bdd" if good else "#7a2b4bdd")
        text text font gui.text_font size 30 color "#ffffff" outlines [(2, "#00000088", 0, 0)]

transform stat_popup_anim:
    alpha 0.0 yoffset 20
    easeout 0.25 alpha 1.0 yoffset 0
    pause 1.1
    easein 0.4 alpha 0.0 yoffset -30


## ---------------------------------------------------------------------------
## 章节标题卡
## ---------------------------------------------------------------------------

screen chapter_card(title, subtitle=""):
    zorder 80
    modal True
    add Solid("#000000d8")
    vbox:
        at chapter_card_anim
        xalign 0.5 yalign 0.45
        spacing 24
        text title font gui.text_font size 84 color "#ffffff" xalign 0.5 outlines [(4, "#0b2a4a", 0, 0)]
        if subtitle:
            text subtitle font gui.text_font size 40 color "#9fd8ff" xalign 0.5
    timer (0.05 if AUTOTEST else 3.0) action Return()
    key "dismiss" action Return()

transform chapter_card_anim:
    alpha 0.0 zoom 0.96
    easeout 0.8 alpha 1.0 zoom 1.0


## ---------------------------------------------------------------------------
## 手机消息弹窗（叠在画面上的通知）
## ---------------------------------------------------------------------------

screen phone_notice(title, body):
    zorder 85
    frame:
        at phone_notice_anim
        xalign 0.5 ypos 40
        xsize 900
        padding (30, 18, 30, 18)
        background Frame(Solid("#f4f6faee"), 0, 0)
        vbox:
            spacing 6
            text title font gui.text_font size 24 color "#5b6b80"
            text body font gui.text_font size 32 color "#14202e"

transform phone_notice_anim:
    yoffset -200
    easeout 0.35 yoffset 0
    on hide:
        easein 0.3 yoffset -200


## ---------------------------------------------------------------------------
## 章节结算
## ---------------------------------------------------------------------------

screen chapter_result(ending_code, ending_title, ending_desc):
    modal True
    zorder 100
    add Solid("#06101cee")
    vbox:
        xalign 0.5 yalign 0.5
        spacing 28
        text "第一章 · 结算" font gui.text_font size 56 color "#9fd8ff" xalign 0.5
        text "【结局 [ending_code]】[ending_title]" font gui.text_font size 48 color "#ffffff" xalign 0.5
        text ending_desc font gui.text_font size 30 color "#d6e6f5" xalign 0.5 text_align 0.5 xmaximum 1300
        null height 10
        grid 2 2:
            xalign 0.5
            spacing 14
            text "今日外卖收入" style "result_label"
            text "¥[delivery_income]" style "result_value"
            text "已收集结局" style "result_label"
            text ("%d / 4" % len(persistent.endings_seen)) style "result_value"
        null height 10
        textbutton "继续" action Return() xalign 0.5 style "result_button" text_style "result_button_text"
    if AUTOTEST:
        timer 0.05 action Return()

style result_label:
    font gui.text_font
    size 30
    color "#9fb6cc"
    xalign 1.0
    min_width 300
    text_align 1.0
style result_value:
    font gui.text_font
    size 30
    color "#ffffff"
    min_width 200
style result_button:
    padding (60, 14, 60, 14)
    background Solid("#1f6fb2")
    hover_background Solid("#3a93db")
style result_button_text:
    font gui.text_font
    size 34
    color "#ffffff"


## ---------------------------------------------------------------------------
## 对话框 / 选项 风格覆盖（screens.rpy 为 init offset -1，此处后加载会覆盖）
## ---------------------------------------------------------------------------

style window:
    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style say_dialogue:
    outlines [(2, "#06121f99", 0, 0)]
    line_spacing 6

style choice_vbox:
    ypos 470

style choice_button:
    background Frame("gui/button/choice_idle_background.png", 40, 10, 40, 10)
    hover_background Frame("gui/button/choice_hover_background.png", 40, 10, 40, 10)
    padding (60, 22, 60, 22)
    xsize 1185
    hover_sound SFX_HOVER
    activate_sound SFX_CLICK

style choice_button_text:
    idle_color "#e6f2ff"
    hover_color "#ffffff"
    size 34
    outlines [(2, "#06121f88", 0, 0)]


## ---------------------------------------------------------------------------
## 章节选择（标题菜单）
## ---------------------------------------------------------------------------

screen chapter_select():
    tag menu
    use game_menu(_("章节选择")):
        vbox:
            spacing 22
            textbutton "序章 · 入职测试" action Start("start")
            textbutton "第一章 · 梦里的女人 / 第一次晚餐" action Start("chapter1")
            textbutton "第二章 · 浪与骗局" action Start("chapter3")
            textbutton "第三章 · 骑手潘师傅（系统觉醒）" action Start("chapter4")
            textbutton "第四章 · 前上司李轩翔" action Start("chapter5")
            textbutton "第五章 · 九分袖与校花" action Start("chapter6")
            null height 20
            text "从中间章节开始时，之前的选择会按默认值处理。" size 24 color "#9fb6cc"
