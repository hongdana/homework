# @Author:洪绍洧 201992262
# -*- coding = utf-8 -*-
# @Time: 2022/1/3 21:47
# @File: h1.py
# @Software: PyCharm
from bs4 import BeautifulSoup
import re
import urllib.request,urllib.error
import xlwt
import sqlite3

def main():
    baseurl="https://movie.douban.com/top250?start="
    #爬取网页
    datalist=getData(baseurl)
    #保存数据
    #savepath="豆瓣电影Top250.xls"
    #saveData(datalist,savepath)
    #dbpath="movie.db"
    #saveDatadb(datalist, dbpath)
    # askURL("https://movie.douban.com/top250?start=0")
    #解析数据
    #score,num=score1()
    #print(score,num)
    fscore,judgenum1=judgenum()
    print(fscore,judgenum1)


#爬取网页
findLink=re.compile(r'<a href="(.*?)">')    #正则表达式提取规则 a href开头>结尾的所有内容
#影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)   #re.S 让换行符包含在字符中
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#找到评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)



def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 根据尾数生成10页网页
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存获取到的网页源码

        # 逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):  # 查找符合要求的字符串，形成列表
            # print(item)   #测试：查看电影item全部信息
            data = []  # 保存一部电影的所有信息
            item = str(item)

            # 影片详情的链接
            link = re.findall(findLink, item)[0]  # re库用来通过正则表达式查找指定的字符串[0]代表第一个链接
            data.append(link)  # 添加链接

            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)  # 添加图片

            titles = re.findall(findTitle, item)  # 片名可能只有一个中文名，没有外国名
            if (len(titles) == 2):
                ctitle = titles[0]  # 添加中文名
                data.append(ctitle)
                otitle = titles[1].replace("/", "").replace("\xa0", "")  #去掉无关符号
                data.append(otitle)  # 添加外国名
            else:
                data.append(titles[0])
                data.append(' ')  # 外国名字留空方便excel对其

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judgeNum = re.findall(findJudge, item)[0]
            data.append(judgeNum)

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  # 去掉句号
                data.append(inq)
            else:
                data.append(" ")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)  # 去掉<br/>
            bd = re.sub('/', " ", bd)  # 替换/
            data.append(bd.strip())  # 去掉前后的空格
            # print(data)
            datalist.append(data)  # 把处理好的一部电影信息放入datalist
    print(datalist) #运行非常非常慢，需要等待
            # print(link)
            # print(imgSrc)
            # print(rating)
            # print(titles)
            # print(bd)
            # print(judgeNum)
    return datalist


def askURL(url):
    head={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    #用户代理#
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response=urllib.request.urlopen(request)
        html=response.read().decode("utf-8")
        #print(html)出现error403就换个header
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html


#保存数据


def saveData(datalist,savepath):# 保存到excel
    print("save....")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)  # 创建工作表
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])  # 列名
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])  # 数据

    book.save('film.xls')  # 保存


def saveDatadb(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index == 5:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                    insert into movie250 (
                    info_link,pic_link,cname,ename,score,rated,instroduction,info) 
                    values(%s)''' % ",".join(data)
        #print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):#创建数据库
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric ,
        rated numeric ,
        instroduction text,
        info text
        )
        
    '''

    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


#储存评分与对应电影数量
def score1():
    score = []  #评分
    num = []    #每个评分所统计出的电影数量
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select score,count(score) from movie250 group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(str(item[0]))
        num.append(item[1])

    cur.close()
    con.close()
    return score, num

#储存前10部电影分数以及观影数量
def judgenum():
    fscore = []  #评分
    judgenum = []    #每个评分所统计出的观影数量
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select score,rated from movie250 limit 0,10"
    data = cur.execute(sql)
    for item in data:
        fscore.append(str(item[0]))
        judgenum.append(item[1])

    cur.close()
    con.close()
    return fscore, judgenum

if __name__ == "__main__":
    main()



