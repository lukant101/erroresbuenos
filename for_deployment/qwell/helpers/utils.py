"""Export various utility functions.

Export:
question_obj_to_json
dict_to_question_obj
is_safe_url
"""

from bson.objectid import ObjectId
import sys
import json
import copy
from urllib.parse import urlparse, urljoin
from flask import request
from qwell.db_model import Question, Student, StudentHistory

def is_safe_url(target):
    ref_url = urlparse(request.url_root)
    test_url = urlparse(urljoin(request.url_root, target))

    return (test_url.scheme in ("http", "https")
            and ref_url.netloc == test_url.netloc)


def question_obj_to_json(question_obj, *, request_type, student_id,
                         prev_q_lang=None, prod_signup=False):
    """Take Question object and return it in json representation.

    Arguments:
    Question instance
    request_type:
        "GET", "POST" ring)
        -- flag to indicate whether the JSON response
        is a reply to a GET or POST request

    student_id: string

    Return:
    Question object in JSON format, with request_type and student_id appended.
    """
    q_json = {}
    q_fields_iter = question_obj._fields.keys()
    for f in q_fields_iter:
        if f == "id":
            # cast ObjectId as string so we get the hexidecimal string
            q_json[f] = str(getattr(question_obj, f))
        else:
            q_json[f] = getattr(question_obj, f)

    q_json["request_type"] = request_type

    q_json["student_id"] = student_id

    if prev_q_lang:
        q_json["prev_q_lang"] = prev_q_lang

    q_json["prod_signup"] = prod_signup
    
    return json.dumps(q_json, ensure_ascii=False)


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
    # question_id = ObjectId("5bc56c47fde08a1908df5987")
    # gotować
    # question_id: 5bc56c47fde08a1908df5a24
    # truskawka
    question_id = ObjectId("5bc56c47fde08a1908df5a24")
    question = Question.objects(id=question_id).first()
    q_as_json = question_obj_to_json(question, request_type="POST")
    print(q_as_json)
    print(type(q_as_json))
