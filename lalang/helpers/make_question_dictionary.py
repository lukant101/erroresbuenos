"""Convert a question stored as a string into a dictionary, and return dict"""

"""
Module currently not used - implemented the functionality with json.load()
instead, which automatically takes json strings
and converts they to Python dictionaries

Requirements:

1) the input string is in JSON

2) document id is listed as the last field in the string
"""


def str_to_dict(str_in):
    temp_list1 = str_in.split("'")

    temp_list2 = [e for e in temp_list1
                  if not e.startswith(("{", ":", ",", ")"))]

    temp_list2[-1] = "ObjectId(" + temp_list2[-1] + ")"

    dict_final = dict(zip(temp_list2[::2], temp_list2[1::2]))

    return dict_final


# for testing only; DELETE in production
if __name__ == "__main__":
    str_in = "{'description': 'word flashcard', 'skill': 'Vocabulary', 'language': 'Spanish', 'word': 'gentía', 'part_of_speech': 'noun', 'audio_files': 'gentia.ogg', 'image_files': 'city-crowd.jpg', 'id': ObjectId('5ba13d0efde08a2e2c56f63c')}"
    question_dict = str_to_dict(str_in)

    class Question():

        description = ""
        skill = ""
        language = ""
        word = ""
        part_of_speech = ""
        audio_files = ""
        image_files = ""

    question = Question()

    for k, v in question_dict.items():
        setattr(question, k, v)

    print(question.word)

    # print("gentía")
