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

from lalang.db_model import Question


def question_obj_to_json(question_obj):
    """Take Question object and return it in json representation."""
    q_json = {}
    q_json_iter = question_obj._fields.keys()
    for k in q_json_iter:
        q_json[k] = str(getattr(question_obj, k))
    return json.dumps(q_json)


def dict_to_question_obj(question_as_dict):
    """Take question represented as dictionary and return Question object."""
    # making a copy in order to not lose email key in dict passed as argument
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
    question_id = ObjectId("5ba13cd3fde08a0ce81856b5")
    question = Question.objects(id=question_id).first()
    q_as_json = question_obj_to_json(question)
    print(q_as_json)
    print(type(q_as_json))
