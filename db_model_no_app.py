import mongoengine
import csv


class Question(mongoengine.Document):
    description = mongoengine.StringField(default="word flashcard",
                                          max_length=20)
    skill = mongoengine.StringField(required=True, max_length=20)
    language = mongoengine.StringField(required=True, max_length=20)
    word = mongoengine.StringField(max_length=30)
    part_of_speech = mongoengine.StringField(max_length=25)
    audio_files = mongoengine.StringField(max_length=200)
    image_files = mongoengine.StringField(max_length=200)


class Student(mongoengine.Document):
    email = mongoengine.EmailField(required=True)
    username = mongoengine.StringField(unique=True, max_length=20)
    first_name = mongoengine.StringField(max_length=30)
    last_name = mongoengine.StringField(max_length=30)
    # make sure to store hashed password in the database
    password = mongoengine.StringField(max_length=30)
    app_language = mongoengine.StringField(required=True, max_length=20)
    # student's proficiency in each language, expressed as a percentage
    language_proficiency = mongoengine.DictField()
    # pairs of: language, sequence of questions
    study_streams = mongoengine.DictField()


class StudentHistory(mongoengine.Document):
    student_id = mongoengine.ObjectIdField()
    answer = mongoengine.StringField()
    answer_correct = mongoengine.BooleanField()
    audio_answer_correct = mongoengine.BooleanField()
    attempts_count = mongoengine.IntField(default=0)
    last_attempted = mongoengine.DateTimeField()


mongoengine.connect("mongoengine_test", host="localhost", port=27017)

csv_file_name = input("Enter the csv file name, including the full path:")
language_in = input("Enter the language of the data:")


with open(csv_file_name) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    column_names = next(csv_reader)

with open(csv_file_name) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=",")
    for row in csv_reader:
        questions = Question(
            description="word flashcard",
            skill="Vocabulary",
            language=language_in,
            word=row[column_names[0]],
            part_of_speech=row[column_names[1]],
            audio_files=row[column_names[2]],
            image_files=row[column_names[3]]
        )

        questions.save()
