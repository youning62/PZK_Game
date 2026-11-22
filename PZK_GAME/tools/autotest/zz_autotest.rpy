## 自动随机通关测试（只在测试时被复制进 game/，不要随游戏发布）
## 用法：python3 tools/autotest/run.py <次数>
## 原理：快进跳过对话；替换菜单函数 store.menu，按种子随机选择；
##       限时选择有一定概率直接跳到超时分支；只靠计时器关闭的 call screen 卡片直接跳过。
## （后台窗口里 Ren'Py 的计时器不触发，所以不依赖任何计时器。）

init offset = 999

init python:
    import os, io, random as _random
    AUTOTEST = True
    _at_seed = int(os.environ.get("PZK_AUTOTEST", "1"))
    _at_rng = _random.Random(_at_seed)
    _at_log = io.open(os.path.join(config.basedir, "autotest_logs", "run_%d.log" % _at_seed), "w", encoding="utf-8")

    def _at_write(s):
        _at_log.write(s + u"\n")
        _at_log.flush()

    def _at_label(name, abnormal):
        if not name.startswith("_"):
            _at_write(u"LABEL " + name)
    config.label_callbacks.append(_at_label)

    def _at_exc(short, full, traceback_fn):
        _at_write(u"EXCEPTION\n" + full)
        _at_log.close()
        os._exit(3)
    config.exception_handler = _at_exc

    def _at_menu(items, **kwargs):
        opts = [(c, v) for (c, v) in items if v is not None and getattr(v, "value", v) is not None]
        if renpy.get_screen("timed_choice_bar") and _at_rng.random() < 0.3:
            _at_write(u"CHOICE <timeout>")
            renpy.jump("ch2_order_timeout")
        c, v = _at_rng.choice(opts)
        _at_write(u"CHOICE " + c)
        return v.value if hasattr(v, "value") else v
    menu = _at_menu

    _at_real_call_screen = renpy.exports.call_screen
    def _at_call_screen(name, *args, **kwargs):
        _at_write(u"SCREEN " + name + u" " + repr(args))
        if name in ("chapter_card", "chapter_result", "person_card", "sys_audit_screen", "fund_card", "fund_recharge_screen"):
            # 先实际渲染一次，确保屏幕本身不报错
            renpy.show_screen(name, *args, **kwargs)
            renpy.hide_screen(name)
            return None
        return _at_real_call_screen(name, *args, **kwargs)
    renpy.exports.call_screen = _at_call_screen
    renpy.call_screen = _at_call_screen

    config.main_menu_music = None
    _preferences.skip_unseen = True
    _preferences.skip_after_choices = True
    _preferences.transitions = 0

label main_menu:
    $ config.skipping = "fast"
    $ _at_start = os.environ.get("PZK_START", "start")
    call expression _at_start
    python:
        _at_write(u"END ending=%s aff=%s zb=%s sincere=%s stage=%s people=%s money=%s fund=%s" % (ch1_ending, yyl_aff, zb, sincere, sys_stage, {k: (v["unlocked"], v["aff"]) for k, v in people_state.items()}, money, fund))
        _at_log.close()
        os._exit(0)

## 小游戏逻辑自测：脚本化输入跑模拟（不需要窗口），PZK_START=mg_selftest
label mg_selftest:
    python:
        _g = EscapeGame()
        _wp = [(820, 380), (1340, 400), (1420, 300), (1535, 105)]
        _t = 0.0; _wi = 0
        while _t < 120 and not _g.result:
            tx, ty = _wp[_wi]
            if abs(_g.px - tx) < 25 and abs(_g.py - ty) < 25 and _wi < len(_wp) - 1:
                _wi += 1
            _g.keys = set()
            if tx > _g.px + 5: _g.keys.add("d")
            if tx < _g.px - 5: _g.keys.add("a")
            if ty > _g.py + 5: _g.keys.add("s")
            if ty < _g.py - 5: _g.keys.add("w")
            _every = float(os.environ.get("MG_ATK", "0.4"))
            if int(_t / 0.02) % max(1, int(_every / 0.02)) == 0: _g.attack()
            _g.update(0.02); _t += 0.02
        _at_write(u"MG result=%s hp=%s t=%.1f pos=(%d,%d)" % (_g.result, _g.hp, _t, _g.px, _g.py))
    return

## 系统规则自测：PZK_START=sys_selftest
label sys_selftest:
    python:
        people_state = {}; owned_rewards = []; focus_target = None; sys_pending_announce = []
        sys_stage = "primary"; money = 200; fund = 0
        _fails = []
        def _ok(c, m):
            if not c: _fails.append(m)
        _ok(give_gift("dhy", "花", 9) == "not_scanned", "未扫描不解锁")
        scan("dhy"); scan("spa_new"); scan("pzk")
        _ok(give_gift("spa_new", "花", 9) == "ineligible", "81 分不符合")
        _ok(give_gift("dhy", "红包", 10, accepted=False) == "refused", "拒收")
        _ok(give_gift("dhy", "转账", 10, completed=False) == "incomplete", "未完成")
        _ok(not unlocked("dhy"), "拒收/未完成不解锁")
        _ok(give_gift("dhy", "红包", 10) == "unlocked" and sealed("dhy") and ps("dhy")["aff"] == 0, "成功赠与解锁+封印，好感不变")
        sys_stage = "active"
        _ok(fund_check(1, "dhy")[0] == "rejected", "基金余额不足")
        _ok(fund_recharge(100) == 1000000 and fund == 1000000 and money == 100, "1 元 = 10000")
        _ok(fund_check(10, "pzk")[0] == "rejected", "自购驳回")
        _ok(fund_check(10, None)[0] == "rejected", "无关消费驳回")
        _ok(fund_check(10, "spa_new")[0] == "rejected", "不到 90 驳回")
        _ok(fund_check(10, "dhy", cashout=True)[0] == "rejected", "套现驳回")
        _ok(fund_check(10, "lxx")[0] == "approved", "未解锁的 90 分以上女性也可以花")
        scan("lxx"); give_gift("lxx", "咖啡", 38)
        _ok(set(pursuing()) == {"dhy", "lxx"}, "多目标")
        love("dhy", 90, quiet=True)
        _ok(ps("dhy")["success"] and not sealed("dhy") and owned_rewards == ["super_body"] and sealed("lxx"), "成功：只解她的封印、只发她的奖励")
        _at_write(u"SELFTEST " + (u"PASS" if not _fails else u"FAIL " + u" | ".join(_fails)))
        _at_log.close()
        os._exit(0)
    return
