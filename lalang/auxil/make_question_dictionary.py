"""Convert a question stored as a string into a dictionary, and return dict."""


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
