from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Department, User, Appointment, Consultation, Prescription, Medicine, Announcement, Bill, BillItem
from datetime import datetime, date, timedelta
from collections import Counter

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    if not current_user.is_admin():
        flash('需要管理员权限', 'error')
        return redirect(url_for('auth.dashboard'))
    return None

# ─── 数据看板 ─────────────────────────────────
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    err = admin_required()
    if err: return err

    today = date.today()
    week_ago = today - timedelta(days=6)

    # 基础统计
    total_appts = Appointment.query.count()
    today_appts = Appointment.query.filter_by(appointment_date=today).count()
    today_consults = Consultation.query.filter(
        Consultation.created_at >= today.strftime('%Y-%m-%d')).count()
    today_prescriptions = Prescription.query.filter(
        Prescription.created_at >= today.strftime('%Y-%m-%d')).count()
    total_patients = User.query.filter_by(role='patient').count()
    total_doctors = User.query.filter_by(role='doctor').count()

    # 科室分布
    dept_stats = db.session.query(Department.name, db.func.count(Appointment.id))\
        .join(Appointment, Appointment.department_id == Department.id)\
        .group_by(Department.name).all()
    dept_labels = [d[0] for d in dept_stats]
    dept_values = [d[1] for d in dept_stats]

    # 近7天预约趋势
    trend_labels = []
    trend_values = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        trend_labels.append(d.strftime('%m-%d'))
        trend_values.append(Appointment.query.filter_by(appointment_date=d).count())

    # 热门医生
    top_doctors = db.session.query(User.name, db.func.count(Appointment.id).label('cnt'))\
        .join(Appointment, Appointment.doctor_id == User.id)\
        .filter(User.role == 'doctor')\
        .group_by(User.name).order_by(db.text('cnt DESC')).limit(5).all()

    # 状态分布
    status_stats = db.session.query(Appointment.status, db.func.count(Appointment.id))\
        .group_by(Appointment.status).all()
    status_map = {'pending': '待确认', 'confirmed': '已确认', 'completed': '已完成', 'cancelled': '已取消'}
    status_labels = [status_map.get(s[0], s[0]) for s in status_stats]
    status_values = [s[1] for s in status_stats]

    # 财务统计
    total_revenue = db.session.query(db.func.sum(Bill.total_amount))\
        .filter(Bill.status == 'paid').scalar() or 0
    today_revenue = db.session.query(db.func.sum(Bill.total_amount))\
        .filter(Bill.status == 'paid', Bill.paid_at >= today.strftime('%Y-%m-%d')).scalar() or 0
    unpaid_count = Bill.query.filter_by(status='unpaid').count()
    low_stock = Medicine.query.filter(Medicine.stock < 20).count()

    return render_template('admin/dashboard.html',
        total_appts=total_appts, today_appts=today_appts,
        today_consults=today_consults, today_prescriptions=today_prescriptions,
        total_patients=total_patients, total_doctors=total_doctors,
        total_revenue=total_revenue, today_revenue=today_revenue,
        unpaid_count=unpaid_count, low_stock=low_stock,
        dept_labels=dept_labels, dept_values=dept_values,
        trend_labels=trend_labels, trend_values=trend_values,
        top_doctors=top_doctors,
        status_labels=status_labels, status_values=status_values)

# ─── 科室管理 ─────────────────────────────────
@admin_bp.route('/departments')
@login_required
def departments():
    err = admin_required()
    if err: return err
    depts = Department.query.all()
    return render_template('admin/departments.html', departments=depts)

@admin_bp.route('/department/add', methods=['POST'])
@login_required
def add_department():
    err = admin_required()
    if err: return err
    name = request.form.get('name', '').strip()
    desc = request.form.get('description', '').strip()
    icon = request.form.get('icon', 'stethoscope')
    if name:
        dept = Department(name=name, description=desc, icon=icon)
        db.session.add(dept)
        db.session.commit()
        flash('科室添加成功', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/department/edit/<int:dept_id>', methods=['POST'])
@login_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    dept.name = request.form.get('name', dept.name).strip()
    dept.description = request.form.get('description', dept.description).strip()
    dept.icon = request.form.get('icon', dept.icon)
    db.session.commit()
    flash('科室更新成功', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/department/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    if dept.doctors.count() > 0:
        flash('该科室下还有医生，请先移除医生', 'error')
        return redirect(url_for('admin.departments'))
    db.session.delete(dept)
    db.session.commit()
    flash('科室已删除', 'info')
    return redirect(url_for('admin.departments'))

# ─── 医生管理 ─────────────────────────────────
@admin_bp.route('/doctors')
@login_required
def doctors():
    err = admin_required()
    if err: return err
    doctors = User.query.filter_by(role='doctor').order_by(User.name).all()
    departments = Department.query.all()
    return render_template('admin/doctors.html', doctors=doctors, departments=departments)

@admin_bp.route('/doctor/add', methods=['POST'])
@login_required
def add_doctor():
    err = admin_required()
    if err: return err
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '123456')
    dept_id = request.form.get('department_id', type=int)
    title = request.form.get('title', '').strip()
    specialty = request.form.get('specialty', '').strip()

    if not all([name, phone, dept_id]):
        flash('请填写完整信息', 'error')
        return redirect(url_for('admin.doctors'))

    if User.query.filter_by(phone=phone).first():
        flash('该手机号已存在', 'error')
        return redirect(url_for('admin.doctors'))

    doctor = User(name=name, phone=phone, role='doctor',
                  department_id=dept_id, title=title, specialty=specialty)
    doctor.set_password(password)
    db.session.add(doctor)
    db.session.commit()
    flash('医生添加成功', 'success')
    return redirect(url_for('admin.doctors'))

@admin_bp.route('/doctor/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_doctor(doc_id):
    doctor = User.query.get_or_404(doc_id)
    if doctor.role != 'doctor':
        flash('无效操作', 'error')
        return redirect(url_for('admin.doctors'))
    db.session.delete(doctor)
    db.session.commit()
    flash('医生已删除', 'info')
    return redirect(url_for('admin.doctors'))

# ─── 患者管理 ─────────────────────────────────
@admin_bp.route('/patients')
@login_required
def patients():
    err = admin_required()
    if err: return err
    patients = User.query.filter_by(role='patient').order_by(User.created_at.desc()).all()
    return render_template('admin/patients.html', patients=patients)

# ─── 药品管理 ─────────────────────────────────
@admin_bp.route('/medicines')
@login_required
def medicines():
    err = admin_required()
    if err: return err
    meds = Medicine.query.order_by(Medicine.name).all()
    return render_template('admin/medicines.html', medicines=meds)

@admin_bp.route('/medicine/add', methods=['POST'])
@login_required
def add_medicine():
    name = request.form.get('name', '').strip()
    spec = request.form.get('specification', '').strip()
    manufacturer = request.form.get('manufacturer', '').strip()
    price = request.form.get('price', type=float, default=0)
    stock = request.form.get('stock', type=int, default=0)
    category = request.form.get('category', '').strip()

    if name:
        med = Medicine(name=name, specification=spec, manufacturer=manufacturer,
                       price=price, stock=stock, category=category)
        db.session.add(med)
        db.session.commit()
        flash('药品添加成功', 'success')
    return redirect(url_for('admin.medicines'))

@admin_bp.route('/medicine/edit/<int:med_id>', methods=['POST'])
@login_required
def edit_medicine(med_id):
    med = Medicine.query.get_or_404(med_id)
    med.name = request.form.get('name', med.name).strip()
    med.specification = request.form.get('specification', med.specification).strip()
    med.manufacturer = request.form.get('manufacturer', med.manufacturer).strip()
    med.price = request.form.get('price', type=float, default=med.price)
    med.stock = request.form.get('stock', type=int, default=med.stock)
    med.category = request.form.get('category', med.category).strip()
    db.session.commit()
    flash('药品更新成功', 'success')
    return redirect(url_for('admin.medicines'))

@admin_bp.route('/medicine/delete/<int:med_id>', methods=['POST'])
@login_required
def delete_medicine(med_id):
    med = Medicine.query.get_or_404(med_id)
    db.session.delete(med)
    db.session.commit()
    flash('药品已删除', 'info')
    return redirect(url_for('admin.medicines'))

# ─── 公告管理 ─────────────────────────────────
@admin_bp.route('/announcements')
@login_required
def announcements():
    err = admin_required()
    if err: return err
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=anns)

@admin_bp.route('/announcement/add', methods=['POST'])
@login_required
def add_announcement():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if title and content:
        ann = Announcement(title=title, content=content, author_id=current_user.id)
        db.session.add(ann)
        db.session.commit()
        flash('公告发布成功', 'success')
    return redirect(url_for('admin.announcements'))

@admin_bp.route('/announcement/delete/<int:ann_id>', methods=['POST'])
@login_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('公告已删除', 'info')
    return redirect(url_for('admin.announcements'))

# ─── 账单管理 ─────────────────────────────────
@admin_bp.route('/bills')
@login_required
def bills():
    err = admin_required()
    if err: return err
    filter_status = request.args.get('status', '')
    query = Bill.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    bills = query.order_by(Bill.created_at.desc()).limit(200).all()
    return render_template('admin/bills.html', bills=bills, filter_status=filter_status)

@admin_bp.route('/bill/<int:bill_id>')
@login_required
def bill_detail(bill_id):
    err = admin_required()
    if err: return err
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill_id).all()
    return render_template('admin/bill_detail.html', bill=bill, items=items)

# ─── 发药管理 ─────────────────────────────────
@admin_bp.route('/pharmacy')
@login_required
def pharmacy():
    err = admin_required()
    if err: return err
    prescriptions = Prescription.query.order_by(Prescription.created_at.desc()).limit(200).all()
    return render_template('admin/pharmacy.html', prescriptions=prescriptions)

@admin_bp.route('/pharmacy/dispense/<int:prescription_id>', methods=['POST'])
@login_required
def pharmacy_dispense(prescription_id):
    p = Prescription.query.get_or_404(prescription_id)
    if p.status == 'dispensed':
        flash('已发药', 'info')
        return redirect(url_for('admin.pharmacy'))
    med = Medicine.query.filter_by(name=p.medicine_name).first()
    if med:
        if med.stock < p.quantity:
            flash(f'{med.name} 库存不足', 'error')
            return redirect(url_for('admin.pharmacy'))
        med.stock -= p.quantity
    p.status = 'dispensed'
    p.dispensed_at = datetime.utcnow()
    db.session.commit()
    flash(f'{p.medicine_name} 发药成功', 'success')
    return redirect(url_for('admin.pharmacy'))
