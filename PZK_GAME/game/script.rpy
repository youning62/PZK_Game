# 游戏的脚本可置于此文件中。

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。

define e = Character('pzk')

image pzk meituan :
    "images/外卖小哥pzk.PNG"
    xalign 0.5
    yalign 0.1
    zoom 0.5

# 游戏在此开始。

label start:
    
    stop music fadeout 5.0
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
            e "我就知道！"
            e "走，今天晚上去我房间"
            jump second_choice
        "我家楼下的野狗都比你有姿色" :
            e "?"
            jump second_choice

    return

label second_choice:
    e "wo cao"
    return