from flask import Flask, request, render_template
import openai
from config import API_KEY_OPENAI  

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')





def getGPTResponse(prompt):
    openai.api_key = API_KEY_OPENAI
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=200)
    return response.choices[0].text.strip()


@app.route('/', methods =["GET", "POST"])
def getFormData():
    protein = request.form.get("protein")
    cals = request.form.get("calories")
    ingredients = request.form.get("ingredients")
    servings = request.form.get("servings")

    return 'Success!'

       


if __name__ == '__main__':
    app.run(debug=True)