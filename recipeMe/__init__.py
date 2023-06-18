from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai
from recipeMe.config import API_KEY_OPENAI  
import re
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_seasurf import SeaSurf
app = Flask(__name__)
app.secret_key = 'zh6songlyepo36e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


from recipeMe import routes