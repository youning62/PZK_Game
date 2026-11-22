# 纯爱致富系统 · 设定与实现

> 代码：`game/system_data.rpy`（人物与奖励数据表）、`game/system.rpy`（状态、规则函数、演出 label、界面）、`game/phone.rpy`（微信聊天 / 红包 / 朋友圈）、`game/hud.rpy`（`sys_hud`）。
> 剧情：`game/Chapter4.rpy`（第三章「十块钱的纯爱」）。

## 系统的三个阶段

| `sys_stage` | 何时 | 能做什么 |
|---|---|---|
| `none` | 系统出现之前 | 无。右上角不显示任何数值 |
| `primary` 初级扫描 | 第三章足疗店门口首次出现 | 扫描任何人，只看姓名、年龄、颜值评分；其余字段显示「系统未激活」 |
| `active` 正式激活 | 向一名 ≥ 90 分的成年女性完成第一次被接受的赠与（第三章：给丁虹依的 10 元红包） | 全部功能；`sys_active = True`，HUD 出现 |

只要系统出现，精灵就出现：系统台词一律 `xt <表情> "……"`，每句换一个表情。

## 核心规则（游戏内「系统 → 规则」页同样列出）

| # | 规则 | 实现 |
|---|---|---|
| 1 | **扫描自由**：任何人都能扫（男女老少、照片也行）。陌生人只显示姓名、年龄、颜值评分 | `call sys_scan(pid)` / `call sys_scan(pid, photo=True)` |
| 2 | 只有**成年女性且评分 ≥ 90** 符合攻略条件 | `eligible(pid)` |
| 3 | 向符合条件的女性**成功赠与**（红包 / 转账 / 礼物 / 请客 / 其他）→ 解锁人物特点、当前好感度、专属奖励、攻略状态，攻略正式开始。拒收、未完成、未扫描、不符合条件 → 不解锁 | `call sys_gift(pid, 物品, 金额, 类型, accepted=, completed=)` |
| 4 | **赠礼不等于好感**，好感只随对方真实反应变化 | `call sys_love(pid, ±N)` |
| 5 | 每人**好感独立**；≥ 90% 攻略成功 → 解除对她的封印 + 发放她的专属奖励（只发一次，精灵播报） | 自动；`owned_rewards` |
| 6 | **纯爱封印**：对每一位已解锁档案的对象单独生效，成功后解除。成人喜剧机制，不写露骨内容 | `sealed(pid)`、`call seal_alarm("台词")` |
| 7 | **多目标**从一开始就支持；系统不指定、不推荐攻略谁；不提供精神控制 | `pursuing()` |
| 8 | **舔狗基金**：激活后用真钱充值，**1 元 = 10,000 元基金**，不可退、不设上限 | `call sys_recharge(元)` |
| 9 | 基金只能花在**任意 ≥ 90 分的成年女性**身上（不要求已解锁）；她收到的是**真钱**。自购、套现、无关消费、余额不足一律驳回 | `call sys_spend(项目, 金额, 收款人pid, 类别, cashout=False, gift=False)` |
| 10 | 基金余额不是宿主的个人财富；首次激活的那笔赠与不算充值；专属奖励和基金是两套独立机制；暂无「好感返现」 | — |

## 数据

**人物（常量）**——`system_data.rpy`：
```python
reward("super_body", "超强体魄")
person("dhy", "丁虹依", 25, score=93, reward="super_body", traits="……")
```
已有：丁虹依 93「超强体魄」、李轩翔 96「生化人保镖」；第三章被扫描的：潘子恺 −250、刘翠芬 81、王桂兰 64、三位前女友 89/89/88、赵磊 62。

**存档变量**：`sys_stage`、`sys_active`、`money`（真钱）、`fund`（基金）、`fund_recharged_rmb`、`fund_spent`、`fund_log`、`rejected_count`、`people_state[pid] = {scanned, unlocked, aff, sealed, success, gifts[]}`、`focus_target`（HUD 显示谁，玩家在系统面板里选）、`owned_rewards`。

## 剧本用法

```renpy
call sys_scan("dhy", photo=True)                 # 扫描
call sys_gift("dhy", "一束花", 199, "礼物")        # 真钱赠与，解锁档案
call sys_spend("一束花", 1990000, "dhy", "礼物", gift=True)   # 用基金送（审核通过同时记赠与）
call sys_recharge(100)                           # 充值 → ¥1,000,000 基金
call sys_love("dhy", 5)                          # 好感（达到 90% 自动播报）
$ chat_open("丁虹依"); $ chat("her", "？"); $ chat("me", "10", "rp"); $ chat_close()
show screen phone_moments("作者", "正文", "点赞", [("评论人", "评论")])
```

## 新增一个攻略对象

1. `system_data.rpy` 加一行 `person(...)`（新奖励先 `reward(...)`）。
2. `assets.rpy` 登记立绘，`characters.rpy` 定义 `Character`。
3. 剧情里扫描、赠与、加减好感。系统代码、HUD、面板都不用改。

## 测试

- 规则自测：`PZK_START=sys_selftest python3 tools/autotest/run.py 1`，日志里应有 `SELFTEST PASS`。
- 第三章随机通关：`PZK_START=chapter4 python3 tools/autotest/run.py 4`。

## 系统的性格

毒舌、一本正经、比宿主先一步看穿他。不剧透任何人的过去，不控制任何人的感情（「那叫犯罪。而且不浪漫。」），不替宿主决定追谁。偶尔流露一点温度（第三章他拒绝用一百万挽回面子时：「本系统记下了。」），这条线要慢慢加深。
