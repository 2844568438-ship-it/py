from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import requests as req

auth_bp = Blueprint('auth', __name__)

# 图片代理——中转Wikipedia真实医生照片
WIKI_IMAGES = {
    '钟南山': 'https://upload.wikimedia.org/wikipedia/commons/9/9d/Zhong_Nanshan_2020.jpg',
    '李兰娟': 'https://upload.wikimedia.org/wikipedia/commons/5/5f/Li_Lanjuan_at_the_2020_CPPCC.jpg',
    '张文宏': 'https://upload.wikimedia.org/wikipedia/commons/4/4f/Zhang_Wenhong.jpg',
}

@auth_bp.route('/proxy_img/<name>')
def proxy_img(name):
    url = WIKI_IMAGES.get(name)
    if not url:
        return '', 404
    try:
        r = req.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        return Response(r.content, mimetype=r.headers.get('content-type','image/jpeg'))
    except:
        return '', 502

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(phone=phone).first()
        if user and user.check_password(password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('auth.dashboard'))
        flash('手机号或密码错误', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        gender = request.form.get('gender', '')
        age = request.form.get('age', type=int, default=0)

        if User.query.filter_by(phone=phone).first():
            flash('该手机号已注册', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('密码至少6位', 'error')
            return render_template('register.html')

        user = User(name=name, phone=phone, role='patient', gender=gender, age=age)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return render_template('index.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_doctor():
        return redirect(url_for('doctor.dashboard'))
    else:
        return redirect(url_for('patient.dashboard'))
