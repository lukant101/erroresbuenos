"""Export functions: create_student and create_temp_student."""

import uuid
import mongoengine
from bson import ObjectId
from qwell.db_model import Student
from qwell.helpers.more_questions import get_default_questions
from qwell.constants import SUPPORTED_LANGUAGES


def create_student(email, username, first_name, last_name, password, temp):
    """Create and return new Student object; also, save to database."""
    student = Student(
        email=email,
        username=username,
        alt_id=ObjectId(),
        first_name=first_name,
        last_name=last_name,
        password=password,
        temp=temp
    )

    student.save()

    return student.id


def create_temp_student():
    """Create and return a temporary Student object; also save to database.

    Until a student registers, his/her information is saved using a temporary
    Student document. This document is generated the first time the student
    answers a question.

    Once the student registers, the Student document is updated.
    """
    random_string = str(uuid.uuid4())[7:27]
    student = Student(
        # username must be no more than 20 characters
        username=random_string,
        email=random_string + "@fantasy.com",
        alt_id=ObjectId(),
        temp=True
    )

    # save the document; if the username not unique, generate new one and retry
    try:
        student.save()
    except mongoengine.NotUniqueError:
        while True:
            random_string = str(uuid.uuid4())[7:27]
            student.username = random_string
            student.email = random_string + "@fantasy.com"
            try:
                student.save()
                break
            except mongoengine.NotUniqueError:
                continue

    # add default questions to the queues in Student document
    for lang in SUPPORTED_LANGUAGES:
        get_default_questions(lang, student.id)

    return student
