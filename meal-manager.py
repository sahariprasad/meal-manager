import os, json
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hey there! Go to /fatboy to find food!'


@app.route('/fatboy')
def fatboy():
    return 'Eat well and get fat.'


@app.route('/fatboy/find_food/<item_list_string>')
def find_food(item_list_string=None):
    # get available items list
    item_list_string = item_list_string.replace('\n',',').lower()
    print(item_list_string)
    available_items = item_list_string.split(',')

    # read all recipes
    recipe_path = "meal-manager/recipes"
    recipe_files = [pos_json for pos_json in os.listdir(recipe_path) if pos_json.endswith('.json')]

    recipe_dict = {}
    for item in recipe_files:
        recipe_name = item.replace(".json", "")
        file = open(recipe_path + '/' + item, 'r', encoding='utf-8')
        file_dict = json.load(file)
        recipe_dict[recipe_name] = file_dict

    # Check for possible dishes
    possible_dishes = []
    for item in recipe_dict:
        if set(recipe_dict[item]["ingredients"]["mandatory"]).issubset(available_items):
            possible_dishes.append(recipe_dict[item]["pretty-name"])

    food_dict = {"foods": possible_dishes}
    food_dict_str = str(food_dict).replace("'", '"')
    return food_dict_str


@app.route('/fatboy/get_all_ingredients')
def get_all_ingredients():
    # read all recipes
    recipe_path = "meal-manager/recipes"
    print(os.listdir(recipe_path))
    recipe_files = [pos_json for pos_json in os.listdir(recipe_path) if pos_json.endswith('.json')]

    recipe_dict = {}
    for item in recipe_files:
        recipe_name = item.replace(".json", "")
        file = open(recipe_path + '/' + item, 'r', encoding='utf-8')
        file_dict = json.load(file)
        recipe_dict[recipe_name] = file_dict

    ingredient_list = []
    for item in recipe_dict:
        ingredient_list += recipe_dict[item]["ingredients"]["mandatory"]
    
    ingredient_dict = {"ingredients": list(set(ingredient_list))}
    ingredient_dict_str = str(ingredient_dict).replace("'", '"')
    return ingredient_dict


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 1234)