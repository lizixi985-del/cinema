import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
DB_USER = 'root'
DB_PASSWORD = 'qazwsxedc'  # 注意你的密码是 qazwsxedc 
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'cinema_database'  # 需要先创建这个数据库

# 创建数据库引擎（修正后的连接字符串）
engine = create_engine(
    f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    echo=True  # 显示SQL语句，方便调试
)
df =pd.read_csv("final.csv")
df = df.replace({np.nan: None})
#年份和数量
def first():
    result = df.groupby('年份')['电影Id'].count().reset_index()
    result.columns = ['year','movie_count']
    print(result)
    result.to_sql('first',engine,if_exists='replace',index=False)
first()
