# coding=utf-8
from flask import Flask
from flask import request
from flask import render_template
from lxml import html
import requests
import urllib
import re

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}


def changenum(num):

    cdata = str(num).split('.')
    ckj = "0"
    num = cdata[0]
    if len(cdata) > 1:
        ckj = cdata[1]
        print(ckj)

    dic_num = {
        "0": u"零",
        "1": u"一",
        "2": u"二",
        "3": u"三",
        "4": u"四",
        "5": u"五",
        "6": u"六",
        "7": u"七",
        "8": u"八",
        "9": u"九"}
    dic_unit = {
        0: "",
        1: u"十",
        2: u"百",
        3: u"千",
        4: u"万",
        5: u"十",
        6: u"百",
        7: u"千",
        8: u"亿"}
    # num = "12345"
    numList = list(str(num))
    s = ""
    a = ""
    x = 0
    print(len(str(num)) - 1)
    index = len(str(num)) - 1
    for i in numList:
        if i == "0":
            if index == 4:
                a = "万"
            x = x + 1
        else:
            if x > 0:
                s += a + u"零" + dic_num[i] + dic_unit[index]
            else:
                s += dic_num[i] + dic_unit[index]
            x = 0

        index -= 1
    return s


@app.route('/', methods={'GET', 'POST'})
def hello_world():
    if request.method == 'POST':
        search_string = request.form['bookname']
        print search_string
        if search_string == '':
            return render_template('hello.html')
        bookname, num = search_string.split(u' ')

        print urllib.quote(bookname.encode('utf-8'))

        # 搜索书籍
        response = requests.get('http://www.33yq.com/')
        page = html.fromstring(response.content.decode('gbk'))
        s = page.xpath('//input[@name="s"]/@value')[0]

        response = requests.get(
            'http://s.33yq.com/cse/search?q=' +
            urllib.quote(
                bookname.encode('utf-8')) +
            '&click=1&s=' +
            s +
            '&nsid=')
        page = response.content.decode('utf-8')
        m = re.findall(r'www.33yq.com/read/\d+/\d+/', page)
        if len(m) == 0:
            return render_template(
                'hello.html',
                input=search_string,
                text=u'未找到书籍')

        # 获取目录
        response = requests.get('http://' + m[0])
        page = html.fromstring(response.content.decode('gbk'))
        title = page.xpath('//title/text()')[0]
        if bookname not in title:
            return render_template(
                'hello.html',
                input=search_string,
                text=u'未找到书籍')
        bookdir = page.xpath('//div[@id="list"]//a')

        if num == '0':
            chapter_title = bookdir[-1].xpath('text()')[0]
            response = requests.get(bookdir[-1].xpath('@href')[0])
            page = html.fromstring(response.content.decode('gbk'))
            content = page.xpath('//div[@class="zhangjieTXT"]/text()')
            return render_template(
                'hello.html',
                input=search_string,
                chapter=chapter_title,
                text=content)

        for a in bookdir:
            chapter_title = a.xpath('text()')[0]
            print chapter_title
            if u'第' + num + u'章' in chapter_title or u'第' + \
                    changenum(num) + u'章' in chapter_title:
                response = requests.get(a.xpath('@href')[0])
                page = html.fromstring(response.content.decode('gbk'))
                content = page.xpath('//div[@class="zhangjieTXT"]/text()')
                return render_template(
                    'hello.html',
                    input=search_string,
                    chapter=chapter_title,
                    text=content)
        return render_template('hello.html', text=u'未找到章节')
    else:
        return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
