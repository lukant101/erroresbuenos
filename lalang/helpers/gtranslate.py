# Imports the Google Cloud client library
from google.cloud import translate
import json


def google_translate(input_text, *, source_lang, target_lang):
    # Instantiates a client
    client = translate.Client()

    # The target language
    target = target_lang

    # Translates some text into Russian
    translation = client.translate(
        input_text,
        target_language=target,
        source_language=source_lang)

    return json.dumps(translation['translatedText'], ensure_ascii=False)
