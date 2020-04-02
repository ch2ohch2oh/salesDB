from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'f3cfe9ed8fae309f02079dbf'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bootstrap = Bootstrap(app)

from app import routes, models
