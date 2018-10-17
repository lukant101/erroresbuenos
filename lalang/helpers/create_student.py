"""Export functions: create_student and create_temp_student."""

import mongoengine
import sys
import uuid

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Student


def create_student(email, username, first_name, last_name, password, temp):
    """Create and return new Student object; also, save to database."""
    student = Student(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        temp=temp
    )

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    student.save()

    return Student.objects(username=student.username).first().id


def create_temp_student():
    """Create and return a temporary Student object; also save to database.

    Until a student registers, his/her information is saved using a temporary
    Student document. This document is generated the first time the student
    answers a question.

    Once the student registers, the Student document is updated.
    """
    student = Student(
        username=uuid.uuid4(),
        temp=True
    )

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    # save the document; if the username not unique, generate new one and retry
    try:
        student.save()
    except mongoengine.ValidationError:
        while True:
            student.username = uuid.uuid4()
            try:
                student.save()
                break
            except mongoengine.ValidationError:
                continue

    return Student.objects(username=student.username).first().id


if __name__ == "__main__":
    # need to comment out from lalang import routes in __init__.py
    # before running
    # create_student("lantos101@gmail.com", username="lantos",
    #                first_name="Lukasz", last_name="Antos",
    #                password="slowko", temp=False)
    create_student("denise@gmail.com", username="denisepach",
                   first_name="Denise", last_name="Pacheco",
                   password="palabra", temp=False)
