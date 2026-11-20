## script.rpy —— 游戏入口与开场"入职测试"
##
## 剧情结构：
##   start            开场测试（BAD END 0）
##   chapter1         第一章 · 第一话「梦里的女人」   Chapter1.rpy
##   chapter2         第一章 · 第二话「第一次晚餐」   Chapter2.rpy
##   chapter1_finale  第一章结局判定与结算           Chapter2.rpy

label start:
    stop music fadeout 1.0
    $ stats_visible = False
    scene bg black
    with fade

    show pzk delivery normal at center_stage
    with dissolve

    p "在游戏开始之前，先回答我一个问题。"
    p "……"
    show pzk delivery proud at center_stage
    play sound sfx_sparkle
    p "我帅吗？"

    menu:
        p "回答我！"

        "你很帅。":
            jump prologue_pass

        "我家楼下的野狗都比你有姿色。":
            show pzk delivery silly at center_stage, shake
            play sound sfx_scratch
            p "？"
            p "你妈妈知道你这么说话吗？"
            tip "系统提示：你已被潘子恺拉黑。"
            play sound sfx_stat_down
            tip "【BAD END 0】野狗的胜利"
            $ record_ending("0")
            show pzk delivery happy at center_stage
            p "……算了算了。"
            p "我潘子恺的胸怀，比我的胸肌还宽广。"
            p "再给你一次机会。"
            jump prologue_retry

label prologue_retry:
    show pzk delivery proud at center_stage
    p "我，帅，吗？"

    menu:
        "你很帅。":
            jump prologue_pass
        "你非常帅。":
            jump prologue_pass
        "你帅到我想报警。":
            p "报警可以，记得跟警察说我帅。"
            jump prologue_pass

label prologue_pass:
    show pzk delivery happy at center_stage, hop
    play sound sfx_stat_up
    p "我就知道！"
    p "你这种审美水平，放在古代是要当宰相的。"
    tip "系统提示：恭喜你通过了潘子恺的入职测试。"
    p "接下来，你将以我的视角，体验一个帅哥平凡的一天。"
    show pzk delivery normal at center_stage
    p "小提示：右上角有三个数值。"
    $ stats_visible = True
    p "「好感」是她对我的好感。「装逼」是我的帅气输出。「社死」……"
    p "「社死」这个数值是策划强行加的，我这辈子都用不上。"
    p "那么——"
    hide pzk with dissolve
    jump chapter1
