## Chapter2.rpy —— 第一章 · 第二话「第一次晚餐」
##
## 流程：搜索攻略 → 衣帽间 → 对镜练习 → 研究菜单 → 选交通工具 → 潮汐餐厅晚餐 → 夜色栏杆 → 结局判定 → 第二个梦
## 分镜见 docs/storyboard_ch1_part2.md

## 星光粒子（夜色栏杆用）
image night_sparkles = SnowBlossom(Transform("images/sprites/fx/sparkle.png", zoom=0.25, alpha=0.7),
                                   count=24, border=50, xspeed=(-15, 15), yspeed=(-40, -15), start=4, fast=True)

## 限时选择的倒计时条
screen timed_choice_bar(seconds, timeout_label):
    zorder 96
    timer seconds action Jump(timeout_label)
    frame:
        xalign 0.5 ypos 300
        padding (16, 10, 16, 10)
        background Solid("#0b1e33cc")
        vbox:
            spacing 6
            text "快决定！" font gui.text_font size 26 color "#ffd34d" xalign 0.5
            bar value AnimatedValue(0, seconds, seconds, seconds) xsize 600 ysize 14 left_bar Solid("#ffd34d") right_bar Solid("#ffffff22")


label chapter2:
    scene bg black
    call screen chapter_card("第一章 · 第二话", "第一次晚餐")
    jump ch2_search


## ---------------------------------------------------------------------------
## 镜头 1：搜索引擎
## ---------------------------------------------------------------------------

label ch2_search:
    play music bgm_comedy fadein 1.0
    scene bg villa_bedroom
    with fade

    n "下午四点。距离约会还有三个小时。"
    n "我潘子恺，阅女无数——"
    n "主要是在梦里。"
    n "但这一次，我决定认真对待。"
    n "认真到，我打开了搜索引擎。"

    show screen phone_notice("搜索", "如何让高冷御姐爱上自己")
    pause 0.3
    hide screen phone_notice

    n "搜索结果第一页，三条高赞回答："
    tip "①「展示经济实力。高冷都是装的，爱马仕不会。」—— 某论坛·富哥交流区（赞 2.3万）"
    tip "②「保持神秘感。话说一半，眼神留一半。」—— 情感博主「渣男修炼手册」（赞 1.8万）"
    tip "③「做你自己。真诚是唯一的必杀技。」—— 一位结婚二十年的网友（赞 3）"
    pt "第三条只有三个赞。"
    pt "其中一个还是他老婆。"

    menu:
        "听谁的？"

        "① 展示经济实力":
            $ search_tip = "money"
            p "钱能解决的问题，都不是问题。"
            p "我的问题是，钱太多了，不知道怎么展示得不经意一点。"
            $ stat("zb", 5)

        "② 保持神秘感":
            $ search_tip = "mystery"
            p "神秘感……"
            p "这个我擅长。我自己都搞不清楚自己有多少钱，够神秘吧。"
            $ stat("zb", 3)

        "③ 做你自己":
            $ search_tip = "sincere"
            p "……做我自己。"
            pt "我自己，是什么样的来着？"
            n "我盯着这条回答看了很久，然后给它点了第四个赞。"
            $ stat("sincere", 5)

    jump ch2_closet


## ---------------------------------------------------------------------------
## 镜头 2：衣帽间
## ---------------------------------------------------------------------------

label ch2_closet:
    scene bg villa_closet
    with dissolve
    play sound sfx_door

    n "我的衣帽间。比很多人的家大。"
    n "比我的情史还长。"

    menu:
        "今晚穿什么？"

        "意大利手工定制西装（一件够买一辆车）":
            $ outfit = "suit"
            n "我穿上了那套深灰色的定制西装。"
            n "裁缝说，这是按我三年前的尺寸做的。"
            n "三年前，我还没有开始练胸。"
            show pzk casual proud at mirror_view
            with dissolve
            play sound sfx_mirror
            p "嗯。成熟。稳重。有钱。"
            p "再配一个——"
            n "我对着镜子，下意识地秀了一下胸肌。"
            play sound sfx_boing
            show pzk casual shock at mirror_view, shake
            with flash
            n "嘣。"
            n "第三颗扣子以大约每小时四十公里的速度射向了镜子。"
            n "镜子上多了一道裂纹。"
            n "镜子里的我，表情很复杂。"
            $ suit_burst = True
            $ outfit = "casual"
            show pzk casual awkward at mirror_view
            p "……没关系。"
            p "西装外套搭在肩上，里面穿紧身背心。"
            p "这叫「松弛感」。"

        "紧身背心（展示我身上最贵的东西：身体）":
            $ outfit = "casual"
            show pzk casual smug at mirror_view
            with dissolve
            play sound sfx_sparkle
            p "西装是给需要包装的人穿的。"
            p "我不需要包装。我就是礼物本身。"
            $ stat("zb", 5)

        "黑色 Alan Walker 卫衣 + 黑色 W 口罩（帽子必须戴着）":
            $ outfit = "hoodie"
            show pzk hoodie normal at mirror_view
            with dissolve
            play sound sfx_sparkle
            n "我从衣柜最深处翻出了一套全黑。"
            n "黑卫衣。黑口罩。口罩正中间一个白色的 W。"
            n "帽子戴上。拉绳拉紧。只露出一双眼睛和我的眼镜。"
            show pzk hoodie proud at mirror_view
            p "神秘感。"
            p "攻略说了，要保持神秘感。"
            pt "我把自己藏起来，她就会想知道我是谁。"
            pt "……虽然她已经知道我是谁了。"
            p "今晚，我不是潘子恺。"
            p "我是 Faded 的那个男人。"
            $ stat("zb", 5)

        "花衬衫（入乡随俗，海岛风）":
            $ outfit = "hawaii"
            show pzk surf laugh at mirror_view
            with dissolve
            p "海岛约会，就该穿花衬衫。"
            p "轻松，自然，不刻意。"
            pt "……而且她今天好像也穿的花衬衫。"
            pt "没有别的意思。纯属巧合。"
            $ stat("sincere", 3)

    hide pzk with dissolve
    jump ch2_mirror


## ---------------------------------------------------------------------------
## 镜头 3：对镜练习 & 研究菜单
## ---------------------------------------------------------------------------

label ch2_mirror:
    n "穿好衣服，下一步：练台词。"
    n "我在镜子前清了清嗓子。"

    if outfit == "hawaii":
        show pzk surf normal at mirror_view
    elif outfit == "hoodie":
        show pzk hoodie normal at mirror_view
    else:
        show pzk casual normal at mirror_view
    with dissolve

    menu:
        "练习哪一句？"

        "「你知道吗？你今天唯一的缺点，就是离我太远。」":
            $ practiced_line = "cheesy"
            p "你知道吗？"
            p "你今天唯一的缺点……"
            p "就是离我太远。"
            n "我说完，自己先打了个寒颤。"
            n "然后又练了二十遍，直到不打寒颤为止。"
            $ stat("zb", 5)

        "「我昨晚梦见你了。」":
            $ practiced_line = "dream"
            p "我昨晚……梦见你了。"
            pt "这句是真的。"
            pt "就是不知道说出来，会不会被当成变态。"

        "「其实我很紧张。」":
            $ practiced_line = "honest"
            p "其实……我很紧张。"
            n "镜子里的人愣了一下。"
            pt "这句不像我会说的话。"
            pt "但好像，是这几年我说过最真的一句。"
            $ stat("sincere", 5)

    hide pzk with dissolve

    n "接下来，研究「潮汐」的菜单。"
    n "法式海鲜。一道菜叫「海风与月光的低语」，价格：时价。"
    n "另一道叫「浪花的初吻」，价格：也是时价。"
    pt "这名字是诗人起的还是罪犯起的。"

    menu:
        "怎么准备？"

        "背下所有法语菜名，到时候惊艳她":
            $ studied_menu = True
            n "我花了一个小时，背下了十二道菜的法语名。"
            n "发音参考了一个视频，博主是东北人。"
            $ stat("zb", 3)

        "算了，到时候看她想吃什么":
            n "我合上了菜单。"
            pt "吃什么不重要。重要的是跟谁吃。"
            pt "……这句也挺好，记下来。"
            $ stat("sincere", 2)

    jump ch2_ride


## ---------------------------------------------------------------------------
## 镜头 4：交通工具
## ---------------------------------------------------------------------------

label ch2_ride:
    scene bg garage
    with dissolve
    n "六点半。车库。"
    n "最后一个问题：开什么去？"

    menu:
        "开什么去？"

        "蓝色兰博基尼「小蓝」":
            $ ride = "lambo"
            play sound sfx_engine
            n "小蓝的引擎声，是我最好的开场白。"
            $ stat("zb", 5)

        "外卖电动车「小黄」":
            $ ride = "ebike"
            show ebike at center_stage
            with dissolve
            n "车库角落里，停着小蓝的远房亲戚——小黄。"
            n "一辆跑了八千公里的外卖电动车。"
            p "今天不装了。"
            p "……主要是小蓝今天被贴了罚单，我有心理阴影。"
            $ stat("sincere", 5)

        "走路去（三公里，顺便热身）":
            $ ride = "walk"
            n "三公里而已。"
            n "对一个每天健身的男人来说，就是热身。"
            n "我出发时是这么想的。"
            $ stat("sincere", 3)

    if ride == "lambo":
        scene cg lambo_beach
        with wipeleft
        play sound sfx_drive
        n "海岸公路，日落时分。小蓝在悬崖边跑出了一道蓝色的线。"
    elif ride == "ebike":
        scene bg coast_road
        with wipeleft
        n "海岸公路，日落时分。小黄以每小时二十五公里的极限速度，被一辆观光大巴超了车。"
        n "大巴上的游客在拍我。"
    else:
        scene bg coast_road
        with wipeleft
        play sound sfx_steps
        n "海岸公路，日落时分。我在走第二公里。"
        n "热带的傍晚，气温二十九度，湿度百分之八十五。"
        n "我在走第三公里。我的背心已经湿透了。"

    jump ch2_arrive


## ---------------------------------------------------------------------------
## 镜头 5：抵达「潮汐」
## ---------------------------------------------------------------------------

label ch2_arrive:
    stop music fadeout 1.0
    scene bg restaurant_sunset
    with fade
    play music bgm_dinner fadein 2.0
    play ambient sfx_waves fadein 2.0 volume 0.35

    n "「潮汐」餐厅，悬崖边的露台。"
    n "夕阳正好落在海平面上，烛光被海风吹得一晃一晃。"
    n "我提前十分钟到了。这是我人生中第一次提前到。"

    if ride == "lambo":
        waiter "先生，您的车不能停在那里，那边是——"
        p "消防通道。"
        waiter "……您怎么知道？"
        p "我今天跟消防通道很熟。"
    elif ride == "ebike":
        n "门童看着我把小黄停在一辆保时捷旁边，表情管理失败了三秒。"
    else:
        n "门童默默递给我一条毛巾。"
        n "那是给客人擦手用的。他让我擦头。"

    manager "先生是杨小姐的客人吧？这边请。"
    pt "杨小姐。"
    pt "听这语气，她是这里的常客。"

    call ch2_show_pzk_seated

    n "我坐下，调整了三次坐姿，找到了一个能同时露出肱二头肌和侧脸的角度。"

    play sound sfx_heels
    n "然后，我听到了高跟鞋的声音。"
    n "嗒。嗒。嗒。"
    n "不急不慢，踩在木地板上，像在倒数。"

    show yyl dinner calm at slide_in_right
    pause 0.6
    show yyl dinner calm at seated(0.80)
    with dissolve

    n "她来了。"
    n "她换掉了白天的花衬衫。"
    n "黑色缎面吊带裙，肩上搭着一条奶白色的披肩，脚上是那双黑色的细高跟。"
    n "双马尾还是那对双马尾。"
    n "我承认，在那一秒，我把背了一个小时的法语全忘了。"

    if outfit == "hawaii":
        show yyl dinner brain_lag at seated(0.80)
        y "……"
        n "她盯着我的花衬衫，嘴歪到一边，两只眼睛各看一个方向。"
        n "我怀疑她的大脑在重新加载。"
        show yyl dinner speechless at seated(0.80)
        y "我白天穿花衬衫，晚上换了裙子。"
        y "你是反过来的？"
        p "我这叫……接你的班。"
        show yyl dinner tease at seated(0.80)
        y "接班的穿的是海岛纪念品店，同一个货架。"
        n "服务生路过，看了看我们，露出了「懂了」的微笑。"
        show yyl dinner smile at seated(0.80)
        n "她低头笑了一下，没有反驳。"
        $ stat("yyl_aff", 5)
    elif outfit == "hoodie":
        show yyl dinner speechless at seated(0.80)
        y "……"
        n "她看了我很久。从帽子看到口罩，从口罩看到那个 W。"
        y "你是来吃饭的，还是来打碟的？"
        p "我是来保持神秘感的。"
        y "海岛，二十九度，你穿卫衣戴帽子。"
        p "神秘感不分季节。"
        show yyl dinner tease at seated(0.80)
        y "口罩上那个 W，是 Walker，还是 Weird？"
        p "……是 Wealthy。"
        n "服务生过来点单，看了我一眼，默默把我们这桌的蜡烛挪远了一点，好像怕我是来抢劫的。"
        $ stat("zb", 3)
        $ stat("yyl_aff", 2)
    elif suit_burst:
        y "你的外套为什么搭在肩上？"
        p "松弛感。"
        y "第三颗扣子呢？"
        p "……在镜子里。"
        show yyl dinner speechless at seated(0.80)
        y "什么？"
        p "没什么。"
    else:
        y "晚上海风大，你穿背心不冷？"
        p "我自带暖气。"
        n "我指了指自己的胸肌。"
        show yyl dinner tease at seated(0.80)
        y "嗯，发电机。"

    if ride == "ebike":
        show yyl dinner smile at seated(0.80)
        y "门口那辆黄色电动车，是你的？"
        p "……小黄。"
        y "小黄比小蓝可爱。"
        $ stat("yyl_aff", 5)
    elif ride == "walk":
        show yyl dinner jaw_drop at seated(0.80)
        play sound sfx_shock
        n "她看到我湿透的背心，双手捂住了脸，下巴掉了下来。"
        y "你……是游泳过来的？"
        show yyl dinner calm at seated(0.80)
        p "走过来的。"
        y "三公里？"
        p "热身。"
        show yyl dinner smile at seated(0.80)
        y "下次可以叫我顺路接你。"
        $ stat("yyl_aff", 3)
    else:
        y "我在路口就听到你了。"
        p "听到我的引擎声？"
        y "听到门童喊「那边不能停」。"

    jump ch2_order


## 根据穿搭显示坐着的潘子恺
label ch2_show_pzk_seated:
    if outfit == "hawaii":
        show pzk surf normal at seated(0.22)
    elif outfit == "hoodie":
        show pzk hoodie normal at seated(0.22)
    else:
        show pzk casual normal at seated(0.22)
    with dissolve
    return

## 根据穿搭切换潘子恺的表情（mood: normal/proud/awkward/shy/shock）
label ch2_pzk(mood="normal"):
    if outfit == "hawaii":
        $ _m = {"normal": "normal", "proud": "laugh", "awkward": "awkward", "shy": "laugh", "shock": "shock", "gloom": "awkward"}[mood]
        $ renpy.show("pzk surf " + _m, at_list=[seated(0.22)])
    elif outfit == "hoodie":
        $ renpy.show("pzk hoodie " + mood, at_list=[seated(0.22)])
    else:
        $ _m = {"normal": "normal", "proud": "proud", "awkward": "awkward", "shy": "shy", "shock": "shock", "gloom": "gloom"}[mood]
        $ renpy.show("pzk casual " + _m, at_list=[seated(0.22)])
    return


## ---------------------------------------------------------------------------
## 镜头 6：点菜
## ---------------------------------------------------------------------------

label ch2_order:
    waiter "两位，可以点菜了吗？"

    menu:
        "怎么点？"

        "全部来最贵的":
            $ ordered = "expensive"
            call ch2_pzk("proud")
            p "把你们菜单上最贵的，每样来一份。"
            waiter "好的先生。龙虾三份，鱼子酱两份，还有一份「海风与月光的低语」。"
            show yyl dinner calm at seated(0.80)
            y "「海风与月光的低语」是什么？"
            waiter "是一勺盐，小姐。来自月圆之夜晒的海盐。时价一千八百八十八。"
            call ch2_pzk("awkward")
            p "……"
            show yyl dinner tease at seated(0.80)
            y "很好。它会是今晚最低调的一道菜。"
            $ stat("zb", 5)
            if search_tip == "money":
                pt "攻略说要展示经济实力。我展示了。展示的是一勺盐。"

        "用法语点菜" if studied_menu:
            $ ordered = "french"
            call ch2_pzk("proud")
            p "咳。Je voudrais……「拉 啵 赛 嘞 嘚 吗 嗐」……"
            waiter "……"
            waiter "先生，我们老板是潮汕人，您说中文就行。"
            show yyl dinner smile at seated(0.80)
            y "他想说 la bouillabaisse，马赛鱼汤。"
            n "她的发音轻得像海风，跟我那个东北博主完全是两个物种。"
            call ch2_pzk("shock")
            p "你会法语？"
            show yyl dinner calm at seated(0.80)
            y "在里昂待过两年。"
            y "那边的鱼汤没有这里的好喝。"
            pt "……我背了一个小时，她一句话就超过了我。"
            pt "但为什么我一点都不生气，反而想多问点里昂的事。"
            $ stat("yyl_aff", 3)
            $ stat("zb", 3)

        "「你来点吧。」":
            $ ordered = "her"
            call ch2_pzk("normal")
            p "你来点吧。你是常客。"
            show yyl dinner surprised at seated(0.80)
            n "她看了我一眼，好像有点意外。"
            show yyl dinner calm at seated(0.80)
            y "老样子，两份。"
            manager "好嘞，杨小姐。"
            n "十分钟后，端上来的是两盘……海鲜炒粉。"
            n "不在菜单上。锅气很足，虾比我的拳头还大。"
            call ch2_pzk("shock")
            p "这家法餐厅……有炒粉？"
            show yyl dinner smile at seated(0.80)
            y "后厨的阿伯是我冲浪认识的。"
            y "法餐是给游客的。这个是给自己人的。"
            pt "自己人。"
            pt "这三个字我在心里嚼了很久，比炒粉还香。"
            $ stat("yyl_aff", 5)
            $ stat("sincere", 3)

    jump ch2_talk


## ---------------------------------------------------------------------------
## 镜头 7：聊工作
## ---------------------------------------------------------------------------

label ch2_talk:
    show yyl dinner calm at seated(0.80)
    call ch2_pzk("normal")

    if outfit == "hoodie":
        n "菜上来了。"
        n "我吃一口，把口罩拉下来一点。嚼完，再拉上去。"
        n "再吃一口，再拉下来。再拉上去。"
        n "帽子不能摘。摘了就不神秘了。"
        show yyl dinner speechless at seated(0.80)
        y "你这样吃饭，像在做贼。"
        call ch2_pzk("awkward")
        p "我在给食物营造仪式感。"
        show yyl dinner calm at seated(0.80)

    y "你呢？除了送外卖，平时做什么？"
    p "金融投资。"
    y "嗯。我做风控。"
    p "风控？控制风的？冲浪那种？"
    show yyl dinner tease at seated(0.80)
    y "控制风险。"
    y "我的工作，就是看一个人在撒什么谎。"
    call ch2_pzk("awkward")
    pt "……这句话为什么让我后背一凉。"

    show yyl dinner calm at seated(0.80)
    y "所以，你投资什么？"

    menu:
        "怎么回答？"

        "「你知道我一年赚多少吗？」":
            call ch2_pzk("proud")
            p "你知道我一年赚多少吗？"
            show yyl dinner cool at seated(0.80)
            y "不知道。也不想知道。"
            y "一个人反复提他有多少钱，一般说明他除了钱，没什么可聊的。"
            call ch2_pzk("gloom")
            n "海风吹过。烛火晃了一下。我的自尊心也晃了一下。"
            $ stat("yyl_aff", -3)
            $ stat("zb", 5)

        "「运气好，早年押对了几只股票。后来……就一直挺无聊的。」":
            call ch2_pzk("normal")
            p "运气好。早年押对了几只股票。"
            p "后来就……一直挺无聊的。"
            show yyl dinner surprised at seated(0.80)
            y "无聊？"
            p "钱多了以后，每天都像同一天。"
            show yyl dinner calm at seated(0.80)
            y "所以去送外卖。"
            p "……你怎么知道是这个原因？"
            y "风控的职业病。"
            $ stat("yyl_aff", 3)
            $ stat("sincere", 5)

        "反问她：「你呢？为什么来岛上？」":
            call ch2_pzk("normal")
            p "先说你。你为什么来岛上？"
            show yyl dinner calm at seated(0.80)
            y "以前在大城市，银行风控部。"
            y "每天看几百份报表，找里面的谎。"
            y "后来发现，找得越准，越不相信任何人。"
            y "两年前辞职，搬到岛上。现在接点自由咨询，每天早上六点冲浪。"
            show yyl dinner smile at seated(0.80)
            y "浪不会撒谎。它要拍你，就真的拍你。"
            pt "……她说这句话的时候，眼睛在看海，不在看我。"
            pt "但我觉得，我好像离她近了一点。"
            $ stat("yyl_aff", 5)
            $ stat("sincere", 3)

    show yyl dinner calm at seated(0.80)
    y "对了。你这种人，钱一般放在哪？"
    y "瑞士？开曼？还是全放在一个账户里？"
    call ch2_pzk("proud")
    p "放在心里。"
    show yyl dinner tease at seated(0.80)
    y "……职业病，别介意。"
    n "她笑着端起了水杯。"
    n "我也笑了。"
    n "那时候，我没多想。"

    jump ch2_line_check


## 对镜练习的台词「验收」
label ch2_line_check:
    pt "现在。是时候用出我练了一下午的台词了。"

    if practiced_line == "cheesy":
        call ch2_pzk("proud")
        p "你知道吗？你今天唯一的缺点……"
        p "就是离我太远。"
        stop music fadeout 0.3
        play sound sfx_crickets
        show yyl dinner dead_fish at seated(0.80)
        n "……"
        n "邻桌的大叔放下了刀叉。"
        n "远处的海浪都安静了。"
        play music bgm_awkward
        y "……你练了多久？"
        call ch2_pzk("awkward")
        p "两小时。"
        y "辛苦了。"
        show yyl dinner creepy_smile at seated(0.80)
        y "不过——挺好笑的。"
        n "她慢慢地笑了。嘴角一直咧到了耳根。"
        pt "……为什么她夸我的时候，我后背发凉。"
        $ stat("yyl_aff", 2)
        play music bgm_dinner fadein 1.0

    elif practiced_line == "dream":
        call ch2_pzk("normal")
        p "我昨晚梦见你了。"
        show yyl dinner surprised at seated(0.80)
        n "她的水杯停在半空。"
        y "……梦见我什么？"
        p "梦里我在冲浪，很帅，一堆人尖叫。"
        p "然后你走过来，找我要微信。"
        y "然后呢？"
        call ch2_pzk("awkward")
        p "我让你去后面排队。"
        show yyl dinner happy at seated(0.80)
        n "她笑出了声。"
        y "那现实里呢？你排队了吗？"
        call ch2_pzk("shy")
        p "……现实里，好像是我排在第一个。"
        play sound sfx_heart
        $ stat("yyl_aff", 5)

        play music bgm_tension fadein 0.5
        show yyl dinner calm at seated(0.80)
        y "梦里，冲浪的人是你？"
        p "嗯。"
        y "……有意思。"
        n "她说「有意思」的时候，一点都不惊讶。"
        n "就好像，她早就知道这个梦。"
        play music bgm_dinner fadein 1.0

    else:
        call ch2_pzk("shy")
        p "……其实我很紧张。"
        show yyl dinner surprised at seated(0.80)
        y "你？"
        if wait_style == "pushup":
            y "白天在沙滩上做俯卧撑的那个人？"
        else:
            y "白天被冲浪板拍了脸的那个人？"
        p "我练了一下午的台词，结果说出口的是这句。"
        show yyl dinner smile at seated(0.80)
        y "那你练的其他台词呢？"
        p "都很烂。这句是最不烂的。"
        show yyl dinner shy at seated(0.80)
        n "她没说话，低头拨了一下盘子里的虾。"
        n "耳朵好像有点红。"
        n "……也可能是夕阳。"
        play sound sfx_heart
        $ stat("yyl_aff", 8)
        $ stat("sincere", 5)

    jump ch2_order_ping


## ---------------------------------------------------------------------------
## 镜头 8：外卖订单响了（限时选择）
## ---------------------------------------------------------------------------

label ch2_order_ping:
    play sound sfx_phone
    show screen phone_notice("岛团外卖", "您有新的订单！—— 隔壁「椰林奶茶」→「潮汐」露台 7号桌")
    with vpunch
    app "您有新的订单！您有新的订单！"
    n "我忘了下线。"
    n "整个露台的人都回头看我。"
    hide screen phone_notice

    call ch2_pzk("shock")
    pt "7号桌……就是我们隔壁桌？？"
    guest "哟，我点的奶茶，派到你这儿了？"

    show screen timed_choice_bar(6.0, "ch2_order_timeout")
    menu:
        "接不接？"

        "拒单，专心约会":
            hide screen timed_choice_bar
            call ch2_pzk("normal")
            n "我按下了「拒单」。"
            show yyl dinner calm at seated(0.80)
            y "拒单会扣分吧？"
            p "扣就扣。今晚我不是骑手。"
            y "那你是什么？"
            call ch2_pzk("proud")
            p "我是你的约会对象。"
            show yyl dinner tease at seated(0.80)
            y "……扣分的那种。"
            $ stat("yyl_aff", 2)
            jump ch2_night

        "接单！骑手的尊严不能丢":
            hide screen timed_choice_bar
            jump ch2_take_order

label ch2_order_timeout:
    hide screen timed_choice_bar
    n "我犹豫了太久。"
    show yyl dinner smile at seated(0.80)
    y "去吧，骑手。"
    y "我在这儿等你。"
    jump ch2_take_order

label ch2_take_order:
    $ took_order = True
    play music bgm_delivery fadein 0.3
    call ch2_pzk("proud")
    n "我站起来，以送外卖的标准速度冲出餐厅。"
    n "隔壁奶茶店。取餐。冲回来。"
    n "全程一分四十秒。"
    play sound sfx_steps
    p "您好，您的椰椰芒芒冰沙，少糖去冰！"
    guest "这么快？？"
    if took_photo:
        guest "哎？你不是……网上那个开兰博基尼送外卖的？我刷到过你，比了十二个耶那个！"
        call ch2_pzk("awkward")
        p "……那是我职业生涯的高光时刻。"
    guest "小伙子可以！五星！"
    play sound sfx_cash
    n "邻桌的大叔带头鼓掌。整个露台都跟着鼓掌。"
    n "我站在掌声里，手里还拿着外卖袋，有点不知所措。"
    $ delivery_income += 4
    $ stat("zb", 3)

    stop music fadeout 1.0
    play music bgm_dinner fadein 1.5
    call ch2_pzk("shy")
    n "我坐回位子上。"
    show yyl dinner smile at seated(0.80)
    n "她一手撑着下巴看我。看了很久。"
    y "潘子恺。"
    p "嗯？"
    show yyl dinner happy at seated(0.80)
    play sound sfx_heart
    y "你送外卖的时候，比你装逼的时候好看。"
    pt "……"
    pt "这是夸我吗？"
    pt "这是在夸我吧。"
    $ stat("yyl_aff", 8)
    $ stat("sincere", 5)
    jump ch2_night


## ---------------------------------------------------------------------------
## 镜头 9：夜色栏杆
## ---------------------------------------------------------------------------

label ch2_night:
    stop music fadeout 2.0
    scene bg restaurant_night
    with Dissolve(2.0)
    play music bgm_tender fadein 2.0
    show night_sparkles

    n "太阳落下去了。"
    n "餐厅的灯一盏一盏亮起来，海面上铺了一层碎掉的月光。"
    n "吃完饭，她走到露台的栏杆边，看海。"
    n "我跟了过去。"

    if outfit == "hawaii":
        show pzk surf normal at left_stage
    elif outfit == "hoodie":
        show pzk hoodie normal at left_stage
    else:
        show pzk casual normal at left_stage
    show yyl dinner calm at right_stage
    with dissolve

    if not told_truth:
        y "所以。"
        y "你为什么送外卖？说真话。"

        menu:
            "怎么回答？"

            "开个玩笑糊弄过去":
                p "体验生活。顺便给顾客提供超跑级配送体验。"
                show yyl dinner calm at right_stage
                y "嗯。标准答案。"
                n "她没有追问。"
                n "但我知道，她听出来了。"
                n "风控的职业病。"

            "说真话":
                $ told_truth = True
                p "……钱多到一定程度，就没人跟你说真话了。"
                p "朋友说我帅，是因为我买单。"
                p "女孩说喜欢我，是因为小蓝。"
                p "我妈说我好，是因为……好吧，我妈是真的。"
                p "但送外卖的时候，顾客骂我送得慢，那是真的。"
                p "阿姨给我五块钱小费，也是真的。"
                show yyl dinner surprised at right_stage
                n "她转过头看我。"
                n "这是今晚她第一次，没有立刻接我的话。"
                show yyl dinner calm at right_stage
                y "浪也是。"
                y "浪不会因为你有钱，就对你客气。"
                y "所以我喜欢它。"
                play sound sfx_heart
                $ stat("yyl_aff", 10)
                $ stat("sincere", 10)

    if told_truth or sincere >= 20:
        $ got_sea_glass = True
        show yyl dinner smile at right_stage
        n "她从口袋里摸出一个小东西，放在我手心。"
        n "一块蓝色的玻璃。边缘圆圆的，摸上去像一颗糖。"
        y "海玻璃。"
        y "碎玻璃在海里磨上十几年，就不扎手了。"
        y "蓝色的，跟你的车一个颜色。"
        y "送你。"
        if outfit == "hawaii":
            show pzk surf laugh at left_stage
        elif outfit == "hoodie":
            show pzk hoodie shy at left_stage
        else:
            show pzk casual shy at left_stage
        p "为什么送我？"
        show yyl dinner tease at right_stage
        y "因为你现在，还有点扎手。"
        pt "……"
        pt "我把它攥在手心里，攥得很紧。"
        $ stat("yyl_aff", 5)

    play sound sfx_vibrate
    show yyl dinner calm at right_stage
    n "她的手机在栏杆上亮了一下。"
    n "我不是故意看的。只是屏幕正对着我。"
    tip "K：到了吗？"
    n "她把手机扣了过去。动作很自然。"
    $ noticed_k = True

    menu:
        "……"

        "「K是谁？」":
            $ asked_k = True
            p "K是谁？"
            show yyl dinner cool at right_stage
            y "一个朋友。"
            n "停了一秒。"
            show yyl dinner calm at right_stage
            y "……很啰嗦的朋友。"
            pt "她说这句话的时候，语气跟说「浪不会撒谎」的时候一模一样。"
            pt "我分不清，那是真话，还是她很会说真话的样子。"

        "装作没看见":
            pt "……我为什么要在意这个。"
            pt "她有朋友，很正常。"
            pt "我又不是她的谁。"
            pt "……暂时。"

    jump ch2_bill


## ---------------------------------------------------------------------------
## 镜头 10：买单 & 结局判定
## ---------------------------------------------------------------------------

label ch2_bill:
    hide night_sparkles
    if outfit == "hawaii":
        show pzk surf laugh at left_stage
    elif outfit == "hoodie":
        show pzk hoodie proud at left_stage
    else:
        show pzk casual proud at left_stage
    show yyl dinner calm at right_stage

    n "回到桌边，我潇洒地抬手。"
    p "买单。"
    n "我把黑卡放在桌上，角度刚好能让烛光照亮卡面。"
    waiter "先生，杨小姐已经结过了。"

    if outfit == "hawaii":
        show pzk surf shock at left_stage
    elif outfit == "hoodie":
        show pzk hoodie shock at left_stage
    else:
        show pzk casual shock at left_stage
    p "？？？"
    p "你不是说我请吗？"
    show yyl dinner smug_chad at right_stage
    y "我说的是「我知道你请」。"
    y "我没说我会让你请。"
    n "她抱着胳膊，下巴抬得很高，用眼角看着我。"

    if yyl_aff >= 45 and sincere >= 30:
        jump ch1_ending_a
    elif yyl_aff >= 25:
        jump ch1_ending_b
    else:
        jump ch1_ending_c


label ch1_ending_a:
    $ ch1_ending = "A"
    if outfit == "hoodie" or outfit == "hawaii":
        scene bg restaurant_night
        if outfit == "hoodie":
            show pzk hoodie shy at seated(0.22)
        else:
            show pzk surf laugh at seated(0.22)
        show yyl dinner smile at seated(0.80)
        with dissolve
    else:
        scene cg first_dinner
        with dissolve
    play sound sfx_heart
    y "下次你请。"
    y "不过不是在这里。"
    p "那在哪？"
    y "明早六点，海滩。"
    y "别开你的车，也别带你的台词。"
    y "我教你在浪上站三秒。真的三秒。"
    n "她站起来，拎起包。"
    n "高跟鞋走了三步，又停下。"
    y "潘子恺。"
    p "嗯？"
    y "今天……挺好玩的。"
    n "然后她走了。"
    n "我在烛光里坐了很久，直到服务生来收桌子。"
    pt "明早六点。"
    pt "我这辈子从来没在早上六点起过床。"
    pt "……定五个闹钟吧。"
    $ record_ending("A")
    call screen chapter_result("A", "明早六点，海滩见", "她邀请你去上冲浪课。\n你第一次觉得，有比钱更难得到的东西。")
    jump ch1_epilogue

label ch1_ending_b:
    $ ch1_ending = "B"
    show yyl dinner smile at right_stage
    y "下次你请。"
    p "下次？"
    y "嗯。如果有下次的话。"
    n "她说完就走了。没有回头。"
    if outfit == "hawaii":
        show pzk surf normal at left_stage
    elif outfit == "hoodie":
        show pzk hoodie normal at left_stage
    else:
        show pzk casual normal at left_stage
    pt "「如果有下次的话」。"
    pt "这是好话还是坏话？"
    pt "我研究了一辈子K线图，第一次看不懂一条走势。"
    $ record_ending("B")
    call screen chapter_result("B", "下次你请", "她没有拒绝你，也没有答应你。\n这一局，平手。")
    jump ch1_epilogue

label ch1_ending_c:
    $ ch1_ending = "C"
    show yyl dinner cool at right_stage
    y "谢谢你的晚餐表演。"
    y "挺精彩的。"
    n "她拎起包走了。高跟鞋的声音越来越远。"
    if outfit == "hawaii":
        show pzk surf awkward at left_stage
    elif outfit == "hoodie":
        show pzk hoodie gloom at left_stage
    else:
        show pzk casual gloom at left_stage
    pt "……「表演」。"
    pt "她说的是「表演」。"
    n "我一个人看着海，把那一勺一千八百八十八的盐吃了。"
    n "很咸。"
    play sound sfx_phone
    show screen phone_notice("微信 · Y", "今天的椰子水钱，你还没收。")
    pause 0.3
    pt "……"
    pt "她这是……给我留了个台阶？"
    hide screen phone_notice
    $ record_ending("C")
    call screen chapter_result("C", "她买的单", "你展示了很多东西，唯独没有展示你自己。\n但她还没有删你。")
    jump ch1_epilogue


## ---------------------------------------------------------------------------
## 镜头 11：夜晚别墅 · 第二个梦
## ---------------------------------------------------------------------------

label ch1_epilogue:
    stop music fadeout 2.0
    stop ambient fadeout 2.0
    scene bg villa_bedroom_night
    with fade
    play ambient sfx_waves fadein 2.0 volume 0.3

    n "回到别墅，已经十一点了。"
    n "我躺在床上，盯着天花板。"
    if got_sea_glass:
        n "那块蓝色的海玻璃放在枕头边，月光照上去，在墙上投出一小块蓝。"
    n "今天发生了很多事。"
    n "被网红差评。被阿姨同情。被冲浪板拍脸。被一个女人请了一顿饭。"
    n "按理说，我应该很丢脸。"
    n "但我闭上眼睛的时候，嘴角是翘着的。"

    scene bg black
    with Dissolve(2.0)
    stop ambient fadeout 3.0
    play music bgm_tension fadein 3.0

    n "那天晚上，我又做梦了。"
    scene bg night_beach
    with dream_fade
    show yyl silhouette at right_stage
    with dissolve
    n "还是那片海。可这一次，没有尖叫的女孩。"
    n "海是黑的。浪很安静。"
    n "她站在岸边，背对着我。手里拿着一部手机。"
    n "屏幕的光，是蓝色的。"
    show yyl creepy_smile at right_stage
    with dissolve
    play sound sfx_sting
    n "她转过头，冲我笑了一下。"
    n "嘴角一直咧到了耳根。"
    n "跟我的余额页面一个颜色。"
    mystery_voice "……别信——"
    stop music
    scene bg black
    n "声音断了。"
    n "我没有听清，后面那个字是什么。"
    n "也没有听清，那是谁的声音。"

    pause 1.0
    tip "—— 第一章 完 ——"
    jump chapter3
