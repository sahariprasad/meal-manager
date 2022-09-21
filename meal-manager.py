import os, json
from flask import Flask, redirect, url_for, request, render_template
import pymongo

# Connect to mongoDB
mongo_client = pymongo.MongoClient("mongodb://172.20.0.2:27017/")
fatboy_db = mongo_client["fatboy"]
food_collection = fatboy_db["food"]

# Set flask app name
app = Flask(__name__)

# Default hello world route
@app.route('/')
def hello_world():
    return 'Hey there! Go to /fatboy to find food!'

# Default fatboy route
@app.route('/fatboy')
def fatboy():
    return 'Eat well and get fat.'

# Route for adding a single recipe
@app.route('/fatboy/add_one_recipe', methods=['POST'])
def add_one_recipe():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        recipe_dict = request.json
        try:
            insert_1 = food_collection.insert_one(recipe_dict)
        except pymongo.errors.DuplicateKeyError:
            return "Duplicate Key, _id:{} already exists. Try another _id.".format(recipe_dict["_id"])
        return "{} added".format(recipe_dict["_id"])
        # return "{} added".format(recipe_dict["name"])
    else:
        return 'Content-Type not supported!'


# Route for adding multiple recipes
@app.route('/fatboy/add_many_recipes', methods=['POST'])
def add_many_recipes():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        recipe_dict = request.json
        try:
            insert_many = food_collection.insert_many(recipe_dict, ordered=False)
        except pymongo.errors.BulkWriteError as exception:
            write_error_count = len(exception.details["writeErrors"])
            write_error_list = []
            for item in exception.details["writeErrors"]:
                if item["code"] == 11000:
                    write_error_list.append("Duplicate Key, _id:{} already exists. Try another _id.".format(item["keyValue"]["_id"]))
            error_dict = {"write_error_count": write_error_count,"write_errors": write_error_list}
            return error_dict
        return "Many recipes added"
    else:
        return 'Content-Type not supported!'


# Route for finding possible foods
@app.route('/fatboy/find_food', methods=["POST"])
def find_food():
    content_type = request.headers.get('Content-Type')
    possible_recipes = []
    if (content_type == 'application/json'):
        ingredient_list = request.json
        all_recipes = list(food_collection.find().sort('pretty_name'))
        for item in all_recipes:
            if set(item["mandatory_ingredients"]).issubset(ingredient_list):
                possible_recipes.append(item["pretty_name"])
        return str(possible_recipes)


# Route for getting list of all recipes
@app.route('/fatboy/get_all_recipes', methods=['GET'])
def get_all_recipes():
    recipe_list = list(food_collection.find())
    return(str(recipe_list))


# Route for getting list of all ingredients (returns pretty names)
@app.route('/fatboy/get_all_ingredients', methods=["GET"])
def get_all_ingredients():
    all_recipes = list(food_collection.find())
    ingredients_list_full = []
    for item in all_recipes:
        ingredients_list_full.extend(item["mandatory_ingredients"])
    ingredients_list_full = set(ingredients_list_full)
    ingredients_list_full = [ingredient.capitalize() for ingredient in ingredients_list_full]
    ingredients_list_full.sort()

    return {"all_ingredients": ingredients_list_full}

# def find_food(item_list_string=None):
#     # get available items list
#     item_list_string = item_list_string.replace('\n',',').lower()
#     print(item_list_string)
#     available_items = item_list_string.split(',')

#     # read all recipes
#     recipe_path = "meal-manager/recipes"
#     recipe_files = [pos_json for pos_json in os.listdir(recipe_path) if pos_json.endswith('.json')]

#     recipe_dict = {}
#     for item in recipe_files:
#         recipe_name = item.replace(".json", "")
#         file = open(recipe_path + '/' + item, 'r', encoding='utf-8')
#         file_dict = json.load(file)
#         recipe_dict[recipe_name] = file_dict

#     # Check for possible dishes
#     possible_dishes = []
#     for item in recipe_dict:
#         if set(recipe_dict[item]["ingredients"]["mandatory"]).issubset(available_items):
#             possible_dishes.append(recipe_dict[item]["pretty-name"])

#     food_dict = {"foods": possible_dishes}
#     food_dict_str = str(food_dict).replace("'", '"')
#     return food_dict_str


# @app.route('/fatboy/get_all_ingredients')
# def get_all_ingredients():
#     # read all recipes
#     recipe_path = "meal-manager/recipes"
#     print(os.listdir(recipe_path))
#     recipe_files = [pos_json for pos_json in os.listdir(recipe_path) if pos_json.endswith('.json')]

#     recipe_dict = {}
#     for item in recipe_files:
#         recipe_name = item.replace(".json", "")
#         file = open(recipe_path + '/' + item, 'r', encoding='utf-8')
#         file_dict = json.load(file)
#         recipe_dict[recipe_name] = file_dict

#     ingredient_list = []
#     for item in recipe_dict:
#         ingredient_list += recipe_dict[item]["ingredients"]["mandatory"]
    
#     ingredient_dict = {"ingredients": list(set(ingredient_list))}
#     ingredient_dict_str = str(ingredient_dict).replace("'", '"')
#     return ingredient_dict


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 1234)