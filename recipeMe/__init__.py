from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai
from recipeMe.config import API_KEY_OPENAI  
import re

app = Flask(__name__)
app.secret_key = 'zh6songlyepo36e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from recipeMe import routes