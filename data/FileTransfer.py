import pymysql
from pymysql import Error
import pandas as pd
import numpy as np
try:
    # Establish connection
    
    connection = pymysql.connect(
        host='localhost',
        database='cinema_database',
        user='root',
        password='qazwsxedc',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # returns rows as dictionaries
    )
    
    print("Connected to MySQL database")
    
    # Create cursor
    with connection.cursor() as cursor:
        # Execute query
        df = pd.read_csv('C:\\Users\\ZiXiTSLi\\Documents\\GitHub\\cinema\\final.csv')
        df = df.replace({np.nan: None})
        # df = df.dropna()
        print(f"读取到 {len(df)} 行数据")
       
        # sql = "select * from cinema_database.movie_data"
        # cursor.execute(sql)
        # # Fetch results
        # results = cursor.fetchall()
        # for row in results:
        #     print(row)
        sql = "insert into cinema_database.movie_data (movie_id,movie_title,movie_publicdate,movie_score,movie_img,movie_actor,movie_region,movie_type,movie_comment,movie_com_count) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        success_count = 0
        for index,row in df.iterrows():
            try:
                cursor.execute(sql,(row['电影Id'],row['标题'],row['年份'],row['评分'],row['海报'],row['主演'],row['地区'],row['类型'],row['评论'],row['评论数']))    
                success_count += 1
                if index % 100 == 0:  # 每100条打印一次进度
                    print(f"已插入 {success_count} 条数据")
            except Error as e:
                print(f"插入第 {index} 行时出错: {e}")
                print(f"数据: {row}")
                raise
        connection.commit()
        print("所有数据插入完成")
        # Fetch results
        # results = cursor.fetchall()
        # for row in results:
        #     print(row)
    
            
except Error as e:
    print(f"Error: {e}")
    
finally:
    if connection:
        connection.close()
        print("Connection closed")