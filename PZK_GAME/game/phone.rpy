## phone.rpy —— 手机界面：微信式聊天、红包、朋友圈、相册
##
## 用法：
##   $ chat_open("丁虹依")                    # 清空并打开聊天窗口（右侧手机）
##   $ chat("me", "在吗")                     # 我发的文字
##   $ chat("her", "？")                      # 对方的文字
##   $ chat("me", "10", "rp")                 # 我发的红包（text = 金额）
##   $ chat("note", "丁虹依领取了你的红包")      # 灰色系统提示
##   $ chat_close()
##   show screen phone_moments(作者, 正文, 点赞, 评论列表)   # 朋友圈

default chat_title = ""
default chat_log = []

init python:
    def chat_open(title):
        store.chat_title = title
        store.chat_log = []
        renpy.show_screen("phone_chat")

    def chat(who, text, kind="text"):
        store.chat_log.append((who, kind, text))
        if who != "note" and renpy.loadable(SFX_CLICK):
            renpy.sound.play("audio/sfx/vibrate.ogg" if who == "her" and renpy.loadable("audio/sfx/vibrate.ogg") else SFX_CLICK, channel="audio")
        renpy.restart_interaction()

    def chat_close():
        renpy.hide_screen("phone_chat")

style phone_text:
    font gui.text_font
    size 24
    color "#1b1b1b"

transform phone_in:
    xoffset 500 alpha 0.0
    easeout 0.3 xoffset 0 alpha 1.0

screen phone_frame(title):
    frame:
        at phone_in
        xpos 1330 ypos 40 xsize 540 ysize 760
        background Frame(Solid("#111"), 0, 0)
        padding (14, 14, 14, 14)
        frame:
            xfill True yfill True
            background Solid("#ededed")
            padding (0, 0, 0, 0)
            vbox:
                frame:
                    xfill True ysize 70
                    background Solid("#f7f7f7")
                    text title style "phone_text" size 26 xalign 0.5 yalign 0.5 bold True
                transclude

screen phone_chat():
    zorder 60
    use phone_frame(chat_title):
        viewport:
            yinitial 1.0
            ysize 650
            vbox:
                spacing 14
                xfill True
                null height 6
                for _who, _kind, _txt in chat_log[-9:]:
                    if _who == "note":
                        text _txt style "phone_text" size 18 color "#999" xalign 0.5
                    elif _kind == "rp":
                        frame:
                            xalign (1.0 if _who == "me" else 0.0)
                            xoffset (-16 if _who == "me" else 16)
                            xsize 300 ysize 110
                            background Solid("#fa9d3b")
                            padding (18, 12, 18, 12)
                            vbox:
                                text "🧧 恭喜发财，大吉大利" style "phone_text" color "#fff" size 22
                                text ("¥" + _txt) style "phone_text" color "#fff" size 30 bold True
                                text "微信红包" style "phone_text" color "#ffe6c8" size 16
                    else:
                        frame:
                            xalign (1.0 if _who == "me" else 0.0)
                            xoffset (-16 if _who == "me" else 16)
                            xmaximum 400
                            background Solid("#95ec69" if _who == "me" else "#ffffff")
                            padding (16, 10, 16, 10)
                            text _txt style "phone_text"

screen phone_moments(author, body, likes, comments):
    zorder 60
    use phone_frame("朋友圈"):
        vbox:
            spacing 12
            xfill True
            null height 10
            text author style "phone_text" color "#576b95" bold True xpos 24
            text body style "phone_text" xpos 24 xmaximum 470
            frame:
                xpos 24 xsize 300 ysize 160
                background Solid("#d9d9d9")
                vbox:
                    xalign 0.5 yalign 0.5
                    text "[[聊天截图]" style "phone_text" size 18 color "#666" xalign 0.5
                    text "🧧 ¥10.00" style "phone_text" size 26 color "#fa9d3b" xalign 0.5
            frame:
                xpos 24 xsize 470
                background Solid("#f3f3f5")
                padding (12, 10, 12, 10)
                vbox:
                    spacing 6
                    text ("♡ " + likes) style "phone_text" size 18 color "#576b95"
                    for _n, _c in comments:
                        text ("{color=#576b95}" + _n + "{/color}：" + _c) style "phone_text" size 20
