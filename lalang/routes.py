"""Handle requests for all endpoints of the website."""

from flask import render_template, request, redirect, flash, url_for, abort
import logging
from bson import ObjectId
from datetime import datetime
import pytz
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from lalang import app, bcrypt, mail, send_email_address
from lalang.helpers.more_questions import (get_questions_all_lang,
                                           get_queue_question)
from lalang.helpers.save_answer import save_answer
from lalang.helpers.create_student import create_temp_student
from lalang.constants import (SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
                              DEFAULT_TEMP_STUDENT_ID)
from lalang.helpers.utils import question_obj_to_json, is_safe_url
from lalang.forms import (StudentRegister,
                          StudentLogin, RequestResetForm, ResetPasswordForm)
from lalang.db_model import Student, Question

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and not current_user.temp:
        return redirect(url_for("home"))
    form = StudentLogin()
    if form.validate_on_submit():
        student = Student.objects(email=form.email.data.lower()).first()
        if student and bcrypt.check_password_hash(student.password,
                                                  form.password.data):
            if current_user.is_authenticated and current_user.temp:
                # user has been using a temp account during session
                # but now wants to log in, so log out from the temp account
                logout_user()
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
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and not current_user.temp:
        return redirect(url_for("home"))
    form = StudentRegister()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)\
            .decode("utf-8")
        if not current_user.is_authenticated:
            # user has never registered or answered a question
            # (ie no temp student document), so create a new Student document
            student = Student(email=form.email.data.lower(),
                              username=form.username.data,
                              alt_id=ObjectId(),
                              first_name=form.first_name.data,
                              last_name=form.last_name.data,
                              password=hash_password,
                              temp=False)
            student.save()
        else:
            # user has answered a question before, but never registered;
            # so update the temp document user has been using and
            # flag it as not temporary
            current_user.email = form.email.data.lower()
            current_user.username = form.username.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.password = hash_password
            current_user.temp = False
            current_user.save()

        flash(f"An account for {form.email.data} \
        has been created successfully.", "success")
        logout_user()
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


def send_reset_email(student):
    token = student.get_reset_token()
    msg=Message("Password Reset",
                sender=send_email_address,
                recipients=[student.email])
    msg.body = f"""To reset the password, go to:
{url_for("reset_password", token=token, _external=True)}

If you did not request a password reset, you can simply ignore this email and no changes will be made to your account.
"""
    mail.send(msg)


@app.route("/request-reset", methods=['GET', "POST"])
def request_reset():
    if current_user.is_authenticated and not current_user.temp:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        student = Student.objects(email=form.email.data).first()
        send_reset_email(student)
        flash("Please check your email for a password reset link.", "info")
        return redirect(url_for("login"))
    return render_template("request-reset.html", form=form)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated and not current_user.temp:
        return redirect(url_for("home"))
    student = Student.verify_reset_token(token)
    if student:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            if current_user.is_authenticated and current_user.temp:
                logout_user()
            student.password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
            student.save()
            flash("Password reset successfully. Please log in.", "success")
            return redirect(url_for("login"))
        return render_template("reset-password.html", form=form)
    flash("Invalid or expired token.", "warning")
    return redirect(url_for("request_reset"))


@app.route("/classroom", methods=['GET', "POST"])
@app.route("/", methods=['GET', "POST"])
def home():
    """Render the home page shell, as well as the initial questions."""
    # set up anonymous user - get questions, and save in database
    if current_user.is_anonymous:
        curr_lang = DEFAULT_LANGUAGE
        student_id = DEFAULT_TEMP_STUDENT_ID
    else:
        curr_lang = current_user.curr_study_lang
        student_id = str(current_user.id)

    questions = get_questions_all_lang(SUPPORTED_LANGUAGES, student_id)

    return render_template('home.html', curr_lang=curr_lang,
                           all_langs=SUPPORTED_LANGUAGES,
                           question=questions[curr_lang],
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
    logging.info(f"the student is anonymous? {str(current_user.is_anonymous)}")

    if request.method == "GET":
        # user changed the language
        requested_lang = request.args.get('language')

        if current_user.is_anonymous:
            # get the default question for the requested language
            question = get_queue_question(requested_lang,
                                          DEFAULT_TEMP_STUDENT_ID)
            # turn the question object into json and return it
            logging.info("language changed for untracked student")
            return question_obj_to_json(question, request_type=request.method)

        if not current_user.is_anonymous:
            # update document for logged-in student
            current_user.curr_study_lang = requested_lang
            current_user.save()
            logging.info("language saved for tracked student")
            # get id for the next question
            next_question_id = current_user.language_progress.\
                filter(language=current_user.
                       curr_study_lang)[0].question_queue[0]

    if request.method == "POST":
        # user answered a question, so save it
        if current_user.is_anonymous:
            # to save, we need a Student document, so create one and
            # log student in (to save subsequent questions)
            temp_student = create_temp_student()
            temp_student.curr_study_lang = request.form.get('language')
            temp_student.save()
            login_user(temp_student)
            logging.info("logged in temp student")
            logging.info(f"temp student id: {str(current_user.id)}")

        if current_user.temp:
            logging.info(f"answer received: {request.form}")
            # update the dictionary with new student id
            # make mutable shallow copy of ImmutableMultiDict
            answer_dict = request.form.copy()
            answer_dict["student_id"] = str(current_user.id)
            logging.info(f"answer after updating student id: {answer_dict}")
            save_answer(**answer_dict)
            current_user.num_questions_answered += 1
            current_user.last_active = datetime.now(tz=pytz.UTC)
            current_user.save()
            logging.info(f"parameters passed to save_answer(): {answer_dict}")
            logging.info("answer saved for temp student")

        if not current_user.temp:
            logging.info(request.form)
            save_answer(**request.form)
            logging.info("answer saved for logged in student")

        # need to query in db to get the current state of student,
        # because it has been updated, but current_user
        # does not refresh until page reload
        student = Student.objects(id=current_user.id).first()
        logging.info(f"student id returned from query: {student.id}")
        # get id for the next question
        next_question_id = student.language_progress.\
            filter(language=current_user.curr_study_lang)[0].question_queue[0]

    next_question = Question.objects(id=next_question_id).first()

    logging.info(f"Next word: {next_question.word}")

    # we'll relay this value back to client
    previous_question_language = request.form.get("language")

    # turn the question object into json and return it
    if current_user.temp:
        # for temp student, include student_id, so it can be updated
        return question_obj_to_json(next_question, request_type=request.method,
                                    student_id=str(current_user.id),
                                    prev_q_lang=previous_question_language)

    return question_obj_to_json(next_question, request_type=request.method,
                                prev_q_lang=previous_question_language)
