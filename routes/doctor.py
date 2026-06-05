from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Appointment, Consultation, ConsultationMessage, Prescription, Medicine, Bill, BillItem
from datetime import datetime, date

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_doctor():
        flash('无权访问', 'error')
        return redirect(url_for('auth.dashboard'))

    today = date.today()
    today_appts = Appointment.query.filter_by(doctor_id=current_user.id,
        appointment_date=today, status='confirmed').count()
    pending = Appointment.query.filter_by(doctor_id=current_user.id,
        status='pending').count()
    completed = Consultation.query.filter_by(doctor_id=current_user.id,
        status='completed').count()
    recent_appts = Appointment.query.filter_by(doctor_id=current_user.id)\
        .filter(Appointment.status.in_(['pending', 'confirmed']))\
        .order_by(Appointment.appointment_date.asc()).limit(8).all()

    return render_template('doctor/dashboard.html',
        today_appts=today_appts, pending=pending, completed=completed,
        recent_appts=recent_appts)

@doctor_bp.route('/appointments')
@login_required
def appointments():
    if not current_user.is_doctor():
        return redirect(url_for('auth.dashboard'))

    status = request.args.get('status', '')
    query = Appointment.query.filter_by(doctor_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    appts = query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('doctor/appointments.html', appointments=appts, filter_status=status)

@doctor_bp.route('/confirm/<int:appt_id>', methods=['POST'])
@login_required
def confirm(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403
    appt.status = 'confirmed'
    db.session.commit()
    flash('预约已确认', 'success')
    return redirect(url_for('doctor.appointments'))

@doctor_bp.route('/reject/<int:appt_id>', methods=['POST'])
@login_required
def reject(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403
    reason = request.form.get('reason', '医生拒绝')
    appt.status = 'cancelled'
    appt.cancel_reason = reason
    db.session.commit()
    flash('已拒绝预约', 'info')
    return redirect(url_for('doctor.appointments'))

@doctor_bp.route('/consult/<int:appt_id>')
@login_required
def consult(appt_id):
    if not current_user.is_doctor():
        return redirect(url_for('auth.dashboard'))

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        flash('无权访问', 'error')
        return redirect(url_for('doctor.appointments'))

    consult = Consultation.query.filter_by(appointment_id=appt_id).first()
    if not consult:
        consult = Consultation(
            appointment_id=appt_id,
            patient_id=appt.patient_id,
            doctor_id=current_user.id,
            status='ongoing'
        )
        db.session.add(consult)
        appt.status = 'confirmed'
        db.session.commit()

    messages = ConsultationMessage.query.filter_by(consultation_id=consult.id)\
        .order_by(ConsultationMessage.created_at.asc()).all()
    prescriptions = Prescription.query.filter_by(consultation_id=consult.id).all()
    medicines = Medicine.query.order_by(Medicine.name).all()

    return render_template('doctor/consult.html',
        consultation=consult, messages=messages,
        prescriptions=prescriptions, appointment=appt, medicines=medicines)

@doctor_bp.route('/send_message/<int:consult_id>', methods=['POST'])
@login_required
def send_message(consult_id):
    consult = Consultation.query.get_or_404(consult_id)
    if consult.doctor_id != current_user.id:
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

@doctor_bp.route('/diagnose/<int:consult_id>', methods=['POST'])
@login_required
def diagnose(consult_id):
    consult = Consultation.query.get_or_404(consult_id)
    if consult.doctor_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403

    consult.chief_complaint = request.form.get('chief_complaint', '').strip()
    consult.present_illness = request.form.get('present_illness', '').strip()
    consult.physical_exam = request.form.get('physical_exam', '').strip()
    consult.vital_signs = request.form.get('vital_signs', '').strip()
    consult.diagnosis = request.form.get('diagnosis', '').strip()
    consult.advice = request.form.get('advice', '').strip()
    consult.status = 'completed'
    consult.completed_at = datetime.utcnow()

    appt = Appointment.query.get(consult.appointment_id)
    if appt:
        appt.status = 'completed'

    # 自动生成账单
    bill = Bill.query.filter_by(consultation_id=consult_id).first()
    if not bill:
        bill = Bill(patient_id=consult.patient_id, consultation_id=consult_id, total_amount=0, status='unpaid')
        db.session.add(bill)
        db.session.flush()
        # 诊查费
        fee = current_user.consultation_fee or 0
        if fee > 0:
            db.session.add(BillItem(bill_id=bill.id, item_type='consultation_fee',
                           item_name='诊查费', quantity=1, unit_price=fee, subtotal=fee))
            bill.total_amount += fee
        # 处方费用
        from models import Prescription as PrescriptionModel
        for p in PrescriptionModel.query.filter_by(consultation_id=consult_id).all():
            if p.status == 'prescribed':
                db.session.add(BillItem(bill_id=bill.id, item_type='medicine',
                               item_name=p.medicine_name, quantity=p.quantity,
                               unit_price=p.price / p.quantity if p.quantity else p.price,
                               subtotal=p.price))
                bill.total_amount += p.price

    db.session.commit()
    flash('诊断完成，账单已生成', 'success')
    return redirect(url_for('doctor.consult', appt_id=consult.appointment_id))

@doctor_bp.route('/prescribe/<int:consult_id>', methods=['POST'])
@login_required
def prescribe(consult_id):
    consult = Consultation.query.get_or_404(consult_id)
    if consult.doctor_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403

    medicine_id = request.form.get('medicine_id', type=int)
    dosage = request.form.get('dosage', '').strip()
    quantity = request.form.get('quantity', type=int, default=1)
    notes = request.form.get('notes', '').strip()

    if medicine_id:
        med = Medicine.query.get(medicine_id)
        if med:
            p = Prescription(
                consultation_id=consult_id,
                patient_id=consult.patient_id,
                doctor_id=current_user.id,
                medicine_name=med.name,
                specification=med.specification,
                dosage=dosage,
                quantity=quantity,
                price=med.price * quantity,
                notes=notes
            )
            db.session.add(p)
            db.session.commit()
            flash('处方已添加', 'success')
    return redirect(url_for('doctor.consult', appt_id=consult.appointment_id))

@doctor_bp.route('/history')
@login_required
def history():
    if not current_user.is_doctor():
        return redirect(url_for('auth.dashboard'))
    consultations = Consultation.query.filter_by(doctor_id=current_user.id)\
        .order_by(Consultation.created_at.desc()).all()
    return render_template('doctor/history.html', consultations=consultations)

# ─── 排队叫号 ─────────────────────────────────
@doctor_bp.route('/queue')
@login_required
def queue():
    if not current_user.is_doctor():
        return redirect(url_for('auth.dashboard'))
    today = date.today()
    queue_list = Appointment.query.filter_by(doctor_id=current_user.id,
        appointment_date=today, status='confirmed')\
        .order_by(Appointment.queue_number.asc()).all()
    current_idx = request.args.get('current', type=int, default=0)
    return render_template('doctor/queue.html', queue_list=queue_list, current_idx=current_idx)

@doctor_bp.route('/call_next/<int:appt_id>', methods=['POST'])
@login_required
def call_next(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        return jsonify({'error': '无权操作'}), 403
    return jsonify({'ok': True, 'patient_name': appt.patient.name, 'queue_number': appt.queue_number})

# ─── 药房发药 ─────────────────────────────────
@doctor_bp.route('/dispense/<int:prescription_id>', methods=['POST'])
@login_required
def dispense(prescription_id):
    p = Prescription.query.get_or_404(prescription_id)
    if p.doctor_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': '无权操作'}), 403
    if p.status == 'dispensed':
        flash('该处方已发药', 'info')
        return redirect(request.referrer or url_for('doctor.history'))
    # 扣库存
    med = Medicine.query.filter_by(name=p.medicine_name).first()
    if med:
        if med.stock < p.quantity:
            flash(f'{med.name} 库存不足（当前库存: {med.stock}）', 'error')
            return redirect(request.referrer or url_for('doctor.history'))
        med.stock -= p.quantity
    p.status = 'dispensed'
    p.dispensed_at = datetime.utcnow()
    db.session.commit()
    flash(f'{p.medicine_name} 发药成功', 'success')
    return redirect(request.referrer or url_for('doctor.history'))
