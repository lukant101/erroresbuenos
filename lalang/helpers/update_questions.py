"""Script to update Question documents in the database.

If there is no such question in the db, it is created.

Input: csv file
"""
import mongoengine
import csv
import sys
from os.path import splitext

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question
from create_question import create_question


def update_questions(db_name, language, filename):
    """Update questions from a csv file to a MongoDB database."""

    update_counter = 0
    added_counter = 0


db.question-backup.renameCollection("question-backup2")

mongoengine.connect(db_name, host="localhost", port=27017)

with open(filename, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            questions = Question.objects(language=language,
                                         source_id=row["Source_Id"])

            if questions.count() == 0:
                create_question(language, odict=row)
                added_counter += 1

            for question in questions:
                question.word = row["Word"]
                question.part_of_speech = row["Part_of_Speech"]
                question.source_id = row["Source_Id"]
                question.audio = row["Audio"].split(", ")

                if row["Child_Appropriate"].lower() == "no":
                    question.child_appropriate = False
                else:
                    question.child_appropriate = True

                # css.DictReader escapes newline characters, so split with:
                # '\\n '
                question.alternative_answers = row["Alternative_Answer"].split('\\n ')

                question.part_of_speech = row["Part_of_Speech"]

                # preparing info for the first image
                fileroot, ext = splitext(row["Photo1"])
                ext = ext.lstrip(".")

                # updating the image array
                question.images = []
                question.images.append([fileroot, ext, float(row["Photo1_ar"])])

                # if there are more images, update them
                for i in [1, 2, 3]:
                    if row[f"Photo{i+1}"]:
                        fileroot, ext = splitext(row[f"Photo{i+1}"])
                        ext = ext.lstrip(".")
                        question.images.append([fileroot, ext,
                                                float(row[f"Photo{i+1}_ar"])])

                question.save()
                update_counter += 1

        print(f"Total records updated: {update_counter} for {language}")
        print(f"Total new records added: {added_counter} for {language}")


if __name__ == "__main__":
    # need to comment out from lalang import routes in __init__.py
    # before running
    languages = ["en", "es", "pl"]
    lang_dict = {"en": "english", "es": "spanish", "pl": "polish"}
    for l in languages:
        filename = ("C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/"
                    "flashcards_{}.csv".format(l))
        update_questions("lalang_db", lang_dict[l], filename)
