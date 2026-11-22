## Chapter5.rpy —— 第四章「前上司李轩翔」（李轩翔攻略篇 · 上）
##
## 流程：接近失败三连 → 深夜订单，48 楼重逢 → 报销审核（兰博基尼 / 西装）
##       → 骑手视角发现「岛团外卖」刷单 → 帮她叫停 IPO 项目（任务二）
##       → 凌晨两点抓娃娃店：她不为人知的一面（隐藏任务）→ 新任务与伏笔
##
## 本章运行中的梗：
##   报销审核 ×3（早餐被拒 → 兰博基尼被拒 → 给她买的煎饼秒批，回收「李轩翔不吃你的早餐」）
##   纯爱封印 ×2（第一次他慌，第二次他真的什么都没想，系统反而只是"例行提示"）
##   「可以」（当年 PPT 打回 17 次后的批注，本章她再说一次）

default lxx_honest_reunion = False   # 重逢时是否说了实话
default lxx_pitch = None             # 怎么把刷单证据交给她：barge / memo / snack
default lxx_meeting_style = None     # 会议上：concise / show
default lxx_claw = None              # 抓娃娃店里：help / company / tease
default lxx_shark = False            # 她把猫猫娃娃给了你
default lxx_suit = False             # 是否租了西装

label chapter5:
    stop music fadeout 1.0
    if not sys_active:
        call ch5_setup
    scene bg black
    call screen chapter_card("第四章", "前上司李轩翔")
    jump ch5_approach


## 从章节选择直接进入时补全系统状态
label ch5_setup:
    $ sys_active = True
    $ money = 312
    $ credit_limit = 3000
    $ bind_target("lxx", "李轩翔", 31, "某顶级投资银行 · 投资银行部董事总经理（MD）", 96,
                  "曾为宿主的直属上司。金色短发，白天西装，晚上十点以后换红色皮衣。强势，冷静，果断。不接受废话，不接受借口，不接受超过二十分钟的会议。")
    $ add_task("lxx_1", "lxx", "重新出现在她的生活里", "自然地。不许冒充快递、不许跟踪、不许在她公司楼下拉横幅。", 5000)
    $ add_task("lxx_2", "lxx", "在她最擅长的领域，帮她一次", "她不缺钱，不缺人追，缺的东西你自己想。", 20000)
    $ add_task("lxx_3", "lxx", "？？？", "隐藏任务。触发条件未知。", 10000, hidden=True)
    return


## ---------------------------------------------------------------------------
## 接近：三种失败
## ---------------------------------------------------------------------------

label ch5_approach:
    play music bgm_comedy fadein 1.0
    scene bg city_street_day
    with fade
    show pzk delivery normal at left_stage
    with dissolve

    n "任务一：重新出现在她的生活里。"
    n "自然地。"
    pt "自然地。这个词对我来说太难了。"
    pt "我这辈子做过最自然的事，是照镜子。"

    menu:
        "怎么接近她？"

        "在公司大堂「偶遇」她":
            scene bg office_lobby
            with dissolve
            show pzk delivery proud at left_stage
            n "我在环球金融中心大堂的沙发上，坐了三个小时。"
            n "摆了一个偶遇专用的姿势：低头看手机，偶尔抬头，眼神里带着一丝忧郁。"
            guard "这位外卖小哥，你的单子是送到沙发上吗？"
            show pzk delivery awkward at left_stage
            n "我被请了出去。"
            xt side_eye "提醒：这不叫偶遇。这叫蹲守。"
            xt jaw_drop "再蹲一次，系统建议你直接去派出所自首。"

        "给她发微信":
            show pzk delivery normal at left_stage
            n "我翻出了她的微信。头像是一片纯黑。"
            n "上一次聊天记录，停在四年前。"
            n "我：「李总，辞职报告我放您桌上了。」"
            n "她：「收到。」"
            pt "……就两个字。我当年在这两个字前面站了五分钟。"
            n "我打了一行字，删掉。又打一行，又删掉。"
            n "最后发出去的是："
            p "「李总，好久不见。最近还好吗？」"
            n "已读。"
            n "没有回复。"
            xt eyeroll "消息发送成功。对方已读。"
            xt side_eye "系统为宿主分析：这条消息信息量为零。她没有理由回复。"

        "找前同事赵磊帮忙":
            show pzk delivery normal at left_stage
            p "赵磊，帮我约一下李轩翔。"
            zhao "你疯了？？"
            zhao "我约她？我连跟她说话都要提前打草稿。"
            zhao "上周有个MD想约她吃饭，她回了一句：「有议程吗？」"
            zhao "人家说没有，就是吃饭。她说：「那就不用吃了。」"
            show pzk delivery awkward at left_stage
            pt "……她还是她。"

    jump ch5_order


## ---------------------------------------------------------------------------
## 深夜订单 & 重逢
## ---------------------------------------------------------------------------

label ch5_order:
    stop music fadeout 1.0
    scene bg city_street_night
    with fade
    play ambient sfx_city fadein 1.0 volume 0.4

    n "三天过去了。任务一毫无进展。"
    n "第四天晚上，十一点四十七分。"
    play sound sfx_phone
    show screen phone_notice("岛团外卖 · 新订单", "黑咖啡 ×1（双份浓缩，不加糖）→ 环球金融中心 A座 48F\n备注：别按门铃。敲三下。")
    pause 0.3
    show pzk delivery shock at center_stage
    with dissolve
    p "……四十八楼。"
    hide screen phone_notice
    n "我盯着那行备注看了很久。"
    n "上一个让我「放在黑色高跟鞋旁边」的女人，把我骗得只剩一辆电动车。"
    pt "但这个不一样。"
    pt "双份浓缩，不加糖。四年前，我每天晚上十一点给她买的就是这个。"
    xt cry_laugh "检测到命运。"
    xt evil_grin "也可能只是她懒得换口味。"

    stop ambient fadeout 1.0
    scene bg elevator
    with dissolve
    play sound sfx_elevator
    show pzk delivery normal at center_stage
    with dissolve
    n "电梯镜子里，是一个穿黄色制服的男人。"
    n "四年前，同一部电梯，镜子里的我穿的是定制西装。"
    menu:
        "电梯里……"

        "整理一下头盔和刘海":
            show pzk delivery smug at center_stage
            n "我把头盔扶正，刘海拨出一个弧度。"
            n "外卖服也是可以穿出高级感的。"
            n "……大概。"
            $ stat("zb", 3)

        "深呼吸。别想太多":
            n "四十八层。电梯走了四十二秒。"
            n "我在心里排练了四十二秒的开场白。"
            n "一句都没用上。"
            $ stat("sincere", 2)

    play sound sfx_knock
    scene bg ib_office_night
    with fade
    play ambient sfx_office fadein 1.0 volume 0.3
    n "咚。咚。咚。"
    lx "进来。"

    stop ambient
    play music bgm_lxx fadein 0.5
    scene cg reunion
    with dissolve

    n "整层楼只有她的办公室还亮着灯。"
    n "她坐在三块屏幕后面，头也没抬。"
    lx "放桌上。"
    n "我放下咖啡。"
    n "她伸手去拿，看了一眼外卖袋上的骑手名字。"
    n "手停了。"
    n "然后，她抬起头。"

    lx "……潘子恺。"

    n "金色短发。西装还没换。"
    n "四年前，她一到晚上十点，就会把西装挂进柜子里，换上一件红色皮衣。"
    n "全组只有我知道。因为那时候，只有我陪她加班到十点以后。"
    n "现在快十二点了。她还穿着西装。"
    pt "……这个项目，让她连换衣服的时间都没有。"

    scene bg ib_office_night
    with dissolve
    show pzk delivery awkward at left_stage
    show lxx surprised at right_stage
    with dissolve

    p "李……李总。好久不见。"
    show lxx cold at right_stage
    n "她的惊讶只持续了一秒。"
    n "然后，我看着她的眼睛像过尽调清单一样，从上到下扫了我一遍。"

    lx "你破产了。"
    p "……您怎么知道？"
    lx "第一，你穿着外卖服。"
    lx "第二，你右手手腕上没有那块表了，但印子还在。卖了不到一个月。"
    lx "第三，你在看我桌上那个三明治。"
    show pzk delivery shock at left_stage
    pt "……我确实在看那个三明治。"

    lx "怎么回事？"

    menu:
        "怎么回答？"

        "「体验生活。顺便……关心一下老领导。」":
            show pzk delivery proud at left_stage
            p "体验生活。顺便关心一下老领导。"
            show lxx speechless at right_stage
            lx "你当年说你的模型没问题，也是这个表情。"
            lx "后来那个模型的折现率填反了。"
            show pzk delivery awkward at left_stage
            p "……"
            $ love("lxx", 2)

        "「被骗了。全部。」":
            $ lxx_honest_reunion = True
            show pzk delivery normal at left_stage
            p "被骗了。"
            p "仙人跳。在海岛上。"
            show lxx cold at right_stage
            lx "多少？"
            p "全部。"
            lx "全部是多少？"
            n "我说了一个数字。"
            n "她沉默了三秒。这三秒里，我看到她在心里算了一下，这个数字后面有几个零。"
            show lxx tired at right_stage
            lx "我四年前就跟你说过。你的持仓集中度太高，风险敞口太大。"
            lx "你说：「李总，富贵险中求。」"
            p "……现在险求到了，富贵没了。"
            n "她把桌上的三明治推到我面前。"
            lx "吃了。"
            p "这是您的晚饭。"
            show lxx cold at right_stage
            lx "我的晚饭是咖啡。吃。"
            $ love("lxx", 8)
            $ stat("sincere", 5)

        "「李总还是这么晚下班啊。」":
            show pzk delivery normal at left_stage
            p "李总还是这么晚下班啊。"
            show lxx speechless at right_stage
            lx "你还是这么不会转移话题。"
            lx "不想说就不说。我没兴趣挖别人的伤口。"
            $ love("lxx", 4)

    n "她站起来，绕过桌子，走到我面前。"
    n "脚步踩在地毯上，没有声音。"
    show lxx cold at center_stage
    with move
    n "她伸手——"
    n "把我歪掉的头盔扣带扶正了。"
    lx "扣带松了。骑车不安全。"

    show pzk delivery sealed at left_stage
    call seal_alarm("检测到宿主与攻略对象距离小于五十厘米。纯爱封印运行正常。")
    show pzk delivery shock at left_stage, shake
    pt "我什么都没想！！"
    pt "我真的什么都没——好吧我想了一点点——"
    xt soul_leave "已记录。"

    show lxx speechless at right_stage
    with move
    lx "你抖什么？"
    p "冷。"
    lx "空调二十六度。"
    p "……我怕冷。"

    show lxx cold at right_stage
    lx "你在跑哪个平台？"
    p "岛团外卖。"
    n "她的眼睛眯了一下。很短。"
    lx "跑了多久？"
    p "两周。"
    lx "……嗯。"
    n "她没再问。回到桌后，打开了一份文件。"
    lx "下次别穿这身来我办公室。保安会以为你要跳楼。"
    lx "还有。"
    lx "五星。"

    $ complete_task("lxx_1")
    $ set_stage("lxx", "重新认识")
    $ add_note("lxx", "她还是喝双份浓缩，不加糖。晚饭是咖啡。")

    stop music fadeout 1.5
    scene bg city_street_night
    with fade
    show pzk delivery normal at center_stage
    with dissolve
    n "我站在楼下，抬头看四十八楼那扇亮着的窗。"
    pt "她问我跑哪个平台的时候，眼神变了。"
    pt "那是她在会上听到一个不对劲的数字时的眼神。"
    pt "我在她手下干了两年。我认得。"

    jump ch5_audit


## ---------------------------------------------------------------------------
## 报销审核：兰博基尼 & 西装
## ---------------------------------------------------------------------------

label ch5_audit:
    play music bgm_system fadein 1.0
    scene bg rental_room
    with fade
    show pzk home normal at left_stage
    with dissolve

    n "第二天。"
    n "我躺在床上，思考一个深刻的问题。"
    p "系统。"
    p "我觉得，要攻略李轩翔，我需要一辆车。"
    xt rage_scream "宿主有小黄。"
    p "我是说，像样的车。比如……兰博基尼。"
    p "约会的时候总得接送吧？这叫约会交通费。"

    call sys_audit("兰博基尼 Huracán（二手，蓝色）", 2800000, "约会交通费", "rejected", "约会交通费不包括车辆所有权。另：宿主目前没有约会。另另：她有司机。")
    show pzk home shock at left_stage
    p "那租呢？租一天！"
    xt idle "租一天的费用超过宿主纯爱卡额度九百倍。"
    xt grimace "另，系统查询到：上一次宿主开蓝色跑车接女生，结果是现在这样。"
    show pzk home gloom at left_stage
    p "……你戳人痛处的能力，跟她有一拼。"

    menu:
        "那申报点什么？"

        "一套西装。下次见她不能再穿外卖服":
            call sys_audit("西装租赁（三天）", 199, "攻略对象工作场合着装", "approved", "合理。她说过别穿外卖服去她办公室。已为宿主选择租赁而非购买。尺码按宿主四年前的身材，可能偏小。")
            $ add_note("lxx", "租了一套西装。袖子短一截。")
            $ lxx_suit = True
            p "等等，为什么是四年前的尺码——"
            xt mock_laugh "因为四年前，你还没开始练胸。"
            pt "这句话我好像在哪听过。"

        "一束花，送到她办公室":
            call sys_audit("玫瑰 99 朵", 1314, "攻略礼物", "rejected", "她办公室不允许摆花，花粉影响空调过滤网。另：99 朵玫瑰属于宿主的旧套路，旧套路的平均有效期是 11 天。")
            p "你怎么知道她办公室不许摆花？"
            xt side_eye "系统做了尽调。宿主也应该做。"
            pt "……尽调。"

    jump ch5_clue


## ---------------------------------------------------------------------------
## 骑手视角：岛团外卖不对劲
## ---------------------------------------------------------------------------

label ch5_clue:
    play music bgm_rider fadein 1.0
    scene bg city_street_day
    with fade
    show pzk delivery normal at left_stage
    with dissolve

    n "尽调。"
    n "这个词在我脑子里转了一整天。"
    n "然后，我开始注意到一些奇怪的事。"

    n "第一件：凌晨三点，App 上会突然冒出一大批订单。"
    n "取餐地址和送餐地址是同一栋楼，距离零米，配送费照付。"
    n "没有骑手接。十分钟后，它们自己显示「已完成」。"

    n "第二件：我们站点的骑手名单上有八十七个人。"
    n "但我每天早上数，来报到的只有三十一个。"
    station "那些号啊？总部给的。不用管，又不占你的单。"

    n "第三件：我连续三天，被派到同一家「餐厅」取餐。"
    play sound sfx_shock
    show pzk delivery shock at left_stage
    n "导航到了，是一个公共厕所。"
    n "厕所门口贴着一张营业执照复印件：「金牌黄焖鸡」。"

    pt "零米订单。幽灵骑手。厕所餐厅。"
    pt "我在投行做了两年尽调。"
    pt "这不是平台的漏洞。"
    pt "这是在刷数据。"

    stop music fadeout 1.0
    scene bg office_lobby
    with dissolve
    play music bgm_office fadein 1.0
    show pzk delivery normal at left_stage
    with dissolve
    n "中午，我又去给赵磊送了一次咖啡。"
    zhao "你最近跑单还顺吗？"
    zhao "跟你说个秘密——我们现在在做的最大的项目，就是岛团外卖的上市。"
    zhao "张总亲自拍板，我们行做主承销。光承销费就好几个亿。"
    zhao "就是轩翔姐一直卡着不签尽调报告，说数据「太好看了」。"
    zhao "张总这两天在会上都快拍桌子了。"
    show pzk delivery shock at left_stage
    pt "……数据太好看了。"
    pt "她问我跑哪个平台。她问我跑了多久。"
    pt "她早就在怀疑了。她只是缺一样东西。"
    pt "缺一个真的在这个平台上跑过的人。"

    xt jaw_drop "提示：任务二「在她最擅长的领域，帮她一次」触发条件已满足。"
    xt eyeroll "提醒：她最擅长的领域，也是宿主曾经擅长的领域。"

    jump ch5_pitch


label ch5_pitch:
    show pzk delivery normal at left_stage

    menu:
        "怎么把这些交给她？"

        "直接冲进她的会议室，当场揭穿！":
            $ lxx_pitch = "barge"
            jump ch5_pitch_barge

        "写一页备忘录。结论先行，三条证据，发到她邮箱":
            $ lxx_pitch = "memo"
            jump ch5_pitch_memo

        "半夜买份煎饼送上去，当面跟她讲":
            $ lxx_pitch = "snack"
            jump ch5_pitch_snack


label ch5_pitch_barge:
    scene bg meeting_room
    with wipeleft
    play music bgm_comedy fadein 0.3
    show lxx angry at right_stage
    show pzk delivery proud at left_stage
    with dissolve
    n "我推开会议室的玻璃门。"
    p "等一下！这个项目有问题！"
    n "会议室里十二个人，十二双眼睛。"
    n "张总的咖啡停在嘴边。"
    n "李轩翔没动。她只是慢慢地，把笔放下了。"
    guard "先生，请你出去。"
    show pzk delivery awkward at left_stage
    n "我被保安架出了会议室。像一只被拎出厨房的龙虾。"
    $ love("lxx", -3)

    scene bg office_lobby
    with dissolve
    show pzk delivery gloom at left_stage
    n "四十分钟后，她下来了。"
    show lxx cold at right_stage
    with dissolve
    lx "你知道你刚才干了什么吗？"
    p "我在帮你。"
    lx "你在会议室里喊「项目有问题」，然后什么证据都没给出来，就被保安拖走了。"
    lx "现在张总觉得我找了个外卖员来闹事。"
    lx "我这三周的努力，被你在十二个人面前变成了一个笑话。"
    show pzk delivery awkward at left_stage
    p "……我有证据。"
    lx "那你为什么不先给我？"
    p "……"
    n "因为我想当着所有人的面帅一次。"
    n "这句话我没说出口。但她看出来了。"
    show lxx tired at right_stage
    lx "证据。给我。"
    n "我把手机里的截图给了她。零米订单，幽灵骑手，厕所门口的营业执照。"
    n "她一张一张看完，看了很久。"
    lx "……这次，我替你收拾烂摊子。"
    lx "下次你再这样，我不会。"
    $ love("lxx", 4)
    jump ch5_meeting


label ch5_pitch_memo:
    scene bg rental_room_night
    with dissolve
    play music bgm_office fadein 0.5
    play sound sfx_typing
    show pzk home normal at left_stage
    with dissolve
    n "我借了楼下网吧的电脑。"
    n "一页纸。她当年教我的格式。"
    n "标题：关于岛团外卖运营数据真实性的骑手端观察。"
    n "第一段，结论：平台订单量与活跃骑手数存在系统性虚增，建议暂缓签署尽调报告。"
    n "第二段，三条证据，每条附截图和时间戳。"
    n "第三段，可验证的方法：随机抽取二十个站点，凌晨三点实地清点骑手。"
    n "全文四百一十二个字。字号统一。标点我检查了三遍。"
    n "发送到她的邮箱。凌晨十二点零四分。"
    n "凌晨十二点十一分，我的手机响了。"
    play sound sfx_call
    show lxx cold at right_stage
    with dissolve
    lx "第三条证据，那个厕所的地址，发我定位。"
    p "……李总，您还没睡？"
    lx "我在看你的备忘录。"
    lx "第二段第三行，「高度疑似」改成「疑似」。没有实锤的东西，不要加程度副词。"
    p "好。"
    n "沉默。"
    show lxx smile at right_stage
    lx "……格式是对的。"
    lx "你还记得。"
    play sound sfx_heart
    pt "……她在电话那头，好像笑了一下。"
    pt "很短。短到我不确定。"
    $ love("lxx", 12)
    $ stat("sincere", 5)
    jump ch5_meeting


label ch5_pitch_snack:
    scene bg street_food_night
    with dissolve
    play music bgm_city_date fadein 0.5
    show pzk delivery normal at left_stage
    with dissolve
    n "凌晨十二点，我在巷子口的煎饼摊买了两个煎饼。"
    n "一个加两个蛋。一个加三个蛋。"
    p "系统。这个，给她的。"
    call sys_audit("煎饼果子 ×1（加三个蛋）", 12, "攻略对象夜宵", "approved", "李轩翔吃你的早餐了。审核通过。另：检测到宿主用自己的钱给自己买了一个，系统表示欣慰。")
    pt "……她吃我的早餐了。"
    pt "等等，现在是半夜。"
    xt cry_laugh "夜宵也是早餐。从时区上讲。"

    scene bg ib_office_night
    with dissolve
    show lxx tired at right_stage
    show pzk delivery normal at left_stage
    with dissolve
    play sound sfx_knock
    lx "我没点外卖。"
    p "不是外卖。是证据。"
    p "顺便……是夜宵。"
    n "我把煎饼放在她桌上，然后把手机里的截图一张一张给她看。"
    n "零米订单。幽灵骑手。厕所门口的「金牌黄焖鸡」。"
    show lxx cold at right_stage
    n "她看得很快。看完以后，拿起了煎饼。"
    n "咬了一口。"
    show lxx surprised at right_stage
    lx "……三个蛋？"
    p "您以前加班，最晚的那几天会让我下楼买。三个蛋，不要香菜。"
    show lxx blush at right_stage
    n "她低头又咬了一口，没看我。"
    lx "……你记这个干什么。"
    lx "这种记性，你当年要是用在模型上——"
    p "折现率就不会填反了。"
    show lxx tongue at right_stage
    play sound sfx_boing
    n "她冲我吐了一下舌头。"
    n "快得像幻觉。"
    show lxx cold at right_stage
    n "下一秒，她已经低头看文件了，好像什么都没发生。"
    pt "……我刚才看到了什么。"
    pt "全行最年轻的MD，对一个外卖员，吐舌头？"
    xt evil_grin "已截图。"
    pt "你还能截图？？"
    xt soul_leave "仅供系统内部存档。宿主无权查看。"
    $ love("lxx", 10)
    $ stat("sincere", 5)
    jump ch5_meeting


## ---------------------------------------------------------------------------
## 会议：二十分钟
## ---------------------------------------------------------------------------

label ch5_meeting:
    stop music fadeout 1.0
    scene bg meeting_room
    with fade
    play music bgm_office fadein 1.0

    n "两天后。"
    n "她派了一个小组，凌晨三点去了二十个站点。"
    n "账上的骑手是一万四千人。实际清点到的，是五千一百人。"
    n "那天下午，她给我打了个电话。"
    lx "明天上午十点，会议室。张总要听骑手端的说法。"
    lx "穿得像个人。"

    show lxx cold at right_stage
    with dissolve
    if lxx_suit:
        show pzk rentsuit normal at left_stage
        with dissolve
        n "我穿着那套系统批准的租赁西装。"
        n "袖子短一截。一抬手就露出手腕。"
        show lxx speechless at right_stage
        lx "……你的袖子。"
        show pzk rentsuit awkward at left_stage
        p "这叫九分袖。今年流行。"
    else:
        show pzk delivery normal at left_stage
        with dissolve
        n "我没有西装。我穿着洗干净的外卖制服。"
        lx "我说穿得像个人。"
        p "我现在就是一个人。一个外卖员。"
        show lxx cold at right_stage
        n "她看了我两秒，没再说什么。"

    boss_zhang "就是他？外卖员？"
    boss_zhang "轩翔，你拿一个外卖员的话，来卡一个几十亿的项目？"
    show lxx cold at right_stage
    lx "我拿的是数据。他是数据的来源。"
    lx "潘子恺。二十分钟。"
    pt "二十分钟。她的会议时长上限。"
    pt "我以前在她手下开会，从来没有一次在二十分钟内讲完过。"

    menu:
        "怎么讲？"

        "结论先行。三条证据。五分钟讲完，剩下的时间留给提问":
            $ lxx_meeting_style = "concise"
            if lxx_suit:
                show pzk rentsuit proud at left_stage
            else:
                show pzk delivery proud at left_stage
            n "我站起来。"
            p "结论：岛团外卖的活跃骑手数虚增约百分之六十四，订单量中存在规模化的自刷单。"
            p "三条证据。第一，凌晨零米订单……"
            n "我讲了四分五十秒。"
            n "没有一个形容词。没有一句「我以前在岛上开兰博基尼送外卖」。"
            n "讲完，我坐下。"
            n "会议室安静了很久。"
            boss_zhang "……你以前是干什么的？"
            p "分析师。她手下的。"
            show lxx smile at right_stage
            n "李轩翔在桌子另一头，低头在文件上写了两个字。"
            n "我后来才知道，那两个字是——"
            lx "「可以。」"
            play sound sfx_heart
            pt "……"
            pt "四年了。"
            pt "我第二次收到这个评价。"
            $ love("lxx", 10)
            $ stat("sincere", 5)

        "这是我的高光时刻！讲一讲我从亿万富翁到外卖员的心路历程":
            $ lxx_meeting_style = "show"
            if lxx_suit:
                show pzk rentsuit proud at left_stage
            else:
                show pzk delivery proud at left_stage
            n "我站起来。"
            p "各位。在讲数据之前，我想先讲一个故事。"
            p "一个关于财富、背叛、和一辆蓝色兰博基尼的故事——"
            show lxx angry at right_stage
            n "第十二分钟，我讲到了海岛。"
            n "第十八分钟，我讲到了仙人跳。"
            n "第十九分钟，我还没讲到数据。"
            play sound sfx_sad
            lx "时间到。"
            n "她站起来，接过我的电脑，用三分钟把三条证据讲完了。"
            n "讲得比我好。"
            boss_zhang "……轩翔，你这个外卖员，挺能说啊。"
            show lxx cold at right_stage
            lx "他的数据是真的。他的故事是废话。"
            $ stat("zb", 10)
            $ love("lxx", 2)

    boss_zhang "……行。项目暂停。补充尽调。"
    n "张总说完就走了。走的时候，看了李轩翔一眼。"
    n "那一眼不太友好。"

    $ complete_task("lxx_2")
    $ set_stage("lxx", "并肩作战")
    $ credit_limit = 8000
    xt rage_scream "攻略进度提升。纯爱卡额度提升至八千元。"
    $ add_note("lxx", "她叫停了一个几十亿的项目。张总不太高兴。")

    jump ch5_arcade


## ---------------------------------------------------------------------------
## 凌晨两点：抓娃娃店（隐藏任务）
## ---------------------------------------------------------------------------

label ch5_arcade:
    stop music fadeout 1.0
    scene bg city_street_night
    with fade
    play ambient sfx_city fadein 1.0 volume 0.3

    n "项目暂停之后的第三天，凌晨一点五十。"
    play sound sfx_phone
    show screen phone_notice("岛团外卖 · 新订单", "矿泉水 ×1 → 二十四小时抓娃娃店\n备注：放在第三排第七台机器旁边。别说话。")
    pause 0.3
    hide screen phone_notice
    show pzk delivery normal at center_stage
    with dissolve
    pt "又是这种备注。"
    pt "我这辈子跟奇怪的备注有缘。"

    stop ambient fadeout 1.0
    scene bg arcade_night
    with fade
    play music bgm_lxx_soft fadein 1.5
    play sound sfx_claw

    n "凌晨两点的抓娃娃店，只有一个客人。"
    n "红色皮衣。宽松的灰色牛仔裤。金色短发乱糟糟的，还戴着那副无框的茶色眼镜。"
    pt "那件皮衣。四年了，她还在穿。"
    n "她站在第三排第七台机器前，盯着里面的一只粉色猫猫娃娃。"
    n "表情跟她在会议室里看财务报表时一模一样。"

    show lxx casual cold at right_stage
    with dissolve
    show pzk delivery shock at left_stage
    with dissolve
    pt "……李轩翔？？"
    pt "凌晨两点、在抓娃娃店里的李轩翔？？"
    pt "这比我破产还不真实。"

    n "她没看我。伸手。"
    n "我把水放在她手里。"
    lx "别说话。"
    lx "这台机器有保夹机制。前面抓力弱，到一定次数会给一次强抓。"
    lx "我已经抓了二百三十六次。根据前面的规律，强抓应该在第二百四十次左右。"
    p "您……从几点开始抓的？"
    lx "十一点。"
    p "……三个小时？"
    lx "两小时五十分钟。不要四舍五入。"

    menu:
        "……"

        "「我来帮你！」——我抓娃娃也是一绝":
            $ lxx_claw = "help"
            show pzk delivery smug at left_stage
            p "我来！"
            p "我抓娃娃也是一绝。以前在岛上——"
            play sound sfx_claw
            n "第二百三十七次。我抓的。"
            n "爪子在猫猫头上摸了一下，像是在跟它打招呼。然后空着回来了。"
            show lxx casual cold at right_stage
            lx "你浪费了我一次。"
            p "那还剩三次就到第二百四十次了。我等于帮你推进了进度。"
            show lxx casual smile at right_stage
            lx "……这个逻辑，我竟然无法反驳。"
            $ love("lxx", 4)

        "什么都不说，站在旁边陪她":
            $ lxx_claw = "company"
            show pzk delivery normal at left_stage
            n "我什么都没说。"
            n "我在她旁边站着，看她抓。"
            play sound sfx_claw
            n "第二百三十七次。第二百三十八次。"
            n "她抓的时候很专注，嘴唇抿着。抓空的时候，会很轻地「啧」一声。"
            n "我从来不知道她会「啧」。"
            $ love("lxx", 7)
            $ stat("sincere", 5)

        "「李总也会输？」":
            $ lxx_claw = "tease"
            show pzk delivery proud at left_stage
            p "李总也会输啊？"
            show lxx casual cold at right_stage
            n "她转过头，透过镜片看了我一眼。"
            lx "我没输。我在建模。"
            lx "你当年做模型的时候，也是在输？"
            p "……那个确实是在输。"
            $ love("lxx", 3)

    call sys_audit("抓娃娃币 ×30", 30, "陪伴攻略对象", "approved", "符合攻略目的。另：系统提醒宿主，她已经在这台机器上花了七百零八块，建议不要提这个数字。")

    play sound sfx_claw
    n "第二百三十九次。"
    play sound sfx_claw
    n "第二百四十次。"
    scene cg claw_machine
    with flash
    n "爪子抓得很稳。"
    n "猫猫被提起来，晃了晃，慢慢地移向出口。"
    n "掉了下去。"
    play sound sfx_stat_up
    n "她蹲下去，从出口把它拿出来，抱在怀里。"
    n "那是我认识她以来，第一次看到她笑得像个……"
    n "像个三十一岁的普通女人。"

    scene bg arcade_night
    with dissolve
    show lxx casual smile at right_stage
    show pzk delivery normal at left_stage
    with dissolve

    lx "第二百四十次。误差为零。"
    lx "它长得像我家的猫。"
    p "您养猫？"
    lx "嗯。叫「止损」。"
    p "……"
    pt "谁会给猫起名叫止损啊。"
    p "您刚才抓到的时候，笑得像个小孩。"
    show lxx casual tongue at right_stage
    play sound sfx_boing
    lx "略。"
    show pzk delivery shock at left_stage
    pt "……她说了「略」。"
    pt "那个开会不许超过二十分钟、PPT 错一个标点就打回重做的李轩翔，说了「略」。"
    show lxx casual cold at right_stage
    if lxx_honest_reunion:
        lx "你要是敢告诉赵磊，明天全行都会知道你在岛上被仙人跳的事。"
        show pzk delivery awkward at left_stage
        p "那是我跟您说的秘密！"
        lx "所以我们扯平了。"
    else:
        lx "你要是敢告诉赵磊，明天全行都会知道你当年把折现率填反的事。"
        show pzk delivery awkward at left_stage
        p "那都四年前了！"
        lx "风控部门的记忆是永久的。"
    p "您这建模能力，用来抓娃娃可惜了。"
    show lxx casual cold at right_stage
    lx "我只在这里建模不用对任何人负责。"

    n "我们在店门口的长椅上坐下。"
    n "她抱着猫猫。我抱着外卖箱。"

    p "您……经常来这里？"
    lx "睡不着的时候。"
    p "最近经常睡不着？"
    lx "从我在会议室里说「暂停」那天开始。"
    show lxx casual cold at right_stage
    lx "全组的人都看着我。好像我把他们的年终奖撕了。"
    lx "张总说我「不懂得团队利益」。"
    lx "我当然懂。我只是不想在一份我知道是假的报告上签字。"
    n "她停了一下。"
    lx "……其实我也怕。"
    lx "我三十一岁。做到这个位置，不是因为我不怕。"
    lx "是因为我怕的时候，没有人看得出来。"

    play sound sfx_heart
    pt "我坐在她旁边，突然不知道该说什么。"
    pt "以前的我，这时候会说一句漂亮话。"
    pt "我想了很多句。每一句都很漂亮。"

    menu:
        "……"

        "「我看出来了。」":
            p "我看出来了。"
            show lxx casual surprised at right_stage
            lx "……什么？"
            p "您怕的时候，会把笔放得很慢。"
            p "那天我冲进——不对，那天会上，您放笔的时候，放得很慢。"
            show lxx casual blush at right_stage
            n "她转过头看着我。没说话。"
            n "然后把脸埋进了猫猫里。"
            $ love("lxx", 8)
            $ stat("sincere", 5)

        "「以后您睡不着，可以点外卖。我接单。」":
            p "以后您睡不着，可以点外卖。"
            p "我接单。"
            show lxx casual smile at right_stage
            lx "你不怕超时？"
            p "怕。但您是五星顾客。"
            lx "……嗯。"
            $ love("lxx", 6)

        "说一句漂亮话":
            show pzk delivery proud at left_stage
            p "怕什么。有我在。"
            show lxx casual cold at right_stage
            n "她看了我一眼。"
            lx "你连自己都没守住。"
            show pzk delivery gloom at left_stage
            n "……这句话说得很轻。但很准。"
            $ love("lxx", 1)

    n "过了一会儿，她不说话了。"
    n "我转头。"
    n "她靠在我肩膀上，睡着了。抱着猫猫，眼镜歪在一边。"

    show pzk delivery sealed at left_stage
    call seal_alarm()
    pt "我这次真的什么都没想。"
    pt "真的。"
    xt soul_leave "系统知道。"
    xt idle "所以这次，只是例行提示。"
    pt "……"
    pt "这个系统，好像比我先一步知道，我在想什么。"

    show pzk delivery normal at left_stage
    n "她在梦里嘟囔了一句。"
    lx "……四年前那件事……"
    lx "……你以为……是怎么过去的……"
    n "然后她就彻底睡着了。"
    pt "四年前那件事？"
    pt "哪件事？"
    n "我想了很久。想到天快亮了，也没想明白。"

    if lxx_claw == "company" or targets["lxx"]["aff"] >= 40:
        $ lxx_shark = True
        n "她醒来的时候，天已经蒙蒙亮了。"
        show lxx casual blush at right_stage
        lx "……我睡了多久？"
        p "四十分钟。误差为零。"
        n "她站起来，把猫猫塞进我怀里。"
        lx "给你。"
        p "您抓了二百四十次——"
        lx "所以送给你。"
        lx "便宜的东西，我不送人。"
        $ add_note("lxx", "她送了你一只抓了 240 次的猫猫娃娃。")
    else:
        n "她醒来的时候，天已经蒙蒙亮了。"
        show lxx casual cold at right_stage
        lx "……刚才的事，不许跟任何人说。"
        p "什么事？"
        lx "很好。"

    $ task("lxx_3")["title"] = "看见她不为人知的一面"
    $ complete_task("lxx_3")
    $ set_stage("lxx", "她的另一面")
    $ add_note("lxx", "她睡不着的时候会去抓娃娃。怕的时候，会把笔放得很慢。")

    jump ch5_end


## ---------------------------------------------------------------------------
## 章末：结算 & 伏笔
## ---------------------------------------------------------------------------

label ch5_end:
    stop music fadeout 2.0
    scene bg rental_room
    with fade
    play music bgm_system fadein 1.0
    show pzk delivery normal at left_stage
    with dissolve

    n "回到出租屋，早上七点。"
    if lxx_shark:
        if got_sea_glass:
            n "我把猫猫放在枕头边。旁边是那块海玻璃。"
        else:
            n "我把猫猫放在枕头边。旁边是那张写着K的便签纸。"
        n "我的枕头边，越来越像一个失物招领处了。"

    xt grimace "阶段结算。"
    call screen target_card("lxx")

    $ _aff = targets["lxx"]["aff"]
    if _aff >= 45:
        xt cry_laugh "当前好感度：[_aff]%%。宿主表现超出系统预期。"
        xt mock_laugh "系统原本预估，宿主会在第三天被保安列入黑名单。"
    elif _aff >= 30:
        xt side_eye "当前好感度：[_aff]%%。进度正常。"
        xt evil_grin "距离解除封印还有很长的路。距离一千万也是。"
    else:
        xt eyeroll "当前好感度：[_aff]%%。宿主的装逼行为对攻略造成了显著拖累。"
        xt jaw_drop "建议宿主少讲故事，多讲数据。"

    p "系统。"
    p "我问你个事。"
    p "她最后说的那句话。四年前那件事。你知道是什么吗？"
    xt eyeroll "知道。"
    p "告诉我。"
    xt side_eye "不能。"
    xt eyeroll "那是她的事。等她愿意告诉你的时候，你自然会知道。"
    xt cry_laugh "本系统不剧透。"
    pt "……一个不剧透的系统。"
    pt "我竟然有点感动。"

    $ add_task("lxx_4", "lxx", "和她吃一顿不是工作餐的饭", "没有议程。没有 PPT。没有二十分钟。", 30000)

    p "没有议程的饭……"
    p "上一个跟她说「没有议程，就是吃饭」的MD，被她拒绝了。"
    xt evil_grin "所以这是任务。不是福利。"

    stop music fadeout 1.0
    play sound sfx_call
    scene bg ib_office_night
    with dissolve
    show lxx cold at right_stage
    with dissolve
    n "同一时间，四十八楼。"
    n "——这是后来赵磊告诉我的。"
    boss_zhang "轩翔，下周的晚宴你必须来。"
    boss_zhang "沈眠点名要见你。还有——那个外卖员顾问。"
    show lxx surprised at right_stage
    lx "沈眠？"
    boss_zhang "她听说有个外卖员掀了岛团的底，很感兴趣。"
    n "李轩翔挂了电话，在窗边站了很久。"
    hide lxx with dissolve

    scene bg city_street_night
    with fade
    play ambient sfx_city fadein 1.0 volume 0.3
    show pzk delivery normal at center_stage
    with dissolve
    n "而我，在那天晚上十一点，接到了一个订单。"
    play sound sfx_phone
    show screen phone_notice("岛团外卖 · 新订单", "冰椰子水 ×1 → 半岛酒店 1708\n备注：放在黑色高跟鞋旁边就行。")
    pause 0.5
    play sound sfx_sting
    show pzk delivery shock at center_stage, shake
    p "……"
    hide screen phone_notice
    pt "黑色高跟鞋。"
    pt "冰椰子水。"
    pt "这座城市里，不会有第二个人这么点单。"

    stop ambient fadeout 2.0
    scene bg black
    with fade
    tip "—— 第四章 完 ——"
    jump chapter6
