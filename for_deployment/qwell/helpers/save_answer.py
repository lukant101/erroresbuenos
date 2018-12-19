"""Exports function: save_answer."""

import mongoengine
import sys
import datetime
import pytz
from bson.objectid import ObjectId
from flask_login import current_user
from qwell.db_model import StudentHistory, Student
from qwell.constants import (NUM_QUESTIONS_TO_LOAD, MIN_QUESTIONS_IN_QUEUE,
                             MAXLEN_ANSWERED_WRONG_STACK,
                             MAXLEN_SLACK_ANSWERED_WRONG_STACK)
from qwell.helpers.create_stud_hist_coll import create_stud_hist_coll
from qwell.helpers.more_questions import prep_questions
from qwell.helpers.sanitize_input import sanitize_input


def save_answer(*, student_id, language,
                question_id, user_answer, answer_correct,
                audio_answer_correct):
    """
    Save user's answer in StudentHistory and Student documents.

    Add new questions to the queue in db, if the queue is short.

    Return:
    None
    """

    if len(user_answer) > 0:
        user_answer = sanitize_input(user_answer)
    else:
        user_answer = ""

    # if no Student History collection in database, create one
    if not StudentHistory.objects:
        create_stud_hist_coll()

    # check if student has seen this question before
    stud_hist = StudentHistory.objects(student_id=str(current_user.id),
                                       question_id=question_id).first()

    if stud_hist:
        # student answered this question before, so update the document
        # add the answer string only if it's not already stored (exact match),
        # and if it's not an empty string
        if (user_answer and
                (not user_answer in stud_hist.answer)):
            stud_hist.update(push__answer=user_answer)
        stud_hist.update(inc__attempts_count=1)
        stud_hist.update(set__last_attempted=datetime.datetime.now
                         (tz=pytz.UTC))

        if stud_hist.answer_correct is False and answer_correct == "true":
            stud_hist.update(set__answer_correct=True)
        if stud_hist.answer_correct and answer_correct == "false":
            stud_hist.update(set__answer_correct=False)

        if (stud_hist.audio_answer_correct is False
                and audio_answer_correct == "true"):
            stud_hist.update(set__audio_answer_correct=True)
        if (stud_hist.audio_answer_correct
                and audio_answer_correct == "false"):
            stud_hist.update(set__audio_answer_correct=False)

        try:
            stud_hist.save()
        except BaseException as err:
            return f"failed to update a doc in StudentHistory. Error: {err}"

    else:
        # first time the student saw the question, so create a document for it
        stud_hist = StudentHistory(
            student_id=current_user.id,
            language=language,
            question_id=ObjectId(question_id),
            attempts_count=1,
            last_attempted=datetime.datetime.now(tz=pytz.UTC)
        )

        # if answer not an empty string, save it
        if user_answer:
            stud_hist.answer = [user_answer]
        if answer_correct == "true":
            stud_hist.answer_correct = True
        if audio_answer_correct == "true":
            stud_hist.audio_answer_correct = True

        try:
            stud_hist.save()
        except BaseException as err:
            return f"failed to save to StudentHistory. Error: {err}"

    # update the Student document

    student = Student.objects(id=str(current_user.id)).first()

    if answer_correct == "true":
        student.update(inc__num_correct_answers=1)

    # update the question queue and answer stacks in Student document

    # get embedded document for this student for this language
    language_embed_doc = student.language_progress.filter(
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

        # DON'T USE condition: answers_to_del > 0
        if wrong_stack_len > MAXLEN_ANSWERED_WRONG_STACK:
            answers_to_del = (wrong_stack_len - MAXLEN_ANSWERED_WRONG_STACK
                              + MAXLEN_SLACK_ANSWERED_WRONG_STACK)
            del wrong_stack[:answers_to_del]

        wrong_stack.append(stud_hist.question_id)

    # remove the answered question from the queue
    assert language_embed_doc[0].question_queue[0] == stud_hist.question_id
    language_embed_doc[0].question_queue.pop(0)

    language_embed_doc.save()

    # if queue doesn't have enough questions, add more questions
    if len(language_embed_doc[0].question_queue) < MIN_QUESTIONS_IN_QUEUE:
        prep_questions(language, str(current_user.id), NUM_QUESTIONS_TO_LOAD)
