"""Exports functions that fetch questions.

Exports functions:
get_default_questions,
get_queue_question,
prep_questions,
get_questions_all_lang.
"""

import os
import json
import mongoengine
import logging
from qwell.db_model import Question, Student, LanguageProgress
from qwell.helpers.utils import dict_to_question_obj
from qwell.constants import START_REVIEW, BASE_ANSWERED_CORRECTLY

logging.basicConfig(level=logging.INFO, filename="app.log",
                    filemode="a")


def get_default_questions(language, student_id):
    """Read and return questions from json file.

    For a language, read questions from a json file and add their ids
    to the question queue in the student's document.
    Also, return the first question as an object Question.

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    Question object -- the first question in the question queue
    """
    question_list = []

    path_ = (os.getcwd() + "/qwell/questions/default/" +
             f"stream_default_{language.lower()}.json")

    logging.info(f"path for {language}: {path_}")

    with open(path_, "r",
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

    # check this EmbeddedDocumentList field exists before adding to it;
    # if all list items get deleted, then MongoDB will delete the list field
    # so guard against that
    assert not Student.objects(id=student_id,
                               __raw__={"language_progress": None}).first()

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # only add a document for this language if it doesn't exist
    if not language_embed_doc:
        # create embedded document for this language
        student = Student.objects(id=student_id).first()

        lang_prog = LanguageProgress(
            language=language,
            question_queue=question_ids_list
        )

        # add new embedded document to list of all studied languages
        student.update(push__language_progress=lang_prog)
        student.save()
        return question_list[0]


def get_queue_question(language, student_id):
    """Read and return first question stored in student's question queue in db.

    Read question queue in Student document, and use the id to
    retrieve a question from Question collection in db.
    Return the question as a Question object, or None if
    no questions in queue

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    Question object or None
    """
    mongoengine.connect("qwell_db", host="localhost", port=27017)

    # check this EmbeddedDocumentList field exists before adding to it;
    # if all list items get deleted, then MongoDB will delete the list field
    # so guard against that
    assert not Student.objects(id=student_id,
                               __raw__={"language_progress": None}).first()

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # in case the list or queue doesn't exist
    try:
        # check that the list and queue are not empty
        if language_embed_doc and language_embed_doc[0].question_queue:
            # if there are questions in queue, query and add them to list
            question_id = language_embed_doc[0].question_queue[0]
            return Question.objects(id=question_id).first()
        else:
            return None
    except IndexError:
        return None


def prep_questions(language, student_id, num_questions_needed):
    """Pick new questions and save them in db.

    Randomly query Question collection for more questions in the database,
    add them to student's queue in Student document - i.e. save them in db.

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB
    num_ques: integer

    Precondition:
    num_ques > 0

    Return:
    None
    """
    num_questions_added = 0

    mongoengine.connect("qwell_db", host="localhost", port=27017)

    query_args = {"language": f"{language}",
                  "description": "word flashcard"}
    questions_iter = Question.objects(__raw__=query_args)

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # if answered_corr_stack is "big", reduce it, i.e. release questions
    # for review
    size_corr_stack = len(language_embed_doc[0].answered_corr_stack)
    logging.info(f"size_corr_stack: {size_corr_stack}")

    if size_corr_stack > START_REVIEW:
        logging.info("We need to release questions for review")
        questions_to_release = (size_corr_stack - BASE_ANSWERED_CORRECTLY)
        logging.info(f"Number of questions to release: {questions_to_release}")
        del language_embed_doc[0].answered_corr_stack[:questions_to_release]
        logging.info("Questions released for review.")

    # draw random question from all possible questions
    # keep drawing questions until you get {num_questions} questions
    while num_questions_added < num_questions_needed:
        q_used = False
        sample_iter = questions_iter.aggregate({"$sample": {"size": 1}})
        # aggregate outputs an iterator holding dictionaries
        new_question = next(sample_iter)
        # aggregate returns key "_id", so change to "id"
        new_question["id"] = new_question.pop("_id")
        # convert the dictionary to Question object
        new_question = dict_to_question_obj(new_question)

        # check that this question is not in the queue, or the two stacks
        # of answered questions
        # if not, then add it to the queue
        for q_id in language_embed_doc[0].question_queue:
            if new_question.id == q_id:
                q_used = True
                break
        if q_used:
            break

        for q_id in language_embed_doc[0].answered_wrong_stack:
            if new_question.id == q_id:
                q_used = True
                break
        if q_used:
            break

        for q_id in language_embed_doc[0].answered_corr_stack:
            if new_question.id == q_id:
                q_used = True
                break
        if q_used:
            break

        # question not used, so add its id to the Student queue of questions
        language_embed_doc[0].question_queue.append(new_question.id)
        language_embed_doc.save()
        num_questions_added += 1

    return None


def get_questions_all_lang(supp_lang_list, student_id):
    """Provide questions to a student for all supported languages.

    For all supported languages, read a question.
    If student already studied a language, read from question queue in
    Student document (i.e. the db), and return the first question.
    If not, read default questions from json file, add them to the db,
    and return the first question.

    Argument:

    supp_lang_list: list[str] -- supported languages
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    dictionary{language: Question}
    """
    questions_all_lang = {}

    for lang in supp_lang_list:
        question_list = get_queue_question(lang, student_id)
        if question_list:
            # questions in student's queue, so add them to dictionary
            # of all supported languages
            questions_all_lang[lang] = question_list
            logging.info(f"Just fetched a question from queue for {lang}")
        else:
            # no questions in queue, i.e. student has not studied
            # this language, so use default questions read from json file
            questions_all_lang[lang] = get_default_questions(lang, student_id)
            logging.info(f"Just added default questions for {lang}")

    return questions_all_lang
