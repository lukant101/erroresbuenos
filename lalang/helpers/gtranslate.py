"""Exports function: google_translate"""

from google.cloud import translate
import json


def google_translate(input_text, *, source_lang, target_lang):
    # Instantiates a client
    client = translate.Client()

    # The target language
    target = target_lang

    # handling exceptions - bad translations by Google
    translations_exceptions_es = {"dirección": "direction"}

    translations_exceptions = {"es": translations_exceptions_es}

    if translations_exceptions.get(source_lang):
        translation = translations_exceptions.get(source_lang).get(input_text)
        if translation:
            return json.dumps(translation)

    translation = client.translate(
        input_text,
        target_language=target,
        source_language=source_lang)

    return json.dumps(translation["translatedText"], ensure_ascii=False)
