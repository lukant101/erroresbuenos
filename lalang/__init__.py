from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, user_logged_out

# app = Flask("lalang", template_folder="C:/Users/Lukasz/Python/ErroresBuenos/lalang/templates")
app = Flask("lalang")

app.config.from_pyfile('app_config.cfg')

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = MongoEngine(app)

bcrypt = Bcrypt(app)

from lalang import routes
