## minigame.rpy —— 仙人跳之夜 · 俯视角逃脱小游戏
##
## 操作：WASD / 方向键移动，空格近战（推开敌人），跑到右上角「安全出口」即胜利。
## 敌人：花衬衫大哥、金链子大哥（追着打）、律师老公（扔「和解协议」，被砸中会减速）、
##       杨永麟（速度最快，绕着你走，扔高跟鞋）。敌人打不死，只能击退。
## 用法：call screen escape_minigame  →  返回 "win" / "lose"
## 美术：tools/art/gen_minigame.py（障碍物坐标与这里的 OBSTACLES 保持一致）

init python:
    import math, random
    import pygame_sdl2 as pygame

    MG_OX, MG_OY = 160, 150          # 地图在屏幕上的位置
    MG_W, MG_H = 1600, 900
    MG_OBSTACLES = [
        (120, 520, 360, 820), (520, 80, 760, 200), (880, 420, 1000, 560),
        (1180, 600, 1300, 900), (1180, 0, 1300, 330), (1380, 520, 1600, 620),
    ]
    MG_EXIT = (1480, 40, 1590, 170)
    MG_R = 34                        # 角色碰撞半径

    def _mg_img(name):
        return renpy.displayable("images/minigame/" + name + ".png")

    class _MGEntity(object):
        def __init__(self, kind, x, y, speed):
            self.kind, self.x, self.y, self.speed = kind, x, y, speed
            self.vx = self.vy = 0.0          # 击退速度
            self.stun = 0.0
            self.cool = random.uniform(0.5, 1.5)
            self.hit_cd = 0.0
            self.orbit = random.choice((-1, 1))

    def _mg_push_out(e):
        """把圆形角色推出矩形障碍物和地图边界。"""
        e.x = max(MG_R, min(MG_W - MG_R, e.x))
        e.y = max(MG_R, min(MG_H - MG_R, e.y))
        for (x0, y0, x1, y1) in MG_OBSTACLES:
            cx = max(x0, min(e.x, x1)); cy = max(y0, min(e.y, y1))
            dx, dy = e.x - cx, e.y - cy
            d2 = dx * dx + dy * dy
            if d2 < MG_R * MG_R:
                if d2 == 0:
                    # 中心在矩形内：从最近的边推出
                    opts = [(e.x - x0, -1, 0), (x1 - e.x, 1, 0), (e.y - y0, 0, -1), (y1 - e.y, 0, 1)]
                    dist, ox, oy = min(opts)
                    e.x += ox * (dist + MG_R); e.y += oy * (dist + MG_R)
                else:
                    d = math.sqrt(d2)
                    e.x = cx + dx / d * MG_R; e.y = cy + dy / d * MG_R

    class EscapeGame(renpy.Displayable):

        def __init__(self, **kw):
            super(EscapeGame, self).__init__(**kw)
            self.keys = set()
            self.last = None
            self.t = 0.0
            self.px, self.py = 470.0, 460.0
            self.face = (1.0, 0.0)
            self.hp = 6
            self.inv = 0.0
            self.slow = 0.0
            self.swing = 0.0
            self.swing_cd = 0.0
            self.result = None
            self.end_t = None
            self.msg = ""
            self.msg_t = 0.0
            self.enemies = [
                _MGEntity("thug1", 60, 330, 265),      # 从破开的门冲进来
                _MGEntity("thug2", 1240, 470, 255),    # 堵在通往走廊的门洞
                _MGEntity("thug1", 1420, 200, 250),    # 走廊上方第二个大哥
                _MGEntity("lawyer", 1450, 800, 125),   # 走廊下方扔「和解协议」
                _MGEntity("yyl", 1460, 330, 225),      # 守在出口前，扔高跟鞋
            ]
            self.shots = []      # [kind, x, y, vx, vy, life]
            self.floor = _mg_img("floor")
            self.tok = dict((k, _mg_img("tok_" + k)) for k in ("pzk", "thug1", "thug2", "lawyer", "yyl"))
            self.heel = _mg_img("proj_heel")
            self.paper = _mg_img("proj_paper")
            self.swing_img = _mg_img("swing")
            self.hf, self.he = _mg_img("heart_full"), _mg_img("heart_empty")
            self.say("他们冲进来了！跑！")

        def say(self, m):
            self.msg, self.msg_t = m, 2.2

        # ------------------------------------------------------------ 逻辑
        def attack(self):
            if self.swing_cd > 0 or self.result:
                return
            self.swing, self.swing_cd = 0.18, 0.6
            renpy.sound.play(audio.sfx_boing, channel="audio")
            fx, fy = self.face
            hit = False
            for e in self.enemies:
                dx, dy = e.x - self.px, e.y - self.py
                d = math.hypot(dx, dy) or 1
                # 前方 110px 内，或者贴身 70px 内
                if d < 70 or (d < 125 and (dx * fx + dy * fy) / d > 0.2):
                    e.vx, e.vy = dx / d * 650, dy / d * 650
                    e.stun = 0.8
                    hit = True
            if hit:
                renpy.sound.play(audio.sfx_thud, channel="audio")

        def hurt(self, why):
            if self.inv > 0 or self.result:
                return
            self.hp -= 1
            self.inv = 0.9
            renpy.sound.play(audio.sfx_shock, channel="audio")
            self.say(why)
            if self.hp <= 0:
                self.result, self.end_t = "lose", self.t
                self.say("……我被按在了地上。")

        def update(self, dt):
            self.t += dt
            for a in ("inv", "slow", "swing", "swing_cd", "msg_t"):
                setattr(self, a, max(0.0, getattr(self, a) - dt))
            if self.result:
                return
            # 玩家移动
            mx = (1 if ("d" in self.keys or "right" in self.keys) else 0) - (1 if ("a" in self.keys or "left" in self.keys) else 0)
            my = (1 if ("s" in self.keys or "down" in self.keys) else 0) - (1 if ("w" in self.keys or "up" in self.keys) else 0)
            if mx or my:
                n = math.hypot(mx, my)
                self.face = (mx / n, my / n)
                sp = 280 * (0.5 if self.slow > 0 else 1.0)
                self.px += mx / n * sp * dt
                self.py += my / n * sp * dt
                p = _MGEntity("p", self.px, self.py, 0)
                _mg_push_out(p)
                self.px, self.py = p.x, p.y
            # 到达出口
            x0, y0, x1, y1 = MG_EXIT
            if x0 - 20 < self.px < x1 + 20 and y0 - 20 < self.py < y1 + 20:
                self.result, self.end_t = "win", self.t
                self.say("安全出口！")
                return
            # 敌人
            for e in self.enemies:
                e.hit_cd = max(0.0, e.hit_cd - dt)
                if abs(e.vx) + abs(e.vy) > 5:
                    e.x += e.vx * dt; e.y += e.vy * dt
                    e.vx *= 0.86; e.vy *= 0.86
                if e.stun > 0:
                    e.stun -= dt
                else:
                    dx, dy = self.px - e.x, self.py - e.y
                    d = math.hypot(dx, dy) or 1
                    if e.kind in ("thug1", "thug2"):
                        e.x += dx / d * e.speed * dt; e.y += dy / d * e.speed * dt
                    else:
                        want = 330 if e.kind == "lawyer" else 250
                        rad = (d - want) / max(d, 1)
                        tx, ty = -dy / d * e.orbit, dx / d * e.orbit        # 绕圈
                        vx = dx * rad * 2.0 + tx * e.speed * 0.8
                        vy = dy * rad * 2.0 + ty * e.speed * 0.8
                        vn = math.hypot(vx, vy) or 1
                        e.x += vx / vn * e.speed * dt; e.y += vy / vn * e.speed * dt
                        e.cool -= dt
                        if e.cool <= 0:
                            spd = 520 if e.kind == "yyl" else 380
                            self.shots.append(["heel" if e.kind == "yyl" else "paper", e.x, e.y, dx / d * spd, dy / d * spd, 2.5])
                            e.cool = 1.05 if e.kind == "yyl" else 1.8
                    if d < MG_R * 2 - 4 and e.hit_cd <= 0 and e.kind in ("thug1", "thug2"):
                        e.hit_cd = 0.8
                        self.hurt({"thug1": "花衬衫大哥：「我是她哥！」", "thug2": "金链子大哥：「我是她老公！」"}[e.kind])
                _mg_push_out(e)
            # 投掷物
            for s in self.shots:
                s[1] += s[3] * dt; s[2] += s[4] * dt; s[5] -= dt
                if math.hypot(s[1] - self.px, s[2] - self.py) < MG_R + 10:
                    s[5] = 0
                    if s[0] == "heel":
                        self.hurt("一只高跟鞋砸在我脑门上。")
                    else:
                        self.slow = 1.6
                        self.say("律师老公：「请签收和解协议。」（移动变慢）")
                for (x0, y0, x1, y1) in MG_OBSTACLES:
                    if x0 < s[1] < x1 and y0 < s[2] < y1:
                        s[5] = 0
            self.shots = [s for s in self.shots if s[5] > 0 and 0 < s[1] < MG_W and 0 < s[2] < MG_H]

        # ------------------------------------------------------------ 绘制
        def blit_center(self, r, d, x, y, st, at, alpha=1.0, rot=0):
            if alpha < 1.0 or rot:
                d = Transform(d, alpha=alpha, rotate=rot)
            cr = renpy.render(d, 1920, 1080, st, at)
            w, h = cr.get_size()
            r.blit(cr, (int(MG_OX + x - w / 2), int(MG_OY + y - h / 2)))

        def render(self, width, height, st, at):
            dt = 0.0 if self.last is None else max(0.0, min(0.05, st - self.last))
            self.last = st
            self.update(dt)
            r = renpy.Render(width, height)
            r.blit(renpy.render(Solid("#120a0c"), width, height, st, at), (0, 0))
            r.blit(renpy.render(self.floor, MG_W, MG_H, st, at), (MG_OX, MG_OY))
            # 角色（按 y 排序，近大远小的遮挡关系）
            ents = [("pzk", self.px, self.py)] + [(e.kind, e.x, e.y) for e in self.enemies]
            for kind, x, y in sorted(ents, key=lambda t: t[2]):
                a = 1.0
                if kind == "pzk" and self.inv > 0 and int(self.t * 20) % 2 == 0:
                    a = 0.35
                self.blit_center(r, self.tok[kind], x, y - 20, st, at, alpha=a)
            if self.swing > 0:
                ang = math.degrees(math.atan2(self.face[1], self.face[0]))
                self.blit_center(r, self.swing_img, self.px + self.face[0] * 60, self.py + self.face[1] * 60 - 20, st, at, rot=ang)
            for s in self.shots:
                img = self.heel if s[0] == "heel" else self.paper
                self.blit_center(r, img, s[1], s[2], st, at, rot=(self.t * 720) % 360 if s[0] == "heel" else 0)
            # HUD
            for i in range(6):
                hr = renpy.render(self.hf if i < self.hp else self.he, 48, 44, st, at)
                r.blit(hr, (MG_OX + i * 56, 40))
            tip = Text("WASD 移动　空格 推开　跑到右上角「安全出口」", size=30, color="#ffffff", outlines=[(2, "#000", 0, 0)])
            tr = renpy.render(tip, 1200, 60, st, at)
            r.blit(tr, (MG_OX + 400, 46))
            if self.msg_t > 0:
                m = Text(self.msg, size=40, color="#ffe066", outlines=[(3, "#000", 0, 0)])
                mr = renpy.render(m, 1600, 80, st, at)
                w, h = mr.get_size()
                r.blit(mr, (int(960 - w / 2), 1000))
            renpy.redraw(self, 0)
            return r

        # ------------------------------------------------------------ 输入
        KEYMAP = {pygame.K_w: "w", pygame.K_a: "a", pygame.K_s: "s", pygame.K_d: "d",
                  pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_LEFT: "left", pygame.K_RIGHT: "right"}

        def event(self, ev, x, y, st):
            if self.result and self.end_t is not None and self.t - self.end_t > 1.2:
                return self.result
            if ev.type == pygame.KEYDOWN:
                if ev.key in self.KEYMAP:
                    self.keys.add(self.KEYMAP[ev.key]); raise renpy.IgnoreEvent()
                if ev.key == pygame.K_SPACE:
                    self.attack(); raise renpy.IgnoreEvent()
            elif ev.type == pygame.KEYUP:
                if ev.key in self.KEYMAP:
                    self.keys.discard(self.KEYMAP[ev.key]); raise renpy.IgnoreEvent()
                if ev.key == pygame.K_SPACE:
                    raise renpy.IgnoreEvent()
            return None

        def visit(self):
            return [self.floor, self.heel, self.paper, self.swing_img, self.hf, self.he] + list(self.tok.values())


screen escape_minigame():
    modal True
    zorder 150
    default game = EscapeGame()
    add game
    ## 让游戏在没有按键时也能结束并返回（每 0.2 秒检查一次）
    timer 0.2 repeat True action If(game.result is not None and game.end_t is not None and game.t - game.end_t > 1.2,
                                     Return(game.result), NullAction())
    textbutton "跳过小游戏" action Return("skip") xalign 0.98 yalign 0.02 text_size 22


## 剧情里调用：返回 "win" / "skip"（失败会让玩家选择重来或跳过）
label escape_minigame_flow:
    if AUTOTEST:
        return "win"
    stop music fadeout 0.5
    play music bgm_scam
    window hide
    call screen mg_intro
    $ _mg_res = renpy.call_screen("escape_minigame")
    while _mg_res == "lose":
        window show
        menu:
            "我被按住了。"
            "再跑一次！":
                window hide
                $ _mg_res = renpy.call_screen("escape_minigame")
            "算了，跳过小游戏":
                $ _mg_res = "skip"
    window show
    return _mg_res

screen mg_intro():
    modal True
    zorder 150
    add Solid("#000000dd")
    vbox:
        xalign 0.5 yalign 0.45 spacing 24
        text "逃出套房！" size 80 color "#ffe066" xalign 0.5 outlines [(4, "#000", 0, 0)]
        text "WASD / 方向键 移动　　空格 推开敌人" size 36 color "#ffffff" xalign 0.5
        text "敌人打不死，只能推开。高跟鞋会扣血，「和解协议」会让你变慢。" size 28 color "#cccccc" xalign 0.5
        text "跑到右上角的「安全出口」就算赢。" size 28 color "#cccccc" xalign 0.5
        null height 20
        textbutton "开始（按回车）" action Return() xalign 0.5 text_size 36
    key "K_RETURN" action Return()
