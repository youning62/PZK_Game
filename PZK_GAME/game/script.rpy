# 游戏的脚本可置于此文件中。

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。

define e = Character('pzk')

image pzk meituan :
    "images/外卖小哥pzk.PNG"
    xalign 0.5
    yalign 0.1
    zoom 0.5

image pzk angry :
    "images/pzk_angry.PNG"
    xalign 0.5
    yalign 0.1
    zoom 0.5

image pzk happy :
    "images/pzk_happy.PNG"
    xalign 0.5
    yalign 0.1
    zoom 0.5

# 游戏在此开始。

label start:
    
    stop music fadeout 1.0
    # 显示一个背景。此处默认显示占位图，但您也可以在图片目录添加一个文件
    # （命名为 bg room.png 或 bg room.jpg）来显示。

    scene bg room

    # 显示角色立绘。此处使用了占位图，但您也可以在图片目录添加命名为
    # eileen happy.png 的文件来将其替换掉。
    
    # 此处显示各行对话。

    show pzk meituan

    e "在游戏开始之前，先回答我一个问题"
    e "..."
    e "我帅吗？"

    
    menu:
        e "回答我！"
        "你很帅":
            hide pzk meituan
            show pzk happy
            e "我就知道！"
            e "走，今天晚上去我房间, 我给你看看我的大宝贝"
            "{b}系统提示{/b}： 恭喜你你通过了pzk的测试"
            jump chapter1
        "我家楼下的野狗都比你有姿色" :
            hide pzk meituan
            show pzk angry
            e "?"
            jump second_choice

    return

label second_choice:
    e "你妈妈知道你这么说话吗？"
    "{b}系统提示{/b}： 你被pzk拉黑了，游戏结束。"
    hide pzk angry
    show pzk happy
    e "其实我可以再给你一次机会"
    e "穿上高跟鞋黑丝今晚来我房间"
    return