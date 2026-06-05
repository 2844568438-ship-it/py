from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Department, User, Schedule, Appointment, Consultation, ConsultationMessage, Prescription
from datetime import datetime, date, timedelta

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_patient():
        flash('无权访问', 'error')
        return redirect(url_for('auth.dashboard'))

    appointments = Appointment.query.filter_by(patient_id=current_user.id)\
        .order_by(Appointment.created_at.desc()).limit(5).all()
    consultations = Consultation.query.filter_by(patient_id=current_user.id)\
        .order_by(Consultation.created_at.desc()).limit(5).all()

    today_appts = Appointment.query.filter_by(patient_id=current_user.id,
        appointment_date=date.today()).count()
    completed = Appointment.query.filter_by(patient_id=current_user.id, status='completed').count()

    return render_template('patient/dashboard.html',
        appointments=appointments, consultations=consultations,
        today_appts=today_appts, completed=completed)

@patient_bp.route('/doctors')
@login_required
def doctors():
    if not current_user.is_patient():
        flash('无权访问', 'error')
        return redirect(url_for('auth.dashboard'))

    dept_id = request.args.get('dept_id', type=int)
    search = request.args.get('search', '').strip()

    departments = Department.query.all()
    query = User.query.filter_by(role='doctor')
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if search:
        query = query.filter(User.name.contains(search) | User.specialty.contains(search))
    doctors = query.all()

    return render_template('patient/doctors.html',
        departments=departments, doctors=doctors,
        current_dept=dept_id, search=search)

@patient_bp.route('/appointments')
@login_required
def appointments():
    if not current_user.is_patient():
        flash('无权访问', 'error')
        return redirect(url_for('auth.dashboard'))

    appts = Appointment.query.filter_by(patient_id=current_user.id)\
        .order_by(Appointment.created_at.desc()).all()
    return render_template('patient/appointments.html', appointments=appts)

@patient_bp.route('/book', methods=['POST'])
@login_required
def book():
    if not current_user.is_patient():
        return jsonify({'error': '无权操作'}), 403

    doctor_id = request.form.get('doctor_id', type=int)
    appt_date = request.form.get('date')
    time_slot = request.form.get('time_slot')
    description = request.form.get('description', '').strip()

    doctor = User.query.get(doctor_id)
    if not doctor or not doctor.is_doctor():
        flash('无效的医生', 'error')
        return redirect(url_for('patient.doctors'))

    if not appt_date or not time_slot:
        flash('请选择日期和时段', 'error')
        return redirect(url_for('patient.doctors'))

    existing = Appointment.query.filter_by(doctor_id=doctor_id,
        appointment_date=appt_date, time_slot=time_slot,
        status='confirmed').first()
    if existing:
        flash('该时段已被预约', 'error')
        return redirect(url_for('patient.doctors'))

    appt = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        department_id=doctor.department_id,
        appointment_date=datetime.strptime(appt_date, '%Y-%m-%d').date(),
        time_slot=time_slot,
        description=description,
        status='pending'
    )
    db.session.add(appt)
    db.session.commit()
    flash('预约提交成功，等待医生确认', 'success')
    return redirect(url_for('patient.appointments'))

@patient_bp.route('/cancel_appointment/<int:appt_id>', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('patient.appointments'))
    appt.status = 'cancelled'
    appt.cancel_reason = request.form.get('reason', '患者取消')
    db.session.commit()
    flash('预约已取消', 'info')
    return redirect(url_for('patient.appointments'))

@patient_bp.route('/consultation/<int:appt_id>')
@login_required
def consultation(appt_id):
    if not current_user.is_patient():
        return redirect(url_for('auth.dashboard'))

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('patient.appointments'))

    consult = Consultation.query.filter_by(appointment_id=appt_id).first()
    if not consult:
        consult = Consultation(
            appointment_id=appt_id,
            patient_id=current_user.id,
            doctor_id=appt.doctor_id,
            status='ongoing'
        )
        db.session.add(consult)
        appt.status = 'confirmed'
        db.session.commit()

    messages = ConsultationMessage.query.filter_by(consultation_id=consult.id)\
        .order_by(ConsultationMessage.created_at.asc()).all()
    prescriptions = Prescription.query.filter_by(consultation_id=consult.id).all()

    return render_template('patient/consultation.html',
        consultation=consult, messages=messages,
        prescriptions=prescriptions, appointment=appt)

@patient_bp.route('/send_message/<int:consult_id>', methods=['POST'])
@login_required
def send_message(consult_id):
    consult = Consultation.query.get_or_404(consult_id)
    if consult.patient_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403

    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'error': '内容不能为空'}), 400

    msg = ConsultationMessage(
        consultation_id=consult_id,
        sender_id=current_user.id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'ok': True, 'time': msg.created_at.strftime('%H:%M')})

@patient_bp.route('/records')
@login_required
def records():
    if not current_user.is_patient():
        return redirect(url_for('auth.dashboard'))

    consultations = Consultation.query.filter_by(patient_id=current_user.id)\
        .order_by(Consultation.created_at.desc()).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id)\
        .order_by(Prescription.created_at.desc()).all()

    return render_template('patient/records.html',
        consultations=consultations, prescriptions=prescriptions)

@patient_bp.route('/doctor/<int:doc_id>')
@login_required
def doctor_detail(doc_id):
    from models import DoctorReview
    doctor = User.query.get_or_404(doc_id)
    reviews = DoctorReview.query.filter_by(doctor_id=doc_id)\
        .order_by(DoctorReview.created_at.desc()).all()
    avg_rating = db.session.query(db.func.avg(DoctorReview.rating))\
        .filter_by(doctor_id=doc_id).scalar() or 0
    review_count = len(reviews)
    return render_template('patient/doctor_detail.html',
        doctor=doctor, reviews=reviews, avg_rating=round(avg_rating, 1), review_count=review_count)

@patient_bp.route('/review/<int:consult_id>', methods=['POST'])
@login_required
def submit_review(consult_id):
    from models import DoctorReview
    consult = Consultation.query.get_or_404(consult_id)
    if consult.patient_id != current_user.id:
        flash('无权操作', 'error')
        return redirect(url_for('patient.records'))
    existing = DoctorReview.query.filter_by(consultation_id=consult_id).first()
    if existing:
        flash('已评价过', 'info')
        return redirect(url_for('patient.records'))
    rating = request.form.get('rating', type=int, default=5)
    content = request.form.get('content', '').strip()
    tags = request.form.get('tags', '').strip()
    review = DoctorReview(doctor_id=consult.doctor_id, patient_id=current_user.id,
                          consultation_id=consult_id, rating=rating, content=content, tags=tags)
    db.session.add(review)
    db.session.commit()
    flash('评价提交成功，感谢您的反馈！', 'success')
    return redirect(url_for('patient.records'))

@patient_bp.route('/articles')
@login_required
def articles():
    from models import HealthArticle
    cat = request.args.get('category', 'all')
    query = HealthArticle.query.filter_by(is_published=True)
    if cat != 'all':
        query = query.filter_by(category=cat)
    articles = query.order_by(HealthArticle.created_at.desc()).all()
    categories = ['常见病', '养生', '儿科', '妇产', '心理', '营养']
    return render_template('patient/articles.html', articles=articles, categories=categories, current_cat=cat)

@patient_bp.route('/article/<int:art_id>')
@login_required
def article_detail(art_id):
    from models import HealthArticle
    article = HealthArticle.query.get_or_404(art_id)
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    return render_template('patient/article_detail.html', article=article)
