"""Delete embedded documents from a database.

Delete all LanguageProgress embedded documents stored in Student document -
filtering only by student id. This also deletes the list of embedded documents
-  the whole field "language_progress" gets deleted.

You will need to add the "language_progress" field back - currently not
implemented.

All parameters are hard-coded right now.

For this to work, you need to comment out "from lalang import routes"
in the __init__.py file for lalang package. Otherwise, new embedded documents
will be created upon the execution of this module.
"""
import mongoengine
import sys


sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Student


# db_in = input("Which database should the questions be deleted from? ")
db_in = "lalang_db"
student_id = "5bb6b5bffde08a535c580608"

mongoengine.connect(db_in, host="localhost", port=27017)

language_embed_docs = Student.objects(
    id=student_id).first().language_progress

num_del_records = language_embed_docs.delete()

language_embed_docs.save()

print(f"{num_del_records} embedded documents deleted for \
Student id: {student_id}")
