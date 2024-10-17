from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config.from_object('config.Config')
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Add this line

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from app.models import User  # Ensure this import is after db initialization

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app.views import main as main_blueprint
from app.auth import auth as auth_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
