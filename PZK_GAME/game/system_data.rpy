## system_data.rpy —— 纯爱致富系统的数据表：可扫描的人物 + 专属奖励
##
## 新增一个人物 = 加一行 person(...)；新奖励 = 加一行 reward(...)。不需要改 system.rpy。
##   pid    内部 id（英文）       name  姓名（扫描显示的是真名）   age  年龄
##   gender "女"/"男"            score 颜值评分（≥ 90 且成年女性才符合攻略条件）
##   traits 人物特点（赠与解锁后显示）   reward  REWARDS 的 key，None = 待定

init -6 python:

    REWARDS = {}
    PEOPLE = {}

    def reward(rid, name, desc="具体效果：待剧情揭晓。"):
        REWARDS[rid] = dict(name=name, desc=desc)

    def person(pid, name, age, gender="女", score=0, traits="", reward=None):
        PEOPLE[pid] = dict(name=name, age=age, gender=gender, score=score, traits=traits, reward=reward)

    # ---------------- 专属奖励 ----------------
    reward("super_body", "超强体魄")
    reward("bio_guard", "生化人保镖")

    # ---------------- 攻略对象（已定） ----------------
    person("dhy", "丁虹依", 25, score=93, reward="super_body",
           traits="宿主高中同学，三中校花。开朗，嘴快，比谁都务实。")
    person("lxx", "李轩翔", 31, score=96, reward="bio_guard",
           traits="宿主的前上司，投资银行部董事总经理（MD）。强势，冷静，果断。")

    # ---------------- 第三章出场 / 被扫描的人（都不到 90） ----------------
    person("pzk", "潘子恺", 25, gender="男", score=-250)
    person("spa_new", "刘翠芬", 34, score=81)          # 足疗店门口自称「小雪，十九岁，刚入行」
    person("spa_desk", "王桂兰", 52, score=64)         # 足疗店前台王姐
    person("ex_su", "苏蔓", 27, score=89)              # 富豪时期·游艇派对
    person("ex_lin", "林可可", 26, score=89)           # 富豪时期·米其林生日宴
    person("ex_zhou", "周雨晴", 28, score=88)          # 富豪时期·滑雪场
    person("zhao", "赵磊", 29, gender="男", score=62)  # 前同事，合照里
