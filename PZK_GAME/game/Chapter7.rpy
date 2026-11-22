## Chapter7.rpy —— 第六章「晚宴」
##
## 流程：系统升级（多目标并行，丁虹依成为第二个攻略对象）→ 找丁虹依改那套九分袖西装
##       → 沈眠的晚宴：李轩翔的深蓝长裙 + 袖口同一块料子（第一次醋意）→ 沈眠想投他
##       → 秦受的报复（大屏幕上的浴巾照）→ 当众认下 → 经侦/证监会带走秦受（「照片是 K 卖给我的」）
##       → 天台 → 沈眠约谈种子轮 → 丁虹依的消息：「那条深蓝裙子……是买给谁的？」
##
## 多目标规则：每个对象独立好感、独立封印；吃醋伏笔用 ch7_* 标记，正式吃醋事件留给后续章节。

default ch7_told_dhy = None        # 告诉丁虹依晚宴是陪李轩翔：True / False（撒谎）
default ch7_shen_pitch = None      # 沈眠问他看法：brag / insight / defer
default ch7_photo = None           # 浴巾照上大屏：own / run
default ch7_cuffs_noticed = False  # 李轩翔认出了袖口的料子

label chapter7:
    stop music fadeout 1.0
    if not sys_active:
        call ch5_setup
        $ love("lxx", 45, quiet=True)
        $ dhy_name = "丁虹依"
        $ unlock_candidate("dhy", "丁虹依", 26, "精品店柜姐 · 宿主高中同学（三中校花）", 93,
                           "开朗，嘴快，比谁都务实。在攒钱开自己的服装设计工作室。")
    scene bg black
    call screen chapter_card("第六章", "晚宴")
    jump ch7_upgrade


## ---------------------------------------------------------------------------
## 系统升级：多目标并行
## ---------------------------------------------------------------------------

label ch7_upgrade:
    play music bgm_system fadein 1.0
    scene bg rental_room
    with fade
    show pzk home normal at left_stage
    with dissolve

    n "晚宴前一天，早上六点零三分。"
    n "我又被脑子里的声音叫醒了。"
    call sys_boot
    xt jaw_drop "系统升级完成：纯爱致富系统 v1.1。"
    xt evil_grin "新功能：多目标并行攻略。"
    p "……什么意思？"
    xt mock_laugh "意思是，你可以同时攻略多个对象。好感度各算各的，封印各封各的。"
    show pzk home smug at left_stage, hop
    play sound sfx_sparkle
    p "这个好！这个才像我！"
    p "万花丛中过——"
    xt side_eye "片片都封印。"
    show pzk home shock at left_stage
    p "……"

    $ promote_candidate("dhy")
    $ set_stage("dhy", "重逢")
    call seal_alarm("女神候选「丁虹依」已转为正式攻略对象。纯爱封印 +1。")
    show pzk home gloom at left_stage
    p "两个封印？？"
    xt cry_laugh "恭喜宿主，成为本系统第一个同时被封印两次的男人。"
    xt eyeroll "另：多目标攻略存在「被发现」风险。"
    xt grimace "攻略对象发现你在追别人时，好感度可能断崖式下跌。系统不负责解释。"
    p "那你别让她们发现啊！"
    xt soul_leave "本系统只负责记账，不负责瞒天过海。"

    $ add_task("lxx_5", "lxx", "在晚宴上站在她身边", "沈眠的晚宴。秦受也会来。", 30000)
    pause 0.4
    $ add_task("dhy_1", "dhy", "让她离梦想近一步", "她在攒钱开服装设计工作室。你帮不了钱，但也许帮得了别的。", 10000)

    n "问题来了。"
    n "明天的晚宴，我要以「外卖员顾问」的身份出席。"
    n "我唯一的西装，是系统批的那套。"
    show pzk rentsuit awkward at left_stage
    with dissolve
    n "九分袖。小两号。抬手露手腕，弯腰露脚踝。"
    pt "穿这个去晚宴，我就是全场唯一一个自带笑点的嘉宾。"
    pt "……等等。"
    pt "我认识一个想当设计师的人。"

    jump ch7_tailor


## ---------------------------------------------------------------------------
## 丁虹依改西装
## ---------------------------------------------------------------------------

label ch7_tailor:
    play music bgm_comedy fadein 1.0
    scene bg boutique
    with fade
    show pzk rentsuit normal at left_stage
    show dhy base at right_stage
    with dissolve

    dhy "潘子恺，你穿的这是——"
    show dhy mock_laugh at right_stage
    play sound sfx_boing
    n "她眼睛笑成了两条缝，腮帮子鼓得像含了两个乒乓球。"
    dhy "你穿的这是你小学的校服吗？？"
    show pzk rentsuit awkward at left_stage
    p "这叫九分袖。"
    dhy "九分袖是袖子，不是你的胳膊长出来了。"

    show dhy base at right_stage
    n "她绕着我转了一圈，从西装口袋里掏出一卷软尺。"
    n "量肩，量袖，量胸围。量到胸围的时候，她停了一下。"
    dhy "……你这个胸，是认真练的。"
    pt "终于有人认可了我的胸！"
    dhy "所以西装才撑不下。"
    pt "……认可得不是很完整。"

    menu:
        "她问：「明天什么场合？」"

        "「沈眠的晚宴。陪李轩翔去。」":
            $ ch7_told_dhy = True
            p "一个投资圈的晚宴。我陪李轩翔去。"
            show dhy side_eye at right_stage
            n "她斜着眼看了我三秒，嘴角往下撇，鼻孔都张大了。"
            dhy "就是那条十二万八的蓝裙子的主人？"
            p "……嗯。"
            show dhy base at right_stage
            dhy "行。那我得把你改得配得上那条裙子。"
            dhy "不然丢的是我们店的脸。"
            $ love("dhy", 2)
            $ stat("sincere", 3, quiet=True)

        "「工作场合。就是个工作晚宴。」":
            $ ch7_told_dhy = False
            p "工作场合。就是个……工作晚宴。"
            show dhy evil_grin at right_stage
            n "她眯起眼睛，笑出了一排牙。"
            dhy "哦——工作晚宴。"
            dhy "行。工作晚宴。"
            pt "……为什么我感觉自己刚刚签了一份看不见的协议。"
            $ love("dhy", 3)

    show dhy base at right_stage
    dhy "袖子接长是接不了的，料子不够。"
    dhy "但我们可以把它变成设计。"
    n "她从柜台底下翻出一卷布。深蓝色，真丝。"
    dhy "上次那条裙子改尺寸剩下的边角料。"
    dhy "袖口滚一道深蓝的边，裤脚也滚一道。九分袖就不是寒酸，是故意的。"
    pt "……这个女人，把我的笑点改成了卖点。"

    n "她改了两个小时。我在旁边给她递剪刀、递针、递奶茶。"
    n "她说起她的工作室。名字都想好了，叫「边角料」。"
    dhy "好的料子谁都会用。我想做的是，把别人剩下的东西，变成好看的东西。"
    pt "……把别人剩下的东西，变成好看的东西。"
    pt "比如一个被骗光了的前富豪。"

    call sys_audit("西装改制手工费", 300, "宿主着装", "rejected", "驳回。这是攻略对象在为你干活，不是你在为她花钱。建议宿主自己付钱，然后请她吃饭。")
    p "改衣服多少钱？我付——"
    show dhy mock_laugh at right_stage
    dhy "你？你现在付得起吗？"
    show dhy base at right_stage
    dhy "请我吃顿麻辣烫。加两份午餐肉。"
    $ love("dhy", 5)
    $ complete_task("dhy_1")
    $ add_note("dhy", "她的工作室要叫「边角料」。她给你的袖口滚了深蓝色的边。")

    jump ch7_gala


## ---------------------------------------------------------------------------
## 晚宴
## ---------------------------------------------------------------------------

label ch7_gala:
    stop music fadeout 1.0
    scene bg ballroom
    with fade
    play music bgm_dinner fadein 1.5
    show pzk rentsuit proud at left_stage
    with dissolve

    n "沈眠的晚宴。五星酒店，宴会厅。"
    n "水晶灯，香槟，满场的投资人。每个人的手表都比我的年薪贵。"
    n "我穿着那套滚了深蓝边的九分袖，站在门口。"
    pt "进去以后，就当自己是去送一单特别大的外卖。"

    play sound sfx_heels
    show lxx gown base at right_stage
    with dissolve
    n "然后，我听到了高跟鞋的声音。"
    n "深蓝色的真丝长裙。她在那条裙子前面停了三秒，现在它在她身上。"
    play sound sfx_heart
    pt "……三秒。"
    pt "我当时只看了吊牌。我应该看她。"

    lx "你迟到了吗？"
    p "提前十五分钟。"
    lx "很好。"
    n "她看了一眼我的袖口。然后，又看了一眼。"
    show lxx gown side_eye at right_stage
    n "眼皮垂下来，嘴角往下一撇，鼻孔微微张大。是一个我从来没在她脸上见过的表情。"
    lx "这块料子。"
    p "……店里剩下的边角料。"
    lx "谁改的？"
    menu:
        "怎么回答？"

        "「高中同学。卖你那条裙子的柜姐。」":
            p "高中同学。就是卖给你那条裙子的柜姐。"
            lx "哦。"
            lx "手艺不错。"
            n "她把头转了过去。"
            $ love("lxx", -1)

        "「我自己改的。」":
            p "我自己改的。"
            show lxx gown smug at right_stage
            lx "你连 PPT 字号都统一不了。"
            lx "你会滚边？"
            p "……"
            $ love("lxx", -2)
            $ stat("zb", 3)

    $ ch7_cuffs_noticed = True
    xt evil_grin "检测到攻略对象「李轩翔」出现轻微醋意。"
    xt side_eye "系统温馨提示：你袖口上的，是她裙子的料子。"
    pt "……我现在才意识到这件事有多危险。"
    $ add_note("lxx", "她认出了你袖口的料子。她问了「谁改的」。")

    jump ch7_shen


label ch7_shen:
    show shen base at center_stage
    with dissolve
    play sound sfx_sparkle
    shen "李——轩——翔——！"
    n "一个穿香槟金短裙的女人端着香槟，几乎是蹦过来的。"
    n "短发，大眼睛，红唇，笑声比水晶灯还亮。"
    show lxx gown base at right_stage
    lx "沈眠。"
    shen "老对手！你居然真的来了！我还以为你会说「有议程吗」！"
    lx "有。他。"
    show shen jaw_drop at center_stage
    play sound sfx_shock
    n "沈眠转过头看着我。眼珠子瞪得像两个乒乓球，下巴差点掉到香槟杯里。"
    shen "你就是那个外卖员！掀了岛团底的那个！"
    show shen base at center_stage
    shen "我投了十年的消费，第一次看见有人从骑手端把一个平台的数据拆穿。"
    shen "我问你一个问题。"
    shen "如果让你做一家公司，你做什么？"

    menu:
        "怎么回答？"

        "「我以前身价上万亿，做什么都能成。」":
            $ ch7_shen_pitch = "brag"
            show pzk rentsuit proud at left_stage
            p "我以前身价一万亿美元以上。做什么都——"
            show shen smug at center_stage
            n "她的眉毛挑到了发际线，下巴抬得能顶到天花板。"
            shen "「以前」。"
            shen "我不投「以前」。"
            show lxx gown smug at right_stage
            lx "我早就告诉过你。"
            $ stat("zb", 5)

        "「骑手数据核验。让平台没法刷单。」":
            $ ch7_shen_pitch = "insight"
            show pzk rentsuit normal at left_stage
            p "骑手数据核验。"
            p "现在投资人看外卖平台，只看平台给的数据。但平台说多少单，就是多少单。"
            p "如果有一个第三方，按站点、按时段、按真人骑手抽查，数据就造不了假。"
            p "我可以从我们站开始。三十一个真人，八十七个账号。"
            show shen evil_grin at center_stage
            n "她的眼睛眯成了两条缝，嘴角咧到了耳根，手指尖对在一起。"
            shen "……我投你。"
            p "啊？"
            shen "种子轮。条件是，你得继续送外卖。"
            $ love("lxx", 3)
            $ stat("sincere", 5, quiet=True)

        "看向李轩翔：「这个，得问我老板。」":
            $ ch7_shen_pitch = "defer"
            p "这个问题……得问我老板。"
            show lxx gown mock_laugh at right_stage
            lx "我不是你老板。四年前就不是了。"
            show shen mock_laugh at center_stage
            shen "哈！轩翔，你笑了！我认识你七年，你在晚宴上笑的次数是零！"
            show lxx gown blush_melt at right_stage
            n "李轩翔的脸一直红到了耳朵，眼睛都开始打转。"
            lx "我没有。"
            $ love("lxx", 4)

    hide shen with dissolve
    jump ch7_qin


## ---------------------------------------------------------------------------
## 秦受的报复
## ---------------------------------------------------------------------------

label ch7_qin:
    stop music fadeout 0.5
    play sound sfx_sting
    n "灯暗了。"
    n "宴会厅前面的大屏幕亮了起来。"
    show qin smug at center_stage
    with dissolve
    play music bgm_tension fadein 0.5
    qin "各位，打扰一下。"
    qin "今晚的慈善环节开始之前，我想给大家介绍一位特别的嘉宾。"
    qin "——前亿万富翁，现外卖骑手，潘子恺先生。"
    play sound sfx_flash
    n "大屏幕上出现了一张照片。"
    n "酒店套房。闪光灯。一个只围着浴巾、表情惊恐的男人。"
    n "那是我。"
    show qin sneer at center_stage
    qin "海岛，仙人跳，一夜之间输得只剩一条浴巾。"
    qin "这样的人，今晚坐在这里，跟各位谈投资？"
    n "全场安静了一秒。"
    n "然后，有人笑了。笑声像水一样从四面八方漫过来。"

    show pzk rentsuit awkward at left_stage
    xt jaw_drop "检测到宿主社会性死亡。"
    xt rage_scream "系统建议：跑！！"
    pt "跑。"
    pt "我跑过一次。穿着浴巾，从三个大哥手里跑出去。"
    pt "推开门，外面还是他们的人。"

    menu:
        "……"

        "站着。拿起话筒":
            $ ch7_photo = "own"
            jump ch7_own

        "转身离开":
            $ ch7_photo = "run"
            jump ch7_run


label ch7_run:
    n "我转过身，往门口走。"
    n "一只手抓住了我的袖口。滚着深蓝边的那只。"
    show lxx gown base at right_stage
    with dissolve
    lx "站住。"
    lx "你在会议室里能讲五分钟，在这里也能。"
    n "她把话筒塞进我手里。"
    $ love("lxx", 2)
    jump ch7_own


label ch7_own:
    play music bgm_lxx fadein 1.0
    show pzk rentsuit normal at left_stage
    n "我走上台。从秦受手里，拿过了话筒。"
    p "照片上是我。"
    p "我被骗了。全部。这是真的。"
    p "我现在送外卖，一天跑十四单，雨天单价高，我会跑到十一点。这也是真的。"
    n "笑声停了。"
    p "还有一件事也是真的。"
    p "我们站点的骑手名单上有八十七个账号，每天来报到的只有三十一个人。"
    p "剩下五十六个账号，注册在「秦氏信息科技」名下。"
    p "秦先生今晚放这张照片，是想让大家别听一个外卖员说话。"
    p "可他怕的，就是一个外卖员说话。"
    show qin angry at center_stage
    qin "你——！"

    show shen mock_laugh at far_right
    with dissolve
    shen "啪、啪、啪。"
    n "沈眠在台下，第一个鼓起了掌。"
    n "然后是第二个、第三个。"

    play sound sfx_door_burst
    stop music fadeout 0.3
    n "宴会厅的门开了。"
    n "进来四个穿便装的人，亮了一下证件。"
    cop "秦受先生？关于岛团外卖数据造假的案子，请你跟我们回去配合调查。"
    show qin pale at center_stage
    play sound sfx_sad
    n "秦受的脸，从红色变成了白色，又从白色变成了灰色。"
    show lxx gown smug at right_stage
    with dissolve
    lx "我说过，下个月来找你的，是证监会。"
    lx "提前了。"

    show qin angry at center_stage
    qin "那张照片——你以为是我拍的吗？"
    qin "是一个叫 K 的人卖给我的！五十万！"
    play sound sfx_sting
    show pzk rentsuit awkward at left_stage
    pt "……K。"
    hide qin with moveoutright
    n "他被带走了。"
    n "大屏幕上的照片，被酒店的人关掉了。"

    $ complete_task("lxx_5")
    $ love("lxx", 8 if ch7_photo == "own" else 5)
    $ set_stage("lxx", "并肩")
    $ add_note("lxx", "那张浴巾照是 K 卖给秦受的。")
    xt cry_laugh "宿主社会性死亡后成功复活。系统已存档。"

    jump ch7_terrace


## ---------------------------------------------------------------------------
## 天台
## ---------------------------------------------------------------------------

label ch7_terrace:
    play music bgm_lxx_soft fadein 2.0
    scene bg hotel_terrace
    with fade
    show pzk rentsuit normal at left_stage
    show lxx gown base at right_stage
    with dissolve

    n "晚宴散场之前，她在天台找到了我。"
    lx "你刚才站在台上的时候，在想什么？"
    p "在想，原来被人笑，也没有那么疼。"
    p "比被骗光了疼得轻多了。"
    n "她没说话。走到栏杆边，看着城市的灯。"
    lx "潘子恺。"
    lx "那个 K……你认识吗？"
    p "见过两个字。一次在她的手机上，一次在一张便签纸上。"
    lx "……我会查。"
    lx "这是风控的职业病。"
    n "她说这话的时候，没有看我。"
    n "但她把手，放在了我旁边的栏杆上。离我的手，大概五厘米。"
    play sound sfx_heart
    show pzk rentsuit awkward at left_stage
    call seal_alarm("纯爱封印运行正常。五厘米。系统量过了。")
    pt "……我真的什么都没想。"
    pt "我只是在想，五厘米，原来这么远。"
    $ love("lxx", 4)

    show lxx gown side_eye at right_stage
    lx "你的袖口。"
    p "嗯？"
    lx "下次，别用别人剩下的料子。"
    lx "……我那里还有。"
    pt "……这是什么意思。"
    xt evil_grin "系统翻译：她想给你做袖口。"
    xt side_eye "或者：她不想别人给你做袖口。"
    xt mock_laugh "两个意思，系统都存档了。"

    jump ch7_scan_shen


label ch7_scan_shen:
    hide lxx with dissolve
    show shen base at right_stage
    with dissolve
    play music bgm_system fadein 1.0
    shen "找到你了！种子轮的事，下周来我办公室详谈！"
    shen "穿这套！九分袖！我喜欢！"
    show shen evil_grin at right_stage
    n "她冲我比了个心，又蹦蹦跳跳地走了。"
    pt "……一个投资人，要投一个外卖员。"
    pt "条件是他得继续送外卖。"
    xt mock_laugh "宿主的人生，终于有人愿意下注了。"
    xt side_eye "提醒：她不在本系统的攻略范围内。她是你的投资人。"
    pt "……我也没想攻略她。"

    jump ch7_end


label ch7_end:
    stop music fadeout 2.0
    scene bg rental_room_night
    with fade
    show pzk home normal at center_stage
    with dissolve
    n "回到出租屋，十二点。"
    n "我把那套九分袖挂在门后。深蓝色的滚边，在台灯下面有一点反光。"
    play sound sfx_phone
    show screen phone_notice("微信 · 丁虹依", "袖子还行吧？对了——")
    pause 0.5
    hide screen phone_notice
    play sound sfx_phone
    if ch7_told_dhy:
        show screen phone_notice("微信 · 丁虹依", "她穿那条裙子好看吗？……算了，别回答。")
    else:
        show screen phone_notice("微信 · 丁虹依", "「工作晚宴」需要穿跟她同一块料子的袖口吗？")
    pause 0.5
    show pzk home shock at center_stage, shake
    play sound sfx_shock
    p "……"
    hide screen phone_notice
    xt evil_grin "检测到攻略对象「丁虹依」的醋意值正在积累。"
    xt eyeroll "系统再说一遍：本系统只负责记账，不负责瞒天过海。"
    pt "两个封印。"
    pt "两条深蓝色的滚边。"
    pt "还有一个叫 K 的人，五十万，卖了我最丢人的一张照片。"
    pt "……行吧。"

    scene bg black
    with fade
    tip "—— 第六章 完 ——"
    call screen chapter_card("未完待续", "吃醋 ／ K ／ 种子轮")
    return
