from flask import Flask
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os
from lalang.response_headers import CustomResponse

app = Flask("lalang")

app.config.from_pyfile('../app_config.cfg')

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')


mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = MongoEngine(app)

bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)

app.response_class = CustomResponse

from lalang import routes
