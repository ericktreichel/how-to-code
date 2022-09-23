from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '6689d962d0d62f80448c1c83fcbbcaab8fda1b9bfa1c77ceb90e042ac9f656cd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-warning'

from comunidadeimpressionadora import routes
