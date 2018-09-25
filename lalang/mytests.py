import mongoengine
import os
# import import_csv_to_db
# import get_template_questions


class Student(mongoengine.Document):
    first_name = mongoengine.StringField()
    last_name = mongoengine.StringField()
    grade = mongoengine.IntField()


class Thing():
    name = "lamp"
    colour = "green"

    def __init__(self, price):
        self.price = price


if __name__ == "__main__":
    mydict = get_template_questions()
    print(mydict)
