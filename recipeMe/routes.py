from flask import request, render_template, session, url_for, redirect, flash, request, jsonify
from recipeMe import app, db, bcrypt 
from recipeMe.models import User, Recipe
from recipeMe.login import RegistrationForm, LoginForm
import openai
from recipeMe.config import API_KEY_OPENAI
import re
from flask_login import login_user, current_user, logout_user, login_required
import json




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
    token = request.form.get('csrf_token')
    
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
# @login_required
def library():
    return render_template('library.html')


@app.route('/form', methods =["GET", "POST"])
def getFormData():
    if request.method == 'POST':
        # Form has been submitted, store the data
        print(request.form)  # This line is new; it prints the form data
        session['protein'] = request.form.get("protein")
        session['cals'] = request.form.get("calories")
        session['ingredients'] = request.form.get("ingredients")
        session['servings'] = request.form.get("servings")
        session['cuisine'] = request.form.get("cuisine")

        redirect_url = url_for('getGPTResponse')
        print('redirect')
        return jsonify({"redirect_url": redirect_url})
        
    if request.method == 'GET':
        return render_template('index.html')

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

protein, cals, ingredients, servings, cuisine = '', '', '', '', ''
@app.route('/recipe', methods =["GET", "POST"])
def getGPTResponse():
    openai.api_key = API_KEY_OPENAI
    protein = session.get('protein', 30)
    cals = session.get('cals', 500)
    ingredients = session.get('ingredients', '')
    servings = session.get('servings', 1)
    cuisine = session.get('cuisine', '')
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
    image_prompt = f'{name}, food photography, morning light, 15mm'
    image = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="256x256"
    )
    image_url = image['data'][0]['url']
    # image_url = 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-4DfDJ6RG5WPUDAvY3ML4Q03p/user-8MIVw41uvGSUWG9K6ImbKrwh/img-PWGIVMhrW9Zg0CWwnhLi7y23.png?st=2023-06-18T15%3A30%3A02Z&se=2023-06-18T17%3A30%3A02Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-06-17T20%3A53%3A36Z&ske=2023-06-18T20%3A53%3A36Z&sks=b&skv=2021-08-06&sig=lQsmOucRxmhZmZfpPDNfAimFtAYAa0uxF12j1GbQVxI%3D'
    json_ingredients = {
        "ingredients": json.dumps(ingredientsList)
    }
    return render_template('recipe.html',ingredients=ingredientsList, name=name , directions=directions, nutrition_facts=nutrition_facts, image_url=image_url)




