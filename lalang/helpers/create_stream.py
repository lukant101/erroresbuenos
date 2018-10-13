"""Create a series of default questions, to be presented to students.

Get questions from database and save them in a json file.
The file stores a list of json strings representing the questions.
"""

import mongoengine
import csv
import sys
import os
import random
import json

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question
from lalang.helpers.utils import question_obj_to_json


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

os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/default")


with open(f"stream_default_{language_in.lower()}.json", "w") as f:
    f.write("[")

    for question in questions:
        # q_json = {}
        # q_json_iter = question._fields.keys()
        # for k in q_json_iter:
        #     q_json[k] = str(getattr(question, k))
        q_json = question_obj_to_json(question)

        json.dump(q_json, f, ensure_ascii=False)

        # separate the question documents in the list
        f.write(", ")

        print(question.word)

    # move cursor back to the end of last question document, so we can
    # overwrite the last comma and close the list
    f.seek(f.tell()-2)
    f.write("]")
