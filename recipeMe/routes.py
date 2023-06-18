from flask import request, render_template, session, url_for, redirect, flash
from recipeMe import app
from recipeMe.models import User, Recipe
from recipeMe.login import RegistrationForm, LoginForm
import openai
from recipeMe.config import API_KEY_OPENAI
import re



@app.route("/home")
@app.route("/")
def home():
    return render_template('/home.html')

@app.route("/register", methods =["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('/'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


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
    return render_template('/recipe.html', name=name, ingredients=ingredients, directions=directions, nutrition_facts=nutrition_facts)



