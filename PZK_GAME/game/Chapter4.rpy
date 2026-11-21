## Chapter4.rpy —— 第三章「骑手潘师傅」
##
## 流程：回城 → 城中村出租屋 → 成为真正的外卖员（三单 + 一场雨）→ 疲惫入睡
##       → 第二天早上「纯爱致富系统」觉醒 → 逐条认识规则 → 发现第一个攻略对象是前上司李轩翔

label chapter4:
    stop music fadeout 1.0
    $ money = 1872
    $ delivery_income = 0
    scene bg black
    call screen chapter_card("第三章", "骑手潘师傅")
    jump ch4_return


## ---------------------------------------------------------------------------
## 回城 & 出租屋
## ---------------------------------------------------------------------------

label ch4_return:
    play music bgm_broke fadein 1.0
    play ambient sfx_city fadein 1.0 volume 0.4
    scene bg city_street_day
    with fade

    n "一周后。城里。"
    n "我拖着一个行李箱，推着小黄，站在城中村的巷子口。"
    n "小黄是跟我一起坐货运回来的。运费一百八。"
    n "它是我身上唯一一件升值的资产：从「零」，涨到了「一百八」。"

    show pzk delivery gloom at center_stage
    with dissolve
    p "……行吧。"
    p "潘子恺，你曾经站在财富的顶点。"
    p "现在，你只是暂时站在了一个……比较低的点。"
    pt "比较低的点。比如下水道井盖。"

    scene bg rental_room
    with dissolve
    play sound sfx_door
    show pzk delivery normal at left_stage
    with dissolve

    landlord "就这间。八平米，独立卫生间。"
    p "卫生间在哪？"
    landlord "你左手边那个帘子后面。"
    p "那不是衣柜吗？"
    landlord "衣柜在你右手边那个帘子后面。"

    n "房东老陈，五十多岁，穿着拖鞋，手里转着一串钥匙。"
    n "他看我的眼神，像在看一个刚从精神病院出来的人。"
    n "也可能是因为我问了一句——"

    menu:
        "看房的时候，问点什么？"

        "「有海景吗？」":
            p "有海景吗？"
            landlord "有。"
            n "他指了指墙上一张泛黄的海报。马尔代夫。边角已经卷起来了。"
            landlord "上一个租客留下的。送你。"

        "「能便宜点吗？」":
            p "能便宜点吗？"
            landlord "八百。押一付三。"
            p "我只有一千八。"
            landlord "……那押一付一。"
            landlord "小伙子，城中村不养闲人，但也不赶穷人。"
            $ stat("sincere", 3)

        "「这房子的投资回报率怎么样？」":
            p "这房子的投资回报率怎么样？"
            landlord "啥？"
            p "租金收益率，大概多少？您考虑过资产证券化吗？"
            landlord "……你到底租不租？"
            $ stat("zb", 3)

    play sound sfx_cash
    $ money -= 1600
    n "押一付一，一千六。"
    n "我的余额从一千八百七十二，变成了二百七十二。"
    n "我打开窗。窗外一米，是对面楼的墙。墙上晾着一条红色秋裤。"
    pt "这就是我的海景房。"
    pt "海是海报里的，景是秋裤做的。"

    jump ch4_station


## ---------------------------------------------------------------------------
## 外卖站点
## ---------------------------------------------------------------------------

label ch4_station:
    stop ambient fadeout 1.0
    scene bg city_street_day
    with fade
    play music bgm_rider fadein 1.0

    n "第二天，我去了附近的外卖站点。"
    station "以前跑过吗？"
    show pzk delivery proud at left_stage
    with dissolve
    p "跑过。开兰博基尼跑的。"
    station "……"
    station "行，吹牛的我见多了。这个月第三个了。"
    station "上一个说他开直升机送过外卖。"
    show pzk delivery awkward at left_stage
    p "我是真的——"
    station "车自备，衣服押金一百，手机下载这个App。"
    station "超时扣钱，差评扣钱，丢餐赔钱。好评……好评没钱，但是心情好。"

    play sound sfx_cash
    $ money -= 100
    n "我交了一百块押金，领了一套黄色制服。"
    n "穿上的那一刻，我照了一下站点门口的玻璃门。"
    show pzk delivery normal at left_stage
    n "嗯。"
    n "还是很帅。"
    n "只是这次，帅是唯一的了。"

    play sound sfx_ebike_start
    play sound sfx_phone
    app "骑手「潘师傅」上线成功！今日已为您匹配附近订单，祝您配送愉快～"
    pt "……这句台词怎么跟岛上的一模一样。"
    pt "那时候我觉得它很可爱。现在我觉得它在嘲讽我。"

    jump ch4_order1


## ---------------------------------------------------------------------------
## 第一单：超时
## ---------------------------------------------------------------------------

label ch4_order1:
    play music bgm_delivery fadein 0.3
    scene bg city_street_day
    with wipeleft
    play sound sfx_ebike_horn

    n "第一单：奶茶两杯，三公里，限时二十五分钟。"
    n "小黄的极速是二十五公里每小时。"
    n "理论上，我有十八分钟的冗余。"

    n "路过一家服装店的时候，橱窗玻璃反光，照出了我的侧脸。"

    menu:
        "……"

        "停下来，照一下":
            $ stat("zb", 3)
            show pzk delivery smug at center_stage
            with dissolve
            n "我停下来，照了一下。"
            n "又换了个角度，照了一下。"
            n "又整理了一下头盔下面的刘海，照了一下。"
            play sound sfx_phone
            app "您的订单即将超时！"
            show pzk delivery shock at center_stage, shake
            n "我照了十二分钟。"
            n "超时三分钟。扣款五元。"
            n "顾客备注：「骑手是在路上停下来拍写真了吗」。"
            n "……是的。"
            $ delivery_income -= 5

        "不照。现在是打工人":
            show pzk delivery normal at center_stage
            with dissolve
            n "我咬着牙，从橱窗前骑了过去。"
            n "这是我人生第一次，路过一面镜子没有照。"
            n "我感觉自己失去了什么。"
            n "大概是自我。"
            n "提前四分钟送达。顾客给了五星。"
            $ delivery_income += 6
            $ stat("sincere", 3)

    jump ch4_order2


## ---------------------------------------------------------------------------
## 第二单：前同事
## ---------------------------------------------------------------------------

label ch4_order2:
    stop music fadeout 1.0
    scene bg office_lobby
    with wipeleft
    play music bgm_office fadein 1.0

    n "第二单：CBD，环球金融中心，A座大堂。咖啡一杯。"
    n "这栋楼我很熟。"
    n "四年前，我每天早上八点走进这里，四十八楼，投资银行部。"
    n "现在，我被保安拦在了闸机外面。"

    guard "外卖放那边架子上。"
    show pzk delivery awkward at left_stage
    with dissolve

    zhao "潘……潘子恺？？"
    n "取餐的人看到我，咖啡差点掉地上。"
    n "赵磊。我以前的同组同事。现在看他的工牌，已经是VP了。"

    zhao "你不是财富自由了吗？？朋友圈天天晒游艇？"
    p "……体验生活。"
    zhao "体验……多久了？"
    p "体验到我有钱为止。"

    zhao "我靠。真的假的。"
    zhao "那你知道吗，轩翔姐现在是MD了。全行最年轻的董事总经理。"
    show pzk delivery shock at left_stage
    p "李轩翔？？"
    zhao "嗯。上个月开了三个VP。我每天上班跟上战场一样。"
    zhao "她还是那样，开会不许超过二十分钟，PPT 字号必须统一，错一个标点打回重做。"
    pt "……我记得。"
    pt "我入职第一个月，一份PPT被她打回了十七次。"
    pt "第十七次的批注只有两个字：「重做」。"
    pt "第十八次她通过了，批注还是两个字：「可以」。"
    pt "那是我那一年收到过最好的评价。"

    n "赵磊掏出手机。"
    zhao "那个……兄弟，我给你转点小费吧。"

    menu:
        "收不收？"

        "收。现在不是要面子的时候":
            show pzk delivery normal at left_stage
            p "……谢了。"
            play sound sfx_cash
            n "他转了二十块。"
            n "我说了谢谢。说出口的时候，比想象中容易。"
            $ delivery_income += 26
            $ stat("sincere", 3)

        "不收。「我送外卖，又不是要饭」":
            show pzk delivery proud at left_stage
            p "不用。我送外卖，又不是要饭。"
            zhao "行……行吧。你还是你。"
            n "我潇洒地转身离开。"
            n "然后在门口发现，小黄被贴了一张违停条。罚款五十。"
            $ delivery_income += 6
            $ money -= 50
            $ stat("zb", 3)

    jump ch4_lunch


## ---------------------------------------------------------------------------
## 午饭：旧习惯
## ---------------------------------------------------------------------------

label ch4_lunch:
    stop music fadeout 1.0
    scene bg city_street_day
    with dissolve
    play music bgm_broke fadein 1.0

    n "中午。"
    n "我的身体，自动走进了一家轻食餐厅。"
    n "以前在这栋楼上班的时候，我每天中午都来这里。"
    n "牛油果吐司，六十八。冷萃咖啡，四十二。"
    n "店员递过来菜单，我才反应过来——"
    show pzk delivery shock at center_stage
    pt "一百一十块。"
    pt "是我今天上午全部收入的三倍。"

    menu:
        "怎么办？"

        "装作若无其事，点一杯白开水":
            show pzk delivery proud at center_stage
            p "一杯水，谢谢。常温。"
            n "店员愣了一下，给我倒了一杯水。"
            n "我坐在落地窗前，优雅地喝完了这杯水。"
            n "全程保持着在曼哈顿喝下午茶的表情。"
            n "出门后在街角买了个煎饼。八块。加了两个蛋。"
            $ money -= 8
            $ stat("zb", 5)

        "转身就走，去街角买煎饼":
            show pzk delivery normal at center_stage
            p "……不好意思，走错了。"
            n "我在街角买了一个煎饼。八块。加了两个蛋。"
            n "坐在马路牙子上吃完。"
            n "说实话，比牛油果吐司好吃。"
            n "可能是因为饿。也可能是因为，这是我自己挣的钱买的。"
            $ money -= 8
            $ stat("sincere", 3)

    jump ch4_rain


## ---------------------------------------------------------------------------
## 晚上：雨
## ---------------------------------------------------------------------------

label ch4_rain:
    stop music fadeout 1.0
    play ambient sfx_rain fadein 1.0
    scene cg rider_rain
    with fade
    play music bgm_rider fadein 2.0 volume 0.7

    n "晚上八点，下雨了。"
    n "雨天单价高，我一直跑到十一点。"
    n "雨衣是站长送的，袖子短一截。"
    n "红绿灯的时候，旁边停着一辆蓝色的跑车。"
    n "不是兰博基尼。只是蓝色的。"
    n "我看了它很久，直到绿灯亮起来，它一脚油门走了，溅了我一身水。"
    pt "……以前，我就是那个溅别人一身水的人。"
    pt "原来被溅的感觉是这样的。"
    pt "我回去以后，要给那些被我溅过的人道歉。"
    pt "……不对，我根本不知道他们是谁。"

    $ delivery_income += 61
    play sound sfx_phone
    app "今日配送已完成 14 单。今日收入：¥[delivery_income]。"
    pt "我曾经一分钟的利息，比这多。"
    pt "但我从来没有像现在这样，记得每一块钱是从哪来的。"

    jump ch4_night


## ---------------------------------------------------------------------------
## 出租屋的夜晚
## ---------------------------------------------------------------------------

label ch4_night:
    stop music fadeout 2.0
    scene bg rental_room_night
    with fade
    play ambient sfx_rain fadein 1.0 volume 0.4

    show pzk delivery tired at center_stage
    with dissolve
    n "回到出租屋，十一点四十。"
    n "我湿着头发，躺在一米二的床上。床板响了一下，像在抱怨。"
    $ money += delivery_income
    n "我把口袋里的东西掏出来，放在枕头边。"
    if got_sea_glass:
        n "手机。钥匙。还有那块蓝色的海玻璃。"
    else:
        n "手机。钥匙。还有那张写着「K」的便签纸。"
    n "我想了一会儿那个冲浪的女人。"
    n "想她是真的不知道，还是全都知道。"
    n "想着想着，就睡着了。"

    hide pzk with dissolve
    stop ambient fadeout 3.0
    scene bg black
    with Dissolve(2.0)
    pause 1.0
    jump ch4_awaken


## ---------------------------------------------------------------------------
## 系统觉醒
## ---------------------------------------------------------------------------

label ch4_awaken:
    scene bg rental_room
    with fade
    n "第二天早上，六点零三分。"
    n "我被一个声音叫醒了。"
    n "不是闹钟。不是对面楼的广场舞音响。"
    n "是我脑子里的声音。"

    call sys_boot
    play music bgm_system fadein 1.0
    scene cg system_awaken
    with flash

    xt "叮。"
    xt "检测到宿主：潘子恺。男。二十七岁。前投行分析师。前亿万富翁。现外卖骑手。"
    xt "宿主资产状况：极度贫困。"
    xt "宿主自恋指数：极度富裕。"
    xt "绑定条件全部满足。"
    xt "「纯爱致富系统」绑定成功。"

    p "……"
    p "我是不是昨天淋雨淋出脑炎了。"

    xt "宿主当前余额：¥[money]。"
    xt "另有五毛钱不在账上。是一枚硬币，在你左脚的袜子里。"
    n "我脱下袜子。"
    n "叮当。一枚五毛硬币掉在了地上。"
    p "……卧槽。"

    $ sys_active = True
    $ stats_visible = True

    scene bg rental_room
    with dissolve
    show pzk casual shock at center_stage
    with dissolve

    p "你是系统？那种小说里的系统？"
    p "那我是主角了？？"
    xt "严格来说，你是我能找到的最穷的帅哥。"
    show pzk casual proud at center_stage
    p "你也觉得我帅？"
    xt "这不是重点。"
    p "这就是重点。"

    xt "本系统的使命：帮助宿主重新获得财富，并超越曾经的巅峰。"
    show pzk casual smug at center_stage, hop
    play sound sfx_sparkle
    p "好！好好好！我就知道！"
    p "上天不会抛弃一个这么帅的男人！"
    p "快，先打一个亿过来，我把小蓝赎回来——"
    xt "本系统不直接发放金钱。"
    show pzk casual normal at center_stage
    p "……那你有什么用？"
    xt "宿主需要完成指定的恋爱攻略任务，才能领取奖励。"

    n "恋爱攻略。"
    n "我愣了三秒。"
    show pzk casual narcissist at center_stage
    play sound sfx_sparkle
    n "然后笑出了声。"
    p "恋爱？攻略？"
    p "你知道我是谁吗？我潘子恺，万花丛中过，片叶不沾身。"
    p "这个系统，简直是给我量身定做的。"
    xt "本系统也是这么认为的。"
    xt "所以规则也是给你量身定做的。"
    pt "……这句话为什么让我后背一凉。"

    jump ch4_rules


## ---------------------------------------------------------------------------
## 规则（不一次讲完：边演示边讲）
## ---------------------------------------------------------------------------

label ch4_rules:
    show pzk casual normal at center_stage

    xt "规则一：本系统会扫描成年女性，并给出颜值评分。满分一百。"
    xt "只有评分达到九十分以上，才能成为正式攻略对象。"
    p "九十分？标准这么高？"
    xt "宿主自己就是按九十八分的标准要求别人的。"
    p "……你怎么知道？"
    xt "演示一下。"

    play sound sfx_sys_ding
    n "眼前弹出了一个蓝色的扫描框。框住了——"
    n "窗户玻璃上，我自己的倒影。"
    xt "扫描对象：男性。不在扫描范围。"
    xt "附加检测：自恋指数九十八，超过全国百分之九十九点九的人类。"
    show pzk casual proud at center_stage
    p "谢谢。"
    xt "不是夸你。"

    menu:
        "那……"

        "「扫一下楼下包子铺的老板娘？」":
            xt "对方已婚。本系统不扫描已婚人士。"
            xt "也不扫描未成年人。也不扫描对宿主报过警的人。"
            p "谁对我报过警？"
            xt "暂时没有。系统只是提前把规则说清楚。"

        "「颜值评分这种东西，也太不尊重人了吧？」":
            $ stat("sincere", 5)
            xt "宿主说得对。"
            xt "所以这个分数只存在于系统内部，仅用于判定任务资格。"
            xt "你要是敢在任何人面前说「你是九十六分」，系统会第一个扣你的分。"
            p "……我本来也没想说。"

    xt "规则二：每个攻略对象有独立的好感度，零到百分之百。"
    xt "好感度达到百分之九十，视为攻略成功。"
    xt "好感度靠互动、靠帮助、靠真心。花钱不一定涨，说错话一定掉。"
    p "那你直接让她爱上我，不就完了？"
    xt "本系统不提供任何精神控制服务。"
    xt "那叫犯罪。而且不浪漫。"
    pt "……一个会说「不浪漫」的系统。"

    xt "接下来，宣布宿主的第一个攻略对象。"
    xt "由命运匹配算法自动生成。不接受更换。"

    jump ch4_target


label ch4_target:
    stop music fadeout 0.5
    play sound sfx_sting
    scene bg rental_room
    show lxx silhouette at right_stage
    with dissolve
    show pzk casual normal at left_stage
    with dissolve

    xt "目标锁定。"
    $ bind_target("lxx", "李轩翔", 31, "某顶级投资银行 · 投资银行部董事总经理（MD）", 96,
                  "曾为宿主的直属上司。金色短发，白天西装，晚上十点以后换红色皮衣。强势，冷静，果断。不接受废话，不接受借口，不接受超过二十分钟的会议。")
    $ add_note("lxx", "宿主入职第一个月，PPT 被她打回 17 次。")
    play music bgm_lxx fadein 0.3
    show lxx cold at right_stage
    with dissolve
    call sys_scan("lxx")

    show pzk casual shock at left_stage, shake
    play sound sfx_shock
    p "……"
    p "…………"
    p "李轩翔？？？"
    p "换一个！换一个！我要换一个！！"
    xt "不接受更换。"
    p "你知道她是谁吗？？"
    xt "知道。你以前的上司。"
    p "你知道她当年怎么对我的吗？？"
    xt "知道。PPT 打回十七次。"
    p "你知道第十七次的批注是什么吗？"
    xt "「重做」。"
    p "……"
    p "你连这个都知道？？"

    show pzk casual gloom at left_stage
    pt "李轩翔。"
    pt "在投行的那两年，我每天早上进办公室，第一件事是看她的脸色。"
    pt "她笑过吗？我想了想。"
    pt "笑过一次。我把一个估值模型做错了，她看着我，笑了一下，说：「潘子恺，你很有勇气。」"
    pt "然后那个模型她自己通宵重做了。"
    pt "第二天，她在所有人面前说，模型是我做的。"
    pt "……我当时没多想。"

    xt "规则四：成功攻略一名对象，系统发放攻略奖金。"
    xt "第一位攻略对象，基础奖金——"
    play sound sfx_money_rain
    xt "一千万。"

    show pzk casual normal at left_stage
    n "我沉默了。"
    n "不是被吓到了。是在算。"
    n "一千万，按我现在的日收入，我需要送……"
    n "十五万六千二百五十天外卖。"
    n "四百二十八年。"
    show pzk casual smug at left_stage, hop
    play sound sfx_sparkle
    p "我接！"
    p "李轩翔是吧！"
    p "我当年搞不定她，是因为我是她下属。"
    p "现在不一样了。现在我是一个有系统的男人。"
    xt "也是一个有外卖箱的男人。"

    jump ch4_card


## ---------------------------------------------------------------------------
## 纯爱卡（第一次报销审核）
## ---------------------------------------------------------------------------

label ch4_card:
    play music bgm_system fadein 1.0
    show pzk casual normal at left_stage
    hide lxx with dissolve

    p "等等。攻略要花钱的吧？约会、吃饭、送礼物……"
    p "我现在全部身家是三百多块。"
    xt "规则三：与攻略目标相关的合理消费，可使用「纯爱卡」。"
    xt "纯爱卡采用预授权机制：宿主刷卡前，系统实时审核。审核通过，由系统支付。"
    xt "审核驳回，刷卡失败。宿主可以自己掏钱，前提是你有。"
    $ credit_limit = 3000
    play sound sfx_coin
    xt "新手期额度：三千元。随攻略进度提升。"

    p "三千？？我以前一顿早餐都不止三千。"
    xt "所以你现在在这里。"

    p "那我试一下。早餐，豆浆油条，八块。"
    call sys_audit("豆浆油条 ×1", 8, "宿主早餐", "rejected", "宿主吃早餐与攻略目标无关。另：建议加个鸡蛋，蛋白质有助于提升体能。")
    show pzk casual angry at left_stage
    p "八块都不给报？？"
    xt "李轩翔不吃你的早餐。"
    p "那她要是吃呢？"
    xt "那就是另一个审核结果了。"

    jump ch4_seal


## ---------------------------------------------------------------------------
## 规则五：纯爱封印
## ---------------------------------------------------------------------------

label ch4_seal:
    xt "最后，附加条款第七条。"
    p "怎么还有附加条款？"
    xt "所有重要的条款，都在附加条款里。你在投行待过，应该知道。"
    pt "……这个系统是不是在我们行实习过。"

    xt "规则五：纯爱封印。"
    xt "对已绑定的攻略对象，在其好感度达到百分之九十之前——"
    xt "宿主对该对象，将保持「功能性失灵」状态。"

    show pzk casual normal at left_stage
    p "功能性……失灵？"
    p "什么功能？"
    xt "你想的那个功能。"

    stop music
    scene bg black
    pause 1.5
    n "……"
    n "……………………"

    scene bg rental_room
    show pzk casual sealed at left_stage
    call seal_alarm("纯爱封印已生效。")

    play music bgm_broke fadein 0.5
    show pzk casual shock at left_stage, shake
    p "我不接受！！"
    p "这是我身上最后一项没被骗走的资产了！！"
    xt "封印仅针对攻略对象生效。"
    p "那对其他人呢？"
    xt "对其他人，你本来也没机会。"
    p "……"

    menu:
        "……"

        "「我要退货！」":
            p "我要退货！这个系统我不要了！"
            xt "本系统不支持七天无理由退货。"
            p "那十五天呢？"
            xt "不支持任何天数。"

        "「为什么要设计这种规则？？」":
            p "为什么要设计这种规则？？"
            xt "因为宿主以前谈恋爱的平均时长是十一天。"
            xt "最长的一次，是因为对方出国了，忘了分手。"
            xt "本系统的名字叫「纯爱」。不是「快餐」。"
            p "……"
            pt "我竟然无法反驳。"
            $ stat("sincere", 3)

    xt "放心。只要她的好感度达到百分之九十，封印会自动解除。"
    xt "到那时候，你会拿到一千万。"
    xt "以及你的尊严。"
    p "顺序能不能倒过来？"
    xt "不能。"

    jump ch4_tasks


## ---------------------------------------------------------------------------
## 任务发布
## ---------------------------------------------------------------------------

label ch4_tasks:
    play music bgm_system fadein 1.0
    show pzk casual normal at left_stage
    xt "发布阶段任务。"

    $ add_task("lxx_1", "lxx", "重新出现在她的生活里", "自然地。不许冒充快递、不许跟踪、不许在她公司楼下拉横幅。", 5000)
    pause 0.6
    $ add_task("lxx_2", "lxx", "在她最擅长的领域，帮她一次", "她不缺钱，不缺人追，缺的东西你自己想。", 20000)
    pause 0.6
    $ add_task("lxx_3", "lxx", "？？？", "隐藏任务。触发条件未知。", 10000, hidden=True)

    xt "任务详情可随时在右上角「系统」中查看。"
    p "第一个任务……重新出现在她的生活里。"
    p "她在四十八楼。我在城中村。"
    p "我们之间的距离，大概是一个保安，加四十七层楼，加一千万。"
    xt "还有你的自恋。"
    p "那个不算距离。那是我的魅力。"

    show pzk delivery normal at left_stage
    with dissolve
    n "我穿上黄色制服，戴好头盔，推着小黄出了门。"
    n "巷子口的煎饼摊冒着热气。"
    n "我不知道接下来要怎么接近李轩翔。"
    n "但我知道一件事——"
    n "今天，我又要送外卖了。"

    stop music fadeout 2.0
    scene bg black
    with fade
    tip "—— 第三章 完 ——"
    jump chapter5
