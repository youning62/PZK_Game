## Chapter1.rpy —— 第一章 · 第一话「梦里的女人」
##
## 流程：梦境冲浪 → 海景别墅醒来 → 车库 → 兰博基尼送外卖（三单）→ 海滩初遇 → 三秒挑战 → 晚餐邀约

label chapter1:
    stop music fadeout 1.0
    scene bg black
    call screen chapter_card("第一章 · 第一话", "梦里的女人")

    jump ch1_dream


## ---------------------------------------------------------------------------
## 梦境
## ---------------------------------------------------------------------------

label ch1_dream:
    play music bgm_dream fadein 2.0
    play ambient sfx_waves fadein 2.0
    scene bg dream_beach
    with dream_fade

    n "那一天，海浪为我让路。"
    n "准确地说，是海浪排着队，等我挑。"

    scene cg dream_surf at slow_zoom
    with flash
    play sound sfx_splash

    n "我踩着冲浪板，从三米高的浪尖上切下来。"
    n "水花在我身后炸开，像给我放的烟花。"
    n "阳光很懂事，专门打在我的腹肌上。"

    girl1 "啊啊啊啊——好帅！"
    girl2 "他的腹肌是不是P上去的？"
    girl1 "海里怎么P？？"
    girl2 "……那就是真的？？"

    n "我没有回头。"
    n "真正的帅哥，从不回头看尖叫声。"
    n "只在心里默默数：今天第三百二十一声。"

    scene bg dream_beach
    with dissolve
    show pzk surf normal at left_stage, dream_float
    with dissolve

    n "我滑上浅滩，甩了甩头发上的海水。"
    n "人群自动分开一条路。"

    show yyl silhouette at right_stage
    with dissolve

    n "一个女人从路的尽头走过来。"
    n "高挑，长腿，走在沙子上像走在T台上。"

    show yyl calm at right_stage
    with dissolve
    play sound sfx_heart

    n "她在我面前停下，晃了晃手机。"
    y "可以加你微信吗？"

    pt "来了。今天的第一百零八个。"

    menu:
        "怎么拒绝她比较帅？"

        "「不好意思，先去后面排队。」":
            $ dream_reply = "queue"
            show pzk surf laugh at left_stage
            p "不好意思。"
            p "先去后面排队。"
            n "我抬手一指。"
            n "她身后，排队加我微信的人一直排到了海平线。"
            n "队尾有人在发号码牌。"
            show yyl rage at right_stage
            play sound sfx_shock
            n "她看着那条队，额头上的青筋跳了一下，头顶开始冒烟。"

        "「微信？我只加有缘人。你先跟这片海聊聊。」":
            $ dream_reply = "sea"
            show pzk surf laugh at left_stage
            p "微信？"
            p "我只加有缘人。"
            p "你先跟这片海聊聊，它同意了，我再考虑。"
            n "大海适时地拍了一个浪，表示拒绝。"
            show yyl derp at right_stage
            play sound sfx_boing
            n "她鼓起腮帮子，眼睛对成了斗鸡眼。"
            n "梦里的女人，表情包都这么丰富。"

        "「我没有微信。我只有私人飞机的塔台频率。」":
            $ dream_reply = "tower"
            show pzk surf laugh at left_stage
            p "我没有微信。"
            p "我只有私人飞机的塔台频率。"
            p "118.6，记得报暗号。"
            n "她身后有个女孩当场开始学航空无线电。"
            show yyl brain_lag at right_stage
            n "她本人歪着嘴、摸着下巴，两只眼睛各看一个方向。"
            n "我怀疑她的大脑在重启。"

    $ stat("zb", 5)

    show yyl smile at right_stage
    show yyl waterfall_cry at right_stage, shake
    play sound sfx_sad
    n "下一秒，她哭了。"
    n "不是普通的哭。是两道瀑布，外加一个鼻涕泡。"
    pt "梦里的我，杀伤力就是这么大。"
    show yyl calm at right_stage
    n "然后眼泪像倒放的视频一样，嗖地缩了回去。"
    n "奇怪的是，她并没有失望。"
    n "她只是笑了一下，好像早就知道我会这么说。"
    y "好。"
    y "那下次——"
    play sound sfx_heart
    y "换你来找我。"

    pt "……嗯？"
    pt "这台词不对吧？剧本里你应该哭着跑开才对。"

    hide yyl with dissolve
    show pzk surf laugh at center_stage
    with move
    p "嘿嘿。"
    show pzk surf damn at closeup
    with qdissolve
    p "嘿嘿嘿嘿嘿。"
    p "傻女人，还想认识我——"

    stop music fadeout 1.5
    stop ambient fadeout 1.5
    scene bg white
    with dream_fade
    jump ch1_wakeup


## ---------------------------------------------------------------------------
## 醒来
## ---------------------------------------------------------------------------

label ch1_wakeup:
    scene bg black
    play sound sfx_alarm
    n "嘀嘀嘀——嘀嘀嘀——"
    n "嘿嘿嘿嘿……"
    n "嘀嘀嘀嘀嘀嘀嘀——"

    play sound sfx_wakeup
    scene bg villa_bedroom
    with fade
    play ambient sfx_waves fadein 3.0 volume 0.5

    p "……草。"
    p "梦？"

    n "我坐在床上，盯着落地窗外的海发了三分钟呆。"
    n "海很蓝。床很大。枕头上有我的口水。"
    n "一切都很正常，除了梦里那个女人最后那句话。"

    pt "「下次，换你来找我。」"
    pt "什么意思？梦还有续集？"
    pt "……算了。梦里的女人而已。"
    pt "我潘子恺现实中的女人都看不过来，哪有空看梦里的。"

    n "说是这么说，我还是下意识摸了摸自己的脸。"
    p "嗯……还在。"
    p "帅还在。"

    n "我掀开被子，光脚走到镜子前。"
    n "这是我每天早上最重要的仪式。"

    play music bgm_luxury fadein 1.0
    show pzk casual normal at mirror_view
    with dissolve
    play sound sfx_mirror

    n "镜子里，一个完美的男人出现了。"

    menu:
        "今天对镜子做点什么？"

        "秀一下二头肌":
            $ mirror_pose = "flex"
            show pzk casual smug at mirror_view
            with qdissolve
            play sound sfx_sparkle
            p "这腹肌，这胸肌，这二头，这脸……"
            p "女娲捏我的时候是不是开了会员？"
            n "镜子沉默着，大概是被我帅到失语了。"
            $ stat("zb", 5)

        "深情凝视自己的眼睛":
            $ mirror_pose = "gaze"
            show pzk casual narcissist at mirror_view
            with qdissolve
            play sound sfx_sparkle
            p "潘子恺啊潘子恺。"
            p "你这辈子最大的缺点，就是找不到自己的缺点。"
            n "我和镜子里的自己对视了整整一分钟。"
            n "最后是他先眨的眼。我赢了。"
            $ stat("zb", 5)

        "仔细检查脸上有没有长痘":
            $ mirror_pose = "pimple"
            show pzk casual shock at mirror_view, shake
            play sound sfx_shock
            p "……？？？"
            p "下巴上这是什么？"
            p "一颗痘？？"
            n "我当场决定取消今天的所有行程。"
            show pzk casual normal at mirror_view
            n "三秒后，我又决定恢复所有行程。"
            p "算了。痘也是帅的一部分。"
            p "就像维纳斯的断臂。"
            $ stat("sincere", 3)

    hide pzk with dissolve

    n "仪式结束，我拿起手机。"
    show phone time at phone_pos
    with dissolve
    n "2066年6月6日，星期五，上午九点。"
    n "早上醒来先看余额，是我多年来坚持的好习惯。"
    n "就像别人醒来先喝一杯温水。"
    show phone money at phone_pos
    with dissolve
    play sound sfx_cash
    n "嗯。"
    n "逗号还在。"
    n "我数了一下，四个。"
    n "钱这种东西，你不管它，它自己会长。跟头发一样。"
    n "当年押对了几只股票，后来就财富自由了。"
    n "听起来很爽。实际上——"
    n "实际上也确实很爽。"
    hide phone with dissolve

    play sound sfx_phone
    show screen phone_notice("微信 · 妈", "儿子，岛上玩得开心吗？别又去送外卖了，你王阿姨说在朋友圈刷到你了。")
    pause 0.3
    p "……"
    p "王阿姨的朋友圈怎么什么都有。"
    hide screen phone_notice

    n "我回了个「收到」，然后熄屏。"
    n "收到的意思是，我收到了，但我不改。"

    p "好。今天的任务很明确。"
    p "别人来海岛度假是为了放松。"
    p "我来海岛度假，是为了给当地人民提供视觉福利。"
    p "出门。祸害世界。"

    jump ch1_garage


## ---------------------------------------------------------------------------
## 车库
## ---------------------------------------------------------------------------

label ch1_garage:
    stop ambient fadeout 1.0
    scene bg garage
    with fade
    play sound sfx_door

    n "别墅的车库里停着我的老婆。"
    n "……不是，是我的车。蓝色兰博基尼。"
    n "我叫它「小蓝」。"
    n "小蓝很漂亮，很快，很贵，从来不跟我吵架。"
    n "唯一的缺点是后备箱只装得下一个外卖箱。"

    show pzk delivery proud at center_stage
    with dissolve
    play sound sfx_sparkle

    n "没错。"
    n "我潘子恺，身价一万亿美元以上，开兰博基尼，送外卖。"

    p "很多人问我为什么。"
    p "别人开兰博基尼是为了泡妞。"
    p "我开兰博基尼，是为了让顾客的外卖拥有超跑级配送体验。"

    pt "……其实真正的原因是太无聊了。"
    pt "钱多到一定程度，每天都像同一天。"
    pt "但送外卖不一样。每一单都不知道门后是谁。"

    show pzk delivery happy at center_stage
    p "而且送外卖有钱拿。"
    p "自己挣的钱，那能一样吗？"

    play sound sfx_engine
    n "引擎点火。小蓝发出一声满足的咆哮。"
    play sound sfx_phone
    app "骑手「潘师傅」上线成功！今日已为您匹配附近订单，祝您配送愉快～"

    jump ch1_delivery_1


## ---------------------------------------------------------------------------
## 外卖一：度假酒店 · 网红
## ---------------------------------------------------------------------------

label ch1_delivery_1:
    play music bgm_delivery fadein 0.5
    scene bg coast_road
    with wipeleft
    play sound sfx_drive

    n "第一单：豪华度假酒店，冰美式一杯。"
    n "距离四公里。预计送达：二十分钟。"
    n "我用了四分钟。"
    n "其中三分钟在等红绿灯。"

    scene bg resort_hotel
    with dissolve
    play sound sfx_doorbell

    show pzk delivery normal at left_stage
    with dissolve

    n "酒店门口，下单的顾客已经在等了。"
    n "一位举着自拍杆的网红小姐姐，看到小蓝的瞬间，眼睛亮得像补光灯。"

    influencer "哇——等等等等，你别动！"
    influencer "兰博基尼送外卖？？这是什么新型营销？"
    influencer "你是哪家MCN的？带货吗？"

    menu:
        "怎么回应她？"

        "「我不是网红。我是真有钱。」":
            show pzk delivery proud at left_stage
            p "我不是网红。"
            p "我是真有钱。"
            influencer "懂，懂。人设嘛。"
            influencer "现在「真有钱」人设很卷的，你这个车是租的吧？一天多少？"
            show pzk delivery awkward at left_stage
            p "……全款。"
            influencer "好的好的，全款人设。"
            n "她给了我一星。"
            n "评价：「外卖员比我还能装。」"
            $ delivery_rating -= 1
            $ stat("zb", 5)

        "「您的冰美式，祝您用餐愉快。」":
            show pzk delivery normal at left_stage
            p "您的冰美式。"
            p "少冰，不加糖。祝您用餐愉快。"
            influencer "……啊？就这样？"
            influencer "你不拍点什么吗？"
            p "不了，下一单要超时了。"
            n "我转身上车，留下她一个人在原地怀疑人生。"
            n "她给了我五星。"
            n "评价：「骑手很专业，就是车有点浮夸。」"
            $ delivery_rating += 1
            $ delivery_income += 3
            $ stat("sincere", 5)

        "「要合影吗？一张五块。」":
            $ took_photo = True
            show pzk delivery happy at left_stage
            p "要合影吗？"
            p "一张五块，跟车十块。"
            influencer "……成交！"
            play sound sfx_cash
            n "她拍了十二张。我比了十二个耶。"
            n "收入一百二十元，外加配送费三元。"
            n "这是我这个月在外卖事业上最大的一笔进账。"
            $ delivery_income += 123
            $ stat("zb", 3)

    jump ch1_delivery_2


## ---------------------------------------------------------------------------
## 外卖二：海滨商业街 · 椰子鸡阿姨
## ---------------------------------------------------------------------------

label ch1_delivery_2:
    scene bg shopping_street
    with wipeleft
    play sound sfx_drive

    n "第二单：海滨商业街，椰子鸡一份。"
    n "下单人：一位开纪念品店的阿姨。"

    show pzk delivery normal at left_stage
    with dissolve

    auntie "小伙子，你的车……"
    p "嗯？"
    auntie "还要还多少年啊？"
    p "？"

    auntie "阿姨跟你说，年轻人不要打肿脸充胖子。"
    auntie "车贷压力大，你还出来跑外卖，阿姨懂的。"
    auntie "我侄子也是，贷款买了个宝马，现在天天吃泡面。"

    menu:
        "怎么回应阿姨？"

        "「阿姨，这车是全款。」":
            show pzk delivery proud at left_stage
            p "阿姨，这车是全款买的。"
            auntie "全款？"
            auntie "那更惨了。全部家当都在车上了是吧。"
            show pzk delivery awkward at left_stage
            p "不是，我还有——"
            auntie "别说了，阿姨都懂。"

        "「……阿姨说得对。」":
            show pzk delivery normal at left_stage
            p "……阿姨说得对。"
            p "我会努力的。"
            auntie "这就对了嘛！知道努力就好！"
            n "阿姨欣慰地拍了拍我的肩膀，像在拍一个迷途知返的侄子。"
            $ stat("sincere", 3)

    play sound sfx_cash
    n "最后，阿姨塞给我五块钱小费。"
    n "还有一个开好口的椰子。"
    auntie "拿着，跑外卖辛苦，路上喝。"

    show pzk delivery happy at left_stage
    n "我捧着椰子，站在商业街上，半天没说出话。"
    pt "五块钱。"
    pt "我这辈子收过最贵的礼物，不是我十八岁那年那块表。"
    pt "是这五块钱。"

    $ delivery_income += 8

    jump ch1_delivery_3


## ---------------------------------------------------------------------------
## 外卖三：海滩 · Y女士
## ---------------------------------------------------------------------------

label ch1_delivery_3:
    play sound sfx_phone
    app "您有新的订单！"
    show screen phone_notice("岛团外卖 · 新订单", "冰椰子水 ×1 → 冲浪海滩 3号救生塔\n备注：放在黑色高跟鞋旁边就行，人在海里。—— Y女士")
    pause 0.3

    show pzk delivery normal at left_stage
    p "……高跟鞋？"
    p "来海边冲浪，带高跟鞋？"
    hide screen phone_notice

    pt "这是什么人？冲浪运动员还是走秀模特？"
    pt "而且我手上正好有个椰子……"
    pt "不行，职业操守。阿姨给的椰子是阿姨给的，订单的椰子要另外买。"

    n "我在路边摊买了一个冰椰子。"
    n "然后把阿姨的椰子放在副驾上，系好了安全带。"

    stop music fadeout 1.5
    jump ch1_beach


## ---------------------------------------------------------------------------
## 海滩 · 她在冲浪
## ---------------------------------------------------------------------------

label ch1_beach:
    scene bg beach_day
    with fade
    play ambient sfx_waves fadein 1.0
    play music bgm_island fadein 2.0

    n "冲浪海滩。"
    n "阳光、白沙、棕榈树，还有一群在浅滩里扑腾的游客。"
    n "我把小蓝停在路边一个很宽敞、很显眼、空无一车的位置。"
    pt "奇怪，这么好的车位怎么没人停。"

    play sound sfx_steps
    show pzk delivery normal at left_stage
    with dissolve

    n "3号救生塔下面，果然放着一双黑色高跟鞋。"
    n "鞋跟又细又高，摆得整整齐齐，旁边是一个冲浪板包。"
    n "鞋的主人，不在岸上。"

    p "人在海里……"

    n "我抬起头。"

    stop music fadeout 0.5
    play music bgm_heroine fadein 0.5
    scene cg yyl_surf
    with flash
    play sound sfx_splash

    n "远处，一道浪正在升起来。"
    n "一个身影在浪的最高点站了起来。"
    n "不是那种游客式的「站起来」，是那种——"
    n "浪是她家的，她回自己家。"
    n "她压低身体，板头一转，切进浪壁里，水花在她身后拉出一条白线。"
    n "整个海滩的人都停下来看她。"
    n "包括我。"

    play sound sfx_heart
    n "然后，我看清了她的脸。"

    p "……"
    p "等等。"
    p "这张脸。"

    play sound sfx_shock
    scene bg beach_day
    with qdissolve
    show pzk delivery awkward at left_stage, shake
    play music bgm_tension fadein 0.5

    p "卧槽？？"
    p "梦里那个找我要微信的女人？？？"

    pt "冷静。潘子恺。"
    pt "世界上长得像的人很多。比如我和吴彦祖。"
    pt "……虽然我比他帅一点。"

    pt "但如果这是预知梦呢？"
    pt "梦里是我冲浪，她来找我。"
    pt "那现实里……"
    show pzk delivery proud at left_stage
    pt "那现实里，她马上就要冲上岸，红着脸问我要微信了。"
    pt "完美。剧本我已经看过了。"
    pt "我只需要——站在这里，等着被搭讪。"

    menu:
        "等她上岸的时候，做点什么？"

        "靠在救生塔上，摆一个看海的帅气姿势":
            $ wait_style = "pose"
            show pzk delivery proud at left_stage
            n "我侧身靠在救生塔的柱子上，单手插兜，四十五度角望向大海。"
            n "这个姿势我在镜子前练过，从这个角度看，我的下颌线能切菜。"
            n "我保持了五分钟。"
            n "中途有个救生员下来问我是不是中暑了。"
            $ stat("zb", 5)

        "当场做二十个俯卧撑，展示一下肌肉":
            $ wait_style = "pushup"
            show pzk delivery proud at left_stage
            n "我把外卖箱放下，在沙滩上趴下。"
            n "一、二、三……"
            n "做到第十五个的时候，旁边围了一圈小朋友帮我数。"
            n "……十九、二十！"
            n "小朋友们鼓掌。一个小男孩给了我一块饼干。"
            $ stat("zb", 10)

        "老老实实等着，顺便给椰子插好吸管":
            $ wait_style = "straw"
            show pzk delivery normal at left_stage
            n "我决定专业一点。"
            n "顾客冲完浪，口渴，应该第一时间喝到椰子水。"
            n "我把吸管插进椰子。"
            n "没插进去。"
            n "第二次，插歪了。"
            n "第三次，成功了，溅了我一脸椰子水。"
            $ stat("sincere", 5)

    jump ch1_collision


## ---------------------------------------------------------------------------
## 意外相识
## ---------------------------------------------------------------------------

label ch1_collision:
    stop music fadeout 1.0
    play sound sfx_splash
    n "她冲上浅滩，拎着冲浪板走上岸。"
    n "她朝救生塔走来。也就是，朝我走来。"
    play sound sfx_heart
    pt "来了来了来了。"
    pt "按照剧本，她会先害羞地低头，然后——"

    show pzk delivery proud at left_stage
    p "你好，你的外卖——"

    n "我迈出了自认为人生中最帅的一步。"
    n "左脚精准地踩进了她冲浪板的脚绳里。"

    play sound sfx_boing
    show pzk delivery awkward at left_stage, shake
    p "诶——"

    n "脚绳一绷。"
    n "我的身体开始向后倒。"
    n "椰子从我手里飞了出去，在空中划出一道优美的抛物线。"

    play sound sfx_thud
    scene cg first_meet
    with vpunch

    n "咚。"
    n "我以一个非常标准的姿势，后脑勺着地，躺进了沙滩。"
    n "天空很蓝。"
    n "椰子呢？"

    n "我看见一只手在空中一抄。"
    n "椰子稳稳地落在了她手里。吸管都没洒。"

    y "……"
    y "你是来送外卖的，还是来碰瓷的？"

    scene bg beach_day
    with dissolve
    show pzk delivery awkward at left_stage
    show yyl cool at right_stage
    with dissolve
    play music bgm_awkward fadein 0.5

    n "她低头看着我。"
    n "逆光。头发还在滴水。"
    n "距离近到我能看清她睫毛上的海盐。"

    pt "完了。真的是梦里那个。"
    pt "而且……剧本跟梦里完全不一样。"
    pt "说点什么。潘子恺，说点帅的。挽回局面。"

    menu:
        "第一句话说什么？"

        "「美女，我们是不是在哪见过？」":
            $ first_line = "seen"
            p "美女……我们是不是在哪见过？"
            show yyl speechless at right_stage
            y "见过。"
            y "三秒前，你用后脑勺跟沙滩见的。"
            p "不是，我是说……在别的地方。比如梦里？"
            show yyl dead_fish at right_stage
            y "这句话我今年听过十一次。"
            y "你是第一个躺在地上说的。"

        "「你好，我是本岛最有钱的外卖员。」":
            $ first_line = "richest"
            $ fire_lane_used = True
            show pzk delivery proud at left_stage
            p "你好。"
            p "我是本岛最有钱的外卖员。"
            show yyl tease at right_stage
            y "本岛最有钱的外卖员。"
            y "你的车停在消防通道了。"
            show pzk delivery awkward at left_stage
            p "……"
            pt "原来那个车位没人停是因为这个。"
            $ stat("zb", 5)
            $ stat("yyl_aff", 3)

        "「你刚刚冲浪的姿势，有我三分帅气。」":
            $ first_line = "surf"
            show pzk delivery proud at left_stage
            p "你刚刚冲浪的姿势……"
            p "有我三分帅气。"
            show yyl tease at right_stage
            y "你刚刚摔倒的姿势，有我十分想笑。"
            p "那你笑啊。"
            y "我在忍。"
            show yyl smile at right_stage
            n "她的嘴角动了一下。真的只有一下。"
            n "但我看见了。"
            $ stat("zb", 5)
            $ stat("yyl_aff", 5)

    n "我从沙子里爬起来，拍了拍衣服。"
    n "拍了五下，沙子越拍越多。"
    show pzk delivery normal at left_stage

    show yyl calm at right_stage
    y "椰子水是我的。"
    p "……你就是Y女士？"
    y "嗯。"
    p "订单备注说，放在高跟鞋旁边。"
    p "你冲浪……带高跟鞋？"
    y "冲浪的时候不穿。"
    y "上岸穿。"
    p "在沙滩上穿高跟鞋？"
    y "嗯。"
    pt "这女人的平衡感是不是开了外挂。"

    n "她喝了一口椰子水，看了一眼我身后的路边。"

    if not fire_lane_used:
        p "咳。你知道我那辆车多少钱吗？"
        show yyl tease at right_stage
        y "不知道。"
        y "但我知道你停在消防通道了。"
        show pzk delivery awkward at left_stage
        p "……"
        pt "原来那个车位没人停是因为这个。"
        $ fire_lane_used = True

    show pzk delivery proud at left_stage
    p "其实我这个人，特别低调。"

    show yyl speechless at right_stage
    if wait_style == "pushup":
        y "你刚刚在沙滩上做了二十个俯卧撑。"
        p "那是热身。"
        y "你冲浪板都没带。"
        p "……"
        y "小朋友给你的饼干，你还揣在兜里。"
    elif wait_style == "pose":
        y "你刚刚靠着救生塔摆了五分钟姿势。"
        p "那是在看海。"
        y "救生员以为你中暑了，问了我两次要不要叫救护车。"
    else:
        y "嗯。低调到插一根吸管插了三次。"
        p "……你看见了？"
        y "全海滩都看见了。"
        show yyl smile at right_stage
        y "不过插得挺认真的。"
        $ stat("yyl_aff", 3)

    show pzk delivery normal at left_stage
    p "至少让我知道，我撞到的人叫什么吧。"
    show yyl calm at right_stage
    y "你没撞到我。你撞到的是沙滩。"
    p "那让我知道沙滩的主人叫什么。"
    n "她看了我两秒。"
    $ yyl_name = "杨永麟"
    y "杨永麟。"

    play sound sfx_heart
    pt "心跳 +1。"
    pt "理智 -5。"

    p "潘子恺。"
    y "我知道。"
    show pzk delivery awkward at left_stage
    p "？"
    p "你怎么知道？"
    y "外卖软件上写着。"

    n "我掏出手机，打开订单详情。"
    n "骑手信息：潘师傅。"
    p "……上面只写了「潘师傅」啊？"

    play music bgm_tension fadein 0.3
    show yyl cool at right_stage
    y "那就是猜的。"

    p "……"
    pt "你猜名字还能猜出名和姓？"
    n "她没有解释，只是看着我。"
    n "那种眼神，像在看一个她早就看过剧透的人。"
    pt "危险。"
    pt "这个女人不对劲。"
    pt "……但我好像更感兴趣了。"

    jump ch1_invite


## ---------------------------------------------------------------------------
## 晚餐邀约 & 三秒挑战
## ---------------------------------------------------------------------------

label ch1_invite:
    play music bgm_heroine fadein 1.0
    show pzk delivery normal at left_stage
    show yyl calm at right_stage

    n "她把喝完的椰子放进垃圾桶，弯腰去拿那双高跟鞋。"
    n "我知道，再不说点什么，她就要走了。"

    p "今晚有空吗？"
    y "做什么？"

    menu:
        "怎么约她？"

        "「我请你吃饭。全岛最贵的那家。」":
            show pzk delivery proud at left_stage
            p "我请你吃饭。全岛最贵的那家。"
            show yyl speechless at right_stage
            y "最贵的那家不好吃。"
            p "那第二贵的？"
            y "第二贵的是最贵的那家的分店。"
            $ stat("zb", 3)

        "「赔你一顿饭。刚刚吓到你了。」":
            show pzk delivery normal at left_stage
            p "赔你一顿饭。刚刚……吓到你了吧。"
            show yyl tease at right_stage
            y "你没吓到我。"
            y "你吓到椰子了。"
            show yyl smile at right_stage
            y "……不过理由还算正常。"
            $ stat("yyl_aff", 3)
            $ stat("sincere", 3)

        "「拯救一个被命运安排必须和你吃饭的男人。」":
            show pzk delivery proud at left_stage
            p "拯救一个被命运安排、今晚必须和你吃饭的男人。"
            show yyl speechless at right_stage
            y "命运这么闲？"
            p "命运很忙的。它专门抽空安排了我。"
            $ stat("zb", 5)

    show yyl calm at right_stage
    n "她想了想。"
    y "这样吧。"
    y "你要是能在冲浪板上站三秒，我就去。"

    show pzk delivery proud at left_stage
    p "三秒？"
    p "我梦里能在浪上站一整天。"
    show yyl tease at right_stage
    y "那是梦里。"

    n "她把冲浪板递给我。"
    n "我脱下外卖服——里面正好是一件花衬衫。"
    pt "天意。这就是天意。"

    scene bg surf_beach
    with dissolve
    show pzk surf normal at left_stage
    show yyl calm at far_right
    with dissolve

    n "十分钟后。"
    play sound sfx_splash
    n "我第一次从板上掉下来。"
    play sound sfx_splash
    n "第二次。"
    play sound sfx_splash
    show pzk surf awkward at left_stage, shake
    n "第三次，板子拍在了我的脸上。"
    n "梦里的我，现在应该在某个平行宇宙里嘲笑我。"

    menu:
        "怎么办？"

        "坦白：「其实我不会冲浪。我只在梦里会。」":
            $ surf_test = "honest"
            show pzk surf normal at left_stage
            n "我拖着板走回岸边，头发上挂着海草。"
            p "……其实我不会冲浪。"
            p "我只在梦里会。"
            show yyl surprised at far_right
            y "梦里？"
            p "嗯。梦里我特别会。还有一堆人尖叫。"
            show yyl happy at far_right
            n "她愣了一下，然后——"
            n "笑了。"
            show yyl villain at far_right
            play sound sfx_boing
            n "不是刚才那种嘴角动一下的笑。是真的笑出了声，笑得要扶着救生塔。"
            n "仰着头，一只手捂着半张脸，笑得像个刚统治了世界的反派。"
            pt "……原来她笑起来是这样的。"
            play sound sfx_heart
            y "好。看在你诚实的份上。"
            $ stat("yyl_aff", 10)
            $ stat("sincere", 10)

        "死磕：再来！我就不信了！":
            $ surf_test = "stubborn"
            show pzk surf damn at left_stage
            p "再来！"
            play sound sfx_splash
            n "第四次。"
            play sound sfx_splash
            n "第五次、第六次。"
            play sound sfx_splash
            n "第七次，我喝了大概半升海水。"
            n "第八次——"
            show pzk surf laugh at left_stage, hop
            n "我站起来了。"
            n "腿在抖，手在抖，灵魂也在抖。"
            show yyl smile at far_right
            y "一……"
            y "二……"
            play sound sfx_splash
            show pzk surf awkward at left_stage, shake
            n "我掉进了海里。"
            show yyl calm at far_right
            y "……三。"
            p "我、我站够了吗？"
            y "两秒九。"
            y "我四舍五入了。"
            n "她说这句话的时候没有笑，但声音比刚才软了一点。"
            y "第八次。你还挺能扛的。"
            $ stat("yyl_aff", 6)

        "作弊：把冲浪板放在沙滩上，站上去":
            $ surf_test = "cheat"
            show pzk surf laugh at left_stage
            n "我把冲浪板拖到沙滩上，放平，站了上去。"
            p "一、二、三。"
            p "我站了。"
            show yyl speechless at far_right
            y "……"
            show yyl tease at far_right
            y "沙滩上不算。"
            p "规则里没说要在海上。"
            y "嗯，没说。"
            show yyl bleh at far_right
            y "冲浪不算，脸皮厚度可以算。"
            n "她冲我拉下眼皮，吐了吐舌头。"
            $ stat("yyl_aff", 3)
            $ stat("zb", 5)

    scene bg beach_day
    with dissolve
    show pzk surf normal at left_stage
    show yyl calm at right_stage
    with dissolve

    y "七点。悬崖边那家「潮汐」。"
    y "我订位。"
    y "迟到一分钟，我就点一瓶最贵的酒。"
    show pzk surf laugh at left_stage
    p "我请。"
    show yyl tease at right_stage
    y "我知道你请。"

    play sound sfx_heels
    hide yyl with dissolve
    n "她拎着冲浪板走了。"
    n "那双黑色高跟鞋没有穿，而是勾在手指上，一晃一晃。"
    n "我站在原地看了很久。"
    n "直到她的背影变成一个点，又变成棕榈树后面的一片影子。"

    play sound sfx_phone
    show screen phone_notice("微信 · 新的朋友", "「Y」请求添加你为朋友")
    pause 0.3
    p "……"
    hide screen phone_notice

    play music bgm_tender fadein 1.5
    pt "梦里，是她找我要微信。"
    pt "现实里……也是她加的我。"
    pt "但梦里冲浪的是我，现实里冲浪的是她。"
    pt "梦里她来找我，现实里，是我走向她。"
    pt "「下次，换你来找我。」"
    pt "……巧合吧。"

    show pzk surf laugh at left_stage
    n "我点了「通过」。"
    pt "如果人生有系统提示的话，现在大概会弹出——"
    tip "【攻略目标：杨永麟】难度：S"
    p "很好。"
    p "挑战越高，奖励越香。"

    play sound sfx_phone
    app "您今日的配送已结束。今日收入：¥[delivery_income]。小蓝已被贴罚单一张：¥200。"
    show pzk surf awkward at left_stage
    p "……"

    stop music fadeout 2.0
    stop ambient fadeout 2.0
    scene bg black
    with fade
    jump chapter2
