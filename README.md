# 医联通 SmartMed — 在线医疗问诊系统

软件工程专业毕业设计作品。

## 功能特色

### 三角色系统
- **患者端**：科室医生浏览、在线预约挂号、图文问诊、病历处方查看
- **医生端**：预约管理（确认/拒绝）、在线接诊、开具诊断和处方、历史记录
- **管理员端**：科室/医生/患者/药品/公告 CRUD 管理、Chart.js 数据可视化看板

### 技术栈
- 后端：Python Flask + SQLAlchemy + Flask-Login
- 数据库：SQLite（开发）/ 可切换 MySQL
- 前端：Jinja2 模板 + 原生 HTML/CSS/JS + Chart.js

## 快速开始

```bash
cd /Users/ruoainengpingshanhe/wechat_profile_mini/py

# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库 + 演示数据
python seed.py

# 3. 启动服务
python app.py
# 访问 http://localhost:5000
```

## 测试账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 患者 | 13800000001 | 123456 |
| 医生 | 13800000002 | 123456 |
| 管理员 | admin | admin123 |

## 数据库表结构

| 表名 | 说明 |
|------|------|
| departments | 科室表 |
| users | 用户表（患者/医生/管理员统一） |
| schedules | 医生排班表 |
| appointments | 预约表 |
| consultations | 问诊记录表 |
| consultation_messages | 问诊消息表 |
| prescriptions | 处方表 |
| medicines | 药品库表 |
| announcements | 公告表 |

## 项目结构

```
py/
├── app.py              # Flask 应用入口
├── config.py           # 配置
├── models.py           # SQLAlchemy 数据模型
├── seed.py             # 初始数据填充
├── routes/             # 路由蓝图
│   ├── auth.py         # 认证
│   ├── patient.py      # 患者端
│   ├── doctor.py       # 医生端
│   └── admin.py        # 管理员端
├── templates/          # Jinja2 模板
└── static/             # CSS/JS 资源
```

## License
MIT — 仅供学习和毕业答辩使用
