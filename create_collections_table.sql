-- 用户收藏表
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

-- Made with Bob
