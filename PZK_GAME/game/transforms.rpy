## transforms.rpy —— 站位、镜头与演出动画

## ---------------------------------------------------------------------------
## 站位
## ---------------------------------------------------------------------------

transform center_stage:
    xalign 0.5 yalign 1.0 yoffset 40

transform left_stage:
    xalign 0.18 yalign 1.0 yoffset 40

transform right_stage:
    xalign 0.82 yalign 1.0 yoffset 40

transform far_right:
    xalign 0.95 yalign 1.0 yoffset 40

## 晚餐时"坐在桌后"：只露上半身
transform seated(x=0.5):
    crop (0.0, 0.0, 1.0, 0.64)
    xalign x yalign 1.0 yoffset 0

## 特写：放大到上半身
transform closeup:
    xalign 0.5 yalign 0.0 yoffset -40
    zoom 1.35

## 镜子里：轻微模糊、水平翻转
transform mirror_view:
    xalign 0.5 yalign 1.0 yoffset 40
    xzoom -1.0
    matrixcolor TintMatrix("#e8f4ff")

## 剪影（梦中看不清脸的人）
transform shadow_figure:
    matrixcolor BrightnessMatrix(-1.0)

## 手机画面
transform phone_pos:
    xalign 0.5 yalign 0.5

## 背景铺满（给非 16:9 的原图用）
transform bg_cover:
    xalign 0.5 yalign 0.5
    fit "cover" xysize (1920, 1080)

## ---------------------------------------------------------------------------
## 动画
## ---------------------------------------------------------------------------

## 惊吓抖动
transform shake:
    linear 0.03 xoffset -12
    linear 0.03 xoffset 12
    linear 0.03 xoffset -8
    linear 0.03 xoffset 8
    linear 0.03 xoffset -4
    linear 0.03 xoffset 0

## 原地小跳（得意、开心）
transform hop:
    easein 0.10 yoffset 10
    easeout 0.12 yoffset -30
    easein 0.12 yoffset 10
    easeout 0.08 yoffset 0

## 呼吸感（静止立绘不至于死板）
transform breathe:
    ease 2.0 zoom 1.006
    ease 2.0 zoom 1.0
    repeat

## 从画面外滑入
transform slide_in_right:
    xalign 1.4 yalign 1.0 yoffset 40
    easeout 0.5 xalign 0.82

transform slide_in_left:
    xalign -0.4 yalign 1.0 yoffset 40
    easeout 0.5 xalign 0.18

## 被撞飞出画面
transform knocked_out:
    easein 0.35 xoffset -900 yoffset 300 rotate -60 alpha 0.0

## 慢慢后退（尴尬）
transform shrink_back:
    ease 0.6 zoom 0.92 yoffset 60

## 凑近（心动）
transform lean_in:
    ease 0.6 zoom 1.06

## 镜头缓推（CG 用）
transform slow_zoom:
    xalign 0.5 yalign 0.5 zoom 1.0
    linear 12.0 zoom 1.08

## 梦境漂浮
transform dream_float:
    ease 2.5 yoffset -12
    ease 2.5 yoffset 12
    repeat

## 兰博基尼从右向左冲过画面（车库/公路用占位：用整张背景的横移代替）
transform pan_left:
    xalign 0.0
    linear 6.0 xalign 1.0

## 白光闪
define flash = Fade(0.1, 0.0, 0.5, color="#fff")
## 梦醒用的慢白闪
define dream_fade = Fade(0.6, 0.6, 1.2, color="#fff")
## 快速溶解
define qdissolve = Dissolve(0.2)
