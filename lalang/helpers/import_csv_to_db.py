""" Copy questions from a csv file to a MongoDB database"""
import mongoengine
import csv
import sys
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from db_model import Question

print(sys.path)
print(os.getcwd())

db_name = input("What is the name of the database you want to add\
 the questions to? ")

mongoengine.connect(db_name, host="localhost", port=27017)


csv_file_name = input("Enter the csv file name, including the full path: ")
language_in = input("Enter the language of the data: ")


with open(csv_file_name) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    column_names = next(csv_reader)

with open(csv_file_name) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=",")
    for row in csv_reader:
        question = Question(
            description="word flashcard",
            skill="Vocabulary",
            language=language_in,
            word=row[column_names[0]],
            part_of_speech=row[column_names[1]],
            audio_files=row[column_names[2]],
            image_files=row[column_names[3]]
        )

        question.save()
