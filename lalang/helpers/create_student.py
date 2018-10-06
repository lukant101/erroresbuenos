import mongoengine
import sys
import uuid

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Student


def create_student(email, username, first_name, last_name, password, temp):

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

    student = Student(
        username=uuid.uuid4()
        temp=True
    )

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    # save the document; if the username not unique, generate new one and retry
    try:
        student.save()
    except ValidationError:
        while True:
            student.username = uuid.uuid4()
            try:
                student.save()
                break
            except ValidationError:
                continue

    return Student.objects(username=student.username).first().id


if __name__ == "__main__":
    create_student("denise@gmail.com", "denispach",
                   "Denise", "Pacheco", "pachpalabra", False)
