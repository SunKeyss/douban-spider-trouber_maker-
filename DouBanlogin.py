import requests
import json
import re
import time
import random

from bs4 import BeautifulSoup

import http.cookiejar as cookielib  # python3
from collections import Counter
from PyMongoDB import mongodao

iscoookies = True
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='DouBanCookies.txt')

session.headers = {
    'Connection': 'keep-alive',
    'Host': 'accounts.douban.com',
    'Referer': '',
    'User-Agent': 'Mozilla/5.0(Windows NT 10.0;WOW64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/63.0.3239.132 Safari/537.36'
}
data = {
    'ck': '',
    'name': '手机账号',
    'password': '密码',
    'remember': 'false',
    'ticket': ''
}

def writebook(info_readbook, time_readbook):
    filename = r'F:\DouBan_bookInfo3.txt'
    with open(filename, 'a+', encoding='utf-8') as f:
        f.write(info_readbook)
        f.write("---------")
        f.write(time_readbook)
        f.write("\n")
        f.close()


def CheckCookies():
    global session
    global iscoookies
    try:
        session.cookies.load(ignore_discard=True)  # 加载Cookies文件
        session.headers['Referer'] = 'https://www.douban.com/explore/'  # 初始化Referer屬性

        check_url = 'https://accounts.douban.com/passport/setting'  # 检验cookies是否还有用
        cht = session.get(check_url, headers=session.headers, cookies=session.cookies)
        cht.encoding = cht.apparent_encoding
        print(session.headers)
        cht_soup = BeautifulSoup(cht.text, 'html.parser').find("title").get_text()

        key_word = r"登录豆瓣"
        matchObj = re.match(key_word, cht_soup)
        print('cookies验证123=========================================')
        print('关键词：' + cht_soup)
        if matchObj is not None:
            iscoookies = True  # cookies信息需要更新
            print('检测到登录关键词：' + cht_soup)
            print('cookies验证123=========================================', end='\n\n')
            # Login(login_url)
        else:
            iscoookies = False
            print('cookies信息验证通过')
    except Exception as e:
        print(e)
        print("cookie未保存或已过期")
    return


def Login(login_url):
    global session
    CheckCookies()
    if iscoookies:
        print('logining#########')
        session.headers['Referer'] = r'https://accounts.douban.com/passport/login?source=main'  # 初始化Referer屬性

        req = session.post(login_url, headers=session.headers, data=data, timeout=30)
        req.encoding = req.apparent_encoding
        print(session.headers)
        message = json.loads(req.text)
        # print(message)
        myId = message['payload']['account_info']['id']
        myName = message['payload']['account_info']['name']
        print('登录状态：')
        print(message['status'])
        print(myName, end=':')
        print(myId)
        print('正在更新cookies！')
        # session.cookies.save()
        session.cookies.save(ignore_discard=True, ignore_expires=True)  # 保存cookies，覆盖原有的
    return


def GetUserList(myInterest_url):
    try:
        session.headers['Host'] = r'www.douban.com'  # host 和referer都必须对应才能正常访问
        session.headers['Referer'] = r'https://www.douban.com/people/156015093/'  # 初始化Referer屬性,此处的id是固定的对应账号

        req = session.get(myInterest_url, headers=session.headers, timeout=30)
        print('\n\n业务操作-----------------------------------------------')
        print(myInterest_url, end='【myInterest_url】')
        print('     页面状态', end=':')
        print(req.status_code, end='    目标链接：')
        print(req.url)
        print(session.headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        Tag_a_list = soup.select('.article .user-list li h3 a')
        Tag_deep_a_list = soup.select('.article .obu dd a')

        user_list = []
        # 我的关注 和 我关注的关注分开写
        # 深遍历的时候，当我关注的人为零时说明此事遍历的对象是我关注的关注
        if len(Tag_a_list) == 0:
            for lii in Tag_deep_a_list:
                a_user = lii['href']
                title_user = lii.getText()
                user_list.append(a_user + '::' + title_user)
        # 从我的关注发散出去
        if len(Tag_deep_a_list) == 0:
            for lii in Tag_a_list:
                # print(lii)
                a_user = lii['href']
                title_user = lii['title']
                user_list.append(a_user + '::' + title_user)

        user_list = list(set(user_list))  # 去出集合中重复的链接，会打乱列表顺序
        print(user_list)
        # user_list = user_list + border_gotuser(user_list)  # =================广度扩展
        return user_list
    except Exception as e:
        print(e)
        print('跳转失败，可能是由于cookies失效导致')
        print('尝试重新登录')


def BroadWise_Getuser(lists):
    total_list = []
    for lii in lists:
        singleUser_list = []  # 每次循环是清空
        singleUser_list = lii.split('::')
        singleUser_url = ''.join(singleUser_list[0])
        singleUser_user = ''.join(singleUser_list[1])

        broad_user_url = singleUser_url + 'contacts'  # 构造新链接
        # print(broad_user_url, end='【broad_user_url】 \n')

        session.headers['Referer'] = singleUser_url  # 初始化Referer属性
        req = session.get(broad_user_url, headers=session.headers, timeout=30)  # , allow_redirects=False
        print('     第二拓展操作-----------------------------------------------')
        print(broad_user_url + ' ' + singleUser_user, end='【border_user_url】')
        print('     页面状态', end=':')
        print(req.status_code, end='    目标链接：')
        print(req.url)

        soup = BeautifulSoup(req.text, 'html.parser')
        Tag_list = soup.select('.article .obu dd a')   #得出的结果是列表

        for i in Tag_list:
            Tag_list_url = i['href']
            Tag_list_user = i.get_text()
            total_list.append(Tag_list_url+'::'+Tag_list_user)   #所有关注的人的关注
    total_list = lists + total_list
    print(len(total_list),end='(筛选重复前 总用户数)')
    total_list = list(set(total_list))  # 去出集合中重复的链接，会打乱列表顺序
    print(len(total_list),end='(筛选重复后 总用户数)\n\n')
    #print(total_list)

    return total_list


def Getbook(list):
    print(list, end='  list \n')  # 存放目标用户的链接
    headers = {
        'Host': 'book.douban.com',
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;WOW64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/63.0.3239.132 Safari/537.36'
    }
    params = {
        'sort': 'rating',
        'start': '0',  # 这里的start参数控制翻页 ，一页15
        'mode': 'grid',
        'tags_sort': 'count'
    }

    for i in list:
        user_url = i.split('::')[0]
        collect_book_url = 'https://book' + user_url.split('www')[1] + 'collect'
        #print(collect_book_url)
        #
        # 所关注用户的读书信息
        headers['Referer'] = user_url

        try:
            req_book = session.get(collect_book_url, headers=headers, params=params, timeout=60)
        except requests.exceptions.ConnectionError as e:
            e.status_code = "Connection refused"
        # 从list中提取链接一个一个访问
        print(req_book.url)
        book_soup = BeautifulSoup(req_book.text, 'html.parser')
        # print(book_soup.prettify())
        list_readbook = book_soup.select('.article .interest-list li')
        # print(list_readbook)     #某个用户读过的一堆书的信息集合
        for b in list_readbook:
            info_readbook = b.select_one('.info h2 a')['title']
            time_readbook = b.select_one('.info .pub').getText().strip()
            print(info_readbook, end=' ------ ')
            print(time_readbook)
            #writebook(info_readbook, time_readbook)  # 下载模块
            document = {
                "bookname": info_readbook,
                "public_info": time_readbook
            }
            # try:
            #     mongodao.insertInfo(document)
            # except Exception as e:
            #     print(e)
            #     print("插入数据库失败")
        # 随机暂停模块
        t = random.random()
        if round(t, 2) < 0.65:
            print("防封ip模块生效中..")
            t_sleep = random.random()
            time.sleep(round(t_sleep, 1) * 8)


if __name__ == '__main__':
    # login_url = 'https://accounts.douban.com/passport/login?source=main'   登录页面
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'  # 提交登录数据的页面
    myInterest_url = 'https://www.douban.com/contacts/list'  # 我的关注

    Login(login_url)
    user_list = GetUserList(myInterest_url)  # 取得我的关注列表

    total_list = BroadWise_Getuser(user_list)  # 横向遍历我关注的人的关注列表
    Getbook(total_list)


    words = mongodao.selectInfo()
    hot_book = Counter(words).most_common(500)
    print("热门前500:")
    print(hot_book)
    #writebook(hot_book)