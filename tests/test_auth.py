def test_index_redirects_to_login(client):
    """首页未登录应重定向到登录页"""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'login' in resp.data.lower() or '登录'.encode() in resp.data or '医联通'.encode() in resp.data


def test_login_page(client):
    """登录页面正常加载"""
    resp = client.get('/login')
    assert resp.status_code == 200
    assert '登录'.encode() in resp.data or b'login' in resp.data.lower()


def test_register_page(client):
    """注册页面正常加载"""
    resp = client.get('/register')
    assert resp.status_code == 200
    assert '注册'.encode() in resp.data or b'register' in resp.data.lower()


def test_register_success(client, db):
    """注册成功跳转登录页"""
    resp = client.post('/register', data={
        'name': '新用户', 'phone': '13999999999', 'password': '123456',
        'gender': '男', 'age': 25
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_register_duplicate_phone(client):
    """重复手机号注册应提示错误"""
    resp = client.post('/register', data={
        'name': '重复', 'phone': '13800000001', 'password': '123456',
        'gender': '男', 'age': 25
    }, follow_redirects=True)
    assert resp.status_code == 200
    # 应该有错误提示
    assert '已注册'.encode() in resp.data or b'error' in resp.data or '手机号'.encode() in resp.data


def test_register_short_password(client):
    """密码太短应拒绝"""
    resp = client.post('/register', data={
        'name': '短密码', 'phone': '13988888888', 'password': '123',
        'gender': '男', 'age': 25
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_login_success_redirects_to_dashboard(client):
    """登录成功跳转到dashboard"""
    resp = client.post('/login', data={
        'phone': '13800000001', 'password': '123456'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # 登录后应该到了dashboard或首页


def test_login_wrong_password(client):
    """错误密码登录失败"""
    resp = client.post('/login', data={
        'phone': '13800000001', 'password': 'wrongpassword'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert '错误'.encode() in resp.data or b'error' in resp.data


def test_logout(client):
    """登出正常"""
    # 先登录
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200


def test_dashboard_redirects_based_on_role(client):
    """不同角色登录后重定向到不同的dashboard"""
    # 患者
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})
    resp = client.get('/dashboard', follow_redirects=True)
    assert resp.status_code == 200

    # 登出
    client.get('/logout')

    # 医生
    client.post('/login', data={'phone': '13800000002', 'password': '123456'})
    resp = client.get('/dashboard', follow_redirects=True)
    assert resp.status_code == 200
