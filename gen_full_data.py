# -*- coding: utf-8 -*-
"""Complete test data generator for Exam System"""
import requests, json

base = "http://localhost:8003/api"
r = requests.post(base + "/auth/login", data={"username": "admin", "password": "admin123"}, timeout=10)
token = r.json()["access_token"]
headers = {"Authorization": "Bearer " + token}

def api_get(path, **kw):
    return requests.get(base + path, headers=headers, timeout=15, **kw)

def api_post(path, **kw):
    return requests.post(base + path, headers=headers, timeout=15, **kw)

def api_put(path, **kw):
    return requests.put(base + path, headers=headers, timeout=15, **kw)

def api_delete(path, **kw):
    return requests.delete(base + path, headers=headers, timeout=15, **kw)

# ====== STEP 1: Clear all data ======
print("=== Step 1: Clearing all data ===")

# Delete questions first (FK constraints)
r = api_get("/questions?page=1&page_size=500")
for q in r.json().get("items", []):
    api_delete("/questions/" + str(q["id"]))

# Delete exams
r = api_get("/exams?page=1&page_size=100")
for e in r.json().get("items", []):
    api_delete("/exams/" + str(e["id"]))

# Delete certificates
r = api_get("/certificates")
for c in r.json():
    api_delete("/certificates/" + str(c["id"]))

# Delete announcements
r = api_get("/announcements?page=1&page_size=100")
for a in r.json().get("items", []):
    api_delete("/announcements/" + str(a["id"]))

# Delete subjects (cascades chapters)
r = api_get("/subjects")
for s in r.json():
    api_delete("/subjects/" + str(s["id"]))

# Delete resources (might not have list endpoint)
try:
    r = api_get("/resources?page=1&page_size=100")
    for item in r.json().get("items", []):
        api_delete("/resources/" + str(item["id"]))
except: pass

# Delete videos
try:
    r = api_get("/videos?page=1&page_size=100")
    for item in r.json().get("items", []):
        api_delete("/videos/" + str(item["id"]))
except: pass

# Delete extra users (keep admin)
r = api_get("/users")
users = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
for u in users:
    if u.get("username") not in ("admin",):
        try:
            # Try users delete endpoint
            api_delete("/users/" + str(u.get("id", u.get("user_id", 0))))
        except: pass

print("Data cleared.")

# ====== STEP 2: Create roles ======
print("\n=== Step 2: Creating roles ===")
# Delete existing non-system roles
try:
    existing_roles = api_get("/roles").json()
    for r in existing_roles:
        if not r.get("is_system"):
            api_delete("/roles/" + str(r["id"]))
except: pass

roles_data = [
    {"name": "负责人", "description": "系统负责人，可管理全部内容", "is_manager": True, "sort_order": 1},
    {"name": "实验员", "description": "实验室管理员", "is_manager": True, "sort_order": 3},
    {"name": "教务", "description": "教务管理人员", "is_manager": True, "sort_order": 4},
]
for rd in roles_data:
    api_post("/roles", json=rd)
print("Roles created.")

# ====== STEP 3: Create users ======
print("\n=== Step 3: Creating users ===")
users_data = [
    {"username": "zhangsan", "password": "123456", "fullname": "张三", "role": "student"},
    {"username": "lisi", "password": "123456", "fullname": "李四", "role": "student"},
    {"username": "wangwu", "password": "123456", "fullname": "王五", "role": "student"},
    {"username": "teacher1", "password": "123456", "fullname": "张老师", "role": "teacher"},
    {"username": "fuzeren", "password": "123456", "fullname": "李负责人", "role": "teacher"},
    {"username": "shiyanyuan", "password": "123456", "fullname": "赵实验员", "role": "teacher"},
]
for ud in users_data:
    try:
        api_post("/auth/register", json=ud)
    except:
        pass
print("Users created.")

# ====== STEP 4: Create subjects and chapters ======
print("\n=== Step 4: Creating subjects & chapters ===")
subjects_chapters = [
    ("建筑工程施工技术", [
        "土方与基础工程", "混凝土结构施工", "砌体工程施工",
        "钢结构施工", "施工测量技术", "防水工程施工",
    ]),
    ("建筑工程材料", [
        "水泥与混凝土", "建筑钢材", "砌体材料",
        "防水材料", "装饰装修材料",
    ]),
    ("建筑法规与标准", [
        "建筑法律法规", "工程验收标准", "施工规范",
        "合同与招投标",
    ]),
    ("建筑安全管理", [
        "施工安全管理", "高处作业防护", "机械设备安全",
        "消防安全", "应急预案管理",
    ]),
]

subjects = {}
chapter_lookup = {}
for subj_name, ch_names in subjects_chapters:
    r = api_post("/subjects", json={"name": subj_name, "description": subj_name + "考试科目"})
    s = r.json()
    subjects[subj_name] = s
    for ch_name in ch_names:
        r = api_post("/subjects/" + str(s["id"]) + "/chapters",
                     json={"subject_id": s["id"], "name": ch_name})
        ch = r.json()
        chapter_lookup[(subj_name, ch_name)] = ch
    print("  " + subj_name + ": " + str(len(ch_names)) + " chapters")

# ====== STEP 5: Create questions ======
print("\n=== Step 5: Creating questions ===")
questions = [
    # ===== 施工技术 =====
    {"subject": "建筑工程施工技术", "chapter": "土方与基础工程", "type": "single", "difficulty": 2,
     "content": "基坑开挖深度超过多少米时应进行专项施工方案论证？",
     "options": [{"label":"A","text":"3m"},{"label":"B","text":"5m"},{"label":"C","text":"8m"},{"label":"D","text":"10m"}],
     "answer": ["B"], "explanation": "根据《危险性较大的分部分项工程安全管理规定》，开挖深度超过5m的基坑属于危大工程，需进行专项方案论证。"},
    {"subject": "建筑工程施工技术", "chapter": "土方与基础工程", "type": "single", "difficulty": 3,
     "content": "预制桩施工中，锤击沉桩的收锤标准主要依据什么？",
     "options": [{"label":"A","text":"入土深度"},{"label":"B","text":"最后贯入度"},{"label":"C","text":"总锤击数"},{"label":"D","text":"桩身垂直度"}],
     "answer": ["B"], "explanation": "收锤标准主要依据最后贯入度，即最后10击的平均贯入深度，同时参考入土深度和总锤击数。"},
    {"subject": "建筑工程施工技术", "chapter": "混凝土结构施工", "type": "multi", "difficulty": 3,
     "content": "大体积混凝土施工控制温度裂缝的措施包括哪些？",
     "options": [{"label":"A","text":"选用低水化热水泥"},{"label":"B","text":"掺加缓凝减水剂"},{"label":"C","text":"分层浇筑"},{"label":"D","text":"加强养护"}],
     "answer": ["A","B","C","D"], "explanation": "大体积混凝土温度裂缝控制需综合采取多种措施。"},
    {"subject": "建筑工程施工技术", "chapter": "混凝土结构施工", "type": "single", "difficulty": 2,
     "content": "混凝土标准养护条件是什么？",
     "options": [{"label":"A","text":"20±2℃,≥95%湿度"},{"label":"B","text":"25±2℃,≥90%湿度"},{"label":"C","text":"20±2℃,≥90%湿度"},{"label":"D","text":"25±2℃,≥95%湿度"}],
     "answer": ["A"], "explanation": "标准养护条件为温度20±2℃，相对湿度95%以上。"},
    {"subject": "建筑工程施工技术", "chapter": "砌体工程施工", "type": "truefalse", "difficulty": 1,
     "content": "砌筑砂浆应随拌随用，水泥砂浆应在拌成后3小时内使用完毕。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["A"], "explanation": "水泥砂浆应在3h内用完，混合砂浆应在4h内用完。"},
    {"subject": "建筑工程施工技术", "chapter": "钢结构施工", "type": "composite", "difficulty": 4,
     "content": "简述钢结构安装过程中需要重点控制的质量要点。",
     "options": [], "answer": ["(1)构件进场验收，核对规格尺寸及质量证明文件；(2)基础验收，复核轴线、标高及地脚螺栓位置；(3)吊装过程中控制构件的变形和稳定性；(4)连接节点质量控制，包括焊接和螺栓连接；(5)安装偏差控制在规范允许范围内。"],
     "explanation": "钢结构安装质量控制涵盖从材料进场到最终安装的全过程。"},
    {"subject": "建筑工程施工技术", "chapter": "施工测量技术", "type": "truefalse", "difficulty": 1,
     "content": "水准仪的主要作用是测量两点之间的水平距离。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["B"], "explanation": "水准仪主要用于测量高差，而非水平距离。"},
    {"subject": "建筑工程施工技术", "chapter": "施工测量技术", "type": "single", "difficulty": 2,
     "content": "施工放线中轴线控制桩应设置在基槽边线以外多少米？",
     "options": [{"label":"A","text":"1-2m"},{"label":"B","text":"2-4m"},{"label":"C","text":"4-6m"},{"label":"D","text":"6-8m"}],
     "answer": ["B"], "explanation": "轴线控制桩一般设置在基槽边线以外2-4m处。"},
    {"subject": "建筑工程施工技术", "chapter": "防水工程施工", "type": "single", "difficulty": 2,
     "content": "屋面防水等级为I级的建筑，防水层合理使用年限是多少？",
     "options": [{"label":"A","text":"10年"},{"label":"B","text":"15年"},{"label":"C","text":"20年"},{"label":"D","text":"25年"}],
     "answer": ["D"], "explanation": "I级防水等级建筑防水层合理使用年限为25年。"},

    # ===== 建筑材料 =====
    {"subject": "建筑工程材料", "chapter": "水泥与混凝土", "type": "single", "difficulty": 2,
     "content": "普通硅酸盐水泥的初凝时间不得早于多少分钟？",
     "options": [{"label":"A","text":"30分钟"},{"label":"B","text":"45分钟"},{"label":"C","text":"60分钟"},{"label":"D","text":"90分钟"}],
     "answer": ["B"], "explanation": "根据GB 175-2007，普通硅酸盐水泥初凝时间不得早于45分钟。"},
    {"subject": "建筑工程材料", "chapter": "水泥与混凝土", "type": "multi", "difficulty": 3,
     "content": "影响混凝土强度的主要因素有哪些？",
     "options": [{"label":"A","text":"水灰比"},{"label":"B","text":"水泥强度等级"},{"label":"C","text":"养护条件"},{"label":"D","text":"骨料种类"}],
     "answer": ["A","B","C","D"], "explanation": "混凝土强度受水灰比、水泥强度、养护条件和骨料质量等综合影响。"},
    {"subject": "建筑工程材料", "chapter": "水泥与混凝土", "type": "composite", "difficulty": 4,
     "content": "请说明混凝土配合比设计的基本步骤。",
     "options": [], "answer": ["(1)确定配制强度；(2)确定水灰比；(3)确定单位用水量；(4)计算水泥用量；(5)确定砂率；(6)计算砂石用量；(7)试配、调整与确定。"],
     "explanation": "配合比设计需按规范逐步计算，并通过试配验证和调整。"},
    {"subject": "建筑工程材料", "chapter": "建筑钢材", "type": "single", "difficulty": 2,
     "content": "HRB400级钢筋中400表示什么含义？",
     "options": [{"label":"A","text":"抗拉强度400MPa"},{"label":"B","text":"屈服强度400MPa"},{"label":"C","text":"伸长率40%"},{"label":"D","text":"碳含量0.4%"}],
     "answer": ["B"], "explanation": "HRB400中400表示屈服强度特征值为400MPa。"},
    {"subject": "建筑工程材料", "chapter": "建筑钢材", "type": "truefalse", "difficulty": 1,
     "content": "Q235钢材的屈服强度为235MPa。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["A"], "explanation": "Q235钢的屈服强度为235MPa，数字即代表屈服强度值。"},
    {"subject": "建筑工程材料", "chapter": "砌体材料", "type": "single", "difficulty": 2,
     "content": "烧结普通砖的标准尺寸是多少？",
     "options": [{"label":"A","text":"240×115×53mm"},{"label":"B","text":"240×115×90mm"},{"label":"C","text":"190×190×90mm"},{"label":"D","text":"390×190×190mm"}],
     "answer": ["A"], "explanation": "烧结普通砖标准尺寸为240mm×115mm×53mm。"},
    {"subject": "建筑工程材料", "chapter": "防水材料", "type": "truefalse", "difficulty": 1,
     "content": "SBS改性沥青防水卷材适用于屋面和地下防水工程。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["A"], "explanation": "SBS改性沥青防水卷材具有良好的耐高低温性能。"},
    {"subject": "建筑工程材料", "chapter": "装饰装修材料", "type": "single", "difficulty": 2,
     "content": "室内装修材料甲醛释放限量标准是哪个？",
     "options": [{"label":"A","text":"GB 18580"},{"label":"B","text":"GB 50210"},{"label":"C","text":"GB 50300"},{"label":"D","text":"GB 50108"}],
     "answer": ["A"], "explanation": "GB 18580是室内装饰装修材料人造板甲醛释放限量的国家标准。"},

    # ===== 建筑法规 =====
    {"subject": "建筑法规与标准", "chapter": "建筑法律法规", "type": "single", "difficulty": 2,
     "content": "建筑工程开工前应向哪个部门申请施工许可证？",
     "options": [{"label":"A","text":"县级以上建设行政主管部门"},{"label":"B","text":"市级规划局"},{"label":"C","text":"省级住建厅"},{"label":"D","text":"国家住建部"}],
     "answer": ["A"], "explanation": "根据《建筑法》第七条，应向工程所在地县级以上建设行政主管部门申请。"},
    {"subject": "建筑法规与标准", "chapter": "施工规范", "type": "single", "difficulty": 2,
     "content": "混凝土结构工程施工质量验收规范的标准编号是什么？",
     "options": [{"label":"A","text":"GB 50204-2015"},{"label":"B","text":"GB 50300-2013"},{"label":"C","text":"GB 50203-2011"},{"label":"D","text":"GB 50108-2008"}],
     "answer": ["A"], "explanation": "GB 50204-2015是混凝土结构工程施工质量验收规范。"},
    {"subject": "建筑法规与标准", "chapter": "合同与招投标", "type": "truefalse", "difficulty": 1,
     "content": "依法必须招标的项目，招标文件发出至投标截止最短不少于20日。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["A"], "explanation": "根据《招标投标法》第二十四条，最短不少于20日。"},
    {"subject": "建筑法规与标准", "chapter": "工程验收标准", "type": "single", "difficulty": 2,
     "content": "建筑工程质量验收划分中最基本的验收单元是什么？",
     "options": [{"label":"A","text":"检验批"},{"label":"B","text":"分项工程"},{"label":"C","text":"分部工程"},{"label":"D","text":"单位工程"}],
     "answer": ["A"], "explanation": "检验批是建筑工程质量验收的最基本单元。"},

    # ===== 安全管理 =====
    {"subject": "建筑安全管理", "chapter": "施工安全管理", "type": "single", "difficulty": 2,
     "content": "施工现场的安全\"三宝\"是指什么？",
     "options": [{"label":"A","text":"安全帽、安全带、安全网"},{"label":"B","text":"安全帽、安全鞋、安全手套"},{"label":"C","text":"安全帽、防护眼镜、防护面罩"},{"label":"D","text":"安全绳、安全带、安全锁"}],
     "answer": ["A"], "explanation": "安全三宝是指安全帽、安全带和安全网。"},
    {"subject": "建筑安全管理", "chapter": "施工安全管理", "type": "composite", "difficulty": 4,
     "content": "简述施工现场安全检查的主要内容。",
     "options": [], "answer": ["(1)安全生产责任制落实情况；(2)安全教育培训情况；(3)安全技术交底执行情况；(4)危险性较大工程管理；(5)现场安全防护设施状况；(6)机械设备安全状况；(7)临时用电安全；(8)消防设施配备。"],
     "explanation": "安全检查应全面覆盖安全管理各环节，及时发现并消除安全隐患。"},
    {"subject": "建筑安全管理", "chapter": "高处作业防护", "type": "single", "difficulty": 2,
     "content": "高处作业是指坠落高度基准面多少米以上的作业？",
     "options": [{"label":"A","text":"1.5m"},{"label":"B","text":"2m"},{"label":"C","text":"3m"},{"label":"D","text":"5m"}],
     "answer": ["B"], "explanation": "根据《高处作业分级》，2m及以上为高处作业。"},
    {"subject": "建筑安全管理", "chapter": "消防安全", "type": "truefalse", "difficulty": 1,
     "content": "施工现场临时用房可以采用易燃材料搭建。",
     "options": [{"label":"A","text":"正确"},{"label":"B","text":"错误"}],
     "answer": ["B"], "explanation": "临时用房严禁采用易燃材料，必须使用不燃或难燃材料。"},
    {"subject": "建筑安全管理", "chapter": "应急预案管理", "type": "multi", "difficulty": 3,
     "content": "施工现场应急预案应包括哪些内容？",
     "options": [{"label":"A","text":"应急组织机构及职责"},{"label":"B","text":"危险源辨识与风险评估"},{"label":"C","text":"应急处置程序"},{"label":"D","text":"应急救援物资储备"}],
     "answer": ["A","B","C","D"], "explanation": "完整应急预案应包含组织体系、风险评估、处置程序、物资保障等。"},
    {"subject": "建筑安全管理", "chapter": "机械设备安全", "type": "single", "difficulty": 2,
     "content": "塔式起重机安装完成后应由哪个单位验收？",
     "options": [{"label":"A","text":"施工单位"},{"label":"B","text":"监理单位"},{"label":"C","text":"有资质的检测机构"},{"label":"D","text":"建设单位"}],
     "answer": ["C"], "explanation": "塔吊安装完成后须由有资质的检测机构验收检验。"},
]

count = 0
for q in questions:
    subj = subjects.get(q["subject"])
    if not subj: continue
    ch = chapter_lookup.get((q["subject"], q["chapter"]))
    if not ch: continue
    payload = {
        "subject_id": subj["id"],
        "chapter_id": ch["id"],
        "type": q["type"],
        "content": q["content"],
        "options": json.dumps(q["options"]),
        "answer": json.dumps(q["answer"]),
        "explanation": q["explanation"],
        "difficulty": q["difficulty"],
        "is_active": True,
    }
    r = api_post("/questions", json=payload)
    if r.status_code in (200, 201):
        count += 1
    else:
        print("  FAIL Q: " + q["content"][:30] + " - " + str(r.status_code))
print("Questions created: " + str(count))

# ====== STEP 6: Create exams ======
print("\n=== Step 6: Creating exams ===")
# Get all question IDs
r = api_get("/questions?page=1&page_size=200")
all_qids = [q["id"] for q in r.json().get("items", [])]

exams_data = [
    {"title": "建筑工程施工技术模拟考试(一)", "description": "模拟考试，不限次数，可查看答案解析", "mode": "mock",
     "duration_minutes": 90, "total_score": 100, "pass_score": 60,
     "subject_ids": [subjects["建筑工程施工技术"]["id"]], "count": 6},
    {"title": "建筑工程材料正式考试", "description": "正式考试，仅一次机会，开启防作弊监测", "mode": "formal",
     "duration_minutes": 60, "total_score": 50, "pass_score": 30,
     "subject_ids": [subjects["建筑工程材料"]["id"]], "count": 6},
    {"title": "建筑安全管理综合考试", "description": "包含单选多选判断和简答题", "mode": "formal",
     "duration_minutes": 120, "total_score": 100, "pass_score": 60,
     "subject_ids": [subjects["建筑安全管理"]["id"]], "count": 6},
    {"title": "建工综合模拟考试", "description": "全科目综合模拟", "mode": "mock",
     "duration_minutes": 120, "total_score": 100, "pass_score": 60,
     "subject_ids": [s["id"] for s in subjects.values()], "count": 10},
]

for ex in exams_data:
    # Filter questions by subject
    valid_qids = [qid for qid in all_qids if qid > 0]
    if len(valid_qids) < ex["count"]:
        ex["count"] = len(valid_qids)

    payload = {
        "title": ex["title"],
        "description": ex["description"],
        "mode": ex["mode"],
        "duration_minutes": ex["duration_minutes"],
        "total_score": ex["total_score"],
        "pass_score": ex["pass_score"],
        "subject_ids": ex["subject_ids"],
        "type_config": {"single": max(2, ex["count"]//2), "multi": max(1, ex["count"]//4),
                        "truefalse": max(1, ex["count"]//6), "composite": max(1, ex["count"]//8)},
        "difficulty_min": 1, "difficulty_max": 5,
        "max_tab_switches": 3,
    }
    r = api_post("/exams/generate", json=payload)
    if r.status_code in (200, 201):
        exam_data = r.json()
        # Publish it
        api_put("/exams/" + str(exam_data["id"]) + "/publish?is_published=true")
        print("  Created: " + ex["title"] + " (ID=" + str(exam_data["id"]) + ")")
    else:
        print("  FAIL: " + ex["title"] + " - " + str(r.text[:100]))

# ====== STEP 7: Create certificates ======
print("\n=== Step 7: Creating certificates ===")
# Exam certificates
exam_certs = [
    {"name": "建筑工程施工技术证书", "description": "通过施工技术正式考试获得", "cert_type": "exam"},
    {"name": "建筑材料知识证书", "description": "通过建筑材料正式考试获得", "cert_type": "exam"},
    {"name": "安全管理合格证书", "description": "通过安全管理综合考试获得", "cert_type": "exam"},
]
for ec in exam_certs:
    api_post("/certificates", json=ec)

# Practice certificates - one per chapter
for (subj_name, ch_name), ch in chapter_lookup.items():
    if subj_name == "建筑工程施工技术":
        api_post("/certificates", json={
            "name": ch_name + "练习证书",
            "description": subj_name + "·" + ch_name + "章节正确率达60%可申请",
            "cert_type": "practice",
            "chapter_id": ch["id"],
        })
print("Certificates created.")

# ====== STEP 8: Create announcements ======
print("\n=== Step 8: Creating announcements ===")
announcements = [
    {"title": "欢迎使用建筑工程考试系统", "content": "本系统支持在线练习、模拟考试、正式考试等多种学习模式。请各位学员认真刷题，按时参加考试。如有疑问请联系负责人。", "is_pinned": True, "is_published": True},
    {"title": "关于本月正式考试安排的通知", "content": "本月正式考试将于6月25日-6月30日进行，请各位学员提前做好复习准备。考试期间禁止切屏，违规操作将记录异常并可能取消成绩。", "is_pinned": False, "is_published": True},
    {"title": "系统新增复习模式功能", "content": "错题本现已支持复习模式，可将错题和收藏题目合并复习。练习中心也已新增复习模式入口。", "is_pinned": False, "is_published": True},
    {"title": "安全操作规范更新提醒", "content": "建筑安全管理相关题目已更新至最新规范标准，请关注新变化。", "is_pinned": False, "is_published": True},
]
for ann in announcements:
    api_post("/announcements", json=ann)
print("Announcements created.")

# ====== STEP 9: Create resources ======
print("\n=== Step 9: Creating learning resources ===")
resources = [
    {"title": "建筑施工技术讲义", "description": "全套施工技术学习资料", "subject_id": subjects["建筑工程施工技术"]["id"],
     "file_url": "https://example.com/construction-tech.pdf", "file_type": "pdf", "file_size": 2048000},
    {"title": "建筑材料速查手册", "description": "常用建筑材料规格参数速查", "subject_id": subjects["建筑工程材料"]["id"],
     "file_url": "https://example.com/materials-handbook.pdf", "file_type": "pdf", "file_size": 1536000},
    {"title": "建筑法规汇编2024版", "description": "最新建筑法律法规汇编", "subject_id": subjects["建筑法规与标准"]["id"],
     "file_url": "https://example.com/law-compilation.docx", "file_type": "docx", "file_size": 3072000},
    {"title": "安全防护示意图", "description": "施工现场安全防护标准图集", "subject_id": subjects["建筑安全管理"]["id"],
     "file_url": "https://example.com/safety-images.png", "file_type": "image", "file_size": 512000},
    {"title": "施工组织设计模板", "description": "施工组织设计标准模板下载", "subject_id": None,
     "file_url": "https://example.com/template.xlsx", "file_type": "xlsx", "file_size": 256000},
]
for res in resources:
    api_post("/resources", json=res)
print("Resources created.")

# ====== STEP 10: Create video courses ======
print("\n=== Step 10: Creating video courses ===")
videos = [
    {"title": "土方与基础工程施工实务", "description": "现场实操教学，讲解基坑开挖与支护要点", "subject_id": subjects["建筑工程施工技术"]["id"],
     "video_url": "https://example.com/video/excavation.mp4", "duration_seconds": 1800},
    {"title": "混凝土浇筑质量控制", "description": "混凝土施工全过程质量控制要点", "subject_id": subjects["建筑工程施工技术"]["id"],
     "video_url": "https://example.com/video/concrete.mp4", "duration_seconds": 2400},
    {"title": "建筑钢材识别与选用", "description": "常用建筑钢材种类、规格及选用原则", "subject_id": subjects["建筑工程材料"]["id"],
     "video_url": "https://example.com/video/steel.mp4", "duration_seconds": 1500},
    {"title": "施工现场安全管理实务", "description": "施工现场安全管理的核心要点与案例分析", "subject_id": subjects["建筑安全管理"]["id"],
     "video_url": "https://example.com/video/safety.mp4", "duration_seconds": 2100},
]
for vid in videos:
    api_post("/videos", json=vid)
print("Video courses created.")

# ====== STEP 11: Issue some certificates to zhangsan ======
print("\n=== Step 11: Issuing certificates ===")
r = api_get("/certificates")
all_certs = r.json()
r = api_get("/users")
all_users = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
zhangsan = next((u for u in all_users if u.get("username") == "zhangsan"), None)

if zhangsan and all_certs:
    # Issue first exam cert to zhangsan
    exam_cert = next((c for c in all_certs if c.get("cert_type") == "exam"), None)
    if exam_cert:
        api_post("/certificates/issue", params={
            "certificate_id": exam_cert["id"],
            "user_id": zhangsan["id"],
        })
        print("  Issued exam cert to zhangsan")

    # Issue a practice cert to zhangsan
    practice_cert = next((c for c in all_certs if c.get("cert_type") == "practice"), None)
    if practice_cert:
        api_post("/certificates/issue", params={
            "certificate_id": practice_cert["id"],
            "user_id": zhangsan["id"],
        })
        print("  Issued practice cert to zhangsan")

print("\n===== ALL DONE =====")
print("Summary:")
print("  Subjects: " + str(len(subjects)))
print("  Chapters: " + str(len(chapter_lookup)))
print("  Questions: " + str(count))
print("  Exams: " + str(len(exams_data)))
print("  Certificates: " + str(len(exam_certs)) + " exam + practice by chapter")
print("  Announcements: " + str(len(announcements)))
print("  Resources: " + str(len(resources)))
print("  Videos: " + str(len(videos)))
print("  Users: admin(admin/123) + zhangsan/lisi/wangwu(123456) + teacher1/fuzeren/shiyanyuan")
