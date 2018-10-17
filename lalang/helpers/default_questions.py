import os
import sys
import json
import logging

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question, Student, LanguageProgress
from lalang.constants import SUPPORTED_LANGUAGES, student_id


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


def get_default_questions2(language, student_id):
    """Read and return questions from json file.

    For a language, read questions from a json file
    and return the questions as a list of objects. Also, add these
    questions' ids to the queue in student's document

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    list[Question]
    """
    question_list = []

    os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/default")

    with open(f"stream_default_{language.lower()}.json", "r",
              encoding="utf8") as f:

        question_list = json.load(f)
        question_ids_list = []

        # convert json documents to Question objects
        for i, q in enumerate(question_list):
            question = Question()
            for k, v in q.items():
                setattr(question, k, v)
                if k == "id":
                    question_ids_list.append(v)
            # replace json document with Question object
            question_list[i] = question

    # since we're using default questions, student has never studied
    # this langauge, and so there should be no embedded document
    # in Student document for this language; if that's the case, create one

    # check if embedded document for this student for this language exists
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # in case field language_progress: EmbeddedDocumentList doesn't exist
    try:
        if language_embed_doc:
            return question_list
        else:
            # create embedded document for this language
            student = Student.objects(id=student_id).first()

            lang_prog = LanguageProgress(
                language=language,
                question_queue=question_ids_list
            )

            # add new embedded document to list of all studied languages
            student.update(push__language_progress=lang_prog)
            student.save()
            return question_list
    except NameError:
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w")

    questions = get_default_questions(SUPPORTED_LANGUAGES)
    logging.info(f"{questions['spanish'][0].word}")
    print(questions["spanish"][0].word)
    questions2 = get_default_questions2("spanish", student_id)
    print(questions2[0].word)
