from myTestSet.db_model import Question
import os
import helpers.get_template_questions

print(os.getcwd())

question = Question(description="fun times")
print(question.description)
