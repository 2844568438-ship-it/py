from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from urllib.request import urlopen, Request

auth_bp = Blueprint('auth', __name__)

# 图片代理——中转Wikipedia真实医生照片
WIKI_IMAGES = {
    '钟南山': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zhong_Nanshan_2020.jpg',
    '王辰': 'https://commons.wikimedia.org/wiki/Special:FilePath/Wang_Chen_2020.jpg',
    '李兰娟': 'https://commons.wikimedia.org/wiki/Special:FilePath/Li_Lanjuan_at_the_2020_CPPCC.jpg',
    '张文宏': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zhang_Wenhong.jpg',
    '葛均波': 'https://commons.wikimedia.org/wiki/Special:FilePath/Ge_Junbo.jpg',
    '宁光': 'https://commons.wikimedia.org/wiki/Special:FilePath/Ning_Guang.jpg',
    '吴孟超': 'https://commons.wikimedia.org/wiki/Special:FilePath/Wu_Mengchao.jpg',
    '郑树森': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zheng_Shusen.jpg',
    '赵继宗': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zhao_Jizong.jpg',
    '郎景和': 'https://commons.wikimedia.org/wiki/Special:FilePath/Lang_Jinghe.jpg',
    '乔杰': 'https://commons.wikimedia.org/wiki/Special:FilePath/Qiao_Jie_2020.jpg',
    '韩德民': 'https://commons.wikimedia.org/wiki/Special:FilePath/Han_Demin.jpg',
    '张志愿': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zhang_Zhiyuan.jpg',
    '樊代明': 'https://commons.wikimedia.org/wiki/Special:FilePath/Fan_Daiming.jpg',
    '李兆申': 'https://commons.wikimedia.org/wiki/Special:FilePath/Li_Zhaoshen.jpg',
    '高润霖': 'https://commons.wikimedia.org/wiki/Special:FilePath/Gao_Runlin.jpg',
    '胡盛寿': 'https://commons.wikimedia.org/wiki/Special:FilePath/Hu_Shengshou.jpg',
    '陈孝平': 'https://commons.wikimedia.org/wiki/Special:FilePath/Chen_Xiaoping.jpg',
    '周良辅': 'https://commons.wikimedia.org/wiki/Special:FilePath/Zhou_Liangfu.jpg',
    '邱贵兴': 'https://commons.wikimedia.org/wiki/Special:FilePath/Qiu_Guixing.jpg',
    '马丁': 'https://commons.wikimedia.org/wiki/Special:FilePath/Ma_Ding_2019.jpg',
    '陈香美': 'https://commons.wikimedia.org/wiki/Special:FilePath/Chen_Xiangmei.jpg',
}

@auth_bp.route('/proxy_img/<name>')
def proxy_img(name):
    url = WIKI_IMAGES.get(name)
    if not url:
        return '', 404
    try:
        rq = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urlopen(rq, timeout=15)
        return Response(r.read(), mimetype=r.headers.get('Content-Type','image/jpeg'))
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
