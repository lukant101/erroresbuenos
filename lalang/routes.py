from lalang import app
from lalang.helpers.default_questions import get_default_questions
from flask import render_template, url_for, request
import os
import json
import mongoengine

supported_languages = ["english", "spanish", "polish"]

default_language = "spanish"

current_language = default_language

current_question_dict = dict(zip(supported_languages,
                                 (0 for x in supported_languages)))

questions = get_default_questions(supported_languages)


@app.route("/", methods=['GET', "POST"])
def home():
    global current_language
    current_language = default_language

    global current_question_dict
    for k, v in current_question_dict.items():
        current_question_dict[k] = 0
    return render_template('home.html', curr_lang=current_language,
                           question=questions[current_language][current_question_dict[current_language]])


@app.route('/next-question', methods=['GET', "POST"])
def load_question():
    if request.args.get('language'):
        global current_language
        current_language = request.args.get('language')
    else:
        current_question_dict[current_language] += 1

    if current_question_dict[current_language] > 4:
        current_question_dict[current_language] = 0

    current_quest_obj = questions[current_language][current_question_dict[current_language]]

    q_json = {}
    q_json_iter = current_quest_obj._fields.keys()
    for k in q_json_iter:
        q_json[k] = getattr(current_quest_obj, k)
    return json.dumps(q_json)
