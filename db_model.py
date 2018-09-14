from flask_mongoengine import MongoEngine
from eb import db
import csv


class Question(db.Document):
    description = db.StringField(default="word flashcard", max_length=20)
    skill = db.StringField(required=True, max_length=20)
    language = db.StringField(required=True, max_length=20)
    word = db.StringField(max_length=30)
    part_of_speech = db.StringField(max_length=25)
    audio_files = db.ListField(field=db.StringField(max_length=50))
    image_files = db.ListField(db.StringField(max_length=50))


class Student(db.Document):
    email = db.EmailField(required=True)
    username = db.StringField(unique=True, max_length=20)
    first_name = db.StringField(max_length=30)
    last_name = db.StringField(max_length=30)
    # make sure to store hashed password in the database
    password = db.StringField(max_length=30)
    app_language = db.StringField(required=True, max_length=20)
    # student's proficiency in each language, expressed as a percentage
    language_proficiency = db.DictField()
    # pairs of: language, sequence of questions
    study_streams = db.DictField()


class StudentHistory(db.Document):
    student_id = db.ObjectIdField()
    answer = db.StringField()
    answer_correct = db.BooleanField()
    audio_answer_correct = db.BooleanField()
    attempts_count = db.IntField(default=0)
    last_attempted = db.DateTimeField()


csv_file_name = input("Enter the csv file name, including the full path:")
language = input("Enter the language of the data:")

Question.description = "word flashcard"
Question.skill = "Vocabulary"
Question.language = language

with open(csv_file_name) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    column_names = next(csv_reader)

with open(csv_file_name) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=",")
    for row in csv_reader:
        Question.word = row[column_names[0]]
        Question.part_of_speech = row[column_names[1]]
        Question.audio_files = row[column_names[2]]
        Question.image_files = row[column_names[3]]
        print(Question.word)
        print(Question.part_of_speech)
        print(Question.audio_files)
        print(Question.image_files)
