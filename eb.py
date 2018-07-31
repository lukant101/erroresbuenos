from flask import Flask, render_template, url_for, request
import os

app = Flask(__name__)


@app.route("/<string:fname>")
def home_pic(fname):
    # os.chdir('static/pics')
    if os.path.exists('static/pics/' + fname + '.jpg'):
        pic_url = url_for('static', filename='pics/' + fname + '.jpg')
    elif os.path.exists('static/pics/' + fname + '.png'):
        pic_url = url_for('static', filename='pics/' + fname + '.png')
    else:
        pic_url = url_for('static', filename='pics/101.jpg')
    return render_template('home.html', fname=fname, pic_url=pic_url)


@app.route("/", methods=['GET', 'POST'])
def home():
    pic_url = url_for('static', filename='pics/101.jpg')
    return render_template('home.html', fname='101', pic_url=pic_url)


@app.route('/user-answer', methods=['POST'])
def user_answer():
    return request.form['user_answer']
    # return f"your name is: {request.form['name']} and your city is {request.form['city']}"
    # return request.form['name']
