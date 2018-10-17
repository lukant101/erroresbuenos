"""Export various utility functions.

Export:
question_obj_to_json
dict_to_question_obj
"""

from bson.objectid import ObjectId
import sys
import json
import copy

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question, Student


def question_obj_to_json(question_obj):
    """Take Question object and return it in json representation."""
    q_json = {}
    q_fields_iter = question_obj._fields.keys()
    for f in q_fields_iter:
        if f == "id":
            # cast ObjectId as string so we get the hexidecimal string
            q_json[f] = str(getattr(question_obj, f))
        else:
            q_json[f] = getattr(question_obj, f)
    return json.dumps(q_json, ensure_ascii=False)
    # return question_obj.word


def dict_to_question_obj(question_as_dict):
    """Take question represented as dictionary and return Question object."""
    q_obj = Question()
    for k, v in question_as_dict.items():
        setattr(q_obj, k, v)
    return q_obj


def dict_to_student_obj(student_as_dict):
    """Take student represented as dictionary and return Student object."""
    # making a copy in order to not lose email key in dict passed as argument
    student_as_dict_copy = copy.deepcopy(student_as_dict)
    email = student_as_dict_copy.pop("email")
    s_obj = Student(email=email)
    # student_as_dict no longer has key "email"
    for k, v in student_as_dict_copy.items():
        setattr(s_obj, k, v)
    return s_obj


if __name__ == "__main__":
    # question_id = ObjectId("5ba13cd3fde08a0ce81856b5")
    # skakać
    # question_id = ObjectId("5ba13d2cfde08a6a948a701f")
    # spaść
    question_id = ObjectId("5ba13d2cfde08a6a948a7015")
    question = Question.objects(id=question_id).first()
    q_as_json = question_obj_to_json(question)
    print(q_as_json)
    print(type(q_as_json))
