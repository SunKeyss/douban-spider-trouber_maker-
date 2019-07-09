import pymongo
from pymongo import MongoClient

from collections import Counter

# 1.链接本地数据库服务  #admin 数据库有帐号，连接-认证-切换库
name = MongoClient('localhost', 27017)
db_auth = name.admin
db_auth.authenticate("root", "a123")

# 2.链接本地数据库  没有会创建
db = name.DouBan  # 数据库名
# 3.创建或连接集合
bi = db.BookInfo  # BookInfo集合名
# 4.根据情况清空聚合   注意每一次操作都会清空集合
#bi.remove(None)


# 5增加数据
def insertInfo(document):
    bi.insert(document)
    return


def selectInfo():
    all_direct = []
    bookname_list = list(db.BookInfo.find({}, {'bookname': 1, '_id':0 }))
    for i in bookname_list:
        direct = i['bookname']
        all_direct.append(direct)
    return all_direct


def writebook(bookname):
    filename = r'F:\HotBookName.txt'
    for i in bookname:
        i = str(i)
        with open(filename, 'a+', encoding='utf-8') as f:
            f.write(i)
            f.write("\n")
            f.close()

if __name__ == "__main__":
#     # documents = [{
#     #     "bookname": "房思琪的初恋乐园",
#     #     "public_info": "林奕含 / 北京联合出版公司 / 2018-1 / 45.00元"
#     # }, {
#     #     "bookname": "猜猜我有多爱你",
#     #     "public_info": "[英] 山姆·麦克布雷尼 文、安妮塔·婕朗 图 / 梅子涵 / 少年儿童出版社 / 2005-4 / 29.80元"
#     # },{
#     #     "bookname": "以上是测试数据",
#     #     "public_info": "测试数据"
#     # }]
#     # documents1 = [{
#     #     "bookname": "以上是测试数据",
#     #     "public_info": "测试数据"
#     # }]
#     #insertInfo(documents)
#     #insertInfo(documents1)
#######################################################
    words = selectInfo()
    hot_book = Counter(words).most_common(1000)
    print(words)
    print(hot_book)
#     writebook(hot_book)