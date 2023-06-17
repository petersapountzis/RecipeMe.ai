from flask import Flask, request, render_template, session, url_for, redirect
import openai
from config import API_KEY_OPENAI  
import re

app = Flask(__name__)
app.secret_key = 'zh6songlyepo36e'
protein, cals, ingredients, servings = None, None, None, None

# @app.route("/")
# def hello_world():
    # return render_template('/index.html')

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
            {"role": "system", "content": "You are a meal generator. I am a user who wants a recipe. I will give you OPTIONAL information about what I want in my recipe. If no servings are specified, assume just 1 serving. For all other fields, if no data is provided, you have jurisdiction over it. I want you to create a recipe for me. It should be a singular recipe. I want a name for the recipe labeled before and after with ##Name##. For example: ##Name## Chicken Curry ##Name##. I want an ingredients section labeled ##Ingredients##, a directions section labeled ##Directions##, and a nutrition facts section labeled ##Nutrition Facts##."},
            {"role": "user", "content": prompt}
        ]
    )
    cleaned_response = completion['choices'][0]['message']['content']

    match = re.search(r'##Name##(.*)##Name##', cleaned_response)
    if match:
        dish_name = match.group(1)

    img = openai.Image.create(
        prompt= dish_name,
        n=1,
        size="1024x1024"
    )
    image = img['images'][0]['url']
    return render_template('/recipe.html', response=cleaned_response, image=image)





       

if __name__ == '__main__':
    app.run(debug=True)