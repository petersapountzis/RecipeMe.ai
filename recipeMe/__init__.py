from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai
import os
  
import re
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_seasurf import SeaSurf
from celery import Celery


app = Flask(__name__)
app.secret_key = 'zh6songlyepo36e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from .celery_utils import make_celery

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0' # or your Redis URL
app.config['API_KEY_OPENAI'] = os.getenv('API_KEY_OPENAI')


# Initialize Celery
celery = make_celery(app.name, app.config['CELERY_BROKER_URL'])

# Import routes after initializing Celery to avoid circular imports
from . import routes

from recipeMe import routes