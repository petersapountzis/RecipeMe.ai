from recipeMe import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False) 
    password = db.Column(db.String(60), nullable = False)
    recipes = db.relationship('Recipe', backref = 'author', lazy = True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    ingredients = db.Column(db.String(1000), nullable = False)
    directions = db.Column(db.String(1000), nullable = False)
    nutrition_facts = db.Column(db.String(1000), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Recipe('{self.name}', '{self.ingredients}', '{self.directions}', '{self.nutrition_facts}')"
