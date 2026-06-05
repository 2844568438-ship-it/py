"""初始化数据库并填充演示数据"""
from models import db, Department, User, Schedule, Medicine, Announcement, HealthArticle, DoctorReview

def init_data():
    print("正在初始化演示数据...")

    # 科室
    dept_names = ['内科','外科','儿科','妇产科','骨科','皮肤科','眼科','口腔科','中医科','心理科']
    for name in dept_names:
        db.session.add(Department(name=name, description=f'{name}专业诊疗服务'))
    db.session.commit()
    print(f"  ✓ {len(dept_names)} 个科室")

    # 管理员
    admin = User(name='系统管理员', phone='admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    # 医生
    doctor_data = [
        ('张伟','13800000002','内科','主任医师','心血管疾病、高血压、糖尿病管理'),
        ('李芳','13800000003','儿科','副主任医师','儿童呼吸道感染、生长发育评估'),
        ('王建国','13800000004','外科','主任医师','腹腔镜手术、胃肠外科'),
        ('陈晓琳','13800000005','妇产科','主治医师','妇科炎症、产前检查'),
        ('刘大明','13800000006','骨科','副主任医师','骨折创伤、关节置换'),
        ('赵雪梅','13800000007','皮肤科','主任医师','痤疮、湿疹、激光美容'),
        ('孙志强','13800000008','眼科','主治医师','白内障、近视防控'),
        ('周海燕','13800000009','口腔科','副主任医师','种植牙、正畸'),
        ('吴明辉','13800000010','中医科','主任医师','针灸推拿、中药调理'),
        ('郑雅文','13800000011','心理科','主治医师','焦虑抑郁、心理咨询'),
    ]
    for name, phone, dept_name, title, specialty in doctor_data:
        dept = Department.query.filter_by(name=dept_name).first()
        d = User(name=name, phone=phone, role='doctor', department_id=dept.id,
                 title=title, specialty=specialty, gender='保密', age=40)
        d.set_password('123456')
        db.session.add(d)
    db.session.commit()
    print(f"  ✓ {len(doctor_data)} 位医生")

    # 患者
    for name, phone, gender, age in [
        ('李明','13800000001','男',28),('王芳','13900000001','女',35),
        ('赵小龙','13900000002','男',12),('陈晨','13900000003','女',45),
        ('刘洋','13900000004','男',52)
    ]:
        p = User(name=name, phone=phone, role='patient', gender=gender, age=age)
        p.set_password('123456')
        db.session.add(p)
    db.session.commit()
    print(f"  ✓ 5 位患者")

    # 排班
    doctors = User.query.filter_by(role='doctor').all()
    for doc in doctors:
        for day in range(0,5):
            db.session.add(Schedule(doctor_id=doc.id, day_of_week=day, start_time='08:00', end_time='12:00', max_patients=15))
            db.session.add(Schedule(doctor_id=doc.id, day_of_week=day, start_time='14:00', end_time='17:30', max_patients=15))
    db.session.commit()
    print("  ✓ 排班记录")

    # 药品
    for name, spec, mfr, price, stock, cat in [
        ('阿莫西林胶囊','0.5g×24粒','华北制药',18.50,200,'西药'),
        ('布洛芬缓释胶囊','0.3g×20粒','中美史克',22.80,300,'西药'),
        ('蒲地蓝消炎口服液','10ml×10支','济川药业',35.60,180,'中成药'),
        ('连花清瘟胶囊','0.35g×36粒','以岭药业',14.80,250,'中成药'),
        ('板蓝根颗粒','10g×20袋','白云山制药',16.00,500,'中成药'),
        ('维生素C片','0.1g×100片','东北制药',5.80,600,'保健品'),
        ('云南白药气雾剂','50ml','云南白药集团',45.00,100,'中成药'),
    ]:
        db.session.add(Medicine(name=name, specification=spec, manufacturer=mfr, price=price, stock=stock, category=cat))
    db.session.commit()
    print(f"  ✓ 7 种药品")

    # 科普文章
    for title, cat, summary in [
        ('夏季如何预防中暑？', '常见病', '介绍中暑的早期症状、预防措施及急救方法。'),
        ('儿童春季常见传染病防护指南', '儿科', '了解流感、手足口病等传染病的传播途径和预防方法。'),
        ('上班族颈椎病的自我检测与保健', '常见病', '教你如何自我检测颈椎健康，并提供有效的日常保健操。'),
        ('女性必须知道的妇科体检项目清单', '妇产', '详细介绍不同年龄段女性应该做的妇科检查项目。'),
        ('如何缓解焦虑情绪？心理科医生的建议', '心理', '6个实用的减压技巧，帮助应对日常焦虑。'),
        ('一日三餐怎么吃最健康？', '营养', '从早餐到晚餐，科学实用的饮食建议。'),
    ]:
        db.session.add(HealthArticle(title=title, summary=summary, content=f'<p>{summary}</p><p>本文由医联通健康科普团队撰写，仅供参考。</p>',
                       category=cat, author_name='医联通健康科普', view_count=100))
    db.session.commit()
    print(f"  ✓ 6 篇科普文章")

    # 公告
    for title, content in [
        ('2026年夏季门诊时间调整通知', '自6月15日起，门诊时间调整为上午8:00-12:00，下午14:00-17:30。'),
        ('新增心理科门诊服务', '心理科门诊正式开设，由郑雅文主治医师坐诊。每周一至周五。'),
        ('医保报销政策更新', '2026年度门诊统筹报销比例调整为65%，年度限额调整为8000元。'),
    ]:
        db.session.add(Announcement(title=title, content=content, author_id=admin.id))
    db.session.commit()
    print(f"  ✓ 3 条公告")

    print("演示数据初始化完成！")
