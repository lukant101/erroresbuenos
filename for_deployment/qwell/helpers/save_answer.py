"""Exports function: save_answer."""

import mongoengine
import sys
import datetime
import pytz
import json
from bson.objectid import ObjectId
from flask_login import current_user
from qwell.db_model import StudentHistory, Student
from qwell.constants import (NUM_QUESTIONS_TO_LOAD, MIN_QUESTIONS_IN_QUEUE,
                              MAXLEN_ANSWERED_WRONG_STACK,
                              MAXLEN_SLACK_ANSWERED_WRONG_STACK)
from qwell.helpers.create_stud_hist_coll import create_stud_hist_coll
from qwell.helpers.more_questions import prep_questions
from qwell.helpers.sanitize_input import sanitize_input


def _reduce_wrong_stack(embed_doc, question_side):
    """Reduce the wrong stack, if it is too big.

    Reduce it to the maximum size minus the slack (as per defined constants).

    Arguments:
    embed_doc: LanguageProgress object (embedded document in Student collection)
    question_side: "front" or "back"

    Return:
    None
    """
    if question_side == "front":
        s = "f"
    else:
        s = "b"

    wrong_stack = getattr(embed_doc, f"{s}_answered_wrong_stack")
    wrong_stack_len = len(wrong_stack)

    # DON'T USE condition: answers_to_del > 0
    if wrong_stack_len > MAXLEN_ANSWERED_WRONG_STACK:
        answers_to_del = (wrong_stack_len - MAXLEN_ANSWERED_WRONG_STACK
                          + MAXLEN_SLACK_ANSWERED_WRONG_STACK)
        del wrong_stack[:answers_to_del]


def save_answer(*, student_id, language,
                question_id, question_side, user_answer, answer_correct=None,
                audio_answer_correct=None):
    """
    Save user's answer in StudentHistory and Student documents.

    Add new questions to the queue in db, if the queue is short.

    Return:
    None
    """
    # if no Student History collection in database, create one
    if not StudentHistory.objects:
        create_stud_hist_coll()

    if question_side == "back":
        if len(user_answer) > 0:
            user_answer = sanitize_input(user_answer)
        else:
            user_answer = ""

        answer_correct = json.loads(answer_correct)
        audio_answer_correct = json.loads(audio_answer_correct)

        queue = "b_question_queue"

    if question_side == "front":
        queue = "f_question_queue"

    # check if student has seen this question before
    stud_hist = StudentHistory.objects(student_id=str(current_user.id),
                                       question_id=question_id,
                                       question_side=question_side).first()

    if stud_hist:
        # student answered this question before, so update the document.
        stud_hist.update(inc__attempts_count=1)
        stud_hist.update(set__last_attempted=datetime.datetime.now
                         (tz=pytz.UTC))

        if question_side == "front":
            stud_hist.update(push__answer=user_answer)

        # For "back" sided questions, add the answer string only if
        # it's not already stored (exact match), and if it's not an empty string
        if (question_side == "back"):
            if user_answer and (not user_answer in stud_hist.answer):
                stud_hist.update(push__answer=user_answer)

            if not stud_hist.answer_correct and answer_correct:
                stud_hist.update(set__answer_correct=True)
            if stud_hist.answer_correct and not answer_correct:
                stud_hist.update(set__answer_correct=False)

            if (not stud_hist.audio_answer_correct
                    and audio_answer_correct):
                stud_hist.update(set__audio_answer_correct=True)
            if (stud_hist.audio_answer_correct
                    and not audio_answer_correct):
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
            question_side=question_side,
            attempts_count=1,
            last_attempted=datetime.datetime.now(tz=pytz.UTC)
        )

        # if answer not an empty string, save it
        if user_answer:
            stud_hist.answer = [user_answer]

        if question_side == "back":
            stud_hist.answer_correct = answer_correct
            stud_hist.audio_answer_correct = audio_answer_correct

        try:
            stud_hist.save()
        except BaseException as err:
            return f"failed to save to StudentHistory. Error: {err}"

    # now update the Student document

    student = Student.objects(id=str(current_user.id)).first()

    if question_side == "back":
        if answer_correct:
            student.update(inc__num_correct_answers=1)

    if question_side == "front":
        if user_answer == "2":
            student.update(inc__num_correct_answers=1)

    # update the question queue and answer stacks in Student document

    # get embedded document for this student for this language
    language_embed_doc = student.language_progress.filter(
        language=stud_hist.language)

    # update the embedded document for this language
    language_embed_doc[0].last_studied = datetime.datetime.now(tz=pytz.UTC)

    if question_side == "back":
        if stud_hist.answer_correct:
            language_embed_doc[0].b_answered_corr_stack.append(
                stud_hist.question_id)
        else:
            # if the wrong answer stack is too big, reduce it
            # before adding the latest wrong answer
            _reduce_wrong_stack(language_embed_doc[0], "back")

            language_embed_doc[0].b_answered_wrong_stack.append(
                stud_hist.question_id)

    if question_side == "front":
        if user_answer == "2":
            language_embed_doc[0].f_answered_corr_stack.append(
                stud_hist.question_id)
        if user_answer == "1":
            language_embed_doc[0].f_answered_review_stack.append(
                stud_hist.question_id)
        if user_answer == "0":
            # if the wrong answer stack is too big, reduce it
            # before adding the latest wrong answer
            _reduce_wrong_stack(language_embed_doc[0], "front")
            language_embed_doc[0].f_answered_wrong_stack.append(
                stud_hist.question_id)

    # remove the answered question from the queue
    assert getattr(language_embed_doc[0], queue)[0] == stud_hist.question_id
    getattr(language_embed_doc[0], queue).pop(0)

    language_embed_doc.save()

    # if queue doesn't have enough questions, add more questions
    if len(getattr(language_embed_doc[0], queue)) < MIN_QUESTIONS_IN_QUEUE:
        prep_questions(language, question_side,
                       current_user.id, NUM_QUESTIONS_TO_LOAD)

    # query database again to check the size of the queue
    language_embed_doc = student.language_progress.filter(
        language=stud_hist.language)
