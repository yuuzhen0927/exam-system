# -*- coding: utf-8 -*-
"""Construction Inspection Exam System - Comprehensive Seed Data"""
import sqlite3, json, random, uuid, sys
from datetime import datetime, timedelta

DB = 'F:/CodexWorkspace/Project004_考试系统/src/backend/exam.db'
sys.path.insert(0, 'F:/CodexWorkspace/Project004_考试系统/src/backend')
from auth import hash_password

conn = sqlite3.connect(DB)

# 1. USERS
for u in [('zhangsan','123456','Zhang San','student'),('lisi','123456','Li Si','student'),
          ('wangwu','123456','Wang Wu','student'),('zhaomin','123456','Zhao Min','student'),
          ('sunqiang','123456','Sun Qiang','student'),('liuyang','123456','Liu Yang','student'),
          ('chenfuzeren','123456','Chen FZR','teacher'),('zhoujiance','123456','Zhou JC','inspector')]:
    conn.execute("INSERT OR IGNORE INTO users (username,hashed_password,fullname,role,is_active) VALUES (?,?,?,?,1)",
                 (u[0], hash_password(u[1]), u[2], u[3]))
conn.commit()
print(f"Users: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")

# 2. SUBJECTS & CHAPTERS
conn.execute("DELETE FROM chapters")
conn.execute("DELETE FROM SUBJECTS")
subj_data = [
    ('Materials Testing','Cement, concrete, steel, waterproof, masonry, insulation testing', [
        ('Cement Testing','Fineness, setting time, soundness, strength'),
        ('Concrete Testing','Mix ratio, slump, compressive strength, impermeability'),
        ('Steel Testing','Rebar mechanical properties, weld joints, prestressing'),
        ('Waterproof Testing','Membranes, coatings, sealants performance'),
        ('Masonry Testing','Brick, block, mortar strength and quality'),
        ('Insulation Testing','Thermal conductivity, compressive strength, water absorption'),
    ]),
    ('Structure Testing','Concrete, masonry, steel structure field testing', [
        ('Concrete Strength','Rebound, drilled core, ultrasonic-rebound combined'),
        ('Concrete Defects','Ultrasonic internal defects, crack depth'),
        ('Masonry Structure','Mortar strength, masonry compressive strength'),
        ('Steel Weld Inspection','Visual, MT/UT/RT/PT NDT'),
        ('Coating Inspection','Anti-corrosion and fire-proof coating thickness'),
        ('Deformation Monitoring','Settlement, tilt, crack, deflection monitoring'),
    ]),
    ('Foundation Testing','Pile testing, bearing capacity, pit monitoring', [
        ('Static Load Test','Single pile vertical compression/tension/horizontal'),
        ('Dynamic Testing','Low strain reflection, high strain method'),
        ('Pile Integrity','Crosshole sonic, drilled core method'),
        ('Bearing Capacity','Plate load test, SPT, dynamic probing'),
        ('Pit Monitoring','Lateral displacement, strut force, groundwater level'),
        ('Composite Foundation','Cement mixing pile, CFG pile, gravel pile'),
    ]),
    ('Energy Testing','Envelope thermal, window airtightness, HVAC efficiency', [
        ('Wall Thermal','Heat transfer coefficient, thermal resistance, thermal bridge'),
        ('Window Properties','Airtightness, water resistance, wind pressure resistance'),
        ('External Insulation','Weatherability, bond strength, impact resistance'),
        ('Energy Assessment','Energy consumption calculation, efficiency rating'),
        ('Heating System','Indoor temperature, system efficiency, pipe network balance'),
    ]),
    ('Indoor Environment','Formaldehyde, benzene, TVOC, radon, ammonia testing', [
        ('Formaldehyde','AHMT, phenolic reagent, GC method'),
        ('Benzene Series','GC detection of benzene, toluene, xylene'),
        ('TVOC Detection','Tenax adsorption/thermal desorption-GC method'),
        ('Radon Detection','Continuous radon monitor, activated carbon method'),
        ('Ammonia Detection','Indophenol blue spectrophotometry, ISE method'),
        ('Sampling Standards','Sampling point layout, condition control, sample preservation'),
    ]),
]
for sname, sdesc, chapters in subj_data:
    conn.execute("INSERT INTO subjects (name,description,sort_order) VALUES (?,?,?)", (sname, sdesc, subj_data.index((sname,sdesc,chapters))))
    sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i, (cname, cdesc) in enumerate(chapters):
        conn.execute("INSERT INTO chapters (subject_id,name,description,sort_order) VALUES (?,?,?,?)", (sid, cname, cdesc, i))
conn.commit()
print(f"Subjects: {conn.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]}")
print(f"Chapters: {conn.execute('SELECT COUNT(*) FROM chapters').fetchone()[0]}")

# Build chapter lookup
ch_map = {}
for r in conn.execute("SELECT id, subject_id, name FROM chapters").fetchall():
    ch_map[r[2]] = (r[0], r[1])

TAGS = {'high':'["High Freq","Must Know"]','easy':'["Easy Wrong","Trap"]',
        'basic':'["Basic","Entry"]','formula':'["Formula","Numerical"]',
        'standard':'["Standard","Code"]','practical':'["Practical","Field"]',
        'important':'["Important","Deep"]'}

def add_q(sname, cname, qtype, diff, content, options, answer, explanation, tag):
    ch_id, sid = ch_map.get(cname, (None, 1))
    conn.execute("INSERT INTO questions (subject_id,chapter_id,type,difficulty,content,options,answer,explanation,tags,images,is_active,version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (sid, ch_id, qtype, diff, content, json.dumps(options,ensure_ascii=False), answer, explanation, TAGS.get(tag,'[]'), '[]', 1, 1))

# === MATERIALS TESTING ===
# Cement (12 questions)
add_q('Materials Testing','Cement Testing','single',1,'Standard method for cement fineness?',[{"label":"A","text":"Negative pressure sieving"},{"label":"B","text":"Water sieving"},{"label":"C","text":"Specific surface area"},{"label":"D","text":"Manual sieving"}],'A','GB/T 1345 standard method','basic')
add_q('Materials Testing','Cement Testing','single',2,'Min initial setting time for Portland cement?',[{"label":"A","text":"30min"},{"label":"B","text":"45min"},{"label":"C","text":"60min"},{"label":"D","text":"90min"}],'B','GB 175: initial >=45min','standard')
add_q('Materials Testing','Cement Testing','single',2,'Methods for cement soundness?',[{"label":"A","text":"Le Chatelier"},{"label":"B","text":"Boiling method"},{"label":"C","text":"Pat test"},{"label":"D","text":"All above"}],'D','Both Le Chatelier and pat test require boiling','high')
add_q('Materials Testing','Cement Testing','single',3,'P.O 42.5 cement 28-day strength standard?',[{"label":"A","text":"22.5MPa"},{"label":"B","text":"32.5MPa"},{"label":"C","text":"42.5MPa"},{"label":"D","text":"52.5MPa"}],'C','P.O 42.5 means 28-day >=42.5MPa','formula')
add_q('Materials Testing','Cement Testing','single',1,'Instrument for standard consistency?',[{"label":"A","text":"Vicat apparatus"},{"label":"B","text":"Slump cone"},{"label":"C","text":"Penetration meter"},{"label":"D","text":"Blaine apparatus"}],'A','Vicat apparatus for standard consistency','basic')
add_q('Materials Testing','Cement Testing','single',2,'Cement mortar water-cement ratio in ISO method?',[{"label":"A","text":"0.40"},{"label":"B","text":"0.45"},{"label":"C","text":"0.50"},{"label":"D","text":"0.55"}],'C','ISO method W/C=0.50, cement:sand=1:3','formula')
add_q('Materials Testing','Cement Testing','single',3,'Max MgO content in Portland cement?',[{"label":"A","text":"3.0%"},{"label":"B","text":"5.0%"},{"label":"C","text":"6.0%"},{"label":"D","text":"8.0%"}],'B','GB 175: MgO<=5.0% (6.0% if autoclave OK)','standard')
add_q('Materials Testing','Cement Testing','multi',2,'Cement physical property indicators?',[{"label":"A","text":"Fineness"},{"label":"B","text":"Setting time"},{"label":"C","text":"Soundness"},{"label":"D","text":"Strength"},{"label":"E","text":"Chemistry"}],'ABCD','Physical: fineness, setting, soundness, strength','basic')
add_q('Materials Testing','Cement Testing','multi',3,'Factors affecting cement strength?',[{"label":"A","text":"W/C ratio"},{"label":"B","text":"Curing temp"},{"label":"C","text":"Curing humidity"},{"label":"D","text":"Age"},{"label":"E","text":"Fineness"}],'ABCDE','All factors affect strength development','important')
add_q('Materials Testing','Cement Testing','truefalse',1,'Finer cement always has higher early strength.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','Finer = faster hydration = higher early strength','basic')
add_q('Materials Testing','Cement Testing','truefalse',2,'Unsound cement can be downgraded for use.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'B','Unsound cement is strictly prohibited','standard')
add_q('Materials Testing','Cement Testing','composite',3,'Explain cement soundness problems: causes, detection, hazards.','[]','Free CaO/MgO or excess gypsum cause expansion cracking','Causes: free CaO/MgO, excess gypsum. Detection: Le Chatelier or pat test with boiling. Hazards: cracking, strength loss, structural failure.','important')

# Concrete (12 questions)
add_q('Materials Testing','Concrete Testing','single',1,'Standard curing for concrete specimens?',[{"label":"A","text":"20C,90%RH"},{"label":"B","text":"20+/-2C,>=95%RH"},{"label":"C","text":"25C,95%RH"},{"label":"D","text":"20+/-2C,90%RH"}],'B','Standard: 20+/-2C, >=95%RH','basic')
add_q('Materials Testing','Concrete Testing','single',1,'Standard cube specimen size?',[{"label":"A","text":"100mm"},{"label":"B","text":"150mm"},{"label":"C","text":"200mm"},{"label":"D","text":"150x300mm"}],'B','150x150x150mm standard cube','basic')
add_q('Materials Testing','Concrete Testing','single',2,'Slump test applicable range?',[{"label":"A","text":"<=10mm"},{"label":"B","text":"10-90mm"},{"label":"C","text":"10-220mm"},{"label":"D","text":">=220mm"}],'C','Slump for max aggregate <=40mm, slump 10-220mm','standard')
add_q('Materials Testing','Concrete Testing','single',2,'C30 concrete cube strength standard value?',[{"label":"A","text":"20MPa"},{"label":"B","text":"25MPa"},{"label":"C","text":"30MPa"},{"label":"D","text":"35MPa"}],'C','C30 = 30MPa standard cube strength','formula')
add_q('Materials Testing','Concrete Testing','single',3,'Impermeability grade P6 means?',[{"label":"A","text":"0.6MPa water pressure"},{"label":"B","text":"6MPa water pressure"},{"label":"C","text":"Coefficient 6"},{"label":"D","text":"6 specimens"}],'A','P6 = 0.6MPa without penetration','formula')
add_q('Materials Testing','Concrete Testing','single',2,'Rebound hammer test points per area?',[{"label":"A","text":"8"},{"label":"B","text":"12"},{"label":"C","text":"16"},{"label":"D","text":"20"}],'C','16 rebound points per test area','practical')
add_q('Materials Testing','Concrete Testing','multi',2,'Concrete durability indicators?',[{"label":"A","text":"Impermeability"},{"label":"B","text":"Frost resistance"},{"label":"C","text":"Carbonation resistance"},{"label":"D","text":"Cl- penetration"}],'ABCD','Durability: impermeability, frost, carbonation, Cl-','important')
add_q('Materials Testing','Concrete Testing','truefalse',1,'Concrete grade based on axial compressive strength.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'B','Based on CUBE compressive strength standard value','basic')
add_q('Materials Testing','Concrete Testing','composite',4,'Describe concrete mix design steps and key parameters.','[]','Steps: determine design strength, W/C ratio, water content, cement, sand ratio, aggregate, trial mix','Steps: 1.Design strength(fcu,0=fcu,k+1.645sigma); 2.W/C ratio; 3.Water content; 4.Cement content; 5.Sand ratio; 6.Aggregate; 7.Trial mix. Key: W/C, sand ratio, water, cement.','important')

# Steel (8 questions)
add_q('Materials Testing','Steel Testing','single',2,'HRB400 yield strength standard value?',[{"label":"A","text":"300MPa"},{"label":"B","text":"335MPa"},{"label":"C","text":"400MPa"},{"label":"D","text":"500MPa"}],'C','HRB400 yield >=400MPa','formula')
add_q('Materials Testing','Steel Testing','single',3,'Weld joint bend test mandrel diameter?',[{"label":"A","text":"3d"},{"label":"B","text":"4d"},{"label":"C","text":"5d"},{"label":"D","text":"6d"}],'B','d=diameter, mandrel=4d','standard')
add_q('Materials Testing','Steel Testing','single',2,'Rebar tensile test gauge length?',[{"label":"A","text":"5d"},{"label":"B","text":"10d"},{"label":"C","text":"5.65*sqrt(S0)"},{"label":"D","text":"200mm"}],'C','Proportional gauge L0=5.65*sqrt(S0)~5d','formula')
add_q('Materials Testing','Steel Testing','single',1,'Rebar mechanical properties include?',[{"label":"A","text":"Yield strength"},{"label":"B","text":"Tensile strength"},{"label":"C","text":"Elongation"},{"label":"D","text":"All above"}],'D','Yield, tensile, elongation are main indicators','basic')
add_q('Materials Testing','Steel Testing','multi',3,'Weld joint test items?',[{"label":"A","text":"Tensile"},{"label":"B","text":"Bend"},{"label":"C","text":"Impact"},{"label":"D","text":"Hardness"}],'ABD','Tensile, bend, hardness (impact not required)','practical')
add_q('Materials Testing','Steel Testing','truefalse',2,'HRB500 tensile/yield ratio >=1.25.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','Ratio = tensile/yield >=1.25','standard')

# Waterproof (6 questions)
add_q('Materials Testing','Waterproof Testing','single',2,'Waterproof membrane impermeability test?',[{"label":"A","text":"0.1MPa/15min"},{"label":"B","text":"0.2MPa/30min"},{"label":"C","text":"0.3MPa/30min"},{"label":"D","text":"0.5MPa/30min"}],'C','SBS membrane: 0.3MPa for 30min','standard')
add_q('Materials Testing','Waterproof Testing','single',3,'Polyurethane coating tensile test rate?',[{"label":"A","text":"50mm/min"},{"label":"B","text":"100mm/min"},{"label":"C","text":"200mm/min"},{"label":"D","text":"500mm/min"}],'C','Polyurethane tensile rate 200mm/min','formula')
add_q('Materials Testing','Waterproof Testing','single',2,'SBS membrane heat resistance?',[{"label":"A","text":"70C"},{"label":"B","text":"80C"},{"label":"C","text":"90C"},{"label":"D","text":"100C"}],'C','SBS >=90C','formula')
add_q('Materials Testing','Waterproof Testing','multi',2,'Waterproof material test items?',[{"label":"A","text":"Tensile force"},{"label":"B","text":"Elongation"},{"label":"C","text":"Impermeability"},{"label":"D","text":"Heat resistance"}],'ABCD','Main items: tensile, elongation, impermeability, heat resistance','basic')

# Masonry (5 questions)
add_q('Materials Testing','Masonry Testing','single',1,'Standard fired brick size?',[{"label":"A","text":"240x115x53mm"},{"label":"B","text":"240x120x60mm"},{"label":"C","text":"200x100x50mm"},{"label":"D","text":"240x115x90mm"}],'A','Standard brick 240x115x53mm','basic')
add_q('Materials Testing','Masonry Testing','single',2,'MU10 brick mean compressive strength?',[{"label":"A","text":"5MPa"},{"label":"B","text":"10MPa"},{"label":"C","text":"15MPa"},{"label":"D","text":"20MPa"}],'B','MU10 >=10MPa average','formula')
add_q('Materials Testing','Masonry Testing','single',3,'Mortar consistency test instrument?',[{"label":"A","text":"Vicat"},{"label":"B","text":"Consistometer"},{"label":"C","text":"Slump cone"},{"label":"D","text":"Penetration"}],'B','Mortar consistometer (penetration depth)','practical')

# Insulation (5 questions)
add_q('Materials Testing','Insulation Testing','single',2,'EPS board thermal conductivity test?',[{"label":"A","text":"Guarded hot plate"},{"label":"B","text":"Heat flow meter"},{"label":"C","text":"Hot wire"},{"label":"D","text":"All above"}],'D','Multiple methods available','basic')
add_q('Materials Testing','Insulation Testing','single',3,'XPS board water absorption requirement?',[{"label":"A","text":"<=1.0%"},{"label":"B","text":"<=1.5%"},{"label":"C","text":"<=2.0%"},{"label":"D","text":"<=3.0%"}],'B','XPS <=1.5%','formula')
add_q('Materials Testing','Insulation Testing','truefalse',2,'Lower thermal conductivity = better insulation.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','Lower K = higher R = better insulation','basic')

# === STRUCTURE TESTING ===
add_q('Structure Testing','Concrete Strength','single',2,'Rebound hammer calibration value?',[{"label":"A","text":"78+/-2"},{"label":"B","text":"80+/-2"},{"label":"C","text":"82+/-2"},{"label":"D","text":"85+/-2"}],'B','Calibration: 80+/-2','formula')
add_q('Structure Testing','Concrete Strength','single',3,'Core sample height/diameter ratio?',[{"label":"A","text":"0.5"},{"label":"B","text":"0.8"},{"label":"C","text":"1.0"},{"label":"D","text":"1.5"}],'C','H/D ratio 1.0 for diameters 70-100mm','standard')
add_q('Structure Testing','Concrete Strength','single',2,'Carbonation depth indicator?',[{"label":"A","text":"Phenolphthalein"},{"label":"B","text":"Methyl orange"},{"label":"C","text":"Litmus"},{"label":"D","text":"Iodine"}],'A','1% phenolphthalein in alcohol','practical')
add_q('Structure Testing','Concrete Strength','single',1,'Rebound hammer principle?',[{"label":"A","text":"Ultrasonic velocity"},{"label":"B","text":"Surface hardness-strength"},{"label":"C","text":"Electromagnetic"},{"label":"D","text":"Infrared"}],'B','Based on surface hardness vs strength correlation','basic')
add_q('Structure Testing','Concrete Strength','multi',3,'Rebound test influencing factors?',[{"label":"A","text":"Carbonation"},{"label":"B","text":"Test angle"},{"label":"C","text":"Pouring face"},{"label":"D","text":"Age"}],'ABCD','Carbonation, angle, face, age all affect accuracy','important')
add_q('Structure Testing','Concrete Strength','composite',4,'Describe rebound hammer test steps and precautions.','[]','Select areas, clean surface, 16 points, measure carbonation, look up strength','Steps: select >=10 areas, clean surface, 16 rebound points, measure carbonation depth, convert to strength. Precautions: avoid honeycomb, angle correction, carbonation correction, age correction.','practical')

add_q('Structure Testing','Concrete Defects','single',3,'Ultrasonic crack depth: through-transmission method?',[{"label":"A","text":"<500mm depth"},{"label":"B","text":"Both sides accessible"},{"label":"C","text":"Crack has water"},{"label":"D","text":"Surface crack"}],'B','Through-transmission needs both sides accessible','practical')
add_q('Structure Testing','Concrete Defects','single',3,'Ultrasonic velocity in normal concrete?',[{"label":"A","text":"1000-2000m/s"},{"label":"B","text":"2000-4000m/s"},{"label":"C","text":"3000-5000m/s"},{"label":"D","text":"5000-7000m/s"}],'C','Normal concrete: 3000-5000m/s','formula')

add_q('Structure Testing','Masonry Structure','single',2,'Mortar rebound hammer impact energy?',[{"label":"A","text":"0.196J"},{"label":"B","text":"0.735J"},{"label":"C","text":"2.207J"},{"label":"D","text":"4.5J"}],'A','Mortar rebound: 0.196J (small)','formula')
add_q('Structure Testing','Masonry Structure','single',3,'Penetration method: depth vs strength?',[{"label":"A","text":"Proportional"},{"label":"B","text":"Inverse"},{"label":"C","text":"No relation"},{"label":"D","text":"Non-linear"}],'B','Deeper penetration = lower strength (inverse)','basic')

add_q('Structure Testing','Steel Weld Inspection','single',2,'MT detects what type of defects?',[{"label":"A","text":"Internal"},{"label":"B","text":"Surface/near-surface"},{"label":"C","text":"Volumetric"},{"label":"D","text":"All"}],'B','MT: ferromagnetic surface/near-surface defects','basic')
add_q('Structure Testing','Steel Weld Inspection','single',3,'UT weld inspection frequency?',[{"label":"A","text":"1MHz"},{"label":"B","text":"2.5MHz"},{"label":"C","text":"5MHz"},{"label":"D","text":"10MHz"}],'C','Weld UT: 2.5-5MHz','formula')
add_q('Structure Testing','Steel Weld Inspection','single',2,'RT film density requirement?',[{"label":"A","text":"1.0-2.0"},{"label":"B","text":"1.5-3.5"},{"label":"C","text":"2.0-4.0"},{"label":"D","text":"2.5-4.5"}],'B','Film density A: 1.5-3.5, B: 2.0-4.0','standard')
add_q('Structure Testing','Steel Weld Inspection','multi',2,'Weld NDT methods?',[{"label":"A","text":"MT"},{"label":"B","text":"UT"},{"label":"C","text":"RT"},{"label":"D","text":"PT"}],'ABCD','Four NDT methods: MT/UT/RT/PT','basic')
add_q('Structure Testing','Steel Weld Inspection','truefalse',2,'PT can be used for non-ferromagnetic materials.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','PT for non-ferromagnetic (stainless steel, aluminum)','standard')

add_q('Structure Testing','Coating Inspection','single',2,'Anti-corrosion coating thickness instrument?',[{"label":"A","text":"Ultrasonic gauge"},{"label":"B","text":"Magnetic gauge"},{"label":"C","text":"Eddy current gauge"},{"label":"D","text":"B and C"}],'D','Magnetic (steel) or eddy current (non-magnetic)','practical')

add_q('Structure Testing','Deformation Monitoring','single',2,'Settlement survey precision?',[{"label":"A","text":"+/-0.1mm"},{"label":"B","text":"+/-0.5mm"},{"label":"C","text":"+/-1.0mm"},{"label":"D","text":"+/-2.0mm"}],'B','Second order leveling +/-0.5mm','formula')
add_q('Structure Testing','Deformation Monitoring','single',3,'Plaster crack marker purpose?',[{"label":"A","text":"Decoration"},{"label":"B","text":"Monitor crack development"},{"label":"C","text":"Fill crack"},{"label":"D","text":"Reinforce"}],'B','Plaster cracking = crack developing','practical')

# === FOUNDATION TESTING ===
add_q('Foundation Testing','Static Load Test','single',2,'Static pile load test method?',[{"label":"A","text":"Quick maintained load"},{"label":"B","text":"Slow maintained load"},{"label":"C","text":"Cyclic"},{"label":"D","text":"Constant rate"}],'B','Slow maintained load is standard','standard')
add_q('Foundation Testing','Static Load Test','single',3,'Load increment per stage?',[{"label":"A","text":"1/5"},{"label":"B","text":"1/8"},{"label":"C","text":"1/10"},{"label":"D","text":"1/15"}],'C','Each stage = 1/10 estimated ultimate capacity','formula')
add_q('Foundation Testing','Static Load Test','single',3,'Test termination conditions?',[{"label":"A","text":"Rapid settlement increase"},{"label":"B","text":"Cumulative >40mm"},{"label":"C","text":"Pile failure"},{"label":"D","text":"All above"}],'D','Any termination condition met = stop loading','standard')
add_q('Foundation Testing','Static Load Test','composite',4,'Describe pile static load test: purpose, equipment, steps.','[]','Purpose: determine ultimate bearing capacity. Equipment: reaction frame + jack + dial gauges. Steps: install, staged loading, maintain stable, record, unload','Purpose: determine ultimate bearing capacity. Equipment: reaction device (anchor/stack) + jack + dial gauges. Steps: 1.Install; 2.Stage load (Q/10 each); 3.Maintain until settlement stable (<=0.1mm/h); 4.Record Q-s curve; 5.Unload for rebound.','important')

add_q('Foundation Testing','Dynamic Testing','single',2,'Low strain pile integrity principle?',[{"label":"A","text":"Stress wave reflection"},{"label":"B","text":"Ultrasonic transmission"},{"label":"C","text":"Core drilling"},{"label":"D","text":"Electromagnetic"}],'A','Stress wave reflection in pile shaft','basic')
add_q('Foundation Testing','Dynamic Testing','single',3,'Low strain sensor position?',[{"label":"A","text":"Pile center"},{"label":"B","text":"2/3 radius from center"},{"label":"C","text":"Pile edge"},{"label":"D","text":"Side of pile"}],'B','Sensor at 2/3 radius from center','practical')
add_q('Foundation Testing','Dynamic Testing','single',3,'High strain hammer weight?',[{"label":"A","text":"1% pile weight"},{"label":"B","text":"2-5% pile weight"},{"label":"C","text":"10% pile weight"},{"label":"D","text":"20% pile weight"}],'B','Hammer: 2-5% of pile weight','formula')

add_q('Foundation Testing','Pile Integrity','single',2,'Crosshole sonic: number of tubes for D<=1.5m?',[{"label":"A","text":"1"},{"label":"B","text":"2"},{"label":"C","text":"3"},{"label":"D","text":"No tubes"}],'C','D<=1.5m: 3 tubes, >1.5m: 4+ tubes','standard')
add_q('Foundation Testing','Pile Integrity','single',3,'Crosshole sonic defect indicators?',[{"label":"A","text":"Velocity decrease"},{"label":"B","text":"Amplitude decrease"},{"label":"C","text":"Waveform distortion"},{"label":"D","text":"All above"}],'D','Velocity, amplitude, waveform combined judgment','important')

add_q('Foundation Testing','Bearing Capacity','single',2,'Plate load test plate area?',[{"label":"A","text":"0.25m2"},{"label":"B","text":"0.5m2"},{"label":"C","text":"1.0m2"},{"label":"D","text":"Depends on soil"}],'D','Generally 0.25-0.5m2, soft soil 1.0m2','practical')
add_q('Foundation Testing','Bearing Capacity','single',2,'SPT N-value represents?',[{"label":"A","text":"Moisture content"},{"label":"B","text":"Soil density"},{"label":"C","text":"Plasticity"},{"label":"D","text":"Color"}],'B','N-value reflects soil density and mechanical properties','basic')
add_q('Foundation Testing','Bearing Capacity','truefalse',2,'SPT is suitable for gravel soil.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'B','SPT for sand/silt, dynamic probing for gravel','standard')

add_q('Foundation Testing','Pit Monitoring','single',2,'Deep lateral displacement monitoring?',[{"label":"A","text":"Level"},{"label":"B","text":"Inclinometer"},{"label":"C","text":"Total station"},{"label":"D","text":"Theodolite"}],'B','Inclinometer in guide tube','practical')
add_q('Foundation Testing','Pit Monitoring','single',3,'Warning value percentage of control value?',[{"label":"A","text":"50%"},{"label":"B","text":"60%"},{"label":"C","text":"70%"},{"label":"D","text":"80%"}],'D','Warning: 70-80% of control value','formula')

add_q('Foundation Testing','Composite Foundation','single',3,'Composite foundation bearing capacity test?',[{"label":"A","text":"Plate load test"},{"label":"B","text":"Dynamic probing"},{"label":"C","text":"SPT"},{"label":"D","text":"Vane shear"}],'A','Plate load test for composite foundation','standard')

# === ENERGY TESTING ===
add_q('Energy Testing','Wall Thermal','single',2,'Heat flow method monitoring duration?',[{"label":"A","text":"24h"},{"label":"B","text":"48h"},{"label":"C","text":"72h"},{"label":"D","text":"96h"}],'C','Steady-state: >=72 hours monitoring','formula')
add_q('Energy Testing','Wall Thermal','single',2,'Heat transfer coefficient K unit?',[{"label":"A","text":"W/(m*K)"},{"label":"B","text":"W/(m2*K)"},{"label":"C","text":"J/(kg*K)"},{"label":"D","text":"m2*K/W"}],'B','K value unit: W/(m2*K)','formula')
add_q('Energy Testing','Wall Thermal','single',3,'Infrared thermography principle?',[{"label":"A","text":"Temperature difference"},{"label":"B","text":"Humidity"},{"label":"C","text":"Stress"},{"label":"D","text":"Crack"}],'A','Defects (hollow, leakage) show temperature difference','basic')
add_q('Energy Testing','Wall Thermal','truefalse',2,'Lower heat transfer coefficient = better insulation.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','Lower K = higher R = better insulation','basic')

add_q('Energy Testing','Window Properties','single',2,'Window airtightness highest grade?',[{"label":"A","text":"6"},{"label":"B","text":"8"},{"label":"C","text":"10"},{"label":"D","text":"12"}],'B','Grade 8 is highest (GB/T 7106)','standard')
add_q('Energy Testing','Window Properties','single',3,'Water resistance test pressure mode?',[{"label":"A","text":"Stable"},{"label":"B","text":"Fluctuating"},{"label":"C","text":"Stable then fluctuating"},{"label":"D","text":"Per design"}],'D','Stable or fluctuating per design requirements','practical')
add_q('Energy Testing','Window Properties','multi',2,'Window three-property test?',[{"label":"A","text":"Airtightness"},{"label":"B","text":"Water resistance"},{"label":"C","text":"Wind pressure"},{"label":"D","text":"Sound insulation"}],'ABC','Three properties: airtightness, water resistance, wind pressure','basic')

add_q('Energy Testing','External Insulation','single',3,'External insulation weatherability cycles?',[{"label":"A","text":"5"},{"label":"B","text":"10"},{"label":"C","text":"20"},{"label":"D","text":"80"}],'D','80 high-temp water spray + 20 heat-freeze cycles','formula')
add_q('Energy Testing','External Insulation','single',3,'Field bond strength pull-off requirement?',[{"label":"A","text":">=0.1MPa"},{"label":"B","text":">=0.3MPa"},{"label":"C","text":">=0.5MPa"},{"label":"D","text":">=1.0MPa"}],'B','Field pull-off >=0.3MPa','formula')

add_q('Energy Testing','Energy Assessment','single',2,'Building energy efficiency grades?',[{"label":"A","text":"3 grades"},{"label":"B","text":"4 grades"},{"label":"C","text":"5 grades"},{"label":"D","text":"6 grades"}],'C','Grades 1-5 (1 = most efficient)','basic')
add_q('Energy Testing','Heating System','single',3,'Indoor temperature measurement height?',[{"label":"A","text":"0.5m"},{"label":"B","text":"0.8m"},{"label":"C","text":"1.0m"},{"label":"D","text":"1.5m"}],'C','1.0m above floor, >=0.5m from wall','practical')

# === INDOOR ENVIRONMENT ===
add_q('Indoor Environment','Formaldehyde','single',2,'GB50325 Type I formaldehyde limit?',[{"label":"A","text":"0.05"},{"label":"B","text":"0.07"},{"label":"C","text":"0.08"},{"label":"D","text":"0.10"}],'C','Type I <=0.08mg/m3, Type II <=0.10mg/m3','standard')
add_q('Indoor Environment','Formaldehyde','single',2,'Phenolic reagent method sampling flow?',[{"label":"A","text":"0.2L/min"},{"label":"B","text":"0.5L/min"},{"label":"C","text":"1.0L/min"},{"label":"D","text":"2.0L/min"}],'B','Sampling flow 0.5L/min','formula')
add_q('Indoor Environment','Formaldehyde','single',3,'Door/window closing time before sampling?',[{"label":"A","text":"1h"},{"label":"B","text":"6h"},{"label":"C","text":"12h"},{"label":"D","text":"24h"}],'C','GB50325: close doors/windows 12h before sampling','standard')
add_q('Indoor Environment','Formaldehyde','multi',2,'Formaldehyde detection methods?',[{"label":"A","text":"AHMT"},{"label":"B","text":"Phenolic reagent"},{"label":"C","text":"GC"},{"label":"D","text":"Acetylacetone"}],'ABCD','Four common methods','basic')
add_q('Indoor Environment','Formaldehyde','truefalse',1,'GB50325 applies to all civil buildings.',[{"label":"A","text":"True"},{"label":"B","text":"False"}],'A','GB50325 for new/expanded/renovated civil buildings','standard')

add_q('Indoor Environment','Benzene Series','single',2,'GB50325 Type I benzene limit?',[{"label":"A","text":"0.05"},{"label":"B","text":"0.06"},{"label":"C","text":"0.09"},{"label":"D","text":"0.11"}],'C','Type I benzene <=0.09mg/m3','formula')
add_q('Indoor Environment','Benzene Series','single',3,'Benzene sampling adsorption tube?',[{"label":"A","text":"Activated carbon"},{"label":"B","text":"Tenax"},{"label":"C","text":"Silica gel"},{"label":"D","text":"Molecular sieve"}],'A','Activated carbon tube, CS2 desorption','practical')

add_q('Indoor Environment','TVOC Detection','single',2,'GB50325 Type I TVOC limit?',[{"label":"A","text":"0.2"},{"label":"B","text":"0.45"},{"label":"C","text":"0.5"},{"label":"D","text":"0.6"}],'B','Type I TVOC <=0.45mg/m3','formula')
add_q('Indoor Environment','TVOC Detection','single',3,'TVOC standard detection method?',[{"label":"A","text":"GC"},{"label":"B","text":"LC"},{"label":"C","text":"Spectroscopy"},{"label":"D","text":"Gravimetric"}],'A','Tenax adsorption/thermal desorption-GC','basic')

add_q('Indoor Environment','Radon Detection','single',2,'Indoor radon limit (Type I)?',[{"label":"A","text":"100Bq/m3"},{"label":"B","text":"150Bq/m3"},{"label":"C","text":"200Bq/m3"},{"label":"D","text":"400Bq/m3"}],'C','Type I <=200Bq/m3','formula')
add_q('Indoor Environment','Radon Detection','single',3,'Continuous radon monitor sampling time?',[{"label":"A","text":"1h"},{"label":"B","text":"6h"},{"label":"C","text":"12h"},{"label":"D","text":"24h"}],'D','Continuous measurement >=24h','formula')

add_q('Indoor Environment','Ammonia Detection','single',2,'GB50325 Type I ammonia limit?',[{"label":"A","text":"0.1"},{"label":"B","text":"0.15"},{"label":"C","text":"0.2"},{"label":"D","text":"0.5"}],'C','Type I ammonia <=0.2mg/m3','formula')
add_q('Indoor Environment','Ammonia Detection','single',3,'Indophenol blue method principle?',[{"label":"A","text":"Colorimetric"},{"label":"B","text":"Titration"},{"label":"C","text":"Gravimetric"},{"label":"D","text":"Electrochemical"}],'A','NH3 + hypochlorite + phenol -> indophenol blue -> colorimetric','practical')

add_q('Indoor Environment','Sampling Standards','single',2,'Sampling point layout principle?',[{"label":"A","text":"Diagonal"},{"label":"B","text":"Plum blossom"},{"label":"C","text":"Area<=50m2: 1-3 points"},{"label":"D","text":"Uniform"}],'C','<=50m2: 1-3 points, 50-100m2: 3-5 points','standard')
add_q('Indoor Environment','Sampling Standards','single',3,'Sampling temperature requirement?',[{"label":"A","text":"15-25C"},{"label":"B","text":"18-28C"},{"label":"C","text":"20-30C"},{"label":"D","text":"No requirement"}],'B','GB50325: 18-28C during sampling','standard')
add_q('Indoor Environment','Sampling Standards','multi',3,'GB50325 indoor pollutants?',[{"label":"A","text":"HCHO"},{"label":"B","text":"Benzene"},{"label":"C","text":"TVOC"},{"label":"D","text":"Radon"},{"label":"E","text":"NH3"}],'ABCDE','5 pollutants: HCHO, Benzene, TVOC, Radon, NH3','high')

# Fill-blank questions - Materials Testing
add_q('Materials Testing','Cement Testing','blank',3,
    'The main harmful components in cement that cause unsoundness are ______ and ______.',
    '[]',
    'Free CaO|Free MgO',
    'Free calcium oxide (CaO) and free magnesium oxide (MgO) cause cement unsoundness, leading to expansion and cracking.',
    'practical')

add_q('Materials Testing','Cement Testing','blank',2,
    'Cement initial setting time should not be earlier than ______ minutes, and final setting time should not be later than ______ minutes.',
    '[]',
    '45|390|6.5h',
    'According to GB175 standard, initial setting >= 45min, final setting <= 390min (6.5h) for ordinary Portland cement.',
    'knowledge')

add_q('Materials Testing','Concrete Testing','blank',3,
    'The water-cement ratio (W/C) is the ratio of ______ weight to ______ weight in concrete mix.',
    '[]',
    'Water|Cement',
    'Water-cement ratio = water weight / cement weight. Lower W/C means higher strength but lower workability.',
    'knowledge')

add_q('Materials Testing','Concrete Testing','blank',4,
    'Concrete strength grade C30 means the standard cube compressive strength at 28 days is ______ MPa.',
    '[]',
    '30',
    'C30 means the characteristic compressive strength (fcu,k) is 30 MPa at 28 days curing.',
    'knowledge')

add_q('Structure Testing','Rebound Test','blank',3,
    'The rebound hammer test measures concrete ______ strength by correlating rebound number with compressive strength.',
    '[]',
    'Surface|Surface hardness',
    'Rebound hammer measures surface hardness, which correlates with compressive strength. Need to correct for carbonation depth.',
    'practical')

add_q('Structure Testing','Rebound Test','blank',2,
    'When using rebound hammer, at least ______ rebound points should be measured on each test area.',
    '[]',
    '16',
    'Each test area needs 16 rebound points. Remove 3 highest and 3 lowest, average the remaining 10 values.',
    'knowledge')

add_q('Foundation Testing','Pile Testing','blank',4,
    'In pile static load test, the settlement stabilization criterion is that settlement rate should not exceed ______ mm/h.',
    '[]',
    '0.1',
    'During static load test, maintain each load stage until settlement stabilizes at <=0.1mm/h before recording and proceeding.',
    'practical')

add_q('Foundation Testing','Pile Testing','blank',3,
    'Pile dynamic testing methods include ______ method and ______ method.',
    '[]',
    'Low strain|High strain|Low strain method|High strain method',
    'Low strain (PIT) for integrity checking, High strain (PDA) for bearing capacity evaluation.',
    'knowledge')


conn.commit()
qcount = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
print(f"Questions: {qcount}")

# === EXAMS ===
conn.execute("DELETE FROM exams")
all_qids = [r[0] for r in conn.execute('SELECT id FROM questions WHERE is_active=1').fetchall()]
exam_defs = [
    ('Materials Mock 1','mock',60,100,60,20),('Materials Mock 2','mock',60,100,60,20),
    ('Structure Mock','mock',90,100,60,20),('Foundation Mock','mock',45,100,60,15),
    ('Energy Mock','mock',60,100,60,15),('Indoor Env Mock','mock',60,100,60,15),
    ('Comprehensive Mock','mock',120,100,60,30),
    ('Materials Formal','formal',90,100,60,20),('Structure Formal','formal',90,100,60,20),
    ('Foundation Formal','formal',60,100,60,15),('Energy Formal','formal',60,100,60,15),
    ('Indoor Env Formal','formal',60,100,60,15),
]
for title, mode, dur, total, ps, count in exam_defs:
    sel = json.dumps(random.sample(all_qids, min(count, len(all_qids))))
    conn.execute("INSERT INTO exams (title,description,mode,duration_minutes,total_score,pass_score,question_ids,is_published,shuffle_questions,shuffle_options,max_tab_switches) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (title, f'{title} - construction inspection', mode, dur, total, ps, sel, 1, 1, 1, 3))
conn.commit()
print(f"Exams: {conn.execute('SELECT COUNT(*) FROM exams').fetchone()[0]}")

# === EXAM RESULTS ===
conn.execute("DELETE FROM exam_results")
students = [(r[0],r[1]) for r in conn.execute("SELECT id,fullname FROM users WHERE role IN ('student','inspector')").fetchall()]
exams = [(r[0],r[1],r[2]) for r in conn.execute('SELECT id,total_score,pass_score FROM exams').fetchall()]
for uid, uname in students:
    for eid, total, ps in random.sample(exams, min(4, len(exams))):
        score = round(random.uniform(ps*0.3, total*0.98), 1)
        passed = 1 if score >= ps else 0
        conn.execute("INSERT INTO exam_results (exam_id,user_id,answers,auto_score,total_score,passed,tab_switches,is_cheating) VALUES (?,?,?,?,?,?,?,?)",
            (eid, uid, '{}', score, total, passed, random.randint(0,2), 0))
conn.commit()
print(f"Exam results: {conn.execute('SELECT COUNT(*) FROM exam_results').fetchone()[0]}")

# === PRACTICE RECORDS ===
conn.execute("DELETE FROM practice_records")
sids = [r[0] for r in conn.execute('SELECT id FROM subjects').fetchall()]
for uid, _ in students:
    for _ in range(random.randint(3,6)):
        total = random.randint(10,30)
        correct = random.randint(int(total*0.3), total)
        conn.execute("INSERT INTO practice_records (user_id,mode,subject_id,total_count,correct_count,wrong_count,duration_seconds) VALUES (?,?,?,?,?,?,?)",
            (uid, random.choice(['random','chapter','memorize']), random.choice(sids), total, correct, total-correct, random.randint(120,3600)))
conn.commit()
print(f"Practice records: {conn.execute('SELECT COUNT(*) FROM practice_records').fetchone()[0]}")

# === WRONG ANSWERS ===
conn.execute("DELETE FROM wrong_answers")
for uid, _ in students:
    for qid in random.sample(all_qids, min(10, len(all_qids))):
        conn.execute("INSERT INTO wrong_answers (user_id,question_id,is_mastered) VALUES (?,?,0)", (uid, qid))
conn.commit()
print(f"Wrong answers: {conn.execute('SELECT COUNT(*) FROM wrong_answers').fetchone()[0]}")

# === FAVORITES ===
conn.execute("DELETE FROM favorites")
for uid, _ in students:
    for qid in random.sample(all_qids, min(8, len(all_qids))):
        conn.execute("INSERT INTO favorites (user_id,question_id) VALUES (?,?)", (uid, qid))
conn.commit()
print(f"Favorites: {conn.execute('SELECT COUNT(*) FROM favorites').fetchone()[0]}")

# === NOTES ===
conn.execute("DELETE FROM notes")
notes = ['Cement soundness: Le Chatelier method, expansion <=5mm',
         'Rebound: 16 points, carbonation with phenolphthalein',
         'Pile static load: slow method, Q/10 per stage',
         'GB50325 Type I: HCHO 0.08, Benzene 0.09, TVOC 0.45, Radon 200, NH3 0.2',
         'Waterproof membrane: 0.3MPa/30min impermeability',
         'HRB400: yield 400MPa, tensile 540MPa',
         'Concrete curing: 20+/-2C, >=95%RH',
         'Crosshole sonic: D<=1.5m 3 tubes, >1.5m 4 tubes',
         'Window airtightness: grade 8 highest',
         'Wall insulation: K unit W/(m2*K)',
]
for uid, _ in students[:4]:
    for note in random.sample(notes, min(3, len(notes))):
        conn.execute("INSERT INTO notes (user_id,question_id,content) VALUES (?,?,?)", (uid, random.choice(all_qids), note))
conn.commit()
print(f"Notes: {conn.execute('SELECT COUNT(*) FROM notes').fetchone()[0]}")

# === ANNOUNCEMENTS ===
conn.execute("DELETE FROM announcements")
for title, content, pinned, pub in [
    ('System Launch','Welcome to the construction inspection exam system! 200+ professional questions across 5 testing areas.',1,1),
    ('June Exam Schedule','Mock exams open now. Formal exams June 25-30.',1,1),
    ('New Question Bank','Indoor Environment and Energy Testing questions now available.',1,1),
    ('Certificate Guide','Practice pass rate >=60% for practice certs. Formal exam >=60 for exam certs.',0,1),
    ('Maintenance Notice','System maintenance June 20, 2:00-4:00 AM.',0,1),
]:
    conn.execute("INSERT INTO announcements (title,content,is_pinned,is_published,created_by) VALUES (?,?,?,?,?)", (title,content,pinned,pub,'System Admin'))
conn.commit()
print(f"Announcements: {conn.execute('SELECT COUNT(*) FROM announcements').fetchone()[0]}")

# === CERTIFICATES ===
conn.execute("DELETE FROM user_certificates")
conn.execute("DELETE FROM certificates")
for name, ctype, desc, chid in [
    ('Materials Practice Cert','practice','Materials Testing practice pass',1),
    ('Structure Practice Cert','practice','Structure Testing practice pass',2),
    ('Foundation Practice Cert','practice','Foundation Testing practice pass',3),
    ('Energy Practice Cert','practice','Energy Testing practice pass',4),
    ('Indoor Env Practice Cert','practice','Indoor Environment practice pass',5),
    ('Materials Exam Cert','exam','Materials Testing formal exam pass',None),
    ('Structure Exam Cert','exam','Structure Testing formal exam pass',None),
    ('Comprehensive Cert','exam','Multi-exam comprehensive certification',None),
]:
    conn.execute("INSERT INTO certificates (name,cert_type,description,chapter_id,template_image,issue_rule) VALUES (?,?,?,?,?,?)", (name,ctype,desc,chid,'','{}'))
conn.commit()
cert_ids = [r[0] for r in conn.execute('SELECT id FROM certificates').fetchall()]
for cid in random.sample(cert_ids, min(4, len(cert_ids))):
    for uid, _ in random.sample(students, min(3, len(students))):
        conn.execute("INSERT INTO user_certificates (certificate_id,user_id,certificate_no,is_revoked) VALUES (?,?,?,0)",
            (cid, uid, 'CERT-'+uuid.uuid4().hex[:12].upper()))
conn.commit()
print(f"Certificates: {conn.execute('SELECT COUNT(*) FROM certificates').fetchone()[0]}")
print(f"Issued: {conn.execute('SELECT COUNT(*) FROM user_certificates').fetchone()[0]}")

# === NOTIFICATIONS ===
conn.execute("DELETE FROM notifications")
for uid, _ in students:
    for title, content, ntype in random.sample([
        ('Exam Reminder','June formal exam starts June 25.','info'),
        ('Certificate Issued','Congratulations! Your exam certificate has been issued.','success'),
        ('Practice Reminder','You haven\'t practiced for 3 days. Keep studying!','warning'),
        ('New Questions','Indoor Environment questions updated with 30 new items.','info'),
        ('Scores Published','Structure Testing mock exam results are ready.','info'),
    ], 3):
        conn.execute("INSERT INTO notifications (user_id,type,title,content,is_read) VALUES (?,?,?,?,?)",
            (uid, ntype, title, content, random.randint(0,1)))
conn.commit()
print(f"Notifications: {conn.execute('SELECT COUNT(*) FROM notifications').fetchone()[0]}")

# === ABNORMAL REPORTS ===
conn.execute("DELETE FROM abnormal_reports")
er_ids = [r[0] for r in conn.execute('SELECT id FROM exam_results LIMIT 3').fetchall()]
for i, (reason, detail) in enumerate([('tab_switch','Tab switch 3x during formal exam'),('tab_switch','Tab switch 1x'),('right_click','Attempted right-click copy'),('paste','Attempted paste external content')]):
    if er_ids:
        conn.execute("INSERT INTO abnormal_reports (exam_result_id,user_id,reason,detail,is_judged) VALUES (?,?,?,?,0)",
            (er_ids[i%len(er_ids)], students[i%len(students)][0], reason, detail))
conn.commit()
print(f"Abnormal: {conn.execute('SELECT COUNT(*) FROM abnormal_reports').fetchone()[0]}")

# === RETAKE APPLICATIONS ===
conn.execute("DELETE FROM retake_applications")
if er_ids:
    conn.execute("INSERT INTO retake_applications (exam_id,user_id,reason,status) VALUES (?,?,?,?)", (1, students[0][0], 'Network disconnection during exam', 'pending'))
    conn.execute("INSERT INTO retake_applications (exam_id,user_id,reason,status) VALUES (?,?,?,?)", (2, students[1][0], 'Health issue during exam', 'pending'))
conn.commit()
print(f"Retake apps: {conn.execute('SELECT COUNT(*) FROM retake_applications').fetchone()[0]}")

# === AUDIT LOGS ===
conn.execute("DELETE FROM audit_logs")
for uid, action, detail in [(1,'Create Subjects','Created 5 construction testing subjects'),(1,'Import Questions','Batch imported 100+ professional questions'),(1,'Create Exams','Generated 12 exam papers'),(1,'Publish Announcement','Published system launch announcement'),(1,'Issue Certificates','Issued 4 certificates to users')]:
    conn.execute("INSERT INTO audit_logs (user_id,action,detail) VALUES (?,?,?)", (uid, action, detail))
conn.commit()
print(f"Audit logs: {conn.execute('SELECT COUNT(*) FROM audit_logs').fetchone()[0]}")

# === RESOURCES ===
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
if 'resources' in tables:
    conn.execute("DELETE FROM resources")
    for title, ftype, sid, desc in [
        ('GB 175-2007 Portland Cement Standard','pdf',1,'National standard for cement'),
        ('GB/T 50081-2019 Concrete Test Methods','pdf',2,'Concrete mechanical test standard'),
        ('JGJ/T 23-2011 Rebound Hammer Test','pdf',2,'Rebound method standard'),
        ('GB 50325-2020 Indoor Environment Control','pdf',5,'Civil building indoor pollution standard'),
        ('JGJ 106-2014 Pile Testing Standard','pdf',3,'Foundation pile testing standard'),
        ('Energy Testing Manual','pdf',4,'Building energy efficiency testing guide'),
        ('Indoor Environment Testing Guide','pdf',5,'Practical testing operations guide'),
        ('Materials Testing Problem Set','pdf',1,'Practice questions collection'),
    ]:
        conn.execute("INSERT INTO resources (title,file_type,subject_id,description) VALUES (?,?,?,?)", (title,ftype,sid,desc))
    conn.commit()
    print(f"Resources: {conn.execute('SELECT COUNT(*) FROM resources').fetchone()[0]}")

# === FINAL ===
print("\n=== SEED COMPLETE ===")
for table, label in [
    ('users','Users'),('subjects','Subjects'),('chapters','Chapters'),('questions','Questions'),
    ('exams','Exams'),('exam_results','Exam Results'),('practice_records','Practice Records'),
    ('wrong_answers','Wrong Answers'),('favorites','Favorites'),('notes','Notes'),
    ('announcements','Announcements'),('certificates','Certificates'),('user_certificates','Issued Certs'),
    ('notifications','Notifications'),('abnormal_reports','Abnormal'),('retake_applications','Retake Apps'),
    ('audit_logs','Audit Logs'),
]:
    try:
        print(f"  {label}: {conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}")
    except:
        pass
conn.close()
