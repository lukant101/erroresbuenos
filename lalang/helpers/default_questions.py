import os
import json
from lalang.db_model import Question


def get_default_questions(supp_lang_list):
    """For the supported languages, read questions from text files
        and return the questions as objects.

        Argument:

        supp_lang_list: list[str] -- supported languages
        student_id = str -- argument for ObjectId() in MongoDB

        Return:
        dictionary{language: list[Question]}
        CHANGE TO:
        list[Question]
    """

    questions_all_lang = {}
    question_list = []

    os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/default")

    for lang in supp_lang_list:
        with open(f"stream_default_{lang.lower()}.json", "r",
                  encoding="utf8") as f:

            question_list = json.load(f)

            # convert json documents to Question objects
            for i, q in enumerate(question_list):
                question = Question()
                for k, v in q.items():
                    setattr(question, k, v)
                # replace json document with Question object
                question_list[i] = question

            questions_all_lang[lang.lower()] = question_list

    return questions_all_lang
