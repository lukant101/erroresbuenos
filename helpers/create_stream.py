"""Create a series of questions, to be presented to students by default."""

import mongoengine
import csv
import sys
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")
# sys.path.append("C:\\Users\\Lukasz\\Python")

from db_model import Question
# from ErroresBuenos.db_model import Question


print(sys.path)
print(os.getcwd())

mongoengine.connect("lalang_db", host="localhost", port=27017)

# query to generate options for user input
# language_in = input("What language are these questions for?")
# type_in = input("What is the type of questions you would like?")
# num_questions = input("How many questions would you like?")

total_questions = Question.objects(language="English",
                                   description="word flashcard").count()
print("Total number of such questions: ", total_questions)

question_list = []

# pick random numbers ('total_questions' of them)
# between 1 and num_questions

question_list_steps = []

res3 = Question.objects(language="English", description="word flashcard")[:5]
for result in res3:
    print(result.image_files)
