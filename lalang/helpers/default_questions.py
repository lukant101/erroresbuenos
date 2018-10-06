import sys
import os
from lalang.helpers.make_question_dictionary import str_to_dict

# sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos")
# sys.path.append("C:\\Users\\Lukasz\\Python")

from lalang.db_model import Question


def get_default_questions(supp_lang_list):
    """For the supported languages, read questions from text files
    and return the questions as objects.

    Argument:

    supp_lang_list: list[str] -- supported languages

    Return:
    dictionary{language: list[Question]}
    """

    questions_dict_all_lang = {}
    question_list = []

    os.chdir("C:/Users/Lukasz/Python/ErroresBuenos/lalang/questions/default")

    for lang in supp_lang_list:
        with open(f"stream_default_{lang.lower()}.json", "r", encoding="utf8") as f:
            question_list = f.readlines()

            # convert strings to Question objects

            for i, _ in enumerate(question_list):
                question = Question()
                question_dict = str_to_dict(question_list[i].rstrip("\n"))
                # go through question stored as a dict and create Question obj
                # could implement going from str to Question obj directly
                for k, v in question_dict.items():
                    setattr(question, k, v)

                question_list[i] = question

            questions_dict_all_lang[lang.lower()] = question_list

    return questions_dict_all_lang


# DELETE THE CODE BELOW ONCE THE HOME PAGE IMPLEMENTED IN PHASE 1
if __name__ == "__main__":
    sys.path.append("C:\\Users\\Lukasz\\Python\\ErroresBuenos\\lalang")
    from helpers.make_question_dictionary import str_to_dict

    print(questions_dict_all_lang["spanish"][0])

# the_stuff = get_template_questions()
# print(the_stuff)
#
# for k, l in the_stuff.items():
#     for q in l:
#         fields_list = tuple(q._fields.keys())
#         for f in fields_list:
#             # print(q.f)
#             print(getattr(q, f))
