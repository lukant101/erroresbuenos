import mongoengine
import sys
import datetime
import pytz
from bson.objectid import ObjectId
import os

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import (StudentHistory, Student, LanguageProgress,
                             NUM_QUESTIONS_TO_LOAD)
from lalang.helpers.create_stud_hist_coll import create_stud_hist_coll


def save_answer(*, student_id, language,
                question_id, user_answer, answer_correct,
                audio_answer_correct):

    mongoengine.connect("lalang_db", host="localhost", port=27017)

    # if no Student History collection in database, create one
    if not StudentHistory.objects:
        create_stud_hist_coll()

    # check if student has seen this question before
    stud_hist = StudentHistory.objects(student_id=student_id[0],
                                       question_id=question_id[0]).first()
    if stud_hist:
        # student answered this question before, so update the document
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
    # no queue implemented yet, but once working, pop first question:

    # get embedded document for this student for this language
    language_embed_doc = Student.objects(
        id=student_id[0]).first().language_progress.filter(
        language=stud_hist.language)

    if language_embed_doc:
        # if there is an existing emb. document, i.e. student has studied
        # this langauge before, update the emb. document for this language
        language_embed_doc[0].last_studied = datetime.datetime.now(tz=pytz.UTC)
        # remove the answered question from the queue
        assert language_embed_doc[0].question_queue[0] == stud_hist.question_id
        language_embed_doc[0].question_queue.pop(0)

        if stud_hist.answer_correct:
            language_embed_doc[0].answered_corr_stack.append(
                stud_hist.question_id)
        else:
            language_embed_doc[0].answered_wrong_stack.append(
                stud_hist.question_id)

        language_embed_doc.save()

    else:
        # student has never studied  this langauge, so create
        # an embedded document in Student document for this language
        student = Student.objects(id=student_id[0]).first()

        lang_prog = LanguageProgress(
            language=language[0],
            last_studied=datetime.datetime.now(tz=pytz.UTC)
        )
        # check if written answer is correct
        # will implement checking of audio answer later
        if stud_hist.answer_correct:
            lang_prog.answered_corr_stack = [stud_hist.question_id]
        else:
            lang_prog.answered_wrong_stack = [stud_hist.question_id]

        # add new embedded document to list of all studied languages
        student.update(push__language_progress=lang_prog)

        student.save()
