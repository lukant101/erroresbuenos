"""Create Question documents and save them to a database.

The module does not export anything.
"""
import mongoengine
import csv
import sys
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question


def add_questions_to_db(db_name, language, filename):
    """Copy questions from a csv file to a MongoDB database."""
    print(sys.path)
    print(os.getcwd())

    # db_name = input("What is the name of the database you want to add\
    #  the questions to? ")
    db_name = db_name

    mongoengine.connect(db_name, host="localhost", port=27017)

    # csv_file_name = input("Enter the csv file name,
    # including the full path: ")
    csv_file_name = filename
    # language_in = input("Enter the language of the data: ")
    language_in = language

    with open(csv_file_name, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        column_names = next(csv_reader)

    with open(csv_file_name, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            question = Question(
                description="word flashcard",
                skill="Vocabulary",
                language=language_in.lower(),
                word=row[column_names[0]],
                part_of_speech=row[column_names[1]],
                audio_files=row[column_names[2]],
                image_files=row[column_names[3]]
            )

            question.save()


if __name__ == "__main__":
    # need to comment out from lalang import routes in __init__.py
    # before running
    filename = "C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/flashcards_polish_deck1.csv"
    add_questions_to_db("lalang_db", "polish", filename)
