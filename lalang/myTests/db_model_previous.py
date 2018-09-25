import mongoengine


class Question(mongoengine.Document):
    # MongoDB will use this class name as the collection name
    description = mongoengine.StringField(default="word flashcard",
                                          max_length=20)
    skill = mongoengine.StringField(required=True, max_length=20)
    language = mongoengine.StringField(required=True, max_length=20)
    word = mongoengine.StringField(max_length=30)
    part_of_speech = mongoengine.StringField(max_length=25)
    audio_files = mongoengine.StringField(max_length=200)
    image_files = mongoengine.StringField(max_length=200)

    def output_field(self, fld):
        print(self.fld)


class TestData(mongoengine.Document):
    # MongoDB will use this class name as the collection name
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
