"""Create a series of default questions, to be presented to students."""

"""Get questions from database and save in a text file"""

import mongoengine
import csv
import sys
import os
import random

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")
# sys.path.append("C:\\Users\\Lukasz\\Python")

from db_model import Question


mongoengine.connect("lalang_db", host="localhost", port=27017)

# query to generate options for user input
language_in = input("What language are these questions for? ").capitalize()


num_questions = 5

# query_args = {"language": "Polish", "description": "word flashcard"}
query_args = {"language": f"{language_in}", "description": "word flashcard"}
results_iter = Question.objects(__raw__=query_args)
total_questions = results_iter.count()

print("Total number of questions: ", total_questions)

question_set = set()
while len(question_set) < num_questions:
    question_set.add(random.randint(0, total_questions))

question_list = sorted(list(question_set))

question_list_steps = []

question_list_steps.append(question_list[0])

for i in range(1, len(question_list)):
    question_list_steps.append(question_list[i]-question_list[i-1])

questions = []

for step in question_list_steps:
    for i in range(step):
        next(results_iter)
    questions.append(next(results_iter))

fields_list = tuple(Question._fields.keys())

question_dict = {}

print("Questions added: ")

os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/questions/templates")


with open(f"stream_default_{language_in.lower()}.txt", "w") as f:

    for question in questions:
        for fld in fields_list:
            question_dict[fld] = getattr(question, fld)

        f.write(str(question_dict)+"\n")
        if 'word' in fields_list:
            print(question_dict["word"], "")
