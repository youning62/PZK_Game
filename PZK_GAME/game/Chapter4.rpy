## Chapter4.rpy —— 第三章「十块钱的纯爱」
##
## 时间线：仙人跳破产之后，已经送了两年外卖（2068 年，潘子恺 25 岁）。
## 流程：两年后的早晨 → 糟糕的一单 → 足疗店（熟悉的技师离职）→ 门口的「新人」→ 初级扫描出现
##       → 系统说明激活条件 → 自扫 -250 → 翻旧照片（前女友全是 89 分）→ 想起高中校花丁虹依，加回微信
##       → 10 元红包 → 系统正式激活（档案解锁、纯爱封印）→ 规则 → 舔狗基金充值 ¥100 → ¥1,000,000
##       → 三次违规操作被驳回 → 丁虹依的嘲讽和朋友圈 → 一百万基金，一包泡面 →「后续剧情待更新」

label chapter4:
    stop music fadeout 1.0
    $ money = 52.5
    $ delivery_income = 0
    $ sys_stage = "none"
    $ sys_active = False
    scene bg black
    call screen chapter_card("第三章", "十块钱的纯爱")
    jump ch4_morning


## ---------------------------------------------------------------------------
## 两年后的早晨
## ---------------------------------------------------------------------------

label ch4_morning:
    scene bg black
    tip "—— 两年后 ——"
    play sound sfx_alarm_old
    scene bg rental_room
    with fade
    play music bgm_broke fadein 1.5

    n "2068 年。早上五点五十。"
    n "闹钟响到第二声，我已经坐起来了。"
    n "两年前，我的闹钟是管家。现在，我的闹钟是房租。"

    show pzk home normal at center_stage
    with dissolve

    n "起床第一件事：看天气。"
    n "小雨转阴。小雨天订单多，但是摔一跤，一天白干。"
    n "第二件事：看电量。"
    n "小黄，电量百分之三十七。昨晚充电站排队，我排到第九个就睡着了。"
    n "第三件事：抢券。"

    play sound sfx_phone
    n "五点五十九分五十八秒，我的手指悬在屏幕上方。"
    n "六点整。点击。"
    play sound sfx_cash
    show pzk home smug at center_stage, hop
    n "「满二十减五」早餐券，到手。"
    p "漂亮。"
    pt "开盘一秒建仓，零滑点，收益率百分之二十五。"
    pt "两年前，我做一单这样的交易，交易员要给我鼓掌。"
    pt "两年后，鼓掌的是楼下煎饼摊老板，因为我又去照顾他生意了。"
    $ stat("zb", 3)

    show pzk home normal at center_stage
    n "墙上那张马尔代夫海报还在。边角卷得更厉害了。"
    if got_sea_glass:
        n "窗台上放着一块蓝色的海玻璃。两年了，我没扔，也没再拿起来看过。"
    else:
        n "窗台上压着一张折好的便签纸，上面只有一个字母。两年了，我没扔，也没再打开过。"
    n "我现在会算一些以前从来不算的东西。"
    n "一顿盒饭十五块，等于三单配送费。一次差评罚五块，等于一顿早饭。"
    n "一件新衣服，等于不存在。"
    pt "但脸还是那张脸。"
    pt "就是晒黑了一点，瘦了一点，眼神里多了一点「这单能不能准时」。"

    show pzk delivery normal at center_stage
    with dissolve
    n "黄色制服，头盔，护膝。"
    n "我推着小黄出了门。"
    jump ch4_order


## ---------------------------------------------------------------------------
## 糟糕的一单
## ---------------------------------------------------------------------------

label ch4_order:
    scene bg city_street_day
    with wipeleft
    play music bgm_delivery fadein 1.0
    play ambient sfx_city fadein 1.0 volume 0.4

    app "岛团外卖提醒您：新订单。翠湖花园 9 栋 1803。黄焖鸡米饭 ×1。备注：送上楼，不要放门口，不要按门铃，要敲三下。"
    show pzk delivery normal at center_stage
    with dissolve
    pt "要求很多。配送费四块二。"
    pt "按每个要求一块钱算，这位顾客应该倒找我。"

    n "翠湖花园 9 栋。电梯门口贴着一张 A4 纸。"
    n "「电梯维修中」。"
    show pzk delivery tired at center_stage
    n "十八楼。"
    n "爬到第十楼的时候，App 提醒我：「即将超时」。"
    n "爬到第十五楼的时候，我想起两年前我住的别墅有电梯，三部。"
    n "其中一部只用来运红酒。"
    n "爬到第十八楼的时候，我什么都没想。我只想活着。"

    play sound sfx_knock
    n "敲门。三下。"
    customer "怎么这么慢？超时两分钟了。"
    show pzk delivery awkward at center_stage

    menu:
        "怎么回？"

        "「电梯坏了，不好意思。」（赔笑）":
            p "电梯坏了，我是爬上来的，不好意思啊。"
            customer "电梯坏了你不会早点出发吗？"
            pt "我早点出发，您早点下单了吗？"
            n "我没说出口。两年了，这句话我在心里说过两百次。"
            $ stat("sincere", 3)

        "「但是我很帅，算是补偿吧。」":
            show pzk delivery smug at center_stage
            p "但您看，送餐的是我。这个颜值，也算是一种补偿。"
            customer "……"
            n "门关上了。"
            n "三秒后，App 提示：您收到一条差评。"
            n "评价内容：「骑手精神状态堪忧」。"
            $ stat("zb", 5)

        "「两年前，我连黄焖鸡都不吃。」":
            show pzk delivery proud at center_stage
            p "说出来您可能不信，两年前，我连黄焖鸡这三个字都没听过。"
            customer "那你现在听过了，能给我吗？"
            n "我把黄焖鸡递了过去。"
            $ stat("zb", 3)

    play sound sfx_vibrate
    station "潘子恺，翠湖花园那单超时，罚五块，你自己去 App 上申诉。"
    show pzk delivery gloom at center_stage
    $ money -= 5
    p "申诉成功率多少？"
    station "你上次申诉成功，是去年。"
    pt "……一年一次。比我的股票分红还稳定。"

    n "那天剩下的时间，就是这样过的。"
    n "送单，等餐，被催，送单。"
    $ delivery_income += 96
    $ money += 96
    app "今日配送已完成 23 单。今日收入：¥[delivery_income]。"
    pt "九十六块。"
    pt "两年前，我在海岛上一顿早餐的小费，是九十六块的十倍。"
    pt "两年后，九十六块，是我今天跟这个城市讨价还价赢回来的全部。"
    stop ambient fadeout 1.0
    jump ch4_spa


## ---------------------------------------------------------------------------
## 足疗店
## ---------------------------------------------------------------------------

label ch4_spa:
    scene bg foot_spa_night
    with fade
    play music bgm_comedy fadein 1.0

    n "晚上九点半。我常去的那家足疗店。"
    n "门口挂着两块招牌。一块写着「足疗店」，另一块也写着「足疗店」。"
    n "老板说，店名叫什么不重要，重要的是让人知道这是足疗店。"
    n "六十八块一个钟，会员价五十八。"
    n "两年来，这是我唯一的「奢侈消费」。一个月一次。"
    pt "以前我做 SPA，按摩师是从泰国请的，按完给我递一杯冰镇椰子水。"
    pt "现在我做足疗，技师是从隔壁县来的，按完给我递一杯热水，问我要不要办卡。"
    pt "说实话，热水更暖。"

    show pzk delivery normal at center_stage
    with dissolve
    play sound sfx_door
    wangjie "哟，潘师傅，又来啦？"
    p "王姐，小芳在吗？还是老样子，四十分钟。"
    wangjie "小芳？小芳上礼拜走了，回老家结婚了。"
    show pzk delivery shock at center_stage
    p "……结婚？"
    wangjie "嫁了个开超市的。人家现在是老板娘了。"
    pt "开超市的。"
    pt "两年前，我能买下那个超市。"
    pt "两年后，那个超市的老板，娶走了我唯一会给我留一杯热水的人。"
    show pzk delivery gloom at center_stage
    wangjie "给你换个新来的？手法也挺好。"

    menu:
        "……"

        "「算了，下次吧。」":
            p "算了，王姐，下次吧。"
            n "五十八块，等于两顿盒饭。没有小芳的话，我算得出来这笔账。"
            $ stat("sincere", 2)

        "「新来的是哪里人？泰国的吗？」":
            show pzk delivery smug at center_stage
            p "新来的是哪里人？泰国的吗？"
            wangjie "隔壁县的。你要泰国的，你自己坐飞机去。"
            p "……我会去的。等我有钱了。"
            wangjie "行，那你先把上个月欠的十块钱给了。"
            pt "我忘了还欠这个。"
            $ money -= 10
            $ stat("zb", 2)

    hide pzk with dissolve
    n "我在门口的台阶上坐下来。"
    n "电动车停在旁边，电量百分之十二。"
    n "我想歇五分钟，再骑回去。"
    jump ch4_stranger


## ---------------------------------------------------------------------------
## 门口的「新人」 & 初级扫描
## ---------------------------------------------------------------------------

label ch4_stranger:
    play music bgm_awkward fadein 1.0
    show pzk delivery tired at left_stage
    with dissolve
    play sound sfx_heels
    n "高跟鞋的声音停在了我旁边。"
    xue "大哥，一个人啊？"
    n "一个穿着亮片短裙的女人，在我旁边坐了下来。"
    n "香水味很重。是那种把整条街都包下来的重。"
    xue "我叫小雪，十九岁，今天第一天来上班。"
    xue "大哥，你看着好面熟啊。你是不是……以前很有钱？"

    show pzk delivery awkward at left_stage
    pt "这一句。"
    pt "两年前，在海岛上，也有人这么开头。"

    stop music
    play sound sfx_glitch
    with vpunch
    n "就在那一瞬间——"
    n "我的脑子里，响起了一个不属于我的声音。"

    xt jaw_drop "叮——！！"
    xt rage_scream "检测到宿主处于高危社交环境。紧急启动：初级扫描模式。"
    $ sys_stage = "primary"
    show pzk delivery shock at left_stage, shake
    p "谁？？"
    xue "啊？什么谁？"
    xt side_eye "她听不见。别出声。看她头顶。"

    call sys_scan("spa_new")

    pt "刘翠芬。"
    pt "三十四岁。"
    pt "八十一分。"
    pt "……十九岁？"
    xt cry_laugh "扫描结果只显示姓名、年龄、颜值评分。其余信息，本系统不负责。"
    xt evil_grin "但宿主可以自己动动脑子。"

    xue "大哥，楼上有个 VIP 包间，第一次来免费喝茶。加个微信呗？"
    show pzk delivery gloom at left_stage
    n "免费喝茶。VIP 包间。加个微信。"
    show cg scam_night
    with dissolve
    n "两年前，那间酒店顶层套房的门，也是这么打开的。"
    n "先夸我，再请我，最后，进来三个大哥。"
    hide cg scam_night
    with dissolve
    pt "我不是第一次进这种剧本了。"
    pt "上一次，我交的学费是全部身家。"
    pt "这一次，我身上只有一百多块钱。人家要是知道，大概会觉得被侮辱了。"

    menu:
        "怎么脱身？"

        "「我电动车没锁。」":
            p "不好意思，我电动车没锁，先走了。"
            xue "电动车就在你旁边啊。"
            p "对，所以它现在很危险。"
            $ stat("zb", 2)

        "「我老婆在家等我。」":
            p "不了，我老婆在家等我。"
            xt mock_laugh "检测到宿主说谎。宿主没有老婆。宿主连女朋友都两年没有了。"
            pt "你闭嘴。"
            $ stat("zb", 1)

        "「我没钱。真的。」":
            p "小雪，不，刘……小雪。我跟你说实话，我没钱。"
            p "我身上最值钱的东西，是那辆电动车。它电量百分之十二。"
            xue "……"
            n "她站起来，拍了拍裙子，走了。走得很快。"
            n "比我那天任何一单都快。"
            $ stat("sincere", 4)

    hide pzk with dissolve
    play sound sfx_ebike_start
    n "我骑上小黄，逃离了足疗店。"
    jump ch4_primary


## ---------------------------------------------------------------------------
## 初级扫描：激活条件 & 自扫 -250
## ---------------------------------------------------------------------------

label ch4_primary:
    scene bg convenience_night
    with fade
    play music bgm_system fadein 1.0
    show pzk delivery shock at center_stage
    with dissolve

    n "我把车停在便利店门口，在玻璃门前站住了。"
    p "你到底是什么东西？"
    xt idle "本系统：「纯爱致富系统」。"
    xt grimace "当前状态：初级扫描。功能：扫描任何人的姓名、年龄、颜值评分。"
    xt side_eye "男女老少，活人照片，都能扫。"
    p "纯爱……致富？"
    p "致富？？"
    show pzk delivery smug at center_stage, hop
    play sound sfx_sparkle
    p "我就知道！老天爷不会让一个这么帅的男人一直送外卖！"
    xt mock_laugh "帅不帅，扫一下就知道了。"

    n "便利店的玻璃门上，映出一个穿黄色制服的人。"
    call sys_scan("pzk")

    show pzk delivery shock at center_stage, shake
    play sound sfx_shock
    p "负？？？二百五？？？"
    p "评分区间是多少？"
    xt eyeroll "零到一百。"
    p "那我为什么是负的！！"
    xt soul_leave "本系统也是第一次见。"
    xt cry_laugh "建议宿主不要在玻璃前站太久。可能会继续下降。"
    show pzk delivery gloom at center_stage
    pt "两年前，有人说我帅得像一笔不良资产重组成功。"
    pt "两年后，一个系统说我是负二百五。"
    pt "……这个系统不专业。"

    xt evil_grin "说正事。初级扫描只是试用版。"
    xt rage_scream "要正式激活「纯爱致富系统」，宿主需要完成一个条件："
    xt jaw_drop "向一名颜值评分九十分以上的成年女性，完成一次有效的赠与。"
    p "赠与？送钱？"
    xt grimace "红包、转账、礼物、请客，都行。金额不限。"
    xt side_eye "但必须真实完成，并且对方接受。发出去没人领，不算。"
    p "九十分以上……"
    p "这个点，我上哪找九十分以上的女人？足疗店里最高的，刚才那位，八十一。"
    xt mock_laugh "宿主可以翻翻手机。照片也能扫。"
    jump ch4_photos


## ---------------------------------------------------------------------------
## 翻旧照片
## ---------------------------------------------------------------------------

label ch4_photos:
    scene bg rental_room_night
    with fade
    play music bgm_broke fadein 1.0
    show pzk home normal at center_stage
    with dissolve

    n "回到出租屋。八平米。"
    n "我躺在床上，打开相册，往上划。"
    n "最近两年：盒饭、差评截图、电动车充电二维码、盒饭。"
    n "再往上划。"
    show pzk home smug at center_stage
    n "两年前：游艇、香槟、小蓝、私人飞机的舷窗、米其林三星的甜点。"
    pt "那时候，我不是在拍照，是在给世界发财报。"

    n "游艇派对的合照。中间那个穿白裙子的，是我那时候的女朋友。"
    call sys_scan("ex_su", photo=True)
    n "米其林生日宴。帮我吹蜡烛的那个，也是我那时候的女朋友。"
    call sys_scan("ex_lin", photo=True)
    n "滑雪场。在缆车上比心的那个，还是我那时候的女朋友。"
    call sys_scan("ex_zhou", photo=True)

    show pzk home shock at center_stage, shake
    p "八十九、八十九、八十八？？"
    p "我谈过的，全是八十九？？"
    xt cry_laugh "宿主当年的品位，非常稳定地，差一点。"
    xt side_eye "建议宿主不要伤心。评分只是系统内部的数字。"
    xt evil_grin "况且她们后来都离开了宿主。说明她们的判断力是九十分以上的。"
    p "……"

    n "一张公司年会合照。我旁边是赵磊，比着剪刀手。"
    call sys_scan("zhao", photo=True)
    pt "六十二。我心里平衡了一点。"
    $ stat("zb", 1)

    show pzk home normal at center_stage
    n "然后，我划到了最上面。"
    n "最早的一张照片，是我高中毕业那年。三中，高三七班，毕业照。"
    n "我站在最后一排，头发是那年最流行的样子。"
    n "第一排，从左数第四个——"
    pt "丁虹依。"
    pt "三中的校花。"
    pt "那年我给她写过一封情书，被她当着全班的面，改了三个错别字。"

    n "后来我发了财，换了手机号，把高中同学全删了。"
    n "那时候我觉得，他们配不上我的朋友圈。"
    pt "现在想想，是我的朋友圈配不上我的未来。"
    pt "因为我的未来，就是这间八平米的出租屋。"

    n "高中班级群我还在。三年没说过话，没退。"
    n "群成员里，她的头像是一张自拍。"
    show dhy base at right_stage
    with dissolve
    n "照片里的她，比毕业照上更好看了。"
    call sys_scan("dhy", photo=True)

    play sound sfx_sparkle
    show pzk home smug at left_stage
    xt jaw_drop "九十三分！！"
    xt rage_scream "符合激活条件！"
    p "……九十三。"
    pt "高中的时候我就知道。"
    pt "我只是没想到，十年后，她会变成我的救命稻草。"
    hide dhy with dissolve

    play sound sfx_phone
    n "我点开她的头像。添加到通讯录。"
    n "验证消息，我删了四遍。"
    menu:
        "最后发的是——"

        "「我是潘子恺。」":
            n "我是潘子恺。"
            n "五个字。我曾经用这五个字，在饭局上让一桌人站起来敬酒。"
            $ stat("sincere", 2)

        "「好久不见，老同学，我是三中最帅的那个。」":
            n "好久不见，老同学，我是三中最帅的那个。"
            xt side_eye "建议宿主附上颜值评分。负二百五。"
            $ stat("zb", 3)

    n "发送。"
    n "然后是等待。"
    n "十分钟。"
    xt mock_laugh "对方可能在思考你是谁。"
    n "二十分钟。"
    xt eyeroll "对方可能在问别人你是谁。"
    n "四十分钟。"
    xt soul_leave "对方可能已经知道你是谁了。"
    play sound sfx_vibrate
    n "四十三分钟。"
    n "「丁虹依通过了你的好友验证。」"
    jump ch4_redpacket


## ---------------------------------------------------------------------------
## 十块钱
## ---------------------------------------------------------------------------

label ch4_redpacket:
    show pzk home shock at center_stage
    $ chat_open("丁虹依")
    $ chat("note", "你已添加了丁虹依，现在可以开始聊天了。")
    $ chat("her", "？？？")
    $ chat("her", "潘子恺？？三中那个潘子恺？？")
    $ chat("her", "你不是把我们全删了吗")
    pt "她还记得。"
    pt "被删这件事，她记得比我清楚。"
    $ chat("me", "好久不见。之前换号，误删了。")
    $ chat("her", "哦。误删了三十几个人。")
    pt "……这个女人，十年前改我错别字，十年后改我谎话。"

    xt evil_grin "发吧。"
    n "我打开红包界面。"
    n "余额：¥[money]。"
    pt "两年前，我发红包，是按「零」的个数算的。"
    pt "两年后，我发红包，是按「明天吃什么」算的。"

    menu:
        "金额"

        "¥1.00（试探一下）":
            xt mock_laugh "可以。对方可能会以为你手滑。"
            p "……那还是十块吧。"

        "¥10.00（体面）":
            p "十块。体面。"
            xt side_eye "宿主对「体面」的定义，这两年变化很大。"

        "¥100.00（赌一把）":
            xt jaw_drop "然后宿主明天吃什么？"
            p "……十块。"
            $ stat("sincere", 1)

    $ chat("me", "10.00", "rp")
    $ chat("me", "一点心意，请你喝杯奶茶")
    play sound sfx_phone
    n "发送。"
    $ money -= 10
    n "我盯着屏幕。"
    n "两年前，我盯着纳斯达克开盘，都没这么紧张。"
    pause 1.0
    play sound sfx_coin
    $ chat("note", "丁虹依领取了你的红包")
    n "「丁虹依领取了你的红包。」"
    $ love("dhy", 15, quiet=True)
    $ give_gift("dhy", "微信红包", 10, "微信红包")
    jump ch4_awaken


## ---------------------------------------------------------------------------
## 系统正式激活
## ---------------------------------------------------------------------------

label ch4_awaken:
    $ chat_close()
    stop music
    play sound sfx_glitch
    with vpunch
    xt jaw_drop "叮——！！！！"
    call sys_boot
    play music bgm_system fadein 1.0
    play sound sfx_money_rain
    scene cg system_awaken
    with flash

    xt rage_scream "激活条件达成！"
    xt jaw_drop "赠与对象：丁虹依。颜值评分九十三。赠与金额：十元。"
    xt cry_laugh "本系统运行史上，最低激活金额：十元。"
    xt evil_grin "「纯爱致富系统」——正式激活！"

    $ sys_stage = "active"
    $ sys_active = True
    $ stats_visible = True

    scene bg rental_room_night
    with dissolve
    show pzk home shock at center_stage
    with dissolve
    n "八平米的出租屋里，金光乱闪。"
    n "隔壁大哥砸了一下墙：「几点了还蹦迪！」"
    p "……对不起！"

    xt mock_laugh "检测宿主资产状况：极度贫困。"
    xt eyeroll "宿主当前余额：¥[money]。"
    xt grimace "另有五毛钱不在账上。是一枚硬币，在你左脚的袜子里。"
    n "我脱下袜子。"
    n "叮当。一枚五毛硬币掉在了地上。"
    p "……卧槽。"
    $ money += 0.5
    p "你连这个都知道？"
    xt side_eye "本系统还知道，宿主是本系统能找到的最穷的……人。"
    p "你本来想说帅哥对吧？"
    xt soul_leave "负二百五。"

    xt evil_grin "首次赠与成立：丁虹依的档案已解锁。"
    call screen person_card("dhy")
    p "超强体魄？"
    xt jaw_drop "她的专属攻略奖励。攻略成功后发放。"
    p "我追她，奖励是我变强壮？"
    xt mock_laugh "考虑到宿主今天爬了十八楼差点没上来，本系统认为这个奖励很贴心。"
    jump ch4_rules


## ---------------------------------------------------------------------------
## 规则
## ---------------------------------------------------------------------------

label ch4_rules:
    show pzk home normal at center_stage
    xt idle "下面宣读规则。宿主可以随时在右上角「系统」里查看。"

    xt grimace "规则一：扫描自由。任何人都能扫。陌生人只显示姓名、年龄、颜值评分。"
    xt side_eye "规则二：成年女性，颜值九十分以上，才符合攻略条件。"
    xt mock_laugh "规则三：向符合条件的女性成功赠与，解锁她的完整档案：人物特点、当前好感度、专属奖励、攻略状态。"
    xt eyeroll "对方拒收，不算。没送到，不算。"
    p "那我送了，她就会喜欢我？"
    xt soul_leave "不会。礼物只是门票。"
    xt rage_scream "规则四：每个人好感度独立计算。达到百分之九十，攻略成功，发放她的专属奖励。"
    xt evil_grin "每个女神的奖励，都不一样。"
    xt cry_laugh "规则五：可以同时攻略多位。攻略谁，宿主自己决定。本系统不指定，不推荐，不包分配。"
    p "那你直接让她们爱上我，不就完了？"
    xt jaw_drop "本系统不提供任何精神控制服务。"
    xt side_eye "那叫犯罪。而且不浪漫。"

    xt grimace "最后，附加条款。"
    p "怎么还有附加条款？"
    xt evil_grin "所有重要的条款，都在附加条款里。宿主在投行待过，应该知道。"
    xt soul_leave "纯爱封印。"
    xt rage_scream "宿主每正式开始攻略一位对象，封印就对她单独生效。"
    xt idle "在她的好感度达到百分之九十之前，宿主对她，将保持「功能性失灵」。"
    p "功能性……什么功能？"
    xt grimace "你想的那个功能。"
    p "等一下。正式开始攻略……"
    p "我刚才那十块钱——"
    xt mock_laugh "对。丁虹依。已生效。"

    call seal_alarm("纯爱封印：丁虹依，生效中。")
    show pzk home shock at center_stage, shake
    p "十块钱！！我花了十块钱，买了一个封印？？"
    p "这是我身上最后一项没被骗走的资产了！！"
    xt cry_laugh "严格来说，十块钱买的是一个系统。封印是赠品。"

    menu:
        "……"

        "「我要退货！」":
            p "我要退货！"
            xt side_eye "本系统不支持七天无理由退货。"
            p "那十块钱能退吗？"
            xt mock_laugh "那十块钱在丁虹依那里。宿主可以自己去问她。"

        "「为什么要设计这种规则？？」":
            p "为什么要设计这种规则？？"
            xt jaw_drop "因为宿主以前谈恋爱的平均时长，是十一天。"
            xt eyeroll "最长的一次，是因为对方出国了，忘了分手。"
            xt cry_laugh "本系统的名字叫「纯爱」。不是「快餐」。"
            pt "……我竟然无法反驳。"
            $ stat("sincere", 3)

    jump ch4_fund


## ---------------------------------------------------------------------------
## 舔狗基金
## ---------------------------------------------------------------------------

label ch4_fund:
    show pzk home normal at center_stage
    p "好。封印我认了。"
    p "那「致富」呢？钱呢？"
    xt soul_leave "本系统不直接发放金钱。"
    p "……那你叫什么致富系统？"
    xt evil_grin "但是本系统可以兑换。"
    xt rage_scream "舔狗基金。宿主充值一元人民币，本系统兑换一万元舔狗基金。"

    show pzk home shock at center_stage
    n "我愣了三秒。"
    n "一比一万。"
    n "我在投行的时候，见过最离谱的杠杆，是一比五十。那家基金第二年就爆了。"
    p "一万倍？？"
    xt grimace "注意：舔狗基金不是宿主的钱。"
    xt side_eye "只能花在颜值九十分以上的成年女性身上。给她转账、发红包、买礼物、请她吃饭、约会，都行。"
    xt mock_laugh "她收到的，是真钱。宿主花掉的，是基金。"
    xt eyeroll "充值不可退。"
    p "那我第一次那十块，能换成十万吗？"
    xt cry_laugh "激活费不是充值。激活费是学费。"

    n "我看了一眼余额。"
    n "¥[money]。"
    pt "两年前，我做决策，是一个团队，三份尽调报告，五轮投委会。"
    pt "两年后，我做决策，是一个人，一张床，一包还没拆的泡面。"
    p "充一百。"
    p "剩下的，够吃到后天。"
    call sys_recharge(100)

    play sound sfx_money_rain
    show pzk home smug at center_stage, hop
    p "一百万……"
    p "一百万！！"
    xt evil_grin "这是宿主的银行卡。"
    call screen fund_card
    p "卡号还挺吉利。"
    p "信用等级……负二百五？"
    xt mock_laugh "跟宿主本人保持一致。"

    p "好。第一件事。"
    p "把小蓝买回来。首付总够了吧。"
    call sys_spend("兰博基尼（小蓝）首付", 1000000, "pzk", "车辆")
    show pzk home shock at center_stage
    p "我自己的车也不行？？"
    xt side_eye "收款人是宿主本人。宿主不是九十分以上的成年女性。"
    xt cry_laugh "宿主甚至不是零分以上的成年男性。"

    p "……行。那吃饭总可以吧。人是铁饭是钢。"
    call sys_spend("泡面 ×1", 4.5, None, "宿主晚饭")
    p "四块五！！"
    xt eyeroll "宿主的泡面，与纯爱无关。"

    show pzk home smug at center_stage
    p "那我换个思路。"
    p "我给丁虹依转一百万，再让她转回来——"
    call sys_spend("转账给丁虹依（再让她转回来）", 1000000, "dhy", "转账", cashout=True)
    xt rage_scream "虚假交易，套现，一律驳回。"
    xt mock_laugh "另外，本系统建议宿主想一想：她会转回来吗？"
    show pzk home gloom at center_stage
    p "……"
    pt "以我对她的了解，她会先把那封情书的错别字再改一遍，然后拉黑我。"
    $ stat("sincere", 2)
    jump ch4_slap


## ---------------------------------------------------------------------------
## 现实
## ---------------------------------------------------------------------------

label ch4_slap:
    play sound sfx_vibrate
    n "手机震了。"
    $ chat_open("丁虹依")
    $ chat("me", "10.00", "rp")
    $ chat("note", "丁虹依领取了你的红包")
    $ chat("her", "不是，潘子恺")
    $ chat("her", "毕业七年，把我删了，现在加回来，第一件事发十块？")
    $ chat("her", "你是被盗号了，还是开始做微商了")
    $ chat("her", "还是借钱之前先铺垫一下？")
    $ chat("her", "我先收了啊。正好蜜雪冰城")
    show pzk home gloom at center_stage
    pt "她收了。"
    pt "但是她收得，好像在帮我一个忙。"
    call sys_love("dhy", -5)
    xt side_eye "提醒：赠礼不等于好感。"
    $ chat_close()

    play sound sfx_vibrate
    n "又震了。不是她。是高中班级群。"
    n "三年没人说话的群，现在九十九加。"
    show screen phone_moments("丁虹依", "高中同学七年没联系，加回来第一件事发我十块钱红包。\n是什么新型诈骗吗？在线等，挺急的。", "王磊、陈思思、李想、高三七班班长等 37 人", [("陈思思", "潘子恺？？他不是在朋友圈晒过游艇吗"), ("李想", "十块，懂了"), ("高三七班班长", "@潘子恺 出来走两步"), ("丁虹依", "别这么说，人家可能是想请我喝水")])
    show pzk home shock at center_stage, shake
    play sound sfx_shock
    p "她发朋友圈了？？"
    xt cry_laugh "三十七个赞。宿主两年来朋友圈互动量的总和。"
    xt mock_laugh "恭喜宿主，重新回到了老同学的视野里。"
    hide screen phone_moments

    show pzk home normal at center_stage
    n "我盯着那张截图看了很久。"
    n "截图里，十块钱的红包，橙色的，很小。"
    n "我的手指停在聊天框上。"
    n "卡里有一百万舔狗基金。"
    n "我只要点几下，十块钱的笑话，就会变成一百万的传说。"
    xt idle "宿主想转的话，审核会通过的。"
    pt "我知道。"
    pt "但是一个七年没联系的人，被嘲笑之后，突然甩过来一百万。"
    pt "两年前，我会觉得这很帅。"
    pt "两年后，我知道这叫什么。"
    pt "这叫剧本。"
    p "不转。"
    xt jaw_drop "……"
    xt evil_grin "本系统记下了。"
    $ stat("sincere", 5)
    jump ch4_end


## ---------------------------------------------------------------------------
## 一百万，一包泡面
## ---------------------------------------------------------------------------

label ch4_end:
    scene bg convenience_night
    with fade
    play music bgm_broke fadein 1.0
    show pzk delivery normal at center_stage
    with dissolve
    n "晚上十一点四十。楼下便利店。"
    n "我用自己的钱，买了一包泡面。四块五。"
    $ money -= 4.5
    play sound sfx_cash
    n "自己的钱。"
    n "这四个字，我两年来第一次觉得有分量。"

    xt mock_laugh "宿主当前真实余额：¥[money]。舔狗基金余额：一百万。"
    p "账户里有一百万。"
    p "碗里有一包泡面。"
    xt eyeroll "还有一个封印。"
    p "……还有一个封印。"

    show pzk delivery smug at center_stage
    pt "但是。"
    pt "两年来，这是第一次，我觉得明天可能会不一样。"
    pt "哪怕只是一点点。"
    pt "哪怕只是从负二百五，到负二百四。"
    xt side_eye "明天早上五点五十，闹钟照样响。"
    p "我知道。"
    p "我又不是第一次送外卖。"

    stop music fadeout 2.0
    scene bg black
    with fade
    tip "—— 第三章 完 ——"
    tip "—— 后续剧情待更新 ——"
    return
