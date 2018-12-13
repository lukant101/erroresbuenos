import mongoengine
from bson.objectid import ObjectId
import sys

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Student, Question, StudentHistory


def print_doc(db_in, collection_class, doc_id):

    mongoengine.connect(db_in, host="localhost", port=27017)

    # query_args = {"_id": ObjectId(doc_id)}
    # query_args = {"username": "lantos"}
    # results_iter = Student.objects(__raw__=query_args)
    results_iter = collection_class.objects(id=doc_id)

    for result in results_iter:
        print("Document: ")
        # print("Document: ", result.username)
        for fld in result._fields.keys():
            try:
                print(f"{fld}: {getattr(result, fld)}")
            except UnicodeEncodeError:
                # print() fails when the script runs in Atom - it uses
                # console encoding cp1252, not utf-8
                # so use bytes objects to represent strings
                # and output to sys.stdout.buffer
                sys.stdout.buffer.write(f"{fld}: {getattr(result, fld)}".encode())
                sys.stdout.buffer.write("\n".encode())


if __name__ == "__main__":
    collection_class = StudentHistory
    doc_id = "5bb7af3afde08a509c8d8284"
    db_in = "lalang_db"
    print_doc(db_in, collection_class, doc_id)
