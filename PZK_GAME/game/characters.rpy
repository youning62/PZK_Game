## characters.rpy —— 角色定义

## 潘子恺：主角，第一人称。说出口的话用 p，内心吐槽用 pt。
define p = Character("潘子恺", color="#6fc3ff", who_outlines=[(3, "#0b2a4a", 0, 0)])
define pt = Character(None, what_color="#bfe6ff", what_prefix="（", what_suffix="）", what_italic=False)

## 杨永麟：知道名字之前显示为"冲浪的女人"
define y = Character("[yyl_name]", color="#ff8fb8", who_outlines=[(3, "#4a0b26", 0, 0)])

## 旁白（潘子恺视角的叙述）
define n = Character(None)

## 系统提示 / 屏幕文字
define tip = Character(None, what_color="#ffe066", what_bold=True, what_text_align=0.5, what_xalign=0.5)

## 配角
define girl1 = Character("沙滩女孩A", color="#ffd27f")
define girl2 = Character("沙滩女孩B", color="#ffd27f")
define dream_guy = Character("冲浪的男人", color="#6fc3ff")
define influencer = Character("网红小姐姐", color="#ff9f6b")
define auntie = Character("椰子鸡阿姨", color="#c8e07a")
define waiter = Character("服务生", color="#d9c6a5")
define manager = Character("餐厅经理", color="#d9c6a5")
define app = Character("岛团外卖", color="#ffcc00", what_color="#fff2b3")
define guest = Character("邻桌大叔", color="#c8b0ff")
define mom = Character("妈", color="#ffb0b0")
define mystery_voice = Character("？？？", color="#aaaaaa", what_color="#cccccc")
