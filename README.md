# 🎬 电影数据可视化系统

一个功能完善的电影管理和展示系统，包含用户管理、电影管理、公告发布、密码重置等功能。

## 📋 功能特性

### 用户功能
- ✅ 用户注册和登录
- ✅ 个人信息管理（头像上传、资料修改）
- ✅ 电影浏览和搜索
- ✅ 电影收藏功能
- ✅ 查看系统公告
- ✅ 忘记密码申请

### 管理员功能
- ✅ 管理员专属登录入口
- ✅ 电影管理（添加、删除电影）
- ✅ 公告管理（发布、编辑、删除公告）
- ✅ 密码重置请求处理
- ✅ 系统数据统计

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd cinema
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置数据库**

编辑 `database.py` 文件，修改数据库连接信息：
```python
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'cinema_database'
```

5. **创建数据库**
```sql
CREATE DATABASE cinema_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **导入数据表**

执行以下SQL文件创建必要的数据表：
```bash
# 在MySQL中执行
mysql -u root -p cinema_database < create_password_reset_table.sql
mysql -u root -p cinema_database < create_announcements_table.sql
```

或者手动执行SQL：

**密码重置请求表：**
```sql
CREATE TABLE IF NOT EXISTS password_reset_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    reason TEXT,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**公告表：**
```sql
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type ENUM('normal', 'important', 'event') DEFAULT 'normal',
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**用户表（如果不存在）：**
```sql
CREATE TABLE IF NOT EXISTS userinfo (
    iduserinfo INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    sex VARCHAR(10),
    age INT,
    avatar VARCHAR(255),
    is_admin TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**电影数据表（如果不存在）：**
```sql
CREATE TABLE IF NOT EXISTS movie_data (
    idmovie_data INT AUTO_INCREMENT PRIMARY KEY,
    movie_id VARCHAR(50) NOT NULL,
    movie_title VARCHAR(200) NOT NULL,
    movie_publicdate VARCHAR(50),
    movie_score VARCHAR(10),
    movie_img TEXT,
    movie_actor TEXT,
    movie_region VARCHAR(100),
    movie_type VARCHAR(100),
    movie_comment TEXT,
    movie_com_count VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**收藏表（如果不存在）：**
```sql
CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES userinfo(iduserinfo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

7. **创建管理员账号**
```sql
INSERT INTO userinfo (username, password, email, is_admin) 
VALUES ('admin', 'admin123', 'admin@example.com', 1);
```

8. **运行项目**
```bash
python app.py
```

9. **访问系统**
- 用户端：http://localhost:5000/Homepage
- 用户登录：http://localhost:5000/login
- 管理员登录：http://localhost:5000/admin/login

## 📦 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.0 | Web框架 |
| Werkzeug | 3.0.1 | WSGI工具库 |
| PyMySQL | 1.1.0 | MySQL数据库连接 |
| pandas | 2.1.4 | 数据处理 |
| numpy | 1.26.2 | 数值计算 |
| requests | 2.31.0 | HTTP请求 |
| urllib3 | 2.1.0 | HTTP客户端 |
| cryptography | 41.0.7 | 加密支持 |
| Flask-Session | 0.5.0 | 会话管理（可选）|

## 🗂️ 项目结构

```
cinema/
├── app.py                          # 应用入口
├── database.py                     # 数据库配置
├── config.py                       # 配置文件
├── requirements.txt                # 依赖包列表
├── README.md                       # 项目说明
├── create_password_reset_table.sql # 密码重置表SQL
├── create_announcements_table.sql  # 公告表SQL
├── cinema_page/                    # 应用包
│   ├── __init__.py
│   ├── views/
│   │   └── create.py              # 路由和视图
│   ├── templates/                 # HTML模板
│   │   ├── base.html
│   │   ├── Homepage.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── movie_management.html
│   │   ├── announcement_management.html
│   │   ├── password_requests.html
│   │   └── ...
│   └── static/                    # 静态文件
│       └── img/
└── data/                          # 数据文件
```

## 🔐 默认账号

### 管理员账号
- 用户名：admin
- 密码：admin123

### 测试用户账号
请自行注册或在数据库中创建

## 📝 使用说明

### 用户端操作
1. 注册账号或使用已有账号登录
2. 浏览首页查看系统公告和推荐电影
3. 进入电影大厅搜索和浏览电影
4. 点击电影查看详情并收藏
5. 在个人中心修改资料和头像
6. 如忘记密码，点击"忘记密码"提交重置请求

### 管理员操作
1. 从管理员入口登录（/admin/login）
2. 点击顶部"管理员面板"按钮进入后台
3. 在后台可以：
   - 管理电影（添加/删除）
   - 发布公告（普通/重要/活动）
   - 处理密码重置请求
   - 查看系统统计数据

## 🛠️ 开发说明

### 添加新功能
1. 在 `cinema_page/views/create.py` 中添加路由
2. 在 `cinema_page/templates/` 中创建模板
3. 如需数据库表，创建对应的SQL文件

### 修改样式
- 全局样式在 `base.html` 中
- 页面特定样式在各自的模板文件中

## ⚠️ 注意事项

1. **安全性**：
   - 生产环境请修改默认管理员密码
   - 建议使用密码加密（如bcrypt）
   - 配置HTTPS

2. **数据库**：
   - 定期备份数据库
   - 注意SQL注入防护

3. **文件上传**：
   - 限制上传文件大小
   - 验证文件类型

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请联系：[your-email@example.com]