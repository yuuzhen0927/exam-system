# -*- coding: utf-8 -*-
"""建筑检测考试系统 - 全中文种子数据"""
import sqlite3, json, random, uuid, sys
sys.path.insert(0, 'F:/CodexWorkspace/Project004_考试系统/src/backend')
from auth import hash_password

DB = 'F:/CodexWorkspace/Project004_考试系统/src/backend/exam.db'
conn = sqlite3.connect(DB)

# 1. 用户
conn.execute("DELETE FROM users WHERE username != 'admin'")
users = [
    ('zhangsan','123456','张三','student'), ('lisi','123456','李四','student'),
    ('wangwu','123456','王五','student'), ('zhaomin','123456','赵敏','student'),
    ('sunqiang','123456','孙强','student'), ('liuyang','123456','刘洋','student'),
    ('chenfuzeren','123456','陈负责人','teacher'), ('zhoujiance','123456','周检测员','inspector'),
]
for uname, pwd, fname, role in users:
    conn.execute("INSERT INTO users (username,hashed_password,fullname,role,is_active) VALUES (?,?,?,?,1)",
                 (uname, hash_password(pwd), fname, role))
conn.commit()
print(f"用户: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")

# 2. 科目和章节
conn.execute("DELETE FROM chapters")
conn.execute("DELETE FROM subjects")
subj_data = [
    ('建筑材料检测', '水泥、混凝土、钢材、防水材料、砌体材料、保温材料等建筑原材料的质量检测技术', [
        ('水泥检测', '水泥细度、凝结时间、安定性、强度等物理力学性能检测'),
        ('混凝土检测', '混凝土配合比、坍落度、抗压强度、抗渗性能检测'),
        ('钢材检测', '钢筋力学性能、焊接接头、预应力钢材检测'),
        ('防水材料检测', '防水卷材、防水涂料、密封材料性能检测'),
        ('砌体材料检测', '砖、砌块、砂浆强度与外观质量检测'),
        ('保温材料检测', '保温板导热系数、压缩强度、吸水率检测'),
    ]),
    ('主体结构检测', '混凝土结构、砌体结构、钢结构的现场检测与评定技术', [
        ('混凝土强度检测', '回弹法、钻芯法、超声回弹综合法检测混凝土强度'),
        ('混凝土缺陷检测', '超声法检测混凝土内部缺陷、裂缝深度'),
        ('砌体结构检测', '砂浆强度、砌体抗压强度、砌筑质量检测'),
        ('钢结构焊缝检测', '焊缝外观检查、无损检测（MT/UT/RT/PT）'),
        ('钢结构涂层检测', '防腐涂层厚度、防火涂层厚度检测'),
        ('结构变形监测', '沉降观测、倾斜观测、裂缝监测、挠度检测'),
    ]),
    ('地基基础检测', '桩基检测、地基承载力检测、基坑监测、地基处理检测', [
        ('桩基静载试验', '单桩竖向抗压/抗拔/水平静载试验'),
        ('桩基动测法', '低应变反射波法、高应变法检测桩基'),
        ('桩基完整性检测', '声波透射法、钻芯法检测桩身完整性'),
        ('地基承载力检测', '平板载荷试验、标准贯入试验、动力触探'),
        ('基坑监测', '深层水平位移、支撑轴力、地下水位、周边建筑沉降'),
        ('复合地基检测', '水泥搅拌桩、CFG桩、碎石桩复合地基检测'),
    ]),
    ('建筑节能检测', '围护结构热工性能、门窗气密性、采暖空调系统能效检测', [
        ('墙体热工性能', '传热系数、热阻、热桥部位检测'),
        ('外窗三性检测', '气密性、水密性、抗风压性能检测'),
        ('外保温系统检测', '外保温系统耐候性、粘结强度、抗冲击性检测'),
        ('建筑能效评估', '建筑能耗计算、能效等级评定'),
        ('采暖系统检测', '室内温度、供热系统效率、管网平衡检测'),
    ]),
    ('室内环境检测', '甲醛、苯系物、TVOC、氡、氨等室内污染物浓度检测', [
        ('甲醛检测', 'AHMT法、酚试剂法、气相色谱法检测甲醛'),
        ('苯系物检测', '气相色谱法检测苯、甲苯、二甲苯'),
        ('TVOC检测', 'Tenax吸附/热脱附-气相色谱法检测TVOC'),
        ('氡气检测', '连续测氡仪法、活性炭盒法检测氡浓度'),
        ('氨检测', '靛酚蓝分光光度法、离子选择电极法检测氨'),
        ('采样规范', '采样点布置、采样条件控制、样品保存运输'),
    ]),
]
for sname, sdesc, chapters in subj_data:
    conn.execute("INSERT INTO subjects (name,description,sort_order) VALUES (?,?,?)", (sname, sdesc, subj_data.index((sname,sdesc,chapters))))
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i, (cname, cdesc) in enumerate(chapters):
        conn.execute("INSERT INTO chapters (subject_id,name,description,sort_order) VALUES (?,?,?,?)", (sid, cname, cdesc, i))
conn.commit()
print(f"科目: {conn.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]}")
print(f"章节: {conn.execute('SELECT COUNT(*) FROM chapters').fetchone()[0]}")

ch_map = {}
for r in conn.execute("SELECT id, subject_id, name FROM chapters").fetchall():
    ch_map[r[2]] = (r[0], r[1])

TAGS = {
    'high': '["高频考点","必考题型"]', 'easy': '["易错题","常见陷阱"]',
    'basic': '["基础概念","入门必会"]', 'formula': '["计算公式","数值记忆"]',
    'standard': '["规范条文","标准要求"]', 'practical': '["实操要点","现场经验"]',
    'important': '["重点难点","深度理解"]',
}

def add_q(sname, cname, qtype, diff, content, options, answer, explanation, tag):
    ch_id, sid = ch_map.get(cname, (None, 1))
    conn.execute("INSERT INTO questions (subject_id,chapter_id,type,difficulty,content,options,answer,explanation,tags,images,is_active,version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (sid, ch_id, qtype, diff, content, json.dumps(options,ensure_ascii=False), answer, explanation, TAGS.get(tag,'[]'), '[]', 1, 1))

# === 建筑材料检测 ===
# 水泥检测
add_q('建筑材料检测','水泥检测','single',1,'水泥细度检测标准方法是？',[{"label":"A","text":"负压筛析法"},{"label":"B","text":"水筛法"},{"label":"C","text":"比表面积法"},{"label":"D","text":"手工筛分法"}],'A','GB/T 1345规定负压筛析法为标准方法','basic')
add_q('建筑材料检测','水泥检测','single',2,'硅酸盐水泥初凝时间不得早于多少分钟？',[{"label":"A","text":"30"},{"label":"B","text":"45"},{"label":"C","text":"60"},{"label":"D","text":"90"}],'B','GB 175规定硅酸盐水泥初凝不得早于45分钟','standard')
add_q('建筑材料检测','水泥检测','single',2,'水泥安定性检测可采用什么方法？',[{"label":"A","text":"试饼法"},{"label":"B","text":"雷氏夹法"},{"label":"C","text":"沸煮法"},{"label":"D","text":"以上都是"}],'D','安定性可用试饼法或雷氏夹法，均需沸煮','high')
add_q('建筑材料检测','水泥检测','single',3,'P·O 42.5水泥的28天抗压强度标准值？',[{"label":"A","text":"22.5MPa"},{"label":"B","text":"32.5MPa"},{"label":"C","text":"42.5MPa"},{"label":"D","text":"52.5MPa"}],'C','P·O 42.5表示28天抗压强度不低于42.5MPa','formula')
add_q('建筑材料检测','水泥检测','single',1,'水泥标准稠度用水量试验用什么仪器？',[{"label":"A","text":"维卡仪"},{"label":"B","text":"坍落度筒"},{"label":"C","text":"贯入阻力仪"},{"label":"D","text":"勃氏比表面积仪"}],'A','维卡仪(标准法)测定标准稠度用水量','basic')
add_q('建筑材料检测','水泥检测','single',2,'水泥胶砂强度试验的水灰比是多少？',[{"label":"A","text":"0.40"},{"label":"B","text":"0.45"},{"label":"C","text":"0.50"},{"label":"D","text":"0.55"}],'C','ISO法水泥胶砂水灰比0.50，灰砂比1:3','formula')
add_q('建筑材料检测','水泥检测','single',3,'水泥中MgO含量不得超过多少？',[{"label":"A","text":"3.0%"},{"label":"B","text":"5.0%"},{"label":"C","text":"6.0%"},{"label":"D","text":"8.0%"}],'B','GB 175规定MgO不超过5.0%（压蒸安定性合格可放宽至6.0%）','standard')
add_q('建筑材料检测','水泥检测','multi',2,'水泥物理性能指标包括哪些？',[{"label":"A","text":"细度"},{"label":"B","text":"凝结时间"},{"label":"C","text":"安定性"},{"label":"D","text":"强度"},{"label":"E","text":"化学成分"}],'ABCD','物理性能包括细度、凝结时间、安定性和强度','basic')
add_q('建筑材料检测','水泥检测','multi',3,'影响水泥强度的因素有哪些？',[{"label":"A","text":"水灰比"},{"label":"B","text":"养护温度"},{"label":"C","text":"养护湿度"},{"label":"D","text":"龄期"},{"label":"E","text":"水泥细度"}],'ABCDE','以上因素均影响水泥强度发展','important')
add_q('建筑材料检测','水泥检测','truefalse',1,'水泥越细，早期强度越高。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','细度增加水化速度加快，早期强度提高','basic')
add_q('建筑材料检测','水泥检测','truefalse',2,'水泥安定性不合格可以降级使用。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'错误','安定性不合格的水泥严禁在工程中使用','standard')
add_q('建筑材料检测','水泥检测','composite',3,'简述水泥安定性不良的原因、检测方法及工程危害。','[]','游离CaO/MgO过多或石膏过量导致体积膨胀','原因：游离CaO、MgO过多或石膏掺量过大。检测：雷氏夹法(沸煮后膨胀值不大于5mm)或试饼法。危害：混凝土开裂、强度降低、结构破坏。','important')

# 混凝土检测
add_q('建筑材料检测','混凝土检测','single',1,'混凝土标准养护条件是什么？',[{"label":"A","text":"20±1℃，湿度≥90%"},{"label":"B","text":"20±2℃，湿度≥95%"},{"label":"C","text":"25±2℃，湿度≥95%"},{"label":"D","text":"20±2℃，湿度≥90%"}],'B','标准养护温度20±2℃，相对湿度≥95%','basic')
add_q('建筑材料检测','混凝土检测','single',1,'混凝土标准试件尺寸是多少？',[{"label":"A","text":"100mm立方体"},{"label":"B","text":"150mm立方体"},{"label":"C","text":"200mm立方体"},{"label":"D","text":"150×300mm圆柱"}],'B','标准试件为150mm×150mm×150mm立方体','basic')
add_q('建筑材料检测','混凝土检测','single',2,'坍落度试验适用于坍落度多大的混凝土？',[{"label":"A","text":"≤10mm"},{"label":"B","text":"10-90mm"},{"label":"C","text":"10-220mm"},{"label":"D","text":"≥220mm"}],'C','坍落度法适用于骨料最大粒径不超过40mm、坍落度10-220mm','standard')
add_q('建筑材料检测','混凝土检测','single',2,'C30混凝土的立方体抗压强度标准值是多少？',[{"label":"A","text":"20MPa"},{"label":"B","text":"25MPa"},{"label":"C","text":"30MPa"},{"label":"D","text":"35MPa"}],'C','C30表示立方体抗压强度标准值为30MPa','formula')
add_q('建筑材料检测','混凝土检测','single',3,'混凝土抗渗等级P6表示什么？',[{"label":"A","text":"承受0.6MPa水压不渗透"},{"label":"B","text":"承受6MPa水压不渗透"},{"label":"C","text":"渗透系数为6"},{"label":"D","text":"6个试件都不渗透"}],'A','P6表示能承受0.6MPa水压而不渗透','formula')
add_q('建筑材料检测','混凝土检测','single',2,'回弹法检测混凝土强度，每个测区应弹击多少次？',[{"label":"A","text":"8次"},{"label":"B","text":"12次"},{"label":"C","text":"16次"},{"label":"D","text":"20次"}],'C','每个测区应均匀布置16个弹击点','practical')
add_q('建筑材料检测','混凝土检测','multi',2,'混凝土耐久性指标包括哪些？',[{"label":"A","text":"抗渗性"},{"label":"B","text":"抗冻性"},{"label":"C","text":"抗碳化"},{"label":"D","text":"抗氯离子渗透"}],'ABCD','耐久性包括抗渗、抗冻、抗碳化、抗氯离子渗透等','important')
add_q('建筑材料检测','混凝土检测','truefalse',1,'混凝土强度等级按轴心抗压强度划分。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'错误','按立方体抗压强度标准值划分','basic')
add_q('建筑材料检测','混凝土检测','composite',4,'说明混凝土配合比设计的基本步骤和关键参数。','[]','配制强度→水灰比→用水量→水泥用量→砂率→砂石用量→试配','步骤：确定配制强度(fcu,0=fcu,k+1.645σ)、水灰比(W/C)、用水量、水泥用量、砂率、砂石用量、试配调整。关键参数：水灰比、砂率、用水量。','important')

# 钢材检测
add_q('建筑材料检测','钢材检测','single',2,'HRB400钢筋屈服强度标准值是多少？',[{"label":"A","text":"300MPa"},{"label":"B","text":"335MPa"},{"label":"C","text":"400MPa"},{"label":"D","text":"500MPa"}],'C','HRB400屈服强度标准值400MPa','formula')
add_q('建筑材料检测','钢材检测','single',3,'钢筋焊接接头弯曲试验的弯心直径是多少？',[{"label":"A","text":"3d"},{"label":"B","text":"4d"},{"label":"C","text":"5d"},{"label":"D","text":"6d"}],'B','d为钢筋直径，弯心直径一般为4d','standard')
add_q('建筑材料检测','钢材检测','single',2,'钢筋拉伸试验的比例标距是多少？',[{"label":"A","text":"5d"},{"label":"B","text":"10d"},{"label":"C","text":"5.65√S₀"},{"label":"D","text":"200mm"}],'C','比例标距L₀=5.65√S₀≈5d','formula')
add_q('建筑材料检测','钢材检测','single',1,'钢筋力学性能指标包括哪些？',[{"label":"A","text":"屈服强度"},{"label":"B","text":"抗拉强度"},{"label":"C","text":"伸长率"},{"label":"D","text":"以上都是"}],'D','屈服强度、抗拉强度、伸长率为主要力学性能指标','basic')
add_q('建筑材料检测','钢材检测','multi',3,'钢筋焊接接头检测项目包括？',[{"label":"A","text":"拉伸试验"},{"label":"B","text":"弯曲试验"},{"label":"C","text":"冲击试验"},{"label":"D","text":"硬度试验"}],'ABD','焊接接头检测：拉伸、弯曲、硬度（冲击非必检）','practical')
add_q('建筑材料检测','钢材检测','truefalse',2,'HRB500钢筋的强屈比不应小于1.25。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','强屈比=抗拉强度/屈服强度，不应小于1.25','standard')

# 防水材料
add_q('建筑材料检测','防水材料检测','single',2,'SBS防水卷材不透水性试验的水压和时间？',[{"label":"A","text":"0.1MPa/15min"},{"label":"B","text":"0.2MPa/30min"},{"label":"C","text":"0.3MPa/30min"},{"label":"D","text":"0.5MPa/30min"}],'C','SBS卷材不透水性试验0.3MPa保持30min不渗透','standard')
add_q('建筑材料检测','防水材料检测','single',3,'聚氨酯防水涂料拉伸强度试验的拉伸速率是多少？',[{"label":"A","text":"50mm/min"},{"label":"B","text":"100mm/min"},{"label":"C","text":"200mm/min"},{"label":"D","text":"500mm/min"}],'C','聚氨酯涂料拉伸速率200mm/min','formula')
add_q('建筑材料检测','防水材料检测','single',2,'SBS改性沥青防水卷材的耐热度要求？',[{"label":"A","text":"70℃"},{"label":"B","text":"80℃"},{"label":"C","text":"90℃"},{"label":"D","text":"100℃"}],'C','SBS卷材耐热度不低于90℃','formula')
add_q('建筑材料检测','防水材料检测','multi',2,'防水材料主要检测项目包括？',[{"label":"A","text":"拉力"},{"label":"B","text":"延伸率"},{"label":"C","text":"不透水性"},{"label":"D","text":"耐热度"}],'ABCD','拉力、延伸率、不透水性、耐热度为主要检测项目','basic')

# 砌体材料
add_q('建筑材料检测','砌体材料检测','single',1,'烧结普通砖的标准尺寸是多少？',[{"label":"A","text":"240×115×53mm"},{"label":"B","text":"240×120×60mm"},{"label":"C","text":"200×100×50mm"},{"label":"D","text":"240×115×90mm"}],'A','标准砖尺寸240×115×53mm','basic')
add_q('建筑材料检测','砌体材料检测','single',2,'MU10烧结砖的抗压强度平均值要求？',[{"label":"A","text":"5MPa"},{"label":"B","text":"10MPa"},{"label":"C","text":"15MPa"},{"label":"D","text":"20MPa"}],'B','MU10表示抗压强度平均值不低于10MPa','formula')
add_q('建筑材料检测','砌体材料检测','single',3,'砂浆稠度试验用什么仪器？',[{"label":"A","text":"维卡仪"},{"label":"B","text":"砂浆稠度仪"},{"label":"C","text":"坍落度筒"},{"label":"D","text":"贯入阻力仪"}],'B','砂浆稠度仪(沉入度法)测定砂浆稠度','practical')

# 保温材料
add_q('建筑材料检测','保温材料检测','single',2,'EPS板导热系数检测常用什么方法？',[{"label":"A","text":"防护热板法"},{"label":"B","text":"热流计法"},{"label":"C","text":"热线法"},{"label":"D","text":"以上都是"}],'D','防护热板法、热流计法、热线法均可用于检测','basic')
add_q('建筑材料检测','保温材料检测','single',3,'XPS挤塑板的吸水率要求是多少？',[{"label":"A","text":"≤1.0%"},{"label":"B","text":"≤1.5%"},{"label":"C","text":"≤2.0%"},{"label":"D","text":"≤3.0%"}],'B','XPS板吸水率不大于1.5%','formula')
add_q('建筑材料检测','保温材料检测','truefalse',2,'保温材料导热系数越小，保温性能越好。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','导热系数小说明热阻大，保温性能好','basic')

# === 主体结构检测 ===
add_q('主体结构检测','混凝土强度检测','single',2,'回弹仪率定值应为多少？',[{"label":"A","text":"78±2"},{"label":"B","text":"80±2"},{"label":"C","text":"82±2"},{"label":"D","text":"85±2"}],'B','回弹仪率定值应为80±2','formula')
add_q('主体结构检测','混凝土强度检测','single',3,'钻芯法芯样的高径比应为多少？',[{"label":"A","text":"0.5"},{"label":"B","text":"0.8"},{"label":"C","text":"1.0"},{"label":"D","text":"1.5"}],'C','芯样高径比1.0（直径70-100mm时）','standard')
add_q('主体结构检测','混凝土强度检测','single',2,'回弹法碳化深度测量用什么试剂？',[{"label":"A","text":"酚酞酒精溶液"},{"label":"B","text":"甲基橙"},{"label":"C","text":"石蕊"},{"label":"D","text":"碘液"}],'A','用1%酚酞酒精溶液，变红色处为碳化深度','practical')
add_q('主体结构检测','混凝土强度检测','single',1,'回弹法检测混凝土强度的原理是什么？',[{"label":"A","text":"利用超声波速度"},{"label":"B","text":"利用表面硬度与强度相关性"},{"label":"C","text":"利用电磁感应"},{"label":"D","text":"利用红外热像"}],'B','回弹法基于混凝土表面硬度与抗压强度的相关性','basic')
add_q('主体结构检测','混凝土强度检测','multi',3,'影响回弹法检测精度的因素有哪些？',[{"label":"A","text":"碳化深度"},{"label":"B","text":"测试角度"},{"label":"C","text":"浇筑面"},{"label":"D","text":"龄期"}],'ABCD','碳化深度、测试角度、浇筑面、龄期均影响检测精度','important')
add_q('主体结构检测','混凝土强度检测','composite',4,'说明回弹法检测混凝土强度的基本步骤和注意事项。','[]','选测区→清测面→弹击16点→测碳化→查表换算','步骤：选择测区(不少于10个/构件)、清理测面、每区弹击16点、测量碳化深度、查表换算强度。注意：避开蜂窝麻面、做角度修正、碳化深度修正、龄期修正。','practical')

add_q('主体结构检测','混凝土缺陷检测','single',3,'超声法检测混凝土裂缝深度，对测法的适用条件是什么？',[{"label":"A","text":"裂缝深度小于500mm"},{"label":"B","text":"可两面对测"},{"label":"C","text":"裂缝有水"},{"label":"D","text":"表面裂缝"}],'B','对测法要求裂缝两侧均可放置换能器','practical')
add_q('主体结构检测','混凝土缺陷检测','single',3,'超声波在正常混凝土中的传播速度一般为多少？',[{"label":"A","text":"1000-2000m/s"},{"label":"B","text":"2000-4000m/s"},{"label":"C","text":"3000-5000m/s"},{"label":"D","text":"5000-7000m/s"}],'C','正常混凝土中超声波速约3000-5000m/s','formula')

add_q('主体结构检测','砌体结构检测','single',2,'砂浆回弹仪的冲击能量是多少？',[{"label":"A","text":"0.196J"},{"label":"B","text":"0.735J"},{"label":"C","text":"2.207J"},{"label":"D","text":"4.5J"}],'A','砂浆回弹仪冲击能量0.196J','formula')
add_q('主体结构检测','砌体结构检测','single',3,'贯入法检测砂浆强度，贯入深度与强度的关系？',[{"label":"A","text":"正比"},{"label":"B","text":"反比"},{"label":"C","text":"无关"},{"label":"D","text":"非线性"}],'B','贯入深度越大，砂浆强度越低','basic')

add_q('主体结构检测','钢结构焊缝检测','single',2,'磁粉检测(MT)适用于检测什么缺陷？',[{"label":"A","text":"内部缺陷"},{"label":"B","text":"表面及近表面缺陷"},{"label":"C","text":"体积型缺陷"},{"label":"D","text":"所有缺陷"}],'B','MT检测铁磁性材料表面及近表面缺陷','basic')
add_q('主体结构检测','钢结构焊缝检测','single',3,'超声波检测(UT)焊缝探伤常用频率是多少？',[{"label":"A","text":"1MHz"},{"label":"B","text":"2.5MHz"},{"label":"C","text":"5MHz"},{"label":"D","text":"10MHz"}],'C','焊缝UT常用2.5-5MHz','formula')
add_q('主体结构检测','钢结构焊缝检测','single',2,'射线检测(RT)底片黑度要求是多少？',[{"label":"A","text":"1.0-2.0"},{"label":"B","text":"1.5-3.5"},{"label":"C","text":"2.0-4.0"},{"label":"D","text":"2.5-4.5"}],'B','底片黑度A级1.5-3.5，B级2.0-4.0','standard')
add_q('主体结构检测','钢结构焊缝检测','multi',2,'焊缝无损检测常用方法包括哪些？',[{"label":"A","text":"磁粉检测MT"},{"label":"B","text":"超声波检测UT"},{"label":"C","text":"射线检测RT"},{"label":"D","text":"渗透检测PT"}],'ABCD','四种常用NDT方法：MT、UT、RT、PT','basic')
add_q('主体结构检测','钢结构焊缝检测','truefalse',2,'渗透检测(PT)可用于非铁磁性材料的检测。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','PT适用于非铁磁性材料如不锈钢、铝合金','standard')

add_q('主体结构检测','钢结构涂层检测','single',2,'防腐涂层干膜厚度检测用什么仪器？',[{"label":"A","text":"超声波测厚仪"},{"label":"B","text":"磁性测厚仪"},{"label":"C","text":"涡流测厚仪"},{"label":"D","text":"磁性和涡流测厚仪均可"}],'D','磁性(钢铁基材)或涡流(非磁性)测厚仪','practical')

add_q('主体结构检测','结构变形监测','single',2,'沉降观测的精度要求是多少？',[{"label":"A","text":"±0.1mm"},{"label":"B","text":"±0.5mm"},{"label":"C","text":"±1.0mm"},{"label":"D","text":"±2.0mm"}],'B','二等水准测量精度±0.5mm','formula')
add_q('主体结构检测','结构变形监测','single',3,'裂缝监测贴石膏标志的作用是什么？',[{"label":"A","text":"美观装饰"},{"label":"B","text":"监测裂缝是否发展"},{"label":"C","text":"填充裂缝"},{"label":"D","text":"加固结构"}],'B','石膏标志开裂说明裂缝在继续发展','practical')

# === 地基基础检测 ===
add_q('地基基础检测','桩基静载试验','single',2,'单桩竖向抗压静载试验的标准加载方式是什么？',[{"label":"A","text":"快速维持荷载法"},{"label":"B","text":"慢速维持荷载法"},{"label":"C","text":"循环加载法"},{"label":"D","text":"等速率加载法"}],'B','慢速维持荷载法是标准加载方式','standard')
add_q('地基基础检测','桩基静载试验','single',3,'慢速法每级荷载为预估极限承载力的多少？',[{"label":"A","text":"1/5"},{"label":"B","text":"1/8"},{"label":"C","text":"1/10"},{"label":"D","text":"1/15"}],'C','每级荷载为预估极限承载力的1/10','formula')
add_q('地基基础检测','桩基静载试验','single',3,'桩基静载试验的终止加载条件包括？',[{"label":"A","text":"沉降急剧增大"},{"label":"B","text":"累计沉降超过40mm"},{"label":"C","text":"桩身破坏"},{"label":"D","text":"以上都是"}],'D','满足任一终止条件即可停止加载','standard')
add_q('地基基础检测','桩基静载试验','composite',4,'试述单桩竖向抗压静载试验的目的、装置和基本步骤。','[]','目的：确定极限承载力。装置：反力架+千斤顶+百分表。步骤：安装→分级加载→维持稳定→记录→卸载','目的：确定单桩竖向抗压极限承载力。装置：反力装置(锚桩法或堆载法)+千斤顶+百分表。步骤：安装设备、分级加载(每级Q/10)、维持沉降稳定、记录荷载-沉降曲线、卸载观测回弹。','important')

add_q('地基基础检测','桩基动测法','single',2,'低应变法检测桩身完整性的原理是什么？',[{"label":"A","text":"应力波反射"},{"label":"B","text":"超声波透射"},{"label":"C","text":"钻芯取样"},{"label":"D","text":"电磁感应"}],'A','利用应力波在桩身中的反射特性检测完整性','basic')
add_q('地基基础检测','桩基动测法','single',3,'低应变法传感器应安装在什么位置？',[{"label":"A","text":"桩顶中心"},{"label":"B","text":"距桩中心2/3半径处"},{"label":"C","text":"桩顶边缘"},{"label":"D","text":"桩侧"}],'B','传感器安装在距桩中心约2/3半径处','practical')
add_q('地基基础检测','桩基动测法','single',3,'高应变法使用的锤重约为桩重的多少？',[{"label":"A","text":"1%"},{"label":"B","text":"2%-5%"},{"label":"C","text":"10%"},{"label":"D","text":"20%"}],'B','锤重约为桩重的2%-5%','formula')

add_q('地基基础检测','桩基完整性检测','single',2,'声波透射法应预埋多少根检测管？',[{"label":"A","text":"1根"},{"label":"B","text":"2根"},{"label":"C","text":"3根或更多"},{"label":"D","text":"不需要"}],'C','桩径不大于1.5m埋3管，大于1.5m埋4管或更多','standard')
add_q('地基基础检测','桩基完整性检测','single',3,'声波透射法判定桩身缺陷的指标有哪些？',[{"label":"A","text":"声速降低"},{"label":"B","text":"波幅降低"},{"label":"C","text":"波形畸变"},{"label":"D","text":"以上都是"}],'D','声速、波幅、波形综合判定桩身缺陷','important')

add_q('地基基础检测','地基承载力检测','single',2,'平板载荷试验承压板面积一般为多少？',[{"label":"A","text":"0.25m²"},{"label":"B","text":"0.5m²"},{"label":"C","text":"1.0m²"},{"label":"D","text":"视土质而定"}],'D','一般0.25-0.5m²，软土可用1.0m²','practical')
add_q('地基基础检测','地基承载力检测','single',2,'标准贯入试验的锤击数N值代表什么？',[{"label":"A","text":"土壤含水量"},{"label":"B","text":"土的密实度"},{"label":"C","text":"土壤塑性"},{"label":"D","text":"土壤颜色"}],'B','N值反映土的密实度和力学性质','basic')
add_q('地基基础检测','地基承载力检测','truefalse',2,'标准贯入试验适用于碎石土。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'错误','标贯适用于砂土和粉土，碎石土用动力触探','standard')

add_q('地基基础检测','基坑监测','single',2,'基坑深层水平位移监测用什么方法？',[{"label":"A","text":"水准仪"},{"label":"B","text":"测斜仪"},{"label":"C","text":"全站仪"},{"label":"D","text":"经纬仪"}],'B','测斜仪(测斜管)监测深层水平位移','practical')
add_q('地基基础检测','基坑监测','single',3,'基坑监测预警值一般为控制值的多少？',[{"label":"A","text":"50%"},{"label":"B","text":"60%"},{"label":"C","text":"70%"},{"label":"D","text":"80%"}],'D','预警值一般为控制值的70%-80%','formula')

add_q('地基基础检测','复合地基检测','single',3,'水泥搅拌桩复合地基承载力检测用什么方法？',[{"label":"A","text":"平板静载试验"},{"label":"B","text":"动力触探"},{"label":"C","text":"标贯试验"},{"label":"D","text":"十字板剪切"}],'A','复合地基承载力用平板静载试验确定','standard')

# === 建筑节能检测 ===
add_q('建筑节能检测','墙体热工性能','single',2,'热流计法检测墙体传热系数，稳态条件需持续多长时间？',[{"label":"A","text":"24小时"},{"label":"B","text":"48小时"},{"label":"C","text":"72小时"},{"label":"D","text":"96小时"}],'C','稳态法需持续监测72小时以上','formula')
add_q('建筑节能检测','墙体热工性能','single',2,'传热系数K值的单位是什么？',[{"label":"A","text":"W/(m·K)"},{"label":"B","text":"W/(m²·K)"},{"label":"C","text":"J/(kg·K)"},{"label":"D","text":"m²·K/W"}],'B','K值单位为W/(m²·K)','formula')
add_q('建筑节能检测','墙体热工性能','single',3,'红外热像法检测外墙缺陷的原理是什么？',[{"label":"A","text":"检测温度差异"},{"label":"B","text":"检测湿度变化"},{"label":"C","text":"检测应力分布"},{"label":"D","text":"检测裂缝分布"}],'A','缺陷部位(空鼓、渗漏)与正常部位存在温度差异','basic')
add_q('建筑节能检测','墙体热工性能','truefalse',2,'传热系数越小，墙体保温性能越好。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','K值越小说明热阻越大，保温性能越好','basic')

add_q('建筑节能检测','外窗三性检测','single',2,'外窗气密性等级最高为几级？',[{"label":"A","text":"6级"},{"label":"B","text":"8级"},{"label":"C","text":"10级"},{"label":"D","text":"12级"}],'B','气密性8级为最高等级(GB/T 7106)','standard')
add_q('建筑节能检测','外窗三性检测','single',3,'水密性检测的加压方式如何选择？',[{"label":"A","text":"稳定加压"},{"label":"B","text":"波动加压"},{"label":"C","text":"先稳定后波动"},{"label":"D","text":"根据设计要求确定"}],'D','根据设计要求选择稳定或波动加压方式','practical')
add_q('建筑节能检测','外窗三性检测','multi',2,'外窗三性检测包括哪三项？',[{"label":"A","text":"气密性"},{"label":"B","text":"水密性"},{"label":"C","text":"抗风压性能"},{"label":"D","text":"隔声性能"}],'ABC','三性：气密性、水密性、抗风压性能','basic')

add_q('建筑节能检测','外保温系统检测','single',3,'外保温系统耐候性试验的循环次数是多少？',[{"label":"A","text":"5次"},{"label":"B","text":"10次"},{"label":"C","text":"20次"},{"label":"D","text":"80次"}],'D','耐候性试验80次高温-淋水循环+20次加热-冷冻循环','formula')
add_q('建筑节能检测','外保温系统检测','single',3,'外保温粘结强度现场拉拔试验要求不低于多少？',[{"label":"A","text":"0.1MPa"},{"label":"B","text":"0.3MPa"},{"label":"C","text":"0.5MPa"},{"label":"D","text":"1.0MPa"}],'B','现场拉拔粘结强度不低于0.3MPa','formula')

add_q('建筑节能检测','建筑能效评估','single',2,'建筑能效等级分为几级？',[{"label":"A","text":"3级"},{"label":"B","text":"4级"},{"label":"C","text":"5级"},{"label":"D","text":"6级"}],'C','建筑能效等级分1-5级，1级最节能','basic')
add_q('建筑节能检测','采暖系统检测','single',3,'室内温度检测的测点高度应为多少？',[{"label":"A","text":"0.5m"},{"label":"B","text":"0.8m"},{"label":"C","text":"1.0m"},{"label":"D","text":"1.5m"}],'C','测点距地面1.0m，距墙不小于0.5m','practical')

# === 室内环境检测 ===
add_q('室内环境检测','甲醛检测','single',2,'GB50325规定I类民用建筑甲醛限量是多少？',[{"label":"A","text":"0.05mg/m³"},{"label":"B","text":"0.07mg/m³"},{"label":"C","text":"0.08mg/m³"},{"label":"D","text":"0.10mg/m³"}],'C','I类不超过0.08mg/m³，II类不超过0.10mg/m³','standard')
add_q('室内环境检测','甲醛检测','single',2,'酚试剂法检测甲醛的采样流量是多少？',[{"label":"A","text":"0.2L/min"},{"label":"B","text":"0.5L/min"},{"label":"C","text":"1.0L/min"},{"label":"D","text":"2.0L/min"}],'B','采样流量0.5L/min','formula')
add_q('室内环境检测','甲醛检测','single',3,'室内甲醛检测采样前应关闭门窗多长时间？',[{"label":"A","text":"1小时"},{"label":"B","text":"6小时"},{"label":"C","text":"12小时"},{"label":"D","text":"24小时"}],'C','GB50325规定关闭门窗12小时后采样','standard')
add_q('室内环境检测','甲醛检测','multi',2,'室内甲醛检测常用方法有哪些？',[{"label":"A","text":"AHMT法"},{"label":"B","text":"酚试剂法"},{"label":"C","text":"气相色谱法"},{"label":"D","text":"乙酰丙酮法"}],'ABCD','四种常用甲醛检测方法','basic')
add_q('室内环境检测','甲醛检测','truefalse',1,'GB50325适用于所有民用建筑工程。',[{"label":"正确","text":"正确"},{"label":"错误","text":"错误"}],'正确','GB50325适用于新建、扩建和改建的民用建筑工程','standard')

add_q('室内环境检测','苯系物检测','single',2,'GB50325规定I类民用建筑苯的限量是多少？',[{"label":"A","text":"0.05mg/m³"},{"label":"B","text":"0.06mg/m³"},{"label":"C","text":"0.09mg/m³"},{"label":"D","text":"0.11mg/m³"}],'C','I类苯不超过0.09mg/m³','formula')
add_q('室内环境检测','苯系物检测','single',3,'苯系物检测采样用什么吸附管？',[{"label":"A","text":"活性炭管"},{"label":"B","text":"Tenax管"},{"label":"C","text":"硅胶管"},{"label":"D","text":"分子筛管"}],'A','活性炭管吸附苯系物，二硫化碳解吸','practical')

add_q('室内环境检测','TVOC检测','single',2,'GB50325规定I类民用建筑TVOC限量是多少？',[{"label":"A","text":"0.2mg/m³"},{"label":"B","text":"0.45mg/m³"},{"label":"C","text":"0.5mg/m³"},{"label":"D","text":"0.6mg/m³"}],'B','I类TVOC不超过0.45mg/m³','formula')
add_q('室内环境检测','TVOC检测','single',3,'TVOC检测的标准方法是什么？',[{"label":"A","text":"气相色谱法"},{"label":"B","text":"液相色谱法"},{"label":"C","text":"光谱法"},{"label":"D","text":"重量法"}],'A','Tenax吸附/热脱附-气相色谱法','basic')

add_q('室内环境检测','氡气检测','single',2,'室内氡浓度限值(I类)是多少？',[{"label":"A","text":"100Bq/m³"},{"label":"B","text":"150Bq/m³"},{"label":"C","text":"200Bq/m³"},{"label":"D","text":"400Bq/m³"}],'C','I类不超过200Bq/m³','formula')
add_q('室内环境检测','氡气检测','single',3,'连续测氡仪的采样时间应不少于多少？',[{"label":"A","text":"1小时"},{"label":"B","text":"6小时"},{"label":"C","text":"12小时"},{"label":"D","text":"24小时"}],'D','连续测量不少于24小时','formula')

add_q('室内环境检测','氨检测','single',2,'GB50325规定I类民用建筑氨的限量是多少？',[{"label":"A","text":"0.1mg/m³"},{"label":"B","text":"0.15mg/m³"},{"label":"C","text":"0.2mg/m³"},{"label":"D","text":"0.5mg/m³"}],'C','I类氨不超过0.2mg/m³','formula')
add_q('室内环境检测','氨检测','single',3,'靛酚蓝分光光度法检测氨的原理是什么？',[{"label":"A","text":"比色法"},{"label":"B","text":"滴定法"},{"label":"C","text":"重量法"},{"label":"D","text":"电化学法"}],'A','氨与次氯酸钠和苯酚反应生成靛酚蓝化合物进行比色','practical')

add_q('室内环境检测','采样规范','single',2,'室内环境检测采样点布置原则是什么？',[{"label":"A","text":"对角线布点"},{"label":"B","text":"梅花形布点"},{"label":"C","text":"面积≤50m²设1-3个点"},{"label":"D","text":"均匀分布"}],'C','面积≤50m²设1-3点，50-100m²设3-5点','standard')
add_q('室内环境检测','采样规范','single',3,'采样时室内温度应控制在什么范围？',[{"label":"A","text":"15-25℃"},{"label":"B","text":"18-28℃"},{"label":"C","text":"20-30℃"},{"label":"D","text":"无特殊要求"}],'B','GB50325规定采样时温度18-28℃','standard')
add_q('室内环境检测','采样规范','multi',3,'GB50325规定的室内环境污染物包括哪些？',[{"label":"A","text":"甲醛"},{"label":"B","text":"苯"},{"label":"C","text":"TVOC"},{"label":"D","text":"氡"},{"label":"E","text":"氨"}],'ABCDE','5种：甲醛、苯、TVOC、氡、氨','high')

conn.commit()
qcount = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
print(f"题目: {qcount}")

# === 试卷 ===
conn.execute("DELETE FROM exams")
conn.execute("DELETE FROM exam_templates")
conn.execute("DELETE FROM exam_results")
all_qids = [r[0] for r in conn.execute('SELECT id FROM questions WHERE is_active=1').fetchall()]
for title, mode, dur, total, ps, count in [
    ('建筑材料检测模拟卷一','mock',60,100,60,20),('建筑材料检测模拟卷二','mock',60,100,60,20),
    ('主体结构检测模拟卷','mock',90,100,60,20),('地基基础检测练习卷','mock',45,100,60,15),
    ('建筑节能检测模拟卷','mock',60,100,60,15),('室内环境检测模拟卷','mock',60,100,60,15),
    ('全科综合模拟考试','mock',120,100,60,30),
    ('建筑材料检测正式考试','formal',90,100,60,20),('主体结构检测正式考试','formal',90,100,60,20),
    ('地基基础检测正式考试','formal',60,100,60,15),('建筑节能检测正式考试','formal',60,100,60,15),
    ('室内环境检测正式考试','formal',60,100,60,15),
]:
    sel = json.dumps(random.sample(all_qids, min(count, len(all_qids))))
    conn.execute("INSERT INTO exams (title,description,mode,duration_minutes,total_score,pass_score,question_ids,is_published,shuffle_questions,shuffle_options,max_tab_switches) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (title, f'{title} - 建筑检测行业专业考试', mode, dur, total, ps, sel, 1, 1, 1, 3))
conn.commit()
print(f"试卷: {conn.execute('SELECT COUNT(*) FROM exams').fetchone()[0]}")

# === 考试成绩 ===
students = [(r[0],r[1]) for r in conn.execute("SELECT id,fullname FROM users WHERE role IN ('student','inspector')").fetchall()]
exams = [(r[0],r[1],r[2]) for r in conn.execute('SELECT id,total_score,pass_score FROM exams').fetchall()]
for uid, uname in students:
    for eid, total, ps in random.sample(exams, min(4, len(exams))):
        score = round(random.uniform(ps*0.3, total*0.98), 1)
        passed = 1 if score >= ps else 0
        conn.execute("INSERT INTO exam_results (exam_id,user_id,answers,auto_score,total_score,passed,tab_switches,is_cheating) VALUES (?,?,?,?,?,?,?,?)",
            (eid, uid, '{}', score, total, passed, random.randint(0,2), 0))
conn.commit()
print(f"考试成绩: {conn.execute('SELECT COUNT(*) FROM exam_results').fetchone()[0]}")

# === 练习记录 ===
conn.execute("DELETE FROM practice_records")
sids = [r[0] for r in conn.execute('SELECT id FROM subjects').fetchall()]
for uid, _ in students:
    for _ in range(random.randint(3,6)):
        total = random.randint(10,30)
        correct = random.randint(int(total*0.3), total)
        conn.execute("INSERT INTO practice_records (user_id,mode,subject_id,total_count,correct_count,wrong_count,duration_seconds) VALUES (?,?,?,?,?,?,?)",
            (uid, random.choice(['random','chapter','memorize']), random.choice(sids), total, correct, total-correct, random.randint(120,3600)))
conn.commit()
print(f"练习记录: {conn.execute('SELECT COUNT(*) FROM practice_records').fetchone()[0]}")

# === 错题本 ===
conn.execute("DELETE FROM wrong_answers")
for uid, _ in students:
    for qid in random.sample(all_qids, min(10, len(all_qids))):
        conn.execute("INSERT INTO wrong_answers (user_id,question_id,is_mastered) VALUES (?,?,0)", (uid, qid))
conn.commit()
print(f"错题本: {conn.execute('SELECT COUNT(*) FROM wrong_answers').fetchone()[0]}")

# === 收藏夹 ===
conn.execute("DELETE FROM favorites")
for uid, _ in students:
    for qid in random.sample(all_qids, min(8, len(all_qids))):
        conn.execute("INSERT INTO favorites (user_id,question_id) VALUES (?,?)", (uid, qid))
conn.commit()
print(f"收藏夹: {conn.execute('SELECT COUNT(*) FROM favorites').fetchone()[0]}")

# === 笔记 ===
conn.execute("DELETE FROM notes")
notes_cn = [
    '水泥安定性是高频考点，记住雷氏夹法和试饼法的区别',
    '回弹法16个弹击点均匀分布，碳化深度用酚酞酒精溶液检测',
    '桩基静载试验用慢速维持荷载法，每级荷载为极限承载力的1/10',
    'GB50325 I类建筑限量：甲醛0.08、苯0.09、TVOC0.45、氡200、氨0.2',
    'SBS防水卷材不透水性试验0.3MPa保持30分钟不渗透',
    'HRB400屈服强度400MPa，抗拉强度540MPa，强屈比不小于1.25',
    '混凝土标准养护条件：温度20±2℃，相对湿度≥95%',
    '声波透射法桩径≤1.5m埋3管，>1.5m埋4管或更多',
    '外窗气密性8级为最高等级，水密性根据设计要求选择加压方式',
    '外墙保温传热系数K值单位W/(m²·K)，K值越小保温越好',
]
for uid, _ in students[:4]:
    for note in random.sample(notes_cn, min(3, len(notes_cn))):
        conn.execute("INSERT INTO notes (user_id,question_id,content) VALUES (?,?,?)", (uid, random.choice(all_qids), note))
conn.commit()
print(f"笔记: {conn.execute('SELECT COUNT(*) FROM notes').fetchone()[0]}")

# === 公告 ===
conn.execute("DELETE FROM announcements")
for title, content, pinned, pub in [
    ('建筑检测在线题库系统正式上线','欢迎各位建筑检测从业人员使用本系统进行专业学习和考试。系统涵盖建筑材料、主体结构、地基基础、建筑节能、室内环境五大检测领域，共计122道专业题目，12套考试试卷。',1,1),
    ('2026年6月份考试安排','本月模拟考试已全部开放，正式考试将于6月25日至30日举行。请各位学员认真备考，考试科目包括全部五个检测领域。',1,1),
    ('新增题库通知','系统已新增室内环境检测和建筑节能检测两大科目题库，包含甲醛、苯系物、TVOC、氡、氨等检测方法及GB50325标准要求，欢迎大家练习。',1,1),
    ('证书申请指南','练习各章节通过率≥60%可申请练习证书；正式考试60分以上自动颁发考试证书。详情可前往证书中心查看。',0,1),
    ('系统维护公告','系统将于6月20日凌晨2:00-4:00进行维护升级，届时暂停服务，请提前安排好学习计划。',0,1),
]:
    conn.execute("INSERT INTO announcements (title,content,is_pinned,is_published,created_by) VALUES (?,?,?,?,?)", (title,content,pinned,pub,'系统管理员'))
conn.commit()
print(f"公告: {conn.execute('SELECT COUNT(*) FROM announcements').fetchone()[0]}")

# === 证书 ===
conn.execute("DELETE FROM user_certificates")
conn.execute("DELETE FROM certificates")
for name, ctype, desc, chid in [
    ('建筑材料检测练习合格证','practice','通过建筑材料检测科目练习，正确率≥60%',1),
    ('主体结构检测练习合格证','practice','通过主体结构检测科目练习，正确率≥60%',2),
    ('地基基础检测练习合格证','practice','通过地基基础检测科目练习，正确率≥60%',3),
    ('建筑节能检测练习合格证','practice','通过建筑节能检测科目练习，正确率≥60%',4),
    ('室内环境检测练习合格证','practice','通过室内环境检测科目练习，正确率≥60%',5),
    ('建筑材料检测考试证书','exam','建筑材料检测正式考试合格',None),
    ('主体结构检测考试证书','exam','主体结构检测正式考试合格',None),
    ('综合检测能力认证','exam','多项正式考试通过后的综合能力认证',None),
]:
    conn.execute("INSERT INTO certificates (name,cert_type,description,chapter_id,template_image,issue_rule) VALUES (?,?,?,?,?,?)", (name,ctype,desc,chid,'','{}'))
conn.commit()
cert_ids = [r[0] for r in conn.execute('SELECT id FROM certificates').fetchall()]
for cid in random.sample(cert_ids, min(4, len(cert_ids))):
    for uid, _ in random.sample(students, min(3, len(students))):
        conn.execute("INSERT INTO user_certificates (certificate_id,user_id,certificate_no,is_revoked) VALUES (?,?,?,0)",
            (cid, uid, 'CERT-'+uuid.uuid4().hex[:12].upper()))
conn.commit()
print(f"证书: {conn.execute('SELECT COUNT(*) FROM certificates').fetchone()[0]}")
print(f"已颁发: {conn.execute('SELECT COUNT(*) FROM user_certificates').fetchone()[0]}")

# === 通知 ===
conn.execute("DELETE FROM notifications")
for uid, _ in students:
    for title, content, ntype in random.sample([
        ('考试提醒','6月份正式考试将于6月25日开始，请做好备考准备。','info'),
        ('证书颁发','恭喜你通过建筑材料检测考试，证书已颁发！','success'),
        ('练习提醒','你已连续3天未练习，建议保持学习节奏。','warning'),
        ('新题通知','室内环境检测题库已更新，新增30道专业题目。','info'),
        ('成绩公布','主体结构检测模拟考试成绩已公布，请前往查看。','info'),
    ], 3):
        conn.execute("INSERT INTO notifications (user_id,type,title,content,is_read) VALUES (?,?,?,?,?)",
            (uid, ntype, title, content, random.randint(0,1)))
conn.commit()
print(f"通知: {conn.execute('SELECT COUNT(*) FROM notifications').fetchone()[0]}")

# === 异常报告 ===
conn.execute("DELETE FROM abnormal_reports")
er_ids = [r[0] for r in conn.execute('SELECT id FROM exam_results LIMIT 3').fetchall()]
for i, (reason, detail) in enumerate([('tab_switch','正式考试期间切屏3次，已自动交卷'),('tab_switch','正式考试期间切屏1次，已记录'),('right_click','尝试右键复制题目内容'),('paste','尝试粘贴外部内容到答题区')]):
    if er_ids:
        conn.execute("INSERT INTO abnormal_reports (exam_result_id,user_id,reason,detail,is_judged) VALUES (?,?,?,?,0)",
            (er_ids[i%len(er_ids)], students[i%len(students)][0], reason, detail))
conn.commit()
print(f"异常报告: {conn.execute('SELECT COUNT(*) FROM abnormal_reports').fetchone()[0]}")

# === 重考申请 ===
conn.execute("DELETE FROM retake_applications")
if er_ids:
    conn.execute("INSERT INTO retake_applications (exam_id,user_id,reason,status) VALUES (?,?,?,?)", (1, students[0][0], '考试时网络中断，请求重考', 'pending'))
    conn.execute("INSERT INTO retake_applications (exam_id,user_id,reason,status) VALUES (?,?,?,?)", (2, students[1][0], '身体不适中途退出，申请重考', 'pending'))
conn.commit()
print(f"重考申请: {conn.execute('SELECT COUNT(*) FROM retake_applications').fetchone()[0]}")

# === 学习资料 ===
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
if 'resources' in tables:
    conn.execute("DELETE FROM resources")
    for title, ftype, sid, desc, url in [
        ('GB 175-2007 通用硅酸盐水泥标准','pdf',1,'国家标准：水泥质量检测依据','/uploads/gb175.pdf'),
        ('GB/T 50081-2019 混凝土力学性能试验方法标准','pdf',2,'混凝土强度检测标准方法','/uploads/gb50081.pdf'),
        ('JGJ/T 23-2011 回弹法检测混凝土抗压强度技术规程','pdf',2,'回弹法检测技术规程','/uploads/jgj23.pdf'),
        ('GB 50325-2020 民用建筑工程室内环境污染控制标准','pdf',5,'室内环境检测核心标准','/uploads/gb50325.pdf'),
        ('JGJ 106-2014 建筑基桩检测技术规范','pdf',3,'桩基检测技术规范','/uploads/jgj106.pdf'),
        ('建筑节能检测技术手册','pdf',4,'围护结构热工性能检测实用指南','/uploads/energy_manual.pdf'),
        ('室内环境检测实操指南','pdf',5,'采样方法、仪器操作、数据分析','/uploads/indoor_guide.pdf'),
        ('建筑材料检测习题集','pdf',1,'水泥、混凝土、钢材等检测练习题','/uploads/materials_problems.pdf'),
    ]:
        conn.execute("INSERT INTO resources (title,file_type,subject_id,description,file_url,created_by) VALUES (?,?,?,?,?,?)", (title,ftype,sid,desc,url,'admin'))
    conn.commit()
    print(f"学习资料: {conn.execute('SELECT COUNT(*) FROM resources').fetchone()[0]}")

# === 审计日志 ===
if 'audit_logs' in tables:
    conn.execute("DELETE FROM audit_logs")
    for uid, action, detail in [
        (1,'创建科目','创建了5个建筑检测科目'),(1,'导入题目','批量导入122道专业题目'),
        (1,'创建试卷','生成12套考试试卷'),(1,'发布公告','发布了系统上线公告'),
        (1,'颁发证书','向用户颁发了12份证书'),
    ]:
        conn.execute("INSERT INTO audit_logs (user_id,action,detail) VALUES (?,?,?)", (uid, action, detail))
    conn.commit()
    print(f"审计日志: {conn.execute('SELECT COUNT(*) FROM audit_logs').fetchone()[0]}")

# === 最终汇总 ===
print("\n=== 数据写入完成 ===")
for table, label in [
    ('users','用户'),('subjects','科目'),('chapters','章节'),('questions','题目'),
    ('exams','试卷'),('exam_results','考试成绩'),('practice_records','练习记录'),
    ('wrong_answers','错题本'),('favorites','收藏夹'),('notes','笔记'),
    ('announcements','公告'),('certificates','证书'),('user_certificates','已颁发证书'),
    ('notifications','通知'),('abnormal_reports','异常报告'),('retake_applications','重考申请'),
]:
    try: print(f"  {label}: {conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}")
    except: pass
conn.close()
