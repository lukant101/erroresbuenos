from lalang import app
from lalang.helpers.default_questions import get_default_questions
from flask import render_template, url_for, request
import os

supported_languages = ["english", "spanish", "polish"]

current_language = "spanish"    # i.e. spanish is the default language

current_question = dict(zip(supported_languages,
                            (0 for x in supported_languages)))

questions = get_default_questions(supported_languages)


@app.route("/", methods=['GET', "POST"])
def home():
    return "I'm home"


@app.route("/<lang>/<int:qnum>", methods=['GET', "POST"])
def question_card(lang, qnum):

    current_language = lang
    if qnum > 4:
        current_question[current_language] = 0
    else:
        current_question[current_language] = qnum

    return render_template('home.html', curr_lang=current_language,
                           question=questions[current_language][current_question[current_language]],
                           curr_q_num=current_question[current_language])


@app.route('/user-answer', methods=['GET', "POST"])
def user_answer():
    return request.form['user_answer']
    # return f"your name is: {request.form['name']} and your city is {request.form['city']}"
    # return request.form['name']
    # return f"Hi there. Your answer was {request.form['user_answer']}"


@app.route('/login', methods=['GET', "POST"])
def login():
    if request.method == "POST":
        return "post method used"
    else:
        return render_template('login.html')
