from flask import Flask
from flask import request
from flask import render_template
app = Flask(__name__)


@app.route('/', methods={'GET', 'POST'})
def hello_world():
    if request.method=='POST':
        return render_template('hello.html', name=request.form['bookname'])
    else:
        return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)
