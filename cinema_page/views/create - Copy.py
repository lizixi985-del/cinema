from flask import Blueprint,render_template,request, jsonify,flash,redirect,url_for,session,Response,current_app
import database  
import requests
import pandas as pd
import database
from werkzeug.utils import secure_filename
import os


cr =Blueprint("create",__name__)

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
        sql = f"SELECT * FROM userinfo WHERE username = '{username}' AND password = '{password}'"
        RESULT= database.query(sql)
        print(RESULT)
        if RESULT:
            session['uid'] = RESULT[0][0]
            flash('登录成功', 'success')
            return redirect(url_for('create.Homepage'))
            # return jsonify({'code':200,'msg':'登录成功'})
        else:
            return jsonify({'code':500,'msg':'登录失败:请确认用户名存在或者密码正确'})
    return render_template("login.html")
@cr.route('/Register',methods=["GET","POST"])
def Register():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        sex = request.form.get('gender')
        age = request.form.get('age')
        email= request.form.get('email')
        avatar ='static/img/user_default.png'
        sql = f"select username from userinfo where username='{username}'"
        RESULT= database.query(sql)
        if RESULT:
            flash('用户名已经存在', 'error')
        else:
            sql = f"insert into userinfo(username,password,sex,age,avatar,email) values ('{username}','{password}','{sex}','{age}','{avatar}','{email}')"
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
    print(random_movie)
    return render_template("Homepage.html",
                           total=total,most_fre_actor=most_fre_actor,
                           most_fre_country=most_fre_country,most_fre_type=most_fre_type,random_movie=random_movie)
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
                           search=search)
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

    # 3. 渲染详情页模板，传递数据
    return render_template(
        "MovieDetail.html",
        movie=movie_info,
        recommend_movies=recommend_movies
    )
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@cr.route('/profile', methods=["GET", "POST"])
def profile(): 
    uid = session['iduserinfo'] 
    if request.method == "GET":
        # 查询用户当前信息
        sql = "SELECT username, email, sex, age, avatar FROM userinfo WHERE iduserinfo = %s"
        user_info = database.query(sql, [uid])
        if not user_info:
            flash('用户信息不存在', 'error')
            return redirect(url_for('create.Homepage'))
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        sex = request.form.get('gender', '').strip()
        age = request.form.get('age', '').strip()
        avatar = request.form.get('avatar')
        # ====================== 验证开始 ======================
        # 1. 邮箱格式验证
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if email and not re.match(email_regex, email):
            flash('❌ 邮箱格式不正确，请输入正确邮箱', 'error')
            return redirect(url_for('create.profile'))

        # 2. 年龄验证（必须是数字 0~120）
        age = None
        if age:
            if not age.isdigit():
                flash('❌ 年龄必须是纯数字', 'error')
                return redirect(url_for('create.profile'))
            age = int(age)
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
        if age:
            update_fields.append("age = %s")
            update_params.append(age)
        if avatar:
            update_fields.append("avatar = %s")
            update_params.append(avatar)
        avatar_path = None
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(f"{uid}_{avatar.filename}")
                # 构建保存路径（static/avatar 需提前创建）
            save_path = os.path.join(current_app.root_path,'static', 'img')
            os.makedir(save_path,exist_ok = True)
            file_path = os.path.join(save_path,filename)
            avatar.save(file_path)
            #生成相对路径
            avatar_path = os.path.join('/static/images/',filename)
            update_fields.append(f"avatar = '{avatar_path}'")
            
        if not update_fields:
            flash('未修改任何信息', 'warning')
            return redirect(url_for('create.profile'))

        # 拼接SQL，主键用 iduserinfo
        sql = f"UPDATE userinfo SET {', '.join(update_fields)} WHERE iduserinfo = %s"
        update_params.append(uid)

        try:
            database.update(sql, update_params)
            flash('个人信息修改成功', 'success')
        except Exception as e:
            flash(f'修改失败：{str(e)}', 'error')

        return redirect(url_for('create.profile'))  
    return render_template()