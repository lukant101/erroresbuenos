"""Export functions: create_question."""

import mongoengine
import sys
from os.path import splitext

sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")

from lalang.db_model import Question

mongoengine.connect("lalang_db", host="localhost", port=27017)


def create_question(language, *, odict):
    """Create a question document and save it to database."""

    question = Question(
        description="word flashcard",
        skill="Vocabulary",
        language=language.lower(),
        word=odict["Word"],
        part_of_speech=odict["Part_of_Speech"],
        source_id=odict["Source_Id"]
    )

    # css.DictReader escapes newline characters, so split with: '\\n '
    question.alternative_answers = odict["Alternative_Answer"].split('\\n ')

    if odict["Child_Appropriate"].lower() == "no":
        question.child_appropriate = False

    question.audio = odict["Audio"].split(", ")

    question.images = []

    # adding info for the first image
    fileroot, ext = splitext(odict["Photo1"])
    ext = ext.lstrip(".")
    question.images.append([fileroot, ext, float(odict["Photo1_ar"])])

    # if there are more images, add info for them
    for i in [1, 2, 3]:
        if odict[f"Photo{i+1}"]:
            fileroot, ext = splitext(odict[f"Photo{i+1}"])
            ext = ext.lstrip(".")
            question.images.append([fileroot, ext,
                                    float(odict[f"Photo{i+1}_ar"])])

    question.save()
