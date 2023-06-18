from flask import request, render_template, session, url_for, redirect, flash, request
from recipeMe import app, db, bcrypt
from recipeMe.models import User, Recipe
from recipeMe.login import RegistrationForm, LoginForm
import openai
from recipeMe.config import API_KEY_OPENAI
import re
from flask_login import login_user, current_user, logout_user, login_required, 



@app.route("/home")
@app.route("/")
def home():
    return render_template('/home.html')

@app.route("/register", methods =["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('landing'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/landing")
def landing():
    return render_template('landing.html')

@app.route("/library")
@login_required
def library():
    return render_template('library.html')


@app.route('/form', methods =["GET", "POST"])
def getFormData():
    if request.method == 'POST':
        # Form has been submitted, store the data
        session[protein] = request.form.get("protein")
        session[cals] = request.form.get("calories")
        session[ingredients] = request.form.get("ingredients")
        session[servings] = request.form.get("servings")
        session[cuisine] = request.form.get("cuisine")
        return redirect(url_for('getGPTResponse'))
    if request.method == 'GET':
        return render_template('/index.html')

def extract_recipe_info(recipe_string):
    name_pattern = r"##Name##(.*?)##Name##"
    ingredients_pattern = r"##Ingredients##(.*?)##Directions##"
    directions_pattern = r"##Directions##(.*?)##Nutrition Facts##"
    nutrition_facts_pattern = r"##Nutrition Facts##(.*)"

    name_match = re.search(name_pattern, recipe_string, re.DOTALL)
    ingredients_match = re.search(ingredients_pattern, recipe_string, re.DOTALL)
    directions_match = re.search(directions_pattern, recipe_string, re.DOTALL)
    nutrition_facts_match = re.search(nutrition_facts_pattern, recipe_string, re.DOTALL)

    recipe_name = name_match.group(1).strip() if name_match else None
    ingredients = ingredients_match.group(1).strip() if ingredients_match else None
    directions = directions_match.group(1).strip() if directions_match else None
    nutrition_facts = nutrition_facts_match.group(1).strip() if nutrition_facts_match else None

    return recipe_name, ingredients, directions, nutrition_facts

def ingredients_to_list(ingredients):
    # Split the string by commas and strip whitespaces
    ingredients_list = [ingredient.strip() for ingredient in ingredients.split('-')]
    return ingredients_list

protein, cals, ingredients, servings, cuisine = None, None, None, None, None
@app.route('/recipe', methods =["GET", "POST"])
def getGPTResponse():
    openai.api_key = API_KEY_OPENAI
    protein = session.get('protein', 'any')
    cals = session.get('cals', 'any')
    ingredients = session.get('ingredients', 'any')
    servings = session.get('servings', 'any')
    cuisine = session.get('cuisine', 'any')
    prompt = f"Hello. I want {servings} servings of {cuisine} cuisine. I want around {protein} grams of protein, and around {cals} calories. I want {ingredients} ingredients included. "


    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a meal generator. I am a user who wants a recipe. I will give you OPTIONAL information about what I want in my recipe. If no servings are specified, assume just 1 serving. For all other fields, if no data is provided, you have jurisdiction over it. I want you to create a recipe for me. It should be a singular recipe. I want a name for the recipe labeled before and after with ##Name##. For example: ##Name## Chicken Curry ##Name##, this will follow the same pattern for all other sections. I want an ingredients section surrounded by ##Ingredients## tag where each ingredient is separated by comma, a directions section surrouned ##Directions## tag, and a nutrition facts section surrounded ##Nutrition Facts## tag."},
            {"role": "user", "content": prompt}
        ]
    )
    cleaned_response = completion['choices'][0]['message']['content']

    name, ingredients, directions, nutrition_facts = extract_recipe_info(cleaned_response)
    ingredientsList = ingredients_to_list(ingredients)
    return render_template('/recipe.html', name=name, ingredients=ingredientsList, directions=directions, nutrition_facts=nutrition_facts)




