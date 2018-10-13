"""Exports functions: get_questions_all_lang, prep_questions."""

import os
import json
import mongoengine
from lalang.db_model import Question, Student, LanguageProgress
from lalang.helpers.utils import dict_to_question_obj


def get_default_questions(language, student_id):
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
            return None
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


def get_queue_questions(language, student_id):
    """Read and return questions already stored in student's question queue.

    Read question queue in Student document, and use those ids to
    retrieve the questions from Question collection.
    Return the questions as a list of Question objects, or None if
    no questions in queue

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    list[Question] or None
    """
    question_list = []

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    # in case the list or queue doesn't exist
    try:
        # check that the list and queue are not empty
        if language_embed_doc and language_embed_doc[0].question_queue:
            # if there are questions in queue, query and add them to list
            for q_id in language_embed_doc[0].question_queue:
                q = Question.objects(id=q_id).first()
                question_list.append(q)
            return question_list
        else:
            return None
    except IndexError:
        return None


def prep_questions(language, student_id, num_questions_needed):
    """Pick new questions, save them in db, and return them.

    Randomly query Question collection for more questions in the database,
    add them to student's queue in Student document - i.e. save them in db.
    Also, return the questions as objects.

    Argument:

    language: str
    student_id = str -- argument for ObjectId() in MongoDB
    num_ques: integer

    Precondition:
    num_ques > 0

    Return:
    list[Question]
    """
    question_list = []
    num_questions_added = 0

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    query_args = {"language": f"{language.capitalize()}",
                  "description": "word flashcard"}
    questions_iter = Question.objects(__raw__=query_args)

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id).first().language_progress.filter(
        language=language)

    print("before while loop")
    # draw random question from all possible questions
    # keep drawing questions until you get {num_questions} questions
    while num_questions_added < num_questions_needed:
        q_used = False
        print("while iteration starts")
        sample_iter = questions_iter.aggregate({"$sample": {"size": 1}})
        # aggregate outputs an iterator holding dictionaries
        new_question = next(sample_iter)
        # aggregate returns key "_id", so change to "id"
        new_question["id"] = new_question.pop("_id")
        # convert back the dictionary to Question object
        new_question = dict_to_question_obj(new_question)
        print("we've got a Question object! ", new_question.id)

        # check that this question is not in the queue, or the two stacks
        # if not, then add it to the queue; also add it to question_list
        for q_id in language_embed_doc[0].question_queue:
            if new_question.id == q_id:
                q_used = True
                print("question found in queue")
                break
        if not q_used:
            for q_id in language_embed_doc[0].answered_wrong_stack:
                if new_question.id == q_id:
                    q_used = True
                    print("question found in answered_wrong_stack")
                    break
        if not q_used:
            for q_id in language_embed_doc[0].answered_corr_stack:
                if new_question.id == q_id:
                    q_used = True
                    print("question found in answered_corr_stack")
                    break
        if not q_used:
            # adding the question id to the Student queue of questions
            print("I should add the question to the queue here")
            language_embed_doc[0].question_queue.append(new_question.id)
            language_embed_doc.save()
            # adding question to the list to be returned
            question_list.append(new_question)
            num_questions_added += 1
            print("Number of questions added: ", num_questions_added)

    return question_list


def get_questions_all_lang(supp_lang_list, student_id):
    """Provide questions to a student for all supported languages.

    For all supported languages, read several questions.
    If student already studied a language, read questions from queue in
    Student document (i.e. the db).
    If not, read default questions from json file.

    Argument:

    supp_lang_list: list[str] -- supported languages
    student_id = str -- argument for ObjectId() in MongoDB

    Return:
    dictionary{language: list[Question]}
    """
    questions_all_lang = {}

    for lang in supp_lang_list:
        question_list = get_queue_questions(lang, student_id)
        if question_list:
            # questions in student's queue, so add them to dictionary
            # of all supported languages
            questions_all_lang[lang] = question_list
        else:
            # no questions in queue, i.e. student has not studied
            # this language, so use default questions read from json file
            questions_all_lang[lang] = get_default_questions(lang, student_id)

    return questions_all_lang
