from flask import Blueprint,render_template,request, jsonify,flash,redirect,url_for
import database  
import requests
import json
cr =Blueprint("create",__name__)
@cr.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('password')
        sql = "select * from userinfo where username = %s and password = %s" %(username,password)
        RESULT= database.query(sql)
        print(RESULT)
        if RESULT:
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
    
    