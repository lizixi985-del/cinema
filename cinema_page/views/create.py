from flask import Blueprint,render_template,request, jsonify,flash,redirect,url_for,session,Response,current_app
import database
import requests
import pandas as pd
import database
from werkzeug.utils import secure_filename
import os
import re


cr =Blueprint("create",__name__)

DEFAULT_AVATAR = '/static/img/user_default.png'

def get_current_user_avatar():
    """获取当前登录用户头像，未登录或无头像时返回默认头像"""
    uid = session.get('uid')
    if not uid:
        return DEFAULT_AVATAR

    try:
        sql = "SELECT avatar FROM userinfo WHERE iduserinfo = %s"
        result = database.query(sql, [uid])
        if result and result[0] and result[0][0]:
            return result[0][0]
    except Exception:
        pass

    return DEFAULT_AVATAR

def login_required(f):
    """登录校验装饰器，保护需要登录的路由"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uid' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('create.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员校验装饰器，保护管理员路由"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'uid' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('create.admin_login'))
        if not session.get('is_admin'):
            flash('无管理员权限', 'error')
            return redirect(url_for('create.Homepage'))
        return f(*args, **kwargs)
    return decorated_function

@cr.route('/proxy/douban-image')
def proxy_douban_image():
    # 获取前端传的图片URL
    img_url = request.args.get('url')
    if not img_url or 'doubanio.com' not in img_url:
        return Response(status=400, response="Invalid URL")
    
    # 模拟浏览器请求头，完美绕过豆瓣反爬和防盗链
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://movie.douban.com/',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        # 由后端代替浏览器请求豆瓣图片
        resp = requests.get(img_url, headers=headers, stream=True, timeout=10)
        # 原样返回图片资源给前端
        return Response(
            resp.iter_content(chunk_size=1024),
            content_type=resp.headers.get('Content-Type', 'image/jpeg'),
            status=resp.status_code
        )
    except Exception as e:
        # 兜底：返回占位图
        placeholder = requests.get('https://picsum.photos/400/600?grayscale', headers=headers)
        return Response(placeholder.content, content_type='image/jpeg')

@cr.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        sql = f"SELECT iduserinfo, is_admin FROM userinfo WHERE username = '{username}' AND password = '{password}'"
        RESULT= database.query(sql)
        print(RESULT)
        if RESULT:
            session['uid'] = RESULT[0][0]
            session['is_admin'] = bool(RESULT[0][1]) if len(RESULT[0]) > 1 else False
            flash('登录成功', 'success')
            return redirect(url_for('create.Homepage'))
            # return jsonify({'code':200,'msg':'登录成功'})
        else:
            return jsonify({'code':500,'msg':'登录失败:请确认用户名存在或者密码正确'})
    return render_template("login.html")
@cr.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        sql = f"SELECT iduserinfo, is_admin FROM userinfo WHERE username = '{username}' AND password = '{password}'"
        RESULT = database.query(sql)
        print(RESULT)
        if RESULT:
            if len(RESULT[0]) > 1 and RESULT[0][1] == 1:
                session['uid'] = RESULT[0][0]
                session['is_admin'] = True
                flash('管理员登录成功', 'success')
                return redirect(url_for('create.admin_dashboard'))
            return jsonify({'code':403,'msg':'当前账号不是管理员，无法从管理员入口登录'})
        else:
            return jsonify({'code':500,'msg':'管理员登录失败:请确认用户名存在或者密码正确'})
    return render_template("admin_login.html")

@cr.route('/Register',methods=["GET","POST"])
def Register():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        sex = request.form.get('gender')
        age = request.form.get('age')
        email= request.form.get('email')
        avatar = DEFAULT_AVATAR
        sql = f"select username from userinfo where username='{username}'"
        RESULT= database.query(sql)
        if RESULT:
            flash('用户名已经存在', 'error')
        else:
            sql = f"insert into userinfo(username,password,sex,age,avatar,email,is_admin) values ('{username}','{password}','{sex}','{age}','{avatar}','{email}',0)"
            database.insert(sql)
            flash('注册成功', 'success')
            return redirect(url_for('create.login'))  # or render_template
        return redirect(url_for('register'))  # Redirect to show flash message
    return render_template("register.html")
    #     if RESULT:
    #         return jsonify({'code':502,'msg':'用户名已经存在'})
    #     else:
    #         sql = f"insert into userinfo(username,password,sex,age,avatar,email) values ('{username}','{password}','{sex}','{age}','{avatar}','{email}')"
    #         database.insert(sql)
    #         return jsonify({'code':200,'msg':'注册成功' })
    # return render_template("register.html")

@cr.route('/admin/dashboard', methods=["GET"])
@login_required
@admin_required
def admin_dashboard():
    user_count = database.query("SELECT COUNT(*) FROM userinfo")[0][0]
    movie_count = database.query("SELECT COUNT(*) FROM movie_data")[0][0]
    collection_count = database.query("SELECT COUNT(*) FROM collections")[0][0]
    admin_count = database.query("SELECT COUNT(*) FROM userinfo WHERE is_admin = 1")[0][0]

    return render_template(
        "admin_dashboard.html",
        avatar=get_current_user_avatar(),
        user_count=user_count,
        movie_count=movie_count,
        collection_count=collection_count,
        admin_count=admin_count
    )

@cr.route('/admin/movie-management', methods=["GET"])
@login_required
@admin_required
def movie_management():
    """电影管理页面"""
    page = int(request.args.get('page', 1))
    items_per_page = 10
    offset = (page - 1) * items_per_page

    count_sql = "SELECT COUNT(DISTINCT movie_title) FROM movie_data"
    total_items = database.query(count_sql)[0][0]
    total_pages = (total_items + items_per_page - 1) // items_per_page if total_items else 1

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * items_per_page

    sql = f"""
    SELECT m.* FROM movie_data m
    INNER JOIN (
        SELECT MIN(movie_id) as min_id
        FROM movie_data
        GROUP BY movie_title
    ) as unique_movies ON m.movie_id = unique_movies.min_id
    ORDER BY m.movie_title ASC
    LIMIT {items_per_page} OFFSET {offset}
    """
    movies = database.query(sql)

    prev_page = page - 1 if page > 1 else 1
    next_page = page + 1 if page < total_pages else total_pages

    return render_template(
        "movie_management.html",
        avatar=get_current_user_avatar(),
        movies=movies,
        current_page=page,
        total_pages=total_pages,
        prev_page=prev_page,
        next_page=next_page,
        total_items=total_items
    )

@cr.route('/admin/add-movie', methods=["POST"])
@login_required
@admin_required
def add_movie():
    """添加新电影"""
    movie_id = request.form.get('movie_id', '').strip()
    movie_title = request.form.get('movie_title', '').strip()
    movie_publicdate = request.form.get('movie_publicdate', '').strip()
    movie_score = request.form.get('movie_score', '').strip()
    movie_img = request.form.get('movie_img', '').strip()
    movie_actor = request.form.get('movie_actor', '').strip()
    movie_region = request.form.get('movie_region', '').strip()
    movie_type = request.form.get('movie_type', '').strip()
    movie_comment = request.form.get('movie_comment', '').strip()
    movie_com_count = request.form.get('movie_com_count', '').strip()
    
    # 验证必填字段
    if not movie_id or not movie_title:
        flash('电影ID和电影名称为必填项', 'error')
        return redirect(url_for('create.movie_management'))
    
    # 检查电影ID是否已存在
    check_sql = "SELECT movie_id FROM movie_data WHERE movie_id = %s"
    existing = database.query(check_sql, [movie_id])
    if existing:
        flash(f'电影ID {movie_id} 已存在，请使用其他ID', 'error')
        return redirect(url_for('create.movie_management'))
    
    # 插入新电影
    insert_sql = """
    INSERT INTO movie_data 
    (movie_id, movie_title, movie_publicdate, movie_score, movie_img, 
     movie_actor, movie_region, movie_type, movie_comment, movie_com_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        # 使用参数化查询防止SQL注入
        con, cur = database.coon()
        cur.execute(insert_sql, (
            movie_id, movie_title, movie_publicdate or None, 
            movie_score or None, movie_img or None,
            movie_actor or None, movie_region or None, 
            movie_type or None, movie_comment or None, 
            movie_com_count or None
        ))
        con.commit()
        cur.close()
        con.close()
        flash(f'电影《{movie_title}》添加成功！', 'success')
    except Exception as e:
        flash(f'添加失败：{str(e)}', 'error')
    
    return redirect(url_for('create.movie_management', page=request.args.get('page', 1)))

@cr.route('/admin/delete-movie/<string:movie_id>', methods=["POST"])
@login_required
@admin_required
def delete_movie(movie_id):
    """删除电影"""
    # 先查询电影名称用于提示
    movie_sql = "SELECT movie_title FROM movie_data WHERE movie_id = %s LIMIT 1"
    movie_info = database.query(movie_sql, [movie_id])
    
    if not movie_info:
        flash('电影不存在', 'error')
        return redirect(url_for('create.movie_management'))
    
    movie_title = movie_info[0][0]
    
    # 删除电影（删除所有相同movie_id的记录）
    delete_sql = f"DELETE FROM movie_data WHERE movie_id = '{movie_id}'"
    affected_rows = database.delete(delete_sql)
    
    if affected_rows > 0:
        # 同时删除相关收藏记录
        delete_collection_sql = f"DELETE FROM collections WHERE movie_id = '{movie_id}'"
        database.delete(delete_collection_sql)
        flash(f'电影《{movie_title}》已删除', 'success')
    else:
        flash('删除失败', 'error')
    
    current_page = request.args.get('page', 1)
    return redirect(url_for('create.movie_management', page=current_page))

    


@cr.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
    """忘记密码请求页面"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        reason = request.form.get('reason', '').strip()
        
        # 验证用户名和邮箱是否匹配
        check_sql = "SELECT iduserinfo FROM userinfo WHERE username = %s AND email = %s"
        user_result = database.query(check_sql, [username, email])
        
        if not user_result:
            flash('用户名或邮箱不正确，请检查后重试', 'error')
            return redirect(url_for('create.forgot_password'))
        
        # 检查是否已有待处理的请求
        pending_sql = "SELECT id FROM password_reset_requests WHERE username = %s AND status = 'pending'"
        pending_result = database.query(pending_sql, [username])
        
        if pending_result:
            flash('您已有待处理的密码重置请求，请耐心等待管理员处理', 'warning')
            return redirect(url_for('create.login'))
        
        # 插入密码重置请求
        insert_sql = """
        INSERT INTO password_reset_requests (username, email, reason, status, created_at)
        VALUES (%s, %s, %s, 'pending', NOW())
        """
        try:
            con, cur = database.coon()
            cur.execute(insert_sql, (username, email, reason or '未填写'))
            con.commit()
            cur.close()
            con.close()
            flash('密码重置请求已提交，请等待管理员处理', 'success')
            return redirect(url_for('create.login'))
        except Exception as e:
            flash(f'提交失败：{str(e)}', 'error')
            return redirect(url_for('create.forgot_password'))
    
    return render_template("forgot_password.html")

@cr.route('/admin/password-requests', methods=["GET"])
@login_required
@admin_required
def password_requests():
    """密码重置请求管理页面"""
    # 查询所有密码重置请求
    sql = """
    SELECT id, username, email, reason, status, created_at
    FROM password_reset_requests
    ORDER BY 
        CASE WHEN status = 'pending' THEN 0 ELSE 1 END,
        created_at DESC
    """
    requests_list = database.query(sql)
    
    # 统计待处理数量
    pending_count_sql = "SELECT COUNT(*) FROM password_reset_requests WHERE status = 'pending'"
    pending_count = database.query(pending_count_sql)[0][0]
    
    return render_template(
        "password_requests.html",
        avatar=get_current_user_avatar(),
        requests=requests_list,
        pending_count=pending_count
    )

@cr.route('/admin/reset-user-password', methods=["POST"])
@login_required
@admin_required
def reset_user_password():
    """管理员重置用户密码"""
    username = request.form.get('resetUsername')  # 从隐藏字段获取
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    request_id = request.form.get('request_id')
    
    # 验证密码
    if not new_password or not confirm_password:
        flash('密码不能为空', 'error')
        return redirect(url_for('create.password_requests'))
    
    if new_password != confirm_password:
        flash('两次输入的密码不一致', 'error')
        return redirect(url_for('create.password_requests'))
    
    # 从请求ID获取用户名
    get_username_sql = "SELECT username FROM password_reset_requests WHERE id = %s"
    username_result = database.query(get_username_sql, [request_id])
    
    if not username_result:
        flash('请求不存在', 'error')
        return redirect(url_for('create.password_requests'))
    
    username = username_result[0][0]
    
    # 更新用户密码
    update_password_sql = f"UPDATE userinfo SET password = '{new_password}' WHERE username = '{username}'"
    affected_rows = database.update(update_password_sql)
    
    if affected_rows > 0:
        # 更新请求状态为已处理
        update_request_sql = f"UPDATE password_reset_requests SET status = 'completed' WHERE id = {request_id}"
        database.update(update_request_sql)
        flash(f'用户 {username} 的密码已成功重置', 'success')
    else:
        flash('密码重置失败', 'error')
    
    return redirect(url_for('create.password_requests'))

@cr.route('/admin/delete-password-request/<int:request_id>', methods=["POST"])
@login_required
@admin_required
def delete_password_request(request_id):
    """删除密码重置请求"""
    delete_sql = f"DELETE FROM password_reset_requests WHERE id = {request_id}"
    affected_rows = database.delete(delete_sql)
    
    if affected_rows > 0:
        flash('请求已删除', 'success')
    else:
        flash('删除失败', 'error')
    
    return redirect(url_for('create.password_requests'))

@cr.route('/Homepage',methods=["GET","POST"])
def Homepage():
    df= pd.read_csv('final.csv')
    #读取电影行的数量
    total=df.shape[0]
    df['主演']= df ['主演'].str.replace(r'\s+',' ',regex=True).str.strip()
    df = df[df['主演'].notna()]
    actors_series = df['主演'].str.split(' ').explode()
    most_fre_actor = actors_series.value_counts().idxmax()
    most_fre_country = df['地区'].value_counts().idxmax()
    most_fre_type = df['类型'].value_counts().idxmax()
    all_movie = database.query("select movie_id,movie_title,movie_img,movie_score from movie_data")
    random_movie = all_movie[:8]
    
    # 查询最新的3条公告
    announcements_sql = """
    SELECT id, title, type, content, created_at
    FROM announcements
    ORDER BY created_at DESC
    LIMIT 3
    """
    announcements = database.query(announcements_sql)
    
    print(random_movie)
    return render_template("Homepage.html",
                           total=total,most_fre_actor=most_fre_actor,
                           most_fre_country=most_fre_country,most_fre_type=most_fre_type,random_movie=random_movie,
                           avatar=get_current_user_avatar(),
                           announcements=announcements)

@cr.route('/admin/announcement-management', methods=["GET"])
@login_required
@admin_required
def announcement_management():
    """公告管理页面"""
    # 查询所有公告，按创建时间倒序
    sql = """
    SELECT id, title, type, content, created_at
    FROM announcements
    ORDER BY created_at DESC
    """
    announcements = database.query(sql)
    
    return render_template(
        "announcement_management.html",
        avatar=get_current_user_avatar(),
        announcements=announcements
    )

@cr.route('/admin/add-announcement', methods=["POST"])
@login_required
@admin_required
def add_announcement():
    """添加新公告"""
    title = request.form.get('title', '').strip()
    ann_type = request.form.get('type', 'normal').strip()
    content = request.form.get('content', '').strip()
    
    if not title or not content:
        flash('标题和内容不能为空', 'error')
        return redirect(url_for('create.announcement_management'))
    
    # 插入新公告
    insert_sql = """
    INSERT INTO announcements (title, type, content, created_at)
    VALUES (%s, %s, %s, NOW())
    """
    
    try:
        con, cur = database.coon()
        cur.execute(insert_sql, (title, ann_type, content))
        con.commit()
        cur.close()
        con.close()
        flash('公告发布成功！', 'success')
    except Exception as e:
        flash(f'发布失败：{str(e)}', 'error')
    
    return redirect(url_for('create.announcement_management'))

@cr.route('/admin/edit-announcement', methods=["POST"])
@login_required
@admin_required
def edit_announcement():
    """编辑公告"""
    announcement_id = request.form.get('announcement_id')
    title = request.form.get('title', '').strip()
    ann_type = request.form.get('type', 'normal').strip()
    content = request.form.get('content', '').strip()
    
    if not announcement_id or not title or not content:
        flash('参数不完整', 'error')
        return redirect(url_for('create.announcement_management'))
    
    # 更新公告
    update_sql = f"""
    UPDATE announcements 
    SET title = '{title}', type = '{ann_type}', content = '{content}'
    WHERE id = {announcement_id}
    """
    
    affected_rows = database.update(update_sql)
    
    if affected_rows > 0:
        flash('公告更新成功！', 'success')
    else:
        flash('更新失败', 'error')
    
    return redirect(url_for('create.announcement_management'))

@cr.route('/admin/delete-announcement/<int:announcement_id>', methods=["POST"])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """删除公告"""
    delete_sql = f"DELETE FROM announcements WHERE id = {announcement_id}"
    affected_rows = database.delete(delete_sql)
    
    if affected_rows > 0:
        flash('公告已删除', 'success')
    else:
        flash('删除失败', 'error')
    
    return redirect(url_for('create.announcement_management'))

    actors_series = df['主演'].str.split(' ').explode()
    most_fre_actor = actors_series.value_counts().idxmax()
    most_fre_country = df['地区'].value_counts().idxmax()
    most_fre_type = df['类型'].value_counts().idxmax()
    all_movie = database.query("select movie_id,movie_title,movie_img,movie_score from movie_data")
    random_movie = all_movie[:8]
    
    # 查询最新的3条公告
    announcements_sql = """
    SELECT id, title, type, content, created_at
    FROM announcements
    ORDER BY created_at DESC
    LIMIT 3
    """
    announcements = database.query(announcements_sql)
    
    print(random_movie)
    return render_template("Homepage.html",
                           total=total,most_fre_actor=most_fre_actor,
                           most_fre_country=most_fre_country,most_fre_type=most_fre_type,random_movie=random_movie,
                           avatar=get_current_user_avatar(),
                           announcements=announcements)
@cr.route('/ListPage',methods=["GET","POST"])
def ListPage():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    itemsPerPage = 8

    # 基础查询：去重获取唯一电影数据
    sql = """
    select m.* from movie_data m
    inner join (
        select min(movie_id) as min_id
        from movie_data
        group by movie_title
    ) as unique_movies on m.movie_id = unique_movies.min_id
    """

    # 拼接搜索条件（带正确缩进+空格）
    if search:
        sql += f" where movie_title like '%{search}%'"  # 前面加空格

    # 拼接排序（无论是否搜索都排序，位置在搜索条件后）
    sql += " order by m.movie_title asc"  # 前面加空格

    # 构造计数 SQL
    totalItemSql = "select count(distinct movie_title) from movie_data"
    if search:
        totalItemSql += f" where movie_title like '%{search}%'"  # 前面加空格

    # 执行计数查询
    totalItems = database.query(totalItemSql)[0][0]
    offset = (page - 1) * itemsPerPage

    # 拼接分页（带空格，确保 SQL 语法正确）
    sql += f" limit {itemsPerPage} offset {offset}"  # 前面加空格
    result = database.query(sql)

    # 修正：计算总页数（必须整除向上取整）
    totalPages = (totalItems + itemsPerPage - 1) // itemsPerPage
    prev_page = page - 1 if page > 1 else 1
    next_page = page + 1 if page < totalPages else totalPages

    return render_template("ListPage.html",
                           result=result,
                           current_page=page,
                           total_pages=totalPages,
                           prev_page=prev_page,
                           next_page=next_page,
                           search=search,
                           avatar=get_current_user_avatar())
@cr.route('/MovieDetail/<string:movie_id>', methods=["GET"])
def MovieDetail(movie_id):
    """
    电影详情页接口（适配你提供的movie_data表结构）
    :param movie_id: 电影ID（从列表页传递）
    :return: 渲染详情页模板，携带电影完整信息
    """
    # 1. 精准查询当前电影的完整信息（完全匹配你的列名）
    movie_sql = """
    SELECT 
        idmovie_data,
        movie_id,
        movie_title,
        movie_publicdate,
        movie_score,
        movie_img,
        movie_actor,
        movie_region,
        movie_type,
        movie_comment,
        movie_com_count
    FROM movie_data 
    WHERE movie_id = %s
    """
    # 参数化查询，避免SQL注入
    movie_detail = database.query(movie_sql, [movie_id])
    
    # 电影不存在的异常处理
    if not movie_detail:
        flash('该电影信息不存在', 'error')
        return redirect(url_for('create.ListPage'))

    # 提取单条电影数据（元组转字典，前端直接调用）
    movie_info = {
        "id": movie_detail[0][0],
        "movie_id": movie_detail[0][1],
        "title": movie_detail[0][2],
        "publicdate": movie_detail[0][3] or '暂无',  # 上映日期（对应movie_publicdate）
        "score": movie_detail[0][4] or '暂无',
        "img": movie_detail[0][5] or '',
        "actor": movie_detail[0][6],       # 主演（对应movie_actor）
        "region": movie_detail[0][7] or '暂无',      # 地区（对应movie_region）
        "type": movie_detail[0][8],        # 类型（对应movie_type）
        "comment": movie_detail[0][9],     # 剧情简介（对应movie_comment）
        "com_count": movie_detail[0][10]    # 评论数（对应movie_com_count）
    }
    print(movie_info)
    # 2. 同类型推荐（最多6部，排除当前电影，适配你的字段）
    # 取第一个类型作为推荐维度，兼容多类型格式（如"剧情 爱情"）
    type_filter = movie_info["type"].split(" ")[0]
    recommend_sql = """
    SELECT movie_id, movie_title, movie_img, movie_score 
    FROM movie_data 
    WHERE movie_type LIKE %s AND movie_id != %s
     LIMIT 6
    """
    # 参数化查询
    recommend_movies = database.query(recommend_sql, [f"%{type_filter}%", movie_id])

    # 3. 检查用户是否已登录，以及是否已收藏该电影
    is_collected = False
    if 'uid' in session:
        uid = session['uid']
        check_sql = "SELECT id FROM collections WHERE user_id = %s AND movie_id = %s"
        check_result = database.query(check_sql, [uid, movie_id])
        if check_result:
            is_collected = True

    # 4. 渲染详情页模板，传递数据
    return render_template(
        "MovieDetail.html",
        movie=movie_info,
        recommend_movies=recommend_movies,
        avatar=get_current_user_avatar(),
        is_collected=is_collected
    )
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cr.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    uid = session['uid']
    
    if request.method == "GET":
        # 查询用户当前信息
        sql = "SELECT username, email, sex, age, avatar FROM userinfo WHERE iduserinfo = %s"
        user_info = database.query(sql, [uid])
        if not user_info:
            flash('用户信息不存在', 'error')
            return redirect(url_for('create.Homepage'))
        
        user_row = user_info[0]
        user = {
            "username": user_row[0] if len(user_row) > 0 else '',
            "email": user_row[1] if len(user_row) > 1 else '',
            "sex": user_row[2] if len(user_row) > 2 else '',
            "age": user_row[3] if len(user_row) > 3 else '',
            "avatar": user_row[4] if len(user_row) > 4 and user_row[4] else DEFAULT_AVATAR
        }
        
        # 传给模板
        return render_template('profile.html', user=user, avatar=user["avatar"])

    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        sex = request.form.get('gender', '').strip()
        age_input = request.form.get('age', '').strip()
        
        # ====================== 验证开始 ======================
        # 1. 邮箱格式验证
        if email:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                flash('❌ 邮箱格式不正确，请输入正确邮箱', 'error')
                return redirect(url_for('create.profile'))

        # 2. 年龄验证
        age = None
        if age_input:
            if not age_input.isdigit():
                flash('❌ 年龄必须是纯数字', 'error')
                return redirect(url_for('create.profile'))
            age = int(age_input)
            if age < 0 or age > 120:
                flash('❌ 年龄必须在 0 ~ 120 之间', 'error')
                return redirect(url_for('create.profile'))

        update_fields = []
        update_params = []

        if username:
            update_fields.append("username = %s")
            update_params.append(username)
        if email:
            update_fields.append("email = %s")
            update_params.append(email)
        if sex:
            update_fields.append("sex = %s")
            update_params.append(sex)
        if age is not None:
            update_fields.append("age = %s")
            update_params.append(age)

        # ====================== 头像上传处理 ======================
        avatar_file = request.files.get('avatar')
        
        if avatar_file and avatar_file.filename:
            if not allowed_file(avatar_file.filename):
                flash('❌ 头像格式不支持，请上传 png/jpg/jpeg/gif 文件', 'error')
                return redirect(url_for('create.profile'))
            # 安全文件名
            filename = secure_filename(f"{uid}_{avatar_file.filename}")
            # 保存目录
            save_dir = os.path.join(current_app.root_path, 'static', 'img')
            os.makedirs(save_dir, exist_ok=True)
            # 完整路径
            file_path = os.path.join(save_dir, filename)
            # 保存文件
            avatar_file.save(file_path)
            # 存入数据库的路径
            avatar_path = f"/static/img/{filename}"
            update_fields.append("avatar = %s")
            update_params.append(avatar_path)

        # 没有任何修改
        if not update_fields:
            flash('未修改任何信息', 'warning')
            return redirect(url_for('create.profile'))

        # 拼接 SQL
        escaped_params = []
        for value in update_params:
            if isinstance(value, str):
                escaped_params.append("'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'")
            else:
                escaped_params.append(str(value))

        sql = f"UPDATE userinfo SET {', '.join(update_fields)} WHERE iduserinfo = %s"
        formatted_sql = sql % (*escaped_params, uid)

        try:
            database.update(formatted_sql)
            flash('✅ 个人信息修改成功', 'success')
        except Exception as e:
            flash(f'❌ 修改失败：{str(e)}', 'error')

        return redirect(url_for('create.profile'))

@cr.route('/collection/<string:movie_id>', methods=["POST"])
@login_required
def collection(movie_id):
    """收藏/取消收藏电影"""
    uid = session['uid']
    
    # 检查是否已经收藏
    check_sql = "SELECT id FROM collections WHERE user_id = %s AND movie_id = %s"
    check_result = database.query(check_sql, [uid, movie_id])
    
    if check_result:
        # 已收藏，取消收藏
        delete_sql = f"DELETE FROM collections WHERE user_id = {uid} AND movie_id = '{movie_id}'"
        database.delete(delete_sql)
        flash('已取消收藏', 'success')
    else:
        # 未收藏，添加收藏
        insert_sql = f"INSERT INTO collections (user_id, movie_id) VALUES ({uid}, '{movie_id}')"
        database.insert(insert_sql)
        flash('收藏成功', 'success')
    
    return redirect(url_for('create.MovieDetail', movie_id=movie_id))

@cr.route('/collections')
@login_required
def collections():
    """用户收藏列表"""
    uid = session['uid']
    
    # 查询用户收藏的电影
    sql = """
    SELECT m.movie_id, m.movie_title, m.movie_img, m.movie_score 
    FROM collections c
    JOIN movie_data m ON c.movie_id = m.movie_id
    WHERE c.user_id = %s
    ORDER BY c.created_at DESC
    """
    collection_movies = database.query(sql, [uid])
    
    return render_template(
        'collections.html',
        collection_movies=collection_movies,
        avatar=get_current_user_avatar()
    )