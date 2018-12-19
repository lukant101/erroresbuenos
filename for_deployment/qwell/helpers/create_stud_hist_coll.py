"""Export function: create_stud_hist_coll."""

import mongoengine
import sys
from bson.objectid import ObjectId
import datetime
import pytz
from qwell.db_model import StudentHistory, Question


def create_stud_hist_coll():
    """If the StudentHistory collection does not exist, create it."""

    # default student - lukasz:
    student_id = "5bb6b5bffde08a535c580608"
    # default question:
    question = Question.objects.first()

    stud_hist = StudentHistory(
        student_id=ObjectId(student_id),
        question_id=ObjectId(question.id),
        language=question.language.lower(),
        answer=["love studying languages"],
        last_attempted=datetime.datetime.now(tz=pytz.UTC)
    )

    stud_hist.save()
