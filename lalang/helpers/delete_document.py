"""Delete questions from a database."""

"""
Matching criteria for the questions to be deleted are hard-coded at the moment.
Also, deletion of every question needs to be confirmed one at a times
- no batch deletion.
"""


import mongoengine
import csv
import sys
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")
# sys.path.append("C:\\Users\\Lukasz\\Python")

from db_model import Question
# from ErroresBuenos.db_model import Question

db_in = input("Which database should the questions be deleted from? ")
mongoengine.connect(db_in, host="localhost", port=27017)


# DUPLICATE DON'T USE IT - iść
# darn_record = Question.objects(language="Polish", word="duży")

del_match = {"word": {"$regex": "^DU"}, "language": "Polish"}
del_records_iter = Question.objects(__raw__=del_match)
num_del_records = del_records_iter.count()
if num_del_records > 0:
    deleted_counter = 0
    print(num_del_records, " records found for deletion.")
    for del_record in del_records_iter:
        del_record_contents = (f"{{\"word\": \"{del_record.word}\", \"description\": \"{del_record.description}\", "
                               f"\"skill\": \"{del_record.skill}\", \"language\": \"{del_record.language}\"}}")

        del_confirm = input("Do you want to delete record: "
                            f"{del_record_contents}? ")
        input_choices = {"yes", "y", "1"}
        if del_confirm.lower() in input_choices:
            del_record.delete()
            deleted_counter += 1
            print("The following document has been deleted: ",
                  f"{{\"word\": \"{del_record.word}\"}}")
        else:
            print("Deletion not executed")
        if deleted_counter > 0:
            print(deleted_counter, " record(s) deleted.")
        else:
            print("No records deleted")
else:
    print("No records found for deletion.")
