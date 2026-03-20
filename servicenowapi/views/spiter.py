import random
import time
import requests
import json
import os
import csv

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6",
    "origin": "https://movie.douban.com",
    "priority": "u=1, i",
    "referer": "https://movie.douban.com/explore",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0"
}
cookies = {
    "ll": "\"108288\"",
    "bid": "5uJH5Q6hbp0",
    "ap_v": "0,6.0",
    "__utma": "30149280.840890780.1773901078.1773901078.1773901078.1",
    "__utmb": "30149280.0.10.1773901078",
    "__utmc": "30149280",
    "__utmz": "30149280.1773901078.1.1.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/",
    "_vwo_uuid_v2": "DA76B8357183C55E7B095019603EE0B83|6aaae8e09a2621fa8855c36cab1241d8"
}
url = "https://m.douban.com/rexxar/api/v2/movie/recommend"


def paqu(tags,page):
    url = "https://m.douban.com/rexxar/api/v2/movie/recommend"
    selected_categories='{{"类型":"{}"}}'.format(tags)
    
    params = {
        "refresh": "0",
        "start": f"{page}",
        "count": "20",
        "selected_categories": selected_categories,
        "uncollect": "false",
        "score_range": "0,10",
        "tags": f"{tags}"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    data = json.loads(response.text)
    print (response.text)
    feeds= data['items']
    csv_file_path='movie.csv'
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path,mode='a',encoding='UTF-8',newline='') as csvfile:
        filenames= ['movie_id','title','subtitle','year','rating','star_count','comment_count',
                   'comment','poster','user_avatar','user_name','rank']
        writer=csv.DictWriter(csvfile,fieldnames=filenames)
        if not file_exists:
            writer.writeheader()
        for feed in feeds:
            movie_data={'movie_id':feed['id'],
                    'title':feed['title'],
                    'subtitle':feed['card_subtitle'],
                    'year':feed['year'],
                    'rating':feed['rating']['value'],
                    'star_count':feed['rating']['star_count'],
                    'comment_count':feed['rating']['count'],
                    'comment':feed['comment']['comment'],
                    'poster':feed['pic']['large'],
                    'user_avatar':feed['comment']['user']['avatar'],
                    'user_name':feed['comment']['user']['name'],
                    'rank':feed['honor_infos'][0]['rank'] if feed ['honor_infos'] else None
                    } 
            print(movie_data)
            writer.writerow(movie_data)
    
if __name__=='__main__':
    tags_list = ['喜剧','爱情','动作','科幻','动画','悬疑','犯罪','音乐','历史','奇幻','恐怖','战争','传记','歌舞','武侠','西部','纪录片','短片']
    for tags in tags_list:
        for page in range(1,4):
            page = page * 20
            paqu(tags,page)
            time.sleep(random.randint(1, 5))