"""Handle requests for all endpoints of the website."""

from flask import render_template, request, Response
import logging
from lalang import app
from lalang.helpers.more_questions import get_questions_all_lang
from lalang.helpers.save_answer import save_answer
from lalang.helpers.create_student import create_temp_student
from lalang.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, student_id
from lalang.helpers.utils import question_obj_to_json

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")

current_language = DEFAULT_LANGUAGE

current_question_num = dict(zip(SUPPORTED_LANGUAGES,
                                (0 for x in SUPPORTED_LANGUAGES)))

if not student_id:
    student_id = create_temp_student()

questions = get_questions_all_lang(SUPPORTED_LANGUAGES, student_id)


@app.route("/", methods=['GET', "POST"])
def home():
    """Render the home page shell, as well as the initial questions.

    - temporarily hard-coding the student's identity
    - needs to check the identity of student: login, cookie, ip address
    """
    global current_language
    current_language = DEFAULT_LANGUAGE

    return render_template('home.html', curr_lang=DEFAULT_LANGUAGE,
                           question=(questions[DEFAULT_LANGUAGE]
                                     [current_question_num[DEFAULT_LANGUAGE]]),
                           student_id=student_id)


@app.route('/next-question', methods=['GET', "POST"])
def load_question():
    """Handle asynchronous request from client for more or different questions.

    If the user changes the studied language, send a question for that
    language.

    If the user answered a question, save the answer (using function
    save_answer) and send the next question.

    Return:
    question as JSON
    """
    if request.args.get('language'):
        # user changed the language
        global current_language
        current_language = request.args.get('language')
    else:
        # user answered a question and is asking for the next one
        global current_question_num
        current_question_num[current_language] += 1

        # need to unpack the dictionary
        new_questions = save_answer(**request.form)

        # if new questions added to question queue in Student document
        # add those questions to questions dictionary
        global questions
        if new_questions:
            questions[current_language].extend(new_questions)

    # get the next question object
    current_quest_obj = (questions[current_language]
                         [current_question_num[current_language]])

    logging.info(f"Next word: {current_quest_obj.word}")

    # turn the question object into json and return it
    return question_obj_to_json(current_quest_obj)
