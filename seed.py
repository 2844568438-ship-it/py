"""初始化数据库并填充演示数据"""
from app import create_app
from models import db, Department, User, Schedule, Medicine, Announcement, HealthArticle, DoctorReview

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✓ 数据库表已创建")

    # ─── 科室 ───────────────────────────────────────
    dept_names = ['内科', '外科', '儿科', '妇产科', '骨科', '皮肤科', '眼科', '口腔科', '中医科', '心理科']
    dept_icons = ['heart-pulse', 'scalpel', 'baby', 'flower', 'bone', 'droplets', 'eye', 'smile', 'leaf', 'brain']
    depts = []
    for name, icon in zip(dept_names, dept_icons):
        d = Department(name=name, description=f'{name}专业诊疗服务', icon=icon)
        db.session.add(d)
        depts.append(d)
    db.session.commit()
    print(f"✓ 创建 {len(depts)} 个科室")

    # ─── 管理员 ──────────────────────────────────────
    admin = User(name='系统管理员', phone='admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # ─── 医生 ────────────────────────────────────────
    doctor_data = [
        ('张伟', '13800000002', '内科', '主任医师', '心血管疾病、高血压、糖尿病管理'),
        ('李芳', '13800000003', '儿科', '副主任医师', '儿童呼吸道感染、消化系统疾病、生长发育评估'),
        ('王建国', '13800000004', '外科', '主任医师', '腹腔镜手术、胃肠外科、甲状腺手术'),
        ('陈晓琳', '13800000005', '妇产科', '主治医师', '妇科炎症、月经不调、产前检查'),
        ('刘大明', '13800000006', '骨科', '副主任医师', '骨折创伤、关节置换、运动损伤'),
        ('赵雪梅', '13800000007', '皮肤科', '主任医师', '痤疮、湿疹、银屑病、激光美容'),
        ('孙志强', '13800000008', '眼科', '主治医师', '白内障、青光眼、近视防控'),
        ('周海燕', '13800000009', '口腔科', '副主任医师', '种植牙、正畸、牙周治疗'),
        ('吴明辉', '13800000010', '中医科', '主任医师', '针灸推拿、中药调理、亚健康管理'),
        ('郑雅文', '13800000011', '心理科', '主治医师', '焦虑抑郁、睡眠障碍、心理咨询'),
    ]
    doctors = []
    for name, phone, dept_name, title, specialty in doctor_data:
        dept = Department.query.filter_by(name=dept_name).first()
        d = User(name=name, phone=phone, role='doctor', department_id=dept.id,
                 title=title, specialty=specialty, gender='保密', age=40,
                 consultation_fee=0.0, bio=f'{title}，擅长{specialty}')
        d.set_password('123456')
        db.session.add(d)
        doctors.append(d)
    db.session.commit()
    print(f"✓ 创建 {len(doctors)} 位医生")

    # ─── 患者 ────────────────────────────────────────
    patient_data = [
        ('李明', '13800000001', '男', 28),
        ('王芳', '13900000001', '女', 35),
        ('赵小龙', '13900000002', '男', 12),
        ('陈晨', '13900000003', '女', 45),
        ('刘洋', '13900000004', '男', 52),
    ]
    for name, phone, gender, age in patient_data:
        p = User(name=name, phone=phone, role='patient', gender=gender, age=age)
        p.set_password('123456')
        db.session.add(p)
    db.session.commit()
    print(f"✓ 创建 {len(patient_data)} 位患者")

    # ─── 排班 ────────────────────────────────────────
    for doctor in doctors:
        for day in range(0, 5):  # 周一至周五
            s = Schedule(doctor_id=doctor.id, day_of_week=day,
                        start_time='08:00', end_time='12:00', max_patients=15)
            db.session.add(s)
            s2 = Schedule(doctor_id=doctor.id, day_of_week=day,
                         start_time='14:00', end_time='17:30', max_patients=15)
            db.session.add(s2)
    db.session.commit()
    print(f"✓ 创建排班记录")

    # ─── 药品 ────────────────────────────────────────
    medicine_data = [
        ('阿莫西林胶囊', '0.5g×24粒', '华北制药', 18.50, 200, '西药'),
        ('头孢克肟分散片', '0.1g×6片', '白云山制药', 32.00, 150, '西药'),
        ('布洛芬缓释胶囊', '0.3g×20粒', '中美史克', 22.80, 300, '西药'),
        ('复方氨酚烷胺片', '12片', '哈药六厂', 12.00, 400, '西药'),
        ('蒲地蓝消炎口服液', '10ml×10支', '济川药业', 35.60, 180, '中成药'),
        ('连花清瘟胶囊', '0.35g×36粒', '以岭药业', 14.80, 250, '中成药'),
        ('板蓝根颗粒', '10g×20袋', '白云山制药', 16.00, 500, '中成药'),
        ('藿香正气水', '10ml×10支', '太极集团', 8.50, 350, '中成药'),
        ('维生素C片', '0.1g×100片', '东北制药', 5.80, 600, '保健品'),
        ('葡萄糖酸钙口服液', '10ml×12支', '三精制药', 28.00, 200, '保健品'),
        ('消食健胃片', '0.5g×100片', '同仁堂', 19.80, 150, '中成药'),
        ('红霉素软膏', '10g', '华北制药', 6.50, 300, '西药'),
        ('氯雷他定片', '10mg×6片', '先声药业', 15.00, 220, '西药'),
        ('云南白药气雾剂', '50ml', '云南白药集团', 45.00, 100, '中成药'),
        ('蒙脱石散', '3g×10袋', '博福-益普生', 18.00, 280, '西药'),
    ]
    for name, spec, mfr, price, stock, cat in medicine_data:
        med = Medicine(name=name, specification=spec, manufacturer=mfr,
                       price=price, stock=stock, category=cat)
        db.session.add(med)
    db.session.commit()
    print(f"✓ 创建 {len(medicine_data)} 种药品")

    # ─── 公告 ────────────────────────────────────────
    ann_data = [
        ('关于2026年夏季门诊时间调整的通知',
         '自6月15日起，门诊时间调整为上午8:00-12:00，下午14:00-17:30。周末及节假日正常开诊。请各位患者合理安排就诊时间。'),
        ('新增心理科门诊服务',
         '我院已正式开设心理科门诊，由郑雅文主治医师坐诊。提供焦虑、抑郁、睡眠障碍等心理咨询服务。门诊时间：每周一至周五。'),
        ('医保报销政策更新',
         '根据广州市医保局最新通知，2026年度门诊统筹报销比例调整为65%（退休人员为70%），年度限额调整为8000元。'),
    ]
    for i, (title, content) in enumerate(ann_data):
        ann = Announcement(title=title, content=content, author_id=admin.id, is_pinned=i < 2)
        db.session.add(ann)
    db.session.commit()
    print(f"✓ 创建 {len(ann_data)} 条公告")

    # ─── 健康科普文章 ────────────────────────────
    article_data = [
        ('夏季如何预防中暑？这些方法要知道', '常见病',
         '随着夏季高温来临，中暑成为常见急症。本文介绍中暑的早期症状、预防措施及急救方法。保持充足饮水、避免高温时段外出、穿着透气衣物是最基本的预防手段。',
         '<p>中暑是指在高温环境下，人体体温调节功能紊乱而引起的以中枢神经系统和循环系统障碍为主要表现的急性疾病。</p><h3>中暑的早期信号</h3><p>出现头晕、头痛、口渴、多汗、四肢无力等症状时，应警惕中暑的发生。此时体温可能正常或略有升高。</p><h3>预防措施</h3><ul><li>每天饮水2000-3000ml，少量多次</li><li>避免在10:00-16:00高温时段外出</li><li>穿着浅色、宽松、透气的棉质衣物</li><li>室内保持通风，使用空调或风扇降温</li></ul>'),
        ('儿童春季常见传染病防护指南', '儿科',
         '春季是流感、手足口病、水痘等传染病的高发季节，儿童由于免疫系统尚未发育完全，更容易被感染。了解常见传染病的传播途径和预防方法，对保护孩子健康至关重要。',
         '<p>春季气温回暖，各种病毒和细菌开始活跃，儿童群体成为传染病的高危人群。</p><h3>常见传染病</h3><p><strong>流感：</strong>由流感病毒引起，表现为高热、咳嗽、全身酸痛。</p><p><strong>手足口病：</strong>多见于5岁以下儿童，手、足、口腔出现疱疹。</p><h3>防护要点</h3><ul><li>按时接种疫苗</li><li>勤洗手，保持个人卫生</li><li>避免去人群密集场所</li><li>保持室内通风</li></ul>'),
        ('上班族必看：颈椎病的自我检测与日常保健', '常见病',
         '长期伏案工作、低头看手机，让颈椎病成为现代都市人的通病。本文教你如何自我检测颈椎健康，并提供简单有效的日常保健操。',
         '<p>颈椎病发病率逐年上升且呈年轻化趋势，20-45岁人群占比超过60%。</p><h3>自我检测方法</h3><p>如果你经常出现以下症状，可能颈椎已经发出警报：颈肩酸痛、手指麻木、头晕头痛、转头时有响声。</p><h3>5分钟颈椎保健操</h3><p>每天早晚各做一次，每个动作保持5秒，重复10次。</p>'),
        ('女性必须知道的妇科体检项目清单', '妇产',
         '定期妇科体检是女性健康的重要保障。本文详细介绍不同年龄段女性应该做的妇科检查项目，帮助你科学规划年度体检。',
         '<p>很多妇科疾病早期没有明显症状，定期体检是早发现、早治疗的关键。</p><h3>基础检查项目</h3><ul><li>妇科常规检查（每年1次）</li><li>宫颈TCT筛查（21岁以上，每3年1次）</li><li>乳腺彩超（每年1次）</li><li>HPV检测（30岁以上，每5年1次）</li></ul>'),
        ('如何缓解焦虑情绪？心理科医生的6个建议', '心理',
         '现代人面临工作压力、人际关系、生活节奏快等多重挑战，焦虑情绪成为常见心理问题。本文由心理科医生分享6个实用减压技巧。',
         '<p>适度焦虑是正常的，但如果影响到日常生活，就需要引起重视。</p><h3>6个减压建议</h3><ol><li>正念呼吸法：每天5分钟专注呼吸</li><li>运动释放：每周3次有氧运动</li><li>规律作息：保证7-8小时睡眠</li><li>社交支持：多与亲友沟通交流</li><li>写日记：记录情绪变化</li><li>必要时寻求专业帮助</li></ol>'),
        ('一日三餐怎么吃最健康？营养师推荐饮食方案', '营养',
         '合理膳食是健康的基石。本文从早餐、午餐、晚餐三个维度，结合中国居民膳食指南，给出科学实用的饮食建议。',
         '<p>根据《中国居民膳食指南（2022）》，建议每天摄入12种以上食物，每周25种以上。</p><h3>三餐黄金比例</h3><p>早餐占全天能量的30%，午餐40%，晚餐30%。</p><h3>推荐食谱示例</h3><p><strong>早餐：</strong>全麦面包+鸡蛋+牛奶+水果</p><p><strong>午餐：</strong>杂粮饭+清蒸鱼+时蔬</p><p><strong>晚餐：</strong>小米粥+豆腐+凉拌菜</p>'),
    ]
    for title, cat, summary, content in article_data:
        art = HealthArticle(title=title, summary=summary, content=content, category=cat,
                            author_name='医联通健康科普', view_count=100 + (len(cat) * 50))
        db.session.add(art)
    db.session.commit()
    print(f"✓ 创建 {len(article_data)} 篇健康科普")

    # ─── 医生评价示例 ────────────────────────────
    all_patients = User.query.filter_by(role='patient').all()
    review_data = [
        (doctors[0].id, all_patients[0].id, 5, '张医生非常专业耐心，详细询问了我的症状，开的药很对症，几天就好了。', '态度好,专业,耐心细致'),
        (doctors[1].id, all_patients[1].id, 4, '李医生对小朋友很温柔，孩子不害怕，诊断也很准确。', '态度好,有耐心'),
        (doctors[4].id, all_patients[2].id, 5, '刘医生技术很好，手术恢复很快，感谢！', '技术好,专业,态度好'),
    ]
    for doc_id, pat_id, rating, content, tags in review_data:
        review = DoctorReview(doctor_id=doc_id, patient_id=pat_id,
                              rating=rating, content=content, tags=tags)
        db.session.add(review)
    db.session.commit()
    print(f"✓ 创建 {len(review_data)} 条医生评价")

    print("\n🎉 数据初始化完成！")
    print("=" * 50)
    print("患者测试账号: 13800000001 / 123456")
    print("医生测试账号: 13800000002 / 123456")
    print("管理员账号:   admin / admin123")
    print("=" * 50)
