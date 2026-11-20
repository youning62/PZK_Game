# 故事板：第一章 · 第二话「第一次晚餐」

（按 renpy-storyboard skill 的格式整理，作为 `game/Chapter2.rpy` 的实现依据）

## 总览
- **基调**：约会前手忙脚乱的喜剧 → 日落晚餐的斗嘴 → 夜色里一点真心；以"她到底是谁"的轻悬疑收尾。
- **角色**：潘子恺（男主，自恋装逼但不坏）、杨永麟（女主，高冷洒脱、做风控、看穿一切）、服务生 / 经理 / 邻桌大叔（配角，无立绘）
- **场景**：bg villa_bedroom、bg villa_closet、bg garage、bg coast_road、bg restaurant_sunset、bg restaurant_night、bg villa_bedroom_night、cg first_dinner、cg lambo_beach
- **核心演出点**：① 西装扣子崩飞 ② 约会中外卖订单响起（限时选择）③ 夜色栏杆边的海玻璃

## 镜头 1：搜索引擎（下午）
- **场景**：bg villa_bedroom　**BGM**：bgm_comedy
- **角色**：无立绘（第一人称）；手机通知 screen phone_notice
- **交互**：menu 三选一 → `search_tip` = money / mystery / sincere（第三条"点赞 3"是吐槽点）

## 镜头 2：衣帽间
- **场景**：bg villa_closet　**SFX**：sfx_mirror、sfx_boing（崩扣子）
- **角色**：pzk casual *（mirror_view）
- **视觉**：主要 shake + 白闪（扣子射向镜子）
- **交互**：menu → `outfit` = suit(→suit_burst，回落为 casual) / casual / hawaii（晚餐撞衫伏笔）

## 镜头 3：对镜练习 & 研究菜单
- **交互**：menu → `practiced_line` = cheesy / dream / honest；menu → `studied_menu`
- **备注**：练过的台词会在镜头 7 被"验收"

## 镜头 4：交通工具
- **场景**：bg garage → bg coast_road（wipeleft）　**SFX**：sfx_engine / sfx_drive
- **交互**：menu → `ride` = lambo / ebike（显示 ebike 道具图）/ walk

## 镜头 5：抵达「潮汐」
- **场景**：bg restaurant_sunset　**BGM**：bgm_dinner　**环境**：sfx_waves 低音量
- **角色**：pzk 左侧 seated；yyl 右侧先 slide_in_right 再 seated
- **SFX**：sfx_heels（她登场前先听到鞋跟声——"先闻其声"）
- **条件分支**：ride / outfit 各自一段反应（撞衫、扣子、小黄电动车）

## 镜头 6：点菜（条件选项）
- **交互**：menu，其中「用法语点菜」仅在 `studied_menu` 为真时出现
- **伏笔**：经理叫她"杨小姐，老样子？"——她是常客

## 镜头 7：聊工作（她做风控）
- **交互**：menu → 吹嘘 / 坦白 / 反问她
- **伏笔**：她随口问"你这种人，钱一般放在哪？"并解释为职业病（不揭示立场）
- **随后**：练过的台词验收（cheesy → bgm_awkward + 蟋蟀声）

## 镜头 8：外卖订单响了（限时选择）
- **视觉**：主要 vpunch + phone_notice；次要 画面暗角
- **交互**：限时 menu（6 秒，屏幕上显示倒计时条）；超时 = 犹豫太久，她替你决定"去吧，骑手。"
- **结果**：送完邻桌大叔的奶茶 → 她说出关键台词"你送外卖的时候，比你装逼的时候好看。"

## 镜头 9：夜色栏杆
- **场景**：bg restaurant_sunset → bg restaurant_night（慢 Dissolve 2.0 = 日落到夜）
- **BGM**：bgm_tender　**视觉**：星光粒子（SnowBlossom 缓慢上浮的光点），不叠加其他效果
- **交互**：menu → 玩笑 / 真话（told_truth）
- **条件**：真诚足够 → 她送出蓝色海玻璃（got_sea_glass）
- **伏笔**：手机亮起联系人「K」，她扣下屏幕；可选择追问

## 镜头 10：买单 & 结局判定
- **判定**：A（好感≥45 且 真诚≥30）「明早六点，海滩见」/ B（好感≥25）「下次你请」/ C「她买的单」
- **演出**：A 线配 cg first_dinner + sfx_heart；结算界面 screen chapter_result

## 镜头 11：夜晚别墅 · 第二个梦
- **场景**：bg villa_bedroom_night → 黑屏
- **视觉**：blur 梦境；声音"……别信——"被切断（不说明别信谁）
- **结尾**：下一章预告卡「第二话预告：冲浪课」

## 实施备注
- 所有资源已登记在 `game/assets.rpy`；立绘表情差分 = 同一张原图 + 漫画符号叠加（项目里每个角色只有一张原始脸）。
- 限时选择用自定义 screen `timed_choice_bar` + `renpy.timeout` 实现，无需 shader。
- 星光粒子使用内置 `SnowBlossom`，无额外依赖。
