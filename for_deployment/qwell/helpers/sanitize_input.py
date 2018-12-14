"""Exports function: sanitize_input."""

import re
from qwell.constants import MAX_USER_ANSWER_LEN


def sanitize_input(input_text):

    text_ = input_text.strip()

    if len(text_) > MAX_USER_ANSWER_LEN:
        text_ = text_[:MAX_USER_ANSWER_LEN]

    # user input is already sanitized for special characters on the client side
    # text_ = (text_.replace(";", "").replace("<", "&lt;").
    #          replace(">", "&gt;").replace("\"", "&quot;").
    #          replace("'", "&#039;").replace("\\", "&#92;").
    #          replace("{", "&#123;").replace("}", "&#125;").
    #          replace("&", "&amp;"))

    return text_
