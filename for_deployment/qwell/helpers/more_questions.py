"""Exports functions that fetch questions.

Exports functions:
get_default_questions,
get_question,
get_queue_question,
prep_questions.
"""

import os
import json
import random
from qwell.db_model import Question, Student, LanguageProgress
from qwell.helpers.utils import dict_to_question_obj
from qwell.constants import (START_REVIEW, BASE_ANSWERED_CORRECTLY,
                              SUPPORTED_LANGUAGES,
                              MIN_WRONG_STACK_SIZE_FOR_DRAW,
                              MIN_REVIEW_STACK_SIZE_FOR_DRAW)


def _read_question_from_json(language, side):
    """Read and return questions from json files.

    Generates a list of question ids and then for the first qusestion returns it
    as a Question object.

    Arguments:
    language: str -- language of the question
    side: "front" or "back"

    Return:
    Tuple: (a list of question ids, question as Question object)
    """

    path_ = (os.getcwd() + "/qwell/questions/default/" +
             f"stream_default_{language.lower()}_{side}.json")

    with open(path_, "r", encoding="utf8") as f:

        question_list = json.load(f)
        question_ids_list = []

        # store the question ids in a list
        for q in question_list:
            question_ids_list.append(q["id"])

        # for the first question, convert the dictionary into Question object
        question = Question()
        for k, v in question_list[0].items():
            setattr(question, k, v)

        return question_ids_list, question


def get_default_questions(language, student_id):
    """Read and return questions from json files.

    For a language, read questions from a json file and add their ids
    to the question queues in the student's embedded document.
    Do this for two separate queues: "front" and "back".

    Randomly pick between the "front" and "back" queues, and return
    the first question in one of those queues, as well the question side:
    "front" or "back".

    Argument:
    language: str
    student_id: str -- argument for ObjectId() in MongoDB

    Return:
    Tuple: (Question object, question side)
    """

    f_question_ids, f_question = _read_question_from_json(language, "front")
    b_question_ids, b_question = _read_question_from_json(language, "back")

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
            f_question_queue=f_question_ids,
            b_question_queue=b_question_ids
        )

        # add this new embedded document to list of all studied languages
        student.update(push__language_progress=lang_prog)
        student.save()

        # pick randomly between the front and back question and return
        if random.choices([0, 1], cum_weights=[40, 100])[0]:
            return f_question, "front"
        else:
            return b_question, "back"


def get_queue_question(language, student_id):
    """Read and return first question stored in student's question queue in db.

    Read question queue in Student document, and use the id to
    retrieve a question from Question collection in db.

    Randomly pick between the "front" and "back" question queues.

    Return the question as a Question object, or None if
    no questions in queue.

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    Tuple: (Question object or None, question side or None)
    """
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
        # check if the embedded document exists and question queues
        # are not empty
        if language_embed_doc and language_embed_doc[0].f_question_queue:
            # if there are questions in queue, query and add them to list
            # pick randomly between the front and back question queues
            if random.choices([0, 1], cum_weights=[40, 100])[0]:
                side = "front"
                question_id = language_embed_doc[0].f_question_queue[0]
            else:
                side = "back"
                question_id = language_embed_doc[0].b_question_queue[0]
            return Question.objects(id=question_id).first(), side
        else:
            return None, None
    except IndexError:
        return None, None


def _draw_random_question(questions_iter):
    """Draw a random question from all questions in the database collection.

    Arguments:
    questions_iter: iterator of all documents in the Question collection.

    Return:
    id of the drawn question: str
    """
    sample_iter = questions_iter.aggregate({"$sample": {"size": 1}})
    # aggregate outputs an iterator holding dictionaries
    # aggregate returns key "_id", so don't use "id"
    return next(sample_iter)["_id"]


def prep_questions(language, side, student_id, num_questions_needed):
    """Pick new questions and save them in db.

    Randomly query Question collection for more questions in the database,
    add them to student's queue in Student document - i.e. save them in db.

    Argument:

    language: str
    side: "front" or "back" - which side of the question card
    student_id = str or ObjectId() from MongoDB
    num_questions_needed: integer

    Precondition:
    num_questions_needed > 0

    Return:
    None
    """
    # set the flags for the queues and stacks, either "f" or "b"
    s = side[0]

    # set the flags for the queues and stacks from the opposite question side
    if s == "f":
        op = "b"
    else:
        op = "f"

    num_questions_added = 0
    # force to string if ObjectId passed
    student_id = str(student_id)

    query_args = {"language": f"{language}",
                  "description": "word flashcard"}
    questions_iter = Question.objects(__raw__=query_args)

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # if answered_corr_stack is "big", reduce it, i.e. release questions
    # for review
    size_corr_stack = len(getattr(language_embed_doc[0],
                                  f"{s}_answered_corr_stack"))

    if size_corr_stack > START_REVIEW:
        questions_to_release = (size_corr_stack - BASE_ANSWERED_CORRECTLY)
        del getattr(language_embed_doc[0],
                    f"{s}_answered_corr_stack")[:questions_to_release]

    # draw random question from all possible questions
    # keep drawing questions until you get {num_questions_needed} questions
    while num_questions_added < num_questions_needed:
        q_used = False
        duplicate_check_passed = False

        # for side="back", draw from three sources:
        # 25% of the time from f_answered_wrong_stack,
        # i.e. the opposite - "front" - side of the question
        # 25% of the time from b_answered_wrong_stack
        # 50% of the time from all questions in the Question collection

        # for side="front", draw from four sources:
        # 20% of the time from b_answered_wrong_stack,
        # i.e. the opposite - "back" - side of the question
        # 15% of the time from f_answered_wrong_stack
        # 50% of the time from all questions in the Question collection
        # 15% of the time from f_answered_review_stack

        choices = [0, 1, 2, 3]

        if side == "back":
            weights = [25, 50, 100, 100]
            draw_bin = random.choices(choices, cum_weights=weights)[0]
        else:
            weights = [20, 35, 85, 100]
            draw_bin = random.choices(choices, cum_weights=weights)[0]

        # if picking from all questions in the Question collection
        if draw_bin == 2:
            drawn_id = _draw_random_question(questions_iter)

        # if picking from wrong_stack from the opposite side
        if draw_bin == 0:
            # check if the opposite answered_wrong_stack is big enough
            # to draw from; if so, draw from the first 10 questions

            if (len(getattr(language_embed_doc[0], f"{op}_answered_wrong_stack"))
                    >= MIN_WRONG_STACK_SIZE_FOR_DRAW):
                pick = random.choice(range(10))
                drawn_id = getattr(language_embed_doc[0],
                                   f"{op}_answered_wrong_stack")[pick]
            else:
                # it didn't work, so just draw a random question
                # from all questions in the collection
                drawn_id = _draw_random_question(questions_iter)

        # if picking from wrong_stack from the same side
        if draw_bin == 1:
            # check if the answered_wrong_stack for the same side is big enough
            # to draw from; if so, use the first question in the stack

            if (len(getattr(language_embed_doc[0], f"{op}_answered_wrong_stack"))
                    >= MIN_WRONG_STACK_SIZE_FOR_DRAW):
                drawn_id = getattr(language_embed_doc[0],
                                   f"{op}_answered_wrong_stack").pop(0)
                # we already know that this drawn question is not present
                # in any relevant queue or stack, so it can be used.
                # So, set a flag to stop further verification.
                duplicate_check_passed = True
            else:
                # it didn't work, so just draw a random question
                # from all questions in the collection
                drawn_id = _draw_random_question(questions_iter)

        # if picking from f_answered_review_stack for "front" sided question
        if draw_bin == 3:
            # check if f_answered_review_stack is big enough to draw from;
            # if so, use the first question in the stack

            if (len(language_embed_doc[0].f_answered_review_stack)
                    >= MIN_REVIEW_STACK_SIZE_FOR_DRAW):
                drawn_id = language_embed_doc[0].f_answered_review_stack.pop(0)
                # we already know that this drawn question is not present
                # in any relevant queue or stack, so it can be used.
                # So, set a flag to stop further verification.
                duplicate_check_passed = True
            else:
                # it didn't work, so just draw a random question
                # from all questions in the collection
                drawn_id = _draw_random_question(questions_iter)

        # check that the drawn question is not in the queue, or the two stacks
        # of answered questions; if not, then add it to the queue
        if not duplicate_check_passed:
            for q_id in getattr(language_embed_doc[0], f"{s}_question_queue"):
                if drawn_id == q_id:
                    q_used = True
                    break

        if not duplicate_check_passed and not q_used:
            for q_id in getattr(language_embed_doc[0], f"{s}_answered_wrong_stack"):
                if drawn_id == q_id:
                    q_used = True
                    break
            if not q_used:
                for q_id in getattr(language_embed_doc[0], f"{s}_answered_corr_stack"):
                    if drawn_id == q_id:
                        q_used = True
                        break

        if duplicate_check_passed or not q_used:
            # question not used, so add its id to the Student queue of questions
            getattr(language_embed_doc[0], f"{s}_question_queue").append(drawn_id)
            language_embed_doc.save()
            num_questions_added += 1

    # query again to check the size of the question queue
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    return None


def get_question(language, student_id):
    """Provide a question to a student for a given language.

    If the student has never seen any question before, read default questions
    from json file for all supported languages,
    add them to the student's question queues in the db,
    and return a question for the given language.

    If the student has been served a question before, read and return the first
    question in the question queue (randomly choose between the "front" and
    "back" question queues).

    For questions that can be asked in two directions - for example
    many flash cards - there are "front" and "back" sides. There are separate
    queues for each side.


    Argument:

    language: str -- language of the question
    student_id: MongoDB ObjectId or str (argument for ObjectId())

    Return:
    tuple: (Question object, question side)
    """

    # in case ObjectId is passed
    student_id = str(student_id)

    question, side = get_queue_question(language, student_id)

    if not question:
        # no question in queue, i.e. brand new student; so read default
        # questions for all supported languages from a json file,
        # set up the question queues and return a question for
        # the given language
        questions_all_lang = {}
        for lang in SUPPORTED_LANGUAGES:
            if lang == language:
                question, side = get_default_questions(lang, student_id)
            else:
                get_default_questions(lang, student_id)

    return question, side
