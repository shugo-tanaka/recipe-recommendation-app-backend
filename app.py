from flask import Flask, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS
import json

from typing import Union, List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import numpy as np

app = Flask(__name__)
CORS(app,resources={r"/*": {"origins": "http://localhost:3000"}})

# prompt = ''
# ingredients = []
# servings = 0
# cookTime = 0
# cuisineType = ""
# allergies = []

url: str=os.environ.get("SUPABASE_URL")
key: str=os.environ.get("SUPABASE_API_KEY")
host_link: str = os.environ.get("FRONTEND_URL")
supabase: Client = create_client(url, key)

origins = [
    host_link,
]

# app2.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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
            allergiesString += ", "
        allergiesString += allergies[i]
    
    if cuisineType == "-":
        cuisineType = "good"
        result['cuisineType'] = cuisineType
    
    dictionary = "{{}}"
    prompt = 'I currently have {} and am looking for a {} dish for {} servings with cook time under {} minutes. My allergies include {}. Can you return a list of at least 5 and up to 15 dishes found on popular food websites with their respecitve cook times? I will provide a format for the response. You do not need to use all the ingredients listed. Please start the response with [ and straight to the format with no dialogue preceding the array. format: [{{"name": name of dish, "cook_time": cook time for dish, "ingredients": list ingredients separated by commas and add (additional) next to ones that are additional ingredients, "instructions": array with numbered cooking steps as elements}}, {{same format as dictionary before but with next dish}},...}}]'.format(ingredientsQuantityString,cuisineType,servings,cookTime,allergiesString)
    result['prompt'] = prompt
    # print(prompt)
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
    responseString = completion.choices[0].message.content
    response = json.loads(responseString)
    print(prompt)
    print(response)
    # print('done')

    return jsonify({'response':response})

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

@app.route('/add_recipe', methods=['POST'])
def addRecipe():
    try:
        # Get the JSON data from the request
        recipe = request.get_json()
        
        # Log the received data for debugging
        logging.info("Received data: %s", recipe)

        # Ensure recipe contains the necessary fields
        if not recipe or 'name' not in recipe or 'cook_time' not in recipe:
            return jsonify({"error": "Invalid recipe data"}), 400

        # Query Supabase for existing recipes
        response = supabase.table('recipe_database').select('id').execute()
        logging.info("Supabase response: %s", response.data)

        # Determine the new recipe ID
        id = 0
        if response.data:
            x = response.data
            x.sort(key=lambda z: z['id'])
            id = x[-1]['id'] + 1
        
        # Prepare data for upsert
        upsert_data = [{
            'id': id,
            'name': recipe['name'],
            'cook_time': recipe['cook_time'],
            'ingredients': recipe['ingredients'],
            'instructions': recipe['instructions']
        }]
        
        # Upsert data into Supabase
        data, count = supabase.table('recipe_database').upsert(upsert_data).execute()
        logging.info("Upserted data: %s", data)

        return jsonify({"message": "Recipe added successfully", "recipe": recipe}), 201

    except Exception as e:
        logging.error("Error adding recipe: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)