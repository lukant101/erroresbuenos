"""Handle requests for all endpoints of the website."""

from flask import render_template, request, redirect, flash, url_for, abort
from bson import ObjectId
from datetime import datetime
import pytz
from flask_login import (login_user, current_user, logout_user, login_required,
                         fresh_login_required)
from qwell import app, bcrypt, mail
from qwell.helpers.more_questions import get_question
from qwell.helpers.save_answer import save_answer
from qwell.helpers.create_student import create_temp_student
from qwell.constants import (SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
                              DEFAULT_TEMP_STUDENT_ID,
                              SUPPORTED_LANGUAGES_ABBREV, EMAIL_SENDER)
from qwell.helpers.utils import question_obj_to_json, is_safe_url
from qwell.forms import (StudentRegister,
                          StudentLogin, RequestResetForm, ResetPasswordForm,
                          AccountUpdateForm, PasswordUpdateForm)
from qwell.db_model import Student, Question
from qwell.helpers.gtranslate import google_translate
from qwell.helpers.send_reset_email import send_reset_email


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
                return redirect(url_for("home"))

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
    """Render the home page shell, as well as the first question."""
    # set up anonymous user - get questions, and save in database
    if current_user.is_anonymous:
        curr_lang = DEFAULT_LANGUAGE
        student_id = DEFAULT_TEMP_STUDENT_ID
    else:
        curr_lang = current_user.curr_study_lang
        student_id = str(current_user.id)

    question, side = get_question(curr_lang, student_id)

    return render_template("home.html", curr_lang=curr_lang,
                           all_langs=SUPPORTED_LANGUAGES,
                           question=question, side=side,
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
    if request.method == "GET":
        # user changed the language
        requested_lang = request.args.get('language')

        if current_user.is_anonymous:
            student_id = DEFAULT_TEMP_STUDENT_ID
            # get the default question for the requested language
            question, side = get_question(requested_lang, student_id)
            # turn the question object into json and return it

        if not current_user.is_anonymous:
            student_id = current_user.id
            # update document for logged-in student
            current_user.curr_study_lang = requested_lang
            current_user.save()

            # get the next question and return it
            question, side = get_question(requested_lang,
                                          current_user.id)

        return question_obj_to_json(question, question_side=side,
                                    student_id=student_id, request_type="GET")

    if request.method == "POST":
        question_language = request.form.get('language')
        # user answered a question, so save it
        if current_user.is_anonymous:
            # to save, we need a Student document, so create one and
            # log student in (to save subsequent questions)
            temp_student = create_temp_student()
            temp_student.curr_study_lang = question_language
            temp_student.save()
            login_user(temp_student)

        if current_user.temp:
            # update the dictionary with new student id
            # make mutable shallow copy of ImmutableMultiDict
            answer_dict = request.form.copy()
            answer_dict["student_id"] = str(current_user.id)
            save_answer(**answer_dict)
            current_user.num_questions_answered += 1
            if current_user.num_questions_answered >= 5 and \
                    (current_user.num_questions_answered % 5) == 0:
                prod_signup = True
            else:
                prod_signup = False

            current_user.last_active = datetime.now(tz=pytz.UTC)
            current_user.save()

        if not current_user.temp:
            save_answer(**request.form)
            prod_signup = False

        # get the next question in the same language as the answer
        question, side = get_question(question_language,
                                      current_user.id)

        # return the question object and other info as json
        return question_obj_to_json(question, question_side=side,
                                    student_id=current_user.id,
                                    request_type="POST",
                                    prev_q_lang=question_language,
                                    prod_signup=prod_signup)


@app.route("/translate", methods=["GET", "POST"])
def translate():
    input_text = request.form.get("input_text")
    input_language = request.form.get("input_language")
    if input_language == "english":
        target_language = "fr"
    else:
        target_language = "en"
    return google_translate(input_text, target_lang=target_language,
                            source_lang=SUPPORTED_LANGUAGES_ABBREV.
                            get(input_language))


@fresh_login_required
@app.route("/account", methods=["GET", "POST"])
def account():
    if not current_user.is_authenticated or \
            (current_user.is_authenticated and current_user.temp):
        return redirect(url_for("home"))
    if current_user.is_authenticated and not current_user.temp:
        form = AccountUpdateForm()

        if form.validate_on_submit() and not current_user.temp:
            if form.email.data:
                current_user.email = form.email.data.lower()
            if form.username.data:
                current_user.username = form.username.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.save()
            flash(f"The account for {form.email.data} \
            has been updated successfully.", "success")
            return redirect(url_for("account"))
        elif request.method == "GET":
            form.email.data = current_user.email
            form.username.data = current_user.username
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name

    return render_template("student-account.html", form=form)


@fresh_login_required
@app.route("/password-update", methods=["GET", "POST"])
def password_update():
    if not current_user.is_authenticated or \
            (current_user.is_authenticated and current_user.temp):
        return redirect(url_for("home"))
    if current_user.is_authenticated and not current_user.temp:
        form = PasswordUpdateForm()

        if form.validate_on_submit() and not current_user.temp:
            hash_password = bcrypt.generate_password_hash(
                form.password.data).decode("utf-8")
            current_user.password = hash_password
            current_user.save()
            flash(f"The password for {current_user.email} \
            has been updated successfully.", "success")
            return redirect(url_for("account"))

    return render_template("password-update.html", form=form)
