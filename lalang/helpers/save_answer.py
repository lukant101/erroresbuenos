"""Exports function: save_answer."""

import mongoengine
import sys
import datetime
import pytz
from bson.objectid import ObjectId
import logging


sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import StudentHistory, Student
from lalang.constants import (NUM_QUESTIONS_TO_LOAD, MIN_QUESTIONS_IN_QUEUE,
                              MAXLEN_ANSWERED_WRONG_STACK,
                              MAXLEN_SLACK_ANSWERED_WRONG_STACK)
from lalang.helpers.create_stud_hist_coll import create_stud_hist_coll
from lalang.helpers.more_questions import prep_questions

logging.basicConfig(level=logging.INFO, filename="app-save-answer.log",
                    filemode="w")


def save_answer(*, student_id, language,
                question_id, user_answer, answer_correct,
                audio_answer_correct):
    """
    Save user's answer in StudentHistory and Student documents.

    Return:
    a list of new questions, if the question queue has been replenished;
    otherwise, return None
    """
    mongoengine.connect("lalang_db", host="localhost", port=27017)

    # if no Student History collection in database, create one
    if not StudentHistory.objects:
        create_stud_hist_coll()

    # check if student has seen this question before
    stud_hist = StudentHistory.objects(student_id=student_id[0],
                                       question_id=question_id[0]).first()
    if stud_hist:
        # student answered this question before, so update the document
        # add the answer string only if it's not already stored (exact match)
        if not user_answer[0] in stud_hist.answer:
            stud_hist.update(push__answer=user_answer[0])
        stud_hist.update(inc__attempts_count=1)
        stud_hist.update(set__last_attempted=datetime.datetime.now
                         (tz=pytz.UTC))

        if stud_hist.answer_correct is False and answer_correct[0] == "true":
            stud_hist.update(set__answer_correct=True)
        if stud_hist.answer_correct and answer_correct[0] == "false":
            stud_hist.update(set__answer_correct=False)

        if (stud_hist.audio_answer_correct is False
                and audio_answer_correct[0] == "true"):
            stud_hist.update(set__audio_answer_correct=True)
        if (stud_hist.audio_answer_correct
                and audio_answer_correct[0] == "false"):
            stud_hist.update(set__audio_answer_correct=False)

        stud_hist.save()

    else:
        # first time the student saw the question, so create a document for it
        stud_hist = StudentHistory(
            student_id=ObjectId(student_id[0]),
            language=language[0],
            question_id=ObjectId(question_id[0]),
            answer=[user_answer[0]],
            attempts_count=1,
            last_attempted=datetime.datetime.now(tz=pytz.UTC)
        )

        if answer_correct[0] == "true":
            stud_hist.answer_correct = True
        if audio_answer_correct[0] == "true":
            stud_hist.audio_answer_correct = True

        stud_hist.save()

    # update the question queue and answer stacks in Student document

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id[0]).first().language_progress.filter(
        language=stud_hist.language)

    # update the embedded document for this language
    language_embed_doc[0].last_studied = datetime.datetime.now(tz=pytz.UTC)

    if stud_hist.answer_correct:
        language_embed_doc[0].answered_corr_stack.append(
            stud_hist.question_id)
    else:
        # if the wrong answer stack is too big, reduce it to the
        # maximum minus the slack, before adding the latest answer
        wrong_stack = language_embed_doc[0].answered_wrong_stack
        wrong_stack_len = len(wrong_stack)
        answers_to_del = (wrong_stack_len - MAXLEN_ANSWERED_WRONG_STACK
                          + MAXLEN_SLACK_ANSWERED_WRONG_STACK)

        # DON'T USE condition: answers_to_del > 0
        if wrong_stack_len > MAXLEN_ANSWERED_WRONG_STACK:
            del wrong_stack[:answers_to_del]

        wrong_stack.append(stud_hist.question_id)

    # remove the answered question from the queue
    assert language_embed_doc[0].question_queue[0] == stud_hist.question_id
    language_embed_doc[0].question_queue.pop(0)
    logging.info(f"Removed question from queue")

    language_embed_doc.save()

    # if queue doesn't have enough questions, add more questions
    if len(language_embed_doc[0].question_queue) < MIN_QUESTIONS_IN_QUEUE:
        new_questions = prep_questions(language[0],
                                       student_id[0], NUM_QUESTIONS_TO_LOAD)
    else:
        new_questions = None

    return new_questions
