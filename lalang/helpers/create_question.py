"""Export functions: create_question."""

import mongoengine
import sys

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question

mongoengine.connect("lalang_db", host="localhost", port=27017)


def create_question(language, *,
                    Word,
                    Part_of_Speech,
                    Audio,
                    Photo1,
                    Photo1_ar,
                    Photo2,
                    Photo2_ar,
                    Photo3,
                    Photo3_ar,
                    Photo4,
                    Photo4_ar,
                    Child_Appropriate,
                    Alternative_Answer,
                    Source_Id):
    """Create a question document and save it to database."""

    question = Question(
        description="word flashcard",
        skill="Vocabulary",
        language=language.lower(),
        word=Word,
        part_of_speech=Part_of_Speech,
        source_id=Source_Id
    )

    alt_answers = Alternative_Answer.split('\n')
    if len(alt_answers) > 1:
        for i in range(1, len(alt_answers)):
            alt_answers[i] = alt_answers[i].lstrip(" ")
    question.alternative_answers = alt_answers

    if Child_Appropriate.lower() == "no":
        question.child_appropriate = False

    question.audio = Audio.split(".")
    question.audio.pop()

    # determine how many images there are
    if Photo4:
        img_count = 4
        images_list = [[Photo1, Photo1_ar], [Photo2, Photo2_ar],
                       [Photo3, Photo3_ar], [Photo4, Photo4_ar]]
    else:
        if Photo3:
            img_count = 3
            images_list = [[Photo1, Photo1_ar], [Photo2, Photo2_ar],
                           [Photo3, Photo3_ar]]
        else:
            if Photo2:
                img_count = 2
                images_list = [[Photo1, Photo1_ar], [Photo2, Photo2_ar]]
            else:
                if Photo1:
                    img_count = 1
                    images_list = [[Photo1, Photo1_ar]]
                else:
                    img_count = 0
                    images_list = []

    question.images = []

    for img in images_list:
        # adding info for each image
        fileroot, ext = img[0].split(".")
        question.images.append([fileroot, ext, img[1]])

    student.save()
