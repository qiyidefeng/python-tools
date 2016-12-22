# coding=utf-8
from flask import Flask
from flask import request
from flask import render_template
from lxml import html
import requests

app = Flask(__name__)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"}

@app.route('/', methods={'GET', 'POST'})
def hello_world():
    if request.method=='POST':
        num=request.form['bookname']
        if num=='':
            return render_template('hello.html')
        #获取目录
        response=requests.get('http://www.33yq.com/read/10/10940/')
        page = html.fromstring(response.content.decode('gbk'))
        bookdir = page.xpath('//div[@id="list"]//a')

        if num=='0':
            chapter_title = bookdir[-1].xpath('text()')[0]
            response = requests.get(bookdir[-1].xpath('@href')[0])
            page = html.fromstring(response.content.decode('gbk'))
            content = page.xpath('//div[@class="zhangjieTXT"]/text()')
            return render_template('hello.html', chapter=chapter_title, text=content)

        for a in bookdir:
            chapter_title=a.xpath('text()')[0]
            if u'第'+num+u'章' in chapter_title:
                response=requests.get(a.xpath('@href')[0])
                page=html.fromstring(response.content.decode('gbk'))
                content=page.xpath('//div[@class="zhangjieTXT"]/text()')
                return render_template('hello.html', chapter=chapter_title, text=content)
        return render_template('hello.html', text=u'未找到章节')
    else:
        return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
