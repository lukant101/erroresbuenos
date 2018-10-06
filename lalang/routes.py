from flask import render_template, request
import json
from lalang import app
from lalang.helpers.default_questions_json import get_default_questions
from lalang.helpers.save_answer import save_answer
from lalang.helpers.create_student import create_temp_student
from lalang.db_model import supported_languages

default_language = "spanish"

current_language = default_language

current_question_dict = dict(zip(supported_languages,
                                 (0 for x in supported_languages)))

questions = get_default_questions(supported_languages)


@app.route("/", methods=['GET', "POST"])
def home():
    global current_language
    current_language = default_language
    # temporarily hard-coding the student's identity
    # needs to check the identity of student: login, cookie, ip address
    # if new user, create a temporary student record; then update it
    # when the user registers
    student_id = "5bb6b5bffde08a535c580608"
    # for testing a new user without a Student document
    # student_id=""

    global current_question_dict
    for k, v in current_question_dict.items():
        current_question_dict[k] = 0
    return render_template('home.html', curr_lang=current_language,
                           question=questions[current_language][current_question_dict[current_language]],
                           student_id=student_id)


@app.route('/next-question', methods=['GET', "POST"])
def load_question():

    if request.args.get('language'):
        # user changed the language
        global current_language
        current_language = request.args.get('language')
    else:
        # user answered a question and is asking for the next one
        current_question_dict[current_language] += 1
        # check if user has a Student Document
        if request.form["student_id"] == "":
            # get the id of the temporary student document
            student_id_temp = create_temp_student()
        else:
            student_id_temp = None

        # need to unpack the dictionary
        save_answer(**request.form, student_id_temp=student_id_temp)

    if current_question_dict[current_language] > 4:
        current_question_dict[current_language] = 0

    # get the next question object
    current_quest_obj = questions[current_language][current_question_dict[current_language]]

    # turn the question object into json and return it
    q_json = {}
    q_json_iter = current_quest_obj._fields.keys()
    for k in q_json_iter:
        q_json[k] = getattr(current_quest_obj, k)
    return json.dumps(q_json)
