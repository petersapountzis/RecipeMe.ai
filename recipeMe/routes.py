from flask import request, render_template, session, url_for, redirect, flash, request, jsonify, make_response
from recipeMe import app, db, bcrypt
from recipeMe.models import User, Recipe
from recipeMe.login import RegistrationForm, LoginForm
import openai
import re
from flask_login import login_user, current_user, logout_user, login_required
import json
import pdfkit
import os

# path_wkhtmltopdf = os.environ.get('WKHTMLTOPDF_BINARY', '/usr/local/bin/wkhtmltopdf')
# config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# home page route
@app.route("/home")
@app.route("/")
def home():
    return render_template('/home.html')

# recipe page route 
@app.route("/register", methods =["GET", "POST"])
def register():
    if current_user.is_authenticated:
        # if logged in send them to home page
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # encrypt password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        # add user to database
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to login.', 'success')
        # once registered, make them login
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# login page route
@app.route("/login", methods=['GET', 'POST'])
def login():
    # fetch cross site request forgery token
    token = request.form.get('csrf_token')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # ensure user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            print('login unsuccessful')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/library")
@login_required
def library():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()  # get all recipes by the current user
    for recipe in recipes:
        # Convert the ingredients and directions string back to list
        recipe.ingredients = json.loads(recipe.ingredients)
        recipe.directions = json.loads(recipe.directions)
    return render_template('library.html', recipes=recipes)  # render the library page with the recipes



@app.route('/form', methods =["GET", "POST"])
def getFormData():
    session_keys = ['protein', 'cals', 'ingredients', 'servings', 'cuisine', 'dish', 'recipe']
    for key in session_keys:
        if key in session:
            session.pop(key)

    if request.method == 'POST':
        # Form has been submitted, store the data in session variables
        session['protein'] = request.form.get("protein")
        session['cals'] = request.form.get("calories")
        session['ingredients'] = request.form.get("ingredients")
        session['servings'] = request.form.get("servings")
        session['cuisine'] = request.form.get("cuisine")
        session['dish'] = request.form.get("dish")

        redirect_url = url_for('getGPTResponse')
        # Redirect to the GPT response page using loading.js, need it in json format
        return jsonify({"redirect_url": redirect_url})
        
    if request.method == 'GET':
        return render_template('index.html')

# Helper function to extract the recipe name, ingredients, directions, and nutrition facts from the GPT response
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


# Helper function to convert the ingredients string to a list
def ingredients_to_list(ingredients):
    if ingredients is None:
        return []
    # Split the string by commas and strip whitespaces
    ingredients_list = [ingredient.strip() for ingredient in ingredients.split('-')]
    ingredients_list = ingredients_list[1:]
    return ingredients_list


# Helper function to parse the directions string into a list of instructions
def parse_instructions(instructions):
    if instructions is None:
        return []
    # Split by digit-period-space pattern, keep the digit and period with the instruction
    return re.split('\s(?=\d+\.)', instructions)


protein, cals, ingredients, servings, cuisine, dish = '', '', '', '', '', ''

# recipe page route
@app.route('/recipe', methods =["GET", "POST"])
def getGPTResponse():
    openai.api_key = os.environ.get('API_KEY_OPENAI')
    print(session)
    # Get the form data from the session variables, add optional fields if not provided
    protein = session.get('protein', 'any')
    cals = session.get('calories', 'any')
    dish = session.get('dish', 'any')
    ingredients = session.get('ingredients', 'any')
    servings = session.get('servings', 1)
    cuisine = session.get('cuisine', 'any')
    # Prompt for the GPT-3.5 API
    prompt = f"Hello. I want {servings} servings of {cuisine} {dish}. I want around {protein} grams of protein, and around {cals} calories. I want {ingredients} ingredients included. If I include any ingredients make sure they are incorportaed in the dish. "
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a meal generator. I am a user who wants a recipe. I will give you OPTIONAL information about what I want in my recipe. If no servings are specified, assume just 1 serving. For all other fields, if no data is provided, you have jurisdiction over it. I want you to create a recipe for me. It should be a singular recipe. I want a name for the recipe that is as appetizing and professional as possible, labeled before and after with ##Name##. For example: ##Name## Chicken Curry ##Name##, this will follow the same pattern for all other sections. I want an ingredients section surrounded by ##Ingredients## tag where each ingredient is separated by comma, a directions section surrouned ##Directions## tag, and a nutrition facts section surrounded ##Nutrition Facts## tag."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )
    # parse json response for content
    cleaned_response = completion['choices'][0]['message']['content']
    name, GPTingredients, directions, nutrition_facts = extract_recipe_info(cleaned_response)

    # DALLE prompt
    image_prompt = f'Generate a high-resolution image of a freshly prepared dish. The dish is a {name}. It is plated on a white, ceramic dish, placed on a rustic wooden table. The lighting should highlight the textures and colors of the dish, making it look appetizing and ready to eat.  In the background, slightly out of focus, there should be a bottle of red wine and a lit candle to create a warm, cozy atmosphere.'

    image = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = image['data'][0]['url']
    
    # Convert the ingredients and directions string to a list
    ingredientsList = ingredients_to_list(GPTingredients)
    instructionsList = parse_instructions(directions)
    
    json_ingredients = {
        "ingredients": json.dumps(ingredientsList)
    }

    recipe_data = {
            'name': name,
            'ingredients': ingredientsList,
            'directions': instructionsList,
            'nutrition_facts': nutrition_facts,
            'image_url': image_url
        }

    session['recipe'] = recipe_data
    return render_template('recipe.html',ingredients=ingredientsList, name=name , directions=instructionsList, nutrition_facts=nutrition_facts, image_url=image_url)


@app.route('/add_to_library', methods=['POST'])
@login_required  # Ensure that a user is logged in before they can add a recipe to the library
def add_to_library():
    # Get the recipe details from the session data
    print('add to library clicked')
    recipe_data = session.get('recipe')
    if recipe_data is None:
        flash('No recipe to add to the library. Please generate a recipe first.', 'warning')
        print('recipe data DNE')
        return redirect(url_for('register'))
        
    # Create a new Recipe and save it to the database
    recipe = Recipe(
        name=recipe_data['name'], 
        ingredients=json.dumps(recipe_data['ingredients']),  # Convert list to string
        directions=json.dumps(recipe_data['directions']),  # Convert list to string
        nutrition_facts=recipe_data['nutrition_facts'], 
        user_id=current_user.id,
        image_url=recipe_data['image_url'])
    
    # add recipe to DB if clicked
    db.session.add(recipe)
    db.session.commit()

    # remove the recipe from the session data now
    session.pop('recipe')

    # Redirect the user back to the library or wherever you want
    return redirect(url_for('library'))



@app.route("/delete_recipe/<int:recipe_id>", methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    # Fetch the recipe by id
    recipeToRemove = Recipe.query.get_or_404(recipe_id)

    # Ensure that the current user is the owner of the recipe
    if recipeToRemove.user_id != current_user.id:
        flash('You do not have permission to delete this recipe.', 'error')
        return redirect(url_for('library'))

    # If the current user is the owner of the recipe, delete the recipe
    db.session.delete(recipeToRemove)
    db.session.commit()
    
    flash('Recipe deleted.', 'success')
    return redirect(url_for('library'))


@app.route('/export_recipe/<int:recipe_id>', methods=['POST', 'GET'])
def export_recipe(recipe_id):
    path_wkhtmltopdf = os.getenv('WKHTMLTOPDF_PATH', '/usr/local/bin/wkhtmltopdf')
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Fetch the recipe by id
    recipe = Recipe.query.get_or_404(recipe_id)
    # Convert the ingredients and directions string back to list
    export_ing = json.loads(recipe.ingredients)
    export_dir = json.loads(recipe.directions)
    # nutrition = json.loads(recipe.nutrition_facts)
    # print(nutrition)
    html = render_template('recipe_export.html', ingredients=export_ing, name=recipe.name, directions=export_dir, nutrition_facts=recipe.nutrition_facts, image_url=recipe.image_url)

    # Create a PDF from the HTML
    pdf = pdfkit.from_string(html, False, configuration=config)

    # Create response with the PDF data
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={recipe.name}.pdf'
    return response


@app.route('/regenerate', methods=['POST'])
def regenerate():
    # Re-generate a new recipe using GPT
    return redirect(url_for('getGPTResponse'))