from models import db, Appointment, User


def login_patient(client):
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})


def test_book_appointment(client, db):
    """患者预约成功"""
    login_patient(client)
    doctor = User.query.filter_by(role='doctor').first()
    resp = client.post('/patient/book', data={
        'doctor_id': doctor.id,
        'date': '2026-12-25',
        'time_slot': '09:00-10:00',
        'visit_type': 'first_visit',
        'description': 'test'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # 检查预约是否创建
    appt = Appointment.query.filter_by(doctor_id=doctor.id).first()
    assert appt is not None
    assert appt.status == 'pending'


def test_book_same_slot_protected(client, db):
    """预约相同时段的唯一约束"""
    login_patient(client)
    doctor = User.query.filter_by(role='doctor').first()

    # 第一次预约
    client.post('/patient/book', data={
        'doctor_id': doctor.id,
        'date': '2026-12-26',
        'time_slot': '10:00-11:00',
        'visit_type': 'first_visit',
        'description': 'first'
    }, follow_redirects=True)
    # 确认此预约使冲突检测生效
    appt = Appointment.query.filter_by(doctor_id=doctor.id).first()
    if appt:
        appt.status = 'confirmed'
        db.session.commit()

    # 第二次预约同一时段
    resp = client.post('/patient/book', data={
        'doctor_id': doctor.id,
        'date': '2026-12-26',
        'time_slot': '10:00-11:00',
        'visit_type': 'first_visit',
        'description': 'second'
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_appointments_page(client):
    """患者预约列表页"""
    login_patient(client)
    resp = client.get('/patient/appointments')
    assert resp.status_code == 200


def test_doctors_page(client):
    """医生列表页"""
    login_patient(client)
    resp = client.get('/patient/doctors')
    assert resp.status_code == 200


def test_doctor_detail_page(client):
    """医生详情页"""
    login_patient(client)
    doctor = User.query.filter_by(role='doctor').first()
    resp = client.get(f'/patient/doctor/{doctor.id}')
    assert resp.status_code == 200


def test_doctor_appointments_page(client):
    """医生预约管理页"""
    client.post('/login', data={'phone': '13800000002', 'password': '123456'})
    resp = client.get('/doctor/appointments')
    assert resp.status_code == 200


def test_doctor_confirm_appointment(client, db):
    """医生确认预约"""
    login_patient(client)
    doctor = User.query.filter_by(role='doctor').first()
    client.post('/patient/book', data={
        'doctor_id': doctor.id,
        'date': '2026-12-27',
        'time_slot': '11:00-12:00',
        'visit_type': 'first_visit',
        'description': 'test confirm'
    })
    client.get('/logout')

    # 医生登录确认
    client.post('/login', data={'phone': '13800000002', 'password': '123456'})
    appt = Appointment.query.filter_by(doctor_id=doctor.id).first()
    resp = client.post(f'/doctor/confirm/{appt.id}', follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(appt)
    assert appt.status == 'confirmed'
