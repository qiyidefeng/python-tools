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

CN_NUM = {
    u'〇': 0,
    u'一': 1,
    u'二': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,

    u'零': 0,
    u'壹': 1,
    u'贰': 2,
    u'叁': 3,
    u'肆': 4,
    u'伍': 5,
    u'陆': 6,
    u'柒': 7,
    u'捌': 8,
    u'玖': 9,

    u'貮': 2,
    u'两': 2,
}
CN_UNIT = {
    u'十': 10,
    u'拾': 10,
    u'百': 100,
    u'佰': 100,
    u'千': 1000,
    u'仟': 1000,
    u'万': 10000,
    u'萬': 10000,
    u'亿': 100000000,
    u'億': 100000000,
    u'兆': 1000000000000,
}


def cn2dig(cn):
    lcn = list(cn)
    unit = 0  # 当前的单位
    ldig = []  # 临时数组

    while lcn:
        cndig = lcn.pop()

        if CN_UNIT.has_key(cndig):
            unit = CN_UNIT.get(cndig)
            if unit == 10000:
                ldig.append('w')  # 标示万位
                unit = 1
            elif unit == 100000000:
                ldig.append('y')  # 标示亿位
                unit = 1
            elif unit == 1000000000000:  # 标示兆位
                ldig.append('z')
                unit = 1

            continue

        else:
            dig = CN_NUM.get(cndig)

            if unit:
                dig = dig * unit
                unit = 0

            ldig.append(dig)

    if unit == 10:  # 处理10-19的数字
        ldig.append(10)

    ret = 0
    tmp = 0

    while ldig:
        x = ldig.pop()

        if x == 'w':
            tmp *= 10000
            ret += tmp
            tmp = 0

        elif x == 'y':
            tmp *= 100000000
            ret += tmp
            tmp = 0

        elif x == 'z':
            tmp *= 1000000000000
            ret += tmp
            tmp = 0

        else:
            tmp += x

    ret += tmp
    return ret


def changenum(num):

    cdata = str(num).split('.')
    ckj = "0"
    num = cdata[0]
    if len(cdata) > 1:
        ckj = cdata[1]
        #print(ckj)

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
    #print(len(str(num)) - 1)
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


def searchQidian(bookname):
    '''在qidian.com上搜索书籍，返回书信息页，最新章节序号
        Args:
            bookname: 书名
        Returns:
            book_url, latest_chapter: 书信息页，最新章节序号
    '''

    try:
        book = urllib.quote(bookname.encode('utf-8'))
        response = requests.get('http://se.qidian.com/?kw=' + book, timeout=10)
        page = html.fromstring(response.text)
        s = page.xpath('//*[@id="result-list"]/div/ul/li')[0]
        title = s.xpath('.//h4')[0]
        title_t = title.text_content()
        title_a = title.xpath('.//a/@href')[0]
        update = s.xpath('.//p[@class="update"]')[0].text_content()

        if bookname in title_t:
            m = re.search(u'第(\d*)([^\d]*)章', update)
            if m is not None:
                if m.groups()[1] == u'':
                    return title_a, m.groups()[0]
                return title_a, str(cn2dig(m.groups()[1]))
        return None, None

    except Exception, e:
        print e.message
        return None, None


def search33yq(bookname, chapter_num):
    '''在33yq.com上搜索书籍某一章，有则返回该章文字，无则返回None
        Args:
            bookname: 书名
            chapter_num: 章节序号
        Returns:
            指定章节的文字
    '''
    try:
        response = requests.get('http://www.33yq.com/', timeout=10)
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
            return None

        # 获取目录
        response = requests.get('http://' + m[0])
        page = html.fromstring(response.content.decode('gbk'))
        title = page.xpath('//title/text()')[0]
        if bookname != title:
            return None
        bookdir = page.xpath('//div[@id="list"]//a')

        content = []
        for a in bookdir:
            chapter_title = a.xpath('text()')[0]
            if u'第' + chapter_num + u'章' in chapter_title or u'第' + \
                    changenum(chapter_num) + u'章' in chapter_title:
                response = requests.get(a.xpath('@href')[0])
                page = html.fromstring(response.content.decode('gbk'))
                content.append(chapter_title)
                content = content + page.xpath('//div[@class="zhangjieTXT"]/text()')

        if content == []:
            return None
        return content
    except Exception, e:
        print '搜索33yq.com出现错误', e.message
        return None


def searchDhzw(bookname, chapter_num):
    '''在dhzw.com上搜索书籍某一章，有则返回该章文字，无则返回None
        Args:
            bookname: 书名
            chapter_num: 章节序号
        Returns:
            指定章节的文字
    '''

    try:
        data = {'searchkey': bookname.encode('gbk')}
        response = requests.post('http://www.dhzw.com/modules/article/search.php', headers=headers, data=data, timeout=10)
        page = html.fromstring(response.content.decode('gbk'))

        lis = page.xpath('//div[@class="l"]//li')
        search_succ = False
        for li in lis:
            name = li.xpath('./*[@class="s2"]')[0].text_content()
            name_url = li.xpath('./*[@class="s2"]/a/@href')[0]
            latest = li.xpath('./*[@class="s3"]')[0].text_content()
            if bookname == name:
                search_succ = True
                break

        if not search_succ:
            return None
        # 获取目录
        response = requests.get(name_url, timeout=10)
        page = html.fromstring(response.content.decode('gbk'))
        title = page.xpath('//title/text()')[0]
        bookdir = page.xpath('//div[@id="list"]//a')

        content = []
        for a in bookdir:
            chapter_title = a.xpath('text()')[0]
            if u'第' + chapter_num + u'章' in chapter_title or u'第' + \
                    changenum(chapter_num) + u'章' in chapter_title:
                response = requests.get(name_url + a.xpath('@href')[0], timeout=10)
                page = html.fromstring(response.content.decode('gbk'))
                content.append(chapter_title)
                content = content + page.xpath('//div[@id="BookText"]/text()')
        if content == []:
            return None
        return content
    except Exception, e:
        print '搜索dhzw.com出现错误', e.message
        return None


def search23zw(bookname, chapter_num):
    '''在23zw.com上搜索书籍某一章，有则返回该章文字，无则返回None
        Args:
            bookname: 书名
            chapter_num: 章节序号
        Returns:
            指定章节的文字
    '''
    pass


@app.route('/', methods={'GET', 'POST'})
def hello_world():
    if request.method == 'POST':
        search_string = request.form['bookname']
        print search_string
        if search_string == '':
            return render_template('index.html')
        words = search_string.split(u' ')
        bookname = words[0]
        chapter_num = '0'
        if len(words) == 2:
            chapter_num = words[1]

        qidian_url, latest_chapter = searchQidian(bookname)
        print 'qidian结果:', qidian_url, latest_chapter
        if qidian_url is None:
            return render_template('index.html')
        #print urllib.quote(bookname.encode('utf-8'))

        if chapter_num == '0':
            chapter_num = latest_chapter
        elif int(chapter_num)>int(latest_chapter):
            return render_template(
                'search.html',
                input=search_string,
                text={u'目前还没有该章节呢！'})

        content = search33yq(bookname, chapter_num)
        if content is None:
            content = searchDhzw(bookname, chapter_num)
        if content is None:
            return render_template(
                'search.html',
                input=search_string,
                text={u'未找到'})
        else:
            return render_template(
                'search.html',
                input=search_string,
                text=content)

    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
