"""Script to update Question documents in the database.

If there is no such question in the db, it is created.

Input: csv file
"""
import mongoengine
import csv
import sys
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question
from lalang import create_question


def update_questions(db_name, language, filename):
    """Update questions from a csv file to a MongoDB database."""

    update_counter = 0

    mongoengine.connect(db_name, host="localhost", port=27017)

    with open(filename, encoding="utf8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            questions = Question.objects(language=language,
                                         source_id=row["Source_Id"])

            if questions.count() == 0:
                create_question(row)

            for question in questions:
                question.source_id = row["Source_Id"]
                question.audio = row["Audio"].split(".")
                question.audio.pop()

                if row["Child_Appropriate"].lower() == "no":
                    question.child_appropriate = False
                else:
                    question.child_appropriate = True

                alt_answers = row["Alternative_Answer"].split('\n')
                if len(alt_answers) > 1:
                    for i in range(1, len(alt_answers)):
                        alt_answers[i] = alt_answers[i].lstrip(" ")
                question.alternative_answers = alt_answers

                question.part_of_speech = row["Part_of_Speech"]

                # adding info for the first image
                no_img_field = False
                fileroot, ext = row["Photo1"].split(".")

                # add filename and aspect ratio for the image
                try:
                    question.images[0] = [fileroot, ext, row["Photo1_ar"]]
                except (AttributeError, IndexError):
                    no_img_field = True

                if not no_img_field:
                    # add info on additonal 3 images, if present
                    current_num_images = len(question.images)
                    for i in [1, 2, 3]:
                        if row[f"Photo{i+1}"]:
                            fileroot, ext = row[f"Photo{i+1}"].split(".")
                            # add info on filename and aspect ratio of the image
                            if i < current_num_images:
                                question.images[i] = [fileroot, ext,
                                                      float(row[f"Photo{i+1}_ar"])]
                            else:
                                question.images.append([fileroot, ext,
                                                        row[f"Photo{i+1}_ar"]])
                        else:
                            # no more images
                            break

                if no_img_field:
                    question.images = []
                    question.images.append([fileroot, ext,
                                            float(row["Photo1_ar"])])

                    # add info on additonal 3 images, if present
                    for i in [1, 2, 3]:
                        if row[f"Photo{i+1}"]:
                            fileroot, ext = row[f"Photo{i+1}"].split(".")
                            # add info on filename and aspect ratio of the image
                            question.images.append([fileroot, ext,
                                                    row[f"Photo{i+1}_ar"]])
                        else:
                            # no more images
                            break

                question.save()
                update_counter += 1

        print(f"Total records updated: {update_counter} for {language}")


if __name__ == "__main__":
    # need to comment out from lalang import routes in __init__.py
    # before running
    languages = ["eng", "esp", "pol"]
    lang_dict = {"eng": "english", "esp": "spanish", "pol": "polish"}
    for l in languages:
        filename = ("C:/Users/Lukasz/Python/ErroresBuenos/assets/questions/"
                    "flashcards_{}.csv".format(l))
        update_questions("lalang_db", lang_dict[l], filename)
