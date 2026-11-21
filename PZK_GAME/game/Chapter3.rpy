## Chapter3.rpy —— 第二章「浪与骗局」
##
## 衔接：第一次晚餐之后的一周 → 最后一晚的仙人跳 → 一夜破产
## 杨永麟在骗局中的角色保持悬念：她不在现场，只留下一双高跟鞋。

label chapter3:
    stop music fadeout 1.0
    scene bg black
    call screen chapter_card("第二章", "浪与骗局")
    jump ch3_week


## ---------------------------------------------------------------------------
## 一周（快节奏蒙太奇，但每一拍都是具体的事）
## ---------------------------------------------------------------------------

label ch3_week:
    play music bgm_island fadein 1.5
    play ambient sfx_waves fadein 1.5 volume 0.4
    scene bg surf_beach
    with fade

    if ch1_ending == "A":
        n "第二天早上六点，我定了五个闹钟，起来了。"
        n "她真的在海滩等我。没带台词，也没开车。"
    elif ch1_ending == "C":
        n "第二天，我给她转了椰子水的钱。"
        n "她没收。只回了一句：「六点，海滩。别迟到。」"
    else:
        n "那句「如果有下次的话」，三天后有了下文。"
        n "她发来一条消息：「六点，海滩。来不来随你。」"
        n "我五点就到了。"

    show pzk surf normal at left_stage
    show yyl calm at right_stage
    with dissolve

    y "趴下。划水。看浪，别看我。"
    p "我没看你。"
    y "你在看。"
    p "……我在看浪在你身上的倒影。"
    show yyl speechless at right_stage
    y "划水。"

    n "那一周，我学会了三件事。"
    n "第一，浪来之前，先低头。"
    n "第二，摔下去的时候，护住头，别护脸。"
    show yyl smile at right_stage
    n "第三，她笑的时候会先低一下头，好像不想让人看见。"

    scene bg sunset_coast
    with dissolve
    show pzk casual normal at left_stage
    show yyl smile at right_stage
    with dissolve

    n "我们一起去了很多地方。"
    n "她带我去吃不在菜单上的炒粉。"
    n "我带她去兜风——开的是小黄，因为她说小蓝太吵。"
    n "她坐在后座，手搭在我腰上。电动车时速二十五。"
    n "那是我这辈子开过最慢、也最不想停的车。"

    menu:
        "第六天晚上，她靠在栏杆边，问了我一个问题。"

        "「你会一直在岛上吗？」——我反问她":
            p "那你呢？你会一直在岛上吗？"
            show yyl calm at right_stage
            y "我？"
            y "我在哪儿都不会待太久。"
            $ stat("sincere", 3)

        "「明天是我在岛上的最后一天。」——我说实话":
            p "明天是我在岛上的最后一天。"
            show yyl surprised at right_stage
            y "……这么快？"
            p "我可以不走。"
            show yyl calm at right_stage
            y "别为了谁不走。不值得。"
            $ stat("sincere", 5)

    show yyl smile at right_stage
    y "明晚，来我住的酒店。"
    y "顶层。我请你看一次真正的日落。"
    show pzk casual shy at left_stage
    play sound sfx_heart
    pt "……"
    pt "顶层。酒店。晚上。"
    pt "我潘子恺纵横情场这么多年，这句话的意思，我懂。"
    pt "我懂得都要冒烟了。"

    stop ambient fadeout 2.0
    jump ch3_scam


## ---------------------------------------------------------------------------
## 最后一晚：仙人跳
## ---------------------------------------------------------------------------

label ch3_scam:
    stop music fadeout 1.5
    scene bg hotel_suite_night
    with fade
    play music bgm_dinner fadein 2.0

    n "酒店顶层套房。"
    n "满床玫瑰花瓣，烛光，阳台外面是月亮和海。"
    n "她穿着那双黑色高跟鞋，倒了两杯酒。"

    show yyl calm at right_stage
    with dissolve
    y "手机给我。"
    p "啊？"
    y "帮你拍一张日落。你的手机像素好。"
    n "我把手机递了过去。解锁的。"
    n "这是我那天晚上犯的第一个错误。"

    show yyl smile at right_stage
    y "先去洗个澡吧。"
    show pzk casual proud at left_stage
    with dissolve
    pt "来了。经典台词。"
    pt "人生的高光时刻，往往从一句「先去洗个澡」开始。"

    menu:
        "洗多久？"

        "洗个战斗澡，三分钟":
            n "我洗了三分钟。"
            n "剩下的时间都在对着浴室镜子做俯卧撑，让肌肉充血。"
            $ stat("zb", 5)

        "认真洗，顺便把头发吹出造型":
            n "我洗了二十分钟，吹了十五分钟头发。"
            n "发胶用掉半瓶。镜子里的人帅得让我自己都有点紧张。"
            $ stat("zb", 3)

    stop music
    play sound sfx_door_burst
    scene cg scam_night
    with vpunch
    play sound sfx_flash
    play music bgm_scam fadein 0.3

    n "我围着浴巾走出来的一瞬间——"
    n "门被踹开了。"
    n "三个大哥冲进来。闪光灯。手电筒。"

    thug1 "别动！"
    thug1 "我是她哥！"
    thug2 "我是她老公！"
    thug3 "我是她律师。"
    pt "……你们能不能先统一一下口径？"
    pt "她到底是有哥哥还是有老公？？"
    thug1 "都有！"
    thug2 "怎么了！不行吗！"
    play sound sfx_flash
    thug3 "潘先生，你涉嫌破坏他人家庭。我们这边有完整的影像资料。"
    pt "我连浴巾都没解开，你们有什么资料？？"

    n "屋子里没有她。"
    n "只有床边整整齐齐地摆着一双黑色高跟鞋。"
    n "就像我第一次在海滩上见到它们时一样。"

    menu:
        "怎么办？"

        "「她人呢？？」":
            p "她人呢？杨永麟呢？？"
            thug2 "你还有脸问我老婆？"
            thug1 "你还有脸问我妹妹？"
            n "他们说完互相看了一眼，明显不太熟。"

        "试图用肌肉震慑对方":
            show pzk casual smug at center_stage
            n "我挺起胸肌。"
            n "浴巾掉了。"
            play sound sfx_flash
            n "金链子大哥默默按下了快门。"
            $ stat("shesi", 15)

        "「我要报警。」":
            p "我要报警。"
            thug3 "可以。报警之前，建议你先看看你的手机。"
            n "我的手机，在她手里。"
            n "她不在这里。"

    stop music fadeout 0.5
    scene bg black
    with fade

    n "后面的事情，我记得不太清楚。"
    n "只记得那个律师很专业，文件准备得很齐全。"
    n "「和解协议」「资产代持授权」「紧急委托书」。"
    n "我签了很多字。每一份都有人在旁边拍照。"
    n "他们说，签了，今晚的事就当没发生过。"
    n "我想，签就签吧，反正我钱多。"
    n "这是我那天晚上犯的第二个错误。"

    jump ch3_broke


## ---------------------------------------------------------------------------
## 一夜破产
## ---------------------------------------------------------------------------

label ch3_broke:
    scene bg villa_bedroom
    with fade
    play music bgm_broke fadein 1.0

    n "第二天早上，我在别墅醒来。"
    n "习惯性地拿起手机，看余额。"
    n "就像别人醒来先喝一杯温水。"

    play sound sfx_sad
    n "……"
    n "逗号没了。"
    n "我数了一下，一个都没了。"
    n "余额：¥1,872.50。"

    show pzk casual shock at center_stage, shake
    with dissolve
    p "？？？？？？？"

    n "接下来的四十八小时，我大概经历了以下流程："
    n "给她打电话——关机。"
    n "给她发微信——「对方已开启好友验证」。"
    n "去她住的酒店——前台说，那间房登记的名字不是她。"
    n "报警——"

    show pzk casual gloom at center_stage
    cop "潘先生，你签的那些授权，从手续上看都是你本人自愿的。"
    cop "资金已经转了好几层，有的到了境外。我们会尽力，但你要有心理准备。"
    p "心理准备是什么意思？"
    cop "意思就是，先想想怎么生活吧。"

    n "别墅是租的，到期了。"
    n "小蓝在一份「资产代持授权」里被转走了。"
    n "投资账户、股票、基金——全在那几份文件里。"
    n "我签字的时候，觉得自己很大方。"

    n "最后，我名下只剩下三样东西："
    n "一千八百七十二块五毛。"
    n "一张回城的经济舱机票。"
    show ebike at right_stage
    with dissolve
    n "还有小黄。"
    n "骗子没要小黄。估计是嫌它不值钱。"
    pt "……行吧。"
    pt "至少它对我是真心的。"
    hide ebike with dissolve

    show pzk casual normal at center_stage
    n "整理行李的时候，我在枕头边上摸到了一样东西。"
    if got_sea_glass:
        n "那块蓝色的海玻璃。"
        n "她说，碎玻璃在海里磨上十几年，就不扎手了。"
        pt "……她送我这个的时候，就已经知道今天了吗？"
        pt "还是说，她也……"
        n "我没想下去。把它放进了口袋。"
    else:
        n "一张酒店便签纸，上面只有一个字母。"
        n "「K」。"
        pt "……K。"
        pt "那天晚上，给她发「到了吗」的那个人。"
        n "我把便签纸折好，放进了口袋。"

    $ stat("sincere", 3, quiet=True)
    stop music fadeout 2.0
    scene bg black
    with fade
    tip "—— 第二章 完 ——"
    jump chapter4
