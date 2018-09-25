from lalang import db


class Question(db.Document):
    # MongoDB will use this class name as the collection name
    description = db.StringField(default="word flashcard",
                                 max_length=20)
    skill = db.StringField(required=True, max_length=20)
    language = db.StringField(required=True, max_length=20)
    word = db.StringField(max_length=30)
    part_of_speech = db.StringField(max_length=25)
    audio_files = db.StringField(max_length=200)
    image_files = db.StringField(max_length=200)

    def output_field(self, fld):
        print(self.fld)


class TestData(db.Document):
    # MongoDB will use this class name as the collection name
    description = db.StringField(default="word flashcard",
                                 max_length=20)
    skill = db.StringField(required=True, max_length=20)
    language = db.StringField(required=True, max_length=20)
    word = db.StringField(max_length=30)
    part_of_speech = db.StringField(max_length=25)
    audio_files = db.StringField(max_length=200)
    image_files = db.StringField(max_length=200)


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
