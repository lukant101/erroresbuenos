"""Handle requests for all endpoints of the website."""

from flask import render_template, request, redirect, flash, url_for, abort
import logging
from bson import ObjectId
from flask_login import login_user, current_user, logout_user, login_required
from lalang import app, bcrypt
from lalang.helpers.more_questions import get_questions_all_lang
from lalang.helpers.save_answer import save_answer
from lalang.helpers.create_student import create_temp_student
from lalang.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, student_id
from lalang.helpers.utils import question_obj_to_json, is_safe_url
from lalang.forms import StudentRegister, StudentLogin
from lalang.db_model import Student

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a")

current_language = DEFAULT_LANGUAGE

current_question_num = dict(zip(SUPPORTED_LANGUAGES,
                                (0 for x in SUPPORTED_LANGUAGES)))

if not student_id:
    student_id = create_temp_student()

questions = get_questions_all_lang(SUPPORTED_LANGUAGES, student_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = StudentLogin()
    if form.validate_on_submit():
        student = Student.objects(email=form.email.data.lower()).first()
        if student and bcrypt.check_password_hash(student.password,
                                                  form.password.data):
            login_user(student, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                if is_safe_url(next_page):
                    return redirect(next_page)
                else:
                    return abort(400)
            else:
                return redirect(url_for("classroom"))

        else:
            flash("We could not log you in. \
            Please check your email and password.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = StudentRegister()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)\
            .decode("utf-8")
        student = Student(email=form.email.data.lower(),
                          username=form.username.data,
                          alt_id=ObjectId(),
                          first_name=form.first_name.data,
                          last_name=form.last_name.data,
                          password=hash_password, temp=False)
        student.save()
        flash(f"An account for {form.email.data} \
        has been created successfully.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/classroom", methods=['GET', "POST"])
@app.route("/", methods=['GET', "POST"])
def home():
    """Render the home page shell, as well as the initial questions."""
    global student_id
    global questions

    return render_template('home.html', curr_lang=DEFAULT_LANGUAGE,
                           question=(questions[DEFAULT_LANGUAGE]
                                     [current_question_num
                                      [DEFAULT_LANGUAGE]]),
                           student_id=student_id)


@app.route("/classroom")
@login_required
def classroom():
    return render_template("classroom.html")


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
        logging.info(request.form)
        logging.info(type(request.form))
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
