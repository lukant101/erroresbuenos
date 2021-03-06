"""Store all constants for the app."""
SUPPORTED_LANGUAGES = ["english", "spanish", "polish"]

# supported languages for questions
SUPPORTED_LANGUAGES_ABBREV = {"english": "en",
                              "spanish": "es",
                              "polish": "pl"}

AUDIO_FORMATS = ['mp3', 'ogg']

# how many questions to asynchronously add to question queque
NUM_QUESTIONS_TO_LOAD = 3

MIN_QUESTIONS_IN_QUEUE = 3

DEFAULT_LANGUAGE = "spanish"

MAXLEN_ANSWERED_WRONG_STACK = 50

# some new questions are drawn from the ?_answered_wrong_stack
# (? either b for "back" or f for "front") if the stack is big enough
MIN_WRONG_STACK_SIZE_FOR_DRAW = 30

# for "front" sided questions, a new question can be drawn from
# f_answered_review_stack, if the stack is big enough
MIN_REVIEW_STACK_SIZE_FOR_DRAW = 30

# in order not be always at the maximum length, delete extra elements
# whenever the stack gets filled up
MAXLEN_SLACK_ANSWERED_WRONG_STACK = 10

# used to serve questions when unlogged user lands on home page
DEFAULT_TEMP_STUDENT_ID = "5bd362a7fde08a404c92228c"

# maxium length of the user's answer
MAX_USER_ANSWER_LEN = 100

# after reaching this many correct answers, the answered_corr_stack
# is reduced to BASE_ANSWERED_CORRECTLY questions,
# i.e. questions are released for review.
START_REVIEW = 400

# when answered_corr_stack size passes START_REVIEW, reduce the stack
# to this number of questions
BASE_ANSWERED_CORRECTLY = 100

# show tutorial messages for temp students with less than these many
# questions answered
TUTORIAL_CUTOFF = 10

# adddress of the email account from which password reset emails are sent.
EMAIL_SENDER = "password@qwell.ca"
