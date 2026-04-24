-- 电影数据表
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

-- Made with Bob
