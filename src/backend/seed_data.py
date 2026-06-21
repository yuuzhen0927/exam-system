#!/usr/bin/env python3
"""Seed data for 考试系统 - 建筑检测行业"""
import sqlite3, json, os, sys
from datetime import datetime, timezone
from passlib.context import CryptContext

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB = os.path.join(os.path.dirname(__file__), "exam.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

# ====== CLEAR ALL DATA ======
tables = [
    "users","subjects","chapters","questions","exams","exam_templates","exam_results",
    "announcements","certificates","user_certificates","roles","practice_records",
    "resources","operation_logs","retake_applications","video_courses","abnormal_reports",
    "question_versions","wrong_answers","favorites","notes","question_feedbacks","video_progress"
]
for t in tables:
    cur.execute(f"DELETE FROM {t}")
# Reset autoincrement
for t in tables:
    try:
        cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
    except:
        pass
conn.commit()
print("All data cleared.")

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# USERS (7 users)
# ==========================================
users = [
    ("admin", pwd.hash("admin123"), "系统管理员", "admin"),
    ("zhangsan", pwd.hash("123456"), "张三", "student"),
    ("lisi", pwd.hash("123456"), "李四", "student"),
    ("wangwu", pwd.hash("123456"), "王五", "student"),
    ("fuzeren", pwd.hash("123456"), "陈负责人", "teacher"),
    ("jianceyuan", pwd.hash("123456"), "林检测员", "student"),
    ("shenheyuan", pwd.hash("123456"), "周审核员", "teacher"),
]
for u in users:
    cur.execute(
        "INSERT INTO users(username,hashed_password,fullname,role,is_active,created_at) VALUES(?,?,?,?,1,?)",
        (u[0], u[1], u[2], u[3], now))
conn.commit()
print(f"Created {len(users)} users.")

# ==========================================
# ROLES (6 roles)
# ==========================================
roles = [
    ("admin", "系统管理员 - 拥有全部权限", 1, 1, 1),
    ("teacher", "负责人 - 可管理教学内容与考试运营", 1, 0, 2),
    ("student", "学生 - 学习与考试", 0, 0, 3),
    ("inspector", "检测员 - 专项学习人员", 0, 0, 4),
    ("reviewer", "审核员 - 可审核考试与证书", 1, 0, 5),
    ("viewer", "只读用户 - 仅可查看", 0, 0, 6),
]
for name, desc, mgr, sys_flag, sort in roles:
    cur.execute(
        "INSERT INTO roles(name,description,is_manager,is_system,sort_order,created_at) VALUES(?,?,?,?,?,?)",
        (name, desc, mgr, sys_flag, sort, now))
conn.commit()

# Assign roles to users
cur.execute("UPDATE users SET role='admin' WHERE username='admin'")
cur.execute("UPDATE users SET role='teacher' WHERE username IN ('fuzeren','shenheyuan')")
cur.execute("UPDATE users SET role='student' WHERE username IN ('zhangsan','lisi','wangwu','jianceyuan')")
conn.commit()

# ==========================================
# SUBJECTS (5)
# ==========================================
subjects = [
    ("建筑材料检测", "水泥、混凝土、钢材、防水材料等建筑材料的检测方法与标准"),
    ("主体结构检测", "混凝土结构、砌体结构、钢结构现场检测技术"),
    ("地基基础检测", "桩基检测、地基承载力、基坑监测"),
    ("建筑节能检测", "围护结构热工性能、门窗气密性、保温材料检测"),
    ("室内环境检测", "甲醛、TVOC、氨气等室内污染物检测"),
]
for i, (name, desc) in enumerate(subjects, 1):
    cur.execute(
        "INSERT INTO subjects(id,name,description,sort_order,created_at) VALUES(?,?,?,?,?)",
        (i, name, desc, i, now))
conn.commit()
print(f"Created {len(subjects)} subjects.")

# ==========================================
# CHAPTERS (16)
# ==========================================
chapters = [
    (1, 1, "水泥物理性能检测", "水泥细度、凝结时间、安定性、强度检测"),
    (2, 1, "混凝土原材料检测", "骨料、外加剂、掺合料检测"),
    (3, 1, "钢材力学性能检测", "拉伸、弯曲、冲击、硬度试验"),
    (4, 1, "防水材料检测", "卷材、涂料、密封材料检测"),
    (5, 2, "混凝土强度检测", "回弹法、钻芯法、超声波法"),
    (6, 2, "钢筋保护层厚度检测", "电磁感应法、雷达法"),
    (7, 2, "钢结构焊缝检测", "超声波探伤、射线探伤、磁粉探伤"),
    (8, 3, "桩基静载试验", "单桩竖向抗压、抗拔静载试验"),
    (9, 3, "低应变检测", "桩身完整性检测"),
    (10, 3, "地基承载力检测", "平板荷载试验、动力触探"),
    (11, 4, "围护结构热工缺陷检测", "红外热像法"),
    (12, 4, "门窗气密性检测", "现场气密性检测方法"),
    (13, 5, "甲醛检测", "AHMT分光光度法、酚试剂分光光度法"),
    (14, 5, "TVOC检测", "热解吸-毛细管气相色谱法"),
    (15, 5, "氨气检测", "靛酚蓝分光光度法"),
    (16, 5, "氡气检测", "闪烁瓶法、径迹蚀刻法"),
]
for cid, sid, name, desc in chapters:
    cur.execute(
        "INSERT INTO chapters(id,subject_id,name,description,sort_order,created_at) VALUES(?,?,?,?,?,?)",
        (cid, sid, name, desc, cid, now))
conn.commit()
print(f"Created {len(chapters)} chapters.")

# ==========================================
# QUESTIONS (120 questions)
# ==========================================
questions = []
qid = 0

def add_q(qtype, content, answer, options=None, explanation="", subject_id=1, chapter_id=1, difficulty=2, specialty=""):
    global qid
    qid += 1
    opts = json.dumps(options) if isinstance(options, list) and options else (
        json.dumps([]) if qtype == "composite" else (options if options else "")
    )
    ans = answer
    if qtype == "composite" and isinstance(answer, list):
        ans = json.dumps(answer)
    questions.append((qtype, content, ans, opts, explanation, subject_id, chapter_id, difficulty, specialty))

# --- Chapter 1: 水泥物理性能检测 (12 questions) ---
add_q("single", "水泥细度用负压筛析法检测时，试验筛的筛孔尺寸为多少？", "B",
    [{"label":"A","text":"45μm"},{"label":"B","text":"80μm"},{"label":"C","text":"100μm"},{"label":"D","text":"125μm"}],
    "GB/T 1345规定水泥细度检测使用80μm方孔筛。", 1, 1, 1)

add_q("single", "水泥标准稠度用水量测定中，试锥下沉深度应为多少？", "C",
    [{"label":"A","text":"20±2mm"},{"label":"B","text":"25±3mm"},{"label":"C","text":"28±2mm"},{"label":"D","text":"30±3mm"}],
    "GB/T 1346规定试锥下沉深度28±2mm时的用水量为标准稠度用水量。", 1, 1, 2)

add_q("single", "硅酸盐水泥的初凝时间不得早于多少分钟？", "C",
    [{"label":"A","text":"30min"},{"label":"B","text":"40min"},{"label":"C","text":"45min"},{"label":"D","text":"60min"}],
    "GB 175规定硅酸盐水泥初凝时间不得早于45min。", 1, 1, 1)

add_q("single", "水泥胶砂强度试验中，水灰比为多少？", "A",
    [{"label":"A","text":"0.50"},{"label":"B","text":"0.45"},{"label":"C","text":"0.55"},{"label":"D","text":"0.40"}],
    "ISO法规定水灰比为0.50（适用于硅酸盐水泥和普通硅酸盐水泥）。", 1, 1, 2)

add_q("single", "水泥安定性检测采用何种方法？", "C",
    [{"label":"A","text":"筛析法"},{"label":"B","text":"比表面积法"},{"label":"C","text":"雷氏夹法"},{"label":"D","text":"负压筛法"}],
    "GB/T 1346规定用雷氏夹法或试饼法检测水泥安定性。", 1, 1, 1)

add_q("single", "P.O 42.5水泥的28d抗压强度不低于多少？", "B",
    [{"label":"A","text":"32.5MPa"},{"label":"B","text":"42.5MPa"},{"label":"C","text":"52.5MPa"},{"label":"D","text":"62.5MPa"}],
    "GB 175规定42.5等级水泥28d抗压强度≥42.5MPa。", 1, 1, 2)

add_q("multi", "以下哪些属于水泥物理性能检测项目？", "ABC",
    [{"label":"A","text":"细度"},{"label":"B","text":"凝结时间"},{"label":"C","text":"安定性"},{"label":"D","text":"化学分析"}],
    "水泥物理性能检测包括细度、凝结时间、安定性、强度等。", 1, 1, 2)

add_q("multi", "影响水泥凝结时间的因素有：", "ABCD",
    [{"label":"A","text":"水灰比"},{"label":"B","text":"环境温度"},{"label":"C","text":"石膏掺量"},{"label":"D","text":"水泥细度"}],
    "以上因素均影响水泥凝结时间。", 1, 1, 3)

add_q("truefalse", "水泥安定性不合格的水泥可以降级使用。", "false",
    [], "安定性不合格的水泥严禁使用，不得降级处理。GB 175强制性条款。", 1, 1, 2)

add_q("truefalse", "水泥胶砂强度试验的试件尺寸为40mm×40mm×160mm。", "true",
    [], "GB/T 17671规定胶砂强度试件为40mm×40mm×160mm棱柱体。", 1, 1, 1)

add_q("single", "水泥比表面积测定常用什么方法？", "B",
    [{"label":"A","text":"筛析法"},{"label":"B","text":"勃氏法"},{"label":"C","text":"沉降法"},{"label":"D","text":"激光法"}],
    "GB/T 8074规定使用勃氏透气法测定水泥比表面积。", 1, 1, 3)

add_q("single", "水泥终凝时间不得超过多少小时？", "D",
    [{"label":"A","text":"6h"},{"label":"B","text":"8h"},{"label":"C","text":"10h"},{"label":"D","text":"12h"}],
    "GB 175规定终凝时间不得迟于12h（硅酸盐水泥为6.5h）。", 1, 1, 2)

# --- Chapter 2: 混凝土原材料检测 (10 questions) ---
add_q("single", "混凝土用砂的细度模数在哪个范围属于中砂？", "C",
    [{"label":"A","text":"1.6～2.2"},{"label":"B","text":"2.0～2.8"},{"label":"C","text":"2.3～3.0"},{"label":"D","text":"3.1～3.7"}],
    "JGJ 52规定中砂细度模数为2.3～3.0。", 1, 2, 1)

add_q("single", "混凝土抗压强度标准试件尺寸为：", "B",
    [{"label":"A","text":"100mm×100mm×100mm"},{"label":"B","text":"150mm×150mm×150mm"},{"label":"C","text":"200mm×200mm×200mm"},{"label":"D","text":"70.7mm×70.7mm×70.7mm"}],
    "GB/T 50081规定混凝土标准试件为150mm立方体。", 1, 2, 1)

add_q("single", "泵送混凝土的砂率宜为多少？", "D",
    [{"label":"A","text":"20%～30%"},{"label":"B","text":"25%～35%"},{"label":"C","text":"30%～40%"},{"label":"D","text":"35%～45%"}],
    "JGJ/T 10规定泵送混凝土砂率宜为35%～45%。", 1, 2, 2)

add_q("single", "混凝土坍落度试验分层装料，每层插捣多少次？", "B",
    [{"label":"A","text":"15次"},{"label":"B","text":"25次"},{"label":"C","text":"30次"},{"label":"D","text":"35次"}],
    "GB/T 50080规定每层由边缘向中心螺旋插捣25次。", 1, 2, 2)

add_q("multi", "混凝土用粗骨料的质量指标包括：", "ABCD",
    [{"label":"A","text":"针片状颗粒含量"},{"label":"B","text":"含泥量"},{"label":"C","text":"压碎指标"},{"label":"D","text":"坚固性"}],
    "以上均为粗骨料质量检测指标。", 1, 2, 2)

add_q("multi", "影响混凝土强度的因素有：", "ABCD",
    [{"label":"A","text":"水灰比"},{"label":"B","text":"水泥强度等级"},{"label":"C","text":"养护条件"},{"label":"D","text":"龄期"}],
    "以上因素均影响混凝土强度。", 1, 2, 1)

add_q("truefalse", "混凝土坍落度越大，表示流动性越好。", "true",
    [], "坍落度是衡量混凝土流动性的重要指标，坍落度越大流动性越好。", 1, 2, 1)

add_q("truefalse", "混凝土用砂的含泥量越高越好。", "false",
    [], "含泥量过高会影响混凝土强度和耐久性，应控制在一定范围内。", 1, 2, 1)

add_q("single", "混凝土外加剂减水率试验中，基准混凝土坍落度控制在多少？", "B",
    [{"label":"A","text":"60±10mm"},{"label":"B","text":"80±10mm"},{"label":"C","text":"100±10mm"},{"label":"D","text":"120±10mm"}],
    "GB 8076规定基准混凝土坍落度控制在80±10mm。", 1, 2, 3)

add_q("single", "C30混凝土的含义是什么？", "A",
    [{"label":"A","text":"立方体抗压强度标准值为30MPa"},{"label":"B","text":"轴心抗压强度为30MPa"},{"label":"C","text":"抗拉强度为30MPa"},{"label":"D","text":"抗折强度为30MPa"}],
    "C30表示混凝土立方体抗压强度标准值为30N/mm²。", 1, 2, 1)

# --- Chapter 3: 钢材力学性能检测 (10 questions) ---
add_q("single", "Q235B钢材的屈服强度不低于多少MPa？", "B",
    [{"label":"A","text":"215MPa"},{"label":"B","text":"235MPa"},{"label":"C","text":"345MPa"},{"label":"D","text":"390MPa"}],
    "Q235表示屈服强度≥235MPa。", 1, 3, 1)

add_q("single", "钢筋拉伸试验中，断后伸长率用什么符号表示？", "C",
    [{"label":"A","text":"ReH"},{"label":"B","text":"Rm"},{"label":"C","text":"A"},{"label":"D","text":"Z"}],
    "GB/T 228.1规定断后伸长率用A表示。", 1, 3, 2)

add_q("single", "HRB400钢筋的屈服强度特征值为多少？", "C",
    [{"label":"A","text":"300MPa"},{"label":"B","text":"335MPa"},{"label":"C","text":"400MPa"},{"label":"D","text":"500MPa"}],
    "HRB400表示热轧带肋钢筋，屈服强度特征值为400MPa。", 1, 3, 1)

add_q("single", "钢筋弯曲试验的弯心直径一般取钢筋直径的多少倍？", "C",
    [{"label":"A","text":"1～2倍"},{"label":"B","text":"2～3倍"},{"label":"C","text":"3～5倍"},{"label":"D","text":"5～7倍"}],
    "GB/T 232规定弯心直径根据钢筋牌号取3～5d。", 1, 3, 2)

add_q("multi", "钢筋力学性能检测包括：", "ABCD",
    [{"label":"A","text":"屈服强度"},{"label":"B","text":"抗拉强度"},{"label":"C","text":"伸长率"},{"label":"D","text":"冷弯性能"}],
    "以上均为钢筋力学性能检测项目。", 1, 3, 2)

add_q("multi", "以下哪些因素影响钢材的拉伸试验结果？", "ABC",
    [{"label":"A","text":"加载速率"},{"label":"B","text":"试件尺寸"},{"label":"C","text":"试验温度"},{"label":"D","text":"大气压力"}],
    "大气压力对拉伸试验无显著影响。加载速率、尺寸、温度均有影响。", 1, 3, 3)

add_q("truefalse", "钢材拉伸试验中，上屈服强度ReH一定大于下屈服强度ReL。", "true",
    [], "上屈服强度是试样发生屈服而力首次下降前的最高应力，总是大于下屈服强度。", 1, 3, 2)

add_q("truefalse", "HRB400钢筋的抗拉强度与屈服强度之比不应小于1.25。", "true",
    [], "GB 1499.2规定HRB400钢筋Rm/ReL≥1.25（强屈比）。", 1, 3, 2)

add_q("single", "钢筋的最大力总延伸率要求不小于多少？", "B",
    [{"label":"A","text":"5%"},{"label":"B","text":"7.5%"},{"label":"C","text":"10%"},{"label":"D","text":"12%"}],
    "GB 1499.2规定最大力总延伸率Agt≥7.5%。", 1, 3, 3)

add_q("single", "金属材料夏比冲击试验的缺口类型不包括：", "D",
    [{"label":"A","text":"V型缺口"},{"label":"B","text":"U型缺口"},{"label":"C","text":"钥匙孔型"},{"label":"D","text":"圆形缺口"}],
    "GB/T 229规定的标准缺口为V型、U型和钥匙孔型。", 1, 3, 3)

# --- Chapter 4: 防水材料检测 (8 questions) ---
add_q("single", "SBS改性沥青防水卷材的低温柔度试验温度通常为多少？", "C",
    [{"label":"A","text":"0℃"},{"label":"B","text":"-5℃"},{"label":"C","text":"-18℃"},{"label":"D","text":"-25℃"}],
    "GB 18242规定SBS卷材低温柔度为-18℃（I型）。", 1, 4, 2)

add_q("single", "聚氨酯防水涂料的固含量应不小于多少？", "A",
    [{"label":"A","text":"80%"},{"label":"B","text":"70%"},{"label":"C","text":"90%"},{"label":"D","text":"60%"}],
    "GB/T 19250规定单组分聚氨酯防水涂料固含量≥80%。", 1, 4, 2)

add_q("multi", "防水卷材的物理性能检测项目包括：", "ABC",
    [{"label":"A","text":"不透水性"},{"label":"B","text":"耐热性"},{"label":"C","text":"拉力及延伸率"},{"label":"D","text":"放射性"}],
    "放射性不属于防水卷材常规检测项目。", 1, 4, 2)

add_q("multi", "建筑防水材料按形态可分为：", "ABCD",
    [{"label":"A","text":"防水卷材"},{"label":"B","text":"防水涂料"},{"label":"C","text":"密封材料"},{"label":"D","text":"刚性防水材料"}],
    "以上均为建筑防水材料的分类。", 1, 4, 1)

add_q("truefalse", "自粘聚合物改性沥青防水卷材不需要热熔施工。", "true",
    [], "自粘卷材通过冷自粘施工，不需要热熔。", 1, 4, 1)

add_q("truefalse", "防水涂料施工前基层必须干燥。", "true",
    [], "基层含水率过高会影响防水涂料的粘结效果。", 1, 4, 1)

add_q("single", "弹性体改性沥青防水卷材的拉力试验，试件宽度为多少？", "B",
    [{"label":"A","text":"25mm"},{"label":"B","text":"50mm"},{"label":"C","text":"75mm"},{"label":"D","text":"100mm"}],
    "GB 18242规定试件宽度为50mm。", 1, 4, 3)

add_q("single", "防水卷材耐热性试验温度，I型要求为多少？", "C",
    [{"label":"A","text":"70℃"},{"label":"B","text":"80℃"},{"label":"C","text":"90℃"},{"label":"D","text":"100℃"}],
    "GB 18242规定I型SBS卷材耐热度为90℃。", 1, 4, 2)

# --- Chapter 5: 混凝土强度检测 (10 questions) ---
add_q("single", "回弹法检测混凝土强度时，测区面积不宜大于多少？", "D",
    [{"label":"A","text":"0.01m²"},{"label":"B","text":"0.02m²"},{"label":"C","text":"0.03m²"},{"label":"D","text":"0.04m²"}],
    "JGJ/T 23规定每个测区面积不宜大于0.04m²。", 2, 5, 2)

add_q("single", "钻芯法检测混凝土强度，芯样直径不宜小于骨料最大粒径的多少倍？", "C",
    [{"label":"A","text":"1倍"},{"label":"B","text":"2倍"},{"label":"C","text":"3倍"},{"label":"D","text":"4倍"}],
    "CECS 03规定芯样直径不宜小于骨料最大粒径的3倍。", 2, 5, 2)

add_q("single", "超声回弹综合法检测混凝土强度，测试面应选择在？", "B",
    [{"label":"A","text":"任意面"},{"label":"B","text":"浇筑侧面"},{"label":"C","text":"浇筑面"},{"label":"D","text":"底面"}],
    "应优先选择混凝土浇筑侧面进行检测。", 2, 5, 3)

add_q("multi", "回弹法检测混凝土强度的修正因素包括：", "ABCD",
    [{"label":"A","text":"碳化深度"},{"label":"B","text":"浇筑面"},{"label":"C","text":"泵送"},{"label":"D","text":"混凝土龄期"}],
    "以上因素均影响回弹值，需要进行修正。", 2, 5, 3)

add_q("truefalse", "回弹法可以直接测定混凝土的抗压强度。", "false",
    [], "回弹法是通过回弹值与抗压强度之间的相关关系推算强度，不是直接测定。", 2, 5, 2)

add_q("single", "回弹法检测时，每个测区应记录多少个回弹值？", "C",
    [{"label":"A","text":"10个"},{"label":"B","text":"12个"},{"label":"C","text":"16个"},{"label":"D","text":"20个"}],
    "JGJ/T 23规定每个测区记录16个回弹值。", 2, 5, 1)

add_q("single", "钻芯法检测时，芯样高径比宜为多少？", "A",
    [{"label":"A","text":"1.0"},{"label":"B","text":"1.5"},{"label":"C","text":"2.0"},{"label":"D","text":"2.5"}],
    "CECS 03规定标准芯样高径比为1.0。", 2, 5, 2)

add_q("truefalse", "回弹仪在使用前必须在钢砧上进行率定。", "true",
    [], "回弹仪使用前后都应在钢砧上率定，率定值应为80±2。", 2, 5, 1)

add_q("multi", "混凝土强度的无损检测方法包括：", "ABC",
    [{"label":"A","text":"回弹法"},{"label":"B","text":"超声法"},{"label":"C","text":"超声回弹综合法"},{"label":"D","text":"拉伸试验"}],
    "拉伸试验是破坏性检测。", 2, 5, 2)

add_q("single", "回弹法检测混凝土强度，碳化深度测量精度为多少？", "B",
    [{"label":"A","text":"0.1mm"},{"label":"B","text":"0.25mm"},{"label":"C","text":"0.5mm"},{"label":"D","text":"1.0mm"}],
    "JGJ/T 23规定碳化深度测量精度为0.25mm。", 2, 5, 2)

# --- Chapter 6: 钢筋保护层厚度检测 (6 questions) ---
add_q("single", "电磁感应法检测钢筋保护层厚度，适用的钢筋直径范围为：", "B",
    [{"label":"A","text":"4～15mm"},{"label":"B","text":"6～50mm"},{"label":"C","text":"10～30mm"},{"label":"D","text":"12～32mm"}],
    "JGJ/T 152规定电磁感应法适用钢筋直径6～50mm。", 2, 6, 2)

add_q("single", "钢筋保护层厚度检测，每个检测构件的测点不应少于多少个？", "C",
    [{"label":"A","text":"3个"},{"label":"B","text":"4个"},{"label":"C","text":"5个"},{"label":"D","text":"6个"}],
    "GB 50204规定每个构件测点不应少于5个。", 2, 6, 2)

add_q("truefalse", "雷达法可以检测双层钢筋的保护层厚度。", "true",
    [], "雷达法具有较高分辨率，可检测双层钢筋网的保护层厚度。", 2, 6, 3)

add_q("single", "电磁感应法检测保护层厚度，检测前需在标准块上校准，标准块厚度应覆盖检测范围的多少？", "D",
    [{"label":"A","text":"50%"},{"label":"B","text":"70%"},{"label":"C","text":"90%"},{"label":"D","text":"100%"}],
    "标准块厚度应能覆盖被测保护层厚度的全范围。", 2, 6, 3)

add_q("truefalse", "保护层厚度检测允许偏差为+10mm、-7mm。", "true",
    [], "GB 50204规定梁类构件保护层厚度允许偏差为+10mm、-7mm。", 2, 6, 1)

add_q("multi", "检测钢筋位置和保护层厚度可采用：", "ABC",
    [{"label":"A","text":"电磁感应法"},{"label":"B","text":"雷达法"},{"label":"C","text":"剔凿验证法"},{"label":"D","text":"回弹法"}],
    "回弹法用于检测混凝土强度，不用于检测保护层厚度。", 2, 6, 2)

# --- Chapter 7: 钢结构焊缝检测 (8 questions) ---
add_q("single", "钢结构焊缝超声波探伤，使用的探头频率通常为：", "C",
    [{"label":"A","text":"1MHz"},{"label":"B","text":"2MHz"},{"label":"C","text":"2.5～5MHz"},{"label":"D","text":"10MHz"}],
    "GB/T 11345规定常用频率为2.5～5MHz。", 2, 7, 2)

add_q("single", "焊缝质量等级分为几级？", "C",
    [{"label":"A","text":"二级"},{"label":"B","text":"三级"},{"label":"C","text":"四级"},{"label":"D","text":"五级"}],
    "GB 50661规定焊缝质量分为一级、二级、三级、四级。", 2, 7, 2)

add_q("multi", "常用的焊缝无损检测方法包括：", "ABC",
    [{"label":"A","text":"超声波探伤"},{"label":"B","text":"射线探伤"},{"label":"C","text":"磁粉探伤"},{"label":"D","text":"拉伸试验"}],
    "拉伸试验是破坏性检测，不属于无损检测。", 2, 7, 2)

add_q("truefalse", "一级焊缝必须进行100%无损检测。", "true",
    [], "GB 50661规定一级焊缝应进行100%超声波检测。", 2, 7, 1)

add_q("single", "超声波探伤时，距离-波幅曲线的判废线比定量线高多少dB？", "B",
    [{"label":"A","text":"3dB"},{"label":"B","text":"6dB"},{"label":"C","text":"9dB"},{"label":"D","text":"12dB"}],
    "判废线比定量线高6dB，定量线比评定线高6dB。", 2, 7, 3)

add_q("truefalse", "磁粉探伤只适用于铁磁性材料的表面和近表面缺陷检测。", "true",
    [], "磁粉探伤仅适用于铁磁性材料。", 2, 7, 2)

add_q("single", "射线探伤评定底片时，评为III级的焊缝允许存在哪种缺陷？", "C",
    [{"label":"A","text":"裂纹"},{"label":"B","text":"未熔合"},{"label":"C","text":"圆形缺陷"},{"label":"D","text":"未焊透"}],
    "裂纹、未熔合、未焊透均为不允许缺陷。III级允许一定数量的圆形缺陷。", 2, 7, 3)

add_q("multi", "超声波探伤仪的主要性能指标包括：", "ABCD",
    [{"label":"A","text":"水平线性"},{"label":"B","text":"垂直线性"},{"label":"C","text":"灵敏度余量"},{"label":"D","text":"分辨力"}],
    "以上均为超声波探伤仪的重要性能指标。", 2, 7, 3)

# --- Chapter 8: 桩基静载试验 (8 questions) ---
add_q("single", "单桩竖向抗压静载试验，加载应分几级进行？", "C",
    [{"label":"A","text":"5级"},{"label":"B","text":"8级"},{"label":"C","text":"10级"},{"label":"D","text":"12级"}],
    "JGJ 106规定加载应分10级进行，每级为最大加载量的1/10。", 3, 8, 2)

add_q("single", "单桩竖向抗压静载试验，每级加载后的稳定标准是什么？", "A",
    [{"label":"A","text":"桩顶沉降速率≤0.1mm/h"},{"label":"B","text":"桩顶沉降速率≤0.5mm/h"},{"label":"C","text":"桩顶沉降速率≤1mm/h"},{"label":"D","text":"桩顶沉降速率≤2mm/h"}],
    "JGJ 106规定连续两次每小时内桩顶沉降量≤0.1mm时可加下一级荷载。", 3, 8, 3)

add_q("multi", "桩基静载试验可以测定桩的哪些参数？", "ABC",
    [{"label":"A","text":"单桩竖向抗压承载力"},{"label":"B","text":"桩侧摩阻力"},{"label":"C","text":"桩端阻力"},{"label":"D","text":"桩身混凝土强度"}],
    "静载试验主要测定承载力相关参数，混凝土强度需钻芯法检测。", 3, 8, 3)

add_q("truefalse", "静载试验的终止条件之一是某级荷载下沉降量为前一级的5倍且总沉降量≥40mm。", "true",
    [], "JGJ 106规定的终止加载条件之一。", 3, 8, 2)

add_q("single", "单桩竖向抗拔静载试验，加载反力装置提供的反力不得小于最大加载量的多少倍？", "C",
    [{"label":"A","text":"1.0倍"},{"label":"B","text":"1.1倍"},{"label":"C","text":"1.2倍"},{"label":"D","text":"1.5倍"}],
    "JGJ 106规定反力装置提供的反力不小于最大加载量的1.2倍。", 3, 8, 2)

add_q("truefalse", "为设计提供依据的试验桩应加载至桩侧与桩端的岩土阻力达到极限状态。", "true",
    [], "设计提供依据的试桩应加载至极限状态。", 3, 8, 3)

add_q("single", "静载试验的基准梁应具有足够的刚度，其两端应简支于基准桩上，基准桩与试桩中心的距离不小于多少？", "D",
    [{"label":"A","text":"2d"},{"label":"B","text":"3d"},{"label":"C","text":"3d且≥1.5m"},{"label":"D","text":"4d且≥2.0m"}],
    "JGJ 106规定基准桩与试桩中心距离≥4d且≥2.0m。", 3, 8, 3)

add_q("single", "工程桩验收检测时，加载量不应小于设计要求的单桩承载力特征值的多少倍？", "C",
    [{"label":"A","text":"1.0倍"},{"label":"B","text":"1.5倍"},{"label":"C","text":"2.0倍"},{"label":"D","text":"2.5倍"}],
    "JGJ 106规定工程桩验收检测加载量≥2.0Ra。", 3, 8, 2)

# --- Chapter 9: 低应变检测 (6 questions) ---
add_q("single", "低应变法检测桩身完整性，使用什么作为激振源？", "A",
    [{"label":"A","text":"手锤或力棒"},{"label":"B","text":"超声波"},{"label":"C","text":"振动台"},{"label":"D","text":"爆破"}],
    "低应变法使用手锤或力棒在桩顶施加瞬态激振。", 3, 9, 2)

add_q("truefalse", "低应变法可用于检测桩身混凝土强度。", "false",
    [], "低应变法仅用于检测桩身完整性，不能检测混凝土强度。", 3, 9, 2)

add_q("single", "低应变法检测，I类桩的定义是什么？", "A",
    [{"label":"A","text":"桩身完整"},{"label":"B","text":"有轻微缺陷"},{"label":"C","text":"有严重缺陷"},{"label":"D","text":"断桩"}],
    "I类桩桩身完整，II类有轻微缺陷不影响使用，III类有明显缺陷，IV类严重缺陷或断桩。", 3, 9, 1)

add_q("multi", "低应变法能检测的项目包括：", "AB",
    [{"label":"A","text":"桩身完整性"},{"label":"B","text":"缺陷位置"},{"label":"C","text":"混凝土强度"},{"label":"D","text":"承载力"}],
    "低应变法检测桩身完整性和缺陷位置，不能检测强度和承载力。", 3, 9, 2)

add_q("truefalse", "低应变检测时，传感器应安装在距桩中心2/3半径处。", "true",
    [], "JGJ 106规定传感器安装点与锤击点应在桩心对称位置，距桩中心约2/3半径。", 3, 9, 3)

add_q("single", "低应变法检测桩身完整性，每根桩的检测信号数不宜少于多少？", "B",
    [{"label":"A","text":"2个"},{"label":"B","text":"3个"},{"label":"C","text":"5个"},{"label":"D","text":"7个"}],
    "每根被检桩的有效信号数不宜少于3个。", 3, 9, 2)

# --- Chapter 10: 地基承载力检测 (6 questions) ---
add_q("single", "平板荷载试验的承压板面积，对于一般粘性土不应小于多少？", "C",
    [{"label":"A","text":"0.1m²"},{"label":"B","text":"0.2m²"},{"label":"C","text":"0.25m²"},{"label":"D","text":"0.5m²"}],
    "GB 50007规定承压板面积不应小于0.25m²。", 3, 10, 3)

add_q("single", "重型动力触探的锤质量为多少？", "C",
    [{"label":"A","text":"10kg"},{"label":"B","text":"28kg"},{"label":"C","text":"63.5kg"},{"label":"D","text":"120kg"}],
    "重型动力触探采用63.5kg锤，落距760mm。", 3, 10, 2)

add_q("multi", "动力触探试验可用于：", "ABC",
    [{"label":"A","text":"评定土的密实度"},{"label":"B","text":"估算地基承载力"},{"label":"C","text":"判断土的均匀性"},{"label":"D","text":"测定土的化学成分"}],
    "动力触探不能测定化学成分。", 3, 10, 2)

add_q("truefalse", "平板荷载试验的试验点应避开地下管线和基础。", "true",
    [], "试验点应避开地下设施，保证试验安全和数据准确。", 3, 10, 1)

add_q("single", "标准贯入试验使用的锤质量为多少？", "B",
    [{"label":"A","text":"28.5kg"},{"label":"B","text":"63.5kg"},{"label":"C","text":"76kg"},{"label":"D","text":"100kg"}],
    "标准贯入试验使用63.5kg锤，落距760mm。", 3, 10, 2)

add_q("truefalse", "标准贯入试验的锤击数越大，说明土越密实。", "true",
    [], "锤击数N值与土的密实度和强度正相关。", 3, 10, 1)

# --- Chapter 11: 围护结构热工缺陷检测 (6 questions) ---
add_q("single", "红外热像法检测围护结构热工缺陷，检测时室内外温差不宜小于多少？", "C",
    [{"label":"A","text":"5℃"},{"label":"B","text":"8℃"},{"label":"C","text":"10℃"},{"label":"D","text":"15℃"}],
    "JGJ/T 177规定室内外温差不宜小于10℃。", 4, 11, 2)

add_q("single", "红外热像仪检测热工缺陷，拍摄距离不宜超过多少米？", "C",
    [{"label":"A","text":"3m"},{"label":"B","text":"5m"},{"label":"C","text":"10m"},{"label":"D","text":"15m"}],
    "拍摄距离不宜超过10m以保证图像质量。", 4, 11, 3)

add_q("multi", "围护结构热工缺陷检测可采用的方法有：", "AB",
    [{"label":"A","text":"红外热像法"},{"label":"B","text":"热流计法"},{"label":"C","text":"回弹法"},{"label":"D","text":"超声波法"}],
    "热工缺陷检测主要使用红外热像法和热流计法。", 4, 11, 2)

add_q("truefalse", "红外热像法检测前，被测建筑外墙不应受到阳光直射。", "true",
    [], "阳光直射会造成外墙表面温度不均，影响检测结果。", 4, 11, 2)

add_q("single", "建筑物围护结构传热系数检测，热流计法检测周期不宜少于多少？", "D",
    [{"label":"A","text":"24h"},{"label":"B","text":"48h"},{"label":"C","text":"72h"},{"label":"D","text":"96h"}],
    "JGJ/T 177规定检测周期不宜少于96h。", 4, 11, 3)

add_q("truefalse", "检测围护结构传热系数时应在供暖期进行。", "true",
    [], "供暖期室内外温差大，检测数据更可靠。", 4, 11, 1)

# --- Chapter 12: 门窗气密性检测 (6 questions) ---
add_q("single", "建筑外窗气密性现场检测，检测压力差为多少Pa？", "C",
    [{"label":"A","text":"10Pa"},{"label":"B","text":"25Pa"},{"label":"C","text":"50Pa"},{"label":"D","text":"100Pa"}],
    "GB/T 7106规定气密性检测压力差为50Pa。", 4, 12, 2)

add_q("single", "建筑外窗气密性分级，共分为几级？", "D",
    [{"label":"A","text":"5级"},{"label":"B","text":"6级"},{"label":"C","text":"7级"},{"label":"D","text":"8级"}],
    "GB/T 7106规定气密性共分8级，1级最低8级最高。", 4, 12, 2)

add_q("multi", "门窗物理性能检测包括：", "ABCD",
    [{"label":"A","text":"气密性"},{"label":"B","text":"水密性"},{"label":"C","text":"抗风压性能"},{"label":"D","text":"隔声性能"}],
    "以上均为门窗物理性能检测项目。", 4, 12, 2)

add_q("truefalse", "外窗气密性检测时应同时测量室内外温度和大气压力。", "true",
    [], "温度和气压影响空气密度，需要记录以修正结果。", 4, 12, 3)

add_q("single", "建筑幕墙气密性检测，压力差通常为多少？", "C",
    [{"label":"A","text":"25Pa"},{"label":"B","text":"50Pa"},{"label":"C","text":"100Pa"},{"label":"D","text":"150Pa"}],
    "GB/T 15227规定幕墙气密性检测压力差通常为100Pa。", 4, 12, 3)

add_q("truefalse", "门窗现场气密性检测可使用鼓风门法。", "true",
    [], "鼓风门法是现场检测建筑气密性的常用方法。", 4, 12, 2)

# --- Chapter 13: 甲醛检测 (8 questions) ---
add_q("single", "室内甲醛检测常用的AHMT分光光度法的检出限为多少？", "B",
    [{"label":"A","text":"0.01mg/m³"},{"label":"B","text":"0.02mg/m³"},{"label":"C","text":"0.05mg/m³"},{"label":"D","text":"0.10mg/m³"}],
    "GB/T 18204.2规定AHMT法检出限为0.02mg/m³。", 5, 13, 2)

add_q("single", "室内空气中甲醛的限量值为多少？", "B",
    [{"label":"A","text":"≤0.05mg/m³"},{"label":"B","text":"≤0.08mg/m³"},{"label":"C","text":"≤0.10mg/m³"},{"label":"D","text":"≤0.12mg/m³"}],
    "GB 50325规定I类民用建筑甲醛限量≤0.08mg/m³。", 5, 13, 1)

add_q("multi", "室内环境污染检测项目包括：", "ABCD",
    [{"label":"A","text":"甲醛"},{"label":"B","text":"TVOC"},{"label":"C","text":"氨气"},{"label":"D","text":"氡气"}],
    "GB 50325规定的五项检测：甲醛、苯、甲苯+二甲苯、TVOC、氨。", 5, 13, 2)

add_q("truefalse", "室内环境检测采样前应关闭门窗24小时以上。", "true",
    [], "GB 50325规定采样前关闭门窗24h（I类）或12h（II类）。", 5, 13, 1)

add_q("single", "酚试剂分光光度法测定甲醛的吸收液是什么？", "A",
    [{"label":"A","text":"酚试剂溶液"},{"label":"B","text":"蒸馏水"},{"label":"C","text":"氢氧化钠溶液"},{"label":"D","text":"盐酸溶液"}],
    "酚试剂吸收液与甲醛反应生成嗪。", 5, 13, 2)

add_q("single", "室内空气中苯的限量值（I类建筑）为多少？", "A",
    [{"label":"A","text":"≤0.06mg/m³"},{"label":"B","text":"≤0.09mg/m³"},{"label":"C","text":"≤0.12mg/m³"},{"label":"D","text":"≤0.15mg/m³"}],
    "GB 50325规定I类建筑苯限量≤0.06mg/m³。", 5, 13, 2)

add_q("multi", "影响室内甲醛浓度的因素有：", "ABCD",
    [{"label":"A","text":"室内温度"},{"label":"B","text":"室内湿度"},{"label":"C","text":"通风条件"},{"label":"D","text":"装修材料"}],
    "以上因素均影响室内甲醛浓度。", 5, 13, 2)

add_q("truefalse", "采用集中空调的建筑应在空调正常运转条件下检测。", "true",
    [], "GB 50325规定应模拟正常使用条件进行检测。", 5, 13, 1)

# --- Chapter 14: TVOC检测 (6 questions) ---
add_q("single", "TVOC检测中，采样管使用什么材料？", "C",
    [{"label":"A","text":"活性炭管"},{"label":"B","text":"硅胶管"},{"label":"C","text":"Tenax-TA吸附管"},{"label":"D","text":"玻璃纤维管"}],
    "GB/T 18883规定使用Tenax-TA吸附管采集TVOC。", 5, 14, 2)

add_q("single", "TVOC检测使用什么分析方法？", "C",
    [{"label":"A","text":"分光光度法"},{"label":"B","text":"电化学法"},{"label":"C","text":"热解吸-气相色谱法"},{"label":"D","text":"原子吸收法"}],
    "TVOC采用热解吸-毛细管气相色谱法分析。", 5, 14, 2)

add_q("truefalse", "TVOC是总挥发性有机化合物的简称。", "true",
    [], "TVOC = Total Volatile Organic Compounds。", 5, 14, 1)

add_q("single", "室内TVOC限量值（I类建筑）为多少？", "B",
    [{"label":"A","text":"≤0.3mg/m³"},{"label":"B","text":"≤0.5mg/m³"},{"label":"C","text":"≤0.7mg/m³"},{"label":"D","text":"≤1.0mg/m³"}],
    "GB 50325规定I类建筑TVOC限量≤0.5mg/m³。", 5, 14, 2)

add_q("multi", "TVOC检测的采样要求包括：", "ABC",
    [{"label":"A","text":"采样流量0.5L/min"},{"label":"B","text":"采样时间20min"},{"label":"C","text":"采样体积10L"},{"label":"D","text":"采样温度60℃"}],
    "采样不需加热至60℃。", 5, 14, 3)

add_q("truefalse", "TVOC检测结果应换算成标准状态下的浓度。", "true",
    [], "检测结果需根据采样时的温度、气压换算成标准状态。", 5, 14, 2)

# --- Chapter 15: 氨气检测 (4 questions) ---
add_q("single", "室内氨气检测常用什么方法？", "C",
    [{"label":"A","text":"气相色谱法"},{"label":"B","text":"原子荧光法"},{"label":"C","text":"靛酚蓝分光光度法"},{"label":"D","text":"紫外分光光度法"}],
    "GB/T 18204.2规定靛酚蓝分光光度法测定氨。", 5, 15, 2)

add_q("single", "I类民用建筑室内氨的限量值为多少？", "B",
    [{"label":"A","text":"≤0.1mg/m³"},{"label":"B","text":"≤0.2mg/m³"},{"label":"C","text":"≤0.3mg/m³"},{"label":"D","text":"≤0.5mg/m³"}],
    "GB 50325规定I类建筑氨限量≤0.2mg/m³。", 5, 15, 2)

add_q("truefalse", "氨气主要来源于混凝土中使用的防冻剂。", "true",
    [], "混凝土防冻剂中的尿素等含氨物质会缓慢释放氨气。", 5, 15, 1)

add_q("multi", "靛酚蓝法测定氨时需要的试剂包括：", "ABC",
    [{"label":"A","text":"次氯酸钠"},{"label":"B","text":"苯酚"},{"label":"C","text":"亚硝基铁氰化钠"},{"label":"D","text":"浓硫酸"}],
    "靛酚蓝法用次氯酸钠-苯酚法显色，亚硝基铁氰化钠为催化剂。", 5, 15, 3)

# --- Chapter 16: 氡气检测 (4 questions) ---
add_q("single", "室内氡气检测常用什么方法？", "B",
    [{"label":"A","text":"气相色谱法"},{"label":"B","text":"闪烁瓶法"},{"label":"C","text":"紫外分光光度法"},{"label":"D","text":"红外光谱法"}],
    "GB/T 16147规定闪烁瓶法测定空气中氡。", 5, 16, 2)

add_q("single", "I类民用建筑室内氡的限量值为多少？", "B",
    [{"label":"A","text":"≤100Bq/m³"},{"label":"B","text":"≤200Bq/m³"},{"label":"C","text":"≤300Bq/m³"},{"label":"D","text":"≤400Bq/m³"}],
    "GB 50325规定I类建筑氡限量≤200Bq/m³。", 5, 16, 2)

add_q("truefalse", "氡气是一种无色无味的放射性气体。", "true",
    [], "氡气是天然放射性气体，无色无味。", 5, 16, 1)

add_q("truefalse", "室内氡浓度检测应关闭门窗24h后进行。", "true",
    [], "GB 50325规定氡浓度检测前应关闭门窗24h。", 5, 16, 1)

print(f"Total questions created: {qid}")

# ==========================================
# COMPOSITE QUESTIONS (8 questions)
# ==========================================
composites = [
    ("composite",
     "某工程使用P.O 42.5普通硅酸盐水泥，请说明：(1)水泥进场检验的项目有哪些？(2)如何判断水泥安定性是否合格？(3)水泥强度等级42.5的含义是什么？",
     json.dumps([
         "(1)进场检验项目包括：产品合格证、出厂检验报告、进场复验报告；复验项目包括安定性、凝结时间、强度。(2)安定性检测采用雷氏夹法或试饼法，雷氏夹膨胀值不大于5mm为合格。(3)42.5表示28d抗压强度不低于42.5MPa。"
     ]),
     "GB 175对通用硅酸盐水泥的技术要求。各项要点各占1/3分值。", 1, 1, 3),
    ("composite",
     "简述回弹法检测混凝土抗压强度的基本步骤及注意事项。",
     json.dumps([
         "(1)选取测区：每构件不少于10个测区；(2)回弹测试：每个测区16个测点；(3)碳化深度测量：每个测区3个测点取平均值；(4)数据处理：去掉3个最大值和3个最小值后取平均值；(5)根据测强曲线换算强度值。注意事项：避开蜂窝麻面、保持仪器垂直于测试面。"
     ]),
     "JGJ/T 23 回弹法检测混凝土抗压强度技术规程。", 2, 5, 3),
    ("composite",
     "某建筑工程桩基础采用钻孔灌注桩，请说明：(1)桩身完整性检测常用方法及适用条件；(2)单桩竖向抗压静载试验的终止加载条件。",
     json.dumps([
         "(1)低应变法适用于检测桩身完整性、判定缺陷位置和程度；声波透射法适用于预埋声测管的灌注桩；钻芯法可直接观察桩身质量。(2)终止条件：某级荷载下桩顶沉降量为前一级沉降量的5倍且总沉降量≥40mm；或某级荷载下桩顶沉降量为前一级的2倍且24h不收敛；或达到设计极限承载力。"
     ]),
     "JGJ 106建筑基桩检测技术规范。", 3, 8, 3),
    ("composite",
     "某办公楼室内环境检测，请说明：(1)室内环境检测应在什么条件下进行？(2)甲醛的检测方法及原理。",
     json.dumps([
         "(1)检测条件：工程完工至少7天后，采样前关闭门窗24h(I类)/12h(II类)；温度控制在22-28℃；采用集中空调的建筑应在空调正常运转条件下检测。(2)常用AHMT分光光度法：空气中甲醛被吸收液吸收，在碱性条件下与AHMT反应生成紫红色化合物，比色定量。检出限0.02mg/m³。"
     ]),
     "GB 50325民用建筑工程室内环境污染控制标准。", 5, 13, 3),
    ("composite",
     "请论述钢筋力学性能检测的完整流程及主要指标评判标准。",
     json.dumps([
         "流程：(1)取样：按批次和规格取样，每批取拉伸2根+弯曲2根；(2)拉伸试验：测定屈服强度ReL、抗拉强度Rm、断后伸长率A、最大力总延伸率Agt；(3)弯曲试验：按规定弯心直径弯曲至180°，观察有无裂纹。评判标准：强屈比Rm/ReL≥1.25，屈标比ReL/标准值≥1.0，Agt≥7.5%，弯曲无裂纹。"
     ]),
     "GB 1499.2钢筋混凝土用钢。", 1, 3, 3),
    ("composite",
     "介绍建筑节能检测中门窗气密性现场检测的方法和判定标准。",
     json.dumps([
         "方法：采用鼓风门法或气压法，在50Pa压力差下测量空气渗透量。步骤：(1)密封门窗以外开口；(2)安装风机和压力测量装置；(3)在正压和负压各50Pa下测量空气流量；(4)计算单位面积空气渗透量。判定：根据GB/T 7106分级，1级（最低）到8级（最高），不同气候区有不同要求。"
     ]),
     "GB/T 7106建筑外门窗气密性能分级及检测方法。", 4, 12, 3),
    ("composite",
     "论述超声波探伤检测钢结构焊缝的基本原理和缺陷评定方法。",
     json.dumps([
         "原理：利用超声波在介质中传播遇缺陷反射的特性。发射探头发出超声脉冲，遇焊缝缺陷部分反射，接收探头接收反射信号。评定方法：(1)制作DAC曲线（距离-波幅曲线），含评定线、定量线、判废线；(2)根据反射波幅度超过的线确定缺陷等级；(3)测量缺陷指示长度；(4)综合评定焊缝质量等级（I～IV级）。"
     ]),
     "GB/T 11345焊缝无损检测-超声检测。", 2, 7, 3),
    ("composite",
     "某住宅小区验收检测，需要对室内环境进行五项检测，请详细说明检测项目、采样要求和各项目的标准限值。",
     json.dumps([
         "五项检测：甲醛(≤0.08mg/m³)、苯(≤0.06mg/m³)、TVOC(≤0.5mg/m³)、氨(≤0.2mg/m³)、氡(≤200Bq/m³)。采样要求：I类建筑门窗关闭24h后采样；采样点避开通风口，离墙壁≥0.5m，离地面0.8～1.5m；房间面积<50m²设1个点，50～100m²设2个点，>100m²设3～5个点。甲醛+氨用吸收液采样，苯+TVOC用吸附管采样，氡用闪烁瓶采样。"
     ]),
     "GB 50325民用建筑工程室内环境污染控制标准。", 5, 13, 3),
]

# ==========================================
# INSERT QUESTIONS
# ==========================================
actual_qids = {}
for q in questions:
    cur.execute(
        "INSERT INTO questions(type,content,answer,options,explanation,subject_id,chapter_id,difficulty,is_active,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
        (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], now))
conn.commit()

single_count = sum(1 for q in questions if q[0] == 'single')
multi_count = sum(1 for q in questions if q[0] == 'multi')
tf_count = sum(1 for q in questions if q[0] == 'truefalse')
print(f"Inserted {len(questions)} questions: {single_count} single, {multi_count} multi, {tf_count} truefalse")

# Insert composite questions
comp_ids = []
for ct, cc, ca, ce, cs, ch, cd in composites:
    cur.execute(
        "INSERT INTO questions(type,content,answer,options,explanation,subject_id,chapter_id,difficulty,is_active,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
        (ct, cc, ca, "[]", ce, cs, ch, cd, now))
    comp_ids.append(cur.lastrowid)
conn.commit()
print(f"Inserted {len(composites)} composite questions")

# Collect all question IDs by subject
cur.execute("SELECT id, subject_id FROM questions")
all_qs = cur.fetchall()
qids_by_subject = {}
for qid_val, sid in all_qs:
    qids_by_subject.setdefault(sid, []).append(qid_val)

# ==========================================
# EXAMS (12 exams)
# ==========================================
exam_ids = []
subj_names = ["建筑材料检测", "主体结构检测", "地基基础检测", "建筑节能检测", "室内环境检测"]

# Per-subject mock & formal
for sid in range(1, 6):
    qids = qids_by_subject[sid][:20]
    if len(qids) < 5:
        continue
    # Mock exam
    cur.execute(
        "INSERT INTO exams(title,description,mode,duration_minutes,total_score,pass_score,question_ids,max_tab_switches,is_published,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
        (f"{subj_names[sid-1]}模拟考试",
         f"建筑检测行业{subj_names[sid-1]}专项练习，含单选、多选、判断，共{len(qids)}题",
         "mock", 90, 100, 60, json.dumps(qids), 99, now))
    exam_ids.append(cur.lastrowid)
    # Formal exam
    cur.execute(
        "INSERT INTO exams(title,description,mode,duration_minutes,total_score,pass_score,question_ids,max_tab_switches,is_published,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
        (f"{subj_names[sid-1]}正式考试",
         f"建筑检测行业{subj_names[sid-1]}正式考核，含单选、多选、判断，共{len(qids)}题，严格防作弊",
         "formal", 120, 100, 60, json.dumps(qids), 3, now))
    exam_ids.append(cur.lastrowid)

# Comprehensive mock and formal (mix across subjects, include composites)
all_qids_list = [q[0] for q in all_qs if q[0] not in comp_ids]
comp_all = [c for c in comp_ids]
mixed_mock = all_qids_list[:25] + comp_all[:3]
mixed_formal = all_qids_list[25:50] + comp_all[3:6]
cur.execute(
    "INSERT INTO exams(title,description,mode,duration_minutes,total_score,pass_score,question_ids,max_tab_switches,is_published,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
    ("建筑检测综合模拟考试", "涵盖五大检测领域的综合练习，含综合题，共{}题".format(len(mixed_mock)),
     "mock", 120, 100, 60, json.dumps(mixed_mock), 99, now))
exam_ids.append(cur.lastrowid)
cur.execute(
    "INSERT INTO exams(title,description,mode,duration_minutes,total_score,pass_score,question_ids,max_tab_switches,is_published,created_at) VALUES(?,?,?,?,?,?,?,?,1,?)",
    ("建筑检测综合正式考试", "全国建筑检测从业人员综合能力考核，含综合题，共{}题".format(len(mixed_formal)),
     "formal", 150, 100, 60, json.dumps(mixed_formal), 3, now))
exam_ids.append(cur.lastrowid)
conn.commit()
print(f"Created {len(exam_ids)} exams.")

# ==========================================
# EXAM RESULTS (some completed)
# ==========================================
# zhangsan completed 3 exams
for eid in exam_ids[:3]:
    qids_json = cur.execute("SELECT question_ids FROM exams WHERE id=?", (eid,)).fetchone()[0]
    qids_list = json.loads(qids_json)
    answers = {}
    for qid_val in qids_list[:15]:
        q_type, q_ans = cur.execute("SELECT type, answer FROM questions WHERE id=?", (qid_val,)).fetchone()
        if q_type == "composite":
            answers[str(qid_val)] = "学生作答内容：根据标准规范要求进行了回答。"
        elif q_type in ("single", "multi"):
            import random
            answers[str(qid_val)] = q_ans if random.random() > 0.3 else "X"
        else:
            answers[str(qid_val)] = q_ans if random.random() > 0.3 else "error"
    correct = sum(1 for k, v in answers.items() if v != "X" and v != "error")
    # Make most scores passing
    passed = correct >= 8
    cur.execute(
        "INSERT INTO exam_results(exam_id,user_id,answers,auto_score,manual_score,total_score,passed,tab_switches,is_cheating,started_at,finished_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, 2, json.dumps(answers), min(correct * 5, 80), 0, min(correct * 5, 80), passed, 0, 0, now, now, now))
conn.commit()

# lisi completed 2 exams
for eid in exam_ids[1:3]:
    qids_json = cur.execute("SELECT question_ids FROM exams WHERE id=?", (eid,)).fetchone()[0]
    qids_list = json.loads(qids_json)
    answers = {}
    for qid_val in qids_list[:15]:
        q_type, q_ans = cur.execute("SELECT type, answer FROM questions WHERE id=?", (qid_val,)).fetchone()
        if q_type == "composite":
            answers[str(qid_val)] = "已作答。"
        elif q_type in ("single", "multi"):
            import random
            answers[str(qid_val)] = q_ans if random.random() > 0.4 else "X"
        else:
            answers[str(qid_val)] = q_ans if random.random() > 0.4 else "error"
    correct = sum(1 for k, v in answers.items() if v != "X" and v != "error")
    passed = correct >= 8
    cur.execute(
        "INSERT INTO exam_results(exam_id,user_id,answers,auto_score,manual_score,total_score,passed,tab_switches,is_cheating,started_at,finished_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, 3, json.dumps(answers), min(correct * 5, 80), 0, min(correct * 5, 80), passed, 0, 0, now, now, now))
conn.commit()
print("Created exam results (zhangsan: 3, lisi: 2).")

# ==========================================
# ANNOUNCEMENTS (5)
# ==========================================
anns = [
    ("关于2026年度建筑检测人员继续教育的通知",
     "各检测机构：根据住建部要求，2026年度建筑检测人员继续教育将于7月1日开始在线学习，请各机构组织相关人员参加。",
     1, 1, "系统管理员", now),
    ("关于更新建筑材料检测标准的通知",
     "GB 175-2023《通用硅酸盐水泥》已发布，将于2026年10月1日正式实施，请各检测人员及时学习新标准。",
     1, 1, "系统管理员", now),
    ("2026年第二季度检测能力验证通知",
     "省质监站定于2026年6月30日组织建筑材料检测能力验证，项目包括水泥强度、混凝土抗压强度、钢筋力学性能。",
     1, 1, "系统管理员", now),
    ("关于规范检测报告格式的通知",
     "即日起所有检测报告需按新版报告模板出具，请各检测人员在系统中下载最新模板。",
     0, 1, "系统管理员", now),
    ("系统升级维护公告",
     "本系统将于本周六凌晨2:00-6:00进行例行维护，届时系统将暂停服务，请提前做好安排。",
     0, 1, "系统管理员", now),
]
for a in anns:
    cur.execute(
        "INSERT INTO announcements(title,content,is_pinned,is_published,created_by,created_at) VALUES(?,?,?,?,?,?)",
        a)
conn.commit()
print(f"Created {len(anns)} announcements.")

# ==========================================
# RESOURCES (8)
# ==========================================
resources = [
    ("GB 175-2023 通用硅酸盐水泥", "最新版水泥国家标准全文", 1, "https://std.samr.gov.cn/gb/search/gbDetailed?id=GB175",
     "pdf", 1024000, 156, 1, 1, "系统管理员", now),
    ("JGJ/T 23-2011 回弹法检测混凝土抗压强度技术规程", "回弹法检测混凝土强度标准", 2,
     "https://www.jianbiaoku.com/webarbs/book/jgj23", "pdf", 2048000, 89, 2, 1, "系统管理员", now),
    ("GB 50325-2020 民用建筑工程室内环境污染控制标准", "室内环境检测标准全文", 5,
     "https://std.samr.gov.cn/gb/search/gbDetailed?id=GB50325", "pdf", 3072000, 67, 3, 1, "系统管理员", now),
    ("建筑检测常用仪器操作手册", "各类检测仪器的操作说明和注意事项", 1,
     "https://example.com/manual/instruments.docx", "docx", 512000, 45, 4, 1, "系统管理员", now),
    ("主体结构检测报告模板", "标准检测报告格式，含计算公式和判定模板", 2,
     "https://example.com/templates/structure.xlsx", "xlsx", 256000, 120, 5, 1, "系统管理员", now),
    ("建筑节能检测技术指南", "围护结构热工性能检测指南", 4,
     "https://example.com/guides/energy.pdf", "pdf", 1536000, 34, 6, 1, "系统管理员", now),
    ("桩基检测数据记录表", "静载试验和低应变检测数据记录表格", 3,
     "https://example.com/templates/pile.xlsx", "xlsx", 128000, 78, 7, 1, "系统管理员", now),
    ("室内空气质量检测标准汇编", "GB 50325、GB/T 18883等相关标准合集", 5,
     "https://example.com/standards/indoor.pdf", "pdf", 5120000, 92, 8, 1, "系统管理员", now),
]
for r in resources:
    cur.execute(
        "INSERT INTO resources(title,description,subject_id,file_url,file_type,file_size,download_count,sort_order,is_published,created_by,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        r)
conn.commit()
print(f"Created {len(resources)} resources.")

# ==========================================
# VIDEO COURSES (6)
# ==========================================
videos = [
    ("水泥标准稠度用水量检测实操", "演示水泥标准稠度用水量检测的完整操作流程",
     1, 1, "https://example.com/videos/cement.mp4", 3600, 1, 1, now),
    ("回弹法检测混凝土强度教学", "回弹仪操作、测区选择、数据处理全流程讲解",
     2, 5, "https://example.com/videos/rebound.mp4", 4800, 2, 1, now),
    ("桩基静载试验现场操作演示", "静载试验设备安装、加载、数据记录全过程",
     3, 8, "https://example.com/videos/pile.mp4", 5400, 3, 1, now),
    ("室内甲醛采样与检测方法", "甲醛采样管使用、吸收液配置、分光光度计操作",
     5, 13, "https://example.com/videos/formaldehyde.mp4", 2400, 4, 1, now),
    ("钢筋力学性能试验实操", "万能试验机操作、应力应变曲线解读",
     1, 3, "https://example.com/videos/steel.mp4", 3000, 5, 1, now),
    ("建筑外窗气密性现场检测", "鼓风门法检测门窗气密性的操作步骤",
     4, 12, "https://example.com/videos/window.mp4", 2800, 6, 1, now),
]
for v in videos:
    cur.execute(
        "INSERT INTO video_courses(title,description,subject_id,chapter_id,video_url,duration_seconds,sort_order,is_published,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
        v)
conn.commit()
print(f"Created {len(videos)} video courses.")

# ==========================================
# CERTIFICATES (8)
# ==========================================
certs_data = [
    ("建筑材料检测员", "颁发给通过建筑材料检测科目考核的学员", "formal", None,
     "需通过对应科目的正式考试且成绩≥60分", now),
    ("主体结构检测员", "颁发给通过主体结构检测科目考核的学员", "formal", None,
     "需通过对应科目的正式考试且成绩≥60分", now),
    ("地基基础检测员", "颁发给通过地基基础检测科目考核的学员", "formal", None,
     "需通过对应科目的正式考试且成绩≥60分", now),
    ("建筑节能检测员", "颁发给通过建筑节能检测科目考核的学员", "formal", None,
     "需通过对应科目的正式考试且成绩≥60分", now),
    ("室内环境检测员", "颁发给通过室内环境检测科目考核的学员", "formal", None,
     "需通过对应科目的正式考试且成绩≥60分", now),
    ("建筑检测综合工程师", "颁发给通过全部五科综合考核的学员", "formal", None,
     "需通过综合正式考试且成绩≥60分", now),
    ("水泥物理性能检测(练习)", "水泥章节练习通过率≥80%可申请", "practice", 1,
     "章节练习通过率≥80%", now),
    ("混凝土强度检测(练习)", "混凝土强度章节练习通过率≥80%可申请", "practice", 5,
     "章节练习通过率≥80%", now),
]
cert_ids = []
for c in certs_data:
    cur.execute(
        "INSERT INTO certificates(name,description,cert_type,chapter_id,issue_rule,created_at) VALUES(?,?,?,?,?,?)",
        c)
    cert_ids.append(cur.lastrowid)
conn.commit()
print(f"Created {len(certs_data)} certificates.")

# ==========================================
# USER CERTIFICATES (issued to zhangsan)
# ==========================================
cur.execute(
    "INSERT INTO user_certificates(certificate_id,user_id,exam_result_id,certificate_no,is_revoked,issued_at) VALUES(?,?,?,?,0,?)",
    (cert_ids[0], 2, 1, "CERT-2026-00001", now))
cur.execute(
    "INSERT INTO user_certificates(certificate_id,user_id,exam_result_id,certificate_no,is_revoked,issued_at) VALUES(?,?,?,?,0,?)",
    (cert_ids[6], 2, None, "CERT-2026-00002", now))
cur.execute(
    "INSERT INTO user_certificates(certificate_id,user_id,exam_result_id,certificate_no,is_revoked,issued_at) VALUES(?,?,?,?,1,?)",
    (cert_ids[4], 3, 5, "CERT-2026-00003", now))
conn.commit()
print("Issued 3 user certificates (2 to zhangsan, 1 revoked to lisi).")

# ==========================================
# PRACTICE RECORDS (20 records)
# ==========================================
import random
for uid in [2, 3, 4, 6]:
    for i in range(5):
        mode = random.choice(["random", "specialty", "chapter"])
        sid = random.randint(1, 5)
        cid = random.choice([ch[0] for ch in chapters if ch[1] == sid])
        total_count = random.randint(10, 30)
        correct = random.randint(5, total_count)
        wrong = total_count - correct
        cur.execute(
            "INSERT INTO practice_records(user_id,mode,subject_id,chapter_id,total_count,correct_count,wrong_count,duration_seconds,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (uid, mode, sid, cid, total_count, correct, wrong, random.randint(120, 1200), now))
conn.commit()
print("Created 20 practice records.")

# ==========================================
# WRONG ANSWERS (15 entries)
# ==========================================
for uid in [2, 3, 4, 6]:
    for j in range(4):
        qid_val = (uid * 7 + j * 3) % len(questions) + 1
        if qid_val > len(questions):
            qid_val = j + 1
        cur.execute(
            "INSERT INTO wrong_answers(user_id,question_id,wrong_count,is_mastered,last_wrong_at,created_at) VALUES(?,?,?,0,?,?)",
            (uid, qid_val, random.randint(1, 3), now, now))
conn.commit()
print("Created 16 wrong answer entries.")

# ==========================================
# FAVORITES (12 entries)
# ==========================================
for uid in [2, 3, 4, 6]:
    for j in range(3):
        qid_val = (uid * 3 + j * 5) % len(questions) + 1
        if qid_val > len(questions):
            qid_val = j + 1
        cur.execute(
            "INSERT INTO favorites(user_id,question_id,created_at) VALUES(?,?,?)",
            (uid, qid_val, now))
conn.commit()
print("Created 12 favorite entries.")

# ==========================================
# NOTES (8 entries)
# ==========================================
notes_data = [
    (2, "水泥安定性检测要点：雷氏夹法膨胀值≤5mm为合格，试饼法无弯曲无裂纹。"),
    (2, "回弹法注意事项：避开工地蜂窝麻面区域，保持仪器垂直。"),
    (3, "低应变法仅用于完整性检测，不用于强度检测。"),
    (3, "HRB400钢筋强屈比Rm/ReL≥1.25，Agt≥7.5%。"),
    (4, "混凝土标准试件150mm立方体，养护温度20±2℃。"),
    (4, "室内甲醛限值0.08mg/m³（I类），采样前关门窗24h。"),
    (6, "静载试验每级稳定标准：沉降≤0.1mm/h。"),
    (6, "超声波探伤频率2.5～5MHz，判废线比定量线高6dB。"),
]
for uid, content in notes_data:
    qid_val = (uid * 7) % len(questions) + 1
    if qid_val > len(questions):
        qid_val = 1
    cur.execute(
        "INSERT INTO notes(user_id,question_id,content,created_at,updated_at) VALUES(?,?,?,?,?)",
        (uid, qid_val, content, now, now))
conn.commit()
print(f"Created {len(notes_data)} notes.")

# ==========================================
# QUESTION FEEDBACKS (4)
# ==========================================
cur.execute(
    "INSERT INTO question_feedbacks(user_id,question_id,type,content,status,created_at) VALUES(?,?,?,?,?,?)",
    (2, 3, "doubt", "此题答案建议补充GB/T 1346的引用来源。", "pending", now))
cur.execute(
    "INSERT INTO question_feedbacks(user_id,question_id,type,content,status,created_at) VALUES(?,?,?,?,?,?)",
    (3, 8, "suggestion", "细度模数范围的解析可以更详细一些。", "resolved", now))
cur.execute(
    "INSERT INTO question_feedbacks(user_id,question_id,type,content,status,created_at) VALUES(?,?,?,?,?,?)",
    (4, 15, "doubt", "超声波频率范围在JGJ中的具体引用是哪个条款？", "pending", now))
cur.execute(
    "INSERT INTO question_feedbacks(user_id,question_id,type,content,status,created_at) VALUES(?,?,?,?,?,?)",
    (6, 25, "suggestion", "建议增加静载试验中反力装置安全系数的说明。", "pending", now))
conn.commit()
print("Created 4 question feedbacks.")

# ==========================================
# VIDEO PROGRESS (6 entries)
# ==========================================
for uid in [2, 3, 4]:
    for vi in range(2):
        cur.execute(
            "INSERT INTO video_progress(user_id,video_id,current_time,duration,is_finished,updated_at) VALUES(?,?,?,?,?,?)",
            (uid, vi + 1, random.randint(100, 3000), 3600, random.choice([0, 1]), now))
conn.commit()
print("Created 6 video progress entries.")

# ==========================================
# OPERATION LOGS (15 entries)
# ==========================================
actions = [("create", "question"), ("edit", "question"), ("delete", "question"),
           ("create", "exam"), ("edit", "exam"), ("publish", "exam"),
           ("create", "user"), ("disable", "user"),
           ("create", "announcement"), ("upload", "resource"),
           ("create", "certificate"), ("issue", "certificate"),
           ("create", "video"), ("grade", "exam_result"),
           ("feedback", "question")]
for i, (act, tgt) in enumerate(actions):
    cur.execute(
        "INSERT INTO operation_logs(user_id,username,action,target_type,target_id,detail,created_at) VALUES(?,?,?,?,?,?,?)",
        (1, "系统管理员", act, tgt, i + 1, f"{act} {tgt} #{i + 1}", now))
conn.commit()
print(f"Created {len(actions)} operation logs.")

# ==========================================
# RETAK APPLICATIONS (3)
# ==========================================
cur.execute(
    "INSERT INTO retake_applications(exam_id,user_id,reason,status,created_at) VALUES(?,?,?,?,?)",
    (exam_ids[1], 2, "上次考试因网络问题影响发挥，申请重考。", "pending", now))
cur.execute(
    "INSERT INTO retake_applications(exam_id,user_id,reason,status,created_at) VALUES(?,?,?,?,?)",
    (exam_ids[3], 3, "身体不适导致考试中途退出。", "approved", now))
cur.execute(
    "INSERT INTO retake_applications(exam_id,user_id,reason,status,created_at) VALUES(?,?,?,?,?)",
    (exam_ids[5], 4, "系统故障导致无法正常答题。", "pending", now))
conn.commit()
print("Created 3 retake applications.")

# ==========================================
# ABNORMAL REPORTS (3)
# ==========================================
cur.execute(
    "INSERT INTO abnormal_reports(exam_result_id,user_id,reason,detail,is_judged,judgment,created_at) VALUES(?,?,?,?,?,?,?)",
    (4, 3, "tab_switch", "考试期间切换浏览器标签页3次", 1, "confirmed", now))
cur.execute(
    "INSERT INTO abnormal_reports(exam_result_id,user_id,reason,detail,is_judged,judgment,created_at) VALUES(?,?,?,?,?,?,?)",
    (2, 2, "tab_switch", "考试期间切换窗口1次", 1, "ignore", now))
cur.execute(
    "INSERT INTO abnormal_reports(exam_result_id,user_id,reason,detail,is_judged,created_at) VALUES(?,?,?,?,?,?)",
    (5, 3, "page_leave", "考试期间离开页面2次", 0, now))
conn.commit()
print("Created 3 abnormal reports.")

conn.close()
print("\n===== Seed Complete =====")
print(f"Users: {len(users)}")
print(f"Subjects: {len(subjects)}")
print(f"Chapters: {len(chapters)}")
print(f"Questions: {len(questions)} + {len(composites)} composite = {len(questions) + len(composites)}")
print(f"Exams: {len(exam_ids)}")
print(f"Resources: {len(resources)}")
print(f"Videos: {len(videos)}")
print(f"Certificates: {len(certs_data)}")
print(f"Practice Records: 20")
print(f"Wrong Answers: 16")
print(f"Favorites: 12")
print(f"Notes: {len(notes_data)}")
print(f"Announcements: {len(anns)}")
print(f"Feedbacks: 4")
print(f"Video Progress: 6")
print(f"Operation Logs: {len(actions)}")
print(f"Retake Applications: 3")
print(f"Abnormal Reports: 3")
print("\nTest accounts:")
print("  admin / admin123   (系统管理员)")
print("  zhangsan / 123456  (学生)")
print("  lisi / 123456      (学生)")
print("  wangwu / 123456    (学生)")
print("  fuzeren / 123456   (负责人)")
print("  jianceyuan / 123456 (检测员)")
print("  shenheyuan / 123456 (审核员)")
