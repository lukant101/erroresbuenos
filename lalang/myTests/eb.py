from flask import Flask, render_template, url_for, request
from flask_mongoengine import MongoEngine
import os
from helpers.get_template_questions import get_template_questions

app = Flask(__name__)
# app.config.from_pyfile('the-config.cfg')

app.config['MONGODB_SETTINGS'] = {
    'db': 'lalang_db',
    'host': 'localhost',
    'port': 27017
}

db = MongoEngine(app)

supported_languages = ["english", "spanish", "polish"]


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
    questions = get_template_questions()
    pic_url = url_for('static', filename='pics/101.jpg')
    audio_url = url_for('static', filename='audio/polish/sto.ogg')
    return render_template('home.html', fname='101', pic_url=pic_url, audio_url=audio_url, questions=questions)


@app.route('/user-answer', methods=['POST'])
def user_answer():
    return request.form['user_answer']
    # return f"your name is: {request.form['name']} and your city is {request.form['city']}"
    # return request.form['name']


@app.route('/login')
def login():
    return request.form['login-page']