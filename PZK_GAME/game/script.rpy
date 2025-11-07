# 游戏的脚本可置于此文件中。

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。

define l = Character('pzk')

image pzk meituan = "images/MeiTuan.PNG"
image pzk meituanwaimai = "images/MeiTuanWithCar.png"

# 游戏在此开始。

label start:
    
    # 显示一个背景。此处默认显示占位图，但您也可以在图片目录添加一个文件
    # （命名为 bg room.png 或 bg room.jpg）来显示。

    scene bg room

    # 显示角色立绘。此处使用了占位图，但您也可以在图片目录添加命名为
    # eileen happy.png 的文件来将其替换掉。
    
    # 此处显示各行对话。

    show pzk meituan

    e "shabi"
    
    menu:
        e "回答我！"
        "你觉得我是谁？":
            e "你觉得我是谁？"
        "你知道我是谁吗？":
            e "你知道我是谁吗？"
        "你认识我吗？":
            e "你认识我吗？"
            hide pzk meituan
            jump second_choice
    # 此处为游戏结尾。

    return

label second_choice:
    e "wo cao"
    return