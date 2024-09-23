from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# prompt = ''
# ingredients = []
# servings = 0
# cookTime = 0
# cuisineType = ""
# allergies = []

@app.route('/')
def home():
    return "Hello, Flask"

@app.route('/test')
def test():
    return 'testing'

@app.route('/recipe_recommendation_input', methods=['POST'])
def recipeRecInput():

    # Parse the JSON request data
    data = request.get_json()

    # Extract the values from the request data
    ingredients = data.get('ingredientsInput')
    quantity = data.get('quantityInput')
    units = data.get('unitInput')
    servings = data.get('servingsInput')
    cookTime = data.get('cookTimeInput')
    cuisineType = data.get('cuisineTypeInput')
    allergies = data.get('allergiesInput')

    # For now, just return the received data as a response
    result = {
        "ingredients": ingredients,
        "quantity": quantity,
        "units":units, 
        "servings": servings,
        "cuisineType": cuisineType,
        "cookTime": cookTime,
        "allergies": allergies,
        "message": "Recipe input received successfully",
        "prompt" : ""
    }
    # return jsonify(result)
    ingredientsQuantityString = ""
    for i in range(len(ingredients)):
        if len(ingredientsQuantityString) != 0:
            ingredientsQuantityString += ", "
        ingredientsQuantityString += "{} {} of {}".format(quantity[i], units[i], ingredients[i])
    
    allergiesString = ""
    for i in range(len(allergies)):
        if len(allergiesString) != 0:
            allergeiesString += ", "
        allergiesString += allergies[i]
    
    if cuisineType == "-":
        cuisineType = "good"
        result['cuisineType'] = cuisineType
    
    prompt = 'I currently have {} and am looking for a {} dish for {} servings with cook time under {} minutes. My allergies include {}. Can you return a list of dishes with their respecitve cook times? You can list dishes that require more ingredients but please list any additional ingredients if necessary. Please also list a link to the data source for each recipe. Please provide an array of recipes, where each element includes the name, cook time, ingredients, and instructions. Please go straight to the json array in your response.'.format(ingredientsQuantityString,cuisineType,servings,cookTime,allergiesString)
    result['prompt'] = prompt
    print(prompt)
    # Return the response as JSON
    client = OpenAI(organization = os.environ.get('ORGANIZATION_ID'),
                    project=os.environ.get('PROJECT_ID'))

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1500
    )
    print(completion.choices[0].message.content)
    return jsonify({'response':completion.choices[0].message.content})

    # return jsonify(result,prompt), 200


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json # extracts body of request
    prompt = data.get('prompt','')

    response = f"You asked: {prompt}"
    return jsonify({'response': response})

@app.route('/aitest', methods=['POST'])
def aitest():
    client = OpenAI(organization = os.environ.get('ORGANIZATION_ID'),
                    project=os.environ.get('PROJECT_ID'))

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "when was Johns Creek High School built?"
            }
        ],
        max_tokens=200
    )
    print(completion.choices[0].message.content)
    return jsonify({'response':completion.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)