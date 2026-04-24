-- 用户信息表
CREATE TABLE IF NOT EXISTS userinfo (
    iduserinfo INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    sex VARCHAR(10) COMMENT '性别',
    age INT COMMENT '年龄',
    avatar VARCHAR(255) DEFAULT '/static/img/user_default.png' COMMENT '头像路径',
    is_admin TINYINT(1) DEFAULT 0 COMMENT '是否为管理员 0-普通用户 1-管理员',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_is_admin (is_admin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- 插入默认管理员账号
INSERT INTO userinfo (username, password, email, is_admin) 
VALUES ('admin', 'admin123', 'admin@example.com', 1)
ON DUPLICATE KEY UPDATE username=username;

-- Made with Bob
