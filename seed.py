"""初始化数据库并填充海量演示数据 — 模拟真实大医院运行数据"""
import random
from datetime import datetime, date, timedelta
from models import (
    db, Department, User, Schedule, Appointment, Consultation,
    ConsultationMessage, Prescription, Medicine, Announcement,
    HealthArticle, DoctorReview, Bill, BillItem, PatientProfile, Notification
)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

def init_data():
    print("=" * 50)
    print("医联通 SmartMed — 初始化大规模演示数据")
    print("=" * 50)

    # ─── 1. 科室 (20个) ───
    dept_data = [
        ('内科', '诊治内科常见病、多发病及疑难杂症', 'activity'),
        ('外科', '开展各类外科手术及微创治疗', 'scalpel'),
        ('儿科', '0-14岁儿童疾病诊疗与健康管理', 'baby'),
        ('妇产科', '妇科疾病、孕产期保健与分娩', 'heart'),
        ('骨科', '骨折创伤、关节疾病与脊柱外科', 'bone'),
        ('皮肤科', '皮肤病、性病与医学美容', 'sun'),
        ('眼科', '眼病诊疗、视力矫正与白内障手术', 'eye'),
        ('口腔科', '牙体牙髓、修复正畸与种植', 'smile'),
        ('中医科', '中药调理、针灸推拿与康复理疗', 'leaf'),
        ('心理科', '心理咨询、心理治疗与危机干预', 'brain'),
        ('神经内科', '脑血管病、癫痫、帕金森与头痛', 'zap'),
        ('心血管内科', '冠心病、高血压、心律失常与心衰', 'heart'),
        ('消化内科', '胃肠肝胆胰疾病与内镜诊疗', 'coffee'),
        ('呼吸内科', '哮喘、慢阻肺、肺部感染与肺癌', 'wind'),
        ('内分泌科', '糖尿病、甲状腺疾病与代谢综合征', 'droplet'),
        ('肾内科', '肾炎、肾病综合征与肾功能衰竭', 'filter'),
        ('肿瘤科', '恶性肿瘤化疗、靶向与免疫治疗', 'shield'),
        ('康复医学科', '术后康复、运动损伤与物理治疗', 'trending-up'),
        ('急诊科', '急危重症抢救与24小时急诊服务', 'alert-circle'),
        ('老年病科', '老年综合评估与多病共存管理', 'users'),
    ]
    for name, desc, icon in dept_data:
        db.session.add(Department(name=name, description=desc, icon=icon))
    db.session.commit()
    departments = Department.query.all()
    dept_id_map = {d.name: d.id for d in departments}
    print(f"  [1/10] {len(dept_data)} 个科室")

    # ─── 2. 管理员 ───
    admin = User(name='系统管理员', phone='admin', role='admin', gender='男', age=35)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("  [2/10] 管理员账号")

    # ─── 3. 医生 (106位知名医生，带详细简历) ───
    from doctor_data import ALL_DOCTORS
    doctors = []
    for dd in ALL_DOCTORS:
        dept = Department.query.filter_by(name=dd['dept']).first()
        if not dept:
            dept = Department.query.first()
        phone = f"139{random.randint(10000000,99999999)}"
        d = User(
            name=dd['name'], phone=phone, role='doctor',
            department_id=dept.id, title=dd.get('title','主任医师'),
            specialty=dd.get('specialty',''),
            bio=dd.get('bio',''),
            education=dd.get('education',''),
            training=dd.get('training',''),
            research=dd.get('research',''),
            mentorship=dd.get('mentorship',''),
            awards=dd.get('awards',''),
            hospital=dd.get('hospital',''),
            avatar="",  # 用CSS渐变+首字母，国内无障碍
            gender=random.choice(['男','女']),
            age=random.randint(40,68),
            consultation_fee=dd.get('fee',25)
        )
        d.set_password('123456')
        db.session.add(d)
        doctors.append(d)
    db.session.commit()
    print(f"  [3/10] {len(doctors)} 位知名医生(含详细简历)")

    # ─── 4. 患者 (80人) ───
    surnames = '赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹柏水窦章苏'
    given_m = ['明', '强', '伟', '勇', '军', '涛', '斌', '文', '辉', '浩', '宇', '峰', '刚', '杰', '磊']
    given_f = ['芳', '丽', '娟', '敏', '静', '娜', '婷', '萍', '红', '玲', '霞', '艳', '秀英', '雪', '慧']
    patient_data = []
    for i in range(80):
        gender = random.choice(['男', '女'])
        surname = random.choice(surnames)
        given = random.choice(given_m if gender == '男' else given_f)
        name = surname + given + (random.choice(given_m + given_f) if random.random() < 0.3 else '')
        age = random.choices(
            [random.randint(3, 14), random.randint(20, 35), random.randint(36, 55), random.randint(60, 82)],
            weights=[1, 3, 3, 2], k=1
        )[0]
        days_ago = random.randint(0, 90)
        phone = f'150{random.randint(10000000, 99999999)}'
        patient_data.append((name, phone, gender, age, days_ago))
    # 保留5个测试账号
    for name, phone, gender, age in [
        ('李明', '13800000001', '男', 28),
        ('王芳', '13900000001', '女', 35),
        ('赵小龙', '13900000002', '男', 12),
        ('陈晨', '13900000003', '女', 45),
        ('刘洋', '13900000004', '男', 52)
    ]:
        if not any(p[1] == phone for p in patient_data):
            patient_data.append((name, phone, gender, age, random.randint(0, 90)))
    patients = []
    for name, phone, gender, age, days_ago in patient_data:
        p = User(name=name, phone=phone, role='patient', gender=gender, age=age,
                 created_at=datetime.utcnow() - timedelta(days=days_ago))
        p.set_password('123456')
        db.session.add(p)
        patients.append(p)
    db.session.commit()
    print(f"  [4/10] {len(patients)} 位患者 ({sum(1 for p in patients if p.gender=='男')}男/{sum(1 for p in patients if p.gender=='女')}女)")

    # ─── 5. 患者健康档案 ───
    blood_types = ['A', 'B', 'AB', 'O']
    allergy_pool = ['青霉素', '头孢', '海鲜', '花粉', '尘螨', '鸡蛋', '牛奶', '花生', '酒精', '碘伏']
    chronic_pool = ['高血压', '糖尿病', '冠心病', '哮喘', '慢性胃炎', '颈椎病', '高脂血症', '痛风', '甲减', '过敏性鼻炎']
    for pt in random.sample(patients, min(55, len(patients))):
        bt = random.choice(blood_types)
        allergies = ','.join(random.sample(allergy_pool, random.randint(0, 3)))
        chronics = ','.join(random.sample(chronic_pool, random.randint(0, 3)))
        profile = PatientProfile(
            patient_id=pt.id, blood_type=bt, allergies=allergies,
            chronic_diseases=chronics,
            family_history=random.choice(['无特殊', '父亲高血压', '母亲糖尿病', '祖父肺癌', '']),
            smoking=random.choice(['never', 'never', 'never', 'former', 'current']),
            alcohol=random.choice(['never', 'never', 'occasional', 'regular']),
            height=round(random.uniform(150, 185), 1),
            weight=round(random.uniform(45, 95), 1)
        )
        db.session.add(profile)
    db.session.commit()
    print(f"  [5/10] 55 份患者健康档案 (含过敏史/慢性病/家族史)")

    # ─── 6. 排班数据 ───
    for doc in doctors:
        for day in range(0, 5):
            db.session.add(Schedule(doctor_id=doc.id, day_of_week=day,
                           start_time='08:00', end_time='12:00', max_patients=15))
            db.session.add(Schedule(doctor_id=doc.id, day_of_week=day,
                           start_time='14:00', end_time='17:30', max_patients=15))
    db.session.commit()
    print(f"  [6/10] {len(doctors) * 5 * 2} 条排班记录")

    # ─── 7. 药品 (60种) ───
    medicine_data = [
        # 抗生素
        ('阿莫西林胶囊', '0.5g×24粒', '华北制药', 18.50, 15, '西药'),
        ('头孢克洛缓释片', '0.375g×12片', '广州白云山', 42.80, 8, '西药'),
        ('阿奇霉素分散片', '0.25g×12片', '辉瑞制药', 58.00, 5, '西药'),
        ('左氧氟沙星片', '0.5g×7片', '第一三共', 35.60, 3, '西药'),
        ('罗红霉素胶囊', '150mg×12粒', '石药集团', 22.00, 20, '西药'),
        # 心脑血管
        ('硝苯地平控释片', '30mg×7片', '拜耳医药', 45.00, 25, '西药'),
        ('阿托伐他汀钙片', '20mg×7片', '辉瑞制药', 68.50, 30, '西药'),
        ('氯沙坦钾片', '50mg×7片', '默沙东', 52.00, 18, '西药'),
        ('阿司匹林肠溶片', '100mg×30片', '拜耳医药', 15.80, 40, '西药'),
        ('美托洛尔缓释片', '47.5mg×7片', '阿斯利康', 32.00, 22, '西药'),
        ('单硝酸异山梨酯片', '20mg×48片', '鲁南贝特', 48.00, 12, '西药'),
        ('瑞舒伐他汀钙片', '10mg×7片', '浙江海正', 56.00, 28, '西药'),
        # 消化系统
        ('奥美拉唑肠溶胶囊', '20mg×14粒', '阿斯利康', 38.00, 35, '西药'),
        ('多潘立酮片', '10mg×30片', '西安杨森', 16.50, 50, '西药'),
        ('铝碳酸镁咀嚼片', '0.5g×20片', '拜耳医药', 25.00, 40, '西药'),
        ('蒙脱石散', '3g×10袋', '法国博福', 22.80, 55, '西药'),
        ('双歧杆菌三联活菌胶囊', '210mg×24粒', '上海信谊', 35.00, 20, '西药'),
        # 呼吸系统
        ('布地奈德福莫特罗吸入剂', '160μg/4.5μg×60吸', '阿斯利康', 228.00, 8, '西药'),
        ('盐酸氨溴索口服液', '30mg/5ml×10支', '勃林格', 32.00, 30, '西药'),
        ('沙美特罗替卡松吸入剂', '50μg/250μg×60吸', '葛兰素史克', 195.00, 6, '西药'),
        ('复方甘草片', '100片/瓶', '国药集团', 8.50, 60, '西药'),
        # 内分泌
        ('盐酸二甲双胍片', '0.5g×20片', '中美上海施贵宝', 12.00, 50, '西药'),
        ('格列美脲片', '2mg×15片', '赛诺菲', 28.00, 25, '西药'),
        ('胰岛素注射液', '10ml:400IU', '诺和诺德', 65.00, 15, '西药'),
        ('阿卡波糖片', '50mg×30片', '拜耳医药', 52.00, 20, '西药'),
        ('左甲状腺素钠片', '50μg×100片', '默克', 32.50, 18, '西药'),
        # 镇痛/抗炎
        ('布洛芬缓释胶囊', '0.3g×20粒', '中美史克', 22.80, 45, '西药'),
        ('塞来昔布胶囊', '200mg×6粒', '辉瑞制药', 38.00, 12, '西药'),
        ('对乙酰氨基酚片', '0.5g×20片', '强生', 9.80, 80, '西药'),
        ('双氯芬酸钠缓释片', '75mg×10片', '诺华', 25.00, 22, '西药'),
        # 皮肤/外用
        ('莫匹罗星软膏', '5g', '中美史克', 28.50, 35, '西药'),
        ('糠酸莫米松乳膏', '10g', '拜耳医药', 32.00, 20, '西药'),
        ('硝酸咪康唑乳膏', '20g', '西安杨森', 18.00, 25, '西药'),
        ('红霉素软膏', '10g', '广州白云山', 5.80, 100, '西药'),
        # 中成药
        ('连花清瘟胶囊', '0.35g×36粒', '以岭药业', 14.80, 40, '中成药'),
        ('蒲地蓝消炎口服液', '10ml×10支', '济川药业', 35.60, 30, '中成药'),
        ('板蓝根颗粒', '10g×20袋', '白云山制药', 16.00, 60, '中成药'),
        ('云南白药气雾剂', '50ml+30ml', '云南白药集团', 45.00, 20, '中成药'),
        ('复方丹参滴丸', '27mg×180丸', '天士力', 28.00, 35, '中成药'),
        ('丹参片', '0.3g×100片', '上海雷允上', 22.00, 40, '中成药'),
        ('六味地黄丸', '360丸/瓶', '同仁堂', 38.00, 25, '中成药'),
        ('藿香正气水', '10ml×10支', '太极集团', 12.00, 55, '中成药'),
        ('牛黄解毒片', '0.3g×24片', '北京同仁堂', 9.80, 50, '中成药'),
        ('通心络胶囊', '0.26g×30粒', '以岭药业', 42.00, 15, '中成药'),
        ('益母草颗粒', '15g×10袋', '广州白云山', 18.50, 35, '中成药'),
        # 保健品/营养
        ('维生素C片', '0.1g×100片', '东北制药', 5.80, 120, '保健品'),
        ('维生素D滴剂', '400IU×30粒', '青岛双鲸', 38.00, 40, '保健品'),
        ('碳酸钙D3片', '600mg×30片', '惠氏', 48.00, 30, '保健品'),
        ('复合维生素B片', '100片/瓶', '上海信谊', 8.50, 80, '保健品'),
        ('葡萄糖酸锌口服液', '10ml×10支', '哈药六厂', 28.00, 25, '保健品'),
        # 儿科用药
        ('小儿氨酚黄那敏颗粒', '2g×10袋', '华润三九', 12.50, 45, '西药'),
        ('小儿消积止咳口服液', '10ml×10支', '鲁南制药', 32.00, 20, '中成药'),
        ('布洛芬混悬液', '100mg/5ml×100ml', '强生', 28.00, 35, '西药'),
        ('小儿肺热咳喘口服液', '10ml×10支', '葵花药业', 26.80, 22, '中成药'),
        # 中药饮片
        ('金银花', '100g/袋', '同仁堂', 35.00, 30, '中药'),
        ('枸杞子', '250g/袋', '同仁堂', 42.00, 25, '中药'),
        ('黄芪', '200g/袋', '同仁堂', 38.00, 18, '中药'),
        ('当归', '150g/袋', '同仁堂', 45.00, 20, '中药'),
        ('党参', '200g/袋', '同仁堂', 36.00, 22, '中药'),
        # 医疗器械
        ('电子血压计', '上臂式', '欧姆龙', 298.00, 10, '器械'),
        ('血糖仪试纸', '50片/盒', '罗氏', 158.00, 15, '器械'),
    ]
    medicines = []
    for name, spec, mfr, price, stock, cat in medicine_data:
        m = Medicine(name=name, specification=spec, manufacturer=mfr,
                     price=price, stock=stock, category=cat)
        db.session.add(m)
        medicines.append(m)
    db.session.commit()
    print(f"  [7/10] {len(medicines)} 种药品 (覆盖{len(set(m.category for m in medicines))}个类别)")

    # ─── 8. 预约/问诊/处方/评价 历史数据 ───
    time_slots = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00',
                  '14:00-15:00', '15:00-16:00', '16:00-17:00']
    visit_types = ['first_visit', 'first_visit', 'first_visit', 'follow_up', 'follow_up', 'emergency']
    today = date.today()

    all_appointments = []
    all_consultations = []
    prescriptions_built = []
    reviews_built = []

    for day_offset in range(90, 0, -1):  # 过去90天
        appt_date = today - timedelta(days=day_offset)
        # 每天随机1-8个预约
        for _ in range(random.randint(1, 8)):
            doc = random.choice(doctors)
            pt = random.choice(patients)
            slot = random.choice(time_slots)
            status = random.choices(
                ['completed', 'completed', 'completed', 'confirmed', 'confirmed', 'pending', 'cancelled'],
                weights=[4, 4, 4, 2, 2, 2, 1]
            )[0]
            # 检查冲突 (简化: 随机有小概率冲突，忽略让它跳过)
            existing = Appointment.query.filter_by(
                doctor_id=doc.id, appointment_date=appt_date,
                time_slot=slot, status=status
            ).first()
            # 构建预约记录(用原始SQL插入方式绕过SQLAlchemy约束检查)
            day_count = Appointment.query.filter_by(
                doctor_id=doc.id, appointment_date=appt_date).count()
            appt = Appointment(
                patient_id=pt.id, doctor_id=doc.id,
                department_id=doc.department_id,
                appointment_date=appt_date, time_slot=slot,
                queue_number=day_count + 1,
                visit_type=random.choice(visit_types),
                description=random.choice([
                    '头痛伴发热2天', '咳嗽咳痰1周', '腹痛腹泻3天',
                    '腰背部疼痛半月', '皮肤瘙痒红肿', '失眠多梦',
                    '关节疼痛活动受限', '胸闷气短', '视力模糊',
                    '牙痛持续加重', '月经不规律', '小儿发热咳嗽',
                    '头晕乏力1月', '胃部不适反酸', '便秘',
                ]),
                status=status,
                cancel_reason='患者自行取消' if status == 'cancelled' else None,
                created_at=datetime.utcnow() - timedelta(days=day_offset)
            )
            db.session.add(appt)
            db.session.flush()  # 立即获取 appt.id
            all_appointments.append((appt, doc, pt, status, day_offset))

            # 如果已完成，生成问诊记录
            if status == 'completed':
                consult = Consultation(
                    appointment_id=appt.id,
                    patient_id=pt.id, doctor_id=doc.id,
                    chief_complaint=random.choice([
                        '反复发作性头痛3个月', '持续性干咳伴胸闷', '上腹部隐痛饭后加重',
                        '双侧膝关节疼痛伴晨僵', '面部皮疹伴瘙痒1周',
                    ]),
                    present_illness=random.choice([
                        '患者自述3天前无明显诱因出现上述症状，曾自行服药未见好转...',
                        '症状呈进行性加重，影响日常生活，遂来就诊...',
                    ]),
                    physical_exam='神志清，精神可。心肺听诊未见明显异常。腹部平软。',
                    vital_signs=f'{{"temp":{round(random.uniform(36.0,38.5),1)},"pulse":{random.randint(60,100)},"resp":{random.randint(16,24)},"bp":"{random.randint(110,140)}/{random.randint(65,95)}"}}',
                    diagnosis=random.choice([
                        '上呼吸道感染', '急性支气管炎', '高血压病1级',
                        '2型糖尿病', '颈椎病', '慢性胃炎', '过敏性皮炎',
                        '腰椎间盘突出症', '偏头痛', '焦虑状态',
                        '骨质疏松症', '冠心病 稳定性心绞痛',
                    ]),
                    advice=random.choice([
                        '清淡饮食，多休息，多饮水。按时服药，一周后复诊。',
                        '避免劳累，控制饮食。定期监测血压。不适随诊。',
                        '注意保暖，适当锻炼。继续服药巩固治疗。',
                    ]),
                    status='completed',
                    created_at=datetime.utcnow() - timedelta(days=day_offset),
                    completed_at=datetime.utcnow() - timedelta(days=day_offset - 1)
                )
                db.session.add(consult)
                db.session.flush()
                all_consultations.append((consult, doc, pt))

    db.session.commit()
    print(f"  [8/10] ~300 条预约记录 + ~{len(all_consultations)} 条问诊记录")

    # 问诊消息 (已完成问诊的对话)
    msg_count = 0
    for consult, doc, pt in all_consultations:
        for j in range(random.randint(2, 8)):
            sender_id = doc.id if j % 2 == 0 else pt.id
            sender = doc if j % 2 == 0 else pt
            db.session.add(ConsultationMessage(
                consultation_id=consult.id,
                sender_id=sender_id,
                content=random.choice([
                    '您好，请问哪里不舒服？', '多久了？有没有吃过什么药？',
                    '之前有没有类似的症状？家族里有没有人得过这个病？',
                    '最近是不是压力比较大？睡眠怎么样？',
                    '我建议先做一些检查，然后根据结果来定治疗方案。',
                    '好的，我先看一下。', '这个情况不算严重，先开点药吃吃看。',
                    '记得按时服药，注意饮食清淡。', '如果症状没有好转再来复诊。',
                    '我给你开个处方，去药房取药。注意看说明书上的用法用量。',
                ]),
                created_at=consult.created_at + timedelta(minutes=j * random.randint(2, 10))
            ))
            msg_count += 1
    db.session.commit()

    # 处方
    for consult, doc, pt in all_consultations:
        n_prescriptions = random.choices([0, 1, 2, 3], weights=[2, 4, 3, 1])[0]
        for _ in range(n_prescriptions):
            med = random.choice(medicines)
            qty = random.randint(1, 3)
            p = Prescription(
                consultation_id=consult.id,
                patient_id=pt.id, doctor_id=doc.id,
                medicine_name=med.name, specification=med.specification,
                dosage=random.choice(['每日3次，每次1片', '每日2次，每次2粒', '每日1次，每次1片', '饭前服用，每日3次']),
                quantity=qty, price=med.price * qty,
                notes=random.choice(['饭后服用', '忌辛辣', '多饮水', '', '注意观察不良反应']),
                status=random.choice(['prescribed', 'dispensed', 'dispensed']),
                created_at=consult.created_at + timedelta(minutes=5),
                dispensed_at=consult.created_at + timedelta(minutes=20) if random.random() > 0.3 else None
            )
            db.session.add(p)
            prescriptions_built.append((p, med, pt, consult))
    db.session.commit()
    print(f"  [8/10] 续: {msg_count} 条问诊消息 + ~{len(prescriptions_built)} 条处方")

    # 医生评价
    for consult, doc, pt in all_consultations:
        if random.random() < 0.6:
            rating = random.choices([5, 4, 3, 2, 1], weights=[4, 3, 2, 1, 0])[0]
            tags_list = [
                '态度好', '专业', '耐心', '讲解详细', '对症下药', '候诊时间短',
                '医术高明', '认真负责', '问诊细致', '值得信赖', '回复及时',
            ]
            review = DoctorReview(
                doctor_id=doc.id, patient_id=pt.id,
                consultation_id=consult.id, rating=rating,
                content=random.choice([
                    '医生态度很好，讲解很详细，非常感谢！',
                    '很专业，开的药效果不错。', '候诊时间有点长，但医生问得很仔细。',
                    '诊断准确，服务周到。', '态度和医术都很好，会推荐给朋友。',
                    '非常耐心，让病人很安心。', '回复及时，给了很好的建议。',
                ]),
                tags=','.join(random.sample(tags_list, random.randint(2, 5))),
                created_at=consult.completed_at + timedelta(hours=random.randint(1, 72))
            )
            db.session.add(review)
            reviews_built.append(review)
    db.session.commit()

    # 账单
    bill_count = 0
    for consult, doc, pt in all_consultations:
        if random.random() < 0.85:
            bill = Bill(
                patient_id=pt.id, consultation_id=consult.id,
                total_amount=0, status=random.choice(['paid', 'paid', 'paid', 'unpaid']),
                payment_method=random.choice(['wechat', 'alipay', 'insurance', 'cash']),
                paid_at=consult.completed_at + timedelta(minutes=random.randint(10, 60)),
                created_at=consult.completed_at
            )
            db.session.add(bill)
            db.session.flush()
            # 诊查费
            fee = doc.consultation_fee or 15
            db.session.add(BillItem(bill_id=bill.id, item_type='consultation_fee',
                           item_name='诊查费', quantity=1, unit_price=fee, subtotal=fee))
            bill.total_amount += fee
            # 处方费
            for p, med, _, _ in prescriptions_built:
                if p.consultation_id == consult.id:
                    db.session.add(BillItem(bill_id=bill.id, item_type='medicine',
                                   item_name=med.name, quantity=p.quantity,
                                   unit_price=med.price, subtotal=p.price))
                    bill.total_amount += p.price
            bill_count += 1
    db.session.commit()
    print(f"  [8/10] 续: {len(reviews_built)} 条评价 + {bill_count} 条账单")

    # ─── 9. 科普文章 (20篇) ───
    article_data = [
        ('夏季如何预防中暑？', '常见病', '介绍中暑的早期症状、预防措施及急救方法。'),
        ('儿童春季常见传染病防护指南', '儿科', '了解流感、手足口病等传染病的传播途径和预防方法。'),
        ('上班族颈椎病的自我检测与保健', '常见病', '教你如何自我检测颈椎健康，并提供有效的日常保健操。'),
        ('女性必须知道的妇科体检项目清单', '妇产', '详细介绍不同年龄段女性应该做的妇科检查项目。'),
        ('如何缓解焦虑情绪？心理科医生的建议', '心理', '6个实用的减压技巧，帮助应对日常焦虑。'),
        ('一日三餐怎么吃最健康？', '营养', '从早餐到晚餐，科学实用的饮食建议。'),
        ('高血压患者的日常管理指南', '心血管内科', '合理用药、低盐饮食和规律运动是控制血压的三驾马车。'),
        ('糖尿病患者饮食误区大盘点', '内分泌科', '很多糖友对饮食存在误解，本文一一澄清。'),
        ('腰椎间盘突出症保守治疗全攻略', '骨科', '90%的腰突患者无需手术，正确的保守治疗是关键。'),
        ('中老年骨质疏松预防指南', '骨科', '从饮食、运动和药物三个维度全面预防骨质疏松。'),
        ('秋季过敏性鼻炎防治手册', '呼吸内科', '花粉季来临前，做好这些准备让你安稳度过。'),
        ('近视防控从娃娃抓起——眼科医生的10条建议', '眼科', '儿童青少年近视率逐年攀升，预防比治疗更重要。'),
        ('牙周病——沉默的口腔健康杀手', '口腔科', '牙龈出血不是小事，可能是牙周病的早期信号。'),
        ('中医养生之春季养肝全攻略', '中医科', '春应肝而养生，介绍食疗、穴位按摩和起居调理方法。'),
        ('肿瘤早期筛查有多重要？', '肿瘤科', '早发现早治疗，5年生存率可提高数倍。'),
        ('脑卒中急救黄金4.5小时', '神经内科', '记住FAST口诀，关键时刻能救命。'),
        ('慢性胃炎患者的饮食调养', '消化内科', '三分治七分养，胃病的日常调理比吃药更重要。'),
        ('老年人防跌倒居家改造指南', '老年病科', '每年超30%的65岁以上老人发生跌倒，居家改造刻不容缓。'),
        ('运动康复——膝关节炎患者的非药物选择', '康复医学科', '科学的力量训练和拉伸可以显著改善膝关节功能。'),
        ('急性心肌梗死的早期识别与急救', '心血管内科', '胸痛、出汗、恶心——这些症状不要忽视。'),
    ]
    for title, cat, summary in article_data:
        body = f'<p>{summary}</p><p>本文由医联通健康科普团队联合{cat}专家撰写，内容经专业审核，仅供健康参考，不构成诊疗建议。如有不适，请及时就医。</p>'
        db.session.add(HealthArticle(
            title=title, summary=summary, content=body,
            category=cat, author_name=f'医联通{cat}科普',
            view_count=random.randint(50, 5000), is_published=True
        ))
    db.session.commit()
    print(f"  [9/10] {len(article_data)} 篇健康科普文章")

    # ─── 10. 公告 + 通知 ───
    announcements = [
        ('2026年夏季门诊时间调整通知', '自6月15日起，门诊时间调整为上午8:00-12:00，下午14:00-17:30。急诊24小时正常接诊。'),
        ('新增心理科门诊服务', '心理科门诊正式开设，由郑雅文主治医师坐诊。每周一至周五，提供心理咨询与心理治疗服务。'),
        ('医保报销政策更新', '2026年度门诊统筹报销比例调整为65%，年度限额调整为8000元。请参保患者就诊时出示医保卡。'),
        ('五一劳动节期间门诊安排', '5月1日-3日普通门诊停诊，急诊科24小时正常接诊。5月4日起恢复正常门诊。'),
        ('在线支付功能上线通知', '系统已开通微信支付和支付宝支付功能，患者可通过手机直接完成诊费支付，减少排队等候时间。'),
    ]
    for title, content in announcements:
        db.session.add(Announcement(title=title, content=content, author_id=admin.id,
                       is_pinned=random.choice([True, False])))
    db.session.commit()

    # 给一些患者发送通知
    for pt in random.sample(patients, min(30, len(patients))):
        db.session.add(Notification(
            user_id=pt.id,
            title=random.choice(['预约确认通知', '处方已开具', '复诊提醒', '账单待支付']),
            content=random.choice([
                '您的预约已被确认，请按时就诊。', '您的处方已生成，请在药房取药。',
                '您预约的就诊时间即将到达，请准时就诊。', '您有1笔账单待支付，请及时缴费。',
            ]),
            category=random.choice(['appointment', 'consultation', 'system']),
            is_read=random.choice([True, False])
        ))
    db.session.commit()
    print(f"  [10/10] {len(announcements)} 条公告 + {30} 条通知")

    print("=" * 50)
    print("✓ 大规模演示数据初始化完成！")
    print(f"  科室: {len(departments)} | 医生: {len(doctors)} | 患者: {len(patients)}")
    print(f"  药品: {len(medicines)} | 预约: ~300 | 问诊: ~{len(all_consultations)}")
    print(f"  处方: ~{len(prescriptions_built)} | 评价: {len(reviews_built)} | 账单: {bill_count}")
    print("=" * 50)

    # 打印测试账号
    print("\n测试账号:")
    print("  患者: 13800000001 / 123456")
    print("  医生: 13900000002 / 123456  (张伟，如存在)")
    print("  管理员: admin / admin123")
    print("  (所有患者/医生密码均为 123456)")
