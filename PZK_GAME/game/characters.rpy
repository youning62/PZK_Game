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

## ---- 第二部 ----
define lx = Character("李轩翔", color="#c9a2ff", who_outlines=[(3, "#2a1046", 0, 0)])
define zhao = Character("赵磊", color="#a8d0a0")            # 前投行同事
define landlord = Character("房东老陈", color="#d8b48a")
define cop = Character("民警", color="#9fb8d8")
define thug1 = Character("花衬衫大哥", color="#e08080")
define thug2 = Character("金链子大哥", color="#e08080")
define thug3 = Character("眼镜大哥", color="#e08080")
define customer = Character("顾客", color="#c8c8c8")
define station = Character("站长老刘", color="#e0c070")      # 外卖站点站长
define guard = Character("保安", color="#a0a0a0")
define boss_zhang = Character("张总", color="#b0b0b0")
define shen = Character("沈眠", color="#ffb27f")             # 投资机构创始合伙人

## ---- 第五章 ----
define qin = Character("秦受", color="#7fb0ff", who_outlines=[(3, "#0a1a3a", 0, 0)])
define dhy = Character("[dhy_name]", color="#ffb6d9", who_outlines=[(3, "#3a0a24", 0, 0)])
define clerk = Character("店长", color="#d9c6a5")
define mall_guard = Character("商场保安", color="#a0a0a0")
