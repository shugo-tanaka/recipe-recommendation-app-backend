# Completed


# To Do
# double check there are no duplicates in the recipe database. -> need to add only if its not in there.


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
    uuid = data.get('uuid')
   

    # get top rated recipes for feedback loop
    data1, count = supabase.table('user_saved').select('saved, ratings').in_('UUID', [uuid]).execute()
    saved = data1[1][0]['saved']
    ratings = data1[1][0]['ratings']
    savedRatings = list(zip(saved, ratings))
    savedRatings.sort(key = lambda x: x[1])
    count = 0
    if len(savedRatings) >= 10:
        count = 10
    else:
        count = len(savedRatings)

    topSaved = [savedRatings[i][0] for i in range(count)]
    topSavedRatings = [savedRatings[i][1] for i in range(count)]
    
    topRecs, count = supabase.table('recipe_database').select('name').order('id', desc=False).in_('id', topSaved).execute()
    topSavedRatings2 = list(zip(topSaved, topSavedRatings))
    topSavedRatings2.sort(key = lambda x: x[0], reverse=False)
    # top recs is in ascending order
    # print('these are the top recipes', topRecs[1])
    # print('these are the corresponding ratings:', topSavedRatings2)
    feedBackPrompt = "Note, here are recipes and their corresponding ratings out of 5 so that the response can be tailored to what you believe may be preferences: "
    if len(topRecs[1]) == 0:
        feeBackPrompt = ""
    else:
        for i in range(len(topRecs[1])):
            feedBackPrompt += "{} was rated a {},".format(topRecs[1][i]['name'], topSavedRatings2[i][1])
        feedBackPrompt = feedBackPrompt[:-1] + ". Also note that any 0 ratings may indicate a lack of rating as opposed to a 0/5 rating."
    
    # print('this is the feed back prompt:', feedBackPrompt)

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
    prompt = 'I currently have {} and am looking for a {} dish for {} servings with cook time under {} minutes. My allergies include {}. Can you return a list of 5 to 15 dishes found on popular food websites with their respecitve cook times? I will provide a format for the response. You do not need to use all the ingredients listed. {} Please start the response with [ and straight to the format with no dialogue preceding the array. format: [{{"name": name of dish, "cook_time": cook time for dish, "ingredients": list ingredients separated by commas and add (additional) next to ones that are additional ingredients, "instructions": array with numbered cooking steps as elements}}, {{same format as dictionary before but with next dish}},...}}]'.format(ingredientsQuantityString,cuisineType,servings,cookTime,allergiesString, feedBackPrompt)
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

@app.route('/add_user_row', methods=['POST'])
def addUserSaveRow():
    try:
        # Get the JSON data from the request
        importedData = request.get_json()
        UUID = importedData['id']
        logging.info("Received data: %s", UUID)

        # Ensure recipe contains the necessary fields
        if not UUID:
            return jsonify({"error": "no UUID"}), 400

        # Prepare data for upsert
        upsert_data = [{
            'UUID': UUID,
            'saved': [],
            'ratings': []
        }]
        
        # Upsert data into Supabase
        data, count = supabase.table('user_saved').upsert(upsert_data).execute()
        logging.info("Upserted data: %s", UUID)

        return jsonify({"message": "saved recipe row for UUID added successfully", "UUID": UUID}), 201

    except Exception as e:
        logging.error("Error adding recipe: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/add_recipe', methods=['POST'])
def addRecipe():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        recipe = data.get('recipe')
        uuid = data.get('uuid')
        uuidList = [uuid]
        # print("this is the id: {}".format(uuid))
        # auth_header = request.get('Authorization')
        # print(auth_header)
        
        # Log the received data for debugging
        logging.info("Received data: %s", recipe)

        # Ensure recipe contains the necessary fields
        if not recipe or 'name' not in recipe or 'cook_time' not in recipe:
            return jsonify({"error": "Invalid recipe data"}), 400

        # Query Supabase for existing recipes
        response = supabase.table('recipe_database').select('id').execute()
        postgres_array = "{" + ", ".join([f'"{step}"' for step in recipe['instructions']])+"}"
        duplicateItems, count = supabase.table('recipe_database').select('id').match({'name':recipe['name'], 'cook_time':recipe['cook_time'], 'ingredients':recipe['ingredients'], 'instructions':postgres_array}).execute()

        print('this is the response', duplicateItems[1])
        # print('response 1 received')
        response2 = supabase.table('user_saved').select('*').in_('UUID', uuidList).execute()
        # print('this is response 2',response2)
        response2Data = response2.data
        # print('this is response2Data', response2Data)
        saved = response2Data[0]['saved']
        ratings = response2Data[0]['ratings']
        # print('response2 received')
        # saved = []
        # for i in response2.data:
        #     if i['UUID'] == uuid:
        #         saved = i['saved']
        # print('saved array pulled', saved)
        
        logging.info("Supabase response: %s", response.data)

        # Determine the new recipe ID
        id = 0
        if response.data:
            if duplicateItems[1]:
                id = duplicateItems[1][0]['id']
            else:
                x = response.data
                x.sort(key=lambda z: z['id'])
                id = x[-1]['id'] + 1

        if id not in saved:
            saved.append(int(id))
            ratings.append(0)
        # print('id added to saved array', saved)
        # once signed up, row for your UUID should already be created.
        
        # Prepare data for upsert
        upsert_data = [{
            'id': id,
            'name': recipe['name'],
            'cook_time': recipe['cook_time'],
            'ingredients': recipe['ingredients'],
            'instructions': recipe['instructions']
        }]

        # upsert_data2 = [{
        #     'UUID': uuid,
        #     'saved': saved,
        #     'ratings': ratings
        # }]

        # print(upsert_data2)
        
        # Upsert data into Supabase
        if not duplicateItems[1]:
            data, count = supabase.table('recipe_database').upsert(upsert_data).execute()
        data2 = supabase.table('user_saved').update({'saved':saved, 'ratings':ratings}).eq('UUID', uuid).execute()
        logging.info("Upserted data: %s", data)
        logging.info("Upserted data: %s", data2)

        return jsonify({"message": "Recipe added successfully", "recipe": recipe}), 201

    except Exception as e:
        logging.error("Error adding recipe: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/fetch_saved', methods=['POST'])
def fetchSaved():
    try:
        # Get the JSON data from the request
        importedData = request.get_json()
        UUID = importedData.get('id')
        logging.info("Received data: %s", UUID)

        # Ensure recipe contains the necessary fields
        if not UUID:
            return jsonify({"error": "no UUID"}), 400
        
        response_user_saved = supabase.table('user_saved').select('*').execute()
        saved_id = []
        ratings = []
        for i in response_user_saved.data:
            if i['UUID'] == UUID:
                saved_id = i['saved']
                ratings = i['ratings']
        
        response_recipe_database, count = supabase.table('recipe_database').select('*').in_('id', saved_id).order('id', desc=False).execute()
        logging.info("Retrieved data: %s", response_recipe_database)

        return jsonify({"saved": response_recipe_database, "ratings":ratings}), 201


    except Exception as e:
        logging.error("Error retrieving saved recipes: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/update_rating', methods=['POST'])
def updateRating():
    try:
        # Get the JSON data from the request
        importedData = request.get_json()
        uuid = importedData.get('id')
        ratings = importedData.get('ratings')
        logging.info("Received data: %s", uuid)
        print(uuid, ratings)

        

        # Ensure recipe contains the necessary fields
        if not uuid:
            return jsonify({"error": "no UUID"}), 400
        
        data = supabase.table('user_saved').update({'ratings':ratings}).eq('UUID', uuid).execute()
    

        return jsonify({"ratings":ratings}), 201


    except Exception as e:
        logging.error("Error updating ratings: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500

@app.route('/unsave_rec', methods=['POST'])
def unsaveRec():
    try:
        importedData = request.get_json()
        uuid = importedData.get('id')
        indexToRemove = importedData.get('indexToRemove')
        newRatings = importedData.get('newRatings')
        # print('these are the new ratings', newRatings)
        print('this is the index to remove', indexToRemove)

        data1 = supabase.table('user_saved').select('saved').in_('UUID', [uuid]).execute()
        indeces = data1.data[0]['saved']
        print('these are the indeces before', indeces)
        indeces = indeces[:indexToRemove] + indeces[indexToRemove+1:]
        print('these are the indeces',indeces)
        if not uuid:
            return jsonify({'error': "no UUID"}), 400
        data = supabase.table('user_saved').update({'saved':indeces, 'ratings':newRatings}).eq('UUID', uuid).execute()
        return jsonify({"message":"recipe has been successfully unsaved"})
    except Exception as e:
        logging.error("Error unsaving: %s", str(e))
        return jsonify({"error":"Internal server error"}), 500
    
@app.route('/unsave_rec_v2', methods=['POST'])
def unsaveRecV2():
    try:
        data = request.get_json()
        
        uuid = data.get('id')
        indexToRemove = data.get('indexToRemove')
        rec = data.get('rec')
        print('check', rec)
        postgres_array = "{" + ", ".join([f'"{step}"' for step in rec['instructions']])+"}"
        recipeIndex, count = supabase.table('recipe_database').select('id').match({'name':rec['name'], 'cook_time':rec['cook_time'], 'ingredients':rec['ingredients'], 'instructions':postgres_array}).execute()
        print('this is the recipe index', recipeIndex)
        tableData, count = supabase.table('user_saved').select('saved, ratings').in_('UUID', [uuid]).execute()
        saved = tableData[1][0]['saved']
        ratings = tableData[1][0]['ratings']
        print('this is prior to loop', saved, ratings)
        for i in range(len(saved)):
            if saved[i] == recipeIndex[1][0]['id']:
                saved = saved[:i] + saved[i+1:]
                ratings = ratings[:i]+ratings[i+1:]
                break
        print('this is post loop', saved, ratings)
        d = supabase.table('user_saved').update({'saved':saved, 'ratings':ratings}).eq('UUID', uuid).execute()
        return jsonify({"message":"unsaved"})
    except Exception as e:
        logging.error("Error unsaving: %s", str(e))
        return jsonify({"error":"Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)