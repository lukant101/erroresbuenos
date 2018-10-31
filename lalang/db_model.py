"""Define data model for the app.

Exports classes:
Question
Student
LanguageProgress - embedded document in Student
StudentHistory
"""
import datetime
import pytz
from lalang import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
import logging
from lalang.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a")


class Question(db.Document):
    """Store questions for all languages.

    The document / class has all the information needed to pose a question.
    """

    description = db.StringField(default="word flashcard",
                                 max_length=20)
    skill = db.StringField(required=True, max_length=20)
    language = db.StringField(required=True, max_length=20,
                              choices=SUPPORTED_LANGUAGES)
    word = db.StringField(max_length=30)
    part_of_speech = db.StringField(max_length=25)
    audio_files = db.StringField(max_length=200)
    image_files = db.StringField(max_length=200)

    # allow subclasses for other question types
    # meta = {'allow_inheritance': True}


class LanguageProgress(db.EmbeddedDocument):
    """Store information about student's studies in a given language.

    The embedded document is stored in a list of embedded documents
    within the Student document (the list represents all languages that
    the student has done exercises for).
    """

    language = db.StringField(required=True, max_length=20,
                              choices=SUPPORTED_LANGUAGES)
    # student's proficiency in each language, expressed as a percentage
    language_proficiency = db.DecimalField(min_value=0,
                                           max_value=100, default=0)
    last_studied = db.DateTimeField(default=datetime.datetime.now(tz=pytz.UTC))
    question_queue = db.ListField(field=db.ObjectIdField())
    answered_wrong_stack = db.ListField(field=db.ObjectIdField())
    answered_corr_stack = db.ListField(field=db.ObjectIdField())


@login_manager.user_loader
def load_student(student_alt_id):
    # query returns None if document not found
    return Student.objects(alt_id=student_alt_id).first()


class Student(db.Document, UserMixin):
    """Store information for each student.

    Information regarding student's studies in a particular language
    is stored in a list of embedded documents.
    """

    # alt_id is needed for Remember Me cookie; otherwise _id would be used
    alt_id = db.ObjectIdField(unique=True, required=True)
    email = db.EmailField(unique=True)
    username = db.StringField(required=True, unique=True, max_length=20)
    first_name = db.StringField(max_length=30)
    last_name = db.StringField(max_length=30)
    # make sure to store  password hash in the database
    password = db.StringField()
    app_language = db.StringField(required=True,
                                  default="english", max_length=20)
    curr_study_lang = db.StringField(required=True,
                                     default=DEFAULT_LANGUAGE)
    language_progress = db.EmbeddedDocumentListField(LanguageProgress)
    # fields for temp students only
    temp = db.BooleanField(default=True)
    last_active = db.DateTimeField(default=datetime.datetime.
                                   now(tz=pytz.UTC))
    num_questions_answered = db.IntField(default=0)
    meta = {'indexes': ["alt_id"]}

    # need to override UserMixin get_id, so that we pass
    # alt_id to load_student, instead of id/_id
    def get_id(self):
        return str(self.alt_id)


class StudentHistory(db.Document):
    """Store data about a question answered by a student.

    Every time a student answers a question, a new StudentHistory document
    is generated.
    """

    student_id = db.ObjectIdField()
    question_id = db.ObjectIdField()
    language = db.StringField(required=True, max_length=20,
                              choices=SUPPORTED_LANGUAGES)
    answer = db.ListField(field=db.StringField())
    answer_correct = db.BooleanField(default=False)
    audio_answer_correct = db.BooleanField(default=False)
    attempts_count = db.IntField(default=0)
    last_attempted = db.DateTimeField(
        default=datetime.datetime.now(tz=pytz.UTC))
