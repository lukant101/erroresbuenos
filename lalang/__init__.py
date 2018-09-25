from flask import Flask
from flask_mongoengine import MongoEngine

# app = Flask("lalang", template_folder="C:/Users/Lukasz/Python/ErroresBuenos/lalang/templates")
app = Flask("lalang")

# app.config.from_pyfile('the-config.cfg')

app.config['MONGODB_SETTINGS'] = {
    'db': 'lalang_db',
    'host': 'localhost',
    'port': 27017
}

db = MongoEngine(app)

from lalang import routes
