import pymysql

DB_USER = 'root'
DB_PASSWORD = 'qazwsxedc'  # 注意你的密码是 qazwsxedc 
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'cinema_database'


def coon():
    con = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
        db= DB_NAME
    )
    cur = con.cursor()
    return con, cur

def close():
    con, cur = coon()  # 关闭数据库
    cur.close()
    con.close()

def query(sql):
    con, cur = coon()  # 查询数据库
    cur.execute(sql)
    res = cur.fetchall()
    close()
    return res

def insert(sql):
    con, cur = coon()  # 插入、修改数据库表
    try:
        cur.execute(sql)
        con.commit()  # 提交事务
        return True  # 返回执行成功
    except Exception as e:
        con.rollback()  # 发生错误时回滚
        print(f"数据库操作失败: {e}")
        return False  # 返回执行失败
    finally:
        close()  # 确保关闭连接

def insert_many(sql, data_list):
    con, cur = coon()  # 批量插入数据
    try:
        cur.executemany(sql, data_list)  # 执行批量插入
        con.commit()  # 提交事务
        return True
    except Exception as e:
        con.rollback()  # 发生错误时回滚
        print(f"批量数据库操作失败: {e}")
        return False
    finally:
        close()  # 确保关闭连接

def update(sql):
    con, cur = coon()  # 更新数据库
    try:
        affected_rows = cur.execute(sql)  # 执行更新操作
        con.commit()  # 提交事务
        return affected_rows  # 返回受影响的行数
    except Exception as e:
        con.rollback()  # 发生错误时回滚
        print(f"数据库更新失败: {e}")
        return -1  # 返回-1表示失败
    finally:
        close()  # 确保关闭连接

def delete(sql):
    con, cur = coon()  # 删除数据
    try:
        affected_rows = cur.execute(sql)  # 执行删除操作
        con.commit()  # 提交事务
        return affected_rows  # 返回受影响的行数
    except Exception as e:
        con.rollback()  # 发生错误时回滚
        print(f"数据库删除失败: {e}")
        return -1  # 返回-1表示失败
    finally:
        close()  # 确保关闭连接