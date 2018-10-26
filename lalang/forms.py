from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (Email, Length, DataRequired,
                                ValidationError, EqualTo)
from lalang.db_model import Student


class StudentRegister(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("User name",
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
