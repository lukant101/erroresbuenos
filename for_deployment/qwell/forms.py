from flask_wtf import FlaskForm
from flask import flash, redirect
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (Email, Length, DataRequired,
                                ValidationError, EqualTo)
from wtforms.widgets import PasswordInput
from qwell.db_model import Student


class StudentRegister(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("User Name",
                           validators=[Length(min=2, max=20, message="User name\
                            has to be between 2 and 20 characters long."),
                                       DataRequired()])
    first_name = StringField("First Name", validators=[Length(max=30)])
    last_name = StringField("Last Name", validators=[Length(max=30)])
    password = PasswordField("Password",
                             validators=[Length(min=6, max=30, message="Password must be between 6 and 30 \
                             characters long"), DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])

    submit = SubmitField("Sign me up!")

    def validate_email(self, email):
        # check that email is unique
        student = Student.objects(email=email.data.lower()).first()
        if student:
            raise ValidationError("An account with this email \
            address already exists.")

    def validate_username(self, username):
        # check that username is unique
        student = Student.objects(username=username.data.lower()).first()
        if student:
            raise ValidationError("An account with this username \
            already exists.")


class StudentLogin(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log me in")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")

    def validate_email(self, email):
        # check that email exists
        student = Student.objects(email=email.data.lower()).first()
        if not student:
            raise ValidationError("No such account exists. Please register.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password",
                             validators=[Length(min=6, max=30, message="Password must be between 6 and 30 \
                             characters long"), DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])
    submit = SubmitField("Reset Password")


class AccountUpdateForm(FlaskForm):
    email = StringField("Email", validators=[Email()])

    username = StringField("User Name",
                           validators=[Length(max=20, message="User name\
                            has to be between 2 and 20 characters long.")])

    first_name = StringField("First Name", validators=[Length(max=30)])
    last_name = StringField("Last Name", validators=[Length(max=30)])

    submit = SubmitField("Update my account")

    def validate_email(self, email):
        if email.data and (email.data.lower() != current_user.email):
            # check that email is unique
            student = Student.objects(email=email.data.lower()).first()
            if student:
                raise ValidationError("An account with this email \
                address already exists.")

    def validate_username(self, username):
        if len(username.data) == 1:
            raise ValidationError("User name has to be between 2 and 20\
            characters long.")
        elif username.data and (username.data.lower() != current_user.username):
            # check that username is unique
            student = Student.objects(username=username.data.lower()).first()
            if student:
                raise ValidationError("An account with this username \
                already exists.")


class PasswordUpdateForm(FlaskForm):
    password = PasswordField("Password",
                             validators=[Length(min=6, max=30, message="Password must be between 6 and 30 \
                             characters long"), DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password")])

    submit = SubmitField("Update my password")
