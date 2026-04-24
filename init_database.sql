-- ============================================
-- 电影数据可视化系统 - 数据库初始化脚本
-- ============================================
-- 使用方法：mysql -u root -p cinema_database < init_database.sql
-- ============================================

-- 1. 用户信息表
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

-- 2. 电影数据表
CREATE TABLE IF NOT EXISTS movie_data (
    idmovie_data INT AUTO_INCREMENT PRIMARY KEY COMMENT '电影数据ID',
    movie_id VARCHAR(50) NOT NULL COMMENT '电影ID（豆瓣ID等）',
    movie_title VARCHAR(200) NOT NULL COMMENT '电影标题',
    movie_publicdate VARCHAR(50) COMMENT '上映日期',
    movie_score VARCHAR(10) COMMENT '电影评分',
    movie_img TEXT COMMENT '电影封面图片URL',
    movie_actor TEXT COMMENT '主演列表',
    movie_region VARCHAR(100) COMMENT '制片地区',
    movie_type VARCHAR(100) COMMENT '电影类型',
    movie_comment TEXT COMMENT '剧情简介',
    movie_com_count VARCHAR(50) COMMENT '评论数量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_movie_id (movie_id),
    INDEX idx_movie_title (movie_title),
    INDEX idx_movie_region (movie_region),
    INDEX idx_movie_type (movie_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电影数据表';

-- 3. 用户收藏表
CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    movie_id VARCHAR(50) NOT NULL COMMENT '电影ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    INDEX idx_user_id (user_id),
    INDEX idx_movie_id (movie_id),
    UNIQUE KEY unique_user_movie (user_id, movie_id) COMMENT '防止重复收藏',
    CONSTRAINT fk_collections_user 
        FOREIGN KEY (user_id) 
        REFERENCES userinfo(iduserinfo) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

-- 4. 密码重置请求表
CREATE TABLE IF NOT EXISTS password_reset_requests (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '请求ID',
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    reason TEXT COMMENT '请求原因',
    status ENUM('pending', 'completed') DEFAULT 'pending' COMMENT '状态：pending-待处理 completed-已处理',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='密码重置请求表';

-- 5. 系统公告表
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '公告ID',
    title VARCHAR(200) NOT NULL COMMENT '公告标题',
    type ENUM('normal', 'important', 'event') DEFAULT 'normal' COMMENT '公告类型：normal-普通 important-重要 event-活动',
    content TEXT NOT NULL COMMENT '公告内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_created_at (created_at),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统公告表';

-- ============================================
-- 插入初始数据
-- ============================================

-- 插入默认管理员账号
INSERT INTO userinfo (username, password, email, is_admin) 
VALUES ('admin', 'admin123', 'admin@example.com', 1)
ON DUPLICATE KEY UPDATE username=username;

-- 插入示例公告
INSERT INTO announcements (title, type, content) VALUES
('欢迎使用电影数据可视化系统', 'important', '欢迎来到电影数据可视化系统！在这里您可以浏览海量电影信息，收藏喜欢的电影，查看详细的电影数据分析。'),
('系统功能介绍', 'normal', '本系统提供电影浏览、搜索、收藏、个人信息管理等功能。管理员可以管理电影数据和系统公告。'),
('新功能上线', 'event', '系统新增公告功能和密码重置功能，为您提供更好的使用体验！')
ON DUPLICATE KEY UPDATE title=title;

-- ============================================
-- 数据库初始化完成
-- ============================================
-- 提示：
-- 1. 默认管理员账号：admin / admin123
-- 2. 请及时修改默认密码
-- 3. 建议定期备份数据库
-- ============================================


