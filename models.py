from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ============================================================
# 科室表
# ============================================================
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(32), default='stethoscope')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctors = db.relationship('User', backref='department', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'description': self.description, 'icon': self.icon,
            'doctor_count': self.doctors.count()
        }

# ============================================================
# 用户基类（多态：Patient / Doctor / Admin）
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(16), nullable=False, default='patient')  # patient / doctor / admin
    gender = db.Column(db.String(8))
    age = db.Column(db.Integer)
    avatar = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 医生专用字段
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    title = db.Column(db.String(64))             # 职称
    specialty = db.Column(db.Text)               # 擅长领域
    bio = db.Column(db.Text)                     # 个人简介
    education = db.Column(db.Text)               # 教育背景 JSON
    training = db.Column(db.Text)                # 规培/进修经历 JSON
    research = db.Column(db.Text)                # 科研方向与成果
    mentorship = db.Column(db.String(64))        # 导师类型
    awards = db.Column(db.Text)                  # 获奖与荣誉
    hospital = db.Column(db.String(128))         # 所在医院
    consultation_fee = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'

# ============================================================
# 排班表
# ============================================================
class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=周一 .. 6=周日
    start_time = db.Column(db.String(8), nullable=False)  # "08:00"
    end_time = db.Column(db.String(8), nullable=False)    # "12:00"
    max_patients = db.Column(db.Integer, default=20)

    doctor = db.relationship('User', backref='schedules')

# ============================================================
# 预约表
# ============================================================
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(32), nullable=False)   # "08:00-09:00"
    queue_number = db.Column(db.Integer)                    # 当日排队号
    visit_type = db.Column(db.String(16), default='first_visit')  # first_visit/follow_up/emergency
    description = db.Column(db.Text)                        # 病情描述
    status = db.Column(db.String(16), default='pending')    # pending/confirmed/completed/cancelled
    cancel_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')
    department = db.relationship('Department', backref='appointments')

    __table_args__ = (
        db.Index('idx_active_appt', 'doctor_id', 'appointment_date', 'time_slot',
                 unique=True,
                 sqlite_where=db.text("status IN ('pending', 'confirmed')")),
    )

# ============================================================
# 问诊记录表
# ============================================================
class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chief_complaint = db.Column(db.Text)     # 主诉
    present_illness = db.Column(db.Text)     # 现病史
    physical_exam = db.Column(db.Text)       # 体格检查
    vital_signs = db.Column(db.Text)         # JSON: {"temp":36.5,"pulse":72,"resp":18,"bp":"120/80"}
    diagnosis = db.Column(db.Text)           # 诊断结果
    advice = db.Column(db.Text)              # 医嘱
    status = db.Column(db.String(16), default='ongoing')  # ongoing / completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    appointment = db.relationship('Appointment', backref='consultation')
    patient = db.relationship('User', foreign_keys=[patient_id])
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    messages = db.relationship('ConsultationMessage', backref='consultation', lazy='dynamic',
                               order_by='ConsultationMessage.created_at')

# ============================================================
# 问诊消息表
# ============================================================
class ConsultationMessage(db.Model):
    __tablename__ = 'consultation_messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User')

# ============================================================
# 处方表
# ============================================================
class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_name = db.Column(db.String(128), nullable=False)
    specification = db.Column(db.String(64))     # 规格
    dosage = db.Column(db.String(64))             # 用法用量
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    status = db.Column(db.String(16), default='prescribed')  # prescribed/dispensed
    dispensed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    consultation = db.relationship('Consultation', backref='prescriptions')
    patient = db.relationship('User', foreign_keys=[patient_id])
    doctor = db.relationship('User', foreign_keys=[doctor_id])

# ============================================================
# 药品库表
# ============================================================
class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    specification = db.Column(db.String(64))
    manufacturer = db.Column(db.String(128))
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(32))   # 西药/中药/中成药/保健品
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================
# 公告表
# ============================================================
class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User')

# ============================================================
# 医生评价表
# ============================================================
class DoctorReview(db.Model):
    __tablename__ = 'doctor_reviews'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 星
    content = db.Column(db.Text)
    tags = db.Column(db.String(256))  # 逗号分隔标签："态度好,专业,耐心"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('User', foreign_keys=[doctor_id])
    patient = db.relationship('User', foreign_keys=[patient_id])

# ============================================================
# 健康科普文章表
# ============================================================
class HealthArticle(db.Model):
    __tablename__ = 'health_articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(32))  # 常见病/养生/儿科/妇产/心理/营养
    cover_image = db.Column(db.String(256))
    author_name = db.Column(db.String(64))
    view_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================
# 消息通知表
# ============================================================
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    link = db.Column(db.String(256))
    is_read = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(16), default='system')  # system/appointment/consultation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')

# ============================================================
# 账单表
# ============================================================
class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey('consultations.id'), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(16), default='unpaid')  # unpaid/paid/refunded
    payment_method = db.Column(db.String(32))  # cash/wechat/alipay/insurance
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('User', foreign_keys=[patient_id])
    consultation = db.relationship('Consultation', backref='bill')
    items = db.relationship('BillItem', backref='bill', lazy='dynamic',
                             order_by='BillItem.id')

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    item_type = db.Column(db.String(16), nullable=False)  # consultation_fee/medicine
    item_name = db.Column(db.String(256), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, default=0.0)

# ============================================================
# 患者健康档案表
# ============================================================
class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    blood_type = db.Column(db.String(8))       # A/B/AB/O
    allergies = db.Column(db.Text)              # JSON: ["青霉素","海鲜"]
    chronic_diseases = db.Column(db.Text)       # JSON: ["高血压","糖尿病"]
    family_history = db.Column(db.Text)
    smoking = db.Column(db.String(16))          # never/former/current
    alcohol = db.Column(db.String(16))          # never/occasional/regular
    height = db.Column(db.Float)                # cm
    weight = db.Column(db.Float)                # kg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('User', backref='profile', uselist=False)
