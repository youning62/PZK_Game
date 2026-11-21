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
        if name in ("chapter_card", "chapter_result", "target_card", "sys_audit_screen"):
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
        _at_write(u"END ending=%s aff=%s zb=%s shesi=%s sincere=%s lxx=%s money=%s" % (ch1_ending, yyl_aff, zb, shesi, sincere, targets.get("lxx", {}).get("aff"), money))
        _at_log.close()
        os._exit(0)
