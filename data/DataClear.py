# import pandas as pd
# df=pd.read_csv('movie.csv',names=['电影Id','标题','副标题','年份','评分',
#                                   '星级人数','评论数','评论','海报','头像',
#                                   '用户名','排名'], skiprows=1)
# subtitle_spilt= df['副标题'].str.split('/',expand=True)
# n_column = subtitle_spilt.shape[1]
# if n_column == 5 :
#     subtitle_spilt[3] = subtitle_spilt[3]+ '/' +subtitle_spilt[0]
#     subtitle_spilt = subtitle_spilt.drop(columns=[4])
# elif n_column > 5 :
#     subtitle_spilt[3] = subtitle_spilt.iloc[:,4:].apply(lambda row:'/'.join(row.dropna()),axis=1)
#     subtitle_spilt =subtitle_spilt.iloc[:,:4]
# subtitle_spilt.columns=['年份','地区','类型','主演']
# df =pd.concat([df,subtitle_spilt],axis=1)
# df.drop(columns=['副标题'],inplace = True)   
# df['主演']  = df ['主演'].replace('/','',regex= True) 
# df['地区']  =df ['地区'].str.split(' ').str[0]
# df['类型']  =df ['类型'].str.split(' ').str[0]     
# df['排名']  =df ['排名'].fillna(0) 
# df.to_csv('final.csv', index=False)                            
import pandas as pd
import numpy as np

# 1. 读取原始数据
df = pd.read_csv('movie.csv', names=['电影Id','标题','副标题','年份','评分',
                                    '星级人数','评论数','评论','海报','头像',
                                    '用户名','排名'], skiprows=1)

# 2. 副标题分割处理（核心修复：正确识别5列结构）
subtitle_split = df['副标题'].str.split('/', expand=True)
n_column = subtitle_split.shape[1]

# 根据分割列数分类处理，确保列对应正确
if n_column >= 5:
    # 正常情况（5列及以上）：年份/地区/类型/导演/主演，多余列合并到主演
    if n_column > 5:
        subtitle_split[4] = subtitle_split.iloc[:, 4:].apply(
            lambda row: '/'.join(str(x).strip() for x in row.dropna() if str(x).strip()), 
            axis=1
        )
    subtitle_split = subtitle_split.iloc[:, :5]  # 只保留前5列
    subtitle_split.columns = ['年份_new', '地区', '类型', '导演', '主演']  # 正确命名5列

elif n_column == 4:
    # 异常情况（4列）：缺少导演列，主演列补空
    subtitle_split.columns = ['年份_new', '地区', '类型', '主演']
    subtitle_split.insert(3, '导演', '')  # 插入空导演列，保证列顺序

else:
    # 异常情况（3列及以下）：补充缺失列
    base_cols = ['年份_new', '地区', '类型']
    subtitle_split.columns = base_cols[:n_column]
    for col in ['导演', '主演']:
        if col not in subtitle_split.columns:
            subtitle_split[col] = ''

# 3. 数据清理（只去空格，不破坏内容）
for col in ['年份_new', '地区', '类型', '导演', '主演']:
    subtitle_split[col] = subtitle_split[col].astype(str).str.strip()

# 4. 合并数据并删除原始副标题列
df = pd.concat([df, subtitle_split], axis=1)
df.drop(columns=['副标题', '年份_new'], inplace=True, errors='ignore')

# 5. 处理排名列缺失值
df['排名'] = df['排名'].fillna(0)

# 6. 保存结果
df.to_csv('final.csv', index=False, encoding='utf-8')