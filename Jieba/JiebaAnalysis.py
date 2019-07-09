import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

content_path = r'F://DouBan_bookInfo2.txt'  # 文本
stop_word_path = r'Stop_Word1'  # 停用词库
font_path =r'C:\Windows\Fonts\STXINGKA.TTF'  # 字体
bg_image_path = r'2.jpg'# 二值化图片
mywordlist = []  # 存放去除了停顿词的
with open(content_path, 'r', encoding='utf-8') as t:
    content = t.read()

seg_list = jieba.cut(content, cut_all=False)
lister = " / ".join(seg_list)  # 分割完成后的文本

# 去除停顿词
with open(stop_word_path, 'r', encoding='utf-8') as fs:
    fs_text = fs.read()
fs_stop_textlist = fs_text.split('\n')
for oneword in lister.split('/'):  # 去除停顿词，生成新文档
    if not (oneword.strip() in fs_stop_textlist) and len(oneword.strip()) > 1:
        mywordlist.append(oneword)
print("have processed:")
# print(mywordlist)
mywordlist = ''.join(mywordlist)

# 抽取1000个关键词，带权重，后面需要根据权重来生成词云
allow_pos = ('nr',)  # 词性 ns地名  nr人名
tags = jieba.analyse.extract_tags(mywordlist, 1000, withWeight=True, allowPOS=allow_pos)
keywords = dict()  # 创建空字典
for i in tags:
    print("%s---%f" % (i[0], i[1]))
    keywords[i[0]] = i[1]

# 词云生成
back_coloring = plt.imread(bg_image_path)  # 设置背景图片
# 设置词云属性
wc = WordCloud(font_path=font_path,  # 设置字体
               background_color="#FFE7BA",  # 背景颜色
               max_words=1000,  # 词云显示的最大词数
               mask=back_coloring,  # 设置背景图片
               )

# 根据频率生成词云
wc.generate_from_frequencies(keywords)
# 显示图片
plt.figure()
plt.imshow(wc)
plt.axis("off")
plt.show()
# 保存到本地
wc.to_file("AnalysisCloud1.jpg")
