import datetime
import pytz
from lalang import db

supported_languages = ["english", "spanish", "polish"]


class Question(db.Document):
    # MongoDB will use this class name as the collection name
    description = db.StringField(default="word flashcard",
                                 max_length=20)
    skill = db.StringField(required=True, max_length=20)
    language = db.StringField(required=True, max_length=20,
                              choices=supported_languages)
    word = db.StringField(max_length=30)
    part_of_speech = db.StringField(max_length=25)
    audio_files = db.StringField(max_length=200)
    image_files = db.StringField(max_length=200)

    # allow subclasses for other question types
    meta = {'allow_inheritance': True}


class Student(db.Document):
    email = db.EmailField(required=True, unique=True)
    username = db.StringField(unique=True, max_length=20)
    first_name = db.StringField(max_length=30)
    last_name = db.StringField(max_length=30)
    # make sure to store  password hash in the database
    password = db.StringField(max_length=30)
    app_language = db.StringField(required=True,
                                  default="english", max_length=20)
    # student's proficiency in each language, expressed as a percentage
    language_proficiency = db.DictField(field=db.DecimalField(
        min_value=0, max_value=100))
    last_studied = db.DictField(field=db.DateTimeField(
        default=datetime.datetime.now(tz=pytz.UTC)))
    # pairs of: language, list of questions
    question_queue = db.DictField(field=db.ListField(
        field=db.ObjectIdField()))
    answered_wrong_stack = db.DictField(field=db.ListField(
        field=db.ObjectIdField()))
    answered_corr_stack = db.DictField(field=db.ListField(
        field=db.ObjectIdField()))


class StudentHistory(db.Document):
    student_id = db.ObjectIdField()
    question_id = db.ObjectIdField()
    language = db.StringField(required=True, max_length=20,
                              choices=supported_languages)
    answer = db.StringField()
    # need to see how to pass boolean from jquery to back-end
    # answer_correct = db.BooleanField(default=False)
    answer_correct = db.BooleanField(default=False)
    audio_answer_correct = db.BooleanField(default=False)
    attempts_count = db.IntField(default=0)
    last_attempted = db.DateTimeField(
        default=datetime.datetime.now(tz=pytz.UTC))
