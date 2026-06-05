def test_patient_bills_page(client):
    """患者账单页"""
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})
    resp = client.get('/patient/bills')
    assert resp.status_code == 200


def test_patient_profile_page(client):
    """患者健康档案页"""
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})
    resp = client.get('/patient/profile')
    assert resp.status_code == 200
    # 提交更新
    resp = client.post('/patient/profile', data={
        'blood_type': 'A', 'height': 175, 'weight': 70,
        'smoking': 'never', 'alcohol': 'occasional',
        'allergies': '青霉素,花粉', 'chronic_diseases': '无',
        'family_history': '父亲高血压'
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_admin_dashboard(client):
    """管理员看板"""
    client.post('/login', data={'phone': 'admin', 'password': 'admin123'})
    resp = client.get('/admin/dashboard')
    assert resp.status_code == 200


def test_admin_bills_page(client):
    """管理员账单管理"""
    client.post('/login', data={'phone': 'admin', 'password': 'admin123'})
    resp = client.get('/admin/bills')
    assert resp.status_code == 200


def test_admin_pharmacy_page(client):
    """管理员发药管理"""
    client.post('/login', data={'phone': 'admin', 'password': 'admin123'})
    resp = client.get('/admin/pharmacy')
    assert resp.status_code == 200


def test_doctor_queue_page(client):
    """医生排队叫号页"""
    client.post('/login', data={'phone': '13800000002', 'password': '123456'})
    resp = client.get('/doctor/queue')
    assert resp.status_code == 200


def test_articles_page(client):
    """健康科普页"""
    client.post('/login', data={'phone': '13800000001', 'password': '123456'})
    resp = client.get('/patient/articles')
    assert resp.status_code == 200


def test_unauthenticated_redirect(client):
    """未登录访问受保护页面应重定向"""
    resp = client.get('/patient/dashboard', follow_redirects=True)
    assert resp.status_code == 200
    # 应该被重定向到登录页或首页
    assert '登录'.encode() in resp.data or 'login'.encode() in resp.data.lower() or '医联通'.encode() in resp.data
