## Chapter6.rpy —— 第五章「九分袖与校花」（李轩翔攻略篇 · 中）
##
## 流程：1708 订单（杨永麟的影子）→ 给「没有议程的饭」发明一个议程 → 周末逛商场（他穿外卖服）
##       → 富二代追求者秦受嘲讽 + 骚扰 → 系统紧急任务 + 纯爱卡打脸 → 骑手视角拆穿租来的车
##       → 业务能力反杀（岛团刷单的幽灵骑手账号就是秦家的）→ 地下美食广场的午饭（任务四完成）
##       → 柜姐是高中校花周沫，系统扫描 93 分 → 新女神解锁（候选，不切换攻略对象）
##
## 运行中的梗：报销审核（给自己买西装 → 驳回；给她买裙子 → 通过）、「九分袖」、封印、精灵每句换表情。

default zhou_name = "柜姐"
default ch6_1708 = None            # 1708 订单怎么处理：knock / leave / wait
default ch6_agenda = None          # 发明的议程：gown / audit / cat
default ch6_clash = None           # 秦受动手时：fight / system / watch
default ch6_dress_paid = False     # 是否用纯爱卡买下了那条裙子
default ch6_zhou_greet = None      # 对周沫：greet / pretend

label chapter6:
    stop music fadeout 1.0
    if not sys_active:
        call ch5_setup
        $ love("lxx", 30, quiet=True)
        $ add_task("lxx_4", "lxx", "和她吃一顿不是工作餐的饭", "没有议程。没有 PPT。没有二十分钟。", 30000)
    scene bg black
    call screen chapter_card("第五章", "九分袖与校花")
    jump ch6_1708


## ---------------------------------------------------------------------------
## 1708
## ---------------------------------------------------------------------------

label ch6_1708:
    play music bgm_tension fadein 1.0
    scene bg elevator
    with fade
    show pzk delivery normal at center_stage
    with dissolve

    n "半岛酒店，十七楼。"
    n "冰椰子水在我手里，冰得发烫。"
    pt "放在黑色高跟鞋旁边就行。"
    pt "这句话我这辈子听过两次。第一次，我失去了全部身家。"

    play sound sfx_elevator
    n "电梯门开了。1708 在走廊尽头。"
    n "门虚掩着。门口，摆着一双黑色细高跟。"
    n "鞋尖朝外，摆得整整齐齐。像在等人。"

    menu:
        "……"

        "敲门":
            $ ch6_1708 = "knock"
            play sound sfx_knock
            n "咚、咚、咚。"
            n "没有人回答。"
            n "门缝里只有一盏没关的台灯，和一张铺得平平整整、没人睡过的床。"

        "把椰子水放下，转身就走":
            $ ch6_1708 = "leave"
            n "我把椰子水放在高跟鞋旁边。"
            n "然后用送外卖以来最快的速度，走回了电梯。"
            $ stat("sincere", 2, quiet=True)

        "在门口等一会儿":
            $ ch6_1708 = "wait"
            n "我在走廊里站了五分钟。"
            n "保洁阿姨推着车经过，看了看我，又看了看那双鞋。"
            n "她说：「这间房，下午就退了。」"

    show pzk delivery gloom at center_stage
    n "订单显示「已送达」。顾客没有留下任何评价。"
    n "只在备注栏里，多了一个字母。"
    tip "Y"
    pt "……她回来了。"
    pt "或者说，她从来没离开过。"
    hide pzk with dissolve

    xt idle "检测到宿主心率异常。"
    xt side_eye "提醒：宿主当前攻略对象是李轩翔。"
    xt eyeroll "前女友（如果算的话）不在本系统的服务范围内。"
    p "……谁说她是前女友。"
    xt mock_laugh "那你心率异常什么。"

    jump ch6_agenda


## ---------------------------------------------------------------------------
## 发明一个议程
## ---------------------------------------------------------------------------

label ch6_agenda:
    play music bgm_rider fadein 1.0
    scene bg rental_room
    with fade
    show pzk home normal at left_stage
    with dissolve

    n "任务四：和她吃一顿不是工作餐的饭。"
    n "问题是，李轩翔不吃没有议程的饭。"
    pt "那就给她一个议程。"
    pt "一个她无法拒绝的议程。"

    menu:
        "微信上，发什么？"

        "「议程：给沈眠的晚宴挑战袍。附带午饭一顿。」":
            $ ch6_agenda = "gown"
            p "「李总，下周的晚宴您是主角之一。议程：挑一件战袍。时长两小时，附带午饭一顿。」"
            n "三分钟后。"
            lx "「议程通过。周六十二点，环贸 B1。不许迟到。」"
            $ love("lxx", 3)

        "「议程：复盘岛团项目。附带午饭一顿。」":
            $ ch6_agenda = "audit"
            p "「李总，岛团项目需要一次非正式复盘。附带午饭一顿。」"
            lx "「复盘在会议室做。」"
            n "我以为没戏了。十分钟后，又来一条。"
            lx "「……下周晚宴我缺一件衣服。周六十二点，环贸 B1。复盘顺便。」"

        "「议程：探讨止损的猫粮选购问题。」":
            $ ch6_agenda = "cat"
            p "「李总，关于止损的猫粮，我有一些行业洞察。」"
            n "已读。"
            n "二十分钟后。"
            lx "「它只吃一个牌子。你没有洞察。」"
            lx "「但我下周晚宴缺件衣服。周六十二点，环贸 B1。」"
            show pzk home smug at left_stage
            pt "猫救了我。"
            $ love("lxx", 2)

    xt evil_grin "议程是假的。饭是真的。系统认可。"
    jump ch6_mall


## ---------------------------------------------------------------------------
## 商场
## ---------------------------------------------------------------------------

label ch6_mall:
    play music bgm_city_date fadein 1.0
    scene bg mall_atrium
    with fade

    n "周六，十二点零三分。"
    n "我迟到了三分钟。"
    n "因为午高峰最后一单，送到了环贸隔壁的写字楼。"
    show pzk delivery awkward at left_stage
    with dissolve
    n "所以我是穿着外卖服来的。"
    n "头盔夹在胳膊底下，后背的保温箱还没来得及放下。"

    show lxx weekend cold at right_stage
    with dissolve
    n "她已经到了。"
    n "米色针织开衫，白 T 恤，牛仔裤，小白鞋。"
    n "不是西装，也不是皮衣。"
    pt "原来她还有第三套。"
    pt "原来她周末，是这个样子的。"

    lx "三分钟。"
    p "最后一单，超时扣钱。"
    show lxx weekend smirk at right_stage
    lx "那你选择了扣我的时间。"
    p "我选择了五星好评。"
    lx "……走吧。保温箱放前台，别背着它试衣服。"

    jump ch6_boutique


label ch6_boutique:
    scene bg boutique
    with dissolve
    play music bgm_lxx_soft fadein 1.0
    show zhou pro_smile at center_stage
    with dissolve

    zhou "欢迎光临。两位有什么需要——"
    n "柜姐的笑容在看到我的外卖服时卡了零点五秒。"
    n "然后完美地恢复了。专业。"
    hide zhou with dissolve
    show pzk delivery normal at left_stage
    show lxx weekend cold at right_stage
    with dissolve

    n "李轩翔挑衣服的方式，和她看财报一模一样。"
    n "扫一眼，排除。扫一眼，排除。"
    n "直到她在一条深蓝色的长裙前面，停了三秒。"
    show lxx weekend smile at right_stage
    pt "三秒。"
    pt "对李轩翔来说，三秒就是一见钟情。"
    n "她翻了一下吊牌，又放下了。"
    show lxx weekend cold at right_stage
    lx "下一件。"
    pt "……她看了价格。"

    jump ch6_qin


## ---------------------------------------------------------------------------
## 秦受
## ---------------------------------------------------------------------------

label ch6_qin:
    stop music fadeout 0.5
    play sound sfx_door
    play music bgm_lxx fadein 0.5
    show qin smug at far_right
    with dissolve

    qin "轩翔？这么巧。"
    n "一个穿宝蓝色西装的男人走进来，手指上转着一把车钥匙。"
    n "金表，尖头皮鞋，衬衫扣子解开两颗。"
    n "他身上的每一样东西都在大声说：我很贵。"
    pt "……这不就是三个月前的我吗。"

    show lxx weekend cold at right_stage
    lx "秦受。"
    qin "给晚宴挑衣服？我就说嘛，沈眠的局，你肯定要来。"
    show qin sneer at far_right
    qin "这位是……？"
    n "他上下打量我。外卖服。头盔。九分长的耐心。"
    qin "哦——岛团的骑手？"
    qin "轩翔，你现在出门逛街，还带个外卖员拎包？"
    qin "兄弟，这家店最便宜的一条丝巾，够你送一年外卖吧？"

    show pzk delivery gloom at left_stage
    pt "一年零两个月。"
    pt "我心算过了。"

    show qin smug at far_right
    qin "轩翔，那条蓝裙子你刚才看了吧？我买给你。"
    qin "晚宴那天，你穿它，跟我一起进场。"
    show lxx weekend angry at right_stage
    lx "不用。"
    qin "别这么见外嘛。"
    show qin angry at far_right
    qin "说起来——你叫停岛团，我们家基金亏了两个亿。"
    qin "陪我吃顿饭，这事就算了。不过分吧？"
    n "他伸手，抓住了她的手腕。"
    play sound sfx_shock
    with vpunch

    menu:
        "……"

        "冲上去，一把推开他":
            $ ch6_clash = "fight"
            show pzk delivery angry at left_stage
            n "我往前跨了一步。"
            n "她却先一步，把手抽了回来，同时抬手拦住了我。"
            show lxx weekend cold at right_stage
            lx "别动手。"
            lx "他巴不得你动手。商场有监控，动手的人就输了。"
            pt "……她连这个都算到了。"
            $ love("lxx", 1)
            $ stat("zb", 3)

        "冷静。先让系统想办法":
            $ ch6_clash = "system"
            show pzk delivery normal at left_stage
            n "我的拳头攥紧了。然后，我松开了。"
            pt "四年前的李轩翔教过我：情绪是成本。"
            $ love("lxx", 3)
            $ stat("sincere", 3)

        "先看她怎么处理":
            $ ch6_clash = "watch"
            show lxx weekend cold at right_stage
            n "她看着秦受的手。很平静。"
            lx "你再不松手，我就按你们家基金的季报，一页一页念给店里所有人听。"
            show qin pale at far_right
            n "秦受的手松开了。但他脸上的笑还挂着。"
            pt "……她不需要我救。"
            pt "但她需要有人站在她这边。"
            $ love("lxx", 4)

    jump ch6_slap


## ---------------------------------------------------------------------------
## 打脸
## ---------------------------------------------------------------------------

label ch6_slap:
    play sound sfx_glitch
    call sys_boot
    xt jaw_drop "叮——！"
    xt rage_scream "检测到攻略对象遭受骚扰！！"
    xt evil_grin "触发紧急任务：「守护攻略对象的尊严」。"
    $ add_task("lxx_e1", "lxx", "守护攻略对象的尊严", "在她被骚扰时站在她这边。不许动手。", 10000)
    xt mock_laugh "临时额度：二十万。仅限一次，仅限为攻略对象消费。"
    $ credit_limit += 200000
    p "二十万？？"
    pt "那我先买一套像样的西装，气场上先压他一头——"

    call sys_audit("男士定制西装（意大利面料）", 38800, "宿主气场维护费", "rejected", "驳回。宿主的气场不是攻略对象。另：上次批的那套租赁西装，袖子还没还。")
    show pzk delivery awkward at left_stage
    pt "……这个系统真的一次都不让我装。"
    xt side_eye "你要装，也得装在她身上。"

    pt "装在她身上……"
    show lxx weekend cold at right_stage
    n "我看向那条深蓝色的长裙。"
    n "她看了三秒，然后放下的那条。"

    show pzk delivery proud at left_stage
    p "这条裙子，我们要了。"
    show qin sneer at far_right
    qin "哈？"
    qin "兄弟，你看清楚吊牌了吗？十二万八。"
    qin "你这身外卖服，扫码都扫不出这个数。"

    call sys_audit("深蓝色真丝长裙", 128000, "攻略对象晚宴战袍", "approved", "通过。她看了三秒。系统看见了。")
    $ ch6_dress_paid = True
    play sound sfx_cash
    n "我走到收银台，掏出手机。"
    n "屏幕上是一张只有我能看见的卡。淡蓝色，卡面上一颗心。"
    n "嘀。"
    clerk "……支付成功。"
    n "店长的声音有点抖。"

    show qin shock at far_right
    play sound sfx_shock
    qin "你、你刷的什么卡？"
    show pzk delivery smug at left_stage
    p "纯爱卡。"
    p "你没有。"
    xt cry_laugh "宿主这辈子说过最帅的一句话。系统已存档。"

    show qin angry at far_right
    qin "装什么？一个送外卖的，不知道哪借的钱——"
    qin "我车就在门口，帕拉梅拉。你骑电动车来的吧？"
    show pzk delivery normal at left_stage
    p "门口那辆白色帕拉梅拉？车牌框上印着「速租」那辆？"
    show qin pale at far_right
    qin "……"
    p "速租汽车，东区三号店。上礼拜我给他们送了十二份猪脚饭。"
    p "他们店长说，最近有个老客户，每个周末都租那辆白色帕拉梅拉。"
    p "一天两千八。押金还是刷的花呗。"
    n "店里安静了。"
    n "旁边一位挑包的阿姨，默默把手机摄像头对准了秦受。"
    $ stat("zb", 5)

    show qin angry at far_right
    qin "你——！"
    qin "你知不知道我们家基金因为岛团亏了多少？两个亿！"
    show pzk delivery normal at left_stage
    p "知道。我还知道你们为什么会亏。"
    p "我们站点的骑手名单上有八十七个账号，每天来报到的只有三十一个人。"
    p "剩下那五十六个幽灵账号，注册在一家叫「秦氏信息科技」的公司名下。"
    p "法人代表，姓秦。"
    show qin shock at far_right
    play sound sfx_sting
    n "秦受的脸，从红色变成了白色。"
    show lxx weekend surprised at right_stage
    n "李轩翔转头看我。她的眼睛里，第一次出现了她在会议室里从不允许出现的东西。"
    n "意外。"
    p "亏两个亿的不是你们家。"
    p "是被你们刷出来的数据骗了的散户。"
    p "她叫停那个项目，是在救你们。不然下个月来找你的，就不是我，是证监会。"

    mall_guard "先生，这边有人反映您骚扰顾客，请您配合一下。"
    show qin pale at far_right
    qin "……你给我等着。"
    hide qin with moveoutright
    n "他走了。车钥匙忘在了柜台上。"
    n "店长拿起来看了看，上面挂着一个小牌子：「速租 · 东区三号店」。"

    $ complete_task("lxx_e1")
    ## 临时额度只用一次：收回额度，裙子的钱由临时额度承担
    $ credit_limit -= 200000
    $ credit_used = max(0, credit_used - 128000)
    $ love("lxx", 10 if ch6_clash != "fight" else 6)
    $ set_stage("lxx", "站在一起")
    $ add_note("lxx", "她在深蓝色长裙前停了三秒。")

    jump ch6_after


label ch6_after:
    play music bgm_lxx_soft fadein 1.5
    show lxx weekend cold at right_stage
    show pzk delivery normal at left_stage

    lx "裙子，我不收。"
    p "我知道。"
    lx "……你知道？"
    p "您不收别人买的东西。您只收自己挣的。"
    show lxx weekend blush at right_stage
    n "她沉默了一会儿。"
    lx "十二期。每月一万零六百六十七。没有利息。"
    p "有点利息也行——"
    show lxx weekend smirk at right_stage
    lx "你要是敢收利息，我就举报你放高利贷。"
    pt "……系统，这钱还回来，算谁的？"
    xt soul_leave "系统没有处理过攻略对象还钱的流程。正在升级。"

    show lxx weekend smile at right_stage
    lx "潘子恺。"
    p "嗯？"
    lx "刚才那八十七个账号的事，你为什么当众说？"
    lx "你可以私下告诉我。那样更安全。"
    p "因为他当众说您亏了他两个亿。"
    p "所以真相也得当众说。"
    play sound sfx_heart
    n "她看着我，没说话。"
    n "然后伸手，把我外卖服的领子翻正了。"
    lx "领子歪了。"

    show pzk delivery sealed at left_stage
    call seal_alarm("纯爱封印运行正常。另：宿主刚才心率 142。")
    pt "……我真的什么都没想。"
    pt "我只是，有点想哭。"
    show pzk delivery shy at left_stage
    $ love("lxx", 3)

    jump ch6_lunch


## ---------------------------------------------------------------------------
## 地下美食广场
## ---------------------------------------------------------------------------

label ch6_lunch:
    play music bgm_city_date fadein 1.0
    scene bg food_court
    with fade
    show pzk delivery normal at left_stage
    show lxx weekend cold at right_stage
    with dissolve

    n "议程上写着「附带午饭一顿」。"
    n "她选的地方，是商场最底下的美食广场。"
    lx "楼上的餐厅要排队。这里的牛肉面，十八块，比楼上的好吃。"
    pt "十八块。"
    pt "我们刚刚在楼上花了十二万八。"

    menu:
        "点什么？"

        "两碗牛肉面，加蛋":
            p "两碗牛肉面。都加蛋。"
            show lxx weekend smile at right_stage
            lx "你知道我要加蛋？"
            p "您连煎饼都要加三个蛋。"
            $ love("lxx", 3)

        "「今天我请，我们吃点贵的」":
            show pzk delivery proud at left_stage
            p "今天我请。我们吃点贵的。"
            lx "这里最贵的是麻辣香锅，四十二。"
            p "……那就麻辣香锅。"
            show lxx weekend smirk at right_stage
            lx "嗯。挺贵的。"

    call sys_audit("牛肉面 ×2（加蛋）", 40, "攻略对象午饭", "approved", "通过。这是本系统审核过最便宜、也最像约会的一笔。")

    n "我们坐在塑料椅子上吃面。"
    n "她把香菜挑出来，放在一张纸巾上，摆成一个小堆。"
    show lxx weekend laugh at right_stage
    n "我讲了一个外卖站点的笑话。她笑出了声。"
    n "邻桌的大爷回头看了一眼，以为我们是一对。"
    n "我没解释。她也没有。"

    show lxx weekend tongue at right_stage
    play sound sfx_boing
    lx "你脸上有辣油。"
    n "她冲我吐了一下舌头，然后递过来一张纸巾。"
    pt "……第二次了。"
    pt "我决定开始记数。"

    $ complete_task("lxx_4")
    $ set_stage("lxx", "没有议程的饭")
    $ add_note("lxx", "她吃牛肉面加蛋，不吃香菜。笑的时候会先低头。")
    xt jaw_drop "任务完成：「和她吃一顿不是工作餐的饭」。"
    xt evil_grin "议程是假的。饭是真的。笑也是真的。"

    jump ch6_zhou


## ---------------------------------------------------------------------------
## 校花
## ---------------------------------------------------------------------------

label ch6_zhou:
    play music bgm_comedy fadein 1.0
    scene bg boutique
    with fade
    n "吃完饭，我们回店里取裙子。"
    n "李轩翔去试衣间改尺寸。我在门口等。"
    show zhou pro_smile at right_stage
    show pzk delivery normal at left_stage
    with dissolve

    zhou "先生，您的小票。"
    n "刚才那个笑容卡了零点五秒的柜姐，把小票递给我。"
    n "我第一次认真看了她的脸。"
    n "然后看到了她胸口的名牌。"
    tip "周沫"
    play sound sfx_shock
    show pzk delivery shock at left_stage, shake
    p "……周沫？？"
    show zhou surprised at right_stage
    zhou "……你认识我？"
    p "三中！高三（七）班！你是那年的校花！"
    p "你的照片被贴在学校光荣榜上，然后被偷走了十一次！"
    $ zhou_name = "周沫"
    zhou "第十二次是我自己撕的。"
    show zhou grin at right_stage
    zhou "等等……你是潘子恺？？那个在毕业典礼上对着镜子说「我是三中最帅的男人」的潘子恺？"
    show pzk delivery awkward at left_stage
    p "……是我。"
    zhou "你不是发财了吗？我们班群里都说你财富自由，在海岛上开兰博基尼。"

    menu:
        "怎么回答？"

        "「说来话长。我现在送外卖。」":
            $ ch6_zhou_greet = "greet"
            show pzk delivery normal at left_stage
            p "说来话长。我现在送外卖。"
            show zhou surprised at right_stage
            zhou "……真的假的？"
            show zhou grin at right_stage
            zhou "那你比我惨。我好歹在这儿还有底薪。"
            $ stat("sincere", 3, quiet=True)

        "「体验生活。」":
            $ ch6_zhou_greet = "pretend"
            show pzk delivery proud at left_stage
            p "体验生活。"
            show zhou tease at right_stage
            zhou "体验生活，然后用一张我没见过的卡，买了十二万八的裙子？"
            zhou "潘子恺，你高中撒谎的时候就是这个表情。"
            $ stat("zb", 3)

    show zhou pro_smile at right_stage
    zhou "我在这儿干了两年了。攒钱。"
    zhou "我想开一家自己的工作室，设计衣服。"
    zhou "……当然，现在离那天还早得很。"
    n "她说这话的时候，笑得很亮。"
    n "跟高中光荣榜上那张照片一模一样。"

    play sound sfx_sys_ding
    show screen scan_overlay
    pause 1.0
    hide screen scan_overlay
    xt jaw_drop "叮——！"
    xt evil_grin "检测到新的符合条件的对象。"
    $ unlock_candidate("zhou", "周沫", 26, "精品店柜姐 · 宿主高中同学（三中校花）", 93,
                       "开朗，嘴快，比谁都务实。在攒钱开自己的服装设计工作室。认识十七岁时的宿主——包括他最丢人的样子。")
    call screen target_card("zhou")
    xt side_eye "已存入「女神候选」。"
    xt eyeroll "宿主当前攻略对象仍为：李轩翔。本系统一次只开一条攻略线。"
    xt mock_laugh "别想了。你的封印，只有一个。"
    show pzk delivery shock at left_stage
    pt "……这个系统什么时候学会读心了。"

    show zhou tease at right_stage
    zhou "发什么呆？加个微信，班群里那帮人要是知道你在送外卖——"
    p "别告诉他们！"
    show zhou grin at right_stage
    zhou "那就看你表现咯，潘、师、傅。"

    hide zhou with dissolve
    show lxx weekend cold at right_stage
    with dissolve
    n "试衣间的门开了。"
    lx "走了。"
    n "她看了一眼周沫，又看了一眼我。"
    show lxx weekend smirk at right_stage
    lx "高中同学？"
    p "……您怎么知道？"
    lx "你脸红的方式，跟四年前第一次交 PPT 的时候一样。"
    pt "……风控部门的记忆是永久的。"

    stop music fadeout 2.0
    scene bg mall_atrium
    with fade
    show pzk delivery normal at center_stage
    with dissolve
    n "那天晚上回家的路上，我在商场门口，看到了那辆白色帕拉梅拉。"
    n "车里没人。"
    n "挡风玻璃上，贴着一张罚单。"
    n "和一张便利贴。"
    tip "「你等着。——秦」"
    pt "……行吧。"
    pt "我等着。"

    scene bg black
    with fade
    tip "—— 第五章 完 ——"
    call screen chapter_card("未完待续", "沈眠的晚宴 ／ 秦受的报复 ／ 女神候选：周沫")
    return
