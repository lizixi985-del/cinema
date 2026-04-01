import pandas as pd
df=pd.read_csv('movie.csv',names=['电影Id','标题','副标题','年份','评分',
                                  '星级人数','评论数','评论','海报','头像',
                                  '用户名','排名'], skiprows=1)
subtitle_spilt= df['副标题'].str.split('/',expand=True)
n_column = subtitle_spilt.shape[1]
if n_column == 5 :
    subtitle_spilt[3] = subtitle_spilt[3]+ '/' +subtitle_spilt[0]
    subtitle_spilt = subtitle_spilt.drop(columns=[4])
elif n_column > 5 :
    subtitle_spilt[3] = subtitle_spilt.iloc[:,4:].apply(lambda row:'/'.join(row.dropna()),axis=1)
    subtitle_spilt =subtitle_spilt.iloc[:,:4]
subtitle_spilt.columns=['年份','地区','类型','主演']
df =pd.concat([df,subtitle_spilt],axis=1)
df.drop(columns=['副标题'],inplace = True)   
df['主演']  = df ['主演'].replace('/','',regex= True) 
df['地区']  =df ['地区'].str.split(' ').str[0]
df['类型']  =df ['类型'].str.split(' ').str[0]     
df['排名']  =df ['排名'].fillna(0) 
df.to_csv('final.csv', index=False)                            