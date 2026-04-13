from flask import Blueprint,render_template,request, jsonify,flash,redirect,url_for,session,Response
import database  
import requests
import pandas as pd
import json
import database
import random

cr =Blueprint("create",__name__)
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
            return jsonify({'code':200,'msg':'登录成功'})
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
    #     if RESULT:
    #         flash('用户名已经存在', 'error')
    #     else:
    #         sql = f"insert into userinfo(username,password,sex,age,avatar,email) values ('{username}','{password}','{sex}','{age}','{avatar}','{email}')"
    #         database.insert(sql)
    #         flash('注册成功', 'success')
    #         return redirect(url_for('register'))  # or render_template
    #     return redirect(url_for('register'))  # Redirect to show flash message
    # return render_template("register.html")
        if RESULT:
            return jsonify({'code':502,'msg':'用户名已经存在'})
        else:
            sql = f"insert into userinfo(username,password,sex,age,avatar,email) values ('{username}','{password}','{sex}','{age}','{avatar}','{email}')"
            database.insert(sql)
            return jsonify({'code':200,'msg':'注册成功' })
    return render_template("register.html")

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
        sql += f" where m.movie_title like '%{search}%'"  # 前面加空格

    # 拼接排序（无论是否搜索都排序，位置在搜索条件后）
    sql += " order by m.movie_title asc"  # 前面加空格

    # 构造计数 SQL
    totalItemSql = "select count(distinct movie_title) from movie_data"
    if search:
        totalItemSql += f" where m.movie_title like '%{search}%'"  # 前面加空格

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
    
    