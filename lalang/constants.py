"""Store all constants for the app."""
SUPPORTED_LANGUAGES = ["english", "spanish", "polish"]

# how many questions to asynchronously add to question queque
NUM_QUESTIONS_TO_LOAD = 3

MIN_QUESTIONS_IN_QUEUE = 3

DEFAULT_LANGUAGE = "spanish"

MAXLEN_ANSWERED_WRONG_STACK = 50

# in order not be always at the maximum length, delete extra elements
# whenever the stack gets filled up
MAXLEN_SLACK_ANSWERED_WRONG_STACK = 10


# lukasz
student_id = "5bc56cb8fde08a2fe809e796"

# denise
# student_id = "5bc56d35fde08a62b029112e"